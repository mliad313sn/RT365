# Session packet P6 — Reconciliation Break and Incident (blueprint 02, 03, 10)

| Session | Date | Environment | Status | Documented by |
|---|---|---|---|---|
| P6 | 2026-09-07 | dev/sim only | Committee working draft; not a release artefact | Program Orchestrator (recommends, never approves) |

The broker statement is the final external truth [Source: 03]; in this build the statement comes from `SimulatedBroker.statement`, so reconciliation is proven against a simulated counterparty only. Tolerances (`price_tolerance_pct = 0.5`, `cash_tolerance = 0.01` in `reconcile()`) are sim fixtures [Open: O-07]. The SLI `reconciliation_completeness_pct` has no target [Open: O-03].

## 1 Roles

| Role in session | Person/role | Line |
|---|---|---|
| Accountable | Trading Domain Lead (break semantics, MARKET_LAUNCH technical part); Backend Lead (implementation, E07/E11 with Compliance Agent as 2nd-line reviewer for E11) | 1st |
| Builder (code) | Backend Lead — `services/reconciliation/reconciliation_service/reconcile.py`, `tickets.py`, `services/portfolio/portfolio_service/ledger.py`, wiring in `apps/web/web_bff/platform.py`; Broker-Connector Lead — `connectors/brokers/broker_adapters/simulated.py` (`statement`, `inject_phantom_order`) | 1st |
| Consulted | Broker-Connector Lead, SRE Lead (incident commander), Operations Analyst (ticket handling), Chief Risk Agent | 1st / 2nd |
| Challenger | Chief Risk Agent (2nd line; challenges severity mapping and the two-person rule; Trading Risk Committee reviews break trends) | 2nd |
| Assurance / IVA | Trading Risk Committee (trend review); Independent Validation Agent (Gate C veto ground "open reconciliation break") | 2nd / 3rd |

Segregation: author != reviewer != approver; nothing here is self-certified. In code, `BreakTicketService.resolve` refuses the same person twice; the packet applies the same rule to its own review.

## 2 Purpose

- [Source: 02] FR-14: reconciliation against broker statements with automatic break management; FR-05 positions match the broker statement at EOD.
- [Source: 03] Broker as final truth; monotonic state; exactly-once business effect.
- [Source: 10] Runbooks "reconciliation break" (account → Supervised; ticket) and "duplicate order" (Kill Switch at account; investigate fencing/idempotency); incident severities S1/S2/S3; post-incident review within 5 working days.
- [Committee] Cycle: intraday position/order and EOD statement reconciliation → break detected → automatic classification (timing, missing fill, duplicate, price, quantity) → account to Supervised (or Halted per severity) → ticket with correlation IDs → two-person resolution → audit → trend review at Trading Risk Committee; an unresolved break blocks Gate C for that account/venue.
- [Open: O-37], [Open: O-38] raised below; [Open: O-15] on-call for break handling.

## 3 Decisions and ADRs

