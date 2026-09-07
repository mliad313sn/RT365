# Session P3 — Change and Promotion (blueprint 00, 12; Committee)

**Environment:** dev/sim only. The ladder is development -> simulation -> shadow -> paper -> supervised pilot -> capped autonomous pilot -> controlled GA; this build is authorised for the first two rungs at most and no gate has been convened. Documented by the Program Orchestrator (1st line, convenes CAB, recommends, never approves).

## 1 Roles

| Function | Role (line) | Basis |
|---|---|---|
| Accountable | Change Advisory & Release Board (convener: Program Orchestrator; members: all 2nd-line leads, SRE Lead, IVA) for production authorisation; SRE Lead for `DEPLOYMENT_RUNBOOK.md` and `ROLLBACK_PLAN.md`; Program Orchestrator for `DEFINITION_OF_DONE.md` | COMMITTEE_DEEP_DIVE §1.3, §P3 |
| Consulted | Enterprise Architect (ADRs), Security Architect (CODEOWNERS, CI gates), QA Lead (evidence records) | RACI |
| Builder | Backend Lead (1st line) — `services/identity/identity_service/{makerchecker.py,accounts.py}`; Security Architect / Cloud Architect — `.github/workflows/ci.yml`, `.github/CODEOWNERS` | RACI |
| Challenger (different line) | Chief Risk Agent (2nd line) — CODEOWNER on risk/killswitch paths; challenged cooling period, fast-path rollback and "builder never sole approver" | `.github/CODEOWNERS`, Protocol §1.4 rule 4 |
| Assurance / IVA | Independent Validation Agent (veto at every gate; CODEOWNER on risk/compliance/execution/killswitch) | GOAL.md |

Statement: author != reviewer != approver. The Program Orchestrator convenes and documents but cannot self-certify evidence completeness (roster row 3); the IVA reviews; the CAB approves. Nothing here is self-certified, and no gate report exists (`docs/GATE_REPORTS/` is empty).

## 2 Purpose

- [Source: 00, 12] Every change (code, policy, limit, tool, model, prompt, jurisdiction flag) has an RTM link, threat-model delta, control-quartet status, rollback plan and observability plan; automatic rollback or halt on failure of guardrails, integrity checks, reconciliation or observability; a gate authorises only the next environment.
- [Source: 13] Production authorisation by the CAB; the builder is never the sole approver.
- [Committee] Policy and limit changes use maker-checker with a cooling period (`MakerChecker`, 1 h in sim, `require_different_line=True`); mode promotion needs a `GateRecord` with IVA APPROVE (`AccountRegistry.promote`); strategy promotion needs gate evidence (`StrategyRegistry.promote`, P2); tool changes need a re-signed registry under MCP Security Agent review; jurisdiction flags need dual key to enable and one person to disable (C6). CI (`ci.yml`) is the evidence pipeline: lint, typecheck, contract schemas, policy invariants, secret scan, all tests with the evidence index, determinism gate, evidence report, broker certification harness, SBOM, artefact upload.
- [Open: O-04] framework; [Open: O-17] roadmap dates; [Open: O-20] CODEOWNERS team handles / branch protection; [Open: O-19] named deputies for emergency authority.

## 3 Decisions and ADRs

| # | Decision | Alternatives compared | Why chosen | Evidence |
|---|---|---|---|---|
| P3-D1 | One generic maker-checker primitive for limits, mode promotion and tool registration: humans only, checker != maker, optional different-line rule, cooling period, `PENDING -> CHECKED -> EFFECTIVE|REJECTED`, every step audited, exported as `limit.changed.v1`. | (a) Approval logic per change type; (b) chosen: one primitive with parameters. | One control surface, one quartet (TC-ID-001). | `services/identity/identity_service/makerchecker.py`; TC-ID-001, TC-ID-003 |
| P3-D2 | Gate evidence is a typed value (`GateRecord{gate, passed, decision_log_ref, iva_verdict}`) required by `promote` and `strategies.promote(gate_passed=...)`; skipping a gate or a vetoed record is refused. | (a) Gate recorded in DECISION_LOG only; (b) chosen: gate record consumed by code. | Turns the ladder into a control; linkage to signed gate reports is still open (O-22). | TC-ID-003, TC-BT-004 |
| P3-D3 | CI as the Definition-of-Done evidence pipeline: `make` targets are identical locally and in CI; `test/evidence_plugin.py` writes an evidence record per `tc` marker (requirement, environment, data version, expected, actual, evidence link, owner, reviewer "pending"); `scripts/evidence_report.py` renders `docs/TEST_CASES/EVIDENCE_REPORT.md`; artefacts uploaded per run. | (a) Manual evidence spreadsheets; (b) chosen: generated from test markers; (c) external test-management tool. | (a) is unverifiable; (c) is procurement. The "reviewer: pending" field is deliberate: the evidence index never self-certifies. | **Proposed ADR-019** [Committee] "CI evidence pipeline and evidence-record schema"; `.github/workflows/ci.yml`, `test/evidence/evidence_index.json` |
| P3-D4 | Protected paths with 2nd-line/3rd-line CODEOWNERS (C5-D5); branch protection is a human act (O-20). | see C5 | — | `.github/CODEOWNERS` |
| P3-D5 | Rollback actions per change type (ROLLBACK_PLAN): service release via lease transfer (`LeaseStore.preempt`), policy via previous `policy_version` (new idempotency keys by ADR-003), model/prompt via `StrategyRegistry.rollback`, tool via `ToolRuntime.revoke_registry/restore_registry`, jurisdiction flag via `disable_flag`, data via snapshot replay. | (a) Generic "redeploy previous image"; (b) chosen: per-type rollback with a safety step first. | Each rollback has a code path and, for most types, a test. | TC-EX-004, TC-AI-004, TC-BT-004, TC-CP-004; drills pending (O-42) |
| P3-D6 | Provisional standards for dev/sim recorded as ADR proposals rather than silent choices: ADR-009 FastAPI (pending O-04), ADR-010 in-process stores, ADR-011 HMAC dev signing, ADR-012 static console pending PWA, ADR-013 PlaneGuard, ADR-014 deterministic hashing, ADR-015 mode ladder, ADR-016 reason-code dictionary, ADR-017 contract alignment, ADR-018 strategy lifecycle, ADR-019 CI evidence, ADR-020 legal hold. | (a) Leave standards implicit until Gate B; (b) chosen: file proposals now for ARB. | DEFINITION_OF_DONE requires "ADR written if a standard was changed"; proposals make the ARB decision explicit. | This packet; `docs/ADRs/ADR-000-template.md` |

