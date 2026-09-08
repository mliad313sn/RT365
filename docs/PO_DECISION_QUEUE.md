# PO_DECISION_QUEUE — every human decision, in the order the gates need them

| Owner | Reviewer (different line) | Approving body | First gate | Status |
|---|---|---|---|---|
| Product Owner (decides) · delegate agent (prepares) | Independent Validation Agent | Product Owner (D-039) | A | living register since 2026-09-08 |

How it works (docs/PRODUCT_OWNER.md §Decision protocol): the delegate convenes the council named in the row, the council writes `docs/SESSIONS/COUNCIL_<date>_<topic>_*.md`, the delegate fills **Recommendation**, the human Product Owner writes the **Decision** (approve / reject / defer / override with written risk acceptance), and the delegate records it in docs/DECISION_LOG.md and executes the consequences. Rows are ordered by the gate they block. A row closes only when its evidence file exists.

## 0. Confirm the authority model on the committed tree (IVA-A-03, O-62)
| Item | Question | Recommendation | Decision (human Product Owner) | Decided on |
|---|---|---|---|---|
| D-039 | Confirm, on the committed tree, that the Product Owner approves every human decision, gate and risk acceptance, drives delivery to a controlled market release and convenes councils as advisory bodies, with the compensating controls of docs/PRODUCT_OWNER.md (deputy for two-person controls by Gate C; written overrides; agents never approve) | IVA: confirm explicitly (an AI-recorded instruction is not the human act); Compliance & Legal: the Product Owner is never a dual-key hand (X-7, now enforced by TC-CP-007) | **Confirmed (D-041) under the owner's delegation D-040** | 2026-09-08 |

## A. Decisions (RAID open items with a decision pack)

Order recommended by Independent Validation (COUNCIL_2026-09-08_gate_A_iva §4): 0 → H-02 → O-11/H-03 → O-16 → O-01 → O-02 → O-19 deputy gate → re-convene Gate A (`gate-a` agent) against the commit CI evidenced.

