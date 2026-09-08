"""TC-AUD — Immutable audit [Source: 03, 06; NFR-AUD-01; T-12]."""

from __future__ import annotations

import json
import shutil
import sqlite3
from pathlib import Path

import pytest
from audit_service.anchor import ANCHOR_FILENAME, AnchorError, AnchorRecord, FileAnchorPublisher
from audit_service.reestablish import inspect_chain, reestablish_witness
from audit_service.store import (
    ANCHOR_PUBLISHED,
    AUDIT_EVENTS_TABLE,
    AUDIT_SEALS_TABLE,
    AUDIT_SEQUENCE,
    WITNESS_REESTABLISHED,
    AuditEvent,
    AuditIntegrityError,
    AuditStore,
    ChainHead,
    SealRefused,
    WitnessAttestation,
    WitnessLostError,
)
from conftest import ACCOUNT, AUDITOR, RISK_OFFICER, TENANT
from killswitch_service.service import KillSwitchLevel
from rtcore.resources import resource_root
from rtcore.store import GENESIS, SEQUENCE_TABLE, SqliteStore, StoreError, StoreIntegrityError, journal_digest, row_digest
from rtobs.alerts import Alert, AlertRouter
from web_bff.platform import AUDIT_STORE_FILENAME, STORE_FILENAME, TENANT_B, build_sim_platform

KEY = b"sim-only-command-authorisation-key-32b!!"  # composition-root key (models the vault path); no AI/MCP component receives it


@pytest.mark.tc("TC-AUD-001")
@pytest.mark.req("NFR-AUD-01")
@pytest.mark.quartet("positive")
def test_every_decision_and_transition_is_audited_with_correlation_id(platform):  # type: ignore[no-untyped-def]
    """One correlation ID links intent, eligibility, risk decision, order command, ack and fill in the audit chain."""
    r = platform.run_intent(platform.make_intent())
    events = platform.audit.by_correlation(r.validated_intent.correlation_id)
    actions = [e.action for e in events]
    for expected in (
        "intent.state",
        "eligibility.decided.v1",
        "risk.decided.v1",
        "order.command.v1",
        "order.submitted.v1",
        "order.acked.v1",
        "order.filled.v1",
    ):
        assert expected in actions, actions
    assert platform.audit.verify().ok and all(e.payload_hash for e in events)


@pytest.mark.tc("TC-AUD-002")
@pytest.mark.req("NFR-AUD-01")
@pytest.mark.quartet("negative")
def test_no_update_or_delete_api_exists():  # type: ignore[no-untyped-def]
    """The audit store exposes no mutation path other than append."""
    store = AuditStore()
    assert not any(hasattr(store, n) for n in ("delete", "update", "remove", "truncate", "clear", "pop"))
    store.append(correlation_id="c", tenant="t", actor="a", action="x", payload={"k": 1})
    assert len(store) == 1 and store.verify().ok


@pytest.mark.tc("TC-AUD-003")
@pytest.mark.req("NFR-AUD-01")
@pytest.mark.quartet("abuse")
def test_tampering_detected_by_hash_chain(platform):  # type: ignore[no-untyped-def]
    """Modifying, replacing or removing a stored event breaks the chain and verification reports the first bad sequence."""
    platform.run_intent(platform.make_intent())
    events = list(platform.audit.all())
    idx = 3
    tampered = events[idx].model_copy(update={"payload": {**events[idx].payload, "outcome": "APPROVED-forged"}})
    forged = events[:idx] + [tampered] + events[idx + 1 :]
    v = platform.audit.verify(forged)
    assert not v.ok and v.first_bad_seq == idx and v.detail == "payload tampered"
    removed = events[:idx] + events[idx + 1 :]
    assert not platform.audit.verify(removed).ok
    rehashed = tampered.model_copy(update={"payload_hash": __import__("rtcore.ids", fromlist=["hash_of"]).hash_of(tampered.payload)})
    v2 = platform.audit.verify(events[:idx] + [rehashed] + events[idx + 1 :])
    assert not v2.ok and v2.detail == "hash mismatch"


@pytest.mark.tc("TC-AUD-004")
@pytest.mark.req("NFR-AUD-01")
@pytest.mark.quartet("recovery")
def test_export_reload_and_file_backed_worm(platform, tmp_path):  # type: ignore[no-untyped-def]
    """Exported chain re-loads into a fresh store and verifies; file backend is append-only and survives restart."""
    platform.run_intent(platform.make_intent())
    exported = platform.audit.export()
    reloaded = [AuditEvent.model_validate_json(line) for line in exported.splitlines()]
    assert AuditStore().verify(reloaded).ok and len(reloaded) == len(platform.audit)
    path = tmp_path / "audit.jsonl"
    s1 = AuditStore(path)
    s1.append(correlation_id="c1", tenant="t", actor="a", action="one", payload={"n": 1})
    s1.append(correlation_id="c1", tenant="t", actor="a", action="two", payload={"n": 2})
    s2 = AuditStore(path)
    assert len(s2) == 2 and s2.verify().ok and s2.head_hash() == s1.head_hash()
    s2.append(correlation_id="c1", tenant="t", actor="a", action="three", payload={"n": 3})
    assert AuditStore(path).verify().ok and len(AuditStore(path)) == 3
    assert AUDITOR.role.value == "auditor" and platform.audit.export("nonexistent") == ""


@pytest.mark.tc("TC-AUD-005")
@pytest.mark.req("NFR-AUD-01")
@pytest.mark.quartet("abuse")
def test_truncation_detected_with_sealed_anchor_and_backdating_refused(platform):  # type: ignore[no-untyped-def]
    """A truncated tail verifies as a valid prefix without an anchor; with the sealed head it is detected; timestamps are monotonic (Security review OBJ-3)."""
    from datetime import timedelta

    platform.run_intent(platform.make_intent())
    anchor = platform.audit.seal()
    events = list(platform.audit.all())
    truncated = events[:-5]
    assert platform.audit.verify(truncated).ok  # prefix is internally consistent...
    v = platform.audit.verify(truncated, anchor=anchor)
    assert not v.ok and "truncated" in v.detail  # ...but the anchor exposes it
    assert platform.audit.verify(anchor=anchor).ok
    e = platform.audit.append(correlation_id="c", tenant="t", actor="a", action="x", payload={}, ts=platform.now - timedelta(days=1))
    assert e.ts >= events[-1].ts


# --- durable audit store on the rtcore.store seam and external anchoring (B-5, D-058; ADR-020 proposed; R-31, O-54) ---------
# The four tests below extend the AUD quartet: events, seals and anchors must survive a rebuild from ``store_dir``; a
# truncated tail, a stale or missing anchor, an edited SQLite row and an edited anchor file must all fail closed; the
# anchor publisher never holds a path that can write or delete audit events; a corrupt anchor directory is recovered
# from the last good copy and the incident is audited with a correlation_id.


def _dirs(tmp_path: Path) -> tuple[Path, Path]:
    """The control/audit store directory and a physically separate anchor directory (the WORM/replica written by a different principal)."""
    return tmp_path / "state", tmp_path / "worm-replica"


def _audit_db(store_dir: Path) -> sqlite3.Connection:
    return sqlite3.connect(store_dir / AUDIT_STORE_FILENAME, isolation_level=None)


def _rewrite_consistently(db: sqlite3.Connection, table: str, key: str, new_value: str) -> None:
    """The strongest offline attacker (O-110): rewrites a row *and* re-computes every unkeyed digest so the store seam is satisfied.

    Only the audit hash chain (payload_hash, event hash, prev_hash) and the external anchor are left to catch it.
    """
    rows = db.execute("SELECT seq, op, tbl, key, value, correlation_id, at FROM journal ORDER BY seq").fetchall()
    prev = GENESIS
    for seq, op, tbl, k, value, corr, at in rows:
        if tbl == table and k == key and op == "put":
            value = new_value
        digest = journal_digest(prev, int(seq), op, tbl, k, value, corr, at)
        db.execute("UPDATE journal SET value=?, prev=?, digest=? WHERE seq=?", (value, prev, digest, seq))
        prev = digest
    (seq,) = db.execute("SELECT seq FROM kv WHERE tbl=? AND key=?", (table, key)).fetchone()
    db.execute(
        "UPDATE kv SET value=?, digest=? WHERE tbl=? AND key=?", (new_value, row_digest(table, key, new_value, int(seq)), table, key)
    )


def _rollback_consistently(db: sqlite3.Connection, keep_upto_seq: int) -> None:
    """Roll the whole store back to journal seq ``keep_upto_seq`` and rebuild the state rows so ``SqliteStore.verify()`` passes:
    a tail truncation that the seam cannot see and only an external witness exposes.

    Rows the truncated tail had deleted are re-created, not merely re-valued, so the attacker models a *complete*
    restore of an earlier state (a released lease is back, a revoked grant is back) rather than a partial one
    [Committee: O-128 quartet, TC-DUR-006/008]."""
    db.execute("DELETE FROM journal WHERE seq > ?", (keep_upto_seq,))
    expected: dict[tuple[str, str], tuple[str, int, int]] = {}  # (value, seq, created_seq)
    for seq, op, tbl, k, value in db.execute("SELECT seq, op, tbl, key, value FROM journal ORDER BY seq").fetchall():
        if op == "put":
            created = expected[(tbl, k)][2] if (tbl, k) in expected else int(seq)
            expected[(tbl, k)] = (value, int(seq), created)
        else:
            expected.pop((tbl, k), None)
    for tbl, k in db.execute("SELECT tbl, key FROM kv").fetchall():
        if (tbl, k) not in expected:
            db.execute("DELETE FROM kv WHERE tbl=? AND key=?", (tbl, k))
    for (tbl, k), (value, seq, created) in expected.items():
        db.execute(
            "INSERT OR REPLACE INTO kv (tbl, key, value, created_seq, seq, digest) VALUES (?, ?, ?, ?, ?, ?)",
            (tbl, k, value, created, seq, row_digest(tbl, k, value, seq)),
        )


