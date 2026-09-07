# TC-EX — Execution gateway: idempotency, fencing, failover

Control: Execution gateway: idempotency, fencing, failover — Requirement: FR-13 — RTM row: FR-13 — Owner: Backend Lead — Reviewer (≠ owner): Trading Domain Lead / Integration Architect — **signature pending** (generated evidence is never self-certified [Source: 00, 11])

Environment tag: dev/sim — Data version: `sim-policy-v0.1 | sim-feed seed=7 | tool_registry 0.1.0` — Generated 2026-09-07T17:33:35.225922+00:00 at `03e673908c3ab4b22bd809990fe06995cc4cf8fb`

| Quartet | Test ID | Given/When/Then (docstring) | Expected | Actual | Evidence link |
|---|---|---|---|---|---|
| positive | TC-EX-001 | One authorised order command -> exactly one broker order with client_order_id derived from the idempotency key. | pass | passed | `test/quartets/test_tc_ex_execution.py::test_one_authorised_command_one_broker_order` |
| negative | TC-EX-002 | Redelivered command (at-least-once) -> inbox dedupe; no second broker submission; audit records the duplicate. | pass | passed | `test/quartets/test_tc_ex_execution.py::test_replayed_command_deduplicated` |
| negative | TC-EX-005 | FILLED is terminal; illegal transitions raise; fills for unknown orders alert instead of mutating state. | pass | passed | `test/quartets/test_tc_ex_execution.py::test_order_states_are_monotonic` |
| negative | TC-EX-006 | Broker capability discovery: TRAILING_STOP unsupported by the sim broker -> BROKER_REJECTED with reason, no fill. | pass | passed | `test/quartets/test_tc_ex_execution.py::test_unsupported_order_type_rejected_by_capability_discovery` |
| abuse | TC-EX-003 | A submission with a stale fencing token is rejected and alerted (S1); no broker order is created. | pass | passed | `test/quartets/test_tc_ex_execution.py::test_stale_fencing_token_rejected` |
| recovery | TC-EX-004 | Executor A loses the broker mid-submission; standby B takes the lease; A's retry is fenced; reconciliation shows one order. | pass | passed | `test/quartets/test_tc_ex_execution.py::test_failover_with_in_flight_order_single_broker_order` |

Quartet complete: yes. Records: 6.
