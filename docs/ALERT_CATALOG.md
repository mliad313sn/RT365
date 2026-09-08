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
| audit.anchor_missing | the external audit anchor is absent, stale beyond the configured lag, its own chain is broken, or its tail was removed [Committee: ADR-020, BUILD_E11] | S1 | none (page; no automatic halt because the audit chain itself may be intact — restore the witness, verify, then seal) | Kill Switch activation |
| Audit chain verification fail | hash mismatch | S1 | halt trading; forensic | Kill Switch activation |
| Limit changed | any | info | — | — |
| execution.unauthorised_command | command without valid control-plane authorisation (forged/altered) [Committee: GATE_C V-C2] | S1 | none (page; the account id in a forged command is attacker-chosen, so no automatic halt — IVA-23) | credential compromise |
| execution.live_under_block | order live at the broker while execution is blocked and the cancel failed or was not confirmed [Committee: REVALIDATION IVA-19] | S1 | killswitch_account | Kill Switch activation |
| mcp.tenant_revoked | tool call denied with `TENANT_REVOKED` while a tenant-wide suspension is in force [Committee: BUILD_E01 C-6] | S2 | none (page the MCP Security Agent; deliberately no grant revocation so the two-person restore stays effective) | — |
| execution.store_unavailable | StoreError (unreadable or corrupt control store) at submit, retry or cancel; the gateway submits nothing and fails closed [Committee: ADR-018, BUILD_E07 C-11] | S1 | none (page; restore the store, run `verify()`, then resume; no automatic halt because the account id may be unknown at retry/cancel) | store unavailable |
| execution.blocked_at_gateway | authorised command refused by Kill Switch / halt / mode / provenance at submit or retry [Committee: GATE_C V-C1] | S1 | none (page) | Kill Switch activation |
