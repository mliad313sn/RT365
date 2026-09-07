# Session packet C10 — Test Master Plan (blueprint 11)

| Session | Date | Environment | Status | Documented by |
|---|---|---|---|---|
| C10 | 2026-09-07 | dev/sim only | Committee working draft; not a release artefact | Program Orchestrator (recommends, never approves) |

Every evidence record in this build carries `environment: dev` and `reviewer: pending` by construction (`test/evidence_plugin.py`). A passing suite is not a gate pass: the QA Lead and a 2nd-line owner must sign rows in `docs/AUDIT_EVIDENCE_INDEX.md`, and the IVA must verify them.

## 1 Roles

| Role in session | Person/role | Line |
|---|---|---|
| Accountable | QA Lead (test strategy, evidence records) | Assurance (3rd per `rtcore.lines.ROLE_LINE`) |
| Builder (code) | Backend Lead — wrote both the code under test and the tests (`evidence_plugin.py` records `owner: "Backend Lead (author of code and test)"`); SRE Lead — `.github/workflows/ci.yml`, `Makefile`; Broker-Connector Lead — `certification.py`, `scripts/certify_broker.py` | 1st |
| Consulted | Performance & Chaos Leads, Red-Team & Pen-Test Leads, Accessibility Lead, all engineering leads | Assurance / 3rd / 1st |
| Challenger | Backend Lead as reviewer of `docs/TEST_STRATEGY.md` (different line from QA Lead) — for the *code-and-test single author* finding the challenger is the Chief Risk Agent (2nd line) | 1st / 2nd |
| Assurance / IVA | Independent Validation Agent (evidence review; veto) | 3rd |

Segregation: author != reviewer != approver; nothing here is self-certified. The QA Lead did not write production code under test; the Backend Lead did write both code and tests, which is recorded as R-08 below.

## 2 Purpose

- [Source: 11] Test families: unit, property-based, contract, integration, e2e; historical replay and deterministic simulation; broker sandbox certification; load/spike/soak/latency/failover/capacity; chaos; security; model; compliance, accessibility, localisation, DR, operational readiness. Evidence record fields: requirement ID, environment, data version, expected, actual, evidence link, owner, reviewer.
- [Source: 00] Control quartet (positive/negative/abuse/recovery) for every critical control; environment ladder dev → sim → shadow → paper → supervised pilot → capped autonomous pilot → controlled GA.
- [Committee] A control without all four quartet cells is not "tested"; tests tagged with the lowest environment in which they must pass; broker certification checklist per adapter; model test suite on every prompt/model change.
- [Open: O-27], [Open: O-28] raised below; [Open: O-23] accessibility (C8).

## 3 Decisions and ADRs

| ID | Decision | Alternatives considered | Why chosen | Status |
|---|---|---|---|---|
| ADR-020 [Committee] | Evidence generated from pytest markers `tc`, `req`, `quartet`, `env` (declared in `pyproject.toml [tool.pytest.ini_options].markers`) by `test/evidence_plugin.py` → `test/evidence/evidence_index.json`; `scripts/evidence_report.py` renders `docs/TEST_CASES/EVIDENCE_REPORT.md` with quartet coverage per area; reviewer is always `pending` | (a) manual evidence spreadsheets; (b) test-management SaaS | (a) drifts from the suite and invites self-certification; (b) vendor dependency before Gate B. Plugin makes "reviewer ≠ owner" structural | Proposed, pending CAB |
| ADR-021 [Committee] | CI is the gate skeleton (`.github/workflows/ci.yml`): lint, typecheck, `make schemas` (ADR-005), `make policy-check` (network policies, signed tool registry), `make secret-scan`, full suite with evidence, a separate determinism step (`test/quartets/test_tc_rk_determinism.py` + `test/property`), evidence report, broker certification harness, CycloneDX SBOM, artefact upload | (a) nightly-only pipeline; (b) pre-commit hooks only | Every PR must fail on any determinism divergence (Gate C blocker); local `make all` mirrors CI | Proposed, pending CAB |
| ADR-022 [Committee] | Broker sandbox certification as code: `run_certification` (`connectors/brokers/broker_adapters/certification.py`) executes the C10 §4 checklist and `certification_markdown` writes `docs/BROKER_CERTIFICATIONS/<broker>.md` with "Reviewer: Trading Domain Lead — pending" | (a) manual checklist; (b) vendor conformance suite | (a) unrepeatable; (b) assumes broker capability, which is never assumed [Source: 00] | Proposed, pending Trading Domain Lead |
| D-C10-1 [Committee] | Environment tag defaults to `dev`; sim/shadow/paper tags exist but are unused | (a) tag every test now; (b) no tags | Deferred until a sim environment beyond in-process exists → O-27 | Proposed |
| D-C10-2 [Committee] | Property-based determinism tests with Hypothesis (`test/property/test_risk_determinism_property.py`) in addition to example-based TC-RK-001..004 | (a) example tests only; (b) formal verification | Property tests give replica-independence evidence cheaply; formal methods out of reach before Gate B | Proposed, pending Chief Risk Agent |

