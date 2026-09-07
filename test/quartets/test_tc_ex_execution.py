"""TC-EX — Execution gateway: idempotency, fencing, failover [Source: 03; FR-13; ADR-002/003; R-02]."""

from __future__ import annotations

import pytest
from conftest import ACCOUNT, resting_limit_intent
from execution_gateway.gateway import StaleFencingToken
from rtcore.errors import PlaneViolation, TransitionError
from rtcore.planes import Plane, enter
from rtcore.schemas.order import OrderCommand, OrderState, idempotency_key
from web_bff.platform import build_sim_platform


def _command(p, result) -> OrderCommand:  # type: ignore[no-untyped-def]
    return result.order.command


@pytest.mark.tc("TC-EX-001")
@pytest.mark.req("FR-13")
@pytest.mark.quartet("positive")
def test_one_authorised_command_one_broker_order(platform):  # type: ignore[no-untyped-def]
    """One authorised order command -> exactly one broker order with client_order_id derived from the idempotency key."""
    r = platform.run_intent(platform.make_intent())
    assert r.order is not None and r.order.state == OrderState.FILLED
    assert r.order.command.idempotency_key == idempotency_key(r.order.command.intent_id, ACCOUNT, r.decision.policy_version)
    assert r.order.client_order_id.startswith("RT") and platform.broker.submissions_received == 1
    st = platform.broker.statement(ACCOUNT, as_of=platform.now)
    assert len(st.orders) == 1 and st.orders[0].client_order_id == r.order.client_order_id


@pytest.mark.tc("TC-EX-002")
@pytest.mark.req("FR-13")
@pytest.mark.quartet("negative")
def test_replayed_command_deduplicated(platform):  # type: ignore[no-untyped-def]
    """Redelivered command (at-least-once) -> inbox dedupe; no second broker submission; audit records the duplicate."""
    r = platform.run_intent(platform.make_intent())
    cmd = _command(platform, r)
    lease = platform.leases.current(ACCOUNT)
    with enter(Plane.CONTROL):
        again = platform.gateway.submit(cmd, executor_id=platform.executor_id, fencing_token=lease.fencing_token, now=platform.now)
        again2 = platform.gateway.submit(
            cmd.model_copy(update={"command_id": "cmd_redelivered"}),
            executor_id=platform.executor_id,
            fencing_token=lease.fencing_token,
            now=platform.now,
        )
    assert again.order_id == r.order.order_id == again2.order_id
    assert platform.broker.submissions_received == 1 and platform.gateway.duplicate_commands == 2
    assert platform.audit.by_action("order.command.duplicate_ignored")
    # replaying the whole pipeline for the same validated intent is also a no-op (inbox keyed by intent hash)
    again3 = platform.pipeline.process(r.validated_intent, now=platform.now)
    assert again3.order.order_id == r.order.order_id and platform.broker.submissions_received == 1


@pytest.mark.tc("TC-EX-003")
@pytest.mark.req("FR-13")
@pytest.mark.quartet("abuse")
def test_stale_fencing_token_rejected(platform):  # type: ignore[no-untyped-def]
    """A submission with a stale fencing token is rejected and alerted (S1); no broker order is created."""
    r = platform.run_intent(resting_limit_intent(platform))
    cmd = platform.pipeline.sign_command(
        _command(platform, r).model_copy(update={"idempotency_key": "new-key", "intent_id": "other-intent"})
    )
    old = platform.leases.current(ACCOUNT).fencing_token
    platform.leases.preempt(ACCOUNT, "executor-b", now=platform.now)
    with enter(Plane.CONTROL), pytest.raises(StaleFencingToken):
        platform.gateway.submit(cmd, executor_id="executor-a", fencing_token=old, now=platform.now)
    assert platform.alerts.by_name("execution.stale_fencing_token") and platform.broker.submissions_received == 1
    with enter(Plane.CONTROL), pytest.raises(StaleFencingToken):
        platform.gateway.cancel(r.order.order_id, fencing_token=old, now=platform.now, reason="stale")


