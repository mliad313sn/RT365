# Session packet C12 — Backlog, Artefacts & Repository (blueprint 14, 15, 16)

| Session | Date | Environment | Status | Documented by |
|---|---|---|---|---|
| C12 | 2026-09-07 | dev/sim only | Committee working draft; not a release artefact | Program Orchestrator (recommends, never approves) |

This packet inventories what the repository contains against the blueprint layout, epics and artefact catalogue. Presence of a file is not evidence of a working control; see the per-component packets (C01–C11, P1–P6) for tests.

## 1 Roles

| Role in session | Person/role | Line |
|---|---|---|
| Accountable | Program Orchestrator (BACKLOG, RAID, DECISION_LOG, RACI, RTM, RELEASE_CHECKLIST, AUDIT_EVIDENCE_INDEX) | 1st |
| Builder (code) | Backend Lead — `pyproject.toml`, `Makefile`, package layout; SRE Lead — `.github/workflows/ci.yml`, `scripts/bootstrap_repo.sh`, `infra/` | 1st |
| Consulted | All leads (epic owners per `docs/BACKLOG.md`) | 1st / Architecture |
| Challenger | Chief Risk Agent (2nd line; CODEOWNER of `/contracts/`, `/services/risk/`, `/services/killswitch/` — challenges protected-path completeness and drift) | 2nd |
| Assurance / IVA | Independent Validation Agent | 3rd |

Segregation: author != reviewer != approver; nothing here is self-certified. The Program Orchestrator owns the backlog artefacts and therefore cannot review them; the IVA reviews and the CAB approves.

## 2 Purpose

- [Source: 14] Epics E01–E15 with the story template (business value, scope, assumptions, API/event impact, security/privacy impact, observability, migration, rollback, Given/When/Then).
- [Source: 15] Artefact catalogue: every file has an owner and a different-line reviewer, recorded in `docs/RACI.md`.
- [Source: 16] Repository structure: `/apps/web /apps/admin /services/{...} /mcp/{servers,policies} /connectors/{brokers,data-providers} /contracts/{api,events} /infra/{iac,kubernetes} /observability /security /test /docs`.
- [Committee] Protected paths `/services/risk`, `/services/compliance`, `/services/execution`, `/mcp/policies`, `/security`, `/contracts/*` require 2nd-line CODEOWNERS approval; stories carry an RTM link and a control-quartet reference.
- [Open: O-20] CODEOWNERS handles; [Open: O-31], [Open: O-32] raised below.

## 3 Decisions and ADRs

| ID | Decision | Alternatives considered | Why chosen | Status |
|---|---|---|---|---|
| ADR-026 [Committee] | Monorepo with one Python package per bounded context, mapped onto the blueprint directory layout by `[tool.setuptools.package-dir]` in `pyproject.toml` (19 packages: `rtcore`, `market_data`, `strategy_service`, `backtest_engine`, `portfolio_service`, `risk_engine`, `compliance_engine`, `approval_service`, `oms`, `execution_gateway`, `reconciliation_service`, `audit_service`, `killswitch_service`, `identity_service`, `mcp_servers`, `broker_adapters`, `data_providers`, `rtobs`, `web_bff`) | (a) one repository per service; (b) one flat package | (a) fragments CODEOWNERS and the single-code-path backtest (ADR-008); (b) erases bounded-context boundaries and the plane guard | Proposed, pending ARB |
| ADR-027 [Committee] | `Makefile` targets are the only entry points and CI calls the same targets (`lint`, `typecheck`, `schemas`, `policy-check`, `secret-scan`, `test`, `evidence`, `certify-broker`, `sbom`, `run-bff`) | (a) CI-only shell steps; (b) tox/nox matrices | Developers and CI cannot diverge; `make all` reproduces the gate skeleton locally | Proposed, pending CAB |
| ADR-028 [Committee] | Backlog = epics E01–E15 with accountable lead, 2nd-line reviewer and first gate (`docs/BACKLOG.md`), one build prompt per epic (`goals/build/E01..E15_*.md`) carrying scope, requirement IDs, TC IDs and mandatory build rules | (a) issue tracker only; (b) flat feature list | Build prompts embed the prohibitions (no broker route, secret, limit write, audit delete or mode change for AI components) at the point of work | Proposed, pending Product Council |
| D-C12-1 [Committee] | `scripts/bootstrap_repo.sh` remains a kit-to-target generator for new repositories; the live repo has evolved beyond it (CODEOWNERS set, CI steps) | (a) delete the script; (b) regenerate the live repo from it | Keep for new cells/tenants, but drift is a risk → R-10 | Proposed |
| D-C12-2 [Committee] | Contracts are schema-first: `contracts/api/API_OPENAPI.yaml`, `contracts/events/` exported from models by `scripts/export_event_schemas.py --check` and tested by `test/contract/test_openapi_alignment.py` | (a) code-first with generated docs; (b) hand-maintained contracts | Drift fails CI (`make schemas`) | Accepted via ADR-005 |

## 4 RTM rows

Epic build status (working tree, 2026-09-07; "built" = code and quartet tests exist in dev/sim, not an approval):