| ID | Decision | Alternatives considered | Why chosen | Why not alternatives | Status |
|---|---|---|---|---|---|
| ADR-035 [Committee] | `reconcile()` is a pure function over internal positions/orders/cash and a `BrokerStatement`; classification into `BreakType` {TIMING, MISSING_FILL, DUPLICATE, PRICE, QUANTITY, CASH} with severity fixed in code: DUPLICATE and "internal fills exceed broker fills" are S1; the rest S2 | (a) broker-push reconciliation events; (b) ledger-as-truth with broker as a check | Pure function is deterministic and testable; statement-as-truth honours [Source: 03] | (a) assumes broker capability; (b) inverts the blueprint's truth rule | Proposed, pending Trading Risk Committee |
| ADR-036 [Committee] | Severity drives the automatic action through the alert catalogue: S1 → `execution.duplicate_order` → `killswitch_account`; S2 → `reconciliation.break` → `account_to_supervised` (`AccountRegistry.suspend_autonomy`, drops BOUNDED_AUTONOMOUS to SUPERVISED) (`platform.on_break`, `alerts.on(...)`) | (a) always Kill Switch; (b) always Supervised | Proportionate: a phantom order is capital at risk; a timing break is not | (a) halts on benign timing breaks; (b) leaves duplicate orders live | Proposed, pending Trading Risk Committee |
| ADR-037 [Committee] | Ticket resolution needs two different authorised humans (`RESOLVERS` = operations analyst, trading domain lead, risk officer, chief risk agent, SRE lead); agents refused; statuses OPEN → PENDING_SECOND → RESOLVED; every update audited `reconciliation.ticket.updated` | (a) single operations resolver; (b) different-*line* rule as for the Kill Switch | Two-person confirmation is the committee text (P6); the different-line variant is put to the Trading Risk Committee (R-15) | (a) single point of collusion; (b) may starve operations at night (O-15) | Proposed, pending Trading Risk Committee |
| D-P6-1 [Committee] | `Ledger` derives positions from fills and cash from fills and fees; it never overrides itself from the statement; breaks are resolved by humans, not by auto-adjusting the ledger | (a) auto-true-up to the statement; (b) dual ledgers | Auto-true-up would hide control failures; humans decide, audit records | — | Proposed, pending Chief Risk Agent |
| D-P6-2 [Committee] | Reconciliation completion is itself audited (`reconciliation.completed.v1` with counts) so an absent run is detectable | (a) audit breaks only | Completeness SLI needs the denominator | — | Proposed, pending SRE Lead |

## 4 RTM rows

| Requirement | Architecture element | Implementation owner | Control | Test IDs | Evidence path | Gate |
|---|---|---|---|---|---|---|
| FR-14 (match) | `reconcile()`; `SimPlatform.reconcile` audit | Backend Lead | Clean result; `reconciliation.completed.v1` with `break_count` | TC-RC-001 `test_positions_and_orders_match_statement` | `test/quartets/test_tc_rc_reconciliation.py` | C |
| FR-14 (break → Supervised) | `BreakTicketService.open` → `on_break` → `reconciliation.break` alert → `suspend_autonomy` | Backend Lead | S2 break drops autonomy to Supervised; ticket and `reconciliation.break.v1` audit | TC-RC-002 `test_break_moves_account_to_supervised` | same | C |
| FR-13 / T-09 (duplicate) | DUPLICATE S1 → `execution.duplicate_order` → account Kill Switch | Backend Lead | Phantom broker order kills the account | TC-RC-003 `test_phantom_broker_order_is_s1_duplicate_and_kills_account`; TC-EX-002 `test_replayed_command_deduplicated`; TC-EX-004 `test_failover_with_in_flight_order_single_broker_order` | same; `test/quartets/test_tc_ex_execution.py` | C |
| FR-14 (resolution) | `BreakTicketService.resolve` two-person; BFF `/v1/reconciliation/tickets/{id}/resolve` (`Permission.RESOLVE_BREAK`) | Backend Lead | Agents and repeat resolvers denied; RESOLVED closes ticket | TC-RC-004 `test_two_person_resolution`; TC-E2E-J06 `test_j06_break_ticket_via_api` | same; `test/e2e/test_journeys_and_bff.py` | C |
| FR-05 | `Ledger.positions/nav/apply_fill`; `SimulatedBroker.statement` | Backend Lead | Positions match statement | TC-RC-001 | `services/portfolio/portfolio_service/ledger.py` | C |
| NFR-CON-02 | Statement as truth; monotonic order states | Backend Lead | Broker truth; monotonic | TC-RC-001/003; TC-EX-005 `test_order_states_are_monotonic` | same | C |
| FR-11 (RT-RECON) | `evaluate_runtime(metrics.open_reconciliation_breaks > 0)` → RT-RECON halt event | Backend Lead | Open break → halt | TC-RK-016 `test_runtime_monitors_emit_halt_events` (explicit metrics) | `test/quartets/test_tc_rk_determinism.py` | C (wiring gap R-14) |
| FR-02 statement download | `BrokerAdapter.statement`; harness row TC-BR-005 | Broker-Connector Lead | Statement present with orders/fills | harness TC-BR-005 PASS | `docs/BROKER_CERTIFICATIONS/sim-broker.md` | C |
| [Source: 10] incident process | `docs/INCIDENT_RESPONSE.md` runbooks "reconciliation break", "duplicate order"; post-incident review ≤ 5 working days | SRE Lead | Runbook executed; review to RAID | GAP — no incident record or review has occurred | `docs/INCIDENT_RESPONSE.md` | C |

