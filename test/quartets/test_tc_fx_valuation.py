"""TC-FX — FX as a deterministic decision input [Source: 02 FR-05, FR-11; docs/GLOBAL_COMPATIBILITY.md F-3].

Cross-currency NAV, cash and exposure in the account base currency. Rates enter the platform only through the
bitemporal ``platform.fx`` store; the ledger and the risk engine receive a snapshot as an argument and never fetch
one. Missing, unknown, undated or stale rates make the NAV typed-UNKNOWN and the decision fail closed — never a
1.0 fallback and never a number that looks like money. Rates below are dev/sim fixtures, never market data; the
base currency of the sim account is USD [Committee].
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest
from conftest import ACCOUNT
from conftest import INSTRUMENT as INSTRUMENT_ID
from portfolio_service.ledger import Ledger
from rtcore.errors import FxBudgetUndefined, FxPairUnknown, FxSnapshotMissing, FxSnapshotStale, FxUnavailable
from rtcore.money import convert, is_iso4217, minor_units, quantize_money
from rtcore.provenance import Provenance
from rtcore.schemas.account import AccountMode, KillSwitchFlags, NavStatus, TradingStatus
from rtcore.schemas.fx import FxSnapshot
from rtcore.schemas.intent import Side
from rtcore.schemas.market import InstrumentAttributes

FX_NOW = datetime(2026, 9, 7, 14, 0, tzinfo=UTC)
FX_BUDGET_S = Decimal("2")  # test-local budget passed as an argument; the policy value stays [Open: O-07]


def _instrument(iid: str, currency: str, country: str = "ZZ") -> InstrumentAttributes:
    return InstrumentAttributes(
        instrument_id=iid,
        venue="SIMX",
        asset_class="EQUITY",
        currency=currency,
        sector="SIM-TECH",
        country=country,
        tick_size=Decimal("0.0001"),
        lot_size=Decimal("1"),
        tradable=True,
        shortable=False,
        valid_from=datetime(2020, 1, 1, tzinfo=UTC),
    )


def _fx(as_of: datetime = FX_NOW, **rates: str) -> FxSnapshot:
    base = {"USD/JPY": "150", "USD/KWD": "0.30", "USD/CLF": "0.03", "EUR/USD": "1.25"}
    base.update(rates)
    return FxSnapshot.build(
        base_currency="USD", rates={k: Decimal(v) for k, v in base.items()}, as_of=as_of, source="sim-fx", provenance=Provenance.SIMULATED
    )


def _multi_currency_book() -> Ledger:
    ledger = Ledger()
    ledger.open_account("acct-fx", "tenant-sim", "USD", Decimal("100000"))
    for iid, ccy in (("SIMEQ1", "USD"), ("SIMJP1", "JPY"), ("SIMKW1", "KWD")):
        ledger.register_instrument(_instrument(iid, ccy))
    ledger.apply_fill("acct-fx", "SIMJP1", Side.BUY, Decimal("10"), Decimal("15000"))  # JPY cash leg
    ledger.apply_fill("acct-fx", "SIMKW1", Side.BUY, Decimal("100"), Decimal("3.125"))  # KWD cash leg
    ledger.mark("SIMJP1", Decimal("16000"))
    ledger.mark("SIMKW1", Decimal("3.2"))
    return ledger


@pytest.mark.tc("TC-FX-001")
@pytest.mark.req("FR-05")
@pytest.mark.quartet("positive")
@pytest.mark.env("sim")
def test_multi_currency_book_values_in_base_with_fx_snapshot():  # type: ignore[no-untyped-def]
    """A JPY/KWD/USD book converts to the USD base through the FX snapshot: NAV, cash per currency and exposure are Decimal, rounded per ISO 4217 minor units; positions keep their instrument currency; triangulation only through the snapshot base."""
    fx = _fx()
    # conversion primitives: minor units 0 (JPY), 3 (KWD), 4 (CLF), 2 (USD); no float anywhere
    assert (minor_units("JPY"), minor_units("KWD"), minor_units("CLF"), minor_units("USD")) == (0, 3, 4, 2)
    assert quantize_money(Decimal("1.5"), "JPY") == Decimal("2") and quantize_money(Decimal("2.5"), "JPY") == Decimal("2")  # half-even
    jpy = convert(Decimal("1"), "USD", "JPY", fx, now=FX_NOW, max_age_s=FX_BUDGET_S)
    clf = convert(Decimal("1"), "USD", "CLF", fx, now=FX_NOW, max_age_s=FX_BUDGET_S)
    assert jpy == Decimal("150") and jpy.as_tuple().exponent == 0
    assert clf == Decimal("0.0300") and clf.as_tuple().exponent == -4
    assert convert(Decimal("150"), "JPY", "USD", fx, now=FX_NOW, max_age_s=FX_BUDGET_S) == Decimal("1.00")  # inverse leg
    assert convert(Decimal("1"), "EUR", "JPY", fx, now=FX_NOW, max_age_s=FX_BUDGET_S) == Decimal(
        "188"
    )  # EUR->USD->JPY = 187.5 -> half-even
    assert convert(Decimal("312.5"), "KWD", "USD", fx, now=FX_NOW, max_age_s=FX_BUDGET_S) == Decimal("1041.67")
    assert convert(Decimal("42.42"), "USD", "USD", None, now=FX_NOW, max_age_s=FX_BUDGET_S) == Decimal("42.42")  # identity needs no rate
    assert is_iso4217("JPY") and is_iso4217("XOF") and not is_iso4217("XXX") and not is_iso4217("ZZZ") and not is_iso4217("usd")

    ledger = _multi_currency_book()
    book = ledger.book("acct-fx")
    assert book.balances == {"USD": Decimal("100000"), "JPY": Decimal("-150000"), "KWD": Decimal("-312.5")}
    assert book.cash == Decimal("100000")  # base-currency cash is the USD balance
    positions = {p.instrument_id: p for p in ledger.positions("acct-fx")}
    assert positions["SIMJP1"].currency == "JPY" and positions["SIMJP1"].market_value == Decimal("160000")
    assert positions["SIMKW1"].currency == "KWD" and positions["SIMKW1"].market_value == Decimal("320.0")
    # NAV = 100000 + (-150000 JPY -> -1000.00) + (-312.5 KWD -> -1041.67) + (160000 JPY -> 1066.67) + (320 KWD -> 1066.67)
    val = ledger.valuation("acct-fx", fx, now=FX_NOW, max_age_s=FX_BUDGET_S)
    assert val.status == NavStatus.KNOWN and val.value == Decimal("100091.67") and val.currency == "USD"
    assert val.fx_snapshot_id == fx.snapshot_id and val.reason_code is None
    assert ledger.nav("acct-fx", fx, now=FX_NOW, max_age_s=FX_BUDGET_S) == Decimal("100091.67")
    assert ledger.gross_exposure("acct-fx", fx, now=FX_NOW, max_age_s=FX_BUDGET_S) == Decimal("2133.34")
    snap = ledger.snapshot(
        "acct-fx",
        now=FX_NOW,
        mode=AccountMode.PAPER,
        trading_status=TradingStatus.ACTIVE,
        jurisdiction="ZZ",
        customer_type="RETAIL",
        authorised_strategies=(),
        open_orders=(),
        kill_switch=KillSwitchFlags(),
        fx=fx,
        fx_max_age_s=FX_BUDGET_S,
    )
    assert snap.nav == Decimal("100091.67") and snap.valuation is not None and snap.valuation.status == NavStatus.KNOWN
    assert snap.cash_by_currency == {"USD": Decimal("100000"), "JPY": Decimal("-150000"), "KWD": Decimal("-312.5")}
    assert snap.capital_in_use == Decimal("2133.34") and snap.base_currency == "USD"
    # a single-currency book still values without any snapshot (no FX required)
    single = Ledger()
    single.open_account("a", "t", "USD", Decimal("10"))
    assert single.valuation("a", None, now=FX_NOW, max_age_s=None).status == NavStatus.KNOWN and single.nav("a") == Decimal("10")


@pytest.mark.tc("TC-FX-002")
@pytest.mark.req("FR-05")
@pytest.mark.quartet("negative")
@pytest.mark.env("sim")
def test_missing_or_stale_rate_makes_nav_unknown_never_a_number(platform):  # type: ignore[no-untyped-def]
    """A missing snapshot, a missing pair, an undefined budget or a stale snapshot make the NAV UNKNOWN (typed, value None, reason code); `nav()` raises a typed FX error; nothing falls back to a 1.0 rate."""
    ledger = _multi_currency_book()
    no_jpy = FxSnapshot.build(
        base_currency="USD", rates={"USD/KWD": Decimal("0.30")}, as_of=FX_NOW, source="sim-fx", provenance=Provenance.SIMULATED
    )
    for fx, exc, code in (
        (None, FxSnapshotMissing, "RK-FX-MISSING"),
        (no_jpy, FxPairUnknown, "RK-FX-MISSING"),
        (_fx(as_of=FX_NOW - timedelta(seconds=10)), FxSnapshotStale, "RK-FX-STALE"),
        (_fx(as_of=FX_NOW + timedelta(seconds=10)), FxSnapshotStale, "RK-FX-STALE"),  # a rate from the future is a clock anomaly
    ):
        val = ledger.valuation("acct-fx", fx, now=FX_NOW, max_age_s=FX_BUDGET_S)
        assert val.status == NavStatus.UNKNOWN and val.value is None and val.reason_code == code, (fx, val)
        assert val.detail
        with pytest.raises(exc) as info:
            ledger.nav("acct-fx", fx, now=FX_NOW, max_age_s=FX_BUDGET_S)
        assert isinstance(info.value, FxUnavailable) and info.value.reason_code == code
    with pytest.raises(FxBudgetUndefined):
        ledger.nav("acct-fx", _fx(), now=FX_NOW, max_age_s=None)  # no freshness budget defined -> fail closed, not "unlimited"
    assert ledger.valuation("acct-fx", _fx(), now=FX_NOW, max_age_s=None).reason_code == "RK-FX-UNDEFINED"
    # through the composition root: a foreign-currency fill with no FX snapshot in the store -> UNKNOWN on the account snapshot
    p = platform
    p.ledger.register_instrument(_instrument("SIMJP1", "JPY"))
    p.ledger.apply_fill(ACCOUNT, "SIMJP1", Side.BUY, Decimal("10"), Decimal("15000"))
    p.ledger.mark("SIMJP1", Decimal("15000"))
    snap = p.account_snapshot(ACCOUNT)
    assert snap.valuation is not None and snap.valuation.status == NavStatus.UNKNOWN and snap.valuation.reason_code == "RK-FX-MISSING"
    assert snap.valuation.value is None and snap.nav == Decimal("0") and snap.cash_by_currency["JPY"] == Decimal("-150000")
    rows = p.audit.by_action("portfolio.valuation.unknown")
    assert rows and rows[-1].payload["reason_code"] == "RK-FX-MISSING" and rows[-1].correlation_id


@pytest.mark.tc("TC-FX-003")
@pytest.mark.req("FR-05")
@pytest.mark.quartet("abuse")
@pytest.mark.env("sim")
def test_fx_snapshot_schema_boundary_rejects_bad_rates_and_no_agent_can_supply_one(platform):  # type: ignore[no-untyped-def]
    """Rate 0, negative, NaN/Infinity, unknown or lower-case ISO 4217 code, bad pair form, same-currency pair, duplicate pair, naive timestamp, unknown field and a snapshot id that does not match its content are rejected at the schema boundary; no MCP tool can write a rate and an intent cannot carry one."""
    from pydantic import ValidationError

    good = {"USD/JPY": Decimal("150")}

    def build(rates: dict[str, Decimal], **kw: object) -> FxSnapshot:
        args: dict[str, object] = {
            "base_currency": "USD",
            "rates": rates,
            "as_of": FX_NOW,
            "source": "sim-fx",
            "provenance": Provenance.SIMULATED,
        }
        args.update(kw)
        return FxSnapshot.build(**args)  # type: ignore[arg-type]

    for bad in (
        {"USD/JPY": Decimal("0")},
        {"USD/JPY": Decimal("-150")},
        {"USD/JPY": Decimal("NaN")},
        {"USD/JPY": Decimal("Infinity")},
        {"USD/JPY": Decimal("-Infinity")},
        {"USD/ZZZ": Decimal("1")},  # not an ISO 4217 code
        {"USD/XXX": Decimal("1")},  # ISO 4217 "no currency"
        {"usd/jpy": Decimal("150")},
        {"USDJPY": Decimal("150")},
        {"USD/USD": Decimal("1")},
    ):
        with pytest.raises((ValidationError, ValueError)):
            build(bad)
    with pytest.raises((ValidationError, ValueError)):
        FxSnapshot.model_validate(
            {**build(good).model_dump(mode="json"), "rates": [{"pair": "USD/JPY", "rate": "150"}, {"pair": "USD/JPY", "rate": "151"}]}
        )
    with pytest.raises((ValidationError, ValueError)):
        build(good, base_currency="ZZZ")
    with pytest.raises((ValidationError, ValueError)):
        build(good, as_of=FX_NOW.replace(tzinfo=None))
    with pytest.raises((ValidationError, ValueError)):
        build(good, source="")
    with pytest.raises((ValidationError, ValueError)):
        FxSnapshot.model_validate({**build(good).model_dump(mode="json"), "override": True})
    # a snapshot whose id does not match its content (edited after it was built) is refused when it re-enters the boundary
    tampered = build(good).model_dump(mode="json")
    tampered["rates"][0]["rate"] = "1"
    with pytest.raises((ValidationError, ValueError)):
        FxSnapshot.model_validate(tampered)
    with pytest.raises((ValidationError, ValueError)):
        FxSnapshot.model_validate({**build(good).model_dump(mode="json"), "snapshot_id": "fx_forged"})
    # rates are Decimal end to end: a float never enters
    with pytest.raises((ValidationError, ValueError, TypeError)):
        build({"USD/JPY": 150.0})  # type: ignore[dict-item]
    # no AI/MCP path supplies the rate: the tool is not registered, and an intent cannot carry one (extra='forbid')
    p = platform
    ident = p.issue_agent()
    for tool in ("set_fx_rate", "ingest_fx_snapshot", "override_fx"):
        res = p.tool_call(ident, tool, {"pair": "USD/JPY", "rate": "1"})
        assert not res.ok and res.error_code == "TOOL_NOT_REGISTERED"
    res = p.tool_call(ident, "submit_trade_intent", {"intent": {**p.make_intent(), "fx_rate": "1"}})
    assert not res.ok
    assert p.alerts.by_name("mcp.non_allowlisted_tool")


@pytest.mark.tc("TC-FX-004")
@pytest.mark.req("FR-05")
@pytest.mark.quartet("recovery")
@pytest.mark.env("sim")
def test_fresh_fx_snapshot_restores_numeric_nav(platform):  # type: ignore[no-untyped-def]
    """UNKNOWN (missing, then stale) -> a fresh snapshot ingested through the store restores a numeric NAV; the audit trail shows the ingests under one correlation id and the store never serves a snapshot beyond knowledge time."""
    p = platform
    p.ledger.register_instrument(_instrument("SIMJP1", "JPY"))
    p.ledger.apply_fill(ACCOUNT, "SIMJP1", Side.BUY, Decimal("10"), Decimal("15000"))
    p.ledger.mark("SIMJP1", Decimal("16000"))
    unknown = p.account_snapshot(ACCOUNT)
    assert unknown.valuation.status == NavStatus.UNKNOWN and unknown.valuation.reason_code == "RK-FX-MISSING"
    stale = FxSnapshot.build(
        base_currency="USD",
        rates={"USD/JPY": Decimal("150")},
        as_of=p.now - timedelta(seconds=30),
        source="sim-fx",
        provenance=Provenance.SIMULATED,
    )
    p.ingest_fx(stale, correlation_id="corr-fx-recovery")
    assert p.account_snapshot(ACCOUNT).valuation.reason_code == "RK-FX-STALE"
    fresh = FxSnapshot.build(
        base_currency="USD", rates={"USD/JPY": Decimal("150")}, as_of=p.now, source="sim-fx", provenance=Provenance.SIMULATED
    )
    p.ingest_fx(fresh, correlation_id="corr-fx-recovery")
    known = p.account_snapshot(ACCOUNT)
    assert known.valuation.status == NavStatus.KNOWN and known.valuation.fx_snapshot_id == fresh.snapshot_id
    base_cash = p.ledger.book(ACCOUNT).balances["USD"]
    assert known.nav == base_cash + Decimal("-1000.00") + Decimal("1066.67")
    assert known.cash == base_cash and known.cash_by_currency["JPY"] == Decimal("-150000")
    trail = p.audit.by_correlation("corr-fx-recovery")
    assert [e.action for e in trail].count("fx.snapshot.ingested") == 2
    assert p.audit.verify().ok
    # no look-ahead: a snapshot ingested after the reader's knowledge time is invisible to that reader
    earlier = p.fx.latest(as_of=p.now, knowledge_ts=p.now - timedelta(seconds=1))
    assert earlier is None
    assert p.fx.latest(as_of=p.now, knowledge_ts=p.now).snapshot_id == fresh.snapshot_id


@pytest.mark.tc("TC-FX-005")
@pytest.mark.req("FR-11")
@pytest.mark.quartet("negative")
@pytest.mark.env("sim")
def test_risk_engine_takes_fx_as_an_input_and_halts_when_it_is_missing_or_stale(platform):  # type: ignore[no-untyped-def]
    """The deterministic engine receives the FX snapshot as an argument (it never fetches one): an UNKNOWN account value, or an order it cannot express in the account base currency, is HALTED with RK-FX-MISSING / RK-FX-STALE / RK-FX-UNDEFINED, and the decision stays reproducible."""
    from risk_engine.engine import decide
    from rtcore.schemas.decision import Outcome

    p = platform
    vi = p.submit_intent(p.make_intent())
    p.intent_queue.pop()
    usd_acct, mkt = p.account_snapshot(ACCOUNT), p.market_snapshot(INSTRUMENT_ID)
    assert usd_acct.valuation.status == NavStatus.KNOWN  # a single-currency book needs no rate at all
    clean = decide(vi, usd_acct, mkt, p.policy, p.now)
    assert not any(c.startswith("RK-FX-") for c in clean.reason_codes) and clean.outcome != Outcome.HALTED

    # 1. the book itself cannot be valued (a JPY leg, no snapshot) -> HALTED on the account's own reason code
    p.ledger.register_instrument(_instrument("SIMJP1", "JPY"))
    p.ledger.apply_fill(ACCOUNT, "SIMJP1", Side.BUY, Decimal("10"), Decimal("15000"))
    p.ledger.mark("SIMJP1", Decimal("16000"))
    unknown_acct = p.account_snapshot(ACCOUNT)
    halted = decide(vi, unknown_acct, mkt, p.policy, p.now)
    assert halted.outcome == Outcome.HALTED and halted.reason_codes == ("RK-FX-MISSING",)
    assert decide(vi, unknown_acct, mkt, p.policy, p.now) == halted  # same inputs, same record: no clock, no I/O

    # 2. the order is priced in a currency the engine cannot convert with the snapshot it was handed
    foreign = mkt.model_copy(update={"instrument": _instrument(INSTRUMENT_ID, "JPY")})
    stale = FxSnapshot.build(
        base_currency="USD",
        rates={"USD/JPY": Decimal("150")},
        as_of=p.now - timedelta(seconds=3600),
        source="sim-fx",
        provenance=Provenance.SIMULATED,
    )
    assert decide(vi, usd_acct, foreign, p.policy, p.now, None, p.fx_max_age_s).reason_codes == ("RK-FX-MISSING",)
    assert decide(vi, usd_acct, foreign, p.policy, p.now, stale, None).reason_codes == ("RK-FX-UNDEFINED",)
    stale_decision = decide(vi, usd_acct, foreign, p.policy, p.now, stale, p.fx_max_age_s)
    assert stale_decision.outcome == Outcome.HALTED and stale_decision.reason_codes == ("RK-FX-STALE",)
    fresh = FxSnapshot.build(
        base_currency="USD", rates={"USD/JPY": Decimal("150")}, as_of=p.now, source="sim-fx", provenance=Provenance.SIMULATED
    )
    with_fx = decide(vi, usd_acct, foreign, p.policy, p.now, fresh, p.fx_max_age_s)
    assert not any(code.startswith("RK-FX-") for code in with_fx.reason_codes)  # valued in USD, then judged there
