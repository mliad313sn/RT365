# INCIDENT_RESPONSE

| Owner | Reviewer (different line) | Approving body | First gate | Status |
|---|---|---|---|---|
| SRE Lead | Security Architect | CAB, Security & Privacy Board | C | Draft v1.0 |

Severity: S1 capital at risk / control bypass / data breach · S2 degraded control or data · S3 other.
Incident command: SRE Lead (commander), Chief Risk Agent (risk decisions), Compliance Agent (notifications), Security Architect (cyber), Support Lead (customers). Deputies documented in RACI.md [Source: 13].

## Runbooks [Source: 10]
| Runbook | Trigger | First action | Escalation |
|---|---|---|---|
| Data stale | freshness SLO breach | autonomy → Supervised; confirm RK-FRESH rejections | Data Eng Lead |
| Broker disconnected | health check fail | cancel-only mode; reconcile on reconnect | Broker-Connector Lead |
| Duplicate order | reconciliation or alert | Kill Switch at account; investigate fencing/idempotency | Integration Architect |
| Risk engine unavailable | health/latency | confirm HALTED outcomes (fail closed); restore | Backend Lead |
| Reconciliation break | EOD/intraday break | account → Supervised; ticket | Operations |
| Unexpected exposure | runtime monitor | halt strategy/account; apply emergency policy | Chief Risk Agent |
| Model drift | drift threshold | suspend challenger/champion signals | Model Risk Lead |
| Credential compromise | detection | revoke/rotate; Kill Switch at tenant; forensic snapshot | Security Architect |
| Regional failure | cell loss | DR_PLAN | Cloud Architect |
| Kill Switch activation | any | evidence snapshot; notify; post-incident review before restore | Incident commander |
Post-incident review within 5 working days; findings to RAID_LOG.md.
