"""TC-DUR — Durable control state across restarts [Source: 03; NFR-CON-01; ADR-010 seam; ADR-018 proposed; R-05, R-23].

The invariants the control envelope relies on (fencing tokens never reissued lower, inbox dedupe, one-shot
grants, Kill Switch activations, outbox delivery) must survive a process restart. A platform built with a
``store_dir`` keeps them in one SQLite file (WAL); a platform rebuilt from the same directory is the restart.
"""

from __future__ import annotations

import json
import shutil
import sqlite3
from pathlib import Path

import pytest
from audit_service.journal_witness import AuditJournalWitness
from audit_service.store import AUDIT_EVENTS_TABLE, GENESIS_HASH, AuditEvent, AuditIntegrityError, AuditStore
from conftest import ACCOUNT, RISK_OFFICER, SRE, STRATEGY, resting_limit_intent
from execution_gateway.gateway import StaleFencingToken
from execution_gateway.lease import LeaseHeld
from killswitch_service.service import KillSwitchLevel
from rtcore.ids import hash_of
from rtcore.journal_anchor import (
    JOURNAL_ANCHORED,
    JOURNAL_FORK,
    JOURNAL_INCIDENT,
    JOURNAL_RECOVERED,
    JOURNAL_ROLLBACK,
    JOURNAL_UNWITNESSED,
    JOURNAL_WITNESS_UNTRUSTED,
    STORE_JOURNAL_ALERT,
    JournalAnchor,
)
from rtcore.planes import Plane, enter
from rtcore.schemas.order import OrderState
from rtcore.store import GENESIS, MemoryStore, SqliteStore, StoreError, StoreIntegrityError, journal_digest, row_digest
from test_tc_aud_audit import _rewrite_consistently, _rollback_consistently
from web_bff.platform import AUDIT_STORE_FILENAME, STORE_FILENAME, build_sim_platform

KEY = b"sim-only-command-authorisation-key-32b!!"  # the composition root receives the key; no AI/MCP component does (V-C2)


def _db(store_dir: Path) -> sqlite3.Connection:
    return sqlite3.connect(store_dir / STORE_FILENAME, isolation_level=None)


def _audit_db(store_dir: Path) -> sqlite3.Connection:
    return sqlite3.connect(store_dir / AUDIT_STORE_FILENAME, isolation_level=None)


@pytest.mark.tc("TC-DUR-001")
@pytest.mark.req("NFR-CON-01")
@pytest.mark.quartet("positive")
def test_control_state_survives_restart_and_outbox_relays_exactly_once(tmp_path):  # type: ignore[no-untyped-def]
    """Orders, lease token, Kill Switch activation and outbox rows written by one process are read back by a rebuilt platform; pending outbox events relay exactly once."""
    p1 = build_sim_platform(store_dir=tmp_path, authorisation_key=KEY)
    r = p1.run_intent(p1.make_intent())
    assert r.order.state == OrderState.FILLED
    token = p1.leases.current(ACCOUNT).fencing_token
    act = p1.killswitch.activate(KillSwitchLevel.STRATEGY, STRATEGY, reason="drill", actor=SRE, now=p1.now)
    written = p1.outbox.events()
    assert written and p1.outbox.pending() == written  # nothing relayed to a bus yet in dev/sim
    p1.store.verify()
    p1.store.close()

    p2 = build_sim_platform(store_dir=tmp_path, authorisation_key=KEY)  # restart
    assert p2.gateway.get(r.order.order_id).state == OrderState.FILLED
    assert p2.gateway.by_key(r.order.command.idempotency_key).order_id == r.order.order_id
    assert p2.leases.current(ACCOUNT).fencing_token == token
    assert p2.killswitch.get(act.activation_id).active and act in p2.killswitch.active()
    assert p2.outbox.events() == written
    delivered: list[str] = []
    assert p2.outbox.relay(lambda e: delivered.append(e.event_id)) == len(written)
    assert delivered == [e.event_id for e in written] and p2.outbox.pending() == ()
    assert p2.outbox.relay(lambda e: delivered.append(e.event_id)) == 0 and len(delivered) == len(written)
    p2.store.verify()
    # the memory implementation is the default: a platform without store_dir shares nothing with the file
    assert isinstance(build_sim_platform().store, MemoryStore)


