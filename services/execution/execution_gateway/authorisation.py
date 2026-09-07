"""Control-plane authorisation of order commands (IVA V-C2, blueprint 03 three-plane topology).

The risk/approval pipeline is the only component holding the authorisation key. It stamps each
``OrderCommand`` with an HMAC over every authorised field; the execution gateway verifies the MAC and
refuses anything else, so a caller that merely reaches the Control plane (or the bus) cannot forge a
command. The key lives in the composition root only: no MCP/AI component, tool or handler is given it.
A shared HMAC is the dev/sim mechanism; an asymmetric signature with HSM-held private key is the
Gate C target [Open: O-53].
"""

from __future__ import annotations

import hmac
import secrets
from hashlib import sha256

from rtcore.schemas.order import OrderCommand


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
            return "command carries no control-plane authorisation"
        expected = hmac.new(self._key, command.authorised_digest().encode(), sha256).hexdigest()
        if not hmac.compare_digest(expected, command.authorisation):
            return "command authorisation invalid (forged or altered after authorisation)"
        return None
