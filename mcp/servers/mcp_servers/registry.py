"""Signed tool registry. Unsigned, tampered, wrong-environment or unauthorised registries are refused [Source: 04; C3 §3].

Trust root (ADR-011, review OBJ-2): the signature covers a metadata envelope (registry, key_id,
algorithm, environment_tag, registry_version, signed_at, fixture flag). The documented dev key is
accepted only when ``RT_ENV`` is explicitly ``dev`` or ``sim``; any other environment with no
``RT_MCP_REGISTRY_KEY`` fails closed at load. Asymmetric signing is the Gate B target [Open: O-22].
"""

from __future__ import annotations

import hmac
import json
import os
from hashlib import sha256
from pathlib import Path
from typing import Any

import jsonschema
from rtcore.errors import RTError
from rtcore.ids import canonical_json
from rtcore.schemas.base import StrictModel

DEV_KEY = "dev-only-registry-key-replace-before-gate-B"
KEY_ENV = "RT_MCP_REGISTRY_KEY"
ENV_VAR = "RT_ENV"
DEV_ENVIRONMENTS = frozenset({"dev", "sim"})
ALLOWED_TOOLS = frozenset(
    {"read_market_snapshot", "read_account_state", "calculate_indicator", "run_simulation", "get_strategy_docs", "submit_trade_intent"}
)

REGISTRY_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["registry_version", "environment_tag", "tools"],
    "properties": {
        "registry_version": {"type": "string"},
        "environment_tag": {"type": "string", "enum": ["dev", "sim", "shadow", "paper", "pilot", "production"]},
        "note": {"type": "string"},
        "canary_tokens": {"type": "array", "items": {"type": "string"}},
        "tools": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "name",
                    "class",
                    "server",
                    "scope",
                    "masking",
                    "quota_per_minute",
                    "timeout_s",
                    "payload_limit_bytes",
                    "owner",
                    "approval_record",
                    "input_schema",
                    "output_schema",
                    "output_provenance",
                ],
                "properties": {
                    "name": {"type": "string", "enum": sorted(ALLOWED_TOOLS)},
                    "class": {"type": "string", "enum": ["read", "write"]},
                    "server": {"type": "string"},
                    "scope": {"type": "string"},
                    "masking": {"type": "string"},
                    "quota_per_minute": {"type": "integer", "minimum": 1},
                    "timeout_s": {"type": "integer", "minimum": 1},
                    "payload_limit_bytes": {"type": "integer", "minimum": 1},
                    "owner": {"type": "string"},
                    "approval_record": {"type": "string"},
                    "input_schema": {"type": "object"},
                    "output_schema": {"type": "object"},
                    "output_provenance": {
                        "type": "string",
                        "enum": ["licensed_feed", "news_adapter", "user_text", "internal_doc", "simulated", "internal"],
                    },
                },
            },
        },
    },
}


class RegistryUnsigned(RTError):
    """Signature missing/invalid, wrong key, wrong environment or fixture outside sim; every MCP server refuses to serve."""


class ToolSpec(StrictModel):
    name: str
    tool_class: str  # read | write
    server: str
    scope: str
    masking: str
    quota_per_minute: int
    timeout_s: int
    payload_limit_bytes: int
    owner: str
    approval_record: str
    output_provenance: str
    input_schema: dict[str, Any]
    output_schema: dict[str, Any]


class ToolRegistry(StrictModel):
    registry_version: str
    environment_tag: str
    canary_tokens: tuple[str, ...]
    tools: dict[str, ToolSpec]
    signature: str
    key_id: str
    signed_at: str
    fixture: bool
    dev_key_in_use: bool

    def get(self, name: str) -> ToolSpec | None:
        return self.tools.get(name)


def current_env() -> str | None:
    return os.environ.get(ENV_VAR)


def signing_key() -> tuple[str, bool]:
    """Configured key, or the dev key only in an explicit dev/sim environment. Anything else fails closed."""
    key = os.environ.get(KEY_ENV)
    if key:
        return key, False
    env = current_env()
    if env in DEV_ENVIRONMENTS:
        return DEV_KEY, True
    raise RegistryUnsigned(f"no {KEY_ENV} configured and {ENV_VAR}={env!r} is not a dev/sim environment; refusing the dev key")


