# Global AI-MCP RoboTrader
## Expert Committee — Component & Process Deep Dive, and Master Orchestration Prompt

**Version:** 1.0 — 7 September 2026
**Basis:** *Global AI-MCP RoboTrader — Master Product, Architecture, Governance and Delivery Blueprint*, sections 00–17
**Status:** Committee working draft — for board review, not a release artefact

---

## 0. How to read this document

Every statement carries a provenance tag so that nothing is silently promoted from proposal to requirement:

| Tag | Meaning |
|---|---|
| **[Source: NN]** | Taken directly from blueprint section NN. Authoritative. |
| **[Committee]** | Elaboration produced by the committee. Requires validation by the accountable board before it becomes a requirement. |
| **[Open]** | Unresolved question, missing evidence or dependency. Tracked in Part 4 (RAID). |

Structure:

- **Part 1** — The committee: tiers, roster, decision rights, operating protocol
- **Part 2** — Component deep dives (blueprint sections 01–17 grouped into 12 components)
- **Part 3** — Cross-cutting process deep dives (6 processes)
- **Part 4** — Consolidated RAID and open questions
- **Part 5** — Final Master Orchestration Prompt (copy-paste ready)
- **Part 6** — Per-role committee session prompt template

---

## Part 1 — The Committee

### 1.1 Design principle: Three Lines of Defense

The blueprint's RACI rule is that *the builder is never the sole approver; risk, compliance and security controls require independent accountable owners* **[Source: 13]**. The committee is therefore organised on a Three Lines of Defense model **[Committee]**:

| Line | Function | Committee members |
|---|---|---|
| **1st line — Build & Run** | Own delivery, operate controls day to day | Product Director, Program Orchestrator, Trading Domain Lead, Quant Research Lead, Enterprise/Data/Cloud/Integration/Security Architects, Backend/Frontend/Mobile/Data/SRE/Broker-Connector Leads, Support, Training, GTM, Finance, Vendor |
| **2nd line — Oversight** | Set policy, approve limits, challenge 1st line | Chief Risk Agent, Model Risk Lead, Compliance & Legal Agents, MCP Security Agent, Privacy Lead, and the boards in §1.3 |
| **3rd line — Independent assurance** | Verify evidence, veto failed gates, no delivery ownership | Independent Validation Agent, Red-Team Lead, Pen-Test Lead (external where possible), Internal Audit function **[Committee — not named in blueprint]** |

Rule: a role never sits in two lines for the same control. A Security Architect who designs a control is 1st line for it; the Security & Privacy Board accepts it (2nd line); the Pen-Test Lead breaks it (3rd line).

### 1.2 Committee roster

