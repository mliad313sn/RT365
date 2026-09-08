# TC-E2E — Journeys through the BFF

Control: Journeys through the BFF — Requirement: FR-16 — RTM row: FR-16 — Owner: Frontend Lead — Reviewer (≠ owner): QA Lead — **signature pending** (generated evidence is never self-certified [Source: 00, 11])

Environment tag: dev/sim — Data version: `sim-policy-v0.1 | sim-feed seed=7 | tool_registry 0.1.0` — Generated 2026-09-08T14:38:20.945658+00:00 at `3628fcdb0753bf1148ab694a3cac5d836af2ea09` (tree dirty, tested tree `84774b7e38a3`)

| Quartet | Test ID | Given/When/Then (docstring) | Expected | Actual | Evidence link |
|---|---|---|---|---|---|
| positive | TC-E2E-API | Every BFF route is in contracts/api/API_OPENAPI.yaml and vice versa (path parameter names normalised). | pass | passed | `test/contract/test_openapi_alignment.py::test_bff_routes_match_openapi_paths` |
| positive | TC-E2E-J03 | J-03: agent submits intent via signed identity -> eligibility -> risk -> approval queue -> human approves -> fill -> reconcile -> audit search. | pass | passed | `test/e2e/test_journeys_and_bff.py::test_j03_supervised_order_end_to_end` |
| negative | TC-E2E-J05 | J-05: risk officer activates the Kill Switch; a second person from another line is needed to deactivate; agents/traders denied. | pass | passed | `test/e2e/test_journeys_and_bff.py::test_j05_kill_switch_via_api` |
| abuse | TC-E2E-SCHEMA | Unknown field -> 400; research-only strategy identity -> 403; unsigned bearer -> 403; human without MFA -> 401. | pass | passed | `test/e2e/test_journeys_and_bff.py::test_schema_violation_and_non_allowlisted_agent` |
| abuse | TC-E2E-AUTH | Agent/system roles cannot be asserted through the human path; the BFF refuses to start outside RT_ENV=sim (R-06). | pass | passed | `test/e2e/test_journeys_and_bff.py::test_dev_header_auth_refuses_non_human_roles_and_non_sim_env` |
| recovery | TC-E2E-J06 | J-06: reconciliation break visible to operations; resolved with two-person confirmation; limits go through maker-checker. | pass | passed | `test/e2e/test_journeys_and_bff.py::test_j06_break_ticket_via_api` |

Quartet complete: yes. Records: 6.