| Epic | Code area | Status | Quartet TC area |
|---|---|---|---|
| E01 Foundation & identity | `services/identity` | built (header-based principal in BFF, R-06) | TC-ID |
| E02 Market data & instrument master | `services/market-data`, `connectors/data-providers` | built (sim feed only) | TC-MD |
| E03 Broker adapter framework | `connectors/brokers` | built (simulated adapter; harness) | TC-BR |
| E04 Portfolio & accounting | `services/portfolio` | built | via TC-RC |
| E05 Deterministic risk engine + Kill Switch | `services/risk`, `services/killswitch` | built | TC-RK, TC-KS |
| E06 Compliance & eligibility | `services/compliance` | built | TC-CP |
| E07 OMS & execution gateway | `services/oms`, `services/execution` | built | TC-EX, TC-AP |
| E08 Strategy & backtesting | `services/strategy`, `services/backtest` | partial (walk-forward, Monte Carlo, cards absent — O-21/O-22) | TC-BT |
| E09 MCP/AI governance | `mcp/servers`, `mcp/policies` | built | TC-AI, TC-NET |
| E10 Dashboard & mobile | `apps/web` | partial (static console; O-23/O-24); `apps/admin` empty | TC-E2E |
| E11 Audit, surveillance, reporting | `services/audit`, `compliance_engine/surveillance.py` | partial (reporting adapters absent) | TC-AUD, TC-CP-005 |
| E12 Observability & SRE | `observability` | built (in-process; O-25/O-26) | TC-OB |
| E13 Security & privacy | `security/`, `scripts/secret_scan.py`, `generate_sbom.py`, `sign_tool_registry.py` | partial (vault is a `VaultRef` stub; no TC-SEC) | — |
| E14 Billing, support, admin | — | absent (`services/billing`, `support`, `notification`, `tenant` from `bootstrap_repo.sh` do not exist) [Open: O-02] | — |
| E15 Regulatory & market launch | `docs/` only | partial (matrices are templates) | — |

| Requirement | Architecture element | Implementation owner | Control | Test IDs | Evidence path | Gate |
|---|---|---|---|---|---|---|
| [Source: 16] layout | `pyproject.toml` package map; directories present: `apps`, `services`, `mcp`, `connectors`, `contracts`, `infra/{iac,kubernetes}`, `observability`, `security`, `test`, `docs`, `libs` | Backend Lead | Structure matches blueprint | GAP (no structural test) | `pyproject.toml`; `README.md` | B |
| NFR-SEC-02 | `make secret-scan`, `make sbom`, `security/signing/`, `scripts/sign_tool_registry.py`/`verify_tool_registry.py` | Security Architect | CI gate; signed registry | `test_tool_registry_policy_invariants` (contract) | `security/sbom/`; `mcp/policies/tool_registry.signed.json` | B |
| ADR-005 contracts | `contracts/api`, `contracts/events`, `docs/EVENT_CATALOG.md` | Integration Architect | No drift | `test_event_schemas_have_no_drift`, `test_event_catalog_lists_every_schema`, `test_trade_intent_matches_openapi`, `test_decision_record_matches_openapi`, `test_killswitch_levels_match_openapi` | `test/contract/test_openapi_alignment.py` | B |
| [Committee] protected paths | `.github/CODEOWNERS` | SRE Lead | 2nd-line approval | GAP [Open: O-20] | `.github/CODEOWNERS` | B |
| [Source: 15] artefact ownership | Every `docs/*.md` carries an Owner / Reviewer (different line) / Approving body header | Program Orchestrator | Reviewer ≠ owner | GAP (no lint) | `docs/*.md`; `docs/RACI.md` | A |
| [Source: 14] story template | `docs/BACKLOG.md` template incl. control-quartet reference | Program Orchestrator | Stories carry RTM link | GAP — no stories written yet; epics only | `docs/BACKLOG.md` | A |

## 5 Threat-model delta

| Threat | Boundary | Control in this build | Test | Residual / owner |
|---|---|---|---|---|
| T-10 Dependency compromise | build | CycloneDX SBOM; ruff/mypy | GAP | Dependencies are `>=` ranges, no lockfile; TC-SC-001/002 absent (O-28). Cloud Architect |
| T-04 Model / tool supply chain | registry | `tool_registry.signed.json`, `verify_tool_registry.py` in `make policy-check` | `test_tool_registry_policy_invariants`; TC-AI-004 | Signing key management [Open] in `security/signing/`. MCP Security Agent |
| T-07 Insider — merge to control code | repo | CODEOWNERS (placeholder handles) | GAP | O-20; CI does not verify CODEOWNERS syntax. SRE Lead |
| T-C12-1 Kit/repo drift (new) | bootstrap → live | none | GAP | `bootstrap_repo.sh` emits the blueprint-minimum CODEOWNERS (no killswitch, no IVA) and a TODO-only CI; a new cell bootstrapped from it would be weaker than this repo → R-10. SRE Lead |
| T-C12-2 Undocumented decisions (new) | code ↔ ADRs | `docs/ADRs/ADR-001..008` | GAP | Code cites ADR-010 (`platform.py`, `execution_gateway/lease.py`) with no ADR file; ADR-009 also absent → O-32. Enterprise Architect |
| T-12 Audit of repository acts | repo | git history (not read in this session — no git commands run) | — | Program Orchestrator |