@pytest.mark.tc("TC-DUR-002")
@pytest.mark.req("NFR-CON-01")
@pytest.mark.quartet("negative")
def test_two_platforms_on_one_store_cannot_both_hold_the_lease(tmp_path):  # type: ignore[no-untyped-def]
    """Two processes on the same store: the second cannot acquire a live lease, its guessed token is fenced, and a preemption by one is stale for the other (ADR-002)."""
    p1 = build_sim_platform(store_dir=tmp_path, authorisation_key=KEY, executor_id="executor-a")
    p2 = build_sim_platform(store_dir=tmp_path, authorisation_key=KEY, executor_id="executor-b")
    r = p1.run_intent(resting_limit_intent(p1))
    assert r.order.state == OrderState.ACKNOWLEDGED
    held = p1.leases.current(ACCOUNT)
    with pytest.raises(LeaseHeld):
        p2.leases.acquire(ACCOUNT, "executor-b", now=p2.now)
    assert p2.leases.current(ACCOUNT) == held  # both read the same truth
    with pytest.raises(LeaseHeld):  # the whole pipeline of the second executor is refused, not just the raw store call
        p2.run_intent(p2.make_intent())
    assert p2.broker.submissions_received == 0
    late = p2.pipeline.sign_command(
        r.order.command.model_copy(update={"idempotency_key": "k-guess", "command_id": "cmd-guess", "intent_id": "other-intent"})
    )
    with enter(Plane.CONTROL), pytest.raises(StaleFencingToken):
        p2.gateway.submit(late, executor_id="executor-b", fencing_token=held.fencing_token + 1, now=p2.now)
    # failover: B preempts through the shared store; A's token is stale in A's own process
    new = p2.leases.preempt(ACCOUNT, "executor-b", now=p2.now)
    assert new.fencing_token > held.fencing_token
    assert not p1.leases.is_valid(ACCOUNT, held.fencing_token, now=p1.now)
    with enter(Plane.CONTROL), pytest.raises(StaleFencingToken):
        p1.gateway.cancel(r.order.order_id, fencing_token=held.fencing_token, now=p1.now, reason="stale after failover")
    # once the live lease expires, a fresh acquisition still never reissues a lower token
    p2.advance(31)
    again = p2.leases.acquire(ACCOUNT, "executor-c", now=p2.now)
    assert again.fencing_token > new.fencing_token


