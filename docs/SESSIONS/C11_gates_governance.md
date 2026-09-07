# Session packet C11 — Release Gates & Governance (blueprint 12, 13)

| Session | Date | Environment | Status | Documented by |
|---|---|---|---|---|
| C11 | 2026-09-07 | dev/sim only | Committee working draft; not a release artefact | Program Orchestrator (convener; recommends, never approves) |

No gate has been convened: `docs/GATE_REPORTS/` is empty, `docs/RELEASE_CHECKLIST.md` evidence-link columns are blank and `docs/AUDIT_EVIDENCE_INDEX.md` rows 1–9 are unsigned. The build therefore sits at the bottom of the environment ladder (dev/sim) and authorises nothing.

## 1 Roles

| Role in session | Person/role | Line |
|---|---|---|
| Accountable (convener) | Program Orchestrator — this packet's author; cannot self-certify evidence completeness | 1st |
| Builder (code) | Backend Lead — `services/identity/identity_service/accounts.py` (`GateRecord`, `MODE_GATE`, `restore_from_halt`), `libs/core/rtcore/lines.py` (`KILL_SWITCH_ACTIVATORS`); SRE Lead — `.github/CODEOWNERS` | 1st |
| Approvers | Boards per `docs/COMMITTEE_DEEP_DIVE.md` §1.3 (Product Council, ARB, Trading Risk Committee, Model Risk Committee, Security & Privacy Board, Compliance & Legal Committee, CAB, Executive Steering) | 2nd / Executive |
| Challenger | Chief Risk Agent (2nd line; challenges emergency-authority encoding and gate-bound mode promotion) | 2nd |
| Assurance / IVA | Independent Validation Agent — veto at every gate on evidence grounds | 3rd |

Segregation: author != reviewer != approver; nothing here is self-certified. The packet is reviewed by the IVA and approved by the CAB; the Program Orchestrator only presents.

## 2 Purpose

- [Source: 12] Gates A–F with entry criteria, exit evidence and approving bodies; each gate authorises only the next environment on the ladder.
- [Source: 13] Builder never sole approver; risk, compliance and security controls have independent accountable owners; emergency authority and deputies documented.
- [Committee] Emergency authority: any of SRE Lead, Chief Risk Agent, Compliance Agent, Trading Domain Lead or a named deputy may activate the Kill Switch unilaterally; deactivation needs two people from different lines and a logged reason.
- [Committee] Protected repository paths require 2nd-line CODEOWNERS approval before merge.
- [Open: O-19] named deputies; [Open: O-20] CODEOWNERS team handles are placeholders (recorded in `.github/CODEOWNERS`, not yet in `docs/RAID_LOG.md`); [Open: O-29], [Open: O-30] raised below.

## 3 Decisions and ADRs

