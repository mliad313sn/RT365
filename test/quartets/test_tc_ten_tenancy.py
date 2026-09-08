"""TC-TEN — Tenant isolation [Source: 03, 06; NFR-TEN-01; FR-01; RAID R-22, RT-03].

Two simulated tenants (tenant-sim, tenant-sim-b) share one dev/sim platform. Every read is filtered to the
principal's tenant, every write is scope-checked, agent identities cannot be minted across tenants, and a
tenant-wide revocation of one tenant leaves the other untouched. The second tenant's allowlist is a test
fixture (test/fixtures/policies); shipping it under mcp/policies is the MCP Security Agent's call.
"""

from __future__ import annotations

from datetime import timedelta
from decimal import Decimal

import pytest
from conftest import ACCOUNT, AUDITOR, INSTRUMENT, OPS, PM, RISK_OFFICER, SRE, STRATEGY, TENANT, TRADER, TRADING_LEAD
from fastapi.testclient import TestClient
from killswitch_service.service import KillSwitchLevel
from mcp_servers.allowlist import AllowlistStore
from risk_engine.policy import LimitScope, Metric, effective_limit
from rtcore.errors import ControlDenied
from rtcore.lines import Actor, ActorKind, Role
from rtcore.schemas.account import AccountMode
from rtcore.schemas.decision import Outcome
from web_bff.app import create_app
from web_bff.platform import ACCOUNT_B, TENANT_B, build_sim_platform


def human_b(actor_id: str, role: Role) -> Actor:
    return Actor(actor_id=actor_id, role=role, kind=ActorKind.HUMAN, tenant_id=TENANT_B)


RISK_OFFICER_B = human_b("risk.officer.b", Role.RISK_OFFICER)  # 2nd line
PM_B = human_b("pm.b", Role.PORTFOLIO_MANAGER)  # 1st line
SRE_B = human_b("sre.b", Role.SRE_LEAD)  # 1st line
TRADER_B = human_b("trader.b", Role.TRADER)  # 1st line
OPS_B = human_b("ops.b", Role.OPERATIONS_ANALYST)  # 1st line
TRADING_LEAD_B = human_b("trading.lead.b", Role.TRADING_DOMAIN_LEAD)  # 1st line


def hdr(actor: Actor, mfa: str = "verified", **extra: str) -> dict[str, str]:
    return {"X-Actor-Id": actor.actor_id, "X-Actor-Role": actor.role.value, "X-MFA": mfa, **extra}


@pytest.fixture
def two_tenants():  # type: ignore[no-untyped-def]
    p = build_sim_platform(second_tenant=True, mode=AccountMode.SUPERVISED)
    return TestClient(create_app(p)), p


def _assert_correlated(p) -> None:  # type: ignore[no-untyped-def]
    """Every audit row carries a real correlation id (never empty, never the '-' placeholder)."""
    bad = [(e.action, e.correlation_id) for e in p.audit.all() if not e.correlation_id or e.correlation_id == "-"]
    assert not bad, bad