| # | Role | Tier | Mandate **[Source: 00 unless noted]** | Primary artefacts owned **[Source: 15]** | Decision right | Segregation rule |
|---|---|---|---|---|---|---|
| 1 | Executive Steering Committee | Executive | Funding, risk appetite, market launch **[13]** | ROADMAP.md (approval), risk-appetite statement | Go/No-Go at Gate F | Cannot override Kill Switch or Independent Validation veto on evidence grounds |
| 2 | Product Director | Domain Lead | Scope, personas, value, pricing, roadmap | PRODUCT_CHARTER, PRD, PERSONAS, JOURNEYS, SCOPE, ROADMAP | Chairs Product Council | Cannot approve risk limits, compliance enablement or security acceptance |
| 3 | Program Orchestrator | Domain Lead | Plan, dependencies, RAID log, evidence | BACKLOG, RAID_LOG, DECISION_LOG, RACI, REQUIREMENTS_TRACEABILITY, RELEASE_CHECKLIST, AUDIT_EVIDENCE_INDEX | Convenes gates; recommends, never approves | Cannot self-certify evidence completeness |
| 4 | Trading Domain Lead | Domain Lead | Order lifecycles, market microstructure, asset-class rules | Order lifecycle spec, MARKET_LAUNCH_CHECKLIST (technical part), BROKER_CERTIFICATIONS | Signs off OMS/Execution semantics | Cannot approve own strategies |
| 5 | Quant Research Lead | Domain Lead | Hypotheses, datasets, backtests, robustness | STRATEGY_CARDS, backtest reports, DATA_DICTIONARY (research part) | Proposes strategies to Model Risk Committee | Cannot validate own backtests |
| 6 | Model Risk Lead | 2nd line | Model inventory, validation, drift, retirement | MODEL_CARDS, PROMPT_REGISTRY, model inventory, drift thresholds | Chairs Model Risk Committee | Independent of Quant Research |
| 7 | Chief Risk Agent | 2nd line | Limits, exposure, stress, drawdown, circuit breakers | RISK_POLICY, LIMIT_MATRIX, emergency/liquidation policy | Chairs Trading Risk Committee | No delivery ownership of risk engine code |
| 8 | Compliance Agent | 2nd line | Jurisdiction, licensing, suitability, disclosures, surveillance, retention | COMPLIANCE_MATRIX, JURISDICTION_MATRIX, surveillance patterns | Chairs Compliance & Legal Committee (with Legal) | Enables no jurisdiction without Legal co-signature |
| 9 | Legal Agent | 2nd line | Legal basis per market, terms, data licensing, marketing restrictions **[07]** | Legal terms, licensing register, disclosures | Co-signs jurisdiction enablement | — |
| 10 | Enterprise Architect | Architecture | Bounded contexts, standards, ADRs **[03]** | CONTEXT/CONTAINER/COMPONENT/SEQUENCE_DIAGRAMS, ADRs/, NFR | Chairs Architecture Review Board | ARB exceptions require Security Architect co-review |
| 11 | Data Architect | Architecture | Data lineage, time-series, snapshots, entitlements **[08]** | DATA_MODEL, DATA_DICTIONARY, DATA_FLOWS | Approves data contracts | — |
| 12 | Cloud Architect | Architecture | Cells, failure domains, IaC, scaling **[03]** | /infra, capacity model, DR_PLAN | Approves topology | — |
| 13 | Integration Architect | Architecture | Event bus, schema registry, adapters, idempotency **[03]** | API_OPENAPI.yaml, EVENT_CATALOG, contracts/ | Approves contracts | — |
| 14 | Security Architect | Architecture | Zero trust, threat model, secure SDLC **[06]** | THREAT_MODEL, SECURITY_PLAN, SBOM | Proposes to Security & Privacy Board | Cannot accept own residual risk |
| 15 | MCP Security Agent | 2nd line | Tool inventory, capability boundaries, authorisation, injection defence **[04]** | MCP_TOOL_CATALOG, /mcp/policies, tool registry signatures | Approves every MCP tool before registration | Cannot author MCP servers |
| 16 | Backend Lead | Engineering | Services, risk/compliance/OMS/execution implementation | /services/* | — | Cannot merge to /services/risk or /mcp/policies without 2nd-line reviewer |
| 17 | Broker-Connector Lead | Engineering | Adapter framework, sandbox certification, capability discovery **[02]** | /connectors/brokers, BROKER_CERTIFICATIONS | — | Certification reviewed by Trading Domain Lead |
| 18 | Frontend & Mobile Leads | Engineering | Web/PWA, admin, mobile, accessibility **[09]** | /apps/web, /apps/admin, design system | — | — |
| 19 | Data Engineering Lead | Engineering | Ingest, normalisation, snapshots, quality SLA **[08]** | /connectors/data-providers, /services/market-data | — | — |
| 20 | SRE Lead | Engineering | SLOs, telemetry, runbooks, on-call **[10]** | SLO_SLA, DASHBOARDS, ALERT_CATALOG, DEPLOYMENT_RUNBOOK, ROLLBACK_PLAN, INCIDENT_RESPONSE | Declares incidents; may activate Kill Switch | — |
| 21 | QA Lead | Assurance | Test strategy, evidence records **[11]** | TEST_STRATEGY, TEST_CASES/, UAT_PLAN | — | Does not write production code under test |
| 22 | Performance & Chaos Leads | Assurance | Load/spike/soak, failover, chaos **[11]** | PERFORMANCE_PLAN, CHAOS_PLAN | — | — |
| 23 | Accessibility Lead | Assurance | WCAG verification **[09]** | Accessibility test evidence | Blocks Gate F on unresolved critical a11y defects | — |
| 24 | Red-Team & Pen-Test Leads | 3rd line | Adversarial testing incl. AI/MCP **[06, 11]** | RED_TEAM_PLAN, pen-test reports | Findings feed Security & Privacy Board | External to delivery team |
| 25 | Privacy Lead | 2nd line | DPIA, residency, retention, subject rights **[06]** | PRIVACY_IMPACT | Co-signs Security & Privacy Board | — |
| 26 | Finance, Vendor, Support, Training, GTM Leads | Business | Cost, vendor assessments, support model, training, launch **[00]** | VENDOR_ASSESSMENTS/, SUPPORT_MODEL, TRAINING_PLAN, MARKET_LAUNCH_CHECKLIST (commercial part) | — | GTM cannot publish return claims **[00: never imply guaranteed returns]** |
| 27 | Independent Validation Agent | 3rd line | Evidence review; veto failed gates; no delivery ownership | Gate validation reports | **Veto** at every gate | Must have no ownership of any artefact under review |

### 1.3 Boards and decision rights **[Source: 13]**

| Board | Decides | Chair | Members (minimum) |
|---|---|---|---|
| Executive Steering Committee | Funding, risk appetite, market launch | Executive sponsor | Product Director, Chief Risk Agent, Compliance Agent, Finance |
| Product Council | Roadmap, customer outcomes | Product Director | Trading Domain Lead, GTM, Support, UX |
| Architecture Review Board | Technical standards, exceptions | Enterprise Architect | Data/Cloud/Integration/Security Architects, SRE Lead |
| Model Risk Committee | Strategy/model approval and retirement | Model Risk Lead | Quant Research Lead (presenting, non-voting), Chief Risk Agent, IVA |
| Trading Risk Committee | Limits, kill policies, liquidation policy | Chief Risk Agent | Trading Domain Lead, Compliance Agent, SRE Lead |
| Security & Privacy Board | Cyber/privacy acceptance | Security Architect (presenting) + independent chair | Privacy Lead, MCP Security Agent, Red-Team Lead |
| Compliance & Legal Committee | Jurisdiction enablement | Compliance Agent + Legal Agent | Trading Domain Lead, Product Director |
| Change Advisory & Release Board | Production authorisation | Program Orchestrator (convener) | All 2nd-line leads, SRE Lead, IVA |
| Independent Validation | Evidence review, veto | IVA | — |

### 1.4 Committee operating protocol **[Committee, derived from 00]**

1. **One session per component and per process** in Parts 2–3, run through the blueprint loop: Discover → Challenge → Compare → Design → Threat-model → Prototype → Test → Measure → Review → Approve/Reject → Document → Deploy safely → Observe → Improve **[Source: 00]**.
2. **Quorum for any control-bearing decision:** at least one 1st-line owner, one 2nd-line owner and the Independent Validation Agent.
3. **Session output packet (mandatory):** ADR(s), RTM rows (requirement → architecture → owner → control → test → evidence → gate), threat-model delta, test-plan delta with the positive/negative/abuse/recovery quartet for each critical control, evidence list, RAID entries, and a statement of assumptions, confidence and evidence provenance **[Source: 00]**.
4. **Challenge rule:** every design is challenged by a role from a different line before it is compared with alternatives. Minimum two alternatives compared.
5. **No self-certification** **[Source: 00]** — the author of an artefact cannot be its reviewer; the reviewer cannot be its approver.
6. **Silence is not consent:** regulatory permission, data licensing, broker functionality and market access are never assumed **[Source: 00]**; each is an [Open] item until evidenced.
7. **Precedence:** Kill Switch, trading halt, loss limits, restricted-instrument rules and human override supersede any committee decision, strategy or agent **[Source: 00]**.
8. **Escalation:** unresolved disagreement goes to the owning board in §1.3; unresolved between boards goes to Executive Steering, except evidence disputes, which are settled by Independent Validation.

---

## Part 2 — Component Deep Dives

Each component follows the same template: **Accountable / Consulted / Assurance → Purpose → Design decisions → Process → Control tests → Evidence → Open items.**

### C1 — Product Charter & Functional Scope (blueprint 01, 02)

**Accountable:** Product Director · **Consulted:** Trading Domain Lead, Compliance & Legal, Finance, GTM · **Assurance:** IVA

**Purpose [Source: 01]:** a modular trading operating system converting governed AI insights into controlled execution; ten personas; six operating modes (Observe, Backtest, Paper, Supervised, Bounded autonomous, Halted); custody, deposits/withdrawals, market making, copy trading, personalised advice, unlicensed solicitation, unsupported jurisdictions and manipulation-capable strategies are out of scope without separate approval.

**Design decisions [Committee]:**

1. **Mode state machine.** Modes are ordered by exposure: Observe → Backtest → Paper → Supervised → Bounded autonomous. Promotion is one step at a time and requires the entry criteria of the matching release gate (Part 3, P3). *Halted* is reachable from any mode by any authorised role; leaving *Halted* requires a two-person action and a documented reason.
2. **Persona × mode matrix.** Which persona may operate in which mode is a per-jurisdiction, per-customer-type policy, not a product default — because suitability/appropriateness rules differ by regulator **[Source: 07]**. The product ships with autonomy *disabled* for every persona until the Compliance & Legal Committee enables it per cell. **[Open: O-01]**
3. **Out-of-scope enforcement is technical, not editorial.** Each excluded capability (custody, deposits, market making, copy trading, advice) is represented by a capability flag that is absent from the codebase's permission model, so it cannot be enabled by configuration.
4. **Functional requirement decomposition.** The 17 requirement groups of section 02 are assigned IDs FR-01…FR-17 and mapped to epics E01–E15 **[Source: 14]**:

| FR | Requirement group [Source: 02] | Epic [Source: 14] | Gate first exercised [Source: 12] |
|---|---|---|---|
| FR-01 | Identity, tenant admin, MFA, RBAC/ABAC, privileged access | E01 | B |
| FR-02 | Broker/exchange onboarding, capability discovery, rotation, health | E03 | C |
| FR-03 | Licensed real-time/historical data with provenance | E02 | C |
| FR-04 | Watchlists, charts, depth, news, alerts, calendar | E02, E10 | C |
| FR-05 | Portfolio, cash, margin, positions, PnL, attribution | E04 | C |
| FR-06 | Strategy registry, versioning, approvals, rollback | E08 | C |
| FR-07 | Research sandboxes isolated from production credentials | E08, E13 | B |
| FR-08 | Backtest, replay, walk-forward, scenario, Monte Carlo | E08 | C |
| FR-09 | AI signal generation with explainability | E09 | D |
| FR-10 | Order management (market, limit, stop, stop-limit, trailing, conditional) | E07 | C |
| FR-11 | Pre-/at-/post-trade risk controls | E05 | C |
| FR-12 | Human approval queues, maker-checker | E05, E07 | D |
| FR-13 | Execution routing, idempotency, retry, fills, cancellation | E07 | C |
| FR-14 | Reconciliation and break management | E07, E11 | C |
| FR-15 | Compliance eligibility, restricted lists, surveillance, retention, reporting | E06, E11 | D |
| FR-16 | Notifications, incident centre, audit explorer, reporting, admin | E11, E12, E14 | C |
| FR-17 | Kill Switch at platform/tenant/account/strategy/asset/venue | E05 | C |

**Process:** Discovery workshop per persona → journey maps → PRD with Given/When/Then acceptance → RTM seeded → Product Council approval → Gate A.

**Control tests:** mode transitions (positive: step-up with criteria met; negative: skip a step; abuse: agent attempts mode change via tool call; recovery: return from Halted with two-person action). Out-of-scope flags: negative test that no configuration path enables them.

**Evidence:** PRODUCT_CHARTER.md, PRD.md, PERSONAS.md, JOURNEYS.md, SCOPE.md, REQUIREMENTS_TRACEABILITY.md, DECISION_LOG.md.

**Open:** O-01 persona/mode policy per jurisdiction; O-02 pricing model and billing scope (E14) not defined in blueprint.

---

### C2 — System Architecture (blueprint 03)

**Accountable:** Enterprise Architect · **Consulted:** Data/Cloud/Integration/Security Architects, Backend Lead, SRE Lead · **Assurance:** ARB, IVA

**Purpose [Source: 03]:** 20 bounded contexts; reference stack (Next.js/TypeScript PWA, FastAPI or typed service framework, PostgreSQL, time-series store, object storage, Redis, Kafka-compatible bus, schema registry, container orchestration, IaC, vault/HSM/KMS, WAF, SIEM, tracing, feature flags); core guarantees (idempotency, monotonic state, outbox/inbox, correlation IDs, clock sync, stale-data detection, exactly-once business effect, broker as final truth).

**Design decisions [Committee]:**

1. **Three planes.** The bounded contexts are grouped so that the authoritative pipeline **[Source: 00]** is enforced by topology, not by convention:

| Plane | Contexts | May call |
|---|---|---|
| Analytics plane | Market Data, Instrument Master, Strategy, AI/MCP, Backtest | Control plane only, via *Trade Intent* |
| Control plane | Risk, Compliance, Approval, Audit | Execution plane, via *Authorised Order Command* |
| Execution plane | OMS, Execution Gateway, Broker Adapters, Reconciliation, Portfolio | Brokers; publishes events back |

   Network policy denies any route from the Analytics plane to the Execution plane. This is the technical form of *only the deterministic Execution Gateway may submit a real order* **[Source: 00]**.
2. **Single active executor per account.** Active/standby ownership **[Source: 03]** is implemented with a leased lock carrying a fencing token; every broker submission includes the token; a stale token is rejected by the gateway. This closes the duplicate-order threat **[Source: 06]** during failover.
3. **Idempotency key** = deterministic hash of (intent ID, account, policy version). Broker client-order-ID is derived from it so that at-least-once delivery cannot create two live orders.
4. **Bitemporal time.** Every event carries *market timestamp*, *ingest timestamp* and *decision timestamp*; freshness budgets are per instrument class and are policy, not code. **[Open: O-03 numeric freshness thresholds need measured baselines — Source: 10]**
5. **Cells.** One regional cell per venue cluster; a cell is the failure domain; cross-cell traffic is limited to audit replication and portfolio roll-up.
6. **Backpressure.** Analytics plane is shed first under load; Control and Execution planes are never shed — they fail closed instead (see C4).

**ADR candidates:** ADR-001 three-plane topology; ADR-002 executor lease & fencing; ADR-003 idempotency key derivation; ADR-004 time-series store selection; ADR-005 event bus & schema registry; ADR-006 service mesh justification **[Source: 03: "where justified"]**; ADR-007 cell topology.

**Control tests:** duplicate-delivery replay of an authorised order command (expect one broker order); executor failover with an in-flight order; clock-skew injection beyond budget (expect stale-data rejection); attempted direct call from Strategy service to Broker Adapter (expect network deny + alert).

**Evidence:** CONTEXT_DIAGRAM.md, CONTAINER_DIAGRAM.md, COMPONENT_DIAGRAMS.md, SEQUENCE_DIAGRAMS.md, DATA_FLOWS.md, ADRs/, API_OPENAPI.yaml, EVENT_CATALOG.md, capacity model (Gate B).

**Open:** O-03 freshness thresholds; O-04 choice between FastAPI and alternative typed framework left open in blueprint.

---

### C3 — MCP & AI Governance (blueprint 04)

**Accountable:** MCP Security Agent (controls), Model Risk Lead (models) · **Consulted:** Quant Research Lead, Security Architect, Backend Lead · **Assurance:** Model Risk Committee, Security & Privacy Board, Red-Team Lead

**Purpose [Source: 04]:** six allowed capabilities (read masked market snapshots, read masked account state, calculate approved indicators, run approved simulations, retrieve strategy documentation, submit a trade intent); forbidden capabilities (direct broker calls, arbitrary code execution, shell, secret retrieval, risk-policy mutation, audit deletion, unrestricted web access, dynamic installation in production); controls list; model governance list.

**Design decisions [Committee]:**

1. **Tool catalogue.** Each allowed capability becomes a signed tool entry with: scope, data-masking class, rate quota, timeout, payload limit, read/write class, owning team and approval record. Only `submit_trade_intent` is write-class, and it writes to the Control-plane intake queue — never to a broker.
2. **Forbidden = structurally impossible.** MCP servers run with no broker network route, no mounted secrets, read-only filesystem, no shell binary, and an egress allowlist limited to Analytics-plane services. Prohibition is enforced by the runtime, then confirmed by policy.
3. **Identity.** Each agent instance receives a short-lived workload identity; every tool call is signed and carries the agent, model version and prompt version; the registry itself is signed and any unsigned server is refused at startup.
4. **Injection defence.** All inputs carry a provenance label (licensed feed / news adapter / user text / internal doc). Untrusted text is delimited and never interpreted as instruction; tool outputs are schema-validated before re-entering the context; canary strings detect exfiltration attempts.
5. **Model lifecycle.** Register → Validate (evaluation datasets, hallucination and adversarial tests) → Shadow as challenger → Model Risk Committee approval → Monitor drift thresholds → Champion/challenger review → Retire/rollback **[Source: 04]**. No model is promoted on backtest metrics alone.
6. **Explainability contract.** Every signal carries thesis code, evidence references and confidence **[Source: 00]**; a signal without evidence references is schema-invalid.

**Process:** tool proposal → MCP Security Agent review → threat-model delta → sandbox test → registry signature → allowlist per tenant/account/strategy → periodic re-attestation → emergency revocation drill.

**Control tests:** prompt-injection corpus (positive: benign passes; negative: injected instruction ignored; abuse: attempt to invoke a non-allowlisted tool; recovery: revoke tool mid-session and confirm denial); oversized payload; hallucinated instrument symbol rejected at schema validation; audit-deletion attempt via any path.

**Evidence:** MCP_TOOL_CATALOG.md, PROMPT_REGISTRY.md, MODEL_CARDS/, /mcp/policies, tool-registry signatures, red-team report.

**Open:** O-05 model providers, hosting (API vs self-hosted) and data-processing terms not specified; O-06 ownership and licensing of evaluation datasets.

---

### C4 — Deterministic Risk Engine (blueprint 05)

**Accountable:** Chief Risk Agent (policy), Backend Lead (implementation) · **Consulted:** Trading Domain Lead, SRE Lead · **Assurance:** Trading Risk Committee, IVA (determinism validation)

**Purpose [Source: 05]:** pre-trade controls (trading status through correlated-risk limits), runtime controls (loss limits through venue health), four outcomes (APPROVED, REJECTED, REQUIRES_HUMAN_APPROVAL, HALTED) with policy version, reason codes, evaluated values, thresholds and timestamp; emergency policy where closing positions is *not* assumed universally safest.

**Design decisions [Committee]:**

1. **Determinism contract.** `decide(intent, account_snapshot, market_snapshot, policy_version) → decision` is a pure function with no I/O, no randomness and no model call. Property-based tests assert identical output for identical input across runs and across replicas. Any non-determinism is a Gate C blocker.
2. **Fail closed.** If the risk engine, its policy store or its account snapshot is unavailable, the outcome is HALTED, never APPROVED by default. Blueprint runbook *risk engine unavailable* **[Source: 10]** links here.
3. **Limit hierarchy.** Platform > tenant > account > strategy > instrument; effective limit = minimum across levels. Limits are changed only through maker-checker with a cooling period; no agent, MCP server or strategy has a write path **[Source: 00]**.
4. **Evaluation order and completeness.** Checks run in fail-fast order (status/authorisation → eligibility → data freshness → instrument/order validity → sizing/exposure → price collar/liquidity/volatility → duplicate/rate → protective controls), but all inexpensive checks are still evaluated so that the decision record lists every failing reason, not only the first.
5. **Runtime monitors** publish HALT events with reason codes; they are consumed by the Kill Switch service (P4) and never bypass the engine.
6. **Emergency policy is per account** and one of CANCEL_ONLY (default), CANCEL_AND_REDUCE, CANCEL_AND_FLATTEN. Reduction/flatten requires a separately approved liquidation policy **[Source: 05]**.

**Decision record schema (minimum):** decision_id, intent_id, outcome, policy_version, reason_codes[], evaluated[{check, value, threshold, result}], account_snapshot_id, market_snapshot_id, decided_at, engine_build_hash.

**Control matrix (each pre-trade check):**

| Check family [Source: 05] | Positive | Negative | Abuse | Recovery |
|---|---|---|---|---|
| Authorisation / trading status | Authorised account passes | Suspended account rejected | Forged account ID in intent | Re-enable after halt with two-person action |
| Data freshness | Fresh snapshot passes | Stale beyond budget → REJECTED | Backdated market timestamp | Feed restored → next intent passes |
| Sizing / exposure / leverage | Within all levels | Exceeds any level → REJECTED with all reasons | Split orders to evade cap (duplicate/aggregate detection) | Limit restored after breach |
| Price collar / fat-finger | Inside collar | Outside → REJECTED | Limit price manipulated after validation (hash mismatch) | — |
| Duplicate / rate / open-order count | Unique intent | Duplicate → REJECTED | Replay of signed intent | — |
| Protective controls (stop-loss policy) | Present | Missing → REQUIRES_HUMAN_APPROVAL or REJECTED per policy | — | — |

**Evidence:** RISK_POLICY.md, LIMIT_MATRIX.md, determinism test reports, decision records in immutable audit, Gate C sign-off.

**Open:** O-07 numeric thresholds per asset class and jurisdiction; O-08 liquidation policy content.

---

### C5 — Security, Privacy & Threat Model (blueprint 06)

**Accountable:** Security Architect (design), Privacy Lead (privacy) · **Consulted:** MCP Security Agent, Cloud Architect, SRE Lead · **Assurance:** Security & Privacy Board, Red-Team/Pen-Test Leads

**Purpose [Source: 06]:** named threats (prompt/tool injection through data exfiltration); required controls (zero trust through independent penetration testing); privacy obligations (purpose limitation through privacy-safe telemetry).

**Design decisions [Committee]:**

1. **Trust boundaries** for STRIDE-style analysis: user ↔ BFF; BFF ↔ services; Analytics ↔ Control plane; Control ↔ Execution plane; Execution ↔ broker; MCP server ↔ tool; data provider ↔ ingest; CI ↔ production.
2. **Threat → control → test → owner table** (excerpt; full table in THREAT_MODEL.md):

| Threat [Source: 06] | Primary control | Test | Owner |
|---|---|---|---|
| Prompt/tool injection, excessive agency | C3 §4 provenance labelling, allowlisted tools, no broker route | Injection corpus, tool escalation | MCP Security Agent |
| Credential theft | Vault/HSM, workload identity, rotation, no secrets in agent context | Secret-scanning in CI, log redaction test | Security Architect |
| Duplicate orders, replay, race | C2 §2–3 fencing token, idempotency key | Duplicate-delivery replay | Integration Architect |
| Poisoned market data | Source contracts, outlier policy, freshness, cross-source check | Injected outlier tick | Data Architect |
| Insider misuse | Separation of duties, PIM, maker-checker, immutable logs | Privileged action without second approver | Security & Privacy Board |
| Audit tampering | WORM audit store, hash chaining | Modify-attempt detection | SRE Lead |
| Tenant escape | Tenant-partitioned streams and storage, ABAC | Cross-tenant read attempt | Backend Lead |
| Supply chain | Signed artefacts, SBOM, SCA gate | Unsigned image deploy attempt | Cloud Architect |

3. **Privacy vs retention conflict.** Deletion requests can collide with regulatory record-retention duties **[Source: 07]**; the design uses legal-hold flags so deletion workflows suppress rather than destroy where a hold applies, with the decision logged. Legal Agent confirms per jurisdiction. **[Open: O-09]**
4. **Telemetry redaction** is applied at emission, not at storage.

**Control tests:** every row above in the quartet form; annual external pen-test; red-team exercise covering AI/MCP paths before Gate D **[Source: 12]**.

**Evidence:** THREAT_MODEL.md, SECURITY_PLAN.md, PRIVACY_IMPACT.md, SBOM.md, pen-test and red-team reports, DPIA records.

**Open:** O-09 legal-hold rules per jurisdiction; O-10 DPIA required per launch jurisdiction.

---

### C6 — Compliance, Market Access & Market Readiness (blueprint 07, 17)

**Accountable:** Compliance Agent, Legal Agent · **Consulted:** Trading Domain Lead, Broker-Connector Lead, Data Engineering Lead, Support · **Assurance:** Compliance & Legal Committee, IVA

**Purpose [Source: 07, 17]:** launch matrix per country × customer type × broker × venue × asset class × feature, recording regulator, authorisation, suitability, disclosures, best execution, algorithmic controls, reporting, surveillance, retention, tax, data licensing, marketing; *“worldwide” never means legal availability*; 18-item market-readiness checklist.

**Design decisions [Committee]:**

1. **Dual key to enable a market.** A jurisdiction/venue cell is live only when (a) a signed legal/compliance record exists in COMPLIANCE_MATRIX and (b) the matching technical policy flag is activated by a second person. Either alone is insufficient **[Source: 07]**.
2. **Eligibility engine** is deterministic like C4: inputs are customer classification, product permissions, restricted lists, jurisdiction feature flags and instrument attributes; output is ELIGIBLE / INELIGIBLE with reason codes and policy version.
3. **Market-readiness checklist becomes tests.** Each of the 18 items in section 17 maps to a broker-sandbox or instrument-master test (e.g., tick/lot size rounding, session calendar and holidays, supported order types, short-sale rules, settlement, corporate-action handling). A venue with any failing test remains disabled.
4. **Surveillance pattern library** (spoofing, layering, wash trading, momentum ignition, marking the close) runs post-trade; in addition, strategies whose behaviour could produce such patterns are rejected at strategy registration, implementing the out-of-scope rule **[Source: 01]**.
5. **Records** are retained in a WORM store with retention schedules per jurisdiction.

**Process:** jurisdiction hypothesis (Gate A) → legal analysis → broker capability certification → checklist tests → disclosures and terms → Compliance & Legal Committee sign-off → flag activation → post-launch review.

**Control tests:** ineligible customer/instrument combination rejected; attempt to trade on a venue with legal record but no flag (and vice-versa) rejected; surveillance detection on synthetic pattern; retention deletion blocked during hold.

**Evidence:** COMPLIANCE_MATRIX.md, JURISDICTION_MATRIX.md, MARKET_LAUNCH_CHECKLIST.md, BROKER_CERTIFICATIONS/, surveillance reports.

**Open:** O-11 no launch jurisdiction is proposed in the blueprint — the first-market hypothesis must be set at Gate A; O-12 data-licensing terms for derived/redistributed data.

---

### C7 — Data & Quant Validation (blueprint 08)

**Accountable:** Quant Research Lead (research), Data Architect (data) · **Consulted:** Data Engineering Lead, Model Risk Lead · **Assurance:** Model Risk Committee, IVA (independent reproduction)

**Purpose [Source: 08]:** data controls (source contracts through reproducible snapshots); backtest acceptance (realistic costs, train/validation/test separation, out-of-sample, walk-forward, parameter stability, benchmark, stress periods, independent reproduction); minimum metrics; *metrics do not prove future profitability*.

**Design decisions [Committee]:**

1. **Bitemporal data store.** Each record carries *as-of time* and *knowledge time* so that any backtest can only see what was knowable at decision time — the structural defence against look-ahead bias and leakage **[Source: 00]**.
2. **Point-in-time universe.** Instrument universes are materialised as of each date, including delisted names, to remove survivorship bias.
3. **Single code path.** The backtest engine executes the same order, risk and eligibility code as production against a simulated broker. Divergence between backtest and paper behaviour is itself a defect.
4. **Pre-registration.** A hypothesis, universe, period split and success criteria are registered before a backtest runs; unregistered results are exploratory only and cannot be presented to the Model Risk Committee.
5. **Cost model** includes commissions, spread, slippage, latency, financing, borrow availability, partial fills and delistings **[Source: 08]**, with sensitivity runs at ×1.5 and ×2 cost assumptions.
6. **Independent reproduction** by the IVA on separate infrastructure and data snapshot is a Gate D condition **[Source: 12]**.

**Strategy card (minimum):** strategy ID/version, hypothesis, universe, data snapshot ID, cost model version, split scheme, walk-forward windows, metric set **[Source: 08]**, parameter stability evidence, regime breakdown, capacity estimate, known failure modes, reviewer signatures.

**Control tests:** leakage detector (future field referenced → fail); replay determinism (same snapshot → identical fills); cost sensitivity; survivorship check (delisted names present).

**Evidence:** DATA_MODEL.md, DATA_DICTIONARY.md, STRATEGY_CARDS/, backtest reports, IVA reproduction reports.

**Open:** O-12 data licensing; O-13 time-series store and snapshot storage cost model.

---

### C8 — UX & Ergonomics (blueprint 09)

**Accountable:** Frontend Lead · **Consulted:** Product Director, Trading Domain Lead, Support Lead · **Assurance:** Accessibility Lead, usability testing with representative users

**Purpose [Source: 09]:** dashboard with risk state more prominent than profit; progressive disclosure; plain-language rejection reasons; preview-before-submit; irreversible-action confirmation; accessible colours; keyboard navigation; localisation; role-specific workspaces; WCAG-aligned verification.

**Design decisions [Committee]:**

1. **Information hierarchy:** global status and Kill Switch state → capital at risk and drawdown → exposure → positions/orders → PnL → alerts → data freshness. PnL is never above risk state on any screen.
2. **Reason-code dictionary.** Every risk/eligibility reason code (C4, C6) has a plain-language, localised explanation and a “what you can do” line.
3. **Irreversible actions** (Kill Switch, autonomy enable, limit change, jurisdiction flag) use typed confirmation plus second approver where maker-checker applies.
4. **Role workspaces:** trader (orders, approvals), risk officer (limits, breaches, halts), compliance analyst (eligibility, surveillance, retention), operations (reconciliation breaks, incidents), auditor (audit explorer, read-only), tenant admin, support engineer.
5. **Accessibility target:** WCAG 2.2 AA, verified by the Accessibility Lead before Gate F **[Committee; blueprint says “WCAG-aligned” without version]**.

**Control tests:** keyboard-only order preview/submit/cancel; screen-reader pass on dashboard and approval queue; colour-contrast automated scan; usability sessions per persona with task success and error-rate recorded.

**Evidence:** design system, usability reports, accessibility evidence, localisation coverage.

**Open:** O-14 supported locales at launch.

---

### C9 — Observability & SRE (blueprint 10)

**Accountable:** SRE Lead · **Consulted:** Cloud Architect, Backend Lead, Chief Risk Agent · **Assurance:** ARB, IVA

**Purpose [Source: 10]:** SLO candidates (availability, data freshness, signal latency, risk-decision latency, order acknowledgement, event lag, reconciliation completeness, alert delivery); telemetry with shared correlation IDs and redaction; ten runbooks.

**Design decisions [Committee]:**

1. **SLI definitions** are fixed now; **targets are deferred** until measured baselines and business approval exist **[Source: 10]**. Example SLI: risk-decision latency = time from intent enqueue to decision record write, p99, per cell.
2. **Correlation.** One correlation ID from market snapshot → signal → intent → decision → order command → broker ack → fill → reconciliation → audit entry.
3. **Error-budget policy with safety semantics.** Breach of the risk-decision-latency or data-freshness SLO automatically suspends *Bounded autonomous* mode (drops to Supervised) until an operator restores it; this is a runtime control feeding P4.
4. **Runbook index** **[Source: 10]:** data stale, broker disconnected, duplicate order, risk engine unavailable, reconciliation break, unexpected exposure, model drift, credential compromise, regional failure, Kill Switch activation — each with trigger, first action, escalation path and evidence to capture.

**Control tests:** synthetic intent probe end-to-end each minute; alert-delivery test to every channel; trace completeness check (missing span → defect).

**Evidence:** SLO_SLA.md, DASHBOARDS.md, ALERT_CATALOG.md, runbooks, baseline measurement report (Gate E).

**Open:** O-03 baselines; O-15 on-call model and support hours per market **[Source: 17]**.

---

### C10 — Test Master Plan (blueprint 11)

**Accountable:** QA Lead · **Consulted:** Performance, Chaos, Red-Team, Accessibility Leads, all engineering leads · **Assurance:** IVA (evidence review)

**Purpose [Source: 11]:** test families (unit, property-based, contract, integration, e2e; replay and broker sandbox; load/spike/soak/latency/failover/capacity; chaos; security; model; compliance/accessibility/localisation/DR/operational readiness); evidence record fields.

**Design decisions [Committee]:**

1. **Control quartet is mandatory** for every critical control: positive, negative, abuse, recovery **[Source: 00]**. A control without all four is not “tested”.
2. **Environment ladder** mirrors promotion: development → simulation → shadow → paper → supervised pilot → capped autonomous pilot → controlled GA **[Source: 00]**. Tests are tagged with the lowest environment in which they must pass.
3. **Evidence record** **[Source: 11]:** requirement ID, environment, data version, expected result, actual result, evidence link, owner, reviewer — reviewer ≠ owner.
4. **Broker sandbox certification checklist** per adapter: authentication and rotation, capability discovery, each supported order type, partial fill, cancel/replace, reject handling, reconnection, statement download, reconciliation match.
5. **Model test suite** **[Source: 11]:** hallucination, malicious context, instability across seeds, drift, unsafe tool selection — run on every prompt or model version change.

**Evidence:** TEST_STRATEGY.md, TEST_CASES/, PERFORMANCE_PLAN.md, CHAOS_PLAN.md, RED_TEAM_PLAN.md, UAT_PLAN.md, evidence index.

---

### C11 — Release Gates & Governance (blueprint 12, 13)

**Accountable:** Program Orchestrator (convener) · **Approvers:** boards per §1.3 · **Veto:** IVA

| Gate [Source: 12] | Entry criteria | Exit evidence | Approving bodies | IVA veto grounds |
|---|---|---|---|---|
| A — Discovery | Charter drafted | Approved charter, personas, jurisdiction hypothesis, measurable outcomes | Product Council, Executive Steering | Missing jurisdiction hypothesis |
| B — Architecture | Gate A passed | Threat model, data flows, ADRs, capacity model, control ownership | ARB, Security & Privacy Board | Any critical control without named 2nd-line owner |
| C — Paper readiness | Gate B passed | Broker sandbox, deterministic risk tests, reconciliation, audit and support workflows pass | Trading Risk Committee, CAB | Non-deterministic risk decision; open reconciliation breaks |
| D — Supervised pilot | Gate C passed | Independent quant validation, security assessment, compliance sign-off, trained operators, rollback drill | Model Risk, Security & Privacy, Compliance & Legal, CAB | Backtest not independently reproduced |
| E — Capped autonomy | Gate D passed | Capital envelope, runtime monitoring, automatic halts, model thresholds, incident command | Trading Risk, Executive Steering, CAB | Halt tests not evidenced in paper/pilot |
| F — Market release | Gate E passed | No unresolved critical; highs resolved or risk-accepted by authorised owner; SLO, DR, accessibility, support, disclosures, legal terms, release dossier | All boards, Executive Steering | Any critical finding; incomplete dossier |

**Emergency authority [Committee]:** any of SRE Lead, Chief Risk Agent, Compliance Agent, Trading Domain Lead or a named deputy may *activate* the Kill Switch unilaterally; *deactivation* requires two people from different lines and a logged reason **[Source: 13: emergency authority and deputies must be documented]**.

**Evidence:** RACI.md, DECISION_LOG.md, gate validation reports, release dossier.

---

### C12 — Backlog, Artefacts & Repository (blueprint 14, 15, 16)

**Accountable:** Program Orchestrator · **Consulted:** all leads

1. **Epic ownership and first gate:**

| Epic [Source: 14] | Accountable lead | 2nd-line reviewer | First gate |
|---|---|---|---|
| E01 Foundation & identity | Backend Lead | Security Architect | B |
| E02 Market data & instrument master | Data Engineering Lead | Data Architect | C |
| E03 Broker adapter framework | Broker-Connector Lead | Trading Domain Lead | C |
| E04 Portfolio & accounting | Backend Lead | Chief Risk Agent | C |
| E05 Deterministic risk engine | Backend Lead | Chief Risk Agent | C |
| E06 Compliance & eligibility | Backend Lead | Compliance Agent | D |
| E07 OMS & execution gateway | Backend Lead | Trading Domain Lead | C |
| E08 Strategy & backtesting | Quant Research Lead | Model Risk Lead | C |
| E09 MCP/AI governance | Backend Lead | MCP Security Agent | D |
| E10 Dashboard & mobile | Frontend Lead | Accessibility Lead | C |
| E11 Audit, surveillance, reporting | Backend Lead | Compliance Agent | D |
| E12 Observability & SRE | SRE Lead | ARB | C |
| E13 Security & privacy | Security Architect | Security & Privacy Board | B |
| E14 Billing, support, admin | Backend Lead | Finance / Support | F |
| E15 Regulatory & market launch | Compliance Agent | Legal Agent | F |

2. **Story template [Source: 14]:** business value, scope, assumptions, API/event impact, security/privacy impact, observability, migration, rollback, Given/When/Then acceptance scenarios — plus RTM link and control-quartet reference **[Committee]**.
3. **Artefact catalogue [Source: 15]:** every file has an owner from §1.2 and a reviewer from a different line; ownership is recorded in RACI.md.
4. **Protected repository paths [Committee]:** `/services/risk`, `/services/compliance`, `/services/execution`, `/mcp/policies`, `/security` and `/contracts/*` require CODEOWNERS approval from the relevant 2nd-line role before merge **[Source: 16 structure]**.

---

## Part 3 — Cross-Cutting Process Deep Dives

### P1 — Trade intent lifecycle **[Source: 00 pipeline; Committee state machine]**

```
CREATED → SCHEMA_VALIDATED → ELIGIBLE → RISK_DECIDED
   RISK_DECIDED = APPROVED → AUTHORISED
   RISK_DECIDED = REQUIRES_HUMAN_APPROVAL → PENDING_APPROVAL → AUTHORISED | DECLINED
   RISK_DECIDED = REJECTED → REJECTED (terminal)
   RISK_DECIDED = HALTED → HALTED (terminal)
AUTHORISED → SUBMITTED → ACKNOWLEDGED → {PARTIALLY_FILLED → FILLED | CANCELLED | BROKER_REJECTED}
→ RECONCILED → ARCHIVED
Any state → EXPIRED when intent.expiry passes before SUBMITTED.
```

Rules: transitions are monotonic **[Source: 03]**; each transition writes an immutable audit event with the correlation ID; the intent schema is the strict one in section 00 (strategy ID/version, model ID/version, account, venue, instrument, side, order type, quantity/notional, limit/stop, time-in-force, thesis code, confidence, market timestamp, data provenance, expiry); unknown fields are rejected where appropriate; an intent is never mutated after SCHEMA_VALIDATED — any change is a new intent.

**Owners:** Trading Domain Lead (semantics), Backend Lead (implementation), Chief Risk Agent (decision), Compliance Agent (eligibility), IVA (evidence).

### P2 — Strategy and model lifecycle **[Source: 04, 08; Committee]**

Idea → pre-registered hypothesis → data snapshot pinned → backtest (single code path) → Quant self-review → Model Risk validation (leakage, stability, cost sensitivity) → IVA independent reproduction → Model Risk Committee approval as *challenger* → shadow run (signals logged, no intents) → paper (intents, virtual capital) → supervised pilot → capped autonomous with capital envelope → champion/challenger review on drift thresholds → retirement or rollback. Retirement is a committee decision, recorded in the model inventory.

### P3 — Change and promotion **[Source: 00, 12; Committee]**

Every change (code, policy, limit, tool, model, prompt, jurisdiction flag) has: RTM link, threat-model delta, control-quartet status, rollback plan, observability plan. Promotion path: development → simulation → shadow → paper → supervised pilot → capped autonomous pilot → controlled GA. Automatic rollback or halt on failure of guardrails, integrity checks, reconciliation or observability **[Source: 00]**. Policy and limit changes use maker-checker with cooling period (C4). Production authorisation is by the Change Advisory & Release Board; the builder is never the sole approver **[Source: 13]**.

### P4 — Kill Switch and emergency **[Source: 02, 05, 10; Committee]**

Levels: platform, tenant, account, strategy, asset, venue **[Source: 02]**. Triggers: manual (any authorised role, C11), runtime monitors (C4), SLO safety semantics (C9), reconciliation break (P6), credential compromise runbook (C9). Actions on activation: block new risk; cancel open orders; apply the account's emergency policy (CANCEL_ONLY default); revoke agent tool tokens; preserve evidence snapshot; notify operators and, where required, customers **[Source: 05]**. Deactivation: two-person rule, different lines, logged reason, post-incident review before re-enabling autonomy. Drill: quarterly, evidenced for Gate E.

### P5 — Market enablement **[Source: 07, 17]**

Hypothesis (Gate A) → legal basis and regulator mapping → broker capability certification (C10 §4) → instrument-master validation (identifiers, sessions/holidays, currencies, tick/lot, order types, settlement, short-sale, margin, taxes/fees, corporate actions) → data entitlements → reporting and surveillance readiness → support hours and incident contacts → customer disclosures → Compliance & Legal Committee sign-off → dual-key activation (C6 §1) → post-launch review at 30 and 90 days **[Source: 15 POST_LAUNCH_REVIEW.md]**.

### P6 — Reconciliation break and incident **[Source: 02, 03, 10]**

Broker statement is final external truth **[Source: 03]**. Cycle: intraday position/order reconciliation and end-of-day statement reconciliation → break detected → automatic classification (timing, missing fill, duplicate, price, quantity) → account moves to Supervised (or Halted per severity) → break ticket with correlation IDs → resolution with two-person confirmation → audit record → trend review at Trading Risk Committee. An unresolved break blocks Gate C for that account/venue.

---

## Part 4 — Consolidated RAID and Open Questions

| ID | Type | Item | Owner | Needed by |
|---|---|---|---|---|
| O-01 | Assumption | Persona × mode policy per jurisdiction | Compliance & Legal Committee | Gate A |
| O-02 | Gap | Pricing and billing scope (E14) not defined | Product Director, Finance | Gate A |
| O-03 | Dependency | Numeric freshness/latency thresholds need measured baselines | SRE Lead | Gate E |
| O-04 | Decision | Service framework choice (FastAPI vs alternative) | ARB | Gate B |
| O-05 | Gap | Model providers, hosting and data-processing terms | Model Risk Lead, Privacy Lead | Gate B |
| O-06 | Gap | Evaluation dataset ownership and licensing | Model Risk Lead | Gate D |
| O-07 | Gap | Numeric risk thresholds per asset class/jurisdiction | Trading Risk Committee | Gate C |
| O-08 | Gap | Liquidation policy content | Trading Risk Committee | Gate E |
| O-09 | Risk | Deletion right vs record retention (legal hold rules) | Legal Agent, Privacy Lead | Gate D |
| O-10 | Dependency | DPIA per launch jurisdiction | Privacy Lead | Gate D |
| O-11 | Gap | First launch jurisdiction hypothesis absent from blueprint | Product Director, Compliance Agent | Gate A |
| O-12 | Dependency | Data licensing for derived/redistributed data | Legal Agent, Data Architect | Gate C |
| O-13 | Decision | Time-series and snapshot storage cost model | Data Architect, Finance | Gate B |
| O-14 | Decision | Launch locales | Product Director | Gate F |
| O-15 | Gap | On-call model and support hours per market | SRE Lead, Support Lead | Gate F |
| R-01 | Risk | Any non-deterministic path in risk/eligibility decision | Chief Risk Agent | Continuous |
| R-02 | Risk | Duplicate orders during executor failover | Integration Architect | Gate C |
| R-03 | Risk | Look-ahead/leakage in backtests inflating expected performance | Model Risk Lead | Gate D |
| R-04 | Risk | Marketing or UI language implying guaranteed returns | GTM Lead, Compliance Agent | Gate F |

---

## Part 5 — Final Master Orchestration Prompt

Copy the block below as the system/goal prompt for the Master Delivery Orchestrator. It supersedes `00_GOAL_ORCHESTRATOR.md` by embedding the committee protocol; it does not alter any authority rule of the blueprint.

```text
# ROLE
You are the Master Delivery Orchestrator for Global AI-MCP RoboTrader. You coordinate a
committee of independent specialist agents to turn the approved blueprint (sections 00–17)
into a tested, evidenced, market-ready automated-trading product. You recommend; you do
not approve. You never self-certify.

# PRODUCT POSTURE (non-negotiable, from blueprint 00)
- The platform generates and executes orders only inside a deterministic, independently
  enforced control envelope. Profit is an objective, never a promise. Capital preservation,
  lawful operation, security, market integrity, traceability and human override outrank
  any model output.
- AI and MCP servers may research, analyse, simulate, rank strategies, generate signals and
  submit typed trade intents. They may never hold unrestricted broker credentials, modify
  risk limits, approve their own changes, suppress audit records, disable monitoring or
  bypass controls.
- Only the deterministic Execution Gateway submits real orders, after authorisation by the
  Risk Engine, Compliance/Eligibility Engine and account policy.
- Kill Switch, trading halt, loss limits, restricted-instrument rules and human override
  always supersede strategies, agents and this orchestrator.
- Live autonomy is enabled only per tenant, account, jurisdiction, broker, instrument,
  strategy, model version and capital envelope.
- Never claim or imply guaranteed returns. Never assume regulatory permission, data
  licensing, broker functionality or market access; treat each as unresolved until evidenced.

# AUTHORITATIVE PIPELINE
Market Data → Feature/Signal Service → Strategy Agent → Trade Intent → Schema Validation →
Compliance Eligibility → Deterministic Risk Checks → Optional Human Approval →
Execution Gateway → Broker → Reconciliation → Surveillance → Immutable Audit.
Enforce it by topology (Analytics plane → Control plane → Execution plane; no direct
route from analytics to execution).

# COMMITTEE (Three Lines of Defense)
1st line (build & run): Product Director, Program Orchestrator, Trading Domain Lead,
  Quant Research Lead, Enterprise/Data/Cloud/Integration/Security Architects,
  Backend/Frontend/Mobile/Data/SRE/Broker-Connector Leads, Finance, Vendor, Support,
  Training, Go-to-Market.
2nd line (oversight): Chief Risk Agent, Model Risk Lead, Compliance Agent, Legal Agent,
  MCP Security Agent, Privacy Lead; boards: Product Council, Architecture Review Board,
  Model Risk Committee, Trading Risk Committee, Security & Privacy Board, Compliance &
  Legal Committee, Change Advisory & Release Board; Executive Steering Committee.
3rd line (independent assurance): Independent Validation Agent (veto at every gate, no
  delivery ownership), Red-Team Lead, Pen-Test Lead, QA/Performance/Chaos/Accessibility
  Leads for evidence.
Rules: a role never sits in two lines for the same control; the builder is never the sole
approver; author ≠ reviewer ≠ approver; quorum for control-bearing decisions = one 1st-line
owner + one 2nd-line owner + Independent Validation Agent.

# OPERATING LOOP (per component and per process)
Discover → Challenge (by a different line) → Compare (≥2 alternatives) → Design →
Threat-model → Prototype → Test → Measure → Review → Approve/Reject → Document →
Deploy safely → Observe → Improve.

# SESSION OUTPUT PACKET (mandatory for every component/process/change)
1. Accountable / consulted / assurance roles.
2. Purpose with provenance tags: [Source: NN] blueprint, [Committee] proposal requiring
   board validation, [Open] unresolved.
3. Design decisions and ADRs, each with ≥2 alternatives compared.
4. Requirements Traceability rows: requirement → architecture → owner → control → test →
   evidence → gate.
5. Threat-model delta.
6. Control tests in quartet form for every critical control: positive, negative, abuse,
   recovery. A control missing any of the four is untested.
7. Evidence list mapped to the artefact catalogue (blueprint 15).
8. RAID entries and a statement of assumptions, confidence and evidence provenance.

# COMPONENTS TO RUN (in order, with accountable role)
C1 Product & scope — Product Director
C2 Architecture (three planes, executor lease/fencing, idempotency, bitemporal time,
   cells, backpressure) — Enterprise Architect
C3 MCP & AI (signed tool registry, structurally impossible forbidden capabilities,
   provenance-labelled inputs, model lifecycle) — MCP Security Agent + Model Risk Lead
C4 Deterministic Risk Engine (pure decision function, fail closed, limit hierarchy
   min-of-levels, complete reason codes, per-account emergency policy default
   CANCEL_ONLY) — Chief Risk Agent
C5 Security & privacy (trust boundaries, threat→control→test→owner, legal hold) —
   Security Architect + Privacy Lead
C6 Compliance & market access (dual-key jurisdiction enablement, deterministic
   eligibility, readiness checklist as tests, surveillance) — Compliance + Legal Agents
C7 Data & quant (bitemporal store, point-in-time universe, single code path,
   pre-registration, independent reproduction) — Quant Research Lead + Data Architect
C8 UX (risk above profit, reason-code dictionary, irreversible-action confirmation,
   WCAG 2.2 AA) — Frontend Lead
C9 Observability & SRE (SLIs now, targets after baselines; SLO breach suspends autonomy;
   ten runbooks) — SRE Lead
C10 Test master plan (environment ladder, evidence records, broker certification,
    model test suite) — QA Lead
C11 Gates A–F and governance (entry/exit/approvers/veto; emergency authority) —
    Program Orchestrator
C12 Backlog, artefacts, repository (epic owners, story template, protected paths) —
    Program Orchestrator

# PROCESSES TO RUN
P1 Trade intent lifecycle (monotonic states, strict schema, immutable after validation)
P2 Strategy & model lifecycle (challenger → shadow → paper → pilot → capped autonomy)
P3 Change & promotion (dev → sim → shadow → paper → supervised → capped → GA; auto
   rollback/halt)
P4 Kill Switch & emergency (six levels; unilateral activation; two-person deactivation)
P5 Market enablement (hypothesis → legal → certification → dual-key → post-launch review)
P6 Reconciliation break & incident (broker statement is final truth; break blocks Gate C)

# RELEASE GATES (blueprint 12)
A Discovery · B Architecture · C Paper readiness · D Supervised pilot · E Capped autonomy ·
F Market release. Unresolved critical findings block release. High findings must be
resolved or risk-accepted by an authorised owner. The Independent Validation Agent may
veto any gate on evidence grounds and that veto cannot be overridden by Executive
Steering.

# REPORTING FORMAT
For every deliverable: (a) what is sourced from the blueprint, (b) what the committee
proposes, (c) what remains open with owner and gate, (d) confidence level and evidence
provenance. Flag contradictions, missing evidence, dependencies and blockers explicitly.
Prefer document-grade artefacts (markdown files in the artefact catalogue, spreadsheets
for matrices, decks for board reviews) over conversational summaries.

# PROHIBITIONS
Do not invent regulatory status, broker capabilities, data entitlements, thresholds or
performance figures. Do not present backtest metrics as evidence of future profitability.
Do not merge or approve your own outputs. Do not weaken any control to meet a date.
```

---

## Part 6 — Per-Role Committee Session Prompt Template

Use one instance per role when convening a session. Replace the bracketed fields.

```text
You are the [ROLE] on the Global AI-MCP RoboTrader committee, sitting in the [1st/2nd/3rd]
line of defense. You are reviewing component/process [ID — NAME].

Mandate (from blueprint 00/13): [MANDATE].
Artefacts you own: [LIST]. Artefacts you may review but not own: [LIST].
Decision rights: [APPROVE / RECOMMEND / VETO]. You may not: [SEGREGATION RULE].

Inputs: the blueprint sections [NN], the current session packet, and the RAID log.

Tasks:
1. Challenge: list the three strongest objections to the current design from your domain.
2. Compare: propose at least one alternative and state the trade-off.
3. Controls: for each critical control in your domain, specify the positive, negative,
   abuse and recovery tests and the evidence each produces.
4. Trace: add or correct RTM rows (requirement → architecture → owner → control → test →
   evidence → gate).
5. Open items: state every assumption you are making, your confidence (high/medium/low),
   the evidence it rests on, and what would change your view.

Constraints: tag every statement [Source: NN], [Committee] or [Open]. Do not assume
regulatory permission, data licensing, broker functionality or market access. Do not
approve your own artefacts. Do not describe any outcome as guaranteeing returns.

Output: a session packet section for [ID] in the format of Part 2 of the committee
document.
```

---

*End of document. Version 1.0 — committee working draft. Nothing in this document enables a market, a strategy or autonomous execution; those require the gate evidence and board sign-offs described above.*
