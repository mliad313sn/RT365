# Session C6 — Compliance, Market Access & Market Readiness (blueprint 07, 17)

**Environment:** dev/sim only. The only jurisdiction cell is `ZZ / RETAIL / sim-broker / SIMX / EQUITY / PAPER`, a fixture; "worldwide" never means legal availability; no regulator, licence, broker or venue is implied [Open: O-11]. Documented by the Program Orchestrator (1st line, recommends, never approves).

## 1 Roles

| Function | Role (line) | Basis |
|---|---|---|
| Accountable | Compliance Agent and Legal Agent (2nd line) | COMMITTEE_DEEP_DIVE §C6 |
| Consulted | Trading Domain Lead, Broker-Connector Lead, Data Engineering Lead, Support Lead | COMMITTEE_DEEP_DIVE §C6 |
| Builder | Backend Lead (1st line) — `services/compliance/compliance_engine/{eligibility.py,jurisdiction.py,surveillance.py,retention.py}`; Frontend/Support Leads — `apps/web/web_bff/reason_codes.py` -> `docs/REASON_CODES.md` | RACI; Backend Lead cannot merge `/services/compliance` without 2nd-line CODEOWNER |
| Challenger (different line) | Compliance Agent (2nd line) — CODEOWNER for `/services/compliance`, `COMPLIANCE_MATRIX.md`, `JURISDICTION_MATRIX.md`; challenged dual-key semantics and registration screen | `.github/CODEOWNERS` |
| Assurance / IVA | Compliance & Legal Committee (enablement), Independent Validation Agent (CODEOWNER on `/services/compliance`) | COMMITTEE_DEEP_DIVE §C6 |

Statement: author != reviewer != approver. Backend Lead built; Compliance Agent challenges; IVA verifies; Compliance & Legal Committee enables a cell only with Legal co-signature and never on this packet. Nothing here is self-certified.

## 2 Purpose

- [Source: 07, 17] Launch matrix per country × customer type × broker × venue × asset class × feature; 18-item market-readiness checklist; suitability, restricted lists, surveillance, retention, tax, data licensing, marketing restrictions.
- [Source: 01] Manipulation-capable strategies and other out-of-scope capabilities are excluded.
- [Committee] Dual key: a cell is live only when a signed legal record exists (`record_legal`) and a *different* human activates the technical flag (`activate_flag`); disabling is single-person (ROLLBACK_PLAN). Eligibility is a pure function (`decide_eligibility`) with reason codes and `policy_version` from the restricted lists; missing inputs -> `CP-HALT-INPUT`. Surveillance pattern library (wash, spoofing/layering, marking the close, momentum ignition) plus a registration screen (`screen_strategy_declaration`). Every reason code has a plain-language explanation and a "what you can do" line, never advice or a return promise (`docs/REASON_CODES.md`).
- [Open: O-11] first jurisdiction; [Open: O-12] data licensing; [Open: O-21] surveillance parameters are fixtures; [Open: O-09] legal hold.

## 3 Decisions and ADRs

| # | Decision | Alternatives compared | Why chosen | Evidence |
|---|---|---|---|---|
| C6-D1 | Dual key enforced in `JurisdictionRegistry`: `activate_flag` refuses agents, non-compliance/legal roles, missing legal record and the same person as the legal signer; `JurisdictionCell.dual_key_satisfied()` is re-checked inside `decide_eligibility` (`CP-JURIS-LEGAL`, `CP-JURIS-FLAG`, `CP-JURIS-DUALKEY`), so a forged cell object still fails. | (a) One compliance approval with MFA; (b) flag in configuration + legal record in a document; (c) chosen: two records, two persons, checked by the engine at decision time. | [Source: 07] either alone is insufficient; (c) makes bypass through configuration impossible because the engine recomputes the condition. | TC-CP-003, TC-CP-004 |
| C6-D2 | Eligibility as a deterministic pure function mirroring C4: `ELIGIBILITY_BUILD_HASH`, `deterministic_id`, all checks evaluated, reason codes deduplicated, `EligibilityDecision` exported as `eligibility.decided.v1`. | (a) Rule engine with external DSL; (b) chosen: code with the same determinism contract as the risk engine. | Same evidence and replay properties as C4 (ADR-014). | TC-CP-001, TC-CP-002 |
| C6-D3 | Out-of-scope and manipulation-capable strategies rejected at registration through a declared behaviour model (`StrategyDeclaration`: two-sided resting quotes, cancel ratio, closing-window trading, replication of other accounts, personal advice) — `StrategyRegistry.register` stores the version as REJECTED and audits reasons. | (a) Post-trade surveillance only; (b) chosen: registration screen plus post-trade library. | [Committee C6 §4] and SCOPE.md: prevention before any capital is at risk. Declarations are self-reported; surveillance is the backstop (R-12). | TC-CP-005 |
| C6-D4 | Reason-code dictionary as code (`REASON_CODES` dict) rendered to `docs/REASON_CODES.md` by `scripts/export_reason_codes.py`; a contract test fails if any code lacks an entry. | (a) Markdown maintained by hand; (b) chosen: generated from code with a test. | Every code the engines can emit is documented (`test_reason_codes_all_documented`); text is reviewed by the Compliance Agent. | **Proposed ADR-016** [Committee] |
| C6-D5 | Records retained with legal hold (see C5-D3, proposed ADR-020). | — | — | TC-CP-006 |