@pytest.mark.tc("TC-AUD-006")
@pytest.mark.req("NFR-AUD-01")
@pytest.mark.quartet("positive")
def test_events_seals_and_anchors_survive_rebuild_and_verify_against_published_anchor(tmp_path):  # type: ignore[no-untyped-def]
    """Events, seals and published anchors written by one process are read back by a platform rebuilt from store_dir; verify against the published anchor passes; the tenant filter still applies."""
    store_dir, anchor_dir = _dirs(tmp_path)
    p1 = build_sim_platform(store_dir=store_dir, anchor_dir=anchor_dir, authorisation_key=KEY)
    assert p1.audit.backend == "SqliteStore" and (store_dir / AUDIT_STORE_FILENAME).exists()
    r = p1.run_intent(p1.make_intent())
    corr = r.validated_intent.correlation_id
    head = p1.audit.seal(correlation_id="seal:operator:1")  # explicit seal publishes immediately
    events, n, head_hash = p1.audit.all(), len(p1.audit), p1.audit.head_hash()
    assert head.length == n and head.head_hash == head_hash
    latest = p1.audit.latest_anchor()
    assert latest is not None and latest.head_hash == head_hash and latest.length == n and latest.correlation_id == "seal:operator:1"
    assert (anchor_dir / ANCHOR_FILENAME).exists() and not (store_dir / ANCHOR_FILENAME).exists()  # anchors live only off-box
    assert p1.audit.verify().ok and p1.audit.verify(anchor=head).ok
    p1.audit.close()
    p1.store.close()

    p2 = build_sim_platform(store_dir=store_dir, anchor_dir=anchor_dir, authorisation_key=KEY)  # restart
    assert p2.audit.backend == "SqliteStore" and len(p2.audit) > n  # composition appended its own rows after the restart
    assert p2.audit.all()[:n] == events and p2.audit.all()[n - 1].hash == head_hash
    assert p2.audit.seals()[-1].head == head  # persisted seal
    latest2 = p2.audit.latest_anchor()
    assert latest2 is not None and latest2.length >= n  # scheduled publication kept going
    v = p2.audit.verify()  # against the latest published anchor by default
    assert v.ok and v.length == len(p2.audit) and v.anchor_length is not None
    assert p2.audit.verify(anchor=head).ok
    # tenant-partitioned reads survive the rebuild: the intent's rows belong to the sim tenant only
    assert p2.audit.by_correlation(corr, tenant=TENANT) == p1.audit.by_correlation(corr, tenant=TENANT)
    assert p2.audit.by_correlation(corr, tenant=TENANT_B) == () and p2.audit.export(corr, tenant=TENANT_B) == ""
    assert all(e.correlation_id for e in p2.audit.all())
    assert not p2.alerts.by_name("audit.anchor_missing") and not p2.alerts.by_name("audit.chain_verification_failed")
    # the memory default is unchanged: no file, no publisher, verify() without an anchor as before
    mem = build_sim_platform()
    assert mem.audit.backend == "MemoryStore" and mem.audit.latest_anchor() is None and mem.audit.verify().ok


@pytest.mark.tc("TC-AUD-007")
@pytest.mark.req("NFR-AUD-01")
@pytest.mark.quartet("negative")
def test_truncated_tail_stale_and_missing_anchor_fail_closed(tmp_path):  # type: ignore[no-untyped-def]
    """A store rolled back consistently (seam satisfied) fails verify against the published anchor; an anchor older than the configured lag or absent fails closed with S1 audit.anchor_missing."""
    store_dir, anchor_dir = _dirs(tmp_path)
    p1 = build_sim_platform(store_dir=store_dir, anchor_dir=anchor_dir, authorisation_key=KEY)
    p1.run_intent(p1.make_intent())
    sealed = p1.audit.seal(correlation_id="seal:operator:1")
    p1.audit.close()
    p1.store.close()
    db = _audit_db(store_dir)
    keys = [k for (k,) in db.execute("SELECT key FROM kv WHERE tbl=? ORDER BY key", (AUDIT_EVENTS_TABLE,)).fetchall()]
    (cut,) = db.execute("SELECT MIN(seq) FROM journal WHERE tbl=? AND key=?", (AUDIT_EVENTS_TABLE, keys[-5])).fetchone()
    _rollback_consistently(db, int(cut) - 2)  # the event row and the sequence bump that preceded it
    db.close()
    SqliteStore(store_dir / AUDIT_STORE_FILENAME).close()  # the seam is satisfied: the rollback is invisible to it
    bare = AuditStore(store=SqliteStore(store_dir / AUDIT_STORE_FILENAME), publisher=FileAnchorPublisher(anchor_dir))
    assert len(bare) == sealed.length - 5 and bare.verify(published=False).ok  # a valid prefix on its own...
    v = bare.verify()
    assert not v.ok and v.reason == "AUD-CHAIN-TRUNCATED" and "truncated" in v.detail and v.anchor_length == sealed.length
    bare.close()
    # ...and through a rebuilt platform: composition rows land on the truncated prefix, the sealed head no longer matches,
    # the S1 alert fires and its catalogued auto-action engages the platform Kill Switch
    p2 = build_sim_platform(store_dir=store_dir, anchor_dir=anchor_dir, authorisation_key=KEY)
    v2 = p2.audit.verify()
    assert not v2.ok and v2.reason == "AUD-CHAIN-HEAD-MISMATCH"
    alert = p2.alerts.by_name("audit.chain_verification_failed")[-1]
    assert alert.severity == "S1" and alert.payload["correlation_id"] and alert.payload["reason"] == v2.reason
    assert any(a.level.value == "PLATFORM" for a in p2.killswitch.active())
    assert p2.broker.submissions_received == 0
    p2.audit.close()
    p2.store.close()

    # stale anchor: explicit-only publication with a lag ceiling of 10 events; one intent run is 15 rows past the genesis anchor
    store3, anchor3 = tmp_path / "state3", tmp_path / "worm3"
    p3 = build_sim_platform(store_dir=store3, anchor_dir=anchor3, authorisation_key=KEY, anchor_every=0, max_anchor_lag=10)
    genesis = p3.audit.latest_anchor()
    assert genesis is not None and genesis.length == 0
    v3 = p3.audit.verify()
    assert not v3.ok and v3.reason == "AUD-ANCHOR-STALE" and v3.lag is not None and v3.lag > 10
    alert = p3.alerts.by_name("audit.anchor_missing")[-1]
    assert alert.severity == "S1" and alert.auto_action == "none"
    assert alert.payload["reason"] == "AUD-ANCHOR-STALE" and alert.payload["lag"] == v3.lag and alert.payload["max_lag"] == 10
    assert alert.payload["correlation_id"]
    assert p3.audit.verify(published=False).ok  # the chain itself is intact: only the anchor is stale
    p3.audit.seal(correlation_id="seal:operator:2")  # an explicit seal publishes and clears the staleness
    assert p3.audit.verify().ok
    # missing anchor: the anchor file disappears (replica lost) -> fail closed, never re-anchored silently
    (anchor3 / ANCHOR_FILENAME).unlink()
    v4 = p3.audit.verify()
    assert not v4.ok and v4.reason == "AUD-ANCHOR-MISSING" and p3.audit.latest_anchor() is None
    assert p3.alerts.by_name("audit.anchor_missing")[-1].payload["reason"] == "AUD-ANCHOR-MISSING"
    p3.audit.close()
    p3.store.close()
    # a restart with events and no anchor never fabricated one, and since ADR-020 amendment 3 it does not even open:
    # a platform whose own records name a witness that is gone is refused (TC-AUD-016/017 are the quartet for it).
    # This assertion is strictly stronger than the one it replaces ("started, and verify() said no").
    with pytest.raises(WitnessLostError):
        build_sim_platform(store_dir=store3, anchor_dir=anchor3, authorisation_key=KEY)
    assert FileAnchorPublisher(anchor3).latest() is None  # and nothing fabricated an anchor on the way out


