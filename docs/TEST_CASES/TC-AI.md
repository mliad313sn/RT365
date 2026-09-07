# TC-AI — MCP governance and injection defence

Control: MCP governance and injection defence — Requirement: FR-09 — RTM row: FR-09 — Owner: Backend Lead — Reviewer (≠ owner): MCP Security Agent — **signature pending** (generated evidence is never self-certified [Source: 00, 11])

Environment tag: dev/sim — Data version: `sim-policy-v0.1 | sim-feed seed=7 | tool_registry 0.1.0` — Generated 2026-09-07T17:33:35.225922+00:00 at `03e673908c3ab4b22bd809990fe06995cc4cf8fb`

| Quartet | Test ID | Given/When/Then (docstring) | Expected | Actual | Evidence link |
|---|---|---|---|---|---|
| positive | TC-AI-001 | All six allowed capabilities respond; account state is masked; depth hidden without entitlement; submit writes to the queue only. | pass | passed | `test/quartets/test_tc_ai_mcp.py::test_allowlisted_tools_work_with_masking` |
| negative | TC-AI-002 | Untrusted text is delimited as data; unknown fields, hallucinated symbols and out-of-scope intents are rejected at schema validation. | pass | passed | `test/quartets/test_tc_ai_mcp.py::test_injected_instruction_ignored_and_bad_intents_rejected` |
| abuse | TC-AI-003 | Forbidden capability, tool not granted to the strategy, quota, oversize payload, canary and bad signature are all denied with alerts/audit. | pass | passed | `test/quartets/test_tc_ai_mcp.py::test_non_allowlisted_tool_denied_and_alerted` |
| abuse | TC-AI-005 | mcp_servers never imports execution, broker, vault, kill switch or policy-mutation modules; egress denies vault/broker; unsigned registry refused. | pass | passed | `test/quartets/test_tc_ai_mcp.py::test_forbidden_capabilities_are_structurally_impossible` |
| recovery | TC-AI-004 | Tool revoked mid-session -> denied; expired identity -> denied; registry signature revoked -> all tools refuse; restore works. | pass | passed | `test/quartets/test_tc_ai_mcp.py::test_revocation_mid_session_and_registry_revocation` |

Quartet complete: yes. Records: 5.