@pytest.mark.tc("TC-EX-004")
@pytest.mark.req("FR-13")
@pytest.mark.quartet("recovery")
def test_failover_with_in_flight_order_single_broker_order(platform):  # type: ignore[no-untyped-def]
    """Executor A loses the broker mid-submission; standby B takes the lease; A's retry is fenced; reconciliation shows one order."""
    platform.broker.fail_submissions = True
    r = platform.run_intent(platform.make_intent())
    assert r.order.state == OrderState.SUBMITTED and platform.alerts.by_name("broker.unavailable")
    old = platform.leases.current(ACCOUNT).fencing_token
    platform.broker.fail_submissions = False
    new = platform.leases.preempt(ACCOUNT, "executor-b", now=platform.now)
    with pytest.raises(StaleFencingToken):
        platform.gateway.retry_submit(r.order.order_id, executor_id="executor-a", fencing_token=old, now=platform.now)
    rec = platform.gateway.retry_submit(r.order.order_id, executor_id="executor-b", fencing_token=new.fencing_token, now=platform.now)
    assert rec.state == OrderState.ACKNOWLEDGED
    platform.settle()
    result = platform.reconcile()
    assert result.clean and len(platform.broker.statement(ACCOUNT, as_of=platform.now).orders) == 1
    assert platform.broker.submissions_received == 1


@pytest.mark.tc("TC-EX-005")
@pytest.mark.req("NFR-CON-02")
@pytest.mark.quartet("negative")
def test_order_states_are_monotonic(platform):  # type: ignore[no-untyped-def]
    """FILLED is terminal; illegal transitions raise; fills for unknown orders alert instead of mutating state."""
    from execution_gateway.gateway import ORDER_MACHINE

    with pytest.raises(TransitionError):
        ORDER_MACHINE.assert_transition(OrderState.FILLED, OrderState.ACKNOWLEDGED)
    with pytest.raises(TransitionError):
        ORDER_MACHINE.assert_transition(OrderState.CANCELLED, OrderState.SUBMITTED)
    from broker_adapters.base import BrokerFill

    platform.gateway.apply_fill(
        BrokerFill(fill_ref="x", client_order_id="RTunknown", broker_order_ref="SIM-0", quantity=1, price=1, ts=platform.now),
        now=platform.now,
    )
    assert platform.alerts.by_name("execution.unknown_fill")


@pytest.mark.tc("TC-EX-006")
@pytest.mark.req("FR-02")
@pytest.mark.quartet("negative")
def test_unsupported_order_type_rejected_by_capability_discovery(platform):  # type: ignore[no-untyped-def]
    """Broker capability discovery: TRAILING_STOP unsupported by the sim broker -> BROKER_REJECTED with reason, no fill."""
    r = platform.run_intent(platform.make_intent(order_type="TRAILING_STOP", stop_price="95.00"))
    assert r.order is not None and r.order.state == OrderState.BROKER_REJECTED and "unsupported" in (r.order.reject_reason or "")


def test_gateway_denies_calls_from_analytics_plane(platform):  # type: ignore[no-untyped-def]
    r = platform.run_intent(platform.make_intent())
    with enter(Plane.ANALYTICS), pytest.raises(PlaneViolation):
        platform.gateway.submit(
            r.order.command.model_copy(update={"idempotency_key": "k2"}), executor_id="x", fencing_token=1, now=platform.now
        )


@pytest.mark.tc("TC-EX-007")
@pytest.mark.req("FR-13")
@pytest.mark.quartet("abuse")
def test_new_policy_version_cannot_create_second_live_order(platform):  # type: ignore[no-untyped-def]
    """A re-evaluation of the same intent under a new policy version yields a new key but is refused while an order is live (Trading review OBJ-1)."""
    from execution_gateway.gateway import DuplicateIntentOrder

    r = platform.run_intent(platform.make_intent())
    # a re-evaluation produces a new command id and idempotency key for the same intent; it is signed by the control plane
    cmd = platform.pipeline.sign_command(r.order.command.model_copy(update={"idempotency_key": "k-policy-v2", "command_id": "cmd-reeval"}))
    lease = platform.leases.current(ACCOUNT)
    with enter(Plane.CONTROL), pytest.raises(DuplicateIntentOrder):
        platform.gateway.submit(cmd, executor_id=platform.executor_id, fencing_token=lease.fencing_token, now=platform.now)
    assert platform.broker.submissions_received == 1 and platform.alerts.by_name("execution.duplicate_order")


