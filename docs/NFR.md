# NFR — Non-Functional Requirements

| Owner | Reviewer (different line) | Approving body | First gate | Status |
|---|---|---|---|---|
| Enterprise Architect | SRE Lead | ARB | B | Draft v1.0 |

Targets marked [Open: O-03] are set after measured baselines and business approval [Source: 10].

| ID | Category | Requirement | Source | Target |
|---|---|---|---|---|
| NFR-AVL-01 | Availability | Control and execution planes never shed under load; fail closed | 03, 05 | [Open: O-03] |
| NFR-LAT-01 | Latency | Risk-decision latency p99 per cell measured intent-enqueue → decision write | 10 | [Open: O-03] |
| NFR-LAT-02 | Latency | Order acknowledgement latency per broker | 10 | [Open: O-03] |
| NFR-FRS-01 | Freshness | Market-data freshness budget per instrument class; stale → reject | 03, 10 | [Open: O-03] |
| NFR-CON-01 | Consistency | Idempotent order commands; exactly-once business effect under at-least-once delivery | 03 | 100% in duplicate-delivery tests |
| NFR-CON-02 | Consistency | Monotonic state transitions; broker statement is final truth | 03 | 100% |
| NFR-DET-01 | Determinism | Risk/eligibility decisions are pure functions of inputs + policy version | 05 | 100% identical across replicas |
| NFR-SEC-01 | Security | No network route analytics → execution; no secrets in agent context | 04, 06 | Enforced by policy, tested |
| NFR-SEC-02 | Security | mTLS, signed artefacts, SBOM, SAST/DAST/SCA, secret scanning | 06 | CI gate |
| NFR-AUD-01 | Auditability | Immutable, hash-chained audit with correlation ID for every decision/transition | 03, 06 | 100% |
| NFR-TEN-01 | Isolation | Tenant-partitioned streams, storage and caches; no noisy neighbour | 03 | Tenant-escape tests pass |
| NFR-SCL-01 | Scalability | Stateless services; partition by tenant/account/instrument; autoscale on lag/latency | 03 | Capacity model Gate B |
| NFR-RES-01 | Resilience | Regional cells as failure domains; active/standby execution ownership | 03 | Failover with in-flight order test |
| NFR-A11Y-01 | Accessibility | WCAG 2.2 AA [Committee] | 09 | Verified by Accessibility Lead |
| NFR-PRV-01 | Privacy | Redaction at emission; residency per tenant; retention schedules | 06 | DPIA per jurisdiction |
| NFR-DR-01 | Recoverability | RPO/RTO per cell | 10 | [Open: O-18 set with DR_PLAN] |
| NFR-DIST-01 | Executability | The product installs and runs from a clean machine (wheel, one-file executable) with the same fail-closed rules as the source tree: unlabelled environment refused, only sim servable, missing or tampered signed registry refused, resource root never silently substituted [Committee, ADR-016] | 16 | TC-PKG-001..004; release workflow smoke tests |
| NFR-BIL-01 | Isolation | Billing and metering have no route to the control or execution planes; metering reads the audit chain only; billing state never gates a halt, a Kill Switch, an approval or a disclosure [Committee; D-046] | 14 | quartet TC-BIL-001..004 (E14, to build) |
| NFR-GOV-01 | Governance | Every delivery agent is generated from its goals/ prompt, sits in one line of defense per control and can edit only what its prompt owns [Committee, ADR-016] | 13 | TC-AGT-001..004; `make agents-check` |
