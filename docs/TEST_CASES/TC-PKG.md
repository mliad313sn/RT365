# TC-PKG — Distribution: rt365 CLI, resource root, installer fail-closed rules

Control: Distribution: rt365 CLI, resource root, installer fail-closed rules — Requirement: NFR-SEC-02 — RTM row: NFR-SEC-02 — Owner: SRE Lead — Reviewer (≠ owner): Security Architect — **signature pending** (generated evidence is never self-certified [Source: 00, 11])

Environment tag: dev/sim — Data version: `sim-policy-v0.1 | sim-feed seed=7 | tool_registry 0.1.0` — Generated 2026-09-08T08:44:59.790245+00:00 at `e437bd03c9484a51aeccbb27168703ca3ddabc59`

| Quartet | Test ID | Given/When/Then (docstring) | Expected | Actual | Evidence link |
|---|---|---|---|---|---|
| positive | TC-PKG-001 | `rt365 version`, `rt365 check --env sim` and `rt365 probe --env sim` succeed against the source checkout; check reports the registry as a sim fixture and the audit chain intact. | pass | passed | `test/quartets/test_tc_pkg_cli.py::test_cli_version_check_and_probe_run_in_sim` |
| negative | TC-PKG-002 | Without an explicit --env or RT_ENV the CLI refuses to serve or check (IVA-06: unlabelled environment fails closed); a production label refuses the fixture registry. | pass | passed | `test/quartets/test_tc_pkg_cli.py::test_cli_refuses_unlabelled_or_non_sim_environments` |
| abuse | TC-PKG-003 | A resource root pointed at a directory without the signed registry (or with a tampered one) fails closed: no silent fallback to the source tree, no service, no MCP server. | pass | passed | `test/quartets/test_tc_pkg_cli.py::test_resource_root_never_falls_back_silently` |
| recovery | TC-PKG-004 | An installed or frozen build without a source tree recovers by pointing RT365_HOME at a complete resource bundle: the same signed policies, same checks, same probe result. | pass | passed | `test/quartets/test_tc_pkg_cli.py::test_resource_root_override_restores_service_for_installed_builds` |

Quartet complete: yes. Records: 4.
