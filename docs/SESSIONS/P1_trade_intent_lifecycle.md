# Session P1 — Trade Intent Lifecycle (blueprint 00 pipeline; Committee state machine)

**Environment:** dev/sim only. The pipeline runs in one process against a simulated broker; no real order is ever submitted. Documented by the Program Orchestrator (1st line, recommends, never approves).

## 1 Roles

| Function | Role (line) | Basis |
|---|---|---|
| Accountable / owners | Trading Domain Lead (semantics, 1st line); Backend Lead (implementation, 1st line); Chief Risk Agent (decision, 2nd line); Compliance Agent (eligibility, 2nd line) | COMMITTEE_DEEP_DIVE §P1 |
| Consulted | Integration Architect (contracts, events), Enterprise Architect | RACI |
| Builder | Backend Lead — `services/oms/oms/{lifecycle.py,intent_queue.py,pipeline.py}`, `libs/core/rtcore/schemas/intent.py`; Integration Architect — `contracts/api/API_OPENAPI.yaml`, `contracts/events/*.json`, `scripts/export_event_schemas.py` | RACI |
| Challenger (different line) | Chief Risk Agent (2nd line) — challenged immutability after validation, HALTED as terminal and approval-time re-check of Kill Switch | Protocol §1.4 rule 4 |
| Assurance / IVA | Independent Validation Agent (evidence; CODEOWNER on `/services/execution`) | COMMITTEE_DEEP_DIVE §P1 |

Statement: author != reviewer != approver. Backend Lead and Integration Architect authored; Chief Risk Agent and Compliance Agent challenge their stages; IVA verifies; Trading Domain Lead signs off OMS semantics but cannot approve strategies. Nothing here is self-certified.

## 2 Purpose

- [Source: 00] Market Data -> Feature/Signal -> Strategy Agent -> Trade Intent -> Schema Validation -> Compliance Eligibility -> Deterministic Risk -> Optional Human Approval -> Execution Gateway -> Broker -> Reconciliation -> Surveillance -> Immutable Audit. The intent schema is strict (strategy/model IDs and versions, account, venue, instrument, side, order type, quantity/notional, limit/stop, time-in-force, thesis code, confidence, market timestamp, data provenance, expiry).
- [Source: 03] Transitions are monotonic; every transition writes an immutable audit event with the correlation ID.
- [Committee] State machine `CREATED -> SCHEMA_VALIDATED -> ELIGIBLE|INELIGIBLE -> RISK_DECIDED -> AUTHORISED|PENDING_APPROVAL|REJECTED|HALTED -> SUBMITTED -> ACKNOWLEDGED -> PARTIALLY_FILLED|FILLED|CANCELLED|BROKER_REJECTED -> RECONCILED -> ARCHIVED`, `EXPIRED` from any pre-submission state, implemented in `oms/lifecycle.py` (`INTENT_MACHINE`, `TERMINAL`). An intent is never mutated after SCHEMA_VALIDATED: `ValidatedIntent.seal` fixes `intent_hash`; every engine recomputes `integrity_ok()`.
- Contracts: `TradeIntent` mirrors `API_OPENAPI.yaml#/components/schemas/TradeIntent`; 21 event schemas are exported from the pydantic models and drift fails CI (`--check`).

## 3 Decisions and ADRs

