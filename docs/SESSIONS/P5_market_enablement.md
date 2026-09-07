# Session packet P5 — Market Enablement (blueprint 07, 17)

| Session | Date | Environment | Status | Documented by |
|---|---|---|---|---|
| P5 | 2026-09-07 | dev/sim only | Committee working draft; not a release artefact | Program Orchestrator (recommends, never approves) |

No market is enabled. The only cell in this build is the fixture `country="ZZ"` (ISO 3166 user-assigned code, explicitly not a jurisdiction) × RETAIL × `sim-broker` × `SIMX` × EQUITY × mode, created by `build_sim_platform` [Open: O-11]. `docs/COMPLIANCE_MATRIX.md` and `docs/JURISDICTION_MATRIX.md` contain no enabled row. Regulatory status, broker capability and data entitlements are never assumed [Source: 00].

## 1 Roles

| Role in session | Person/role | Line |
|---|---|---|
| Accountable | Compliance Agent + Legal Agent (co-chairs, Compliance & Legal Committee; no cell without Legal co-signature) | 2nd |
| Builder (code) | Backend Lead — `services/compliance/compliance_engine/jurisdiction.py`, `eligibility.py` (protected path: `@rt365/compliance-agent` + IVA per CODEOWNERS); Broker-Connector Lead — certification harness | 1st |
| Consulted | Trading Domain Lead (MARKET_LAUNCH_CHECKLIST technical part), Product Director, Data Architect (entitlements), GTM Lead (commercial part, no return claims) | 1st / Architecture |
| Challenger | Trading Domain Lead (1st line; challenges instrument-master validation and broker certification completeness) | 1st |
| Assurance / IVA | Compliance & Legal Committee (sign-off); Executive Steering (launch); Independent Validation Agent | 2nd / Executive / 3rd |

Segregation: author != reviewer != approver; nothing here is self-certified. In code, the legal signer and the flag activator must be different humans (`activate_flag`), mirroring the dual-key rule for the humans H-12/H-17.

## 2 Purpose

- [Source: 07] Compliance matrix by country × customer type × broker × venue × asset class × feature; suitability/appropriateness; disclosures; restricted lists; surveillance; retention; "worldwide" never means legal availability.
- [Source: 17] Market launch checklist: legal basis, broker capability, instrument identifiers, sessions/holidays, currencies, tick/lot, order types, settlement, short-sale, margin, taxes/fees, corporate actions, data entitlements, reporting, surveillance, support hours, incident contacts, disclosures.
- [Committee] Sequence: hypothesis (Gate A) → legal basis → broker certification (C10 §4) → instrument-master validation → data entitlements → reporting/surveillance readiness → support and incident contacts → disclosures → C&L sign-off → dual-key activation → post-launch review at 30/90 days.
- [Open: O-11] first jurisdiction hypothesis; [Open: O-12] data licensing; [Open: O-09] legal hold vs deletion; [Open: O-10] DPIA; [Open: O-15] support hours; [Open: O-35], [Open: O-36] raised below.

## 3 Decisions and ADRs

