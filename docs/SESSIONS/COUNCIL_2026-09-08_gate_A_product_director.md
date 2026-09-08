# Council packet — Gate A option analyses (Product Director)

| Council | Date | Member | Line | Status |
|---|---|---|---|---|
| Product Council (advisory; convened by the Product Owner under D-039) | 2026-09-08 | Product Director (`goals/01_product_director.md`; agent `product-director`) | 1st | recommendation, decision pending |

**Environment:** dev/sim only. **Nothing in this packet is a decision.** It is an option analysis for the human Product Owner (docs/PRODUCT_OWNER.md v2.0, D-039). It enables no market, mode, strategy, autonomy or price; it asserts no regulatory status, licence requirement, broker capability, data entitlement, price or threshold. Where such a fact is needed it is written as a question with the source to consult and tagged [Open]. Profit is an objective, never a promise [Source: 00].

**Provenance note.** The blueprint (sections 00–17) is not in this repository; `[Source: NN]` tags below are taken as transmitted by the repository artefacts that cite them (docs/PRD.md, docs/COMMITTEE_DEEP_DIVE.md, docs/SESSIONS/C01, C06, P5, docs/GATE_REPORTS/GATE_A_2026-09-07.md). `[Verified]` marks a fact I re-read in code or docs at the working tree of 2026-09-08 (HEAD `b82f932` plus uncommitted edits to GOAL.md, goals/00 and goals/gate_*.md). `[Committee]` is this council's reasoning. `[Open]` is undecided or unknown.

---

## 0 Roles for this packet [Source: 13; Committee]

| Function | Role | Line | Note |
|---|---|---|---|
| Author (options and recommendation) | Product Director (AI agent) | 1st | Owns PRODUCT_CHARTER, PRD, PERSONAS, JOURNEYS, SCOPE, ROADMAP; may not approve risk limits, compliance enablement, security acceptance or any model/strategy |
| Challenger (different line) — O-11, O-01 | Compliance Agent (2nd line; owner of JURISDICTION_MATRIX / COMPLIANCE_MATRIX) with Legal Agent | 2nd | Required before the decision (PRODUCT_OWNER.md protocol step 2) |
| Challenger (different line) — O-02 | Chief Risk Agent or Compliance Agent (2nd line); Finance & Vendor Lead co-prepares (1st line, not a challenger) | 2nd | Finance is same line as the author, so cannot be the challenger |
| Challenger (different line) — O-16 | Chief Risk Agent (2nd line); SRE Lead consulted on measurement points | 2nd | |
| Evidence check | Independent Validation Agent | 3rd | Verifies the [Verified] claims below; may veto Gate A on evidence grounds (GATE_A_2026-09-07 V-A1, V-A2) |
| Decider | Human Product Owner | — | Records the decision in docs/DECISION_LOG.md with alternatives and dissent (D-039) |

Author ≠ challenger ≠ decider. Nothing here is self-certified.

## 1 Facts the repository already fixes (inputs common to all four items)

| # | Fact | Evidence |
|---|---|---|
| F-1 | Gate A exit evidence = approved charter, personas, jurisdiction hypothesis, measurable outcomes; IVA minimum veto ground = missing jurisdiction hypothesis; passing Gate A enables no market, strategy or autonomy [Source: 12] | goals/gate_A_discovery.md [Verified] |
| F-2 | IVA verdict on Gate A at commit 09a6e71: REJECT; veto grounds V-A1 (no jurisdiction hypothesis), V-A2 (charter unapproved); conditions C-A1 (O-16 targets), C-A3 (O-01), C-A5 (O-02 decided or formally deferred) | docs/GATE_REPORTS/GATE_A_2026-09-07.md §4 [Verified] |
| F-3 | The only jurisdiction cell in the build is the fixture `ZZ / RETAIL / sim-broker / SIMX / EQUITY / <mode>` (ISO 3166 user-assigned code, not a jurisdiction, D-012); JURISDICTION_MATRIX and COMPLIANCE_MATRIX have no enabled row | docs/DECISION_LOG.md D-012; docs/JURISDICTION_MATRIX.md; docs/COMPLIANCE_MATRIX.md [Verified] |
| F-4 | A cell is six-dimensional: country × customer type × broker × venue × asset class × feature, where feature = operating mode; a different mode is a different cell (`CP-JURIS-NOCELL`) [Source: 07; Committee ADR-034] | libs/core/rtcore/schemas/compliance.py `JurisdictionCell.key`; TC-CP-004 [Verified] |
| F-5 | `CustomerType` enum = RETAIL, PROFESSIONAL, ELIGIBLE_COUNTERPARTY, INSTITUTIONAL; eligibility checks `appropriateness_assessed` and `complex_products_allowed` as inputs (values are inputs, not policy) | libs/core/rtcore/schemas/compliance.py:15-19; services/compliance/compliance_engine/eligibility.py:164-167 [Verified] |
| F-6 | Enablement is dual-key: signed legal record by one human + technical flag by a different human; agents denied; disable is single-person; the engine re-checks the cell on every intent | C06-D1, ADR-032; TC-CP-003/004 [Verified] |
| F-7 | Mode ladder Observe → Backtest → Paper → Supervised → Bounded autonomous, one step per gate record; HALTED from anywhere; two-person different-line restore capped at `enabled_feature` ≤ SUPERVISED; agents can never change mode; autonomy ships OFF for every persona [Committee C1-D1, C1-D3, C1-D4, D-021] | services/identity/identity_service/accounts.py (`MODE_CHANGERS`, `enabled_feature`); TC-ID-003/004, TC-KS-004 [Verified] |
| F-8 | Out-of-scope capabilities are enum-absent permissions (no CUSTODY, MONEY_MOVEMENT, MARKET_MAKING, COPY_TRADING, PERSONAL_ADVICE, MODIFY_AUDIT, DISABLE_MONITORING) [Committee C1-D2] | services/identity/identity_service/rbac.py; docs/SCOPE.md; TC-ID-003 [Verified via C01 packet] |
| F-9 | SLIs are defined with `target: null` incl. `reconciliation_completeness_pct` (safety semantic: Supervised on break); no `time_to_halt` SLI exists; targets deferred to measured baselines [Source: 10] [Open: O-03] | observability/slis.yaml; docs/SLO_SLA.md [Verified] |
| F-10 | Kill Switch engagement is persist-first with `activated_at`; no wall-clock time-to-halt is recorded by any test; TC-KS quartet 12 tests pass in dev/sim | services/killswitch/killswitch_service/service.py:32,90; docs/TEST_CASES/TC-KS.md; EVIDENCE_REPORT.md [Verified] |
| F-11 | Determinism: IVA re-derived byte-identical DecisionRecords across 50 in-process runs and 3 interpreters; NFR-DET-01 target 100% [Source: 05] | GATE_A_2026-09-07 §3; docs/NFR.md [Verified] |
| F-12 | Evidence report: 145 records, 17/17 areas with a full quartet, pytest exit 0, base commit 2b44f76, reviewer column pending by construction (D-014) | docs/TEST_CASES/EVIDENCE_REPORT.md [Verified] |
| F-13 | E14 (billing, support, admin) is gate F, not built; rule: billing never gates a Kill Switch or a halt; support is read-only plus runbooks [Source: 14; Committee] | goals/build/E14_billing_support_admin.md; docs/BACKLOG.md P7; RAID O-31 [Verified] |
| F-14 | Decision authority: the human Product Owner decides every human decision; councils are advisory; IVA veto override only in writing with risk accepted (D-039, R-48); deputy for two-person runtime controls still [Open: O-19] | docs/DECISION_LOG.md D-039; docs/PRODUCT_OWNER.md v2.0 [Verified] |
| F-15 | Ledger state at writing: RAID O-01, O-02, O-11, O-16 all "Open" (not "Pack ready"); docs/PO_DECISION_QUEUE.md was created by the delegate during this council (rows O-01, O-02, O-11, O-16: council convened 2026-09-08, recommendation pending, decision pending); a Compliance & Legal challenge packet (COUNCIL_2026-09-08_gate_A_compliance_legal.md) and an IVA packet (COUNCIL_2026-09-08_gate_A_iva.md) were written in parallel and were not relied on here | docs/RAID_LOG.md rows 9, 10, 19, 24; docs/PO_DECISION_QUEUE.md §A [Verified 2026-09-08, working tree] |