## 5 Threat-model delta

| Threat | Boundary | Control in this build | Test | Residual / owner |
|---|---|---|---|---|
| T-09 Duplicate orders / race | execution ↔ broker | Statement-side DUPLICATE detection (shared broker ref; order without internal counterpart) → S1 → account Kill Switch | TC-RC-003; TC-EX-002/004 | Real-broker statement format unknown (H-07). Integration Architect |
| T-07 Insider — collusive or unilateral break closure | operations | Two different humans from `RESOLVERS`; agents refused | TC-RC-004; TC-E2E-J06 | Same-line pair allowed (e.g. two 1st-line operators) → R-15. Chief Risk Agent |
| T-P6-1 Reconciliation never runs (new) | scheduler | `reconcile` is on demand (`POST /v1/reconciliation/run`, tests); `reconciliation.completed.v1` audited when it does run | GAP — no test for a missed cycle | No intraday/EOD scheduler; completeness SLI has no denominator source → O-37. SRE Lead |
| T-P6-2 Break persists while account trades (new) | tickets → risk | `RT-RECON` exists in `evaluate_runtime` but `open_reconciliation_breaks` is not fed from `BreakTicketService.open_tickets()`; only the alert-driven `suspend_autonomy` acts, and nothing clears `autonomy_suspended` after RESOLVED (no method exists in `AccountRegistry`) | TC-RC-002 (suspension), TC-RK-016 (explicit metric) | Automatic path is one-directional and partially unwired → R-14. Backend Lead |
| T-12 Evidence of breaks | audit | `reconciliation.break.v1`, `reconciliation.ticket.updated`, `reconciliation.completed.v1` with correlation IDs from the affected orders | TC-RC-002/004 | None. SRE Lead |
| T-P6-3 Statement spoofing / tampering (new) | broker → reconciliation | none in sim (statement produced in-process) | GAP | Signed/verified statement download is broker-specific (H-07). Broker-Connector Lead |
| T-03 Price break masking | ledger marks | PRICE break on average-price deviation > fixture 0.5 % | GAP — no PRICE-break test | Trading Domain Lead |

## 6 Control quartet per critical control

| Control | Positive | Negative | Abuse | Recovery |
|---|---|---|---|---|
| Break detection and classification | TC-RC-001 (clean: 1 position, 2 orders) | TC-RC-002 (QUANTITY S2 on internal drift) | TC-RC-003 (phantom order → DUPLICATE S1) | TC-RC-004 (resolution closes ticket) — PRICE/CASH/TIMING/MISSING_FILL classes: GAP |
| Account → Supervised on break | TC-RC-002 (BOUNDED_AUTONOMOUS → SUPERVISED, `autonomy_suspended`) | GAP — non-autonomous account: flag only, no mode change asserted | TC-RC-003 (S1 → Kill Switch rather than Supervised) | GAP — no path clears `autonomy_suspended` after RESOLVED (R-14) |
| Two-person ticket resolution | TC-RC-004 (OPS then TRADING_LEAD → RESOLVED); TC-E2E-J06 | TC-RC-004 (same resolver twice → denied) | TC-RC-004 (agent denied); TC-E2E-J06 (trader cannot run reconciliation → 403) | TC-E2E-J06 (`open_tickets` empty after RESOLVED) |
| Duplicate-order defence (idempotency + fencing + statement) | TC-EX-001 `test_one_authorised_command_one_broker_order` | TC-EX-002 | TC-EX-003 `test_stale_fencing_token_rejected`; TC-RC-003 | TC-EX-004 |
| Statement download and match (per adapter) | harness TC-BR-005 PASS | GAP | GAP | GAP |
| Scheduled intraday/EOD cycle and completeness SLI | GAP [Open: O-37] | GAP | GAP | GAP |
| Trend review at Trading Risk Committee | GAP [Open: O-38] | GAP | GAP | GAP |

