"""FastAPI BFF [Source: 03, 09]. Implements contracts/api/API_OPENAPI.yaml plus the operator endpoints.

Authentication in the dev/sim build [Committee; Open: IdP/MFA integration is E01 human setup]:
- Agents: ``Authorization: Bearer <token_id>`` + ``X-Call-Signature`` (signed MCP identity); the BFF
  routes the call through the MCP tool runtime so every control applies (allowlist, quota, schema).
- Humans: ``X-Actor-Id``, ``X-Actor-Role``, ``X-MFA: verified`` headers stand in for an IdP session.
"""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import Any

from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from identity_service.rbac import Permission, User, authorize
from killswitch_service.service import KillSwitchLevel
from pydantic import BaseModel, Field
from rtcore.clock import utc_now
from rtcore.errors import ControlDenied, PlaneViolation, RTError, SchemaViolation, TransitionError
from rtcore.lines import Actor, ActorKind, Role
from rtcore.planes import Plane, enter
from rtobs.correlation import correlation
from rtobs.logging import get_logger

from web_bff.platform import ACCOUNT, TENANT, SimPlatform, build_sim_platform
from web_bff.reason_codes import REASON_CODES, explain

STATIC = Path(__file__).resolve().parent.parent / "static"
log = get_logger("web_bff")

# Roles that can never be asserted by a human principal: they are system/agent identities [Source: 00].
NON_HUMAN_ROLES = frozenset({Role.STRATEGY_AGENT, Role.RUNTIME_MONITOR, Role.SYSTEM})


def dev_header_auth_allowed() -> bool:
    """Header-asserted principals exist only in the sim environment (RAID R-06). Any other value refuses to start."""
    return os.environ.get("RT_ENV", "sim") == "sim"


class KillSwitchRequest(BaseModel):
    model_config = {"extra": "forbid"}
    level: KillSwitchLevel
    target_id: str
    reason: str = Field(min_length=3)
    actor: str


class ApprovalAction(BaseModel):
    model_config = {"extra": "forbid"}
    reason: str = Field(min_length=3)


class DeactivateRequest(BaseModel):
    model_config = {"extra": "forbid"}
    reason: str = Field(min_length=3)


class LimitProposal(BaseModel):
    model_config = {"extra": "forbid"}
    level: str
    scope_id: str
    metric: str
    threshold: str


class ResolveRequest(BaseModel):
    model_config = {"extra": "forbid"}
    resolution: str = Field(min_length=3)