Dependency order for the decisions [Committee]: **O-11 first** (the cell fixes country and customer type), then **O-01** (persona × mode inherits the cell) and **O-02** (billing scope depends on whether the first cell has third-party customers); **O-16** is independent and can be decided in the same sitting.

---

## 2 O-11 — First launch jurisdiction cell hypothesis

### 2.1 What is fixed and what is open
- Fixed [Source: 07]: the unit of launch is the six-dimension cell; "worldwide" never means legal availability; no row is enabled by a document. [Source: 17]: 18-item market-readiness checklist per market, each item evidenced. [Source: 12]: Gate A needs a *hypothesis*, not an enabled market. [Source: 00]: regulatory permission, data licensing, broker functionality and market access are never assumed. [Committee]: P5 sequence hypothesis → legal basis → broker certification → instrument master → entitlements → reporting/surveillance → support → disclosures → C&L sign-off → dual key → 30/90-day review; sim code keeps `ZZ` until a real cell is dual-key enabled (D-012).
- Open: country, customer type, broker, venue, asset class, regulator, authorisation path, operating legal entity. None of these exists in any artefact [Verified: F-3].

### 2.2 Questions that only humans or external sources can answer [Open]

| Q | Question | Who answers | Source to consult |
|---|---|---|---|
| Q-11-1 | Which legal entity (or natural person) will operate the platform, and in which country is it established and registered? | Product Owner | The entity's registration/constitutional documents |
| Q-11-2 | Will the first cell serve third-party customers, or only the operating entity's own capital (first-party account)? | Product Owner | Business intent; shareholder/board resolution if an entity |
| Q-11-3 | For the answers to Q-11-1/2: which regulator has jurisdiction over (a) automated order generation on the entity's own account through a regulated broker, (b) providing the platform to third parties (retail vs professional); which authorisation, registration, exemption or notification applies; do algorithmic-trading rules attach to the operator, the broker or both? | External counsel (H-04) | The regulator's public register and rulebook; counsel's written opinion filed as the legal record |
| Q-11-4 | Which brokers serving that country publish an API with a sandbox/paper environment, API-retrievable statements, and terms that permit automated order submission by a third-party system? | Broker-Connector Lead + Finance (H-07) | Each broker's published API documentation and terms of service; docs/VENDOR_ASSESSMENTS/TEMPLATE.md |
| Q-11-5 | What licence does the primary venue require for real-time or delayed data used for automated (non-display) decisions, and for redistribution to tenants? | Legal Agent + Data Architect (H-08, O-12) | The venue's market-data policy; the data vendor's licence agreement |
| Q-11-6 | Is a DPIA required for that country, and what data-residency rules apply to customer and trade records? | Privacy Lead (O-10) | Applicable data-protection law and supervisory-authority guidance |
| Q-11-7 | Which transaction taxes, reporting duties and fee regimes apply on that venue (checklist item 11)? | Finance + tax adviser | The tax authority's published rules; the broker's fee schedule |

### 2.3 Options

| | Option A — First-party pilot cell (recommended) | Option B — Retail SaaS cell | Option C — Broker-first selection |
|---|---|---|---|
| Cell hypothesis | country = country of the operating entity [Open: Q-11-1]; customer type = the operating entity's own account, mapped to PROFESSIONAL or INSTITUTIONAL [Open: Q-11-3 decides which]; broker = one broker with a sandbox API [Open: Q-11-4]; venue = that country's primary listed-equity venue [Open]; asset class = cash equities and ETFs, long-only, no margin, no derivatives; feature = PAPER, then SUPERVISED; regulator = [Open: Q-11-3]; authorisation path = [Open: Q-11-3] | Same country; customer type = RETAIL (third-party tenants); same broker/venue/asset class; feature = SUPERVISED only; regulator and authorisation [Open: Q-11-3 (b)] | Shortlist brokers by sandbox availability first (Q-11-4), then take the country the chosen broker serves as the hypothesis |
| Pros | Smallest set of external unknowns: no third-party customer → the suitability, disclosure and marketing columns of COMPLIANCE_MATRIX are exercised later, not first [Committee]; exercises the whole pipeline (P1, P4, P6) on real broker/venue data in paper and supervised modes; cash equities are the simplest instrument master (no margin/expiry/exercise) and match the existing sim cell asset class EQUITY; customer type exists in the enum (F-5); aligns O-01 (autonomy OFF, supervised for professional persona) and O-02 (no invoicing needed before a third-party tenant exists) | Validates the commercial product earliest; personas Retail investor / Active trader get real journeys; reveals the full regulatory surface early | Fastest path to a certified adapter (Gate C evidence) |
| Cons | Delays learning about the retail regulatory surface; a first-party pilot is not proof of a marketable product; whether own-account automated trading needs authorisation is still a counsel question — this option does **not** assume it needs none [Open: Q-11-3] | Heaviest regulatory surface first (suitability/appropriateness, disclosures, marketing, client classification) [Source: 07 columns; requirements themselves [Open: Q-11-3]]; requires E14 billing, E15 disclosures and IdP/MFA (R-06) before any customer; highest reputational exposure (R-04) | Lets a vendor drive the legal hypothesis; contradicts the P5 sequence (hypothesis before broker certification); broker terms may still forbid the intended use [Open] |
| Cost | Counsel opinion (H-04), one broker sandbox (H-07), one data licence (H-08); no customer-facing build before Gate F | Counsel opinion covering third-party services; E14 + E15 + IdP build before first customer; DPIA (O-10); support hours (O-15) | As A plus rework if the broker's country is not where the entity may operate |
| Risk | Medium: regulatory status unknown until H-04; low market/customer risk (own capital, capped) | High: customer harm and regulatory risk if any of Q-11-3 (b) is answered late | Medium-high: hypothesis anchored on a vendor |
| Reversibility | High: a hypothesis row with Status "Hypothesis — not enabled"; nothing in code changes (ZZ stays until dual key at Gate F); changing the country before H-04 costs a document edit | Medium: build investment in E14/E15 is sunk if the cell is abandoned | Medium |
| Controls / tests affected | JURISDICTION_MATRIX + COMPLIANCE_MATRIX hypothesis rows (Compliance Agent); MARKET_LAUNCH_CHECKLIST items 1–18 targeted at one venue; TC-CP-003/004 unchanged; TC-BR-001..004 re-run against the real sandbox at Gate C; O-36 checklist-as-tests; no LIMIT_MATRIX effect (O-07 numbers still Trading Risk Committee) | As A plus suitability inputs in TC-CP-002, disclosure tests (H-16), TC-E2E persona journeys | As A |

