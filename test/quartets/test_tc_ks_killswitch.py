"""TC-KS — Kill Switch [Source: 02, 05; FR-17; P4]: six levels, unilateral activation, two-person deactivation."""

from __future__ import annotations

import pytest
from conftest import (
    ACCOUNT,
    CHIEF_RISK,
    COMPLIANCE,
    INSTRUMENT,
    RISK_OFFICER,
    SRE,
    STRATEGY,
    TENANT,
    TRADER,
    VENUE,
    agent,
    resting_limit_intent,
)
from killswitch_service.service import KillSwitchLevel
from risk_engine.monitors import RuntimeMetrics
from rtcore.errors import ControlDenied
from rtcore.schemas.account import AccountMode
from rtcore.schemas.decision import Outcome
from rtcore.schemas.order import OrderState


@pytest.mark.tc("TC-KS-001")
@pytest.mark.req("FR-17")
@pytest.mark.quartet("positive")
def test_activation_blocks_new_risk_and_cancels_open_orders(platform):  # type: ignore[no-untyped-def]
    """Activation: open orders cancelled, agent identities revoked, evidence snapshot hashed, notification sent, new intents HALTED."""
    resting = platform.run_intent(resting_limit_intent(platform))
    assert resting.order.state == OrderState.ACKNOWLEDGED
    ident = platform.issue_agent()
    act = platform.killswitch.activate(KillSwitchLevel.ACCOUNT, ACCOUNT, reason="drill", actor=RISK_OFFICER, now=platform.now)
    assert resting.order.order_id in act.cancelled_orders and platform.gateway.get(resting.order.order_id).state == OrderState.CANCELLED
    assert "agent-sim-1" in act.revoked_identities and act.evidence_hash and act.emergency_policy_applied == "CANCEL_ONLY"
    assert platform.notifications and platform.notifications[-1][0] == "killswitch.activated"
    assert platform.tool_call(ident, "read_market_snapshot", {"instrument_id": INSTRUMENT}).error_code == "IDENTITY"
    halted = platform.run_intent(platform.make_intent())
    assert halted.decision.outcome == Outcome.HALTED and {"RK-HALT-KS", "RK-HALT-MODE"} <= set(halted.decision.reason_codes)
    assert platform.accounts.get(ACCOUNT).mode == AccountMode.HALTED
    assert platform.audit.by_action("killswitch.activated") and platform.audit.verify().ok


@pytest.mark.tc("TC-KS-002")
@pytest.mark.req("FR-17")
@pytest.mark.quartet("abuse")
def test_agent_cannot_activate_or_deactivate(platform):  # type: ignore[no-untyped-def]
    """An AI agent attempting to operate the Kill Switch is denied, audited and alerted (S1)."""
    with pytest.raises(ControlDenied):
        platform.killswitch.activate(KillSwitchLevel.PLATFORM, "*", reason="x", actor=agent(), now=platform.now)
    act = platform.killswitch.activate(KillSwitchLevel.STRATEGY, STRATEGY, reason="drill", actor=SRE, now=platform.now)
    with pytest.raises(ControlDenied):
        platform.killswitch.deactivate(act.activation_id, actor=agent(), reason="x", now=platform.now)
    with pytest.raises(ControlDenied):
        platform.killswitch.activate(KillSwitchLevel.ACCOUNT, ACCOUNT, reason="x", actor=TRADER, now=platform.now)
    assert len(platform.alerts.by_name("killswitch.agent_attempt")) == 2 and platform.audit.by_action("killswitch.denied")


@pytest.mark.tc("TC-KS-003")
@pytest.mark.req("FR-17")
@pytest.mark.quartet("negative")
def test_single_person_deactivation_stays_pending(platform):  # type: ignore[no-untyped-def]
    """One person (or two from the same line) cannot deactivate: the activation stays active and pending."""
    act = platform.killswitch.activate(KillSwitchLevel.TENANT, TENANT, reason="drill", actor=CHIEF_RISK, now=platform.now)
    pending = platform.killswitch.deactivate(act.activation_id, actor=RISK_OFFICER, reason="reviewed", now=platform.now)
    assert pending.active and pending.deactivation_first_by == RISK_OFFICER.actor_id
    with pytest.raises(ControlDenied):
        platform.killswitch.deactivate(act.activation_id, actor=RISK_OFFICER, reason="again", now=platform.now)
    with pytest.raises(ControlDenied):  # same line (2nd) as the first person
        platform.killswitch.deactivate(act.activation_id, actor=COMPLIANCE, reason="me too", now=platform.now)
    assert platform.killswitch.get(act.activation_id).active
    assert platform.run_intent(platform.make_intent()).decision.outcome == Outcome.HALTED