@pytest.mark.tc("TC-DUR-003")
@pytest.mark.req("NFR-CON-01")
@pytest.mark.quartet("abuse")
def test_tampered_store_is_refused_and_store_errors_fail_closed(tmp_path):  # type: ignore[no-untyped-def]
    """A row edited, deleted or re-journalled behind the store's back is detected (row digest, hash-chained journal, replay check); a gateway whose store fails submits nothing."""
    p1 = build_sim_platform(store_dir=tmp_path, authorisation_key=KEY)
    act = p1.killswitch.activate(KillSwitchLevel.ACCOUNT, ACCOUNT, reason="drill", actor=RISK_OFFICER, now=p1.now)
    p1.store.verify()
    db = _db(tmp_path)
    (raw,) = db.execute("SELECT value FROM kv WHERE tbl='killswitch.activations' AND key=?", (act.activation_id,)).fetchone()
    doc = json.loads(raw)
    doc["active"] = False  # an attacker "deactivates" the switch by editing the file
    db.execute("UPDATE kv SET value=? WHERE tbl='killswitch.activations' AND key=?", (json.dumps(doc), act.activation_id))
    with pytest.raises(StoreIntegrityError):  # the live process refuses the row at read time
        p1.killswitch.active()
    with pytest.raises(StoreIntegrityError):
        p1.run_intent(p1.make_intent())  # the risk engine cannot even form a snapshot: nothing is decided, nothing is sent
    assert p1.broker.submissions_received == 0
    with pytest.raises(StoreIntegrityError):  # and a restart refuses the store as a whole
        build_sim_platform(store_dir=tmp_path, authorisation_key=KEY)
    # deleting the row (and its digest) is caught by the journal replay, not just the row digest
    db.execute("DELETE FROM kv WHERE tbl='killswitch.activations' AND key=?", (act.activation_id,))
    with pytest.raises(StoreIntegrityError):
        build_sim_platform(store_dir=tmp_path, authorisation_key=KEY)
    # rewriting history: dropping the journal entries that engaged the switch breaks the chain
    db.execute("DELETE FROM journal WHERE tbl='killswitch.activations'")
    with pytest.raises(StoreIntegrityError):
        build_sim_platform(store_dir=tmp_path, authorisation_key=KEY)
    db.close()

    # a store that cannot be read: the gateway submits nothing and alerts (fail closed)
    class Broken(MemoryStore):
        armed = False

        def get(self, table: str, key: str) -> str | None:
            if self.armed:
                raise StoreError("disk gone")
            return super().get(table, key)

    p3 = build_sim_platform()
    r = p3.run_intent(resting_limit_intent(p3))
    broken = Broken()
    for tbl, key, value in p3.store.dump():
        broken.put(tbl, key, value)
    p3.gateway._store = broken  # swap the backend under the live gateway
    broken.armed = True
    late = p3.pipeline.sign_command(r.order.command.model_copy(update={"idempotency_key": "k-late", "command_id": "cmd-late"}))
    lease = p3.leases.current(ACCOUNT)
    with enter(Plane.CONTROL), pytest.raises(StoreError):
        p3.gateway.submit(late, executor_id=p3.executor_id, fencing_token=lease.fencing_token, now=p3.now)
    with enter(Plane.CONTROL), pytest.raises(StoreError):
        p3.gateway.retry_submit(r.order.order_id, executor_id=p3.executor_id, fencing_token=lease.fencing_token, now=p3.now)
    assert p3.broker.submissions_received == 1 and p3.alerts.by_name("execution.store_unavailable")


@pytest.mark.tc("TC-DUR-004")
@pytest.mark.req("NFR-CON-01")
@pytest.mark.quartet("recovery")
def test_relay_crash_and_pipeline_replay_after_restart(tmp_path):  # type: ignore[no-untyped-def]
    """A relay that dies mid-batch leaves the rest pending; after a restart the remainder relays exactly once and a replayed pipeline message returns the stored result without a second broker order."""
    p1 = build_sim_platform(store_dir=tmp_path, authorisation_key=KEY)
    r = p1.run_intent(p1.make_intent())
    total = len(p1.outbox.events())
    assert total >= 4
    sent: list[str] = []

    def crashing_bus(e):  # type: ignore[no-untyped-def]
        if len(sent) == 2:
            raise ConnectionError("bus gone")
        sent.append(e.event_id)

    with pytest.raises(ConnectionError):
        p1.outbox.relay(crashing_bus)
    assert len(sent) == 2 and len(p1.outbox.pending()) == total - 2
    p1.store.close()

    p2 = build_sim_platform(store_dir=tmp_path, authorisation_key=KEY)
    rest: list[str] = []
    assert p2.outbox.relay(lambda e: rest.append(e.event_id)) == total - 2
    assert set(sent).isdisjoint(rest) and len(set(sent) | set(rest)) == total and p2.outbox.pending() == ()
    # the same validated intent redelivered to the rebuilt pipeline: inbox answers from the store, nothing executes twice
    again = p2.pipeline.process(r.validated_intent, now=p2.now)
    assert again.order.order_id == r.order.order_id and p2.gateway.get(again.order.order_id).state == OrderState.FILLED
    assert p2.broker.submissions_received == 0 and p2.pipeline.inbox.duplicates == 1
    p2.store.verify()


# --- the control store's journal head anchored into the audit chain (O-128, D-061 (5); ADR-018 amendment 1) --------------
# ADR-018 admits by construction the attack its own digests cannot see: an offline actor who rewrites rows *and*
# re-computes every unkeyed digest, or who rolls the whole file back to an earlier consistent state, leaves a store
# that satisfies ``SqliteStore.verify()``. The Security & Privacy Board chose (D-061 (5), Option B) to close that
# class by writing the journal head into the audit chain — a different store, verified on its own hashes and
# witnessed off-box by a different principal (ADR-020) — instead of putting an HMAC key inside the Execution plane.
# The four tests below are the quartet for that mechanism. TC-DUR-007 does not stop at "each half detects its own
# half": it carries the rewrite through *both* stores and shows where the composition breaks.


