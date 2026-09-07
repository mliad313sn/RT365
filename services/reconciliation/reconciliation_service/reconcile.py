from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import Enum

from broker_adapters.base import BrokerStatement
from rtcore.money import ZERO
from rtcore.schemas.account import Position
from rtcore.schemas.base import StrictModel
from rtcore.schemas.order import OrderRecord, OrderState


class BreakType(str, Enum):
    TIMING = "TIMING"
    MISSING_FILL = "MISSING_FILL"
    DUPLICATE = "DUPLICATE"
    PRICE = "PRICE"
    QUANTITY = "QUANTITY"
    CASH = "CASH"
    STATUS = "STATUS"  # internal terminal state disagrees with the broker's (review OBJ-3)


class BreakSeverity(str, Enum):
    S1 = "S1"  # capital at risk / control bypass -> Kill Switch account
    S2 = "S2"  # degraded -> account to Supervised


class Break(StrictModel):
    break_id: str
    account_id: str
    break_type: BreakType
    severity: BreakSeverity
    instrument_id: str | None
    internal_value: str
    broker_value: str
    correlation_ids: tuple[str, ...]
    detected_at: datetime
    detail: str


class ReconciliationResult(StrictModel):
    account_id: str
    as_of: datetime
    positions_compared: int
    orders_compared: int
    breaks: tuple[Break, ...]

    @property
    def clean(self) -> bool:
        return not self.breaks


def reconcile(
    *,
    account_id: str,
    internal_positions: tuple[Position, ...],
    internal_orders: tuple[OrderRecord, ...],
    internal_cash: Decimal,
    statement: BrokerStatement,
    now: datetime,
    price_tolerance_pct: Decimal = Decimal("0.5"),
    cash_tolerance: Decimal = Decimal("0.01"),
) -> ReconciliationResult:
    breaks: list[Break] = []
    n = 0

    def add(
        bt: BreakType, sev: BreakSeverity, inst: str | None, internal: object, broker: object, corr: tuple[str, ...], detail: str
    ) -> None:
        nonlocal n
        n += 1
        breaks.append(
            Break(
                break_id=f"brk_{account_id}_{now.strftime('%Y%m%dT%H%M%S')}_{n}",
                account_id=account_id,
                break_type=bt,
                severity=sev,
                instrument_id=inst,
                internal_value=str(internal),
                broker_value=str(broker),
                correlation_ids=corr,
                detected_at=now,
                detail=detail,
            )
        )

    ipos = {p.instrument_id: p for p in internal_positions}
    bpos = {p.instrument_id: p for p in statement.positions}
    for inst in sorted(set(ipos) | set(bpos)):
        iq = ipos[inst].quantity if inst in ipos else ZERO
        bq = bpos[inst].quantity if inst in bpos else ZERO
        corr = tuple(o.command.correlation_id for o in internal_orders if o.command.instrument_id == inst)
        if iq != bq:
            add(BreakType.QUANTITY, BreakSeverity.S2, inst, iq, bq, corr, "position quantity differs from broker statement")
        elif inst in ipos and inst in bpos and bpos[inst].average_price > ZERO:
            diff = abs(ipos[inst].average_price - bpos[inst].average_price) / bpos[inst].average_price * Decimal("100")
            if diff > price_tolerance_pct:
                add(
                    BreakType.PRICE,
                    BreakSeverity.S2,
                    inst,
                    ipos[inst].average_price,
                    bpos[inst].average_price,
                    corr,
                    "average price differs beyond tolerance",
                )

    iorders = {o.client_order_id: o for o in internal_orders}
    borders = {o.client_order_id: o for o in statement.orders}
    # More than one live/filled order for the same intent is a duplicate whatever the broker says (review OBJ-1)
    by_intent: dict[str, list[OrderRecord]] = {}
    for o in internal_orders:
        if o.state in (OrderState.SUBMITTED, OrderState.ACKNOWLEDGED, OrderState.PARTIALLY_FILLED, OrderState.FILLED):
            by_intent.setdefault(o.command.intent_id, []).append(o)
    for intent_id, orders in by_intent.items():
        if len(orders) > 1:
            add(
                BreakType.DUPLICATE,
                BreakSeverity.S1,
                orders[0].command.instrument_id,
                len(orders),
                "1 expected",
                tuple(o.command.correlation_id for o in orders),
                f"{len(orders)} live orders for intent {intent_id}",
            )
    seen_refs: dict[str, str] = {}
    _closed = {"CANCELLED", "REJECTED"}
    _open = {"OPEN", "PARTIAL"}
    for coid, bo in borders.items():
        if bo.broker_order_ref in seen_refs and seen_refs[bo.broker_order_ref] != coid:
            add(
                BreakType.DUPLICATE,
                BreakSeverity.S1,
                None,
                seen_refs[bo.broker_order_ref],
                coid,
                (),
                "two client orders share a broker reference",
            )
        seen_refs[bo.broker_order_ref] = coid
        io = iorders.get(coid)
        if io is None:
            add(BreakType.DUPLICATE, BreakSeverity.S1, None, "none", coid, (), "broker order has no internal counterpart")
            continue
        # Status disagreement (review OBJ-3): an order we believe closed but the broker still works can hit the book
        # without any internal control seeing it -> S1. The reverse (broker closed, internal open) is adoptable by
        # ExecutionGateway.sync_statuses and is flagged S2 so that a stale adoption loop is still visible.
        if bo.status.upper() in _open and io.state in (OrderState.CANCELLED, OrderState.BROKER_REJECTED, OrderState.EXPIRED):
            add(
                BreakType.STATUS,
                BreakSeverity.S1,
                io.command.instrument_id,
                io.state.value,
                bo.status,
                (io.command.correlation_id,),
                "internal terminal state but the broker still reports the order live",
            )
        elif bo.status.upper() in _closed and io.state in (OrderState.SUBMITTED, OrderState.ACKNOWLEDGED, OrderState.PARTIALLY_FILLED):
            add(
                BreakType.STATUS,
                BreakSeverity.S2,
                io.command.instrument_id,
                io.state.value,
                bo.status,
                (io.command.correlation_id,),
                "broker closed the order but it is still open internally (sync_statuses should adopt)",
            )
        if bo.filled_quantity > io.filled_quantity:
            add(
                BreakType.MISSING_FILL,
                BreakSeverity.S2,
                io.command.instrument_id,
                io.filled_quantity,
                bo.filled_quantity,
                (io.command.correlation_id,),
                "broker reports fills not yet applied internally",
            )
        elif bo.filled_quantity < io.filled_quantity:
            add(
                BreakType.QUANTITY,
                BreakSeverity.S1,
                io.command.instrument_id,
                io.filled_quantity,
                bo.filled_quantity,
                (io.command.correlation_id,),
                "internal fills exceed broker fills",
            )
    for coid, io in iorders.items():
        if coid not in borders and io.state in (OrderState.ACKNOWLEDGED, OrderState.PARTIALLY_FILLED, OrderState.FILLED):
            add(
                BreakType.TIMING,
                BreakSeverity.S2,
                io.command.instrument_id,
                io.state.value,
                "absent",
                (io.command.correlation_id,),
                "internal order acknowledged but absent from statement",
            )
    if abs(internal_cash - statement.cash) > cash_tolerance:
        add(BreakType.CASH, BreakSeverity.S2, None, internal_cash, statement.cash, (), "cash differs from broker statement")
    return ReconciliationResult(
        account_id=account_id,
        as_of=now,
        positions_compared=len(set(ipos) | set(bpos)),
        orders_compared=len(set(iorders) | set(borders)),
        breaks=tuple(breaks),
    )
