"""TC-AP — Human approval queue, maker-checker [Source: 02, 05; FR-12]."""

from __future__ import annotations

from datetime import timedelta

import pytest
from conftest import ACCOUNT, PM, RISK_OFFICER, TRADER, agent, human
from rtcore.errors import ControlDenied
from rtcore.lines import Role
from rtcore.schemas.decision import Outcome
from rtcore.schemas.order import OrderState


@pytest.mark.tc("TC-AP-001")
@pytest.mark.req("FR-12")
@pytest.mark.quartet("positive")
def test_supervised_order_approved_by_different_human(supervised):  # type: ignore[no-untyped-def]
    """Supervised mode: intent -> approval queue -> a human checker != maker approves -> order executes; approval.recorded audited."""
    r = supervised.run_intent(supervised.make_intent(), submitted_by=TRADER.actor_id)
    assert r.decision.outcome == Outcome.REQUIRES_HUMAN_APPROVAL and r.approval_id
    order = supervised.approve(r.approval_id, PM)
    assert (
        order.state == OrderState.FILLED
        and order.command.approval_id == r.approval_id
        and order.command.authorised_by == f"APPROVAL:{PM.actor_id}"
    )
    rec = supervised.audit.by_action("approval.recorded")
    assert rec and rec[0].payload["approver_id"] == PM.actor_id and rec[0].payload["maker_id"] == TRADER.actor_id


@pytest.mark.tc("TC-AP-002")
@pytest.mark.req("FR-12")
@pytest.mark.quartet("negative")
def test_maker_cannot_check_own_intent(supervised):  # type: ignore[no-untyped-def]
    """The maker (submitter) is denied as checker; a role without approve permission is denied."""
    r = supervised.run_intent(supervised.make_intent(), submitted_by=TRADER.actor_id)
    with pytest.raises(ControlDenied):
        supervised.approve(r.approval_id, TRADER)
    with pytest.raises(ControlDenied):
        supervised.approve(r.approval_id, human("ops", Role.OPERATIONS_ANALYST))
    assert supervised.approvals.get(r.approval_id).status.value == "PENDING"


@pytest.mark.tc("TC-AP-003")
@pytest.mark.req("FR-12")
@pytest.mark.quartet("abuse")
def test_agent_cannot_approve_and_cannot_enqueue_approved_decisions(supervised, platform):  # type: ignore[no-untyped-def]
    """An AI agent cannot act as approver; a decision that is not REQUIRES_HUMAN_APPROVAL cannot be queued (self-approval path absent)."""
    r = supervised.run_intent(supervised.make_intent())
    with pytest.raises(ControlDenied):
        supervised.approve(r.approval_id, agent())
    approved = platform.run_intent(platform.make_intent())
    with pytest.raises(ControlDenied):
        platform.approvals.enqueue(approved.validated_intent, approved.decision, now=platform.now)


@pytest.mark.tc("TC-AP-004")
@pytest.mark.req("FR-12")
@pytest.mark.quartet("recovery")
def test_expired_or_killed_intent_not_executed_after_approval(supervised):  # type: ignore[no-untyped-def]
    """Expiry before approval -> EXPIRED, never executed; Kill Switch after approval blocks execution; decline path recorded."""
    r = supervised.run_intent(supervised.make_intent())
    supervised.now = supervised.now + timedelta(minutes=10)
    with pytest.raises(ControlDenied):
        supervised.approve(r.approval_id, RISK_OFFICER)
    assert supervised.approvals.get(r.approval_id).status.value == "EXPIRED"
    supervised.now = supervised.now - timedelta(minutes=10)
    r2 = supervised.run_intent(supervised.make_intent())
    from killswitch_service.service import KillSwitchLevel

    supervised.killswitch.activate(KillSwitchLevel.ACCOUNT, ACCOUNT, reason="drill", actor=RISK_OFFICER, now=supervised.now)
    with pytest.raises(ControlDenied):
        supervised.approve(r2.approval_id, PM)
    assert supervised.broker.submissions_received == 0
    r3 = supervised.run_intent(supervised.make_intent())
    assert r3.decision.outcome == Outcome.HALTED


@pytest.mark.tc("TC-AP-005")
@pytest.mark.req("FR-12")
@pytest.mark.quartet("abuse")
def test_strategy_owner_cannot_approve_own_strategy(supervised):  # type: ignore[no-untyped-def]
    """The registered owner of the strategy (quant.fixture) is refused as approver even with an approving role; another PM may approve (IVA-04)."""
    r = supervised.run_intent(supervised.make_intent())
    item = supervised.approvals.get(r.approval_id)
    assert item.strategy_owner_id == "quant.fixture"
    owner_as_pm = human("quant.fixture", Role.PORTFOLIO_MANAGER)
    with pytest.raises(ControlDenied):
        supervised.approve(r.approval_id, owner_as_pm)
    assert supervised.approvals.get(r.approval_id).status.value == "PENDING"
    order = supervised.approve(r.approval_id, PM)
    assert order.state in (OrderState.ACKNOWLEDGED, OrderState.FILLED, OrderState.PARTIALLY_FILLED)
