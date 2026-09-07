# DATA_MODEL

| Owner | Reviewer (different line) | Approving body | First gate | Status |
|---|---|---|---|---|
| Data Architect | Integration Architect | ARB | B | Draft v1.0 |

## Core entities [Committee, derived from 00, 03, 05, 08]
| Entity | Key fields | Notes |
|---|---|---|
| Tenant, Account | ids, jurisdiction, customer_type, mode, emergency_policy, capital_envelope | Mode transitions audited |
| Instrument (point-in-time) | id, venue, identifiers, tick, lot, session_calendar, valid_from, valid_to | Universe as-of date incl. delisted |
| MarketSnapshot | snapshot_id, instrument, market_ts, ingest_ts, provenance, quality | Bitemporal: as-of + knowledge time |
| Strategy, StrategyVersion | id, version, params, status, approvals, model_version | Registry with rollback |
| Model, PromptVersion | id, version, card_ref, eval_results, drift_thresholds | Inventory |
| TradeIntent | strategy id/version, model id/version, account, venue, instrument, side, order_type, qty/notional, limit/stop, tif, thesis_code, confidence, market_ts, provenance, expiry | Immutable after validation |
| EligibilityDecision, RiskDecision | decision_id, intent_id, outcome, policy_version, reason_codes[], evaluated[], snapshot ids, decided_at, build_hash | Deterministic |
| OrderCommand, Order, Fill | idempotency_key, fencing_token, client_order_id, state, broker_refs | Monotonic states |
| Position, Cash, Margin, PnL | account, instrument, as_of | Reconciled vs statement |
| ReconciliationBreak | type, severity, correlation_id, resolution, approvers | Blocks Gate C if open |
| AuditEvent | correlation_id, actor, action, payload_hash, prev_hash, ts | WORM |
| Limit | level (platform/tenant/account/strategy/instrument), metric, threshold, version, maker, checker, effective_from | Effective = min |
| JurisdictionFlag | cell, legal_record_ref, flag_state, activated_by | Dual key |