| # | Decision | Alternatives compared | Why chosen | Evidence |
|---|---|---|---|---|
| P1-D1 | Single intake path: `IntentQueue.submit` is the only Analytics -> Control channel; it validates the strict schema (`extra="forbid"`, provenance labels, price/type consistency, expiry after market_ts), rejects expired or future-dated intents, rejects invalid/delisted symbols via `instrument_valid` (point-in-time), applies backpressure, seals the intent and publishes `intent.submitted.v1`. | (a) Validation inside each consumer; (b) API gateway validation only; (c) chosen: one queue with validation before any engine. | (a) duplicates rules and lets a stage see an unvalidated intent; (b) leaves the MCP path unguarded. | TC-AI-002, TC-NET-001, TC-E2E-SCHEMA |
| P1-D2 | Immutability after validation via canonical hash (`TradeIntent.canonical_hash`, ADR-014); eligibility emits `CP-INTEG`, risk emits `RK-INTEG` with S1 alert. | (a) Database row lock; (b) chosen: content hash recomputed by each engine. | Works across process boundaries and replays; tamper is detected wherever the intent is consumed. | TC-RK-003, `EligibilityDecision.intent_hash` |
| P1-D3 | Coordinator `TradePipeline.process` wraps `_process` in `Inbox.process_once("intent:<hash>")`, enters `Plane.CONTROL` explicitly, audits `eligibility.decided.v1` and `risk.decided.v1`, routes REQUIRES_HUMAN_APPROVAL to `ApprovalQueue`, and on approval re-checks Kill Switch and HALTED mode before executing (`on_approval`). | (a) One service per stage on the bus now; (b) chosen: in-process coordinator with the same functions the bus consumers will call (ADR-005/ADR-010). | Dev/sim has no bus; the coordinator makes the plane crossings explicit so `PlaneGuard` can prove them. | TC-EX-002 (pipeline replay no-op), TC-AP-004 (Kill Switch after approval blocks execution) |
| P1-D4 | Authorised Order Command derived from the decision: `idempotency_key(intent_id, account, policy_version)` (ADR-003), `execution_target`, `approval_id`, `authorised_by` (`RISK_ENGINE` or `APPROVAL:<approver>`); only Control may call `ExecutionGateway.submit`. | (a) Gateway re-reads the decision; (b) chosen: command carries decision_id, approval_id and key. | Auditable link decision -> command -> order in one correlation ID. | TC-AUD-001 (seven actions on one correlation ID) |
| P1-D5 | Contract-first alignment enforced by tests: OpenAPI properties/required/enums == pydantic fields; event JSON schemas regenerated and compared; `EVENT_CATALOG.md` must list every schema. | (a) Generate OpenAPI from code at runtime; (b) hand-maintained YAML without tests; (c) chosen: hand-maintained contract plus alignment tests. | The contract remains the reviewable artefact (Integration Architect CODEOWNER on `/contracts`) while drift is impossible to merge. | **Proposed ADR-017** [Committee]; `test/contract/test_openapi_alignment.py` |

Standing ADRs: ADR-001, ADR-002, ADR-003, ADR-005; proposed ADR-010, ADR-014 (C4).

## 4 RTM rows

| Requirement | Architecture element | Implementation owner | Control | Test IDs | Evidence path | Gate |
|---|---|---|---|---|---|---|
| FR-09 / [Source: 00] strict intent schema | `TradeIntent`, `ValidatedIntent`, `IntentQueue.submit` | Backend Lead | Unknown fields, bad provenance, invalid symbol, expiry, future ts rejected | TC-AI-002, TC-E2E-SCHEMA | `libs/core/rtcore/schemas/intent.py`, `test/e2e/test_journeys_and_bff.py` | D |
| NFR-CON-02 (monotonic intent states) | `INTENT_MACHINE`, `IntentTracker.transition` | Backend Lead | Illegal transition raises; terminal states fixed | TC-EX-005 (order machine); GAP for intent machine | `services/oms/oms/lifecycle.py` | C |
| FR-11 / FR-15 stage order | `TradePipeline._process` (eligibility before risk; INELIGIBLE short-circuits) | Backend Lead | Eligibility -> risk -> approval -> gateway | TC-CP-003 (INELIGIBLE, no decision), TC-RK-014, TC-AP-001 | `services/oms/oms/pipeline.py` | C/D |
| FR-12 | `ApprovalQueue`, `on_approval` re-check | Backend Lead | Maker != checker; Kill Switch/expiry re-checked at execution | TC-AP-001..004, TC-E2E-J03 | `test/quartets/test_tc_ap_approval.py` | D |
| FR-13 / NFR-CON-01 | `OrderCommand`, `idempotency_key`, `Inbox` | Backend Lead | Exactly-once effect | TC-EX-001, TC-EX-002 | `test/quartets/test_tc_ex_execution.py` | C |
| NFR-AUD-01 / NFR-OBS-01 | Audit on every `IntentTracker` transition; `EventEnvelope.correlation_id` | Backend Lead / SRE Lead | One correlation ID across stages | TC-AUD-001, TC-OB-001, TC-OB-003 | `services/audit/audit_service/store.py` | C |
| [Source: 03] schema registry | `scripts/export_event_schemas.py --check`, `contracts/events/*.v1.json` | Integration Architect | No drift; catalogue complete | `test_event_schemas_have_no_drift`, `test_event_catalog_lists_every_schema`, `test_trade_intent_matches_openapi` | `.github/workflows/ci.yml` step "Contract schemas match models" | B |

## 5 Threat-model delta

| Threat | Boundary | Control | Test | Owner |
|---|---|---|---|---|
| T-01 Injection via intent fields | B3 | Strict schema, length limits, provenance allowlist | TC-AI-002 | MCP Security Agent |
| T-08 Replay | B3/B4 | `RK-DUP`, expiry, idempotency key | TC-RK-015, TC-EX-002 | Integration Architect |
| T-02 Excessive agency (agent enqueues an APPROVED decision or approves) | B2/B3 | `ApprovalQueue.enqueue` accepts only REQUIRES_HUMAN_APPROVAL; agents cannot approve | TC-AP-003 | MCP Security Agent |
| NEW T-20 (from C4) Intent mutated after validation | B3 | Hash recomputation at eligibility and risk | TC-RK-003 | Backend Lead |
| NEW T-28 Approval granted, then Kill Switch or expiry before execution | B4 | `on_approval` re-check; `ApprovalQueue.approve` refuses expired intents | TC-AP-004 | Chief Risk Agent |
| NEW T-29 Schema drift between BFF, models and event consumers | B2/B8 | Contract tests in CI | `test_openapi_alignment.py` | Integration Architect |

