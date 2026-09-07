"""TC-ID — Identity, privileged access, maker-checker, mode ladder [Source: 02; FR-01; C1]."""

from __future__ import annotations

from datetime import timedelta

import pytest
from conftest import ACCOUNT, CHIEF_RISK, PM, RISK_OFFICER, SRE, agent
from identity_service.accounts import GateRecord
from identity_service.makerchecker import MakerChecker
from identity_service.rbac import Permission, User, authorize, permissions_for
from rtcore.errors import ControlDenied, TransitionError
from rtcore.lines import Role
from rtcore.schemas.account import AccountMode


@pytest.mark.tc("TC-ID-001")
@pytest.mark.req("FR-01")
@pytest.mark.quartet("positive")
def test_privileged_change_needs_second_approver_from_different_line(platform):  # type: ignore[no-untyped-def]
    """A limit change proposed by one person stays pending until a different person from another line checks it; cooling period applies."""
    mc: MakerChecker = platform.limits_mc
    change = mc.propose("limit.changed", {"metric": "leverage_x", "threshold": "1.5"}, RISK_OFFICER, now=platform.now)
    assert change.status.value == "PENDING" and mc.effective(change.change_id, now=platform.now) is None
    with pytest.raises(ControlDenied):
        mc.check(change.change_id, RISK_OFFICER, now=platform.now)
    with pytest.raises(ControlDenied):
        mc.check(change.change_id, CHIEF_RISK, now=platform.now)  # same (2nd) line
    checked = mc.check(change.change_id, SRE, now=platform.now, reason="reviewed")
    assert checked.status.value == "CHECKED" and mc.effective(change.change_id, now=platform.now) is None
    assert mc.effective(change.change_id, now=platform.now + timedelta(hours=1)).status.value == "EFFECTIVE"
    assert {"limit.changed.proposed", "limit.changed.checked", "limit.changed.effective"} <= {e.action for e in platform.audit.all()}


@pytest.mark.tc("TC-ID-002")
@pytest.mark.req("FR-01")
@pytest.mark.quartet("negative")
def test_rbac_mfa_and_pim(platform):  # type: ignore[no-untyped-def]
    """RBAC denies missing permissions; MFA is required; privileged permissions need an active elevation window."""
    user = User(user_id="u1", tenant_id="tenant-sim", roles=(Role.RISK_OFFICER,), mfa_enrolled=True)
    authorize(user, Permission.PROPOSE_LIMIT, now=platform.now, mfa_verified=True)
    with pytest.raises(ControlDenied):
        authorize(user, Permission.PROPOSE_LIMIT, now=platform.now, mfa_verified=False)
    with pytest.raises(ControlDenied):
        authorize(user, Permission.MANAGE_BROKERS, now=platform.now, mfa_verified=True)
    with pytest.raises(ControlDenied):
        authorize(user, Permission.DEACTIVATE_KILL_SWITCH, now=platform.now, mfa_verified=True)
    elevated = user.model_copy(update={"privileged_until": platform.now + timedelta(minutes=30)})
    authorize(elevated, Permission.DEACTIVATE_KILL_SWITCH, now=platform.now, mfa_verified=True)
    with pytest.raises(ControlDenied):
        authorize(elevated, Permission.DEACTIVATE_KILL_SWITCH, now=platform.now + timedelta(hours=1), mfa_verified=True)
    assert Permission.SUBMIT_INTENT in permissions_for(User(user_id="a", tenant_id="t", roles=(Role.STRATEGY_AGENT,)))
    assert Permission.APPROVE_ORDER not in permissions_for(User(user_id="a", tenant_id="t", roles=(Role.STRATEGY_AGENT,)))


