"""``decide`` — the deterministic pre-trade decision [Source: 05].

Evaluation order (fail-fast, but every cheap check is still evaluated so the record lists all
failing reasons) [Committee]: 1 authorisation/status -> 2 lists -> 3 session -> 4 freshness ->
instrument validity -> 5-9 sizing/exposure/leverage -> 10 collar, 13 liquidity, 14 volatility ->
11 duplicate, 12 rate -> 15 protective, 16 correlated -> mode/envelope semantics.

Outcome precedence: HALTED > REJECTED > REQUIRES_HUMAN_APPROVAL > APPROVED.
"""

from __future__ import annotations

import hashlib
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from rtcore.clock import age_seconds, ensure_utc
from rtcore.ids import deterministic_id
from rtcore.money import ZERO, pct
from rtcore.provenance import TRUSTED_FOR_DECISIONS, Provenance
from rtcore.schemas.account import AccountMode, AccountSnapshot, TradingStatus
from rtcore.schemas.decision import CheckResult, DecisionRecord, EvaluatedCheck, Outcome
from rtcore.schemas.intent import OrderType, Side, ValidatedIntent
from rtcore.schemas.market import DataQuality, MarketSnapshot, SessionState

from risk_engine.policy import FailAction, LimitScope, Metric, RiskPolicy, effective_limit


def _build_hash() -> str:
    """Hash of this package's source: identical builds yield identical ``engine_build_hash``."""
    digest = hashlib.sha256()
    for file in sorted(Path(__file__).parent.glob("*.py")):
        digest.update(file.name.encode())
        digest.update(file.read_bytes())
    return digest.hexdigest()[:16]


ENGINE_BUILD_HASH = _build_hash()

# Reason-code semantics. HALT reasons dominate; REJECT reasons next; APPROVAL reasons last.
HALT_CODES = frozenset({"RK-HALT-INPUT", "RK-HALT-KS", "RK-HALT-MODE"})


@dataclass(frozen=True)
class _Ctx:
    vi: ValidatedIntent
    acct: AccountSnapshot
    mkt: MarketSnapshot
    policy: RiskPolicy
    now: datetime
    scope: LimitScope

    @property
    def est_price(self) -> Decimal:
        i = self.vi.intent
        if i.limit_price is not None:
            return i.limit_price
        return self.mkt.reference_price

    @property
    def order_notional(self) -> Decimal:
        return self.vi.intent.quantity * self.est_price

    @property
    def is_buy(self) -> bool:
        return self.vi.intent.side in (Side.BUY, Side.BUY_TO_COVER)

    @property
    def signed_qty(self) -> Decimal:
        return self.vi.intent.quantity if self.is_buy else -self.vi.intent.quantity

    @property
    def is_risk_reducing(self) -> bool:
        """Closing order that does not flip the position (review P4; policy flag, [Committee] pending TRC)."""
        pos = self.acct.position_for(self.vi.intent.instrument_id)
        cur = pos.quantity if pos else ZERO
        if cur == ZERO:
            return False
        new = cur + self.signed_qty
        return abs(new) < abs(cur) and (new == ZERO or (new > ZERO) == (cur > ZERO))


def _ev(check: str, value: object, threshold: object, ok: bool, code: str | None = None) -> EvaluatedCheck:
    return EvaluatedCheck(
        check=check,
        value=str(value),
        threshold=str(threshold),
        result=CheckResult.PASS if ok else CheckResult.FAIL,
        reason_code=None if ok else code,
    )


def _ne(check: str, threshold: object = "n/a", code: str | None = None) -> EvaluatedCheck:
    return EvaluatedCheck(check=check, value="n/a", threshold=str(threshold), result=CheckResult.NOT_EVALUATED, reason_code=code)


def _limit(ctx: _Ctx, metric: Metric) -> Decimal | None:
    return effective_limit(ctx.policy, metric, ctx.scope, ctx.now).threshold


EXPOSURE_METRICS = frozenset(
    {
        Metric.MAX_POSITION_PER_INSTRUMENT,
        Metric.GROSS_EXPOSURE_PCT_NAV,
        Metric.NET_EXPOSURE_PCT_NAV,
        Metric.CONCENTRATION_SINGLE_NAME_PCT,
        Metric.CONCENTRATION_SECTOR_PCT,
        Metric.CONCENTRATION_COUNTRY_PCT,
        Metric.CONCENTRATION_CURRENCY_PCT,
        Metric.LEVERAGE_X,
        Metric.CORRELATED_GROUP_PCT_NAV,
    }
)