@pytest.mark.tc("TC-AUD-008")
@pytest.mark.req("NFR-AUD-01")
@pytest.mark.quartet("abuse")
def test_edited_row_refused_anchor_tamper_detected_and_publisher_has_no_audit_write_path(tmp_path):  # type: ignore[no-untyped-def]
    """An edited event row in the SQLite file is refused (seam digest, then the audit chain even after a consistent digest rewrite); an edited or shortened anchor file breaks the anchor chain; the publisher's handle and the publisher expose no method that writes or deletes audit events."""
    store_dir, anchor_dir = _dirs(tmp_path)
    p1 = build_sim_platform(store_dir=store_dir, anchor_dir=anchor_dir, authorisation_key=KEY)
    p1.run_intent(p1.make_intent())
    p1.audit.seal(correlation_id="seal:operator:1")
    p1.audit.seal(correlation_id="seal:operator:2")
    # (c) capability inspection: the handle the publisher may hold and the publisher itself carry no audit write or delete path
    handle = p1.audit.anchor_handle()
    forbidden = {"append", "put", "delete", "update", "remove", "truncate", "clear", "pop", "seal", "subscribe"}
    assert {n for n in dir(handle) if not n.startswith("_")} == {"head", "length"}
    assert not any(isinstance(v, AuditStore) or hasattr(v, "put") or hasattr(v, "delete") for v in vars(handle).values())
    assert isinstance(handle.head(), ChainHead) and handle.length == len(p1.audit)
    publisher = p1.audit.publisher
    assert isinstance(publisher, FileAnchorPublisher)
    assert not ({n for n in dir(publisher) if not n.startswith("_")} & forbidden)
    assert not any(isinstance(v, AuditStore) or hasattr(v, "put") for v in vars(publisher).values())
    assert not any(hasattr(p1.audit, n) for n in ("delete", "update", "remove", "truncate", "clear", "pop"))  # TC-AUD-002 still holds
    # a rollback anchor (shorter than the latest) is refused by the publisher, whoever asks
    with pytest.raises(AnchorError):
        publisher.publish(ChainHead(length=1, head_hash="00" * 32, sealed_at=p1.now), correlation_id="attacker")
    with pytest.raises(AnchorError):  # a fork at the same length is refused too
        publisher.publish(ChainHead(length=len(p1.audit), head_hash="11" * 32, sealed_at=p1.now), correlation_id="attacker")
    p1.audit.close()
    p1.store.close()

    # (a) edit an event row in the SQLite file: the seam refuses the store at open (row digest / journal replay)
    db = _audit_db(store_dir)
    keys = [k for (k,) in db.execute("SELECT key FROM kv WHERE tbl=? ORDER BY key", (AUDIT_EVENTS_TABLE,)).fetchall()]
    (raw,) = db.execute("SELECT value FROM kv WHERE tbl=? AND key=?", (AUDIT_EVENTS_TABLE, keys[3])).fetchone()
    doc = json.loads(raw)
    doc["payload"] = {**doc["payload"], "outcome": "APPROVED-forged"}
    db.execute("UPDATE kv SET value=? WHERE tbl=? AND key=?", (json.dumps(doc), AUDIT_EVENTS_TABLE, keys[3]))
    with pytest.raises(StoreIntegrityError):
        build_sim_platform(store_dir=store_dir, anchor_dir=anchor_dir, authorisation_key=KEY)
    # the same edit with every seam digest re-computed (O-110 attacker): the audit hash chain refuses it at open
    _rewrite_consistently(db, AUDIT_EVENTS_TABLE, keys[3], json.dumps(doc))
    SqliteStore(store_dir / AUDIT_STORE_FILENAME).close()  # seam satisfied
    with pytest.raises(AuditIntegrityError) as exc:
        AuditStore(store=SqliteStore(store_dir / AUDIT_STORE_FILENAME))
    assert "payload tampered" in str(exc.value) and "seq 3" in str(exc.value)
    db.close()

    # (b) the anchor file: an edited record or a removed record breaks the anchor chain; a removed tail is caught by the store's seals
    store2, anchor2 = tmp_path / "state2", tmp_path / "worm2"
    p2 = build_sim_platform(store_dir=store2, anchor_dir=anchor2, authorisation_key=KEY)
    p2.run_intent(p2.make_intent())
    p2.audit.seal(correlation_id="seal:operator:1")
    p2.audit.seal(correlation_id="seal:operator:2")
    assert p2.audit.verify().ok
    anchor_file = anchor2 / ANCHOR_FILENAME
    lines = anchor_file.read_text(encoding="utf-8").splitlines()
    assert len(lines) >= 3
    records = [AnchorRecord.model_validate_json(line) for line in lines]
    assert all(r.principal == publisher.principal for r in records) and records[-1].correlation_id == "seal:operator:2"
    edited = records[1].model_copy(update={"head_hash": "22" * 32})
    anchor_file.write_text("\n".join([lines[0], edited.model_dump_json(), *lines[2:]]) + "\n", encoding="utf-8")
    assert not p2.audit.publisher.verify().ok
    v = p2.audit.verify()
    assert not v.ok and v.reason == "AUD-ANCHOR-CHAIN-BROKEN" and p2.alerts.by_name("audit.anchor_missing")
    anchor_file.write_text("\n".join([lines[0], *lines[2:]]) + "\n", encoding="utf-8")  # a record removed from the middle
    assert not p2.audit.verify().ok and p2.audit.verify().reason == "AUD-ANCHOR-CHAIN-BROKEN"
    anchor_file.write_text(
        "\n".join(lines[:-1]) + "\n", encoding="utf-8"
    )  # the last record removed: chain valid, but the store sealed later
    assert p2.audit.publisher.verify().ok
    v = p2.audit.verify()
    assert not v.ok and v.reason == "AUD-ANCHOR-TAIL-REMOVED"
    anchor_file.write_text("\n".join([lines[0], edited.model_dump_json(), *lines[2:]]) + "\n", encoding="utf-8")
    with pytest.raises(AnchorError):  # while the anchor chain is broken, nothing can be published on top of it
        p2.audit.seal(correlation_id="seal:operator:3")


@pytest.mark.tc("TC-AUD-009")
@pytest.mark.req("NFR-AUD-01")
@pytest.mark.quartet("recovery")
def test_corrupt_anchor_directory_restored_from_last_good_copy_and_incident_audited(tmp_path):  # type: ignore[no-untyped-def]
    """After a corrupt anchor directory is replaced by the last good copy, verify passes again; the incident and its recovery are audit rows sharing the alert's correlation_id and are anchored by the next seal; a restart sees them."""
    store_dir, anchor_dir = _dirs(tmp_path)
    p = build_sim_platform(store_dir=store_dir, anchor_dir=anchor_dir, authorisation_key=KEY)
    p.run_intent(p.make_intent())
    p.audit.seal(correlation_id="seal:operator:1")
    assert p.audit.verify().ok
    good = tmp_path / "last-good-copy"
    shutil.copytree(anchor_dir, good)
    n = len(p.audit)
    (anchor_dir / ANCHOR_FILENAME).write_text("garbage\n", encoding="utf-8")  # the replica is corrupt
    v = p.audit.verify()
    assert not v.ok and v.reason == "AUD-ANCHOR-CHAIN-BROKEN"
    alert = p.alerts.by_name("audit.anchor_missing")[-1]
    corr = alert.payload["correlation_id"]
    assert corr and alert.severity == "S1"
    incident = p.audit.by_correlation(corr)
    assert [e.action for e in incident] == ["audit.anchor.incident"] and incident[0].payload["reason"] == "AUD-ANCHOR-CHAIN-BROKEN"
    assert len(p.audit) == n + 1
    assert not p.audit.verify().ok and len(p.audit) == n + 1  # a second failing verify re-alerts but opens no second incident
    assert p.alerts.by_name("audit.anchor_missing")[-1].payload["correlation_id"] == corr
    # recovery: the operator replaces the corrupt directory with the last good copy
    shutil.rmtree(anchor_dir)
    shutil.copytree(good, anchor_dir)
    assert p.audit.publisher.verify().ok
    v2 = p.audit.verify()
    assert v2.ok and v2.anchor_length == n
    rows = p.audit.by_correlation(corr)
    assert [e.action for e in rows] == ["audit.anchor.incident", "audit.anchor.recovered"]
    assert all(e.correlation_id == corr and e.actor == "audit_service" for e in rows)
    assert rows[1].payload["incident_reason"] == "AUD-ANCHOR-CHAIN-BROKEN" and rows[1].payload["anchor_length"] == n
    sealed = p.audit.seal(correlation_id=corr)  # the incident rows are now under a published anchor
    latest = p.audit.latest_anchor()
    assert sealed.length == len(p.audit) and latest is not None and latest.correlation_id == corr and p.audit.verify().ok
    p.audit.close()
    p.store.close()
    p2 = build_sim_platform(store_dir=store_dir, anchor_dir=anchor_dir, authorisation_key=KEY)  # restart after recovery
    assert p2.audit.verify().ok and [e.action for e in p2.audit.by_correlation(corr)] == ["audit.anchor.incident", "audit.anchor.recovered"]
    assert not p2.alerts.by_name("audit.anchor_missing")


# --- the alert path exists before any store is opened, and the witness is verified at start-up ----------------------
# (SRE review F-02 / SRE-R1 and D-066 / O-164; ADR-020 amendment 2). Two integrity checks can refuse this platform:
# the control store replays its journal (ADR-018) and the audit store verifies its chain (ADR-020). Both used to run
# inside the constructors that open the stores, while the alert router was loaded a few lines *later* — so the two
# loudest failures the platform has emitted nothing at all: no S1, no auto-action, no delivery, and the only signal an
# operator got was a process that would not come back. The four tests below are the quartet for the corrected order:
# the router is built first, every open is attempted with the sink in place, the exception still propagates unchanged
# (an alert is a notification, never a licence to continue), and composition additionally asks the *published* witness
# whether it agrees before the platform trades.

STARTUP_ALERTS = ("execution.store_unavailable", "audit.chain_verification_failed", "alert.autoaction_failed")


def _router() -> AlertRouter:
    """A real router over ``observability/alerts.yaml`` — severities and auto-actions come from the catalogue, not the test."""
    return AlertRouter.load(resource_root() / "observability" / "alerts.yaml")


def _channels(router: AlertRouter, alert: Alert) -> list[str]:
    """What the router actually *delivered*, not what it was asked to raise (SRE-R5: delivery is the assertion)."""
    return [ch for ch, a in router.delivered if a is alert]


def _control_db(store_dir: Path) -> sqlite3.Connection:
    return sqlite3.connect(store_dir / STORE_FILENAME, isolation_level=None)


