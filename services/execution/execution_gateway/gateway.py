from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from typing import Any

from broker_adapters.base import AckStatus, BrokerAdapter, BrokerFill, BrokerUnavailable, SubmitRequest
from rtcore.envelope import make_event
from rtcore.errors import ControlDenied, RTError
from rtcore.ids import new_id
from rtcore.money import ZERO
from rtcore.planes import GUARD, Plane, PlaneGuard
from rtcore.schemas.events import OrderEvent
from rtcore.schemas.order import Fill, OrderCommand, OrderRecord, OrderState, client_order_id
from rtcore.statemachine import MonotonicStateMachine

from execution_gateway.lease import LeaseStore

_T = {
    OrderState.CREATED: {OrderState.SUBMITTED, OrderState.EXPIRED},
    OrderState.SUBMITTED: {
        OrderState.ACKNOWLEDGED,
        OrderState.BROKER_REJECTED,
        OrderState.PARTIALLY_FILLED,
        OrderState.FILLED,
        OrderState.CANCELLED,
        OrderState.EXPIRED,
    },
    OrderState.ACKNOWLEDGED: {
        OrderState.PARTIALLY_FILLED,
        OrderState.FILLED,
        OrderState.CANCELLED,
        OrderState.BROKER_REJECTED,
        OrderState.EXPIRED,
    },
    OrderState.PARTIALLY_FILLED: {OrderState.PARTIALLY_FILLED, OrderState.FILLED, OrderState.CANCELLED},
}
ORDER_MACHINE: MonotonicStateMachine[OrderState] = MonotonicStateMachine(
    {k: frozenset(v) for k, v in _T.items()},
    frozenset({OrderState.FILLED, OrderState.CANCELLED, OrderState.BROKER_REJECTED, OrderState.EXPIRED}),
)

OPEN_STATES = frozenset({OrderState.SUBMITTED, OrderState.ACKNOWLEDGED, OrderState.PARTIALLY_FILLED})


class StaleFencingToken(RTError):
    """Submission carried a fencing token that is not the current lease (ADR-002)."""


class DuplicateIntentOrder(ControlDenied):
    """A live order already exists for this intent: at most one live broker order per intent (review OBJ-1)."""


