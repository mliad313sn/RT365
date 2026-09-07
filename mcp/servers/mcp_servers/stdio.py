"""MCP stdio transport for the six allowed capabilities [Source: 04; C3; ADR-016].

Speaks the Model Context Protocol (JSON-RPC 2.0, one frame per line) so that an external agent host —
Claude Code, any MCP client — reaches the tool runtime through the same ``ToolRuntime.call`` path as the
BFF agent route. The transport adds no capability: it lists what the signed registry lists, calls what the
runtime allows, and exposes neither resources, prompts nor sampling. Identity is bound by the process that
starts the server (``rt365 mcp-serve``); nothing a client sends can choose or change it.

Structural rules (TC-AI-005, TC-AI-014): this module imports no execution, broker, Kill Switch, policy-mutation,
shell, socket or HTTP module and never imports the composition root.
"""

from __future__ import annotations

import json
import re
from collections.abc import Callable, Iterable
from typing import IO, Any

from rtcore.ids import canonical_json

from mcp_servers.registry import ToolRegistry, ToolSpec
from mcp_servers.runtime import ToolResult

PROTOCOL_VERSION = "2025-06-18"
MAX_LINE_BYTES = 1_048_576  # one frame; per-tool payload limits inside the runtime are stricter
SERVER_NAME = "rt365-sim"
INSTRUCTIONS = (
    "Global AI-MCP RoboTrader dev/sim tool server. Tools may research, analyse, simulate and submit typed trade "
    "intents to the Control-plane intent queue only. No broker route, no secrets, no limit changes, no audit deletion, "
    "no mode changes exist here; every call is identity-bound, allowlisted, quota-limited, schema-validated and audited. "
    "Profit is an objective, never a promise; simulated outputs are not performance evidence."
)
_ID_PREFIX = re.compile(r'"id"\s*:\s*("(?:[^"\\]|\\.)*"|-?\d+)')

CallFn = Callable[[str, dict[str, Any]], ToolResult]


def _error(req_id: Any, code: int, message: str) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}}


def _tool_description(spec: ToolSpec) -> str:
    return (
        f"{spec.scope} [class={spec.tool_class}; provenance={spec.output_provenance}; masking={spec.masking}; "
        f"owner={spec.owner}; quota={spec.quota_per_minute}/min; timeout={spec.timeout_s}s; payload<={spec.payload_limit_bytes}B]"
    )


class StdioMcpServer:
    def __init__(self, *, tools: Iterable[ToolSpec], call: CallFn, server_name: str = SERVER_NAME, server_version: str = "0.1.0") -> None:
        self._tools = {t.name: t for t in tools}
        self._call = call
        self._name = server_name
        self._version = server_version
        self.frames_served = 0
        self.frames_rejected = 0

    # --- protocol -------------------------------------------------------------------------------------------
    def tool_list(self) -> list[dict[str, Any]]:
        return [
            {
                "name": spec.name,
                "description": _tool_description(spec),
                "inputSchema": spec.input_schema,
                "outputSchema": spec.output_schema,
            }
            for spec in self._tools.values()
        ]

    def _tool_call(self, req_id: Any, params: Any) -> dict[str, Any]:
        if not isinstance(params, dict) or not isinstance(params.get("name"), str):
            return _error(req_id, -32602, "tools/call requires params.name")
        args = params.get("arguments", {})
        if not isinstance(args, dict):
            return _error(req_id, -32602, "tools/call arguments must be an object")
        # params._meta and any other client-supplied field are ignored: identity is bound server-side (TC-AI-014)
        try:
            res = self._call(params["name"], args)
        except Exception as exc:  # noqa: BLE001 - the runtime audits its own failures; the transport must not leak details
            return _error(req_id, -32603, f"tool call failed: {type(exc).__name__}")
        if res.ok:
            structured: dict[str, Any] = res.output or {}
            text = canonical_json(structured)
        else:
            structured = {"error_code": res.error_code or "DENIED", "tool": res.tool, "call_hash": res.call_hash}
            text = canonical_json(structured)
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {"content": [{"type": "text", "text": text}], "structuredContent": structured, "isError": not res.ok},
        }

    def handle(self, line: str) -> dict[str, Any] | None:
        """One frame in, at most one frame out (``None`` for notifications and empty lines)."""
        if not line.strip():
            return None
        if len(line.encode("utf-8", errors="replace")) > MAX_LINE_BYTES:
            self.frames_rejected += 1
            m = _ID_PREFIX.search(line[:512])
            req_id: Any = json.loads(m.group(1)) if m else None
            return _error(req_id, -32600, f"frame exceeds {MAX_LINE_BYTES} bytes; refused before parsing")
        try:
            msg = json.loads(line)
        except ValueError:
            self.frames_rejected += 1
            return _error(None, -32700, "parse error")
        if not isinstance(msg, dict) or msg.get("jsonrpc") != "2.0" or not isinstance(msg.get("method"), str):
            self.frames_rejected += 1
            return _error(
                msg.get("id") if isinstance(msg, dict) else None, -32600, "invalid request (JSON-RPC 2.0 with a method is required)"
            )
        self.frames_served += 1
        method, req_id, params = msg["method"], msg.get("id"), msg.get("params")
        if method.startswith("notifications/"):
            return None
        if req_id is None:
            return None  # a request without an id is a notification by definition; nothing to answer
        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": PROTOCOL_VERSION,
                    "capabilities": {"tools": {"listChanged": False}},
                    "serverInfo": {"name": self._name, "version": self._version},
                    "instructions": INSTRUCTIONS,
                },
            }
        if method == "ping":
            return {"jsonrpc": "2.0", "id": req_id, "result": {}}
        if method == "tools/list":
            return {"jsonrpc": "2.0", "id": req_id, "result": {"tools": self.tool_list()}}
        if method == "tools/call":
            return self._tool_call(req_id, params)
        return _error(req_id, -32601, f"method not supported by this server: {method}")

    def serve(self, src: IO[str], dst: IO[str]) -> None:
        """Blocking loop over newline-delimited frames; a bad frame is answered and the loop continues (TC-AI-015)."""
        for line in src:
            resp = self.handle(line.rstrip("\r\n"))
            if resp is not None:
                dst.write(json.dumps(resp, separators=(",", ":")) + "\n")
                dst.flush()


def build_stdio_server(registry: ToolRegistry, call: CallFn, *, server_name: str = SERVER_NAME) -> StdioMcpServer:
    """Expose exactly the signed registry's tools; ``call`` is the identity-bound runtime call installed by the host process."""
    return StdioMcpServer(tools=registry.tools.values(), call=call, server_name=server_name, server_version=registry.registry_version)
