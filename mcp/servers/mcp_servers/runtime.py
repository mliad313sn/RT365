"""Tool runtime: identity -> signed registry -> revocation -> allowlist -> quota -> payload -> input schema
-> handler (deadline) -> output schema -> canary check -> tamper-evident log [Source: 04; C3]."""

from __future__ import annotations

import time
from collections import deque
from collections.abc import Callable
from datetime import datetime
from typing import Any

import jsonschema
from rtcore.errors import ControlDenied, RTError
from rtcore.ids import canonical_json, hash_of
from rtcore.provenance import Provenance, delimit_untrusted
from rtcore.schemas.base import StrictModel

from mcp_servers.allowlist import TenantAllowlist
from mcp_servers.identity import AgentIdentity, IdentityIssuer
from mcp_servers.registry import ToolRegistry

Handler = Callable[[AgentIdentity, dict[str, Any], datetime], dict[str, Any]]


class ToolDenied(RTError):
    def __init__(self, code: str, detail: str) -> None:
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail


class ToolResult(StrictModel):
    tool: str
    ok: bool
    output: dict[str, Any] | None
    error_code: str | None
    elapsed_ms: int
    call_hash: str


class ToolRuntime:
    def __init__(
        self,
        *,
        registry: ToolRegistry,
        issuer: IdentityIssuer,
        allowlists: dict[str, TenantAllowlist],
        audit: Callable[[str, str, str, dict[str, Any]], object],
        alert: Callable[[str, dict[str, Any]], object] | None = None,
    ) -> None:
        self._registry = registry
        self._issuer = issuer
        self._allowlists = allowlists
        self._handlers: dict[str, Handler] = {}
        self._audit = audit  # (action, correlation, tenant, payload)
        self._alert = alert or (lambda name, payload: None)
        self._calls: dict[tuple[str, str], deque[datetime]] = {}
        self._revoked_tools: set[str] = set()
        self._registry_revoked = False

    # --- registration / revocation ---------------------------------------------------------------------
    def register_handler(self, tool: str, handler: Handler) -> None:
        if self._registry.get(tool) is None:
            raise ControlDenied(f"tool {tool} is not in the signed registry; handlers cannot be added dynamically")
        self._handlers[tool] = handler

    def revoke_tool(self, tool: str, *, by: str) -> None:
        self._revoked_tools.add(tool)
        self._audit("mcp.tool.revoked", "-", "-", {"tool": tool, "by": by})

    def revoke_registry(self, *, by: str) -> None:
        """Emergency revocation: every server refuses at next call."""
        self._registry_revoked = True
        self._audit("mcp.registry.revoked", "-", "-", {"by": by})

    def restore_registry(self, registry: ToolRegistry, *, by: str) -> None:
        self._registry = registry
        self._registry_revoked = False
        self._audit("mcp.registry.restored", "-", "-", {"by": by, "version": registry.registry_version})

    @staticmethod
    def label_untrusted(text: str, provenance: Provenance) -> str:
        return delimit_untrusted(text, provenance)

    # --- call path ----------------------------------------------------------------------------------------
    def call(
        self, *, token_id: str, signature: str, tool: str, args: dict[str, Any], now: datetime, correlation_id: str = "-"
    ) -> ToolResult:
        started = time.perf_counter()
        call_hash = hash_of({"token": token_id, "tool": tool, "args": args, "at": now.isoformat()})
        tenant = "-"
        try:
            if self._registry_revoked:
                raise ToolDenied("REGISTRY_REVOKED", "tool registry signature revoked")
            ident = self._issuer.verify(token_id, tool=tool, args=args, signature=signature, now=now)
            tenant = ident.tenant_id
            spec = self._registry.get(tool)
            if spec is None or tool not in self._handlers:
                self._alert("mcp.non_allowlisted_tool", {"tool": tool, "agent": ident.agent_id, "tenant": tenant})
                raise ToolDenied("TOOL_NOT_REGISTERED", f"{tool} is not an allowed capability")
            if tool in self._revoked_tools:
                raise ToolDenied("TOOL_REVOKED", f"{tool} revoked")
            allow = self._allowlists.get(ident.tenant_id)
            if allow is None or not allow.allowed(
                tenant_id=ident.tenant_id, account_id=ident.account_id, strategy_id=ident.strategy_id, tool=tool
            ):
                self._alert("mcp.non_allowlisted_tool", {"tool": tool, "agent": ident.agent_id, "tenant": tenant})
                raise ToolDenied("NOT_ALLOWLISTED", f"{tool} not granted to {ident.tenant_id}/{ident.account_id}/{ident.strategy_id}")
            window = self._calls.setdefault((ident.tenant_id, tool), deque())
            while window and (now - window[0]).total_seconds() > 60:
                window.popleft()
            if len(window) >= spec.quota_per_minute:
                raise ToolDenied("QUOTA_EXCEEDED", f"{tool} quota {spec.quota_per_minute}/min")
            window.append(now)
            arg_bytes = len(canonical_json(args).encode())
            if arg_bytes > spec.payload_limit_bytes:
                raise ToolDenied("PAYLOAD_TOO_LARGE", f"{arg_bytes} > {spec.payload_limit_bytes}")
            for canary in self._registry.canary_tokens:
                if canary in canonical_json(args):
                    self._alert("mcp.canary_in_input", {"tool": tool, "agent": ident.agent_id})
                    raise ToolDenied("CANARY_DETECTED", "exfiltration marker present in input")
            try:
                jsonschema.validate(args, spec.input_schema)
            except jsonschema.ValidationError as exc:
                raise ToolDenied("INPUT_SCHEMA", exc.message) from exc
            output = self._handlers[tool](ident, args, now)
            elapsed = time.perf_counter() - started
            if elapsed > spec.timeout_s:
                raise ToolDenied("TIMEOUT", f"{elapsed:.2f}s > {spec.timeout_s}s; result discarded")
            out_json = canonical_json(output)
            if len(out_json.encode()) > spec.payload_limit_bytes:
                raise ToolDenied("OUTPUT_TOO_LARGE", "tool output exceeds payload limit")
            for canary in self._registry.canary_tokens:
                if canary in out_json:
                    self._alert("mcp.canary_in_output", {"tool": tool, "agent": ident.agent_id})
                    raise ToolDenied("CANARY_DETECTED", "exfiltration marker present in output")
            try:
                jsonschema.validate(output, spec.output_schema)
            except jsonschema.ValidationError as exc:
                raise ToolDenied("OUTPUT_SCHEMA", exc.message) from exc
            result = ToolResult(tool=tool, ok=True, output=output, error_code=None, elapsed_ms=int(elapsed * 1000), call_hash=call_hash)
            self._audit(
                "mcp.tool.called",
                correlation_id,
                tenant,
                {
                    "tool": tool,
                    "agent": ident.agent_id,
                    "model": f"{ident.model_id}@{ident.model_version}",
                    "prompt": f"{ident.prompt_id}@{ident.prompt_version}",
                    "call_hash": call_hash,
                    "ok": True,
                    "output_hash": hash_of(output),
                },
            )
            return result
        except ToolDenied as exc:
            self._audit(
                "mcp.tool.denied", correlation_id, tenant, {"tool": tool, "code": exc.code, "detail": exc.detail, "call_hash": call_hash}
            )
            return ToolResult(
                tool=tool,
                ok=False,
                output=None,
                error_code=exc.code,
                elapsed_ms=int((time.perf_counter() - started) * 1000),
                call_hash=call_hash,
            )
        except ControlDenied as exc:
            self._audit(
                "mcp.tool.denied", correlation_id, tenant, {"tool": tool, "code": "IDENTITY", "detail": str(exc), "call_hash": call_hash}
            )
            return ToolResult(
                tool=tool,
                ok=False,
                output=None,
                error_code="IDENTITY",
                elapsed_ms=int((time.perf_counter() - started) * 1000),
                call_hash=call_hash,
            )