| ID | Decision | Alternatives considered | Why chosen | Status |
|---|---|---|---|---|
| ADR-032 [Committee] | Dual-key enablement in `JurisdictionRegistry`: `record_legal` (human Legal or Compliance Agent) then `activate_flag` by a *different* human in a Compliance/Legal role; `is_live` = `JurisdictionCell.dual_key_satisfied()`; `disable_flag` is single-person (rollback); every change audited as `jurisdiction.flag.changed` | (a) single compliance approval + config flag; (b) time-locked activation with one approver | (a) one person could enable a market; (b) delay is not independence. Eligibility re-checks the cell on every intent (CP-JURIS-LEGAL / -FLAG / -DUALKEY), so a stale flag cannot trade | Proposed, pending Compliance & Legal Committee |
| ADR-033 [Committee] | Eligibility is a pure function `decide_eligibility(validated_intent, customer, instrument, cells, restricted, broker, feature, now)` with `ELIGIBILITY_BUILD_HASH`, deterministic `decision_id`, fail-closed `CP-HALT-INPUT` on any missing input, all failing checks listed | (a) rule-engine service with live DB lookups; (b) fold eligibility into the risk engine | (a) non-deterministic (R-01); (b) blurs 2nd-line ownership between Chief Risk and Compliance Agents | Proposed, pending Compliance & Legal Committee |
| ADR-034 [Committee] | The unit of enablement is the six-dimension cell key incl. `feature` (= operating mode); a different mode is a different cell (`CP-JURIS-NOCELL` for BOUNDED_AUTONOMOUS in TC-CP-004) | (a) country-level flag; (b) per-account allowlist | (a) ignores broker/venue/asset/mode differences [Source: 07]; (b) unscalable and unauditable | Proposed, pending Compliance & Legal Committee |
| D-P5-1 [Committee] | Manipulation-capable and out-of-scope strategies are refused at registration (`screen_strategy_declaration`: CP-SCOPE-*, CP-SURV-*) rather than at trade time | (a) trade-time surveillance only; (b) manual review | Out-of-scope capabilities must be structurally absent [Source: 01; C1 §3] | Proposed, pending Compliance Agent |
| D-P5-2 [Committee] | Retention/deletion: `RetentionService` suppresses deletion under retention schedule or legal hold and logs `retention.deletion.decided` | (a) hard delete on request; (b) never delete | Both violate one side of O-09; suppression with an audited decision is reversible | Proposed, pending Legal Agent / Privacy Lead |

## 4 RTM rows

| Requirement | Architecture element | Implementation owner | Control | Test IDs | Evidence path | Gate |
|---|---|---|---|---|---|---|
| FR-15 (eligibility) | `decide_eligibility`; `TradePipeline` eligibility step before risk | Backend Lead (Compliance Agent owns policy) | ELIGIBLE/INELIGIBLE with reason codes; deterministic; fail closed | TC-CP-001 `test_eligible_combination_passes_and_is_deterministic`; TC-CP-002 `test_ineligible_combinations_carry_reason_codes` | `test/quartets/test_tc_cp_eligibility.py` | D |
| FR-15 (dual key) | `JurisdictionRegistry.record_legal/activate_flag/disable_flag/is_live` | Backend Lead | Legal record + flag by different persons; single-person disable | TC-CP-003 `test_legal_record_without_flag_blocked`; TC-CP-004 `test_flag_without_record_blocked_then_dual_key_enables_and_disable_is_single_person` | same | D / F (H-17) |
| FR-15 (restricted lists, short-sale) | `RestrictedLists` (`policy_version` `lists-sim-v0.1`), CP-LIST-*, CP-SHORT, CP-SHORT-BAN, CP-PERM, CP-APPR | Compliance Agent | Ineligible combination rejected with reason code; decision absent (`r.decision is None`) | TC-CP-002 | same | D |
| FR-15 (surveillance) | `compliance_engine/surveillance.py` `surveil`, `screen_strategy_declaration` | Backend Lead | WASH_TRADE, SPOOFING, MARKING_THE_CLOSE detected; scope screen at registration | TC-CP-005 `test_surveillance_patterns_and_registration_screen` | same | D |
| FR-15 (retention) | `compliance_engine/retention.py` | Backend Lead (Legal/Privacy own policy) | Deletion suppressed under retention/legal hold, audited | TC-CP-006 `test_retention_deletion_suppressed_under_legal_hold` | same | D [Open: O-09] |
| FR-02 / [Source: 17] items 2, 7 | `run_certification` rows TC-BR-001..005 | Broker-Connector Lead (Trading Domain Lead reviews) | Broker capability certified per adapter | TC-BR-001..004; harness TC-BR-005 PASS | `docs/BROKER_CERTIFICATIONS/sim-broker.md` (12 PASS / 2 OPEN) | C |
| [Source: 17] items 3–6, 8, 12 (identifiers, sessions, currencies, tick/lot, settlement, corporate actions) | `InstrumentMaster`, `SessionCalendar`, `round_down_to_lot`, RK-INSTR-LOT/TICK/PIT | Data Engineering Lead / Backend Lead | Per-market validation | harness TC-BR-006 OPEN; TC-RK-010 (lot/tick/PIT reason codes, sim fixture) | `sim-broker.md`; `test_tc_rk_determinism.py` | F [Open: O-36] |
| [Source: 17] items 16–18 (support hours, incident contacts, disclosures) | `docs/SUPPORT_MODEL.md`, `docs/INCIDENT_RESPONSE.md`, approved copy | Support Lead, SRE Lead, Legal/GTM | Evidenced, not asserted | harness TC-BR-007 OPEN; disclosures GAP (H-16) | `docs/MARKET_LAUNCH_CHECKLIST.md` (all statuses blank) | F |
| CP-JURIS-NOCELL per mode | cell `feature` dimension | Backend Lead | Autonomy is a separate cell | TC-CP-004 (`feature="BOUNDED_AUTONOMOUS"` → NOCELL) | same | E |