def _cap_check(ctx: _Ctx, name: str, metric: Metric, value: Decimal, code: str, current: Decimal | None = None) -> EvaluatedCheck:
    """Fail closed when the metric has no defined limit at any level [Committee; O-07].

    A risk-reducing order that leaves an exposure metric no worse than before passes that metric
    (``policy.risk_reducing_orders_exempt_exposure_caps``): the book must be allowed to shrink.
    """
    threshold = _limit(ctx, metric)
    if threshold is None:
        return EvaluatedCheck(check=name, value=str(value), threshold="UNDEFINED", result=CheckResult.FAIL, reason_code=f"{code}-UNDEFINED")
    if (
        ctx.policy.risk_reducing_orders_exempt_exposure_caps
        and metric in EXPOSURE_METRICS
        and ctx.is_risk_reducing
        and current is not None
        and value <= current
    ):
        return EvaluatedCheck(
            check=name,
            value=str(value),
            threshold=f"{threshold} (risk-reducing: {current} -> {value})",
            result=CheckResult.PASS,
            reason_code=None,
        )
    return _ev(name, value, threshold, value <= threshold, code)


# ---- 1 authorisation / trading status --------------------------------------------------
def chk_authorisation(ctx: _Ctx) -> list[EvaluatedCheck]:
    a, i = ctx.acct, ctx.vi.intent
    out = [
        _ev(
            "trading_status", a.trading_status.value, TradingStatus.ACTIVE.value, a.trading_status == TradingStatus.ACTIVE, "RK-AUTH-STATUS"
        ),
        _ev("account_match", i.account_id, a.account_id, i.account_id == a.account_id, "RK-AUTH-ACCOUNT"),
        _ev(
            "strategy_authorised",
            i.strategy_id,
            ",".join(a.authorised_strategies) or "(none)",
            i.strategy_id in a.authorised_strategies,
            "RK-AUTH-STRATEGY",
        ),
    ]
    # Ordered tuple, never a set: string order must be identical across interpreters (TC-RK-001 replica check).
    tradable_modes = (AccountMode.BACKTEST, AccountMode.PAPER, AccountMode.SUPERVISED, AccountMode.BOUNDED_AUTONOMOUS)
    if a.mode == AccountMode.HALTED:
        out.append(_ev("account_mode", a.mode.value, "not HALTED", False, "RK-HALT-MODE"))
    else:
        out.append(_ev("account_mode", a.mode.value, "|".join(m.value for m in tradable_modes), a.mode in tradable_modes, "RK-AUTH-MODE"))
    ks = a.kill_switch
    ks_hits = []
    if ks.platform:
        ks_hits.append("PLATFORM")
    if ks.tenant:
        ks_hits.append("TENANT")
    if ks.account:
        ks_hits.append("ACCOUNT")
    if i.strategy_id in ks.strategies:
        ks_hits.append(f"STRATEGY:{i.strategy_id}")
    if i.instrument_id in ks.assets or ctx.mkt.instrument.asset_class in ks.assets:
        ks_hits.append("ASSET")
    if i.venue in ks.venues:
        ks_hits.append(f"VENUE:{i.venue}")
    out.append(_ev("kill_switch", ",".join(ks_hits) or "none", "none", not ks_hits, "RK-HALT-KS"))
    out.append(_ev("intent_expiry", i.expiry.isoformat(), f"> {ctx.now.isoformat()}", i.expiry > ctx.now, "RK-EXPIRED"))
    out.append(_ev("tenant_match", ctx.vi.tenant_id, a.tenant_id, ctx.vi.tenant_id == a.tenant_id, "RK-AUTH-TENANT"))
    # Account snapshot must be recent (review P2): a stale snapshot is an unavailable input -> HALTED
    snap_age = Decimal(str(age_seconds(a.as_of, ctx.now)))
    budget = ctx.policy.account_snapshot_max_age_s
    out.append(_ev("account_snapshot_age_s", snap_age, budget, ZERO <= snap_age <= budget, "RK-HALT-INPUT"))
    out.append(_ev("nav_positive", a.nav, "> 0", a.nav > ZERO, "RK-NAV"))
    # An already-breached daily loss limit blocks new risk pre-trade too (review P14)
    loss_limit = _limit(ctx, Metric.DAILY_LOSS_LIMIT_PCT)
    loss_pct = pct(-a.daily_pnl, a.nav) if (a.daily_pnl < ZERO and a.nav > ZERO) else ZERO
    if loss_limit is None:
        out.append(
            EvaluatedCheck(
                check="daily_loss_breached",
                value=str(loss_pct),
                threshold="UNDEFINED",
                result=CheckResult.FAIL,
                reason_code="RK-LOSS-UNDEFINED",
            )
        )
    else:
        out.append(_ev("daily_loss_breached", loss_pct, loss_limit, loss_pct < loss_limit, "RK-LOSS"))
    return out


