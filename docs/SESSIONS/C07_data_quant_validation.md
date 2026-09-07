# Session packet C07 — Data & Quant Validation (blueprint 08)

| Session | Date | Environment | Status | Documented by |
|---|---|---|---|---|
| C7 | 2026-09-07 | dev/sim only | Committee working draft; not a release artefact | Program Orchestrator (recommends, never approves) |

Nothing in this packet enables a market, strategy or autonomy. Backtest metrics inform decisions; they do not prove future profitability [Source: 08]. Numeric sim-policy values (freshness budgets, outlier 20 %, cost bps) are fixtures [Open: O-07].

## 1 Roles

| Role in session | Person/role | Line |
|---|---|---|
| Accountable | Quant Research Lead (research), Data Architect (data) | 1st / Architecture |
| Builder (code) | Backend Lead — `services/backtest`, `services/strategy`; Data Engineering Lead — `services/market-data`, `connectors/data-providers` | 1st |
| Consulted | Data Engineering Lead, Model Risk Lead | 1st / 2nd |
| Challenger | Model Risk Lead (independent of Quant Research; challenges leakage, pre-registration, cost model) | 2nd |
| Assurance / IVA | Model Risk Committee; Independent Validation Agent (independent reproduction, Gate D) | 3rd |

Segregation: author != reviewer != approver; nothing here is self-certified. The Quant Research Lead cannot validate own backtests; `PROMOTER` in `services/strategy/strategy_service/registry.py` encodes this (VALIDATED by Model Risk, REPRODUCED by IVA, owner may not validate/reproduce/approve own strategy).

## 2 Purpose

- [Source: 08] Data controls from source contracts through reproducible snapshots; backtest acceptance (realistic costs, train/validation/test separation, out-of-sample, walk-forward, parameter stability, benchmark, stress periods, independent reproduction); minimum metric set; metrics do not prove future profitability.
- [Source: 00] Bitemporal defence against look-ahead: any backtest may only see what was knowable at decision time.
- [Committee] Single code path (ADR-008): the backtest runner drives the same eligibility, risk, OMS and simulated-broker code as the sim pipeline.
- [Committee] Pre-registration before any backtest; unregistered results are exploratory and cannot be recorded.
- [Open: O-12] data licensing for derived/redistributed data; [Open: O-13] time-series/snapshot storage cost model; [Open: O-06] evaluation dataset ownership; [Open: O-21], [Open: O-22] raised below.

## 3 Decisions and ADRs

| ID | Decision | Alternatives considered | Why chosen | Status |
|---|---|---|---|---|
| ADR-008 (docs/ADRs/ADR-008.md) | Single code path: `BacktestRunner` (`services/backtest/backtest_engine/runner.py`) is handed callables that run the production pipeline; `run_sim_backtest` (`apps/web/web_bff/platform.py`) builds a fresh sim platform in `AccountMode.BACKTEST` and replays bars through `run_intent` | (a) vectorised research backtester (fast, but risk/eligibility divergence is invisible); (b) containerised replay of production binaries (closest to prod; reserved for IVA reproduction, Gate D) | Divergence between backtest and paper is itself a defect [Committee C7 §3]; proven by TC-BT-001 | Accepted (ARB) |
| ADR-011 [Committee] | Bitemporal store with hard failure: `BitemporalStore.latest/series` raise `LookAheadViolation` when `as_of > knowledge_ts` (`services/market-data/market_data/store.py`) | (a) single-timestamp store with a "cutoff" argument by convention; (b) immutable daily snapshot files | Convention can be forgotten; files lose intraday knowledge time. Structural defence for R-03 | Proposed, pending ARB |
| ADR-012 [Committee] | Pre-registration gate in code: `StrategyRegistry.promote(..., BACKTESTED)` raises `ControlDenied` unless `pre_registration` is set; `PreRegistration.hypothesis_hash` travels into `BacktestReport.hypothesis_hash` | (a) pre-registration recorded only in the strategy card; (b) external lab-notebook system | (a) unenforceable; (b) adds a vendor dependency before O-05 is settled | Proposed, pending Model Risk Committee |
| ADR-013 [Committee] | Versioned cost model `CostModel` with `scaled()` producing labelled ×1.5/×2 variants (`costs.py`); `latency_bars=1` so decisions never execute on the signal bar | (a) broker fee schedule only; (b) per-venue empirical cost curves | (a) omits slippage/latency; (b) needs licensed data [Open: O-12] | Proposed, pending Model Risk Committee |
| D-C7-1 [Committee] | Point-in-time instrument master: `InstrumentMaster.universe(as_of, include_delisted=True)` keeps delisted names (`instruments.py`) | (a) current-listing universe; (b) vendor survivorship-free files | (a) survivorship bias; (b) [Open: O-12] | Proposed, pending Data Architect |
| D-C7-2 [Committee] | Provenance is an enum stamped at ingest (`Provenance.SIMULATED` for the sim feed; `TRUSTED_FOR_DECISIONS` = licensed or simulated, `libs/core/rtcore/provenance.py`) and re-checked by the risk engine (RK-FRESH-PROV) | (a) free-text source field; (b) trust every configured feed | Enum + engine check make "simulated" impossible to relabel as licensed | Proposed, pending Data Architect |