Standing ADRs: ADR-001 (compliance sits in the Control plane), ADR-005 (`jurisdiction.flag.changed.v1`, `eligibility.decided.v1`).

## 4 RTM rows

| Requirement | Architecture element | Implementation owner | Control | Test IDs | Evidence path | Gate |
|---|---|---|---|---|---|---|
| FR-15 (eligibility, restricted lists) | `decide_eligibility`, `RestrictedLists` (`policy_version` `lists-sim-v0.1`) | Backend Lead | Deterministic ELIGIBLE/INELIGIBLE with reason codes; fail closed | TC-CP-001, TC-CP-002 | `test/quartets/test_tc_cp_eligibility.py` | D |
| FR-15 (dual-key enablement) | `JurisdictionRegistry`, `JurisdictionCell.dual_key_satisfied` | Backend Lead | Two records, two persons; single-person disable | TC-CP-003, TC-CP-004 | same; `contracts/events/jurisdiction.flag.changed.v1.json` | D |
| FR-15 (surveillance) | `surveil`, `screen_strategy_declaration` | Backend Lead | Pattern detection; registration screen | TC-CP-005 | `services/compliance/compliance_engine/surveillance.py` | D — GAP: not wired post-trade (O-35) |
| FR-15 (retention) | `RetentionService` | Backend Lead | Suppress under hold | TC-CP-006 | C5 packet | D |
| FR-16 (plain-language reason codes) | `reason_codes.py`, `/v1/reason-codes` endpoint | Frontend / Support & Training Leads | Every code documented; no advice/return language | `test_reason_codes_all_documented` | `docs/REASON_CODES.md` | C |
| FR-02 (capability certification feeds readiness) | `broker_adapters.certification`, `scripts/certify_broker.py` | Broker-Connector Lead | Unsupported order types rejected | TC-BR-002, TC-EX-006 | `docs/BROKER_CERTIFICATIONS/TEMPLATE.md` | C |
| [Source: 17] market-readiness checklist as tests | Instrument master tick/lot, session calendar (`RK-INSTR-*`, `RK-SESS`) | Backend Lead / Data Engineering Lead | Venue with a failing test stays disabled | TC-RK-010 instrument/session rows | `services/market-data/market_data/{instruments.py,calendar.py}` | C — partial (18 items not all mapped) |

## 5 Threat-model delta

| Threat | Boundary | Control | Test | Owner |
|---|---|---|---|---|
| T-07 Insider misuse (self-enabling a market) | B2 | Dual key: signer != activator; agents denied; engine recomputes | TC-CP-003 | Security & Privacy Board / Compliance Agent |
| T-02 Excessive agency (agent activates a flag) | B2 | `activate_flag` requires human Compliance/Legal role | TC-CP-003 | MCP Security Agent |
| NEW T-25 Forged `JurisdictionCell` injected into eligibility inputs | B2 | Engine checks legal record, flag and distinct persons on the object itself | TC-CP-003, TC-CP-004 (forged cells) | Backend Lead |
| NEW T-26 Strategy misdeclares behaviour to pass the registration screen | B3 | Post-trade `surveil` library as backstop; not yet wired | TC-CP-005 (library only) — GAP for wiring | Compliance Agent (O-35, R-12) |
| NEW T-27 Sim fixture cell promoted to a real environment (`build_sim_platform(enable_cell=True)` auto-signs with fixture actors) | B8 | None in code; must be an environment assertion | GAP (R-13) | Compliance Agent, Cloud Architect |