# ---- 2 lists (handled primarily by eligibility; risk re-checks instrument tradability) ----
def chk_lists(ctx: _Ctx) -> list[EvaluatedCheck]:
    inst = ctx.mkt.instrument
    return [
        _ev("instrument_tradable", inst.tradable, True, inst.tradable, "RK-LIST-TRADABLE"),
    ]


# ---- 3 market session ------------------------------------------------------------------
def chk_session(ctx: _Ctx) -> list[EvaluatedCheck]:
    s = ctx.mkt.session_state
    ok = s == SessionState.OPEN or (
        ctx.policy.allow_pre_open_limit_orders and s == SessionState.PRE_OPEN and ctx.vi.intent.order_type == OrderType.LIMIT
    )
    return [
        _ev("market_session", s.value, SessionState.OPEN.value, ok, "RK-SESS"),
        _ev("venue_health", ctx.mkt.venue_healthy, True, ctx.mkt.venue_healthy, "RK-SESS-VENUE"),
    ]


# ---- 4 data freshness ------------------------------------------------------------------
def chk_freshness(ctx: _Ctx) -> list[EvaluatedCheck]:
    m = ctx.mkt
    budget = ctx.policy.freshness_budget_s_by_asset_class.get(
        m.instrument.asset_class, ctx.policy.freshness_budget_s_by_asset_class.get("DEFAULT")
    )
    out: list[EvaluatedCheck] = []
    if budget is None:
        out.append(
            EvaluatedCheck(
                check="data_freshness", value="n/a", threshold="UNDEFINED", result=CheckResult.FAIL, reason_code="RK-FRESH-UNDEFINED"
            )
        )
    else:
        age = Decimal(str(age_seconds(m.market_ts, ctx.now)))
        # A market timestamp in the future relative to decision time is a clock/backdating anomaly.
        out.append(_ev("data_freshness_s", age, budget, ZERO <= age <= budget, "RK-FRESH"))
        ingest_age = Decimal(str(age_seconds(m.market_ts, m.ingest_ts)))
        out.append(_ev("ingest_after_market_ts", ingest_age, ">= 0", ingest_age >= ZERO, "RK-FRESH-CLOCK"))
    out.append(_ev("data_quality", m.quality.value, DataQuality.OK.value, m.quality == DataQuality.OK, "RK-FRESH-QUALITY"))
    trusted = m.provenance in TRUSTED_FOR_DECISIONS
    out.append(
        _ev(
            "data_provenance",
            m.provenance.value,
            "|".join(p.value for p in (Provenance.LICENSED_FEED, Provenance.SIMULATED)),
            trusted,
            "RK-FRESH-PROV",
        )
    )
    out.append(
        _ev(
            "intent_market_ts_not_ahead",
            ctx.vi.intent.market_ts.isoformat(),
            f"<= {ctx.now.isoformat()}",
            ctx.vi.intent.market_ts <= ctx.now,
            "RK-FRESH-INTENT",
        )
    )
    return out