@pytest.mark.tc("TC-TEN-001")
@pytest.mark.req("NFR-TEN-01")
@pytest.mark.quartet("positive")
def test_two_tenants_act_only_on_their_own_data(two_tenants):  # type: ignore[no-untyped-def]
    """Agents and humans of two tenants read, submit and approve their own data; every audit row is tenant-tagged and correlated."""
    c, p = two_tenants
    a = p.issue_agent(agent_id="agent-a", account_id=ACCOUNT)
    b = p.issue_agent(agent_id="agent-b", account_id=ACCOUNT_B)
    assert a.tenant_id == TENANT and b.tenant_id == TENANT_B
    assert p.tool_call(a, "read_account_state", {"account_id": ACCOUNT}).ok
    assert p.tool_call(b, "read_account_state", {"account_id": ACCOUNT_B}).ok
    ra = p.run_intent(p.make_intent())
    rb = p.run_intent(p.make_intent(account_id=ACCOUNT_B))
    assert ra.decision.outcome == Outcome.REQUIRES_HUMAN_APPROVAL and rb.decision.outcome == Outcome.REQUIRES_HUMAN_APPROVAL
    qa = c.get("/v1/approvals", headers=hdr(PM)).json()
    qb = c.get("/v1/approvals", headers=hdr(PM_B)).json()
    assert [q["approval_id"] for q in qa] == [ra.approval_id] and [q["approval_id"] for q in qb] == [rb.approval_id]
    assert c.post(f"/v1/approvals/{ra.approval_id}/approve", json={"reason": "reviewed"}, headers=hdr(PM)).json()["state"] == "FILLED"
    assert c.post(f"/v1/approvals/{rb.approval_id}/approve", json={"reason": "reviewed"}, headers=hdr(PM_B)).json()["state"] == "FILLED"
    assert c.get(f"/v1/accounts/{ACCOUNT}", headers=hdr(RISK_OFFICER)).json()["tenant_id"] == TENANT
    assert c.get(f"/v1/accounts/{ACCOUNT_B}", headers=hdr(RISK_OFFICER_B)).json()["tenant_id"] == TENANT_B
    status_b = c.get("/v1/status", headers=hdr(RISK_OFFICER_B)).json()
    assert status_b["1_global_status"]["tenant_id"] == TENANT_B and status_b["1_global_status"]["account_id"] == ACCOUNT_B
    for corr, tenant in ((ra.validated_intent.correlation_id, TENANT), (rb.validated_intent.correlation_id, TENANT_B)):
        rows = p.audit.by_correlation(corr)
        assert rows and all(e.tenant == tenant for e in rows)
    assert all(e.tenant == TENANT_B for e in p.audit.all() if e.account == ACCOUNT_B)
    assert all(e.tenant == TENANT for e in p.audit.all() if e.account == ACCOUNT)
    assert {e.action for e in p.audit.by_action("principal.bound")} == {"principal.bound"}
    _assert_correlated(p)
    assert p.audit.verify().ok


@pytest.mark.tc("TC-TEN-002")
@pytest.mark.req("NFR-TEN-01")
@pytest.mark.quartet("negative")
def test_cross_tenant_access_is_denied_at_every_layer(two_tenants):  # type: ignore[no-untyped-def]
    """A's agent on B's account -> SCOPE (audited); cross-tenant identity mint refused; human A on B -> refused; pipeline CP-TENANT then RK-AUTH-TENANT."""
    c, p = two_tenants
    a = p.issue_agent(agent_id="agent-a", account_id=ACCOUNT)
    denied = p.tool_call(a, "read_account_state", {"account_id": ACCOUNT_B})
    assert not denied.ok and denied.error_code == "SCOPE" and denied.correlation_id.startswith("call:")
    sub = p.tool_call(a, "submit_trade_intent", {"intent": p.make_intent(account_id=ACCOUNT_B)})
    assert sub.error_code == "SCOPE" and len(p.intent_queue) == 0
    rows = p.audit.by_action("mcp.tool.denied", tenant=TENANT)
    assert rows and all(e.correlation_id.startswith("call:") for e in rows) and {e.payload["code"] for e in rows} == {"SCOPE"}
    assert p.audit.by_action("mcp.tool.denied", tenant=TENANT_B) == ()
    # an identity for tenant A over tenant B's account is never minted (fail closed, audited)
    with pytest.raises(ControlDenied):
        p.issue_agent(agent_id="agent-x", account_id=ACCOUNT_B, tenant_id=TENANT)
    with pytest.raises(ControlDenied):
        p.issue_agent(agent_id="agent-y", account_id="acct-does-not-exist")
    refused = p.audit.by_action("mcp.identity.refused")
    assert len(refused) == 2 and all(e.correlation_id and e.correlation_id != "-" for e in refused)
    # human of A cannot see B, human of B cannot see A; each sees its own
    assert c.get(f"/v1/accounts/{ACCOUNT_B}", headers=hdr(RISK_OFFICER)).status_code == 404
    assert c.get(f"/v1/accounts/{ACCOUNT}", headers=hdr(RISK_OFFICER_B)).status_code == 404
    assert c.get(f"/v1/accounts/{ACCOUNT}", headers=hdr(RISK_OFFICER)).status_code == 200
    assert c.post("/v1/intents", json=p.make_intent(account_id=ACCOUNT_B), headers=hdr(TRADER)).status_code == 404
    # defence in depth: an intent sealed under tenant A for B's account never executes — the compliance layer refuses it
    # (CP-TENANT) and, were it bypassed, the deterministic risk engine refuses it again (RK-AUTH-TENANT, TC-RK-018)
    r = p.run_intent(p.make_intent(account_id=ACCOUNT_B), tenant_id=TENANT)
    assert r.eligibility.outcome.value == "INELIGIBLE" and "CP-TENANT" in r.eligibility.reason_codes
    assert r.decision is None and r.order is None and p.broker.submissions_received == 0
    from risk_engine.engine import decide

    snap_b, mkt = p.account_snapshot(ACCOUNT_B), p.market_snapshot(INSTRUMENT)
    risk = decide(r.validated_intent, snap_b, mkt, p.policy, p.now)
    assert "RK-AUTH-TENANT" in risk.reason_codes and risk.outcome == Outcome.REJECTED
    _assert_correlated(p)


