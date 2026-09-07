# REQUIREMENTS_TRACEABILITY

| Owner | Reviewer (different line) | Approving body | First gate | Status |
|---|---|---|---|---|
| Program Orchestrator | Independent Validation Agent | CAB | A | Draft v1.0 |

Every requirement maps to architecture, owner, control, test, evidence and gate [Source: 00]. Seed rows below; extend per story.

| Req | Architecture element | Implementation owner | Control | Test IDs (quartet) | Evidence | Gate |
|---|---|---|---|---|---|---|
| FR-01 | Identity service, PIM | Backend Lead | Maker-checker, MFA | TC-ID-001..004 | AUDIT_EVIDENCE_INDEX #… | B |
| FR-02 | Broker Adapter framework | Broker-Connector Lead | Capability discovery, vault credentials | TC-BR-001..004 | BROKER_CERTIFICATIONS/ | C |
| FR-03 | Market Data, bitemporal store | Data Engineering Lead | Provenance, freshness SLA | TC-MD-001..004 | quality reports | C |
| FR-09 | AI/MCP context, signed registry | Backend Lead | Allowlisted tools, schema validation | TC-AI-001..004 | MCP_TOOL_CATALOG.md | D |
| FR-11 | Risk service | Backend Lead | Deterministic decision, fail closed | TC-RK-001..004 | determinism report | C |
| FR-12 | Approval service | Backend Lead | Maker ≠ checker | TC-AP-001..004 | approval logs | D |
| FR-13 | OMS/Execution Gateway | Backend Lead | Executor lease + fencing, idempotency key | TC-EX-001..004 | duplicate-delivery report | C |
| FR-14 | Reconciliation service | Backend Lead | Break → Supervised | TC-RC-001..004 | reconciliation reports | C |
| FR-15 | Compliance service, WORM | Backend Lead | Eligibility, dual-key flag, retention | TC-CP-001..004 | COMPLIANCE_MATRIX.md | D |
| FR-17 | Kill Switch service | Backend Lead | Six levels, two-person restore | TC-KS-001..004 | drill evidence | C |
| NFR-SEC-01 | Network policy | Cloud Architect | No analytics→execution route | TC-NET-001..004 | policy test | B |
| NFR-OBS-01 | Telemetry | SRE Lead | Correlation ID end to end | TC-OB-001..004 | trace completeness | C |
