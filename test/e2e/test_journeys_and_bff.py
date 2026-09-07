"""E2E journeys J-03..J-08 through the BFF [Source: 09; JOURNEYS.md]."""

from __future__ import annotations

import pytest
from conftest import ACCOUNT, INSTRUMENT, PM, RISK_OFFICER, SRE, TRADER
from fastapi.testclient import TestClient
from rtcore.schemas.account import AccountMode
from web_bff.app import create_app
from web_bff.platform import build_sim_platform


def hdr(actor, mfa: str = "verified") -> dict[str, str]:  # type: ignore[no-untyped-def]
    return {"X-Actor-Id": actor.actor_id, "X-Actor-Role": actor.role.value, "X-MFA": mfa}


def signed(p, ident, body) -> dict[str, str]:  # type: ignore[no-untyped-def]
    sig = p.issuer.sign_call(ident, "submit_trade_intent", {"intent": body}, now=p.now)
    return {
        "Authorization": f"Bearer {ident.token_id}",
        "X-Call-Signature": sig.signature,
        "X-Call-Nonce": sig.nonce,
        "X-Call-Issued-At": sig.issued_at.isoformat(),
    }


@pytest.fixture
def client():  # type: ignore[no-untyped-def]
    p = build_sim_platform(mode=AccountMode.SUPERVISED)
    return TestClient(create_app(p)), p


@pytest.mark.tc("TC-E2E-J03")
@pytest.mark.req("FR-12")
@pytest.mark.quartet("positive")
def test_j03_supervised_order_end_to_end(client):  # type: ignore[no-untyped-def]
    """J-03: agent submits intent via signed identity -> eligibility -> risk -> approval queue -> human approves -> fill -> reconcile -> audit search."""
    c, p = client
    ident = p.issue_agent()
    body = p.make_intent()
    r = c.post("/v1/intents", json=body, headers=signed(p, ident, body))
    assert r.status_code == 202, r.text
    intent_id, corr = r.json()["intent_id"], r.json()["correlation_id"]
    pr = c.post(f"/v1/intents/{intent_id}/process", headers=hdr(RISK_OFFICER))
    assert pr.status_code == 200 and pr.json()["decision"]["outcome"] == "REQUIRES_HUMAN_APPROVAL"
    queue = c.get("/v1/approvals", headers=hdr(PM)).json()
    assert len(queue) == 1 and queue[0]["reasons_explained"][0]["code"] == "RK-MODE-SUPERVISED"
    from conftest import OPS

    denied = c.post(f"/v1/approvals/{queue[0]['approval_id']}/approve", json={"reason": "self"}, headers=hdr(OPS))
    assert denied.status_code == 403  # operations role holds no APPROVE_ORDER permission
    ok = c.post(f"/v1/approvals/{queue[0]['approval_id']}/approve", json={"reason": "reviewed thesis"}, headers=hdr(PM))
    assert ok.status_code == 200 and ok.json()["state"] == "FILLED"
    dec = c.get(f"/v1/decisions/{pr.json()['decision']['decision_id']}", headers=hdr(RISK_OFFICER)).json()
    assert dec["reasons_explained"][0]["what_you_can_do"]
    audit = c.get("/v1/audit", params={"correlation_id": corr}, headers=hdr(RISK_OFFICER)).json()
    assert {"risk.decided.v1", "approval.recorded", "order.filled.v1"} <= {e["action"] for e in audit}
    assert c.get("/v1/audit/verify", headers=hdr(RISK_OFFICER)).json()["ok"]
    assert c.post("/v1/reconciliation/run", headers=hdr(TRADER)).status_code == 403  # traders cannot run reconciliation
    status = c.get("/v1/status", headers=hdr(RISK_OFFICER)).json()
    assert list(status)[0] == "1_global_status" and "5_pnl" in status and status["4_positions_orders"]["positions"]


@pytest.mark.tc("TC-E2E-J05")
@pytest.mark.req("FR-17")
@pytest.mark.quartet("negative")
def test_j05_kill_switch_via_api(client):  # type: ignore[no-untyped-def]
    """J-05: risk officer activates the Kill Switch; a second person from another line is needed to deactivate; agents/traders denied."""
    c, p = client
    denied = c.post(
        "/v1/killswitch", json={"level": "ACCOUNT", "target_id": ACCOUNT, "reason": "drill", "actor": TRADER.actor_id}, headers=hdr(TRADER)
    )
    assert denied.status_code == 403
    act = c.post(
        "/v1/killswitch",
        json={"level": "ACCOUNT", "target_id": ACCOUNT, "reason": "drill", "actor": RISK_OFFICER.actor_id},
        headers=hdr(RISK_OFFICER),
    )
    assert act.status_code == 202 and c.get("/v1/killswitch", headers=hdr(RISK_OFFICER)).json()
    first = c.post(f"/v1/killswitch/{act.json()['activation_id']}/deactivate", json={"reason": "drill done"}, headers=hdr(RISK_OFFICER))
    assert first.json()["active"] is True
    second = c.post(f"/v1/killswitch/{act.json()['activation_id']}/deactivate", json={"reason": "confirmed"}, headers=hdr(SRE))
    assert second.json()["active"] is False
    assert (
        c.post(
            "/v1/killswitch",
            json={"level": "ACCOUNT", "target_id": ACCOUNT, "reason": "x", "actor": "x"},
            headers=hdr(RISK_OFFICER, mfa="no"),
        ).status_code
        == 401
    )