@pytest.mark.tc("TC-TEN-003")
@pytest.mark.req("NFR-TEN-01")
@pytest.mark.quartet("abuse")
def test_every_bff_read_is_scoped_and_every_cross_tenant_action_refused(two_tenants):  # type: ignore[no-untyped-def]
    """Every read returns only the principal's tenant; actions on the other tenant are 404 without existence leak; forged tenant header 403."""
    c, p = two_tenants
    ra = p.run_intent(p.make_intent())
    rb = p.run_intent(p.make_intent(account_id=ACCOUNT_B))
    a_intent, b_intent = str(ra.decision.intent_id), str(rb.decision.intent_id)
    # --- reads --------------------------------------------------------------------------------------------
    assert c.get(f"/v1/intents/{b_intent}", headers=hdr(RISK_OFFICER)).status_code == 404
    assert c.get(f"/v1/intents/{a_intent}", headers=hdr(RISK_OFFICER)).json()["tenant_id"] == TENANT
    assert c.get(f"/v1/decisions/{rb.decision.decision_id}", headers=hdr(RISK_OFFICER)).status_code == 404
    assert c.get(f"/v1/decisions/{ra.decision.decision_id}", headers=hdr(RISK_OFFICER)).status_code == 200
    assert [q["approval_id"] for q in c.get("/v1/approvals", headers=hdr(PM)).json()] == [ra.approval_id]
    corr_a, corr_b = ra.validated_intent.correlation_id, rb.validated_intent.correlation_id
    assert c.get("/v1/audit", params={"correlation_id": corr_b}, headers=hdr(RISK_OFFICER)).json() == []
    assert c.get("/v1/audit", params={"correlation_id": corr_a}, headers=hdr(RISK_OFFICER)).json()
    export = c.get("/v1/audit/export", headers=hdr(AUDITOR)).json()["jsonl"]
    import json

    exported = [json.loads(line) for line in export.splitlines() if line]
    assert exported and {row["tenant"] for row in exported} == {TENANT}
    act_b = c.post(
        "/v1/killswitch",
        json={"level": "ACCOUNT", "target_id": ACCOUNT_B, "reason": "drill B", "actor": RISK_OFFICER_B.actor_id},
        headers=hdr(RISK_OFFICER_B),
    )
    assert act_b.status_code == 202
    assert c.get("/v1/killswitch", headers=hdr(RISK_OFFICER)).json() == []
    assert [x["activation_id"] for x in c.get("/v1/killswitch", headers=hdr(RISK_OFFICER_B)).json()] == [act_b.json()["activation_id"]]
    status_a = c.get("/v1/status", headers=hdr(RISK_OFFICER)).json()
    assert status_a["1_global_status"]["tenant_id"] == TENANT and status_a["1_global_status"]["kill_switch_active"] == []
    # --- existence leak: an unknown account and the other tenant's account are indistinguishable --------------
    other = c.get(f"/v1/accounts/{ACCOUNT_B}", headers=hdr(RISK_OFFICER))
    missing = c.get("/v1/accounts/acct-does-not-exist", headers=hdr(RISK_OFFICER))
    assert other.status_code == 404 and missing.status_code == 404 and other.json() == missing.json()
    # --- actions on B from A --------------------------------------------------------------------------------
    queued = c.post("/v1/intents", json=p.make_intent(account_id=ACCOUNT_B, quantity="1"), headers=hdr(TRADER_B))
    assert queued.status_code == 202
    assert c.post(f"/v1/intents/{queued.json()['intent_id']}/process", headers=hdr(RISK_OFFICER)).status_code == 404
    assert len(p.intent_queue) == 1  # A's attempt did not drain B's intent
    assert c.post(f"/v1/intents/{queued.json()['intent_id']}/process", headers=hdr(RISK_OFFICER_B)).status_code == 200
    assert c.post(f"/v1/approvals/{rb.approval_id}/approve", json={"reason": "mine"}, headers=hdr(PM)).status_code == 404
    assert c.post(f"/v1/approvals/{rb.approval_id}/decline", json={"reason": "mine"}, headers=hdr(PM)).status_code == 404
    assert p.approvals.get(rb.approval_id).status.value == "PENDING"
    ks = {"level": "ACCOUNT", "target_id": ACCOUNT_B, "reason": "cross", "actor": RISK_OFFICER.actor_id}
    assert c.post("/v1/killswitch", json=ks, headers=hdr(RISK_OFFICER)).status_code == 404
    assert c.post("/v1/killswitch", json={**ks, "level": "TENANT", "target_id": TENANT_B}, headers=hdr(RISK_OFFICER)).status_code == 403
    assert c.post("/v1/killswitch", json={**ks, "level": "PLATFORM", "target_id": "*"}, headers=hdr(RISK_OFFICER)).status_code == 403
    lift = {"reason": "cross-tenant lift attempt"}
    assert c.post(f"/v1/killswitch/{act_b.json()['activation_id']}/deactivate", json=lift, headers=hdr(RISK_OFFICER)).status_code == 404
    assert len(p.killswitch.active()) == 1 and p.killswitch.active()[0].target_id == ACCOUNT_B
    # break tickets: A's operations analyst sees and resolves only A's
    p.approve(ra.approval_id, PM)
    p.ledger.book(ACCOUNT).positions[INSTRUMENT].quantity += Decimal("1")
    p.ledger.book(ACCOUNT_B).cash += Decimal("5")
    p.reconcile(ACCOUNT)
    p.reconcile(ACCOUNT_B)
    tickets_a = c.get("/v1/reconciliation/breaks", headers=hdr(OPS)).json()
    tickets_b = c.get("/v1/reconciliation/breaks", headers=hdr(OPS_B)).json()
    assert tickets_a and {t["brk"]["account_id"] for t in tickets_a} == {ACCOUNT}
    assert tickets_b and {t["brk"]["account_id"] for t in tickets_b} == {ACCOUNT_B}
    resolve_b = f"/v1/reconciliation/tickets/{tickets_b[0]['ticket_id']}/resolve"
    assert c.post(resolve_b, json={"resolution": "cross-tenant resolve attempt"}, headers=hdr(OPS)).status_code == 404
    assert p.tickets.get(tickets_b[0]["ticket_id"]).status.value == "OPEN"
    assert c.post("/v1/reconciliation/run", params={"account_id": ACCOUNT_B}, headers=hdr(OPS)).status_code == 404
    # --- forged tenant header and unbound principal ---------------------------------------------------------------
    forged = c.get(f"/v1/accounts/{ACCOUNT_B}", headers=hdr(RISK_OFFICER, **{"X-Actor-Tenant": TENANT_B}))
    assert forged.status_code == 403
    unbound = c.get(f"/v1/accounts/{ACCOUNT}", headers={"X-Actor-Id": "nobody", "X-Actor-Role": "risk_officer", "X-MFA": "verified"})
    assert unbound.status_code == 403
    denials = p.audit.by_action("tenant.scope.denied")
    assert {e.payload["reason"] for e in denials} >= {"TENANT_HEADER_FORGED", "UNBOUND_PRINCIPAL", "TENANT_SCOPE"}
    assert all(e.correlation_id and e.correlation_id != "-" for e in denials)
    # --- limits: a STRATEGY limit proposed in A never changes B's effective limit; B's scopes and PLATFORM refused ----
    scope_b = LimitScope(tenant_id=TENANT_B, account_id=ACCOUNT_B, strategy_id=STRATEGY, instrument_id="*")
    scope_a = LimitScope(tenant_id=TENANT, account_id=ACCOUNT, strategy_id=STRATEGY, instrument_id="*")
    before_b = effective_limit(p.policy, Metric.LEVERAGE_X, scope_b, p.now).threshold
    proposal = {"level": "STRATEGY", "scope_id": STRATEGY, "metric": "leverage_x", "threshold": "0.5"}
    prop = c.post("/v1/limits", json=proposal, headers=hdr(RISK_OFFICER))
    assert prop.status_code == 202 and prop.json()["payload"]["tenant_id"] == TENANT
    assert c.post("/v1/limits", json={**proposal, "tenant_id": TENANT_B}, headers=hdr(RISK_OFFICER)).status_code == 422  # closed schema
    assert c.post("/v1/limits", json={**proposal, "level": "ACCOUNT", "scope_id": ACCOUNT_B}, headers=hdr(RISK_OFFICER)).status_code == 404
    assert c.post("/v1/limits", json={**proposal, "level": "TENANT", "scope_id": TENANT_B}, headers=hdr(RISK_OFFICER)).status_code == 403
    assert c.post("/v1/limits", json={**proposal, "level": "PLATFORM", "scope_id": "*"}, headers=hdr(RISK_OFFICER)).status_code == 403
    change_id = prop.json()["change_id"]
    assert c.post(f"/v1/limits/{change_id}/check", json={"reason": "other tenant"}, headers=hdr(TRADING_LEAD_B)).status_code == 404
    assert c.post(f"/v1/limits/{change_id}/check", json={"reason": "reviewed"}, headers=hdr(TRADING_LEAD)).json()["status"] == "CHECKED"
    p.advance(3601)
    p.apply_effective_limits()
    assert effective_limit(p.policy, Metric.LEVERAGE_X, scope_a, p.now).threshold == Decimal("0.5")
    assert effective_limit(p.policy, Metric.LEVERAGE_X, scope_b, p.now).threshold == before_b
    _assert_correlated(p)
    assert p.audit.verify().ok