# ---- instrument validity ---------------------------------------------------------------
def chk_instrument(ctx: _Ctx) -> list[EvaluatedCheck]:
    i, inst = ctx.vi.intent, ctx.mkt.instrument
    q = i.quantity
    lot_ok = (q % inst.lot_size) == ZERO
    tick_ok = True
    for px in (i.limit_price, i.stop_price):
        if px is not None and (px % inst.tick_size) != ZERO:
            tick_ok = False
    return [
        _ev("instrument_match", i.instrument_id, inst.instrument_id, i.instrument_id == inst.instrument_id, "RK-INSTR-ID"),
        _ev("venue_match", i.venue, inst.venue, i.venue == inst.venue, "RK-INSTR-VENUE"),
        _ev(
            "instrument_valid_at_ts",
            i.market_ts.isoformat(),
            f"[{inst.valid_from.isoformat()}, {inst.valid_to.isoformat() if inst.valid_to else 'open'})",
            inst.valid_at(i.market_ts),
            "RK-INSTR-PIT",
        ),
        _ev("lot_size", q, inst.lot_size, lot_ok, "RK-INSTR-LOT"),
        _ev("tick_size", f"{i.limit_price}/{i.stop_price}", inst.tick_size, tick_ok, "RK-INSTR-TICK"),
        _ev(
            "short_allowed",
            i.side.value,
            "shortable" if inst.shortable else "not shortable",
            i.side != Side.SELL_SHORT or inst.shortable,
            "RK-INSTR-SHORT",
        ),
    ]


# ---- 5 buying power --------------------------------------------------------------------
def chk_buying_power(ctx: _Ctx) -> list[EvaluatedCheck]:
    if not ctx.is_buy:
        return [
            EvaluatedCheck(
                check="buying_power",
                value=str(ctx.order_notional),
                threshold=str(ctx.acct.buying_power),
                result=CheckResult.PASS,
                reason_code=None,
            )
        ]
    return [_ev("buying_power", ctx.order_notional, ctx.acct.buying_power, ctx.order_notional <= ctx.acct.buying_power, "RK-BP")]


# ---- 6 position / notional caps --------------------------------------------------------
def chk_caps(ctx: _Ctx) -> list[EvaluatedCheck]:
    i = ctx.vi.intent
    out = [_cap_check(ctx, "max_notional_per_order", Metric.MAX_NOTIONAL_PER_ORDER, ctx.order_notional, "RK-CAP")]
    pos = ctx.acct.position_for(i.instrument_id)
    current_qty = pos.quantity if pos else ZERO
    projected_qty = current_qty + ctx.signed_qty
    projected_value = abs(projected_qty) * ctx.est_price
    out.append(
        _cap_check(
            ctx,
            "max_position_per_instrument",
            Metric.MAX_POSITION_PER_INSTRUMENT,
            projected_value,
            "RK-CAP-POS",
            current=abs(current_qty) * ctx.est_price,
        )
    )
    # Aggregate open same-side orders on the instrument: order splitting cannot evade the cap [Committee C4 abuse test].
    same_side_open = sum((o.notional for o in ctx.acct.open_orders if o.instrument_id == i.instrument_id and o.side == i.side), ZERO)
    out.append(_cap_check(ctx, "aggregate_open_notional", Metric.MAX_NOTIONAL_PER_ORDER, same_side_open + ctx.order_notional, "RK-CAP-AGG"))
    return out


# ---- 7 gross / net exposure ------------------------------------------------------------
def _book(ctx: _Ctx, *, include_order: bool) -> dict[str, tuple[Decimal, str, str, str]]:
    """instrument -> (market_value, sector, country, currency) including open orders as if filled (review P3)."""
    book: dict[str, tuple[Decimal, str, str, str]] = {
        p.instrument_id: (p.market_value, p.sector, p.country, p.currency) for p in ctx.acct.positions
    }
    inst = ctx.mkt.instrument
    for o in ctx.acct.open_orders:
        mv, sector, country, ccy = book.get(
            o.instrument_id,
            (
                ZERO,
                inst.sector if o.instrument_id == inst.instrument_id else "UNKNOWN",
                inst.country if o.instrument_id == inst.instrument_id else "UNKNOWN",
                inst.currency,
            ),
        )
        signed = o.notional if o.side in (Side.BUY, Side.BUY_TO_COVER) else -o.notional
        book[o.instrument_id] = (mv + signed, sector, country, ccy)
    if include_order:
        mv, sector, country, ccy = book.get(inst.instrument_id, (ZERO, inst.sector, inst.country, inst.currency))
        book[inst.instrument_id] = (mv + ctx.signed_qty * ctx.est_price, sector, country, ccy)
    return book


def _projected_positions(ctx: _Ctx) -> dict[str, tuple[Decimal, str, str, str]]:
    return _book(ctx, include_order=True)


