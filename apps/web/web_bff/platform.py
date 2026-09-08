"""Composition root for the dev/sim environment [Committee; ADR-010].

Wires every bounded context in one process with in-memory stores. It exists so that the
control envelope can be exercised end to end (tests, BFF, backtests, synthetic probes)
before any external dependency exists. Nothing here enables a market, a strategy or autonomy:
the fixture tenant/account/jurisdiction are explicitly simulated.

Review remediations wired here: private PlaneGuard per platform (MCP OBJ-1), persisted revocations
and alert payload contracts (MCP OBJ-3), scoped Kill Switch cancels and lease preemption (Trading
review), fees charged by the broker inside the pipeline (ADR-008), maker-checker as the only limit
write path (Risk review F-04), RT-RECON fed from open tickets and two-person autonomy restore (P6).
"""

from __future__ import annotations

import hashlib
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime, time, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any

from approval_service.queue import ApprovalQueue, ApprovalRecord
from audit_service.anchor import FileAnchorPublisher
from audit_service.store import DEFAULT_ANCHOR_EVERY, DEFAULT_MAX_ANCHOR_LAG, AuditStore
from backtest_engine.costs import CostModel
from backtest_engine.runner import BacktestReport, BacktestRunner
from broker_adapters.base import VaultRef
from broker_adapters.simulated import SimulatedBroker
from compliance_engine.jurisdiction import JurisdictionRegistry
from compliance_engine.retention import RetentionService
from compliance_engine.surveillance import StrategyDeclaration
from data_providers.simulated import SimulatedFeed
from execution_gateway.authorisation import CommandAuthoriser, Ed25519CommandAuthoriser
from execution_gateway.gateway import ExecutionGateway
from execution_gateway.lease import LeaseStore
from identity_service.accounts import Account, AccountRegistry, Tenant
from identity_service.makerchecker import MakerChecker
from killswitch_service.service import KillSwitchHooks, KillSwitchLevel, KillSwitchService
from market_data.calendar import SessionCalendar
from market_data.fx import FxStore
from market_data.instruments import InstrumentMaster
from market_data.service import MarketDataService
from market_data.store import BitemporalStore
from mcp_servers.allowlist import AllowlistStore
from mcp_servers.egress import EgressPolicy
from mcp_servers.identity import AgentIdentity, IdentityIssuer, Principal
from mcp_servers.registry import ToolRegistry, load_registry
from mcp_servers.revocation import RevocationList
from mcp_servers.runtime import ToolRuntime, current_principal
from mcp_servers.tools import build_tools
from oms.intent_queue import IntentQueue
from oms.lifecycle import IntentState, IntentTracker
from oms.outbox import Inbox, Outbox
from oms.pipeline import TARGET_FOR_MODE, EligibilityInputs, PipelineResult, TradePipeline
from portfolio_service.ledger import Ledger, PositionState
from reconciliation_service.reconcile import BreakSeverity, ReconciliationResult, reconcile
from reconciliation_service.tickets import BreakTicketService
from risk_engine.monitors import RuntimeMetrics, evaluate_runtime
from risk_engine.policy import RiskPolicy, apply_limit_change, load_policy
from rtcore.envelope import make_event
from rtcore.errors import ControlDenied
from rtcore.ids import hash_of
from rtcore.lines import Actor, ActorKind, Role, system_actor
from rtcore.money import ZERO
from rtcore.planes import Plane, PlaneGuard, enter
from rtcore.resources import resource_root
from rtcore.schemas.account import AccountMode, AccountSnapshot, EmergencyPolicy, NavStatus, OpenOrder, TradingStatus
from rtcore.schemas.compliance import (
    ClassificationBasis,
    ClassificationEvidence,
    CustomerProfile,
    CustomerType,
    DisclosureAcknowledgement,
    LegalRecordRef,
    ModeConsent,
    RestrictedLists,
)
from rtcore.schemas.decision import DecisionRecord, Outcome
from rtcore.schemas.fx import FxSnapshot
from rtcore.schemas.intent import TradeIntent, ValidatedIntent
from rtcore.schemas.market import InstrumentAttributes, MarketSnapshot
from rtcore.schemas.order import OrderCommand, OrderRecord
from rtcore.store import MemoryStore, SqliteStore, Store
from rtcore.trust import TrustSet
from rtobs.alerts import Alert, AlertRouter
from rtobs.metrics import MetricsRegistry
from rtobs.slis import SliCatalog
from rtobs.tracing import Tracer
from strategy_service.registry import StrategyRegistry, StrategyStatus, StrategyVersion
from strategy_service.signals import SmaCrossoverStrategy, intent_from_signal

TENANT = "tenant-sim"
ACCOUNT = "acct-sim-001"
CUSTOMER = "cust-sim-001"
# Second simulated tenant (opt-in via build_sim_platform(second_tenant=True)) for the TC-TEN isolation quartet [RAID R-22, RT-03]
TENANT_B = "tenant-sim-b"
ACCOUNT_B = "acct-sim-b-001"
CUSTOMER_B = "cust-sim-b-001"
# Human principals are bound to a tenant server-side (identity_service.accounts.bind_principal); in sim the fixture
# roster below stands in for the IdP tenant claim [Open: R-06]. Tenant is never a client-asserted header.
SIM_PRINCIPALS: dict[str, tuple[str, ...]] = {
    TENANT: (
        "risk.officer.1",
        "chief.risk",
        "sre.lead",
        "trading.lead",
        "compliance.agent",
        "legal.agent",
        "trader.1",
        "pm.1",
        "ops.1",
        "auditor.1",
        "iva.1",
        "quant.fixture",
        "model.risk",
        "legal.fixture",
        "compliance.fixture",
    ),
    TENANT_B: ("risk.officer.b", "pm.b", "sre.b", "trader.b", "ops.b", "trading.lead.b"),
}
INSTRUMENT = "SIMEQ1"
INSTRUMENT_2 = "SIMEQ2"
VENUE = "SIMX"
BROKER = "sim-broker"
STRATEGY = "strat-sma-xover"
STRATEGY_VERSION = "0.1"
JURISDICTION = "ZZ"  # ISO 3166 user-assigned code: explicitly not a real jurisdiction [Open: O-11]
SIM_DISCLOSURE_VERSION = "SIM-DISCL-v0.1"  # fixture disclosure pack version; approved wording per cell is a human act [Open: H-16]
SIM_LEGAL_RECORD_ID = "SIM-LEGAL-FIXTURE-001"  # SIM- prefix: valid only on the simulated cell, never a legal opinion (D-012)
BASE_TIME = datetime(2026, 9, 7, 14, 0, tzinfo=UTC)  # a Monday, session open
BACKTEST_START = datetime(2026, 9, 4, 14, 0, tzinfo=UTC)  # a Friday, session open
# dev/sim fixture only: the FX freshness budget a valuation is allowed to use. It is *not* a policy value — the
# budget per currency pair, venue and asset class is a Trading Risk Committee decision [Open: O-07, O-29].
FX_MAX_AGE_S = Decimal("5")
STORE_FILENAME = "control_state.sqlite"
AUDIT_STORE_FILENAME = "audit_state.sqlite"  # the audit trail is its own store (B-5): control state and its evidence never share a file  # one file per platform under store_dir (ADR-018 proposed; R-05)