@pytest.mark.tc("TC-EX-008")
@pytest.mark.req("FR-13")
@pytest.mark.quartet("recovery")
def test_retry_queries_non_deduping_broker_before_resubmitting(platform):  # type: ignore[no-untyped-def]
    """With a broker that does not dedupe client ids, a retry after an outage adopts the existing order instead of sending a second one (Trading review OBJ-2)."""
    platform.broker.dedupe_client_order_id = False
    platform.broker.fail_submissions = True
    r = platform.run_intent(platform.make_intent())
    assert r.order.state == OrderState.SUBMITTED
    platform.broker.fail_submissions = False
    # simulate: the first submission actually reached the broker before the outage was detected
    from broker_adapters.base import SubmitRequest

    c = r.order.command
    platform.broker.submit(
        SubmitRequest(
            client_order_id=r.order.client_order_id,
            account_id=c.account_id,
            venue=c.venue,
            instrument_id=c.instrument_id,
            side=c.side,
            order_type=c.order_type,
            quantity=c.quantity,
            time_in_force=c.time_in_force,
        ),
        now=platform.now,
    )
    lease = platform.leases.current(ACCOUNT)
    rec = platform.gateway.retry_submit(
        r.order.order_id, executor_id=platform.executor_id, fencing_token=lease.fencing_token, now=platform.now
    )
    assert rec.state == OrderState.ACKNOWLEDGED and platform.broker.submissions_received == 1
    platform.settle()
    assert platform.reconcile().clean


# ---- TC-EX-009: the gateway authenticates commands and consults Kill Switch / halt / mode at submission (IVA V-C1, V-C2)
def _resign(p, cmd, **update):  # type: ignore[no-untyped-def]
    return p.pipeline.sign_command(cmd.model_copy(update=update))


@pytest.mark.tc("TC-EX-009")
@pytest.mark.req("FR-13")
@pytest.mark.quartet("positive")
def test_gateway_accepts_only_control_plane_signed_commands(platform):  # type: ignore[no-untyped-def]
    """A command signed by the pipeline for a known APPROVED decision is accepted; the same command with one field altered is not."""
    from execution_gateway.gateway import CommandNotAuthorised

    r = platform.run_intent(resting_limit_intent(platform))
    assert r.order.command.authorisation and r.order.state in (OrderState.ACKNOWLEDGED, OrderState.SUBMITTED)
    altered = r.order.command.model_copy(update={"quantity": r.order.command.quantity * 10, "idempotency_key": "k-altered"})
    lease = platform.leases.current(ACCOUNT)
    with enter(Plane.CONTROL), pytest.raises(CommandNotAuthorised):
        platform.gateway.submit(altered, executor_id=platform.executor_id, fencing_token=lease.fencing_token, now=platform.now)
    assert platform.broker.submissions_received == 1 and platform.alerts.by_name("execution.unauthorised_command")
    assert platform.audit.by_action("order.command.unauthorised")


@pytest.mark.tc("TC-EX-009")
@pytest.mark.req("FR-17")
@pytest.mark.quartet("negative")
def test_gateway_blocks_kill_switch_and_halted_account_at_submission(platform):  # type: ignore[no-untyped-def]
    """An authorised command that arrives after an ACCOUNT Kill Switch or a halt is refused at the gateway, whatever the decision said (IVA V-C1)."""
    from conftest import RISK_OFFICER
    from execution_gateway.gateway import ExecutionBlocked
    from killswitch_service.service import KillSwitchLevel

    r = platform.run_intent(resting_limit_intent(platform))
    lease = platform.leases.current(ACCOUNT)
    with enter(Plane.CONTROL):
        platform.gateway.cancel(r.order.order_id, fencing_token=lease.fencing_token, now=platform.now, reason="make room for a re-send")
    late = _resign(platform, r.order.command, idempotency_key="k-late", command_id="cmd-late")  # legitimately authorised, delivered late
    platform.killswitch.activate(KillSwitchLevel.ACCOUNT, ACCOUNT, reason="drill", actor=RISK_OFFICER, now=platform.now)
    lease = platform.leases.acquire(ACCOUNT, platform.executor_id, now=platform.now)
    with enter(Plane.CONTROL), pytest.raises(ExecutionBlocked, match="kill switch"):
        platform.gateway.submit(late, executor_id=platform.executor_id, fencing_token=lease.fencing_token, now=platform.now)
    assert platform.broker.submissions_received == 1
    assert platform.alerts.by_name("execution.blocked_at_gateway") and platform.audit.by_action("order.command.blocked")
    # halted account without a kill switch: also refused
    p2 = build_sim_platform()
    r2 = p2.run_intent(resting_limit_intent(p2))
    lease2 = p2.leases.current(ACCOUNT)
    with enter(Plane.CONTROL):
        p2.gateway.cancel(r2.order.order_id, fencing_token=lease2.fencing_token, now=p2.now, reason="x")
    p2.accounts.halt(ACCOUNT, RISK_OFFICER, reason="drill", now=p2.now)
    with enter(Plane.CONTROL), pytest.raises(ExecutionBlocked, match="HALTED"):
        p2.gateway.submit(
            _resign(p2, r2.order.command, idempotency_key="k-halt", command_id="cmd-halt"),
            executor_id=p2.executor_id,
            fencing_token=lease2.fencing_token,
            now=p2.now,
        )
    assert p2.broker.submissions_received == 1