### 2.4 Recommendation
**Option A**, as a hypothesis only. Confidence: **medium** on the structure of the cell (customer type, asset class, mode sequence follow from F-4..F-8 and the P5 sequence); **none/low** on every external fact — country, regulator, authorisation path, broker, venue, data licence are all [Open] until Q-11-1..Q-11-7 are answered. Provenance: [Source: 00, 07, 12, 17] via docs; [Committee] for the option design; [Verified] F-3..F-8.

### 2.5 Draft decision record line (for the Product Owner to accept, amend or reject)
`| D-0nn | 2026-09-__ | O-11 first launch cell **hypothesis** (not an enablement): country = <country of the operating entity, Q-11-1> × customer type = <PROFESSIONAL or INSTITUTIONAL, first-party account of the operating entity> × broker = <to be shortlisted, Q-11-4> × venue = <primary listed-equity venue> × asset class = cash equities/ETFs long-only, no margin or derivatives × feature = PAPER then SUPERVISED; regulator and authorisation path [Open: H-04 counsel opinion]; sim code keeps ZZ until dual-key enablement at Gate F; Bounded autonomous is not part of the hypothesis | Decided by: human Product Owner · Council: Product Council (recommend A) · Challenger: Compliance Agent · Recorded by: product-owner delegate | B: retail SaaS cell in the same country (rejected for now: heaviest regulatory surface first); C: broker-first selection (rejected: vendor drives the legal hypothesis) | [Committee: COUNCIL_2026-09-08_gate_A_product_director §2] / [Open: Q-11-1..Q-11-7] | docs/JURISDICTION_MATRIX.md hypothesis row; docs/COMPLIANCE_MATRIX.md hypothesis row; MISSING_ACTIONS H-03 evidence |`

### 2.6 Artefact edits implied (proposed; owners in brackets; none made by this packet)
- docs/JURISDICTION_MATRIX.md [Compliance Agent]: replace the "[Open: O-11 first hypothesis]" row with the hypothesis row; every legal column stays "No"; Dual-key "— / OFF"; Enabled modes "none"; Status "Hypothesis — not enabled".
- docs/COMPLIANCE_MATRIX.md [Compliance Agent]: one row per feature (PAPER, SUPERVISED) for the cell; Regulator, Authorisation, Suitability, Disclosures, Best execution, Algo controls, Reporting, Surveillance, Retention, Tax, Data licensing, Marketing = "[Open: H-04 / H-08 / Q-11-7]"; Technical flag OFF; Status "Not enabled".
- docs/PRODUCT_CHARTER.md [Product Director, after decision]: add "Launch hypothesis (Gate A)" section quoting the D-0nn line; docs/SCOPE.md assumptions: replace "O-11 first jurisdiction" with the cell reference; docs/ROADMAP.md Phase 0 row: "E15 hypothesis recorded (D-0nn)".
- docs/MARKET_LAUNCH_CHECKLIST.md [Compliance / Trading Domain / GTM]: header names the cell; all 18 statuses stay blank.
- docs/BACKLOG.md [Product Owner]: E15 story "Hypothesis cell dossier" (counsel questions Q-11-3, broker questions Q-11-4, data questions Q-11-5) with an RTM row FR-15.
- docs/RAID_LOG.md [Program Orchestrator / delegate]: O-11 Status → "Pack ready"; new dependency rows for Q-11-3..Q-11-7 if not already covered by H-04, H-07, H-08, O-10, O-12.
- Code: **no change**. `JURISDICTION = "ZZ"` remains until H-12 + H-17 (dual key) at Gate F [Verified: D-012].

### 2.7 Human actions required
| Act | Owner | Blocks | Register |
|---|---|---|---|
| Answer Q-11-1 and Q-11-2 in writing; record D-0nn | Product Owner | Gate A (V-A1) | H-03 (evidence: JURISDICTION_MATRIX row) |
| Engage external counsel with Q-11-3 (and Q-01-1/2, Q-02-2 below) as one brief | Legal Agent prepares; Product Owner signs the engagement | Gate D legal record; Gate A only needs the engagement started (PROJECT_EXECUTION_PLAN Phase 1) | H-04 |
| Start broker shortlist per Q-11-4 (no contract) | Broker-Connector Lead + Finance | Gate C | H-07 |
| Start data-licence enquiry per Q-11-5 | Legal Agent + Data Architect | Gate C | H-08, O-12 |
| DPIA scoping per Q-11-6 | Privacy Lead | Gate D | O-10 |

---

## 3 O-16 — Measurable outcome targets for Gate A

### 3.1 What is fixed and what is open
- Fixed: the four outcome dimensions in the charter — paper-mode reconciliation completeness, deterministic decision rate 100%, zero critical findings at each gate, operator time-to-halt in drills [Committee: PRODUCT_CHARTER.md]; NFR-DET-01 = 100% identical across replicas [Source: 05]; NFR-CON-01/02 = 100% [Source: 03]; SLI definitions fixed, numeric SLO targets only after measured baselines and business approval [Source: 10] [Open: O-03]; gate F requires no unresolved critical and highs resolved or risk-accepted [Source: 12]; IVA finding: only determinism carries a number and is verifiable in dev/sim (F-11).
- Open: a target, a measurement point, an evidence path and an independent measurer for each outcome; whether "reconciliation completeness" covers cash and open orders as well as positions; a numeric ceiling for time-to-halt.

