"""Re-establishing an audit witness that was genuinely lost [Source: 03, 06; NFR-AUD-01]
/ [Committee: ADR-020 amendment 3 proposed, Product Owner decision 2026-09-08 on Red-Team Case B/C, D-066]
/ [Open: O-54 anchor principal, H-21 WORM/replica written by a separate principal].

A platform whose own records name an external witness that is now absent **does not open** (``AuditStore`` raises
``WitnessLostError``). That refusal has to be recoverable, because a replica really can be lost, and it must not be
recoverable by the ordinary gesture, because a deliberate truncation looks exactly like a lost replica to the
operator and sealing over it makes the two indistinguishable to everyone else, for ever.

So the recovery lives here, in its own module, as two operations and nothing else:

* ``inspect_chain`` — **read only**. It opens no ``AuditStore``, appends nothing, publishes nothing and returns no
  object that can write: a length, a head hash, whether the chain verifies, what the store recorded witnessing.
  The operator needs it because the attestation below must state exactly what they are witnessing.
* ``reestablish_witness`` — the named act. It is refused unless the witness really is absent, the attestation
  describes this chain exactly (length, head hash and the last anchor sequence this store recorded publishing) and
  the chain agrees with every head this store recorded witnessing. It writes one ``audit.witness.reestablished``
  row naming the actor and their reason under the operator's correlation id, and publishes an anchor that covers
  that row. There is no flag, no environment variable and no composition-root parameter that reaches it, and
  repeating an ordinary ``seal`` can never become it.

What this is **not**: it is not a way to make a refused platform start without evidence, and it is not a control
against an attacker who already owns both stores — such an actor can take this path too. What it costs them is a
row in the hash chain that says a witness was replaced, by whom, and on what claim. Restoring the last good copy
of the replica (RB-13, TC-AUD-009) remains the first choice; this is for when there is no copy left.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from typing import Any

from rtcore.clock import utc_now
from rtcore.schemas.base import StrictModel
from rtcore.store import Store

from audit_service.anchor import AnchorError, AnchorPublisher
from audit_service.store import (
    ANCHOR_PUBLISHED,
    ATTESTATION_MISMATCH,
    AUDIT_EVENTS_TABLE,
    AUDIT_SEALS_TABLE,
    GENESIS_HASH,
    AuditEvent,
    AuditStore,
    Reestablishment,
    SealRecord,
    SealRefused,
    WitnessAttestation,
)


class ChainInspection(StrictModel):
    """What an operator may read about a store that will not open. Values only: nothing here can write anything."""

    length: int
    head_hash: str
    chain_ok: bool
    detail: str = ""
    witness_present: bool = False
    witness_readable: bool = True
    #: The highest anchor sequence the store recorded publishing (0 when it recorded none) — the value the
    #: attestation must repeat, so that the act cannot be performed without having read the store first.
    last_anchor_seq: int = 0
    #: The highest length recorded by a *seal record* (None when no seal record survives; publication rows in the
    #: chain prove the store was witnessed, but only ever describe a prefix that is still intact).
    floor_length: int | None = None
    seals: int = 0
    marks: int = 0


def inspect_chain(store: Store, publisher: AnchorPublisher | None = None) -> ChainInspection:
    """Read the persisted chain and its own witness records without opening an ``AuditStore`` (read only).

    It deliberately does not construct an ``AuditStore``: that constructor is the thing that refuses, and an
    inspection an operator runs on a refused store must not be able to become an open store by accident.
    """
    events: list[AuditEvent] = [AuditEvent.model_validate_json(raw) for _, raw in sorted(store.items(AUDIT_EVENTS_TABLE))]
    seals: list[SealRecord] = [SealRecord.model_validate_json(raw) for _, raw in sorted(store.items(AUDIT_SEALS_TABLE))]
    verification = AuditStore().verify(events, published=False)
    marks = [e for e in events if e.action == ANCHOR_PUBLISHED]
    seal_lengths = [s.head.length for s in seals if s.anchor_seq is not None]
    present, readable = False, True
    if publisher is not None:
        try:
            present = publisher.latest() is not None
        except AnchorError:
            readable = False
    return ChainInspection(
        length=len(events),
        head_hash=events[-1].hash if events else GENESIS_HASH,
        chain_ok=verification.ok,
        detail=verification.detail,
        witness_present=present,
        witness_readable=readable,
        last_anchor_seq=max(
            [*(s.anchor_seq for s in seals if s.anchor_seq is not None), *(int(m.payload["anchor_seq"]) for m in marks)], default=0
        ),
        floor_length=max(seal_lengths) if seal_lengths else None,
        seals=len(seals),
        marks=len(marks),
    )


def reestablish_witness(
    *,
    store: Store,
    publisher: AnchorPublisher,
    attestation: WitnessAttestation,
    alerts: Callable[[str, dict[str, Any]], object] | None = None,
    clock: Callable[[], datetime] = utc_now,
) -> Reestablishment:
    """Perform the attested act on a store that will not open, and close it again.

    The store handle is consumed: this returns evidence, never a usable audit store. The platform is started
    normally afterwards, and it starts because there is a witness again — not because a check was skipped.
    """
    audit = AuditStore(store=store, clock=clock, publisher=publisher, alerts=alerts, attestation=attestation)
    try:
        done = audit.last_reestablishment
        if done is None:  # pragma: no cover - the constructor either performs the act or raises
            raise SealRefused(f"{ATTESTATION_MISMATCH}: the attested act did not run (fail closed)")
        return done
    finally:
        audit.close()