## 4 RTM rows

Test inventory (working tree, 2026-09-07): 15 test modules, 89 test functions, 104 evidence records (parametrisation expands TC-KS-005 and TC-RK cases), quartet marks positive 20 / negative 21 / abuse 17 / recovery 16, 15/15 areas with a full quartet per `docs/TEST_CASES/EVIDENCE_REPORT.md`.

| Area (file) | Tests | TC IDs | Requirement marks |
|---|---|---|---|
| `test/quartets/test_tc_rk_determinism.py` | 12 | TC-RK-001..004, 010..016 | FR-11 |
| `test/quartets/test_tc_ex_execution.py` | 7 | TC-EX-001..006 | FR-13, NFR-CON-02 |
| `test/quartets/test_tc_ks_killswitch.py` | 7 | TC-KS-001..006 | FR-17 |
| `test/quartets/test_tc_ai_mcp.py` | 6 | TC-AI-001..005 | FR-09 |
| `test/quartets/test_tc_cp_eligibility.py` | 6 | TC-CP-001..006 | FR-15 |
| `test/quartets/test_tc_ap_approval.py`, `_aud_audit.py`, `_br_broker.py`, `_id_identity.py`, `_md_marketdata.py`, `_net_planes.py`, `_ob_observability.py`, `_rc_reconciliation.py` | 4 each | TC-AP/AUD/BR/ID/MD/NET/OB/RC-001..004 | FR-12, NFR-AUD-01, FR-02, FR-01, FR-03, NFR-SEC-01, NFR-OBS-01/NFR-PRV-01, FR-14 |
| `test/integration/test_backtest_single_code_path.py` | 5 | TC-BT-001..004 (+1 untagged) | FR-06, FR-08 |
| `test/e2e/test_journeys_and_bff.py` | 4 | TC-E2E-J03, J05, J06, SCHEMA | FR-12, FR-17, FR-09, FR-14 |
| `test/contract/test_openapi_alignment.py` | 7 | untagged | contracts/api, events, tool registry, reason codes |
| `test/property/test_risk_determinism_property.py` | 3 | untagged | NFR-DET-01 |