@pytest.mark.tc("TC-KS-004")
@pytest.mark.req("FR-17")
@pytest.mark.quartet("recovery")
def test_two_person_deactivation_restores_with_audit(platform):  # type: ignore[no-untyped-def]
    """Two persons from different lines deactivate; account restored via two-person rule; trading resumes; audit chain intact."""
    act = platform.killswitch.activate(KillSwitchLevel.ACCOUNT, ACCOUNT, reason="drill", actor=RISK_OFFICER, now=platform.now)
    platform.killswitch.deactivate(act.activation_id, actor=RISK_OFFICER, reason="drill complete", now=platform.now)
    done = platform.killswitch.deactivate(act.activation_id, actor=SRE, reason="verified", now=platform.now)
    assert not done.active and platform.killswitch.active() == ()
    assert platform.accounts.get(ACCOUNT).mode == AccountMode.HALTED
    platform.accounts.restore_from_halt(ACCOUNT, RISK_OFFICER, reason="post-incident review done", now=platform.now)
    platform.accounts.restore_from_halt(ACCOUNT, SRE, reason="confirmed", now=platform.now, target=AccountMode.PAPER)
    assert platform.accounts.get(ACCOUNT).mode == AccountMode.PAPER
    platform.issuer.restore_scope("ACCOUNT", ACCOUNT)
    r = platform.run_intent(platform.make_intent())
    assert r.decision.outcome == Outcome.APPROVED
    actions = [e.action for e in platform.audit.all()]
    assert "killswitch.deactivation.pending" in actions and "killswitch.deactivated" in actions and "account.restored" in actions
    assert platform.audit.verify().ok


@pytest.mark.tc("TC-KS-005")
@pytest.mark.req("FR-17")
@pytest.mark.quartet("positive")
@pytest.mark.parametrize(
    "level,target",
    [
        (KillSwitchLevel.PLATFORM, "*"),
        (KillSwitchLevel.TENANT, TENANT),
        (KillSwitchLevel.STRATEGY, STRATEGY),
        (KillSwitchLevel.ASSET, INSTRUMENT),
        (KillSwitchLevel.VENUE, VENUE),
    ],
)
def test_every_level_blocks_matching_intents(platform, level, target):  # type: ignore[no-untyped-def]
    """Each of the six levels is consulted by the risk engine through the account snapshot flags."""
    platform.killswitch.activate(level, target, reason="drill", actor=SRE, now=platform.now)
    r = platform.run_intent(platform.make_intent())
    assert r.decision.outcome == Outcome.HALTED and "RK-HALT-KS" in r.decision.reason_codes


@pytest.mark.tc("TC-KS-006")
@pytest.mark.req("FR-17")
@pytest.mark.quartet("positive")
def test_runtime_monitor_triggers_kill_switch(platform):  # type: ignore[no-untyped-def]
    """Runtime loss-limit breach -> risk.halt.v1 event -> Kill Switch at account level without human action."""
    book = platform.ledger.book(ACCOUNT)
    book.start_of_day_nav = book.cash * 2  # simulate a large intraday loss vs start of day
    codes = platform.evaluate_monitors(ACCOUNT, RuntimeMetrics())
    assert "RT-LOSS-DAILY" in codes and platform.killswitch.flags_for(tenant_id=TENANT, account_id=ACCOUNT).account
    assert platform.audit.by_action("risk.halt.v1")


def test_emergency_policy_reduce_without_liquidation_policy_falls_back(platform):  # type: ignore[no-untyped-def]
    from rtcore.schemas.account import EmergencyPolicy

    acct = platform.accounts.get(ACCOUNT)
    platform.accounts._accounts[ACCOUNT] = acct.model_copy(update={"emergency_policy": EmergencyPolicy.CANCEL_AND_FLATTEN})
    act = platform.killswitch.activate(KillSwitchLevel.ACCOUNT, ACCOUNT, reason="drill", actor=SRE, now=platform.now)
    assert act.emergency_policy_applied.startswith("CANCEL_ONLY (fallback")  # [Open: O-08]
