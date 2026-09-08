from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal

from rtcore.errors import FxUnavailable
from rtcore.ids import deterministic_id
from rtcore.money import ZERO, convert
from rtcore.schemas.account import (
    AccountMode,
    AccountSnapshot,
    EmergencyPolicy,
    KillSwitchFlags,
    NavStatus,
    OpenOrder,
    Position,
    TradingStatus,
    Valuation,
)
from rtcore.schemas.fx import FxSnapshot
from rtcore.schemas.intent import Side
from rtcore.schemas.market import InstrumentAttributes


@dataclass
class PositionState:
    instrument_id: str
    quantity: Decimal = ZERO
    average_price: Decimal = ZERO
    realized_pnl: Decimal = ZERO


@dataclass
class AccountBook:
    """Cash is a balance *per currency* (F-3): a JPY fill settles a JPY leg, and only FX turns the set into one number."""

    account_id: str
    tenant_id: str
    base_currency: str
    start_of_day_nav: Decimal
    start_of_week_nav: Decimal
    start_of_month_nav: Decimal
    peak_nav: Decimal
    balances: dict[str, Decimal] = field(default_factory=dict)
    positions: dict[str, PositionState] = field(default_factory=dict)
    recent_intent_hashes: list[str] = field(default_factory=list)
    order_signatures: list[tuple[datetime, str]] = field(default_factory=list)
    order_timestamps: list[datetime] = field(default_factory=list)
    fees_paid: Decimal = ZERO
    capital_in_use: Decimal = ZERO

    @property
    def cash(self) -> Decimal:
        """Base-currency cash. Other currencies are in ``balances`` and are only comparable through an FX snapshot."""
        return self.balances.get(self.base_currency, ZERO)

    @cash.setter
    def cash(self, value: Decimal) -> None:
        self.balances[self.base_currency] = value

    def credit(self, currency: str, amount: Decimal) -> None:
        self.balances[currency] = self.balances.get(currency, ZERO) + amount