| Item | Gate | Question | Council to convene | Pack | Council status | Recommendation | Decision (human Product Owner) | Decided on |
|---|---|---|---|---|---|---|---|---|
| O-01 | A | Persona × mode policy per jurisdiction (autonomy default OFF) | Compliance & Legal Committee + Product Council | goals/decisions/O-01_decision_pack.md | convened 2026-09-08: COUNCIL_2026-09-08_gate_A_product_director.md (options), _compliance_legal.md (challenge), _iva.md (evidence) | Product Council: **Option B — global floor plus first-cell hypothesis matrix**: every persona and jurisdiction = Observe/Backtest/Paper; Supervised and Bounded OFF everywhere; enablement only per six-dimension cell by dual key after Gate D/E (what the code enforces today); Retail Supervised OFF for the first cell, Bounded OFF in every hypothesis; control personas have no trading mode; persona→CustomerType mapping [Open: Q-01-1]. Compliance & Legal: consistent; reject autonomy default ON (X-4) and self-declared customer type (X-5); PAPER-only interim policy if deferred (X-11). Confidence medium-high (floor), low (hypothesis cells). **Decision request:** Adopt the global floor plus the first-cell hypothesis matrix (autonomy default OFF everywhere)? | **Adopted (D-045)**: Option B, autonomy OFF by default | 2026-09-08 |
| O-02 | A | Pricing and billing scope (E14) | Product Council (Finance) | goals/decisions/O-02_decision_pack.md | convened 2026-09-08: COUNCIL_2026-09-08_gate_A_product_director.md (options), _compliance_legal.md (challenge), _iva.md (evidence) | Product Council: **Option A — meter from Gate D, invoice from Gate F**: per-tenant subscription tiered by seats/accounts, prices from the cost model (O-13); usage metered from the audit chain for cost attribution only; invoicing and tax via an external provider once a third-party tenant exists; permanently excluded without a separate decision: performance fees, per-trade fees, commission sharing, broker rebates, client money, referral payments; new NFR-BIL-01 and quartet TC-BIL-001..004. Compliance & Legal: consistent; reject performance-linked or profit-share billing and billed 'recommendations' (X-8, X-9). Confidence medium-high (scope), none (prices, tax, provider). **Decision request:** Adopt 'meter from Gate D, invoice from Gate F, subscription hypothesis, no performance or per-trade fees', or formally defer to a named gate? | **Adopted (D-046)**: Option A | 2026-09-08 |
| O-11 | A | First launch jurisdiction cell hypothesis | Compliance & Legal Committee + Product Council | goals/decisions/O-11_decision_pack.md | convened 2026-09-08: COUNCIL_2026-09-08_gate_A_product_director.md (options), _compliance_legal.md (challenge), _iva.md (evidence) | Product Council: **Option A — first-party pilot cell**: country of the operating legal entity [Open: Q-11-1] × the entity's own account (PROFESSIONAL/INSTITUTIONAL) × one sandbox-API broker [Open] × primary listed-equity venue × cash equities/ETFs long-only × PAPER then SUPERVISED; regulator and authorisation path are counsel questions (H-04). Compliance & Legal: consistent; reject any retail × Supervised/Bounded first cell, a multi-cell hypothesis, or replacing `ZZ` in code before a legal record; minimum evidence E-1..E-10; counsel questions Q-J01..Q-J18. IVA: records the hypothesis as 'Legal basis: No / dual-key OFF / modes none', never as a legal fact. Confidence medium (structure), none (external facts). **Decision request:** Adopt the first-party cash-equity cell hypothesis and answer Q-11-1 (operating entity's country) and Q-11-2 (first party before third parties)? | **Adopted as hypothesis (D-043)**: Option A; Q-11-2 = first party; Q-11-1 country = owner's operating entity [fact to supply] | 2026-09-08 |
| O-16 | A | Measurable outcome targets for Gate A | Product Council + IVA | goals/decisions/O-16_decision_pack.md | convened 2026-09-08: COUNCIL_2026-09-08_gate_A_product_director.md (options), _compliance_legal.md (challenge), _iva.md (evidence) | Product Council: **Option A — definitional targets now**: reconciliation completeness 100% reconciled-or-classified (positions, cash, open orders, EOD+1); deterministic decision rate 100% byte-identical (IVA-verified in dev/sim); 0 open critical findings per gate, highs risk-accepted in writing; time-to-halt = 100% block of approvals after `activated_at` plus measured operator-action→engaged→last-cancel per drill, numeric ceiling [Open: Q-16-1] until the first drill (O-64). Compliance & Legal: no target denominated in PnL or return (X-10). IVA: each target needs method, evidence ID and first-measurable gate; two of four are unmeasurable until a paper environment and a drill exist. Confidence medium-high. **Decision request:** Adopt the four outcome targets with the time-to-halt ceiling left open until the first drill? | **Adopted (D-044)**; ceiling at first drill | 2026-09-08 |
| O-04 | B | Service framework choice (D-006 proposed FastAPI/Pydantic) | ARB | goals/decisions/O-04_decision_pack.md; ADR-009 | not yet convened | pending | **pending** | |
| O-05 | B | Model providers, hosting, data-processing terms | Security & Privacy Board + Model Risk Committee | goals/decisions/O-05_decision_pack.md | not yet convened | pending | **pending** | |
| O-13 | B | Time-series/snapshot storage cost model | ARB (Data Architect, Finance) | goals/decisions/O-13_decision_pack.md | not yet convened | pending | **pending** | |
| O-17 | B | Roadmap dates after capacity model | Product Council | goals/decisions/O-17_decision_pack.md | not yet convened | pending | **pending** | |
| O-22 | B | Registry signing key (dev HMAC → KMS asymmetric) | Security & Privacy Board | ADR-011, ADR-015; H-20 | not yet convened | pending | **pending** | |
| O-23 | B | Gating SAST/DAST/SCA and artefact signing | Security & Privacy Board + ARB | ci.yml advisory steps; release workflow | not yet convened | pending | **pending** | |
| O-07 | C | Numeric risk thresholds per asset class/jurisdiction | Trading Risk Committee | goals/decisions/O-07_decision_pack.md; docs/LIMIT_MATRIX.md | not yet convened | pending | **pending** | |
| O-12 | C | Data licensing for derived/redistributed data | Compliance & Legal Committee + ARB | goals/decisions/O-12_decision_pack.md | not yet convened | pending | **pending** | |
| O-19 | C | Deputies for emergency authority (second human for two-person controls) | Trading Risk Committee | goals/decisions/O-19_decision_pack.md | not yet convened | pending | **Deputy required before Gate C (D-047)**; person to be named by the owner | 2026-09-08 |
| O-06 | D | Evaluation dataset ownership/licensing | Model Risk Committee | goals/decisions/O-06_decision_pack.md | not yet convened | pending | **pending** | |
| O-09 | D | Deletion right vs record retention (legal hold) | Compliance & Legal Committee + Privacy Lead | goals/decisions/O-09_decision_pack.md | not yet convened | pending | **pending** | |
| O-10 | D | DPIA per launch jurisdiction | Security & Privacy Board (Privacy Lead) | goals/decisions/O-10_decision_pack.md | not yet convened | pending | **pending** | |
| O-35 | D | MCP tool registration after the MCP Security Agent review | Security & Privacy Board | docs/SESSIONS/REVIEW_C3_mcp_security_agent.md; docs/MCP_TOOL_CATALOG.md | not yet convened | pending | **pending** | |
| O-03 | E | Freshness/latency SLO targets after baselines | CAB (SRE Lead) | goals/decisions/O-03_decision_pack.md | not yet convened | pending | **pending** | |
| O-08 | E | Liquidation policy content | Trading Risk Committee | goals/decisions/O-08_decision_pack.md | not yet convened | pending | **pending** | |
| O-18 | E | RPO/RTO per cell | ARB (Cloud Architect) | goals/decisions/O-18_decision_pack.md | not yet convened | pending | **pending** | |
| O-14 | F | Launch locales | Product Council | goals/decisions/O-14_decision_pack.md | not yet convened | pending | **pending** | |
| O-15 | F | On-call model and support hours per market | CAB + Product Council | goals/decisions/O-15_decision_pack.md | not yet convened | pending | **pending** | |

