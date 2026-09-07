# AUDIT_EVIDENCE_INDEX

| Owner | Reviewer (different line) | Approving body | First gate | Status |
|---|---|---|---|---|
| Program Orchestrator | Independent Validation Agent | CAB | A–F | v1.1 — locations filled for the dev/sim build; reviewer and IVA columns blank until humans sign |

Rule: an entry with a location but no reviewer/IVA signature is *evidence submitted*, not *evidence accepted* [Source: 00 no self-certification].

| # | Gate | Criterion | Evidence type | Location | Owner | Reviewer | Date | IVA verified |
|---|---|---|---|---|---|---|---|---|
| 1 | A | Approved charter | DECISION_LOG entry | PRODUCT_CHARTER.md; D-001..D-004 pending Executive Steering (MISSING_ACTIONS H-02) | Product Director | | | |
| 1b | A | Jurisdiction hypothesis | JURISDICTION_MATRIX row | none — [Open: O-11]; sim uses ISO user-assigned code ZZ, explicitly not a jurisdiction | Product Director / Compliance Agent | | | |
| 2 | B | Threat model approved | THREAT_MODEL.md + board minutes | THREAT_MODEL.md; deltas in SESSIONS/REVIEW_C5_C1_C9_security_redteam.md; board minutes none | Security Architect | | | |
| 2b | B | Data flows, ADRs, capacity model, control ownership | docs | DATA_FLOWS.md; ADRs/ADR-001..012; CAPACITY_MODEL.md (skeleton); RACI.md + CODEOWNERS | Enterprise Architect | | | |
| 3 | C | Determinism test report | TC-RK-001..004 | TEST_CASES/TC-RK.md; TEST_CASES/EVIDENCE_REPORT.md; CI job "Determinism gate" | QA Lead | | | |
| 4 | C | Duplicate-delivery report | TC-EX-001..004 | TEST_CASES/TC-EX.md | QA Lead | | | |
| 5 | C | Broker certification | BROKER_CERTIFICATIONS/ | BROKER_CERTIFICATIONS/sim-broker.md (simulated broker; 2 rows OPEN; reviewer pending) | Broker-Connector Lead | | | |
| 5b | C | Reconciliation, audit and support workflows | TC-RC, TC-AUD, REASON_CODES | TEST_CASES/TC-RC.md, TC-AUD.md; REASON_CODES.md; SUPPORT_MODEL.md | Backend Lead | | | |
| 6 | D | Independent reproduction | IVA report | none — strategy is a fixture; see STRATEGY_CARDS/strat-sma-xover.md | IVA | — | | |
| 7 | D | Rollback drill | drill log | none [Open: H-19] | SRE Lead | | | |
| 8 | E | Halt drill in paper/pilot | TC-KS-001..004 | TEST_CASES/TC-KS.md (dev/sim only; paper/pilot drill pending) | SRE Lead | | | |
| 9 | F | DR drill, SLO evidence, accessibility, disclosures, legal terms, dossier | various | none | Program Orchestrator | | | |
| 10 | B | MCP registry signed and policy-consistent | scripts/verify_tool_registry.py | CI job "Policy invariants"; dev key flagged | MCP Security Agent | | | |
| 11 | B | Network policy invariants | scripts/check_network_policies.py | CI job "Policy invariants"; TEST_CASES/TC-NET.md | Cloud Architect | | | |
| 12 | B | SBOM | CycloneDX | security/sbom/sbom.cdx.json (unsigned) | Security Architect | | | |
| 13 | C | Session packets and independent reviews | docs/SESSIONS/ | C01..C12, P1..P6, REVIEW_* | Program Orchestrator | | | |
