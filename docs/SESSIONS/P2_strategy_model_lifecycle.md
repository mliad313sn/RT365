# Session P2 — Strategy and Model Lifecycle (blueprint 04, 08; Committee)

**Environment:** dev/sim only. The only strategy is a simulation-only SMA crossover that exists to exercise the control envelope; its backtest metrics are informational and are never evidence of future profitability [Source: 08]. Documented by the Program Orchestrator (1st line, recommends, never approves).

## 1 Roles

| Function | Role (line) | Basis |
|---|---|---|
| Accountable | Quant Research Lead (1st line, proposes); Model Risk Lead (2nd line, validates and chairs the Model Risk Committee) | COMMITTEE_DEEP_DIVE §P2, roster rows 5–6 |
| Consulted | Chief Risk Agent, Data Architect, Backend Lead, Compliance Agent (registration screen) | RACI |
| Builder | Backend Lead (1st line) — `services/strategy/strategy_service/{registry.py,signals.py}`, `services/backtest/backtest_engine/{runner.py,costs.py,metrics.py}`, `apps/web/web_bff/platform.py::run_sim_backtest` | RACI |
| Challenger (different line) | Model Risk Lead (2nd line) — challenged leakage defence, pre-registration and owner segregation | Protocol §1.4 rule 4 |
| Assurance / IVA | Independent Validation Agent (independent reproduction is a lifecycle state, `REPRODUCED`, that only the IVA may set) | COMMITTEE_DEEP_DIVE §P2 |

Statement: author != reviewer != approver. The Quant Research Lead cannot validate own backtests (roster row 5); the registry enforces it in code (`promote` refuses the owner for VALIDATED/REPRODUCED/CHALLENGER). Backend Lead built; Model Risk Lead challenges; IVA reproduces; Model Risk Committee approves. Nothing here is self-certified.

## 2 Purpose

- [Source: 04] Model lifecycle: register -> validate (evaluation datasets, hallucination and adversarial tests) -> shadow as challenger -> Model Risk Committee approval -> monitor drift -> champion/challenger -> retire/rollback; no model promoted on backtest metrics alone.
- [Source: 08] Single code path for backtest and production; costs (commission, spread, slippage, latency, financing, borrow, partial fills); minimum metric set; leakage and look-ahead defence.
- [Committee] Lifecycle as a monotonic state machine (`StrategyStatus` PROPOSED -> PRE_REGISTERED -> BACKTESTED -> VALIDATED -> REPRODUCED -> CHALLENGER -> SHADOW -> PAPER -> SUPERVISED_PILOT -> CAPPED_AUTONOMOUS -> RETIRED, or REJECTED) with role-segregated `PROMOTER`s and gate requirements (`GATE_FOR`: PAPER=C, SUPERVISED_PILOT=D, CAPPED_AUTONOMOUS=E); pre-registration (hypothesis, universe, period, split, success criteria) hashed before any backtest; data snapshot pinned; backtest runs the production pipeline bar by bar (ADR-008) with `knowledge_ts` gating (`LookAheadViolation`).
- [Open: O-05] providers/hosting; [Open: O-06] evaluation datasets; [Open: O-07] policy numbers used by backtest decisions are fixtures; R-03 leakage risk.

## 3 Decisions and ADRs

