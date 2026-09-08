"""External anchoring of the audit chain head [Source: 03, 06; NFR-AUD-01; Committee: REVIEW_C5 OBJ-3, D-024; Open: O-54, R-31].

A sealed ``ChainHead`` (length, head hash, time) is published to a store the audit process cannot rewrite: in
deployment a WORM bucket or replica written by a *different principal* (the anchor publisher's identity, not the
audit service's). Truncating or replacing the audit tail then needs write access to both principals' stores.

``AnchorPublisher`` is the seam. ``FileAnchorPublisher`` is the dev/sim implementation: one append-only JSONL file
under ``anchor_dir`` whose records form their own hash chain, so an edited or removed anchor record is detected
when the chain is read. The publisher receives only a ``ChainHead`` (or an ``AnchorHandle``): it can read a sealed
head and nothing else. Neither holds a reference through which an audit event could be written or deleted.

The anchor is a monotonic witness: a record shorter than the latest, or a fork at the same length with a different
head hash, is refused. Nothing here holds a secret; the anchor chain is tamper-evident because it is *elsewhere*,
not because it is keyed [Open: O-110 keyed integrity before shadow].
"""

from __future__ import annotations

import threading
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Protocol

from pydantic import ValidationError
from rtcore.clock import utc_now
from rtcore.errors import RTError
from rtcore.ids import canonical_json, sha256_hex
from rtcore.schemas.base import StrictModel

ANCHOR_FILENAME = "audit_anchors.jsonl"
GENESIS_ANCHOR_HASH = sha256_hex("rt365-audit-anchor-genesis")
DEFAULT_PRINCIPAL = "audit-anchor-publisher"  # the separate deployment identity that owns the WORM/replica [Open: O-54]


class AnchorError(RTError):
    """The anchor store could not be read or written, or refused a publication; callers fail closed."""


class AnchorIntegrityError(AnchorError):
    """The anchor chain does not verify (edited, removed or inserted record)."""


class ChainHead(StrictModel):
    """Sealed anchor published out of band (WORM object store / replica) so truncation is detectable (review OBJ-3)."""

    length: int
    head_hash: str
    sealed_at: datetime


class AnchorRecord(StrictModel):
    """One published anchor: the sealed head plus the publisher's own hash chain and provenance."""

    anchor_seq: int
    length: int
    head_hash: str
    sealed_at: datetime
    published_at: datetime
    principal: str
    correlation_id: str
    prev_hash: str
    hash: str

    @staticmethod
    def compute_hash(
        anchor_seq: int,
        length: int,
        head_hash: str,
        sealed_at: datetime,
        published_at: datetime,
        principal: str,
        correlation_id: str,
        prev_hash: str,
    ) -> str:
        return sha256_hex(
            canonical_json(
                {
                    "anchor_seq": anchor_seq,
                    "length": length,
                    "head_hash": head_hash,
                    "sealed_at": sealed_at.isoformat(),
                    "published_at": published_at.isoformat(),
                    "principal": principal,
                    "correlation_id": correlation_id,
                    "prev_hash": prev_hash,
                }
            )
        )

    @property
    def head(self) -> ChainHead:
        return ChainHead(length=self.length, head_hash=self.head_hash, sealed_at=self.sealed_at)


class AnchorVerification(StrictModel):
    ok: bool
    count: int
    detail: str = ""


class AnchorHandle:
    """Anchor-only view of an audit store: the current sealed head and the chain length, nothing else.

    Built from a callable so that no attribute of the handle references the store or any object with a write path.
    Python has no capability isolation; the handle is the *interface* a separate publisher principal is given, and the
    process/identity boundary in deployment is what enforces it [Open: O-54].
    """

    def __init__(self, head: Callable[[], ChainHead]) -> None:
        self._head_fn = head

    def head(self) -> ChainHead:
        return self._head_fn()

    @property
    def length(self) -> int:
        return self._head_fn().length


class AnchorPublisher(Protocol):
    """Writes sealed heads to the external store and reads them back. Receives heads, never events."""

    @property
    def principal(self) -> str: ...

    def publish(self, head: ChainHead, *, correlation_id: str) -> AnchorRecord: ...

    def latest(self) -> AnchorRecord | None: ...

    def records(self) -> tuple[AnchorRecord, ...]: ...

    def verify(self) -> AnchorVerification: ...


