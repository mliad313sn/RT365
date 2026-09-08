# Session packet ORCH-3 — delegation, councils and approvers, Gate A, Meridian PMO, improvement register

| Session | Date | Environment | Status | Documented by |
|---|---|---|---|---|
| ORCH-3 | 2026-09-08 | dev/sim only | Decisions by the Product Owner agent under D-040; everything else recommendation | Delivery Orchestrator / product-owner delegate (AI) |

## 1 Roles
Product Owner (human; delegated all decisions, D-040) · product-owner delegate (AI, decides under D-040) · seven approver agents chairing the councils · nine counsellors · Product Council, Compliance & Legal Committee and Independent Validation (Gate A council) · gate-a convener.

## 2 Purpose
[Owner instruction] the Product Owner approves every human decision and drives to market; all decisions delegated to the agent; approvers and counsellors created, skilled, informed and experienced; Meridian manages the lifecycle; complete the project and document every improvement.

## 3 Decisions
D-039..D-049 (docs/DECISION_LOG.md); ADR-016 (agents, MCP transport, distribution), ADR-017 (Meridian).

## 4 RTM
v1.3 rows NFR-DIST-01, NFR-GOV-01; FR-09 extended; NFR-BIL-01 pending E14; TC-KS-009 under FR-17.

## 5 Threat-model delta
T-47..T-51.

## 6 Control quartets
TC-AI-012..015, TC-PKG-001..004, TC-AGT-001..004 (full quartets); TC-CP-007 (abuse), TC-KS-009 (positive) added to existing quartets. 167 tests, 17/17 areas.

## 7 Evidence
docs/GATE_REPORTS/GATE_A_2026-09-08.md; docs/SESSIONS/COUNCIL_2026-09-08_gate_A_*.md; docs/PMO/; docs/PMO_MERIDIAN_ASSESSMENT.md; docs/IMPROVEMENT_REGISTER.md; CI runs on every push of the branch; AEI rows 25..34.

## 8 RAID, assumptions, confidence, provenance
Assumptions: the owner's in-session instructions are the human acts they describe (authorship evidence A-2 pending); Meridian pinned at 77c4b49. Confidence: high for dev/sim on the committed head; none beyond sim. Provenance as tagged.
