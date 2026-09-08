# TC-EX — Execution gateway: idempotency, fencing, failover

Control: Execution gateway: idempotency, fencing, failover — Requirement: FR-13 — RTM row: FR-13 — Owner: Backend Lead — Reviewer (≠ owner): Trading Domain Lead / Integration Architect — **signature pending** (generated evidence is never self-certified [Source: 00, 11])

Environment tag: dev/sim — Data version: `sim-policy-v0.1 | sim-feed seed=7 | tool_registry 0.1.0` — Generated 2026-09-08T14:20:15.686197+00:00 at `7d61bd14972d4a8d16c011f4349e3a9dc9677340` (tree dirty, tested tree `1a23b8278a11`)

| Quartet | Test ID | Given/When/Then (docstring) | Expected | Actual | Evidence link |
|---|---|---|---|---|---|
| positive | TC-EX-001 | One authorised order command -> exactly one broker order with client_order_id derived from the idempotency key. | pass | passed | `test/quartets/test_tc_ex_execution.py::test_one_authorised_command_one_broker_order` |
| positive | TC-EX-009 | A command signed by the pipeline for a known APPROVED decision is accepted; the same command with one field altered is not. | pass | passed | `test/quartets/test_tc_ex_execution.py::test_gateway_accepts_only_control_plane_signed_commands` |
| positive | TC-EX-010 | Two distinct commands never share a digest, whatever the field boundaries (IVA-20); each field participates. | pass | passed | `test/quartets/test_tc_ex_execution.py::test_authorised_digest_binds_every_field_injectively` |
| negative | TC-EX-002 | Redelivered command (at-least-once) -> inbox dedupe; no second broker submission; audit records the duplicate. | pass | passed | `test/quartets/test_tc_ex_execution.py::test_replayed_command_deduplicated` |
| negative | TC-EX-005 | FILLED is terminal; illegal transitions raise; fills for unknown orders alert instead of mutating state. | pass | passed | `test/quartets/test_tc_ex_execution.py::test_order_states_are_monotonic` |
| negative | TC-EX-006 | Broker capability discovery: TRAILING_STOP unsupported by the sim broker -> BROKER_REJECTED with reason, no fill. | pass | passed | `test/quartets/test_tc_ex_execution.py::test_unsupported_order_type_rejected_by_capability_discovery` |
| negative | TC-EX-009 | An authorised command that arrives after an ACCOUNT Kill Switch or a halt is refused at the gateway, whatever the decision said (IVA V-C1). | pass | passed | `test/quartets/test_tc_ex_execution.py::test_gateway_blocks_kill_switch_and_halted_account_at_submission` |
| negative | TC-EX-010 | An altered command reusing a known idempotency key is refused as unauthorised before the inbox answers (IVA-25); an unknown account halts the intent instead of crashing (IVA-24). | pass | passed | `test/quartets/test_tc_ex_execution.py::test_unauthenticated_command_learns_nothing_from_the_inbox` |
| abuse | TC-EX-003 | A submission with a stale fencing token is rejected and alerted (S1); no broker order is created. | pass | passed | `test/quartets/test_tc_ex_execution.py::test_stale_fencing_token_rejected` |
| abuse | TC-EX-007 | A re-evaluation of the same intent under a new policy version yields a new key but is refused while an order is live (Trading review OBJ-1). | pass | passed | `test/quartets/test_tc_ex_execution.py::test_new_policy_version_cannot_create_second_live_order` |
| abuse | TC-EX-009 | A correctly signed command naming a decision the control plane never made is refused; a gateway built without hooks submits nothing. | pass | passed | `test/quartets/test_tc_ex_execution.py::test_forged_decision_and_gateway_without_oracle_fail_closed` |
| abuse | TC-EX-010 | A command authorised more than five minutes ago, or one whose authorisation was already consumed under a new key, is refused (IVA-21); a cancelled intent cannot be re-executed. | pass | passed | `test/quartets/test_tc_ex_execution.py::test_stale_and_consumed_authorisations_are_refused` |
| recovery | TC-EX-004 | Executor A loses the broker mid-submission; standby B takes the lease; A's retry is fenced; reconciliation shows one order. | pass | passed | `test/quartets/test_tc_ex_execution.py::test_failover_with_in_flight_order_single_broker_order` |
| recovery | TC-EX-008 | With a broker that does not dedupe client ids, a retry after an outage adopts the existing order instead of sending a second one (Trading review OBJ-2). | pass | passed | `test/quartets/test_tc_ex_execution.py::test_retry_queries_non_deduping_broker_before_resubmitting` |
| recovery | TC-EX-009 | An order left SUBMITTED by a broker outage is not re-sent once the account was halted during the outage. | pass | passed | `test/quartets/test_tc_ex_execution.py::test_retry_after_outage_rechecks_kill_switch` |
| recovery | TC-EX-010 | An order that reached the broker during an outage is adopted on retry and, because the account was halted meanwhile, cancelled at the broker immediately (IVA-19). | pass | passed | `test/quartets/test_tc_ex_execution.py::test_order_adopted_on_retry_under_halt_is_cancelled_at_broker` |
| recovery | TC-EX-011 | A gateway rebuilt from its store after a crash with an order in flight: the fencing token is never reissued lower, the replayed command is deduplicated, the consumed grant and decision stay refused, and nothing reaches the broker. | pass | passed | `test/quartets/test_tc_ex_execution.py::test_restart_with_order_in_flight_keeps_fencing_inbox_and_one_shot_grants` |

Quartet complete: yes. Records: 17.
