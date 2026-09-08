# COUNCIL_2026-09-08_gate_A_compliance_legal — Compliance & Legal Committee challenge of the Gate A decisions

| Council | Date | Member | Line | Status |
|---|---|---|---|---|
| Compliance & Legal Committee (advisory; convened by the Product Owner, D-039) | 2026-09-08 | Compliance Agent and Legal Agent view (goals/07, goals/08), written by the compliance-agent delegate (AI) | 2nd | challenge, decision pending |

> This packet is a challenge, not an approval and not a recommendation to enable anything. It records no decision. Nothing in it asserts a regulatory position, a licence requirement, or that any jurisdiction permits or forbids any activity; every such point is a question for external counsel or a regulator and stays [Open] until a signed legal record exists (MISSING_ACTIONS H-04, H-12). Profit is an objective, never a promise; no figure here is a return [Source: 00]. Author != reviewer != approver: this delegate authored the packet; the Product Owner decides; the Independent Validation Agent checks the evidence [Source: 13; D-039].

## 0. Scope, inputs and what was verified

| Item | Detail |
|---|---|
| Questions challenged | O-11 first jurisdiction cell hypothesis; O-01 persona x mode policy (autonomy default OFF); briefly O-02 billing scope and O-16 Gate A targets [Source: RAID_LOG O-01, O-02, O-11, O-16] |
| Read | GOAL.md; docs/PRODUCT_CHARTER.md; docs/SCOPE.md; docs/PERSONAS.md; docs/JURISDICTION_MATRIX.md; docs/COMPLIANCE_MATRIX.md; docs/MARKET_LAUNCH_CHECKLIST.md; docs/PRIVACY_IMPACT.md; docs/REASON_CODES.md; docs/RAID_LOG.md (O-01, O-02, O-09, O-10, O-11, O-12, O-16, R-33, R-04); docs/MISSING_ACTIONS.md (H-03, H-04, H-12, H-16, H-17); docs/DECISION_LOG.md (D-012, D-025, D-035, D-039); goals/decisions/O-01, O-02, O-11, O-16; goals/external/legal_regulatory_engagement.md; goals/gate_A_discovery.md; docs/GATE_REPORTS/GATE_A_2026-09-07.md; docs/SESSIONS/C06_compliance_market_access.md and P5_market_enablement.md |
| Code read (challenge only; this role writes no production code) | services/compliance/compliance_engine/{jurisdiction.py, eligibility.py, surveillance.py, retention.py}; libs/core/rtcore/schemas/compliance.py; libs/core/rtcore/lines.py (Role); apps/web/web_bff/platform.py (`JURISDICTION = "ZZ"`, `build_sim_platform(enable_cell=True)`); test/quartets/test_tc_cp_eligibility.py (TC-CP-001..006) |
| Environment of all evidence | dev/sim only. The only cell is the fixture `ZZ / RETAIL / sim-broker / SIMX / EQUITY / <mode>` with a fixture legal record (D-012). No real cell exists; JURISDICTION_MATRIX and COMPLIANCE_MATRIX have no enabled row [Verified: file reads] |
| Gate A status | IVA recommended REJECT on 2026-09-07 (V-A1 jurisdiction hypothesis absent; V-A2 charter unapproved) [Source: GATE_A_2026-09-07] |

### 0.1 What the blueprint already fixes (so counsel is not asked to re-decide it)

- [Source: 00] Never assume regulatory permission, data licensing, broker functionality or market access. "Worldwide" never means legal availability [Source: 07].
- [Source: 07] Enablement unit is country x customer type x broker x venue x asset class x feature; dual key = signed legal record + technical flag activated by a different person; default OFF.
- [Source: 01] Custody, deposits/withdrawals, market making, copy trading, personalised advice, unlicensed solicitation, unsupported jurisdictions and manipulation-capable strategies are out of scope without separate approval.
- [Source: 01; Committee] Modes Observe, Backtest, Paper need no gate; Supervised needs Gate D; Bounded autonomous needs Gate E and per-cell enablement; autonomy default OFF [Source: PRODUCT_CHARTER; PERSONAS].
- [Source: 12] Passing Gate A authorises only the next environment; it enables no market, strategy or autonomy.

### 0.2 Facts verified in code that shape the challenge [Verified 2026-09-08]

