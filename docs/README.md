# README — Artefact Catalogue Index

| Owner | Reviewer (different line) | Approving body | First gate | Status |
|---|---|---|---|---|
| Program Orchestrator | Independent Validation Agent | CAB | A | Draft v1.0 |

Every artefact of blueprint §15 [Source: 15], its owner and the gate at which it must be complete.

| Artefact | Owner | Gate |
|---|---|---|
| GOAL.md (root) | Program Orchestrator | A |
| PRODUCT_CHARTER.md, PRD.md, PERSONAS.md, JOURNEYS.md, SCOPE.md, ROADMAP.md | Product Director | A |
| BACKLOG.md, DEFINITION_OF_READY.md, DEFINITION_OF_DONE.md, REQUIREMENTS_TRACEABILITY.md, RAID_LOG.md, DECISION_LOG.md, RACI.md, RELEASE_CHECKLIST.md, AUDIT_EVIDENCE_INDEX.md | Program Orchestrator | A–F |
| NFR.md, CONTEXT_DIAGRAM.md, CONTAINER_DIAGRAM.md, COMPONENT_DIAGRAMS.md, SEQUENCE_DIAGRAMS.md, ADRs/ | Enterprise Architect | B |
| DATA_FLOWS.md, DATA_MODEL.md, DATA_DICTIONARY.md | Data Architect | B |
| API_OPENAPI.yaml, EVENT_CATALOG.md | Integration Architect | B |
| MCP_TOOL_CATALOG.md | MCP Security Agent | B |
| PROMPT_REGISTRY.md, MODEL_CARDS/ | Model Risk Lead | D |
| STRATEGY_CARDS/ | Quant Research Lead | D |
| RISK_POLICY.md, LIMIT_MATRIX.md | Chief Risk Agent | C |
| COMPLIANCE_MATRIX.md, JURISDICTION_MATRIX.md, MARKET_LAUNCH_CHECKLIST.md | Compliance Agent | D/F |
| THREAT_MODEL.md, SECURITY_PLAN.md, SBOM.md | Security Architect | B |
| PRIVACY_IMPACT.md | Privacy Lead | D |
| TEST_STRATEGY.md, TEST_CASES/, UAT_PLAN.md | QA Lead | C |
| PERFORMANCE_PLAN.md, CHAOS_PLAN.md | Performance & Chaos Lead | C/E |
| RED_TEAM_PLAN.md | Red-Team & Pen-Test Lead | D |
| DEPLOYMENT_RUNBOOK.md, ROLLBACK_PLAN.md, INCIDENT_RESPONSE.md, SLO_SLA.md, DASHBOARDS.md, ALERT_CATALOG.md | SRE Lead | C/E |
| DR_PLAN.md | Cloud Architect | E |
| SUPPORT_MODEL.md, TRAINING_PLAN.md | Support & Training Lead | D |
| VENDOR_ASSESSMENTS/ | Finance & Vendor Lead | B |
| BROKER_CERTIFICATIONS/ | Broker-Connector Lead | C |
| POST_LAUNCH_REVIEW.md | Product Director | post-F |

## Added by the dev/sim build [Committee]
| Artefact | Owner | Gate |
|---|---|---|
| SESSIONS/C01..C12, P1..P6 (session packets); SESSIONS/REVIEW_* (independent challenges) | Program Orchestrator; challengers per packet | A–D |
| GATE_REPORTS/ (IVA validation reports) | Independent Validation Agent | A–F |
| REASON_CODES.md (generated) | Frontend Lead / Support & Training Lead | C |
| CAPACITY_MODEL.md (skeleton) | Enterprise/Cloud Architect | B |
| TEST_CASES/TC-*.md, TEST_CASES/EVIDENCE_REPORT.md (generated) | QA Lead | C |
| BROKER_CERTIFICATIONS/sim-broker.md (generated) | Broker-Connector Lead | C |
| STRATEGY_CARDS/strat-sma-xover.md, MODEL_CARDS/rule-sma.md | Quant Research Lead / Model Risk Lead | D |
| ADRs/ADR-009..012 | Enterprise Architect | B |
| REPORTS/WEEKLY_*.md | Program Orchestrator | weekly |
| PRODUCT_OWNER.md (appointment and authority record), PO_DECISION_QUEUE.md (every human decision, council, recommendation, decision), AGENT_ROSTER.md (agents and MCP servers), INSTALLATION.md | Product Owner | A/B |
| SESSIONS/COUNCIL_*.md (council packets convened by the Product Owner) | council members per packet | A–F |
| ADRs/ADR-013..016 | Enterprise Architect | B |
| goals/build/README.md, E01..E15 (build-agent prompts); goals/profiles/ (expertise profiles); goals/approvers/ (council chairs with delegated approval scope); goals/counsel/ (specialist counsellors) — all generated into .claude/agents/ | Program Orchestrator / Product Owner | B |
| TEST_CASES/TC-PKG.md, TC-AGT.md (generated) | QA Lead | B |
