# TC-KS — Kill Switch

Control: Kill Switch — Requirement: FR-17 — RTM row: FR-17 — Owner: Backend Lead — Reviewer (≠ owner): Chief Risk Agent — **signature pending** (generated evidence is never self-certified [Source: 00, 11])

Environment tag: dev/sim — Data version: `sim-policy-v0.1 | sim-feed seed=7 | tool_registry 0.1.0` — Generated 2026-09-08T15:02:56.208976+00:00 at `0e43d82cde7f5637a570bc313cf07c267c296cd3` (tree dirty, tested tree `8b31aa663d14`)

| Quartet | Test ID | Given/When/Then (docstring) | Expected | Actual | Evidence link |
|---|---|---|---|---|---|
| positive | TC-KS-001 | Activation: open orders cancelled, agent identities revoked, evidence snapshot hashed, notification sent, new intents HALTED. | pass | passed | `test/quartets/test_tc_ks_killswitch.py::test_activation_blocks_new_risk_and_cancels_open_orders` |
| positive | TC-KS-005 | Each of the six levels is consulted by the risk engine through the account snapshot flags. | pass | passed | `test/quartets/test_tc_ks_killswitch.py::test_every_level_blocks_matching_intents[PLATFORM-*]` |
| positive | TC-KS-005 | Each of the six levels is consulted by the risk engine through the account snapshot flags. | pass | passed | `test/quartets/test_tc_ks_killswitch.py::test_every_level_blocks_matching_intents[TENANT-tenant-sim]` |
| positive | TC-KS-005 | Each of the six levels is consulted by the risk engine through the account snapshot flags. | pass | passed | `test/quartets/test_tc_ks_killswitch.py::test_every_level_blocks_matching_intents[STRATEGY-strat-sma-xover]` |
| positive | TC-KS-005 | Each of the six levels is consulted by the risk engine through the account snapshot flags. | pass | passed | `test/quartets/test_tc_ks_killswitch.py::test_every_level_blocks_matching_intents[ASSET-SIMEQ1]` |
| positive | TC-KS-005 | Each of the six levels is consulted by the risk engine through the account snapshot flags. | pass | passed | `test/quartets/test_tc_ks_killswitch.py::test_every_level_blocks_matching_intents[VENUE-SIMX]` |
| positive | TC-KS-006 | Runtime loss-limit breach -> risk.halt.v1 event -> Kill Switch at account level without human action. | pass | passed | `test/quartets/test_tc_ks_killswitch.py::test_runtime_monitor_triggers_kill_switch` |
| positive | TC-KS-009 | Outcome target D-044: 100% of approvals after activated_at are blocked; the activation records engage time and elapsed halt time; the time_to_halt_s SLI is catalogued and observed. | pass | passed | `test/quartets/test_tc_ks_killswitch.py::test_time_to_halt_is_measured_and_every_later_approval_is_blocked` |
| negative | TC-KS-003 | One person (or two from the same line) cannot deactivate: the activation stays active and pending. | pass | passed | `test/quartets/test_tc_ks_killswitch.py::test_single_person_deactivation_stays_pending` |
| negative | TC-KS-008 | A STRATEGY-level switch cancels the strategy's open orders only and leaves other strategies' orders alone (Trading review). | pass | passed | `test/quartets/test_tc_ks_killswitch.py::test_strategy_level_switch_cancels_only_that_strategy` |
| abuse | TC-KS-002 | An AI agent attempting to operate the Kill Switch is denied, audited and alerted (S1). | pass | passed | `test/quartets/test_tc_ks_killswitch.py::test_agent_cannot_activate_or_deactivate` |
| recovery | TC-KS-004 | Two persons from different lines deactivate; account restored via two-person rule; trading resumes; audit chain intact. | pass | passed | `test/quartets/test_tc_ks_killswitch.py::test_two_person_deactivation_restores_with_audit` |
| recovery | TC-KS-007 | Broker down during activation: the switch is engaged first; the failed hook is recorded and alerted (Risk review OBJ-1). | pass | passed | `test/quartets/test_tc_ks_killswitch.py::test_kill_switch_engages_even_when_a_hook_fails` |
| recovery | TC-KS-010 | A STRATEGY-level activation (no account halt to fall back on) and its pending first-person deactivation survive a restart: the rebuilt platform still halts intents and revokes agents; the second person completes the deactivation after the restart (R-23). | pass | passed | `test/quartets/test_tc_ks_killswitch.py::test_activation_survives_restart_and_two_person_deactivation_spans_it` |

Quartet complete: yes. Records: 14.