@dataclass
class SimPlatform:
    now: datetime
    audit: AuditStore
    outbox: Outbox
    tracker: IntentTracker
    intent_queue: IntentQueue
    accounts: AccountRegistry
    ledger: Ledger
    market: MarketDataService
    fx: FxStore
    feed: SimulatedFeed
    broker: SimulatedBroker
    leases: LeaseStore
    gateway: ExecutionGateway
    approvals: ApprovalQueue
    jurisdictions: JurisdictionRegistry
    retention: RetentionService
    strategies: StrategyRegistry
    policy: RiskPolicy | None
    restricted: RestrictedLists
    customers: dict[str, CustomerProfile]
    issuer: IdentityIssuer
    registry: ToolRegistry
    runtime: ToolRuntime
    egress: EgressPolicy
    revocations: RevocationList
    limits_mc: MakerChecker
    alerts: AlertRouter
    metrics: MetricsRegistry
    tracer: Tracer
    slis: SliCatalog
    guard: PlaneGuard
    allowlists: AllowlistStore
    pipeline: TradePipeline = field(init=False)
    killswitch: KillSwitchService = field(init=False)
    tickets: BreakTicketService = field(init=False)
    notifications: list[tuple[str, dict[str, Any]]] = field(default_factory=list)
    applied_fill_refs: set[str] = field(default_factory=set)
    applied_changes: set[str] = field(default_factory=set)
    executor_id: str = "executor-a"
    fx_max_age_s: Decimal | None = FX_MAX_AGE_S  # dev/sim fixture; the real budget is a committee decision [Open: O-07]
    store: Store = field(default_factory=MemoryStore)  # lease, outbox/inbox, gateway indexes, Kill Switch activations

    # --- clock ----------------------------------------------------------------------------------------
    def advance(self, seconds: float) -> datetime:
        self.now = self.now + timedelta(seconds=seconds)
        return self.now

    # --- tenancy ---------------------------------------------------------------------------------------
    def tenant_for(self, account_id: str | None) -> str:
        """The tenant an account belongs to. An unknown account maps to the default sim tenant so the pipeline
        can fail closed on inputs (IVA-24) instead of the composition root raising first."""
        try:
            return self.accounts.get(str(account_id)).tenant_id
        except KeyError:
            return TENANT

    # --- FX ----------------------------------------------------------------------------------------------
    def ingest_fx(self, snapshot: FxSnapshot, *, correlation_id: str, now: datetime | None = None) -> FxSnapshot:
        """The only write path for a rate. Knowledge time is the platform clock, so no reader sees it earlier.

        There is deliberately no MCP tool and no intent field behind this: rates are operator/feed data, and the
        analytics plane has no route to it (ADR-001, F-3).
        """
        at = now or self.now
        self.fx.put(snapshot, knowledge_ts=at)
        self.audit.append(
            correlation_id=correlation_id,
            tenant=TENANT,
            account=None,
            actor="market_data.fx",
            action="fx.snapshot.ingested",
            payload=snapshot.audit_payload(),
            ts=at,
        )
        self.metrics.inc("fx.snapshots.ingested")
        return snapshot

    def fx_for_decision(self, now: datetime | None = None) -> FxSnapshot | None:
        at = now or self.now
        return self.fx.latest(as_of=at, knowledge_ts=at)

    # --- snapshot providers ------------------------------------------------------------------------------
    def account_snapshot(self, account_id: str, now: datetime | None = None, correlation_id: str | None = None) -> AccountSnapshot | None:
        now = now or self.now
        try:
            acct = self.accounts.get(account_id)
        except KeyError:
            return None
        open_orders = tuple(
            OpenOrder(
                order_id=o.order_id,
                instrument_id=o.command.instrument_id,
                side=o.command.side,
                quantity=o.remaining_quantity,
                notional=o.remaining_quantity * (o.command.limit_price or self._last_price(o.command.instrument_id, now)),
                currency=self.ledger.currency_of(o.command.instrument_id, self.ledger.book(account_id)),
                submitted_at=o.updated_at,
            )
            for o in self.gateway.open_orders(account_id)
        )
        flags = self.killswitch.flags_for(tenant_id=acct.tenant_id, account_id=account_id)
        snapshot = self.ledger.snapshot(
            account_id,
            now=now,
            mode=acct.mode,
            trading_status=acct.trading_status,
            jurisdiction=acct.jurisdiction,
            customer_type=acct.customer_type,
            authorised_strategies=acct.authorised_strategies,
            open_orders=open_orders,
            kill_switch=flags,
            emergency_policy=acct.emergency_policy,
            capital_envelope=acct.capital_envelope,
            autonomy_suspended=acct.autonomy_suspended,
            liquidation_policy_ref=acct.liquidation_policy_ref,
            correlation_groups={"sim-equities": (INSTRUMENT, INSTRUMENT_2)},
            fx=self.fx_for_decision(now),
            fx_max_age_s=self.fx_max_age_s,
        )
        if snapshot.valuation is not None and snapshot.valuation.status == NavStatus.UNKNOWN:
            # An unvaluable book is an operational event, not a silent zero: reason code, values and thresholds.
            self.audit.append(
                correlation_id=correlation_id or f"valuation:{account_id}:{now.isoformat()}",
                tenant=acct.tenant_id,
                account=account_id,
                actor="portfolio.ledger",
                action="portfolio.valuation.unknown",
                payload={
                    "account_id": account_id,
                    "base_currency": snapshot.base_currency,
                    "reason_code": snapshot.valuation.reason_code,
                    "detail": snapshot.valuation.detail,
                    "fx_snapshot_id": snapshot.valuation.fx_snapshot_id,
                    "fx_max_age_s": str(self.fx_max_age_s),
                    "currencies": sorted(snapshot.cash_by_currency),
                },
                ts=now,
            )
            self.metrics.inc("portfolio.valuation.unknown")
        return snapshot

    def _last_price(self, instrument_id: str, now: datetime) -> Decimal:
        snap = self.market.store.latest(instrument_id, as_of=now, knowledge_ts=now)
        return snap.last_price if snap else Decimal("100")

    def market_snapshot(self, instrument_id: str, now: datetime | None = None) -> MarketSnapshot | None:
        return self.market.for_decision(instrument_id, now=now or self.now)

    # --- data ingestion ------------------------------------------------------------------------------------
    def ingest_bars(
        self, instrument_id: str, *, start: datetime, count: int, ingest_lag: timedelta = timedelta(milliseconds=200)
    ) -> tuple[MarketSnapshot, ...]:
        bars = self.feed.bars(instrument_id, start=start, end=start + self.feed.step * (count - 1))
        out = []
        for b in bars:
            snap = self.market.ingest(self.feed, b, tenant_id=TENANT, ingest_ts=b.market_ts + ingest_lag)
            self.ledger.mark(instrument_id, snap.last_price)
            self.broker.set_reference_price(instrument_id, snap.last_price, now=snap.market_ts)
            out.append(snap)
        return tuple(out)

    # --- intents -------------------------------------------------------------------------------------------
    def rotate_command_signer(self, signer: Ed25519CommandAuthoriser) -> None:
        """Rotation step 2 of 3 (add the new key to the trust set; re-point the pipeline; retire the old key).

        Only the composition root calls this; the gateway's verifier is untouched because it reads the trust set.
        """
        self.pipeline.sign_command = signer.sign
        self.audit.append(
            correlation_id=f"rotation:{signer.key_id}",
            tenant=TENANT,
            account=None,
            actor="composition_root",
            action="command.signer.rotated",
            payload={"key_id": signer.key_id, "algorithm": "Ed25519"},
        )

    def make_intent(self, **overrides: Any) -> dict[str, Any]:
        from uuid import uuid4

        snap = self.market_snapshot(INSTRUMENT)
        price = snap.last_price if snap else Decimal("100")
        base: dict[str, Any] = {
            "intent_id": str(uuid4()),
            "strategy_id": STRATEGY,
            "strategy_version": STRATEGY_VERSION,
            "model_id": "rule-sma",
            "model_version": "0.1",
            "account_id": ACCOUNT,
            "venue": VENUE,
            "instrument_id": INSTRUMENT,
            "side": "BUY",
            "order_type": "MARKET",
            "quantity": "100",
            "time_in_force": "DAY",
            "thesis_code": "SMA_XOVER_UP",
            "confidence": 0.55,
            "market_ts": (self.now - timedelta(seconds=1)).isoformat(),
            "data_provenance": ["simulated"],
            "expiry": (self.now + timedelta(minutes=5)).isoformat(),
            "protective_stop": str((price * Decimal("0.98")).quantize(Decimal("0.01"))),
            "evidence_refs": ["snapshot:fixture"],
        }
        base.update(overrides)
        return base

    def submit_intent(
        self,
        raw: dict[str, Any] | TradeIntent,
        *,
        submitted_by: str = "agent:sim",
        plane: Plane = Plane.ANALYTICS,
        now: datetime | None = None,
        tenant_id: str | None = None,
    ) -> ValidatedIntent:
        """Seal the intent under the tenant of its account; ``tenant_id`` overrides only for defence-in-depth tests."""
        account_id = raw.get("account_id") if isinstance(raw, dict) else raw.account_id
        tenant = tenant_id or self.tenant_for(str(account_id))
        with enter(plane):
            return self.intent_queue.submit(raw, tenant_id=tenant, submitted_by=submitted_by, now=now or self.now)

    def run_intent(
        self,
        raw: dict[str, Any] | TradeIntent,
        *,
        submitted_by: str = "agent:sim",
        now: datetime | None = None,
        tenant_id: str | None = None,
    ) -> PipelineResult:
        now = now or self.now
        vi = self.submit_intent(raw, submitted_by=submitted_by, now=now, tenant_id=tenant_id)
        self.intent_queue.take(str(vi.intent.intent_id), vi.tenant_id)
        result = self.pipeline.process(vi, now=now)
        self.settle(now)
        if result.order is not None:
            result = result.model_copy(
                update={"order": self.gateway.get(result.order.order_id), "final_state": self.tracker.get(str(vi.intent.intent_id)).state}
            )
        return result

    def approve(self, approval_id: str, actor: Actor, *, reason: str = "reviewed", now: datetime | None = None) -> OrderRecord:
        now = now or self.now
        record: ApprovalRecord = self.approvals.approve(approval_id, actor, reason=reason, now=now)
        order = self.pipeline.on_approval(record, now=now)
        self.settle(now)
        return self.gateway.get(order.order_id)

    def settle(self, now: datetime | None = None) -> None:
        now = now or self.now
        for order in self.gateway.poll_fills(now=now):
            self.pipeline.sync_order_state(order, now=now)
        for order in self.gateway.sync_statuses(now=now):
            self.pipeline.sync_order_state(order, now=now)
        for order in self.gateway.orders():
            for f in order.fills:
                if f.broker_ref in self.applied_fill_refs:
                    continue
                self.applied_fill_refs.add(f.broker_ref)
                self.ledger.apply_fill(
                    order.command.account_id, order.command.instrument_id, order.command.side, f.quantity, f.price, fee=f.fee
                )

    # --- reconciliation (P6) -------------------------------------------------------------------------------
    def reconcile(self, account_id: str = ACCOUNT, now: datetime | None = None) -> ReconciliationResult:
        now = now or self.now
        statement = self.broker.statement(account_id, as_of=now)
        result = reconcile(
            account_id=account_id,
            internal_positions=self.ledger.positions(account_id),
            internal_orders=self.gateway.orders(account_id),
            internal_cash=self.ledger.book(account_id).cash,
            statement=statement,
            now=now,
        )
        corr = f"recon:{account_id}:{now.isoformat()}"
        tenant = self.tenant_for(account_id)
        payload = {
            "account_id": account_id,
            "as_of": now.isoformat(),
            "positions_compared": result.positions_compared,
            "orders_compared": result.orders_compared,
            "break_count": len(result.breaks),
        }
        self.audit.append(
            correlation_id=corr,
            tenant=tenant,
            account=account_id,
            actor="reconciliation_service",
            action="reconciliation.completed.v1",
            payload=payload,
        )
        self.outbox.publish(
            make_event(
                "reconciliation.completed.v1",
                correlation_id=corr,
                tenant=tenant,
                account=account_id,
                producer="reconciliation_service",
                payload=payload,
                emitted_ts=now,
            )
        )
        for brk in result.breaks:
            self.tickets.open(brk, now=now)
            self.outbox.publish(
                make_event(
                    "reconciliation.break.v1",
                    correlation_id=brk.correlation_ids[0] if brk.correlation_ids else brk.break_id,
                    tenant=tenant,
                    account=account_id,
                    producer="reconciliation_service",
                    payload=brk,
                    emitted_ts=now,
                )
            )
        return result

    # --- runtime monitors (P4 triggers) -------------------------------------------------------------------
    def evaluate_monitors(self, account_id: str, metrics: RuntimeMetrics, now: datetime | None = None) -> tuple[str, ...]:
        now = now or self.now
        snap = self.account_snapshot(account_id, now)
        if snap is None or self.policy is None:
            return ()
        open_breaks = len(self.tickets.open_tickets(account_id))
        if open_breaks and metrics.open_reconciliation_breaks == 0:
            metrics = metrics.model_copy(update={"open_reconciliation_breaks": open_breaks})  # RT-RECON is fed from open tickets (P6)
        events = evaluate_runtime(snap, self.policy, metrics, now)
        activated = []
        monitor = Actor(actor_id="runtime-monitor", role=Role.RUNTIME_MONITOR, kind=ActorKind.SYSTEM)
        for ev in events:
            corr = f"halt:{account_id}:{ev.reason_code}"
            self.audit.append(
                correlation_id=corr,
                tenant=snap.tenant_id,
                account=account_id,
                actor="runtime_monitor",
                action="risk.halt.v1",
                payload=ev.model_dump(mode="json"),
            )
            self.outbox.publish(
                make_event(
                    "risk.halt.v1",
                    correlation_id=corr,
                    tenant=snap.tenant_id,
                    account=account_id,
                    producer="runtime_monitor",
                    payload=ev,
                    emitted_ts=now,
                )
            )
            level = KillSwitchLevel(ev.level) if ev.level in KillSwitchLevel.__members__ else KillSwitchLevel.ACCOUNT
            target = ev.target_id if ev.target_id != "*" else (account_id if level == KillSwitchLevel.ACCOUNT else "*")
            if not any(a.level == level and a.target_id == target for a in self.killswitch.active()):
                self.killswitch.activate(
                    level, target, reason=f"runtime monitor {ev.reason_code}: {ev.value} vs {ev.threshold}", actor=monitor, now=now
                )
            activated.append(ev.reason_code)
        return tuple(activated)

    # --- limits: the only write path (review F-04) ----------------------------------------------------------
    def apply_effective_limits(self, now: datetime | None = None) -> RiskPolicy | None:
        """EFFECTIVE maker-checker changes become a new policy version; nothing else can write a limit."""
        now = now or self.now
        if self.policy is None:
            return None
        for change_id in self.limits_mc.pending_ids():
            change = self.limits_mc.effective(change_id, now=now)
            if change is None or change.kind != "limit.changed" or change.change_id in self.applied_changes:
                continue
            payload = change.payload
            tenant = str(payload.get("tenant_id") or TENANT)
            self.policy = apply_limit_change(
                self.policy,
                level=str(payload["level"]),
                scope_id=str(payload["scope_id"]),
                metric=str(payload["metric"]),
                threshold=Decimal(str(payload["threshold"])),
                tenant_id=tenant,
                maker=change.maker_id,
                checker=change.checker_id or "",
                change_id=change.change_id,
                effective_from=change.effective_at or now,
            )
            self.applied_changes.add(change.change_id)
            self.audit.append(
                correlation_id=change.change_id,
                tenant=tenant,
                account=None,
                actor="policy_store",
                action="limit.changed.v1",
                payload={
                    **payload,
                    "change_id": change.change_id,
                    "policy_version": self.policy.policy_version,
                    "maker": change.maker_id,
                    "checker": change.checker_id,
                },
            )
            self.alerts.raise_alert("limit.changed", {"change_id": change.change_id, "policy_version": self.policy.policy_version})
        return self.policy

    def restore_autonomy(self, account_id: str, actor: Actor, second: Actor, *, reason: str) -> None:
        """Clearing an SLO/break suspension is a two-person, different-line human action (P4/P6)."""
        if not (actor.is_human and second.is_human) or actor.actor_id == second.actor_id or actor.line == second.line:
            raise ControlDenied("restoring autonomy requires two humans from different lines")
        acct = self.accounts.get(account_id)
        self.accounts._accounts[account_id] = acct.model_copy(update={"autonomy_suspended": False})
        self.audit.append(
            correlation_id=f"autonomy:{account_id}",
            tenant=acct.tenant_id,
            account=account_id,
            actor=actor.actor_id,
            action="account.autonomy.restored",
            payload={"first": actor.actor_id, "second": second.actor_id, "reason": reason},
        )

    # --- MCP helpers ---------------------------------------------------------------------------------------
    def issue_agent(
        self,
        *,
        agent_id: str = "agent-sim-1",
        strategy_id: str = STRATEGY,
        strategy_version: str = STRATEGY_VERSION,
        account_id: str = ACCOUNT,
        now: datetime | None = None,
        ttl: timedelta | None = None,
        tenant_id: str | None = None,
    ) -> AgentIdentity:
        """Mint an agent identity in the tenant of its account; ``tenant_id`` overrides only for negative tests."""
        return self.issuer.issue(
            agent_id=agent_id,
            tenant_id=tenant_id or self.tenant_for(account_id),
            account_id=account_id,
            strategy_id=strategy_id,
            strategy_version=strategy_version,
            model_id="rule-sma",
            model_version="0.1",
            prompt_id="P-STRAT-SIGNAL",
            prompt_version="0.1",
            now=now or self.now,
            ttl=ttl,
        )

    def tool_call(
        self, ident: AgentIdentity, tool: str, args: dict[str, Any], *, now: datetime | None = None, nonce: str | None = None
    ) -> Any:
        at = now or self.now
        sig = self.issuer.sign_call(ident, tool, args, now=at, nonce=nonce)
        with enter(Plane.ANALYTICS):
            return self.runtime.call(token_id=ident.token_id, signature=sig, tool=tool, args=args, now=at)

    # --- synthetic probe [C9] ---------------------------------------------------------------------------------
    def synthetic_probe(self, now: datetime | None = None) -> dict[str, Any]:
        now = now or self.now
        corr = f"probe-{now.isoformat()}"
        with self.tracer.span("market_snapshot", corr):
            snap = self.market_snapshot(INSTRUMENT, now)
        with self.tracer.span("signal", corr):
            raw = self.make_intent(quantity="1")
        with self.tracer.span("intent", corr):
            vi = self.submit_intent(raw, submitted_by="probe", now=now)
            self.intent_queue.pop()
        with self.tracer.span("eligibility", corr), self.tracer.span("risk", corr):
            result = self.pipeline.process(vi, now=now)
        if result.order is not None:
            self.tracer.record("order_command", corr)
            self.tracer.record("broker_ack", corr, ok=result.order.state.value != "BROKER_REJECTED")
        self.tracer.record("audit", corr, ok=len(self.audit.by_correlation(vi.correlation_id)) > 0)
        missing = self.tracer.missing(corr)
        self.metrics.inc("probe.runs")
        return {
            "correlation_id": vi.correlation_id,
            "snapshot": snap.snapshot_id if snap else None,
            "final_state": result.final_state.value,
            "missing_spans": list(missing),
        }


