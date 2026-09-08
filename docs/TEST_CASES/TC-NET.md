# TC-NET — Plane topology / network policy

Control: Plane topology / network policy — Requirement: NFR-SEC-01 — RTM row: NFR-SEC-01 — Owner: Cloud Architect — Reviewer (≠ owner): Security Architect — **signature pending** (generated evidence is never self-certified [Source: 00, 11])

Environment tag: dev/sim — Data version: `sim-policy-v0.1 | sim-feed seed=7 | tool_registry 0.1.0` — Generated 2026-09-08T16:33:28.271529+00:00 at `47fd3496e35791bcdca06431ae1fb9e1f5affe9a` (tree clean, tested tree `96409b1389a7`)

| Quartet | Test ID | Given/When/Then (docstring) | Expected | Actual | Evidence link |
|---|---|---|---|---|---|
| positive | TC-NET-001 | Analytics plane may reach the Control plane only through the intent queue channel. | pass | passed | `test/quartets/test_tc_net_planes.py::test_analytics_to_control_via_intent_queue_allowed` |
| negative | TC-NET-002 | A call from the Analytics plane to the Execution gateway is denied and raises an S1 plane.deny alert. | pass | passed | `test/quartets/test_tc_net_planes.py::test_analytics_to_execution_denied_with_alert` |
| abuse | TC-NET-003 | No route exists from Analytics (MCP) to the vault or brokers, in-process and in the Kubernetes policies. | pass | passed | `test/quartets/test_tc_net_planes.py::test_mcp_to_vault_and_broker_denied` |
| recovery | TC-NET-004 | A policy edit that opens analytics->execution fails the invariant check; restoring the file passes again. | pass | passed | `test/quartets/test_tc_net_planes.py::test_policy_change_detected_and_restore` |

Quartet complete: yes. Records: 4.
