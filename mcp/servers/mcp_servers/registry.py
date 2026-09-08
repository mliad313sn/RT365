"""Signed tool registry. Unsigned, tampered, wrong-environment or unauthorised registries are refused [Source: 04; C3 §3].

Trust root (ADR-011, review OBJ-2; D-053, ADR-019 proposed): the signature covers a metadata envelope (registry,
key_id, algorithm, environment_tag, registry_version, signed_at, fixture). Two algorithms, checked against an allowlist
before any cryptographic operation:

* ``Ed25519`` — verified with the public-key trust set (``<registry dir>/trust/registry_keys.json`` by default, or the
  ``trust_set`` argument); ``key_id`` must be a trusted, current, non-retired key. Verifiers hold no secret. This is the
  only algorithm accepted outside dev/sim.
* ``HMAC-SHA256`` — the in-process dev/sim mechanism: the documented dev key only when ``RT_ENV`` is explicitly
  ``dev`` or ``sim``, black-listed elsewhere however supplied (IVA-07); a configured ``RT_MCP_REGISTRY_KEY`` is likewise
  accepted in dev/sim only. Any other environment fails closed at load.

This module verifies only: it imports ``rtcore.trust`` (public material) and never ``rtcore.signing`` (TC-AI-005).
"""

from __future__ import annotations

import hmac
import json
import os
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
from typing import Any

import jsonschema
from rtcore.errors import RTError
from rtcore.ids import canonical_json
from rtcore.schemas.base import StrictModel
from rtcore.trust import ALGORITHM_ED25519, TrustSet

DEV_KEY = "dev-only-registry-key-replace-before-gate-B"
KEY_ENV = "RT_MCP_REGISTRY_KEY"
ENV_VAR = "RT_ENV"
DEV_ENVIRONMENTS = frozenset({"dev", "sim"})
ALGORITHM_HMAC = "HMAC-SHA256"
ALGORITHMS = frozenset({ALGORITHM_HMAC, ALGORITHM_ED25519})
REGISTRY_PURPOSE = "rt365.tool-registry.v1"  # domain separation from command authorisation (one key, one purpose)
TRUST_SET_FILENAME = "registry_keys.json"
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
    algorithm: str = ALGORITHM_HMAC

    def get(self, name: str) -> ToolSpec | None:
        return self.tools.get(name)


def current_env() -> str | None:
    return os.environ.get(ENV_VAR)


def signing_key() -> tuple[str, bool]:
    """HMAC key for dev/sim: the configured key, or the dev key only in an explicit dev/sim environment. Anything else fails closed.

    Outside dev/sim no symmetric key is acceptable (D-053): the registry must be Ed25519-signed under the trust set.
    """
    key = os.environ.get(KEY_ENV)
    env = current_env()
    if env not in DEV_ENVIRONMENTS:
        if key == DEV_KEY:
            raise RegistryUnsigned(f"the published dev key is black-listed outside dev/sim ({ENV_VAR}={env!r})")
        raise RegistryUnsigned(
            f"{ALGORITHM_HMAC} is accepted in dev/sim only ({ENV_VAR}={env!r}); the registry must be Ed25519-signed under the trust set"
        )
    if key:
        return (DEV_KEY, True) if key == DEV_KEY else (key, False)
    return DEV_KEY, True


def trust_set_path(registry_path: Path) -> Path:
    return registry_path.parent / "trust" / TRUST_SET_FILENAME


def load_trust_set(registry_path: Path) -> TrustSet:
    """The public trust set shipped next to the registry; absent means empty (nothing asymmetric loads)."""
    path = trust_set_path(registry_path)
    return TrustSet.load(path) if path.exists() else TrustSet(purpose="tool-registry")


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


def envelope_message(envelope: dict[str, Any]) -> bytes:
    """The exact bytes a signer signs and a verifier checks (canonical JSON of the envelope)."""
    return canonical_json(envelope).encode()


def _digest(envelope: dict[str, Any], key: str) -> str:
    return hmac.new(key.encode(), envelope_message(envelope), sha256).hexdigest()


def pending_approvals(content: dict[str, Any]) -> list[str]:
    return [t["name"] for t in content.get("tools", []) if "pending" in str(t.get("approval_record", "")).lower()]


