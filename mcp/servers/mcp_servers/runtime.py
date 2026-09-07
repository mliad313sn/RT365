"""Tool runtime: identity -> signed registry -> revocation -> allowlist -> quota (denials counted) -> payload
-> input schema -> handler under a pre-emptive deadline -> output schema -> canary -> provenance delimiting
-> tamper-evident log [Source: 04; C3]. Addresses review OBJ-3, F-01, F-02, F-03, F-05, F-06, F-13, F-15."""

from __future__ import annotations

import contextvars
import time
from collections import deque
from collections.abc import Callable
from concurrent.futures import Future, ThreadPoolExecutor
from concurrent.futures import TimeoutError as FutureTimeout
from datetime import UTC, datetime
from typing import Any

import jsonschema
from rtcore.errors import ControlDenied, RTError
from rtcore.ids import canonical_json, hash_of, sha256_hex
from rtcore.provenance import TRUSTED_FOR_DECISIONS, Provenance, delimit_untrusted
from rtcore.schemas.base import StrictModel

from mcp_servers.allowlist import TenantAllowlist
from mcp_servers.identity import CallSignature, IdentityIssuer, Principal
from mcp_servers.registry import ToolRegistry
from mcp_servers.revocation import RevocationList

Handler = Callable[[Principal, dict[str, Any], datetime], dict[str, Any]]

_current_principal: contextvars.ContextVar[Principal | None] = contextvars.ContextVar("mcp_principal", default=None)


def current_principal() -> Principal | None:
    """The agent whose tool call is executing (for alert payloads raised inside handlers)."""
    return _current_principal.get()


class ToolDenied(RTError):
    def __init__(self, code: str, detail: str) -> None:
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail


class ToolResult(StrictModel):
    tool: str
    ok: bool
    output: dict[str, Any] | None
    output_provenance: str | None
    error_code: str | None
    elapsed_ms: int
    call_hash: str


def _delimit_strings(value: Any, label: Provenance) -> Any:
    if isinstance(value, str):
        return delimit_untrusted(value, label)
    if isinstance(value, list):
        return [_delimit_strings(v, label) for v in value]
    if isinstance(value, dict):
        return {k: _delimit_strings(v, label) for k, v in value.items()}
    return value


