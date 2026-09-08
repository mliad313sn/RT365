# BUILD_E06_2026-09-08_compliance_fields — legal-record integrity, customer standing fields, persona and cell-exactness tests (B-10)

| Session | Date | Author | Line | Status |
|---|---|---|---|---|
| Build packet E06 (register item B-10 under delegation D-051) | 2026-09-08 | build-e06 agent (AI) for the Backend Lead | 1st | built and tested in dev/sim; review requested from the Compliance Agent (CODEOWNER, 2nd line) and the Independent Validation Agent (3rd line); nothing here is an approval |

**Commits:** code, tests, contracts and evidence at e6d103f; this packet and the AEI row in the following commit on the same branch.

**Environment:** dev/sim only. Branch `build/e06-compliance-fields`, not pushed. The only jurisdiction cell in code remains `ZZ` (user-assigned, not a jurisdiction, D-012). Nothing in this packet enables a market, a mode, a strategy, a broker or autonomy; no regulatory position is asserted — the shape of a legal record is a data-integrity control, not legal advice [Source: 00, 07; Committee]. Profit is an objective, never a promise [Source: 00].

## 1 Roles [Source: 13]

| Function | Role (line) | Note |
|---|---|---|
| Builder (author of code and tests) | build-e06 agent for the Backend Lead (1st) | may not approve, certify or promote |
| 2nd-line reviewer / CODEOWNER | Compliance Agent (2nd) — `/services/compliance`, reason-code text | review pending |
| Contract reviewer | Integration Architect (1st, different owner) — `/contracts/events` regenerated schema | review pending |
| Owning roles for out-of-scope edits made on the delegator's instruction | Frontend / Support and Training Leads (`apps/web/web_bff/reason_codes.py`); E10 build owner (`apps/web/web_bff/platform.py` sim fixture) | to acknowledge or amend |
| Assurance | Independent Validation Agent (3rd) | may veto the evidence |
| Decider | Human Product Owner (D-039) | records decisions; the "Concerns" section is addressed to the Product Owner |

Author != reviewer != approver. The builder recorded no approval, edited no ledger row in RAID_LOG.md or REQUIREMENTS_TRACEABILITY.md (proposed text below), and closed no open item.

## 2 Purpose

- [Source: 07] A cell is live only with a signed legal record and a technical flag by different persons; customer type, product permissions and jurisdiction cell are eligibility inputs; "worldwide" never means legal availability.
- [Source: 00, 01] Autonomy default OFF; control personas have no trading mode; AI/MCP components never change mode.
- [Committee: COUNCIL_2026-09-08_gate_A_compliance_legal F-2/P-2, F-3/P-3/P-4, X-5, X-6] `legal_record_ref` was a free string (a fabricated reference passed); `CustomerProfile` had no disclosure acknowledgement, no per-mode consent and no classification evidence, so a self-declared "professional" would have bypassed retail protections through an eligibility input.
- [Committee: COUNCIL_2026-09-08_gate_A_product_director §4.4 rules 1-4; D-045] a persona is never an entitlement; the six-dimension cell and the gate record are; tenant admin cannot change mode; customer type is never self-declared.
- [Committee: IMPROVEMENT_REGISTER B-10; D-051] this packet delivers the first five bullets of B-10. Not delivered here: surveillance wiring at strategy registration beyond the existing screen, and reporting adapters (E11) — both remain open under B-10 / BACKLOG P9.
- [Open: Q-J06, Q-P03, Q-P04, H-16, H-04] which disclosures, which classification bases and which consent rules apply in a real cell are counsel questions; the code only makes their absence fail closed.

## 3 Design choices made in code (proposed decision rows; the Product Owner records or rejects them) [Committee]

