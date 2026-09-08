# TC-PMO — PMO

Control: PMO — Requirement: - — RTM row: - — Owner: Backend Lead — Reviewer (≠ owner): pending — **signature pending** (generated evidence is never self-certified [Source: 00, 11])

Environment tag: dev/sim — Data version: `sim-policy-v0.1 | sim-feed seed=7 | tool_registry 0.1.0` — Generated 2026-09-08T16:22:27.833552+00:00 at `4823984b83a5800eded1ed58d1375599408452f8` (tree dirty, tested tree `2b73030af402`)

| Quartet | Test ID | Given/When/Then (docstring) | Expected | Actual | Evidence link |
|---|---|---|---|---|---|
| positive | TC-PMO-001 | test_ledger_readers_cover_the_lifecycle | pass | passed | `test/contract/test_meridian_sync.py::test_ledger_readers_cover_the_lifecycle` |
| negative | TC-PMO-002 | The programme payload carries the six gates A..F as Meridian's `gateModel` contract requires (names, strictly increasing positions in the open interval, evidence), because a programme that does not declare a ladder gets Meridian's default four-gate one and every project is then born with two ladders. | pass | passed | `test/contract/test_meridian_sync.py::test_the_programme_declares_our_gate_ladder_so_projects_are_not_born_with_meridian_defaults` |
| abuse | TC-PMO-003 | test_refuses_to_run_without_credentials | pass | passed | `test/contract/test_meridian_sync.py::test_refuses_to_run_without_credentials` |
| recovery | TC-PMO-004 | The loader is a one-way projection of the ledgers (ADR-017): re-reading them yields the same rows, so an interrupted load is recovered by running it again; and the evidence file it writes carries no credential, because that file is committed. | pass | passed | `test/contract/test_meridian_sync.py::test_a_reloaded_portfolio_converges_and_no_secret_reaches_the_evidence_file` |

Quartet complete: yes. Records: 4.
