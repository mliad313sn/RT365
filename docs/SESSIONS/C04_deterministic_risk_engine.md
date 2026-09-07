# Session C4 — Deterministic Risk Engine (blueprint 05)

**Environment:** dev/sim only. Every numeric value in `services/risk/policies/sim-policy-v0.1.yaml` is a fixture chosen so the quartet can exercise each check; `approved_for_production: false` [Open: O-07]. Documented by the Program Orchestrator (1st line, recommends, never approves).

## 1 Roles

| Function | Role (line) | Basis |
|---|---|---|
| Accountable | Chief Risk Agent (2nd line, policy); Backend Lead (1st line, implementation) | COMMITTEE_DEEP_DIVE §C4 |
| Consulted | Trading Domain Lead, SRE Lead | COMMITTEE_DEEP_DIVE §C4 |
| Builder | Backend Lead — `services/risk/risk_engine/{engine.py,policy.py,monitors.py}`, `services/killswitch/killswitch_service/service.py` | RACI; Backend Lead cannot merge `/services/risk` without a 2nd-line reviewer |
| Challenger (different line) | Chief Risk Agent (2nd line) — CODEOWNER for `/services/risk`, `/services/killswitch`, `docs/RISK_POLICY.md`, `docs/LIMIT_MATRIX.md`; challenged fail-closed semantics and limit hierarchy | `.github/CODEOWNERS` |
| Assurance / IVA | Trading Risk Committee (limits, kill policy); Independent Validation Agent (determinism validation; CODEOWNER on `/services/risk`) | COMMITTEE_DEEP_DIVE §C4 |

Statement: author != reviewer != approver. `test/quartets/test_tc_rk_determinism.py:1` records "Owner: Backend Lead. Reviewer: pending (Chief Risk Agent)". The Chief Risk Agent has no delivery ownership of engine code; the IVA validates determinism; the Trading Risk Committee approves policy. Nothing here is self-certified.

## 2 Purpose

- [Source: 05] Pre-trade controls (trading status through correlated-risk limits), runtime controls (loss limits through venue health), four outcomes (APPROVED, REJECTED, REQUIRES_HUMAN_APPROVAL, HALTED) with policy version, reason codes, evaluated values, thresholds, timestamp; emergency policy where closing positions is not assumed universally safest.
- [Committee] `decide(intent, account_snapshot, market_snapshot, policy, now) -> DecisionRecord` is a pure function: no I/O, no randomness, no model call; missing input -> HALTED `RK-HALT-INPUT`; tampered intent -> REJECTED `RK-INTEG`; effective limit = minimum across platform > tenant > account > strategy > instrument; undefined limit fails closed (`RK-*-UNDEFINED`); all cheap checks are evaluated so the record lists every failing reason; outcome precedence HALTED > REJECTED > REQUIRES_HUMAN_APPROVAL > APPROVED.
- [Committee] Runtime monitors (`evaluate_runtime`) emit `risk.halt.v1` events consumed by the Kill Switch service; six Kill Switch levels; activation by any emergency-authority human or the runtime monitor; deactivation by two humans from different lines.
- [Open: O-07] numeric thresholds; [Open: O-08] liquidation policy — `CANCEL_AND_REDUCE/FLATTEN` fall back to `CANCEL_ONLY` without an approved `liquidation_policy_ref`.

## 3 Decisions and ADRs

| # | Decision | Alternatives compared | Why chosen | Evidence |
|---|---|---|---|---|
| C4-D1 | Determinism by construction: `decision_id = deterministic_id(intent_hash, account_snapshot_id, market_snapshot_id, policy_version, ENGINE_BUILD_HASH)`; `ENGINE_BUILD_HASH` is a SHA-256 over the package source; no `new_id` inside the engine (`rtcore/ids.py`). | (a) Random decision IDs plus a "same outcome" test; (b) chosen: deterministic IDs so replicas produce byte-identical records; (c) seeded RNG. | (a) cannot detect divergence in evaluated values; (c) is still non-deterministic across code versions. TC-RK-001 runs `decide` in a separate interpreter and compares records. | **Proposed ADR-014** [Committee] "Canonical JSON hashing, deterministic IDs and build hash for pure engines"; TC-RK-001, property tests |
| C4-D2 | Fail closed on missing inputs and on undefined limits (`_cap_check` -> `RK-*-UNDEFINED`, `RK-FRESH-UNDEFINED`). | (a) Skip a check whose limit is absent; (b) chosen: absent limit is a failing check. | [Source: 05] never APPROVED by default; O-07 means many limits are undefined in early environments, so silence must fail. | TC-RK-004, TC-RK-013, `test_fail_closed_for_every_missing_input` |
| C4-D3 | Evaluate all checks, classify codes: `-APPROVAL` suffix and `APPROVAL_CODES` -> REQUIRES_HUMAN_APPROVAL; `HALT_CODES` -> HALTED; others -> REJECTED. | (a) Return on first failure; (b) chosen: full list with precedence. | Operators and auditors see every failing reason (TC-RK-011); precedence is property-tested. | TC-RK-010 (parametrised over the reason codes), TC-RK-011, `test_decide_is_pure_and_precedence_holds` |
| C4-D4 | Limit hierarchy via `effective_limit` = min over applicable `LimitLevel`s; limits are data (`RiskPolicy`, maker/checker fields) changed only through `MakerChecker` with cooling period; no agent write path. | (a) Most specific level wins; (b) chosen: minimum. | Minimum cannot be loosened by a lower level, matching [Committee C4 §3]. | TC-RK-012, `test_effective_limit_is_minimum_of_applicable`, TC-ID-001 |
| C4-D5 | Kill Switch as a service with hooks (`KillSwitchHooks`: cancel open orders via fencing tokens, emergency policy, revoke agent identities, evidence snapshot hash, halt account, notify); agents denied with S1 alert; two-person, different-line deactivation. | (a) Kill Switch as a flag in the account record only; (b) chosen: orchestrating service whose activation is the flag consulted by `decide` via `KillSwitchFlags`. | (a) does not cancel orders or revoke tokens [Source: 05 actions on activation]. | TC-KS-001..006 |
| C4-D6 | Order-splitting evasion aggregated: `chk_caps` sums open same-side orders (`RK-CAP-AGG`); replay of a signed intent rejected through `recent_intent_hashes` (`RK-DUP`). | (a) Per-order cap only; (b) chosen: aggregate. | Abuse row of the C4 control matrix. | TC-RK-010[RK-CAP-AGG], TC-RK-015 |