## 4 RTM rows

| Requirement | Architecture element | Implementation owner | Control | Test IDs | Evidence path | Gate |
|---|---|---|---|---|---|---|
| FR-03 | `MarketDataService.ingest` (entitlement → point-in-time instrument → outlier → provenance → bitemporal store) | Data Engineering Lead | Provenance/timestamps on every snapshot; entitlement denial audited (`market.entitlement.denied`) | TC-MD-001 `test_bar_stored_with_timestamps_and_provenance`; TC-MD-003 `test_outlier_backdated_and_unentitled_data` | `test/quartets/test_tc_md_marketdata.py`; `test/evidence/evidence_index.json` | C |
| FR-04 (depth where licensed) | `SimulatedFeed.entitled_field("depth")` gates bid/ask in `ingest` | Data Engineering Lead | Depth hidden when entitlement absent | GAP — no dedicated TC; TC-AI-001 masks depth on the tool path only | `connectors/data-providers/data_providers/simulated.py` | C |
| NFR-FRS-01 | Risk engine freshness check (`services/risk/risk_engine/engine.py` RK-FRESH/-CLOCK/-QUALITY/-PROV/-INTENT) fed by `MarketDataService.for_decision` | Backend Lead | Stale → REJECTED; recovery without manual step | TC-MD-002 `test_stale_beyond_budget_rejected`; TC-MD-004 `test_feed_restored_next_intent_passes` | `test/quartets/test_tc_md_marketdata.py` | C |
| FR-08 | `BacktestRunner`, `run_sim_backtest`, `BitemporalStore.snapshot_id_for_range` | Quant Research Lead (Backend Lead builds) | Same snapshot → identical `fills_hash`/`decisions_hash`; cost sensitivity | TC-BT-001 `test_same_snapshot_identical_fills_and_decisions`; TC-BT-002 `test_cost_sensitivity_runs_change_results` | `test/integration/test_backtest_single_code_path.py` | C |
| FR-08 / R-03 | `LookAheadViolation` in store; `history()` in `run_sim_backtest` reads with `knowledge_ts = bar_ts + 1 s` | Data Architect | Look-ahead structurally impossible | TC-BT-003 `test_look_ahead_is_structurally_impossible` | same | C |
| FR-06 | `StrategyRegistry` lifecycle (`LIFECYCLE`, `PROMOTER`, `GATE_FOR`), `rollback` | Quant Research Lead | Pre-registration, owner segregation, gate-bound promotion, rollback retires versions | TC-BT-004 `test_strategy_lifecycle_pre_registration_and_segregation` | same | C |
| FR-09 | `Signal` schema `evidence_refs: min_length=1` (`services/strategy/strategy_service/signals.py`) | Backend Lead | Signal without evidence is schema-invalid | `test_signal_without_evidence_is_schema_invalid` (untagged — needs a TC ID) | same | D |
| FR-06 (scope screen) | `StrategyRegistry.register` → `screen_strategy_declaration` | Backend Lead | Manipulation-capable / out-of-scope declarations rejected at registration | TC-CP-005 `test_surveillance_patterns_and_registration_screen` | `test/quartets/test_tc_cp_eligibility.py` | D |

## 5 Threat-model delta

| Threat | Boundary | Control in this build | Test | Residual / owner |
|---|---|---|---|---|
| T-03 Poisoned market data | B7 | Outlier jump > fixture 20 % → `DataQuality.SUSPECT` + `market.quality.outlier` audit; engine rejects with RK-FRESH-QUALITY | TC-MD-003 | Cross-source check not built; single sim feed. Data Architect |
| R-03 Look-ahead / leakage | research → decision | ADR-011 hard failure; decision time = bar + 1 s | TC-BT-003, TC-MD-003 | IVA reproduction on separate infra still open (Gate D). Model Risk Lead |
| T-C7-1 Survivorship bias (new) | instrument master | `universe(include_delisted=True)`; `get(as_of)` returns None for delisted | TC-MD-001 | No delisting event feed; sim fixture `SIMDELISTED` only. Data Architect |
| T-C7-2 Entitlement bypass (new) | provider → tenant | `DataProvider.entitled` checked before storing; `ControlDenied` + audit | TC-MD-003 | Entitlement register is in-memory; licences [Open: O-12]. Legal Agent |
| T-C7-3 Unregistered / p-hacked results reaching MRC (new) | quant → MRC | ADR-012; `hypothesis_hash` in report | TC-BT-004 | Hash of pre-registration is not anchored in the audit chain until `strategy.pre_registered` event; acceptable. Model Risk Lead |
| T-C7-4 Backtest/production cost divergence (new) | runner → ledger | Commission+slippage applied by mutating `ledger.book(ACCOUNT).cash` in `run_sim_backtest.submit_and_process`; spread via `broker.spread_bps` | TC-BT-002 (monotonic only) | Financing, borrow, partial fills, delistings in `CostModel` fields but not applied by the runner → R-05. Quant Research Lead |

