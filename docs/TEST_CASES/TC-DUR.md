# TC-DUR — Durable control state across restarts

Control: Durable control state across restarts — Requirement: NFR-CON-01 — RTM row: NFR-CON-01 — Owner: Backend Lead — Reviewer (≠ owner): Integration Architect — **signature pending** (generated evidence is never self-certified [Source: 00, 11])

Environment tag: dev/sim — Data version: `sim-policy-v0.1 | sim-feed seed=7 | tool_registry 0.1.0` — Generated 2026-09-08T14:43:35.198187+00:00 at `a6203401a7e15f083758da1ae974ceb181e08e32` (tree clean, tested tree `4495631c3d91`)

| Quartet | Test ID | Given/When/Then (docstring) | Expected | Actual | Evidence link |
|---|---|---|---|---|---|
| positive | TC-DUR-001 | Orders, lease token, Kill Switch activation and outbox rows written by one process are read back by a rebuilt platform; pending outbox events relay exactly once. | pass | passed | `test/quartets/test_tc_dur_durability.py::test_control_state_survives_restart_and_outbox_relays_exactly_once` |
| negative | TC-DUR-002 | Two processes on the same store: the second cannot acquire a live lease, its guessed token is fenced, and a preemption by one is stale for the other (ADR-002). | pass | passed | `test/quartets/test_tc_dur_durability.py::test_two_platforms_on_one_store_cannot_both_hold_the_lease` |
| abuse | TC-DUR-003 | A row edited, deleted or re-journalled behind the store's back is detected (row digest, hash-chained journal, replay check); a gateway whose store fails submits nothing. | pass | passed | `test/quartets/test_tc_dur_durability.py::test_tampered_store_is_refused_and_store_errors_fail_closed` |
| recovery | TC-DUR-004 | A relay that dies mid-batch leaves the rest pending; after a restart the remainder relays exactly once and a replayed pipeline message returns the stored result without a second broker order. | pass | passed | `test/quartets/test_tc_dur_durability.py::test_relay_crash_and_pipeline_replay_after_restart` |

Quartet complete: yes. Records: 4.
