# TC-RC — Reconciliation and break management

Control: Reconciliation and break management — Requirement: FR-14 — RTM row: FR-14 — Owner: Backend Lead — Reviewer (≠ owner): Trading Domain Lead — **signature pending** (generated evidence is never self-certified [Source: 00, 11])

Environment tag: dev/sim — Data version: `sim-policy-v0.1 | sim-feed seed=7 | tool_registry 0.1.0` — Generated 2026-09-08T14:46:24.342677+00:00 at `335ec189663653e3b58a95d49ea9c26c9243ff00` (tree dirty, tested tree `398dcaba2a96`)

| Quartet | Test ID | Given/When/Then (docstring) | Expected | Actual | Evidence link |
|---|---|---|---|---|---|
| positive | TC-RC-001 | After fills, internal positions/orders/cash reconcile cleanly against the broker statement; completion audited. | pass | passed | `test/quartets/test_tc_rc_reconciliation.py::test_positions_and_orders_match_statement` |
| negative | TC-RC-002 | A quantity/missing-fill break (S2) opens a ticket, raises an alert and drops the account from autonomy to Supervised. | pass | passed | `test/quartets/test_tc_rc_reconciliation.py::test_break_moves_account_to_supervised` |
| negative | TC-RC-005 | IOC cancelled at the broker is adopted into the internal state; internal CANCELLED vs broker OPEN is an S1 STATUS break (Trading review OBJ-3). | pass | passed | `test/quartets/test_tc_rc_reconciliation.py::test_status_disagreement_is_a_break_and_broker_cancel_is_adopted` |
| abuse | TC-RC-003 | A broker-side order with no internal counterpart is classified DUPLICATE (S1) and triggers the account Kill Switch. | pass | passed | `test/quartets/test_tc_rc_reconciliation.py::test_phantom_broker_order_is_s1_duplicate_and_kills_account` |
| recovery | TC-RC-004 | Ticket resolution needs two different authorised humans; agents and repeat resolvers are denied; audit records both. | pass | passed | `test/quartets/test_tc_rc_reconciliation.py::test_two_person_resolution` |

Quartet complete: yes. Records: 5.