## 6 Control quartet per critical control

| Control | Positive | Negative | Abuse | Recovery |
|---|---|---|---|---|
| Look-ahead defence (bitemporal read) | TC-BT-001 `test_same_snapshot_identical_fills_and_decisions` | TC-MD-002 `test_stale_beyond_budget_rejected` | TC-BT-003 `test_look_ahead_is_structurally_impossible`; TC-MD-003 (backdated read raises) | TC-MD-004 `test_feed_restored_next_intent_passes` |
| Pre-registration and owner segregation | TC-BT-004 (pre_register → BACKTESTED) | TC-BT-004 (promote without pre-registration → `ControlDenied`) | TC-BT-004 (owner self-validates; trader role promotes; no gate) | TC-BT-004 (`rollback` retires versions, audited `strategy.rollback`) |
| Cost sensitivity ×1.5 / ×2 | TC-BT-002 (labelled `cost-v0.1-simx1.5`, `x2`) | TC-BT-002 (returns non-increasing with cost) | GAP — no test that a report with unlabelled/edited cost version is rejected | GAP |
| Provenance and entitlement | TC-MD-001 (`provenance == simulated`) | TC-RK-010 `test_each_pre_trade_control_fails_with_its_reason_code` (RK-FRESH family) | TC-MD-003 (unentitled tenant denied) | GAP — no test for entitlement restored |
| Survivorship (point-in-time universe) | TC-MD-001 (`SIMDELISTED` in universe, `get` → None) | TC-RK-010 (RK-INSTR-PIT) | GAP | GAP |
| Replay determinism of fills | TC-BT-001 (`fills_hash`, `decisions_hash`, `data_snapshot_id` equal) | GAP — no test that a changed snapshot changes the hash | GAP | GAP |

## 7 Evidence list

| Evidence | Path |
|---|---|
| Bitemporal store, look-ahead exception | `services/market-data/market_data/store.py` |
| Ingest pipeline, outlier flag, entitlement, provenance | `services/market-data/market_data/service.py`; `connectors/data-providers/data_providers/base.py`, `simulated.py` |
| Point-in-time instrument master; session calendar | `services/market-data/market_data/instruments.py`, `calendar.py` |
| Runner, cost model, metrics, disclaimer text | `services/backtest/backtest_engine/runner.py`, `costs.py`, `metrics.py` |
| Strategy lifecycle, pre-registration, promoter matrix | `services/strategy/strategy_service/registry.py`; explainability contract `signals.py` |
| Composition of backtest on production pipeline | `apps/web/web_bff/platform.py` (`run_sim_backtest`, `run_sim` MCP tool `run_simulation`) |
| Tests and evidence records (104 records, all `passed`, environment `dev`, generated 2026-09-07T17:28:57Z) | `test/quartets/test_tc_md_marketdata.py`; `test/integration/test_backtest_single_code_path.py`; `test/evidence/evidence_index.json`; `docs/TEST_CASES/EVIDENCE_REPORT.md` |
| Card templates (no instances yet) | `docs/STRATEGY_CARDS/TEMPLATE.md`; `docs/MODEL_CARDS/TEMPLATE.md` |
| Data model and dictionary | `docs/DATA_MODEL.md`; `docs/DATA_DICTIONARY.md`; `docs/DATA_FLOWS.md` |
| Governance | `docs/COMMITTEE_DEEP_DIVE.md` §C7, P2; `docs/ADRs/ADR-008.md`; `goals/build/E08_strategy_backtesting.md` |

## 8 RAID entries, assumptions, confidence, provenance

| ID | Type | Item | Owner | Needed by | Status |
|---|---|---|---|---|---|
| O-21 | Gap | Walk-forward, scenario, Monte Carlo, parameter-stability, benchmark and stress-period runs (E08 scope, [Source: 08]) are not implemented; only replay + cost scaling exist | Quant Research Lead | Gate D | Open |
| O-22 | Gap | `signals.py` cites `docs/STRATEGY_CARDS/strat-sma-xover.md`, which does not exist; no model card instance for `rule-sma`; only templates | Quant Research Lead / Model Risk Lead | Gate C | Open |
| R-05 | Risk | Cost application in `run_sim_backtest` bypasses `Ledger.apply_fill(fee=...)` and ignores financing/borrow/partial-fill fields of `CostModel`; backtest may understate cost vs sim/paper (ADR-008 partially honoured) | Quant Research Lead (Backend Lead fixes) | Gate D | Open |
| O-12, O-13, O-06, R-03 | carried | see `docs/RAID_LOG.md` | — | — | Open |

Assumptions: the sim feed (`SimulatedFeed`, seed 7, Gaussian walk) is a fixture with no relation to any market; `SmaCrossoverStrategy` exists only to exercise the envelope. Confidence: high that the cited controls behave as the tests assert in dev; low for anything about real data, licences or performance (none evidenced). Provenance: code read from the working tree on 2026-09-07; evidence index at `test/evidence/evidence_index.json` (git sha recorded as `HEAD`, exit status 0). No item here is approved; review by Model Risk Lead, then IVA, is required before any RTM row is marked closed.