## 5 Threat-model delta

| Threat | Boundary | Control in this build | Test | Residual / owner |
|---|---|---|---|---|
| T-07 Insider — one person enables a market | compliance → cell | Legal signer ≠ activator enforced in `activate_flag`; `CP-JURIS-DUALKEY` re-checked per intent even for a forged cell with same person | TC-CP-003 (same person denied; forged same-person cell → DUALKEY) | None in code; human process H-12/H-17. Compliance Agent |
| T-02 Agent enables a market | agent → registry | `activate_flag` and `record_legal` require `actor.is_human` | TC-CP-003 (agent denied) | None. MCP Security Agent |
| T-P5-1 Unauthenticated disable (new) | any actor → registry | `disable_flag` performs **no** role or `is_human` check; it only audits `disabled_by` | GAP | Fails safe (disables trading) but any caller, including an agent, could switch a market off — availability abuse. No BFF endpoint exposes it today → R-13. Backend Lead |
| T-P5-2 Legal record integrity (new) | Legal → registry | `legal_record_ref` is an unverified string; no document hash, signature or store | GAP | A fabricated reference satisfies the legal half of the dual key → O-35. Legal Agent |
| T-P5-3 Forged cell objects | pipeline inputs | `eligibility_inputs` reads cells from the registry only; forged cells only reachable in tests | TC-CP-003/004 (forged cells still fail LEGAL/DUALKEY) | Registry is in-memory; persistence and access control are E06 deployment scope. Backend Lead |
| T-08 Replay / intent tampering | edge → eligibility | `CP-INTEG` on hash mismatch (defence in depth before risk) | TC-RK-003 `test_tampered_intent_hash_rejected` (`eligibility.reason_codes == ("CP-INTEG",)`) | None. Integration Architect |
| R-04 Return-implying disclosures | GTM | Checklist item 18 requires "approved copy (no return claims)" | GAP | Nothing drafted (H-16). GTM Lead, Legal Agent |

## 6 Control quartet per critical control

| Control | Positive | Negative | Abuse | Recovery |
|---|---|---|---|---|
| Dual-key cell activation | TC-CP-004 (legal by LEGAL, flag by COMPLIANCE → live, ELIGIBLE) | TC-CP-003 (legal record only → CP-JURIS-FLAG); TC-CP-004 (flag without record impossible; forged flag-only cell → CP-JURIS-LEGAL) | TC-CP-003 (same person; agent; forged same-person cell → CP-JURIS-DUALKEY) | TC-CP-004 (single-person `disable_flag` → INELIGIBLE; `jurisdiction.flag.changed` audited) |
| Eligibility decision (deterministic, fail closed) | TC-CP-001 (`d1 == d2`, policy version) | TC-CP-002 (venue, instrument, whitelist, permission, short-sale codes) | TC-RK-003 (CP-INTEG on tampered intent) | TC-CP-002 (`CP-HALT-INPUT` on missing inputs) — restore after input recovery: GAP |
| Restricted lists and whitelist | TC-CP-001 | TC-CP-002 | GAP — list tampering / version rollback | GAP — list update propagation |
| Registration screen (scope and surveillance) | TC-CP-005 (`register` refuses advice-providing strategy) | TC-CP-005 (`screen_strategy_declaration` codes) | GAP — declaration understates capability | GAP |
| Trade surveillance patterns | TC-CP-005 (wash, spoof, close) | GAP — benign flow yields no pattern | GAP | GAP — case handling/escalation |
| Retention and legal hold | TC-CP-006 (SUPPRESSED_RETENTION, SUPPRESSED_LEGAL_HOLD, DELETED after release) | TC-CP-006 | GAP — hold release by unauthorised actor | TC-CP-006 (release → DELETED, 3 audited decisions) |
| Instrument-master validation per market | GAP (TC-BR-006 OPEN) | GAP | GAP | GAP — [Open: O-36] |