### 3.2 Questions for humans [Open]
| Q | Question | Who answers | Source |
|---|---|---|---|
| Q-16-1 | What is the maximum time the Product Owner accepts between a human halt action and the platform refusing all new risk at the halted scope (the time-to-halt ceiling)? The council proposes no number: no risk-appetite statement exists and no drill has been run (H-19) | Product Owner (risk appetite) with the Chief Risk Agent | Risk-appetite statement (Executive Steering artefact per COMMITTEE_DEEP_DIVE §1.2 row 1 — not yet written [Open]); first drill baseline |
| Q-16-2 | Does "reconciliation completeness" include cash balances and open orders, or positions only? (Council proposes: positions + cash + open orders, since the reconciler already compares all three [Verified: reconcile.py].) | Product Owner | docs/SLO_SLA.md row definition |
| Q-16-3 | Does "zero critical findings" also require zero *unaccepted* high findings at each gate, or only at Gate F as [Source: 12] states? | Product Owner | goals/gate_*.md exit criteria |

### 3.3 Options

| | Option A — Definitional targets now; empirical ceiling after first drill (recommended) | Option B — Full numeric targets now, ceiling supplied by the Product Owner | Option C — Defer all targets to Gate C baselines |
|---|---|---|---|
| Content | Three outcomes get absolute targets that follow from the fail-closed design (100%, 100%, 0); time-to-halt gets a definitional target (no approval after activation) plus a mandatory wall-clock measurement per drill; the ceiling is added as an amendment after the first drill (H-19) | As A, plus a numeric time-to-halt ceiling recorded now from Q-16-1 | Only outcome names at Gate A |
| Pros | Every target is measurable today with an existing measurement point (F-9..F-12) or a named one to add; no invented number; satisfies IVA C-A1 "numeric targets" for 3 of 4 and a measurable definition for the 4th | Complete at Gate A | No risk of a wrong number |
| Cons | Time-to-halt remains without a ceiling until the first drill; Gate A record must say so explicitly | The number has no baseline; if too tight it will be missed for reasons unrelated to safety, if too loose it is not a control | Repeats the IVA PARTIAL finding; Gate A cannot pass [Source: 12] |
| Cost | One new SLI (`time_to_halt_s`) and a drill script (SRE Lead); a paper-run reconciliation report (Gate C) | As A | None now, all later |
| Risk | Low | Low-medium (number set without evidence) | High (gate blocked) |
| Reversibility | High: targets are documents; tightening later is a DECISION_LOG amendment | High | — |
| Controls / tests affected | TC-RC-001..005 (completeness), TC-RK-001 replica test (determinism), GATE_REPORTS + RAID (findings), TC-KS-001/006 + new drill evidence (halt); `observability/slis.yaml` new SLI; docs/SLO_SLA.md new row | As A | None |

### 3.4 Proposed target table (Option A) [Committee]

| Outcome | Definition | Measurement point | Target | Evidence path | Measured by (never the builder) | First measured |
|---|---|---|---|---|---|---|
| Paper-mode reconciliation completeness | (positions + cash + open orders reconciled against the broker statement by EOD+1) / total, per account [Open: Q-16-2] | `reconciliation_completeness_pct` (observability/slis.yaml) | 100% reconciled or classified: every unreconciled item is a typed break with one open ticket and the account in Supervised (F-9 safety semantic; D-017). No silent break. | docs/TEST_CASES/TC-RC.md; paper-run report at Gate C | QA Lead + IVA | Gate C (paper); dev/sim quartet now |
| Deterministic decision rate | Byte-identical `DecisionRecord` and `EligibilityDecision` across replicas for identical inputs and `policy_version` | TC-RK-001 replica test; IVA probe | 100% (already in NFR-DET-01) | GATE_A_2026-09-07 §3; EVIDENCE_REPORT.md | IVA | Now (dev/sim) |
| Gate findings | Open critical findings at gate decision; high findings without a written risk acceptance by the Product Owner (D-039 step 4) [Open: Q-16-3] | docs/GATE_REPORTS/, docs/RAID_LOG.md | 0 open critical at every gate; highs closed or risk-accepted in writing before the gate passes | GATE_REPORTS + DECISION_LOG risk-acceptance rows | IVA | Now |
| Operator time-to-halt | (a) Block rate: number of decisions with decision time > `activated_at` that are APPROVED within the halted scope; (b) wall-clock from the operator's action timestamp (UI/CLI) to the `killswitch.engaged` audit event and to the last cancel request sent | Kill Switch service `activated_at` (F-10); new SLI `time_to_halt_s` | (a) 0 in every drill and test (100% block); (b) recorded in every drill; ceiling [Open: Q-16-1, set after first drill H-19] | TC-KS-001/006; drill logs (H-19); docs/SLO_SLA.md new row | SRE Lead runs, IVA witnesses | Sim drill at Gate C; real infrastructure at Gate D/E (H-19) |

### 3.5 Recommendation
**Option A**, amended to B as soon as the Product Owner answers Q-16-1 after the first drill. Confidence: **medium-high** — all four measurement points exist or are one SLI away, and the three absolute targets are the fail-closed semantics already implemented (F-9..F-12); the only unknown is the halt ceiling, which is deliberately left [Open]. Provenance: [Source: 03, 05, 10, 12] via docs/NFR.md and docs/SLO_SLA.md; [Verified] F-9..F-12; [Committee] table 3.4.

### 3.6 Draft decision record line
`| D-0nn | 2026-09-__ | O-16 Gate A outcome targets: reconciliation completeness 100% reconciled-or-classified (positions, cash, open orders, EOD+1; any residue = typed break + ticket + Supervised); deterministic decision rate 100% byte-identical across replicas; 0 open critical findings at every gate and highs closed or risk-accepted in writing; time-to-halt = 0 approvals after `activated_at` in every drill (100% block) with wall-clock operator-action → `killswitch.engaged` → last cancel recorded per drill; numeric ceiling [Open] until the first drill (H-19) | Decided by: human Product Owner · Council: Product Council (recommend A) · Challenger: Chief Risk Agent · Recorded by: product-owner delegate | B: numeric ceiling now without a baseline (deferred); C: defer all to Gate C (rejected: Gate A blocked) | [Committee: COUNCIL_2026-09-08_gate_A_product_director §3] / [Open: Q-16-1..3] | docs/PRODUCT_CHARTER.md §Measurable outcomes; docs/SLO_SLA.md; observability/slis.yaml |`

### 3.7 Artefact edits implied
- docs/PRODUCT_CHARTER.md [Product Director, after decision]: replace the "[Open: O-16 ...]" line with table 3.4 and the D-0nn reference.
- docs/SLO_SLA.md and observability/slis.yaml [SRE Lead]: add `time_to_halt_s` (definition, measurement point Kill Switch service, target null until Q-16-1, safety semantic: drill failure = Gate D/E finding); annotate `reconciliation_completeness_pct` with the Gate A target.
- docs/TEST_STRATEGY.md / docs/TEST_CASES [QA Lead]: a drill test ID (proposed TC-KS-009 "time-to-halt measured") that writes the two timestamps to the evidence record.
- docs/RELEASE_CHECKLIST.md Gate A row [Program Orchestrator]: link the four evidence paths.
- docs/RAID_LOG.md: O-16 Status → "Pack ready"; a new dependency "time-to-halt ceiling after first drill" [Open], owner Chief Risk Agent, needed by Gate C.