@pytest.mark.tc("TC-AUD-010")
@pytest.mark.req("NFR-AUD-01")
@pytest.mark.env("dev")
@pytest.mark.quartet("positive")
def test_router_is_the_first_thing_built_and_startup_verifies_the_published_witness(tmp_path):  # type: ignore[no-untyped-def]
    """A clean durable start is silent: the router the caller supplies is the router the platform uses, no start-up S1 is raised, and the D-066 published-anchor verification runs at start-up and passes against the anchor a different principal wrote."""
    store_dir, anchor_dir = _dirs(tmp_path)
    router = _router()
    p = build_sim_platform(store_dir=store_dir, anchor_dir=anchor_dir, authorisation_key=KEY, alert_router=router)
    assert p.alerts is router  # the router given to the composition root is the one every component alerts through
    assert not [a for a in router.fired if a.name in STARTUP_ALERTS] and not router.by_name("audit.anchor_missing")
    # D-066: the *published* witness was asked at start-up, not only the cheap journal-head comparison
    sv = p.startup_verification
    assert sv is not None and sv.ok and sv.length == len(p.audit) and sv.anchor_length is not None and sv.lag is not None
    assert p.journal_anchor is not None and p.audit.publisher is not None
    assert p.audit.verify().ok
    p.audit.close()
    p.store.close()
    # a restart is silent too, and the start-up verdict is recomputed rather than remembered
    p2 = build_sim_platform(store_dir=store_dir, anchor_dir=anchor_dir, authorisation_key=KEY)
    assert p2.startup_verification is not None and p2.startup_verification.ok
    assert p2.startup_verification.length == len(p2.audit) and not [a for a in p2.alerts.fired if a.name in STARTUP_ALERTS]
    p2.audit.close()
    p2.store.close()
    # the memory default is unchanged: nothing is published, so there is no published witness to verify against
    mem = build_sim_platform()
    assert mem.startup_verification is None and mem.audit.publisher is None
    assert not [a for a in mem.alerts.fired if a.name in STARTUP_ALERTS]


@pytest.mark.tc("TC-AUD-011")
@pytest.mark.req("NFR-AUD-01")
@pytest.mark.env("dev")
@pytest.mark.quartet("negative")
def test_audit_chain_refused_at_open_emits_its_catalogued_s1_before_the_exception_propagates(tmp_path):  # type: ignore[no-untyped-def]
    """The audit store refuses to open — at the seam, and after a consistent digest rewrite on its own chain — and each refusal raises and *delivers* the catalogued S1 with a correlation id before the exception propagates; the platform still fails closed and never composes."""
    store_dir, anchor_dir = _dirs(tmp_path)
    p1 = build_sim_platform(store_dir=store_dir, anchor_dir=anchor_dir, authorisation_key=KEY)
    p1.run_intent(p1.make_intent())
    p1.audit.seal(correlation_id="seal:operator:1")
    p1.audit.close()
    p1.store.close()

    # (a) an edited audit row: the seam refuses the file. The catalogued alert is the audit chain's own S1 — the
    # evidence store did not open, which is the largest blast radius this platform has.
    db = _audit_db(store_dir)
    keys = [k for (k,) in db.execute("SELECT key FROM kv WHERE tbl=? ORDER BY key", (AUDIT_EVENTS_TABLE,)).fetchall()]
    (raw,) = db.execute("SELECT value FROM kv WHERE tbl=? AND key=?", (AUDIT_EVENTS_TABLE, keys[3])).fetchone()
    doc = json.loads(raw)
    doc["payload"] = {**doc["payload"], "outcome": "APPROVED-forged"}
    db.execute("UPDATE kv SET value=? WHERE tbl=? AND key=?", (json.dumps(doc), AUDIT_EVENTS_TABLE, keys[3]))
    seam_router = _router()
    with pytest.raises(StoreIntegrityError):
        build_sim_platform(store_dir=store_dir, anchor_dir=anchor_dir, authorisation_key=KEY, alert_router=seam_router)
    seam = seam_router.by_name("audit.chain_verification_failed")[-1]
    assert seam.severity == "S1" and seam.payload["reason"] == "STORE-OPEN-REFUSED" and seam.payload["store"] == AUDIT_STORE_FILENAME
    assert seam.payload["correlation_id"] and seam.payload["phase"] == "open" and _channels(seam_router, seam) == ["pager", "email"]

    # (b) the same edit with every seam digest re-computed (the O-110 attacker): the audit chain refuses it at open
    _rewrite_consistently(db, AUDIT_EVENTS_TABLE, keys[3], json.dumps(doc))
    db.close()
    SqliteStore(store_dir / AUDIT_STORE_FILENAME).close()  # the seam is satisfied
    router = _router()
    with pytest.raises(AuditIntegrityError) as exc:
        build_sim_platform(store_dir=store_dir, anchor_dir=anchor_dir, authorisation_key=KEY, alert_router=router)
    assert "payload tampered" in str(exc.value)
    chain = router.by_name("audit.chain_verification_failed")[-1]
    assert chain.severity == "S1" and chain.payload["reason"] == "AUD-CHAIN-BROKEN" and "tampered" in chain.payload["detail"]
    assert chain.payload["correlation_id"].startswith("startup:")  # one id for the whole refused start-up
    assert _channels(router, chain) == ["pager", "email"]  # raised *and* delivered, on every channel
    # the catalogued auto-action is killswitch_platform and there is no platform yet to halt: that is itself an S1,
    # so the operator is told both that the chain failed and that the automatic halt did not run (never a silent no-op)
    unbound = router.by_name("alert.autoaction_failed")[-1]
    assert unbound.payload["alert"] == "audit.chain_verification_failed" and unbound.payload["auto_action"] == "killswitch_platform"
    assert unbound.payload["unbound"] is True and _channels(router, unbound) == ["pager", "email"]
    # fail closed: alerting is not permission. No platform was returned, so nothing was decided, ordered or submitted.
    assert not router.by_name("limit.changed")


@pytest.mark.tc("TC-AUD-012")
@pytest.mark.req("NFR-AUD-01")
@pytest.mark.env("dev")
@pytest.mark.quartet("abuse")
def test_a_journal_corrupted_on_purpose_pages_before_the_process_dies(tmp_path):  # type: ignore[no-untyped-def]
    """The abuse case the SRE Lead asked for (F-02): corrupt the control store's journal offline, start the process, and assert an S1 is delivered — with the integrity and availability classes distinguished, because their recoveries are opposite (RB-13)."""
    store_dir, anchor_dir = _dirs(tmp_path)
    p1 = build_sim_platform(store_dir=store_dir, anchor_dir=anchor_dir, authorisation_key=KEY)
    p1.run_intent(p1.make_intent())
    p1.audit.close()
    p1.store.close()

    # the attacker (or a bad disk) rewrites one journal entry without re-computing its digest: the chain breaks
    db = _control_db(store_dir)
    (seq,) = db.execute("SELECT MIN(seq) FROM journal WHERE tbl='execution.orders'").fetchone()
    db.execute("UPDATE journal SET correlation_id='forged' WHERE seq=?", (int(seq),))
    db.close()
    router = _router()
    with pytest.raises(StoreIntegrityError) as exc:
        build_sim_platform(store_dir=store_dir, anchor_dir=anchor_dir, authorisation_key=KEY, alert_router=router)
    assert "journal chain broken" in str(exc.value)
    alert = router.by_name("execution.store_unavailable")[-1]
    assert alert.severity == "S1" and alert.auto_action == "none"  # never an automatic write to a store under investigation
    assert alert.payload["reason"] == "STORE-OPEN-REFUSED" and alert.payload["store"] == STORE_FILENAME
    assert alert.payload["phase"] == "open" and alert.payload["correlation_id"].startswith("startup:")
    assert alert.payload["error"] == "StoreIntegrityError" and str(seq) in alert.payload["detail"]
    assert _channels(router, alert) == ["pager", "email"]  # delivered, not merely raised
    # the ordering is the whole finding: this is the *first* alert of the process, raised by a router that existed
    # before the store was opened, from a composition that never returned an object anyone could have alerted through
    assert router.fired[0] is alert and len(router.fired) == 1
    # restarting does not clear it: the refusal is a property of the file, not of the attempt
    with pytest.raises(StoreIntegrityError):
        build_sim_platform(store_dir=store_dir, anchor_dir=anchor_dir, authorisation_key=KEY)

    # the availability class is distinguished from the integrity class: same refusal, opposite recoveries (RB-13)
    broken_dir, broken_anchor = tmp_path / "unreadable", tmp_path / "worm-unreadable"
    (broken_dir / STORE_FILENAME).mkdir(parents=True)  # a store file that is not a file: SQLite cannot open it
    unreadable = _router()
    with pytest.raises(StoreError) as exc2:
        build_sim_platform(store_dir=broken_dir, anchor_dir=broken_anchor, authorisation_key=KEY, alert_router=unreadable)
    assert not isinstance(exc2.value, StoreIntegrityError)
    avail = unreadable.by_name("execution.store_unavailable")[-1]
    assert avail.payload["reason"] == "STORE-OPEN-UNAVAILABLE" and avail.payload["error"] == "StoreError"
    assert avail.severity == "S1" and _channels(unreadable, avail) == ["pager", "email"]


