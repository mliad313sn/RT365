"""Short-lived agent workload identity; every tool call is signed with a nonce and issue time [C3 §3; review F-01, F-07, F-08]."""

from __future__ import annotations

import hmac
import json
from collections.abc import Callable
from datetime import datetime, timedelta
from hashlib import sha256
from pathlib import Path

from rtcore.errors import ControlDenied
from rtcore.ids import hash_of, new_id
from rtcore.schemas.base import StrictModel

from mcp_servers.revocation import RevocationList

CALL_MAX_AGE = timedelta(seconds=60)


class AgentIdentity(StrictModel):
    token_id: str
    agent_id: str
    tenant_id: str
    account_id: str
    strategy_id: str
    strategy_version: str
    model_id: str
    model_version: str
    prompt_id: str
    prompt_version: str
    issued_at: datetime
    expires_at: datetime
    secret: str  # per-token HMAC secret; never logged, never passed to handlers


class Principal(StrictModel):
    """The identity view handlers receive: no secret."""

    token_id: str
    agent_id: str
    tenant_id: str
    account_id: str
    strategy_id: str
    strategy_version: str
    model_id: str
    model_version: str
    prompt_id: str
    prompt_version: str

    @classmethod
    def of(cls, ident: AgentIdentity) -> Principal:
        return cls(**{k: getattr(ident, k) for k in cls.model_fields})


class CallSignature(StrictModel):
    nonce: str
    issued_at: datetime
    signature: str


class IdentityIssuer:
    def __init__(
        self,
        *,
        default_ttl: timedelta = timedelta(minutes=5),
        revocations: RevocationList | None = None,
        audit: Callable[[str, dict[str, object]], object] | None = None,
        nonce_path: Path | None = None,
    ) -> None:
        self._ttl = default_ttl
        self._tokens: dict[str, AgentIdentity] = {}
        self._revocations = revocations or RevocationList()
        self._audit = audit or (lambda action, payload: None)
        # nonces are keyed per agent (not per token) and journalled, so a replay survives neither a token
        # re-issue nor a process restart (IVA-08). Deployment target: replicated store [Open: R-05].
        self._seen_nonces: dict[str, set[str]] = {}
        self._nonce_path = nonce_path
        if nonce_path is not None and nonce_path.exists():
            for line in nonce_path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    rec = json.loads(line)
                    self._seen_nonces.setdefault(str(rec["agent_id"]), set()).add(str(rec["nonce"]))

    def adopt(self, ident: AgentIdentity) -> None:
        """Re-register an identity restored from a durable token store after a restart [Open: R-05]."""
        self._tokens[ident.token_id] = ident

    def _remember_nonce(self, ident: AgentIdentity, nonce: str, issued_at: datetime) -> None:
        self._seen_nonces.setdefault(ident.agent_id, set()).add(nonce)
        if self._nonce_path is not None:
            self._nonce_path.parent.mkdir(parents=True, exist_ok=True)
            with self._nonce_path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps({"agent_id": ident.agent_id, "nonce": nonce, "issued_at": issued_at.isoformat()}) + "\n")

    def issue(
        self,
        *,
        agent_id: str,
        tenant_id: str,
        account_id: str,
        strategy_id: str,
        strategy_version: str,
        model_id: str,
        model_version: str,
        prompt_id: str,
        prompt_version: str,
        now: datetime,
        ttl: timedelta | None = None,
        issued_by: str = "identity_service",
    ) -> AgentIdentity:
        ident = AgentIdentity(
            token_id=new_id("tok"),
            agent_id=agent_id,
            tenant_id=tenant_id,
            account_id=account_id,
            strategy_id=strategy_id,
            strategy_version=strategy_version,
            model_id=model_id,
            model_version=model_version,
            prompt_id=prompt_id,
            prompt_version=prompt_version,
            issued_at=now,
            expires_at=now + (ttl or self._ttl),
            secret=new_id("sec"),
        )
        self._tokens[ident.token_id] = ident
        self._audit(
            "mcp.identity.issued",
            {
                "token_id": ident.token_id,
                "agent_id": agent_id,
                "tenant": tenant_id,
                "account": account_id,
                "strategy": f"{strategy_id}@{strategy_version}",
                "model": f"{model_id}@{model_version}",
                "expires_at": ident.expires_at.isoformat(),
                "issued_by": issued_by,
            },
        )
        return ident

    def _mac(self, ident: AgentIdentity, tool: str, args: dict[str, object], nonce: str, issued_at: datetime) -> str:
        return hmac.new(
            ident.secret.encode(), f"{ident.token_id}|{tool}|{hash_of(args)}|{nonce}|{issued_at.isoformat()}".encode(), sha256
        ).hexdigest()

    def sign_call(
        self, ident: AgentIdentity, tool: str, args: dict[str, object], *, now: datetime, nonce: str | None = None
    ) -> CallSignature:
        n = nonce or new_id("nonce")
        return CallSignature(nonce=n, issued_at=now, signature=self._mac(ident, tool, args, n, now))

    def verify(self, token_id: str, *, tool: str, args: dict[str, object], call: CallSignature, now: datetime) -> AgentIdentity:
        ident = self._tokens.get(token_id)
        if ident is None:
            raise ControlDenied("unknown agent identity")
        if ident.expires_at <= now:
            raise ControlDenied("agent identity expired")
        if self._revocations.is_revoked("agent", ident.agent_id):
            raise ControlDenied("agent identity revoked")
        for level, target in (
            (("TENANT", ident.tenant_id)),
            ("ACCOUNT", ident.account_id),
            ("STRATEGY", ident.strategy_id),
            ("PLATFORM", "*"),
        ):
            if self._revocations.is_revoked("scope", f"{level}:{target}"):
                raise ControlDenied(f"agent identity revoked at {level} level")
        if not hmac.compare_digest(self._mac(ident, tool, args, call.nonce, call.issued_at), call.signature):
            raise ControlDenied("tool call signature invalid")
        if abs((now - call.issued_at).total_seconds()) > CALL_MAX_AGE.total_seconds():
            raise ControlDenied("tool call signature too old (replay window)")
        if call.nonce in self._seen_nonces.get(ident.agent_id, set()):
            raise ControlDenied("tool call replayed (nonce already used)")
        self._remember_nonce(ident, call.nonce, call.issued_at)
        return ident

    def revoke_agent(self, agent_id: str, *, by: str = "system", now: datetime | None = None, reason: str = "") -> None:
        self._revocations.revoke("agent", agent_id, by=by, at=now or datetime.now().astimezone(), reason=reason)
        self._audit("mcp.identity.revoked", {"agent_id": agent_id, "by": by, "reason": reason})

    def revoke_scope(self, level: str, target: str, *, by: str = "killswitch", now: datetime | None = None) -> list[str]:
        self._revocations.revoke("scope", f"{level}:{target}", by=by, at=now or datetime.now().astimezone())
        return [
            i.agent_id
            for i in self._tokens.values()
            if level == "PLATFORM"
            or (level == "TENANT" and i.tenant_id == target)
            or (level == "ACCOUNT" and i.account_id == target)
            or (level == "STRATEGY" and i.strategy_id == target)
        ]

    def restore_scope(self, level: str, target: str, *, by: str = "two-person", now: datetime | None = None) -> None:
        self._revocations.lift("scope", f"{level}:{target}", by=by, at=now or datetime.now().astimezone())