| # | Decision | Alternatives compared | Why chosen | Evidence |
|---|---|---|---|---|
| P2-D1 | Single code path: `run_sim_backtest` builds a fresh sim platform in `AccountMode.BACKTEST` and calls `p.run_intent` (schema -> eligibility -> risk -> gateway -> simulated broker) per bar; `BacktestRunner` receives callables only. | ADR-008: (a) separate research engine; (b) shared library; (c) chosen: same services in sim mode. | Divergence hides defects; TC-BT-001 proves replay determinism (`fills_hash`, `decisions_hash`). | ADR-008; TC-BT-001 |
| P2-D2 | Look-ahead structurally impossible: strategy history is `store.series(..., knowledge_ts=decision_time)`; `BitemporalStore.latest/series` raise `LookAheadViolation` when `as_of/end > knowledge_ts`; decisions occur one second after the bar and execute on the next bar (`CostModel.latency_bars=1`). | (a) Convention "do not peek"; (b) pre-sliced data frames per bar; (c) chosen: bitemporal store with knowledge-time enforcement. | (a) is R-03 unmitigated; (b) does not prevent access to future rows. | TC-BT-003 |
| P2-D3 | Lifecycle registry with segregation: owner cannot validate/reproduce/approve own strategy; only IVA may set REPRODUCED; agents cannot change status; unregistered results cannot be recorded (BACKTESTED requires pre-registration); `rollback` retires all other live versions and audits. | (a) Free-text status field with review notes; (b) chosen: state machine + `PROMOTER` map + gate check. | Makes the P2 process a control rather than a procedure. | **Proposed ADR-018** [Committee] "Strategy lifecycle state machine with role-segregated promotion and pre-registration"; TC-BT-004 |
| P2-D4 | Registration screen for out-of-scope/manipulation-capable declarations runs inside `StrategyRegistry.register` (C6-D3). | see C6 | — | TC-CP-005 |
| P2-D5 | Cost sensitivity as a first-class run (`CostModel.scaled`, version suffix `x1.5`/`x2`); report carries `DISCLAIMER`, `data_snapshot_id`, `cost_model_version`, `hypothesis_hash`. | (a) Single cost assumption; (b) chosen: scaled runs labelled in the report. | [Source: 08] cost sensitivity is a validation input; the disclaimer prevents R-04 wording. | TC-BT-002 |
| P2-D6 | Deterministic sample strategy (`SmaCrossoverStrategy`) and deterministic `intent_id` (uuid5 over strategy/version/account/instrument/ts/side) so replays produce identical intents. | (a) Random intent ids; (b) chosen: uuid5. | Replay equality is only meaningful with stable ids. | TC-BT-001 |

## 4 RTM rows

| Requirement | Architecture element | Implementation owner | Control | Test IDs | Evidence path | Gate |
|---|---|---|---|---|---|---|
| FR-06 (registry, versioning, approvals, rollback) | `StrategyRegistry`, `LIFECYCLE`, `PROMOTER`, `GATE_FOR`, `rollback` | Backend Lead | Segregated promotion; gate evidence; rollback audited | TC-BT-004 | `test/integration/test_backtest_single_code_path.py` | C |
| FR-08 (backtest, replay, sensitivity) | `BacktestRunner`, `CostModel`, `compute_metrics`, `run_sim_backtest` | Backend Lead | Same snapshot -> identical fills; cost sensitivity | TC-BT-001, TC-BT-002 | same; `services/backtest/backtest_engine/*` | C |
| FR-08 / R-03 (leakage) | `BitemporalStore` knowledge-time gating | Data Engineering Lead / Backend Lead | `LookAheadViolation` | TC-BT-003 | `services/market-data/market_data/store.py` | D |
| FR-09 (explainability) | `Signal` (evidence_refs, confidence, provenance) | Backend Lead | Signal without evidence is schema-invalid | `test_signal_without_evidence_is_schema_invalid` | `services/strategy/strategy_service/signals.py` | D |
| FR-07 (sandbox isolation) | `run_simulation` MCP tool -> `run_sim_backtest` on a fresh platform; MCP egress | Backend Lead | No vault/broker route | TC-AI-005, TC-NET-003 | C3 packet | B |
| [Source: 04] drift monitoring | `RT-DRIFT` runtime halt, `model.drift.v1` schema | Backend Lead | Signals suspended on drift | TC-RK-016 (fixture) | `contracts/events/model.drift.v1.json` | D — GAP: no drift computation exists |
| [Source: 01] manipulation-capable strategies excluded | `screen_strategy_declaration` at registration | Backend Lead | Rejected with CP-SCOPE/CP-SURV codes | TC-CP-005 | C6 packet | D |

## 5 Threat-model delta

| Threat | Boundary | Control | Test | Owner |
|---|---|---|---|---|
| T-04 Model supply chain | B8 | model_id/model_version on signal and intent; registry audit; artefact signing pending (O-33) | TC-BT-004 (partial) | Model Risk Lead |
| T-07 Insider misuse (self-validation) | B2 | Owner cannot validate/reproduce/approve; IVA-only REPRODUCED | TC-BT-004 | Model Risk Lead |
| T-02 Excessive agency (agent promotes a strategy) | B3 | `promote` refuses non-human actors | GAP — no explicit agent-actor test in TC-BT-004 | MCP Security Agent |
| NEW T-30 Look-ahead leakage inflating results (R-03) | B7 | Bitemporal knowledge-time gating; next-bar execution | TC-BT-003 | Model Risk Lead |
| NEW T-31 Backtest metrics presented as performance claims (R-04) | B1 | `DISCLAIMER` on every report; strategy docs say "not a performance claim" | TC-BT-001 asserts disclaimer text | GTM Lead, Compliance Agent |
| NEW T-32 Post-hoc hypothesis change | B2 | `PreRegistration.hypothesis_hash` recorded before BACKTESTED; report carries `hypothesis_hash` | TC-BT-004 | Model Risk Lead |

