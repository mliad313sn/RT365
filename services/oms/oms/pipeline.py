"""Trade pipeline coordinator (P1): Schema Validation -> Eligibility -> Risk -> Optional Approval -> Gateway.

[Committee] In the dev/sim build the coordinator runs in one process; it enters each plane
explicitly so the PlaneGuard proves the topology. In deployment each stage is a service on the
bus (ADR-005) and the same functions are invoked by consumers with inbox dedupe.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from approval_service.queue import ApprovalQueue, ApprovalRecord
from compliance_engine.eligibility import decide_eligibility
from execution_gateway.gateway import ExecutionGateway
from execution_gateway.lease import LeaseStore
from risk_engine.engine import decide
from risk_engine.policy import RiskPolicy
from rtcore.envelope import make_event
from rtcore.ids import new_id
from rtcore.planes import Plane, enter
from rtcore.schemas.account import AccountMode, AccountSnapshot
from rtcore.schemas.base import StrictModel
from rtcore.schemas.compliance import CustomerProfile, EligibilityDecision, EligibilityOutcome, JurisdictionCell, RestrictedLists
from rtcore.schemas.decision import DecisionRecord, Outcome
from rtcore.schemas.intent import ValidatedIntent
from rtcore.schemas.market import InstrumentAttributes, MarketSnapshot
from rtcore.schemas.order import ExecutionTarget, OrderCommand, OrderRecord, idempotency_key

from oms.lifecycle import IntentState, IntentTracker
from oms.outbox import Inbox, Outbox


class EligibilityInputs(StrictModel):
    customer: CustomerProfile | None
    instrument: InstrumentAttributes | None
    cells: tuple[JurisdictionCell, ...] | None
    restricted: RestrictedLists | None
    broker: str
    feature: str


class PipelineResult(StrictModel):
    validated_intent: ValidatedIntent
    eligibility: EligibilityDecision
    decision: DecisionRecord | None
    approval_id: str | None
    order: OrderRecord | None
    final_state: IntentState


TARGET_FOR_MODE = {AccountMode.BACKTEST: ExecutionTarget.SIM, AccountMode.PAPER: ExecutionTarget.PAPER}


@dataclass
class TradePipeline:
    tracker: IntentTracker
    outbox: Outbox
    audit: Callable[[str, str, str, str | None, dict[str, Any]], object]
    eligibility_inputs: Callable[[ValidatedIntent, datetime], EligibilityInputs]
    account_snapshot: Callable[[ValidatedIntent, datetime], AccountSnapshot | None]
    market_snapshot: Callable[[ValidatedIntent, datetime], MarketSnapshot | None]
    policy: Callable[[], RiskPolicy | None]
    approvals: ApprovalQueue
    gateway: ExecutionGateway
    leases: LeaseStore
    executor_id: str
    on_authorised: Callable[[ValidatedIntent, DecisionRecord], object] = lambda vi, d: None
    inbox: Inbox | None = None
    alert: Callable[[str, dict[str, Any]], object] = lambda name, payload: None

    def _emit(self, name: str, vi: ValidatedIntent, payload: Any, now: datetime) -> None:
        self.outbox.publish(
            make_event(
                name,
                correlation_id=vi.correlation_id,
                tenant=vi.tenant_id,
                account=vi.intent.account_id,
                producer="oms.pipeline",
                payload=payload,
                market_ts=vi.intent.market_ts,
                emitted_ts=now,
            )
        )

    # --- stages ---------------------------------------------------------------------------------------
    def process(self, vi: ValidatedIntent, *, now: datetime) -> PipelineResult:
        inbox = self.inbox or Inbox()
        result, _fresh = inbox.process_once(f"intent:{vi.intent_hash}", lambda: self._process(vi, now))
        return result

    def _process(self, vi: ValidatedIntent, now: datetime) -> PipelineResult:
        intent_id = str(vi.intent.intent_id)
        with enter(Plane.CONTROL):
            ei = self.eligibility_inputs(vi, now)
            elig = decide_eligibility(
                vi, ei.customer, ei.instrument, ei.cells, ei.restricted, broker=ei.broker, feature=ei.feature, now=now
            )
            self.audit("eligibility.decided.v1", vi.correlation_id, vi.tenant_id, vi.intent.account_id, elig.model_dump(mode="json"))
            self._emit("eligibility.decided.v1", vi, elig, now)
            if "CP-INTEG" in elig.reason_codes:
                self.alert(
                    "risk.integrity_violation", {"intent_id": intent_id, "correlation_id": vi.correlation_id, "stage": "eligibility"}
                )
            if elig.outcome != EligibilityOutcome.ELIGIBLE:
                self.tracker.transition(intent_id, IntentState.INELIGIBLE, now=now, detail={"reason_codes": list(elig.reason_codes)})
                return PipelineResult(
                    validated_intent=vi, eligibility=elig, decision=None, approval_id=None, order=None, final_state=IntentState.INELIGIBLE
                )
            self.tracker.transition(intent_id, IntentState.ELIGIBLE, now=now)

            acct = self.account_snapshot(vi, now)
            mkt = self.market_snapshot(vi, now)
            decision = decide(vi, acct, mkt, self.policy(), now)
            self.audit("risk.decided.v1", vi.correlation_id, vi.tenant_id, vi.intent.account_id, decision.model_dump(mode="json"))
            self._emit("risk.decided.v1", vi, decision, now)
            if "RK-INTEG" in decision.reason_codes:
                self.alert("risk.integrity_violation", {"intent_id": intent_id, "correlation_id": vi.correlation_id})
            if decision.outcome == Outcome.HALTED:
                self.tracker.transition(intent_id, IntentState.HALTED, now=now, detail={"reason_codes": list(decision.reason_codes)})
                return PipelineResult(
                    validated_intent=vi, eligibility=elig, decision=decision, approval_id=None, order=None, final_state=IntentState.HALTED
                )
            self.tracker.transition(
                intent_id,
                IntentState.RISK_DECIDED,
                now=now,
                detail={"outcome": decision.outcome.value, "reason_codes": list(decision.reason_codes)},
            )
            if decision.outcome == Outcome.REJECTED:
                self.tracker.transition(intent_id, IntentState.REJECTED, now=now)
                return PipelineResult(
                    validated_intent=vi, eligibility=elig, decision=decision, approval_id=None, order=None, final_state=IntentState.REJECTED
                )
            if decision.outcome == Outcome.REQUIRES_HUMAN_APPROVAL:
                item = self.approvals.enqueue(vi, decision, now=now)
                self.tracker.transition(intent_id, IntentState.PENDING_APPROVAL, now=now, detail={"approval_id": item.approval_id})
                return PipelineResult(
                    validated_intent=vi,
                    eligibility=elig,
                    decision=decision,
                    approval_id=item.approval_id,
                    order=None,
                    final_state=IntentState.PENDING_APPROVAL,
                )
            assert acct is not None
            order = self._authorise_and_execute(vi, decision, approval_id=None, authorised_by="RISK_ENGINE", mode=acct.mode, now=now)
            return PipelineResult(
                validated_intent=vi,
                eligibility=elig,
                decision=decision,
                approval_id=None,
                order=order,
                final_state=self.tracker.get(intent_id).state,
            )

    def on_approval(self, record: ApprovalRecord, *, now: datetime) -> OrderRecord:
        item = self.approvals.get(record.approval_id)
        vi, decision = item.validated_intent, item.decision
        with enter(Plane.CONTROL):
            self._emit("approval.recorded.v1", vi, record, now)
            acct = self.account_snapshot(vi, now)
            mode = acct.mode if acct else AccountMode.SUPERVISED
            if acct is not None and (acct.kill_switch.any_active() or acct.mode == AccountMode.HALTED):
                self.tracker.transition(
                    str(vi.intent.intent_id), IntentState.HALTED, now=now, detail={"reason": "kill switch active at execution time"}
                )
                raise RuntimeError("Kill Switch active; approved intent halted")
            return self._authorise_and_execute(
                vi, decision, approval_id=record.approval_id, authorised_by=f"APPROVAL:{record.approver_id}", mode=mode, now=now
            )

    def _authorise_and_execute(
        self,
        vi: ValidatedIntent,
        decision: DecisionRecord,
        *,
        approval_id: str | None,
        authorised_by: str,
        mode: AccountMode,
        now: datetime,
    ) -> OrderRecord:
        intent_id = str(vi.intent.intent_id)
        i = vi.intent
        command = OrderCommand(
            command_id=new_id("cmd"),
            idempotency_key=idempotency_key(intent_id, i.account_id, decision.policy_version),
            intent_id=intent_id,
            intent_hash=vi.intent_hash,
            decision_id=decision.decision_id,
            approval_id=approval_id,
            tenant_id=vi.tenant_id,
            account_id=i.account_id,
            venue=i.venue,
            instrument_id=i.instrument_id,
            side=i.side,
            order_type=i.order_type,
            quantity=i.quantity,
            limit_price=i.limit_price,
            stop_price=i.stop_price,
            time_in_force=i.time_in_force,
            policy_version=decision.policy_version,
            correlation_id=vi.correlation_id,
            authorised_at=now,
            authorised_by=authorised_by,
            execution_target=TARGET_FOR_MODE.get(mode, ExecutionTarget.LIVE),
        )
        self.tracker.transition(
            intent_id,
            IntentState.AUTHORISED,
            now=now,
            detail={"idempotency_key": command.idempotency_key, "target": command.execution_target.value},
        )
        self.on_authorised(vi, decision)
        self._emit("order.command.v1", vi, command, now)
        with enter(Plane.CONTROL):
            lease = self.leases.acquire(i.account_id, self.executor_id, now=now)
            order = self.gateway.submit(command, executor_id=self.executor_id, fencing_token=lease.fencing_token, now=now)
        state_map = {
            "SUBMITTED": IntentState.SUBMITTED,
            "ACKNOWLEDGED": IntentState.ACKNOWLEDGED,
            "BROKER_REJECTED": IntentState.BROKER_REJECTED,
            "PARTIALLY_FILLED": IntentState.PARTIALLY_FILLED,
            "FILLED": IntentState.FILLED,
        }
        self.tracker.transition(intent_id, IntentState.SUBMITTED, now=now)
        if order.state.value in ("ACKNOWLEDGED", "PARTIALLY_FILLED", "FILLED", "BROKER_REJECTED"):
            self.tracker.transition(
                intent_id, IntentState.ACKNOWLEDGED if order.state.value != "BROKER_REJECTED" else IntentState.BROKER_REJECTED, now=now
            )
            if order.state.value in ("PARTIALLY_FILLED", "FILLED"):
                self.tracker.transition(intent_id, state_map[order.state.value], now=now)
        return order

    def sync_order_state(self, order: OrderRecord, *, now: datetime) -> None:
        """Bring the intent tracker in line with later fills/cancels reported by the gateway."""
        intent_id = order.command.intent_id
        cur = self.tracker.get(intent_id).state
        target = {"PARTIALLY_FILLED": IntentState.PARTIALLY_FILLED, "FILLED": IntentState.FILLED, "CANCELLED": IntentState.CANCELLED}.get(
            order.state.value
        )
        if target is not None and cur != target and not (cur == IntentState.FILLED):
            try:
                self.tracker.transition(intent_id, target, now=now)
            except Exception:  # noqa: BLE001 - state already terminal; nothing to sync
                pass