@pytest.mark.tc("TC-AUD-013")
@pytest.mark.req("NFR-AUD-01")
@pytest.mark.env("dev")
@pytest.mark.quartet("negative")
def test_both_stores_rewritten_consistently_are_caught_at_startup_not_at_the_next_publication(tmp_path):  # type: ignore[no-untyped-def]
    """D-066/O-164: an attacker who rewrites the control store *and* re-computes the whole audit chain leaves two stores that verify on their own terms and agree with each other. Only the anchor a different principal published disagrees — and composition now asks it, so the platform is halted at start-up instead of trading until the next scheduled publication."""
    from test_tc_dur_durability import _forge_audit_chain  # imported here: the durability module imports this one

    store_dir, anchor_dir = _dirs(tmp_path)
    p1 = build_sim_platform(store_dir=store_dir, anchor_dir=anchor_dir, authorisation_key=KEY)
    p1.run_intent(p1.make_intent())
    act = p1.killswitch.activate(KillSwitchLevel.ACCOUNT, ACCOUNT, reason="drill", actor=RISK_OFFICER, now=p1.now)
    p1.journal_anchor.anchor(correlation_id="operator:anchor:1", trigger="operator")
    witnessed = p1.journal_anchor.last_witnessed()
    p1.audit.seal(correlation_id="seal:operator:1")
    assert p1.audit.verify().ok
    p1.audit.close()
    p1.store.close()

    # (a) flip the engaged Kill Switch off and re-compute every unkeyed digest in the control store
    db = _control_db(store_dir)
    (raw,) = db.execute("SELECT value FROM kv WHERE tbl='killswitch.activations' AND key=?", (act.activation_id,)).fetchone()
    doc = json.loads(raw)
    doc["active"] = False
    _rewrite_consistently(db, "killswitch.activations", act.activation_id, json.dumps(doc))
    db.close()
    forged = SqliteStore(store_dir / STORE_FILENAME)
    forged_head = forged.journal_head()
    forged.close()
    # (b) and re-compute the whole audit chain from genesis so the witness carries the attacker's head
    adb = _audit_db(store_dir)
    _forge_audit_chain(adb, witnessed.store_id, witnessed.sequence, forged_head.digest)
    adb.close()
    SqliteStore(store_dir / AUDIT_STORE_FILENAME).close()  # both seams are satisfied and the two stores agree

    router = _router()
    p2 = build_sim_platform(store_dir=store_dir, anchor_dir=anchor_dir, authorisation_key=KEY, alert_router=router)
    # D-066: composition is not refused — it follows ADR-020's existing path, because refusing here would leave
    # nothing able to run the Kill Switch the failure calls for
    sv = p2.startup_verification
    assert sv is not None and not sv.ok and sv.reason == "AUD-CHAIN-HEAD-MISMATCH" and sv.anchor_length is not None
    fired = router.by_name("audit.chain_verification_failed")
    alert = [a for a in fired if a.payload["reason"] == sv.reason][-1]
    assert alert.severity == "S1" and alert.payload["correlation_id"].startswith("startup:")
    assert _channels(router, alert) == ["pager", "email"]
    # ADR-020 amendment 3: the forged chain also contradicts the seal record this store kept, so the scheduled
    # publication during composition was refused before the start-up verification ran. Two S1s, both true.
    assert [a for a in fired if a.payload["reason"] == "AUD-SEAL-BELOW-FLOOR"]
    # ...and the auto-action ran this time, because by this point there is a platform to halt
    assert any(a.level.value == "PLATFORM" for a in p2.killswitch.active())
    assert not [a for a in router.by_name("alert.autoaction_failed") if a.payload["alert"] == "audit.chain_verification_failed"]
    # caught at start-up: the halt is in force before the platform has decided anything or sent anything
    assert p2.broker.submissions_received == 0
    after = p2.run_intent(p2.make_intent())
    assert after.order is None and p2.broker.submissions_received == 0
    p2.audit.close()
    p2.store.close()


@pytest.mark.tc("TC-AUD-014")
@pytest.mark.req("NFR-AUD-01")
@pytest.mark.env("dev")
@pytest.mark.quartet("recovery")
def test_restore_then_verify_reopens_the_platform_and_the_startup_verdict_is_clean(tmp_path):  # type: ignore[no-untyped-def]
    """Recovery is restore-then-verify, never disable-the-check (O-134, RB-13): a corrupted control store is restored from the last good copy taken with the audit store and the anchor directory, the platform opens, and the start-up published-anchor verification passes and is silent. Restarting without restoring never clears the refusal."""
    store_dir, anchor_dir = _dirs(tmp_path)
    p1 = build_sim_platform(store_dir=store_dir, anchor_dir=anchor_dir, authorisation_key=KEY)
    p1.run_intent(p1.make_intent())
    p1.audit.seal(correlation_id="seal:operator:1")
    p1.audit.close()
    p1.store.close()
    backup = tmp_path / "last-good-copy"
    shutil.copytree(store_dir, backup / "state")  # control store and audit store as a matched set...
    shutil.copytree(anchor_dir, backup / "worm")  # ...with the witness written by the other principal

    db = _control_db(store_dir)
    db.execute("UPDATE journal SET correlation_id='forged' WHERE seq=(SELECT MIN(seq) FROM journal WHERE tbl='execution.orders')")
    db.close()
    for _ in range(2):  # a crash loop adds nothing: the refusal is not cleared by restarting
        refused = _router()
        with pytest.raises(StoreIntegrityError):
            build_sim_platform(store_dir=store_dir, anchor_dir=anchor_dir, authorisation_key=KEY, alert_router=refused)
        assert refused.by_name("execution.store_unavailable")[-1].payload["reason"] == "STORE-OPEN-REFUSED"

    shutil.rmtree(store_dir)  # the operator restores the matched set; the check is never disabled to make it start
    shutil.rmtree(anchor_dir)
    shutil.copytree(backup / "state", store_dir)
    shutil.copytree(backup / "worm", anchor_dir)
    router = _router()
    p2 = build_sim_platform(store_dir=store_dir, anchor_dir=anchor_dir, authorisation_key=KEY, alert_router=router)
    assert not [a for a in router.fired if a.name in STARTUP_ALERTS] and not router.by_name("audit.anchor_missing")
    sv = p2.startup_verification
    assert sv is not None and sv.ok and sv.anchor_length is not None
    assert p2.audit.verify().ok and p2.store.journal_head() is not None
    assert p2.run_intent(p2.make_intent()).order is not None  # the platform trades again only after both checks passed
    p2.audit.close()
    p2.store.close()


# --- witness continuity and the seal floor (Red-Team Lead Case B and Case C; ADR-020 amendment 3 proposed) ----------
# Case B measured before this change: delete ``audit_anchors.jsonl``, restart, and the platform started, an intent ran
# to FILLED and one order reached the broker; the S1 ``audit.anchor_missing`` fired with ``auto_action: none``, so
# nothing stopped. Case C measured before this change: truncate the chain, delete the witness, let an operator seal —
# "the truncation is now witnessed as if it had never happened".
#
# Two behaviours, a quartet each:
#   (1) a platform that *had* a witness and no longer has one does not open. The response is a refusal, not a Kill
#       Switch: D-066 stands, because a Kill Switch activation is itself a store row and would write to the store
#       under suspicion. The genesis case is distinguished honestly — a chain that has never been witnessed at all
#       is ADR-020's existing behaviour and still opens.
#   (2) a seal never witnesses a chain that contradicts what this store already recorded witnessing, whatever the
#       witness says or does not say, and an ordinary seal can no longer create the first anchor for a non-empty
#       chain. Re-establishing a lost witness is a separate, attested, audited operator act.
#
# The evidence the store keeps about its own witness is deliberately in two places, because they fail differently:
# a ``SealRecord`` in the seals table (an operator seal) and an ``audit.anchor.published`` row *in the hash chain*
# (a genesis or scheduled publication). Measured: the Case C rollback removes the seal records with the events,
# because a seal is written after the events it seals — the chain row is what survives it.


def _witness_marks(audit: AuditStore) -> list[dict[str, object]]:
    """The publication rows the store wrote into its own chain: the evidence a tail truncation cannot remove."""
    return [dict(e.payload) for e in audit.by_action(ANCHOR_PUBLISHED)]


def _excise_tail_events_consistently(db: sqlite3.Connection, keep_events: int) -> None:
    """A more careful offline attacker than ``_rollback_consistently``: remove the last audit events *and* their
    journal entries, renumber and re-chain the journal and rebuild the state rows — but leave the store's seal
    records in place, because a blunt rollback takes them with it (a seal is written after the events it seals).

    The seam is satisfied and the chain is a valid prefix; only the store's own record of what it has already
    sealed contradicts it. This is the attacker the seal floor exists for.
    """
    keys = [k for (k,) in db.execute("SELECT key FROM kv WHERE tbl=? ORDER BY key", (AUDIT_EVENTS_TABLE,)).fetchall()]
    doomed = set(keys[keep_events:])
    rows = db.execute("SELECT seq, op, tbl, key, value, correlation_id, at FROM journal ORDER BY seq").fetchall()
    drop: set[int] = set()
    for idx, (seq, _op, tbl, key, _v, _c, _a) in enumerate(rows):
        if tbl == AUDIT_EVENTS_TABLE and key in doomed:
            drop.add(int(seq))
            if idx and rows[idx - 1][2] == SEQUENCE_TABLE and rows[idx - 1][3] == AUDIT_SEQUENCE:
                drop.add(int(rows[idx - 1][0]))  # the sequence bump that allocated the event
    kept = [r for r in rows if int(r[0]) not in drop]
    db.execute("DELETE FROM journal")
    prev = GENESIS
    expected: dict[tuple[str, str], tuple[str, int]] = {}
    for n, (_seq, op, tbl, key, value, corr, at) in enumerate(kept, start=1):
        digest = journal_digest(prev, n, op, tbl, key, value, corr, at)
        db.execute(
            "INSERT INTO journal (seq, op, tbl, key, value, correlation_id, at, prev, digest) VALUES (?,?,?,?,?,?,?,?,?)",
            (n, op, tbl, key, value, corr, at, prev, digest),
        )
        prev = digest
        if op == "put":
            expected[(tbl, key)] = (value, n)
        else:
            expected.pop((tbl, key), None)
    db.execute("DELETE FROM kv")
    for (tbl, key), (value, seq) in expected.items():
        db.execute(
            "INSERT INTO kv (tbl, key, value, created_seq, seq, digest) VALUES (?,?,?,?,?,?)",
            (tbl, key, value, seq, seq, row_digest(tbl, key, value, seq)),
        )