def _control_backup(store_dir: Path, dest: Path) -> Path:
    """Copy the closed control-store file (and any WAL sidecars) as an operator's backup."""
    dest.mkdir(parents=True, exist_ok=True)
    for f in store_dir.glob(f"{STORE_FILENAME}*"):
        shutil.copy(f, dest / f.name)
    return dest


def _restore_control(backup: Path, store_dir: Path) -> None:
    for f in store_dir.glob(f"{STORE_FILENAME}*"):
        f.unlink()
    for f in backup.glob(f"{STORE_FILENAME}*"):
        shutil.copy(f, store_dir / f.name)


def _anchored_rows(audit: AuditStore, store_id: str) -> tuple[AuditEvent, ...]:
    return tuple(e for e in audit.by_action(JOURNAL_ANCHORED) if e.payload.get("store_id") == store_id)


def _rewrite_rows_consistently(db: sqlite3.Connection, updates: dict[tuple[str, str], str]) -> None:
    """``_rewrite_consistently`` for many rows at once: rewrite the values and re-compute every unkeyed seam digest."""
    prev = GENESIS
    for seq, op, tbl, k, value, corr, at in db.execute(
        "SELECT seq, op, tbl, key, value, correlation_id, at FROM journal ORDER BY seq"
    ).fetchall():
        if op == "put" and (tbl, k) in updates:
            value = updates[(tbl, k)]
        digest = journal_digest(prev, int(seq), op, tbl, k, value, corr, at)
        db.execute("UPDATE journal SET value=?, prev=?, digest=? WHERE seq=?", (value, prev, digest, seq))
        prev = digest
    for (tbl, k), new in updates.items():
        row = db.execute("SELECT seq FROM kv WHERE tbl=? AND key=?", (tbl, k)).fetchone()
        if row is not None:
            db.execute("UPDATE kv SET value=?, digest=? WHERE tbl=? AND key=?", (new, row_digest(tbl, k, new, int(row[0])), tbl, k))


def _forge_audit_chain(db: sqlite3.Connection, store_id: str, sequence: int, head_digest: str) -> None:
    """The complete attack: make the audit chain agree with a rewritten control store.

    Rewrites the ``store.journal.anchored`` row for ``sequence`` to carry the attacker's head digest, then
    re-computes *every* audit event payload_hash, hash and prev_hash from genesis and every seam digest, so the
    audit store verifies on its own terms. Only the externally published anchor is left to catch it.
    """
    rows = db.execute("SELECT key, value FROM kv WHERE tbl=? ORDER BY key", (AUDIT_EVENTS_TABLE,)).fetchall()
    prev = GENESIS_HASH
    updates: dict[tuple[str, str], str] = {}
    for key, raw in rows:
        e = AuditEvent.model_validate_json(raw)
        payload = dict(e.payload)
        if e.action == JOURNAL_ANCHORED and payload.get("store_id") == store_id and int(payload.get("sequence", -1)) == sequence:
            payload["head_digest"] = head_digest
        payload_hash = hash_of(payload)
        digest = AuditEvent.compute_hash(
            e.seq, e.event_id, e.ts, e.correlation_id, e.tenant, e.account, e.actor, e.action, payload_hash, prev
        )
        updates[(AUDIT_EVENTS_TABLE, str(key))] = e.model_copy(
            update={"payload": payload, "payload_hash": payload_hash, "prev_hash": prev, "hash": digest}
        ).model_dump_json()
        prev = digest
    _rewrite_rows_consistently(db, updates)


