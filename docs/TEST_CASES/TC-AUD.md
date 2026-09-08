# TC-AUD — Immutable audit

Control: Immutable audit — Requirement: NFR-AUD-01 — RTM row: NFR-AUD-01 — Owner: SRE Lead — Reviewer (≠ owner): IVA — **signature pending** (generated evidence is never self-certified [Source: 00, 11])

Environment tag: dev/sim — Data version: `sim-policy-v0.1 | sim-feed seed=7 | tool_registry 0.1.0` — Generated 2026-09-08T15:27:49.350565+00:00 at `c991075d014343f731eeaa4a911340e31a1eb7d4` (tree dirty, tested tree `f673199b3f63`)

| Quartet | Test ID | Given/When/Then (docstring) | Expected | Actual | Evidence link |
|---|---|---|---|---|---|
| positive | TC-AUD-001 | One correlation ID links intent, eligibility, risk decision, order command, ack and fill in the audit chain. | pass | passed | `test/quartets/test_tc_aud_audit.py::test_every_decision_and_transition_is_audited_with_correlation_id` |
| positive | TC-AUD-006 | Events, seals and published anchors written by one process are read back by a platform rebuilt from store_dir; verify against the published anchor passes; the tenant filter still applies. | pass | passed | `test/quartets/test_tc_aud_audit.py::test_events_seals_and_anchors_survive_rebuild_and_verify_against_published_anchor` |
| negative | TC-AUD-002 | The audit store exposes no mutation path other than append. | pass | passed | `test/quartets/test_tc_aud_audit.py::test_no_update_or_delete_api_exists` |
| negative | TC-AUD-007 | A store rolled back consistently (seam satisfied) fails verify against the published anchor; an anchor older than the configured lag or absent fails closed with S1 audit.anchor_missing. | pass | passed | `test/quartets/test_tc_aud_audit.py::test_truncated_tail_stale_and_missing_anchor_fail_closed` |
| abuse | TC-AUD-003 | Modifying, replacing or removing a stored event breaks the chain and verification reports the first bad sequence. | pass | passed | `test/quartets/test_tc_aud_audit.py::test_tampering_detected_by_hash_chain` |
| abuse | TC-AUD-005 | A truncated tail verifies as a valid prefix without an anchor; with the sealed head it is detected; timestamps are monotonic (Security review OBJ-3). | pass | passed | `test/quartets/test_tc_aud_audit.py::test_truncation_detected_with_sealed_anchor_and_backdating_refused` |
| abuse | TC-AUD-008 | An edited event row in the SQLite file is refused (seam digest, then the audit chain even after a consistent digest rewrite); an edited or shortened anchor file breaks the anchor chain; the publisher's handle and the publisher expose no method that writes or deletes audit events. | pass | passed | `test/quartets/test_tc_aud_audit.py::test_edited_row_refused_anchor_tamper_detected_and_publisher_has_no_audit_write_path` |
| recovery | TC-AUD-004 | Exported chain re-loads into a fresh store and verifies; file backend is append-only and survives restart. | pass | passed | `test/quartets/test_tc_aud_audit.py::test_export_reload_and_file_backed_worm` |
| recovery | TC-AUD-009 | After a corrupt anchor directory is replaced by the last good copy, verify passes again; the incident and its recovery are audit rows sharing the alert's correlation_id and are anchored by the next seal; a restart sees them. | pass | passed | `test/quartets/test_tc_aud_audit.py::test_corrupt_anchor_directory_restored_from_last_good_copy_and_incident_audited` |

Quartet complete: yes. Records: 9.
