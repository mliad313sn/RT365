"""Signed tool registry. Unsigned or tampered registries are refused at load [Source: 04; C3 §3]."""

from __future__ import annotations

import hmac
import json
import os
from hashlib import sha256
from pathlib import Path
from typing import Any

from rtcore.errors import RTError
from rtcore.ids import canonical_json
from rtcore.schemas.base import StrictModel

DEV_KEY = "dev-only-registry-key-replace-before-gate-B"
KEY_ENV = "RT_MCP_REGISTRY_KEY"


class RegistryUnsigned(RTError):
    """Signature missing or invalid; every MCP server refuses to serve."""


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
    input_schema: dict[str, Any]
    output_schema: dict[str, Any]


class ToolRegistry(StrictModel):
    registry_version: str
    environment_tag: str
    canary_tokens: tuple[str, ...]
    tools: dict[str, ToolSpec]
    signature: str
    key_id: str
    dev_key_in_use: bool

    def get(self, name: str) -> ToolSpec | None:
        return self.tools.get(name)


def signing_key() -> tuple[str, bool]:
    key = os.environ.get(KEY_ENV)
    if key:
        return key, False
    return DEV_KEY, True


def _digest(content: dict[str, Any], key: str) -> str:
    return hmac.new(key.encode(), canonical_json(content).encode(), sha256).hexdigest()


def sign_registry(content: dict[str, Any], key: str, key_id: str) -> dict[str, Any]:
    return {"registry": content, "signature": _digest(content, key), "key_id": key_id, "algorithm": "HMAC-SHA256"}


def load_registry(path: Path, key: str | None = None) -> ToolRegistry:
    """Load ``tool_registry.signed.json``; refuse unsigned or tampered content."""
    raw = json.loads(path.read_text(encoding="utf-8"))
    content, sig = raw.get("registry"), raw.get("signature")
    if not isinstance(content, dict) or not isinstance(sig, str):
        raise RegistryUnsigned("registry is not signed")
    k, dev = (key, key == DEV_KEY) if key is not None else signing_key()
    if not hmac.compare_digest(_digest(content, k), sig):
        raise RegistryUnsigned("registry signature invalid (tampered or wrong key)")
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
            input_schema=t["input_schema"],
            output_schema=t["output_schema"],
        )
        for t in content["tools"]
    }
    return ToolRegistry(
        registry_version=content["registry_version"],
        environment_tag=content["environment_tag"],
        canary_tokens=tuple(content.get("canary_tokens", ())),
        tools=tools,
        signature=sig,
        key_id=str(raw.get("key_id", "")),
        dev_key_in_use=dev,
    )
