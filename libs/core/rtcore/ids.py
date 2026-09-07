"""Identifiers and canonical hashing.

Deterministic engines never call ``new_id``; they derive identifiers from their inputs with
``deterministic_id`` so identical inputs yield identical records [Source: 05, NFR-DET-01].
"""

from __future__ import annotations

import hashlib
import json
import uuid
from typing import Any

from pydantic import BaseModel


def canonical_json(obj: Any) -> str:
    """Serialise ``obj`` to a canonical JSON string (sorted keys, no whitespace)."""
    if isinstance(obj, BaseModel):
        obj = obj.model_dump(mode="json")
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True, default=str)


def sha256_hex(data: str | bytes) -> str:
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def hash_of(obj: Any) -> str:
    """SHA-256 of the canonical JSON form of ``obj``."""
    return sha256_hex(canonical_json(obj))


def deterministic_id(prefix: str, *parts: Any) -> str:
    """Stable identifier derived only from ``parts``; safe inside pure functions."""
    return f"{prefix}_{sha256_hex('|'.join(str(p) for p in parts))[:32]}"


def new_id(prefix: str) -> str:
    """Random identifier for non-deterministic contexts (API requests, operators)."""
    return f"{prefix}_{uuid.uuid4().hex}"


def new_uuid() -> uuid.UUID:
    return uuid.uuid4()