Standing ADRs: ADR-003 (policy_version in idempotency key: a re-evaluated intent under a new policy is a new order key). Runtime thresholds in `RuntimeThresholds` are fixtures [Open: O-03/O-07].

## 4 RTM rows

| Requirement | Architecture element | Implementation owner | Control | Test IDs | Evidence path | Gate |
|---|---|---|---|---|---|---|
| FR-11 (pre-trade) | `risk_engine.engine.decide`, `CHECKS` (16 families) | Backend Lead | Deterministic decision, fail closed, complete reason list | TC-RK-001..004, TC-RK-010..015, `test_evaluated_checks_cover_all_sixteen_families` | `test/quartets/test_tc_rk_determinism.py` | C |
| NFR-DET-01 | `deterministic_id`, `ENGINE_BUILD_HASH`, property tests | Backend Lead / IVA | 100% identical across replicas | TC-RK-001, `test_decide_is_pure_and_precedence_holds`, `test_fail_closed_for_every_missing_input` | `test/property/test_risk_determinism_property.py`; CI step "Determinism gate" | C |
| FR-11 (runtime) | `risk_engine.monitors.evaluate_runtime` -> `risk.halt.v1` | Backend Lead | HALT events with reason codes RT-* | TC-RK-016, TC-KS-006 | `services/risk/risk_engine/monitors.py` | C |
| FR-17 | `KillSwitchService` (six levels) | Backend Lead | Activation blocks new risk; two-person restore | TC-KS-001..006 | `test/quartets/test_tc_ks_killswitch.py` | C |
| FR-11 / [Source: 05] limits via maker-checker | `RiskPolicy.maker/checker`, `MakerChecker` (`limits_mc`, 1 h cooling, different line) | Backend Lead | No agent write path | TC-ID-001, TC-ID-003 | `services/identity/identity_service/makerchecker.py` | C |
| FR-11 decision record schema | `rtcore/schemas/decision.py`; OpenAPI `DecisionRecord` | Integration Architect | Contract alignment | `test_decision_record_matches_openapi` | `contracts/api/API_OPENAPI.yaml` | C |
| NFR-LAT-01 | `RT-LATENCY` monitor, `RuntimeThresholds.decision_latency_p99_ms` | SRE Lead | Autonomy suspended above threshold | TC-RK-016 (fixture threshold) | `observability/slis.yaml` | E [Open: O-03] |

## 5 Threat-model delta

| Threat | Boundary | Control | Test | Owner |
|---|---|---|---|---|
| T-08 Replay of a signed intent | B3 | `RK-DUP` via `recent_intent_hashes`; `RK-EXPIRED` | TC-RK-015, TC-RK-010[RK-EXPIRED] | Integration Architect |
| T-07 Insider misuse (limit change) | B2 | Maker-checker with cooling; policy is data, engine has no setter | TC-ID-001 | Security & Privacy Board |
| T-02 Excessive agency (agent operates Kill Switch) | B2 | `ActorKind.AGENT` denied, `killswitch.agent_attempt` S1 alert | TC-KS-002 | MCP Security Agent |
| T-03 Poisoned market data | B7 | `RK-FRESH*`, `RK-FRESH-PROV` (untrusted provenance), `RK-FRESH-CLOCK` | TC-RK-010 freshness rows, TC-MD-002/003 | Data Architect |
| NEW T-20 Intent mutated between validation and decision | B3 | `ValidatedIntent.integrity_ok()` -> `RK-INTEG`, S1 alert in pipeline | TC-RK-003 | Backend Lead |
| NEW T-21 Emergency policy escalation without approved liquidation policy | B4 | Fallback to `CANCEL_ONLY` recorded in `emergency_policy_applied` | `test_emergency_policy_reduce_without_liquidation_policy_falls_back` (no TC id) | Chief Risk Agent (O-08) |

