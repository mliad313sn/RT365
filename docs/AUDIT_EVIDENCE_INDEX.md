# AUDIT_EVIDENCE_INDEX

| Owner | Reviewer (different line) | Approving body | First gate | Status |
|---|---|---|---|---|
| Program Orchestrator | Independent Validation Agent | CAB | A–F | v1.1 — locations filled for the dev/sim build; reviewer and IVA columns blank until humans sign |

Rule: an entry with a location but no reviewer/IVA signature is *evidence submitted*, not *evidence accepted* [Source: 00 no self-certification].

| # | Gate | Criterion | Evidence type | Location | Owner | Reviewer | Date | IVA verified |
|---|---|---|---|---|---|---|---|---|
| 1 | A | Approved charter | DECISION_LOG entry | PRODUCT_CHARTER.md v1.1; D-042 (ratifies D-001..D-004; H-02 closed) under D-040 | Product Director | product-owner agent (D-040) | 2026-09-08 | |
| 1b | A | Jurisdiction hypothesis | JURISDICTION_MATRIX row | JURISDICTION_MATRIX.md v1.1 hypothesis row (D-043); country fact [Open: Q-11-1]; legal basis No; sim keeps ZZ | Product Director / Compliance Agent | product-owner agent (D-040) | 2026-09-08 | |
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

## Committee review cycle 1 (2026-09-07)

Four independent challenge packets were issued against the dev/sim build and answered by one remediation commit. Rows below are *evidence submitted*; the Reviewer and IVA columns stay blank until humans sign. Verdicts are the reviewers' own; "remediation status" is the Delivery Orchestrator's (AI) reading of the code and tests, verified per item in RAID_LOG.md §Remediation and evidence — it is not an acceptance. Global IDs follow RAID_LOG.md §Review ID renumbering map.