class ExecutionGateway:
    def __init__(
        self,
        *,
        adapters: dict[str, BrokerAdapter],
        lease_store: LeaseStore,
        audit: Callable[[str, str, str, str | None, dict[str, Any]], object],
        publish: Callable[[Any], object],
        alert: Callable[[str, dict[str, Any]], object] | None = None,
        broker_for_account: Callable[[str], str],
        guard: PlaneGuard = GUARD,
    ) -> None:
        self._adapters = adapters
        self._leases = lease_store
        self._guard = guard
        self._by_intent: dict[str, list[str]] = {}
        self._audit = audit  # (action, correlation_id, tenant, account, payload)
        self._publish = publish
        self._alert = alert or (lambda name, payload: None)
        self._broker_for_account = broker_for_account
        self._orders: dict[str, OrderRecord] = {}  # order_id -> record
        self._by_key: dict[str, str] = {}  # idempotency_key -> order_id
        self._by_client_id: dict[str, str] = {}
        self.duplicate_commands: int = 0

    # --- helpers ------------------------------------------------------------------------------------
    def _save(
        self, rec: OrderRecord, event: str, now: datetime, extra: dict[str, Any] | None = None, *, publish: bool = True
    ) -> OrderRecord:
        self._orders[rec.order_id] = rec
        cmd = rec.command
        fields: dict[str, Any] = {
            "order_id": rec.order_id,
            "client_order_id": rec.client_order_id,
            "state": rec.state.value,
            "fencing_token": rec.fencing_token,
            "idempotency_key": cmd.idempotency_key,
            "intent_id": cmd.intent_id,
            "decision_id": cmd.decision_id,
            "broker_order_ref": rec.broker_order_ref,
            "reason": rec.reject_reason,
        }
        fields.update(extra or {})
        payload = OrderEvent(**fields)
        self._audit(event, cmd.correlation_id, cmd.tenant_id, cmd.account_id, payload.model_dump(mode="json"))
        if publish:
            self._publish(
                make_event(
                    event,
                    correlation_id=cmd.correlation_id,
                    tenant=cmd.tenant_id,
                    account=cmd.account_id,
                    producer="execution_gateway",
                    payload=payload,
                    emitted_ts=now,
                )
            )
        return rec

    def _live_orders_for_intent(self, intent_id: str) -> list[OrderRecord]:
        return [
            self._orders[o]
            for o in self._by_intent.get(intent_id, [])
            if self._orders[o].state in OPEN_STATES or self._orders[o].filled_quantity > ZERO
        ]

    def _transition(self, rec: OrderRecord, nxt: OrderState, now: datetime, **updates: Any) -> OrderRecord:
        ORDER_MACHINE.assert_transition(rec.state, nxt)
        return rec.model_copy(update={"state": nxt, "history": (*rec.history, (nxt.value, now.isoformat())), "updated_at": now, **updates})

    # --- submission -----------------------------------------------------------------------------------
    def submit(self, command: OrderCommand, *, executor_id: str, fencing_token: int, now: datetime) -> OrderRecord:
        self._guard.check_caller(Plane.EXECUTION, "order_command")
        # Inbox: at-least-once delivery, exactly-once business effect (ADR-003, NFR-CON-01)
        existing_id = self._by_key.get(command.idempotency_key)
        if existing_id is not None:
            self.duplicate_commands += 1
            existing = self._orders[existing_id]
            self._audit(
                "order.command.duplicate_ignored",
                command.correlation_id,
                command.tenant_id,
                command.account_id,
                {"idempotency_key": command.idempotency_key, "order_id": existing_id},
            )
            return existing
        # Per-intent invariant: one live order per intent regardless of policy version (Trading review C2)
        live = self._live_orders_for_intent(command.intent_id)
        if live:
            self._audit(
                "order.command.duplicate_intent_rejected",
                command.correlation_id,
                command.tenant_id,
                command.account_id,
                {"intent_id": command.intent_id, "live_orders": [o.order_id for o in live]},
            )
            self._alert(
                "execution.duplicate_order",
                {
                    "account": command.account_id,
                    "intent_id": command.intent_id,
                    "strategy": command.strategy_id,
                    "order_id": live[0].order_id,
                },
            )
            raise DuplicateIntentOrder(f"intent {command.intent_id} already has a live order {live[0].order_id}")
        # Fencing: only the current lease holder may submit (ADR-002)
        if not self._leases.is_valid(command.account_id, fencing_token, now=now):
            self._alert("execution.stale_fencing_token", {"account": command.account_id, "executor": executor_id, "token": fencing_token})
            self._audit(
                "order.command.stale_token_rejected",
                command.correlation_id,
                command.tenant_id,
                command.account_id,
                {"executor": executor_id, "token": fencing_token},
            )
            raise StaleFencingToken(f"executor {executor_id} token {fencing_token} is not the current lease for {command.account_id}")
        broker = self._broker_for_account(command.account_id)
        adapter = self._adapters.get(broker)
        if adapter is None:
            raise ControlDenied(f"no certified adapter for broker {broker}")
        coid = client_order_id(command.idempotency_key)
        rec = OrderRecord(
            order_id=new_id("ord"),
            client_order_id=coid,
            command=command,
            state=OrderState.CREATED,
            fencing_token=fencing_token,
            history=((OrderState.CREATED.value, now.isoformat()),),
            updated_at=now,
        )
        self._by_key[command.idempotency_key] = rec.order_id
        self._by_client_id[coid] = rec.order_id
        self._by_intent.setdefault(command.intent_id, []).append(rec.order_id)
        self._save(rec, "order.created", now, publish=False)  # the Control plane already published order.command.v1
        req = SubmitRequest(
            client_order_id=coid,
            account_id=command.account_id,
            venue=command.venue,
            instrument_id=command.instrument_id,
            side=command.side,
            order_type=command.order_type,
            quantity=command.quantity,
            limit_price=command.limit_price,
            stop_price=command.stop_price,
            time_in_force=command.time_in_force,
        )
        rec = self._transition(rec, OrderState.SUBMITTED, now)
        self._save(rec, "order.submitted.v1", now)
        try:
            ack = adapter.submit(req, now=now)
        except BrokerUnavailable as exc:
            # Leave SUBMITTED: a retry with the same key is deduped; reconciliation confirms broker state.
            self._alert("broker.unavailable", {"broker": broker, "order_id": rec.order_id, "error": str(exc)})
            self._audit(
                "order.submit.broker_unavailable",
                command.correlation_id,
                command.tenant_id,
                command.account_id,
                {"order_id": rec.order_id, "error": str(exc)},
            )
            return rec
        if ack.status in (AckStatus.ACKNOWLEDGED, AckStatus.DUPLICATE):
            rec = self._transition(rec, OrderState.ACKNOWLEDGED, now, broker_order_ref=ack.broker_order_ref)
            rec = self._save(rec, "order.acked.v1", now, {"broker_dedupe": ack.status == AckStatus.DUPLICATE})
        else:
            rec = self._transition(rec, OrderState.BROKER_REJECTED, now, reject_reason=ack.reason)
            rec = self._save(rec, "order.rejected.v1", now)
        return rec

    def retry_submit(self, order_id: str, *, executor_id: str, fencing_token: int, now: datetime) -> OrderRecord:
        """Re-send a SUBMITTED-but-unacked order after a broker outage.

        The broker is queried first (review OBJ-2): if it already knows the client_order_id the order is adopted
        instead of re-sent, so brokers that do not dedupe never receive a second live order.
        """
        rec = self._orders[order_id]
        if rec.state != OrderState.SUBMITTED:
            return rec
        if not self._leases.is_valid(rec.command.account_id, fencing_token, now=now):
            raise StaleFencingToken("retry with stale token")
        adapter = self._adapters[self._broker_for_account(rec.command.account_id)]
        c = rec.command
        try:
            status = adapter.query_order(rec.client_order_id, now=now)
        except BrokerUnavailable:
            return rec
        if status.known:
            if status.status in ("OPEN", "PARTIAL", "FILLED"):
                rec = self._transition(
                    rec, OrderState.ACKNOWLEDGED, now, broker_order_ref=status.broker_order_ref, fencing_token=fencing_token
                )
                return self._save(rec, "order.acked.v1", now, {"retry": True, "broker_dedupe": True})
            if status.status == "CANCELLED":
                rec = self._transition(
                    rec, OrderState.CANCELLED, now, broker_order_ref=status.broker_order_ref, fencing_token=fencing_token
                )
                return self._save(rec, "order.cancelled.v1", now, {"retry": True})
            rec = self._transition(rec, OrderState.BROKER_REJECTED, now, reject_reason="rejected at broker", fencing_token=fencing_token)
            return self._save(rec, "order.rejected.v1", now, {"retry": True})
        req = SubmitRequest(
            client_order_id=rec.client_order_id,
            account_id=c.account_id,
            venue=c.venue,
            instrument_id=c.instrument_id,
            side=c.side,
            order_type=c.order_type,
            quantity=c.quantity,
            limit_price=c.limit_price,
            stop_price=c.stop_price,
            time_in_force=c.time_in_force,
        )
        ack = adapter.submit(req, now=now)
        if ack.status in (AckStatus.ACKNOWLEDGED, AckStatus.DUPLICATE):
            rec = self._transition(rec, OrderState.ACKNOWLEDGED, now, broker_order_ref=ack.broker_order_ref, fencing_token=fencing_token)
            return self._save(rec, "order.acked.v1", now, {"retry": True, "broker_dedupe": ack.status == AckStatus.DUPLICATE})
        rec = self._transition(rec, OrderState.BROKER_REJECTED, now, reject_reason=ack.reason)
        return self._save(rec, "order.rejected.v1", now, {"retry": True})

    # --- fills ------------------------------------------------------------------------------------------
    def apply_fill(self, bf: BrokerFill, *, now: datetime) -> OrderRecord | None:
        order_id = self._by_client_id.get(bf.client_order_id)
        if order_id is None:
            self._alert("execution.unknown_fill", {"client_order_id": bf.client_order_id, "broker_order_ref": bf.broker_order_ref})
            return None
        rec = self._orders[order_id]
        if any(f.broker_ref == bf.fill_ref for f in rec.fills):
            return rec  # duplicate fill delivery ignored
        fill = Fill(
            fill_id=new_id("fil"),
            order_id=order_id,
            client_order_id=bf.client_order_id,
            quantity=bf.quantity,
            price=bf.price,
            fee=bf.fee,
            fill_ts=bf.ts,
            broker_ref=bf.fill_ref,
        )
        filled = rec.filled_quantity + bf.quantity
        if filled > rec.command.quantity or rec.state in (
            OrderState.CANCELLED,
            OrderState.BROKER_REJECTED,
            OrderState.EXPIRED,
            OrderState.FILLED,
        ):
            # Over-fill or fill after a terminal state: the broker is the truth, but this is a break, not a crash.
            self._alert(
                "execution.unexpected_fill",
                {
                    "account": rec.command.account_id,
                    "order_id": order_id,
                    "state": rec.state.value,
                    "filled": str(filled),
                    "ordered": str(rec.command.quantity),
                },
            )
            self._audit(
                "order.fill.unexpected",
                rec.command.correlation_id,
                rec.command.tenant_id,
                rec.command.account_id,
                {"order_id": order_id, "fill_ref": bf.fill_ref, "state": rec.state.value},
            )
            return rec
        nxt = OrderState.FILLED if filled >= rec.command.quantity else OrderState.PARTIALLY_FILLED
        rec = self._transition(
            rec, nxt, now, filled_quantity=filled, fills=(*rec.fills, fill), broker_order_ref=rec.broker_order_ref or bf.broker_order_ref
        )
        return self._save(
            rec, "order.filled.v1", now, {"fill_quantity": fill.quantity, "fill_price": fill.price, "fill_ref": fill.broker_ref}
        )

    def poll_fills(self, *, now: datetime) -> tuple[OrderRecord, ...]:
        touched: list[OrderRecord] = []
        for adapter in self._adapters.values():
            try:
                fills = adapter.poll_fills(now=now)
            except BrokerUnavailable:
                continue
            for bf in fills:
                rec = self.apply_fill(bf, now=now)
                if rec is not None:
                    touched.append(rec)
        return tuple(touched)

    def sync_statuses(self, *, now: datetime) -> tuple[OrderRecord, ...]:
        """Adopt broker-side terminal states (IOC cancelled, rejected after ack) into internal orders (review OBJ-3)."""
        touched: list[OrderRecord] = []
        for rec in list(self._orders.values()):
            if rec.state not in OPEN_STATES:
                continue
            adapter = self._adapters.get(self._broker_for_account(rec.command.account_id))
            if adapter is None:
                continue
            try:
                st = adapter.query_order(rec.client_order_id, now=now)
            except BrokerUnavailable:
                continue
            if st.known and st.status == "CANCELLED" and rec.state != OrderState.CANCELLED:
                rec = self._transition(rec, OrderState.CANCELLED, now)
                touched.append(self._save(rec, "order.cancelled.v1", now, {"reason": "broker-side cancel adopted"}))
            elif st.known and st.status == "REJECTED" and rec.state == OrderState.ACKNOWLEDGED:
                rec = self._transition(rec, OrderState.BROKER_REJECTED, now, reject_reason="rejected after ack")
                touched.append(self._save(rec, "order.rejected.v1", now))
        return tuple(touched)

    def expire(self, *, now: datetime) -> tuple[OrderRecord, ...]:
        """SUBMITTED orders whose intent expiry passed without an ack are EXPIRED after the broker confirms it never saw them."""
        touched: list[OrderRecord] = []
        for rec in list(self._orders.values()):
            if rec.state != OrderState.SUBMITTED:
                continue
            adapter = self._adapters.get(self._broker_for_account(rec.command.account_id))
            try:
                st = adapter.query_order(rec.client_order_id, now=now) if adapter else None
            except BrokerUnavailable:
                continue
            if st is not None and not st.known:
                rec = self._transition(rec, OrderState.EXPIRED, now)
                touched.append(self._save(rec, "order.cancelled.v1", now, {"reason": "expired: never reached the broker"}))
        return tuple(touched)

    # --- cancellation ---------------------------------------------------------------------------------
    def cancel(self, order_id: str, *, fencing_token: int, now: datetime, reason: str) -> OrderRecord:
        rec = self._orders[order_id]
        if rec.state not in OPEN_STATES:
            return rec
        if not self._leases.is_valid(rec.command.account_id, fencing_token, now=now):
            raise StaleFencingToken("cancel with stale token")
        adapter = self._adapters[self._broker_for_account(rec.command.account_id)]
        if rec.state == OrderState.SUBMITTED:
            st = adapter.query_order(rec.client_order_id, now=now)
            if not st.known:
                rec = self._transition(rec, OrderState.CANCELLED, now)
                return self._save(rec, "order.cancelled.v1", now, {"reason": "never reached broker"})
        ack = adapter.cancel(rec.client_order_id, now=now)
        if ack.status == AckStatus.CANCELLED:
            rec = self._transition(rec, OrderState.CANCELLED, now)
            return self._save(rec, "order.cancelled.v1", now)
        if ack.status == AckStatus.REJECTED and ack.reason == "ALREADY_FILLED":
            self.poll_fills(now=now)
        return self._orders[order_id]

    def affected_accounts(
        self,
        *,
        account_id: str | None = None,
        tenant_id: str | None = None,
        strategy_id: str | None = None,
        instrument_id: str | None = None,
        venue: str | None = None,
    ) -> tuple[str, ...]:
        """Accounts holding open orders inside a Kill Switch scope (only their leases are preempted)."""
        out: set[str] = set()
        for rec in self._orders.values():
            c = rec.command
            if rec.state not in OPEN_STATES:
                continue
            if (account_id and c.account_id != account_id) or (tenant_id and c.tenant_id != tenant_id):
                continue
            if (
                (strategy_id and c.strategy_id != strategy_id)
                or (instrument_id and c.instrument_id != instrument_id)
                or (venue and c.venue != venue)
            ):
                continue
            out.add(c.account_id)
        return tuple(sorted(out))

    def cancel_all(
        self,
        *,
        account_id: str | None = None,
        tenant_id: str | None = None,
        strategy_id: str | None = None,
        instrument_id: str | None = None,
        venue: str | None = None,
        fencing_tokens: dict[str, int],
        now: datetime,
        reason: str,
    ) -> list[str]:
        """Used by the Kill Switch (P4). Caller supplies the current lease token per account."""
        cancelled: list[str] = []
        for rec in list(self._orders.values()):
            c = rec.command
            if rec.state not in OPEN_STATES:
                continue
            if account_id and c.account_id != account_id:
                continue
            if tenant_id and c.tenant_id != tenant_id:
                continue
            if strategy_id and c.strategy_id != strategy_id:
                continue
            if instrument_id and c.instrument_id != instrument_id:
                continue
            if venue and c.venue != venue:
                continue
            token = fencing_tokens.get(c.account_id)
            if token is None:
                continue
            out = self.cancel(rec.order_id, fencing_token=token, now=now, reason=reason)
            if out.state == OrderState.CANCELLED:
                cancelled.append(out.order_id)
        return cancelled

    # --- queries ---------------------------------------------------------------------------------------
    def get(self, order_id: str) -> OrderRecord:
        return self._orders[order_id]

    def by_key(self, idempotency_key: str) -> OrderRecord | None:
        oid = self._by_key.get(idempotency_key)
        return self._orders[oid] if oid else None

    def orders(self, account_id: str | None = None) -> tuple[OrderRecord, ...]:
        return tuple(o for o in self._orders.values() if account_id is None or o.command.account_id == account_id)

    def open_orders(self, account_id: str) -> tuple[OrderRecord, ...]:
        return tuple(o for o in self.orders(account_id) if o.state in OPEN_STATES)

    def filled_quantity(self, account_id: str) -> dict[str, Any]:
        out: dict[str, Any] = {}
        for o in self.orders(account_id):
            if o.filled_quantity > ZERO:
                out[o.client_order_id] = o.filled_quantity
        return out
