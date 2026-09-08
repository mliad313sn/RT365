"""FastAPI BFF [Source: 03, 09]. Implements contracts/api/API_OPENAPI.yaml plus the operator endpoints.

Authentication in the dev/sim build [Committee; Open: IdP/MFA integration is E01 human setup]:
- Agents: ``Authorization: Bearer <token_id>`` + ``X-Call-Signature`` (signed MCP identity); the BFF
  routes the call through the MCP tool runtime so every control applies (allowlist, quota, schema).
- Humans: ``X-Actor-Id``, ``X-Actor-Role``, ``X-MFA: verified`` headers stand in for an IdP session.

Tenant isolation (NFR-TEN-01; RAID R-22): the tenant of a human principal is resolved server-side from the
identity service (``accounts.tenant_of_principal``), never from a header — an ``X-Actor-Tenant`` header is
refused and audited. Every read is filtered to the principal's tenant and every write is scope-checked;
another tenant's object is indistinguishable from a missing one (404, no existence leak).
"""

from __future__ import annotations

import asyncio
import os
from datetime import datetime
from datetime import datetime as _dt
from pathlib import Path
from typing import Any

from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from identity_service.rbac import Permission, User, authorize
from killswitch_service.service import KillSwitchLevel
from mcp_servers.identity import CallSignature
from pydantic import BaseModel, Field
from rtcore.clock import utc_now
from rtcore.errors import ControlDenied, PlaneViolation, RTError, SchemaViolation, TransitionError
from rtcore.ids import new_id, sha256_hex
from rtcore.lines import Actor, ActorKind, Role
from rtcore.planes import Plane, enter
from rtcore.resources import resource_root
from rtobs.correlation import correlation
from rtobs.logging import get_logger

from web_bff.platform import SimPlatform, build_sim_platform
from web_bff.reason_codes import REASON_CODES, explain

log = get_logger("web_bff")

# Roles that can never be asserted by a human principal: they are system/agent identities [Source: 00].
NON_HUMAN_ROLES = frozenset({Role.STRATEGY_AGENT, Role.RUNTIME_MONITOR, Role.SYSTEM})


