"""Anchor the control store's journal head into the audit chain [Source: 03, 06] / [Committee: D-061 (5) Option B,
Security & Privacy Board COUNCIL_2026-09-08_gate_B_spb_docs §3.1, ADR-018 amendment 1, ADR-020] / [Open: O-54, O-128, O-133].

ADR-018 says plainly what its own digests cannot see: an offline actor with write access who rewrites rows *and*
re-computes the unkeyed journal chain, or who rolls the whole file back to an earlier consistent state, leaves a
store that satisfies ``SqliteStore.verify()``. The Security & Privacy Board chose to close that class by anchoring
rather than by keying: the store's journal head (a sequence and a chained digest, no row values, no secret) is
written into the **audit chain**, which is a different store, verified on its own hashes, and witnessed off-box by
a **different principal** (ADR-020). An attacker must then rewrite both, and rewriting the second breaks the
external anchor it does not own. No key enters the Execution plane, where ``secrets_mount: none`` holds.

**Direction of dependency.** This module is in the core library and imports nothing from any service. It talks to
the audit trail through the narrow ``JournalWitness`` protocol — *append a typed row, read typed rows back, say
whether you verify* — which is exactly the audit service's existing append path and nothing more. The composition
root wires an adapter (``audit_service.journal_witness.AuditJournalWitness``). The audit service therefore never
imports the control store's internals, and the control plane gains no audit write path it did not already have.

**Ordering.** Heads are recorded *after* the control-store transaction commits. Recording before the commit would
witness heads that never existed (every crash would look like tampering); recording after means the store may be
ahead of the witness, which is the benign direction and is bounded by ``max_lag``. Scheduled recording is best
effort and alerts; **verification fails closed** and refuses the store.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, Protocol

from rtcore.ids import new_id
from rtcore.store import GENESIS, SEQUENCE_TABLE, CommitInfo, JournalHead, Store, StoreIntegrityError

#: Audit actions. The Board's packet wrote ``store.journal.sealed``; ``anchored`` is used here so that "seal" keeps
#: the single meaning ADR-020 gave it (an operator sealing the *audit* head) [Committee: SPB §3.1].
JOURNAL_ANCHORED = "store.journal.anchored"
JOURNAL_INCIDENT = "store.journal.incident"
JOURNAL_RECOVERED = "store.journal.recovered"

#: Reason codes (docs/REASON_CODES.md). ``AUD-*`` names failures of the audit chain itself (ADR-020); these name
#: failures of the *control store* against its witness, and they surface as ``StoreIntegrityError`` beside the rest
#: of the ADR-018 store family, which is what an operator reading a refusal at start-up will be holding.
JOURNAL_ROLLBACK = "STORE-JOURNAL-ROLLBACK"
JOURNAL_FORK = "STORE-JOURNAL-FORK"
JOURNAL_UNWITNESSED = "STORE-JOURNAL-UNWITNESSED"
JOURNAL_STALE = "STORE-JOURNAL-STALE"
JOURNAL_WITNESS_UNTRUSTED = "STORE-JOURNAL-WITNESS-UNTRUSTED"

#: Catalogued alert (observability/alerts.yaml). S1, ``auto_action: none`` on purpose: an automatic reaction that
#: wrote to the store under investigation (a Kill Switch activation is a store row) would destroy the evidence.
STORE_JOURNAL_ALERT = "store.journal_unwitnessed"

#: Cadence. Both are dev/sim placeholders in the shape ADR-020 already uses for the audit anchor, not decided
#: values: the real cadence and staleness ceiling come with the anchor principal [Open: O-54, O-133].
DEFAULT_ANCHOR_EVERY = 25
DEFAULT_MAX_LAG = 200

#: The tables the Security & Privacy Board named as carrying a control invariant: a commit that touches one of
#: them is anchored immediately, whatever the count-based cadence says, so the window an attacker could rewrite
#: never contains a consumed grant, a decision, a lease or a Kill Switch activation [Committee: SPB §3.1].
#: Widening this list is the owner's decision, not the builder's [Open: O-128].
DEFAULT_CONTROL_TABLES: tuple[str, ...] = (
    "killswitch.activations",
    "execution.consumed_authorisations",
    "execution.by_decision",
    "execution.leases",
)
#: ...and the named sequences that are themselves control invariants (the fencing counter).
DEFAULT_CONTROL_SEQUENCES: tuple[str, ...] = ("fencing:",)


@dataclass(frozen=True)
class WitnessRow:
    """One row read back from the witness: only what this module wrote."""

    correlation_id: str
    payload: dict[str, Any]


class JournalWitness(Protocol):
    """The audit trail, seen from the control store: append one typed row, read typed rows back, self-report.

    Deliberately three methods. There is no update, no delete, and no way to reach an audit event that this
    module did not write; ``verified`` answers a question, it does not repair anything.
    """

    def record(self, action: str, payload: dict[str, Any], *, correlation_id: str) -> None: ...

    def rows(self, action: str) -> tuple[WitnessRow, ...]: ...

    def verified(self) -> tuple[bool, str]: ...


@dataclass(frozen=True)
class AnchorCheck:
    """The result of comparing a store's journal head with the head the audit chain witnessed."""

    ok: bool
    store_id: str
    sequence: int
    witnessed_sequence: int | None = None
    lag: int | None = None
    reason: str = ""
    detail: str = ""

    def as_payload(self) -> dict[str, Any]:
        return {
            "store_id": self.store_id,
            "sequence": self.sequence,
            "witnessed_sequence": self.witnessed_sequence,
            "lag": self.lag,
            "reason": self.reason,
            "detail": self.detail,
        }


