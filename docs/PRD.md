# PRD — Product Requirements

| Owner | Reviewer (different line) | Approving body | First gate | Status |
|---|---|---|---|---|
| Product Director | Trading Domain Lead | Product Council | A | Draft v1.0 |

Requirement groups from blueprint 02 with IDs, epic and gate. Each FR must have Given/When/Then acceptance in TEST_CASES/ and an RTM row.

| FR | Requirement [Source: 02] | Epic | Gate | Acceptance sketch [Committee] |
|---|---|---|---|---|
| FR-01 | Identity, tenant admin, MFA, sessions, RBAC/ABAC, privileged-access workflows | E01 | B | Given a privileged action, when one approver acts, then it stays pending until a second approver from a different line acts |
| FR-02 | Broker/exchange onboarding, capability discovery, credential rotation, connection health | E03 | C | Given an adapter, when capability discovery runs, then unsupported order types are rejected at schema validation |
| FR-03 | Licensed real-time/historical data with timestamp, quality and provenance | E02 | C | Given a bar, when stored, then market/ingest timestamps and provenance are present |
| FR-04 | Watchlists, charts, depth (where licensed), news/events, alerts, economic calendar | E02, E10 | C | Depth hidden when entitlement absent |
| FR-05 | Portfolio, cash, margin, positions, exposure, PnL, attribution | E04 | C | Positions match broker statement at EOD |
| FR-06 | Strategy registry, versioning, parameters, approvals, lifecycle, rollback | E08 | C | No strategy reaches paper without MRC approval record |
| FR-07 | Research notebooks/sandboxes isolated from production credentials | E08, E13 | B | Sandbox has no vault access (negative test) |
| FR-08 | Backtest, replay, walk-forward, scenario, sensitivity, Monte Carlo | E08 | C | Same snapshot → identical fills |
| FR-09 | AI signal generation with explainability, confidence, evidence refs | E09 | D | Signal without evidence refs is schema-invalid |
| FR-10 | Market, limit, stop, stop-limit, trailing, conditional orders | E07 | C | Each type certified per broker |
| FR-11 | Pre-trade, at-trade, post-trade risk controls | E05 | C | Decision record has policy version, reason codes, values, thresholds, timestamp |
| FR-12 | Human approval queues, maker-checker | E05, E07 | D | Maker cannot check own intent |
| FR-13 | Execution routing, idempotency, retry, fills, cancellation | E07 | C | Duplicate delivery → one broker order |
| FR-14 | Reconciliation vs broker statements, automatic break management | E07, E11 | C | Break moves account to Supervised |
| FR-15 | Eligibility, restricted lists, surveillance, retention, regulatory reporting adapters | E06, E11 | D | Ineligible combo rejected with reason code |
| FR-16 | Notifications, incident centre, audit explorer, customer reporting, admin | E11, E12, E14 | C | Audit explorer is read-only for auditor role |
| FR-17 | Kill Switch at platform/tenant/account/strategy/asset/venue | E05 | C | Activation blocks new risk within measured latency; deactivation needs two persons |

## Non-functional requirements
See NFR.md. Global compatibility (every country on every continent, enabled per cell only) is NFR-GLO-01 (D-050; docs/GLOBAL_COMPATIBILITY.md).