class FileAnchorPublisher:
    """Append-only JSONL anchor file under ``anchor_dir`` with its own hash chain (dev/sim stand-in for the WORM/replica).

    The file is opened for append only; every read re-verifies the whole chain and any defect raises
    ``AnchorIntegrityError`` (fail closed). Publication is refused while the chain is broken, so a corrupt replica
    can never be "healed" by writing on top of it: it is restored from the last good copy (TC-AUD-009).
    """

    def __init__(self, anchor_dir: Path, *, principal: str = DEFAULT_PRINCIPAL, clock: Callable[[], datetime] = utc_now) -> None:
        self._dir = Path(anchor_dir)
        self._file = self._dir / ANCHOR_FILENAME
        self._principal = principal
        self._clock = clock
        self._lock = threading.RLock()
        try:
            self._dir.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            raise AnchorError(f"cannot open anchor directory {self._dir}: {type(exc).__name__}") from exc

    @property
    def principal(self) -> str:
        return self._principal

    @property
    def path(self) -> Path:
        return self._file

    # --- read path --------------------------------------------------------------------------------------------
    def _read(self) -> tuple[AnchorRecord, ...]:
        """Every record, chain-checked; raises AnchorIntegrityError on the first defect."""
        if not self._file.exists():
            return ()
        try:
            lines = self._file.read_text(encoding="utf-8").splitlines()
        except OSError as exc:
            raise AnchorError(f"cannot read anchor file: {type(exc).__name__}") from exc
        out: list[AnchorRecord] = []
        prev = GENESIS_ANCHOR_HASH
        for n, line in enumerate((ln for ln in lines if ln.strip()), start=1):
            try:
                rec = AnchorRecord.model_validate_json(line)
            except ValidationError as exc:
                raise AnchorIntegrityError(f"anchor record {n} unreadable (fail closed)") from exc
            recomputed = AnchorRecord.compute_hash(
                rec.anchor_seq, rec.length, rec.head_hash, rec.sealed_at, rec.published_at, rec.principal, rec.correlation_id, rec.prev_hash
            )
            if rec.anchor_seq != n or rec.prev_hash != prev or recomputed != rec.hash:
                raise AnchorIntegrityError(f"anchor chain broken at record {n} (fail closed)")
            if out and rec.length < out[-1].length:
                raise AnchorIntegrityError(f"anchor chain not monotonic at record {n} (fail closed)")
            prev = rec.hash
            out.append(rec)
        return tuple(out)

    def records(self) -> tuple[AnchorRecord, ...]:
        with self._lock:
            return self._read()

    def latest(self) -> AnchorRecord | None:
        with self._lock:
            recs = self._read()
            return recs[-1] if recs else None

    def verify(self) -> AnchorVerification:
        with self._lock:
            try:
                recs = self._read()
            except AnchorError as exc:
                return AnchorVerification(ok=False, count=0, detail=str(exc))
            return AnchorVerification(ok=True, count=len(recs))

    # --- write path (append only; the audit store is never touched) -------------------------------------------------
    def publish(self, head: ChainHead, *, correlation_id: str) -> AnchorRecord:
        with self._lock:
            recs = self._read()  # a broken chain refuses publication (AnchorIntegrityError)
            last = recs[-1] if recs else None
            if last is not None:
                if head.length < last.length:
                    raise AnchorError(f"anchor rollback refused: {head.length} < published {last.length} (fail closed)")
                if head.length == last.length and head.head_hash != last.head_hash:
                    raise AnchorError(f"anchor fork refused at length {head.length}: head differs from the published one (fail closed)")
            seq = (last.anchor_seq + 1) if last else 1
            prev = last.hash if last else GENESIS_ANCHOR_HASH
            at = self._clock()
            digest = AnchorRecord.compute_hash(seq, head.length, head.head_hash, head.sealed_at, at, self._principal, correlation_id, prev)
            rec = AnchorRecord(
                anchor_seq=seq,
                length=head.length,
                head_hash=head.head_hash,
                sealed_at=head.sealed_at,
                published_at=at,
                principal=self._principal,
                correlation_id=correlation_id,
                prev_hash=prev,
                hash=digest,
            )
            try:
                with self._file.open("a", encoding="utf-8") as fh:
                    fh.write(rec.model_dump_json() + "\n")
                    fh.flush()
            except OSError as exc:
                raise AnchorError(f"anchor publication failed: {type(exc).__name__}") from exc
            return rec