def _current_positions(ctx: _Ctx) -> dict[str, tuple[Decimal, str, str, str]]:
    return _book(ctx, include_order=False)


def _gross(book: dict[str, tuple[Decimal, str, str, str]]) -> Decimal:
    return sum((abs(v[0]) for v in book.values()), ZERO)


def chk_exposure(ctx: _Ctx) -> list[EvaluatedCheck]:
    book, cur = _projected_positions(ctx), _current_positions(ctx)
    nav = ctx.acct.nav
    if nav <= ZERO:
        return [
            EvaluatedCheck(
                check="gross_exposure_pct_nav", value="n/a", threshold="NAV must be positive", result=CheckResult.FAIL, reason_code="RK-NAV"
            )
        ]
    gross, net = _gross(book), sum((v[0] for v in book.values()), ZERO)
    gross_cur, net_cur = _gross(cur), sum((v[0] for v in cur.values()), ZERO)
    return [
        _cap_check(ctx, "gross_exposure_pct_nav", Metric.GROSS_EXPOSURE_PCT_NAV, pct(gross, nav), "RK-EXP", current=pct(gross_cur, nav)),
        _cap_check(
            ctx, "net_exposure_pct_nav", Metric.NET_EXPOSURE_PCT_NAV, pct(abs(net), nav), "RK-EXP-NET", current=pct(abs(net_cur), nav)
        ),
    ]


# ---- 8 concentration -------------------------------------------------------------------
def _conc(
    book: dict[str, tuple[Decimal, str, str, str]], inst_id: str, sector: str, country: str, ccy: str
) -> tuple[Decimal, Decimal, Decimal, Decimal]:
    single = abs(book.get(inst_id, (ZERO, "", "", ""))[0])
    by_sector = sum((abs(v[0]) for v in book.values() if v[1] == sector), ZERO)
    by_country = sum((abs(v[0]) for v in book.values() if v[2] == country), ZERO)
    by_ccy = sum((abs(v[0]) for v in book.values() if v[3] == ccy), ZERO)
    return single, by_sector, by_country, by_ccy


def chk_concentration(ctx: _Ctx) -> list[EvaluatedCheck]:
    book, cur = _projected_positions(ctx), _current_positions(ctx)
    nav = ctx.acct.nav
    if nav <= ZERO:
        return [
            EvaluatedCheck(
                check="concentration_single_name_pct",
                value="n/a",
                threshold="NAV must be positive",
                result=CheckResult.FAIL,
                reason_code="RK-NAV",
            )
        ]
    inst = ctx.mkt.instrument
    single, by_sector, by_country, by_ccy = _conc(book, inst.instrument_id, inst.sector, inst.country, inst.currency)
    c_single, c_sector, c_country, c_ccy = _conc(cur, inst.instrument_id, inst.sector, inst.country, inst.currency)
    return [
        _cap_check(
            ctx,
            "concentration_single_name_pct",
            Metric.CONCENTRATION_SINGLE_NAME_PCT,
            pct(single, nav),
            "RK-CONC",
            current=pct(c_single, nav),
        ),
        _cap_check(
            ctx,
            "concentration_sector_pct",
            Metric.CONCENTRATION_SECTOR_PCT,
            pct(by_sector, nav),
            "RK-CONC-SECTOR",
            current=pct(c_sector, nav),
        ),
        _cap_check(
            ctx,
            "concentration_country_pct",
            Metric.CONCENTRATION_COUNTRY_PCT,
            pct(by_country, nav),
            "RK-CONC-COUNTRY",
            current=pct(c_country, nav),
        ),
        _cap_check(
            ctx, "concentration_currency_pct", Metric.CONCENTRATION_CURRENCY_PCT, pct(by_ccy, nav), "RK-CONC-CCY", current=pct(c_ccy, nav)
        ),
    ]


# ---- 9 leverage ------------------------------------------------------------------------
def chk_leverage(ctx: _Ctx) -> list[EvaluatedCheck]:
    if ctx.acct.nav <= ZERO:
        return [
            EvaluatedCheck(check="leverage_x", value="n/a", threshold="NAV must be positive", result=CheckResult.FAIL, reason_code="RK-NAV")
        ]
    lev = _gross(_projected_positions(ctx)) / ctx.acct.nav
    lev_cur = _gross(_current_positions(ctx)) / ctx.acct.nav
    return [_cap_check(ctx, "leverage_x", Metric.LEVERAGE_X, lev, "RK-LEV", current=lev_cur)]


