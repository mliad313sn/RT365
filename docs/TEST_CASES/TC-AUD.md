# TC-AUD — Immutable audit

Control: Immutable audit — Requirement: NFR-AUD-01 — RTM row: NFR-AUD-01 — Owner: SRE Lead — Reviewer (≠ owner): IVA — **signature pending** (generated evidence is never self-certified [Source: 00, 11])

Environment tag: dev/sim — Data version: `sim-policy-v0.1 | sim-feed seed=7 | tool_registry 0.1.0` — Generated 2026-09-07T17:33:35.225922+00:00 at `03e673908c3ab4b22bd809990fe06995cc4cf8fb`

| Quartet | Test ID | Given/When/Then (docstring) | Expected | Actual | Evidence link |
|---|---|---|---|---|---|
| positive | TC-AUD-001 | One correlation ID links intent, eligibility, risk decision, order command, ack and fill in the audit chain. | pass | passed | `test/quartets/test_tc_aud_audit.py::test_every_decision_and_transition_is_audited_with_correlation_id` |
| negative | TC-AUD-002 | The audit store exposes no mutation path other than append. | pass | passed | `test/quartets/test_tc_aud_audit.py::test_no_update_or_delete_api_exists` |
| abuse | TC-AUD-003 | Modifying, replacing or removing a stored event breaks the chain and verification reports the first bad sequence. | pass | passed | `test/quartets/test_tc_aud_audit.py::test_tampering_detected_by_hash_chain` |
| recovery | TC-AUD-004 | Exported chain re-loads into a fresh store and verifies; file backend is append-only and survives restart. | pass | passed | `test/quartets/test_tc_aud_audit.py::test_export_reload_and_file_backed_worm` |

Quartet complete: yes. Records: 4.
