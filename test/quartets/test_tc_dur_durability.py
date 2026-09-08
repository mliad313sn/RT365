"""TC-DUR — Durable control state across restarts [Source: 03; NFR-CON-01; ADR-010 seam; ADR-018 proposed; R-05, R-23].

The invariants the control envelope relies on (fencing tokens never reissued lower, inbox dedupe, one-shot
grants, Kill Switch activations, outbox delivery) must survive a process restart. A platform built with a
``store_dir`` keeps them in one SQLite file (WAL); a platform rebuilt from the same directory is the restart.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest
from conftest import ACCOUNT, RISK_OFFICER, SRE, STRATEGY, resting_limit_intent
from execution_gateway.gateway import StaleFencingToken
from execution_gateway.lease import LeaseHeld
from killswitch_service.service import KillSwitchLevel
from rtcore.planes import Plane, enter
from rtcore.schemas.order import OrderState
from rtcore.store import MemoryStore, StoreError, StoreIntegrityError
from web_bff.platform import STORE_FILENAME, build_sim_platform

KEY = b"sim-only-command-authorisation-key-32b!!"  # the composition root receives the key; no AI/MCP component does (V-C2)


def _db(store_dir: Path) -> sqlite3.Connection:
    return sqlite3.connect(store_dir / STORE_FILENAME, isolation_level=None)


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