| # | Observation | Consequence for this challenge |
|---|---|---|
| F-1 | `JurisdictionRegistry.record_legal` accepts a human `Role.COMPLIANCE_AGENT` as the "legal" signer; `activate_flag` accepts `COMPLIANCE_AGENT`, `LEGAL_AGENT` or `COMPLIANCE_ANALYST`. Two Compliance people therefore satisfy the code's dual key with no Legal Agent involved. | The code is weaker than the mandate "may not enable a jurisdiction without Legal co-signature" (goals/07) and "co-sign jurisdiction enablement" (goals/08). See §4.1 proposal P-1. |
| F-2 | `legal_record_ref` is a free string; nothing verifies a document, hash, signer identity or counsel opinion (P5 §8 local O-35, global ID [Open]). The sim fixture is `"SIM-LEGAL-FIXTURE-001 [Committee: simulated cell, not a legal opinion]"`. | The legal half of the dual key is not evidenced in code. See P-2. |
| F-3 | `CustomerProfile` carries `customer_type`, `jurisdiction`, `product_permissions`, `appropriateness_assessed`, `complex_products_allowed`, `short_selling_allowed`. It has no disclosure-acknowledgement version, no per-mode consent, no classification evidence reference, no residency/tax fields. Persona (PERSONAS.md) is not modelled; only `CustomerType` is. | O-01 cannot be enforced in code today beyond `feature` (mode) being part of the cell key. See P-3, P-4. |
| F-4 | `feature` (= account mode) is one of the six cell dimensions; a different mode is a different cell (`CP-JURIS-NOCELL` for `BOUNDED_AUTONOMOUS` in TC-CP-004). | O-01's "default OFF" is already structural: autonomy needs its own dual-keyed cell. This is the strongest control in the build and must be preserved by every O-01 option. |
| F-5 | `RetentionService` fails closed: no `(record_class, jurisdiction)` schedule -> `SUPPRESSED_NO_SCHEDULE` (D-025); each schedule carries a `source_ref` to a COMPLIANCE_MATRIX row or legal record. | Until counsel supplies retention periods per record class for the chosen cell, every deletion request in that jurisdiction is suppressed. This is a privacy consequence of O-11 (O-09, O-10). |
| F-6 | `disable_flag` now requires a human Compliance/Legal role (R-33 remediated); abuse test TC-CP-007 is proposed, not implemented. | Rollback path exists; evidence of it is incomplete. |
| F-7 | `surveil()` parameters are fixtures (O-21) and the library is not wired post-trade (C6-local O-35). `StrategyDeclaration` is self-reported (C6-local R-12). | Checklist item 15 "Surveillance" cannot be evidenced for any cell yet. |
| F-8 | The Compliance & Legal Committee roster in goals/00_product_owner.md §COUNCILS includes `product-director` (1st line). | Segregation question for the Product Owner: a 1st-line member may sit in the council but must not be either dual-key hand [Committee]. |

## 1. Questions that must be answered by external counsel or a regulator before any cell can be enabled

Format: ID | question | exact type of source to consult | why it matters (which control, artefact or gate it feeds). All are [Open] and require counsel; none is answered here. "Target jurisdiction" means whichever country the Product Owner records as the O-11 hypothesis.

### 1.1 O-11 — first jurisdiction cell (country x customer type x broker x venue x asset class x feature)

