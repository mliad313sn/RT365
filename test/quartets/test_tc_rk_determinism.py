"""TC-RK — Deterministic risk engine [Source: 05; FR-11; NFR-DET-01]. RTM row FR-11. Owner: Backend Lead. Reviewer: pending (Chief Risk Agent)."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import timedelta
from decimal import Decimal
from pathlib import Path

import pytest
from conftest import ACCOUNT, INSTRUMENT, INSTRUMENT_2, STRATEGY, TENANT, VENUE
from risk_engine.engine import ENGINE_BUILD_HASH, decide
from risk_engine.monitors import RuntimeMetrics, evaluate_runtime
from risk_engine.policy import LimitLevel, LimitScope, Metric, effective_limit
from rtcore.errors import SchemaViolation
from rtcore.schemas.account import AccountMode, KillSwitchFlags, OpenOrder, TradingStatus
from rtcore.schemas.decision import CheckResult, Outcome
from rtcore.schemas.intent import Side, TradeIntent, ValidatedIntent
from rtcore.schemas.market import DataQuality, SessionState

ROOT = Path(__file__).resolve().parents[2]


def _inputs(p, **overrides):  # type: ignore[no-untyped-def]
    vi = p.submit_intent(p.make_intent(**overrides))
    p.intent_queue.pop()
    return vi, p.account_snapshot(ACCOUNT), p.market_snapshot(INSTRUMENT), p.policy, p.now


@pytest.mark.tc("TC-RK-001")
@pytest.mark.req("FR-11")
@pytest.mark.quartet("positive")
@pytest.mark.env("dev")
def test_identical_inputs_identical_decision_across_replicas(platform):  # type: ignore[no-untyped-def]
    """Identical inputs -> identical decision record in-process and in a separate interpreter (replica)."""
    vi, acct, mkt, policy, now = _inputs(platform)
    d1 = decide(vi, acct, mkt, policy, now)
    d2 = decide(vi, acct, mkt, policy, now)
    assert d1 == d2 and d1.outcome == Outcome.APPROVED
    payload = json.dumps(
        {
            "vi": vi.model_dump(mode="json"),
            "acct": acct.model_dump(mode="json"),
            "mkt": mkt.model_dump(mode="json"),
            "policy": policy.model_dump(mode="json"),
            "now": now.isoformat(),
        }
    )
    code = (
        "import json,sys;from datetime import datetime;from risk_engine.engine import decide;from risk_engine.policy import RiskPolicy;"
        "from rtcore.schemas.intent import ValidatedIntent;from rtcore.schemas.account import AccountSnapshot;from rtcore.schemas.market import MarketSnapshot;"
        "d=json.load(sys.stdin);r=decide(ValidatedIntent.model_validate(d['vi']),AccountSnapshot.model_validate(d['acct']),MarketSnapshot.model_validate(d['mkt']),RiskPolicy.model_validate(d['policy']),datetime.fromisoformat(d['now']));print(r.model_dump_json())"
    )
    env = {"PYTHONPATH": ":".join(str(ROOT / p) for p in ("libs/core", "services/risk"))}
    out = subprocess.run(
        [sys.executable, "-c", code],
        input=payload,
        capture_output=True,
        text=True,
        env={**env, "PATH": "/usr/bin:/bin"},
        check=True,
        cwd=ROOT,
    )
    replica = json.loads(out.stdout)
    assert replica == json.loads(d1.model_dump_json()), "replica decision differs"
    assert replica["engine_build_hash"] == ENGINE_BUILD_HASH


@pytest.mark.tc("TC-RK-002")
@pytest.mark.req("FR-11")
@pytest.mark.quartet("negative")
@pytest.mark.env("dev")
def test_changed_policy_version_yields_new_decision(platform):  # type: ignore[no-untyped-def]
    """Changing policy_version produces a different decision_id and is recorded in the decision."""
    vi, acct, mkt, policy, now = _inputs(platform)
    d1 = decide(vi, acct, mkt, policy, now)
    d2 = decide(vi, acct, mkt, policy.model_copy(update={"policy_version": "sim-policy-v0.2"}), now)
    assert d1.decision_id != d2.decision_id and d2.policy_version == "sim-policy-v0.2"


@pytest.mark.tc("TC-RK-003")
@pytest.mark.req("FR-11")
@pytest.mark.quartet("abuse")
@pytest.mark.env("dev")
def test_tampered_intent_hash_rejected(platform):  # type: ignore[no-untyped-def]
    """Intent mutated after validation (hash mismatch) -> REJECTED with RK-INTEG; pipeline raises an S1 alert."""
    vi, acct, mkt, policy, now = _inputs(platform)
    tampered = vi.model_copy(update={"intent": vi.intent.model_copy(update={"quantity": Decimal("100000")})})
    d = decide(tampered, acct, mkt, policy, now)
    assert d.outcome == Outcome.REJECTED and d.reason_codes == ("RK-INTEG",)
    result = platform.pipeline.process(tampered, now=now)  # defence in depth: eligibility catches it first (CP-INTEG)
    assert result.eligibility.reason_codes == ("CP-INTEG",) and result.decision is None
    assert platform.alerts.by_name("risk.integrity_violation")[0].severity == "S1"


@pytest.mark.tc("TC-RK-004")
@pytest.mark.req("FR-11")
@pytest.mark.quartet("recovery")
@pytest.mark.env("dev")
def test_engine_restart_same_decision_and_fail_closed_on_missing_inputs(platform):  # type: ignore[no-untyped-def]
    """Missing policy/snapshots -> HALTED (fail closed); after restore the same inputs give the same decision as before."""
    vi, acct, mkt, policy, now = _inputs(platform)
    before = decide(vi, acct, mkt, policy, now)
    assert decide(vi, acct, mkt, None, now).outcome == Outcome.HALTED
    assert decide(vi, None, mkt, policy, now).reason_codes == ("RK-HALT-INPUT",)
    assert decide(vi, acct, None, policy, now).outcome == Outcome.HALTED
    assert decide(None, acct, mkt, policy, now).outcome == Outcome.HALTED
    platform.policy = None
    halted = platform.run_intent(platform.make_intent())
    assert halted.decision is not None and halted.decision.outcome == Outcome.HALTED and halted.final_state.value == "HALTED"
    platform.policy = policy
    after = decide(vi, acct, mkt, policy, now)
    assert after == before


# ---- every pre-trade control has a negative test [Source: 05 table] ----------------------------------------
@pytest.mark.tc("TC-RK-010")
@pytest.mark.req("FR-11")
@pytest.mark.quartet("negative")
@pytest.mark.parametrize(
    "mutate,code,outcome",
    [
        (lambda p, a, m, i: (a.model_copy(update={"trading_status": TradingStatus.SUSPENDED}), m, i), "RK-AUTH-STATUS", Outcome.REJECTED),
        (lambda p, a, m, i: (a.model_copy(update={"authorised_strategies": ()}), m, i), "RK-AUTH-STRATEGY", Outcome.REJECTED),
        (lambda p, a, m, i: (a.model_copy(update={"mode": AccountMode.OBSERVE}), m, i), "RK-AUTH-MODE", Outcome.REJECTED),
        (lambda p, a, m, i: (a.model_copy(update={"mode": AccountMode.HALTED}), m, i), "RK-HALT-MODE", Outcome.HALTED),
        (lambda p, a, m, i: (a.model_copy(update={"kill_switch": KillSwitchFlags(account=True)}), m, i), "RK-HALT-KS", Outcome.HALTED),
        (lambda p, a, m, i: (a.model_copy(update={"kill_switch": KillSwitchFlags(venues=(VENUE,))}), m, i), "RK-HALT-KS", Outcome.HALTED),
        (
            lambda p, a, m, i: (a, m.model_copy(update={"instrument": m.instrument.model_copy(update={"tradable": False})}), i),
            "RK-LIST-TRADABLE",
            Outcome.REJECTED,
        ),
        (lambda p, a, m, i: (a, m.model_copy(update={"session_state": SessionState.CLOSED}), i), "RK-SESS", Outcome.REJECTED),
        (lambda p, a, m, i: (a, m.model_copy(update={"venue_healthy": False}), i), "RK-SESS-VENUE", Outcome.REJECTED),
        (lambda p, a, m, i: (a, m.model_copy(update={"market_ts": m.market_ts - timedelta(seconds=30)}), i), "RK-FRESH", Outcome.REJECTED),
        (lambda p, a, m, i: (a, m.model_copy(update={"quality": DataQuality.SUSPECT}), i), "RK-FRESH-QUALITY", Outcome.REJECTED),
        (
            lambda p, a, m, i: (a, m.model_copy(update={"ingest_ts": m.market_ts - timedelta(seconds=5)}), i),
            "RK-FRESH-CLOCK",
            Outcome.REJECTED,
        ),
        (lambda p, a, m, i: (a, m, {"quantity": "7.5"}), "RK-INSTR-LOT", Outcome.REJECTED),
        (lambda p, a, m, i: (a, m, {"order_type": "LIMIT", "limit_price": "100.005"}), "RK-INSTR-TICK", Outcome.REJECTED),
        (lambda p, a, m, i: (a, m, {"side": "SELL_SHORT", "protective_stop": "200"}), "RK-INSTR-SHORT", Outcome.REJECTED),
        (lambda p, a, m, i: (a.model_copy(update={"buying_power": Decimal("10")}), m, i), "RK-BP", Outcome.REJECTED),
        (lambda p, a, m, i: (a, m, {"quantity": "600"}), "RK-CAP", Outcome.REJECTED),
        (
            lambda p, a, m, i: (
                a.model_copy(
                    update={
                        "open_orders": (
                            OpenOrder(
                                order_id="o1",
                                instrument_id=INSTRUMENT,
                                side=Side.BUY,
                                quantity=Decimal("400"),
                                notional=Decimal("40000"),
                                submitted_at=p.now,
                            ),
                        )
                    }
                ),
                m,
                {"quantity": "150"},
            ),
            "RK-CAP-AGG",
            Outcome.REJECTED,
        ),
        (
            lambda p, a, m, i: (
                a.model_copy(update={"nav": Decimal("1000"), "peak_nav": Decimal("1000"), "buying_power": Decimal("50000")}),
                m,
                {"quantity": "100"},
            ),
            "RK-EXP",
            Outcome.REJECTED,
        ),
        (
            lambda p, a, m, i: (a.model_copy(update={"nav": Decimal("30000"), "peak_nav": Decimal("30000")}), m, {"quantity": "100"}),
            "RK-CONC",
            Outcome.REJECTED,
        ),
        (
            lambda p, a, m, i: (
                a,
                m,
                {"order_type": "LIMIT", "limit_price": str((m.reference_price * Decimal("1.2")).quantize(Decimal("0.01")))},
            ),
            "RK-COLLAR",
            Outcome.REJECTED,
        ),
        (lambda p, a, m, i: (a.model_copy(update={"orders_last_minute": 10}), m, i), "RK-RATE", Outcome.REJECTED),
        (
            lambda p, a, m, i: (a, m.model_copy(update={"average_daily_volume": Decimal("100")}), i),
            "RK-LIQ-APPROVAL",
            Outcome.REQUIRES_HUMAN_APPROVAL,
        ),
        (
            lambda p, a, m, i: (a, m.model_copy(update={"realized_volatility_pct": Decimal("95")}), i),
            "RK-VOL-APPROVAL",
            Outcome.REQUIRES_HUMAN_APPROVAL,
        ),
        (lambda p, a, m, i: (a, m, {"protective_stop": None}), "RK-PROT", Outcome.REJECTED),
        (lambda p, a, m, i: (a, m, {"protective_stop": "150"}), "RK-PROT", Outcome.REJECTED),
        (
            lambda p, a, m, i: (
                a,
                m,
                {"market_ts": (p.now - timedelta(seconds=3)).isoformat(), "expiry": (p.now - timedelta(seconds=1)).isoformat()},
            ),
            "RK-EXPIRED",
            Outcome.REJECTED,
        ),
    ],
)
def test_each_pre_trade_control_fails_with_its_reason_code(platform, mutate, code, outcome):  # type: ignore[no-untyped-def]
    """Each pre-trade control produces its reason code, evaluated value and threshold; outcome follows precedence."""
    p = platform
    acct, mkt = p.account_snapshot(ACCOUNT), p.market_snapshot(INSTRUMENT)
    acct2, mkt2, overrides = mutate(p, acct, mkt, {})
    raw = p.make_intent(**overrides)
    from rtcore.schemas.intent import TradeIntent, ValidatedIntent

    vi = ValidatedIntent.seal(TradeIntent.model_validate(raw), correlation_id="c", tenant_id=TENANT, submitted_by="t", validated_at=p.now)
    d = decide(vi, acct2, mkt2, p.policy, p.now)
    assert code in d.reason_codes, d.reason_codes
    assert d.outcome == outcome
    failing = [e for e in d.evaluated if e.reason_code == code]
    assert failing and all(e.threshold and e.value for e in failing)


@pytest.mark.tc("TC-RK-011")
@pytest.mark.req("FR-11")
@pytest.mark.quartet("negative")
def test_all_failing_reasons_listed_not_only_first(platform):  # type: ignore[no-untyped-def]
    """Fail-fast order but complete reason list: several failing controls appear together."""
    p = platform
    acct = p.account_snapshot(ACCOUNT).model_copy(update={"trading_status": TradingStatus.SUSPENDED, "buying_power": Decimal("1")})
    mkt = p.market_snapshot(INSTRUMENT).model_copy(update={"session_state": SessionState.CLOSED})
    vi = p.submit_intent(p.make_intent(quantity="600", protective_stop=None))
    d = decide(vi, acct, mkt, p.policy, p.now)
    assert {"RK-AUTH-STATUS", "RK-SESS", "RK-BP", "RK-CAP", "RK-PROT"} <= set(d.reason_codes)
    assert d.outcome == Outcome.REJECTED


@pytest.mark.tc("TC-RK-012")
@pytest.mark.req("FR-11")
@pytest.mark.quartet("positive")
def test_limit_hierarchy_effective_is_minimum(platform):  # type: ignore[no-untyped-def]
    """Effective limit = min over platform/tenant/account/strategy/instrument levels [Committee]."""
    scope = LimitScope(tenant_id=TENANT, account_id=ACCOUNT, strategy_id=STRATEGY, instrument_id=INSTRUMENT)
    eff = effective_limit(platform.policy, Metric.MAX_NOTIONAL_PER_ORDER, scope, platform.now)
    assert eff.threshold == Decimal("50000") and eff.source_level == LimitLevel.STRATEGY
    other = effective_limit(
        platform.policy,
        Metric.MAX_NOTIONAL_PER_ORDER,
        scope.model_copy(update={"strategy_id": "other", "account_id": "other"}),
        platform.now,
    )
    assert other.threshold == Decimal("250000") and other.source_level == LimitLevel.TENANT
    undefined = effective_limit(platform.policy.model_copy(update={"limits": ()}), Metric.LEVERAGE_X, scope, platform.now)
    assert undefined.threshold is None


@pytest.mark.tc("TC-RK-013")
@pytest.mark.req("FR-11")
@pytest.mark.quartet("negative")
def test_undefined_limit_fails_closed(platform):  # type: ignore[no-untyped-def]
    """A metric with no limit at any level fails (RK-*-UNDEFINED) rather than passing silently [O-07]."""
    vi = platform.submit_intent(platform.make_intent())
    policy = platform.policy.model_copy(update={"limits": tuple(lim for lim in platform.policy.limits if lim.metric != Metric.LEVERAGE_X)})
    d = decide(vi, platform.account_snapshot(ACCOUNT), platform.market_snapshot(INSTRUMENT), policy, platform.now)
    assert "RK-LEV-UNDEFINED" in d.reason_codes and d.outcome == Outcome.REJECTED


@pytest.mark.tc("TC-RK-014")
@pytest.mark.req("FR-11")
@pytest.mark.quartet("positive")
def test_mode_semantics_supervised_and_envelope(supervised, autonomous):  # type: ignore[no-untyped-def]
    """Supervised -> REQUIRES_HUMAN_APPROVAL; bounded autonomy inside envelope -> APPROVED, beyond -> approval."""
    r = supervised.run_intent(supervised.make_intent())
    assert r.decision.outcome == Outcome.REQUIRES_HUMAN_APPROVAL and "RK-MODE-SUPERVISED" in r.decision.reason_codes and r.approval_id
    ok = autonomous.run_intent(autonomous.make_intent(quantity="100"))
    assert ok.decision.outcome == Outcome.APPROVED
    acct = autonomous.accounts.get(ACCOUNT)
    autonomous.accounts._accounts[ACCOUNT] = acct.model_copy(update={"capital_envelope": Decimal("15000")})
    beyond = autonomous.run_intent(autonomous.make_intent(quantity="120"))  # not an economic duplicate of the first order
    assert beyond.decision.outcome == Outcome.REQUIRES_HUMAN_APPROVAL and "RK-ENVELOPE" in beyond.decision.reason_codes


@pytest.mark.tc("TC-RK-015")
@pytest.mark.req("FR-11")
@pytest.mark.quartet("abuse")
def test_duplicate_and_correlated_group(platform):  # type: ignore[no-untyped-def]
    """Replayed signed intent -> RK-DUP; correlated group exposure enforced across instruments."""
    raw = platform.make_intent()
    first = platform.run_intent(raw)
    assert first.decision.outcome == Outcome.APPROVED
    with pytest.raises(SchemaViolation):  # the queue refuses a replayed intent_id outright
        platform.submit_intent(raw)
    replay = ValidatedIntent.seal(
        TradeIntent.model_validate(raw), correlation_id="corr-replay", tenant_id=TENANT, submitted_by="agent:sim", validated_at=platform.now
    )
    d = decide(replay, platform.account_snapshot(ACCOUNT), platform.market_snapshot(INSTRUMENT), platform.policy, platform.now)
    assert "RK-DUP" in d.reason_codes  # economic duplicate of a recent order even if the queue were bypassed
    acct = platform.account_snapshot(ACCOUNT).model_copy(
        update={"nav": Decimal("20000"), "peak_nav": Decimal("20000"), "buying_power": Decimal("20000")}
    )
    vi = platform.submit_intent(platform.make_intent(instrument_id=INSTRUMENT_2, quantity="100"))
    d2 = decide(vi, acct, platform.market_snapshot(INSTRUMENT_2), platform.policy, platform.now)
    assert "RK-CORR" in d2.reason_codes


@pytest.mark.tc("TC-RK-016")
@pytest.mark.req("FR-17")
@pytest.mark.quartet("positive")
def test_runtime_monitors_emit_halt_events(platform):  # type: ignore[no-untyped-def]
    """Runtime controls produce HALT events for loss, drawdown, frequency, slippage, rejects, latency, connectivity, drift, breaks, venue."""
    acct = platform.account_snapshot(ACCOUNT).model_copy(update={"daily_pnl": Decimal("-40000"), "peak_nav": Decimal("1300000")})
    events = evaluate_runtime(
        acct,
        platform.policy,
        RuntimeMetrics(
            orders_last_minute=100,
            slippage_bps_p95=Decimal("80"),
            rejection_rate_pct=Decimal("50"),
            decision_latency_p99_ms=Decimal("900"),
            broker_connected=False,
            venue_healthy=False,
            model_drift_breached=True,
            open_reconciliation_breaks=1,
        ),
        platform.now,
    )
    codes = {e.reason_code for e in events}
    assert {
        "RT-LOSS-DAILY",
        "RT-DRAWDOWN",
        "RT-FREQ",
        "RT-SLIPPAGE",
        "RT-REJECTS",
        "RT-LATENCY",
        "RT-CONNECTIVITY",
        "RT-DRIFT",
        "RT-RECON",
        "RT-VENUE",
    } <= codes
    assert all(e.value and e.threshold for e in events)
    assert evaluate_runtime(platform.account_snapshot(ACCOUNT), platform.policy, RuntimeMetrics(), platform.now) == ()


def test_evaluated_checks_cover_all_sixteen_families(platform):  # type: ignore[no-untyped-def]
    vi = platform.submit_intent(platform.make_intent())
    d = decide(vi, platform.account_snapshot(ACCOUNT), platform.market_snapshot(INSTRUMENT), platform.policy, platform.now)
    names = {e.check.split("[")[0] for e in d.evaluated}
    expected = {
        "trading_status",
        "instrument_tradable",
        "market_session",
        "data_freshness_s",
        "instrument_match",
        "buying_power",
        "max_notional_per_order",
        "gross_exposure_pct_nav",
        "concentration_single_name_pct",
        "leverage_x",
        "price_collar_pct",
        "duplicate_intent",
        "orders_per_minute",
        "max_order_pct_adv",
        "volatility_regime_pct",
        "protective_stop",
        "correlated_group_pct_nav",
    }
    assert expected <= names
    assert all(e.result in (CheckResult.PASS, CheckResult.FAIL, CheckResult.NOT_EVALUATED) for e in d.evaluated)


@pytest.mark.tc("TC-RK-017")
@pytest.mark.req("FR-11")
@pytest.mark.quartet("abuse")
def test_open_orders_count_towards_exposure_and_risk_reducing_orders_pass(platform):  # type: ignore[no-untyped-def]
    """Open buys are projected into gross exposure (no evasion via resting orders); a SELL that shrinks an over-limit book is allowed (Risk review OBJ-3/P4)."""
    p = platform
    acct = p.account_snapshot(ACCOUNT)
    heavy = acct.model_copy(
        update={
            "nav": Decimal("100000"),
            "peak_nav": Decimal("100000"),
            "buying_power": Decimal("500000"),
            "open_orders": tuple(
                OpenOrder(
                    order_id=f"o{i}",
                    instrument_id=INSTRUMENT_2,
                    side=Side.BUY,
                    quantity=Decimal("2000"),
                    notional=Decimal("100000"),
                    submitted_at=p.now,
                )
                for i in range(2)
            ),
        }
    )
    vi = p.submit_intent(p.make_intent(quantity="10"))
    d = decide(vi, heavy, p.market_snapshot(INSTRUMENT), p.policy, p.now)
    assert "RK-EXP" in d.reason_codes  # 200k of open buys on 100k NAV already breaches gross exposure
    from rtcore.schemas.account import Position

    over = acct.model_copy(
        update={
            "nav": Decimal("100000"),
            "peak_nav": Decimal("100000"),
            "positions": (
                Position(
                    instrument_id=INSTRUMENT,
                    quantity=Decimal("3000"),
                    average_price=Decimal("100"),
                    market_value=Decimal("300000"),
                    sector="SIM-TECH",
                    country="ZZ",
                    currency="USD",
                ),
            ),
        }
    )
    sell = p.submit_intent(p.make_intent(side="SELL", quantity="100", protective_stop=None))
    d2 = decide(sell, over, p.market_snapshot(INSTRUMENT), p.policy, p.now)
    assert d2.outcome == Outcome.APPROVED, d2.reason_codes
    buy_more = p.submit_intent(p.make_intent(quantity="100"))
    assert decide(buy_more, over, p.market_snapshot(INSTRUMENT), p.policy, p.now).outcome == Outcome.REJECTED


@pytest.mark.tc("TC-RK-018")
@pytest.mark.req("FR-11")
@pytest.mark.quartet("negative")
def test_stale_snapshot_tenant_mismatch_and_breached_loss(platform):  # type: ignore[no-untyped-def]
    """Stale account snapshot -> HALTED; tenant mismatch -> REJECTED; already-breached daily loss -> REJECTED; NAV <= 0 -> REJECTED (Risk review OBJ-2)."""
    p = platform
    vi = p.submit_intent(p.make_intent())
    acct, mkt = p.account_snapshot(ACCOUNT), p.market_snapshot(INSTRUMENT)
    stale = decide(vi, acct.model_copy(update={"as_of": p.now - timedelta(days=1)}), mkt, p.policy, p.now)
    assert stale.outcome == Outcome.HALTED and "RK-HALT-INPUT" in stale.reason_codes
    wrong_tenant = decide(vi.model_copy(update={"tenant_id": "tenant-other"}), acct, mkt, p.policy, p.now)
    assert "RK-AUTH-TENANT" in wrong_tenant.reason_codes
    breached = decide(vi, acct.model_copy(update={"daily_pnl": Decimal("-40000")}), mkt, p.policy, p.now)
    assert "RK-LOSS" in breached.reason_codes and breached.outcome == Outcome.REJECTED
    negative = decide(vi, acct.model_copy(update={"nav": Decimal("-1"), "peak_nav": Decimal("1")}), mkt, p.policy, p.now)
    assert "RK-NAV" in negative.reason_codes


@pytest.mark.tc("TC-RK-019")
@pytest.mark.req("FR-12")
@pytest.mark.quartet("recovery")
def test_approval_re_decides_on_current_snapshots(supervised):  # type: ignore[no-untyped-def]
    """An approved intent is re-decided at execution time; a limit breached meanwhile blocks execution (Risk review OBJ-2)."""
    from conftest import PM
    from rtcore.errors import ControlDenied

    r = supervised.run_intent(supervised.make_intent())
    supervised.policy = supervised.policy.model_copy(
        update={"limits": tuple(lim for lim in supervised.policy.limits if lim.metric.value != "max_notional_per_order")}
    )
    with pytest.raises(ControlDenied):
        supervised.approve(r.approval_id, PM)
    assert supervised.broker.submissions_received == 0 and supervised.audit.by_action("risk.redecided.v1")
    assert supervised.tracker.get(r.decision.intent_id).state.value == "REJECTED"


@pytest.mark.tc("TC-RK-020")
@pytest.mark.req("FR-11")
@pytest.mark.quartet("positive")
def test_limit_change_only_via_maker_checker(platform):  # type: ignore[no-untyped-def]
    """A checked, cooled-down limit change becomes a new policy version; nothing else writes limits (Risk review F-04)."""
    from conftest import RISK_OFFICER, SRE
    from risk_engine.policy import LimitScope, Metric, effective_limit

    scope = LimitScope(tenant_id=TENANT, account_id=ACCOUNT, strategy_id="*", instrument_id="*")
    before = effective_limit(platform.policy, Metric.LEVERAGE_X, scope, platform.now).threshold
    change = platform.limits_mc.propose(
        "limit.changed",
        {"level": "ACCOUNT", "scope_id": ACCOUNT, "metric": "leverage_x", "threshold": "1.5"},
        RISK_OFFICER,
        now=platform.now,
    )
    platform.limits_mc.check(change.change_id, SRE, now=platform.now, reason="reviewed")
    assert platform.apply_effective_limits(platform.now).policy_version == platform.policy.policy_version  # cooling period not over
    assert effective_limit(platform.policy, Metric.LEVERAGE_X, scope, platform.now).threshold == before
    platform.apply_effective_limits(platform.now + timedelta(hours=1, seconds=1))
    assert effective_limit(platform.policy, Metric.LEVERAGE_X, scope, platform.now + timedelta(hours=2)).threshold == Decimal("1.5")
    assert platform.policy.policy_version != "sim-policy-v0.1" and platform.audit.by_action("limit.changed.v1")