def _default_customer(now: datetime, customer_id: str = CUSTOMER, tenant_id: str = TENANT) -> CustomerProfile:
    # Fixture standing (council P-3/P-4): disclosures acknowledged, consent recorded for every order-placing mode so the sim
    # cell for each mode is exercisable, classification established by the fixture assessor (never self-declared). All values
    # are labelled simulated; none is evidence of a real onboarding.
    recorded = now - timedelta(days=1)
    return CustomerProfile(
        customer_id=customer_id,
        tenant_id=tenant_id,
        customer_type=CustomerType.RETAIL,
        jurisdiction=JURISDICTION,
        product_permissions=("EQUITY", "ETF"),
        appropriateness_assessed=False,
        complex_products_allowed=False,
        short_selling_allowed=False,
        disclosure_acknowledgement=DisclosureAcknowledgement(version=SIM_DISCLOSURE_VERSION, acknowledged_at=recorded),
        mode_consents=tuple(
            ModeConsent(mode=m, consented_at=recorded, consent_ref="SIM-CONSENT-FIXTURE [Committee: simulated]")
            for m in ("PAPER", "SUPERVISED", "BOUNDED_AUTONOMOUS")
        ),
        classification_evidence=ClassificationEvidence(
            evidence_ref="SIM-CLASS-FIXTURE-001 [Committee: simulated assessment]",
            assessed_by="compliance.fixture",
            assessed_at=recorded,
            basis=ClassificationBasis.ASSESSOR_REVIEW,
        ),
    )