### 3.8 Human actions required
| Act | Owner | Blocks | Register |
|---|---|---|---|
| Answer Q-16-2, Q-16-3; record D-0nn | Product Owner | Gate A (C-A1) | new H row proposed: "Approve Gate A outcome targets" |
| Answer Q-16-1 after the first sim drill | Product Owner + Chief Risk Agent | Gate C | H-19 (drill), H-14 (SLO targets) |
| Witness the first drill | IVA | Gate C | H-19 |

---

## 4 O-01 — Persona × mode policy per jurisdiction (autonomy default OFF)

### 4.1 What is fixed and what is open
- Fixed [Source: 01]: ten personas; six modes. [Source: 00]: live autonomy only per tenant, account, jurisdiction, broker, instrument, strategy, model version and capital envelope; human override supersedes everything. [Source: 07]: customer type is a cell dimension. [Source: 12]: Supervised needs Gate D, Bounded autonomy Gate E. [Committee]: mode = cell feature (ADR-034, F-4); one-step ladder with gate records; agents never change mode; restore from HALTED capped at SUPERVISED (D-021); PERSONAS.md default column already says autonomy only per jurisdiction policy; `CustomerType` enum (F-5).
- Open: mapping of personas to `CustomerType`; which persona may reach Supervised or Bounded autonomous in which cell; whether a retail customer may ever be offered Bounded autonomy; the classification criteria (regulatory facts).

### 4.2 Questions for humans [Open]
| Q | Question | Who answers | Source |
|---|---|---|---|
| Q-01-1 | In the O-11 country, what are the criteria that classify a customer as retail, professional, eligible counterparty or institutional, and may a retail customer elect a professional classification? | External counsel (H-04) | The regulator's client-classification rules; counsel opinion |
| Q-01-2 | Does offering (a) human-approved execution (Supervised) or (b) automatic execution inside limits (Bounded autonomous) to a third-party customer constitute a distinct regulated service (e.g. discretionary management) requiring its own authorisation, suitability or appropriateness assessment, or disclosure? | External counsel (H-04) | Same rulebook; counsel opinion |
| Q-01-3 | Does the first cell involve any third-party customer? (Inherits Q-11-2.) | Product Owner | O-11 decision |
| Q-01-4 | Which human roles in the operating entity will hold the personas Professional trader / Portfolio manager / Risk officer / Compliance analyst for the first cell, and are they distinct persons (author ≠ reviewer ≠ approver; deputy O-19)? | Product Owner | H-01 appointments |

### 4.3 Options

| | Option A — Global floor only | Option B — Global floor + hypothesis matrix for the first cell (recommended) | Option C — Persona-level global entitlement |
|---|---|---|---|
| Policy | Every persona, every jurisdiction: Observe, Backtest, Paper. Supervised and Bounded autonomous OFF everywhere; any enablement is a per-cell dual-key act after Gate D/E. No planning matrix | Same floor, plus the matrix in 4.4 declared as a *hypothesis* for the O-11 cell: it drives backlog and test design and has **no technical effect** (flags stay OFF, `CP-JURIS-NOCELL` applies until dual key) | E.g. Professional trader gets Supervised in every jurisdiction once Gate D passes; Retail gets Supervised after appropriateness |
| Pros | Simplest; exactly what the code does today (F-4, F-6, F-7) | Keeps the floor and gives Gate D/E builders and counsel a concrete question set; retail autonomy explicitly excluded from the hypothesis; reversible | Simple to explain commercially |
| Cons | Gives E05/E07 (approval queue), E14 and E15 no persona target; counsel brief has no concrete question | Requires discipline that "hypothesis" ≠ entitlement (a documentation and test rule, see 4.6) | Contradicts [Source: 07] ("worldwide" never legal availability) and ADR-034 (mode is a cell dimension); would need per-jurisdiction exceptions anyway |
| Cost | None | Document edits; two parametrised tests | Rework at every new jurisdiction |
| Risk | Low technical, medium delivery (untargeted build) | Low | High compliance |
| Reversibility | High | High | Low once customers rely on it |
| Controls / tests affected | TC-CP-004 (NOCELL per mode), TC-ID-003 (ladder), TC-KS-004 (restore cap) | As A plus proposed TC-CP-007 (every `CustomerType` × mode without a cell → NOCELL) and TC-ID-006 (no persona role can promote beyond `enabled_feature`); PERSONAS.md column change; COMPLIANCE_MATRIX feature rows | Would need a persona-level flag path — a new attack surface (T-15 drift) |

### 4.4 Hypothesis matrix for the first cell (Option B) — no technical effect [Committee]

Legend: Y = available at the floor now (dev/sim → paper per gate); H(D) = hypothesis, only after Gate D and a dual-key cell for that feature; H(E) = hypothesis, only after Gate E, a dual-key cell for BOUNDED_AUTONOMOUS and an approved capital envelope (H-13); OFF = not in the hypothesis for the first cell; — = not a trading persona.

| Persona [Source: 01] | `CustomerType` mapping [Open: Q-01-1] | Observe | Backtest | Paper | Supervised | Bounded autonomous | Halted / controls |
|---|---|---|---|---|---|---|---|
| Retail investor | RETAIL | Y | Y | Y | OFF — not in the first cell (Option A of O-11 has no retail customer); revisit only with Q-01-2 answered | OFF — not planned for any cell until a separate decision | may request halt of own account |
| Active trader | RETAIL or PROFESSIONAL [Open: Q-01-1] | Y | Y | Y | H(D) only if classified PROFESSIONAL in the cell | OFF | may halt own account |
| Professional trader | PROFESSIONAL | Y | Y | Y | H(D) — the first-party account of the operating entity | H(E), per strategy, per cell, capital envelope H-13 | may halt own account |
| Portfolio manager | PROFESSIONAL / INSTITUTIONAL | Y | Y | Y | H(D) for accounts under management | H(E) as above | may halt managed accounts; is in `MODE_CHANGERS` (R-05 open) |
| Risk officer | — | Y (read) | — | — | — | — | halt any scope; set limits via maker-checker |
| Compliance analyst | — | Y (read) | — | — | — | — | legal record / technical flag (dual key, different persons) |
| Operations analyst | — | Y (read) | — | — | — | — | break resolution; may demote to Supervised |
| Tenant administrator | — | Y (read) | — | — | — | — | users, roles, brokers; **no mode change** |
| Auditor | — | Y (read-only) | — | — | — | — | none |
| Support engineer | — | Y (read) | — | — | — | — | runbooks only; no mode, limit or approval path (F-13) |

