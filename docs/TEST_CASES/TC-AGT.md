# TC-AGT — Agent roster and write-scope guard (three lines of defense for agents)

Control: Agent roster and write-scope guard (three lines of defense for agents) — Requirement: NFR-SEC-02 — RTM row: NFR-SEC-02 — Owner: Product Owner / Delivery Orchestrator — Reviewer (≠ owner): MCP Security Agent — **signature pending** (generated evidence is never self-certified [Source: 00, 11])

Environment tag: dev/sim — Data version: `sim-policy-v0.1 | sim-feed seed=7 | tool_registry 0.1.0` — Generated 2026-09-08T15:13:31.873260+00:00 at `b40664d2ec081d5121204d3e1433512851b5996a` (tree clean, tested tree `a40288fadaa2`)

| Quartet | Test ID | Given/When/Then (docstring) | Expected | Actual | Evidence link |
|---|---|---|---|---|---|
| positive | TC-AGT-001 | Every goals/ prompt has exactly one generated agent that matches it; an agent may edit the artefacts its prompt says it owns and the shared ledgers. | pass | passed | `test/quartets/test_tc_agt_agent_guard.py::test_agents_are_generated_from_goals_and_owners_may_edit_their_artefacts` |
| negative | TC-AGT-002 | A 2nd-line agent cannot write the code it reviews, a builder cannot write 2nd-line policy, the Product Owner cannot write risk policy, and 3rd-line agents own no code or policy at all. | pass | passed | `test/quartets/test_tc_agt_agent_guard.py::test_lines_are_segregated` |
| abuse | TC-AGT-003 | Path traversal, absolute paths outside the repository, unknown agents, missing file paths and CODEOWNERS edits are all denied. | pass | passed | `test/quartets/test_tc_agt_agent_guard.py::test_guard_resists_traversal_unknown_agents_and_human_only_files` |
| recovery | TC-AGT-004 | Without a roster every write is denied; regenerating from goals/ restores the exact roster and the drift check passes again. | pass | passed | `test/quartets/test_tc_agt_agent_guard.py::test_missing_roster_fails_closed_and_regeneration_restores_it` |

Quartet complete: yes. Records: 4.
