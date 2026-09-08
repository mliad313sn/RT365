"""TC-AUD — Immutable audit [Source: 03, 06; NFR-AUD-01; T-12]."""

from __future__ import annotations

import json
import shutil
import sqlite3
from pathlib import Path

import pytest
from audit_service.anchor import ANCHOR_FILENAME, AnchorError, AnchorRecord, FileAnchorPublisher
from audit_service.store import AUDIT_EVENTS_TABLE, AuditEvent, AuditIntegrityError, AuditStore, ChainHead
from conftest import AUDITOR, TENANT
from rtcore.store import GENESIS, SqliteStore, StoreIntegrityError, journal_digest, row_digest
from web_bff.platform import AUDIT_STORE_FILENAME, TENANT_B, build_sim_platform

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
    a tail truncation that the seam cannot see and only the external anchor exposes."""
    db.execute("DELETE FROM journal WHERE seq > ?", (keep_upto_seq,))
    expected: dict[tuple[str, str], tuple[str, int]] = {}
    for seq, op, tbl, k, value in db.execute("SELECT seq, op, tbl, key, value FROM journal ORDER BY seq").fetchall():
        if op == "put":
            expected[(tbl, k)] = (value, int(seq))
        else:
            expected.pop((tbl, k), None)
    for tbl, k in db.execute("SELECT tbl, key FROM kv").fetchall():
        if (tbl, k) not in expected:
            db.execute("DELETE FROM kv WHERE tbl=? AND key=?", (tbl, k))
    for (tbl, k), (value, seq) in expected.items():
        db.execute("UPDATE kv SET value=?, seq=?, digest=? WHERE tbl=? AND key=?", (value, seq, row_digest(tbl, k, value, seq), tbl, k))


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
    p4 = build_sim_platform(store_dir=store3, anchor_dir=anchor3, authorisation_key=KEY)  # restart with events but no anchor
    assert p4.audit.latest_anchor() is None and not p4.audit.verify().ok  # a restart does not fabricate a fresh anchor


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