Rules attached to the matrix [Committee]: (1) a persona is never an entitlement — the account's cell (feature dimension) and gate record are; (2) H(D)/H(E) become real only through the dual key (H-12, H-17) and the ladder (F-6, F-7); (3) the "System" actor of journey J-04 acts only for an account whose human persona owner exists and whose cell has feature BOUNDED_AUTONOMOUS; (4) no AI/MCP component holds any persona.

### 4.5 Recommendation
**Option B.** Confidence: **medium-high** for the floor (it is what the code enforces, F-4..F-7) and **low** for the H(D)/H(E) cells, which depend entirely on Q-01-1/Q-01-2 and the O-11 decision. Provenance: [Source: 00, 01, 07, 12]; [Verified] F-4..F-8; [Committee] 4.4.

### 4.6 Draft decision record line
`| D-0nn | 2026-09-__ | O-01 persona × mode policy: global floor for every persona and jurisdiction = Observe, Backtest, Paper; Supervised and Bounded autonomous OFF everywhere; enablement only per six-dimension cell by dual key after Gate D (Supervised) / Gate E (Bounded, with capital envelope); the matrix in COUNCIL_2026-09-08_gate_A_product_director §4.4 is a planning hypothesis for the O-11 cell with no technical effect; retail Bounded autonomy is not in any hypothesis | Decided by: human Product Owner · Council: Product Council (recommend B) · Challenger: Compliance Agent (owner of the underlying policy per the O-01 pack) · Recorded by: product-owner delegate | A: floor only (rejected: no build/counsel target); C: persona-level global entitlement (rejected: contradicts [Source: 07] and ADR-034) | [Committee] / [Open: Q-01-1..4] | docs/PERSONAS.md; docs/COMPLIANCE_MATRIX.md feature rows; TC-CP-004, proposed TC-CP-007, TC-ID-006 |`

### 4.7 Artefact edits implied
- docs/PERSONAS.md [Product Director, after decision]: replace the "Modes available (default)" column with the 4.4 matrix columns and the four rules; add the `CustomerType` mapping column marked [Open: Q-01-1].
- docs/COMPLIANCE_MATRIX.md [Compliance Agent]: the O-11 hypothesis rows carry feature PAPER and SUPERVISED only; no BOUNDED_AUTONOMOUS row exists until Gate E.
- docs/JOURNEYS.md [Product Director]: J-04 persona "System" annotated with rule (3).
- docs/PRD.md [Product Director]: FR-12 acceptance sketch gains "Given a persona with no cell for the requested mode, when an intent is submitted, then eligibility returns CP-JURIS-NOCELL"; FR-01 gains "tenant administrator cannot change mode".
- test/ [Backend Lead; 2nd-line Compliance Agent CODEOWNER]: TC-CP-007 parametrised over `CustomerType` × mode; TC-ID-006 persona role vs `enabled_feature`; RTM rows FR-15 and FR-01 updated [Program Orchestrator].
- docs/RAID_LOG.md: O-01 Status → "Pack ready"; R-05 (PORTFOLIO_MANAGER in `MODE_CHANGERS`) is re-raised to the Product Owner as a question: should promotion route through maker-checker with a 2nd-line checker (C01 §8)?

### 4.8 Human actions required
| Act | Owner | Blocks | Register |
|---|---|---|---|
| Record D-0nn for O-01 after the O-11 decision | Product Owner | Gate A (C-A3) | new H row proposed: "Approve persona × mode floor and hypothesis" |
| Include Q-01-1 and Q-01-2 in the counsel brief | Legal Agent | Gate D | H-04 |
| Name the humans holding the trading and control personas for the first cell (Q-01-4) | Product Owner | Gate A/C (author ≠ reviewer ≠ approver; deputy) | H-01, O-19 |

---

## 5 O-02 — Pricing and billing scope (E14)

### 5.1 What is fixed and what is open
- Fixed [Source: 14]: E14 Billing, support, admin is an epic with first gate F; owner Backend Lead, reviewer Finance / Support & Training Lead. [Source: 00]: profit is never a promise, so no commercial term may imply returns. [Source: 01]: custody and deposits/withdrawals are out of scope, so billing never touches client money or broker funding. [Committee]: billing never gates a Kill Switch or a halt; support is read-only plus runbooks (F-13); Finance & Vendor Lead defines billing scope with the Product Director (goals/25); the cost model (O-13) is not yet produced. No pricing model, price, tax rule or invoicing vendor exists anywhere in the repository [Verified: grep "billing|pricing|invoice|tax" across docs/ and goals/].
- Open: pricing model; what is metered; what is billed; what is excluded; invoicing and tax handling; whether any billing is needed before a third-party tenant exists.

### 5.2 Questions for humans [Open]
| Q | Question | Who answers | Source |
|---|---|---|---|
| Q-02-1 | Is the commercial intent first-party operation during the pilots with SaaS later, or SaaS from the outset? (Inherits Q-11-2.) | Product Owner | Business plan |
| Q-02-2 | In the O-11 country, does charging a fee for the platform — and specifically any performance-linked or per-trade fee — constitute or change a regulated activity, or trigger disclosure or marketing rules? | External counsel (H-04) | The regulator's rulebook; counsel opinion |
| Q-02-3 | What VAT / sales-tax treatment and invoice content rules apply to a software subscription sold from the operating entity's country to domestic and cross-border tenants? | Finance + tax adviser | Tax authority's published rules; adviser's written advice |
| Q-02-4 | Which invoicing/billing provider will be used, under what terms, with what data-processing agreement? | Finance & Vendor Lead | Provider terms; docs/VENDOR_ASSESSMENTS/TEMPLATE.md |
| Q-02-5 | Price points and tier boundaries | Product Owner + Finance, from the cost model (O-13) | Cost model; never set by the council |

### 5.3 Options

| | Option A — Meter now, invoice later; subscription hypothesis (recommended) | Option B — Usage-based billing per intent/order from Gate D | Option C — Performance fee / profit share |
|---|---|---|---|
| Scope | Pricing model hypothesis: per-tenant subscription with tiers by seats and connected accounts [prices Open: Q-02-5]. Metered from Gate D for cost attribution only: intents decided, backtests run, data volume, tool calls — emitted as `billing.metered` events derived from the audit chain, never from the execution path. Invoicing, tax and dunning through an external provider [Open: Q-02-4] from Gate F, and only once a third-party tenant exists. Excluded: performance fees, per-trade fees, commission sharing, broker rebates or payment for order flow [legality Open: Q-02-2 — excluded on posture grounds regardless], client-money handling, referral payments | Charge per decided intent or executed order; invoice monthly from Gate D | Fee as a share of realised PnL |
| Pros | No invoicing build before a customer exists (consistent with O-11 Option A); revenue never depends on trading volume, so no incentive to over-trade (PERSONAS.md design risk for Active trader); billing stays outside the control and execution planes; every metered unit is reconstructible from audit | Aligns price with cost | Aligns price with customer outcome |
| Cons | Deferred commercial validation; the subscription tiers are a hypothesis until Q-02-5 | Creates an over-trading incentive; couples billing to the execution path; a metering error could look like an execution error; per-order pricing may be a regulated-fee question [Open: Q-02-2] | Implies returns [Source: 00 prohibition]; may be a regulated activity [Open: Q-02-2]; conflicts with "profit is never a promise" in every customer document; rejected on posture, not only on legality |
| Cost | Metering events + external provider integration at Gate F; tax advice | Metering + invoicing at Gate D; more E14 build before Gate D | Legal review; PnL attribution certified for billing |
| Risk | Low | Medium-high (incentive misalignment, R-04) | High |
| Reversibility | High: switching to usage tiers later is a price-list change if metering exists from Gate D | Medium | Low |
| Controls / tests affected | Proposed NFR-BIL-01 (billing plane isolation: no route to control/execution planes; no write path to mode, limits, approvals; billing outage never blocks halt); proposed quartet TC-BIL-001..004; enum-absent permissions extended (no BILLING_ADJUST_LIMITS, no CLIENT_MONEY); THREAT_MODEL new boundary B-BIL | As A plus execution-path metering tests | As A plus PnL attribution tests |