def _trim_anchor_file(anchor_dir: Path, keep: int) -> None:
    """The attacker trims the witness's tail instead of deleting it, so what is left agrees with the shorter chain."""
    path = anchor_dir / ANCHOR_FILENAME
    lines = [ln for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]
    path.write_text("\n".join(lines[:keep]) + "\n", encoding="utf-8")


@pytest.mark.tc("TC-AUD-015")
@pytest.mark.req("NFR-AUD-01")
@pytest.mark.env("dev")
@pytest.mark.quartet("positive")
def test_a_witnessed_platform_opens_and_records_every_publication_it_makes(tmp_path):  # type: ignore[no-untyped-def]
    """A platform whose witness is present opens, restarts and trades exactly as before, and every publication it makes is durably recorded by the store itself — an operator seal as a SealRecord, a genesis or scheduled publication as an ``audit.anchor.published`` row with its own correlation id. A chain that has never been witnessed at all still opens: that is the genesis case, and it is not the same thing as a witness that is gone."""
    store_dir, anchor_dir = _dirs(tmp_path)
    router = _router()
    p1 = build_sim_platform(store_dir=store_dir, anchor_dir=anchor_dir, authorisation_key=KEY, alert_router=router)
    marks = _witness_marks(p1.audit)
    assert marks and marks[0]["anchor_seq"] == 1 and marks[0]["length"] == 0 and marks[0]["trigger"] == "genesis"
    assert p1.audit.all()[0].action == ANCHOR_PUBLISHED  # at the head of the chain: no tail truncation can remove it
    assert all(e.correlation_id for e in p1.audit.by_action(ANCHOR_PUBLISHED))
    p1.run_intent(p1.make_intent())
    head = p1.audit.seal(correlation_id="seal:operator:1")
    assert head.length == len(p1.audit) and p1.audit.seals()[-1].head == head and p1.audit.seals()[-1].anchor_seq is not None
    floor = p1.audit.witness_floor()
    assert floor is not None and floor.length == head.length and floor.head_hash == head.head_hash and floor.source == "seal"
    assert p1.audit.verify().ok and not router.by_name("audit.anchor_missing")
    p1.audit.close()
    p1.store.close()

    p2 = build_sim_platform(store_dir=store_dir, anchor_dir=anchor_dir, authorisation_key=KEY)  # restart: witness present
    assert p2.startup_verification is not None and p2.startup_verification.ok
    assert p2.run_intent(p2.make_intent()).order is not None and not p2.alerts.by_name("audit.anchor_missing")
    assert len(_witness_marks(p2.audit)) >= 1 and p2.audit.witness_floor() is not None
    p2.audit.close()
    p2.store.close()

    # the genesis case, distinguished honestly: no publisher was ever configured, so nothing this store recorded
    # names a witness. Nothing is refused and nothing is fabricated.
    unwitnessed = tmp_path / "never-witnessed"
    u1 = build_sim_platform(store_dir=unwitnessed, authorisation_key=KEY)
    u1.run_intent(u1.make_intent())
    assert u1.audit.publisher is None and u1.audit.witness_floor() is None and not _witness_marks(u1.audit)
    u1.audit.close()
    u1.store.close()
    u2 = build_sim_platform(store_dir=unwitnessed, authorisation_key=KEY)  # opens: it never had a witness to lose
    assert len(u2.audit) > 0 and u2.audit.verify().ok
    u2.audit.close()
    u2.store.close()
    mem = build_sim_platform()  # the memory default is unchanged
    assert mem.audit.backend == "MemoryStore" and mem.audit.witness_floor() is None and mem.audit.verify().ok


@pytest.mark.tc("TC-AUD-016")
@pytest.mark.req("NFR-AUD-01")
@pytest.mark.env("dev")
@pytest.mark.quartet("negative")
def test_a_platform_whose_witness_is_gone_refuses_to_open_and_writes_nothing(tmp_path):  # type: ignore[no-untyped-def]
    """The witness this store's own records name is absent, or present but unreadable: composition raises WitnessLostError, the catalogued S1 ``audit.anchor_missing`` is delivered with AUD-WITNESS-LOST / AUD-WITNESS-UNREADABLE and the start-up correlation id, and nothing at all is written to the store under suspicion — no incident row, no Kill Switch activation, no new event. Restarting never clears it."""
    store_dir, anchor_dir = _dirs(tmp_path)
    p1 = build_sim_platform(store_dir=store_dir, anchor_dir=anchor_dir, authorisation_key=KEY)
    p1.run_intent(p1.make_intent())
    p1.audit.seal(correlation_id="seal:operator:1")
    before = len(p1.audit)
    p1.audit.close()
    p1.store.close()

    (anchor_dir / ANCHOR_FILENAME).unlink()  # the replica is lost, or removed
    router = _router()
    with pytest.raises(WitnessLostError) as exc:
        build_sim_platform(store_dir=store_dir, anchor_dir=anchor_dir, authorisation_key=KEY, alert_router=router)
    assert "AUD-WITNESS-LOST" in str(exc.value)
    alert = router.by_name("audit.anchor_missing")[-1]
    assert alert.severity == "S1" and alert.auto_action == "none"  # D-066 stands: no automatic write to this store
    assert alert.payload["reason"] == "AUD-WITNESS-LOST" and alert.payload["correlation_id"].startswith("startup:")
    assert alert.payload["length"] == before and alert.payload["floor_length"] == before and alert.payload["marks"] >= 1
    assert _channels(router, alert) == ["pager", "email"]  # delivered, not merely raised
    assert not router.by_name("limit.changed")  # nothing composed: nothing decided, ordered or submitted
    assert not router.by_name("killswitch.hook_failed")

    def audit_rows() -> int:
        db = _audit_db(store_dir)
        (n,) = db.execute("SELECT count(*) FROM kv WHERE tbl=?", (AUDIT_EVENTS_TABLE,)).fetchone()
        db.close()
        return int(n)

    assert audit_rows() == before  # write nothing: the refusal appends no incident row of its own
    for _ in range(2):  # a crash loop adds nothing: the refusal is a property of the two stores, not of the attempt
        with pytest.raises(WitnessLostError):
            build_sim_platform(store_dir=store_dir, anchor_dir=anchor_dir, authorisation_key=KEY)
    assert audit_rows() == before

    # a witness that cannot be read is not a witness: same refusal, its own reason code, and the fix is to restore
    # the replica, never to overwrite it
    (anchor_dir / ANCHOR_FILENAME).write_text("garbage\n", encoding="utf-8")
    unreadable = _router()
    with pytest.raises(WitnessLostError) as exc2:
        build_sim_platform(store_dir=store_dir, anchor_dir=anchor_dir, authorisation_key=KEY, alert_router=unreadable)
    assert "AUD-WITNESS-UNREADABLE" in str(exc2.value)
    assert unreadable.by_name("audit.anchor_missing")[-1].payload["reason"] == "AUD-WITNESS-UNREADABLE"
    assert audit_rows() == before

    # an empty anchor directory is the same refusal as a missing file: "no witness" is one condition, however it
    # was produced. Recovery is restore-then-verify (TC-AUD-009) or the attested act (TC-AUD-018), never a flag.
    shutil.rmtree(anchor_dir)
    with pytest.raises(WitnessLostError):
        build_sim_platform(store_dir=store_dir, anchor_dir=anchor_dir, authorisation_key=KEY)
    assert audit_rows() == before