class ToolRuntime:
    def __init__(
        self,
        *,
        registry: ToolRegistry,
        issuer: IdentityIssuer,
        allowlists: dict[str, TenantAllowlist],
        audit: Callable[[str, str, str, dict[str, Any]], object],
        alert: Callable[[str, dict[str, Any]], object] | None = None,
        revocations: RevocationList | None = None,
        quota_clock: Callable[[], datetime] = lambda: datetime.now(tz=UTC),
        tenant_ceiling_per_minute: int = 600,
        deny_limit_per_minute: int = 30,
        workers: int = 4,
    ) -> None:
        self._registry = registry
        self._issuer = issuer
        self._allowlists = allowlists
        self._handlers: dict[str, Handler] = {}
        self._audit = audit  # (action, correlation, tenant, payload)
        self._alert = alert or (lambda name, payload: None)
        self._revocations = revocations or RevocationList()
        self._quota_clock = quota_clock
        self._tenant_ceiling = tenant_ceiling_per_minute
        self._deny_limit = deny_limit_per_minute
        self._calls: dict[str, deque[datetime]] = {}
        self._registry_revoked = self._revocations.is_revoked("registry", registry.registry_version)
        self._pool = ThreadPoolExecutor(max_workers=workers, thread_name_prefix="mcp-handler")

    # --- registration / revocation ---------------------------------------------------------------------
    def register_handler(self, tool: str, handler: Handler) -> None:
        if self._registry.get(tool) is None:
            raise ControlDenied(f"tool {tool} is not in the signed registry; handlers cannot be added dynamically")
        self._handlers[tool] = handler

    def revoke_tool(self, tool: str, *, by: str, now: datetime | None = None, reason: str = "") -> None:
        self._revocations.revoke("tool", tool, by=by, at=now or self._quota_clock(), reason=reason)
        self._audit("mcp.tool.revoked", "-", "-", {"tool": tool, "by": by, "reason": reason})

    def revoke_registry(self, *, by: str, now: datetime | None = None) -> None:
        """Emergency revocation: every runtime sharing the revocation list refuses at next call and after restart."""
        self._revocations.revoke("registry", self._registry.registry_version, by=by, at=now or self._quota_clock())
        self._registry_revoked = True
        self._audit("mcp.registry.revoked", "-", "-", {"by": by, "version": self._registry.registry_version})

    def restore_registry(self, registry: ToolRegistry, *, approvers: tuple[str, str], now: datetime | None = None) -> None:
        """Two distinct human approvers are required to restore (P4 two-person rule)."""
        if len(set(approvers)) != 2 or not all(approvers):
            raise ControlDenied("registry restore requires two distinct approvers")
        self._revocations.lift("registry", registry.registry_version, by="+".join(approvers), at=now or self._quota_clock())
        self._registry = registry
        self._registry_revoked = False
        self._audit("mcp.registry.restored", "-", "-", {"by": list(approvers), "version": registry.registry_version})

    @staticmethod
    def label_untrusted(text: str, provenance: Provenance) -> str:
        return delimit_untrusted(text, provenance)

    # --- quota ---------------------------------------------------------------------------------------------
    def _window(self, key: str) -> deque[datetime]:
        now = self._quota_clock()
        w = self._calls.setdefault(key, deque())
        while w and (now - w[0]).total_seconds() > 60:
            w.popleft()
        return w

    def _count(self, key: str) -> int:
        w = self._window(key)
        w.append(self._quota_clock())
        return len(w)

    # --- call path ----------------------------------------------------------------------------------------
    def call(
        self, *, token_id: str, signature: CallSignature, tool: str, args: dict[str, Any], now: datetime, correlation_id: str = "-"
    ) -> ToolResult:
        started = time.perf_counter()
        call_hash = hash_of({"token": token_id, "tool": tool, "args": args, "nonce": signature.nonce})
        tenant = "-"
        actor = f"token:{token_id[-8:]}"

        def deny(code: str, detail: str, *, alert: str | None = None, extra: dict[str, Any] | None = None) -> ToolResult:
            # F-15: codes and hashes only in the immutable chain, never agent-supplied text
            self._audit(
                "mcp.tool.denied",
                correlation_id,
                tenant,
                {"tool": tool, "code": code, "detail_hash": sha256_hex(detail)[:16], "actor": actor, "call_hash": call_hash},
            )
            if alert is not None:
                self._alert(alert, {"tool": tool, "tenant": tenant, "code": code, **(extra or {})})
            return ToolResult(
                tool=tool,
                ok=False,
                output=None,
                output_provenance=None,
                error_code=code,
                elapsed_ms=int((time.perf_counter() - started) * 1000),
                call_hash=call_hash,
            )

        if self._registry_revoked or self._revocations.is_revoked("registry", self._registry.registry_version):
            return deny("REGISTRY_REVOKED", "tool registry signature revoked")
        # 1. identity (its own try block: handler errors are never relabelled as identity failures — F-02)
        try:
            ident = self._issuer.verify(token_id, tool=tool, args=args, call=signature, now=now)
        except ControlDenied as exc:
            if self._count(f"deny:{token_id}") > self._deny_limit:
                return deny("DENY_RATE", "too many denials for this token")
            return deny("IDENTITY", str(exc))
        tenant = ident.tenant_id
        actor = f"agent:{ident.agent_id}"
        principal = Principal.of(ident)
        scope = {"agent": ident.agent_id, "account": ident.account_id, "strategy": ident.strategy_id}
        # 2. quota first, so denials and alert storms are bounded (F-06, OBJ-3c)
        if self._count(f"deny:{token_id}") > self._deny_limit:
            return deny("DENY_RATE", "too many denied calls for this token")
        spec = self._registry.get(tool)
        if spec is None or tool not in self._handlers:
            return deny("TOOL_NOT_REGISTERED", f"{tool} is not an allowed capability", alert="mcp.non_allowlisted_tool", extra=scope)
        if self._revocations.is_revoked("tool", tool):
            return deny("TOOL_REVOKED", f"{tool} revoked")
        allow = self._allowlists.get(ident.tenant_id)
        if allow is None or not allow.allowed(
            tenant_id=ident.tenant_id, account_id=ident.account_id, strategy_id=ident.strategy_id, tool=tool
        ):
            return deny("NOT_ALLOWLISTED", f"{tool} not granted to this scope", alert="mcp.non_allowlisted_tool", extra=scope)
        # the deny bucket above already consumed a slot; the successful-path quota is per scope plus a tenant ceiling
        self._window(f"deny:{token_id}").pop()
        if self._count(f"{ident.tenant_id}/{ident.account_id}/{ident.strategy_id}/{tool}") > spec.quota_per_minute:
            return deny("QUOTA_EXCEEDED", f"{tool} quota {spec.quota_per_minute}/min for this scope")
        if self._count(f"tenant:{ident.tenant_id}") > self._tenant_ceiling:
            return deny("QUOTA_EXCEEDED", "tenant ceiling")
        arg_json = canonical_json(args)
        if len(arg_json.encode()) > spec.payload_limit_bytes:
            return deny("PAYLOAD_TOO_LARGE", "input exceeds payload limit")
        for canary in self._registry.canary_tokens:
            if canary in arg_json:
                return deny("CANARY_DETECTED", "exfiltration marker present in input", alert="mcp.canary_in_input", extra=scope)
        try:
            jsonschema.validate(args, spec.input_schema)
        except jsonschema.ValidationError as exc:
            return deny("INPUT_SCHEMA", exc.message)
        # 3. handler under a pre-emptive deadline (F-05); the principal never carries the token secret (F-08)
        token = _current_principal.set(principal)
        future: Future[dict[str, Any]] = self._pool.submit(self._handlers[tool], principal, args, now)
        try:
            output = future.result(timeout=spec.timeout_s)
        except FutureTimeout:
            future.cancel()
            return deny("TIMEOUT", f"handler exceeded {spec.timeout_s}s; result discarded", alert="mcp.handler_timeout", extra=scope)
        except ToolDenied as exc:
            return deny(exc.code, exc.detail)
        except ControlDenied as exc:
            return deny("HANDLER_DENIED", str(exc))
        except Exception as exc:  # noqa: BLE001 - every failure must leave an audit row (F-03)
            return deny("HANDLER_ERROR", f"{type(exc).__name__}", alert="mcp.handler_error", extra=scope)
        finally:
            _current_principal.reset(token)
        out_json = canonical_json(output)
        if len(out_json.encode()) > spec.payload_limit_bytes:
            return deny("OUTPUT_TOO_LARGE", "tool output exceeds payload limit")
        for canary in self._registry.canary_tokens:
            if canary in out_json:
                return deny("CANARY_DETECTED", "exfiltration marker present in output", alert="mcp.canary_in_output", extra=scope)
        try:
            jsonschema.validate(output, spec.output_schema)
        except jsonschema.ValidationError as exc:
            return deny("OUTPUT_SCHEMA", exc.message)
        # 4. provenance: anything not trusted for decisions is delimited before it can reach a model context (F-13)
        prov = Provenance(spec.output_provenance) if spec.output_provenance in Provenance._value2member_map_ else None
        if prov is not None and prov not in TRUSTED_FOR_DECISIONS:
            output = _delimit_strings(output, prov)
        elapsed = time.perf_counter() - started
        self._audit(
            "mcp.tool.called",
            correlation_id,
            tenant,
            {
                "tool": tool,
                "actor": actor,
                "agent": ident.agent_id,
                "model": f"{ident.model_id}@{ident.model_version}",
                "prompt": f"{ident.prompt_id}@{ident.prompt_version}",
                "strategy": f"{ident.strategy_id}@{ident.strategy_version}",
                "call_hash": call_hash,
                "ok": True,
                "output_hash": hash_of(output),
                "output_provenance": spec.output_provenance,
            },
        )
        return ToolResult(
            tool=tool,
            ok=True,
            output=output,
            output_provenance=spec.output_provenance,
            error_code=None,
            elapsed_ms=int(elapsed * 1000),
            call_hash=call_hash,
        )