| Requirement | Architecture element | Implementation owner | Control | Test IDs | Evidence path | Gate |
|---|---|---|---|---|---|---|
| [Source: 11] evidence record | `evidence_plugin.py`, `evidence_report.py` | QA Lead (SRE Lead builds) | Reviewer ≠ owner enforced by `reviewer: pending` | all tagged tests | `test/evidence/evidence_index.json`; `docs/TEST_CASES/EVIDENCE_REPORT.md` | C |
| NFR-DET-01 | CI determinism step | Backend Lead | Fail on any divergence | TC-RK-001..004; `test_decide_is_pure_and_precedence_holds` | `.github/workflows/ci.yml` | C |
| FR-02 / C10 §4 | `run_certification`, `scripts/certify_broker.py` | Broker-Connector Lead | Checklist rows TC-BR-001..007 | TC-BR-001..004 (`test_tc_br_broker.py`); harness rows TC-BR-001b, 003p/c/r, 005 PASS; TC-BR-006, TC-BR-007 OPEN | `docs/BROKER_CERTIFICATIONS/sim-broker.md` (12 PASS / 2 OPEN) | C |
| NFR-SEC-02 | `make secret-scan`, `make sbom`, `make policy-check` (`scripts/secret_scan.py`, `generate_sbom.py`, `verify_tool_registry.py`, `check_network_policies.py`) | Security Architect | CI gate | GAP — no TC-SEC/TC-SC tests; scripts run in CI only | `security/sbom/`; `security/secret_scan_allowlist.txt` | B |
| [Source: 11] model test suite | `test_tc_ai_mcp.py` | Backend Lead / Model Risk Lead | Injection, unsafe tool selection | TC-AI-002 `test_injected_instruction_ignored_and_bad_intents_rejected`; TC-AI-003 `test_non_allowlisted_tool_denied_and_alerted` | `test/quartets/test_tc_ai_mcp.py` | D |
| [Source: 11] performance, chaos, DR, a11y, localisation, tenancy | — | Performance & Chaos Leads, Accessibility Lead | — | GAP [Open: O-28] | `docs/PERFORMANCE_PLAN.md`, `CHAOS_PLAN.md`, `DR_PLAN.md`, `UAT_PLAN.md` (plans only) | D–F |

## 5 Threat-model delta