# ---- 10 price collar / fat finger ------------------------------------------------------
def chk_collar(ctx: _Ctx) -> list[EvaluatedCheck]:
    i = ctx.vi.intent
    ref = ctx.mkt.reference_price
    px = i.limit_price if i.limit_price is not None else (i.stop_price if i.stop_price is not None else None)
    if px is None:
        return [
            EvaluatedCheck(
                check="price_collar_pct",
                value="market",
                threshold=str(_limit(ctx, Metric.PRICE_COLLAR_PCT)),
                result=CheckResult.PASS,
                reason_code=None,
            )
        ]
    deviation = pct(abs(px - ref), ref)
    return [_cap_check(ctx, "price_collar_pct", Metric.PRICE_COLLAR_PCT, deviation, "RK-COLLAR")]


# ---- 11 duplicate detection ------------------------------------------------------------
def chk_duplicate(ctx: _Ctx) -> list[EvaluatedCheck]:
    i = ctx.vi.intent
    dup = ctx.vi.intent_hash in ctx.acct.recent_intent_hashes
    econ = f"{i.instrument_id}|{i.side.value}|{i.order_type.value}|{i.quantity}|{i.limit_price}"
    econ_dup = econ in ctx.acct.recent_order_signatures  # same economics under a fresh intent_id (review P17)
    return [
        _ev("duplicate_intent", ctx.vi.intent_hash[:12], "not in recent intents", not dup, "RK-DUP"),
        _ev("duplicate_economics", econ, "not repeated within the duplicate window", not econ_dup, "RK-DUP"),
    ]


# ---- 12 rate / open orders --------------------------------------------------------------
def chk_rate(ctx: _Ctx) -> list[EvaluatedCheck]:
    return [
        _cap_check(ctx, "orders_per_minute", Metric.ORDERS_PER_MINUTE, Decimal(ctx.acct.orders_last_minute + 1), "RK-RATE"),
        _cap_check(ctx, "open_order_count", Metric.OPEN_ORDER_COUNT, Decimal(len(ctx.acct.open_orders) + 1), "RK-RATE-OPEN"),
    ]


# ---- 13 liquidity ----------------------------------------------------------------------
def chk_liquidity(ctx: _Ctx) -> list[EvaluatedCheck]:
    adv = ctx.mkt.average_daily_volume
    share = pct(ctx.vi.intent.quantity, adv) if adv > ZERO else Decimal("Infinity")
    code = "RK-LIQ" if ctx.policy.liquidity_action == FailAction.REJECT else "RK-LIQ-APPROVAL"
    return [_cap_check(ctx, "max_order_pct_adv", Metric.MAX_ORDER_PCT_ADV, share, code)]


# ---- 14 volatility regime --------------------------------------------------------------
def chk_volatility(ctx: _Ctx) -> list[EvaluatedCheck]:
    return [_cap_check(ctx, "volatility_regime_pct", Metric.VOLATILITY_REGIME_PCT, ctx.mkt.realized_volatility_pct, "RK-VOL-APPROVAL")]


# ---- 15 protective controls ------------------------------------------------------------
def chk_protective(ctx: _Ctx) -> list[EvaluatedCheck]:
    i = ctx.vi.intent
    if not ctx.policy.protective_stop_required:
        return [
            EvaluatedCheck(
                check="protective_stop", value=str(i.protective_stop), threshold="not required", result=CheckResult.PASS, reason_code=None
            )
        ]
    opening = i.side in (Side.BUY, Side.SELL_SHORT)
    if not opening:
        return [
            EvaluatedCheck(
                check="protective_stop", value=str(i.protective_stop), threshold="closing order", result=CheckResult.PASS, reason_code=None
            )
        ]
    code = "RK-PROT" if ctx.policy.protective_stop_action == FailAction.REJECT else "RK-PROT-APPROVAL"
    present = i.protective_stop is not None
    sane = True
    if present and i.protective_stop is not None:
        sane = (i.protective_stop < ctx.est_price) if i.side == Side.BUY else (i.protective_stop > ctx.est_price)
        distance = pct(abs(i.protective_stop - ctx.est_price), ctx.est_price)
        sane = sane and distance <= ctx.policy.max_protective_stop_distance_pct
    return [
        _ev(
            "protective_stop",
            i.protective_stop,
            f"present, on the loss side, within {ctx.policy.max_protective_stop_distance_pct}% of entry",
            present and sane,
            code,
        )
    ]


