"""TC-RC — Reconciliation and break management [Source: 02, 03; FR-14; P6]. Broker statement is final truth."""

from __future__ import annotations

from decimal import Decimal

import pytest
from conftest import ACCOUNT, INSTRUMENT, OPS, TRADING_LEAD, agent
from reconciliation_service.reconcile import BreakSeverity, BreakType
from rtcore.errors import ControlDenied
from rtcore.schemas.account import AccountMode
from rtcore.schemas.intent import Side
from rtcore.schemas.order import OrderState


@pytest.mark.tc("TC-RC-001")
@pytest.mark.req("FR-14")
@pytest.mark.quartet("positive")
def test_positions_and_orders_match_statement(platform):  # type: ignore[no-untyped-def]
    """After fills, internal positions/orders/cash reconcile cleanly against the broker statement; completion audited."""
    platform.run_intent(platform.make_intent())
    platform.run_intent(platform.make_intent(quantity="50"))
    res = platform.reconcile()
    assert res.clean and res.positions_compared == 1 and res.orders_compared == 2
    assert platform.audit.by_action("reconciliation.completed.v1")[-1].payload["break_count"] == 0


@pytest.mark.tc("TC-RC-002")
@pytest.mark.req("FR-14")
@pytest.mark.quartet("negative")
def test_break_moves_account_to_supervised(autonomous):  # type: ignore[no-untyped-def]
    """A quantity/missing-fill break (S2) opens a ticket, raises an alert and drops the account from autonomy to Supervised."""
    p = autonomous
    p.run_intent(p.make_intent())
    pos = p.ledger.book(ACCOUNT).positions[INSTRUMENT]
    pos.quantity = pos.quantity - Decimal("10")  # internal drift vs broker
    res = p.reconcile()
    assert res.breaks and res.breaks[0].break_type == BreakType.QUANTITY and res.breaks[0].severity == BreakSeverity.S2
    assert p.accounts.get(ACCOUNT).mode == AccountMode.SUPERVISED and p.accounts.get(ACCOUNT).autonomy_suspended
    assert p.tickets.open_tickets(ACCOUNT) and p.alerts.by_name("reconciliation.break")
    assert p.audit.by_action("reconciliation.break.v1")


@pytest.mark.tc("TC-RC-003")
@pytest.mark.req("FR-14")
@pytest.mark.quartet("abuse")
def test_phantom_broker_order_is_s1_duplicate_and_kills_account(platform):  # type: ignore[no-untyped-def]
    """A broker-side order with no internal counterpart is classified DUPLICATE (S1) and triggers the account Kill Switch."""
    platform.run_intent(platform.make_intent())
    platform.broker.inject_phantom_order(ACCOUNT, INSTRUMENT, Side.BUY, Decimal("5"), Decimal("100"), now=platform.now)
    res = platform.reconcile()
    types = {b.break_type for b in res.breaks}
    assert BreakType.DUPLICATE in types and any(b.severity == BreakSeverity.S1 for b in res.breaks)
    assert platform.killswitch.flags_for(tenant_id="tenant-sim", account_id=ACCOUNT).account
    assert platform.alerts.by_name("execution.duplicate_order")


@pytest.mark.tc("TC-RC-004")
@pytest.mark.req("FR-14")
@pytest.mark.quartet("recovery")
def test_two_person_resolution(autonomous):  # type: ignore[no-untyped-def]
    """Ticket resolution needs two different authorised humans; agents and repeat resolvers are denied; audit records both."""
    p = autonomous
    p.run_intent(p.make_intent())
    p.ledger.book(ACCOUNT).positions[INSTRUMENT].quantity += Decimal("1")
    res = p.reconcile()
    ticket = p.tickets.open_tickets(ACCOUNT)[0]
    with pytest.raises(ControlDenied):
        p.tickets.resolve(ticket.ticket_id, agent(), resolution="x", now=p.now)
    first = p.tickets.resolve(ticket.ticket_id, OPS, resolution="timing: fill applied late", now=p.now)
    assert first.status.value == "PENDING_SECOND"
    with pytest.raises(ControlDenied):
        p.tickets.resolve(ticket.ticket_id, OPS, resolution="again", now=p.now)
    with pytest.raises(ControlDenied):  # same (1st) line as the first resolver
        p.tickets.resolve(ticket.ticket_id, TRADING_LEAD, resolution="same line", now=p.now)
    from conftest import RISK_OFFICER

    done = p.tickets.resolve(ticket.ticket_id, RISK_OFFICER, resolution="confirmed", now=p.now)
    assert done.status.value == "RESOLVED" and not p.tickets.open_tickets(ACCOUNT)
    assert len(res.breaks) == 1 and p.audit.by_action("reconciliation.ticket.updated")


@pytest.mark.tc("TC-RC-005")
@pytest.mark.req("FR-14")
@pytest.mark.quartet("negative")
def test_status_disagreement_is_a_break_and_broker_cancel_is_adopted(platform):  # type: ignore[no-untyped-def]
    """IOC cancelled at the broker is adopted into the internal state; internal CANCELLED vs broker OPEN is an S1 STATUS break (Trading review OBJ-3)."""
    from conftest import resting_limit_intent

    snap = platform.market_snapshot(INSTRUMENT)
    assert snap is not None
    px = (snap.reference_price * Decimal("0.97")).quantize(Decimal("0.01"))
    stop = (px * Decimal("0.98")).quantize(Decimal("0.01"))
    ioc = platform.run_intent(
        platform.make_intent(order_type="LIMIT", limit_price=str(px), time_in_force="IOC", protective_stop=str(stop), quantity="10")
    )
    assert ioc.order.state == OrderState.CANCELLED  # broker-side IOC cancel adopted by sync_statuses
    r = platform.run_intent(resting_limit_intent(platform))
    platform.gateway._orders[r.order.order_id] = r.order.model_copy(update={"state": OrderState.CANCELLED})  # internal drift
    res = platform.reconcile()
    assert any(b.break_type == BreakType.STATUS and b.severity == BreakSeverity.S1 for b in res.breaks)