| Proposed ID | Choice | Alternatives compared | Why chosen |
|---|---|---|---|
| D-new-1 | `LegalRecordRef` = record id (3-64 upper-case chars, digits, ._-), signing entity (as written on the document), signature date, SHA-256 of the document; `record_legal` accepts only this type; `JurisdictionCell` validates label consistency (SIM- records only on simulated cells and only SIM- records there; the `simulated` label is derived from the country code) | (a) keep a free string plus a naming convention; (b) typed reference, hash checked for shape only (chosen); (c) content-addressed document store with the hash verified against a stored blob and anchored in the audit chain | (a) is the finding; (c) needs a document store and a legal-record process that does not exist yet (H-04, H-12) — the typed reference is the minimum that makes fabrication detectable now and is forward-compatible with (c); the hash is anchored today through the `jurisdiction.legal.recorded` audit payload |
| D-new-2 | Customer standing as typed sub-models: `DisclosureAcknowledgement(version, acknowledged_at)`, `ModeConsent(mode, consented_at, consent_ref)` (one per mode, never transitive), `ClassificationEvidence(evidence_ref, assessed_by, assessed_at, basis)` with `ClassificationBasis` = ASSESSOR_REVIEW, DOCUMENTARY_EVIDENCE, SELF_DECLARED | (a) booleans (`disclosures_ok`, `consented`); (b) free strings as proposed in P-3/P-4; (c) typed models with timestamps and an explicit refused basis (chosen) | (a) and (b) cannot express "which version", "which mode", "by whom" or "self-declared", so they cannot fail closed on the abuse the council named (X-5); (c) keeps every value on the decision record with a threshold |
| D-new-3 | Enforcement at decision time: CP-CLASS for every customer without third-party, non-future-dated, non-self-declared evidence (all customer types, stricter than P-4's opt-up-only scope); CP-DISCL when no acknowledgement, a different version than the cell requires, or a future-dated one; CP-MODE-CONSENT only for SUPERVISED and BOUNDED_AUTONOMOUS (PAPER needs none) | (a) enforce only in the UI/onboarding; (b) enforce for opt-up types only; (c) enforce for all customers at decision time (chosen) | The delegator's instruction and the council (P-3: "at decision time, not only in UI") require (c); RETAIL classification is still an assessment someone made, so it must be evidenced too. Whether PAPER should also need consent is left to the Product Owner (section 9) |
| D-new-4 | `JurisdictionCell.required_disclosure_version` set by `propose(...)`; when a cell has none, any non-future acknowledgement passes | (a) global disclosure version; (b) per-cell version (chosen); (c) per-cell and per-customer-type | Disclosures are approved per cell and language (H-16); (c) can be added without a schema break |
| D-new-5 | Registry audit rows carry `correlation_id = "jurisdiction:" + "/".join(cell.key)` | (a) "-" as today; (b) per-call UUID; (c) deterministic per cell (chosen) | (c) lets an auditor pull every proposal, record and flag change of a cell with one query and is replay-stable |

No ADR: no standard changed; the event `jurisdiction.flag.changed.v1` gained a nested object and an optional field (additive; ADR-005 drift check regenerated, Integration Architect to review).

## 4 Proposed RTM row text (Program Orchestrator edits docs/REQUIREMENTS_TRACEABILITY.md; not edited here)

| Requirement | Architecture element | Owner | Control | Test IDs | Evidence path | Gate | Status |
|---|---|---|---|---|---|---|---|
| FR-15 | Eligibility engine, jurisdiction registry, restricted lists, surveillance, retention (`compliance_engine`); typed legal record (`LegalRecordRef`), customer standing fields (`CustomerProfile.disclosure_acknowledgement / mode_consents / classification_evidence`) | Backend Lead | Deterministic eligibility; dual key with typed, hashed legal record (SIM- only on simulated cells); CP-CLASS / CP-DISCL / CP-MODE-CONSENT fail closed; six-dimension cell match exact per CustomerType x mode; legal hold suppresses deletion | TC-CP-001..012 | TEST_CASES/TC-CP.md | D | dev/sim; no real cell enabled [Open: O-11]; classification bases, disclosure versions and consent rules per cell are counsel questions [Open: Q-J06, Q-P03, Q-P04, H-16] |
| FR-01 | Identity service: RBAC/PIM/MFA (`identity_service.rbac`), maker-checker, mode ladder (`identity_service.accounts`); persona is never an entitlement | Backend Lead | Maker != checker, different lines, cooling period; MFA; PIM; two-person exit from HALTED; absent out-of-scope permissions; roles without a trading persona (tenant admin, control, read, governance, assurance) cannot change mode, restore from halt or submit intents (registry, RBAC, BFF) | TC-ID-001..006 | TEST_CASES/TC-ID.md | B | dev/sim evidenced; IdP/MFA integration [Open: MISSING_ACTIONS]; RBAC/registry mode-changer mismatch [Open: see packet section 9] |

## 5 Threat-model delta (proposed rows for docs/THREAT_MODEL.md; Security Architect owns)

| ID | Threat | Boundary | Mitigation in this change | Test | Owner |
|---|---|---|---|---|---|
| T-52 | Fabricated legal record: a string that looks like a reference satisfies the legal half of the dual key (council F-2/P-2) | B2 | `record_legal` accepts only `LegalRecordRef` (id pattern, named signing entity, date, 64-hex SHA-256); dict/str refused with ControlDenied; record anchored in `jurisdiction.legal.recorded` with correlation_id; only the stored cell is updated (a caller-side cell object is ignored; unknown cells refused) | TC-CP-008 | Backend Lead / Compliance Agent |
| T-53 | Sim evidence dressed as real: a real-looking record on the ZZ cell, a SIM- record on a real-country cell, or a forged `simulated=False` label (council X-6, D-012) | B2 | Schema validator derives the label from the country code and refuses SIM-/real mismatches in both directions; registry re-validates on record | TC-CP-008, TC-GLO-002/003 | Backend Lead |
| T-54 | Self-declared classification bypasses retail protections through an eligibility input (council X-5/P-4, D-045) | B3 | CP-CLASS for absent, self-declared, self-assessed or future-dated evidence; evidence is a typed model (no free strings, no unknown basis) | TC-CP-010, TC-CP-011 | Backend Lead / Compliance Agent |
| T-55 | Mode operated without recorded customer consent or without acknowledged disclosures (Q-J06, Q-P04) | B3 | CP-MODE-CONSENT for SUPERVISED/BOUNDED without a non-future consent for that exact mode; CP-DISCL for missing/stale/future acknowledgement against the cell's required version; withdrawal takes effect on the next decision | TC-CP-010, TC-CP-012 | Backend Lead |
| T-56 | Persona read as entitlement: a control/read/governance role (tenant admin in particular) changes a mode, restores from halt or submits an intent (D-045; product_director T-28) | B1/B3 | Registry MODE_CHANGERS, RBAC permissions and BFF 403 evidenced for 17 roles; agent path re-asserted | TC-ID-006 | Backend Lead / Security Architect |
| T-57 | Cell granted for one CustomerType x mode read as covering another | B2 | Six-dimension exact match evidenced for all 4 x 3 pairs against a live PROFESSIONAL/PAPER cell | TC-CP-009 | Backend Lead / Compliance Agent |

## 6 Control quartets touched (all pass in dev/sim, 188 tests)

| Control | Positive | Negative | Abuse | Recovery |
|---|---|---|---|---|
| Dual key with typed legal record | TC-CP-001 (fixture record is typed, simulated, hash on the decision) | TC-CP-002 (unchanged) | TC-CP-003, TC-CP-007 (unchanged, now with typed records), TC-CP-008 (new) | TC-CP-004 (unchanged) |
| Customer standing (classification, disclosure, consent) | TC-CP-001 (all checks PASS for the fixture; PAPER needs no consent) | TC-CP-010 (new) | TC-CP-011 (new) | TC-CP-012 (new) |
| Cell exactness CustomerType x mode | TC-CP-009 PROFESSIONAL/PAPER case | TC-CP-009 (11 NOCELL cases), TC-CP-004 (BOUNDED without cell) | TC-CP-011 (live PROFESSIONAL cell does not help a self-declared customer) | TC-CP-004 |
| Persona vs mode (FR-01) | TC-ID-003 (authorised promotion with gate record) | TC-ID-002 | TC-ID-003, TC-ID-005, TC-ID-006 (new) | TC-ID-004 |
| Global compatibility label | TC-GLO-001 (XK registry row stays a country) | TC-GLO-002 | TC-GLO-003 (typed SIM record in the audit) | TC-GLO-004 |

## 7 Evidence

| Evidence | Location |
|---|---|
| Quartet evidence (generated, reviewer signature pending by construction) | docs/TEST_CASES/TC-CP.md (23 records), docs/TEST_CASES/TC-ID.md (6 records), docs/TEST_CASES/TC-GLO.md, docs/TEST_CASES/EVIDENCE_REPORT.md (168 records, 18/18 areas complete) |
| Tests | test/quartets/test_tc_cp_eligibility.py (TC-CP-008..012), test/quartets/test_tc_id_identity.py (TC-ID-006), test/quartets/test_tc_glo_global.py, test/conftest.py (`sim_legal_record` helper) |
| Code | libs/core/rtcore/schemas/compliance.py; services/compliance/compliance_engine/eligibility.py; services/compliance/compliance_engine/jurisdiction.py |
| Out-of-scope edits on the delegator's instruction (owning roles to acknowledge) | apps/web/web_bff/platform.py (fixture customer standing, typed SIM legal record, `required_disclosure_version`); apps/web/web_bff/reason_codes.py (CP-DISCL, CP-MODE-CONSENT, CP-CLASS) and docs/REASON_CODES.md (generated, 93 codes) |
| Contract | contracts/events/jurisdiction.flag.changed.v1.json (nested LegalRecordRef, optional required_disclosure_version; additive) |
| Pipeline | `make all` green (lint, mypy 97 files, schema drift OK, policy checks, 67 agents match goals/, secret scan, 188 passed, evidence) |

## 8 Proposed RAID updates (Program Orchestrator records; nothing edited here)

| ID | Proposed text |
|---|---|
| O-71 (closure proposal, P-2 half) | Status to "Remediated in dev/sim 2026-09-08 (P-2 half): `legal_record_ref` is a typed `LegalRecordRef` (id, signing entity, date, SHA-256); `record_legal` refuses strings and label mismatches; SIM- records only on simulated cells; TC-CP-008 (abuse). Compliance Agent review due Gate B (AEI #36). Residual: the hash is checked for shape and anchored in the audit payload, not verified against a stored document (no legal-record store exists, H-04/H-12) — proposed follow-up O-new-A. Surveillance-wiring half stays open under E06 P9 / B-10." |
| O-new-A | Gap: no legal-record document store; `LegalRecordRef.document_sha256` is not verified against a stored blob. Owner Backend Lead, Legal Agent (process); needed by Gate D |
| O-new-B | Gap: classification bases that count per cell, disclosure versions per cell/language, consent expiry and renewal are undecided (Q-P03, Q-J06, Q-P04); engine treats any non-self-declared basis and any recorded consent as sufficient. Owner Compliance Agent, Legal Agent; needed by Gate D |
| O-new-C | Gap: `identity_service.accounts.MODE_CHANGERS` (RISK_OFFICER, CHIEF_RISK_AGENT, PORTFOLIO_MANAGER, COMPLIANCE_AGENT, SRE_LEAD, TRADING_DOMAIN_LEAD) and RBAC `Permission.CHANGE_MODE` (PORTFOLIO_MANAGER, RISK_OFFICER, CHIEF_RISK_AGENT) disagree; control personas Risk officer / Compliance analyst are "no trading mode" in §4.4 yet RISK_OFFICER and COMPLIANCE_AGENT can promote in the registry (R-05 re-raised). Owner Backend Lead; decision Product Owner; needed by Gate D |
| O-new-D | Gap: consent, acknowledgement and classification are set on the profile by whoever edits `p.customers`; no onboarding write path, maker-checker or audit event exists for recording them. Owner Backend Lead (E01/E14); needed by Gate D |
| R-49 | No change; TC-CP-007 re-run green with typed records |

**Assumptions [Committee]:** the fixture consents for all three modes and the fixture assessor "compliance.fixture" are labelled simulated and are not evidence of any onboarding; the disclosure version "SIM-DISCL-v0.1" is a fixture string, not an approved pack (H-16); the SIM- prefix convention is the only marker of a simulated legal record and is enforced against the cell label.

**Confidence:** high that the tests evidence what their docstrings say (188 green at the tested tree recorded in TEST_CASES headers); high that no cell, mode or market was enabled (ZZ only; dual key untouched apart from typing); none on which bases, versions or consent rules a real cell needs (counsel).

**Provenance:** [Source: 00, 01, 07, 13] posture, out-of-scope list, cell dimensions, three lines; [Committee] council packets 2026-09-08 (compliance_legal F-2/F-3/P-2..P-4/X-5/X-6; product_director §4.4/T-28), D-043, D-045, D-051, IMPROVEMENT_REGISTER B-10; [Open] every legal question cited. Files read at HEAD d1ccb21 on 2026-09-08.

## 9 Concerns for the Product Owner

Design choices the PRD leaves open (each is implemented one way in dev/sim and can be reversed before any real customer record exists; none asserts a regulatory position):

1. **What counts as classification evidence [Open: Q-P03].** The engine accepts any `ClassificationBasis` other than SELF_DECLARED (ASSESSOR_REVIEW, DOCUMENTARY_EVIDENCE) from any assessor id that is not the customer. It does not check that the assessor holds a role, that the evidence reference resolves to a document, or that the assessment is recent. Which bases, which assessors and what recency a real cell requires is a counsel question; the enum can be narrowed per cell later.
2. **Classification evidence is required for every customer type, including RETAIL.** The council proposed CP-CLASS for opt-up types only (P-4); the delegation asked for "any customer". I implemented the stricter reading. If the Product Owner prefers the narrower one, TC-CP-010 changes and the fixture stays valid.
3. **Consent expiry and renewal [Open: Q-P04].** A `ModeConsent` never expires and has no version; withdrawal is modelled only as removal from the profile. Whether consent must be renewed (per period, per disclosure version, per strategy) and whether withdrawal must itself be an audited, dated record is open.
4. **PAPER needs no consent.** Only SUPERVISED and BOUNDED_AUTONOMOUS require a recorded consent (as instructed). If PAPER with a real broker sandbox is treated as a customer-facing mode in the first cell (D-043), the Product Owner may want consent there too (one-line change to `CONSENT_REQUIRED_MODES`).
5. **Disclosure version semantics [Open: Q-J06, H-16].** A cell may carry `required_disclosure_version`; a cell without one accepts any acknowledged version. The fixture sets "SIM-DISCL-v0.1". Versions per language, per customer type and re-acknowledgement on change are not modelled.
6. **Legal record: shape, not content [O-71 residual].** `LegalRecordRef` proves that a caller supplied an id, a named signer, a date and a well-formed SHA-256, and anchors them in the audit chain. There is no document store, so the hash is not compared against a stored document, the signing entity is not checked against a counsel of record (H-04), and the signature date is not checked against the clock (no clock is passed to `record_legal`). This is weaker than "the legal half of the dual key is verified"; it makes fabrication detectable, not impossible.
7. **Simulated-record convention.** A record id prefixed "SIM-" is the only marker of a fixture record; the schema enforces it against the cell label in both directions (a real-looking record on ZZ is refused, a SIM- record on FR is refused). If the Product Owner wants a stronger marker (a dedicated flag signed by the fixture actor), that is a schema change.
8. **Registry versus RBAC on who may change a mode (R-05 re-raised).** TC-ID-006 evidences that 17 roles without a trading persona cannot change mode. It deliberately excludes RISK_OFFICER, CHIEF_RISK_AGENT, COMPLIANCE_AGENT, SRE_LEAD and TRADING_DOMAIN_LEAD, which `MODE_CHANGERS` allows although §4.4 lists Risk officer and Compliance analyst as "no trading mode" personas, and although RBAC grants CHANGE_MODE to a different set. Nothing was changed there (identity service is outside this epic and the existing quartet relies on RISK_OFFICER promoting). The Product Owner should decide whether promotion routes through maker-checker with a 2nd-line checker (C01 §8) and whether the two lists must be reconciled.
9. **No write path for the new fields.** Consent, acknowledgement and classification are plain profile fields set by the composition root; there is no onboarding endpoint, no maker-checker, no audit event and no customer-facing acknowledgement flow. Until one exists (E01/E14), the control is only as good as whoever edits the profile store.
10. **What I could not verify.** That "SIM-DISCL-v0.1", the fixture assessor and the fixture consents match any real onboarding artefact (none exists); that the XK convention (Kosovo as a registry row with a user-assigned code, D-050) is what the Product Owner intends — the validator treats registry rows as countries first, so XK is a real cell, not a simulated one; that the Integration Architect accepts the nested `LegalRecordRef` in `jurisdiction.flag.changed.v1` (additive, but consumers that read `legal_record_ref` as a string will break — grep found none in the repository).
11. **Controls weaker than the PRD states.** FR-15 says "ineligible combo rejected with reason code" — met. FR-01 says privileged actions stay pending until a second approver from a different line acts — mode promotion still needs no second person (TC-ID-003 promotes with one RISK_OFFICER and a gate record); this predates the change and is the R-05 question above.
12. **Out-of-scope edits made on the delegator's instruction.** `apps/web/web_bff/platform.py` and `apps/web/web_bff/reason_codes.py` are outside the build-e06 write scope; they were edited because the instruction required a valid fixture and exported reason codes. The owning roles (E10 build owner; Frontend / Support and Training Leads) and the Compliance Agent (reason-code wording) should acknowledge or amend them.
