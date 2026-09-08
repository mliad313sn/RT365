# TC-CP — Compliance eligibility, dual key, surveillance, retention

Control: Compliance eligibility, dual key, surveillance, retention — Requirement: FR-15 — RTM row: FR-15 — Owner: Backend Lead — Reviewer (≠ owner): Compliance Agent — **signature pending** (generated evidence is never self-certified [Source: 00, 11])

Environment tag: dev/sim — Data version: `sim-policy-v0.1 | sim-feed seed=7 | tool_registry 0.1.0` — Generated 2026-09-08T09:51:24.927874+00:00 at `d1ccb21596456977a7d1b69d4694eb4724546445` (tree dirty, tested tree `4366fa62fdac`)

| Quartet | Test ID | Given/When/Then (docstring) | Expected | Actual | Evidence link |
|---|---|---|---|---|---|
| positive | TC-CP-001 | Eligible customer/instrument/cell -> ELIGIBLE with policy version; identical inputs give identical decision. | pass | passed | `test/quartets/test_tc_cp_eligibility.py::test_eligible_combination_passes_and_is_deterministic` |
| negative | TC-CP-002 | Restricted instrument/venue, missing product permission, short-sale ban and missing inputs are INELIGIBLE with reason codes. | pass | passed | `test/quartets/test_tc_cp_eligibility.py::test_ineligible_combinations_carry_reason_codes` |
| negative | TC-CP-005 | Synthetic wash/spoof/close patterns are detected; manipulation-capable or out-of-scope strategies are rejected at registration. | pass | passed | `test/quartets/test_tc_cp_eligibility.py::test_surveillance_patterns_and_registration_screen` |
| abuse | TC-CP-003 | Legal record alone (no technical flag) blocks; same person signing and activating blocks; agents cannot activate flags. | pass | passed | `test/quartets/test_tc_cp_eligibility.py::test_legal_record_without_flag_blocked` |
| abuse | TC-CP-007 | The legal record must be signed by a human Legal Agent: two Compliance people, an agent, or the same person twice never satisfy the dual key (council finding F-1, 2026-09-08). | pass | passed | `test/quartets/test_tc_cp_eligibility.py::test_dual_key_requires_legal_and_compliance_hands` |
| recovery | TC-CP-004 | Flag without legal record is impossible/blocked; after dual key the cell is live; one person can disable (rollback). | pass | passed | `test/quartets/test_tc_cp_eligibility.py::test_flag_without_record_blocked_then_dual_key_enables_and_disable_is_single_person` |
| recovery | TC-CP-006 | Deletion requests are suppressed (not destroyed) under legal hold or retention; decision logged [O-09]. | pass | passed | `test/quartets/test_tc_cp_eligibility.py::test_retention_deletion_suppressed_under_legal_hold` |

Quartet complete: yes. Records: 7.
