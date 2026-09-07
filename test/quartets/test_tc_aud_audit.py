"""TC-AUD — Immutable audit [Source: 03, 06; NFR-AUD-01; T-12]."""

from __future__ import annotations

import pytest
from audit_service.store import AuditEvent, AuditStore
from conftest import AUDITOR


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