@pytest.mark.tc("TC-DUR-005")
@pytest.mark.req("NFR-CON-01")
@pytest.mark.env("dev")
@pytest.mark.quartet("positive")
def test_journal_head_is_anchored_into_the_audit_chain_and_verifies_across_a_restart(tmp_path):  # type: ignore[no-untyped-def]
    """Every commit that touches a control invariant writes the control store's journal head into the audit chain as a correlated `store.journal.anchored` row; the row is covered by the chain hashes and, once sealed, by the external anchor; a restart verifies its head against it."""
    store_dir, anchor_dir = tmp_path / "state", tmp_path / "worm-replica"
    p1 = build_sim_platform(store_dir=store_dir, anchor_dir=anchor_dir, authorisation_key=KEY)
    anchor = p1.journal_anchor
    assert anchor is not None and anchor.store_id == p1.store.store_id
    genesis = _anchored_rows(p1.audit, anchor.store_id)
    assert genesis and genesis[0].payload["sequence"] == 0  # an empty journal is witnessed at 0: "no anchor" is never "nothing yet"

    r = p1.run_intent(p1.make_intent())  # writes execution.by_decision, execution.consumed_authorisations and the lease
    assert r.order.state == OrderState.FILLED
    act = p1.killswitch.activate(KillSwitchLevel.STRATEGY, STRATEGY, reason="drill", actor=SRE, now=p1.now)
    head = p1.store.journal_head()
    assert head is not None and head.store_id == anchor.store_id and head.sequence > 0

    rows = _anchored_rows(p1.audit, anchor.store_id)
    assert len(rows) > len(genesis)  # control-table commits are anchored, not only the open
    assert rows[-1].payload["sequence"] == head.sequence and rows[-1].payload["head_digest"] == head.digest
    assert all(e.correlation_id for e in rows) and all(e.actor == "control_store" for e in rows)
    assert any("killswitch.activations" in e.payload["tables"] for e in rows)
    assert r.validated_intent.correlation_id in {e.correlation_id for e in rows}  # the business correlation, not a synthetic one
    check = anchor.check()
    assert check.ok and check.witnessed_sequence == head.sequence and check.lag == 0

    # the anchored row is covered by the audit chain's own hashes and, once sealed, by the external anchor
    assert p1.audit.verify(published=False).ok
    sealed = p1.audit.seal(correlation_id="seal:operator:1")
    latest = p1.audit.latest_anchor()
    assert latest is not None and latest.length == sealed.length and sealed.length > rows[-1].seq
    assert p1.audit.verify().ok and anchor.verify(with_witness=True).ok
    p1.audit.close()
    p1.store.close()

    p2 = build_sim_platform(store_dir=store_dir, anchor_dir=anchor_dir, authorisation_key=KEY)  # restart
    assert p2.journal_anchor is not None and p2.journal_anchor.check().ok
    assert p2.store.journal_head().sequence >= head.sequence
    assert p2.killswitch.get(act.activation_id).active
    witnessed = p2.journal_anchor.last_witnessed()
    assert witnessed is not None and witnessed.sequence >= head.sequence
    assert p2.audit.verify().ok and p2.journal_anchor.verify(with_witness=True).ok
    assert not p2.alerts.by_name(STORE_JOURNAL_ALERT)
    # the in-memory default is unchanged: nothing durable to tamper with offline, so no anchor and no anchored rows
    mem = build_sim_platform()
    assert mem.journal_anchor is None and mem.store.journal_head() is None and mem.audit.by_action(JOURNAL_ANCHORED) == ()