def prepare_envelope(content: dict[str, Any], *, key_id: str, algorithm: str, signed_at: str, fixture: bool = False) -> dict[str, Any]:
    """Validate and build the envelope to sign. A registry with pending approval records may only be signed as a sim fixture (never embodies approval)."""
    if algorithm not in ALGORITHMS:
        raise RegistryUnsigned(f"algorithm {algorithm!r} not in the allowlist {sorted(ALGORITHMS)}")
    jsonschema.validate(content, REGISTRY_SCHEMA)
    if pending_approvals(content) and not fixture:
        raise RegistryUnsigned(f"approval pending for {pending_approvals(content)}; signing would fake approval (blueprint 13)")
    if fixture and content.get("environment_tag") != "sim":
        raise RegistryUnsigned("fixture signatures are only valid for environment_tag=sim")
    return _envelope(content, key_id, algorithm, signed_at, fixture)


def sign_registry(content: dict[str, Any], key: str, key_id: str, *, signed_at: str, fixture: bool = False) -> dict[str, Any]:
    """HMAC (dev/sim) signing. Ed25519 signing lives in scripts/sign_tool_registry.py with ``rtcore.signing``."""
    env = prepare_envelope(content, key_id=key_id, algorithm=ALGORITHM_HMAC, signed_at=signed_at, fixture=fixture)
    return {**env, "signature": _digest(env, key)}


def _verify_hmac(envelope: dict[str, Any], sig: str, key: str | None) -> bool:
    """Returns dev_key_in_use. Refuses the dev key outside dev/sim from any source and any HMAC outside dev/sim."""
    if key is not None:
        dev = key == DEV_KEY
        if current_env() not in DEV_ENVIRONMENTS:
            if dev:
                raise RegistryUnsigned(f"the published dev key is black-listed outside dev/sim ({ENV_VAR}={current_env()!r})")
            raise RegistryUnsigned(f"{ALGORITHM_HMAC} is accepted in dev/sim only ({ENV_VAR}={current_env()!r})")
    else:
        key, dev = signing_key()
    if not hmac.compare_digest(_digest(envelope, key), sig):
        raise RegistryUnsigned("registry signature invalid (tampered, wrong key, or envelope mismatch)")
    return dev


def _verify_ed25519(envelope: dict[str, Any], sig: str, trust: TrustSet, at: datetime) -> None:
    reason = trust.verify(
        key_id=str(envelope["key_id"]),
        algorithm=ALGORITHM_ED25519,
        purpose=REGISTRY_PURPOSE,
        message=envelope_message(envelope),
        signature_hex=sig,
        at=at,
    )
    if reason is not None:
        if "does not verify" in reason or "not hex" in reason:
            raise RegistryUnsigned("registry signature invalid (tampered, wrong key, or envelope mismatch)")
        raise RegistryUnsigned(f"registry key refused: {reason}")


def load_registry(path: Path, key: str | None = None, *, trust_set: TrustSet | None = None, at: datetime | None = None) -> ToolRegistry:
    """Load ``tool_registry.signed.json``; refuse unsigned, tampered, wrong-environment, untrusted-key or unauthorised content."""
    raw = json.loads(path.read_text(encoding="utf-8"))
    content, sig = raw.get("registry"), raw.get("signature")
    if not isinstance(content, dict) or not isinstance(sig, str):
        raise RegistryUnsigned("registry is not signed")
    try:
        jsonschema.validate(content, REGISTRY_SCHEMA)
    except jsonschema.ValidationError as exc:
        raise RegistryUnsigned(f"registry schema violation: {exc.message}") from exc
    algorithm = str(raw.get("algorithm", ""))
    if algorithm not in ALGORITHMS:  # allowlist before any cryptographic operation (R-50)
        raise RegistryUnsigned(f"registry algorithm {algorithm!r} not in the allowlist {sorted(ALGORITHMS)}")
    fixture = bool(raw.get("fixture", False))
    envelope = _envelope(content, str(raw.get("key_id", "")), algorithm, str(raw.get("signed_at", "")), fixture)
    if algorithm == ALGORITHM_ED25519:
        _verify_ed25519(envelope, sig, trust_set if trust_set is not None else load_trust_set(path), at or datetime.now(tz=UTC))
        dev = False
    else:
        dev = _verify_hmac(envelope, sig, key)
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
        algorithm=algorithm,
    )
