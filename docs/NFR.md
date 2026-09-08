# NFR — Non-Functional Requirements

| Owner | Reviewer (different line) | Approving body | First gate | Status |
|---|---|---|---|---|
| Enterprise Architect | SRE Lead | ARB | B | Draft v1.1 — **not reviewed**; the SRE Lead's review is pending (O-129) |

Targets marked [Open: O-03] are set after measured baselines and business approval [Source: 10].

**v1.1 (2026-09-08)** applies the ARB's recommendation of `docs/SESSIONS/COUNCIL_2026-09-08_arb_adr_007.md` §9 (condition C-007-7, register item O-163): NFR-SCL-01 replaced, NFR-SCL-02 added, NFR-RES-01 split into NFR-RES-01a and NFR-RES-01b, NFR-DR-01 amended, and the "cell" note added below the table. Author: Enterprise Architect (owner). Reviewer (different line): SRE Lead — **pending**. Approving body: ARB (advisory). Decision: the Product Owner (D-039/D-040). **No target, threshold or figure is added by v1.1** [Committee] [Source: 13].

| ID | Category | Requirement | Source | Target |
|---|---|---|---|---|
| NFR-AVL-01 | Availability | Control and execution planes never shed under load; fail closed | 03, 05 | [Open: O-03] |
| NFR-LAT-01 | Latency | Risk-decision latency p99 per **deployment cell**, measured intent-enqueue → decision write | 10 | [Open: O-03] |
| NFR-LAT-02 | Latency | Order acknowledgement latency per broker | 10 | [Open: O-03] |
| NFR-FRS-01 | Freshness | Market-data freshness budget per instrument class; stale → reject | 03, 10 | [Open: O-03] |
| NFR-CON-01 | Consistency | Idempotent order commands; exactly-once business effect under at-least-once delivery | 03 | 100% in duplicate-delivery tests |
| NFR-CON-02 | Consistency | Monotonic state transitions; broker statement is final truth | 03 | 100% |
| NFR-DET-01 | Determinism | Risk/eligibility decisions are pure functions of inputs + policy version | 05 | 100% identical across replicas |
| NFR-SEC-01 | Security | No network route analytics → execution; no secrets in agent context | 04, 06 | Enforced by policy, tested |
| NFR-SEC-02 | Security | mTLS, signed artefacts, SBOM, SAST/DAST/SCA, secret scanning | 06 | CI gate |
| NFR-AUD-01 | Auditability | Immutable, hash-chained audit with correlation ID for every decision/transition | 03, 06 | 100% |
| NFR-TEN-01 | Isolation | Tenant-partitioned streams, storage and caches; no noisy neighbour | 03 | Tenant-escape tests pass |
| NFR-SCL-01 | Scalability | **Service tier holds no request state**: any replica may serve any request, no session or decision state lives in a process, and a replica may be added or removed without moving state. **All durable state lives in named stores, each with a declared unit of scale and partition key**, and the platform scales by adding partitions, not by making a store bigger: control-state store per service per deployment cell / account and tenant (ADR-018, D-058, O-115); bitemporal market-data store per deployment cell / instrument and market_ts (D-056); audit store per platform with an anchor directory owned by a different principal / tenant on read, chain sequence on write (ADR-020, D-062, O-54); MCP revocation and nonce journals (O-55, O-118); event bus and outbox relay / topic and tenant — **no bus is deployed in any environment** [Open: R-05]. Autoscale on lag/latency; no scaler, admission control or threshold exists today [Open: O-162, O-03]. **Each durable store is a new thing to protect: file permissions, backup, residency and retention do not exist for any of them** [Open: O-111, O-136, F-7] [Committee; O-163] | 03 | Structure at Gate B (`docs/CAPACITY_MODEL.md` §1, §3, §4, §7 — a **structure** reference, never a threshold); baselines Gate C; targets Gate E [Open: O-03] |
| NFR-SCL-02 | Scalability | Partition keys are the ones declared in `docs/CAPACITY_MODEL.md` §1 and are not restated elsewhere, so they cannot drift: tenant/instrument, tenant/account, account, instrument/market_ts, tenant and chain sequence, topic/tenant [Committee] | 03 | Capacity model §1; no number |
| NFR-RES-01a | Resilience | **Active/standby execution ownership**: one active executor per account holds a leased lock with a monotonic fencing token; a stale token is refused; the token strictly increases across preemption, expiry and restart (ADR-002, ADR-018) | 03 | Failover with an in-flight order — TC-EX-003, TC-EX-004, TC-DUR-002, TC-EX-011; dev/sim, two connections in one process stand in for two processes [Open: O-117] |
| NFR-RES-01b | Resilience | **The regional deployment cell is the failure domain** (ADR-007 as amended, `Proposed`): only the closed, directional four-item list of ADR-007 item 4 crosses a deployment-cell boundary; the audit witness lives outside the deployment cell it witnesses (ADR-007 item 5); an account is served by exactly one deployment cell at a time | 03 | **No test exists and none can exist until a second deployment cell is provisioned**; evidenced by a DR drill with O-18. Gate E [Open: O-18, H-05, A-6, B-15] |
| NFR-A11Y-01 | Accessibility | WCAG 2.2 AA [Committee] | 09 | Verified by Accessibility Lead |
| NFR-PRV-01 | Privacy | Redaction at emission; residency per tenant; retention schedules | 06 | DPIA per jurisdiction |
| NFR-DR-01 | Recoverability | RPO/RTO per **deployment cell**; a standby deployment cell inherits **two** unmeasured O(n) verifications (control-store journal replay, audit-chain and anchor verification) and must reach an anchor directory that survived the loss of the failed deployment cell (ADR-007 item 5, ADR-018, ADR-020) | 10 | [Open: O-18, blocked on O-111, O-133, O-156, O-167 and a drill that states the history length it ran against — `docs/DR_PLAN.md`, `docs/CAPACITY_MODEL.md` §4a] |
| NFR-DIST-01 | Executability | The product installs and runs from a clean machine (wheel, one-file executable) with the same fail-closed rules as the source tree: unlabelled environment refused, only sim servable, missing or tampered signed registry refused, resource root never silently substituted [Committee, ADR-016] | 16 | TC-PKG-001..004; release workflow smoke tests |
| NFR-BIL-01 | Isolation | Billing and metering have no route to the control or execution planes; metering reads the audit chain only; billing state never gates a halt, a Kill Switch, an approval or a disclosure [Committee; D-046] | 14 | quartet TC-BIL-001..004 (E14, to build) |
| NFR-GLO-01 | Global compatibility | Capable in every country on every continent: any ISO 3166-1 jurisdiction cell, any ISO 4217 currency, venue calendars in their own timezone, residency per tenant region, localisable UI and disclosures; enablement per cell by dual key only [Owner requirement; D-050] | 07, 08, 17 | TC-GLO-001..004; docs/GLOBAL_COMPATIBILITY.md |
| NFR-GOV-01 | Governance | Every delivery agent is generated from its goals/ prompt, sits in one line of defense per control and can edit only what its prompt owns [Committee, ADR-016] | 13 | TC-AGT-001..004; `make agents-check` |

