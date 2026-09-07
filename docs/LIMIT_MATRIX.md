# LIMIT_MATRIX

| Owner | Reviewer (different line) | Approving body | First gate | Status |
|---|---|---|---|---|
| Chief Risk Agent | Compliance Agent | Trading Risk Committee | C | Draft v1.0 |

Hierarchy platform > tenant > account > strategy > instrument; effective limit = minimum [Committee]. All numeric values [Open: O-07]; the structure is fixed now.

| Metric | Platform | Tenant | Account | Strategy | Instrument | Unit | Reason code |
|---|---|---|---|---|---|---|---|
| Max notional per order | | | | | | ccy | RK-CAP |
| Max position per instrument | | | | | | qty/ccy | RK-CAP |
| Gross exposure | | | | | | % NAV | RK-EXP |
| Net exposure | | | | | | % NAV | RK-EXP |
| Concentration (single name / sector / country / currency) | | | | | | % | RK-CONC |
| Leverage | | | | | | × | RK-LEV |
| Daily / weekly / monthly loss limit | | | | | | ccy or % | runtime HALT |
| Max drawdown (peak-to-trough) | | | | | | % | runtime HALT |
| Orders per minute / open-order count | | | | | | n | RK-RATE |
| Price collar | | | | | | % from reference | RK-COLLAR |
| Min liquidity (ADV %) | | | | | | % | RK-LIQ |
| Freshness budget | | | | | | ms/s | RK-FRESH |
| Capital envelope (bounded autonomy) | | | | | | ccy | envelope |
Change log: maker, checker, cooling period end, policy_version.
