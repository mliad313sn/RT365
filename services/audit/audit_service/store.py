from __future__ import annotations

import json
import threading
from collections.abc import Callable, Iterable
from datetime import datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel
from rtcore.clock import utc_now
from rtcore.ids import canonical_json, hash_of, new_id, sha256_hex
from rtcore.schemas.base import StrictModel

GENESIS_HASH = sha256_hex("rt365-audit-genesis")


class AuditEvent(StrictModel):
    seq: int
    event_id: str
    ts: datetime
    correlation_id: str
    tenant: str
    account: str | None
    actor: str
    action: str
    payload_hash: str
    payload: dict[str, Any]
    prev_hash: str
    hash: str

    @staticmethod
    def compute_hash(
        seq: int,
        event_id: str,
        ts: datetime,
        correlation_id: str,
        tenant: str,
        account: str | None,
        actor: str,
        action: str,
        payload_hash: str,
        prev_hash: str,
    ) -> str:
        body = {
            "seq": seq,
            "event_id": event_id,
            "ts": ts.isoformat(),
            "correlation_id": correlation_id,
            "tenant": tenant,
            "account": account,
            "actor": actor,
            "action": action,
            "payload_hash": payload_hash,
            "prev_hash": prev_hash,
        }
        return sha256_hex(canonical_json(body))


class ChainVerification(StrictModel):
    ok: bool
    length: int
    head_hash: str = ""
    first_bad_seq: int | None = None
    detail: str = ""


class ChainHead(StrictModel):
    """Sealed anchor published out of band (WORM object store / replica) so truncation is detectable (review OBJ-3)."""

    length: int
    head_hash: str
    sealed_at: datetime


class AuditStore:
    """Append-only store. Optional JSONL file backend is opened in append mode only (WORM semantics).

    The in-memory list is private; production deployments back this with a WORM object store
    and replicate the chain head (DR_PLAN). [Committee: dev/sim implementation; ADR-010]
    """

    def __init__(self, path: Path | None = None, clock: Callable[[], datetime] = utc_now) -> None:
        self._events: list[AuditEvent] = []
        self._lock = threading.Lock()
        self._path = path
        self._clock = clock
        self._listeners: list[Callable[[AuditEvent], object]] = []
        if path is not None and path.exists():
            for line in path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    self._events.append(AuditEvent.model_validate_json(line))

    # --- write path (append only) -------------------------------------------------------
    def append(
        self,
        *,
        correlation_id: str,
        tenant: str,
        actor: str,
        action: str,
        payload: BaseModel | dict[str, Any],
        account: str | None = None,
        ts: datetime | None = None,
    ) -> AuditEvent:
        body = payload.model_dump(mode="json") if isinstance(payload, BaseModel) else dict(payload)
        with self._lock:
            seq = len(self._events)
            prev_hash = self._events[-1].hash if self._events else GENESIS_HASH
            event_id = new_id("aud")
            when = ts or self._clock()
            if self._events and when < self._events[-1].ts:
                # Backdating is refused: chain time is monotonic; the caller's clock is evidence, not authority.
                when = self._events[-1].ts
            payload_hash = hash_of(body)
            digest = AuditEvent.compute_hash(seq, event_id, when, correlation_id, tenant, account, actor, action, payload_hash, prev_hash)
            event = AuditEvent(
                seq=seq,
                event_id=event_id,
                ts=when,
                correlation_id=correlation_id,
                tenant=tenant,
                account=account,
                actor=actor,
                action=action,
                payload_hash=payload_hash,
                payload=body,
                prev_hash=prev_hash,
                hash=digest,
            )
            self._events.append(event)
            if self._path is not None:
                with self._path.open("a", encoding="utf-8") as fh:
                    fh.write(event.model_dump_json() + "\n")
        for listener in self._listeners:
            listener(event)
        return event

    def subscribe(self, listener: Callable[[AuditEvent], object]) -> None:
        self._listeners.append(listener)

    # --- read path ----------------------------------------------------------------------
    def __len__(self) -> int:
        return len(self._events)

    def all(self) -> tuple[AuditEvent, ...]:
        return tuple(self._events)

    def by_correlation(self, correlation_id: str, *, tenant: str | None = None) -> tuple[AuditEvent, ...]:
        """Rows of one correlation; with ``tenant`` only that tenant's rows (tenant-partitioned reads, NFR-TEN-01)."""
        return tuple(e for e in self._events if e.correlation_id == correlation_id and (tenant is None or e.tenant == tenant))

    def by_action(self, action: str, *, tenant: str | None = None) -> tuple[AuditEvent, ...]:
        return tuple(e for e in self._events if e.action == action and (tenant is None or e.tenant == tenant))

    def for_tenant(self, tenant: str) -> tuple[AuditEvent, ...]:
        return tuple(e for e in self._events if e.tenant == tenant)

    def head_hash(self) -> str:
        return self._events[-1].hash if self._events else GENESIS_HASH

    def seal(self) -> ChainHead:
        """Anchor to publish outside the store (replica, WORM bucket, printed in the gate dossier)."""
        return ChainHead(length=len(self._events), head_hash=self.head_hash(), sealed_at=self._clock())

    def verify(self, events: Iterable[AuditEvent] | None = None, *, anchor: ChainHead | None = None) -> ChainVerification:
        """Verify hashes and sequence; with an ``anchor`` also detect truncation/replacement of the tail."""
        prev = GENESIS_HASH
        seq_expected = 0
        items = list(events) if events is not None else list(self._events)
        if anchor is not None:
            if len(items) < anchor.length:
                return ChainVerification(
                    ok=False,
                    length=len(items),
                    head_hash=items[-1].hash if items else GENESIS_HASH,
                    first_bad_seq=len(items),
                    detail=f"chain truncated: {len(items)} < sealed {anchor.length}",
                )
            if items[anchor.length - 1].hash != anchor.head_hash if anchor.length else GENESIS_HASH != anchor.head_hash:
                return ChainVerification(
                    ok=False,
                    length=len(items),
                    head_hash=items[-1].hash if items else GENESIS_HASH,
                    first_bad_seq=anchor.length - 1,
                    detail="sealed head does not match",
                )
        for e in items:
            if e.seq != seq_expected:
                return ChainVerification(ok=False, length=len(items), first_bad_seq=e.seq, detail="sequence gap")
            if e.prev_hash != prev:
                return ChainVerification(ok=False, length=len(items), first_bad_seq=e.seq, detail="prev_hash mismatch")
            if hash_of(e.payload) != e.payload_hash:
                return ChainVerification(ok=False, length=len(items), first_bad_seq=e.seq, detail="payload tampered")
            recomputed = AuditEvent.compute_hash(
                e.seq, e.event_id, e.ts, e.correlation_id, e.tenant, e.account, e.actor, e.action, e.payload_hash, e.prev_hash
            )
            if recomputed != e.hash:
                return ChainVerification(ok=False, length=len(items), first_bad_seq=e.seq, detail="hash mismatch")
            prev = e.hash
            seq_expected += 1
        return ChainVerification(ok=True, length=len(items), head_hash=prev)

    def export(self, correlation_id: str | None = None, *, tenant: str | None = None) -> str:
        items = self.by_correlation(correlation_id, tenant=tenant) if correlation_id else self.for_tenant(tenant) if tenant else self.all()
        return "\n".join(json.dumps(e.model_dump(mode="json"), sort_keys=True) for e in items)