def dev_header_auth_allowed() -> bool:
    """Header-asserted principals exist only in the sim environment (RAID R-06). Any other value refuses to start."""
    return os.environ.get("RT_ENV") == "sim"  # unset is NOT sim: an unlabelled environment fails closed (IVA-06)


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
    static: Path = resource_root() / "apps" / "web" / "static"
    app = FastAPI(title="Global AI-MCP RoboTrader — Control & Execution contracts", version="0.1.0-draft")
    app.state.platform = p
    log.warning(
        "BFF started with DEV HEADER AUTHENTICATION (sim only): principals are client-asserted; not a control", extra={"env": "sim"}
    )

    def now() -> datetime:
        return p.now if platform is not None else utc_now() if False else p.now

    # --- principals ------------------------------------------------------------------------------------------
    def deny_scope(reason: str, *, actor_id: str, tenant: str | None, target: str | None = None) -> None:
        """Audit a tenant-scope refusal (reason code + hashed target, never the other tenant's identifier) with a correlation id."""
        p.audit.append(
            correlation_id=new_id("scope"),
            tenant=tenant or "-",
            account=None,
            actor=actor_id or "-",
            action="tenant.scope.denied",
            payload={"reason": reason, "actor_id": actor_id, "target_hash": sha256_hex(target)[:16] if target else None},
        )

    def human(
        x_actor_id: str | None = Header(default=None),
        x_actor_role: str | None = Header(default=None),
        x_mfa: str | None = Header(default=None),
        x_actor_tenant: str | None = Header(default=None),
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
        if x_actor_tenant is not None:
            # tenant is a server-side fact, never a client claim (RAID R-22): a forged tenant header is refused outright
            deny_scope("TENANT_HEADER_FORGED", actor_id=x_actor_id, tenant=None, target=x_actor_tenant)
            raise HTTPException(403, "tenant is not a client-asserted claim")
        try:
            tenant = p.accounts.tenant_of_principal(x_actor_id)
        except ControlDenied as exc:
            deny_scope("UNBOUND_PRINCIPAL", actor_id=x_actor_id, tenant=None)
            raise HTTPException(403, "principal is not bound to a tenant") from exc
        return Actor(actor_id=x_actor_id, role=role, kind=ActorKind.HUMAN, tenant_id=tenant)

    def tenant_of(actor: Actor) -> str:
        if not actor.tenant_id:  # unreachable through human(); kept so no route can run tenant-less by accident
            raise HTTPException(403, "principal is not bound to a tenant")
        return actor.tenant_id

    def require(actor: Actor, permission: Permission) -> None:
        user = User(
            user_id=actor.actor_id,
            tenant_id=tenant_of(actor),
            roles=(actor.role,),
            mfa_enrolled=True,
            privileged_until=p.now.replace(year=p.now.year + 1),
        )
        try:
            authorize(user, permission, now=p.now, mfa_verified=True)
        except ControlDenied as exc:
            raise HTTPException(403, str(exc)) from exc

    # --- tenant scope helpers: another tenant's object is indistinguishable from a missing one (404) -------------
    def scoped_account(account_id: str, actor: Actor) -> Any:
        acct = p.accounts.get_in_tenant(account_id, tenant_of(actor))
        if acct is None:
            deny_scope("TENANT_SCOPE", actor_id=actor.actor_id, tenant=tenant_of(actor), target=account_id)
            raise HTTPException(404, "unknown account")
        return acct

    def tenant_accounts(actor: Actor) -> tuple[str, ...]:
        return tuple(sorted(a.account_id for a in p.accounts.accounts(tenant_of(actor))))

    def activation_in_scope(act: Any, actor: Actor) -> bool:
        """ACCOUNT activations of the tenant's accounts, the tenant's own TENANT activation, platform-wide levels
        (PLATFORM/ASSET/VENUE) and STRATEGY activations for strategies authorised in the tenant are visible."""
        tenant = tenant_of(actor)
        if act.level == KillSwitchLevel.ACCOUNT:
            return act.target_id in tenant_accounts(actor)
        if act.level == KillSwitchLevel.TENANT:
            return act.target_id == tenant
        if act.level == KillSwitchLevel.STRATEGY:
            return any(act.target_id in a.authorised_strategies for a in p.accounts.accounts(tenant))
        return True

    def scoped_activation(activation_id: str, actor: Actor) -> Any:
        try:
            act = p.killswitch.get(activation_id)
        except KeyError as exc:
            raise HTTPException(404, "unknown activation") from exc
        if not activation_in_scope(act, actor) or act.level in (KillSwitchLevel.PLATFORM, KillSwitchLevel.ASSET, KillSwitchLevel.VENUE):
            # tenant-bound principals never lift a platform-wide switch; other tenants' switches do not exist for them
            deny_scope("TENANT_SCOPE", actor_id=actor.actor_id, tenant=tenant_of(actor), target=activation_id)
            raise HTTPException(404, "unknown activation")
        return act

    def scoped_approval(approval_id: str, actor: Actor) -> Any:
        try:
            item = p.approvals.get(approval_id)
        except KeyError as exc:
            raise HTTPException(404, "unknown approval") from exc
        if item.validated_intent.tenant_id != tenant_of(actor):
            deny_scope("TENANT_SCOPE", actor_id=actor.actor_id, tenant=tenant_of(actor), target=approval_id)
            raise HTTPException(404, "unknown approval")
        return item

    def scoped_ticket(ticket_id: str, actor: Actor) -> Any:
        t = p.tickets.get(ticket_id)
        if t is None or t.brk.account_id not in tenant_accounts(actor):
            deny_scope("TENANT_SCOPE", actor_id=actor.actor_id, tenant=tenant_of(actor), target=ticket_id)
            raise HTTPException(404, "unknown ticket")
        return t

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
        x_call_nonce: str | None = Header(default=None),
        x_call_issued_at: str | None = Header(default=None),
        x_actor_id: str | None = Header(default=None),
        x_actor_role: str | None = Header(default=None),
        x_mfa: str | None = Header(default=None),
        x_actor_tenant: str | None = Header(default=None),
    ) -> dict[str, Any]:
        if authorization and authorization.lower().startswith("bearer "):
            token = authorization.split(" ", 1)[1]
            # Agent path: the request must carry a nonce-bound, time-bound signature over (token, tool, args)
            # (security review F-01: bearer alone is never authentication). Malformed headers fail closed as IDENTITY.
            try:
                issued = _dt.fromisoformat(x_call_issued_at) if x_call_issued_at else p.now
                sig = CallSignature(nonce=x_call_nonce or "", issued_at=issued, signature=x_call_signature or "")
            except (ValueError, TypeError) as exc:
                raise HTTPException(403, {"error": "IDENTITY"}) from exc

            def _call() -> Any:
                with enter(Plane.ANALYTICS):
                    return p.runtime.call(token_id=token, signature=sig, tool="submit_trade_intent", args={"intent": body}, now=p.now)

            res = await asyncio.get_running_loop().run_in_executor(None, _call)
            if not res.ok:
                code = res.error_code or "DENIED"
                status = 400 if code in ("INTENT_SCHEMA", "INPUT_SCHEMA") else 403
                raise HTTPException(status, {"error": code})
            assert res.output is not None
            return {"accepted": True, **res.output}
        actor = human(x_actor_id, x_actor_role, x_mfa, x_actor_tenant)
        require(actor, Permission.SUBMIT_INTENT)
        scoped_account(str(body.get("account_id")), actor)  # the intent's account must sit inside the principal's tenant
        with enter(Plane.EDGE):
            vi = p.intent_queue.submit(body, tenant_id=tenant_of(actor), submitted_by=actor.actor_id, now=p.now)
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
        vi = p.intent_queue.take(intent_id, tenant_of(actor))  # never drains another tenant's intents
        if vi is None:
            deny_scope("TENANT_SCOPE", actor_id=actor.actor_id, tenant=tenant_of(actor), target=intent_id)
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
        st = p.tracker.get_in_tenant(intent_id, tenant_of(actor))
        if st is None:
            deny_scope("TENANT_SCOPE", actor_id=actor.actor_id, tenant=tenant_of(actor), target=intent_id)
            raise HTTPException(404, "unknown intent")
        return st.model_dump(mode="json")

    @app.get("/v1/decisions/{decision_id}")
    async def get_decision(decision_id: str, actor: Actor = Depends(human)) -> dict[str, Any]:
        require(actor, Permission.VIEW_DASHBOARD)
        for ev in p.audit.by_action("risk.decided.v1", tenant=tenant_of(actor)):
            if ev.payload.get("decision_id") == decision_id:
                payload = dict(ev.payload)
                payload["reasons_explained"] = [explain(c) for c in payload.get("reason_codes", [])]
                return payload
        raise HTTPException(404, "decision not found")

    @app.post("/v1/killswitch", status_code=202)
    async def activate_killswitch(body: KillSwitchRequest, actor: Actor = Depends(human)) -> dict[str, Any]:
        require(actor, Permission.ACTIVATE_KILL_SWITCH)
        tenant = tenant_of(actor)
        if body.level == KillSwitchLevel.PLATFORM:
            # a tenant-bound principal never engages the platform-wide switch through the tenant BFF (platform operator path)
            deny_scope("PLATFORM_LEVEL", actor_id=actor.actor_id, tenant=tenant, target=body.target_id)
            raise HTTPException(403, "PLATFORM level is not available to a tenant-bound principal")
        if body.level == KillSwitchLevel.TENANT and body.target_id != tenant:
            deny_scope("TENANT_SCOPE", actor_id=actor.actor_id, tenant=tenant, target=body.target_id)
            raise HTTPException(403, "tenant scope: only the principal's own tenant")
        if body.level == KillSwitchLevel.ACCOUNT:
            scoped_account(body.target_id, actor)
        act = p.killswitch.activate(body.level, body.target_id, reason=body.reason, actor=actor, now=p.now)
        return act.model_dump(mode="json")

    @app.post("/v1/killswitch/{activation_id}/deactivate", status_code=202)
    async def deactivate_killswitch(activation_id: str, body: DeactivateRequest, actor: Actor = Depends(human)) -> dict[str, Any]:
        require(actor, Permission.DEACTIVATE_KILL_SWITCH)
        scoped_activation(activation_id, actor)
        act = p.killswitch.deactivate(activation_id, actor=actor, reason=body.reason, now=p.now)
        return act.model_dump(mode="json")

    @app.get("/v1/killswitch")
    async def list_killswitch(actor: Actor = Depends(human)) -> list[dict[str, Any]]:
        require(actor, Permission.VIEW_DASHBOARD)
        return [a.model_dump(mode="json") for a in p.killswitch.active() if activation_in_scope(a, actor)]

    # --- approvals (FR-12) ---------------------------------------------------------------------------------------
    @app.get("/v1/approvals")
    async def list_approvals(actor: Actor = Depends(human)) -> list[dict[str, Any]]:
        require(actor, Permission.VIEW_DASHBOARD)
        out = []
        for item in p.approvals.pending():
            if item.validated_intent.tenant_id != tenant_of(actor):
                continue
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
        scoped_approval(approval_id, actor)
        order = p.approve(approval_id, actor, reason=body.reason)
        return {"approval_id": approval_id, "order_id": order.order_id, "state": order.state.value}

    @app.post("/v1/approvals/{approval_id}/decline")
    async def decline(approval_id: str, body: ApprovalAction, actor: Actor = Depends(human)) -> dict[str, Any]:
        require(actor, Permission.APPROVE_ORDER)
        scoped_approval(approval_id, actor)
        item = p.approvals.decline(approval_id, actor, reason=body.reason, now=p.now)
        from oms.lifecycle import IntentState

        p.tracker.transition(item.decision.intent_id, IntentState.DECLINED, now=p.now)
        return {"approval_id": approval_id, "status": item.status.value}

    # --- audit (FR-16) -----------------------------------------------------------------------------------------------
    @app.get("/v1/audit")
    async def audit_search(correlation_id: str, actor: Actor = Depends(human)) -> list[dict[str, Any]]:
        require(actor, Permission.VIEW_AUDIT)
        return [e.model_dump(mode="json") for e in p.audit.by_correlation(correlation_id, tenant=tenant_of(actor))]

    @app.get("/v1/audit/verify")
    async def audit_verify(actor: Actor = Depends(human)) -> dict[str, Any]:
        require(actor, Permission.VIEW_AUDIT)
        # ``startup`` is what the platform concluded about its own witness when it started (D-066; ADR-020
        # amendment 2), not a re-run: a reader must be able to tell "verified at boot and passed" from "nobody
        # asked until you did" without inferring it from the process being alive (DR review D-03).
        startup = p.startup_verification
        return {
            **p.audit.verify().model_dump(mode="json"),
            "startup": startup.model_dump(mode="json") if startup is not None else None,
        }

    @app.get("/v1/audit/export")
    async def audit_export(actor: Actor = Depends(human), correlation_id: str | None = None) -> dict[str, Any]:
        require(actor, Permission.EXPORT_AUDIT)
        # the chain head is chain-wide (integrity anchor, no tenant data); the rows are the principal's tenant only
        return {"jsonl": p.audit.export(correlation_id, tenant=tenant_of(actor)), "head_hash": p.audit.head_hash()}

    # --- accounts, reconciliation, limits ------------------------------------------------------------------------------
    @app.get("/v1/accounts/{account_id}")
    async def account(account_id: str, actor: Actor = Depends(human)) -> dict[str, Any]:
        require(actor, Permission.VIEW_DASHBOARD)
        scoped_account(account_id, actor)
        snap = p.account_snapshot(account_id)
        if snap is None:
            raise HTTPException(404, "unknown account")
        return snap.model_dump(mode="json")

    @app.post("/v1/reconciliation/run")
    async def run_reconciliation(actor: Actor = Depends(human), account_id: str | None = None) -> dict[str, Any]:
        require(actor, Permission.RESOLVE_BREAK)
        target = account_id or (tenant_accounts(actor) or ("",))[0]
        scoped_account(target, actor)
        res = p.reconcile(target)
        return res.model_dump(mode="json")

    @app.get("/v1/reconciliation/breaks")
    async def breaks(actor: Actor = Depends(human)) -> list[dict[str, Any]]:
        require(actor, Permission.VIEW_DASHBOARD)
        mine = tenant_accounts(actor)
        return [t.model_dump(mode="json") for t in p.tickets.open_tickets() if t.brk.account_id in mine]

    @app.post("/v1/reconciliation/tickets/{ticket_id}/resolve")
    async def resolve_ticket(ticket_id: str, body: ResolveRequest, actor: Actor = Depends(human)) -> dict[str, Any]:
        require(actor, Permission.RESOLVE_BREAK)
        scoped_ticket(ticket_id, actor)
        return p.tickets.resolve(ticket_id, actor, resolution=body.resolution, now=p.now).model_dump(mode="json")

    @app.post("/v1/limits", status_code=202)
    async def propose_limit(body: LimitProposal, actor: Actor = Depends(human)) -> dict[str, Any]:
        require(actor, Permission.PROPOSE_LIMIT)
        tenant = tenant_of(actor)
        if body.level == "PLATFORM":
            deny_scope("PLATFORM_LEVEL", actor_id=actor.actor_id, tenant=tenant, target=body.scope_id)
            raise HTTPException(403, "PLATFORM limits are not proposed through a tenant principal")
        if body.level == "TENANT" and body.scope_id != tenant:
            deny_scope("TENANT_SCOPE", actor_id=actor.actor_id, tenant=tenant, target=body.scope_id)
            raise HTTPException(403, "tenant scope: only the principal's own tenant")
        if body.level == "ACCOUNT":
            scoped_account(body.scope_id, actor)
        # tenant_id is injected server-side: STRATEGY/INSTRUMENT limits are tenant-qualified and never leak (TC-RK-018)
        change = p.limits_mc.propose("limit.changed", {**body.model_dump(), "tenant_id": tenant}, actor, now=p.now)
        return change.model_dump(mode="json")

    @app.post("/v1/limits/{change_id}/check")
    async def check_limit(change_id: str, body: ApprovalAction, actor: Actor = Depends(human)) -> dict[str, Any]:
        require(actor, Permission.CHECK_LIMIT)
        try:
            change = p.limits_mc.get(change_id)
        except KeyError as exc:
            raise HTTPException(404, "unknown change") from exc
        if change.payload.get("tenant_id") != tenant_of(actor):
            deny_scope("TENANT_SCOPE", actor_id=actor.actor_id, tenant=tenant_of(actor), target=change_id)
            raise HTTPException(404, "unknown change")
        return p.limits_mc.check(change_id, actor, now=p.now, reason=body.reason).model_dump(mode="json")

    @app.get("/v1/reason-codes")
    async def reason_codes() -> list[dict[str, str]]:
        return [explain(c) for c in sorted(REASON_CODES)]

    # --- dashboard model: risk before profit [Source: 09] -----------------------------------------------------------------
    @app.get("/v1/status")
    async def status(actor: Actor = Depends(human)) -> dict[str, Any]:
        require(actor, Permission.VIEW_DASHBOARD)
        tenant = tenant_of(actor)
        mine = tenant_accounts(actor)
        if not mine:
            raise HTTPException(404, "no account in tenant")
        account_id = mine[0]  # dashboard of the tenant's first account (single-account fixture tenants in sim)
        snap = p.account_snapshot(account_id)
        mkt = p.market_snapshot(__import__("web_bff.platform", fromlist=["INSTRUMENT"]).INSTRUMENT)
        health = p.broker.health(now=p.now)
        from risk_engine.policy import LimitScope, Metric, effective_limit

        scope = LimitScope(tenant_id=tenant, account_id=account_id, strategy_id="*", instrument_id="*")
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
                "tenant_id": tenant,
                "account_id": account_id,
                "kill_switch_active": [a.model_dump(mode="json") for a in p.killswitch.active() if activation_in_scope(a, actor)],
                "account_mode": snap.mode.value,
                "trading_status": snap.trading_status.value,
                "autonomy_suspended": snap.autonomy_suspended,
                "broker_connected": health.connected,
                "data_freshness_s": (p.now - mkt.market_ts).total_seconds() if mkt else None,
                "policy_version": p.policy.policy_version if p.policy else "UNAVAILABLE (fail closed)",
                "audit_chain_ok": p.audit.verify().ok,
                # False only when the platform started with a witness that disagreed; None when no external witness
                # is configured, so "not checked" is never displayed as "checked and fine" (D-066, F-01).
                "audit_startup_verified": p.startup_verification.ok if p.startup_verification is not None else None,
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
                "pending_approvals": sum(1 for i in p.approvals.pending() if i.validated_intent.tenant_id == tenant),
            },
            "5_pnl": {
                "nav": str(snap.nav),
                "daily_pnl": str(snap.daily_pnl),
                "note": "PnL is an outcome, never a promise; shown below risk state by design [Source: 09].",
            },
            "6_alerts": [
                {"name": a.name, "severity": a.severity, "auto_action": a.auto_action}
                for a in p.alerts.fired
                # alerts naming another tenant's account or tenant are not this tenant's data; platform-wide ones are shown
                if (a.payload.get("account") in (None, *mine)) and (a.payload.get("tenant") in (None, tenant))
            ][-20:],
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
        return FileResponse(static / "index.html")

    app.mount("/static", StaticFiles(directory=str(static)), name="static")
    return app
