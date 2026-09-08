# TC-AP — Human approval, maker != checker

Control: Human approval, maker != checker — Requirement: FR-12 — RTM row: FR-12 — Owner: Backend Lead — Reviewer (≠ owner): Chief Risk Agent — **signature pending** (generated evidence is never self-certified [Source: 00, 11])

Environment tag: dev/sim — Data version: `sim-policy-v0.1 | sim-feed seed=7 | tool_registry 0.1.0` — Generated 2026-09-08T15:31:50.784178+00:00 at `600fc397ec6f6d8bc47f4a1149af32c73bfa54f6` (tree dirty, tested tree `0ca77ddfb9cf`)

| Quartet | Test ID | Given/When/Then (docstring) | Expected | Actual | Evidence link |
|---|---|---|---|---|---|
| positive | TC-AP-001 | Supervised mode: intent -> approval queue -> a human checker != maker approves -> order executes; approval.recorded audited. | pass | passed | `test/quartets/test_tc_ap_approval.py::test_supervised_order_approved_by_different_human` |
| negative | TC-AP-002 | The maker (submitter) is denied as checker; a role without approve permission is denied. | pass | passed | `test/quartets/test_tc_ap_approval.py::test_maker_cannot_check_own_intent` |
| abuse | TC-AP-003 | An AI agent cannot act as approver; a decision that is not REQUIRES_HUMAN_APPROVAL cannot be queued (self-approval path absent). | pass | passed | `test/quartets/test_tc_ap_approval.py::test_agent_cannot_approve_and_cannot_enqueue_approved_decisions` |
| abuse | TC-AP-005 | The registered owner of the strategy (quant.fixture) is refused as approver even with an approving role; another PM may approve (IVA-04). | pass | passed | `test/quartets/test_tc_ap_approval.py::test_strategy_owner_cannot_approve_own_strategy` |
| recovery | TC-AP-004 | Expiry before approval -> EXPIRED, never executed; Kill Switch after approval blocks execution; decline path recorded. | pass | passed | `test/quartets/test_tc_ap_approval.py::test_expired_or_killed_intent_not_executed_after_approval` |

Quartet complete: yes. Records: 5.