## B. Human acts (MISSING_ACTIONS rows still open)

| Act | Gate | Action | Category | Prepares / executes | Council to consult | Decision (human Product Owner) | Status |
|---|---|---|---|---|---|---|---|
| H-01 | A | Appoint people to the 27 committee roles and name deputies | Governance | Executive sponsor | Product Council + CAB | **pending** | Open |
| H-02 | A | Ratify committee structure and decisions D-001..D-004 | Governance | Product Owner (agent) | Product Council + CAB | **Ratified (D-042)** | Closed 2026-09-08 |
| H-03 | A | Choose first jurisdiction cell | Strategy | Product Owner (agent); owner supplies the country | Product Council + Compliance & Legal Committee | **Hypothesis adopted (D-043)** | country fact open |
| H-05 | B | Approve budget and cloud spend | Finance | Executive Steering | Product Council (Finance & Vendor Lead) + ARB | **pending** | Open |
| H-06 | B | Sign model-provider terms and DPA | Procurement | Finance + Privacy | ARB / Trading Risk Committee (broker, data) + Security & Privacy Board (model provider) | **pending** | Open |
| H-22 | B | Convene the Committee to receive GATE_A/B/C_2026-09-07 and the re-validation report; record the human approver of record for each verdict | Governance | Committee chair | Product Council + CAB | **pending** | Open |
| H-24 | B | Confirm the `release` workflow evidence (run 34167194283 built and smoke-tested `rt365.exe`, SHA-256 recorded in AUDIT_EVIDENCE_INDEX #28), download `rt365-windows-x64`, verify the checksum on a Windows machine, sign the row; decide artefact signing (O-23) | Operations | SRE Lead + Security Architect | CAB + SRE Lead | **pending** | Open |
| H-07 | C | Sign broker agreements; obtain sandbox and production credentials into vault | Procurement | Finance + Broker-Connector | ARB / Trading Risk Committee (broker, data) + Security & Privacy Board (model provider) | **pending** | Open |
| H-08 | C | Sign market-data licences | Procurement | Finance + Legal | ARB / Trading Risk Committee (broker, data) + Security & Privacy Board (model provider) | **pending** | Open |
| H-09 | C | Fill numeric limits in LIMIT_MATRIX at all levels | Risk | Trading Risk Committee | Trading Risk Committee | **pending** | Open |
| H-20 | C | Provision KMS/HSM-held asymmetric key for order-command authorisation and registry signing, with rotation (replaces dev/sim shared HMAC and dev registry key) | Security | Security Architect + Cloud Architect | Security & Privacy Board + ARB | **pending** | Open |
| H-21 | C | Provision a WORM/replica anchor store for the audit `ChainHead`, written by a principal separate from the audit service | Operations | SRE Lead + Internal Audit | CAB + SRE Lead | **pending** | Open |
| H-04 | D | Engage external counsel; obtain legal opinion per cell | Legal | Legal Agent | Compliance & Legal Committee | **pending** | Open |
| H-10 | D | Contract external pen-test and red team | Procurement | Security Architect + Finance | ARB / Trading Risk Committee (broker, data) + Security & Privacy Board (model provider) | **pending** | Open |
| H-11 | D | Certify operators after training | Operations | Support & Training Lead | CAB + SRE Lead | **pending** | Open |
| H-12 | D | Compliance & Legal sign-off per cell (legal record) | Compliance | C&L Committee | Compliance & Legal Committee | **pending** | Open |
| H-19 | D/E/F | Perform DR, rollback and Kill Switch drills with named operators | Operations | SRE Lead | CAB + SRE Lead | **pending** | Open |
| H-13 | E | Approve capital envelope for bounded autonomy | Risk | Trading Risk Committee + Exec Steering | Trading Risk Committee | **pending** | Open |
| H-14 | E | Approve SLO targets from baselines | SRE | Executive Steering | CAB | **pending** | Open |
| H-15 | E | Approve liquidation policy | Risk | Trading Risk Committee | Trading Risk Committee | **pending** | Open |
| H-16 | F | Approve disclosures, terms and marketing copy | Legal/GTM | Legal Agent | Compliance & Legal Committee + Product Council | **pending** | Open |
| H-17 | F | Activate technical jurisdiction flag (second person) | Compliance | named second approver | Compliance & Legal Committee | **pending** | Open |
| H-18 | F | Launch decision | Governance | Executive Steering | Product Council + CAB | **pending** | Open |

## B2. Tooling decisions taken under D-040
| Item | Decision | Decided on |
|---|---|---|
| Lifecycle system | Meridian IT-PMO as portfolio and rhythm system, ledgers stay the truth, one-way sync (D-049, ADR-017); operate-for-real acts H-28 | 2026-09-08 |

## B3. Concerns raised to the human Product Owner (owner instruction 2026-09-08: keep communication open)
The delegate consults the request list in detail before every change — the PRD's 17 functional groups (FR-01..FR-17), the NFRs, SCOPE, the blueprint sections tagged [Source] and the owner's instructions recorded as D-039..D-051 — and records here anything that needs the human's eye. Build agents append their own "Concerns for the Product Owner" from their session packets. A concern is closed when the owner answers in session or the delegate records a decision citing it.

| # | Raised by | Concern | What the delegate did meanwhile | Owner's answer |
|---|---|---|---|---|
| PC-1 | delegate | "Compatible with all countries" was read as capability everywhere, enablement per cell (D-050). If you meant legal availability everywhere, that is impossible without a legal record per cell; say so and the roadmap changes to a multi-cell counsel programme | built the capability layer (world registry, calendars, validation) | pending |
| PC-2 | delegate | The first-cell hypothesis (D-043) cannot name a regulator until you give the country of your operating entity (Q-11-1) | recorded as hypothesis; Gate B condition GA-C1 | pending |
| PC-3 | delegate | Authorship evidence: every commit is authored by the AI delegate; GA-C3 asks for one owner-authored merge or commit (H-27). Merging the branch's pull request would close it | left open; no PR created without your ask | pending |
| PC-4 | delegate | The FX dimension (F-3) changes the risk engine's inputs: a missing FX rate must fail closed, which will HALT intents on foreign-currency instruments until a licensed FX feed exists (H-08). Confirm that is acceptable for paper | scheduled under Gate C | pending |
| PC-5 | delegate | Meridian is loaded from a demo book with public credentials; nothing real should go there until H-28 | documented; PMO guide warns | pending |
| PC-7 | delegate | The agent write-scope guard in agent frontmatter is not enforced by this harness (probe O-58). I moved it to the project settings hook; if the harness does not name the sub-agent in the hook payload, the guard stays advisory and author ≠ reviewer for agents is enforced only by review and CODEOWNERS. Decide whether that residual risk (R-46) is accepted for dev/sim | project-level hook installed and verified: the harness passes `agent_type` in the payload, the guard enforces it (O-58 closed); only the Bash bypass R-46 remains for you to accept or not | pending |
| PC-6 | delegate | Sections B–F are being executed by build agents in parallel worktrees; each will bring design choices the PRD leaves open (listed in their packets and appended below). Expect a batch per cycle | running E01 (tenant isolation), E06 (compliance fields), E07 (durable stores) | pending |

## C. Gates

| Gate | Environment it authorises | Entry | Council(s) | IVA recommendation | Decision (human Product Owner) |
|---|---|---|---|---|---|
| A — Discovery | (none; charter and hypothesis) | charter drafted | Product Council, Compliance & Legal Committee | REJECT (2026-09-07); **VETO recommended 2026-09-08** (COUNCIL_2026-09-08_gate_A_iva §7) on evidence grounds V-A1 hypothesis absent, V-A2 charter unapproved, V-A3 targets unset — all closable by Product Owner decisions | **Passed with conditions — D-048 (2026-09-08, commit 2edc87d)**; conditions GA-C1..GA-C8 tracked as O-66..O-72, H-25..H-27; next: Gate B |
| B — Architecture | development, simulation | Gate A passed (D-048) | ARB, Security & Privacy Board | ACCEPT WITH CONDITIONS (2026-09-07); conditions remediated in dev/sim, re-validation O-56 | **pending** |
| C — Paper readiness | shadow, paper | Gate B | Trading Risk Committee, CAB | REJECT (2026-09-07): V-C3 broker certification, V-C4 numeric limits | **pending** |
| D — Supervised pilot | supervised pilot | Gate C | Model Risk Committee, Security & Privacy Board, Compliance & Legal Committee, CAB | not convened | **pending** |
| E — Capped autonomy | capped autonomous pilot | Gate D | Trading Risk Committee, CAB | not convened | **pending** |
| F — Market release | controlled GA (one cell) | Gate E | all councils | not convened | **pending** |

## Next convening
The Gate A council (Product Council + Compliance & Legal Committee challenge + Independent Validation) was convened on 2026-09-08 for O-11, O-16, O-01 and O-02; its packets are in docs/SESSIONS/COUNCIL_2026-09-08_gate_A_*.md and the reconciled recommendations are in section A (the three packets agree on the direction; none relied on the others). The Product Owner's decisions on row 0, H-02, O-11/H-03, O-16, O-01 and O-02 allow Gate A to be re-convened (`gate-a` agent with `approve-product-council-chair` and `approve-compliance-legal-committee-chair`). Findings acted on already: dual-key role pair fixed (R-49, TC-CP-007); gate-prompt contradiction fixed (O-60); deputy gate set to C (O-63).

## How decisions are taken (D-040)
The Product Owner agent decides after convening the council and records D-nnn; the owner may reverse any decision by replying in session, for example: `confirm D-039`, `O-11: adopt option A; Q-11-1 = <country>; Q-11-2 = first party`, `O-16: adopt`, `O-01: adopt B`, `O-02: adopt A` / `O-02: defer to Gate D`, `H-02: ratify D-001..D-004`. The delegate records each in docs/DECISION_LOG.md with the alternatives and dissent, updates RAID and MISSING_ACTIONS, edits the owned artefacts through the owning role agents, and re-convenes the gate.
