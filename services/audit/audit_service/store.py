"""Append-only audit chain, durable on the ``rtcore.store`` seam and witnessed by an external anchor.

[Source: 03, 06; NFR-AUD-01; T-12] / [Committee: ADR-018 seam, ADR-020 proposed, REVIEW_C5 OBJ-3] / [Open: O-54, O-110]

Three layers, each catching what the one below cannot:

1. the **seam** (``rtcore.store``) gives per-row digests and a hash-chained journal, so an edited or deleted row in
   the file is refused when the store is opened;
2. the **audit chain** (``prev_hash``/``hash`` per event) survives a consistent rewrite of every seam digest, which
   is the offline attacker O-110 admits;
3. the **external anchor** (``audit_service.anchor``) is written by a *different principal* to a store the audit
   process cannot rewrite, so a consistent rewrite of rows, journal *and* chain is still caught — and so is a
   truncation or a silent restore of a stale backup.

There is no update and no delete path here, at any layer, for any caller. A verification failure never repairs
itself: it raises the catalogued alert, opens one incident row, and stays failed until an operator acts.
"""

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
from rtcore.store import SEQUENCE_TABLE, MemoryStore, Store

from audit_service.anchor import AnchorError, AnchorHandle, AnchorPublisher, AnchorRecord, ChainHead

GENESIS_HASH = sha256_hex("rt365-audit-genesis")

AUDIT_EVENTS_TABLE = "audit_events"
AUDIT_SEALS_TABLE = "audit_seals"
AUDIT_SEQUENCE = "audit_seq"  # the sequence is allocated by the store, not by the length of an in-memory list

#: Publish an anchor every N appended events (0 = only on an explicit ``seal``). Scheduled publication bounds how
#: many events a consistent-rewrite attacker could reach; the ceiling below bounds how stale the witness may get.
DEFAULT_ANCHOR_EVERY = 25
#: Events allowed between the published anchor and the head before ``verify`` fails closed (O-54 cadence [Open]).
DEFAULT_MAX_ANCHOR_LAG = 200

# Reason codes on a failed verification (docs/REASON_CODES.md).
CHAIN_BROKEN = "AUD-CHAIN-BROKEN"
CHAIN_TRUNCATED = "AUD-CHAIN-TRUNCATED"
CHAIN_HEAD_MISMATCH = "AUD-CHAIN-HEAD-MISMATCH"
ANCHOR_MISSING = "AUD-ANCHOR-MISSING"
ANCHOR_STALE = "AUD-ANCHOR-STALE"
ANCHOR_CHAIN_BROKEN = "AUD-ANCHOR-CHAIN-BROKEN"
ANCHOR_TAIL_REMOVED = "AUD-ANCHOR-TAIL-REMOVED"
_ANCHOR_REASONS = frozenset({ANCHOR_MISSING, ANCHOR_STALE, ANCHOR_CHAIN_BROKEN, ANCHOR_TAIL_REMOVED})

# Witness continuity and the seal floor (ADR-020 amendment 3 proposed; Product Owner decision 2026-09-08 on the
# Red-Team Lead's Case B and Case C). These are refusals, not verdicts a running platform may carry.
WITNESS_LOST = "AUD-WITNESS-LOST"  # this store's own records name a witness; the anchor store holds no record at all
WITNESS_UNREADABLE = "AUD-WITNESS-UNREADABLE"  # ...and one that cannot be read is not a witness either
SEAL_BELOW_FLOOR = "AUD-SEAL-BELOW-FLOOR"  # the chain contradicts a head this store already recorded witnessing
SEAL_UNWITNESSED = "AUD-SEAL-UNWITNESSED"  # an ordinary seal may not create the first anchor for a non-empty chain
WITNESS_PRESENT = "AUD-WITNESS-PRESENT"  # re-establishment refused: there is a witness, so there is nothing to restore
ATTESTATION_MISMATCH = "AUD-ATTESTATION-MISMATCH"  # the operator's attestation does not describe this chain

# The two catalogued alerts this store raises (docs/ALERT_CATALOG.md, observability/alerts.yaml). Named here so the
# composition root raises the same name for a refusal it detects before this store exists (SRE review F-02).
CHAIN_ALERT = "audit.chain_verification_failed"  # S1, auto-action killswitch_platform
ANCHOR_ALERT = "audit.anchor_missing"  # S1, auto-action none: the chain may be intact; a human restores the witness