## Notes on two words this table uses [Committee] [Source: 13]

**"Cell".** "Cell" in NFR-RES-01b, NFR-DR-01, NFR-SCL-01, NFR-LAT-01 and NFR-PRV-01 means a **deployment cell** (ADR-007, `Proposed`). "Cell" in NFR-GLO-01 means a **`JurisdictionCell`** — a six-dimension compliance enablement tuple (country × customer type × broker × venue × asset class × feature) whose enablement requires a dual key (D-050, `services/compliance/compliance_engine/eligibility.py`). The two are unrelated and neither implies the other: **provisioning a deployment cell enables no market, and enabling a jurisdiction cell provisions nothing**. NFR-GLO-01's wording is the owner's requirement as recorded in D-050 and is not rewritten here; this note disambiguates it (C-007-1) [Open: O-168 proposed — the same disambiguation is owed in `docs/PRIVACY_IMPACT.md` rows 13–14, which say "per cell" without saying which, and belongs to the Privacy Lead].

**"Stateless".** NFR-SCL-01 said "stateless services" until v1.1. That word was written before this platform had durable state, and it had begun to do security work by accident: it was read as "nothing persists, so nothing leaks". It is now false and it was never the whole truth. The platform's stateful dimensions are **named, not counted**, because the existing register row and the capacity model each say "four" and mean different sets whose union is six [Committee; O-163, `docs/CAPACITY_MODEL.md` §6]:

| Stateful dimension | Register / decision id | Protected today? |
|---|---|---|
| Control-state store, one per service per deployment cell from shadow | ADR-018, D-058, O-115 | file permissions, backup, residency and retention: **none** [Open: O-111, O-136, F-7, O-128] |
| Bitemporal market-data store and its object-storage archive | D-056, O-87, O-88 | **none** [Open: O-136, F-7] |
| Audit store | ADR-020, D-062, O-111 | append-only at every layer and hash-chained; permissions, backup, residency and retention **none** [Open: O-135, O-167] |
| Anchor directory (a different principal's) | ADR-020, D-062, O-54, O-134 | one host, one principal, unkeyed in dev/sim [Open: O-54] |
| MCP revocation and nonce journals | O-55, O-118 | co-located with the control store in dev/sim only [Open: O-118] |
| Event bus and outbox relay | ADR-005, R-05, O-162 | **no bus is deployed in any environment**; this row is a target, not a description [Open: R-05] |

Four of these hold Confidential data at rest (`docs/DATA_FLOWS.md` DF-10 and the classification table). **Amending the requirement to match a correct architecture is not an achievement and must not be read as one**: durable state is why the platform can fail closed across a restart (D-058, D-062), and each store is a new thing to protect [Committee; Security Architect's caution recorded at COUNCIL_2026-09-08_arb_adr_007.md §4.4].