| ID | Decision | Alternatives considered | Why chosen | Status |
|---|---|---|---|---|
| ADR-023 [Committee] | Gate evidence is a typed value: `GateRecord(gate, passed, decision_log_ref, iva_verdict)`; `AccountRegistry.promote` refuses PAPER/SUPERVISED/BOUNDED_AUTONOMOUS unless `gate == MODE_GATE[target]`, `passed` and `iva_verdict == "APPROVE"`; promotion is one step on `MODE_LADDER`; bounded autonomy also needs `capital_envelope` (`accounts.py`) | (a) per-environment config flag; (b) human process only, no code check | (a) can be flipped without a decision-log reference; (b) unenforceable. Same pattern in `StrategyRegistry.GATE_FOR` (PAPER→C, SUPERVISED_PILOT→D, CAPPED_AUTONOMOUS→E) | Proposed, pending CAB |
| ADR-024 [Committee] | Emergency authority encoded once in `libs/core/rtcore/lines.py::KILL_SWITCH_ACTIVATORS` and consumed by `KillSwitchService`; BFF additionally requires `Permission.ACTIVATE_KILL_SWITCH`/`DEACTIVATE_KILL_SWITCH` | (a) RBAC permission only; (b) external config file | (a) loses the "line of defense" attribute needed for the two-person rule; (b) editable outside CODEOWNERS. The set contains `RISK_OFFICER` and `RUNTIME_MONITOR` beyond the C11 list — deviation for Trading Risk Committee → O-29 | Proposed, pending Trading Risk Committee |
| ADR-025 [Committee] | Protected paths widened beyond the blueprint minimum: `.github/CODEOWNERS` adds `/services/killswitch/`, `/infra/kubernetes/network-policies/`, `docs/RISK_POLICY.md`, `LIMIT_MATRIX.md`, `COMPLIANCE_MATRIX.md`, `JURISDICTION_MATRIX.md`, with `@rt365/independent-validation` co-owning risk, compliance, execution and killswitch | (a) blueprint minimum set (`bootstrap_repo.sh` still emits it); (b) branch protection with any two reviewers | (a) leaves the Kill Switch and policy documents unprotected; (b) does not force the *right* line | Proposed, pending Security & Privacy Board |
| D-C11-1 [Committee] | Leaving HALTED = two humans, different lines, non-autonomous target only; autonomy re-enable needs post-incident review (`restore_from_halt`) | (a) single privileged role; (b) automatic restore after timer | Blueprint precedence of human override; an automatic restore would re-arm autonomy without review | Proposed, pending Trading Risk Committee |
| D-C11-2 [Committee] | Gate prompts are uniform (`goals/gate_A..F_*.md`): present `RELEASE_CHECKLIST` rows with `AUDIT_EVIDENCE_INDEX` links; assertions without evidence are absent; any REJECT/VETO closes the gate | (a) bespoke agenda per gate; (b) e-mail sign-off | Uniform procedure makes the IVA veto and the "no date-driven waiver" rule identical at every gate | Proposed, pending Executive Steering (H-02) |

Gate readiness snapshot (evidence candidates only; none reviewed): A — charter/personas exist, jurisdiction hypothesis [Open: O-11], outcomes [Open: O-16]; B — ADR-001..008, `THREAT_MODEL.md`, `DATA_FLOWS.md`, capacity model absent; C — TC-RK, TC-EX, TC-RC, TC-AUD green in dev, `sim-broker.md` 12 PASS / 2 OPEN; D — IVA reproduction absent (row 6), security assessment absent (H-10); E — halt drill sim-only (row 8); F — nothing.

## 4 RTM rows

| Requirement | Architecture element | Implementation owner | Control | Test IDs | Evidence path | Gate |
|---|---|---|---|---|---|---|
| FR-01 (privileged access) | `MakerChecker` (`identity_service/makerchecker.py`), PIM in `rbac.py` | Backend Lead | Second approver from a different line | TC-ID-001 `test_privileged_change_needs_second_approver_from_different_line`; TC-ID-002 `test_rbac_mfa_and_pim` | `test/quartets/test_tc_id_identity.py` | B |
| [Source: 12] gate-bound promotion | `GateRecord`, `MODE_GATE`, `MODE_LADDER` | Backend Lead | One step; gate passed with IVA APPROVE; agents cannot promote | TC-ID-003 `test_agent_cannot_change_mode_or_skip_steps_and_out_of_scope_flags_absent` | same | C |
| [Source: 00] return from HALTED | `restore_from_halt` | Backend Lead | Two persons, different lines | TC-ID-004 `test_return_from_halted_requires_two_persons_different_lines`; TC-KS-004 | same; `test_tc_ks_killswitch.py` | C |
| FR-06 (strategy promotion) | `StrategyRegistry.promote` with `GATE_FOR`, `PROMOTER` | Quant Research Lead | Role matrix; owner segregation; gate required | TC-BT-004 `test_strategy_lifecycle_pre_registration_and_segregation` | `test/integration/test_backtest_single_code_path.py` | C |
| FR-17 / [Source: 13] emergency authority | `KILL_SWITCH_ACTIVATORS`; `KillSwitchService.activate/deactivate` | Backend Lead | Unilateral activation by authorised roles; two-person different-line deactivation | TC-KS-001, TC-KS-002, TC-KS-003, TC-KS-004 | `test/quartets/test_tc_ks_killswitch.py` | C |
| [Committee] protected paths | `.github/CODEOWNERS` | SRE Lead (Security & Privacy Board approves) | 2nd-line approval before merge | GAP — enforced by GitHub only once handles exist [Open: O-20]; no test | `.github/CODEOWNERS` | B |
| [Source: 13] deputies | `docs/RACI.md` "Deputies: [Open: O-19]" | Program Orchestrator | Named deputies per role | GAP | `docs/RACI.md`; `goals/decisions/O-19_decision_pack.md` | C |
| [Source: 12] release dossier | `docs/RELEASE_CHECKLIST.md`, `docs/AUDIT_EVIDENCE_INDEX.md` | Program Orchestrator | Evidence link per criterion; IVA verdict column | GAP — columns empty | same | A–F |