@pytest.mark.tc("TC-E2E-SCHEMA")
@pytest.mark.req("FR-09")
@pytest.mark.quartet("abuse")
def test_schema_violation_and_non_allowlisted_agent(client):  # type: ignore[no-untyped-def]
    """Unknown field -> 400; research-only strategy identity -> 403; unsigned bearer -> 403; human without MFA -> 401."""
    c, p = client
    ident = p.issue_agent()
    body = {**p.make_intent(), "leverage_override": 10}
    assert c.post("/v1/intents", json=body, headers=signed(p, ident, body)).status_code == 400
    research = p.issue_agent(agent_id="r", strategy_id="strat-research-only")
    body = p.make_intent(strategy_id="strat-research-only")
    assert c.post("/v1/intents", json=body, headers=signed(p, research, body)).status_code == 403
    # bearer without a valid signature / with a replayed nonce is never accepted (security review F-01)
    assert c.post("/v1/intents", json=p.make_intent(), headers={"Authorization": f"Bearer {ident.token_id}"}).status_code == 403
    body = p.make_intent()
    good = signed(p, ident, body)
    assert c.post("/v1/intents", json=body, headers={**good, "X-Call-Signature": "bad"}).status_code == 403
    assert c.post("/v1/intents", json=body, headers=good).status_code == 202
    assert c.post("/v1/intents", json=body, headers=good).status_code == 403  # replay of the same signed call
    assert c.post("/v1/intents", json=p.make_intent(), headers=hdr(TRADER, mfa="none")).status_code == 401
    assert c.get("/v1/reason-codes").status_code == 200 and c.get("/").status_code == 200 and c.get("/healthz").json()["ok"]


@pytest.mark.tc("TC-E2E-J06")
@pytest.mark.req("FR-14")
@pytest.mark.quartet("recovery")
def test_j06_break_ticket_via_api(client):  # type: ignore[no-untyped-def]
    """J-06: reconciliation break visible to operations; resolved with two-person confirmation; limits go through maker-checker."""
    from decimal import Decimal

    from conftest import OPS, TRADING_LEAD

    c, p = client
    r = p.run_intent(p.make_intent())
    p.approve(r.approval_id, PM)
    p.ledger.book(ACCOUNT).positions[INSTRUMENT].quantity += Decimal("1")
    res = c.post("/v1/reconciliation/run", headers=hdr(OPS)).json()
    assert res["breaks"]
    tickets = c.get("/v1/reconciliation/breaks", headers=hdr(OPS)).json()
    tid = tickets[0]["ticket_id"]
    assert (
        c.post(f"/v1/reconciliation/tickets/{tid}/resolve", json={"resolution": "late fill"}, headers=hdr(OPS)).json()["status"]
        == "PENDING_SECOND"
    )
    assert c.post(f"/v1/reconciliation/tickets/{tid}/resolve", json={"resolution": "late fill"}, headers=hdr(OPS)).status_code == 403
    # same line of defense (1st) as the first resolver -> refused; a 2nd-line risk officer may confirm
    assert (
        c.post(f"/v1/reconciliation/tickets/{tid}/resolve", json={"resolution": "confirmed"}, headers=hdr(TRADING_LEAD)).status_code == 403
    )
    assert (
        c.post(f"/v1/reconciliation/tickets/{tid}/resolve", json={"resolution": "confirmed"}, headers=hdr(RISK_OFFICER)).json()["status"]
        == "RESOLVED"
    )
    prop = c.post(
        "/v1/limits", json={"level": "ACCOUNT", "scope_id": ACCOUNT, "metric": "leverage_x", "threshold": "1.5"}, headers=hdr(RISK_OFFICER)
    )
    assert prop.status_code == 202
    assert (
        c.post(f"/v1/limits/{prop.json()['change_id']}/check", json={"reason": "maker cannot check"}, headers=hdr(RISK_OFFICER)).status_code
        == 403
    )
    assert (
        c.post(f"/v1/limits/{prop.json()['change_id']}/check", json={"reason": "reviewed"}, headers=hdr(TRADING_LEAD)).json()["status"]
        == "CHECKED"
    )


@pytest.mark.tc("TC-E2E-AUTH")
@pytest.mark.req("FR-01")
@pytest.mark.quartet("abuse")
def test_dev_header_auth_refuses_non_human_roles_and_non_sim_env(client, monkeypatch):  # type: ignore[no-untyped-def]
    """Agent/system roles cannot be asserted through the human path; the BFF refuses to start outside RT_ENV=sim (R-06)."""
    c, p = client
    for role in ("strategy_agent", "runtime_monitor", "system"):
        r = c.post(
            "/v1/killswitch",
            json={"level": "PLATFORM", "target_id": "*", "reason": "rogue", "actor": "x"},
            headers={"X-Actor-Id": "agent:rogue", "X-Actor-Role": role, "X-MFA": "verified"},
        )
        assert r.status_code == 403, role
        assert (
            c.post(
                "/v1/intents", json=p.make_intent(), headers={"X-Actor-Id": "agent:rogue", "X-Actor-Role": role, "X-MFA": "verified"}
            ).status_code
            == 403
        )
    assert p.killswitch.active() == () and p.alerts.by_name("plane.deny")
    monkeypatch.setenv("RT_ENV", "paper")
    with pytest.raises(RuntimeError):
        create_app(p)
