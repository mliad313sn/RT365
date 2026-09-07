# RAID_LOG

| Owner | Reviewer (different line) | Approving body | First gate | Status |
|---|---|---|---|---|
| Program Orchestrator | Independent Validation Agent | CAB | A–F | Draft v1.0 |

| ID | Type | Item | Owner | Needed by | Status |
|---|---|---|---|---|---|
| O-01 | Assumption | Persona × mode policy per jurisdiction | Compliance & Legal Committee | Gate A | Open |
| O-02 | Gap | Pricing and billing scope (E14) | Product Director, Finance | Gate A | Open |
| O-03 | Dependency | Numeric freshness/latency thresholds after baselines | SRE Lead | Gate E | Open |
| O-04 | Decision | Service framework choice | ARB | Gate B | Open |
| O-05 | Gap | Model providers, hosting, data-processing terms | Model Risk Lead, Privacy Lead | Gate B | Open |
| O-06 | Gap | Evaluation dataset ownership/licensing | Model Risk Lead | Gate D | Open |
| O-07 | Gap | Numeric risk thresholds per asset class/jurisdiction | Trading Risk Committee | Gate C | Open |
| O-08 | Gap | Liquidation policy content | Trading Risk Committee | Gate E | Open |
| O-09 | Risk | Deletion right vs record retention (legal hold) | Legal Agent, Privacy Lead | Gate D | Open |
| O-10 | Dependency | DPIA per launch jurisdiction | Privacy Lead | Gate D | Open |
| O-11 | Gap | First launch jurisdiction hypothesis | Product Director, Compliance Agent | Gate A | Open |
| O-12 | Dependency | Data licensing for derived/redistributed data | Legal Agent, Data Architect | Gate C | Open |
| O-13 | Decision | Time-series/snapshot storage cost model | Data Architect, Finance | Gate B | Open |
| O-14 | Decision | Launch locales | Product Director | Gate F | Open |
| O-15 | Gap | On-call model and support hours per market | SRE Lead, Support Lead | Gate F | Open |
| O-16 | Gap | Measurable outcome targets for Gate A | Product Council | Gate A | Open |
| O-17 | Gap | Roadmap dates after capacity model | Executive Steering | Gate B | Open |
| O-18 | Gap | RPO/RTO per cell | Cloud Architect | Gate E | Open |
| O-19 | Gap | Named deputies for emergency authority | Program Orchestrator | Gate C | Open |
| R-01 | Risk | Non-deterministic path in risk/eligibility | Chief Risk Agent | continuous | Open |
| R-02 | Risk | Duplicate orders during executor failover | Integration Architect | Gate C | Open |
| R-03 | Risk | Look-ahead/leakage inflating backtests | Model Risk Lead | Gate D | Open |
| R-04 | Risk | Marketing/UI language implying guaranteed returns | GTM Lead, Compliance Agent | Gate F | Open |
| O-20 | Gap | CODEOWNERS team handles map to real reviewers; branch protection enabled | Program Orchestrator | Gate B | Open |
| O-21 | Gap | Surveillance detector parameters (wash/spoof/close windows) approved by Compliance & Legal | Compliance Agent | Gate D | Open |
| O-22 | Decision | Asymmetric (Ed25519/KMS) signing of the tool registry and artefacts; dev HMAC key retired | Security Architect, MCP Security Agent | Gate B | Open |
| O-23 | Gap | SAST/DAST/SCA scanners and artefact signing wired into CI (currently lint, typecheck, secret scan, SBOM only) | Cloud Architect | Gate B | Open |
| O-24 | Gap | Accessibility (WCAG 2.2 AA) pass on the operator console; PWA build (E10) | Frontend Lead, Accessibility Lead | Gate F | Open |
| O-25 | Decision | Trailing-stop and conditional order semantics per broker (schema accepts; sim broker rejects) | Trading Domain Lead | Gate C | Open |
| R-05 | Risk | Dev/sim stores are in-memory: durability, exactly-once under real redelivery and lease consistency are unproven on the deployed topology | Enterprise Architect | Gate C | Open |
| R-06 | Risk | BFF dev authentication (client-asserted headers) must be replaced by IdP/MFA sessions before any shared environment | Backend Lead, Security Architect | Gate B | Open |
| R-07 | Risk | Sim risk-policy fixture values could be mistaken for approved thresholds; `approved_for_production=false` guards it | Chief Risk Agent | Gate C | Open |
| R-08 | Risk | Set/dict ordering non-determinism in engine code (one instance found and fixed by the replica test TC-RK-001) | Backend Lead | continuous | Mitigated (replica test in CI) |
