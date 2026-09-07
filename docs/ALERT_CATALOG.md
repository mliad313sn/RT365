# ALERT_CATALOG

| Owner | Reviewer (different line) | Approving body | First gate | Status |
|---|---|---|---|---|
| SRE Lead | Chief Risk Agent | ARB | C | Draft v1.0 |

| Alert | Condition | Severity | Auto-action | Runbook |
|---|---|---|---|---|
| Duplicate order detected | >0 | S1 | Kill Switch account | duplicate order |
| Risk engine fail-open attempt | any APPROVED without decision record | S1 | Kill Switch platform | risk engine unavailable |
| Analytics→Execution route attempt | network deny event | S1 | revoke agent identity | credential compromise |
| Non-allowlisted tool call | deny event | S2 | revoke tool for tenant | — |
| Freshness SLO breach | per SLO | S2 | autonomy → Supervised | data stale |
| Decision-latency SLO breach | per SLO | S2 | autonomy → Supervised | — |
| Reconciliation break | any | S2 | account → Supervised | reconciliation break |
| Drift threshold | per model card | S2 | suspend signals | model drift |
| Broker health fail | health check | S2 | cancel-only | broker disconnected |
| Audit chain verification fail | hash mismatch | S1 | halt trading; forensic | Kill Switch activation |
| Limit changed | any | info | — | — |
| execution.unauthorised_command | command without valid control-plane authorisation (forged/altered) [Committee: GATE_C V-C2] | S1 | killswitch_account | credential compromise |
| execution.blocked_at_gateway | authorised command refused by Kill Switch / halt / mode / provenance at submit or retry [Committee: GATE_C V-C1] | S1 | none (page) | Kill Switch activation |
