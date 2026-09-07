# POST_LAUNCH_REVIEW

| Owner | Reviewer (different line) | Approving body | First gate | Status |
|---|---|---|---|---|
| Product Director | Independent Validation Agent | Executive Steering | post-F | Draft v1.0 |

Reviews at 30 and 90 days per market [Committee].
| Area | Question | Evidence | Finding | Action / RAID ID |
|---|---|---|---|---|
| Control effectiveness | Any fail-open, duplicate, or bypass? | alerts, audit | | |
| Determinism | Any decision divergence across replicas? | TC-RK | | |
| Reconciliation | Breaks by type; ageing | reports | | |
| Halts | Drills and real activations; restore time | logs | | |
| Model/MCP | Drift, denied tool calls, injection detections | dashboards | | |
| Customer | Support tickets by reason code; usability issues | SUPPORT_MODEL | | |
| Compliance | Surveillance alerts, reporting completeness | COMPLIANCE_MATRIX | | |
| SLOs | Baselines vs candidates; targets to propose | SLO_SLA | | |
| Outcomes | Measurable outcomes from charter (never framed as return promises) | charter | | |