### 5.4 Recommendation
**Option A.** Confidence: **medium-high** on scope and exclusions (they follow from [Source: 00, 01] and F-13); **none** on prices, tiers, tax and provider, all [Open]. Provenance: [Source: 00, 01, 14] via docs; [Verified] F-13; [Committee] 5.3.

### 5.5 Draft decision record line
`| D-0nn | 2026-09-__ | O-02 billing scope for E14: pricing model hypothesis = per-tenant subscription tiered by seats and connected accounts (prices [Open: cost model O-13]); usage metered from Gate D for cost attribution only (`billing.metered` events derived from the audit chain); invoicing, tax and dunning via an external provider from Gate F and only once a third-party tenant exists; excluded permanently without a separate decision: performance fees, per-trade fees, commission sharing, broker rebates, client-money handling, referral payments; billing has no route to the control or execution planes and never gates a halt or Kill Switch (NFR-BIL-01) | Decided by: human Product Owner · Council: Product Council with Finance & Vendor Lead (recommend A) · Challenger: Chief Risk Agent or Compliance Agent · Recorded by: product-owner delegate | B: usage-based per intent/order from Gate D (rejected: over-trading incentive, execution-path coupling); C: performance fee (rejected: implies returns, [Source: 00]) | [Committee] / [Open: Q-02-1..5] | docs/SCOPE.md billing exclusions; docs/PRD.md FR-16; docs/NFR.md NFR-BIL-01; goals/build/E14 |`

### 5.6 Artefact edits implied
- docs/SCOPE.md [Product Director, after decision]: add rows "Performance fees / per-trade fees / commission sharing / broker rebates / client money / referral payments — no permission flag; billing plane has no control-plane route".
- docs/PRD.md [Product Director]: FR-16 acceptance gains "Given a billing outage or an unpaid tenant, when a halt or Kill Switch is requested, then it executes unaffected" and "Given the billing service, when it attempts any mode, limit or approval write, then it is denied (no permission exists)".
- docs/PERSONAS.md / docs/JOURNEYS.md [Product Director]: Tenant administrator sees metering and invoices (read); new journey J-09 "Tenant metering and invoice view" (Gate F).
- docs/ROADMAP.md [Product Director]: Phase 3 (Gate D) "E14 metering"; Phase 5 (Gate F) "E14 invoicing via provider".
- docs/NFR.md [Enterprise Architect]: NFR-BIL-01 as above; docs/THREAT_MODEL.md [Security Architect]: boundary B-BIL, threats "billing writes to control plane", "metering tampering to hide activity".
- goals/build/E14_billing_support_admin.md and docs/BACKLOG.md P7 [Product Owner / Program Orchestrator]: scope text replaced by D-0nn; first story = metering quartet TC-BIL-001..004 (positive: one `billing.metered` per decided intent with correlation_id; negative: metering absent → no effect on decisions; abuse: billing principal attempts limit/mode write → denied; recovery: metering rebuilt from the audit chain export).
- docs/RAID_LOG.md: O-02 Status → "Pack ready"; O-31 (services absent) unchanged.

### 5.7 Human actions required
| Act | Owner | Blocks | Register |
|---|---|---|---|
| Answer Q-02-1; record D-0nn (or a formal deferral, which the IVA also accepts as closing C-A5) | Product Owner | Gate A (C-A5) | new H row proposed: "Approve billing scope" |
| Include Q-02-2 in the counsel brief | Legal Agent | Gate F | H-04 |
| Obtain tax advice (Q-02-3) | Finance | Gate F | new H row proposed |
| Billing provider assessment and contract (Q-02-4) | Finance & Vendor Lead | Gate F | new H row proposed; VENDOR_ASSESSMENTS/ |
| Set price list from the cost model (Q-02-5) | Product Owner + Finance | Gate F | O-13, new H row proposed |

---

## 6 Threat-model delta (proposed for the Security Architect; nothing changed here)

| Threat | Boundary | Introduced by | Control | Test | Owner |
|---|---|---|---|---|---|
| T-14 (existing) Gate-record forgery lets a "hypothesis" be treated as an enablement | B2 | O-11 hypothesis row | Hypothesis rows carry Status "Hypothesis — not enabled", Technical flag OFF; engine re-checks dual key per intent (F-6); GateRecord signing still open (O-22) | TC-CP-003/004 | Compliance Agent, Program Orchestrator |
| NEW T-28 Persona matrix read as entitlement (a role grants Supervised without a cell) | B2/B3 | O-01 Option B | Rule (1) in §4.4; `CP-JURIS-NOCELL` for any mode without a cell | proposed TC-CP-007, TC-ID-006 | Backend Lead / Compliance Agent |
| NEW T-29 Billing principal reaches the control plane (limit/mode/approval write) or its outage blocks a halt | new B-BIL | O-02 Option A | Enum-absent permissions; plane guard extended to a billing plane; halt path has no billing dependency | proposed TC-BIL-003, TC-BIL-001 | Security Architect / Backend Lead |
| NEW T-30 Metering tampering hides or inflates activity | B-BIL ↔ audit | O-02 Option A | Metering derived from the hash-chained audit export, never written by the execution path | proposed TC-BIL-004 | SRE Lead |
| NEW T-31 Time-to-halt drill run by the builder and self-reported | evidence | O-16 | Drill run by SRE Lead, witnessed by IVA, timestamps in the evidence record | proposed TC-KS-009 | IVA |

## 7 Control quartet per critical control touched (existing tests are [Verified]; proposed are [Committee])

