"""Short-lived agent workload identity; every tool call is signed and carries model and prompt versions [C3 §3]."""

from __future__ import annotations

import hmac
from datetime import datetime, timedelta
from hashlib import sha256

from rtcore.errors import ControlDenied
from rtcore.ids import hash_of, new_id
from rtcore.schemas.base import StrictModel


class AgentIdentity(StrictModel):
    token_id: str
    agent_id: str
    tenant_id: str
    account_id: str
    strategy_id: str
    model_id: str
    model_version: str
    prompt_id: str
    prompt_version: str
    issued_at: datetime
    expires_at: datetime
    secret: str  # per-token HMAC secret; never logged


class IdentityIssuer:
    def __init__(self, *, default_ttl: timedelta = timedelta(minutes=5)) -> None:
        self._ttl = default_ttl
        self._tokens: dict[str, AgentIdentity] = {}
        self._revoked_agents: set[str] = set()
        self._revoked_scopes: set[tuple[str, str]] = set()  # (level, target)

    def issue(
        self,
        *,
        agent_id: str,
        tenant_id: str,
        account_id: str,
        strategy_id: str,
        model_id: str,
        model_version: str,
        prompt_id: str,
        prompt_version: str,
        now: datetime,
        ttl: timedelta | None = None,
    ) -> AgentIdentity:
        ident = AgentIdentity(
            token_id=new_id("tok"),
            agent_id=agent_id,
            tenant_id=tenant_id,
            account_id=account_id,
            strategy_id=strategy_id,
            model_id=model_id,
            model_version=model_version,
            prompt_id=prompt_id,
            prompt_version=prompt_version,
            issued_at=now,
            expires_at=now + (ttl or self._ttl),
            secret=new_id("sec"),
        )
        self._tokens[ident.token_id] = ident
        return ident

    def sign_call(self, ident: AgentIdentity, tool: str, args: dict[str, object]) -> str:
        return hmac.new(ident.secret.encode(), f"{ident.token_id}|{tool}|{hash_of(args)}".encode(), sha256).hexdigest()

    def verify(self, token_id: str, *, tool: str, args: dict[str, object], signature: str, now: datetime) -> AgentIdentity:
        ident = self._tokens.get(token_id)
        if ident is None:
            raise ControlDenied("unknown agent identity")
        if ident.expires_at <= now:
            raise ControlDenied("agent identity expired")
        if ident.agent_id in self._revoked_agents:
            raise ControlDenied("agent identity revoked")
        for level, target in self._revoked_scopes:
            if (
                (level == "TENANT" and ident.tenant_id == target)
                or (level == "ACCOUNT" and ident.account_id == target)
                or (level == "STRATEGY" and ident.strategy_id == target)
                or level == "PLATFORM"
            ):
                raise ControlDenied(f"agent identity revoked at {level} level")
        if not hmac.compare_digest(self.sign_call(ident, tool, args), signature):
            raise ControlDenied("tool call signature invalid")
        return ident

    def revoke_agent(self, agent_id: str) -> None:
        self._revoked_agents.add(agent_id)

    def revoke_scope(self, level: str, target: str) -> list[str]:
        self._revoked_scopes.add((level, target))
        return [
            i.agent_id
            for i in self._tokens.values()
            if level == "PLATFORM"
            or (level == "TENANT" and i.tenant_id == target)
            or (level == "ACCOUNT" and i.account_id == target)
            or (level == "STRATEGY" and i.strategy_id == target)
        ]

    def restore_scope(self, level: str, target: str) -> None:
        self._revoked_scopes.discard((level, target))