@pytest.mark.tc("TC-AUD-017")
@pytest.mark.req("NFR-AUD-01")
@pytest.mark.env("dev")
@pytest.mark.quartet("abuse")
def test_red_team_case_b_deleting_the_witness_no_longer_lets_the_platform_trade(tmp_path):  # type: ignore[no-untyped-def]
    """The Red-Team Lead's Case B, run as ``docs/PENTEST/probes/rt_probe_01_audit_witness.py`` runs it: build a durable platform, run an intent, seal, stop, delete ``audit_anchors.jsonl``, restart. Measured before: the platform started, an intent ran to FILLED and one order reached the broker. Now there is no platform to run an intent on. The same attacker who also rolls the store back — which takes the seal records with it — is refused too, on the publication row the chain carries."""
    store_dir, anchor_dir = _dirs(tmp_path)
    p1 = build_sim_platform(store_dir=store_dir, anchor_dir=anchor_dir, authorisation_key=KEY)
    p1.run_intent(p1.make_intent())
    p1.audit.seal(correlation_id="seal:operator:1")
    assert p1.broker.submissions_received == 1  # the platform that had its witness did trade: this is a refusal, not a break
    p1.audit.close()
    p1.store.close()
    (anchor_dir / ANCHOR_FILENAME).unlink()

    router = _router()
    with pytest.raises(WitnessLostError):
        build_sim_platform(store_dir=store_dir, anchor_dir=anchor_dir, authorisation_key=KEY, alert_router=router)
    assert router.by_name("audit.anchor_missing")[-1].payload["reason"] == "AUD-WITNESS-LOST"

    # the probe's Case C rollback, run against the store: it removes the seal records with the events (measured),
    # so the evidence that this store had a witness is the ``audit.anchor.published`` row at the head of the chain
    store2, anchor2 = tmp_path / "state2", tmp_path / "worm2"
    p2 = build_sim_platform(store_dir=store2, anchor_dir=anchor2, authorisation_key=KEY)
    p2.run_intent(p2.make_intent())
    sealed = p2.audit.seal(correlation_id="seal:operator:1")
    p2.audit.close()
    p2.store.close()
    db = _audit_db(store2)
    keys = [k for (k,) in db.execute("SELECT key FROM kv WHERE tbl=? ORDER BY key", (AUDIT_EVENTS_TABLE,)).fetchall()]
    (cut,) = db.execute("SELECT MIN(seq) FROM journal WHERE tbl=? AND key=?", (AUDIT_EVENTS_TABLE, keys[-5])).fetchone()
    _rollback_consistently(db, int(cut) - 2)
    (seal_rows,) = db.execute("SELECT count(*) FROM kv WHERE tbl=?", (AUDIT_SEALS_TABLE,)).fetchone()
    db.close()
    assert seal_rows == 0 and sealed.length > 0  # the rollback took the seal records with it
    SqliteStore(store2 / AUDIT_STORE_FILENAME).close()  # the seam accepts the rollback
    (anchor2 / ANCHOR_FILENAME).unlink()
    rolled = _router()
    with pytest.raises(WitnessLostError) as exc:
        build_sim_platform(store_dir=store2, anchor_dir=anchor2, authorisation_key=KEY, alert_router=rolled)
    assert "AUD-WITNESS-LOST" in str(exc.value)
    assert rolled.by_name("audit.anchor_missing")[-1].payload["marks"] >= 1
    assert rolled.by_name("audit.anchor_missing")[-1].payload["floor_length"] is None  # no seal record survived


@pytest.mark.tc("TC-AUD-018")
@pytest.mark.req("NFR-AUD-01")
@pytest.mark.env("dev")
@pytest.mark.quartet("recovery")
def test_re_establishing_a_lost_witness_is_an_explicit_attested_act_an_ordinary_seal_cannot_reach(tmp_path):  # type: ignore[no-untyped-def]
    """A genuine replica loss is recoverable, and only through the named path. The ordinary gesture is refused: a seal over an absent witness raises SealRefused with AUD-SEAL-UNWITNESSED and publishes nothing. The named act requires an actor, a reason, the exact length and head hash of the chain and the anchor sequence this store last recorded publishing; it writes one audit row under the operator's correlation id, inside the anchor it publishes; a repeat is refused; and no parameter of the composition root can reach it."""
    import inspect as inspect_mod

    store_dir, anchor_dir = _dirs(tmp_path)
    p = build_sim_platform(store_dir=store_dir, anchor_dir=anchor_dir, authorisation_key=KEY)
    p.run_intent(p.make_intent())
    p.audit.seal(correlation_id="seal:operator:1")
    (anchor_dir / ANCHOR_FILENAME).unlink()  # the replica volume is destroyed under a running platform

    # (a) the ordinary gesture cannot re-establish a witness, and it never could reach this path by habit
    with pytest.raises(SealRefused) as exc:
        p.audit.seal(correlation_id="operator:habit")
    assert "AUD-SEAL-UNWITNESSED" in str(exc.value)
    assert p.audit.publisher.latest() is None and not [s for s in p.audit.seals() if s.correlation_id == "operator:habit"]
    alert = p.alerts.by_name("audit.anchor_missing")[-1]
    assert alert.severity == "S1" and alert.payload["reason"] == "AUD-SEAL-UNWITNESSED" and alert.payload["correlation_id"] == "operator:habit"
    p.audit.close()
    p.store.close()
    with pytest.raises(WitnessLostError):  # and a restart does not clear it either
        build_sim_platform(store_dir=store_dir, anchor_dir=anchor_dir, authorisation_key=KEY)

    # (b) the operator reads the chain with the read-only inspection: no store is opened for use to do it
    seam = SqliteStore(store_dir / AUDIT_STORE_FILENAME)
    report = inspect_chain(seam, FileAnchorPublisher(anchor_dir))
    seam.close()
    assert report.chain_ok and not report.witness_present and report.length > 0 and report.last_anchor_seq >= 1
    assert set(dir(report)) & {"append", "put", "seal"} == set()

    # (c) the attestation must describe this chain exactly: a wrong length, head, anchor sequence, actor or reason fails
    good = dict(actor="ops:alice", reason="anchor replica volume destroyed", length=report.length, head_hash=report.head_hash, last_anchor_seq=report.last_anchor_seq)
    for bad in (
        {**good, "length": report.length - 1},
        {**good, "head_hash": "99" * 32},
        {**good, "last_anchor_seq": report.last_anchor_seq + 1},
        {**good, "actor": ""},
        {**good, "reason": ""},
    ):
        with pytest.raises(SealRefused) as bad_exc:
            reestablish_witness(
                store=SqliteStore(store_dir / AUDIT_STORE_FILENAME),
                publisher=FileAnchorPublisher(anchor_dir),
                attestation=WitnessAttestation(correlation_id="c1", **bad),  # type: ignore[arg-type]
            )
        assert "AUD-ATTESTATION-MISMATCH" in str(bad_exc.value)
        assert FileAnchorPublisher(anchor_dir).latest() is None  # a refused attempt publishes nothing

    # (d) the named act
    corr = "incident:witness-loss:2026-09-08"
    done = reestablish_witness(
        store=SqliteStore(store_dir / AUDIT_STORE_FILENAME),
        publisher=FileAnchorPublisher(anchor_dir),
        attestation=WitnessAttestation(correlation_id=corr, **good),  # type: ignore[arg-type]
    )
    assert done.record.anchor_seq == 1 and done.record.correlation_id == corr and done.record.length == report.length + 1
    assert done.row.action == WITNESS_REESTABLISHED and done.row.correlation_id == corr and done.row.actor == "ops:alice"
    assert done.row.payload["reason"] == good["reason"] and done.row.payload["attested_length"] == report.length
    assert done.row.payload["lost_anchor_seq"] == report.last_anchor_seq
    assert done.record.length == done.row.seq + 1  # the row is inside the anchor it caused: the act witnesses itself

    # (e) a repeat is refused: there is a witness again, so there is nothing to re-establish
    with pytest.raises(SealRefused) as again:
        reestablish_witness(
            store=SqliteStore(store_dir / AUDIT_STORE_FILENAME),
            publisher=FileAnchorPublisher(anchor_dir),
            attestation=WitnessAttestation(correlation_id=corr, **good),  # type: ignore[arg-type]
        )
    assert "AUD-WITNESS-PRESENT" in str(again.value)

    # (f) the platform opens again, the act is in the chain a restart reads, and composition cannot reach the path
    router = _router()
    p2 = build_sim_platform(store_dir=store_dir, anchor_dir=anchor_dir, authorisation_key=KEY, alert_router=router)
    assert p2.startup_verification is not None and p2.startup_verification.ok
    assert [e.action for e in p2.audit.by_correlation(corr)] == [WITNESS_REESTABLISHED]
    assert p2.run_intent(p2.make_intent()).order is not None
    assert "attestation" not in inspect_mod.signature(build_sim_platform).parameters
    p2.audit.close()
    p2.store.close()


@pytest.mark.tc("TC-AUD-019")
@pytest.mark.req("NFR-AUD-01")
@pytest.mark.env("dev")
@pytest.mark.quartet("positive")
def test_a_seal_on_a_chain_that_agrees_with_every_earlier_seal_publishes_as_before(tmp_path):  # type: ignore[no-untyped-def]
    """The floor is not a new gate on the honest path: repeated seals on a growing chain publish, each raises the floor, and the floor a restart reads is the highest head this store recorded witnessing."""
    store_dir, anchor_dir = _dirs(tmp_path)
    p = build_sim_platform(store_dir=store_dir, anchor_dir=anchor_dir, authorisation_key=KEY)
    first = p.audit.seal(correlation_id="seal:operator:1")
    assert p.audit.witness_floor().length == first.length  # type: ignore[union-attr]
    p.run_intent(p.make_intent())
    second = p.audit.seal(correlation_id="seal:operator:2")
    assert second.length > first.length and p.audit.witness_floor().length == second.length  # type: ignore[union-attr]
    assert p.audit.verify().ok and not p.alerts.by_name("audit.chain_verification_failed")
    p.audit.close()
    p.store.close()
    p2 = build_sim_platform(store_dir=store_dir, anchor_dir=anchor_dir, authorisation_key=KEY)
    floor = p2.audit.witness_floor()  # the restart's own scheduled publications raise it further
    assert floor is not None and floor.length >= second.length
    third = p2.audit.seal(correlation_id="seal:operator:3")
    assert third.length >= second.length and p2.audit.verify().ok and p2.audit.witness_floor().length == third.length  # type: ignore[union-attr]
    p2.audit.close()
    p2.store.close()


