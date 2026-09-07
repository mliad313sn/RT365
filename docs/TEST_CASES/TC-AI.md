# TC-AI — MCP governance and injection defence

Control: MCP governance and injection defence — Requirement: FR-09 — RTM row: FR-09 — Owner: Backend Lead — Reviewer (≠ owner): MCP Security Agent — **signature pending** (generated evidence is never self-certified [Source: 00, 11])

Environment tag: dev/sim — Data version: `sim-policy-v0.1 | sim-feed seed=7 | tool_registry 0.1.0` — Generated 2026-09-07T18:09:37.793153+00:00 at `78742a240edbfb535d75ff8c942a4b2a9b6a2bb1`

| Quartet | Test ID | Given/When/Then (docstring) | Expected | Actual | Evidence link |
|---|---|---|---|---|---|
| positive | TC-AI-001 | All six allowed capabilities respond; account state is masked; depth hidden without entitlement; submit writes to the queue only. | pass | passed | `test/quartets/test_tc_ai_mcp.py::test_allowlisted_tools_work_with_masking` |
| negative | TC-AI-002 | Untrusted text is delimited as data; unknown fields, hallucinated symbols and out-of-scope intents are rejected at schema validation. | pass | passed | `test/quartets/test_tc_ai_mcp.py::test_injected_instruction_ignored_and_bad_intents_rejected` |
| negative | TC-AI-010 | No key outside dev/sim -> refused; fixture registry outside sim -> refused; strategy_version pinned; handler errors audited. | pass | passed | `test/quartets/test_tc_ai_mcp.py::test_registry_key_and_environment_fail_closed` |
| abuse | TC-AI-003 | Forbidden capability, tool not granted to the strategy, quota, oversize payload, canary and bad signature are all denied with alerts/audit. | pass | passed | `test/quartets/test_tc_ai_mcp.py::test_non_allowlisted_tool_denied_and_alerted` |
| abuse | TC-AI-005 | mcp_servers never imports execution, broker, vault, kill switch or policy-mutation modules; egress denies vault/broker; unsigned registry refused. | pass | passed | `test/quartets/test_tc_ai_mcp.py::test_forbidden_capabilities_are_structurally_impossible` |
| abuse | TC-AI-006 | After an allowed run_simulation call, a plane crossing on the live platform still raises the S1 plane.deny alert (MCP review OBJ-1). | pass | passed | `test/quartets/test_tc_ai_mcp.py::test_run_simulation_cannot_touch_live_monitoring` |
| abuse | TC-AI-009 | The same signed call (nonce) is accepted once; a replay is refused and a duplicate intent never enters the queue (T-08). | pass | passed | `test/quartets/test_tc_ai_mcp.py::test_signed_call_replay_rejected` |
| recovery | TC-AI-004 | Tool revoked mid-session -> denied; expired identity -> denied; registry signature revoked -> all tools refuse; restore works. | pass | passed | `test/quartets/test_tc_ai_mcp.py::test_revocation_mid_session_and_registry_revocation` |
| recovery | TC-AI-008 | Tool and agent revocations are persisted; a rebuilt runtime (restart) still refuses them (MCP review OBJ-3d). | pass | passed | `test/quartets/test_tc_ai_mcp.py::test_revocation_survives_runtime_restart` |

Quartet complete: yes. Records: 9.