def _envelope(content: dict[str, Any], key_id: str, algorithm: str, signed_at: str, fixture: bool) -> dict[str, Any]:
    return {
        "registry": content,
        "key_id": key_id,
        "algorithm": algorithm,
        "environment_tag": content.get("environment_tag"),
        "registry_version": content.get("registry_version"),
        "signed_at": signed_at,
        "fixture": fixture,
    }


def _digest(envelope: dict[str, Any], key: str) -> str:
    return hmac.new(key.encode(), canonical_json(envelope).encode(), sha256).hexdigest()


def pending_approvals(content: dict[str, Any]) -> list[str]:
    return [t["name"] for t in content.get("tools", []) if "pending" in str(t.get("approval_record", "")).lower()]


def sign_registry(content: dict[str, Any], key: str, key_id: str, *, signed_at: str, fixture: bool = False) -> dict[str, Any]:
    """Sign. A registry with pending approval records may only be signed as a sim fixture (never embodies approval)."""
    jsonschema.validate(content, REGISTRY_SCHEMA)
    if pending_approvals(content) and not fixture:
        raise RegistryUnsigned(f"approval pending for {pending_approvals(content)}; signing would fake approval (blueprint 13)")
    if fixture and content.get("environment_tag") != "sim":
        raise RegistryUnsigned("fixture signatures are only valid for environment_tag=sim")
    env = _envelope(content, key_id, "HMAC-SHA256", signed_at, fixture)
    return {**env, "signature": _digest(env, key)}


def load_registry(path: Path, key: str | None = None) -> ToolRegistry:
    """Load ``tool_registry.signed.json``; refuse unsigned, tampered, wrong-environment or unauthorised content."""
    raw = json.loads(path.read_text(encoding="utf-8"))
    content, sig = raw.get("registry"), raw.get("signature")
    if not isinstance(content, dict) or not isinstance(sig, str):
        raise RegistryUnsigned("registry is not signed")
    try:
        jsonschema.validate(content, REGISTRY_SCHEMA)
    except jsonschema.ValidationError as exc:
        raise RegistryUnsigned(f"registry schema violation: {exc.message}") from exc
    if key is not None:
        k, dev = key, key == DEV_KEY
    else:
        k, dev = signing_key()
    fixture = bool(raw.get("fixture", False))
    envelope = _envelope(content, str(raw.get("key_id", "")), str(raw.get("algorithm", "")), str(raw.get("signed_at", "")), fixture)
    if not hmac.compare_digest(_digest(envelope, k), sig):
        raise RegistryUnsigned("registry signature invalid (tampered, wrong key, or envelope mismatch)")
    env = current_env()
    tag = str(content["environment_tag"])
    if env is not None and tag != env and not (env == "dev" and tag == "sim"):
        raise RegistryUnsigned(f"registry environment_tag={tag} does not match {ENV_VAR}={env}")
    if fixture and (env not in DEV_ENVIRONMENTS):
        raise RegistryUnsigned("fixture-signed registry (approvals pending) refused outside dev/sim")
    if not fixture and pending_approvals(content):
        raise RegistryUnsigned("registry carries pending approvals but is not marked as a sim fixture")
    tools = {
        t["name"]: ToolSpec(
            name=t["name"],
            tool_class=t["class"],
            server=t["server"],
            scope=t["scope"],
            masking=t["masking"],
            quota_per_minute=int(t["quota_per_minute"]),
            timeout_s=int(t["timeout_s"]),
            payload_limit_bytes=int(t["payload_limit_bytes"]),
            owner=t["owner"],
            approval_record=t["approval_record"],
            output_provenance=t["output_provenance"],
            input_schema=t["input_schema"],
            output_schema=t["output_schema"],
        )
        for t in content["tools"]
    }
    return ToolRegistry(
        registry_version=content["registry_version"],
        environment_tag=tag,
        canary_tokens=tuple(content.get("canary_tokens", ())),
        tools=tools,
        signature=sig,
        key_id=str(raw.get("key_id", "")),
        signed_at=str(raw.get("signed_at", "")),
        fixture=fixture,
        dev_key_in_use=dev,
    )