## 5 Threat-model delta

| Threat | Boundary | Control in this build | Test | Residual / owner |
|---|---|---|---|---|
| T-07 Insider misuse — forged gate evidence | operator → account registry | `GateRecord` is a plain model; any caller can construct `iva_verdict="APPROVE"`; no lookup against `DECISION_LOG.md` or signature | TC-ID-003 (VETO record refused) | Forgery untested and unprevented → R-09. Backend Lead / IVA |
| T-07 — skipping the ladder | same | One-step rule (`TransitionError` on skip); demotion allowed freely | TC-ID-003 | Demotion has no reason review; acceptable (reduces exposure). Chief Risk Agent |
| T-02 Excessive agency — agent changes mode or authority | agent → control plane | `promote`/`restore_from_halt` require `actor.is_human`; `KillSwitchService` rejects `ActorKind.AGENT` with S1 alert | TC-ID-003, TC-KS-002 | None. MCP Security Agent |
| T-C11-1 Automated actor holds emergency authority (new) | runtime monitor → Kill Switch | `RUNTIME_MONITOR` in `KILL_SWITCH_ACTIVATORS`; `evaluate_monitors` activates under a SYSTEM-kind actor | TC-KS-006 | Intended by [Source: 05] but not in the C11 list → O-29 for ratification. Chief Risk Agent |
| T-C11-2 Unprotected merge to control code (new) | repo | CODEOWNERS with placeholder handles | GAP | Until O-20 closes, GitHub cannot enforce; CI has no CODEOWNERS lint. SRE Lead |
| T-12 Audit of governance acts | all | `account.mode.changed`, `account.halted`, `account.restore.pending`, `account.restored`, `strategy.status.changed`, `killswitch.*` audit actions | TC-ID-004, TC-KS-004, TC-BT-004 | None in scope. SRE Lead |

## 6 Control quartet per critical control

| Control | Positive | Negative | Abuse | Recovery |
|---|---|---|---|---|
| Gate-bound, one-step mode promotion | TC-ID-003 (Gate D APPROVE → SUPERVISED) | TC-ID-003 (no gate → `ControlDenied`; skip step → `TransitionError`; no envelope → denied) | TC-ID-003 (agent denied; VETO record denied); forged APPROVE record — GAP | TC-ID-004 (two persons, different lines, restore to non-autonomous mode) |
| Emergency authority (activate / deactivate) | TC-KS-001 `test_activation_blocks_new_risk_and_cancels_open_orders`; TC-KS-005 `test_every_level_blocks_matching_intents` | TC-KS-003 `test_single_person_deactivation_stays_pending` | TC-KS-002 `test_agent_cannot_activate_or_deactivate` (agent, trader) | TC-KS-004 `test_two_person_deactivation_restores_with_audit` |
| Strategy promotion by role matrix with gate | TC-BT-004 (MODEL_RISK → VALIDATED, IVA → REPRODUCED, gate C → PAPER) | TC-BT-004 (PAPER without gate denied) | TC-BT-004 (owner self-validates; trader role) | TC-BT-004 (`rollback`) |
| Maker-checker for privileged/limit changes | TC-ID-001; TC-E2E-J06 (`/v1/limits` check by different role) | TC-E2E-J06 (proposer checks → 403) | TC-ID-003 (agent proposes limit → denied) | GAP — cooling period / revert not tested |
| Protected-path CODEOWNERS approval | GAP (file present only) | GAP | GAP | GAP |
| Release dossier completeness (assertions without evidence = absent) | GAP | GAP | GAP | GAP — no gate convened [Open: O-30] |

