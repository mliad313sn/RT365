# JOURNEYS

| Owner | Reviewer (different line) | Approving body | First gate | Status |
|---|---|---|---|---|
| Product Director | Frontend & Mobile Lead | Product Council | A | Draft v1.0 |

Each journey maps to sequence diagrams and TEST_CASES/.

| ID | Journey | Persona | Steps | Controls exercised |
|---|---|---|---|---|
| J-01 | Onboard tenant and broker | Tenant admin, Broker-Connector | Create tenant → MFA → connect broker via vault → capability discovery → health check | FR-01, FR-02 |
| J-02 | Register and validate a strategy | Quant, Model Risk, IVA | Pre-register → backtest → validation → reproduction → MRC approval → shadow | FR-06, FR-08, C7, P2 |
| J-03 | Supervised order | Trader | Signal → intent → eligibility → risk → approval queue → execute → fill → reconcile | P1, FR-11, FR-12, FR-13 |
| J-04 | Bounded autonomous order | System | Same as J-03 without approval, inside envelope | P1, C4 |
| J-05 | Risk breach and halt | Risk officer | Runtime monitor → HALT event → Kill Switch → cancel open orders → notify → two-person restore | P4, FR-17 |
| J-06 | Reconciliation break | Operations | EOD reconcile → break → Supervised → ticket → resolve → audit | P6, FR-14 |
| J-07 | Enable a market | Compliance, Legal | Hypothesis → legal record → certification → checklist tests → dual-key flag | P5, C6 |
| J-08 | Audit review | Auditor | Correlation-ID search → decision record → broker ack → evidence export | FR-16 |
