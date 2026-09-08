# ALERT_CATALOG

| Owner | Reviewer (different line) | Approving body | First gate | Status |
|---|---|---|---|---|
| SRE Lead | Chief Risk Agent | ARB | C | Draft v1.1, 2026-09-08 — the delivery semantics of the alert path recorded (SRE-R5); **no alert, severity or auto-action added, removed or changed**; **reviewer signature pending**; not accepted |

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
| store.journal_unwitnessed | the control store's journal head is rolled back, forked, unwitnessed or staler than the ceiling against the audit chain that witnesses it [Committee: ADR-018 amendment 1, D-061 (5), D-066] | S1 | none (page; the platform has already refused to open the store — deliberately no automatic halt, because a Kill Switch activation is itself a control-store row and writing to a store under investigation would destroy the evidence) | store unavailable |
| audit.anchor_missing | the external audit anchor is absent, stale beyond the configured lag, its own chain is broken, or its tail was removed [Committee: ADR-020, BUILD_E11] | S1 | none (page; no automatic halt because the audit chain itself may be intact — restore the witness, verify, then seal) | Kill Switch activation |
| Audit chain verification fail | hash mismatch | S1 | halt trading; forensic | Kill Switch activation |
| Limit changed | any | info | — | — |
| execution.unauthorised_command | command without valid control-plane authorisation (forged/altered) [Committee: GATE_C V-C2] | S1 | none (page; the account id in a forged command is attacker-chosen, so no automatic halt — IVA-23) | credential compromise |
| execution.live_under_block | order live at the broker while execution is blocked and the cancel failed or was not confirmed [Committee: REVALIDATION IVA-19] | S1 | killswitch_account | Kill Switch activation |
| mcp.tenant_revoked | tool call denied with `TENANT_REVOKED` while a tenant-wide suspension is in force [Committee: BUILD_E01 C-6] | S2 | none (page the MCP Security Agent; deliberately no grant revocation so the two-person restore stays effective) | — |
| execution.store_unavailable | StoreError (unreadable or corrupt control store) at submit, retry or cancel; the gateway submits nothing and fails closed [Committee: ADR-018, BUILD_E07 C-11] | S1 | none (page; restore the store, run `verify()`, then resume; no automatic halt because the account id may be unknown at retry/cancel) | store unavailable |
| execution.blocked_at_gateway | authorised command refused by Kill Switch / halt / mode / provenance at submit or retry [Committee: GATE_C V-C1] | S1 | none (page) | Kill Switch activation |

## What "delivered" means on this path [Committee] — SRE-R5, read against the tree at `8f2258e`

The catalogue is the source of truth for what an alert **does**; this section is the truth about what happens to an alert **after** it fires. It changes no row above.

- **Every alert now carries the time it was raised** (`raised_at`) and an `alert_id`, and each channel copy is recorded as its own delivery with the time it left. That is the first end of the `alert_delivery_s` SLI, which had neither end before (`observability/slis.yaml`).
- **The second end is an operator acknowledgement**, and it has **no producer**: there is no notification component and no operator-facing acknowledgement path, so nothing acknowledges an alert outside a test. `AlertRouter.acknowledge` exists, refuses an alert that was never raised (a delivery time can never be manufactured without the raise it is measured from, TC-OB-013) and records the first acknowledgement only. Until a channel exists, the honest operational view is `AlertRouter.unacknowledged()` — **alerts outstanding**, not time-to-acknowledge [Open: SRE-R5, O-15].
- **"Delivered" means handed to the in-process channel list.** There is no pager, no mail transport and no export: `channels` is `["pager", "email"]` in name only. A delivery record is evidence that the platform tried, never that a human was reached.
- **An unacknowledged alert is never recorded as delivered in zero seconds.** A missing measurement read as zero is a measurement in the safe-looking direction, which is the direction that hides an outage.
- **The standing rule is unchanged and is not softened by any of this**: an auto-action may halt, suspend, revoke, cancel or narrow; it may never approve, enable, widen or resume. Nothing in the delivery path can trigger an auto-action, and `alert.autoaction_failed` (S1) still fires when an auto-action is unbound or its payload is incomplete, so a silent no-op remains impossible.
- **The two loudest failures on this platform still emit no alert at all**, because both store verifications run before the alert router is wired — detection is a process that will not start (INCIDENT_RESPONSE RB-13) [Open: SRE-R1]. No delivery improvement changes that.