| # | Gate | Criterion | Evidence type | Location | Owner | Reviewer | Date | IVA verified |
|---|---|---|---|---|---|---|---|---|
| 14 | C | Committee review — trading integration (C2 / P1 / P6 / E03 / E07) | REVIEW packet (challenge, 1st line different owner) | SESSIONS/REVIEW_C2_P1_P6_trading_integration.md — verdict REJECT for Gate C → OBJ-1/2/3 remediated in dev/sim (R-02, R-09, R-10, R-11, R-13); R-12, R-14 partial; O-26..O-34 open → ADR-014, D-015..D-017 | Trading Domain Lead + Integration Architect (challengers) | | 2026-09-07 | |
| 15 | B / D | Committee review — MCP and AI governance (C3) | REVIEW packet (challenge, 2nd line) | SESSIONS/REVIEW_C3_mcp_security_agent.md — verdicts: tool registration REJECT; Gate B ACCEPT WITH CONDITIONS; Gate D REJECT → Gate B conditions addressed in code (R-16 ADR-013, O-22 fail-closed key, O-35 fixture-only signing, R-18); R-15, R-21 remediated; R-17, R-19, R-20 partial; O-36..O-45 open → D-018, D-019, D-026, D-027 | MCP Security Agent (challenger) | | 2026-09-07 | |
| 16 | C | Committee review — deterministic risk engine and Kill Switch (C4 / P4) | REVIEW packet (challenge, 2nd line) | SESSIONS/REVIEW_C4_P4_chief_risk_agent.md — verdict RECOMMEND REJECT for Gate C → R-23, R-24, R-25 remediated in dev/sim; R-26..R-29 partial; O-46..O-49 pending Trading Risk Committee → D-020..D-023 | Chief Risk Agent (challenger) | | 2026-09-07 | |
| 17 | B | Committee review — security, identity, observability, audit (C5 / C1 / C9 / E11) | REVIEW packet + threat-model delta | SESSIONS/REVIEW_C5_C1_C9_security_redteam.md — verdict REJECT for Gate B → R-18 remediated; R-31 partial (seal/anchor); O-09 fail-closed retention; R-06 interim hardening; R-30, R-22, R-32..R-35 open/partial; T-14..T-25 added → D-024, D-025; single-author packet, ratification O-43 | Security Architect + Red-Team & Pen-Test Lead (one author; see O-43) | | 2026-09-07 | |
| 18 | B / C | Remediation commit for review cycle 1 | git commit | `09a6e716d50ac9b89a26a9f295fa54509b4492c3` "Remediate committee review findings (Gate B/C conditions)"; decisions D-015..D-027; ADRs/ADR-013.md, ADR-014.md (Proposed) | Backend Lead (author of code and tests) | | 2026-09-07 | |
| 19 | B / C | Regenerated evidence after remediation | EVIDENCE_REPORT | TEST_CASES/EVIDENCE_REPORT.md and TEST_CASES/TC-*.md (135 evidence records, 138 tests passing at commit 09a6e716, 15/15 areas with a full quartet; reviewer column pending by construction, D-014) | QA Lead | | 2026-09-07 | |
| 20 | B / C | Review ID renumbering and threat-model delta | RAID_LOG / THREAT_MODEL sections | RAID_LOG.md §Review ID renumbering map (2026-09-07) and §Remediation and evidence; THREAT_MODEL.md T-14..T-37 | Delivery Orchestrator (AI) | | 2026-09-07 | |
| 21 | A / B / C | Independent Validation Agent gate reports (cycle 1) | IVA reports (3rd line) | GATE_REPORTS/GATE_A_2026-09-07.md (REJECT: human decisions O-11/H-03, H-02), GATE_B_2026-09-07.md (ACCEPT WITH CONDITIONS, dev/sim), GATE_C_2026-09-07.md (REJECT: V-C1..V-C4) — all against 09a6e71; recommendations only, approver pending | Independent Validation Agent (AI) | | 2026-09-07 | |
| 22 | B / C | IVA cycle-1 remediation (V-C1, V-C2, IVA-03..08) | Code + control quartets | IVA remediation commit (2026-09-07, branch claude/attachment-solution-dev-52k8u0, after 09a6e71); R-36..R-40, D-028..D-031, T-38..T-43, ADR-015; TC-EX-009, TC-RK-021, TC-AP-005, TC-ID-005, TC-AI-011, TC-E2E-AUTH; re-validation O-56 | Delivery Orchestrator (AI) | | 2026-09-07 | |
| 23 | B / C | IVA re-validation of 0cbc895 | IVA report (3rd line) | GATE_REPORTS/REVALIDATION_2026-09-07_0cbc895.md — V-C1, V-C2, IVA-03..07 CLOSED (dev/sim); IVA-08 partial; IVA-09 not closed (O-54); new IVA-19..25; Gate B stays ACCEPT WITH CONDITIONS, Gate C stays REJECT | Independent Validation Agent (AI) | | 2026-09-07 | |
| 24 | B / C | Remediation of IVA-19..25 and IVA-08 residual | Code + control quartet | re-validation remediation commit (2026-09-07, after c0bb1fb); R-41..R-45, D-032..D-034, T-44..T-46, ADR-015 addendum; TC-EX-010; re-validation pending (O-56) | Delivery Orchestrator (AI) | | 2026-09-07 | |
| 25 | A | Product Owner appointed and declared decision authority (D-035, D-039); councils advisory; deviation R-48 accepted | appointment and authority record | PRODUCT_OWNER.md v2.0; goals/00_product_owner.md; D-035; D-039; H-23 closed by owner declaration (O-62: owner confirmation on the committed tree pending) | Delivery Orchestrator (AI) | | 2026-09-07 | |
| 26 | B | Agent roster generated from goals/ with write-scope guard; drift check in CI | generated files + quartet | .claude/agents/ (51 agents, roster.json); AGENT_ROSTER.md; TEST_CASES/TC-AGT.md; CI job 'Agent roster matches goals/' | Product Owner (Delivery Orchestrator builds) | | 2026-09-07 | |
| 27 | B / D | MCP stdio transport for the six tools, declared in .mcp.json | quartet + smoke test | TEST_CASES/TC-AI.md (TC-AI-012..015); MCP_TOOL_CATALOG.md §Servers; release workflow `mcp-serve tools/list` step | Backend Lead | | 2026-09-07 | |
| 28 | B | Installable distribution: wheel/sdist, Linux one-file executable, installers, release workflow (Windows .exe) | quartet + build logs | TEST_CASES/TC-PKG.md; installer/; dist/ built locally (wheel installed in a clean venv and self-checked from /tmp; Linux binary SHA-256 recorded in SESSIONS/ORCH_2026-09-07_product_owner_agents_packaging.md); release workflow run https://github.com/mliad313sn/RT365/actions/runs/34167194283 on f5baf2b: package, exe(linux/macos/windows) all green; `rt365.exe` SHA-256 `b57dc022985f72fc11250fa8816041cce8d9cb1b80e9cb8cf31ca48754c876a4` (artifact rt365-windows-x64, id 10034556905); human sign-off and signing decision [Open: H-24, O-23] | SRE Lead | | 2026-09-07 | |
| 29 | B | Build-agent prompts for E01..E15 (previously referenced but absent, O-31) | prompts | goals/build/README.md, E01..E15 | Program Orchestrator | | 2026-09-07 | |
| 30 | A | Gate A council convened by the Product Owner: Product Council option analyses, Compliance & Legal challenge, Independent Validation check | council packets | SESSIONS/COUNCIL_2026-09-08_gate_A_product_director.md, _compliance_legal.md, _iva.md; recommendations in PO_DECISION_QUEUE.md; IVA recommendation VETO (human decisions absent; closable by the Product Owner's decisions) | product-owner delegate (convener) | | 2026-09-08 | |
| 31 | D | Dual-key role pair remediated (council finding F-1) | quartet | TEST_CASES/TC-CP.md (TC-CP-007); R-49; T-51 | Backend Lead | Compliance Agent (pending) | 2026-09-08 | |