| Control | Positive | Negative | Abuse | Recovery |
|---|---|---|---|---|
| Cell/no-cell default OFF (O-11, O-01) | TC-CP-004 dual key → live | TC-CP-003 legal record without flag blocked | TC-CP-003 same signer/activator; agent activation denied | TC-CP-004 single-person disable; proposed TC-CP-007 every `CustomerType` × mode without cell → NOCELL |
| Mode ladder / persona floor (O-01) | TC-ID-003 promotion with gate record | TC-ID-003 no gate / skip step denied | TC-ID-003 agent promotion denied; proposed TC-ID-006 persona role beyond `enabled_feature` denied | TC-ID-004 / TC-KS-004 two-person restore capped at SUPERVISED |
| Billing isolation (O-02) | proposed TC-BIL-001 metering event per decided intent, correlation_id present | proposed TC-BIL-002 metering absent → decision unaffected; halt unaffected by billing outage | proposed TC-BIL-003 billing principal limit/mode write denied | proposed TC-BIL-004 metering rebuilt from audit export |
| Time-to-halt measurement (O-16) | TC-KS-001 activation blocks new risk | TC-KS-006 monitor-triggered halt | GAP — no test that a decision timestamped after `activated_at` is refused at every level (proposed TC-KS-009 block-rate assertion) | TC-KS-004 restore; drill log H-19 |
| Reconciliation completeness (O-16) | TC-RC-001 | TC-RC-002/005 breaks classified | TC-RC abuse row (see TC-RC.md) | TC-RC recovery row; Supervised on break |

## 8 Evidence list (all read at the 2026-09-08 working tree)
- docs/PRODUCT_CHARTER.md, docs/PRD.md, docs/PERSONAS.md, docs/SCOPE.md, docs/JOURNEYS.md, docs/ROADMAP.md (owned; not edited by this packet)
- docs/JURISDICTION_MATRIX.md, docs/COMPLIANCE_MATRIX.md, docs/MARKET_LAUNCH_CHECKLIST.md, docs/LIMIT_MATRIX.md, docs/SLO_SLA.md, docs/NFR.md, observability/slis.yaml
- docs/RAID_LOG.md (O-01, O-02, O-11, O-16, O-19, R-05, R-48), docs/DECISION_LOG.md (D-003, D-012, D-017, D-021, D-035, D-039), docs/MISSING_ACTIONS.md (H-01..H-24), docs/PRODUCT_OWNER.md v2.0
- docs/GATE_REPORTS/GATE_A_2026-09-07.md; docs/SESSIONS/C01_product_scope.md, C06_compliance_market_access.md, P5_market_enablement.md; docs/TEST_CASES/EVIDENCE_REPORT.md, TC-KS.md, TC-RC.md
- goals/decisions/O-01, O-02, O-11, O-16 packs; goals/gate_A_discovery.md; goals/00_product_owner.md §COUNCILS; goals/build/E14_billing_support_admin.md; goals/external/legal_regulatory_engagement.md, broker_onboarding.md
- Code: libs/core/rtcore/schemas/compliance.py; services/identity/identity_service/accounts.py; services/compliance/compliance_engine/eligibility.py; services/killswitch/killswitch_service/service.py; services/reconciliation/reconciliation_service/reconcile.py

## 9 RAID entries proposed (numbering by the Program Orchestrator / delegate), assumptions, confidence, provenance

| Type | Item | Owner | Needed by |
|---|---|---|---|
| Status change | O-11, O-16, O-01, O-02 → "Pack ready" (this packet); they close only when the Product Owner records D-0nn | product-owner delegate | Gate A |
| Dependency | Counsel brief must bundle Q-11-3, Q-01-1, Q-01-2, Q-02-2 so that one opinion covers cell, classification and fees | Legal Agent | Gate D (engagement started before Gate A) |
| Gap | No risk-appetite statement exists to derive the time-to-halt ceiling (Q-16-1) | Product Owner, Chief Risk Agent | Gate C |
| Gap | No `time_to_halt_s` SLI and no block-rate assertion after `activated_at` (proposed TC-KS-009) | SRE Lead, QA Lead | Gate C |
| Gap | No tests for persona-role vs `enabled_feature` (TC-ID-006) and `CustomerType` × mode NOCELL (TC-CP-007) | Backend Lead; Compliance Agent CODEOWNER | Gate D |
| Gap | E14 billing isolation NFR-BIL-01, boundary B-BIL and quartet TC-BIL-001..004 absent | Enterprise Architect, Security Architect, Backend Lead | Gate D (metering), F (invoicing) |
| Observation | docs/PO_DECISION_QUEUE.md now exists (untracked); the delegate should copy the four one-line decision requests below into its Recommendation column after the Compliance Agent's challenge (COUNCIL_2026-09-08_gate_A_compliance_legal.md) and the IVA evidence check are reconciled with this packet | product-owner delegate | Gate A |
| Observation | R-05 (PORTFOLIO_MANAGER may promote with a gate record) is a Product Owner question raised again under O-01 | Product Owner, Chief Risk Agent | Gate B |

**Assumptions [Committee]:** the Product Owner intends to operate before offering the product to third parties (Option A of O-11 and O-02 both rest on this; if Q-11-2 is answered "third-party from the outset", Option B of O-11 and the retail rows of §4.4 must be re-analysed with counsel input before Gate A); the cash-equity asset class is chosen for simplicity of the instrument master, not for any expected return; nothing in this packet moves the sim cell from ZZ.

**Confidence:** O-11 medium (structure) / none (external facts); O-16 medium-high; O-01 medium-high (floor) / low (hypothesis cells); O-02 medium-high (scope) / none (prices, tax, provider).

**Provenance:** [Source: 00, 01, 02, 03, 05, 07, 10, 12, 13, 14, 17] as transmitted by docs/; [Verified] facts F-1..F-15 re-read in the working tree on 2026-09-08; [Committee] all option designs, matrices and target definitions; [Open] every question Q-11-*, Q-16-*, Q-01-*, Q-02-* and every price, threshold, regulator, licence, broker and data entitlement.

**Decision requests for docs/PO_DECISION_QUEUE.md (one line each, for the delegate):**
1. O-11 — Adopt the first-party cash-equity cell hypothesis (§2.5) and answer Q-11-1/Q-11-2? Blocks Gate A (IVA V-A1).
2. O-16 — Adopt the four outcome targets (§3.4) with the time-to-halt ceiling left open until the first drill? Blocks Gate A (C-A1).
3. O-01 — Adopt the global floor plus the first-cell hypothesis matrix (§4.4)? Blocks Gate A (C-A3).
4. O-02 — Adopt "meter from Gate D, invoice from Gate F, subscription hypothesis, no performance or per-trade fees" (§5.5), or formally defer? Blocks Gate A (C-A5).

| Role | Name | Line | Signature | Date |
|---|---|---|---|---|
| Author | Product Director (AI agent) | 1st | — (AI output; recommends only) | 2026-09-08 |
| Challenger | pending (Compliance Agent for O-11/O-01; Chief Risk Agent for O-16/O-02) | 2nd | | |
| Evidence check | pending (Independent Validation Agent) | 3rd | | |
| Decider | pending (human Product Owner) | — | | |