@pytest.mark.tc("TC-DUR-006")
@pytest.mark.req("NFR-CON-01")
@pytest.mark.env("dev")
@pytest.mark.quartet("negative")
def test_consistently_rolled_back_control_store_is_refused_because_the_chain_remembers_a_later_head(tmp_path):  # type: ignore[no-untyped-def]
    """A control store rolled back to an earlier *internally consistent* state satisfies its own row digests and journal replay and is still refused, because the audit chain witnessed a later journal head: STORE-JOURNAL-ROLLBACK, one catalogued S1 alert, one durable incident row."""
    store_dir, anchor_dir = tmp_path / "state", tmp_path / "worm-replica"
    p1 = build_sim_platform(store_dir=store_dir, anchor_dir=anchor_dir, authorisation_key=KEY)
    p1.run_intent(p1.make_intent())
    act = p1.killswitch.activate(KillSwitchLevel.ACCOUNT, ACCOUNT, reason="drill", actor=RISK_OFFICER, now=p1.now)
    witnessed = p1.journal_anchor.last_witnessed()
    assert witnessed is not None and witnessed.sequence == p1.store.journal_head().sequence
    p1.audit.seal(correlation_id="seal:operator:1")  # the witnessed head is under the external anchor too
    p1.audit.close()
    p1.store.close()

    db = _db(store_dir)
    (cut,) = db.execute("SELECT MIN(seq) FROM journal WHERE tbl='killswitch.activations' AND key=?", (act.activation_id,)).fetchone()
    _rollback_consistently(db, int(cut) - 1)  # roll the whole store back to before the switch was engaged
    db.close()
    rolled = SqliteStore(store_dir / STORE_FILENAME)
    rolled.verify()  # ADR-018's own evidence is satisfied: rows, digests and journal replay all agree...
    assert rolled.get("killswitch.activations", act.activation_id) is None  # ...and the engaged switch is simply gone
    assert rolled.journal_head().sequence < witnessed.sequence
    rolled.close()

    with pytest.raises(StoreIntegrityError) as exc:  # ...but the audit chain remembers a later head
        build_sim_platform(store_dir=store_dir, anchor_dir=anchor_dir, authorisation_key=KEY)
    assert JOURNAL_ROLLBACK in str(exc.value) and str(witnessed.sequence) in str(exc.value)

    # the refusal is a durable audit row, written exactly once, and the alert is catalogued S1 with no auto write-back
    audit = AuditStore(store=SqliteStore(store_dir / AUDIT_STORE_FILENAME))
    incidents = [e for e in audit.by_action(JOURNAL_INCIDENT) if e.payload["store_id"] == witnessed.store_id]
    assert len(incidents) == 1 and incidents[0].payload["reason"] == JOURNAL_ROLLBACK and incidents[0].correlation_id
    assert incidents[0].payload["witnessed_sequence"] == witnessed.sequence
    audit.close()
    sink = build_sim_platform()  # a real AlertRouter over observability/alerts.yaml: the alert must be catalogued
    store = SqliteStore(store_dir / STORE_FILENAME)
    replay = AuditStore(store=SqliteStore(store_dir / AUDIT_STORE_FILENAME))
    with pytest.raises(StoreIntegrityError):
        JournalAnchor(store, AuditJournalWitness(replay), alerts=sink.alerts.raise_alert).verify()
    alert = sink.alerts.by_name(STORE_JOURNAL_ALERT)[-1]
    assert alert.severity == "S1" and alert.auto_action == "none"  # never an automatic write to a store under investigation
    assert alert.payload["reason"] == JOURNAL_ROLLBACK and alert.payload["correlation_id"] == incidents[0].correlation_id
    assert alert.payload["sequence"] < alert.payload["witnessed_sequence"]
    assert len([e for e in replay.by_action(JOURNAL_INCIDENT) if e.payload["store_id"] == witnessed.store_id]) == 1
    store.close()
    replay.close()
    # a fresh, empty control store put in place of the rolled-back one is refused too: sequence 0 against a witnessed head
    for f in store_dir.glob(f"{STORE_FILENAME}*"):
        f.unlink()
    with pytest.raises(StoreIntegrityError) as exc2:
        build_sim_platform(store_dir=store_dir, anchor_dir=anchor_dir, authorisation_key=KEY)
    assert JOURNAL_ROLLBACK in str(exc2.value) or JOURNAL_UNWITNESSED in str(exc2.value)