class Ledger:
    """Positions are derived from fills; cash from fills and fees. Broker statement remains final truth [Source: 03].

    Every amount keeps the currency it was earned or paid in; nothing is converted at fill time. Conversion happens
    once, at valuation time, from an FX snapshot the caller supplies (``rtcore.money.convert``): the ledger performs
    no I/O and never invents a rate. When a rate needed to value the book is missing or stale the valuation is
    ``NavStatus.UNKNOWN`` with a reason code, and ``nav()`` raises rather than returning a number [F-3].
    """

    def __init__(self) -> None:
        self._books: dict[str, AccountBook] = {}
        self._marks: dict[str, Decimal] = {}
        self._instruments: dict[str, InstrumentAttributes] = {}

    def open_account(self, account_id: str, tenant_id: str, base_currency: str, cash: Decimal) -> AccountBook:
        book = AccountBook(
            account_id=account_id,
            tenant_id=tenant_id,
            base_currency=base_currency,
            start_of_day_nav=cash,
            start_of_week_nav=cash,
            start_of_month_nav=cash,
            peak_nav=cash,
            balances={base_currency: cash},
        )
        self._books[account_id] = book
        return book

    def book(self, account_id: str) -> AccountBook:
        return self._books[account_id]

    def register_instrument(self, inst: InstrumentAttributes) -> None:
        self._instruments[inst.instrument_id] = inst

    def mark(self, instrument_id: str, price: Decimal) -> None:
        self._marks[instrument_id] = price

    def currency_of(self, instrument_id: str, book: AccountBook) -> str:
        """Settlement/trading currency of the instrument; the account base currency when the master row is unknown."""
        inst = self._instruments.get(instrument_id)
        return inst.currency if inst else book.base_currency

    def apply_fill(
        self, account_id: str, instrument_id: str, side: Side, quantity: Decimal, price: Decimal, fee: Decimal = ZERO
    ) -> PositionState:
        book = self._books[account_id]
        pos = book.positions.setdefault(instrument_id, PositionState(instrument_id=instrument_id))
        signed = quantity if side in (Side.BUY, Side.BUY_TO_COVER) else -quantity
        if pos.quantity == ZERO or (pos.quantity > ZERO) == (signed > ZERO):
            total = abs(pos.quantity) + quantity
            pos.average_price = ((abs(pos.quantity) * pos.average_price) + quantity * price) / total
        else:
            closing = min(quantity, abs(pos.quantity))
            direction = Decimal(1) if pos.quantity > ZERO else Decimal(-1)
            pos.realized_pnl += (price - pos.average_price) * closing * direction
            if quantity > abs(pos.quantity):
                pos.average_price = price
        pos.quantity += signed
        if pos.quantity == ZERO:
            pos.average_price = ZERO
        # The cash leg settles in the instrument's currency. Fees are charged by the broker in the same currency
        # (ADR-008); a per-broker fee/accrual model per currency is [Open: O-29].
        book.credit(self.currency_of(instrument_id, book), -(signed * price + fee))
        book.fees_paid += fee
        return pos

    def record_intent_hash(self, account_id: str, intent_hash: str, keep: int = 500) -> None:
        book = self._books[account_id]
        book.recent_intent_hashes.append(intent_hash)
        del book.recent_intent_hashes[:-keep]

    def record_order_ts(self, account_id: str, ts: datetime, signature: str | None = None) -> None:
        book = self._books[account_id]
        book.order_timestamps.append(ts)
        if signature is not None:
            book.order_signatures.append((ts, signature))

    # --- valuation -------------------------------------------------------------------------------------------
    def _position_legs(self, book: AccountBook) -> tuple[tuple[Decimal, str], ...]:
        """Marked value of every open position, in the instrument's own currency."""
        return tuple(
            (p.quantity * self._marks.get(i, p.average_price), self.currency_of(i, book))
            for i, p in book.positions.items()
            if p.quantity != ZERO
        )

    def _legs(self, book: AccountBook) -> tuple[tuple[Decimal, str], ...]:
        """Every amount that makes up the NAV, with its own currency: cash balances first, then marked positions."""
        return tuple((amount, currency) for currency, amount in book.balances.items()) + self._position_legs(book)

    def _to_base(
        self, book: AccountBook, amount: Decimal, currency: str, fx: FxSnapshot | None, now: datetime | None, max_age_s: Decimal | None
    ) -> Decimal:
        return convert(amount, currency, book.base_currency, fx, now=now, max_age_s=max_age_s)

    def valuation(
        self,
        account_id: str,
        fx: FxSnapshot | None = None,
        *,
        now: datetime | None = None,
        max_age_s: Decimal | None = None,
    ) -> Valuation:
        """NAV in the base currency, or a typed UNKNOWN naming the reason code. Never raises for a missing rate."""
        book = self._books[account_id]
        try:
            value = self._nav(book, fx, now, max_age_s)
        except FxUnavailable as exc:
            return Valuation(
                status=NavStatus.UNKNOWN,
                currency=book.base_currency,
                value=None,
                reason_code=exc.reason_code,
                detail=str(exc),
                fx_snapshot_id=fx.snapshot_id if fx else None,
            )
        return Valuation(
            status=NavStatus.KNOWN,
            currency=book.base_currency,
            value=value,
            detail=f"{len(book.balances)} cash leg(s), {len(book.positions)} position(s)",
            fx_snapshot_id=fx.snapshot_id if fx else None,
        )

    def _nav(self, book: AccountBook, fx: FxSnapshot | None, now: datetime | None, max_age_s: Decimal | None) -> Decimal:
        return sum((self._to_base(book, amount, ccy, fx, now, max_age_s) for amount, ccy in self._legs(book)), ZERO)

    def nav(
        self,
        account_id: str,
        fx: FxSnapshot | None = None,
        *,
        now: datetime | None = None,
        max_age_s: Decimal | None = None,
    ) -> Decimal:
        """NAV in the base currency; raises ``FxUnavailable`` when a required rate is missing, stale or unbudgeted."""
        return self._nav(self._books[account_id], fx, now, max_age_s)

    def gross_exposure(
        self,
        account_id: str,
        fx: FxSnapshot | None = None,
        *,
        now: datetime | None = None,
        max_age_s: Decimal | None = None,
    ) -> Decimal:
        """Sum of |position market value| expressed in the base currency (cash legs excluded); raises when unknown."""
        book = self._books[account_id]
        return sum((abs(self._to_base(book, value, ccy, fx, now, max_age_s)) for value, ccy in self._position_legs(book)), ZERO)

    def roll_day(
        self,
        account_id: str,
        fx: FxSnapshot | None = None,
        *,
        now: datetime | None = None,
        max_age_s: Decimal | None = None,
    ) -> None:
        book = self._books[account_id]
        book.start_of_day_nav = self.nav(account_id, fx, now=now, max_age_s=max_age_s)

    def positions(
        self,
        account_id: str,
        fx: FxSnapshot | None = None,
        *,
        now: datetime | None = None,
        max_age_s: Decimal | None = None,
    ) -> tuple[Position, ...]:
        """Positions keep their instrument currency; ``base_market_value`` is the converted value, None if unknown."""
        book = self._books[account_id]
        out = []
        for i, p in book.positions.items():
            if p.quantity == ZERO:
                continue
            inst = self._instruments.get(i)
            currency = inst.currency if inst else book.base_currency
            market_value = p.quantity * self._marks.get(i, p.average_price)
            try:
                base_value: Decimal | None = self._to_base(book, market_value, currency, fx, now, max_age_s)
            except FxUnavailable:
                base_value = None
            out.append(
                Position(
                    instrument_id=i,
                    quantity=p.quantity,
                    average_price=p.average_price,
                    market_value=market_value,
                    base_market_value=base_value,
                    sector=inst.sector if inst else "UNKNOWN",
                    country=inst.country if inst else "UNKNOWN",
                    currency=currency,
                )
            )
        return tuple(out)

    def snapshot(
        self,
        account_id: str,
        *,
        now: datetime,
        mode: AccountMode,
        trading_status: TradingStatus,
        jurisdiction: str,
        customer_type: str,
        authorised_strategies: tuple[str, ...],
        open_orders: tuple[OpenOrder, ...],
        kill_switch: KillSwitchFlags,
        emergency_policy: EmergencyPolicy = EmergencyPolicy.CANCEL_ONLY,
        capital_envelope: Decimal | None = None,
        autonomy_suspended: bool = False,
        liquidation_policy_ref: str | None = None,
        correlation_groups: dict[str, tuple[str, ...]] | None = None,
        fx: FxSnapshot | None = None,
        fx_max_age_s: Decimal | None = None,
    ) -> AccountSnapshot:
        """Account snapshot in the base currency. With an UNKNOWN valuation the money fields are ZERO and the
        typed ``valuation`` carries the reason: the risk engine fails closed on it rather than reading a number
        that was never computed [F-3]."""
        book = self._books[account_id]
        valuation = self.valuation(account_id, fx, now=now, max_age_s=fx_max_age_s)
        known = valuation.status == NavStatus.KNOWN
        nav = valuation.value if valuation.value is not None else ZERO
        if known:
            book.peak_nav = max(book.peak_nav, nav)
        positions = self.positions(account_id, fx, now=now, max_age_s=fx_max_age_s)
        gross = sum((abs(p.base_market_value) for p in positions if p.base_market_value is not None), ZERO) if known else ZERO
        recent = [t for t in book.order_timestamps if (now - t).total_seconds() <= 60]
        signatures = tuple(sig for t, sig in book.order_signatures if (now - t).total_seconds() <= 60)
        snapshot_id = deterministic_id(
            "acs",
            account_id,
            now.isoformat(),
            str(nav),
            valuation.status.value,
            valuation.fx_snapshot_id or "-",
            len(positions),
            len(open_orders),
            kill_switch.canonical_hash(),
        )
        return AccountSnapshot(
            snapshot_id=snapshot_id,
            tenant_id=book.tenant_id,
            account_id=account_id,
            as_of=now,
            mode=mode,
            trading_status=trading_status,
            jurisdiction=jurisdiction,
            customer_type=customer_type,
            base_currency=book.base_currency,
            authorised_strategies=authorised_strategies,
            cash=book.cash,
            cash_by_currency=dict(book.balances),
            buying_power=max(book.cash, ZERO),
            nav=nav,
            valuation=valuation,
            peak_nav=book.peak_nav,
            # PnL is only meaningful against a known NAV; with an UNKNOWN valuation it is not shown as a number.
            daily_pnl=nav - book.start_of_day_nav if known else ZERO,
            weekly_pnl=nav - book.start_of_week_nav if known else ZERO,
            monthly_pnl=nav - book.start_of_month_nav if known else ZERO,
            positions=positions,
            open_orders=open_orders,
            orders_last_minute=len(recent),
            recent_intent_hashes=tuple(book.recent_intent_hashes),
            recent_order_signatures=signatures,
            kill_switch=kill_switch,
            emergency_policy=emergency_policy,
            capital_envelope=capital_envelope,
            capital_in_use=gross,
            correlation_groups=correlation_groups or {},
            autonomy_suspended=autonomy_suspended,
            liquidation_policy_ref=liquidation_policy_ref,
        )
