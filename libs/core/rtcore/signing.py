"""Ed25519 signing (RFC 8032, standard library only): the signer side of ``rtcore.trust``.

Import this module only in composition roots and signing jobs. Verifiers import ``rtcore.trust`` and never this
module (TC-AI-005 bans it from ``mcp_servers``). The pure-Python private-key operation here is dev/sim material:
the production private key is generated non-exportable in the KMS/HSM and only its public half enters a trust set
(D-053, ceremony H-20) [Open: O-53, O-22, H-20].
"""

from __future__ import annotations

import hashlib
import secrets
from datetime import datetime

from rtcore.trust import _L, ALGORITHM_ED25519, BASE, TrustedKey, _mul, point_compress, sha512_modq, signed_message


def _expand(seed: bytes) -> tuple[int, bytes]:
    if len(seed) != 32:
        raise ValueError("an Ed25519 private seed is 32 bytes")
    h = hashlib.sha512(seed).digest()
    a = int.from_bytes(h[:32], "little")
    a &= (1 << 254) - 8
    a |= 1 << 254
    return a, h[32:]


def ed25519_public_key(seed: bytes) -> bytes:
    a, _ = _expand(seed)
    return point_compress(_mul(a, BASE))


def ed25519_sign(seed: bytes, message: bytes) -> bytes:
    a, prefix = _expand(seed)
    public = point_compress(_mul(a, BASE))
    r = sha512_modq(prefix + message)
    r_enc = point_compress(_mul(r, BASE))
    k = sha512_modq(r_enc + public + message)
    s = (r + k * a) % _L
    return r_enc + int.to_bytes(s, 32, "little")


class Ed25519Signer:
    """Holds one private seed for one ``key_id``. Never logged, never serialised; ``repr`` shows the key_id only."""

    __slots__ = ("_seed", "key_id", "public_key")

    def __init__(self, key_id: str, seed: bytes) -> None:
        if not key_id:
            raise ValueError("key_id required")
        self.key_id = key_id
        self._seed = bytes(seed)
        self.public_key = ed25519_public_key(self._seed)

    @classmethod
    def generate(cls, key_id: str) -> Ed25519Signer:
        return cls(key_id, secrets.token_bytes(32))

    @classmethod
    def from_file(cls, key_id: str, path: str) -> Ed25519Signer:
        """Read a 32-byte seed (raw or 64 hex characters) from a file that is never committed."""
        raw = open(path, "rb").read().strip()  # noqa: SIM115
        seed = bytes.fromhex(raw.decode("ascii")) if len(raw) == 64 else raw
        return cls(key_id, seed)

    def __repr__(self) -> str:
        return f"Ed25519Signer(key_id={self.key_id!r}, public_key={self.public_key.hex()[:16]}...)"

    def trusted_key(
        self, *, valid_from: datetime, valid_until: datetime | None = None, ceremony: str = "sim-only: generated in process"
    ) -> TrustedKey:
        return TrustedKey(
            key_id=self.key_id,
            algorithm=ALGORITHM_ED25519,
            public_key=self.public_key.hex(),
            valid_from=valid_from,
            valid_until=valid_until,
            ceremony=ceremony,
        )

    def sign(self, purpose: str, message: bytes) -> str:
        """Hex signature over the domain-separated (purpose, key_id, message) bytes that ``TrustSet.verify`` checks."""
        return ed25519_sign(self._seed, signed_message(purpose, self.key_id, message)).hex()

    def private_seed_for_test_only(self) -> bytes:
        """Used by the SIG quartet to prove the seed is unreachable from verifiers; never call it from product code."""
        return self._seed