| ID | Question for counsel / regulator | Source type to consult | Why it matters |
|---|---|---|---|
| Q-J01 | Which activities does the platform perform in the target jurisdiction in counsel's characterisation: receiving and transmitting orders, executing orders on behalf of clients, discretionary portfolio management, investment advice, operating an automated/algorithmic trading service, providing software only? Does the answer differ per mode (Paper, Supervised, Bounded autonomous)? | Written opinion from admitted counsel citing the primary statute/regulation and the regulator's published perimeter guidance | Fixes the licence category (Q-J02) and therefore the "Authorisation required" column of COMPLIANCE_MATRIX; determines whether the operating entity, the broker, or both hold the permission the customer relies on |
| Q-J02 | For each activity in Q-J01, what authorisation, registration, exemption or reliance on the broker's licence applies, and who is the legal person that must hold it? | Regulator's public register of authorised firms (to check any partner's permissions) and the licence-category schedule in the statute | Column "Authorisation required"; MISSING_ACTIONS H-04 evidence; determines whether the hypothesis is executable at all |
| Q-J03 | Does the target jurisdiction have specific rules for algorithmic trading, direct electronic access or automated order generation (e.g. testing, kill functionality, record-keeping, notification to the regulator, annual self-assessment)? Which apply to the operator, which to the broker? | Regulator's algorithmic-trading rulebook / technical standards and the applicable market rules of the venue | Column "Algorithmic-trading controls"; feeds O-16 (time-to-halt target may be constrained by rule); checklist items 14, 15 |
| Q-J04 | What customer classification regime exists (retail / professional / eligible counterparty / institutional or local equivalents), what evidence is required to classify, and can a customer opt up or down? Does the code's `CustomerType` enum map one-to-one to it? | Statute and regulator conduct rules on client categorisation | The cell key uses `customer_type`; a mismatch between legal taxonomy and the enum invalidates every row |
| Q-J05 | Which suitability or appropriateness assessment, if any, applies per customer type and per asset class (equities, ETFs, derivatives, crypto-assets), and must it be repeated for a change of mode? | Conduct-of-business rules; regulator guidance on complex products | `CP-APPR` currently triggers only for `COMPLEX_ASSET_CLASSES`; counsel's answer may change that set and add a per-mode assessment |
| Q-J06 | Which customer disclosures are mandatory before onboarding, before first order, and periodically (risk warnings, costs and charges, order-execution policy, conflicts, complaints, compensation scheme)? Are there prescribed wordings or formats? | Conduct-of-business rules; regulator disclosure templates | Checklist item 18; H-16; `CustomerProfile` has no acknowledgement field (P-3); R-04 |
| Q-J07 | Does a best-execution or order-handling duty attach to the operator when the broker executes? What records prove it? | Conduct rules; broker terms of business | Column "Best-execution duty"; reconciliation and audit evidence design |
| Q-J08 | Which transaction, position or trade reports must be made, by whom, in what format and within what deadline? Does the broker report on the operator's behalf under its terms? | Regulator reporting rules; broker terms of business; venue rulebook | Column "Reporting"; FR-15 "regulatory reporting adapters"; checklist item 14 |
| Q-J09 | What market-abuse and surveillance obligations apply to the operator (monitoring, suspicious-order reporting, thresholds, retention of alerts)? | Market-abuse statute; regulator guidance on suspicious transaction and order reports | Column "Surveillance"; O-21 parameter approval; C6-local O-35 wiring |
| Q-J10 | What record-retention periods apply per record class (orders, communications, client files, audit trail, AI decision records) and where must records be held? | Regulator record-keeping rules; data-protection statute | `RetentionSchedule(record_class, jurisdiction, retain_for, source_ref)` cannot be filled without this; until then deletions are `SUPPRESSED_NO_SCHEDULE` (F-5); O-09 |
| Q-J11 | Which data-protection regime applies; is a DPIA required for automated trading decisions about customers; what is the lawful basis for each data category in PRIVACY_IMPACT; are cross-border transfers to model or cloud providers restricted? | Data-protection statute and supervisory-authority guidance | O-10 column "DPIA done"; PRIVACY_IMPACT "Legal basis (per jurisdiction)"; O-05 model hosting |
| Q-J12 | Are there residency, nationality or tax-status restrictions on who may be onboarded, and does the operator need a tax-reporting or withholding role? | Tax authority guidance; broker terms on tax handling | Column "Tax"; checklist item 11; `CustomerProfile` has no such field |
| Q-J13 | Does the broker's licence and its terms of business permit third-party automated order submission via API for the target customer type, asset class and venue, and does it require the operator to be authorised, registered as an introducing party, or named in its own regulatory filings? | Broker terms of business, API terms, developer agreement; regulator register entry for the broker | Column "Broker"; H-07; without this the cell's broker dimension is unknowable |
| Q-J14 | Does the venue rulebook (or the broker's venue access terms) impose obligations on automated participants (order-to-trade ratios, tagging of algorithmic orders, testing)? | Venue rulebook / member notices | Column "Venue"; checklist item 7; surveillance thresholds |
| Q-J15 | Do the market-data licences permit use of the data to drive automated orders, derived data generation and display to customers in the target jurisdiction (professional vs non-professional)? | Data-provider licence agreement and exchange data policy | O-12; column "Data licensing"; checklist item 13 |
| Q-J16 | Which marketing, financial-promotion and solicitation rules apply, including to paper-trading and "simulated performance" content, and who must approve promotions? | Financial-promotion rules; regulator guidance on past/simulated performance | R-04; H-16; column "Marketing restrictions"; GTM content gate |
| Q-J17 | Is any regulator notification, sandbox application or pre-approval required for AI-generated trade intents or for an AI-driven service to retail customers? | Regulator innovation/sandbox pages; AI-specific guidance or statute if any | Determines whether "authorisation path" in O-11 includes a regulator dialogue and its timeline |
| Q-J18 | Which entity is the contracting party with the customer, and what governing law, dispute resolution and complaints/ombudsman scheme must the terms name? | Corporate structure advice; consumer-contract law; ombudsman scheme rules | Legal terms (Legal Agent owns); checklist item 18 |

### 1.2 O-01 — persona x mode policy per jurisdiction (autonomy default OFF)

| ID | Question for counsel / regulator | Source type to consult | Why it matters |
|---|---|---|---|
| Q-P01 | Does customer per-order approval in Supervised mode change the legal characterisation of the service compared with Bounded autonomous mode (execution-only vs discretionary management)? | Counsel opinion against the statute's activity definitions | Decides whether Supervised and Bounded autonomous are one licence question or two; ADR-034 already makes them separate cells |
| Q-P02 | May retail-classified customers be offered automated execution at all in the target jurisdiction, and if so with which additional protections (cooling-off, leverage limits, negative balance protection, appropriateness)? | Conduct rules; product-intervention measures published by the regulator | Determines whether the RETAIL x SUPERVISED and RETAIL x BOUNDED_AUTONOMOUS cells can ever be hypothesised |
| Q-P03 | Who may perform customer classification and how must it be evidenced; may it be self-declared? | Client-categorisation rules | `CustomerType` is an input to eligibility; a self-declared PROFESSIONAL would bypass retail protections (P-4) |
| Q-P04 | Is explicit, recorded customer consent required per mode change (Paper -> Supervised -> Bounded), and must it be renewable? | Conduct rules; contract law | `CustomerProfile` has no consent field (F-3); P-3 |
| Q-P05 | Do operator personas (risk officer, compliance analyst, portfolio manager, trader) need individual registration, certification or fitness assessment in the target jurisdiction when they approve or override orders? | Regulator's individual-accountability / certification regime | RACI and H-01 appointments; whether "human approval" in Supervised mode must be by a certified individual |
| Q-P06 | Are there rules on the human-oversight ratio (approvals per person, hours) or on the identity of the approver relative to the customer (may a tenant administrator approve for a customer)? | Regulator algorithmic-trading and outsourcing guidance | Supervised mode design; maker-checker |
| Q-P07 | Do "Backtest" and "Paper" results shown to a customer count as performance information subject to promotion rules? | Financial-promotion rules on simulated performance | R-04; strategy card disclaimer; UI copy |

### 1.3 O-02 — billing scope (brief)

| ID | Question for counsel / regulator | Source type to consult | Why it matters |
|---|---|---|---|
| Q-B01 | Does the fee model (subscription, usage, per-order, performance-linked) affect the regulatory characterisation or trigger inducement, fee-disclosure or client-money rules? | Conduct rules on fees and inducements; counsel opinion | A performance-linked fee may imply a return relationship (R-04) and may alter Q-J01; see §5 |
| Q-B02 | What indirect tax applies to each billed item per customer location, and where must the operator register? | Tax authority guidance; tax adviser | Invoicing and tax handling in the O-02 question |
| Q-B03 | Do broker terms restrict or require disclosure of charges the operator adds on top of broker commissions? | Broker terms of business | Column "Disclosures"; costs-and-charges wording |
| Q-B04 | Must billing records be retained under the same schedule as trading records? | Record-keeping rules | `RetentionSchedule` record classes |

### 1.4 O-16 — Gate A measurable targets (brief)

| ID | Question for counsel / regulator | Source type to consult | Why it matters |
|---|---|---|---|
| Q-T01 | Do any regulatory technical standards prescribe minimum expectations for kill functionality latency, reconciliation timeliness or record completeness that the Gate A targets must at least meet? | Algorithmic-trading technical standards; venue rules | Time-to-halt and reconciliation-completeness targets are internal until counsel confirms no external floor applies |
| Q-T02 | May outcome targets be published to customers, and if so is any target that could be read as a performance expectation restricted? | Financial-promotion rules | Targets must stay operational (halt latency, reconciliation, determinism, findings), never PnL |

## 2. Reversibility of the choices

| Choice | Reversible? | Basis |
|---|---|---|
| Recording an O-11 hypothesis row in JURISDICTION_MATRIX labelled "hypothesis", dual-key state "— / OFF", modes none | Reversible; enables nothing; needs no counsel | [Source: 07 default OFF; Verified: matrix has no live row] |
| Engaging counsel and paying for an opinion on that hypothesis (H-04) | Reversible (sunk cost only) | [Committee] |
| Choosing customer type for the first cell (RETAIL vs PROFESSIONAL/INSTITUTIONAL) | Reversible until the first customer is onboarded under terms; after that, re-papering and possibly re-classification are needed | [Committee]; Q-J04, Q-P03 |
| Applying for authorisation, registration or a regulator sandbox in the target jurisdiction | Effectively not reversible: public record, ongoing obligations, formal withdrawal | [Committee]; Q-J02, Q-J17 |
| Signing broker and data-licence agreements (H-07, H-08) | Contractually reversible with notice; termination cost; data already used under licence terms is not "un-used" | [Committee]; Q-J13, Q-J15 |
| Activating the technical flag (H-17) | Reversible in code by a single human Compliance/Legal disable (`disable_flag`, R-33) — but orders submitted while live are not reversible, and disclosures made are made | [Verified: jurisdiction.py; TC-CP-004] |
| Any solicitation or marketing in the target jurisdiction before the legal record | Not reversible; characterisation questions follow the act | [Source: 01 unlicensed solicitation out of scope]; Q-J16 |
| O-01: autonomy default OFF for every persona | Reversible at any time; is the blueprint default | [Source: 01; F-4] |
| O-01: autonomy default ON for any persona/customer type | Reversal requires customer communication and possibly consent withdrawal handling; trades executed meanwhile are not reversible | [Committee] |
| O-01: modelling persona x mode in code (P-3, P-4) | Reversible (schema change) before any real customer record exists | [Committee] |
| O-02: subscription or usage billing | Reversible before first invoice; refunds and tax filings after | [Committee] |
| O-02: performance-linked or profit-share billing | Hard to reverse once contracted; may change characterisation (Q-B01) | [Committee] |
| O-16: numeric targets | Reversible; internal | [Committee] |
| Replacing the `ZZ` fixture with a real country code in `apps/web/web_bff/platform.py` before a legal record exists | Technically reversible, but it would make sim output carry a real jurisdiction label with a fixture legal record — see §5 | [Verified: D-012] |

## 3. Minimum evidence the Committee would need to recommend the O-11 hypothesis (recommend the hypothesis, not enablement)

A hypothesis is a statement "we intend to seek authorisation and evidence for cell X first". The Committee could recommend recording it when all of the following exist. None of them is a legal opinion; the opinion (H-04) is Gate D evidence.

| # | Evidence | Where it lives | Owner (human) |
|---|---|---|---|
| E-1 | One fully specified cell: country (ISO 3166-1 alpha-2, not ZZ), customer type from `CustomerType`, named broker, named venue, one asset class, feature = PAPER first; stated explicitly as hypothesis, dual-key "— / OFF", modes "none" | docs/JURISDICTION_MATRIX.md row; docs/COMPLIANCE_MATRIX.md row with all regulatory columns "[Open: counsel Q-Jnn]" | Product Director + Compliance Agent (H-03) |
| E-2 | Product Owner's written rationale with >= 2 alternative cells compared (pros, cons, cost, risk, reversibility) and dissent recorded | docs/DECISION_LOG.md (drafted, approver = Product Owner) | Product Owner |
| E-3 | Counsel engagement scope: the Q-J01..Q-J18 list above tailored to the cell, with the source types named, and a named admitted law firm or in-house counsel of record | goals/external/legal_regulatory_engagement.md step 1 output; MISSING_ACTIONS H-04 owner and due date filled | Legal Agent (human of record) |
| E-4 | Regulator map: name of the regulator(s), link to the public register, the licence-category schedule to be read — as pointers, not conclusions | COMPLIANCE_MATRIX "Regulator" column with "[Open]" status | Legal Agent |
| E-5 | Broker candidate identified with its public register entry reference and the specific terms documents to be reviewed (Q-J13) — no capability assumed | goals/external/broker_onboarding.md; docs/BROKER_CERTIFICATIONS/ (none for a real broker yet) | Broker-Connector Lead + Legal Agent |
| E-6 | Data-licence documents to be reviewed for Q-J15 identified | goals/external/data_licensing.md; O-12 | Data Architect + Legal Agent |
| E-7 | Privacy: DPIA scoping note for the cell (Q-J11) and the PRIVACY_IMPACT "Legal basis" column marked "[Open: counsel]" rather than blank | docs/PRIVACY_IMPACT.md; O-10 | Privacy Lead |
| E-8 | Statement that the hypothesis enables nothing: `ZZ` stays the only cell in code; no `RT_ENV` other than dev/sim exists; H-12 and H-17 remain Open | docs/AUDIT_EVIDENCE_INDEX.md row 1b updated to "hypothesis recorded; no legal record" | Program Orchestrator |
| E-9 | O-01 answered for that cell at minimum as "PAPER only for all personas; SUPERVISED and BOUNDED_AUTONOMOUS not hypothesised until Q-P01..Q-P04 are answered" | docs/PERSONAS.md "[Open: O-01]" replaced by the per-cell policy; DECISION_LOG draft | Compliance & Legal Committee -> Product Owner |
| E-10 | IVA check that E-1..E-9 are files, not assertions | docs/GATE_REPORTS/ re-validation | Independent Validation Agent |

## 4. Dual-key and disclosure consequences in code and docs

This role may not write production code. Items marked P-n are proposals for the owning role (Backend Lead for services/compliance, with `@rt365/compliance-agent` and IVA as CODEOWNERS) [Verified: .github/CODEOWNERS].

### 4.1 services/compliance (proposals for Backend Lead; tests first, control quartet)

| ID | Proposal | Why | Test to add |
|---|---|---|---|
| P-1 | `record_legal` should require `Role.LEGAL_AGENT` (human), or `activate_flag` should require that the signer and activator span both Legal and Compliance roles, so that the pair is never Compliance + Compliance (F-1). | Mandate: no enablement without Legal co-signature (goals/07, goals/08). Today two Compliance humans satisfy the code. | TC-CP-009 abuse: Compliance Agent signs legal record, Compliance Analyst activates -> `ControlDenied`; `dual_key_satisfied()` should also encode the role pair if the schema gains `legal_signed_role` / `flag_activated_role` |
| P-2 | `legal_record_ref` should reference a stored, hashed legal record (counsel opinion + Compliance/Legal signatures) whose hash is anchored in the audit chain; `record_legal` verifies the hash exists (P5-local O-35). | The legal half of the dual key is currently a string; a fabricated reference passes. | TC-CP-010 abuse: unknown ref rejected; recovery: re-anchoring after store restore |
| P-3 | `CustomerProfile` gains `disclosures_acknowledged_version: str | None` and `mode_consent: tuple[str, ...]` (modes consented to, with version); eligibility emits `CP-DISCL` when the cell's required disclosure version is not acknowledged and `CP-MODE-CONSENT` when `feature` is not in `mode_consent`. Cell gains `required_disclosure_version`. | Q-J06, Q-P04: disclosure and consent must be enforced at decision time, not only in UI. | Extend TC-CP-002 (negative) and add positive case in TC-CP-001; REASON_CODES entries with plain language, no advice |
| P-4 | `CustomerProfile` gains `classification_evidence_ref: str | None` and `classified_by: str | None`; eligibility emits `CP-CLASS` for `PROFESSIONAL`/`ELIGIBLE_COUNTERPARTY`/`INSTITUTIONAL` without evidence. | Q-J04, Q-P03: self-declared opt-up would bypass retail protections. | TC-CP-011 abuse |
| P-5 | `COMPLEX_ASSET_CLASSES` and the `CP-APPR` trigger should be policy data versioned with `RestrictedLists.policy_version` (per jurisdiction), not a code constant. | Q-J05: the set is a legal question per cell. | Determinism test unchanged; add negative case per policy version |
| P-6 | Environment guard: `build_sim_platform(enable_cell=True)` must refuse when `RT_ENV` is not dev/sim (C6-local R-13 / T-27); the fixture legal actors must never exist outside sim. | Prevents the fixture dual key faking enablement. | TC-CP-012 abuse |
| P-7 | Implement proposed TC-CP-007 (agent or non-Compliance/Legal actor cannot `disable_flag`) to close the evidence gap on R-33. | Rollback path must be evidenced. | TC-CP-007 |
| P-8 | Surveillance parameters (`wash_window`, `spoof_cancel_within`, `close_window`, `max_cancel_ratio`) loaded from a versioned per-cell policy file approved by the Committee (O-21), and `surveil()` wired to post-trade fills with alerts routed to P6 (C6-local O-35). | Checklist item 15 cannot be evidenced otherwise; Q-J09. | Positive/negative/abuse/recovery on the wiring |
| P-9 | `RetentionSchedule` rows per record class for the chosen cell, each `source_ref` pointing to the counsel opinion paragraph; add the proposed TC-CP-008 (no-schedule outcome; tenant-scope hold). | F-5: deletions are suppressed until schedules exist; O-09. | TC-CP-008 |

### 4.2 docs/JURISDICTION_MATRIX.md (Compliance Agent owns; Legal Agent reviews)

- Add the hypothesis row only when E-1..E-3 exist; the row must read: Legal basis established = "No [Open: Q-J01..Q-J02]"; DPIA done = "No [Open: O-10, Q-J11]"; Legal-hold rules = "No [Open: O-09, Q-J10]"; Support hours = "[Open: O-15]"; Incident contacts = "[Open]"; Customer disclosures approved = "No [Open: H-16, Q-J06]"; Dual-key state = "— / OFF"; Enabled modes = "none"; Post-launch review dates = "—".
- Add a column "Hypothesis status" (Hypothesised / Counsel engaged / Opinion received / Signed legal record) so that the row can never be read as "established" [Committee].
- Keep the `ZZ` fixture out of this document: it is not a jurisdiction (D-012).

### 4.3 docs/COMPLIANCE_MATRIX.md (Compliance Agent owns; Legal Agent reviews)

- One row per cell; the first row's 12 regulatory columns (Regulator ... Marketing restrictions) each carry "[Open: Q-Jnn]" with the question ID, never blank and never a conclusion; Legal record ref = "—"; Technical flag = OFF; Status = "Hypothesis — not enabled".
- Add a column "Persona x mode policy [O-01]" whose only permitted values are "PAPER" until counsel answers Q-P01..Q-P04; SUPERVISED and BOUNDED_AUTONOMOUS rows are separate cells (ADR-034) and must not be created by copying the PAPER row.
- Add a column "Required disclosure version" to pair with P-3.
- Retention column must cite the counsel paragraph per record class (P-9), because `RetentionSchedule.source_ref` points here.

### 4.4 Other docs (owning roles)

| Doc | Owner | Consequence |
|---|---|---|
| docs/REASON_CODES.md (generated from `apps/web/web_bff/reason_codes.py`) | Frontend / Support & Training Leads; Compliance Agent reviews text | New codes CP-DISCL, CP-MODE-CONSENT, CP-CLASS need plain-language entries with no advice and no return language (R-04); add a negative test that rejects such wording (C6 §6 gap) |
| docs/PRIVACY_IMPACT.md | Privacy Lead | "Legal basis (per jurisdiction)" and "DPIA status" must reference Q-J11 and the cell; AI-context row must state whether AI decision records are customer data subject to access rights (Q-J10, Q-J11) |
| docs/MARKET_LAUNCH_CHECKLIST.md | Compliance Agent / Trading Domain Lead / GTM Lead | Items 1, 9, 13, 14, 15, 18 map to Q-J01/02, Q-J05, Q-J15, Q-J08, Q-J09, Q-J06 respectively; the Status column stays blank until a file exists |
| docs/PERSONAS.md | Product Director | Replace "[Open: O-01]" with the per-cell policy from E-9; retail row must say "Supervised/autonomy: not hypothesised [Open: Q-P02]" |
| docs/MISSING_ACTIONS.md | Program Orchestrator | H-04 must name the counsel and cell; propose new rows: H-25 "Adopt Q-J/Q-P/Q-B/Q-T question list as counsel engagement scope" (Legal Agent, Gate A); H-26 "Name the two humans of record for the dual key, one Legal and one Compliance, neither the Product Owner nor a 1st-line member" (Executive Steering, Gate D) |
| docs/RAID_LOG.md | Program Orchestrator | Proposed entries in §7 |

### 4.5 Dual-key operating consequences [Committee]

- Neither the Compliance Agent nor the Legal Agent as AI agents can be a dual-key hand: `record_legal` and `activate_flag` require `actor.is_human` [Verified]. The two hands are the humans appointed under H-01 to those roles.
- The Product Owner decides the hypothesis and may override an IVA veto in writing (D-039), but the Product Owner is 1st line and may not be either dual-key hand, may not approve compliance enablement (PRODUCT_OWNER.md §Segregation), and cannot substitute for the Legal co-signature. A D-039 override cannot activate a flag; only H-12 + H-17 by two distinct humans can.
- Disabling is single-person and available to any human Compliance/Legal role; a Product Owner instruction to keep a cell live over a Compliance/Legal disable would be a control bypass and must not be honoured [Source: 00 human override supersedes].

## 5. Options the Committee would recommend the Product Owner reject (and why)

| # | Option | Why reject | Tag |
|---|---|---|---|
| X-1 | Treat the Gate A hypothesis as permission to open any cell (even PAPER) to real customers or to solicit customers in the target jurisdiction before the signed legal record | Gate A authorises only the next environment and enables no market [Source: 12]; solicitation is out of scope without approval [Source: 01]; not reversible (§2) | [Source: 01, 12] |
| X-2 | A "worldwide", multi-country or multi-broker first hypothesis | "Worldwide" never means legal availability [Source: 07]; the counsel question set multiplies per cell; the matrix design is one cell at a time | [Source: 07] |
| X-3 | RETAIL x BOUNDED_AUTONOMOUS (or RETAIL x SUPERVISED) as the first cell | Q-P02 is unanswered; the autonomy cell is the one with the most counsel questions and the least reversibility; the blueprint's default OFF and the ladder (paper before supervised before capped autonomous) point to PAPER first for whatever customer type is chosen | [Source: 00, 01; Committee] |
| X-4 | Autonomy or Supervised mode default ON for any persona, including "professional trader" or "portfolio manager" | Default OFF is fixed by the blueprint [Source: 01]; F-4 already makes each mode a separate dual-keyed cell; defaulting ON would require a code path that weakens `CP-JURIS-NOCELL` | [Source: 01] |
| X-5 | Answering O-01 with a self-declared customer type (customer ticks "professional") | Q-P03 unanswered; would bypass retail protections through an eligibility input (P-4) | [Committee] |
| X-6 | Closing O-11 by replacing `JURISDICTION = "ZZ"` with the hypothesised country code in `apps/web/web_bff/platform.py` while the fixture legal record remains | Sim output would carry a real jurisdiction label backed by a fixture legal record; D-012 exists precisely to prevent this; it would look like enablement evidence | [Verified: D-012; Committee] |
| X-7 | Letting the dual key be satisfied by two Compliance people, or by the Product Owner as one hand, or by an AI agent | Mandate requires Legal co-signature (goals/07, goals/08); PO segregation (PRODUCT_OWNER.md); agents denied in code; F-1 shows the code currently allows the first of these — reject the option and adopt P-1 | [Source: 07, 13; Verified] |
| X-8 | O-02: performance-linked or profit-share billing as the launch model | Implies a return relationship (R-04; profit is an objective, never a promise [Source: 00]); Q-B01 unanswered; hardest billing choice to reverse (§2) | [Source: 00; Committee] |
| X-9 | O-02: billing for "signals" or "recommendations" as a product line before counsel answers Q-J01 | SCOPE.md fixes AI outputs as analytics, never recommendations to a person; a billed "recommendation" product would contradict that positioning | [Source: 01; Committee] |
| X-10 | O-16: any target denominated in PnL, return, win rate or "profit objective achieved" | Never claim or imply returns [Source: 00]; Q-T02; targets must stay operational (halt latency, reconciliation completeness, determinism, findings) | [Source: 00] |
| X-11 | Deferring O-01 entirely past Gate A ("decide per cell later") without at least the PAPER-only interim policy of E-9 | RAID says O-01 is needed by Gate A; IVA condition C-A3; without an interim policy the PERSONAS row stays "[Open]" and the hypothesis row has no mode column | [Source: RAID O-01; GATE_A C-A3] |
| X-12 | Waiving IVA's V-A1 by override before the hypothesis row and E-1..E-9 exist | D-039 allows override in writing with risk accepted, but the gate's minimum veto ground is a missing file, not a judgement call; overriding it would record a risk acceptance for an absence that costs nothing to fix | [Source: 12; D-039; Committee] |

## 6. What the Committee does not object to at Gate A [Committee]

- Recording one clearly labelled hypothesis row (E-1) with all regulatory columns "[Open]".
- Choosing PAPER as the first feature for that cell and answering O-01 as "PAPER only; other modes not hypothesised" as the interim policy.
- Commissioning counsel with the question list in §1 (H-04 scoped to the cell).
- Setting O-16 targets that are purely operational (time-to-halt, reconciliation completeness, deterministic decision rate, critical findings) with the understanding that Q-T01 may raise a floor later.
- Deferring O-02 to a subscription-or-usage decision at Gate B, provided X-8 and X-9 are excluded now.

## 7. Proposed RAID entries, assumptions, confidence, provenance

Proposed for the Program Orchestrator to record (this packet records nothing):

| Proposed ID | Type | Item | Owner | Needed by |
|---|---|---|---|---|
| R-new-1 | Risk | Dual key satisfiable in code by two Compliance humans without a Legal Agent (F-1, P-1) | Backend Lead (fix), Compliance Agent (review), Legal Agent | Gate D |
| O-new-1 | Gap | Disclosure acknowledgement, mode consent and classification evidence absent from `CustomerProfile` and eligibility (F-3, P-3, P-4) | Backend Lead, Compliance Agent | Gate D |
| O-new-2 | Gap | Counsel question list Q-J01..Q-J18, Q-P01..Q-P07, Q-B01..Q-B04, Q-T01..Q-T02 not yet adopted as the H-04 engagement scope | Legal Agent | Gate A (scope) / Gate D (answers) |
| O-new-3 | Gap | Global RAID ID for P5-local O-35 (legal-record integrity) and C6-local O-35 (surveillance wiring) not found in RAID_LOG renumbering map; confirm or allocate | Program Orchestrator | Gate B |
| O-new-4 | Gap | Compliance & Legal Committee roster includes a 1st-line member (product-director); rule that no 1st-line member or the Product Owner is a dual-key hand is not written anywhere (F-8) | Product Owner (roster), Executive Steering | Gate D |

Assumptions: the Product Owner will choose a single real ISO 3166-1 country for the hypothesis; the customer type will be one `CustomerType` value; the feature will be PAPER; no counsel has yet been engaged (H-04 Open) [Verified: MISSING_ACTIONS].

Confidence: high that the code facts F-1..F-8 are as stated (files read at working tree on 2026-09-08); high that the question list covers the COMPLIANCE_MATRIX columns and the 18-item checklist [Source: 07, 17]; none on the answer to any question — that is counsel's work. No regulatory position is taken anywhere in this packet.

Provenance: [Source: 00, 01, 07, 12, 13, 17] for posture, scope, matrix dimensions, gate rule, segregation and checklist; [Committee] for the code review, proposals and rejection list; [Open] for every legal, tax, privacy, broker, venue and data question. Reviewer: Legal Agent (human of record, pending); approver of the decisions challenged here: Product Owner (D-039); evidence check: Independent Validation Agent (pending).
