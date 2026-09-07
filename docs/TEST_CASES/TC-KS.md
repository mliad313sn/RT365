# TC-KS — Kill Switch

Control: Kill Switch — Requirement: FR-17 — RTM row: FR-17 — Owner: Backend Lead — Reviewer (≠ owner): Chief Risk Agent — **signature pending** (generated evidence is never self-certified [Source: 00, 11])

Environment tag: dev/sim — Data version: `sim-policy-v0.1 | sim-feed seed=7 | tool_registry 0.1.0` — Generated 2026-09-07T17:33:35.225922+00:00 at `03e673908c3ab4b22bd809990fe06995cc4cf8fb`

| Quartet | Test ID | Given/When/Then (docstring) | Expected | Actual | Evidence link |
|---|---|---|---|---|---|
| positive | TC-KS-001 | Activation: open orders cancelled, agent identities revoked, evidence snapshot hashed, notification sent, new intents HALTED. | pass | passed | `test/quartets/test_tc_ks_killswitch.py::test_activation_blocks_new_risk_and_cancels_open_orders` |
| positive | TC-KS-005 | Each of the six levels is consulted by the risk engine through the account snapshot flags. | pass | passed | `test/quartets/test_tc_ks_killswitch.py::test_every_level_blocks_matching_intents[PLATFORM-*]` |
| positive | TC-KS-005 | Each of the six levels is consulted by the risk engine through the account snapshot flags. | pass | passed | `test/quartets/test_tc_ks_killswitch.py::test_every_level_blocks_matching_intents[TENANT-tenant-sim]` |
| positive | TC-KS-005 | Each of the six levels is consulted by the risk engine through the account snapshot flags. | pass | passed | `test/quartets/test_tc_ks_killswitch.py::test_every_level_blocks_matching_intents[STRATEGY-strat-sma-xover]` |
| positive | TC-KS-005 | Each of the six levels is consulted by the risk engine through the account snapshot flags. | pass | passed | `test/quartets/test_tc_ks_killswitch.py::test_every_level_blocks_matching_intents[ASSET-SIMEQ1]` |
| positive | TC-KS-005 | Each of the six levels is consulted by the risk engine through the account snapshot flags. | pass | passed | `test/quartets/test_tc_ks_killswitch.py::test_every_level_blocks_matching_intents[VENUE-SIMX]` |
| positive | TC-KS-006 | Runtime loss-limit breach -> risk.halt.v1 event -> Kill Switch at account level without human action. | pass | passed | `test/quartets/test_tc_ks_killswitch.py::test_runtime_monitor_triggers_kill_switch` |
| negative | TC-KS-003 | One person (or two from the same line) cannot deactivate: the activation stays active and pending. | pass | passed | `test/quartets/test_tc_ks_killswitch.py::test_single_person_deactivation_stays_pending` |
| abuse | TC-KS-002 | An AI agent attempting to operate the Kill Switch is denied, audited and alerted (S1). | pass | passed | `test/quartets/test_tc_ks_killswitch.py::test_agent_cannot_activate_or_deactivate` |
| recovery | TC-KS-004 | Two persons from different lines deactivate; account restored via two-person rule; trading resumes; audit chain intact. | pass | passed | `test/quartets/test_tc_ks_killswitch.py::test_two_person_deactivation_restores_with_audit` |

Quartet complete: yes. Records: 10.