## 6 Control quartet per critical control

| Control | Positive | Negative | Abuse | Recovery |
|---|---|---|---|---|
| Eligibility engine | TC-CP-001 `test_eligible_combination_passes_and_is_deterministic` | TC-CP-002 `test_ineligible_combinations_carry_reason_codes` (restricted instrument/venue, permission, short-sale ban, missing inputs) | TC-CP-003 (same-person cell -> `CP-JURIS-DUALKEY`) | TC-CP-004 (cell disabled -> INELIGIBLE; feature mismatch -> `CP-JURIS-NOCELL`) |
| Dual-key market enablement | TC-CP-004 `test_flag_without_record_blocked_then_dual_key_enables_and_disable_is_single_person` (dual key -> live) | TC-CP-003 `test_legal_record_without_flag_blocked` | TC-CP-003 (same signer/activator, agent activation) | TC-CP-004 (single-person disable = rollback; audit `jurisdiction.flag.changed`) |
| Surveillance / registration screen | TC-CP-005 `test_surveillance_patterns_and_registration_screen` (clean declaration registers) | TC-CP-005 (synthetic wash/spoof/close detected) | TC-CP-005 (market-making, copy-trading, advice declarations rejected) | GAP — no test that a detected pattern moves the account to Supervised/Halted (P6 linkage) |
| Retention / legal hold | TC-CP-006 | TC-CP-006 | TC-CP-006 | TC-CP-006 |
| Reason-code dictionary | `test_reason_codes_all_documented` | GAP — no test rejecting advice/return-promise wording (R-04) | GAP | GAP |

## 7 Evidence list

- `docs/COMPLIANCE_MATRIX.md`, `docs/JURISDICTION_MATRIX.md`, `docs/MARKET_LAUNCH_CHECKLIST.md`, `docs/REASON_CODES.md`, `docs/BROKER_CERTIFICATIONS/TEMPLATE.md`, `docs/POST_LAUNCH_REVIEW.md`
- `services/compliance/compliance_engine/{eligibility.py,jurisdiction.py,surveillance.py,retention.py}`, `libs/core/rtcore/schemas/compliance.py`, `apps/web/web_bff/reason_codes.py`, `scripts/export_reason_codes.py`
- `test/quartets/test_tc_cp_eligibility.py` (TC-CP-001..006), `test/contract/test_openapi_alignment.py::test_reason_codes_all_documented`, `contracts/events/{eligibility.decided.v1,jurisdiction.flag.changed.v1}.json`

## 8 RAID entries, assumptions, confidence, provenance

| ID | Type | Item | Owner | Gate |
|---|---|---|---|---|
| O-35 | Gap | `surveil()` is exercised only by TC-CP-005; no post-trade job feeds gateway fills into it or routes alerts to P6 (Supervised/Halted) | Backend Lead, Compliance Agent | D |
| O-36 | Gap | Market-readiness checklist (18 items) is only partially represented as tests (tick/lot, session, order types); settlement, corporate actions, short-sale rules, tax and data entitlement have no tests | Trading Domain Lead, Broker-Connector Lead | C |
| R-12 | Risk | `StrategyDeclaration` is self-reported; a misdeclared strategy passes registration until surveillance (unwired) catches it (T-26) | Compliance Agent, Model Risk Lead | D |
| R-13 | Risk | `build_sim_platform(enable_cell=True)` activates the fixture dual key with fixture actors; if reused outside sim it would fake enablement (T-27) — needs an environment guard (`RT_ENV`) | Compliance Agent, Cloud Architect | C |

Assumptions: `lists-sim-v0.1`, jurisdiction `ZZ`, broker `sim-broker`, venue `SIMX` and customer `cust-sim-001` are fixtures; no legal opinion exists (MISSING_ACTIONS H-04, H-12, H-17).

Confidence: **high** for dual-key and eligibility determinism (code and tests read); **medium** for the registration screen; **low** for surveillance effectiveness and market-readiness coverage.

Provenance: [Source: 01, 07, 09, 17] scope, dual key, checklist, reason-code intent; [Committee] engine design, ADR-016/020 proposals; [Open] O-09, O-11, O-12, O-21, O-35, O-36. Evidence cited by path; Compliance & Legal Committee sign-off pending and never assumed.
