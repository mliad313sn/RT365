"""Trade pipeline coordinator (P1): Schema Validation -> Eligibility -> Risk -> Optional Approval -> Gateway.

[Committee] In the dev/sim build the coordinator runs in one process; it enters each plane
explicitly so the PlaneGuard proves the topology. In deployment each stage is a service on the
bus (ADR-005) and the same functions are invoked by consumers with inbox dedupe.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Any

from approval_service.queue import ApprovalQueue, ApprovalRecord
from compliance_engine.eligibility import decide_eligibility
from execution_gateway.gateway import ExecutionGateway
from execution_gateway.lease import LeaseStore
from risk_engine.engine import decide
from risk_engine.policy import RiskPolicy
from rtcore.envelope import make_event
from rtcore.errors import ControlDenied
from rtcore.ids import new_id
from rtcore.planes import Plane, enter
from rtcore.schemas.account import AccountMode, AccountSnapshot
from rtcore.schemas.base import StrictModel
from rtcore.schemas.compliance import CustomerProfile, EligibilityDecision, EligibilityOutcome, JurisdictionCell, RestrictedLists
from rtcore.schemas.decision import DecisionRecord, Outcome
from rtcore.schemas.fx import FxSnapshot
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


# SLI emission points owned by this coordinator [Source: 10; observability/slis.yaml]. The pipeline is the only
# place that sees a decision request, the snapshot it decided on and the ack that followed, so it is where the
# control-plane SLIs are emitted. Names are the ones slis.yaml declares; a change here is a change there.
M_DECISION_REQUESTS = "control_plane.decision_requests"
M_DECISIONS_RECORDED = "control_plane.decisions_recorded"
M_DECISION_UNAVAILABLE = "control_plane.decision_unavailable"
M_FRESHNESS_S = "pipeline.market_data_freshness_s"
M_DECISION_LATENCY_MS = "pipeline.risk_decision_latency_ms"
M_ORDER_ACK_LATENCY_MS = "pipeline.order_ack_latency_ms"
ACK_STATES = ("ACKNOWLEDGED", "PARTIALLY_FILLED", "FILLED", "BROKER_REJECTED")

# Explicit map; an unknown mode is refused, never defaulted to LIVE (review P13).
TARGET_FOR_MODE = {
    AccountMode.BACKTEST: ExecutionTarget.SIM,
    AccountMode.PAPER: ExecutionTarget.PAPER,
    AccountMode.SUPERVISED: ExecutionTarget.LIVE,
    AccountMode.BOUNDED_AUTONOMOUS: ExecutionTarget.LIVE,
}


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
    sign_command: Callable[[OrderCommand], OrderCommand]  # control-plane authorisation (IVA V-C2)
    strategy_owner: Callable[[str, str], str | None]  # (strategy_id, version) -> owner; owner never approves own intents (IVA-04)
    on_authorised: Callable[[ValidatedIntent, DecisionRecord], object] = lambda vi, d: None
    inbox: Inbox | None = None
    alert: Callable[[str, dict[str, Any]], object] = lambda name, payload: None
    # FX is read here, at decision time, and handed to the engine as data: (snapshot, freshness budget). The default
    # supplies neither, which is fail-closed for a cross-currency book and a no-op for a single-currency one (F-3).
    fx_inputs: Callable[[ValidatedIntent, datetime], tuple[FxSnapshot | None, Decimal | None]] = lambda vi, at: (None, None)
    # Observability hooks [F-03, SRE step 0]. Measurement only: nothing here is ever a decision input, and the
    # default pair is a no-op so a caller that wires no registry behaves exactly as before.
    count: Callable[[str], object] = lambda name: None
    observe: Callable[[str, float], object] = lambda name, value: None

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

    # --- measurement (never a decision input) ------------------------------------------------------------
    def _observe_freshness(self, mkt: MarketSnapshot | None, now: datetime) -> None:
        """market_data_freshness_s at the point the decision actually used the snapshot (the RK-FRESH input)."""
        if mkt is not None:
            self.observe(M_FRESHNESS_S, (now - mkt.market_ts).total_seconds())

    def _observe_decision_latency(self, intent_id: str) -> None:
        """risk_decision_latency_ms: intent enqueue -> decision record write, on the monotonic clock of this process.

        In-process only: there is no trace-context carrier between services, so this cannot be joined across a
        deployed cell today [Open: R-05, SRE-R10].
        """
        elapsed = self.tracker.since_create_ms(intent_id)
        if elapsed is not None:
            self.observe(M_DECISION_LATENCY_MS, elapsed)

    # --- stages ---------------------------------------------------------------------------------------
    def process(self, vi: ValidatedIntent, *, now: datetime) -> PipelineResult:
        inbox = self.inbox or Inbox()
        result, _fresh = inbox.process_once(f"intent:{vi.intent_hash}", lambda: self._process(vi, now))
        return result

    def _process(self, vi: ValidatedIntent, now: datetime) -> PipelineResult:
        intent_id = str(vi.intent.intent_id)
        # control_plane_availability, first end: one request counted per intent actually processed (a deduped
        # replay is answered from the inbox and is not a second request).
        self.count(M_DECISION_REQUESTS)
        with enter(Plane.CONTROL):
            try:
                ei = self.eligibility_inputs(vi, now)
            except Exception as exc:  # unknown account/customer/instrument: fail closed, never crash the consumer (IVA-24)
                self.count(M_DECISION_UNAVAILABLE)
                self.tracker.transition(
                    intent_id, IntentState.HALTED, now=now, detail={"reason": f"inputs unavailable: {type(exc).__name__}"}
                )
                self.audit(
                    "eligibility.inputs_unavailable",
                    vi.correlation_id,
                    vi.tenant_id,
                    vi.intent.account_id,
                    {"intent_id": intent_id, "error": type(exc).__name__},
                )
                raise ControlDenied(f"eligibility inputs unavailable for intent {intent_id}: {type(exc).__name__}") from exc
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
                # A refusal is a control-plane decision, and a successful one: availability counts answers, not approvals.
                self.count(M_DECISIONS_RECORDED)
                self.tracker.transition(intent_id, IntentState.INELIGIBLE, now=now, detail={"reason_codes": list(elig.reason_codes)})
                return PipelineResult(
                    validated_intent=vi, eligibility=elig, decision=None, approval_id=None, order=None, final_state=IntentState.INELIGIBLE
                )
            self.tracker.transition(intent_id, IntentState.ELIGIBLE, now=now)

            acct = self.account_snapshot(vi, now)
            mkt = self.market_snapshot(vi, now)
            self._observe_freshness(mkt, now)
            fx, fx_budget = self.fx_inputs(vi, now)
            decision = decide(vi, acct, mkt, self.policy(), now, fx, fx_budget)
            self.audit("risk.decided.v1", vi.correlation_id, vi.tenant_id, vi.intent.account_id, decision.model_dump(mode="json"))
            self.count(M_DECISIONS_RECORDED)
            self._observe_decision_latency(intent_id)
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
                item = self.approvals.enqueue(
                    vi, decision, now=now, strategy_owner_id=self.strategy_owner(vi.intent.strategy_id, vi.intent.strategy_version)
                )
                self.tracker.transition(intent_id, IntentState.PENDING_APPROVAL, now=now, detail={"approval_id": item.approval_id})
                return PipelineResult(
                    validated_intent=vi,
                    eligibility=elig,
                    decision=decision,
                    approval_id=item.approval_id,
                    order=None,
                    final_state=IntentState.PENDING_APPROVAL,
                )
            if acct is None:  # decide() already returns HALTED for a missing snapshot; this guards the type, not the logic
                raise ControlDenied("account snapshot unavailable after an APPROVED decision (impossible by construction)")
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
        """Human approval authorises execution only if a fresh decision on current snapshots still allows it (Risk review OBJ-2)."""
        item = self.approvals.get(record.approval_id)
        vi, decision = item.validated_intent, item.decision
        intent_id = str(vi.intent.intent_id)
        self.count(M_DECISION_REQUESTS)  # a re-decision is a control-plane decision request like any other
        with enter(Plane.CONTROL):
            self._emit("approval.recorded.v1", vi, record, now)
            acct = self.account_snapshot(vi, now)
            mkt = self.market_snapshot(vi, now)
            self._observe_freshness(mkt, now)
            fx, fx_budget = self.fx_inputs(vi, now)
            fresh = decide(vi, acct, mkt, self.policy(), now, fx, fx_budget)
            self.audit(
                "risk.redecided.v1",
                vi.correlation_id,
                vi.tenant_id,
                vi.intent.account_id,
                {**fresh.model_dump(mode="json"), "approval_id": record.approval_id},
            )
            self.count(M_DECISIONS_RECORDED)
            if acct is None or fresh.outcome == Outcome.HALTED:
                self.tracker.transition(
                    intent_id,
                    IntentState.HALTED,
                    now=now,
                    detail={"reason": "inputs unavailable or halted at execution time", "reason_codes": list(fresh.reason_codes)},
                )
                raise ControlDenied(f"approved intent halted at execution time: {fresh.reason_codes}")
            if fresh.outcome == Outcome.REJECTED:
                self.tracker.transition(
                    intent_id,
                    IntentState.REJECTED,
                    now=now,
                    detail={"reason": "re-decision rejected", "reason_codes": list(fresh.reason_codes)},
                )
                raise ControlDenied(f"approved intent rejected on re-decision: {fresh.reason_codes}")
            return self._authorise_and_execute(
                vi, decision, approval_id=record.approval_id, authorised_by=f"APPROVAL:{record.approver_id}", mode=acct.mode, now=now
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
        if mode not in TARGET_FOR_MODE:
            self.tracker.transition(intent_id, IntentState.HALTED, now=now, detail={"reason": f"no execution target for mode {mode.value}"})
            raise ControlDenied(f"mode {mode.value} has no execution target (fail closed)")
        command = OrderCommand(
            command_id=new_id("cmd"),
            strategy_id=i.strategy_id,
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
            execution_target=TARGET_FOR_MODE[mode],
        )
        command = self.sign_command(command)
        self.tracker.transition(
            intent_id,
            IntentState.AUTHORISED,
            now=now,
            detail={"idempotency_key": command.idempotency_key, "target": command.execution_target.value},
        )
        self.on_authorised(vi, decision)
        self._emit("order.command.v1", vi, command, now)
        self.audit(
            "order.command.v1",
            vi.correlation_id,
            vi.tenant_id,
            i.account_id,
            {
                "command_id": command.command_id,
                "intent_id": intent_id,
                "decision_id": decision.decision_id,
                "approval_id": approval_id,
                "authorised_by": authorised_by,
                "idempotency_key": command.idempotency_key,
                "policy_version": decision.policy_version,
                "target": command.execution_target.value,
            },
        )
        # order_ack_latency_ms: authorised command -> broker ack, measured by the caller. The gateway itself is a
        # protected path and is not instrumented from here; this is the command-to-ack wall time including the lease.
        ack_started = time.perf_counter()
        with enter(Plane.CONTROL):
            lease = self.leases.acquire(i.account_id, self.executor_id, now=now)
            order = self.gateway.submit(command, executor_id=self.executor_id, fencing_token=lease.fencing_token, now=now)
        if order.state.value in ACK_STATES:
            self.observe(M_ORDER_ACK_LATENCY_MS, (time.perf_counter() - ack_started) * 1000.0)
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
