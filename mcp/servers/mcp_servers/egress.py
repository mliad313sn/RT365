"""Egress allowlist and the one seam through which an MCP tool handler could acquire an outbound client.

Why this file changed [Committee: REVIEW_2026-09-08_threat_model_redteam RT-F1]: ``EgressPolicy.check()`` was
called by no product code. The policy was loaded in the composition root and never consulted, so the test that
appeared to cover it only proved that the YAML parses.

What is true, and is now proved by test rather than asserted: **no MCP tool handler performs network I/O and
none can**. ``mcp_servers`` imports no network module (TC-AI-005) and neither does any first-party module its
six handlers reach (TC-AI-026 walks the transitive import closure and runs every tool under a socket
sentinel). The allowlist is therefore enforced at the point where a *future* handler would acquire a client:
``EgressGuard``. A handler asks the guard for a destination; the guard consults the policy, audits the
decision with the tool call's correlation id and a reason code, and raises ``PlaneViolation`` on anything the
allowlist does not name. With no policy the guard denies everything (``EGRESS_NO_POLICY``) — an unconfigured
guard is never an open one.

This is one half of the control. The deployed half is the NetworkPolicy set (``infra/kubernetes``,
TC-NET-003), which is checked against manifests for a cluster that does not exist yet [Open: H-05].
The guard cannot itself open a socket: nothing in this package may import a network module.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from fnmatch import fnmatch
from pathlib import Path
from typing import Any, TypeVar

import yaml
from rtcore.errors import PlaneViolation

T = TypeVar("T")

POLICY_FILE = "mcp/policies/egress.yaml"
REASON_ALLOWED = "EGRESS_ALLOWED"
REASON_NOT_ALLOWLISTED = "EGRESS_NOT_ALLOWLISTED"
REASON_NO_POLICY = "EGRESS_NO_POLICY"
DENIED_ALERT = "mcp.egress_denied"

AuditFn = Callable[[str, str, str, dict[str, Any]], object]  # (action, correlation_id, tenant, payload)
AlertFn = Callable[[str, dict[str, Any]], object]


class EgressPolicy:
    def __init__(self, allowed_hosts: tuple[str, ...]) -> None:
        self._allowed = allowed_hosts

    @classmethod
    def load(cls, path: Path) -> EgressPolicy:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        return cls(tuple(data.get("allowed_hosts", ())))

    @property
    def allowed_hosts(self) -> tuple[str, ...]:
        return self._allowed

    def match(self, host: str) -> str | None:
        """The allowlist pattern that admits ``host``, or None. An empty allowlist admits nothing."""
        for pattern in self._allowed:
            if fnmatch(host, pattern):
                return pattern
        return None

    def allows(self, host: str) -> bool:
        return self.match(host) is not None

    def check(self, host: str) -> None:
        if not self.allows(host):
            raise PlaneViolation(f"{REASON_NOT_ALLOWLISTED}: egress to {host} denied by {POLICY_FILE}")


@dataclass(frozen=True)
class EgressDecision:
    """What was decided, on what basis: reason code, value and threshold on every decision [Source: 00]."""

    host: str
    allowed: bool
    reason_code: str
    pattern: str | None
    policy: str
    correlation_id: str
    tenant: str
    actor: str
    tool: str

    def payload(self) -> dict[str, Any]:
        return {
            "host": self.host,
            "reason_code": self.reason_code,
            "pattern": self.pattern,
            "policy": self.policy,
            "actor": self.actor,
            "tool": self.tool,
            "allowed": self.allowed,
        }


class EgressGuard:
    """The only sanctioned way for an MCP tool handler to reach a destination outside its process.

    Bound per tool call by ``ToolRuntime`` so every decision carries the call's correlation id, tenant, actor
    and tool. It authorises; it never connects — the caller supplies the client factory, and the factory is
    not called on a denial.
    """

    def __init__(
        self,
        policy: EgressPolicy | None = None,
        *,
        audit: AuditFn | None = None,
        alert: AlertFn | None = None,
        policy_source: str = POLICY_FILE,
        correlation_id: str = "-",
        tenant: str = "-",
        actor: str = "-",
        tool: str = "-",
    ) -> None:
        self._policy = policy
        self._audit = audit or (lambda action, correlation_id, tenant, payload: None)
        self._alert = alert or (lambda name, payload: None)
        self._source = policy_source
        self._correlation_id = correlation_id
        self._tenant = tenant
        self._actor = actor
        self._tool = tool

    @property
    def policy(self) -> EgressPolicy | None:
        return self._policy

    @property
    def policy_source(self) -> str:
        return self._source

    def bound(self, *, correlation_id: str, tenant: str = "-", actor: str = "-", tool: str = "-") -> EgressGuard:
        """A guard for one tool call: same policy and sinks, this call's correlation id."""
        return EgressGuard(
            self._policy,
            audit=self._audit,
            alert=self._alert,
            policy_source=self._source,
            correlation_id=correlation_id or "-",
            tenant=tenant or "-",
            actor=actor or "-",
            tool=tool or "-",
        )

    def decide(self, host: str) -> EgressDecision:
        if self._policy is None:
            reason, pattern = REASON_NO_POLICY, None
        else:
            pattern = self._policy.match(host)
            reason = REASON_ALLOWED if pattern is not None else REASON_NOT_ALLOWLISTED
        return EgressDecision(
            host=host,
            allowed=reason == REASON_ALLOWED,
            reason_code=reason,
            pattern=pattern,
            policy=self._source,
            correlation_id=self._correlation_id,
            tenant=self._tenant,
            actor=self._actor,
            tool=self._tool,
        )

    def check(self, host: str, *, purpose: str = "") -> EgressDecision:
        """Refuse anything the allowlist does not name; audit either way; alert on a denial."""
        decision = self.decide(host)
        payload = {**decision.payload(), "purpose": purpose} if purpose else decision.payload()
        self._audit("mcp.egress.allowed" if decision.allowed else "mcp.egress.denied", decision.correlation_id, decision.tenant, payload)
        if not decision.allowed:
            self._alert(DENIED_ALERT, payload)
            raise PlaneViolation(
                f"{decision.reason_code}: egress to {host} refused by {self._source} "
                f"(tool={decision.tool}, correlation_id={decision.correlation_id})"
            )
        return decision

    def acquire(self, host: str, *, connect: Callable[[str, int | None], T], port: int | None = None, purpose: str = "") -> T:
        """Authorise, then let the caller build its client. Nothing is created for a denied destination."""
        self.check(host, purpose=purpose)
        return connect(host, port)


DENY_ALL = EgressGuard(None)
"""The ambient guard outside a tool call: no policy, therefore no destination. Fail closed, never 'unfiltered'."""