## 4 RTM rows

| Requirement | Architecture element | Implementation owner | Control | Test IDs | Evidence path | Gate |
|---|---|---|---|---|---|---|
| FR-01 (privileged workflows) | `MakerChecker` | Backend Lead | Maker != checker, different line, cooling | TC-ID-001, TC-ID-003 | `test/quartets/test_tc_id_identity.py` | B |
| [Source: 12] one step per gate | `MODE_GATE`, `GateRecord`, `GATE_FOR` | Backend Lead | Promotion refused without matching gate + IVA APPROVE | TC-ID-003, TC-BT-004 | `services/identity/identity_service/accounts.py`, `services/strategy/strategy_service/registry.py` | B/C |
| NFR-SEC-02 (CI gate) | `ci.yml` jobs | Security Architect / Cloud Architect | Lint, typecheck, schemas, policy-check, secret-scan, tests, determinism, SBOM | CI run | `.github/workflows/ci.yml`, `Makefile` | B |
| NFR-DET-01 (determinism gate in CI) | CI step "Determinism gate" | QA Lead | Fail on any divergence | TC-RK-001..004, property tests | `.github/workflows/ci.yml` | C |
| [Source: 11] evidence record per test | `test/evidence_plugin.py`, `scripts/evidence_report.py` | QA Lead | Requirement, env, data version, expected, actual, link, owner, reviewer | all `tc`-marked tests | `test/evidence/evidence_index.json`, `docs/TEST_CASES/EVIDENCE_REPORT.md` | B |
| [Source: 00] automatic rollback/halt triggers | `AlertRouter` auto-actions (`autonomy_to_supervised`), Kill Switch on `risk.halt.v1`, break -> Supervised | SRE Lead | Guardrail/integrity/reconciliation/observability failure -> halt | TC-OB-004, TC-KS-006, TC-RC-002 | `observability/alerts.yaml`, `docs/ALERT_CATALOG.md` | C |
| [Source: 13] builder never sole approver | CODEOWNERS | Security Architect | 2nd-line approval on protected paths | GAP (branch protection not verifiable) | `.github/CODEOWNERS` | B |

## 5 Threat-model delta

| Threat | Boundary | Control | Test | Owner |
|---|---|---|---|---|
| T-07 Insider misuse (limit change, self-merge) | B2/B8 | Maker-checker; CODEOWNERS | TC-ID-001; GAP for merge path | Security & Privacy Board |
| T-10 Dependency compromise | B8 | SBOM per run; SCA pending (O-32) | GAP | Cloud Architect |
| T-04 Model supply chain | B8 | Strategy rollback to champion; artefact signing pending (O-33) | TC-BT-004 | Model Risk Lead |
| NEW T-33 Promotion past the authorised rung (deploying beyond the gate) | B8 | `GateRecord` in code; DEPLOYMENT_RUNBOOK step 1; no deployment automation exists | GAP | Program Orchestrator, SRE Lead |
| NEW T-34 Evidence index generated on an untracked commit (`git_sha` "HEAD" in the committed index) | B8 | CI uploads the index as an artefact per run; local runs are not evidence | GAP (R-17) | QA Lead |
| NEW T-35 Cooling-period bypass by proposing under a different change kind | B2 | `kind` is free text; the checker sees the payload | GAP | Chief Risk Agent |