## 7 Evidence list

| Evidence | Path |
|---|---|
| Reconciliation function, break types, severities, tolerances | `services/reconciliation/reconciliation_service/reconcile.py` |
| Ticket service, resolvers, two-person rule | `services/reconciliation/reconciliation_service/tickets.py` |
| Ledger (fills → positions/cash; NAV; snapshot) | `services/portfolio/portfolio_service/ledger.py` |
| Broker statement contract and simulated statement; phantom-order chaos helper | `connectors/brokers/broker_adapters/base.py` (`BrokerStatement`); `simulated.py` (`statement`, `inject_phantom_order`) |
| Wiring: reconcile audit, ticket opening, severity → alert → auto-action, monitors | `apps/web/web_bff/platform.py` (`reconcile`, `on_break`, `alerts.on("account_to_supervised")`, `alerts.on("killswitch_account")`, `evaluate_monitors`) |
| BFF endpoints | `apps/web/web_bff/app.py` (`/v1/reconciliation/run`, `/breaks`, `/tickets/{id}/resolve`) |
| Runtime monitor RT-RECON | `services/risk/risk_engine/monitors.py` |
| Incident process, alert catalogue, SLI | `docs/INCIDENT_RESPONSE.md`; `docs/ALERT_CATALOG.md`; `observability/alerts.yaml`; `observability/slis.yaml` (`reconciliation_completeness_pct`) |
| Tests and evidence records (2026-09-07T17:28:57Z, 104 passed, env `dev`) | `test/quartets/test_tc_rc_reconciliation.py`; `test/quartets/test_tc_ex_execution.py`; `test/e2e/test_journeys_and_bff.py`; `test/evidence/evidence_index.json` |
| Governance | `docs/COMMITTEE_DEEP_DIVE.md` §P6; `goals/build/E07_oms_execution_gateway.md`, `E11_audit_surveillance_reporting.md`; `docs/MISSING_ACTIONS.md` H-07 |

## 8 RAID entries, assumptions, confidence, provenance

| ID | Type | Item | Owner | Needed by | Status |
|---|---|---|---|---|---|
| O-37 | Gap | No intraday/EOD reconciliation scheduler; `reconcile` runs only on demand; `reconciliation_completeness_pct` has no denominator source and no target (O-03); a missed cycle is undetectable | SRE Lead (Backend Lead builds) | Gate C | Open |
| O-38 | Gap | Trend review of breaks at the Trading Risk Committee and the "unresolved break blocks Gate C for that account/venue" rule are not operationalised (no ageing report, no gate check reads `open_tickets()`) | Program Orchestrator / Chief Risk Agent | Gate C | Open |
| R-14 | Risk | Break-to-risk wiring is partial: `RT-RECON` is not fed from open tickets; `autonomy_suspended` can never be cleared (no `AccountRegistry` method), so a resolved break leaves the account in Supervised until a code change — safe direction, but an operational dead end that invites workarounds | Backend Lead (Chief Risk Agent reviews) | Gate C | Open |
| R-15 | Risk | Ticket resolution requires two different persons but not different lines (unlike Kill Switch deactivation); two 1st-line operators can close an S1 break | Chief Risk Agent / Trading Risk Committee (decide rule) | Gate C | Open |
| O-15, H-07 | carried | on-call for break handling; real broker statements | SRE/Support; Finance + Broker-Connector | F / C | Open |

Assumptions: `SimulatedBroker` fills at reference price ± spread and produces a self-consistent statement; real statements (formats, timing, T+n settlement) are unknown until H-07. Confidence: high for the classification and two-person semantics asserted by TC-RC-001..004 and TC-E2E-J06; none for behaviour against a real broker or for completeness under load. Provenance: code read on 2026-09-07; evidence index sha `HEAD`. Reviewer: Chief Risk Agent pending; approver: Trading Risk Committee pending; IVA verdict pending.