# ---- 16 correlated-risk limits ---------------------------------------------------------
def chk_correlated(ctx: _Ctx) -> list[EvaluatedCheck]:
    inst_id = ctx.vi.intent.instrument_id
    groups = [g for g, members in ctx.acct.correlation_groups.items() if inst_id in members]
    if not groups:
        return [
            EvaluatedCheck(
                check="correlated_group_pct_nav",
                value="0",
                threshold=str(_limit(ctx, Metric.CORRELATED_GROUP_PCT_NAV)),
                result=CheckResult.PASS,
                reason_code=None,
            )
        ]
    book = _projected_positions(ctx)
    current_book = _current_positions(ctx)
    out = []
    for g in groups:
        members = ctx.acct.correlation_groups[g]
        exposure = sum((abs(book[m][0]) for m in members if m in book), ZERO)
        current = sum((abs(current_book[m][0]) for m in members if m in current_book), ZERO)
        out.append(
            _cap_check(
                ctx,
                f"correlated_group_pct_nav[{g}]",
                Metric.CORRELATED_GROUP_PCT_NAV,
                pct(exposure, ctx.acct.nav),
                "RK-CORR",
                current=pct(current, ctx.acct.nav),
            )
        )
    return out


# ---- mode / envelope semantics [Committee C1 §1, C4] ------------------------------------
def chk_mode_semantics(ctx: _Ctx) -> list[EvaluatedCheck]:
    a = ctx.acct
    out: list[EvaluatedCheck] = []
    if a.mode == AccountMode.SUPERVISED:
        out.append(
            EvaluatedCheck(
                check="mode_requires_approval",
                value=a.mode.value,
                threshold="human approval per order",
                result=CheckResult.FAIL,
                reason_code="RK-MODE-SUPERVISED",
            )
        )
    if a.mode == AccountMode.BOUNDED_AUTONOMOUS:
        out.append(_ev("autonomy_not_suspended", a.autonomy_suspended, False, not a.autonomy_suspended, "RK-AUTONOMY-SUSPENDED"))
        if a.capital_envelope is None:
            out.append(
                EvaluatedCheck(
                    check="capital_envelope",
                    value="undefined",
                    threshold="required for autonomy",
                    result=CheckResult.FAIL,
                    reason_code="RK-ENVELOPE",
                )
            )
        else:
            projected = a.capital_in_use + ctx.order_notional
            out.append(_ev("capital_envelope", projected, a.capital_envelope, projected <= a.capital_envelope, "RK-ENVELOPE"))
    return out


CHECKS: tuple[Callable[[_Ctx], list[EvaluatedCheck]], ...] = (
    chk_authorisation,
    chk_lists,
    chk_session,
    chk_freshness,
    chk_instrument,
    chk_buying_power,
    chk_caps,
    chk_exposure,
    chk_concentration,
    chk_leverage,
    chk_collar,
    chk_liquidity,
    chk_volatility,
    chk_duplicate,
    chk_rate,
    chk_protective,
    chk_correlated,
    chk_mode_semantics,
)

APPROVAL_SUFFIXES = ("-APPROVAL",)
APPROVAL_CODES = frozenset({"RK-MODE-SUPERVISED", "RK-ENVELOPE", "RK-AUTONOMY-SUSPENDED"})


def _classify(code: str) -> Outcome:
    if code in HALT_CODES:
        return Outcome.HALTED
    if code in APPROVAL_CODES or code.endswith(APPROVAL_SUFFIXES):
        return Outcome.REQUIRES_HUMAN_APPROVAL
    return Outcome.REJECTED


