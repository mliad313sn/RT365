# TC-BR — Broker adapter certification

Control: Broker adapter certification — Requirement: FR-02 — RTM row: FR-02 — Owner: Broker-Connector Lead — Reviewer (≠ owner): Trading Domain Lead — **signature pending** (generated evidence is never self-certified [Source: 00, 11])

Environment tag: dev/sim — Data version: `sim-policy-v0.1 | sim-feed seed=7 | tool_registry 0.1.0` — Generated 2026-09-08T15:48:15.949441+00:00 at `5bf73b616d466abb75922409297f9ef323a3239c` (tree clean, tested tree `18b0a7418af7`)

| Quartet | Test ID | Given/When/Then (docstring) | Expected | Actual | Evidence link |
|---|---|---|---|---|---|
| positive | TC-BR-001 | Adapter authenticates only via vault reference and rotates credentials; raw credentials are refused. | pass | passed | `test/quartets/test_tc_br_broker.py::test_vault_auth_and_rotation` |
| negative | TC-BR-002 | Unsupported order type is rejected by capability discovery before submission. | pass | passed | `test/quartets/test_tc_br_broker.py::test_capability_discovery_rejects_unsupported` |
| abuse | TC-BR-003 | Each supported order type acks; partial fills; cancel/replace; broker rejects map to reasons. | pass | passed | `test/quartets/test_tc_br_broker.py::test_order_types_partial_fill_cancel_replace_reject` |
| recovery | TC-BR-004 | Disconnected submissions raise; after reconnect the same client_order_id is deduplicated; statements download. | pass | passed | `test/quartets/test_tc_br_broker.py::test_reconnection_and_idempotent_resubmission` |

Quartet complete: yes. Records: 4.