## 6 Control quartet per critical control

| Control | Positive | Negative | Abuse | Recovery |
|---|---|---|---|---|
| Single code path / replay determinism | TC-BT-001 `test_same_snapshot_identical_fills_and_decisions` | TC-BT-002 `test_cost_sensitivity_runs_change_results` (different costs -> different, labelled results) | TC-BT-003 `test_look_ahead_is_structurally_impossible` | GAP — no test that a changed data snapshot id yields a new report identity |
| Lifecycle segregation | TC-BT-004 (Quant -> Model Risk -> IVA -> MRC path succeeds with gate) | TC-BT-004 (no pre-registration, no gate, wrong role denied) | TC-BT-004 (owner self-validation denied); GAP for agent actor | TC-BT-004 (`rollback` retires versions, audited) |
| Explainability contract | TC-AI-001 (intent with evidence accepted) | `test_signal_without_evidence_is_schema_invalid` | TC-AI-002 (empty provenance rejected) | GAP |
| Registration screen | TC-CP-005 | TC-CP-005 | TC-CP-005 | GAP — no re-registration after redesign test |
| Drift / champion-challenger | GAP | GAP | GAP | GAP — only a `RT-DRIFT` halt code and event schema exist |

## 7 Evidence list

- `docs/STRATEGY_CARDS/TEMPLATE.md`, `docs/MODEL_CARDS/TEMPLATE.md` (no filled card exists; `signals.py:50` cites `docs/STRATEGY_CARDS/strat-sma-xover.md`, which is absent), `docs/PROMPT_REGISTRY.md`, `docs/DATA_DICTIONARY.md`, `docs/JOURNEYS.md` (J-02)
- `services/strategy/strategy_service/{registry.py,signals.py}`, `services/backtest/backtest_engine/{runner.py,costs.py,metrics.py}`, `services/market-data/market_data/store.py`, `apps/web/web_bff/platform.py::run_sim_backtest`
- `test/integration/test_backtest_single_code_path.py` (TC-BT-001..004, `test_signal_without_evidence_is_schema_invalid`), `test/quartets/test_tc_cp_eligibility.py::test_surveillance_patterns_and_registration_screen`, `contracts/events/{strategy.signal.v1,model.drift.v1}.json`

## 8 RAID entries, assumptions, confidence, provenance

| ID | Type | Item | Owner | Gate |
|---|---|---|---|---|
| O-39 | Gap | FR-08 partial: walk-forward, scenario, sensitivity beyond cost scaling, and Monte Carlo are not implemented; `PreRegistration.split_scheme` is free text and unenforced | Quant Research Lead, Backend Lead | C |
| O-40 | Gap | Strategy card `docs/STRATEGY_CARDS/strat-sma-xover.md` referenced by code does not exist; no model card; MODEL_CARDS/STRATEGY_CARDS are templates only | Quant Research Lead, Model Risk Lead | D |
| O-41 | Gap | Drift monitoring, champion/challenger comparison and shadow-run signal logging without intents have no implementation beyond the `RT-DRIFT` code and `model.drift.v1` schema | Model Risk Lead, Backend Lead | D |
| R-16 | Risk | `run_sim_backtest` uses `SimulatedFeed` (seed 7) and sim policy fixtures; any metric it produces is meaningless outside the control-envelope test and must not be quoted (R-04) | Model Risk Lead, GTM Lead | continuous |

Assumptions: `TradeIntent`s in backtest carry `data_provenance=["simulated"]`, which the risk engine trusts only because `SIMULATED` is in `TRUSTED_FOR_DECISIONS` for dev/sim; that label must be removed from the trusted set before any environment with licensed data (C3-D4).

Confidence: **high** for the single code path, look-ahead defence and segregated lifecycle (code and tests read); **low** for model governance content (no cards, datasets, drift, providers).

Provenance: [Source: 00, 01, 04, 08] lifecycle, explainability, single code path, costs, metrics; [Committee] state machine, promoters, ADR-018 proposal; [Open] O-05, O-06, O-07, O-39..O-41; R-03, R-04. Evidence cited by path; Model Risk Committee approval pending and never assumed.