#: Actions this store writes about its own witness. ``ANCHOR_PUBLISHED`` is written into the chain after a genesis
#: or scheduled publication (an operator seal is recorded as a ``SealRecord`` instead, with its anchor sequence).
#: It is the fact "this store has been witnessed", kept where a tail truncation cannot remove it: the genesis mark
#: is the first event of the chain, and removing it breaks the chain at seq 0.
ANCHOR_PUBLISHED = "audit.anchor.published"
#: The named, attested operator act that re-establishes a witness after a genuine loss. Never automatic.
WITNESS_REESTABLISHED = "audit.witness.reestablished"


class AuditIntegrityError(RuntimeError):
    """The persisted chain does not verify when the store is opened; the caller must not proceed (fail closed)."""


class WitnessLostError(AuditIntegrityError):
    """This store's own records name an external witness, and that witness is absent or unreadable.

    A platform that had a witness and no longer has one does not open — the same refusal, for the same reason, as a
    control store whose head cannot be confirmed: refuse, alert, write nothing. It is deliberately *not* a Kill
    Switch: a Kill Switch activation is itself a store row and would write to the store under suspicion (D-066).
    """


class SealRefused(AuditIntegrityError):
    """A publication was refused: it would witness a chain that contradicts, or is unwitnessed by, what is recorded.

    Raised by ``seal`` and by the attested re-establishment. Nothing is published and no seal record is written.
    """


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
    reason: str = ""
    #: Length of the anchor the chain was checked against, when one was published.
    anchor_length: int | None = None
    #: Events between that anchor and the head.
    lag: int | None = None


class SealRecord(StrictModel):
    """A seal the audit store took, kept with the chain so a removed anchor tail is still detectable."""

    head: ChainHead
    correlation_id: str
    #: Sequence of the witness record this seal was published as; two seals at the same length differ here, so a
    #: removed anchor tail is detectable even when it removed no length.
    anchor_seq: int | None = None


class WitnessFloor(StrictModel):
    """The highest head this store recorded having witnessed, and where that record lives.

    Two sources, because they fail differently. A ``SealRecord`` in the seals table carries a length, a head hash
    *and* the anchor sequence, but it is written after the events it seals, so a rollback of the store takes it
    with them (measured against the Red-Team Lead's Case C). An ``audit.anchor.published`` row is inside the hash
    chain, so a tail truncation that leaves a non-empty chain cannot remove the genesis mark — but a mark can only
    ever describe a prefix that is still intact, so it proves *that* the store was witnessed, not *how far*.

    Together: the mark answers "did this store have a witness" (Case B), the seal record answers "how far had it
    been witnessed" (Case C). Neither is a substitute for the witness itself.
    """

    length: int
    head_hash: str
    anchor_seq: int | None
    source: str  # "seal" or "mark"


class WitnessAttestation(StrictModel):
    """An operator's explicit statement that a lost witness is being re-established over a chain they have read.

    Every field must match the store, so the act cannot be performed by accident, from a stale runbook, or by
    repeating the ordinary seal: the operator must first read the chain (``audit_service.reestablish.inspect_chain``)
    and say what they are witnessing. It is not a flag and it does not disable anything — an attestation that does
    not describe this chain, or a chain that contradicts the floor, is refused exactly like a seal.
    """

    actor: str  # a named human operator; never an agent, never a service
    reason: str  # why the witness is gone, in the operator's words, on the audit row for ever
    length: int  # the chain length being witnessed
    head_hash: str  # the head hash at that length
    last_anchor_seq: int  # the highest anchor sequence this store recorded publishing (0 when it recorded none)
    correlation_id: str


class Reestablishment(StrictModel):
    """What the attested act produced: the new anchor, the audit row that records it, and the head it witnessed."""

    record: AnchorRecord
    row: "AuditEvent"
    head: ChainHead


def _key(seq: int) -> str:
    """Zero-padded so the store's lexicographic key order is sequence order."""
    return f"{seq:012d}"