def create_app(platform: SimPlatform | None = None) -> FastAPI:
    if not dev_header_auth_allowed():
        raise RuntimeError(
            "RT_ENV is not 'sim': the BFF has no IdP/MFA session provider yet (RAID R-06, MISSING_ACTIONS). "
            "Header-asserted principals are refused outside the simulation environment."
        )
    p = platform or build_sim_platform()
    app = FastAPI(title="Global AI-MCP RoboTrader — Control & Execution contracts", version="0.1.0-draft")
    app.state.platform = p
    log.warning(
        "BFF started with DEV HEADER AUTHENTICATION (sim only): principals are client-asserted; not a control", extra={"env": "sim"}
    )

    def now() -> datetime:
        return p.now if platform is not None else utc_now() if False else p.now

    # --- principals ------------------------------------------------------------------------------------------
    def human(
        x_actor_id: str | None = Header(default=None),
        x_actor_role: str | None = Header(default=None),
        x_mfa: str | None = Header(default=None),
    ) -> Actor:
        if not x_actor_id or not x_actor_role:
            raise HTTPException(401, "human principal required (X-Actor-Id, X-Actor-Role)")
        try:
            role = Role(x_actor_role)
        except ValueError as exc:
            raise HTTPException(403, f"unknown role {x_actor_role}") from exc
        if role in NON_HUMAN_ROLES:
            p.alerts.raise_alert("plane.deny", {"source": "edge", "destination": "control", "channel": f"human-path role {role.value}"})
            raise HTTPException(403, f"role {role.value} is not a human role; agents use the signed MCP path")
        if x_mfa != "verified":
            raise HTTPException(401, "MFA required")
        return Actor(actor_id=x_actor_id, role=role, kind=ActorKind.HUMAN, tenant_id=TENANT)

    def require(actor: Actor, permission: Permission) -> None:
        user = User(
            user_id=actor.actor_id,
            tenant_id=TENANT,
            roles=(actor.role,),
            mfa_enrolled=True,
            privileged_until=p.now.replace(year=p.now.year + 1),
        )
        try:
            authorize(user, permission, now=p.now, mfa_verified=True)
        except ControlDenied as exc:
            raise HTTPException(403, str(exc)) from exc

    @app.exception_handler(RTError)
    async def _rt_error(request: Request, exc: RTError) -> JSONResponse:
        status = (
            403
            if isinstance(exc, ControlDenied | PlaneViolation)
            else 400
            if isinstance(exc, SchemaViolation)
            else 409
            if isinstance(exc, TransitionError)
            else 500
        )
        return JSONResponse(status_code=status, content={"error": type(exc).__name__, "detail": str(exc)[:500]})

    # --- contracts/api paths ------------------------------------------------------------------------------------
    @app.post("/v1/intents", status_code=202)
    async def submit_intent(
        body: dict[str, Any],
        authorization: str | None = Header(default=None),
        x_call_signature: str | None = Header(default=None),
        x_actor_id: str | None = Header(default=None),
        x_actor_role: str | None = Header(default=None),
        x_mfa: str | None = Header(default=None),
    ) -> dict[str, Any]:
        if authorization and authorization.lower().startswith("bearer "):
            token = authorization.split(" ", 1)[1]
            with enter(Plane.ANALYTICS):
                res = p.runtime.call(
                    token_id=token, signature=x_call_signature or "", tool="submit_trade_intent", args={"intent": body}, now=p.now
                )
            if not res.ok:
                code = res.error_code or "DENIED"
                status = 400 if code in ("INTENT_SCHEMA", "INPUT_SCHEMA") else 403
                raise HTTPException(status, {"error": code})
            assert res.output is not None
            return {"accepted": True, **res.output}
        actor = human(x_actor_id, x_actor_role, x_mfa)
        require(actor, Permission.SUBMIT_INTENT)
        with enter(Plane.EDGE):
            vi = p.intent_queue.submit(body, tenant_id=TENANT, submitted_by=actor.actor_id, now=p.now)
        return {
            "accepted": True,
            "intent_id": str(vi.intent.intent_id),
            "intent_hash": vi.intent_hash,
            "correlation_id": vi.correlation_id,
            "state": "SCHEMA_VALIDATED",
        }

    @app.post("/v1/intents/{intent_id}/process")
    async def process_intent(intent_id: str, actor: Actor = Depends(human)) -> dict[str, Any]:
        """Dev/sim only: drain the queue and run the control pipeline for the intent (in deployment a consumer does this)."""
        require(actor, Permission.VIEW_DASHBOARD)
        vi = p.intent_queue.pop()
        while vi is not None and str(vi.intent.intent_id) != intent_id:
            vi = p.intent_queue.pop()
        if vi is None:
            raise HTTPException(404, "intent not queued")
        with correlation(vi.correlation_id):
            result = p.pipeline.process(vi, now=p.now)
            p.settle()
        return {
            "intent_id": intent_id,
            "eligibility": result.eligibility.outcome.value,
            "decision": result.decision.model_dump(mode="json") if result.decision else None,
            "approval_id": result.approval_id,
            "final_state": p.tracker.get(intent_id).state.value,
        }

    @app.get("/v1/intents/{intent_id}")
    async def intent_status(intent_id: str, actor: Actor = Depends(human)) -> dict[str, Any]:
        require(actor, Permission.VIEW_DASHBOARD)
        try:
            st = p.tracker.get(intent_id)
        except KeyError as exc:
            raise HTTPException(404, "unknown intent") from exc
        return st.model_dump(mode="json")

    @app.get("/v1/decisions/{decision_id}")
    async def get_decision(decision_id: str, actor: Actor = Depends(human)) -> dict[str, Any]:
        require(actor, Permission.VIEW_DASHBOARD)
        for ev in p.audit.by_action("risk.decided.v1"):
            if ev.payload.get("decision_id") == decision_id:
                payload = dict(ev.payload)
                payload["reasons_explained"] = [explain(c) for c in payload.get("reason_codes", [])]
                return payload
        raise HTTPException(404, "decision not found")

    @app.post("/v1/killswitch", status_code=202)
    async def activate_killswitch(body: KillSwitchRequest, actor: Actor = Depends(human)) -> dict[str, Any]:
        require(actor, Permission.ACTIVATE_KILL_SWITCH)
        act = p.killswitch.activate(body.level, body.target_id, reason=body.reason, actor=actor, now=p.now)
        return act.model_dump(mode="json")

    @app.post("/v1/killswitch/{activation_id}/deactivate", status_code=202)
    async def deactivate_killswitch(activation_id: str, body: DeactivateRequest, actor: Actor = Depends(human)) -> dict[str, Any]:
        require(actor, Permission.DEACTIVATE_KILL_SWITCH)
        act = p.killswitch.deactivate(activation_id, actor=actor, reason=body.reason, now=p.now)
        return act.model_dump(mode="json")

    @app.get("/v1/killswitch")
    async def list_killswitch(actor: Actor = Depends(human)) -> list[dict[str, Any]]:
        require(actor, Permission.VIEW_DASHBOARD)
        return [a.model_dump(mode="json") for a in p.killswitch.active()]

    # --- approvals (FR-12) ---------------------------------------------------------------------------------------
    @app.get("/v1/approvals")
    async def list_approvals(actor: Actor = Depends(human)) -> list[dict[str, Any]]:
        require(actor, Permission.VIEW_DASHBOARD)
        out = []
        for item in p.approvals.pending():
            d = item.decision
            out.append(
                {
                    "approval_id": item.approval_id,
                    "intent_id": d.intent_id,
                    "instrument_id": item.validated_intent.intent.instrument_id,
                    "side": item.validated_intent.intent.side.value,
                    "quantity": str(item.validated_intent.intent.quantity),
                    "maker_id": item.maker_id,
                    "reason_codes": list(d.reason_codes),
                    "reasons_explained": [explain(c) for c in d.reason_codes],
                    "expiry": item.validated_intent.intent.expiry.isoformat(),
                }
            )
        return out

    @app.post("/v1/approvals/{approval_id}/approve")
    async def approve(approval_id: str, body: ApprovalAction, actor: Actor = Depends(human)) -> dict[str, Any]:
        require(actor, Permission.APPROVE_ORDER)
        order = p.approve(approval_id, actor, reason=body.reason)
        return {"approval_id": approval_id, "order_id": order.order_id, "state": order.state.value}

    @app.post("/v1/approvals/{approval_id}/decline")
    async def decline(approval_id: str, body: ApprovalAction, actor: Actor = Depends(human)) -> dict[str, Any]:
        require(actor, Permission.APPROVE_ORDER)
        item = p.approvals.decline(approval_id, actor, reason=body.reason, now=p.now)
        from oms.lifecycle import IntentState

        p.tracker.transition(item.decision.intent_id, IntentState.DECLINED, now=p.now)
        return {"approval_id": approval_id, "status": item.status.value}

    # --- audit (FR-16) -----------------------------------------------------------------------------------------------
    @app.get("/v1/audit")
    async def audit_search(correlation_id: str, actor: Actor = Depends(human)) -> list[dict[str, Any]]:
        require(actor, Permission.VIEW_AUDIT)
        return [e.model_dump(mode="json") for e in p.audit.by_correlation(correlation_id)]

    @app.get("/v1/audit/verify")
    async def audit_verify(actor: Actor = Depends(human)) -> dict[str, Any]:
        require(actor, Permission.VIEW_AUDIT)
        return p.audit.verify().model_dump(mode="json")

    @app.get("/v1/audit/export")
    async def audit_export(actor: Actor = Depends(human), correlation_id: str | None = None) -> dict[str, Any]:
        require(actor, Permission.EXPORT_AUDIT)
        return {"jsonl": p.audit.export(correlation_id), "head_hash": p.audit.head_hash()}

    # --- accounts, reconciliation, limits ------------------------------------------------------------------------------
    @app.get("/v1/accounts/{account_id}")
    async def account(account_id: str, actor: Actor = Depends(human)) -> dict[str, Any]:
        require(actor, Permission.VIEW_DASHBOARD)
        snap = p.account_snapshot(account_id)
        if snap is None:
            raise HTTPException(404, "unknown account")
        return snap.model_dump(mode="json")

    @app.post("/v1/reconciliation/run")
    async def run_reconciliation(actor: Actor = Depends(human)) -> dict[str, Any]:
        require(actor, Permission.RESOLVE_BREAK)
        res = p.reconcile()
        return res.model_dump(mode="json")

    @app.get("/v1/reconciliation/breaks")
    async def breaks(actor: Actor = Depends(human)) -> list[dict[str, Any]]:
        require(actor, Permission.VIEW_DASHBOARD)
        return [t.model_dump(mode="json") for t in p.tickets.open_tickets()]

    @app.post("/v1/reconciliation/tickets/{ticket_id}/resolve")
    async def resolve_ticket(ticket_id: str, body: ResolveRequest, actor: Actor = Depends(human)) -> dict[str, Any]:
        require(actor, Permission.RESOLVE_BREAK)
        return p.tickets.resolve(ticket_id, actor, resolution=body.resolution, now=p.now).model_dump(mode="json")

    @app.post("/v1/limits", status_code=202)
    async def propose_limit(body: LimitProposal, actor: Actor = Depends(human)) -> dict[str, Any]:
        require(actor, Permission.PROPOSE_LIMIT)
        change = p.limits_mc.propose("limit.changed", body.model_dump(), actor, now=p.now)
        return change.model_dump(mode="json")

    @app.post("/v1/limits/{change_id}/check")
    async def check_limit(change_id: str, body: ApprovalAction, actor: Actor = Depends(human)) -> dict[str, Any]:
        require(actor, Permission.CHECK_LIMIT)
        return p.limits_mc.check(change_id, actor, now=p.now, reason=body.reason).model_dump(mode="json")

    @app.get("/v1/reason-codes")
    async def reason_codes() -> list[dict[str, str]]:
        return [explain(c) for c in sorted(REASON_CODES)]

    # --- dashboard model: risk before profit [Source: 09] -----------------------------------------------------------------
    @app.get("/v1/status")
    async def status(actor: Actor = Depends(human)) -> dict[str, Any]:
        require(actor, Permission.VIEW_DASHBOARD)
        snap = p.account_snapshot(ACCOUNT)
        mkt = p.market_snapshot(__import__("web_bff.platform", fromlist=["INSTRUMENT"]).INSTRUMENT)
        health = p.broker.health(now=p.now)
        from risk_engine.policy import LimitScope, Metric, effective_limit

        scope = LimitScope(tenant_id=TENANT, account_id=ACCOUNT, strategy_id="*", instrument_id="*")
        limits = (
            {
                m.value: str(effective_limit(p.policy, m, scope, p.now).threshold)
                for m in (
                    Metric.GROSS_EXPOSURE_PCT_NAV,
                    Metric.NET_EXPOSURE_PCT_NAV,
                    Metric.LEVERAGE_X,
                    Metric.MAX_DRAWDOWN_PCT,
                    Metric.DAILY_LOSS_LIMIT_PCT,
                )
            }
            if p.policy
            else {}
        )
        assert snap is not None
        from rtcore.money import pct

        return {
            "1_global_status": {
                "kill_switch_active": [a.model_dump(mode="json") for a in p.killswitch.active()],
                "account_mode": snap.mode.value,
                "trading_status": snap.trading_status.value,
                "autonomy_suspended": snap.autonomy_suspended,
                "broker_connected": health.connected,
                "data_freshness_s": (p.now - mkt.market_ts).total_seconds() if mkt else None,
                "policy_version": p.policy.policy_version if p.policy else "UNAVAILABLE (fail closed)",
                "audit_chain_ok": p.audit.verify().ok,
            },
            "2_capital_at_risk": {
                "capital_in_use": str(snap.capital_in_use),
                "capital_envelope": str(snap.capital_envelope),
                "drawdown_pct": str(pct(snap.peak_nav - snap.nav, snap.peak_nav) if snap.peak_nav > snap.nav else 0),
                "max_drawdown_limit_pct": limits.get("max_drawdown_pct"),
                "daily_loss_pct": str(pct(-snap.daily_pnl, snap.nav) if snap.daily_pnl < 0 else 0),
                "daily_loss_limit_pct": limits.get("daily_loss_limit_pct"),
            },
            "3_exposure_vs_limits": {
                "gross_pct_nav": str(pct(snap.gross_exposure, snap.nav)),
                "gross_limit_pct": limits.get("gross_exposure_pct_nav"),
                "net_pct_nav": str(pct(abs(snap.net_exposure), snap.nav)),
                "net_limit_pct": limits.get("net_exposure_pct_nav"),
                "leverage_x": str(snap.gross_exposure / snap.nav if snap.nav else 0),
                "leverage_limit_x": limits.get("leverage_x"),
            },
            "4_positions_orders": {
                "positions": [pos.model_dump(mode="json") for pos in snap.positions],
                "open_orders": [o.model_dump(mode="json") for o in snap.open_orders],
                "pending_approvals": len(p.approvals.pending()),
            },
            "5_pnl": {
                "nav": str(snap.nav),
                "daily_pnl": str(snap.daily_pnl),
                "note": "PnL is an outcome, never a promise; shown below risk state by design [Source: 09].",
            },
            "6_alerts": [{"name": a.name, "severity": a.severity, "auto_action": a.auto_action} for a in p.alerts.fired[-20:]],
            "7_data_freshness": {
                "snapshot_id": mkt.snapshot_id if mkt else None,
                "market_ts": mkt.market_ts.isoformat() if mkt else None,
                "provenance": mkt.provenance.value if mkt else None,
                "quality": mkt.quality.value if mkt else None,
            },
        }

    @app.get("/healthz")
    async def healthz() -> dict[str, Any]:
        return {
            "ok": True,
            "environment": "sim",
            "auth": "dev-headers (client-asserted; sim only; RAID R-06)",
            "audit_length": len(p.audit),
        }

    @app.get("/")
    async def index() -> FileResponse:
        return FileResponse(STATIC / "index.html")

    app.mount("/static", StaticFiles(directory=str(STATIC)), name="static")
    return app
