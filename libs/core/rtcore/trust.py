"""Verify-only trust material: Ed25519 verification (RFC 8032, standard library only) and the public-key trust set.

This module holds no private key and no signing capability; it is what verifiers (execution gateway, MCP registry
loader, CLI, installers) import [Committee: D-053 §2.3 items 1, 4, 5; ADR-019 proposed]. Signing lives in
``rtcore.signing`` and is imported only by composition roots and signing jobs.

Why a pure-Python Ed25519: ``cryptography`` is not in the declared dependency closure (pyproject.toml,
requirements.lock.txt) and the build rule is not to add one; RFC 8032 is short and its test vectors are public.
Verification uses public inputs only, so constant-time behaviour is not required here; the pure-Python signer in
``rtcore.signing`` is dev/sim material (the production private key is KMS/HSM-held, H-20) [Open: O-53, H-20].
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from rtcore.errors import RTError

ALGORITHM_ED25519 = "Ed25519"
ALGORITHMS = frozenset({ALGORITHM_ED25519})  # asymmetric allowlist checked before any curve operation

# --- curve arithmetic (RFC 8032 §5.1; extended twisted Edwards coordinates, a = -1) ---------------------------------
_P = 2**255 - 19
_L = 2**252 + 27742317777372353535851937790883648493
_D = (-121665 * pow(121666, _P - 2, _P)) % _P
_SQRT_M1 = pow(2, (_P - 1) // 4, _P)
_Point = tuple[int, int, int, int]  # (X, Y, Z, T) with x = X/Z, y = Y/Z, x*y = T/Z


def _add(p: _Point, q: _Point) -> _Point:
    x1, y1, z1, t1 = p
    x2, y2, z2, t2 = q
    a = (y1 - x1) * (y2 - x2) % _P
    b = (y1 + x1) * (y2 + x2) % _P
    c = 2 * t1 * t2 * _D % _P
    d = 2 * z1 * z2 % _P
    e, f, g, h = b - a, d - c, d + c, b + a
    return e * f % _P, g * h % _P, f * g % _P, e * h % _P


def _mul(s: int, p: _Point) -> _Point:
    q: _Point = (0, 1, 1, 0)
    while s > 0:
        if s & 1:
            q = _add(q, p)
        p = _add(p, p)
        s >>= 1
    return q


def _equal(p: _Point, q: _Point) -> bool:
    x1, y1, z1, _ = p
    x2, y2, z2, _ = q
    return (x1 * z2 - x2 * z1) % _P == 0 and (y1 * z2 - y2 * z1) % _P == 0


def _recover_x(y: int, sign: int) -> int | None:
    if y >= _P:
        return None
    x2 = (y * y - 1) * pow(_D * y * y + 1, _P - 2, _P) % _P
    if x2 == 0:
        return None if sign else 0
    x = pow(x2, (_P + 3) // 8, _P)
    if (x * x - x2) % _P != 0:
        x = x * _SQRT_M1 % _P
    if (x * x - x2) % _P != 0:
        return None
    if (x & 1) != sign:
        x = _P - x
    return x


_BY = 4 * pow(5, _P - 2, _P) % _P
_BX = _recover_x(_BY, 0)
assert _BX is not None
BASE: _Point = (_BX, _BY, 1, _BX * _BY % _P)


def point_compress(p: _Point) -> bytes:
    x, y, z, _ = p
    zinv = pow(z, _P - 2, _P)
    x, y = x * zinv % _P, y * zinv % _P
    return int.to_bytes(y | ((x & 1) << 255), 32, "little")


def point_decompress(s: bytes) -> _Point | None:
    if len(s) != 32:
        return None
    y = int.from_bytes(s, "little")
    sign = y >> 255
    y &= (1 << 255) - 1
    x = _recover_x(y, sign)
    if x is None:
        return None
    return x, y, 1, x * y % _P


def sha512_modq(data: bytes) -> int:
    return int.from_bytes(hashlib.sha512(data).digest(), "little") % _L


def ed25519_verify(public_key: bytes, message: bytes, signature: bytes) -> bool:
    """RFC 8032 §5.1.7 verification. Any malformed input verifies nothing (False)."""
    if len(public_key) != 32 or len(signature) != 64:
        return False
    a = point_decompress(public_key)
    r = point_decompress(signature[:32])
    if a is None or r is None:
        return False
    s = int.from_bytes(signature[32:], "little")
    if s >= _L:
        return False
    k = sha512_modq(signature[:32] + public_key + message)
    return _equal(_mul(s, BASE), _add(r, _mul(k, a)))


def signed_message(purpose: str, key_id: str, message: bytes) -> bytes:
    """Domain-separated bytes every signer signs and every verifier checks: purpose, key_id and payload are all bound."""
    if not purpose or "\n" in purpose or not key_id or "\n" in key_id:
        raise ValueError("purpose and key_id must be non-empty single-line strings")
    return purpose.encode() + b"\n" + key_id.encode() + b"\n" + message


# --- trust set -------------------------------------------------------------------------------------------------------
class UntrustedKey(RTError):
    """key_id unknown, algorithm not allowed, key outside its validity window, or retired (revoked)."""


def _ts(value: str | datetime | None) -> datetime | None:
    if value is None:
        return None
    dt = datetime.fromisoformat(value) if isinstance(value, str) else value
    return dt if dt.tzinfo is not None else dt.replace(tzinfo=UTC)


@dataclass(frozen=True)
class TrustedKey:
    """One public key of the trust set. ``public_key`` is hex; nothing private ever enters this type."""

    key_id: str
    public_key: str
    valid_from: datetime
    algorithm: str = ALGORITHM_ED25519
    valid_until: datetime | None = None
    revoked: bool = False
    ceremony: str = ""  # security/signing/ceremonies/<key_id>.md (H-20) or "sim-only: generated in process"

    def __post_init__(self) -> None:
        if self.algorithm not in ALGORITHMS:
            raise UntrustedKey(f"algorithm {self.algorithm!r} not in the allowlist {sorted(ALGORITHMS)}")
        if len(bytes.fromhex(self.public_key)) != 32:
            raise UntrustedKey(f"public key of {self.key_id!r} is not 32 bytes")
        object.__setattr__(self, "valid_from", _ts(self.valid_from))
        object.__setattr__(self, "valid_until", _ts(self.valid_until))

    def to_dict(self) -> dict[str, Any]:
        return {
            "key_id": self.key_id,
            "algorithm": self.algorithm,
            "public_key": self.public_key,
            "valid_from": self.valid_from.isoformat(),
            "valid_until": self.valid_until.isoformat() if self.valid_until else None,
            "revoked": self.revoked,
            "ceremony": self.ceremony,
        }


class TrustSet:
    """Public keys keyed by ``key_id``; rotation is add (overlap) then ``retire`` (absolute refusal) [Committee: D-053]."""

    def __init__(self, keys: Any = (), *, purpose: str = "") -> None:
        self.purpose = purpose
        self._keys: dict[str, TrustedKey] = {}
        for k in keys:
            self.add(k)

    def __len__(self) -> int:
        return len(self._keys)

    def __repr__(self) -> str:
        return f"TrustSet(purpose={self.purpose!r}, keys={sorted(self._keys)})"

    @property
    def key_ids(self) -> tuple[str, ...]:
        return tuple(sorted(self._keys))

    def get(self, key_id: str) -> TrustedKey | None:
        return self._keys.get(key_id)

    def add(self, key: TrustedKey) -> None:
        if key.key_id in self._keys:
            raise UntrustedKey(f"key_id {key.key_id!r} already in the trust set; rotation adds a new key_id")
        self._keys[key.key_id] = key

    def retire(self, key_id: str, *, at: datetime) -> TrustedKey:
        """Retire (revoke) a key: from now on it verifies nothing, whatever the timestamps say."""
        key = self._keys.get(key_id)
        if key is None:
            raise UntrustedKey(f"unknown key_id {key_id!r}")
        retired = replace(key, revoked=True, valid_until=min(filter(None, (key.valid_until, _ts(at)))))
        self._keys[key_id] = retired
        return retired

    def resolve(self, key_id: str, *, algorithm: str, at: datetime) -> TrustedKey:
        if algorithm not in ALGORITHMS:
            raise UntrustedKey(f"algorithm {algorithm!r} not in the allowlist {sorted(ALGORITHMS)}")
        key = self._keys.get(key_id)
        if key is None:
            raise UntrustedKey(f"unknown key_id {key_id!r} for {self.purpose or 'this'} trust set")
        if key.revoked:
            raise UntrustedKey(f"key_id {key_id!r} is retired (revoked)")
        if key.algorithm != algorithm:
            raise UntrustedKey(f"key_id {key_id!r} is a {key.algorithm} key, not {algorithm}")
        when = _ts(at)
        assert when is not None
        if when < key.valid_from:
            raise UntrustedKey(f"key_id {key_id!r} not yet valid at {when.isoformat()} (valid_from {key.valid_from.isoformat()})")
        if key.valid_until is not None and when > key.valid_until:
            raise UntrustedKey(f"key_id {key_id!r} expired at {key.valid_until.isoformat()}")
        return key

    def verify(self, *, key_id: str, algorithm: str, purpose: str, message: bytes, signature_hex: str, at: datetime) -> str | None:
        """Denial reason, or None when ``signature_hex`` is a valid signature by a trusted, current key."""
        try:
            key = self.resolve(key_id, algorithm=algorithm, at=at)
        except UntrustedKey as exc:
            return str(exc)
        try:
            sig = bytes.fromhex(signature_hex)
        except ValueError:
            return "signature is not hex"
        if not ed25519_verify(bytes.fromhex(key.public_key), signed_message(purpose, key_id, message), sig):
            return "signature does not verify under the trusted public key"
        return None

    def to_dict(self) -> dict[str, Any]:
        return {"purpose": self.purpose, "keys": [k.to_dict() for k in self._keys.values()]}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TrustSet:
        keys = [TrustedKey(**{k: v for k, v in entry.items() if k in TrustedKey.__dataclass_fields__}) for entry in data.get("keys", [])]
        return cls(keys, purpose=str(data.get("purpose", "")))

    @classmethod
    def load(cls, path: Path) -> TrustSet:
        return cls.from_dict(json.loads(path.read_text(encoding="utf-8")))

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
