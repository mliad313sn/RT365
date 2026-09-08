# TC-BT — Backtest single code path and strategy lifecycle

Control: Backtest single code path and strategy lifecycle — Requirement: FR-08 — RTM row: FR-08 — Owner: Quant Research Lead — Reviewer (≠ owner): Model Risk Lead — **signature pending** (generated evidence is never self-certified [Source: 00, 11])

Environment tag: dev/sim — Data version: `sim-policy-v0.1 | sim-feed seed=7 | tool_registry 0.1.0` — Generated 2026-09-08T09:51:24.927874+00:00 at `d1ccb21596456977a7d1b69d4694eb4724546445` (tree dirty, tested tree `4366fa62fdac`)

| Quartet | Test ID | Given/When/Then (docstring) | Expected | Actual | Evidence link |
|---|---|---|---|---|---|
| positive | TC-BT-001 | Replay determinism: same data snapshot -> identical fills and decisions; report carries the disclaimer. | pass | passed | `test/integration/test_backtest_single_code_path.py::test_same_snapshot_identical_fills_and_decisions` |
| negative | TC-BT-002 | x1.5 and x2 cost assumptions produce distinct, labelled reports. | pass | passed | `test/integration/test_backtest_single_code_path.py::test_cost_sensitivity_runs_change_results` |
| abuse | TC-BT-003 | Reading beyond knowledge time raises; the strategy sees only bars ingested before the decision time. | pass | passed | `test/integration/test_backtest_single_code_path.py::test_look_ahead_is_structurally_impossible` |
| recovery | TC-BT-004 | Unregistered results cannot be recorded; owner cannot validate own strategy; promotion needs gates; rollback retires versions. | pass | passed | `test/integration/test_backtest_single_code_path.py::test_strategy_lifecycle_pre_registration_and_segregation` |

Quartet complete: yes. Records: 4.
