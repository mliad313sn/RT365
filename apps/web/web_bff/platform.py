"""Composition root for the dev/sim environment [Committee; ADR-010].

Wires every bounded context in one process with in-memory stores. It exists so that the
control envelope can be exercised end to end (tests, BFF, backtests, synthetic probes)
before any external dependency exists. Nothing here enables a market, a strategy or autonomy:
the fixture tenant/account/jurisdiction are explicitly simulated.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime, time, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any

from approval_service.queue import ApprovalQueue, ApprovalRecord
from audit_service.store import AuditStore
from backtest_engine.costs import CostModel
from backtest_engine.runner import BacktestReport, BacktestRunner
from broker_adapters.simulated import SimulatedBroker
from compliance_engine.jurisdiction import JurisdictionRegistry
from compliance_engine.retention import RetentionService
from compliance_engine.surveillance import StrategyDeclaration
from data_providers.simulated import SimulatedFeed
from execution_gateway.gateway import ExecutionGateway
from execution_gateway.lease import LeaseStore
from identity_service.accounts import Account, AccountRegistry, Tenant
from identity_service.makerchecker import MakerChecker
from killswitch_service.service import KillSwitchHooks, KillSwitchLevel, KillSwitchService
from market_data.calendar import SessionCalendar
from market_data.instruments import InstrumentMaster
from market_data.service import MarketDataService
from market_data.store import BitemporalStore
from mcp_servers.allowlist import TenantAllowlist
from mcp_servers.egress import EgressPolicy
from mcp_servers.identity import AgentIdentity, IdentityIssuer
from mcp_servers.registry import ToolRegistry, load_registry
from mcp_servers.runtime import ToolRuntime
from mcp_servers.tools import build_tools
from oms.intent_queue import IntentQueue
from oms.lifecycle import IntentTracker
from oms.outbox import Inbox, Outbox
from oms.pipeline import EligibilityInputs, PipelineResult, TradePipeline
from portfolio_service.ledger import Ledger
from reconciliation_service.reconcile import BreakSeverity, ReconciliationResult, reconcile
from reconciliation_service.tickets import BreakTicketService
from risk_engine.monitors import RuntimeMetrics, evaluate_runtime
from risk_engine.policy import RiskPolicy, load_policy
from rtcore.lines import Actor, Role, system_actor
from rtcore.money import ZERO
from rtcore.planes import GUARD, Plane, PlaneGuard, enter
from rtcore.schemas.account import AccountMode, AccountSnapshot, EmergencyPolicy
from rtcore.schemas.compliance import CustomerProfile, CustomerType, RestrictedLists
from rtcore.schemas.intent import TradeIntent, ValidatedIntent
from rtcore.schemas.market import InstrumentAttributes, MarketSnapshot
from rtcore.schemas.order import OrderRecord
from rtobs.alerts import AlertRouter
from rtobs.metrics import MetricsRegistry
from rtobs.slis import SliCatalog
from rtobs.tracing import Tracer
from strategy_service.registry import StrategyRegistry, StrategyVersion
from strategy_service.signals import SmaCrossoverStrategy, intent_from_signal

REPO_ROOT = Path(__file__).resolve().parents[3]
TENANT = "tenant-sim"
ACCOUNT = "acct-sim-001"
CUSTOMER = "cust-sim-001"
INSTRUMENT = "SIMEQ1"
INSTRUMENT_2 = "SIMEQ2"
VENUE = "SIMX"
BROKER = "sim-broker"
STRATEGY = "strat-sma-xover"
JURISDICTION = "ZZ"  # ISO 3166 user-assigned code: explicitly not a real jurisdiction [Open: O-11]
BASE_TIME = datetime(2026, 9, 7, 14, 0, tzinfo=UTC)  # a Monday, session open


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
    feed: SimulatedFeed
    broker: SimulatedBroker
    leases: LeaseStore
    gateway: ExecutionGateway
    approvals: ApprovalQueue
    killswitch: KillSwitchService
    jurisdictions: JurisdictionRegistry
    retention: RetentionService
    strategies: StrategyRegistry
    policy: RiskPolicy | None
    restricted: RestrictedLists
    customers: dict[str, CustomerProfile]
    pipeline: TradePipeline = field(init=False)
    issuer: IdentityIssuer
    registry: ToolRegistry
    runtime: ToolRuntime
    egress: EgressPolicy
    tickets: BreakTicketService
    limits_mc: MakerChecker
    alerts: AlertRouter
    metrics: MetricsRegistry
    tracer: Tracer
    slis: SliCatalog
    guard: PlaneGuard
    notifications: list[tuple[str, dict[str, Any]]] = field(default_factory=list)
    applied_fill_refs: set[str] = field(default_factory=set)
    executor_id: str = "executor-a"

    # --- clock ----------------------------------------------------------------------------------------
    def advance(self, seconds: float) -> datetime:
        self.now = self.now + timedelta(seconds=seconds)
        return self.now

    # --- snapshot providers --------------------------------------------------------------------------------
    def account_snapshot(self, account_id: str, now: datetime | None = None) -> AccountSnapshot | None:
        now = now or self.now
        try:
            acct = self.accounts.get(account_id)
        except KeyError:
            return None
        from rtcore.schemas.account import OpenOrder

        open_orders = tuple(
            OpenOrder(
                order_id=o.order_id,
                instrument_id=o.command.instrument_id,
                side=o.command.side,
                quantity=o.remaining_quantity,
                notional=o.remaining_quantity * (o.command.limit_price or self._last_price(o.command.instrument_id, now)),
                submitted_at=o.updated_at,
            )
            for o in self.gateway.open_orders(account_id)
        )
        flags = self.killswitch.flags_for(tenant_id=acct.tenant_id, account_id=account_id)
        return self.ledger.snapshot(
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
        )

    def _last_price(self, instrument_id: str, now: datetime) -> Decimal:
        snap = self.market.store.latest(instrument_id, as_of=now, knowledge_ts=now)
        return snap.last_price if snap else Decimal("100")

    def market_snapshot(self, instrument_id: str, now: datetime | None = None) -> MarketSnapshot | None:
        return self.market.for_decision(instrument_id, now=now or self.now)

    # --- data ingestion -----------------------------------------------------------------------------------
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
    def make_intent(self, **overrides: Any) -> dict[str, Any]:
        from uuid import uuid4

        snap = self.market_snapshot(INSTRUMENT)
        price = snap.last_price if snap else Decimal("100")
        base: dict[str, Any] = {
            "intent_id": str(uuid4()),
            "strategy_id": STRATEGY,
            "strategy_version": "0.1",
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
    ) -> ValidatedIntent:
        with enter(plane):
            return self.intent_queue.submit(raw, tenant_id=TENANT, submitted_by=submitted_by, now=now or self.now)

    def run_intent(
        self, raw: dict[str, Any] | TradeIntent, *, submitted_by: str = "agent:sim", now: datetime | None = None
    ) -> PipelineResult:
        now = now or self.now
        vi = self.submit_intent(raw, submitted_by=submitted_by, now=now)
        self.intent_queue.pop()
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
        for order in self.gateway.orders():
            for f in order.fills:
                if f.broker_ref in self.applied_fill_refs:
                    continue
                self.applied_fill_refs.add(f.broker_ref)
                self.ledger.apply_fill(order.command.account_id, order.command.instrument_id, order.command.side, f.quantity, f.price)

    # --- reconciliation (P6) ---------------------------------------------------------------------------------------
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
        self.audit.append(
            correlation_id=f"recon:{account_id}:{now.isoformat()}",
            tenant=TENANT,
            account=account_id,
            actor="reconciliation_service",
            action="reconciliation.completed.v1",
            payload={
                "account_id": account_id,
                "as_of": now.isoformat(),
                "positions_compared": result.positions_compared,
                "orders_compared": result.orders_compared,
                "break_count": len(result.breaks),
            },
        )
        for brk in result.breaks:
            self.tickets.open(brk, now=now)
        return result

    # --- runtime monitors (P4 triggers) -------------------------------------------------------------------------------
    def evaluate_monitors(self, account_id: str, metrics: RuntimeMetrics, now: datetime | None = None) -> tuple[str, ...]:
        now = now or self.now
        snap = self.account_snapshot(account_id, now)
        if snap is None or self.policy is None:
            return ()
        events = evaluate_runtime(snap, self.policy, metrics, now)
        activated = []
        monitor = Actor(
            actor_id="runtime-monitor", role=Role.RUNTIME_MONITOR, kind=__import__("rtcore.lines", fromlist=["ActorKind"]).ActorKind.SYSTEM
        )
        for ev in events:
            self.audit.append(
                correlation_id=f"halt:{account_id}:{ev.reason_code}",
                tenant=TENANT,
                account=account_id,
                actor="runtime_monitor",
                action="risk.halt.v1",
                payload=ev.model_dump(mode="json"),
            )
            level = KillSwitchLevel(ev.level) if ev.level in KillSwitchLevel.__members__ else KillSwitchLevel.ACCOUNT
            target = ev.target_id if ev.target_id != "*" else (account_id if level == KillSwitchLevel.ACCOUNT else "*")
            if not any(a.level == level and a.target_id == target for a in self.killswitch.active()):
                self.killswitch.activate(
                    level, target, reason=f"runtime monitor {ev.reason_code}: {ev.value} vs {ev.threshold}", actor=monitor, now=now
                )
            activated.append(ev.reason_code)
        return tuple(activated)

    # --- MCP helpers ------------------------------------------------------------------------------------------
    def issue_agent(
        self,
        *,
        agent_id: str = "agent-sim-1",
        strategy_id: str = STRATEGY,
        account_id: str = ACCOUNT,
        now: datetime | None = None,
        ttl: timedelta | None = None,
    ) -> AgentIdentity:
        return self.issuer.issue(
            agent_id=agent_id,
            tenant_id=TENANT,
            account_id=account_id,
            strategy_id=strategy_id,
            model_id="rule-sma",
            model_version="0.1",
            prompt_id="P-STRAT-SIGNAL",
            prompt_version="0.1",
            now=now or self.now,
            ttl=ttl,
        )

    def tool_call(self, ident: AgentIdentity, tool: str, args: dict[str, Any], *, now: datetime | None = None) -> Any:
        sig = self.issuer.sign_call(ident, tool, args)
        with enter(Plane.ANALYTICS):
            return self.runtime.call(token_id=ident.token_id, signature=sig, tool=tool, args=args, now=now or self.now)

    # --- synthetic probe [C9] -------------------------------------------------------------------------------------
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


def _default_customer() -> CustomerProfile:
    return CustomerProfile(
        customer_id=CUSTOMER,
        tenant_id=TENANT,
        customer_type=CustomerType.RETAIL,
        jurisdiction=JURISDICTION,
        product_permissions=("EQUITY", "ETF"),
        appropriateness_assessed=False,
        complex_products_allowed=False,
        short_selling_allowed=False,
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
) -> SimPlatform:
    audit = AuditStore()
    outbox = Outbox()
    alerts = AlertRouter.load(REPO_ROOT / "observability" / "alerts.yaml")
    metrics = MetricsRegistry()
    tracer = Tracer()
    guard = GUARD
    guard.denies.clear()
    guard.alert_hook = lambda ev: alerts.raise_alert(
        "plane.deny", {"source": ev.source.value, "destination": ev.destination.value, "channel": ev.channel}
    )

    def audit5(action: str, correlation_id: str, tenant: str, account: str | None, payload: dict[str, Any]) -> None:
        audit.append(correlation_id=correlation_id, tenant=tenant, account=account, actor="platform", action=action, payload=payload)

    def audit3(action: str, correlation_id: str, payload: dict[str, Any]) -> None:
        audit.append(correlation_id=correlation_id, tenant=TENANT, account=None, actor="platform", action=action, payload=payload)

    def audit2(action: str, payload: dict[str, Any]) -> None:
        audit.append(
            correlation_id=str(payload.get("correlation_id", "-")),
            tenant=TENANT,
            account=None,
            actor="platform",
            action=action,
            payload=payload,
        )

    tracker = IntentTracker(audit_hook=audit3)
    store, master, cal = BitemporalStore(), InstrumentMaster(), SessionCalendar()
    intent_queue = IntentQueue(
        tracker,
        outbox,
        on_reject=lambda c, p: metrics.inc("intent.schema_rejected"),
        instrument_valid=lambda iid, venue, ts: (inst := master.get(iid, as_of=ts)) is not None and inst.venue == venue,
    )
    accounts = AccountRegistry(
        audit_hook=lambda action, tenant, payload: audit.append(
            correlation_id="-",
            tenant=tenant,
            account=str(payload.get("account_id")),
            actor="identity_service",
            action=action,
            payload=payload,
        )
    )
    accounts.add_tenant(Tenant(tenant_id=TENANT, name="Simulation tenant", residency_region="sim", jurisdiction=JURISDICTION))
    accounts.add_account(
        Account(
            account_id=ACCOUNT,
            tenant_id=TENANT,
            customer_id=CUSTOMER,
            broker=BROKER,
            jurisdiction=JURISDICTION,
            customer_type=CustomerType.RETAIL.value,
            base_currency="USD",
            mode=mode,
            authorised_strategies=(STRATEGY,),
            capital_envelope=Decimal("200000") if mode == AccountMode.BOUNDED_AUTONOMOUS else None,
        )
    )

    ledger = Ledger()
    ledger.open_account(ACCOUNT, TENANT, "USD", cash)
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
    delisted = InstrumentAttributes(
        instrument_id="SIMDELISTED",
        venue=VENUE,
        asset_class="EQUITY",
        currency="USD",
        tick_size=Decimal("0.01"),
        lot_size=Decimal("1"),
        valid_from=valid_from,
        valid_to=datetime(2025, 1, 1, tzinfo=UTC),
    )
    master.add(delisted)
    market = MarketDataService(store, master, cal, audit=audit2)
    feed = SimulatedFeed(start_prices={INSTRUMENT: Decimal("100"), INSTRUMENT_2: Decimal("50")}, entitlements={TENANT: {"*"}})
    broker = SimulatedBroker(known_instruments={INSTRUMENT: "EQUITY", INSTRUMENT_2: "EQUITY"}, venues=(VENUE,))
    from broker_adapters.base import VaultRef

    broker.connect(VaultRef(path="vault://brokers/sim/creds", version=1), now=now)
    broker.fund(ACCOUNT, cash)
    leases = LeaseStore()
    gateway = ExecutionGateway(
        adapters={BROKER: broker},
        lease_store=leases,
        audit=audit5,
        publish=outbox.publish,
        alert=lambda n, p: alerts.raise_alert(n, p),
        broker_for_account=lambda a: accounts.get(a).broker,
    )
    approvals = ApprovalQueue(audit_hook=audit3)
    jurisdictions = JurisdictionRegistry(audit_hook=audit2)
    retention = RetentionService(audit_hook=audit2)
    strategies = StrategyRegistry(audit=audit2)
    strategies.register(
        StrategyVersion(
            strategy_id=STRATEGY,
            version="0.1",
            owner_id="quant.fixture",
            model_id="rule-sma",
            model_version="0.1",
            params={"fast": 3, "slow": 8},
            declaration=StrategyDeclaration(strategy_id=STRATEGY),
            status=__import__("strategy_service.registry", fromlist=["StrategyStatus"]).StrategyStatus.PROPOSED,
            docs="Simulation-only SMA crossover used to exercise the control envelope. Not a performance claim.",
        )
    )
    policy = load_policy(policy_path or REPO_ROOT / "services" / "risk" / "policies" / "sim-policy-v0.1.yaml")
    restricted = RestrictedLists(
        policy_version="lists-sim-v0.1", restricted_instruments=("SIMRESTRICTED",), restricted_venues=("SIMBANNED",)
    )
    customers = {CUSTOMER: _default_customer()}
    cell = jurisdictions.propose(
        country=JURISDICTION, customer_type=CustomerType.RETAIL, broker=BROKER, venue=VENUE, asset_class="EQUITY", feature=mode.value
    )
    if enable_cell:
        legal = Actor(actor_id="legal.fixture", role=Role.LEGAL_AGENT)
        comp = Actor(actor_id="compliance.fixture", role=Role.COMPLIANCE_AGENT)
        cell = jurisdictions.record_legal(
            cell, legal_record_ref="SIM-LEGAL-FIXTURE-001 [Committee: simulated cell, not a legal opinion]", actor=legal
        )
        jurisdictions.activate_flag(cell, actor=comp, now=now)
    issuer = IdentityIssuer()
    registry = load_registry(registry_path or REPO_ROOT / "mcp" / "policies" / "tool_registry.signed.json")
    allowlists = {TENANT: TenantAllowlist.load(REPO_ROOT / "mcp" / "policies" / "allowlist.tenant-sim.yaml")}
    egress = EgressPolicy.load(REPO_ROOT / "mcp" / "policies" / "egress.yaml")
    runtime = ToolRuntime(
        registry=registry,
        issuer=issuer,
        allowlists=allowlists,
        audit=lambda action, corr, tenant, payload: audit.append(
            correlation_id=corr, tenant=tenant, account=None, actor="mcp_runtime", action=action, payload=payload
        ),
        alert=lambda n, p: alerts.raise_alert(n, p),
    )
    tickets = BreakTicketService(on_break=lambda brk: None, audit=audit3)
    limits_mc = MakerChecker(cooling_period=timedelta(hours=1), require_different_line=True, audit_hook=audit2)
    slis = SliCatalog.load(REPO_ROOT / "observability" / "slis.yaml")

    platform = SimPlatform(
        now=now,
        audit=audit,
        outbox=outbox,
        tracker=tracker,
        intent_queue=intent_queue,
        accounts=accounts,
        ledger=ledger,
        market=market,
        feed=feed,
        broker=broker,
        leases=leases,
        gateway=gateway,
        approvals=approvals,
        killswitch=KillSwitchService(),
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
        tickets=tickets,
        limits_mc=limits_mc,
        alerts=alerts,
        metrics=metrics,
        tracer=tracer,
        slis=slis,
        guard=guard,
    )

    # --- pipeline wiring -----------------------------------------------------------------------------------------
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
        ledger.record_intent_hash(vi.intent.account_id, vi.intent_hash)
        ledger.record_order_ts(vi.intent.account_id, platform.now)

    platform.pipeline = TradePipeline(
        tracker=tracker,
        outbox=outbox,
        audit=audit5,
        eligibility_inputs=elig_inputs,
        account_snapshot=lambda vi, at: platform.account_snapshot(vi.intent.account_id, at),
        market_snapshot=lambda vi, at: platform.market_snapshot(vi.intent.instrument_id, at),
        policy=lambda: platform.policy,
        approvals=approvals,
        gateway=gateway,
        leases=leases,
        executor_id=platform.executor_id,
        on_authorised=on_authorised,
        inbox=Inbox(),
        alert=lambda n, pl: alerts.raise_alert(n, pl),
    )

    # --- kill switch wiring (P4) ----------------------------------------------------------------------------------
    def cancel_open(level: KillSwitchLevel, target: str) -> list[str]:
        tokens: dict[str, int] = {}
        for acct in accounts.accounts():
            if level == KillSwitchLevel.ACCOUNT and acct.account_id != target:
                continue
            if level == KillSwitchLevel.TENANT and acct.tenant_id != target:
                continue
            tokens[acct.account_id] = leases.preempt(acct.account_id, "killswitch", now=platform.now).fencing_token
        kw: dict[str, Any] = {"fencing_tokens": tokens, "now": platform.now, "reason": f"killswitch {level.value}:{target}"}
        if level == KillSwitchLevel.ACCOUNT:
            kw["account_id"] = target
        elif level == KillSwitchLevel.TENANT:
            kw["tenant_id"] = target
        elif level == KillSwitchLevel.ASSET:
            kw["instrument_id"] = target
        elif level == KillSwitchLevel.VENUE:
            kw["venue"] = target
        with enter(Plane.CONTROL):
            cancelled = gateway.cancel_all(**kw)
        for acct_id in tokens:
            leases.release(acct_id, "killswitch")  # old executor token stays stale; a fresh lease is needed to resume
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

    platform.killswitch = KillSwitchService(
        hooks=KillSwitchHooks(
            cancel_open_orders=cancel_open,
            revoke_agent_identities=lambda level, target: issuer.revoke_scope(level.value, target),
            emergency_policy_for=emergency_policy,
            evidence_snapshot=evidence,
            notify=lambda subject, payload: platform.notifications.append((subject, payload)),
            audit=lambda action, corr, payload: audit.append(
                correlation_id=corr, tenant=TENANT, account=None, actor="killswitch_service", action=action, payload=payload
            ),
            alert=lambda n, p: alerts.raise_alert(n, p),
            halt_account=halt_account,
        )
    )

    # --- reconciliation break handling (P6) -----------------------------------------------------------------------
    def on_break(brk: Any) -> None:
        if brk.severity == BreakSeverity.S1:
            alerts.raise_alert("execution.duplicate_order", {"account": brk.account_id, "break_id": brk.break_id})
        else:
            alerts.raise_alert("reconciliation.break", {"account": brk.account_id, "break_id": brk.break_id})

    platform.tickets = BreakTicketService(on_break=on_break, audit=audit3)
    ops = Actor(actor_id="risk-officer.system", role=Role.RISK_OFFICER)
    alerts.on(
        "account_to_supervised",
        lambda a: (
            accounts.suspend_autonomy(str(a.payload["account"]), reason=a.name, by="alert_router") if a.payload.get("account") else None
        ),
    )
    alerts.on(
        "autonomy_to_supervised",
        lambda a: accounts.suspend_autonomy(str(a.payload.get("account", ACCOUNT)), reason=a.name, by="alert_router"),
    )
    alerts.on(
        "killswitch_account",
        lambda a: (
            platform.killswitch.activate(KillSwitchLevel.ACCOUNT, str(a.payload["account"]), reason=a.name, actor=ops, now=platform.now)
            if a.payload.get("account")
            and not platform.killswitch.flags_for(tenant_id=TENANT, account_id=str(a.payload["account"])).account
            else None
        ),
    )
    alerts.on("revoke_agent_identity", lambda a: issuer.revoke_agent(str(a.payload.get("agent", "unknown"))))
    alerts.on(
        "revoke_tool_for_tenant",
        lambda a: (
            allowlists[TENANT].revoke_tool(str(a.payload.get("tool", "")))
            if a.payload.get("tool") in registry.tools and str(a.payload.get("tenant")) == TENANT
            else None
        ),
    )

    # --- MCP tools ----------------------------------------------------------------------------------------------
    def run_sim(args: dict[str, Any], ident: AgentIdentity, at: datetime) -> dict[str, Any]:
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
    )
    for name, handler in handlers.items():
        runtime.register_handler(name, handler)

    if bars:
        # Last bar at now-1s, ingested 200 ms later: fresh at decision time ``now``.
        platform.ingest_bars(INSTRUMENT, start=now - timedelta(seconds=1) - feed.step * bars, count=bars + 1)
        platform.ingest_bars(INSTRUMENT_2, start=now - timedelta(seconds=1) - feed.step * bars, count=bars + 1)
    return platform


BACKTEST_START = datetime(2026, 9, 4, 14, 0, tzinfo=UTC)  # a Friday, session open


def run_sim_backtest(
    *,
    instrument_id: str = INSTRUMENT,
    bars: int = 60,
    cost_factor: Decimal = Decimal("1"),
    start: datetime = BACKTEST_START,
    strategy: SmaCrossoverStrategy | None = None,
) -> BacktestReport:
    """ADR-008: a fresh sim platform in BACKTEST mode runs the production pipeline bar by bar."""
    p = build_sim_platform(now=start, mode=AccountMode.BACKTEST, bars=0)
    strat = strategy or SmaCrossoverStrategy()
    cost = CostModel().scaled(cost_factor)
    p.broker.spread_bps = cost.spread_bps
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
        fills = [{"quantity": str(f.quantity), "price": str(f.price)} for f in (result.order.fills if result.order else ())]
        for f in fills:
            p.ledger.book(ACCOUNT).cash -= cost.fee_for(Decimal(f["quantity"]) * Decimal(f["price"]))
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
        position_qty=lambda iid: (
            p.ledger.book(ACCOUNT)
            .positions.get(iid, __import__("portfolio_service.ledger", fromlist=["PositionState"]).PositionState(instrument_id=iid))
            .quantity
        ),
        nav=lambda: p.ledger.nav(ACCOUNT),
        gross=lambda: sum((abs(x.market_value) for x in p.ledger.positions(ACCOUNT)), ZERO),
        submit_and_process=submit_and_process,
        settle_bar=settle,
        cost_model=cost,
    )
    sv = p.strategies.get(STRATEGY, "0.1")
    return runner.run(
        strategy=strat,
        intent_builder=lambda sig, snap, qty: intent_from_signal(sig, snap, account_id=ACCOUNT, position_qty=qty),
        instrument_id=instrument_id,
        bar_timestamps=timestamps,
        data_snapshot_id=snapshot_id,
        hypothesis_hash=sv.pre_registration.hypothesis_hash if sv.pre_registration else None,
    )