| Threat | Boundary | Control in this build | Test | Residual / owner |
|---|---|---|---|---|
| T-07 Insider misuse — self-certified evidence | build → gate | `reviewer: pending` in every record; `AUDIT_EVIDENCE_INDEX.md` requires a different-line reviewer and IVA column | structural (plugin) | Index has no signed rows yet; code and tests share an author → R-08. QA Lead |
| T-10 Dependency compromise | CI | CycloneDX SBOM (`make sbom`); dependencies pinned as `>=` in `pyproject.toml` | GAP | No lockfile / hash pinning; TC-SC-001/002 referenced in `docs/THREAT_MODEL.md` do not exist. Cloud Architect |
| T-05 Credential theft | repo | `scripts/secret_scan.py` in CI | GAP (TC-SEC-001 absent) | Security Architect |
| T-C10-1 Evidence tampering (new) | evidence file | none: `evidence_index.json` is a plain file; git sha recorded as `HEAD` string when not resolvable | GAP | Sign the evidence artefact in CI; anchor sha. SRE Lead |
| T-C10-2 Coverage illusion (new) | quartet report | Report counts marks, not controls: TC-RK shows 30 negative records because of parametrisation; a control with one quartet mark per cell passes "full quartet" | GAP | Quartet completeness must be judged per control (this packet's §6 across sessions), not per area. QA Lead |
| T-04 Model supply chain | registry | `test_tool_registry_policy_invariants`; `scripts/verify_tool_registry.py` | contract test | Signed model artefacts not in scope of this build. Model Risk Lead |

## 6 Control quartet per critical control

| Control | Positive | Negative | Abuse | Recovery |
|---|---|---|---|---|
| Evidence record integrity (reviewer ≠ owner) | `evidence_plugin.py` writes 8 fields incl. `reviewer: pending` (structural, exercised by every tagged test) | GAP — no test that an unreviewed record cannot satisfy a gate row | GAP — tampered `evidence_index.json` | GAP |
| Determinism gate in CI | TC-RK-001 `test_identical_inputs_identical_decision_across_replicas` | TC-RK-002 `test_changed_policy_version_yields_new_decision` | TC-RK-003 `test_tampered_intent_hash_rejected` | TC-RK-004 `test_engine_restart_same_decision_and_fail_closed_on_missing_inputs` |
| Broker sandbox certification | TC-BR-001 `test_vault_auth_and_rotation` | TC-BR-002 `test_capability_discovery_rejects_unsupported` | TC-BR-003 `test_order_types_partial_fill_cancel_replace_reject` | TC-BR-004 `test_reconnection_and_idempotent_resubmission` |
| Model test suite (hallucination, malicious context, seeds, drift, unsafe tool) | TC-AI-001 `test_allowlisted_tools_work_with_masking` | TC-AI-002 (injected instruction ignored) | TC-AI-003, TC-AI-005 `test_forbidden_capabilities_are_structurally_impossible` | TC-AI-004 `test_revocation_mid_session_and_registry_revocation`; seeds/drift GAP |
| Contract alignment (schema-first) | `test_trade_intent_matches_openapi`, `test_decision_record_matches_openapi` | `test_event_schemas_have_no_drift` | GAP | GAP |
| Environment-ladder tagging | GAP (all records `dev`) | GAP | GAP | GAP — [Open: O-27] |

## 7 Evidence list

| Evidence | Path |
|---|---|
| Evidence plugin, report generator, fixtures/actors | `test/evidence_plugin.py`; `scripts/evidence_report.py`; `test/conftest.py` |
| Test modules | `test/quartets/*.py`; `test/integration/test_backtest_single_code_path.py`; `test/e2e/test_journeys_and_bff.py`; `test/contract/test_openapi_alignment.py`; `test/property/test_risk_determinism_property.py` |
| Generated evidence (2026-09-07T17:28:57Z, sha `HEAD`, exit 0, 104 records passed) | `test/evidence/evidence_index.json`; `docs/TEST_CASES/EVIDENCE_REPORT.md` |
| Certification harness and output | `connectors/brokers/broker_adapters/certification.py`; `scripts/certify_broker.py`; `docs/BROKER_CERTIFICATIONS/sim-broker.md`, `TEMPLATE.md` |
| CI and local targets | `.github/workflows/ci.yml`; `Makefile`; `pyproject.toml` (markers, pythonpath) |
| Plans (documents only) | `docs/TEST_STRATEGY.md`; `docs/TEST_CASES/README.md`; `docs/PERFORMANCE_PLAN.md`; `docs/CHAOS_PLAN.md`; `docs/RED_TEAM_PLAN.md`; `docs/UAT_PLAN.md`; `docs/DEFINITION_OF_DONE.md` |
| Governance | `docs/COMMITTEE_DEEP_DIVE.md` §C10; `docs/AUDIT_EVIDENCE_INDEX.md`; `goals/20_qa_lead.md`; `goals/28_independent_validation_agent.md` |

## 8 RAID entries, assumptions, confidence, provenance

| ID | Type | Item | Owner | Needed by | Status |
|---|---|---|---|---|---|
| O-27 | Gap | Environment-ladder tags unused: all 104 records are `dev`; no sim/shadow/paper environment exists to tag against; `TEST_STRATEGY.md` coverage report before each gate not yet produced | QA Lead | Gate C | Open |
| O-28 | Gap | Test families absent: performance/load/spike/soak, chaos/failover, security (TC-SEC), supply chain (TC-SC), tenancy (TC-TEN), accessibility (TC-A11Y), DR, localisation; `docs/THREAT_MODEL.md` cites TC-SEC-001, TC-SC-001/002, TC-TEN-003, TC-PERF-004 that do not exist | QA Lead; Performance & Chaos Leads; Security Architect; Accessibility Lead | Gate C (perf baseline), D (security), F (a11y, DR) | Open |
| R-08 | Risk | Code and tests share one author (Backend Lead); `AUDIT_EVIDENCE_INDEX.md` has no signed rows; until the QA Lead/2nd-line reviewers sign and the IVA verifies, the 104 green records are builder assertions, not evidence | QA Lead (IVA verifies) | Gate C | Open |

Assumptions: pytest 8 + Hypothesis per `pyproject.toml [dev]`; CI has not been observed running in this session (workflow file read only). Confidence: high on inventory counts (derived from the working tree); medium on CI behaviour (unexecuted here); none on non-functional families (absent). Provenance: files read on 2026-09-07; evidence index sha `HEAD`. Reviewer: Backend Lead (strategy) / Chief Risk Agent (R-08) pending; approver: CAB pending; IVA verdict pending.
