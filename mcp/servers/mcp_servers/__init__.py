"""MCP servers and sandbox runtime [Source: 04; C3].

Structural rules enforced by tests (TC-AI-*, TC-NET-*): this package never imports the
execution gateway, broker adapters, the vault or the Kill Switch; its only write path is
``submit_trade_intent`` -> Control-plane intent queue.
"""

from mcp_servers.identity import AgentIdentity, IdentityIssuer
from mcp_servers.registry import RegistryUnsigned, ToolRegistry, ToolSpec, load_registry, sign_registry
from mcp_servers.runtime import ToolDenied, ToolResult, ToolRuntime

__all__ = [
    "AgentIdentity",
    "IdentityIssuer",
    "ToolRegistry",
    "ToolSpec",
    "RegistryUnsigned",
    "load_registry",
    "sign_registry",
    "ToolRuntime",
    "ToolResult",
    "ToolDenied",
]
