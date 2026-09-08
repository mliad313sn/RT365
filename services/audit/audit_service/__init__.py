"""Immutable, hash-chained audit store [Source: 03, 06; NFR-AUD-01].

There is no update or delete API. Tampering with stored bytes is detected by ``verify``. A store whose own records
name an external witness that is now absent does not open (``WitnessLostError``), and no seal witnesses a chain
that contradicts what this store already recorded witnessing (``SealRefused``) — ADR-020 amendment 3.
"""

from audit_service.store import (
    AuditEvent,
    AuditStore,
    ChainHead,
    ChainVerification,
    SealRefused,
    WitnessAttestation,
    WitnessLostError,
)

__all__ = [
    "AuditEvent",
    "AuditStore",
    "ChainHead",
    "ChainVerification",
    "SealRefused",
    "WitnessAttestation",
    "WitnessLostError",
]
