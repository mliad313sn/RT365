from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal

from rtcore.ids import deterministic_id
from rtcore.money import ZERO
from rtcore.schemas.account import AccountMode, AccountSnapshot, EmergencyPolicy, KillSwitchFlags, OpenOrder, Position, TradingStatus
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
    account_id: str
    tenant_id: str
    base_currency: str
    cash: Decimal
    start_of_day_nav: Decimal
    start_of_week_nav: Decimal
    start_of_month_nav: Decimal
    peak_nav: Decimal
    positions: dict[str, PositionState] = field(default_factory=dict)
    recent_intent_hashes: list[str] = field(default_factory=list)
    order_timestamps: list[datetime] = field(default_factory=list)
    capital_in_use: Decimal = ZERO


class Ledger:
    """Positions are derived from fills; cash from fills and fees. Broker statement remains final truth [Source: 03]."""

    def __init__(self) -> None:
        self._books: dict[str, AccountBook] = {}
        self._marks: dict[str, Decimal] = {}
        self._instruments: dict[str, InstrumentAttributes] = {}

    def open_account(self, account_id: str, tenant_id: str, base_currency: str, cash: Decimal) -> AccountBook:
        book = AccountBook(
            account_id=account_id,
            tenant_id=tenant_id,
            base_currency=base_currency,
            cash=cash,
            start_of_day_nav=cash,
            start_of_week_nav=cash,
            start_of_month_nav=cash,
            peak_nav=cash,
        )
        self._books[account_id] = book
        return book

    def book(self, account_id: str) -> AccountBook:
        return self._books[account_id]

    def register_instrument(self, inst: InstrumentAttributes) -> None:
        self._instruments[inst.instrument_id] = inst

    def mark(self, instrument_id: str, price: Decimal) -> None:
        self._marks[instrument_id] = price

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
        book.cash -= signed * price + fee
        return pos

    def record_intent_hash(self, account_id: str, intent_hash: str, keep: int = 500) -> None:
        book = self._books[account_id]
        book.recent_intent_hashes.append(intent_hash)
        del book.recent_intent_hashes[:-keep]

    def record_order_ts(self, account_id: str, ts: datetime) -> None:
        self._books[account_id].order_timestamps.append(ts)

    def nav(self, account_id: str) -> Decimal:
        book = self._books[account_id]
        mv = sum((p.quantity * self._marks.get(i, p.average_price) for i, p in book.positions.items()), ZERO)
        return book.cash + mv

    def roll_day(self, account_id: str) -> None:
        book = self._books[account_id]
        book.start_of_day_nav = self.nav(account_id)

    def positions(self, account_id: str) -> tuple[Position, ...]:
        book = self._books[account_id]
        out = []
        for i, p in book.positions.items():
            if p.quantity == ZERO:
                continue
            inst = self._instruments.get(i)
            out.append(
                Position(
                    instrument_id=i,
                    quantity=p.quantity,
                    average_price=p.average_price,
                    market_value=p.quantity * self._marks.get(i, p.average_price),
                    sector=inst.sector if inst else "UNKNOWN",
                    country=inst.country if inst else "UNKNOWN",
                    currency=inst.currency if inst else book.base_currency,
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
    ) -> AccountSnapshot:
        book = self._books[account_id]
        nav = self.nav(account_id)
        book.peak_nav = max(book.peak_nav, nav)
        positions = self.positions(account_id)
        gross = sum((abs(p.market_value) for p in positions), ZERO)
        recent = [t for t in book.order_timestamps if (now - t).total_seconds() <= 60]
        snapshot_id = deterministic_id(
            "acs", account_id, now.isoformat(), str(nav), len(positions), len(open_orders), kill_switch.canonical_hash()
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
            buying_power=max(book.cash, ZERO),
            nav=nav,
            peak_nav=book.peak_nav,
            daily_pnl=nav - book.start_of_day_nav,
            weekly_pnl=nav - book.start_of_week_nav,
            monthly_pnl=nav - book.start_of_month_nav,
            positions=positions,
            open_orders=open_orders,
            orders_last_minute=len(recent),
            recent_intent_hashes=tuple(book.recent_intent_hashes),
            kill_switch=kill_switch,
            emergency_policy=emergency_policy,
            capital_envelope=capital_envelope,
            capital_in_use=gross,
            correlation_groups=correlation_groups or {},
            autonomy_suspended=autonomy_suspended,
            liquidation_policy_ref=liquidation_policy_ref,
        )
