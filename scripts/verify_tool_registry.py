#!/usr/bin/env python3
"""Verify the signed tool registry and policy invariants [Source: 04]. Exit 1 on any violation."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "libs" / "core"))
sys.path.insert(0, str(ROOT / "mcp" / "servers"))
import yaml  # noqa: E402
from mcp_servers.registry import RegistryUnsigned, load_registry  # noqa: E402

production = "--production" in sys.argv
problems: list[str] = []
if production:
    import os

    os.environ["RT_ENV"] = os.environ.get("RT_ENV_PRODUCTION_LABEL", "production")
    os.environ.pop("RT_ALLOW_DEV_REGISTRY_KEY", None)
try:
    reg = load_registry(ROOT / "mcp" / "policies" / "tool_registry.signed.json")
except RegistryUnsigned as exc:
    print(f"FAIL: {'dev signing key / fixture registry refused for production: ' if production else ''}{exc}")
    sys.exit(1)
if production and (reg.dev_key_in_use or reg.fixture):
    problems.append(
        "dev signing key or fixture registry in use; production requires the KMS-managed key and approved records (MISSING_ACTIONS)"
    )
if reg.fixture:
    print("NOTE: registry is a sim FIXTURE (approvals pending); it embodies no approval and is refused outside dev/sim")
src = json.loads((ROOT / "mcp" / "policies" / "tool_registry.json").read_text())
signed = json.loads((ROOT / "mcp" / "policies" / "tool_registry.signed.json").read_text())["registry"]
if src != signed:
    problems.append("tool_registry.json differs from the signed copy; re-run scripts/sign_tool_registry.py under MCP Security Agent review")
allowed = {
    "read_market_snapshot",
    "read_account_state",
    "calculate_indicator",
    "run_simulation",
    "get_strategy_docs",
    "submit_trade_intent",
}
names = set(reg.tools)
if names - allowed:
    problems.append(f"tools outside the six allowed capabilities: {sorted(names - allowed)}")
writes = [t for t in reg.tools.values() if t.tool_class == "write"]
if [t.name for t in writes] != ["submit_trade_intent"]:
    problems.append("only submit_trade_intent may be write-class")
if writes and "queue" not in writes[0].scope.lower():
    problems.append("submit_trade_intent scope must state it writes to the intent queue only")
egress = yaml.safe_load((ROOT / "mcp" / "policies" / "egress.yaml").read_text())
for host in egress.get("allowed_hosts", []):
    if any(bad in host for bad in ("vault", "execution", "broker")) or host.strip() in ("*", "0.0.0.0/0"):
        problems.append(f"egress allowlist contains forbidden host: {host}")
runtime = yaml.safe_load((ROOT / "mcp" / "policies" / "runtime.yaml").read_text())
for key, expected in (("filesystem", "read-only"), ("shell", "absent"), ("secrets_mount", "none")):
    if str(runtime.get(key, "")).split()[0] != expected:
        problems.append(f"runtime.yaml {key} must be {expected}")
if not runtime.get("registry_signature_required"):
    problems.append("runtime.yaml must require registry signature")
for spec in reg.tools.values():
    if spec.quota_per_minute <= 0 or spec.timeout_s <= 0 or spec.payload_limit_bytes <= 0:
        problems.append(f"{spec.name}: quota/timeout/payload limit must be positive")
if problems:
    print("FAIL:\n - " + "\n - ".join(problems))
    sys.exit(1)
print(
    f"OK: registry {reg.registry_version} ({'dev key' if reg.dev_key_in_use else 'configured key'}), {len(reg.tools)} tools, policies consistent"
)