@pytest.mark.tc("TC-AUD-020")
@pytest.mark.req("NFR-AUD-01")
@pytest.mark.env("dev")
@pytest.mark.quartet("negative")
def test_a_seal_never_witnesses_a_chain_that_contradicts_what_this_store_already_sealed(tmp_path):  # type: ignore[no-untyped-def]
    """The attack Case C becomes once the witness may not simply be deleted: truncate the chain *and* trim the witness's tail so that what is left of it agrees with what is left of the chain. The platform opens — there is a witness, and it agrees — but the store's own seal ledger does not: the start-up verification returns AUD-SEAL-BELOW-FLOOR, and the operator's seal, the one action that would clear the alert, is refused with the same reason and the catalogued S1. Nothing is published and no SealRecord is written."""
    store_dir, anchor_dir = _dirs(tmp_path)
    p1 = build_sim_platform(store_dir=store_dir, anchor_dir=anchor_dir, authorisation_key=KEY)
    p1.run_intent(p1.make_intent())
    sealed = p1.audit.seal(correlation_id="seal:operator:1")
    p1.audit.close()
    p1.store.close()
    db = _audit_db(store_dir)
    _excise_tail_events_consistently(db, sealed.length - 5)
    (seal_rows,) = db.execute("SELECT count(*) FROM kv WHERE tbl=?", (AUDIT_SEALS_TABLE,)).fetchone()
    db.close()
    assert seal_rows == 1  # this attacker kept the ledger of what was sealed; the events are gone
    SqliteStore(store_dir / AUDIT_STORE_FILENAME).close()  # the seam is satisfied
    _trim_anchor_file(anchor_dir, 2)  # ...and the witness now stops at a head the shortened chain still matches

    router = _router()
    p2 = build_sim_platform(store_dir=store_dir, anchor_dir=anchor_dir, authorisation_key=KEY, alert_router=router)
    assert p2.startup_verification is not None and not p2.startup_verification.ok
    assert p2.startup_verification.reason == "AUD-SEAL-BELOW-FLOOR"  # the witness agrees; this store's ledger does not
    assert any(a.level.value == "PLATFORM" for a in p2.killswitch.active())  # the catalogued auto-action ran
    with pytest.raises(SealRefused) as exc:
        p2.audit.seal(correlation_id="operator:recovery")
    assert "AUD-SEAL-BELOW-FLOOR" in str(exc.value)
    alert = router.by_name("audit.chain_verification_failed")[-1]
    assert alert.severity == "S1" and alert.payload["reason"] == "AUD-SEAL-BELOW-FLOOR"
    assert alert.payload["correlation_id"] == "operator:recovery" and alert.payload["floor_length"] == sealed.length
    assert _channels(router, alert) == ["pager", "email"]
    assert p2.audit.publisher.latest().anchor_seq == 2  # nothing was published on top of the trimmed witness
    assert not [s for s in p2.audit.seals() if s.correlation_id == "operator:recovery"]
    # ...and the attested path is refused for the same reason: a recovery never launders a truncation
    with pytest.raises(SealRefused) as exc2:
        p2.audit.reestablish(
            WitnessAttestation(
                actor="ops:alice",
                reason="replica lost",
                length=len(p2.audit),
                head_hash=p2.audit.head_hash(),
                last_anchor_seq=2,
                correlation_id="operator:recovery",
            )
        )
    assert "AUD-SEAL-BELOW-FLOOR" in str(exc2.value) or "AUD-WITNESS-PRESENT" in str(exc2.value)
    p2.audit.close()
    p2.store.close()


@pytest.mark.tc("TC-AUD-021")
@pytest.mark.req("NFR-AUD-01")
@pytest.mark.env("dev")
@pytest.mark.quartet("abuse")
def test_red_team_case_c_the_recovery_no_longer_destroys_the_evidence_it_protects(tmp_path):  # type: ignore[no-untyped-def]
    """The Red-Team Lead's Case C, run exactly as the probe runs it: seal a chain, roll five events off the tail so the seam still accepts the file, delete the witness, restart, and let an operator seal. Measured before: 'the truncation is now witnessed as if it had never happened'. Now the restart is refused, so the operator's seal never happens; the only path left is the attested one, and it writes an indelible row naming who did it and why — which is the point, because an attacker with write access to both stores can still take that path (a residual for the Product Owner, not a control)."""
    store_dir, anchor_dir = _dirs(tmp_path)
    p1 = build_sim_platform(store_dir=store_dir, anchor_dir=anchor_dir, authorisation_key=KEY)
    p1.run_intent(p1.make_intent())
    sealed = p1.audit.seal(correlation_id="seal:operator:1")
    p1.audit.close()
    p1.store.close()
    db = _audit_db(store_dir)
    keys = [k for (k,) in db.execute("SELECT key FROM kv WHERE tbl=? ORDER BY key", (AUDIT_EVENTS_TABLE,)).fetchall()]
    (cut,) = db.execute("SELECT MIN(seq) FROM journal WHERE tbl=? AND key=?", (AUDIT_EVENTS_TABLE, keys[-5])).fetchone()
    _rollback_consistently(db, int(cut) - 2)
    db.close()
    (anchor_dir / ANCHOR_FILENAME).unlink()

    router = _router()
    with pytest.raises(WitnessLostError):  # the restart the probe performs
        build_sim_platform(store_dir=store_dir, anchor_dir=anchor_dir, authorisation_key=KEY, alert_router=router)
    assert router.by_name("audit.anchor_missing")[-1].payload["reason"] == "AUD-WITNESS-LOST"
    assert FileAnchorPublisher(anchor_dir).latest() is None  # the seal the probe performs next never happens

    # the residual, pinned by a test so that nobody discovers it later: the attested path is still open to an
    # actor who owns both stores. What it costs them is a row in the chain that says so, for ever.
    seam = SqliteStore(store_dir / AUDIT_STORE_FILENAME)
    report = inspect_chain(seam, FileAnchorPublisher(anchor_dir))
    seam.close()
    done = reestablish_witness(
        store=SqliteStore(store_dir / AUDIT_STORE_FILENAME),
        publisher=FileAnchorPublisher(anchor_dir),
        attestation=WitnessAttestation(
            actor="attacker",
            reason="claims a replica loss",
            length=report.length,
            head_hash=report.head_hash,
            last_anchor_seq=report.last_anchor_seq,
            correlation_id="x",
        ),
    )
    assert done.row.action == WITNESS_REESTABLISHED and done.row.actor == "attacker" and report.length < sealed.length
    p2 = build_sim_platform(store_dir=store_dir, anchor_dir=anchor_dir, authorisation_key=KEY)
    rows = p2.audit.by_action(WITNESS_REESTABLISHED)
    assert len(rows) == 1 and rows[0].actor == "attacker" and rows[0].payload["attested_length"] == report.length
    assert rows[0].payload["lost_anchor_seq"] == report.last_anchor_seq  # the chain says a witness was replaced here
    p2.audit.close()
    p2.store.close()


@pytest.mark.tc("TC-AUD-022")
@pytest.mark.req("NFR-AUD-01")
@pytest.mark.env("dev")
@pytest.mark.quartet("recovery")
def test_a_genuine_replica_loss_is_recoverable_and_the_floor_survives_the_recovery(tmp_path):  # type: ignore[no-untyped-def]
    """The honest half of Case C: a replica genuinely lost with the chain intact is re-established, the platform opens, verifies and trades, and the floor afterwards is the re-established head — so the next truncation is still refused its seal. Restoring the last good copy stays the first choice and is unchanged (TC-AUD-009)."""
    store_dir, anchor_dir = _dirs(tmp_path)
    p1 = build_sim_platform(store_dir=store_dir, anchor_dir=anchor_dir, authorisation_key=KEY)
    p1.run_intent(p1.make_intent())
    p1.audit.seal(correlation_id="seal:operator:1")
    p1.audit.close()
    p1.store.close()
    shutil.rmtree(anchor_dir)  # the whole replica volume is gone; the chain is untouched

    seam = SqliteStore(store_dir / AUDIT_STORE_FILENAME)
    report = inspect_chain(seam, FileAnchorPublisher(anchor_dir))
    seam.close()
    assert report.chain_ok and not report.witness_present and report.floor_length is not None
    corr = "incident:witness-loss:recovery"
    done = reestablish_witness(
        store=SqliteStore(store_dir / AUDIT_STORE_FILENAME),
        publisher=FileAnchorPublisher(anchor_dir),
        attestation=WitnessAttestation(
            actor="ops:alice",
            reason="replica volume lost",
            length=report.length,
            head_hash=report.head_hash,
            last_anchor_seq=report.last_anchor_seq,
            correlation_id=corr,
        ),
    )
    router = _router()
    p2 = build_sim_platform(store_dir=store_dir, anchor_dir=anchor_dir, authorisation_key=KEY, alert_router=router)
    assert p2.startup_verification is not None and p2.startup_verification.ok
    assert p2.audit.verify().ok and p2.run_intent(p2.make_intent()).order is not None
    floor = p2.audit.witness_floor()
    assert floor is not None and floor.length >= done.record.length
    assert [e.action for e in p2.audit.by_correlation(corr)] == [WITNESS_REESTABLISHED]
    reestablished = p2.audit.seal(correlation_id="seal:operator:after-recovery")
    p2.audit.close()
    p2.store.close()

    # the floor survives the recovery: a truncation below the re-established head is still refused its seal
    db = _audit_db(store_dir)
    _excise_tail_events_consistently(db, reestablished.length - 3)
    db.close()
    SqliteStore(store_dir / AUDIT_STORE_FILENAME).close()
    p3 = build_sim_platform(store_dir=store_dir, anchor_dir=anchor_dir, authorisation_key=KEY)
    with pytest.raises(SealRefused) as exc:
        p3.audit.seal(correlation_id="operator:again")
    assert "AUD-SEAL-BELOW-FLOOR" in str(exc.value)
    p3.audit.close()
    p3.store.close()

