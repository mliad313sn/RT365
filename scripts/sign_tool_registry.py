#!/usr/bin/env python3
"""Sign mcp/policies/tool_registry.json -> tool_registry.signed.json.

Uses RT_MCP_REGISTRY_KEY when set; otherwise the documented dev key (refused for production by
verify_tool_registry.py when --production is passed). Only the MCP Security Agent runs this in CI.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "libs" / "core"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "mcp" / "servers"))
from mcp_servers.registry import sign_registry, signing_key  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
src = ROOT / "mcp" / "policies" / "tool_registry.json"
dst = ROOT / "mcp" / "policies" / "tool_registry.signed.json"
key, dev = signing_key()
signed = sign_registry(json.loads(src.read_text()), key, "dev-key-v0" if dev else "kms-key")
dst.write_text(json.dumps(signed, indent=2, sort_keys=True) + "\n")
print(f"signed {dst.relative_to(ROOT)} with {'DEV KEY (not for production)' if dev else 'configured key'}")
