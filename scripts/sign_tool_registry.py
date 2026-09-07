#!/usr/bin/env python3
"""Sign mcp/policies/tool_registry.json -> tool_registry.signed.json (MCP Security Agent's job).

Rules (ADR-011, review OBJ-2): a registry with any pending approval_record cannot be signed as an
approved registry; it can only be signed as a sim FIXTURE (--sim-fixture) that the loader refuses
outside dev/sim. The dev key is used only when RT_ENV is explicitly dev or sim.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "libs" / "core"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "mcp" / "servers"))
from mcp_servers.registry import RegistryUnsigned, pending_approvals, sign_registry, signing_key  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
src = ROOT / "mcp" / "policies" / "tool_registry.json"
dst = ROOT / "mcp" / "policies" / "tool_registry.signed.json"
fixture = "--sim-fixture" in sys.argv
content = json.loads(src.read_text())
try:
    key, dev = signing_key()
    signed = sign_registry(
        content,
        key,
        "dev-key-v0" if dev else os.environ.get("RT_MCP_REGISTRY_KEY_ID", "kms-key"),
        signed_at=datetime.now(tz=UTC).isoformat(),
        fixture=fixture,
    )
except RegistryUnsigned as exc:
    print(f"REFUSED: {exc}")
    sys.exit(1)
dst.write_text(json.dumps(signed, indent=2, sort_keys=True) + "\n")
print(
    f"signed {dst.relative_to(ROOT)} with {'DEV KEY (not for production)' if dev else 'configured key'}; fixture={fixture}; pending approvals={pending_approvals(content)}"
)