@pytest.mark.tc("TC-ID-003")
@pytest.mark.req("FR-01")
@pytest.mark.quartet("abuse")
def test_agent_cannot_change_mode_or_skip_steps_and_out_of_scope_flags_absent(platform):  # type: ignore[no-untyped-def]
    """Agents cannot promote modes; promotion is one step with gate evidence; out-of-scope capabilities have no permission flag."""
    p = platform
    with pytest.raises(ControlDenied):
        p.accounts.promote(ACCOUNT, AccountMode.SUPERVISED, agent(), None, reason="x", now=p.now)
    with pytest.raises(ControlDenied):
        p.limits_mc.propose("limit.changed", {"threshold": "0"}, agent(), now=p.now)
    with pytest.raises(TransitionError):
        p.accounts.promote(
            ACCOUNT,
            AccountMode.BOUNDED_AUTONOMOUS,
            RISK_OFFICER,
            GateRecord(gate="E", passed=True, decision_log_ref="D-x", iva_verdict="APPROVE"),
            reason="skip",
            now=p.now,
        )
    with pytest.raises(ControlDenied):
        p.accounts.promote(
            ACCOUNT,
            AccountMode.SUPERVISED,
            RISK_OFFICER,
            GateRecord(gate="D", passed=True, decision_log_ref="D-x", iva_verdict="VETO"),
            reason="vetoed",
            now=p.now,
        )
    with pytest.raises(ControlDenied):
        p.accounts.promote(ACCOUNT, AccountMode.SUPERVISED, RISK_OFFICER, None, reason="no gate", now=p.now)
    ok = p.accounts.promote(
        ACCOUNT,
        AccountMode.SUPERVISED,
        RISK_OFFICER,
        GateRecord(gate="D", passed=True, decision_log_ref="D-x", iva_verdict="APPROVE"),
        reason="gate D passed",
        now=p.now,
    )
    assert ok.mode == AccountMode.SUPERVISED
    with pytest.raises(ControlDenied):  # no capital envelope
        p.accounts.promote(
            ACCOUNT,
            AccountMode.BOUNDED_AUTONOMOUS,
            CHIEF_RISK,
            GateRecord(gate="E", passed=True, decision_log_ref="D-x", iva_verdict="APPROVE"),
            reason="x",
            now=p.now,
        )
    for absent in (
        "CUSTODY",
        "MONEY_MOVEMENT",
        "DEPOSIT",
        "WITHDRAWAL",
        "MARKET_MAKING",
        "COPY_TRADING",
        "PERSONAL_ADVICE",
        "MODIFY_AUDIT",
        "DISABLE_MONITORING",
    ):
        assert absent not in Permission.__members__


@pytest.mark.tc("TC-ID-004")
@pytest.mark.req("FR-01")
@pytest.mark.quartet("recovery")
def test_return_from_halted_requires_two_persons_different_lines(platform):  # type: ignore[no-untyped-def]
    """Halted is reachable by an authorised role; leaving it needs two persons from different lines and never straight to autonomy."""
    p = platform
    p.accounts.halt(ACCOUNT, RISK_OFFICER, reason="drill", now=p.now)
    assert p.accounts.get(ACCOUNT).mode == AccountMode.HALTED
    with pytest.raises(TransitionError):
        p.accounts.promote(ACCOUNT, AccountMode.PAPER, RISK_OFFICER, None, reason="x", now=p.now)
    first = p.accounts.restore_from_halt(ACCOUNT, RISK_OFFICER, reason="reviewed", now=p.now)
    assert first.mode == AccountMode.HALTED and first.pending_unhalt_by == RISK_OFFICER.actor_id
    with pytest.raises(ControlDenied):
        p.accounts.restore_from_halt(ACCOUNT, CHIEF_RISK, reason="same line", now=p.now)
    with pytest.raises(ControlDenied):
        p.accounts.restore_from_halt(ACCOUNT, PM, reason="to autonomy", now=p.now, target=AccountMode.BOUNDED_AUTONOMOUS)
    with pytest.raises(ControlDenied):  # enabled feature is PAPER: a restore cannot promote past it (Risk review F-02)
        p.accounts.restore_from_halt(ACCOUNT, PM, reason="to supervised", now=p.now, target=AccountMode.SUPERVISED)
    done = p.accounts.restore_from_halt(ACCOUNT, PM, reason="confirmed", now=p.now)
    assert done.mode == AccountMode.PAPER and done.pending_unhalt_by is None
    with pytest.raises(ControlDenied):
        p.accounts.halt(ACCOUNT, agent(), reason="rogue", now=p.now)
    assert p.audit.by_action("account.restored")