## 6 Control quartet per critical control

| Control | Positive | Negative | Abuse | Recovery |
|---|---|---|---|---|
| Schema validation at intake | TC-AI-001 (`SCHEMA_VALIDATED`, queue length 1) | TC-AI-002 (unknown field, empty provenance) | TC-AI-002 (hallucinated / delisted symbol, foreign account scope) | GAP — no test that a queue rejected under `BACKPRESSURE` accepts again once drained |
| Immutability after validation | TC-CP-001 (`intent_hash` in decision) | TC-RK-003 (`RK-INTEG`) | TC-RK-003 (mutated intent -> S1 alert) | GAP — no test of resubmission as a new intent after tamper detection |
| Stage ordering and terminal states | TC-AUD-001 (all stages on one correlation) | TC-CP-003 (INELIGIBLE is terminal; no risk decision) | TC-AP-003 (agent cannot skip approval) | TC-AP-004 (expired -> EXPIRED, never executed) |
| Authorised command -> gateway | TC-EX-001 | TC-EX-002 | TC-EX-003, `test_gateway_denies_calls_from_analytics_plane` | TC-EX-004 |
| Contract alignment | `test_trade_intent_matches_openapi`, `test_decision_record_matches_openapi` | `test_event_schemas_have_no_drift` | GAP — no test that an extra OpenAPI field without a model field fails (covered by set equality in the positive test) | GAP — regeneration procedure is manual (`scripts/export_event_schemas.py` without `--check`) |

## 7 Evidence list

- `docs/SEQUENCE_DIAGRAMS.md`, `docs/EVENT_CATALOG.md`, `docs/DATA_MODEL.md`, `docs/JOURNEYS.md` (J-03)
- `services/oms/oms/{lifecycle.py,intent_queue.py,pipeline.py,outbox.py}`, `services/approval/approval_service/queue.py`, `libs/core/rtcore/schemas/{intent.py,order.py,decision.py}`, `libs/core/rtcore/envelope.py`
- `contracts/api/API_OPENAPI.yaml`, `contracts/events/README.md`, `contracts/events/*.v1.json` (21 schemas), `scripts/export_event_schemas.py`
- `test/contract/test_openapi_alignment.py`, `test/quartets/test_tc_ap_approval.py`, `test/quartets/test_tc_ex_execution.py`, `test/quartets/test_tc_aud_audit.py`, `test/e2e/test_journeys_and_bff.py` (TC-E2E-J03, TC-E2E-SCHEMA)

## 8 RAID entries, assumptions, confidence, provenance

| ID | Type | Item | Owner | Gate |
|---|---|---|---|---|
| O-37 | Dependency | Bus consumers per stage with inbox dedupe (ADR-005) do not exist; `TradePipeline` is the only executor of the state machine, so stage-level idempotency under redelivery is proven only at pipeline granularity | Integration Architect, Backend Lead | C |
| O-38 | Gap | No direct quartet for `INTENT_MACHINE` (illegal intent transitions, terminal HALTED/INELIGIBLE) — add TC-OMS-001..004 | QA Lead | C |
| R-14 | Risk | `IntentQueue._seen_hashes` is declared but never used (`intent_queue.py:40`); duplicate detection relies on `recent_intent_hashes` in the account snapshot and the pipeline inbox — a reader may assume queue-level dedupe exists | Backend Lead | C |
| R-15 | Risk | `intent_id` is client-supplied (uuid5 in `intent_from_signal`); collision across strategies would be caught by `intent_hash` dedupe, but two different intents sharing an id would produce misleading tracker history | Backend Lead, Trading Domain Lead | C |

Assumptions: one process, one correlation ID per intent, simulated broker fills immediately for market orders; approval queue and Kill Switch state are in-memory.

Confidence: **high** for schema strictness, immutability and stage ordering (tests trace to code); **medium** for lifecycle completeness (RECONCILED/ARCHIVED transitions exercised only through reconciliation tests); **low** for behaviour under a real bus.

Provenance: [Source: 00, 03, 04] pipeline, guarantees, intent schema; [Committee] state machine, coordinator, ADR-017 proposal; [Open] O-37, O-38. Evidence cited by path; IVA review pending.
