# TC-RC — Reconciliation and break management

Control: Reconciliation and break management — Requirement: FR-14 — RTM row: FR-14 — Owner: Backend Lead — Reviewer (≠ owner): Trading Domain Lead — **signature pending** (generated evidence is never self-certified [Source: 00, 11])

Environment tag: dev/sim — Data version: `sim-policy-v0.1 | sim-feed seed=7 | tool_registry 0.1.0` — Generated 2026-09-07T17:33:35.225922+00:00 at `03e673908c3ab4b22bd809990fe06995cc4cf8fb`

| Quartet | Test ID | Given/When/Then (docstring) | Expected | Actual | Evidence link |
|---|---|---|---|---|---|
| positive | TC-RC-001 | After fills, internal positions/orders/cash reconcile cleanly against the broker statement; completion audited. | pass | passed | `test/quartets/test_tc_rc_reconciliation.py::test_positions_and_orders_match_statement` |
| negative | TC-RC-002 | A quantity/missing-fill break (S2) opens a ticket, raises an alert and drops the account from autonomy to Supervised. | pass | passed | `test/quartets/test_tc_rc_reconciliation.py::test_break_moves_account_to_supervised` |
| abuse | TC-RC-003 | A broker-side order with no internal counterpart is classified DUPLICATE (S1) and triggers the account Kill Switch. | pass | passed | `test/quartets/test_tc_rc_reconciliation.py::test_phantom_broker_order_is_s1_duplicate_and_kills_account` |
| recovery | TC-RC-004 | Ticket resolution needs two different authorised humans; agents and repeat resolvers are denied; audit records both. | pass | passed | `test/quartets/test_tc_rc_reconciliation.py::test_two_person_resolution` |

Quartet complete: yes. Records: 4.