## 6 Control quartet per critical control

| Control | Positive | Negative | Abuse | Recovery |
|---|---|---|---|---|
| Determinism | TC-RK-001 `test_identical_inputs_identical_decision_across_replicas` | TC-RK-002 `test_changed_policy_version_yields_new_decision` | TC-RK-003 `test_tampered_intent_hash_rejected` | TC-RK-004 `test_engine_restart_same_decision_and_fail_closed_on_missing_inputs` |
| Fail closed | TC-RK-012 `test_limit_hierarchy_effective_is_minimum` (defined limits pass) | TC-RK-013 `test_undefined_limit_fails_closed` | `test_fail_closed_for_every_missing_input` (parametrised vi/acct/mkt/policy) | TC-RK-004 (restore inputs -> same decision) |
| Pre-trade check families | TC-RK-010 (each mutation yields its code) | TC-RK-011 `test_all_failing_reasons_listed_not_only_first` | TC-RK-015 `test_duplicate_and_correlated_group`; TC-RK-010[RK-CAP-AGG] | GAP — no test that a limit restored after breach lets the next intent pass (C4 matrix "limit restored") |
| Kill Switch | TC-KS-001 `test_activation_blocks_new_risk_and_cancels_open_orders`; TC-KS-005 (all levels) | TC-KS-003 `test_single_person_deactivation_stays_pending` | TC-KS-002 `test_agent_cannot_activate_or_deactivate` | TC-KS-004 `test_two_person_deactivation_restores_with_audit` |
| Runtime monitors | TC-KS-006 `test_runtime_monitor_triggers_kill_switch` | TC-RK-016 `test_runtime_monitors_emit_halt_events` | GAP — no test of a forged `risk.halt.v1` event from a non-monitor actor | GAP — no drill evidence of restore after RT-* halt (P4 quarterly drill, MISSING_ACTIONS H-19) |

## 7 Evidence list

- `docs/RISK_POLICY.md`, `docs/LIMIT_MATRIX.md` (numbers absent by design, O-07), `docs/REASON_CODES.md` (RK-*, RT-* rows generated from `apps/web/web_bff/reason_codes.py`)
- `services/risk/risk_engine/{engine.py,policy.py,monitors.py}`, `services/risk/policies/sim-policy-v0.1.yaml`, `services/killswitch/killswitch_service/service.py`, `libs/core/rtcore/schemas/{decision.py,account.py}`, `libs/core/rtcore/ids.py`
- `test/quartets/test_tc_rk_determinism.py` (TC-RK-001..004, 010..016), `test/property/test_risk_determinism_property.py`, `test/quartets/test_tc_ks_killswitch.py` (TC-KS-001..006)
- `.github/workflows/ci.yml` step "Determinism gate"; `test/evidence/evidence_index.json`; `contracts/events/{risk.decided.v1,risk.halt.v1,killswitch.activated.v1,killswitch.deactivated.v1}.json`

## 8 RAID entries, assumptions, confidence, provenance

| ID | Type | Item | Owner | Gate |
|---|---|---|---|---|
| O-30 | Gap | `ENGINE_BUILD_HASH` is computed from source files at import; deployment must pin it to the signed artefact digest so replicas on different images cannot silently differ | Backend Lead, Cloud Architect | C |
| O-31 | Gap | Recovery row "limit restored after breach" and a forged-halt-event abuse test are missing; add TC-RK-017/018 | QA Lead, Backend Lead | C |
| R-09 | Risk | Determinism evidence has reviewer "pending"; without IVA independent reproduction (AUDIT_EVIDENCE_INDEX #3) Gate C cannot pass | Independent Validation Agent | C |
| R-01 (existing) | Risk | Non-deterministic path: `RuntimeThresholds` defaults and `SessionCalendar` are inputs the tests fix; any wall-clock read inside `decide` would break NFR-DET-01 — property test guards it | Chief Risk Agent | continuous |

Assumptions: sim policy fixtures (e.g. per-order cap 1,000,000 / 250,000 / 100,000 / 50,000 across levels, collar 5%, leverage 2x) exist only to make `effective = min` and each check testable; they are not proposals. `SessionCalendar` and `venue_healthy` are simulated.

Confidence: **high** for purity, fail-closed and reason-code completeness (code, quartet and property tests read); **medium** for Kill Switch orchestration (hooks are wired in the sim composition root only); **low** for any numeric threshold.

Provenance: [Source: 00, 02, 05, 10] posture, outcomes, actions on activation; [Committee] ADR-014 proposal, precedence, aggregation, hook model; [Open] O-03, O-07, O-08, O-30, O-31. Evidence cited by path; Chief Risk Agent review and IVA validation pending.