@pytest.mark.tc("TC-DUR-007")
@pytest.mark.req("NFR-CON-01")
@pytest.mark.env("dev")
@pytest.mark.quartet("abuse")
def test_consistent_rewrite_must_also_rewrite_the_audit_chain_and_that_breaks_the_chain_or_its_anchor(tmp_path):  # type: ignore[no-untyped-def]
    """The composition end to end: an attacker rewrites the control store's rows *and* journal consistently (the attack ADR-018 admits) and the anchored head exposes it; rewriting the audit row too is refused by the seam and then by the audit chain; rewriting the whole audit chain consistently is refused by the external anchor, which the audit process does not own."""
    store_dir, anchor_dir = tmp_path / "state", tmp_path / "worm-replica"
    p1 = build_sim_platform(store_dir=store_dir, anchor_dir=anchor_dir, authorisation_key=KEY)
    p1.run_intent(p1.make_intent())
    act = p1.killswitch.activate(KillSwitchLevel.ACCOUNT, ACCOUNT, reason="drill", actor=RISK_OFFICER, now=p1.now)
    witnessed = p1.journal_anchor.last_witnessed()
    p1.audit.seal(correlation_id="seal:operator:1")
    assert p1.audit.verify().ok
    p1.audit.close()
    p1.store.close()

    # (a) the attack ADR-018 admits: flip the engaged switch off and re-compute every unkeyed digest in the control store
    db = _db(store_dir)
    (raw,) = db.execute("SELECT value FROM kv WHERE tbl='killswitch.activations' AND key=?", (act.activation_id,)).fetchone()
    doc = json.loads(raw)
    doc["active"] = False
    _rewrite_consistently(db, "killswitch.activations", act.activation_id, json.dumps(doc))
    db.close()
    forged = SqliteStore(store_dir / STORE_FILENAME)
    forged.verify()  # the seam is satisfied: this is exactly what ADR-018 says it cannot see
    assert json.loads(forged.get("killswitch.activations", act.activation_id))["active"] is False
    forged_head = forged.journal_head()
    assert forged_head.sequence == witnessed.sequence and forged_head.digest != witnessed.digest
    forged.close()
    with pytest.raises(StoreIntegrityError) as exc:  # the anchored head disagrees at a sequence the chain does record
        build_sim_platform(store_dir=store_dir, anchor_dir=anchor_dir, authorisation_key=KEY)
    assert JOURNAL_FORK in str(exc.value)

    # (b) so the attacker must also rewrite the audit row that carries the head. Editing it alone is refused by the seam.
    adb = _audit_db(store_dir)
    key, raw = next(
        (str(k), v)
        for k, v in adb.execute("SELECT key, value FROM kv WHERE tbl=? ORDER BY key", (AUDIT_EVENTS_TABLE,)).fetchall()
        if json.loads(v)["action"] == JOURNAL_ANCHORED and json.loads(v)["payload"].get("sequence") == witnessed.sequence
    )
    edited = json.loads(raw)
    edited["payload"] = {**edited["payload"], "head_digest": forged_head.digest}
    adb.execute("UPDATE kv SET value=? WHERE tbl=? AND key=?", (json.dumps(edited), AUDIT_EVENTS_TABLE, key))
    with pytest.raises(StoreIntegrityError):
        build_sim_platform(store_dir=store_dir, anchor_dir=anchor_dir, authorisation_key=KEY)
    # (c) with every seam digest re-computed, the audit chain itself refuses it (payload_hash, event hash, prev_hash)
    _rewrite_consistently(adb, AUDIT_EVENTS_TABLE, key, json.dumps(edited))
    SqliteStore(store_dir / AUDIT_STORE_FILENAME).close()  # the audit seam is satisfied
    with pytest.raises(AuditIntegrityError):
        AuditStore(store=SqliteStore(store_dir / AUDIT_STORE_FILENAME))
    with pytest.raises(AuditIntegrityError):
        build_sim_platform(store_dir=store_dir, anchor_dir=anchor_dir, authorisation_key=KEY)

    # (d) the complete attack: re-compute the whole audit chain from genesis so that both stores agree with each other
    _forge_audit_chain(adb, witnessed.store_id, witnessed.sequence, forged_head.digest)
    adb.close()
    SqliteStore(store_dir / AUDIT_STORE_FILENAME).close()
    control = SqliteStore(store_dir / STORE_FILENAME)
    audit = AuditStore(store=SqliteStore(store_dir / AUDIT_STORE_FILENAME))  # the audit chain now verifies on its own terms
    assert audit.verify(published=False).ok
    anchor = JournalAnchor(control, AuditJournalWitness(audit))
    assert anchor.check().ok  # head and witness agree: each half, taken alone, is satisfied
    # ...and the composition is not: the head the witness now carries is not the head the external principal published
    published = audit.verify()
    assert not published.ok and published.reason == "AUD-CHAIN-HEAD-MISMATCH"
    composed = anchor.check_witness()
    assert not composed.ok and composed.reason == JOURNAL_WITNESS_UNTRUSTED and "AUD-CHAIN-HEAD-MISMATCH" in composed.detail
    with pytest.raises(StoreIntegrityError):
        anchor.verify(with_witness=True)
    control.close()
    audit.close()
    # Rewriting the anchor file instead is refused by the anchor chain and by the publisher (TC-AUD-008). The attacker
    # now needs write access to two stores owned by two principals: the property D-061 (5) bought without a new secret.