def _halted(
    vi: ValidatedIntent | None,
    reason: str,
    detail: str,
    now: datetime,
    policy_version: str,
    acct_id: str,
    mkt_id: str,
    outcome: Outcome = Outcome.HALTED,
) -> DecisionRecord:
    intent_id = str(vi.intent.intent_id) if vi else "unknown"
    intent_hash = vi.intent_hash if vi else "unknown"
    correlation = vi.correlation_id if vi else "unknown"
    return DecisionRecord(
        decision_id=deterministic_id("dec", intent_hash, acct_id, mkt_id, policy_version, ENGINE_BUILD_HASH, reason, now.isoformat()),
        intent_id=intent_id,
        outcome=outcome,
        policy_version=policy_version,
        reason_codes=(reason,),
        evaluated=(
            EvaluatedCheck(
                check="inputs_available", value=detail, threshold="all inputs present", result=CheckResult.FAIL, reason_code=reason
            ),
        ),
        account_snapshot_id=acct_id,
        market_snapshot_id=mkt_id,
        decided_at=now,
        engine_build_hash=ENGINE_BUILD_HASH,
        correlation_id=correlation,
        intent_hash=intent_hash,
    )


def decide(
    validated_intent: ValidatedIntent | None,
    account_snapshot: AccountSnapshot | None,
    market_snapshot: MarketSnapshot | None,
    policy: RiskPolicy | None,
    now: datetime,
) -> DecisionRecord:
    """Pure decision. Any missing input -> HALTED (fail closed). Never raises for domain reasons."""
    now = ensure_utc(now)
    pv = policy.policy_version if policy else "unavailable"
    acct_id = account_snapshot.snapshot_id if account_snapshot else "unavailable"
    mkt_id = market_snapshot.snapshot_id if market_snapshot else "unavailable"
    if validated_intent is None:
        return _halted(None, "RK-HALT-INPUT", "intent missing", now, pv, acct_id, mkt_id)
    if policy is None:
        return _halted(validated_intent, "RK-HALT-INPUT", "policy unavailable", now, pv, acct_id, mkt_id)
    if account_snapshot is None:
        return _halted(validated_intent, "RK-HALT-INPUT", "account snapshot unavailable", now, pv, acct_id, mkt_id)
    if market_snapshot is None:
        return _halted(validated_intent, "RK-HALT-INPUT", "market snapshot unavailable", now, pv, acct_id, mkt_id)
    if not validated_intent.integrity_ok():
        # Tampered after validation: REJECTED with RK-INTEG (TC-RK-003); the pipeline raises an S1 alert on this code.
        return _halted(
            validated_intent,
            "RK-INTEG",
            "intent hash mismatch (tampered after validation)",
            now,
            pv,
            acct_id,
            mkt_id,
            outcome=Outcome.REJECTED,
        )

    scope = LimitScope(
        tenant_id=account_snapshot.tenant_id,
        account_id=account_snapshot.account_id,
        strategy_id=validated_intent.intent.strategy_id,
        instrument_id=validated_intent.intent.instrument_id,
    )
    ctx = _Ctx(validated_intent, account_snapshot, market_snapshot, policy, now, scope)

    evaluated: list[EvaluatedCheck] = []
    for check in CHECKS:
        try:
            evaluated.extend(check(ctx))
        except Exception as exc:  # noqa: BLE001 - an engine defect must never fail open
            return _halted(
                validated_intent, "RK-HALT-INPUT", f"engine error in {check.__name__}: {type(exc).__name__}", now, pv, acct_id, mkt_id
            )

    codes: list[str] = []
    for e in evaluated:
        if e.result == CheckResult.FAIL and e.reason_code and e.reason_code not in codes:
            codes.append(e.reason_code)

    outcome = Outcome.APPROVED
    rank = {Outcome.APPROVED: 0, Outcome.REQUIRES_HUMAN_APPROVAL: 1, Outcome.REJECTED: 2, Outcome.HALTED: 3}
    for code in codes:
        candidate = _classify(code)
        if rank[candidate] > rank[outcome]:
            outcome = candidate

    decision_id = deterministic_id(
        "dec", validated_intent.intent_hash, acct_id, mkt_id, policy.policy_version, ENGINE_BUILD_HASH, now.isoformat()
    )
    return DecisionRecord(
        decision_id=decision_id,
        intent_id=str(validated_intent.intent.intent_id),
        outcome=outcome,
        policy_version=policy.policy_version,
        reason_codes=tuple(codes),
        evaluated=tuple(evaluated),
        account_snapshot_id=acct_id,
        market_snapshot_id=mkt_id,
        decided_at=now,
        engine_build_hash=ENGINE_BUILD_HASH,
        correlation_id=validated_intent.correlation_id,
        intent_hash=validated_intent.intent_hash,
    )
