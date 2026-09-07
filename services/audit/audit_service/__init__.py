"""Immutable, hash-chained audit store [Source: 03, 06; NFR-AUD-01].

There is no update or delete API. Tampering with stored bytes is detected by ``verify``.
"""

from audit_service.store import AuditEvent, AuditStore, ChainHead, ChainVerification

__all__ = ["AuditEvent", "AuditStore", "ChainHead", "ChainVerification"]
