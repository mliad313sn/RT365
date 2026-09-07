# EVENT_CATALOG

| Owner | Reviewer (different line) | Approving body | First gate | Status |
|---|---|---|---|---|
| Integration Architect | Backend Lead | ARB | B | Draft v1.0 |

All events carry the common envelope (`contracts/events/envelope.v1.json`): event_id, correlation_id, tenant, account, market_ts (where applicable), emitted_ts, schema_version, producer, payload_hash. Payload schemas are generated from the typed models by `scripts/export_event_schemas.py` into contracts/events/<name>.v1.json and checked for drift in CI [Source: 03 schema registry; ADR-005].

| Event | Producer | Consumers | Key semantics |
|---|---|---|---|
| market.snapshot.v1 | Market Data | Strategy, Risk | provenance, quality |
| strategy.signal.v1 | Strategy/AI | Audit | thesis_code, evidence_refs, confidence |
| intent.submitted.v1 | Intent queue | Compliance | strict schema, expiry |
| eligibility.decided.v1 | Compliance | Risk, Audit | outcome, reason_codes, policy_version |
| risk.decided.v1 | Risk | Approval/OMS, Audit | APPROVED/REJECTED/REQUIRES_HUMAN_APPROVAL/HALTED |
| approval.recorded.v1 | Approval | OMS, Audit | approver ≠ maker |
| order.command.v1 | Approval/Risk | OMS | idempotency_key |
| order.submitted/acked/rejected/filled/cancelled.v1 | Execution | Portfolio, Reconciliation, Audit | fencing_token, client_order_id |
| reconciliation.completed/break.v1 | Reconciliation | Risk (mode change), Ops, Audit | break type, severity |
| risk.halt.v1 | Runtime monitors | Kill Switch | reason |
| killswitch.activated/deactivated.v1 | Kill Switch | All planes, Audit | level, actors (two for deactivate) |
| limit.changed.v1 | Policy store | Risk, Audit | maker, checker, cooling period |
| model.drift.v1 | Model monitoring | Model Risk, Kill Switch | threshold breached |
| jurisdiction.flag.changed.v1 | Compliance | Eligibility, Audit | legal_record_ref, activated_by |
Delivery: at-least-once; consumers idempotent via inbox [Source: 03].