@pytest.mark.tc("TC-DUR-008")
@pytest.mark.req("NFR-CON-01")
@pytest.mark.env("dev")
@pytest.mark.quartet("recovery")
def test_restore_from_a_backup_consistent_with_the_witnessed_head_verifies_and_the_incident_is_audited_once(tmp_path):  # type: ignore[no-untyped-def]
    """After the operator restores the control store from a backup consistent with the witnessed head, verification passes; the refusal and the recovery are two audit rows under one correlation id, no second incident is opened in between, and a restart sees both."""
    store_dir, anchor_dir = tmp_path / "state", tmp_path / "worm-replica"
    p1 = build_sim_platform(store_dir=store_dir, anchor_dir=anchor_dir, authorisation_key=KEY)
    p1.run_intent(p1.make_intent())
    act = p1.killswitch.activate(KillSwitchLevel.ACCOUNT, ACCOUNT, reason="drill", actor=RISK_OFFICER, now=p1.now)
    witnessed = p1.journal_anchor.last_witnessed()
    p1.audit.seal(correlation_id="seal:operator:1")
    p1.audit.close()
    p1.store.close()
    backup = _control_backup(store_dir, tmp_path / "last-good-backup")  # taken at the witnessed head

    db = _db(store_dir)
    (cut,) = db.execute("SELECT MIN(seq) FROM journal WHERE tbl='killswitch.activations' AND key=?", (act.activation_id,)).fetchone()
    _rollback_consistently(db, int(cut) - 1)
    db.close()
    with pytest.raises(StoreIntegrityError):
        build_sim_platform(store_dir=store_dir, anchor_dir=anchor_dir, authorisation_key=KEY)
    with pytest.raises(StoreIntegrityError):  # a second attempt re-alerts and re-refuses; it opens no second incident
        build_sim_platform(store_dir=store_dir, anchor_dir=anchor_dir, authorisation_key=KEY)
    audit = AuditStore(store=SqliteStore(store_dir / AUDIT_STORE_FILENAME))
    incidents = [e for e in audit.by_action(JOURNAL_INCIDENT) if e.payload["store_id"] == witnessed.store_id]
    assert len(incidents) == 1 and not audit.by_action(JOURNAL_RECOVERED)
    corr = incidents[0].correlation_id
    audit.close()

    _restore_control(backup, store_dir)  # the operator restores the backup that matches the witnessed head
    p2 = build_sim_platform(store_dir=store_dir, anchor_dir=anchor_dir, authorisation_key=KEY)
    assert p2.journal_anchor.check().ok
    assert p2.killswitch.get(act.activation_id).active  # the engaged switch is back
    rows = p2.audit.by_correlation(corr)
    assert [e.action for e in rows] == [JOURNAL_INCIDENT, JOURNAL_RECOVERED]
    assert all(e.correlation_id == corr and e.actor == "control_store" for e in rows)
    assert rows[1].payload["incident_reason"] == JOURNAL_ROLLBACK and rows[1].payload["store_id"] == witnessed.store_id
    sealed = p2.audit.seal(correlation_id=corr)  # the incident and its recovery are now under the external anchor
    latest = p2.audit.latest_anchor()
    assert latest is not None and latest.length == sealed.length and latest.correlation_id == corr
    assert p2.audit.verify().ok and p2.journal_anchor.verify(with_witness=True).ok
    p2.audit.close()
    p2.store.close()

    p3 = build_sim_platform(store_dir=store_dir, anchor_dir=anchor_dir, authorisation_key=KEY)  # a restart sees both rows
    assert [e.action for e in p3.audit.by_correlation(corr)] == [JOURNAL_INCIDENT, JOURNAL_RECOVERED]
    assert p3.journal_anchor.check().ok and not p3.alerts.by_name(STORE_JOURNAL_ALERT)