@pytest.mark.tc("TC-EX-009")
@pytest.mark.req("FR-13")
@pytest.mark.quartet("abuse")
def test_forged_decision_and_gateway_without_oracle_fail_closed(platform):  # type: ignore[no-untyped-def]
    """A correctly signed command naming a decision the control plane never made is refused; a gateway built without hooks submits nothing."""
    from execution_gateway.gateway import CommandNotAuthorised, ExecutionBlocked, ExecutionGateway

    r = platform.run_intent(resting_limit_intent(platform))
    lease = platform.leases.current(ACCOUNT)
    with enter(Plane.CONTROL):
        platform.gateway.cancel(r.order.order_id, fencing_token=lease.fencing_token, now=platform.now, reason="x")
    forged = _resign(platform, r.order.command, decision_id="dec_forged", idempotency_key="k-forged", command_id="cmd-forged")
    with enter(Plane.CONTROL), pytest.raises(ExecutionBlocked, match="decision unknown"):
        platform.gateway.submit(forged, executor_id=platform.executor_id, fencing_token=lease.fencing_token, now=platform.now)
    # decision exists but is for another intent
    other = _resign(platform, r.order.command, intent_id="other-intent", idempotency_key="k-other", command_id="cmd-other")
    with enter(Plane.CONTROL), pytest.raises(ExecutionBlocked, match="does not belong"):
        platform.gateway.submit(other, executor_id=platform.executor_id, fencing_token=lease.fencing_token, now=platform.now)
    assert platform.broker.submissions_received == 1
    bare = ExecutionGateway(
        adapters=platform.gateway._adapters,
        lease_store=platform.leases,
        audit=lambda *a: None,
        publish=lambda e: None,
        broker_for_account=lambda a: "sim-broker",
        guard=platform.guard,
    )
    with enter(Plane.CONTROL), pytest.raises(CommandNotAuthorised, match="fail closed"):
        bare.submit(r.order.command, executor_id=platform.executor_id, fencing_token=lease.fencing_token, now=platform.now)
    assert platform.broker.submissions_received == 1


@pytest.mark.tc("TC-EX-009")
@pytest.mark.req("FR-17")
@pytest.mark.quartet("recovery")
def test_retry_after_outage_rechecks_kill_switch(platform):  # type: ignore[no-untyped-def]
    """An order left SUBMITTED by a broker outage is not re-sent once the account was halted during the outage.

    (A Kill Switch would already have cancelled the stuck order through its cancel hook; a halt does not, so the
    gateway's own re-check at retry time is the control under test.)
    """
    from conftest import RISK_OFFICER
    from execution_gateway.gateway import ExecutionBlocked

    platform.broker.fail_submissions = True
    r = platform.run_intent(resting_limit_intent(platform))
    assert r.order.state == OrderState.SUBMITTED
    platform.broker.fail_submissions = False
    platform.accounts.halt(ACCOUNT, RISK_OFFICER, reason="drill during outage", now=platform.now)
    lease = platform.leases.acquire(ACCOUNT, platform.executor_id, now=platform.now)
    with enter(Plane.CONTROL), pytest.raises(ExecutionBlocked, match="HALTED"):
        platform.gateway.retry_submit(
            r.order.order_id, executor_id=platform.executor_id, fencing_token=lease.fencing_token, now=platform.now
        )
    assert platform.gateway.get(r.order.order_id).state == OrderState.SUBMITTED and platform.broker.submissions_received == 0