class AuditStore:
    """Append-only store: events on the ``Store`` seam, heads witnessed by an external ``AnchorPublisher``.

    ``AuditStore()`` keeps the previous behaviour exactly (in-memory, no anchor). ``path=`` keeps the JSONL backend.
    ``store=`` persists on the seam; ``publisher=`` adds the external witness.
    """

    def __init__(
        self,
        path: Path | None = None,
        clock: Callable[[], datetime] = utc_now,
        *,
        store: Store | None = None,
        publisher: AnchorPublisher | None = None,
        anchor_every: int = DEFAULT_ANCHOR_EVERY,
        max_anchor_lag: int = DEFAULT_MAX_ANCHOR_LAG,
        alerts: Callable[[str, dict[str, Any]], object] | None = None,
        correlation_id: str = "",
        attestation: WitnessAttestation | None = None,
    ) -> None:
        self._events: list[AuditEvent] = []
        self._seals: list[SealRecord] = []
        self._lock = threading.RLock()
        self._path = path
        self._clock = clock
        self._listeners: list[Callable[[AuditEvent], object]] = []
        self._store: Store = store if store is not None else MemoryStore()
        self._publisher = publisher
        self._anchor_every = max(0, int(anchor_every))
        self._max_anchor_lag = max(0, int(max_anchor_lag))
        self._alerts = alerts
        self._incident: str | None = None  # correlation_id of the open anchor incident, if any
        self._incident_reason = ""
        #: Evidence of the attested act, when this store was opened to perform one. It is a result, not a state:
        #: nothing consults it to decide anything.
        self.last_reestablishment: Reestablishment | None = None
        self._in_publish = False  # re-entrancy guard: the publication row must not trigger another publication
        if path is not None and path.exists():
            for line in path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    self._events.append(AuditEvent.model_validate_json(line))
        else:
            self._load_from_store()
        if self._path is not None and self._events:
            # Legacy JSONL backend: the sequence lives in the file, so bring the store's counter up to it.
            self._store.put(SEQUENCE_TABLE, AUDIT_SEQUENCE, str(len(self._events)), correlation_id="audit:open")
        # ``alerts`` is accepted at construction, not only through ``set_alert_sink``, so that the open-time
        # verification below has somewhere to raise: a chain refused at open is the loudest failure this platform
        # has, and it used to be silent because the composition root wired the sink after the store was built
        # (SRE review F-02 / SRE-R1). ``correlation_id`` carries the caller's start-up id onto that alert.
        opened = self.verify(published=False, correlation_id=correlation_id)
        if not opened.ok:
            raise AuditIntegrityError(f"audit chain refused at open: {opened.detail} (seq {opened.first_bad_seq})")
        # Witness continuity, before anything else may happen to this store (ADR-020 amendment 3, PO 2026-09-08).
        # This raises ``WitnessLostError`` and writes nothing, or — when the caller is the named operator act —
        # performs the attested re-establishment. Neither path is reachable from a configuration value.
        self._open_witness_check(correlation_id=correlation_id, attestation=attestation)
        if self._publisher is not None and not self._events and self._publisher.latest() is None:
            # Genesis witness: an empty chain is anchored at length 0 so that "no anchor" can never be confused
            # with "nothing has happened yet". A restart with events and no anchor is never re-anchored silently.
            self._publish(self.seal_head(), correlation_id="anchor:genesis", trigger="genesis")

    # --- opening ------------------------------------------------------------------------
    def _load_from_store(self) -> None:
        for _, raw in sorted(self._store.items(AUDIT_EVENTS_TABLE)):
            self._events.append(AuditEvent.model_validate_json(raw))
        for _, raw in sorted(self._store.items(AUDIT_SEALS_TABLE)):
            self._seals.append(SealRecord.model_validate_json(raw))

    @property
    def backend(self) -> str:
        return type(self._store).__name__

    @property
    def publisher(self) -> AnchorPublisher | None:
        return self._publisher

    def set_alert_sink(self, sink: Callable[[str, dict[str, Any]], object]) -> None:
        """The composition root wires the alert router after both objects exist; nothing else may call this."""
        self._alerts = sink

    def close(self) -> None:
        self._store.close()

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
        with self._lock, self._store.transaction():
            # The sequence comes from the store so that the number a restart reads is the number that was durably
            # allocated, never the length of a list that a partial write could disagree with.
            seq = self._store.next_sequence(AUDIT_SEQUENCE, correlation_id=correlation_id) - 1
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
            self._store.put(AUDIT_EVENTS_TABLE, _key(seq), event.model_dump_json(), correlation_id=correlation_id)
            self._events.append(event)
            if self._path is not None:
                with self._path.open("a", encoding="utf-8") as fh:
                    fh.write(event.model_dump_json() + "\n")
            due = self._anchor_every and len(self._events) % self._anchor_every == 0
        if due:
            # Scheduled publication is best effort: a witness that cannot be written is an alert, never a lost event.
            self._publish(
                self.seal_head(), correlation_id=f"anchor:scheduled:{len(self._events)}", best_effort=True, trigger="scheduled"
            )
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

    def seals(self) -> tuple[SealRecord, ...]:
        return tuple(self._seals)

    def latest_anchor(self) -> AnchorRecord | None:
        if self._publisher is None:
            return None
        try:
            return self._publisher.latest()
        except AnchorError:
            return None

    def anchor_handle(self) -> AnchorHandle:
        """The interface a separate publisher principal is given: the sealed head and the length, nothing else."""
        store = self
        return AnchorHandle(lambda: store.seal_head())

    def seal_head(self) -> ChainHead:
        return ChainHead(length=len(self._events), head_hash=self.head_hash(), sealed_at=self._clock())

    # --- sealing and anchoring ----------------------------------------------------------
    def seal(self, correlation_id: str = "-") -> ChainHead:
        """Seal the head and publish it to the external witness. A witness that refuses the head raises (fail closed).

        Two refusals guard the publication, and neither can be turned off (ADR-020 amendment 3):

        * **the floor** — a chain that contradicts a head this store already recorded witnessing is never witnessed
          again, whatever the external witness says or does not say. A genuine replica loss and a deliberate
          truncation look the same to the operator; sealing over the second is what made them look the same to
          everyone else, for ever;
        * **the witness** — an ordinary seal may no longer create the *first* anchor for a non-empty chain. That is
          the attested operator act (``reestablish``), because a fresh anchor over an unwitnessed chain is exactly
          what restoring a stale backup, or truncating one, produces.
        """
        with self._lock:
            unwitnessed = False
            if self._publisher is not None and self._events:
                try:
                    unwitnessed = self._publisher.latest() is None
                except AnchorError:
                    unwitnessed = False  # a broken anchor chain is refused by ``_publish`` below, as it always was
            if unwitnessed:
                detail = (
                    "this store holds no published anchor for a non-empty chain: an ordinary seal may not establish "
                    "one. Re-establishing a witness is an explicit, attested operator act (reestablish)."
                )
                self._alert(
                    ANCHOR_ALERT,
                    {
                        "reason": SEAL_UNWITNESSED,
                        "detail": detail,
                        "correlation_id": correlation_id,
                        "length": len(self._events),
                        "floor_length": (floor := self.witness_floor()) and floor.length,
                    },
                )
                raise SealRefused(f"{SEAL_UNWITNESSED}: {detail} (fail closed)")
            head = self.seal_head()
            published = self._publish(head, correlation_id=correlation_id) if self._publisher is not None else None
            record = SealRecord(head=head, correlation_id=correlation_id, anchor_seq=published.anchor_seq if published else None)
            self._store.put(AUDIT_SEALS_TABLE, _key(len(self._seals)), record.model_dump_json(), correlation_id=correlation_id)
            self._seals.append(record)
            return head

    def _publish(
        self, head: ChainHead, *, correlation_id: str, best_effort: bool = False, trigger: str = "seal"
    ) -> AnchorRecord | None:
        if self._publisher is None:
            return None
        if self._in_publish:  # a mark appended below must never re-enter publication through the scheduled cadence
            return None
        # The floor, before *any* publication and not only before an operator's seal: an automatic publication that
        # re-anchored a chain contradicting what this store already recorded witnessing would launder a truncation
        # with nobody in the room at all (ADR-020 amendment 3).
        violation = self._floor_violation(list(self._events))
        if violation is not None:
            floor = self.witness_floor()
            self._alert(
                CHAIN_ALERT,
                {
                    "reason": SEAL_BELOW_FLOOR,
                    "detail": violation.detail,
                    "correlation_id": correlation_id,
                    "length": violation.length,
                    "floor_length": floor.length if floor else None,
                    "floor_source": floor.source if floor else None,
                    "anchor_length": violation.anchor_length,
                },
            )
            if best_effort:
                return None  # fail closed: no witness is published over a chain that contradicts our own record
            raise SealRefused(f"{SEAL_BELOW_FLOOR}: {violation.detail} (fail closed)")
        try:
            latest = self._publisher.latest()
            if latest is None and self._events and best_effort:
                # The witness is gone while the chain is not empty. A scheduled publication must never quietly
                # re-establish it: a fresh anchor over an unwitnessed chain is exactly what a restore of a stale
                # backup would produce. Only the attested operator act may re-anchor, and it is itself audited.
                raise AnchorError("no anchor published for a non-empty chain: refusing to re-anchor automatically")
            if latest is not None:
                against = self._verify_against(list(self._events), latest.length, latest.head_hash)
                if not against.ok:
                    # Never witness a head that contradicts the head already witnessed: an anchor published over a
                    # tampered or rolled-back chain would launder it. The contradiction is the finding, not the anchor.
                    raise AnchorError(f"publication refused: {against.detail} ({against.reason})")
            record = self._publisher.publish(head, correlation_id=correlation_id)
        except AnchorError as exc:
            if not best_effort:
                raise
            self._alert(
                ANCHOR_ALERT,
                {
                    "reason": ANCHOR_MISSING if "no anchor published" in str(exc) else ANCHOR_CHAIN_BROKEN,
                    "detail": str(exc),
                    "correlation_id": correlation_id,
                },
            )
            return None
        if trigger in ("genesis", "scheduled"):
            # A publication that takes no seal record is recorded in the chain itself, so that "this store has been
            # witnessed" is a fact an attacker cannot remove by deleting the witness: the genesis mark is the first
            # event of the chain and removing it breaks the chain at seq 0 (ADR-020 amendment 3). Only the anchor's
            # own numbers go in — a sequence, a length and a head hash — never a payload and never anything an agent
            # supplied (F-15).
            self._in_publish = True
            try:
                self.append(
                    correlation_id=correlation_id,
                    tenant="-",
                    actor="audit_service",
                    action=ANCHOR_PUBLISHED,
                    payload={
                        "anchor_seq": record.anchor_seq,
                        "length": record.length,
                        "head_hash": record.head_hash,
                        "principal": record.principal,
                        "trigger": trigger,
                    },
                )
            finally:
                self._in_publish = False
        return record

    # --- witness continuity and the seal floor (ADR-020 amendment 3) --------------------
    def witness_floor(self) -> WitnessFloor | None:
        """The highest head this store recorded witnessing, from its seal records and its own publication rows.

        ``None`` means this store has no record of ever having been witnessed — the genesis case, which is not the
        same thing as a witness that is gone, and is not refused.
        """
        best: WitnessFloor | None = None
        for seal in self._seals:
            if seal.anchor_seq is None:
                continue  # a seal taken with no publisher witnesses nothing
            if best is None or seal.head.length > best.length:
                best = WitnessFloor(length=seal.head.length, head_hash=seal.head.head_hash, anchor_seq=seal.anchor_seq, source="seal")
        for mark in self.by_action(ANCHOR_PUBLISHED):
            length = int(mark.payload["length"])
            if best is None or length > best.length:
                best = WitnessFloor(
                    length=length, head_hash=str(mark.payload["head_hash"]), anchor_seq=int(mark.payload["anchor_seq"]), source="mark"
                )
        return best

    def _witness_generation(self) -> tuple[int, int]:
        """Where the current witness begins: the chain sequence and length of the last re-established witness.

        Anchor *sequences* are the witness's own numbering, so they start again at 1 when a witness is replaced.
        Comparing a new witness with sequences recorded against the one that was lost would report a removed tail
        for ever. Chain *lengths* are not witness-relative and are never scoped: the floor keeps them all.
        """
        rows = self.by_action(WITNESS_REESTABLISHED)
        if not rows:
            return (-1, -1)
        return (rows[-1].seq, int(rows[-1].payload["attested_length"]))

    def recorded_anchor_seq(self) -> int:
        """The highest anchor sequence this store recorded publishing to the *current* witness (0 when none)."""
        since_seq, since_length = self._witness_generation()
        seals = [s.anchor_seq for s in self._seals if s.anchor_seq is not None and s.head.length > since_length]
        marks = [int(e.payload["anchor_seq"]) for e in self.by_action(ANCHOR_PUBLISHED) if e.seq > since_seq]
        return max([*seals, *marks], default=0)

    def _floor_violation(self, items: list[AuditEvent]) -> ChainVerification | None:
        """The chain checked against every head this store recorded witnessing; the first contradiction, or None."""
        recorded: list[tuple[int, str, str]] = [
            (s.head.length, s.head.head_hash, "seal") for s in self._seals if s.anchor_seq is not None
        ] + [(int(e.payload["length"]), str(e.payload["head_hash"]), "mark") for e in self.by_action(ANCHOR_PUBLISHED)]
        for length, head_hash, source in sorted(recorded, reverse=True):
            against = self._verify_against(items, length, head_hash)
            if not against.ok:
                return against.model_copy(
                    update={
                        "reason": SEAL_BELOW_FLOOR,
                        "detail": (
                            f"this store recorded witnessing length {length} ({source}); the chain now offers "
                            f"{len(items)}: {against.detail}"
                        ),
                    }
                )
        return None

    def _refuse_if_below_floor(self, *, correlation_id: str) -> None:
        violation = self._floor_violation(list(self._events))
        if violation is None:
            return
        floor = self.witness_floor()
        self._alert(
            CHAIN_ALERT,
            {
                "reason": SEAL_BELOW_FLOOR,
                "detail": violation.detail,
                "correlation_id": correlation_id,
                "length": violation.length,
                "floor_length": floor.length if floor else None,
                "floor_source": floor.source if floor else None,
                "anchor_length": violation.anchor_length,
            },
        )
        raise SealRefused(f"{SEAL_BELOW_FLOOR}: {violation.detail} (fail closed)")

    def _open_witness_check(self, *, correlation_id: str, attestation: WitnessAttestation | None) -> None:
        """At open: refuse a store whose own records name a witness that is absent, or perform the attested act.

        Nothing is written on the refusal path — no incident row, no publication, no Kill Switch. A store under
        suspicion is evidence; the response is to refuse to open it and to page a human (D-066).
        """
        if self._publisher is None:
            if attestation is not None:
                raise SealRefused(f"{ATTESTATION_MISMATCH}: there is no anchor publisher to re-establish (fail closed)")
            return
        readable, latest = True, None
        try:
            latest = self._publisher.latest()
        except AnchorError:
            readable = False
        if attestation is not None:
            self.last_reestablishment = self._reestablish(attestation, latest=latest, readable=readable)
            return
        floor = self.witness_floor()
        if floor is None or latest is not None:
            return  # never witnessed (genesis, unchanged), or the witness is here and ``verify`` owns what it says
        reason = WITNESS_LOST if readable else WITNESS_UNREADABLE
        detail = (
            f"this store recorded witnessing length {floor.length} as anchor {floor.anchor_seq} ({floor.source}), and the "
            + ("anchor store holds no record" if readable else "anchor store cannot be read")
            + ": a platform that had a witness and no longer has one does not open"
        )
        self._alert(
            ANCHOR_ALERT,
            {
                "reason": reason,
                "detail": detail,
                "correlation_id": correlation_id or f"audit-witness-{new_id('inc')}",
                "length": len(self._events),
                "floor_length": floor.length if floor.source == "seal" else None,
                "floor_source": floor.source,
                "marks": len(self.by_action(ANCHOR_PUBLISHED)),
                "recorded_anchor_seq": self.recorded_anchor_seq(),
            },
        )
        raise WitnessLostError(f"{reason}: {detail} (fail closed)")

    def reestablish(self, attestation: WitnessAttestation) -> "Reestablishment":
        """The named operator act: re-establish a witness this store lost, over a chain the operator has read.

        It is not a seal and a seal cannot reach it. It is refused unless the witness really is absent, the
        attestation describes this chain exactly, and the chain agrees with every head this store recorded
        witnessing. It writes one audit row — actor, reason, what was attested, what was lost — and publishes an
        anchor that covers that row, so the act is inside the evidence it re-establishes.
        """
        with self._lock:
            readable, latest = True, None
            try:
                latest = self._publisher.latest() if self._publisher is not None else None
            except AnchorError:
                readable = False
            self.last_reestablishment = self._reestablish(attestation, latest=latest, readable=readable)
            return self.last_reestablishment

    def _reestablish(self, attestation: WitnessAttestation, *, latest: AnchorRecord | None, readable: bool) -> "Reestablishment":
        if self._publisher is None:
            raise SealRefused(f"{ATTESTATION_MISMATCH}: there is no anchor publisher to re-establish (fail closed)")
        if latest is not None:
            raise SealRefused(
                f"{WITNESS_PRESENT}: the anchor store holds a witness at length {latest.length} (anchor {latest.anchor_seq}); "
                "there is nothing to re-establish (fail closed)"
            )
        if not readable:
            raise SealRefused(
                f"{WITNESS_UNREADABLE}: the anchor store cannot be read; it is restored from the last good copy, "
                "never overwritten (fail closed)"
            )
        recorded = self.recorded_anchor_seq()
        mismatches = [
            name
            for name, ok in (
                ("actor", bool(attestation.actor.strip())),
                ("reason", bool(attestation.reason.strip())),
                ("correlation_id", bool(attestation.correlation_id.strip())),
                ("length", attestation.length == len(self._events)),
                ("head_hash", attestation.head_hash == self.head_hash()),
                ("last_anchor_seq", attestation.last_anchor_seq == recorded),
            )
            if not ok
        ]
        if mismatches:
            raise SealRefused(
                f"{ATTESTATION_MISMATCH}: {', '.join(mismatches)} does not describe this chain "
                f"(length {len(self._events)}, head {self.head_hash()[:12]}…, last recorded anchor {recorded}) (fail closed)"
            )
        self._refuse_if_below_floor(correlation_id=attestation.correlation_id)
        floor = self.witness_floor()
        row = self.append(
            correlation_id=attestation.correlation_id,
            tenant="-",
            actor=attestation.actor,
            action=WITNESS_REESTABLISHED,
            payload={
                "reason": attestation.reason,
                "attested_length": attestation.length,
                "attested_head_hash": attestation.head_hash,
                "lost_anchor_seq": attestation.last_anchor_seq,
                "previous_floor_length": floor.length if floor else None,
                "previous_floor_source": floor.source if floor else None,
            },
        )
        head = self.seal_head()  # the head that includes the row above: the act witnesses itself
        record = self._publisher.publish(head, correlation_id=attestation.correlation_id)
        seal = SealRecord(head=head, correlation_id=attestation.correlation_id, anchor_seq=record.anchor_seq)
        self._store.put(AUDIT_SEALS_TABLE, _key(len(self._seals)), seal.model_dump_json(), correlation_id=attestation.correlation_id)
        self._seals.append(seal)
        self._alert(
            ANCHOR_ALERT,
            {
                "reason": WITNESS_REESTABLISHED,
                "detail": f"{attestation.actor} re-established the witness at length {head.length}: {attestation.reason}",
                "correlation_id": attestation.correlation_id,
                "length": head.length,
                "floor_length": floor.length if floor else None,
                "lost_anchor_seq": attestation.last_anchor_seq,
            },
        )
        return Reestablishment(record=record, row=row, head=head)

    def _alert(self, name: str, payload: dict[str, Any]) -> None:
        if self._alerts is not None:
            self._alerts(name, payload)

    # --- verification -------------------------------------------------------------------
    def verify(
        self,
        events: Iterable[AuditEvent] | None = None,
        *,
        anchor: ChainHead | None = None,
        published: bool = True,
        correlation_id: str = "",
    ) -> ChainVerification:
        """Verify the chain; with ``anchor`` against that sealed head, and by default against the published witness.

        A failure alerts and, for an anchor failure, opens exactly one incident row until the chain verifies again.
        ``correlation_id`` lets a caller that already owns an id (the composition root's start-up attempt) put the
        failure under it instead of a fresh one; an open incident's id always wins, so an incident is never split.
        """
        items = list(events) if events is not None else list(self._events)
        result = self._verify_chain(items)
        if result.ok and anchor is not None:
            result = self._verify_against(items, anchor.length, anchor.head_hash)
        if result.ok and published and events is None and self._publisher is not None:
            result = self._verify_published(items)
        if not result.ok:
            self._on_failed(result, correlation_id=correlation_id)
        elif events is None:
            self._on_recovered(result)
        return result

    def _verify_chain(self, items: list[AuditEvent]) -> ChainVerification:
        prev = GENESIS_HASH
        seq_expected = 0
        for e in items:
            bad = None
            if e.seq != seq_expected:
                bad = "sequence gap"
            elif e.prev_hash != prev:
                bad = "prev_hash mismatch"
            elif hash_of(e.payload) != e.payload_hash:
                bad = "payload tampered"
            elif (
                AuditEvent.compute_hash(
                    e.seq, e.event_id, e.ts, e.correlation_id, e.tenant, e.account, e.actor, e.action, e.payload_hash, e.prev_hash
                )
                != e.hash
            ):
                bad = "hash mismatch"
            if bad is not None:
                return ChainVerification(ok=False, length=len(items), first_bad_seq=e.seq, detail=bad, reason=CHAIN_BROKEN)
            prev = e.hash
            seq_expected += 1
        return ChainVerification(ok=True, length=len(items), head_hash=prev)

    def _verify_against(self, items: list[AuditEvent], length: int, head_hash: str) -> ChainVerification:
        head = items[-1].hash if items else GENESIS_HASH
        if len(items) < length:
            return ChainVerification(
                ok=False,
                length=len(items),
                head_hash=head,
                first_bad_seq=len(items),
                detail=f"chain truncated: {len(items)} < sealed {length}",
                reason=CHAIN_TRUNCATED,
                anchor_length=length,
            )
        sealed_head = items[length - 1].hash if length else GENESIS_HASH
        if sealed_head != head_hash:
            return ChainVerification(
                ok=False,
                length=len(items),
                head_hash=head,
                first_bad_seq=max(length - 1, 0),
                detail="sealed head does not match",
                reason=CHAIN_HEAD_MISMATCH,
                anchor_length=length,
            )
        return ChainVerification(ok=True, length=len(items), head_hash=head, anchor_length=length, lag=len(items) - length)

    def _verify_published(self, items: list[AuditEvent]) -> ChainVerification:
        assert self._publisher is not None  # noqa: S101 - a private helper's precondition, never a control decision
        head = items[-1].hash if items else GENESIS_HASH
        chain = self._publisher.verify()
        if not chain.ok:
            return ChainVerification(ok=False, length=len(items), head_hash=head, detail=chain.detail, reason=ANCHOR_CHAIN_BROKEN)
        latest = self._publisher.latest()
        if latest is None:
            return ChainVerification(
                ok=False,
                length=len(items),
                head_hash=head,
                detail="no anchor published: the external witness is absent (fail closed)",
                reason=ANCHOR_MISSING,
            )
        result = self._verify_against(items, latest.length, latest.head_hash)
        if not result.ok:
            return result
        # The witness agrees — and it is exactly what an attacker trims until it does. The floor needs no witness:
        # a chain that contradicts a head *this store* recorded witnessing is a finding whatever the anchor store
        # now says (ADR-020 amendment 3). It is asked after the witness so that, when the witness can speak, the
        # operator gets the witness's own more specific verdict.
        floor_violation = self._floor_violation(items)
        if floor_violation is not None:
            return floor_violation
        recorded = self.recorded_anchor_seq()  # seal records *and* the publication rows in the chain
        if recorded > latest.anchor_seq:
            return ChainVerification(
                ok=False,
                length=len(items),
                head_hash=head,
                detail=f"the store published anchor {recorded} but the witness stops at {latest.anchor_seq}: anchor tail removed",
                reason=ANCHOR_TAIL_REMOVED,
                anchor_length=latest.length,
                lag=len(items) - latest.length,
            )
        lag = len(items) - latest.length
        if lag > self._max_anchor_lag:
            return ChainVerification(
                ok=False,
                length=len(items),
                head_hash=head,
                detail=f"anchor is {lag} events behind the head, ceiling {self._max_anchor_lag}",
                reason=ANCHOR_STALE,
                anchor_length=latest.length,
                lag=lag,
            )
        return ChainVerification(ok=True, length=len(items), head_hash=head, anchor_length=latest.length, lag=lag)

    # --- incident handling --------------------------------------------------------------
    def _on_failed(self, result: ChainVerification, *, correlation_id: str = "") -> None:
        anchor_failure = result.reason in _ANCHOR_REASONS
        correlation_id = self._incident or correlation_id or f"audit-anchor-{new_id('inc')}"
        payload = {
            "reason": result.reason,
            "detail": result.detail,
            "correlation_id": correlation_id,
            "length": result.length,
            "anchor_length": result.anchor_length,
            "lag": result.lag,
            "max_lag": self._max_anchor_lag,
        }
        if anchor_failure:
            self._alert(ANCHOR_ALERT, payload)
            if self._incident is None:
                self._incident = correlation_id
                self._incident_reason = result.reason
                self.append(
                    correlation_id=correlation_id,
                    tenant="-",
                    actor="audit_service",
                    action="audit.anchor.incident",
                    payload={k: v for k, v in payload.items() if k != "correlation_id"},
                )
        else:
            self._alert(CHAIN_ALERT, payload)

    def _on_recovered(self, result: ChainVerification) -> None:
        if self._incident is None:
            return
        correlation_id, reason = self._incident, self._incident_reason
        self._incident, self._incident_reason = None, ""
        self.append(
            correlation_id=correlation_id,
            tenant="-",
            actor="audit_service",
            action="audit.anchor.recovered",
            payload={"incident_reason": reason, "anchor_length": result.anchor_length, "length": result.length},
        )

    # --- export -------------------------------------------------------------------------
    def export(self, correlation_id: str | None = None, *, tenant: str | None = None) -> str:
        items = self.by_correlation(correlation_id, tenant=tenant) if correlation_id else self.for_tenant(tenant) if tenant else self.all()
        return "\n".join(json.dumps(e.model_dump(mode="json"), sort_keys=True) for e in items)