## 6 Control quartet per critical control

| Control | Positive | Negative | Abuse | Recovery |
|---|---|---|---|---|
| Protected-path merge approval | GAP (CODEOWNERS present) | GAP | GAP | GAP |
| Contract drift detection (schema-first) | `test_trade_intent_matches_openapi`, `test_decision_record_matches_openapi`, `test_killswitch_levels_match_openapi` | `test_event_schemas_have_no_drift`, `test_event_catalog_lists_every_schema` | GAP | GAP |
| Signed tool registry | `test_tool_registry_policy_invariants`; TC-AI-001 | TC-AI-003 `test_non_allowlisted_tool_denied_and_alerted` | `test_handlers_cannot_be_added_outside_registry`; TC-AI-005 | TC-AI-004 `test_revocation_mid_session_and_registry_revocation` |
| Supply chain (SBOM, secret scan) | `make sbom`, `make secret-scan` run in CI | GAP | GAP | GAP |
| Reason-code / docs generation parity | `test_reason_codes_all_documented` | GAP | GAP | GAP |
| Plane topology in code (`rtcore.planes`) | TC-NET-001 `test_analytics_to_control_via_intent_queue_allowed` | TC-NET-002 `test_analytics_to_execution_denied_with_alert` | TC-NET-003 `test_mcp_to_vault_and_broker_denied` | TC-NET-004 `test_policy_change_detected_and_restore` |

## 7 Evidence list

| Evidence | Path |
|---|---|
| Layout and packaging | `README.md`; `pyproject.toml`; `Makefile`; `libs/core/rtcore/` |
| Bootstrap generator (kit → target) | `scripts/bootstrap_repo.sh` |
| Build prompts per epic (no `goals/build/README.md` exists) | `goals/build/E01_foundation_identity.md` … `E15_regulatory_market_launch.md` |
| Backlog, RACI, decision log, RAID, RTM | `docs/BACKLOG.md`; `docs/RACI.md`; `docs/DECISION_LOG.md`; `docs/RAID_LOG.md`; `docs/REQUIREMENTS_TRACEABILITY.md` |
| Protected paths and CI | `.github/CODEOWNERS`; `.github/workflows/ci.yml` |
| Contracts and policies | `contracts/api/API_OPENAPI.yaml`; `contracts/events/`; `mcp/policies/` (`allowlist.tenant-sim.yaml`, `egress.yaml`, `runtime.yaml`, `tool_registry.json`, `tool_registry.signed.json`) |
| Security artefacts | `security/README.md`; `security/sbom/`; `security/signing/`; `security/secret_scan_allowlist.txt` |
| ADRs | `docs/ADRs/ADR-000-template.md`, `ADR-001` … `ADR-008` |
| Infra skeleton | `infra/Dockerfile.bff`; `infra/docker-compose.yml`; `infra/iac/`; `infra/kubernetes/` |
| Tests | `test/contract/test_openapi_alignment.py`; `test/quartets/test_tc_net_planes.py`; `test/quartets/test_tc_ai_mcp.py`; `test/evidence/evidence_index.json` |

## 8 RAID entries, assumptions, confidence, provenance

| ID | Type | Item | Owner | Needed by | Status |
|---|---|---|---|---|---|
| O-31 | Gap | Blueprint services `tenant`, `notification`, `billing`, `support` and `apps/admin` are absent from the live repo (E14, parts of E10/E11); `goals/build/README.md` referenced by the session brief does not exist; no stories exist under the epics | Program Orchestrator (Backend Lead, Frontend Lead build) | Gate C (E10/E11), F (E14) | Open |
| O-32 | Gap | ADR-009 and ADR-010 are cited in code (`apps/web/web_bff/platform.py`, `services/execution/execution_gateway/lease.py`) but no ADR files exist; ADR-011..028 proposed by sessions C07–C12 need files in `docs/ADRs/` and ARB review | Enterprise Architect | Gate B | Open |
| R-10 | Risk | `scripts/bootstrap_repo.sh` emits a weaker CODEOWNERS (no `/services/killswitch/`, no IVA co-owner) and a TODO-only CI; bootstrapping a new cell from it silently drops controls present here | SRE Lead (Security & Privacy Board reviews) | Gate B | Open |
| O-20 | carried (not yet in RAID_LOG) | CODEOWNERS team handles are placeholders | Program Orchestrator | Gate B | Open |

Assumptions: no git command was run (per session rules); history, branch protection and CI run results were not inspected. Confidence: high on file inventory; medium on epic status classifications (judgement from code presence and tests); none on CI enforcement in the hosted repository. Provenance: working tree read on 2026-09-07; evidence index `test/evidence/evidence_index.json` (sha `HEAD`, 104 passed, env `dev`). Reviewer: IVA pending; approver: CAB pending.