@dataclass
class JournalAnchor:
    """Writes a store's journal head into the audit chain, and refuses the store when the two disagree.

    ``check`` is a pure comparison. ``verify`` is the fail-closed gate: it alerts, opens exactly one durable
    incident row, and raises ``StoreIntegrityError``. ``start`` is what a composition root calls at open, before
    anything is allowed to read or write the store.
    """

    store: Store
    witness: JournalWitness
    anchor_every: int = DEFAULT_ANCHOR_EVERY
    max_lag: int = DEFAULT_MAX_LAG
    control_tables: tuple[str, ...] = DEFAULT_CONTROL_TABLES
    control_sequences: tuple[str, ...] = DEFAULT_CONTROL_SEQUENCES
    alerts: Callable[[str, dict[str, Any]], object] | None = None
    _last: JournalHead | None = field(default=None, init=False, repr=False)
    _recording: bool = field(default=False, init=False, repr=False)
    _attached: bool = field(default=False, init=False, repr=False)

    # --- identity and reads -------------------------------------------------------------------------------
    @property
    def store_id(self) -> str:
        return self.store.store_id

    def _head(self) -> JournalHead:
        """The current head, or the genesis head when the journal is empty (an empty journal is still witnessed)."""
        head = self.store.journal_head()
        return head if head is not None else JournalHead(self.store_id, 0, GENESIS)

    def last_witnessed(self) -> JournalHead | None:
        """The last head this store's identity was anchored at, read back out of the audit chain."""
        for row in reversed(self.witness.rows(JOURNAL_ANCHORED)):
            if row.payload.get("store_id") == self.store_id:
                return JournalHead(self.store_id, int(row.payload["sequence"]), str(row.payload["head_digest"]))
        return None

    def open_incident(self) -> tuple[str, str] | None:
        """The correlation id and reason of an incident that has no recovery row yet; the state is durable, not in memory."""
        closed = {row.correlation_id for row in self.witness.rows(JOURNAL_RECOVERED)}
        for row in reversed(self.witness.rows(JOURNAL_INCIDENT)):
            if row.payload.get("store_id") == self.store_id and row.correlation_id not in closed:
                return row.correlation_id, str(row.payload.get("reason", ""))
        return None

    # --- writing the head ---------------------------------------------------------------------------------
    def anchor(self, *, correlation_id: str, trigger: str, tables: tuple[str, ...] = ()) -> JournalHead | None:
        """Write the current head into the audit chain. Returns ``None`` when the witness already carries it."""
        head = self._head()
        if self._last is not None and (head.sequence, head.digest) == (self._last.sequence, self._last.digest):
            return None
        self.witness.record(
            JOURNAL_ANCHORED,
            {
                "store_id": head.store_id,
                "sequence": head.sequence,
                "head_digest": head.digest,
                "trigger": trigger,
                "tables": sorted(set(tables)),
            },
            correlation_id=correlation_id or self._synthetic_correlation(head),
        )
        self._last = head
        return head

    def _synthetic_correlation(self, head: JournalHead) -> str:
        """Only used when a journal entry carried no correlation id: every audit row still has one."""
        return f"store-journal:{head.store_id}:{head.sequence}"

    def _is_control_write(self, table: str, key: str) -> bool:
        if table in self.control_tables:
            return True
        return table == SEQUENCE_TABLE and key.startswith(self.control_sequences)

    def _on_commit(self, info: CommitInfo) -> None:
        if self._recording:  # the witness is a different store, but never let a witness write re-enter this path
            return
        triggered = tuple(sorted({t for t, k in info.writes if self._is_control_write(t, k)}))
        behind = info.head.sequence - (self._last.sequence if self._last is not None else 0)
        due = bool(self.anchor_every) and behind >= self.anchor_every
        if not triggered and not due:
            return
        self._recording = True
        try:
            self.anchor(
                correlation_id=info.correlation_id if info.correlation_id != "-" else "",
                trigger="control_write" if triggered else "scheduled",
                tables=tuple(sorted({t for t, _ in info.writes})),
            )
        except Exception as exc:  # noqa: BLE001 - best effort by design: see the module docstring on ordering
            # The control write is already committed. A witness that cannot be written is an alert and a widening
            # lag that ``check`` will refuse; it is never a lost or rolled-back control write.
            self._alert(
                {
                    "store_id": self.store_id,
                    "sequence": info.head.sequence,
                    "witnessed_sequence": self._last.sequence if self._last is not None else None,
                    "reason": JOURNAL_UNWITNESSED,
                    "detail": f"could not record the journal head: {type(exc).__name__}: {exc}",
                    "correlation_id": info.correlation_id,
                }
            )
        finally:
            self._recording = False

    def attach(self) -> None:
        self.store.set_commit_observer(self._on_commit)
        self._attached = True

    def detach(self) -> None:
        self.store.set_commit_observer(None)
        self._attached = False

    # --- the check ----------------------------------------------------------------------------------------
    def check(self) -> AnchorCheck:
        """Compare the store's journal head with the last head the audit chain witnessed. No side effects."""
        head = self._head()
        witnessed = self.last_witnessed()
        if witnessed is None:
            if head.sequence == 0:
                # Genesis: an empty journal with no witness is a store that has not done anything yet. Anything
                # else without a witness is a store whose history the chain never saw, which fails closed below.
                return AnchorCheck(ok=True, store_id=head.store_id, sequence=0)
            return AnchorCheck(
                ok=False,
                store_id=head.store_id,
                sequence=head.sequence,
                reason=JOURNAL_UNWITNESSED,
                detail=f"the audit chain holds no anchored head for store '{head.store_id}', whose journal is at {head.sequence}",
            )
        if witnessed.sequence > head.sequence:
            return AnchorCheck(
                ok=False,
                store_id=head.store_id,
                sequence=head.sequence,
                witnessed_sequence=witnessed.sequence,
                reason=JOURNAL_ROLLBACK,
                detail=(
                    f"the journal is at {head.sequence} but the audit chain witnessed {witnessed.sequence}: "
                    "the store was rolled back or replaced"
                ),
            )
        at = self.store.journal_head(at=witnessed.sequence) if witnessed.sequence else JournalHead(head.store_id, 0, GENESIS)
        if at is None or at.digest != witnessed.digest:
            return AnchorCheck(
                ok=False,
                store_id=head.store_id,
                sequence=head.sequence,
                witnessed_sequence=witnessed.sequence,
                reason=JOURNAL_FORK,
                detail=(
                    f"the journal digest at sequence {witnessed.sequence} is not the one the audit chain witnessed: "
                    "the history was rewritten"
                ),
            )
        lag = head.sequence - witnessed.sequence
        if self.max_lag and lag > self.max_lag:
            return AnchorCheck(
                ok=False,
                store_id=head.store_id,
                sequence=head.sequence,
                witnessed_sequence=witnessed.sequence,
                lag=lag,
                reason=JOURNAL_STALE,
                detail=f"the witnessed head is {lag} journal entries behind, ceiling {self.max_lag}",
            )
        return AnchorCheck(ok=True, store_id=head.store_id, sequence=head.sequence, witnessed_sequence=witnessed.sequence, lag=lag)

    def check_witness(self) -> AnchorCheck:
        """The composition: a head is only witnessed if the chain that carries it verifies against *its* witness.

        Without this, an attacker who rewrote both stores consistently would satisfy ``check``; with it, they must
        also produce an external anchor they do not own (TC-DUR-007). It is a separate call because it costs a full
        audit-chain and anchor-chain verification, and because ADR-020 — not this module — owns what a failing
        audit chain does to a running platform (S1 and the platform Kill Switch).
        """
        head = self._head()
        ok, reason = self.witness.verified()
        if ok:
            return AnchorCheck(ok=True, store_id=head.store_id, sequence=head.sequence)
        return AnchorCheck(
            ok=False,
            store_id=head.store_id,
            sequence=head.sequence,
            reason=JOURNAL_WITNESS_UNTRUSTED,
            detail=f"the audit chain that witnesses this journal does not itself verify: {reason}",
        )

    def verify(self, *, with_witness: bool = False) -> AnchorCheck:
        """Fail-closed gate: alert, open exactly one durable incident, and raise on any disagreement."""
        result = self.check()
        if result.ok and with_witness:
            result = self.check_witness()
        if not result.ok:
            self._on_failed(result)
            raise StoreIntegrityError(f"{result.reason}: {result.detail} (fail closed)")
        return result

    def start(self) -> AnchorCheck:
        """What a composition root calls at open: verify, close any open incident, witness the head, then observe.

        Nothing may read or write the store before this returns: a rolled-back store must be refused *before* the
        composition writes on top of its journal, which would make the rollback permanent and self-consistent.
        """
        result = self.verify()
        self._last = self.last_witnessed()
        incident = self.open_incident()
        if incident is not None:
            correlation_id, reason = incident
            self.witness.record(
                JOURNAL_RECOVERED,
                {
                    "store_id": self.store_id,
                    "incident_reason": reason,
                    "sequence": result.sequence,
                    "witnessed_sequence": result.witnessed_sequence,
                    "lag": result.lag,
                },
                correlation_id=correlation_id,
            )
        self.anchor(correlation_id=f"store-open:{self.store_id}:{result.sequence}", trigger="open")
        self.attach()
        return result

    # --- incident handling --------------------------------------------------------------------------------
    def _on_failed(self, result: AnchorCheck) -> None:
        open_incident = self.open_incident()
        correlation_id = open_incident[0] if open_incident is not None else f"store-journal-{new_id('inc')}"
        self._alert({**result.as_payload(), "correlation_id": correlation_id, "max_lag": self.max_lag})
        if open_incident is None:
            # Exactly one incident row until it is closed by a recovery row under the same correlation id.
            self.witness.record(JOURNAL_INCIDENT, result.as_payload(), correlation_id=correlation_id)

    def _alert(self, payload: dict[str, Any]) -> None:
        if self.alerts is not None:
            self.alerts(STORE_JOURNAL_ALERT, payload)
