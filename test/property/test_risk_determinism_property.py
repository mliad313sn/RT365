"""Property-based determinism [Source: 05; NFR-DET-01]: for arbitrary inputs decide() is a pure function."""

from __future__ import annotations

import json
from datetime import timedelta
from decimal import Decimal

import pytest
from conftest import ACCOUNT, INSTRUMENT, TENANT
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st
from risk_engine.engine import decide
from risk_engine.policy import LimitLevel, LimitScope, Metric, effective_limit
from rtcore.schemas.account import AccountMode, KillSwitchFlags, TradingStatus
from rtcore.schemas.decision import CheckResult, DecisionRecord, Outcome
from rtcore.schemas.intent import TradeIntent, ValidatedIntent
from rtcore.schemas.market import DataQuality, SessionState
from web_bff.platform import build_sim_platform

P = build_sim_platform()
ACCT = P.account_snapshot(ACCOUNT)
MKT = P.market_snapshot(INSTRUMENT)
assert ACCT is not None and MKT is not None

qty = st.integers(min_value=1, max_value=5000).map(lambda n: str(n))
stop = st.one_of(st.none(), st.decimals(min_value=Decimal("50"), max_value=Decimal("150"), places=2).map(str))
account_variants = st.fixed_dictionaries(
    {
        "mode": st.sampled_from(list(AccountMode)),
        "trading_status": st.sampled_from(list(TradingStatus)),
        "buying_power": st.integers(min_value=0, max_value=2_000_000).map(Decimal),
        "orders_last_minute": st.integers(min_value=0, max_value=40),
        "kill_switch": st.sampled_from([KillSwitchFlags(), KillSwitchFlags(platform=True), KillSwitchFlags(account=True)]),
        "capital_envelope": st.one_of(st.none(), st.integers(min_value=1000, max_value=500000).map(Decimal)),
    }
)
market_variants = st.fixed_dictionaries(
    {
        "session_state": st.sampled_from(list(SessionState)),
        "quality": st.sampled_from(list(DataQuality)),
        "realized_volatility_pct": st.integers(min_value=0, max_value=120).map(Decimal),
        "average_daily_volume": st.integers(min_value=0, max_value=5_000_000).map(Decimal),
        "market_ts_offset_s": st.integers(min_value=-120, max_value=60),
    }
)


def _vi(q: str, protective: str | None) -> ValidatedIntent:
    raw = P.make_intent(quantity=q, protective_stop=protective)
    return ValidatedIntent.seal(
        TradeIntent.model_validate(raw), correlation_id="prop", tenant_id=TENANT, submitted_by="prop", validated_at=P.now
    )


@settings(max_examples=150, deadline=None, suppress_health_check=[HealthCheck.too_slow])
@given(qty, stop, account_variants, market_variants)
def test_decide_is_pure_and_precedence_holds(q, protective, av, mv):  # type: ignore[no-untyped-def]
    vi = _vi(q, protective)
    acct = ACCT.model_copy(update=av)
    off = mv.pop("market_ts_offset_s")
    mkt = MKT.model_copy(
        update={**mv, "market_ts": MKT.market_ts + timedelta(seconds=off), "ingest_ts": MKT.ingest_ts + timedelta(seconds=off)}
    )
    d1 = decide(vi, acct, mkt, P.policy, P.now)
    d2 = decide(vi, acct, mkt, P.policy, P.now)
    assert d1 == d2
    assert DecisionRecord.model_validate(json.loads(d1.model_dump_json())) == d1
    fails = {e.reason_code for e in d1.evaluated if e.result == CheckResult.FAIL and e.reason_code}
    assert set(d1.reason_codes) == fails
    if any(c.startswith("RK-HALT") for c in fails):
        assert d1.outcome == Outcome.HALTED
    elif any(not (c.endswith("-APPROVAL") or c in {"RK-MODE-SUPERVISED", "RK-ENVELOPE", "RK-AUTONOMY-SUSPENDED"}) for c in fails):
        assert d1.outcome == Outcome.REJECTED
    elif fails:
        assert d1.outcome == Outcome.REQUIRES_HUMAN_APPROVAL
    else:
        assert d1.outcome == Outcome.APPROVED
    assert d1.policy_version == P.policy.policy_version and d1.intent_hash == vi.intent_hash


@settings(max_examples=100, deadline=None)
@given(st.lists(st.tuples(st.sampled_from(list(LimitLevel)), st.integers(min_value=1, max_value=10_000_000)), min_size=1, max_size=8))
def test_effective_limit_is_minimum_of_applicable(levels):  # type: ignore[no-untyped-def]
    from risk_engine.policy import Limit

    scope = LimitScope(tenant_id="t", account_id="a", strategy_id="s", instrument_id="i")
    limits = tuple(
        Limit(level=lvl, scope_id=scope.id_for(lvl), tenant_id="t", metric=Metric.LEVERAGE_X, threshold=Decimal(v)) for lvl, v in levels
    )
    policy = P.policy.model_copy(update={"limits": limits})
    eff = effective_limit(policy, Metric.LEVERAGE_X, scope, P.now)
    assert eff.threshold == min(Decimal(v) for _, v in levels)


@pytest.mark.parametrize("missing", ["vi", "acct", "mkt", "policy"])
def test_fail_closed_for_every_missing_input(missing):  # type: ignore[no-untyped-def]
    vi = _vi("10", "95")
    args = {"vi": vi, "acct": ACCT, "mkt": MKT, "policy": P.policy}
    args[missing] = None
    d = decide(args["vi"], args["acct"], args["mkt"], args["policy"], P.now)
    assert d.outcome == Outcome.HALTED and d.reason_codes == ("RK-HALT-INPUT",)
