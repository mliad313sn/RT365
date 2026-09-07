# DASHBOARDS

| Owner | Reviewer (different line) | Approving body | First gate | Status |
|---|---|---|---|---|
| SRE Lead | Frontend Lead | ARB | C | Draft v1.0 |

| Dashboard | Audience | Panels (risk before profit [Source: 09]) |
|---|---|---|
| Global status | all | Kill Switch state per level, mode per account, data freshness, broker health |
| Risk | Risk officer | capital at risk, drawdown, exposure vs limits, HALT events, decision latency |
| Execution | Ops | intent funnel (created→filled), rejects by reason code, duplicates (must be 0), acks |
| Reconciliation | Ops | breaks by type/severity, ageing |
| Model/MCP | Model Risk, MCP Security | drift, tool calls by tool/tenant, denied calls, injection detections |
| SLOs | SRE | all SLIs with error budgets and safety-semantic status |
| Audit | Auditor | correlation-ID search, hash-chain verification status |
