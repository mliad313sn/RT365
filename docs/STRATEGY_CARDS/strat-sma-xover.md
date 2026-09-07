# Strategy Card — strat-sma-xover v0.1  [Source: 08]
| Field | Value |
|---|---|
| Owner (Quant) / Validator (Model Risk) / Reproducer (IVA) | quant.fixture (Quant Research Lead) / **not validated** / **not reproduced** — status PROPOSED in the registry |
| Purpose | Simulation-only rule strategy (fast SMA 3 over slow SMA 8, long/flat) used to exercise the control envelope end to end. It is a test fixture, not a candidate for any market. |
| Pre-registered hypothesis (date, hash) | None recorded outside tests; `test_strategy_lifecycle_pre_registration_and_segregation` shows the pre-registration path (hypothesis hash computed by `PreRegistration.hypothesis_hash`) |
| Universe (point-in-time) and data snapshot ID | SIMEQ1 on venue SIMX (simulated feed, seed 7); data snapshot id reported per run by `run_sim_backtest` (`ds_…` = hash of the bars in range) |
| Cost model version | cost-v0.1-sim: commission 1 bps, spread 5 bps, slippage 2 bps, 1-bar latency, financing/borrow placeholders; ×1.5 and ×2 runs in `test_cost_sensitivity_runs_change_results` |
| Split scheme and walk-forward windows | [Open] — not applicable to a fixture; the registry enforces that a split scheme is declared at pre-registration |
| Metrics (return, volatility, max drawdown, turnover, exposure, hit rate, profit factor, tail loss, trades) | Computed by `backtest_engine.metrics.compute_metrics` and reported by the `run_simulation` MCP tool. Values are not reproduced here on purpose: they are simulated, informational and **do not prove future profitability** [Source: 08]. |
| Parameter stability evidence | none (fixture) |
| Stress periods | none (fixture) |
| Benchmark comparison | none (fixture) |
| Cost sensitivity ×1.5 / ×2 | mechanism evidenced by test; monotone non-increasing return with cost factor asserted |
| Known failure modes | whipsaw in ranging markets; single instrument; no regime awareness |
| Manipulation-pattern screen result | PASS — `StrategyDeclaration` declares no two-sided quoting, no near-close trading, no replication, no advice (`screen_strategy_declaration`) |
| Independent reproduction result | not performed (IVA) |
| MRC approval / status | none; registry status PROPOSED. Promotion path and segregation enforced by `strategy_service.registry.StrategyRegistry.promote` |
Metrics inform decisions; they do not prove future profitability [Source: 08].
