"""Simulated sandbox broker [Committee; ADR-008 single code path].

Deterministic: fills depend only on the order sequence and the reference prices set by the
caller. Used for backtest (SIM), paper (PAPER) and the certification harness. It is *not* a
certified live broker; live adapters are separate, vault-backed classes [Open: MA broker contracts].
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal

from rtcore.money import ZERO
from rtcore.schemas.intent import OrderType, Side, TimeInForce

from broker_adapters.base import (
    AckStatus,
    BrokerAck,
    BrokerAdapter,
    BrokerFill,
    BrokerHealth,
    BrokerStatement,
    BrokerUnavailable,
    Capabilities,
    OrderStatus,
    StatementOrder,
    StatementPosition,
    SubmitRequest,
    VaultRef,
)


@dataclass
class _SimOrder:
    request: SubmitRequest
    broker_ref: str
    status: str = "OPEN"
    filled: Decimal = ZERO
    avg_price: Decimal = ZERO


@dataclass
class SimulatedBroker(BrokerAdapter):
    name: str = "sim-broker"
    spread_bps: Decimal = Decimal("5")
    fee_bps: Decimal = Decimal("1")  # commissions charged by the broker: costs stay inside the single code path (ADR-008)
    partial_fill_ratio: Decimal | None = None  # e.g. 0.5 -> first fill half, rest on next poll
    dedupe_client_order_id: bool = True
    known_instruments: dict[str, str] = field(default_factory=dict)  # instrument -> asset class
    venues: tuple[str, ...] = ("SIMX",)
    fail_submissions: bool = False  # chaos: broker down
    _connected: bool = False
    _vault_ref: VaultRef | None = None
    _prices: dict[str, Decimal] = field(default_factory=dict)
    _orders: dict[str, _SimOrder] = field(default_factory=dict)
    _pending_fills: list[BrokerFill] = field(default_factory=list)
    _fill_seq: int = 0
    _order_seq: int = 0
    _cash: dict[str, Decimal] = field(default_factory=dict)
    _all_fills: list[BrokerFill] = field(default_factory=list)
    _positions: dict[tuple[str, str], tuple[Decimal, Decimal]] = field(default_factory=dict)  # (acct, inst) -> (qty, avg)
    submissions_received: int = 0

    # --- lifecycle ---------------------------------------------------------------------------------
    def capabilities(self) -> Capabilities:
        return Capabilities(
            broker=self.name,
            venues=self.venues,
            asset_classes=tuple(sorted(set(self.known_instruments.values()))) or ("EQUITY",),
            order_types=(OrderType.MARKET, OrderType.LIMIT, OrderType.STOP, OrderType.STOP_LIMIT),
            time_in_force=(TimeInForce.DAY, TimeInForce.GTC, TimeInForce.IOC),
            supports_partial_fills=True,
            supports_cancel_replace=True,
            dedupes_client_order_id=self.dedupe_client_order_id,
            sandbox=True,
        )

    def connect(self, vault_ref: VaultRef, *, now: datetime) -> None:
        if not vault_ref.path.startswith("vault://"):
            raise BrokerUnavailable("credentials must be referenced from the vault (vault://...)")
        self._vault_ref = vault_ref
        self._connected = True

    def disconnect(self) -> None:
        self._connected = False

    def rotate_credentials(self, vault_ref: VaultRef, *, now: datetime) -> None:
        if self._vault_ref is None or vault_ref.version <= self._vault_ref.version:
            raise BrokerUnavailable("rotation requires a newer credential version")
        self._vault_ref = vault_ref

    def health(self, *, now: datetime) -> BrokerHealth:
        return BrokerHealth(
            connected=self._connected and not self.fail_submissions,
            latency_ms=Decimal("1"),
            last_heartbeat=now,
            credential_version=self._vault_ref.version if self._vault_ref else 0,
        )

    def set_reference_price(self, instrument_id: str, price: Decimal, *, now: datetime) -> None:
        self._prices[instrument_id] = price
        self._try_fill_resting(now)

    def fund(self, account_id: str, cash: Decimal) -> None:
        self._cash[account_id] = self._cash.get(account_id, ZERO) + cash

    # --- orders ------------------------------------------------------------------------------------
    def _require_connected(self) -> None:
        if not self._connected or self.fail_submissions:
            raise BrokerUnavailable(f"{self.name} not connected")

    def submit(self, request: SubmitRequest, *, now: datetime) -> BrokerAck:
        self._require_connected()
        self.submissions_received += 1
        if self.dedupe_client_order_id and request.client_order_id in self._orders:
            existing = self._orders[request.client_order_id]
            return BrokerAck(
                client_order_id=request.client_order_id,
                broker_order_ref=existing.broker_ref,
                status=AckStatus.DUPLICATE,
                reason="client_order_id already known",
                ts=now,
            )
        if request.instrument_id not in self.known_instruments:
            return BrokerAck(
                client_order_id=request.client_order_id,
                broker_order_ref=None,
                status=AckStatus.REJECTED,
                reason="UNKNOWN_INSTRUMENT",
                ts=now,
            )
        ok, why = self.supports(request.order_type, request.time_in_force, self.known_instruments[request.instrument_id], request.venue)
        if not ok:
            return BrokerAck(client_order_id=request.client_order_id, broker_order_ref=None, status=AckStatus.REJECTED, reason=why, ts=now)
        self._order_seq += 1
        ref = f"SIM-{self._order_seq:08d}"
        key = request.client_order_id if self.dedupe_client_order_id else f"{request.client_order_id}#{self._order_seq}"
        order = _SimOrder(request=request, broker_ref=ref)
        self._orders[key] = order
        self._try_fill(order, now)
        return BrokerAck(client_order_id=request.client_order_id, broker_order_ref=ref, status=AckStatus.ACKNOWLEDGED, ts=now)

    def _exec_price(self, req: SubmitRequest) -> Decimal | None:
        ref = self._prices.get(req.instrument_id)
        if ref is None:
            return None
        half_spread = ref * self.spread_bps / Decimal("20000")
        buy = req.side in (Side.BUY, Side.BUY_TO_COVER)
        px = ref + half_spread if buy else ref - half_spread
        if req.order_type == OrderType.MARKET:
            return px
        if req.order_type == OrderType.LIMIT and req.limit_price is not None:
            if (buy and req.limit_price >= px) or (not buy and req.limit_price <= px):
                return min(px, req.limit_price) if buy else max(px, req.limit_price)
            return None
        if req.order_type in (OrderType.STOP, OrderType.STOP_LIMIT) and req.stop_price is not None:
            triggered = (buy and ref >= req.stop_price) or (not buy and ref <= req.stop_price)
            if not triggered:
                return None
            if req.order_type == OrderType.STOP:
                return px
            if req.limit_price is not None and ((buy and req.limit_price >= px) or (not buy and req.limit_price <= px)):
                return px
        return None

    def _try_fill(self, order: _SimOrder, now: datetime) -> None:
        if order.status not in ("OPEN", "PARTIAL"):
            return
        px = self._exec_price(order.request)
        if px is None:
            if order.request.time_in_force == TimeInForce.IOC:
                order.status = "CANCELLED"
            return
        remaining = order.request.quantity - order.filled
        qty = remaining
        if self.partial_fill_ratio is not None and order.filled == ZERO and remaining > order.request.quantity * self.partial_fill_ratio:
            qty = (order.request.quantity * self.partial_fill_ratio).quantize(Decimal("1"))
            if qty <= ZERO:
                qty = remaining
        self._fill_seq += 1
        fee = (qty * px * self.fee_bps / Decimal("10000")).quantize(Decimal("0.01"))
        fill = BrokerFill(
            fill_ref=f"F-{self._fill_seq:08d}",
            client_order_id=order.request.client_order_id,
            broker_order_ref=order.broker_ref,
            quantity=qty,
            price=px,
            fee=fee,
            ts=now,
        )
        order.avg_price = ((order.avg_price * order.filled) + px * qty) / (order.filled + qty)
        order.filled += qty
        order.status = "FILLED" if order.filled >= order.request.quantity else "PARTIAL"
        self._pending_fills.append(fill)
        self._all_fills.append(fill)
        self._apply_position(order.request.account_id, order.request.instrument_id, order.request.side, qty, px)
        self._cash[order.request.account_id] = self._cash.get(order.request.account_id, ZERO) - fee

    def _apply_position(self, account_id: str, instrument_id: str, side: Side, qty: Decimal, px: Decimal) -> None:
        cur_qty, cur_avg = self._positions.get((account_id, instrument_id), (ZERO, ZERO))
        signed = qty if side in (Side.BUY, Side.BUY_TO_COVER) else -qty
        new_qty = cur_qty + signed
        if (cur_qty >= ZERO and signed > ZERO) or (cur_qty <= ZERO and signed < ZERO):
            new_avg = ((abs(cur_qty) * cur_avg) + qty * px) / (abs(cur_qty) + qty)
        else:
            new_avg = cur_avg if new_qty != ZERO and abs(new_qty) < abs(cur_qty) else (px if new_qty != ZERO else ZERO)
        self._positions[(account_id, instrument_id)] = (new_qty, new_avg)
        self._cash[account_id] = self._cash.get(account_id, ZERO) - signed * px

    def _try_fill_resting(self, now: datetime) -> None:
        for order in list(self._orders.values()):
            self._try_fill(order, now)

    def cancel(self, client_order_id: str, *, now: datetime) -> BrokerAck:
        self._require_connected()
        order = self._orders.get(client_order_id)
        if order is None:
            return BrokerAck(
                client_order_id=client_order_id, broker_order_ref=None, status=AckStatus.REJECTED, reason="UNKNOWN_ORDER", ts=now
            )
        if order.status == "FILLED":
            return BrokerAck(
                client_order_id=client_order_id,
                broker_order_ref=order.broker_ref,
                status=AckStatus.REJECTED,
                reason="ALREADY_FILLED",
                ts=now,
            )
        order.status = "CANCELLED"
        return BrokerAck(client_order_id=client_order_id, broker_order_ref=order.broker_ref, status=AckStatus.CANCELLED, ts=now)

    def replace(self, client_order_id: str, *, quantity: Decimal | None, limit_price: Decimal | None, now: datetime) -> BrokerAck:
        self._require_connected()
        order = self._orders.get(client_order_id)
        if order is None or order.status not in ("OPEN", "PARTIAL"):
            return BrokerAck(
                client_order_id=client_order_id, broker_order_ref=None, status=AckStatus.REJECTED, reason="NOT_REPLACEABLE", ts=now
            )
        updates: dict[str, Decimal] = {}
        if quantity is not None:
            updates["quantity"] = quantity
        if limit_price is not None:
            updates["limit_price"] = limit_price
        order.request = order.request.model_copy(update=updates)
        self._try_fill(order, now)
        return BrokerAck(client_order_id=client_order_id, broker_order_ref=order.broker_ref, status=AckStatus.REPLACED, ts=now)

    def poll_fills(self, *, now: datetime) -> tuple[BrokerFill, ...]:
        self._require_connected()
        out = tuple(self._pending_fills)
        self._pending_fills.clear()
        self._try_fill_resting(now)  # remaining quantity of partial fills arrives on the next poll
        return out

    def query_order(self, client_order_id: str, *, now: datetime) -> OrderStatus:
        self._require_connected()
        for key, o in self._orders.items():
            if o.request.client_order_id == client_order_id or key == client_order_id:
                return OrderStatus(
                    client_order_id=client_order_id, known=True, broker_order_ref=o.broker_ref, status=o.status, filled_quantity=o.filled
                )
        return OrderStatus(client_order_id=client_order_id, known=False)

    def statement(self, account_id: str, *, as_of: datetime) -> BrokerStatement:
        positions = tuple(
            StatementPosition(instrument_id=inst, quantity=qty, average_price=avg)
            for (acct, inst), (qty, avg) in sorted(self._positions.items())
            if acct == account_id and qty != ZERO
        )
        orders = tuple(
            StatementOrder(
                client_order_id=o.request.client_order_id, broker_order_ref=o.broker_ref, status=o.status, filled_quantity=o.filled
            )
            for o in self._orders.values()
            if o.request.account_id == account_id
        )
        fills = tuple(
            f
            for f in self._all_fills
            if any(o.broker_ref == f.broker_order_ref and o.request.account_id == account_id for o in self._orders.values())
        )
        return BrokerStatement(
            broker=self.name,
            account_id=account_id,
            as_of=as_of,
            cash=self._cash.get(account_id, ZERO),
            positions=positions,
            orders=orders,
            fills=fills,
        )

    # --- chaos helpers used by tests/certification --------------------------------------------------
    def inject_phantom_order(self, account_id: str, instrument_id: str, side: Side, qty: Decimal, price: Decimal, *, now: datetime) -> str:
        """Creates a broker-side order/fill with no internal counterpart (reconciliation DUPLICATE/MISSING_FILL test)."""
        self._order_seq += 1
        ref = f"SIM-{self._order_seq:08d}"
        req = SubmitRequest(
            client_order_id=f"PHANTOM-{ref}",
            account_id=account_id,
            venue=self.venues[0],
            instrument_id=instrument_id,
            side=side,
            order_type=OrderType.MARKET,
            quantity=qty,
            time_in_force=TimeInForce.DAY,
        )
        order = _SimOrder(request=req, broker_ref=ref)
        self._orders[req.client_order_id] = order
        self._prices.setdefault(instrument_id, price)
        self._try_fill(order, now)
        return ref
