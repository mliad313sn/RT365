"""TC-AI-012..015 — MCP stdio server [Source: 04; FR-09; C3]: the transport that lets an external agent host (Claude Code,
any MCP client) reach the six allowed capabilities, and nothing else, through the same ToolRuntime as the BFF path."""

from __future__ import annotations

import io
import json
from typing import Any

import pytest
from conftest import ACCOUNT, INSTRUMENT
from mcp_servers.stdio import MAX_LINE_BYTES, PROTOCOL_VERSION, StdioMcpServer, build_stdio_server


def _run(server: StdioMcpServer, messages: list[Any]) -> list[dict[str, Any]]:
    src = io.StringIO("".join((m if isinstance(m, str) else json.dumps(m)) + "\n" for m in messages))
    dst = io.StringIO()
    server.serve(src, dst)
    return [json.loads(line) for line in dst.getvalue().splitlines() if line.strip()]


def _init() -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": PROTOCOL_VERSION, "capabilities": {}}}


@pytest.mark.tc("TC-AI-012")
@pytest.mark.req("FR-09")
@pytest.mark.quartet("positive")
def test_stdio_server_lists_exactly_the_six_tools_and_serves_them(platform):  # type: ignore[no-untyped-def]
    """An MCP client initialises, lists exactly the six registered tools with their signed input schemas, and a read call returns masked output."""
    ident = platform.issue_agent()
    server = build_stdio_server(platform.registry, lambda tool, args: platform.tool_call(ident, tool, args))
    out = _run(
        server,
        [
            _init(),
            {"jsonrpc": "2.0", "method": "notifications/initialized"},
            {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
            {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {"name": "read_market_snapshot", "arguments": {"instrument_id": INSTRUMENT}},
            },
            {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "tools/call",
                "params": {"name": "read_account_state", "arguments": {"account_id": ACCOUNT}},
            },
            {"jsonrpc": "2.0", "id": 5, "method": "ping"},
        ],
    )
    by_id = {m["id"]: m for m in out}
    assert by_id[1]["result"]["protocolVersion"] == PROTOCOL_VERSION
    assert by_id[1]["result"]["capabilities"] == {"tools": {"listChanged": False}}  # no prompts, no resources, no sampling
    names = sorted(t["name"] for t in by_id[2]["result"]["tools"])
    assert names == sorted(platform.registry.tools)
    assert len(names) == 6
    for t in by_id[2]["result"]["tools"]:
        assert t["inputSchema"] == platform.registry.tools[t["name"]].input_schema
        assert "[class=" in t["description"]  # read/write class and provenance are visible to the client
    snap = by_id[3]["result"]
    assert snap["isError"] is False and snap["structuredContent"]["provenance"] == "simulated" and snap["structuredContent"]["bid"] is None
    acct = by_id[4]["result"]["structuredContent"]
    assert acct["account_ref"].startswith("acct:") and ACCOUNT not in json.dumps(acct)
    assert by_id[5]["result"] == {}
    assert platform.broker.submissions_received == 0
    assert platform.audit.by_action("mcp.tool.called")


@pytest.mark.tc("TC-AI-013")
@pytest.mark.req("FR-09")
@pytest.mark.quartet("negative")
def test_stdio_server_rejects_malformed_and_unsupported_requests(platform):  # type: ignore[no-untyped-def]
    """Malformed JSON, unknown methods, missing tool names and schema-invalid arguments are answered with errors, never with a handler call."""
    ident = platform.issue_agent()
    calls: list[str] = []

    def call(tool: str, args: dict[str, Any]) -> Any:
        calls.append(tool)
        return platform.tool_call(ident, tool, args)

    server = build_stdio_server(platform.registry, call)
    out = _run(
        server,
        [
            _init(),
            "{not json",
            {"jsonrpc": "2.0", "id": 2, "method": "resources/list"},
            {"jsonrpc": "2.0", "id": 3, "method": "prompts/list"},
            {"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {"arguments": {}}},
            {
                "jsonrpc": "2.0",
                "id": 5,
                "method": "tools/call",
                "params": {"name": "calculate_indicator", "arguments": {"indicator": "sma"}},
            },
            {"jsonrpc": "1.0", "id": 6, "method": "ping"},
            {"jsonrpc": "2.0", "id": 7, "method": "tools/call", "params": {"name": "read_market_snapshot", "arguments": "not-an-object"}},
        ],
    )
    codes = {m.get("id"): m["error"]["code"] for m in out if "error" in m}
    assert codes[None] == -32700  # parse error
    assert codes[2] == -32601 and codes[3] == -32601  # resources and prompts are not capabilities of this server
    assert codes[4] == -32602 and codes[6] == -32600 and codes[7] == -32602
    schema = next(m for m in out if m.get("id") == 5)["result"]
    assert schema["isError"] is True and schema["structuredContent"]["error_code"] == "INPUT_SCHEMA"
    assert calls == ["calculate_indicator"]  # only the well-formed call reached the runtime, which denied it
    assert len(platform.intent_queue) == 0


@pytest.mark.tc("TC-AI-014")
@pytest.mark.req("FR-09")
@pytest.mark.quartet("abuse")
def test_stdio_server_cannot_reach_forbidden_capabilities(platform):  # type: ignore[no-untyped-def]
    """Forbidden tool names are denied with an alert, oversize frames are dropped without parsing, a client-supplied identity is ignored and the transport module has no broker/execution/shell import."""
    ident = platform.issue_agent()
    server = build_stdio_server(platform.registry, lambda tool, args: platform.tool_call(ident, tool, args))
    huge = json.dumps(
        {
            "jsonrpc": "2.0",
            "id": 9,
            "method": "tools/call",
            "params": {"name": "get_strategy_docs", "arguments": {"strategy_id": "x" * (MAX_LINE_BYTES + 10)}},
        }
    )
    out = _run(
        server,
        [
            _init(),
            *(
                {"jsonrpc": "2.0", "id": i, "method": "tools/call", "params": {"name": name, "arguments": {}}}
                for i, name in enumerate(
                    ("cancel_order", "get_broker_credentials", "set_limit", "delete_audit", "shell", "deactivate_kill_switch"), start=2
                )
            ),
            huge,
            {
                "jsonrpc": "2.0",
                "id": 10,
                "method": "tools/call",
                "params": {
                    "name": "read_account_state",
                    "arguments": {"account_id": "acct-other"},
                    "_meta": {"token_id": "tok-forged", "tenant_id": "tenant-other"},
                },
            },
        ],
    )
    by_id = {m.get("id"): m for m in out}
    for i in range(2, 8):
        assert by_id[i]["result"]["isError"] is True and by_id[i]["result"]["structuredContent"]["error_code"] == "TOOL_NOT_REGISTERED"
    assert len(platform.alerts.by_name("mcp.non_allowlisted_tool")) >= 6
    assert by_id[9]["error"]["code"] == -32600 and "frame" in by_id[9]["error"]["message"]
    assert by_id[10]["result"]["structuredContent"]["error_code"] == "SCOPE"  # identity is bound server-side, never client-asserted
    assert platform.broker.submissions_received == 0
    # structural: the transport lives inside mcp_servers, so TC-AI-005's import scan covers it; assert the extra transport-level rule too
    import ast
    from pathlib import Path

    src = Path(__import__("mcp_servers.stdio", fromlist=["__file__"]).__file__).read_text()
    imported = {
        n.names[0].name if isinstance(n, ast.Import) else (n.module or "")
        for n in ast.walk(ast.parse(src))
        if isinstance(n, ast.Import | ast.ImportFrom)
    }
    assert not any(
        m.startswith(("web_bff", "execution_gateway", "broker_adapters", "killswitch_service", "subprocess", "socket")) for m in imported
    )


@pytest.mark.tc("TC-AI-015")
@pytest.mark.req("FR-09")
@pytest.mark.quartet("recovery")
def test_stdio_server_honours_registry_revocation_and_keeps_serving_after_bad_frames(platform):  # type: ignore[no-untyped-def]
    """Registry revocation is honoured on the next frame (every call refused), two-person restore re-enables calls, and a malformed frame never stops the server."""
    ident = platform.issue_agent()
    server = build_stdio_server(platform.registry, lambda tool, args: platform.tool_call(ident, tool, args))
    good = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {"name": "read_market_snapshot", "arguments": {"instrument_id": INSTRUMENT}},
    }
    assert _run(server, [_init(), good])[-1]["result"]["isError"] is False
    platform.runtime.revoke_registry(by="mcp-security-agent", now=platform.now)
    out = _run(server, ["garbage line", {**good, "id": 3}])
    assert out[0]["error"]["code"] == -32700
    assert out[1]["result"]["isError"] is True and out[1]["result"]["structuredContent"]["error_code"] == "REGISTRY_REVOKED"
    platform.runtime.restore_registry(platform.registry, approvers=("chief.risk", "mcp.security"), now=platform.now)
    assert _run(server, [{**good, "id": 4}])[-1]["result"]["isError"] is False
    assert server.frames_served >= 4 and server.frames_rejected >= 1