def _sim_legal_record(now: datetime) -> LegalRecordRef:
    """Typed fixture record for the simulated cell: hash of a fixture byte string, never a document or an opinion."""
    return LegalRecordRef(
        record_id=SIM_LEGAL_RECORD_ID,
        signing_entity="sim fixture counsel [Committee: simulated cell, not a legal opinion]",
        signed_on=now.date(),
        document_sha256=hashlib.sha256(SIM_LEGAL_RECORD_ID.encode()).hexdigest(),
    )


def build_sim_platform(
    *,
    now: datetime = BASE_TIME,
    mode: AccountMode = AccountMode.PAPER,
    policy_path: Path | None = None,
    registry_path: Path | None = None,
    bars: int = 30,
    cash: Decimal = Decimal("1000000"),
    enable_cell: bool = True,
    revocations_path: Path | None = None,
    nonce_path: Path | None = None,
    store_dir: Path | None = None,
    anchor_dir: Path | None = None,
    anchor_every: int = DEFAULT_ANCHOR_EVERY,
    max_anchor_lag: int = DEFAULT_MAX_ANCHOR_LAG,
    executor_id: str = "executor-a",
    authorisation_key: bytes | None = None,
    second_tenant: bool = False,
    command_signer: Ed25519CommandAuthoriser | None = None,
    command_trust_set: TrustSet | None = None,
) -> SimPlatform:
    root = resource_root()  # source checkout, installed bundle or frozen executable; fails closed when absent (ADR-016)
    # Durable control state (ADR-010 seam): None keeps every store in memory (the default for tests and backtests);
    # a directory keeps lease, outbox/inbox, gateway indexes and Kill Switch activations in one SQLite file so a
    # rebuilt platform is a restart. The revocation and nonce journals default to the same directory so that a
    # restored activation is never paired with forgotten revocations. Audit durability is E11 (B-5), not this seam.
    control_store: Store = SqliteStore(store_dir / STORE_FILENAME) if store_dir is not None else MemoryStore()
    if store_dir is not None:
        revocations_path = revocations_path or store_dir / "revocations.jsonl"
        nonce_path = nonce_path or store_dir / "nonces.jsonl"
    # Durable, witnessed audit (B-5, ADR-020 proposed): the trail lives in its own store so that control state and
    # the evidence of what happened to it are never one file, and its head is anchored by a different principal in a
    # directory the audit process does not own (anchor_dir; a WORM bucket or replica in deployment) [Open: O-54].
    audit = AuditStore(
        store=SqliteStore(store_dir / AUDIT_STORE_FILENAME) if store_dir is not None else MemoryStore(),
        publisher=FileAnchorPublisher(anchor_dir) if anchor_dir is not None else None,
        anchor_every=anchor_every,
        max_anchor_lag=max_anchor_lag,
    )
    outbox = Outbox(control_store)
    alerts = AlertRouter.load(root / "observability" / "alerts.yaml")
    audit.set_alert_sink(alerts.raise_alert)
    metrics = MetricsRegistry()
    tracer = Tracer()
    # Every platform (live or a throwaway backtest) owns a private PlaneGuard: nothing an agent can call
    # touches the process-global guard or its deny evidence (MCP review OBJ-1).
    guard = PlaneGuard()

    def on_deny(ev: Any) -> None:
        principal = current_principal()
        alerts.raise_alert(
            "plane.deny",
            {
                "source": ev.source.value,
                "destination": ev.destination.value,
                "channel": ev.channel,
                "agent": principal.agent_id if principal else None,
                "account": principal.account_id if principal else None,
                "strategy": principal.strategy_id if principal else None,
            },
        )

    guard.alert_hook = on_deny

    # Every audit row is tenant-tagged and correlated (NFR-AUD-01, NFR-TEN-01). Hooks that only receive a payload
    # resolve the tenant from it (tenant id, account, intent) instead of stamping the default tenant constant.
    # (``tracker`` and ``platform`` are bound later in this scope; the closures look them up at call time.)
    def tenant_of(payload: dict[str, Any]) -> str:
        for key in ("tenant_id", "tenant"):
            if payload.get(key):
                return str(payload[key])
        nested = payload.get("payload")
        if isinstance(nested, dict) and nested.get("tenant_id"):
            return str(nested["tenant_id"])
        brk = payload.get("brk")
        account = payload.get("account_id") or payload.get("account") or (brk.get("account_id") if isinstance(brk, dict) else None)
        if account:
            return platform.tenant_for(str(account))
        intent_id = payload.get("intent_id")
        if intent_id and tracker.exists(str(intent_id)):
            return tracker.get(str(intent_id)).tenant_id
        return TENANT

    def corr_of(action: str, payload: dict[str, Any]) -> str:
        for key in ("correlation_id", "change_id", "activation_id", "token_id", "snapshot_id", "break_id", "cell_id"):
            if payload.get(key):
                return str(payload[key])
        if payload.get("intent_id") and tracker.exists(str(payload["intent_id"])):
            return tracker.get(str(payload["intent_id"])).correlation_id
        if payload.get("account_id"):
            return f"account:{payload['account_id']}"
        if payload.get("strategy_id"):
            return f"strategy:{payload['strategy_id']}@{payload.get('version', '')}"
        return f"{action}:{hash_of(payload)[:16]}"

    def audit5(action: str, correlation_id: str, tenant: str, account: str | None, payload: dict[str, Any]) -> None:
        audit.append(correlation_id=correlation_id, tenant=tenant, account=account, actor="platform", action=action, payload=payload)

    def audit3(action: str, correlation_id: str, payload: dict[str, Any]) -> None:
        audit.append(
            correlation_id=correlation_id, tenant=tenant_of(payload), account=None, actor="platform", action=action, payload=payload
        )

    def audit2(action: str, payload: dict[str, Any]) -> None:
        audit.append(
            correlation_id=corr_of(action, payload),
            tenant=tenant_of(payload),
            account=None,
            actor="platform",
            action=action,
            payload=payload,
        )

    tracker = IntentTracker(audit_hook=audit3)
    store, master, cal = BitemporalStore(), InstrumentMaster(), SessionCalendar()
    fx_store = FxStore()  # rates enter only here, and only from an operator/feed path (F-3)
    intent_queue = IntentQueue(
        tracker,
        outbox,
        on_reject=lambda c, p: metrics.inc("intent.schema_rejected"),
        instrument_valid=lambda iid, venue, ts: (inst := master.get(iid, as_of=ts)) is not None and inst.venue == venue,
        guard=guard,
    )
    accounts = AccountRegistry(
        audit_hook=lambda action, tenant, payload: audit.append(
            correlation_id=corr_of(action, payload),
            tenant=tenant,
            account=str(payload["account_id"]) if payload.get("account_id") else None,
            actor="identity_service",
            action=action,
            payload=payload,
        )
    )
    # Tenants of the simulation: the default one always; the second only when a test asks for it (TC-TEN).
    tenants: tuple[tuple[str, str, str], ...] = ((TENANT, ACCOUNT, CUSTOMER),)
    if second_tenant:
        tenants += ((TENANT_B, ACCOUNT_B, CUSTOMER_B),)
    ledger = Ledger()
    for tenant_id, account_id, customer_id in tenants:
        accounts.add_tenant(
            Tenant(tenant_id=tenant_id, name=f"Simulation tenant {tenant_id}", residency_region="sim", jurisdiction=JURISDICTION)
        )
        accounts.add_account(
            Account(
                account_id=account_id,
                tenant_id=tenant_id,
                customer_id=customer_id,
                broker=BROKER,
                jurisdiction=JURISDICTION,
                customer_type=CustomerType.RETAIL.value,
                base_currency="USD",
                mode=mode,
                authorised_strategies=(STRATEGY,),
                capital_envelope=Decimal("200000") if mode == AccountMode.BOUNDED_AUTONOMOUS else None,
            )
        )
        ledger.open_account(account_id, tenant_id, "USD", cash)
        for principal in SIM_PRINCIPALS.get(tenant_id, ()):
            accounts.bind_principal(principal, tenant_id)
    cal.add_venue(VENUE, time(0, 0), time(23, 59, 59))
    valid_from = datetime(2020, 1, 1, tzinfo=UTC)
    for iid, sector in ((INSTRUMENT, "SIM-TECH"), (INSTRUMENT_2, "SIM-TECH")):
        inst = InstrumentAttributes(
            instrument_id=iid,
            venue=VENUE,
            asset_class="EQUITY",
            currency="USD",
            sector=sector,
            country=JURISDICTION,
            tick_size=Decimal("0.01"),
            lot_size=Decimal("1"),
            tradable=True,
            shortable=False,
            valid_from=valid_from,
            identifiers={"issuer": f"ISSUER-{iid}"},
        )
        master.add(inst)
        ledger.register_instrument(inst)
    master.add(
        InstrumentAttributes(
            instrument_id="SIMDELISTED",
            venue=VENUE,
            asset_class="EQUITY",
            currency="USD",
            tick_size=Decimal("0.01"),
            lot_size=Decimal("1"),
            valid_from=valid_from,
            valid_to=datetime(2025, 1, 1, tzinfo=UTC),
        )
    )
    market = MarketDataService(store, master, cal, audit=audit2)
    feed = SimulatedFeed(
        start_prices={INSTRUMENT: Decimal("100"), INSTRUMENT_2: Decimal("50")}, entitlements={t: {"*"} for t, _a, _c in tenants}
    )
    broker = SimulatedBroker(known_instruments={INSTRUMENT: "EQUITY", INSTRUMENT_2: "EQUITY"}, venues=(VENUE,))
    broker.connect(VaultRef(path="vault://brokers/sim/creds", version=1), now=now)
    for _tenant_id, account_id, _customer_id in tenants:
        broker.fund(account_id, cash)
    leases = LeaseStore(control_store)
    # Control-plane command authorisation key: created here, handed only to the pipeline (sign) and the gateway
    # (verify). No MCP/AI component, tool, handler or BFF route ever receives it (IVA V-C2). A caller-supplied key is the
    # vault/KMS path of a deployment (O-53): it lets a restarted process verify commands its predecessor signed.
    # Asymmetric path (D-053, ADR-019 proposed), selected explicitly: the signer stays here, the gateway receives a
    # PublicKeyCommandVerifier over the trust set (rotation = add a key, re-point the signer, retire the old key).
    # The default stays the in-process HMAC authoriser so no existing dev/sim outcome changes.
    sign_command: Callable[[OrderCommand], OrderCommand]
    verify_command: Callable[[OrderCommand], str | None]
    if command_signer is not None:
        sign_command = command_signer.sign
        verify_command = command_signer.verifier(command_trust_set).verify
    else:
        authoriser = CommandAuthoriser(authorisation_key) if authorisation_key is not None else CommandAuthoriser.generate()
        sign_command = authoriser.sign
        verify_command = authoriser.verifier().verify
    decisions: dict[str, DecisionRecord] = {}

    def execution_permitted(command: OrderCommand, at: datetime) -> str | None:
        """Permission oracle consulted by the gateway at submission/retry time (IVA V-C1).

        Order of precedence: Kill Switch > halt/trading status > mode/target > decision provenance.
        """
        acct = accounts.get(command.account_id)
        ks = platform.killswitch
        if ks.blocks(
            tenant_id=command.tenant_id,
            account_id=command.account_id,
            strategy_id=command.strategy_id,
            instrument_id=command.instrument_id,
            asset_class=broker.known_instruments.get(command.instrument_id, ""),
            venue=command.venue,
        ):
            return "kill switch engaged for this scope"
        if acct.mode == AccountMode.HALTED or acct.trading_status != TradingStatus.ACTIVE:
            return f"account {acct.mode.value}/{acct.trading_status.value}"
        if acct.tenant_id != command.tenant_id:
            return "tenant mismatch"
        if TARGET_FOR_MODE.get(acct.mode) != command.execution_target:
            return f"execution target {command.execution_target.value} does not match account mode {acct.mode.value}"
        try:
            st = tracker.get(command.intent_id).state
        except KeyError:
            return "intent unknown to the control plane"
        if st not in (IntentState.AUTHORISED, IntentState.SUBMITTED, IntentState.ACKNOWLEDGED, IntentState.PARTIALLY_FILLED):
            return f"intent is {st.value}; a superseded or terminal intent cannot be (re)executed"
        dec = decisions.get(command.decision_id)
        if dec is None:
            return "decision unknown to the control plane"
        if dec.intent_id != command.intent_id or dec.policy_version != command.policy_version:
            return "decision does not belong to this intent/policy version"
        if dec.outcome == Outcome.APPROVED and command.approval_id is None:
            return None
        if dec.outcome == Outcome.REQUIRES_HUMAN_APPROVAL and command.approval_id is not None:
            item = approvals.get(command.approval_id)
            if item.status.value != "APPROVED" or item.decision.decision_id != command.decision_id:
                return "approval record does not authorise this decision"
            return None
        return f"decision outcome {dec.outcome.value} does not authorise execution"

    gateway = ExecutionGateway(
        adapters={BROKER: broker},
        lease_store=leases,
        audit=audit5,
        publish=outbox.publish,
        alert=lambda n, p: alerts.raise_alert(n, p),
        broker_for_account=lambda a: accounts.get(a).broker,
        guard=guard,
        verify_command=verify_command,
        execution_permitted=execution_permitted,
        store=control_store,
    )
    approvals = ApprovalQueue(audit_hook=audit3)
    jurisdictions = JurisdictionRegistry(audit_hook=audit2)
    retention = RetentionService(audit_hook=audit2)
    strategies = StrategyRegistry(audit=audit2)
    strategies.register(
        StrategyVersion(
            strategy_id=STRATEGY,
            version=STRATEGY_VERSION,
            owner_id="quant.fixture",
            model_id="rule-sma",
            model_version="0.1",
            params={"fast": 3, "slow": 8},
            declaration=StrategyDeclaration(strategy_id=STRATEGY),
            status=StrategyStatus.PROPOSED,
            docs="Simulation-only SMA crossover used to exercise the control envelope. Not a performance claim. See docs/STRATEGY_CARDS/strat-sma-xover.md.",
        )
    )
    policy = load_policy(policy_path or root / "services" / "risk" / "policies" / "sim-policy-v0.1.yaml")
    restricted = RestrictedLists(
        policy_version="lists-sim-v0.1", restricted_instruments=("SIMRESTRICTED",), restricted_venues=("SIMBANNED",)
    )
    customers = {customer_id: _default_customer(now, customer_id, tenant_id) for tenant_id, _account_id, customer_id in tenants}
    cell = jurisdictions.propose(
        country=JURISDICTION,
        customer_type=CustomerType.RETAIL,
        broker=BROKER,
        venue=VENUE,
        asset_class="EQUITY",
        feature=mode.value,
        required_disclosure_version=SIM_DISCLOSURE_VERSION,
    )
    if enable_cell:
        legal = Actor(actor_id="legal.fixture", role=Role.LEGAL_AGENT)
        comp = Actor(actor_id="compliance.fixture", role=Role.COMPLIANCE_AGENT)
        cell = jurisdictions.record_legal(cell, legal_record_ref=_sim_legal_record(now), actor=legal)
        jurisdictions.activate_flag(cell, actor=comp, now=now)
    revocations = RevocationList(revocations_path)
    # An agent identity is minted only for an account inside its tenant: the registry answers, the issuer refuses.
    issuer = IdentityIssuer(
        revocations=revocations,
        audit=audit2,
        nonce_path=nonce_path,
        scope_valid=lambda tenant_id, account_id: accounts.get_in_tenant(account_id, tenant_id) is not None,
    )
    registry = load_registry(registry_path or root / "mcp" / "policies" / "tool_registry.signed.json")
    allowlists = AllowlistStore.load_dir(root / "mcp" / "policies", revocations, tenants=(TENANT,), audit=audit2)
    if second_tenant:
        # The second tenant's grants are a test fixture; shipping them under mcp/policies is the MCP Security Agent's call.
        allowlists.add(AllowlistStore.load_file(root / "test" / "fixtures" / "policies" / f"allowlist.{TENANT_B}.yaml", revocations))
    egress = EgressPolicy.load(root / "mcp" / "policies" / "egress.yaml")
    runtime = ToolRuntime(
        registry=registry,
        issuer=issuer,
        allowlists=allowlists,
        audit=lambda action, corr, tenant, payload: audit.append(
            correlation_id=corr, tenant=tenant, account=None, actor=str(payload.get("actor", "mcp_runtime")), action=action, payload=payload
        ),
        alert=lambda n, p: alerts.raise_alert(n, p),
        revocations=revocations,
    )
    limits_mc = MakerChecker(cooling_period=timedelta(hours=1), require_different_line=True, audit_hook=audit2)
    slis = SliCatalog.load(root / "observability" / "slis.yaml")

    platform = SimPlatform(
        now=now,
        audit=audit,
        outbox=outbox,
        tracker=tracker,
        intent_queue=intent_queue,
        accounts=accounts,
        ledger=ledger,
        market=market,
        fx=fx_store,
        feed=feed,
        broker=broker,
        leases=leases,
        gateway=gateway,
        approvals=approvals,
        jurisdictions=jurisdictions,
        retention=retention,
        strategies=strategies,
        policy=policy,
        restricted=restricted,
        customers=customers,
        issuer=issuer,
        registry=registry,
        runtime=runtime,
        egress=egress,
        revocations=revocations,
        limits_mc=limits_mc,
        alerts=alerts,
        metrics=metrics,
        tracer=tracer,
        slis=slis,
        guard=guard,
        allowlists=allowlists,
        executor_id=executor_id,
        store=control_store,
    )

    # --- pipeline wiring -----------------------------------------------------------------------------------
    def elig_inputs(vi: ValidatedIntent, at: datetime) -> EligibilityInputs:
        acct = accounts.get(vi.intent.account_id)
        return EligibilityInputs(
            customer=customers.get(acct.customer_id),
            instrument=master.get(vi.intent.instrument_id, as_of=vi.intent.market_ts),
            cells=jurisdictions.cells(),
            restricted=platform.restricted,
            broker=acct.broker,
            feature=(acct.enabled_feature or acct.mode).value,
        )

    def on_authorised(vi: ValidatedIntent, decision: Any) -> None:
        i = vi.intent
        ledger.record_intent_hash(i.account_id, vi.intent_hash)
        ledger.record_order_ts(
            i.account_id, platform.now, f"{i.instrument_id}|{i.side.value}|{i.order_type.value}|{i.quantity}|{i.limit_price}"
        )

    def audit_pipeline(action: str, correlation_id: str, tenant: str, account: str | None, payload: dict[str, Any]) -> None:
        if action in ("risk.decided.v1", "risk.redecided.v1"):
            rec = DecisionRecord.model_validate({k: v for k, v in payload.items() if k != "approval_id"})
            decisions[rec.decision_id] = rec
        audit5(action, correlation_id, tenant, account, payload)

    def strategy_owner(strategy_id: str, version: str) -> str | None:
        try:
            return strategies.get(strategy_id, version).owner_id
        except KeyError:
            return None

    platform.pipeline = TradePipeline(
        tracker=tracker,
        outbox=outbox,
        audit=audit_pipeline,
        sign_command=sign_command,
        strategy_owner=strategy_owner,
        eligibility_inputs=elig_inputs,
        account_snapshot=lambda vi, at: platform.account_snapshot(vi.intent.account_id, at, vi.correlation_id),
        market_snapshot=lambda vi, at: platform.market_snapshot(vi.intent.instrument_id, at),
        policy=lambda: platform.policy,
        fx_inputs=lambda vi, at: (platform.fx.latest(as_of=at, knowledge_ts=at), platform.fx_max_age_s),
        approvals=approvals,
        gateway=gateway,
        leases=leases,
        executor_id=platform.executor_id,
        on_authorised=on_authorised,
        inbox=Inbox(control_store, table="oms.pipeline_inbox", model=PipelineResult),
        alert=lambda n, pl: alerts.raise_alert(n, pl),
    )

    # --- kill switch wiring (P4) ----------------------------------------------------------------------------
    def cancel_open(level: KillSwitchLevel, target: str) -> list[str]:
        """Cancel exactly the scope's open orders; preempt only the leases of accounts inside the scope."""
        filters: dict[str, Any] = {}
        if level == KillSwitchLevel.ACCOUNT:
            filters["account_id"] = target
        elif level == KillSwitchLevel.TENANT:
            filters["tenant_id"] = target
        elif level == KillSwitchLevel.STRATEGY:
            filters["strategy_id"] = target
        elif level == KillSwitchLevel.ASSET:
            filters["instrument_id"] = target
        elif level == KillSwitchLevel.VENUE:
            filters["venue"] = target
        affected = set(gateway.affected_accounts(**filters))
        if level == KillSwitchLevel.ACCOUNT:
            affected.add(target)
        if level == KillSwitchLevel.TENANT:
            affected |= {a.account_id for a in accounts.accounts(target)}
        if level == KillSwitchLevel.PLATFORM:
            affected |= {a.account_id for a in accounts.accounts()}
        tokens = {acct_id: leases.preempt(acct_id, "killswitch", now=platform.now).fencing_token for acct_id in sorted(affected)}
        with enter(Plane.CONTROL):
            cancelled = gateway.cancel_all(fencing_tokens=tokens, now=platform.now, reason=f"killswitch {level.value}:{target}", **filters)
        for acct_id in tokens:
            leases.release(acct_id, "killswitch")  # the old executor token stays stale; a fresh lease is needed to resume
        return cancelled

    def emergency_policy(level: KillSwitchLevel, target: str) -> tuple[EmergencyPolicy, str | None]:
        if level == KillSwitchLevel.ACCOUNT:
            a = accounts.get(target)
            return a.emergency_policy, a.liquidation_policy_ref
        return EmergencyPolicy.CANCEL_ONLY, None

    def evidence(level: KillSwitchLevel, target: str) -> dict[str, Any]:
        return {
            "audit_head": audit.head_hash(),
            "open_orders": [o.order_id for a in accounts.accounts() for o in gateway.open_orders(a.account_id)],
            "positions": {a.account_id: [p.model_dump(mode="json") for p in ledger.positions(a.account_id)] for a in accounts.accounts()},
            "at": platform.now.isoformat(),
        }

    def halt_account(account_id: str, reason: str) -> None:
        accounts.halt(account_id, system_actor("killswitch"), reason=reason, now=platform.now)

    def ks_tenant(payload: dict[str, Any]) -> str:
        """ACCOUNT-level rows belong to the account's tenant, TENANT-level rows to the target; other levels are platform-wide."""
        level, target = str(payload.get("level", "")), str(payload.get("target") or payload.get("target_id") or "")
        if level == KillSwitchLevel.TENANT.value and target:
            return target
        if level == KillSwitchLevel.ACCOUNT.value and target:
            return platform.tenant_for(target)
        return tenant_of(payload)

    def ks_audit(action: str, corr: str, payload: dict[str, Any]) -> None:
        if "level" not in payload:
            try:  # deactivation rows carry the activation id as correlation: resolve level/target from the activation
                act = platform.killswitch.get(corr)
                payload_scope: dict[str, Any] = {**payload, "level": act.level.value, "target": act.target_id}
            except (KeyError, AttributeError):
                payload_scope = payload
        else:
            payload_scope = payload
        tenant = ks_tenant(payload_scope)
        audit.append(correlation_id=corr, tenant=tenant, account=None, actor="killswitch_service", action=action, payload=payload)
        if action in ("killswitch.activated", "killswitch.deactivated"):
            outbox.publish(
                make_event(
                    f"{action}.v1",
                    correlation_id=corr,
                    tenant=tenant,
                    producer="killswitch_service",
                    payload={k: v for k, v in payload.items() if k != "evidence_snapshot"},
                    emitted_ts=platform.now,
                )
            )

    platform.killswitch = KillSwitchService(
        approved_liquidation_policies=policy.approved_liquidation_policies,
        store=control_store,
        hooks=KillSwitchHooks(
            cancel_open_orders=cancel_open,
            revoke_agent_identities=lambda level, target: issuer.revoke_scope(level.value, target, now=platform.now),
            emergency_policy_for=emergency_policy,
            evidence_snapshot=evidence,
            notify=lambda subject, payload: platform.notifications.append((subject, payload)),
            audit=ks_audit,
            alert=lambda n, p: alerts.raise_alert(n, p),
            halt_account=halt_account,
            observe=lambda name, value: metrics.observe(name, value),
        ),
    )

    # --- reconciliation break handling (P6) -------------------------------------------------------------------
    def on_break(brk: Any) -> None:
        if brk.severity == BreakSeverity.S1:
            alerts.raise_alert("execution.duplicate_order", {"account": brk.account_id, "break_id": brk.break_id})
        else:
            alerts.raise_alert("reconciliation.break", {"account": brk.account_id, "break_id": brk.break_id})

    platform.tickets = BreakTicketService(on_break=on_break, audit=audit3)

    # --- alert auto-actions with payload contracts (MCP review OBJ-3) ------------------------------------------
    ops = Actor(actor_id="risk-officer.system", role=Role.RISK_OFFICER)

    def killswitch_from_alert(level: KillSwitchLevel, target_key: str | None) -> Any:
        def run(a: Alert) -> None:
            target = str(a.payload[target_key]) if target_key else "*"
            if not any(x.level == level and x.target_id == target for x in platform.killswitch.active()):
                platform.killswitch.activate(level, target, reason=a.name, actor=ops, now=platform.now)

        return run

    def revoke_grant_for_scope(a: Alert) -> None:
        # the runtime's alert payload names the tenant of the offending identity; only that tenant's grant is revoked
        tenant = str(a.payload.get("tenant") or platform.tenant_for(str(a.payload["account"])))
        allowlist = allowlists.get(tenant)
        if allowlist is None:
            return
        allowlist.revoke_grant(
            account_id=str(a.payload["account"]),
            strategy_id=str(a.payload["strategy"]),
            tool=str(a.payload["tool"]),
            by="alert_router",
            at=platform.now,
            reason=a.name,
        )

    alerts.on(
        "account_to_supervised",
        lambda a: accounts.suspend_autonomy(str(a.payload["account"]), reason=a.name, by="alert_router"),
        required=("account",),
    )
    alerts.on(
        "autonomy_to_supervised",
        lambda a: accounts.suspend_autonomy(str(a.payload.get("account", ACCOUNT)), reason=a.name, by="alert_router"),
    )
    alerts.on("killswitch_account", killswitch_from_alert(KillSwitchLevel.ACCOUNT, "account"), required=("account",))
    alerts.on("killswitch_platform", killswitch_from_alert(KillSwitchLevel.PLATFORM, None))
    alerts.on(
        "revoke_agent_identity",
        lambda a: issuer.revoke_agent(str(a.payload["agent"]), by="alert_router", now=platform.now, reason=a.name),
        required=("agent",),
    )
    alerts.on("revoke_tool_for_scope", revoke_grant_for_scope, required=("tool", "account", "strategy"))
    alerts.on("cancel_only", lambda a: accounts.suspend_autonomy(str(a.payload.get("account", ACCOUNT)), reason=a.name, by="alert_router"))
    alerts.on(
        "suspend_signals",
        lambda a: issuer.revoke_scope("STRATEGY", str(a.payload["strategy"]), by="alert_router", now=platform.now),
        required=("strategy",),
    )

    # --- MCP tools ---------------------------------------------------------------------------------------------
    def run_sim(args: dict[str, Any], principal: Principal, at: datetime) -> dict[str, Any]:
        # A throwaway platform with its own guard, alerts and audit: nothing here can reach the live platform.
        report = run_sim_backtest(instrument_id=str(args["instrument_id"]), cost_factor=Decimal(str(args.get("cost_factor", "1"))), bars=60)
        return {
            "data_snapshot_id": report.data_snapshot_id,
            "metrics": report.metrics.model_dump(mode="json"),
            "disclaimer": report.disclaimer,
        }

    handlers = build_tools(
        store=store,
        account_state=lambda acct_id, at: platform.account_snapshot(acct_id, at),
        registry=strategies,
        intent_queue=intent_queue,
        run_simulation=run_sim,
        depth_entitled=lambda t: t in feed.depth_entitled,
        instrument_entitled=lambda t, iid: feed.entitled(t, iid),
    )
    for name, handler in handlers.items():
        runtime.register_handler(name, handler)

    if bars:
        # Last bar at now-1s, ingested 200 ms later: fresh at decision time ``now``.
        platform.ingest_bars(INSTRUMENT, start=now - timedelta(seconds=1) - feed.step * bars, count=bars + 1)
        platform.ingest_bars(INSTRUMENT_2, start=now - timedelta(seconds=1) - feed.step * bars, count=bars + 1)
    return platform


