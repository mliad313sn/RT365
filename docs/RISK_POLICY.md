# RISK_POLICY

| Owner | Reviewer (different line) | Approving body | First gate | Status |
|---|---|---|---|---|
| Chief Risk Agent | Trading Domain Lead | Trading Risk Committee | C | Draft v1.0 |

## Decision contract [Committee, derived from 05]
`decide(intent, account_snapshot, market_snapshot, policy_version) → DecisionRecord` — pure, deterministic, no I/O, no model call. Unavailable inputs → HALTED (fail closed). Outcomes [Source: 05]: APPROVED, REJECTED, REQUIRES_HUMAN_APPROVAL, HALTED; each returns policy version, reason codes, evaluated values, thresholds, timestamp.

## Pre-trade controls [Source: 05]
| # | Control | Reason code prefix | Outcome on fail |
|---|---|---|---|
| 1 | Trading status / account authorisation | RK-AUTH | REJECTED |
| 2 | Whitelist / restricted list | RK-LIST | REJECTED |
| 3 | Market session | RK-SESS | REJECTED |
| 4 | Data freshness | RK-FRESH | REJECTED |
| 5 | Buying power | RK-BP | REJECTED |
| 6 | Position / notional cap | RK-CAP | REJECTED |
| 7 | Gross / net exposure | RK-EXP | REJECTED |
| 8 | Concentration; sector/country/currency exposure | RK-CONC | REJECTED or REQUIRES_HUMAN_APPROVAL per policy |
| 9 | Leverage / margin | RK-LEV | REJECTED |
| 10 | Order-price collar / fat-finger | RK-COLLAR | REJECTED |
| 11 | Duplicate detection | RK-DUP | REJECTED |
| 12 | Open-order count / rate limit | RK-RATE | REJECTED |
| 13 | Liquidity / volume threshold | RK-LIQ | REJECTED or REQUIRES_HUMAN_APPROVAL |
| 14 | Volatility regime | RK-VOL | REQUIRES_HUMAN_APPROVAL |
| 15 | Stop-loss / protective policy | RK-PROT | REJECTED or REQUIRES_HUMAN_APPROVAL |
| 16 | Correlated-risk limits | RK-CORR | REJECTED |
Evaluation: fail-fast order 1→4→instrument validity→5–9→10,13,14→11,12→15,16; all cheap checks still evaluated for a complete reason list [Committee].

## Runtime controls → HALT events [Source: 05]
Daily/weekly/monthly loss limits · peak-to-trough drawdown · abnormal order frequency · slippage · rejection rate · latency · connectivity · model drift · reconciliation breaks · venue health.

## Emergency policy [Source: 05; Committee]
Per account: CANCEL_ONLY (default) | CANCEL_AND_REDUCE | CANCEL_AND_FLATTEN. Reduce/flatten require the separately approved liquidation policy [Open: O-08]. On activation: cancel open orders, block new risk, revoke agent tools, preserve evidence, notify.

## Change control
Limits and policy change only via maker-checker with cooling period; no agent/MCP write path [Source: 00]. Thresholds per asset class/jurisdiction: [Open: O-07].
