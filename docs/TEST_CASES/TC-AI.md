# TC-AI — MCP governance and injection defence

Control: MCP governance and injection defence — Requirement: FR-09 — RTM row: FR-09 — Owner: Backend Lead — Reviewer (≠ owner): MCP Security Agent — **signature pending** (generated evidence is never self-certified [Source: 00, 11])

Environment tag: dev/sim — Data version: `sim-policy-v0.1 | sim-feed seed=7 | tool_registry 0.1.0` — Generated 2026-09-08T15:42:45.979018+00:00 at `caab32e1e2e735a62348ebeca8f1e2a2bea8b8d4` (tree dirty, tested tree `3d4956157547`)

| Quartet | Test ID | Given/When/Then (docstring) | Expected | Actual | Evidence link |
|---|---|---|---|---|---|
| positive | TC-AI-001 | All six allowed capabilities respond; account state is masked; depth hidden without entitlement; submit writes to the queue only. | pass | passed | `test/quartets/test_tc_ai_mcp.py::test_allowlisted_tools_work_with_masking` |
| positive | TC-AI-012 | An MCP client initialises, lists exactly the six registered tools with their signed input schemas, and a read call returns masked output. | pass | passed | `test/quartets/test_tc_ai_stdio.py::test_stdio_server_lists_exactly_the_six_tools_and_serves_them` |
| negative | TC-AI-002 | Untrusted text is delimited as data; unknown fields, hallucinated symbols and out-of-scope intents are rejected at schema validation. | pass | passed | `test/quartets/test_tc_ai_mcp.py::test_injected_instruction_ignored_and_bad_intents_rejected` |
| negative | TC-AI-010 | No key outside dev/sim -> refused; fixture registry outside sim -> refused; strategy_version pinned; handler errors audited. | pass | passed | `test/quartets/test_tc_ai_mcp.py::test_registry_key_and_environment_fail_closed` |
| negative | TC-AI-013 | Malformed JSON, unknown methods, missing tool names and schema-invalid arguments are answered with errors, never with a handler call. | pass | passed | `test/quartets/test_tc_ai_stdio.py::test_stdio_server_rejects_malformed_and_unsupported_requests` |
| abuse | TC-AI-003 | Forbidden capability, tool not granted to the strategy, quota, oversize payload, canary and bad signature are all denied with alerts/audit. | pass | passed | `test/quartets/test_tc_ai_mcp.py::test_non_allowlisted_tool_denied_and_alerted` |
| abuse | TC-AI-005 | mcp_servers never imports execution, broker, vault, kill switch, policy-mutation or signing modules; egress denies vault/broker; unsigned registry refused. | pass | passed | `test/quartets/test_tc_ai_mcp.py::test_forbidden_capabilities_are_structurally_impossible` |
| abuse | TC-AI-006 | After an allowed run_simulation call, a plane crossing on the live platform still raises the S1 plane.deny alert (MCP review OBJ-1). | pass | passed | `test/quartets/test_tc_ai_mcp.py::test_run_simulation_cannot_touch_live_monitoring` |
| abuse | TC-AI-009 | The same signed call (nonce) is accepted once; a replay is refused and a duplicate intent never enters the queue (T-08). | pass | passed | `test/quartets/test_tc_ai_mcp.py::test_signed_call_replay_rejected` |
| abuse | TC-AI-011 | The published dev key is refused outside dev/sim however it is supplied (IVA-07); replay is refused across issuer restarts (IVA-08). | pass | passed | `test/quartets/test_tc_ai_mcp.py::test_dev_key_blacklisted_outside_sim_and_nonce_journal_survives_restart` |
| abuse | TC-AI-014 | Forbidden tool names are denied with an alert, oversize frames are dropped without parsing, a client-supplied identity is ignored and the transport module has no broker/execution/shell import. | pass | passed | `test/quartets/test_tc_ai_stdio.py::test_stdio_server_cannot_reach_forbidden_capabilities` |
| recovery | TC-AI-004 | Tool revoked mid-session -> denied; expired identity -> denied; registry signature revoked -> all tools refuse; restore works. | pass | passed | `test/quartets/test_tc_ai_mcp.py::test_revocation_mid_session_and_registry_revocation` |
| recovery | TC-AI-008 | Tool and agent revocations are persisted; a rebuilt runtime (restart) still refuses them (MCP review OBJ-3d). | pass | passed | `test/quartets/test_tc_ai_mcp.py::test_revocation_survives_runtime_restart` |
| recovery | TC-AI-015 | Registry revocation is honoured on the next frame (every call refused), two-person restore re-enables calls, and a malformed frame never stops the server. | pass | passed | `test/quartets/test_tc_ai_stdio.py::test_stdio_server_honours_registry_revocation_and_keeps_serving_after_bad_frames` |

Quartet complete: yes. Records: 14.