def run_sim_backtest(
    *,
    instrument_id: str = INSTRUMENT,
    bars: int = 60,
    cost_factor: Decimal = Decimal("1"),
    start: datetime = BACKTEST_START,
    strategy: SmaCrossoverStrategy | None = None,
) -> BacktestReport:
    """ADR-008: a fresh sim platform in BACKTEST mode runs the production pipeline bar by bar.

    Costs are charged by the simulated broker inside the pipeline (commission + slippage as fee_bps, spread
    in the fill price), so backtest and paper share one code path. Financing/borrow [Open: C7 O-21].
    """
    p = build_sim_platform(now=start, mode=AccountMode.BACKTEST, bars=0)
    strat = strategy or SmaCrossoverStrategy()
    cost = CostModel().scaled(cost_factor)
    p.broker.spread_bps = cost.spread_bps
    p.broker.fee_bps = cost.commission_bps + cost.slippage_bps
    p.ingest_bars(instrument_id, start=start, count=bars)
    timestamps = p.market.store.market_timestamps(instrument_id)
    snapshot_id = p.market.store.snapshot_id_for_range(instrument_id, timestamps[0], timestamps[-1])
    trade_pnls: list[Decimal] = []

    def decision_time(ts: datetime) -> datetime:
        """Decisions happen one second after the bar's market_ts (after ingestion), never before."""
        return ts + timedelta(seconds=1)

    def history(iid: str, ts: datetime) -> tuple[MarketSnapshot, ...]:
        p.now = decision_time(ts)
        return p.market.store.series(iid, start=timestamps[0], end=ts, knowledge_ts=p.now)

    def submit_and_process(intent: TradeIntent, ts: datetime) -> dict[str, Any]:
        p.now = decision_time(ts)
        result = p.run_intent(intent, submitted_by="backtest", now=p.now)
        fills = [
            {"quantity": str(f.quantity), "price": str(f.price), "fee": str(f.fee)} for f in (result.order.fills if result.order else ())
        ]
        return {
            "outcome": result.decision.outcome.value if result.decision else result.eligibility.outcome.value,
            "reason_codes": list(result.decision.reason_codes) if result.decision else list(result.eligibility.reason_codes),
            "fills": fills,
        }

    def settle(ts: datetime) -> tuple[Decimal, ...]:
        p.now = decision_time(ts)
        snap = p.market.store.latest(instrument_id, as_of=ts, knowledge_ts=p.now)
        if snap is not None:
            p.ledger.mark(instrument_id, snap.last_price)
        p.settle(p.now)
        pos = p.ledger.book(ACCOUNT).positions.get(instrument_id)
        realized = pos.realized_pnl if pos else ZERO
        delta = realized - sum(trade_pnls, ZERO)
        if delta != ZERO:
            trade_pnls.append(delta)
            return (delta,)
        return ()

    runner = BacktestRunner(
        history=history,
        position_qty=lambda iid: p.ledger.book(ACCOUNT).positions.get(iid, PositionState(instrument_id=iid)).quantity,
        nav=lambda: p.ledger.nav(ACCOUNT),
        gross=lambda: sum((abs(x.market_value) for x in p.ledger.positions(ACCOUNT)), ZERO),
        submit_and_process=submit_and_process,
        settle_bar=settle,
        cost_model=cost,
    )
    sv = p.strategies.get(STRATEGY, STRATEGY_VERSION)
    return runner.run(
        strategy=strat,
        intent_builder=lambda sig, snap, qty: intent_from_signal(sig, snap, account_id=ACCOUNT, position_qty=qty),
        instrument_id=instrument_id,
        bar_timestamps=timestamps,
        data_snapshot_id=snapshot_id,
        hypothesis_hash=sv.pre_registration.hypothesis_hash if sv.pre_registration else None,
    )