## 6 Control quartet per critical control

| Control | Positive | Negative | Abuse | Recovery |
|---|---|---|---|---|
| Maker-checker with cooling | TC-ID-001 `test_privileged_change_needs_second_approver_from_different_line` | TC-ID-001 (same person / same line) | TC-ID-003 (agent proposes -> denied) | TC-ID-001 (EFFECTIVE after cooling); GAP — `reject` path and "fast path" rollback of a policy version untested |
| Gate-bound promotion | TC-ID-003 (Gate D record -> SUPERVISED) | TC-ID-003 (missing / vetoed / skipped) | TC-ID-003 (agent) | TC-ID-004 (demotion via halt and two-person restore) |
| CI evidence pipeline | CI green run with evidence artefact | `test_event_schemas_have_no_drift`, `make policy-check` failures block | TC-NET-004 (policy tampering caught by the checker) | GAP — no rerun/reproduction of the evidence index by the IVA on a pinned SHA |
| Rollback per change type | TC-AI-004 (registry restore), TC-CP-004 (flag disable), TC-BT-004 (strategy rollback), TC-EX-004 (lease transfer) | GAP — no test that rollback is refused for a non-authorised role except strategy (`rollback` role check) | GAP | GAP — drills not performed (H-19, O-42) |
| Protected-path approval | CODEOWNERS present | GAP | GAP | GAP |

## 7 Evidence list

- `docs/DEFINITION_OF_DONE.md`, `docs/DEFINITION_OF_READY.md`, `docs/ROLLBACK_PLAN.md`, `docs/DEPLOYMENT_RUNBOOK.md`, `docs/RELEASE_CHECKLIST.md`, `docs/DECISION_LOG.md` (D-001..D-004), `docs/MISSING_ACTIONS.md` (H-01, H-02, H-19), `docs/PROJECT_EXECUTION_PLAN.md`, `docs/ADRs/*`
- `services/identity/identity_service/{makerchecker.py,accounts.py}`, `services/strategy/strategy_service/registry.py::rollback`, `mcp/servers/mcp_servers/runtime.py::revoke_registry/restore_registry`, `services/compliance/compliance_engine/jurisdiction.py::disable_flag`
- `.github/workflows/ci.yml`, `.github/CODEOWNERS`, `Makefile`, `test/evidence_plugin.py`, `scripts/evidence_report.py`, `test/evidence/evidence_index.json`, `security/sbom/sbom.cdx.json`
- `test/quartets/test_tc_id_identity.py`, `test/quartets/test_tc_ai_mcp.py`, `test/quartets/test_tc_cp_eligibility.py`, `test/integration/test_backtest_single_code_path.py`, `test/quartets/test_tc_ex_execution.py`

## 8 RAID entries, assumptions, confidence, provenance

| ID | Type | Item | Owner | Gate |
|---|---|---|---|---|
| O-42 | Gap | Rollback drills for each change type (ROLLBACK_PLAN: "evidenced before Gate D") and Kill Switch / DR drills (H-19) have no drill logs; `docs/GATE_REPORTS/` is empty | SRE Lead | D |
| O-43 | Gap | No deployment automation exists; DEPLOYMENT_RUNBOOK steps 2–6 (signature verification, IaC apply, lease-transfer deploy, synthetic probe, progressive flags) are procedure only; `synthetic_probe` exists in `platform.py` but is not a deployment step | SRE Lead, Cloud Architect | C |
| O-44 | Gap | CAB convening record: no DECISION_LOG entry format for a merge/release authorisation, and no link from PR to RTM row / threat-model delta / quartet status as P3 requires | Program Orchestrator | B |
| R-17 | Risk | Committed `test/evidence/evidence_index.json` carries `git_sha: "HEAD"` (generated where git was unavailable); evidence that is not pinned to a commit cannot be reproduced by the IVA (T-34) | QA Lead, IVA | C |
| R-18 | Risk | `MakerChecker.kind` is free text; the cooling period and different-line rule are per instance (`limits_mc` only); mode promotion and tool registration do not yet route through it despite the module docstring | Backend Lead, Chief Risk Agent | B |

Assumptions: CI runs on `main` and `claude/**` branches; team handles `@rt365/*` are placeholders until O-20 closes; cooling period 1 h is a sim fixture.

Confidence: **high** for the maker-checker and gate-bound promotion controls in code; **medium** for CI as an evidence pipeline (runs, but reviewer sign-off and SHA pinning are open); **low** for deployment, rollback drills and CAB procedure (documents only).

Provenance: [Source: 00, 11, 12, 13] promotion rules, evidence record fields, gates, CAB; [Committee] maker-checker design, GateRecord, ADR-019 proposal and the ADR-009..020 register; [Open] O-04, O-17, O-19, O-20, O-42..O-44. Evidence cited by path; the Program Orchestrator recommends and the CAB decides; IVA review pending.
