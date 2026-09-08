"""Control-plane authorisation of order commands (IVA V-C2, blueprint 03 three-plane topology).

The risk/approval pipeline is the only component holding the authorisation key. It stamps each
``OrderCommand`` with an HMAC over every authorised field; the execution gateway verifies the MAC and
refuses anything else, so a caller that merely reaches the Control plane (or the bus) cannot forge a
command. The key lives in the composition root only: no MCP/AI component, tool or handler is given it.
A shared HMAC (``CommandAuthoriser``/``CommandVerifier``) is the in-process dev/sim mechanism, selected by default by
the composition root. ``Ed25519CommandAuthoriser``/``PublicKeyCommandVerifier`` is the asymmetric path (D-053, ADR-019
proposed): the signer holds the private key, the verifier holds only a public trust set keyed by ``key_id``, and
rotation is overlap-then-retire. The authorisation string on the wire is ``ed25519:<key_id>:<hex signature>``; a bare
hex string is the HMAC form. The production private key is KMS/HSM-held after the ceremony [Open: O-53, H-20].
"""

from __future__ import annotations

import hmac
import secrets
from datetime import datetime
from hashlib import sha256

from rtcore.schemas.order import OrderCommand
from rtcore.signing import Ed25519Signer
from rtcore.trust import ALGORITHM_ED25519, TrustedKey, TrustSet

COMMAND_PURPOSE = "rt365.order-command.v1"  # domain separation: a registry signature can never pass as a command grant
_ALGORITHM_TAG = "ed25519"
_NO_AUTH = "command carries no control-plane authorisation"
_INVALID = "command authorisation invalid"


class CommandAuthoriser:
    def __init__(self, key: bytes) -> None:
        if len(key) < 32:
            raise ValueError("command authorisation key must be at least 32 bytes")
        self._key = key

    @classmethod
    def generate(cls) -> CommandAuthoriser:
        return cls(secrets.token_bytes(32))

    def _mac(self, command: OrderCommand) -> str:
        return hmac.new(self._key, command.authorised_digest().encode(), sha256).hexdigest()

    def sign(self, command: OrderCommand) -> OrderCommand:
        return command.model_copy(update={"authorisation": self._mac(command)})

    def verify(self, command: OrderCommand) -> str | None:
        """Denial reason, or None when the command carries a valid control-plane authorisation."""
        if not command.authorisation:
            return "command carries no control-plane authorisation"
        if not hmac.compare_digest(self._mac(command), command.authorisation):
            return "command authorisation invalid (forged or altered after authorisation)"
        return None

    def verifier(self) -> CommandVerifier:
        """A verify-only handle for the gateway: it cannot sign (IVA-22).

        In-process Python offers no true isolation (the key is still in memory); the deployment
        boundary is a separate gateway process holding only the verification material [Open: O-53].
        """
        return CommandVerifier(self._key)


class CommandVerifier:
    def __init__(self, key: bytes) -> None:
        self._key = key

    def verify(self, command: OrderCommand) -> str | None:
        if not command.authorisation:
            return _NO_AUTH
        expected = hmac.new(self._key, command.authorised_digest().encode(), sha256).hexdigest()
        if not hmac.compare_digest(expected, command.authorisation):
            return f"{_INVALID} (forged or altered after authorisation)"
        return None


class Ed25519CommandAuthoriser:
    """The control-plane signer for the asymmetric path. Lives in the composition root (or the pipeline's signing job)."""

    __slots__ = ("_signer",)

    def __init__(self, signer: Ed25519Signer) -> None:
        self._signer = signer

    @classmethod
    def generate(cls, key_id: str) -> Ed25519CommandAuthoriser:
        return cls(Ed25519Signer.generate(key_id))

    @property
    def key_id(self) -> str:
        return self._signer.key_id

    def __repr__(self) -> str:
        return f"Ed25519CommandAuthoriser(key_id={self.key_id!r})"

    def trusted_key(
        self, *, valid_from: datetime, valid_until: datetime | None = None, ceremony: str = "sim-only: generated in process"
    ) -> TrustedKey:
        return self._signer.trusted_key(valid_from=valid_from, valid_until=valid_until, ceremony=ceremony)

    def sign(self, command: OrderCommand) -> OrderCommand:
        sig = self._signer.sign(COMMAND_PURPOSE, command.authorised_digest().encode())
        return command.model_copy(update={"authorisation": f"{_ALGORITHM_TAG}:{self.key_id}:{sig}"})

    def verifier(self, trust_set: TrustSet | None = None) -> PublicKeyCommandVerifier:
        """A verifier over ``trust_set`` (rotation happens there) or, by default, over this signer's public key alone."""
        return PublicKeyCommandVerifier(trust_set or TrustSet([self.trusted_key(valid_from=datetime.min)], purpose="order-command"))

    def private_seed_for_test_only(self) -> bytes:
        return self._signer.private_seed_for_test_only()


class PublicKeyCommandVerifier:
    """Verify-only handle for the gateway: public keys only, no ``sign``, no private bytes (R-44, IVA-22).

    The validity window is checked at ``authorised_at`` (the gateway bounds it to COMMAND_MAX_AGE around now);
    a retired key is refused whatever the timestamps say.
    """

    __slots__ = ("_trust",)

    def __init__(self, trust_set: TrustSet) -> None:
        self._trust = trust_set

    def __repr__(self) -> str:
        return f"PublicKeyCommandVerifier({self._trust!r})"

    def verify(self, command: OrderCommand) -> str | None:
        if not command.authorisation:
            return _NO_AUTH
        parts = command.authorisation.split(":")
        if len(parts) != 3 or parts[0] != _ALGORITHM_TAG or not parts[1] or not parts[2]:
            return f"{_INVALID} (algorithm not in the verifier's allowlist: expected {_ALGORITHM_TAG}:<key_id>:<signature>)"
        key_id, sig = parts[1], parts[2]
        reason = self._trust.verify(
            key_id=key_id,
            algorithm=ALGORITHM_ED25519,
            purpose=COMMAND_PURPOSE,
            message=command.authorised_digest().encode(),
            signature_hex=sig,
            at=command.authorised_at,
        )
        if reason is not None:
            if "does not verify" in reason or "not hex" in reason:
                return f"{_INVALID} (forged or altered after authorisation)"
            return f"{_INVALID} ({reason})"
        return None