## 7 Evidence list

| Evidence | Path |
|---|---|
| Dual-key registry; eligibility function | `services/compliance/compliance_engine/jurisdiction.py`; `eligibility.py` |
| Surveillance and registration screen; retention | `services/compliance/compliance_engine/surveillance.py`; `retention.py` |
| Cell and list schemas | `libs/core/rtcore/schemas/compliance.py` (`JurisdictionCell.key`, `dual_key_satisfied`, `RestrictedLists`) |
| Fixture cell and enablement wiring | `apps/web/web_bff/platform.py` (`JURISDICTION = "ZZ"`, `build_sim_platform(enable_cell=...)`) |
| Matrices and checklist (no enabled rows; all statuses blank) | `docs/COMPLIANCE_MATRIX.md`; `docs/JURISDICTION_MATRIX.md`; `docs/MARKET_LAUNCH_CHECKLIST.md`; `docs/POST_LAUNCH_REVIEW.md` |
| External workflow and human acts | `goals/external/legal_regulatory_engagement.md`; `goals/external/broker_onboarding.md`; `goals/external/data_licensing.md`; `docs/MISSING_ACTIONS.md` H-03, H-04, H-07, H-08, H-12, H-16, H-17 |
| Broker certification output | `docs/BROKER_CERTIFICATIONS/sim-broker.md` (generated by `scripts/certify_broker.py`; reviewer pending) |
| Tests and evidence records (2026-09-07T17:28:57Z, 104 passed, env `dev`) | `test/quartets/test_tc_cp_eligibility.py`; `test/quartets/test_tc_br_broker.py`; `test/quartets/test_tc_rk_determinism.py`; `test/evidence/evidence_index.json` |
| Governance | `docs/COMMITTEE_DEEP_DIVE.md` §C6, §P5; `goals/07_compliance_agent.md`; `goals/08_legal_agent.md`; `goals/build/E06_compliance_eligibility.md`, `E15_regulatory_market_launch.md` |

## 8 RAID entries, assumptions, confidence, provenance

| ID | Type | Item | Owner | Needed by | Status |
|---|---|---|---|---|---|
| O-35 | Gap | Legal record integrity: `legal_record_ref` is a free string; no signed document store, hash anchoring in the audit chain or counsel-opinion register; the legal half of the dual key is unverifiable in code | Legal Agent (Backend Lead builds) | Gate D | Open |
| O-36 | Gap | Market-launch technical items (instrument identifiers, sessions/holidays, currencies, settlement, corporate actions, taxes/fees) have no per-market validation suite; harness row TC-BR-006 is OPEN; `MARKET_LAUNCH_CHECKLIST.md` statuses blank | Trading Domain Lead, Data Engineering Lead | Gate F | Open |
| R-13 | Risk | `JurisdictionRegistry.disable_flag` has no actor authorisation (`is_human`/role) — any caller can disable a market; fails safe but is an availability-abuse path once exposed through an API | Backend Lead (Compliance Agent reviews) | Gate D | Open |
| O-11, O-12, O-09, O-10, O-15 | carried | first jurisdiction; data licensing; legal hold; DPIA; support hours | Product Director/Compliance Agent; Legal Agent/Data Architect; Legal/Privacy; Privacy Lead; SRE/Support | A / C / D / D / F | Open |

Assumptions: the "ZZ" fixture cell exists only so the pipeline can be exercised; enabling any real cell requires H-03, H-04, H-07, H-08, H-12, H-16 and H-17. Confidence: high for the dual-key and eligibility semantics asserted by TC-CP-001..006; none for any regulatory position, broker capability or data entitlement (none exists). Provenance: code read on 2026-09-07; evidence index sha `HEAD`. Reviewer: Trading Domain Lead pending; approver: Compliance & Legal Committee pending; IVA verdict pending.
