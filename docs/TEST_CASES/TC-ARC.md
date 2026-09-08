# TC-ARC — ARC

Control: ARC — Requirement: - — RTM row: - — Owner: Backend Lead — Reviewer (≠ owner): pending — **signature pending** (generated evidence is never self-certified [Source: 00, 11])

Environment tag: dev/sim — Data version: `sim-policy-v0.1 | sim-feed seed=7 | tool_registry 0.1.0` — Generated 2026-09-08T15:56:20.950210+00:00 at `0bc7beb7576a32493c52a4951eaf6a799c350f11` (tree dirty, tested tree `7337735ef85d`)

| Quartet | Test ID | Given/When/Then (docstring) | Expected | Actual | Evidence link |
|---|---|---|---|---|---|
| positive | TC-ARC-002 | The BFF under apps/ imports FastAPI (the edge is where the framework lives) and the scanner reports it there only, never under the engine roots. | pass | passed | `test/contract/test_engine_import_ban.py::test_edges_may_import_the_framework_and_engines_use_only_the_kernel` |
| negative | TC-ARC-001 | Every module under the engine roots is free of fastapi/starlette/uvicorn/httpx/requests imports (ADR-009: framework at the edges only). | pass | passed | `test/contract/test_engine_import_ban.py::test_engines_do_not_import_the_web_framework` |
| abuse | TC-ARC-003 | Aliased, nested, dotted, try-guarded and importlib/__import__ literal imports of a banned package are all reported. | pass | passed | `test/contract/test_engine_import_ban.py::test_disguised_imports_are_caught` |
| recovery | TC-ARC-004 | A planted offender under a copy of an engine root is reported with its path; deleting the import restores an empty report. | pass | passed | `test/contract/test_engine_import_ban.py::test_offender_is_located_and_removal_restores_green` |

Quartet complete: yes. Records: 4.