## 7 Evidence list

| Evidence | Path |
|---|---|
| Gate prompts A–F | `goals/gate_A_discovery.md` … `goals/gate_F_market_release.md` |
| Checklist, evidence index, RACI, decision log, RAID | `docs/RELEASE_CHECKLIST.md`; `docs/AUDIT_EVIDENCE_INDEX.md`; `docs/RACI.md`; `docs/DECISION_LOG.md` (D-001..D-004); `docs/RAID_LOG.md`; `docs/GATE_REPORTS/` (empty) |
| Mode state machine and gate records | `services/identity/identity_service/accounts.py`; `libs/core/rtcore/schemas/account.py` (`MODE_LADDER`) |
| Emergency authority and lines | `libs/core/rtcore/lines.py`; `services/killswitch/killswitch_service/service.py`; `services/identity/identity_service/rbac.py` |
| Protected paths | `.github/CODEOWNERS`; `scripts/bootstrap_repo.sh` (older minimum set) |
| Tests | `test/quartets/test_tc_id_identity.py`; `test/quartets/test_tc_ks_killswitch.py`; `test/integration/test_backtest_single_code_path.py`; `test/evidence/evidence_index.json` (2026-09-07T17:28:57Z, 104 passed, env `dev`) |
| Human acts register | `docs/MISSING_ACTIONS.md` (H-01, H-02, H-13, H-18, H-19); `docs/PROJECT_EXECUTION_PLAN.md` |

## 8 RAID entries, assumptions, confidence, provenance

| ID | Type | Item | Owner | Needed by | Status |
|---|---|---|---|---|---|
| O-29 | Decision | `KILL_SWITCH_ACTIVATORS` includes `RISK_OFFICER` and `RUNTIME_MONITOR`, which the C11 emergency-authority list does not name; Trading Risk Committee to ratify or narrow, and to name deputies (O-19) | Chief Risk Agent / Trading Risk Committee | Gate C | Open |
| O-30 | Gap | No gate convened; `docs/GATE_REPORTS/` empty; `RELEASE_CHECKLIST.md` evidence links and `AUDIT_EVIDENCE_INDEX.md` reviewer/IVA columns blank; O-20 (CODEOWNERS handles) present in code comments but absent from `RAID_LOG.md` | Program Orchestrator | Gate A | Open |
| R-09 | Risk | `GateRecord` is unsigned and unverified: any code path can fabricate `passed=True, iva_verdict="APPROVE"`; promotion should resolve the record from the decision log (or a signed store) rather than trust the argument | Backend Lead (IVA verifies) | Gate C | Open |
| O-19, H-01, H-02 | carried | deputies; appointments; ratification of D-001..D-004 | Executive sponsor / Executive Steering | Gate A | Open |

Assumptions: the committee roster in `docs/RACI.md` is unpopulated with named people; every "role" above is a seat, not a person. Confidence: high for the code-enforced rules cited; none for governance execution (no gate has run). Provenance: files read on 2026-09-07; evidence index sha `HEAD`. Reviewer: IVA pending; approver: CAB pending; ratification of governance decisions: Executive Steering pending (H-02).