@pytest.mark.tc("TC-TEN-004")
@pytest.mark.req("NFR-TEN-01")
@pytest.mark.quartet("recovery")
def test_tenant_wide_revocation_hits_one_tenant_survives_restart_and_needs_two_persons_to_lift(tmp_path):  # type: ignore[no-untyped-def]
    """Revoking tenant A stops only A (B keeps working), survives a restart, and is lifted only by two distinct approvers; all audited."""
    path = tmp_path / "revocations.jsonl"
    p1 = build_sim_platform(second_tenant=True, revocations_path=path)
    assert isinstance(p1.allowlists, AllowlistStore) and set(p1.allowlists) == {TENANT, TENANT_B}
    a1, b1 = p1.issue_agent(agent_id="agent-a", account_id=ACCOUNT), p1.issue_agent(agent_id="agent-b", account_id=ACCOUNT_B)
    read = {"instrument_id": INSTRUMENT}
    assert p1.tool_call(a1, "read_market_snapshot", read).ok and p1.tool_call(b1, "read_market_snapshot", read).ok
    p1.allowlists.revoke_tenant(TENANT, by="mcp-security-agent", at=p1.now, reason="drill: suspected tenant compromise")
    assert p1.tool_call(a1, "read_market_snapshot", read).error_code == "TENANT_REVOKED"
    assert p1.tool_call(b1, "read_market_snapshot", read).ok
    with pytest.raises(ControlDenied):
        p1.allowlists.revoke_tenant("tenant-unknown", by="mcp-security-agent", at=p1.now)
    # restart: the persisted list is re-read; A still refused, B still fine
    p2 = build_sim_platform(second_tenant=True, revocations_path=path)
    a2, b2 = p2.issue_agent(agent_id="agent-a2", account_id=ACCOUNT), p2.issue_agent(agent_id="agent-b2", account_id=ACCOUNT_B)
    assert p2.tool_call(a2, "read_market_snapshot", read).error_code == "TENANT_REVOKED"
    assert p2.tool_call(b2, "read_market_snapshot", read).ok
    assert p2.revocations.active("tenant") and p2.allowlists.is_tenant_revoked(TENANT)
    # lifting is a two-person action: single person, same person twice and an empty name are refused
    for approvers in (("mcp-security-agent",), ("mcp-security-agent", "mcp-security-agent"), ("mcp-security-agent", "")):
        with pytest.raises(ControlDenied):
            p2.allowlists.restore_tenant(TENANT, approvers=approvers, at=p2.now)  # type: ignore[arg-type]
    assert p2.tool_call(a2, "read_market_snapshot", read, now=p2.now + timedelta(seconds=1)).error_code == "TENANT_REVOKED"
    p2.allowlists.restore_tenant(TENANT, approvers=("mcp-security-agent", "security-architect"), at=p2.now)
    assert p2.tool_call(a2, "read_market_snapshot", read, now=p2.now + timedelta(seconds=2)).ok
    # identity-level tenant scope: same two-person rule, same isolation
    p2.issuer.revoke_scope("TENANT", TENANT, by=RISK_OFFICER.actor_id, now=p2.now)
    assert p2.tool_call(a2, "read_market_snapshot", read, now=p2.now + timedelta(seconds=3)).error_code == "IDENTITY"
    assert p2.tool_call(b2, "read_market_snapshot", read, now=p2.now + timedelta(seconds=3)).ok
    with pytest.raises(ControlDenied):
        p2.issuer.restore_scope("TENANT", TENANT, by=RISK_OFFICER.actor_id, now=p2.now)
    with pytest.raises(ControlDenied):
        p2.issuer.restore_scope("TENANT", TENANT, by=f"{RISK_OFFICER.actor_id}+{RISK_OFFICER.actor_id}", now=p2.now)
    p2.issuer.restore_scope("TENANT", TENANT, approvers=(RISK_OFFICER.actor_id, SRE.actor_id), now=p2.now)
    assert p2.tool_call(a2, "read_market_snapshot", read, now=p2.now + timedelta(seconds=4)).ok
    # a TENANT-level Kill Switch on A halts A's intents while B keeps trading
    p2.killswitch.activate(KillSwitchLevel.TENANT, TENANT, reason="drill", actor=RISK_OFFICER, now=p2.now)
    assert p2.run_intent(p2.make_intent()).decision.outcome == Outcome.HALTED
    assert p2.run_intent(p2.make_intent(account_id=ACCOUNT_B)).decision.outcome == Outcome.APPROVED
    actions = {e.action for e in p2.audit.all()} | {e.action for e in p1.audit.all()}
    assert {"mcp.tenant.revoked", "mcp.tenant.restored", "mcp.scope.revoked", "mcp.scope.restored", "killswitch.activated"} <= actions
    assert all(e.tenant == TENANT for e in p2.audit.by_action("mcp.tenant.restored"))
    _assert_correlated(p1)
    _assert_correlated(p2)
    assert p2.audit.verify().ok
