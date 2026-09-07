# CHAOS_PLAN

| Owner | Reviewer (different line) | Approving body | First gate | Status |
|---|---|---|---|---|
| Performance & Chaos Lead | Backend Lead | ARB | E | Draft v1.0 |

Faults [Source: 11] + [Committee]:
| Fault | Injected where | Expected behaviour | Runbook |
|---|---|---|---|
| Network partition between planes | B3/B4 | Control plane fails closed; no orders | risk engine unavailable |
| Stale feed | Market Data | RK-FRESH rejections; autonomy suspended if SLO breached | data stale |
| Broker timeout | B5 | retries idempotent; no duplicates; connection health alert | broker disconnected |
| Message duplication | bus | inbox dedupe; single business effect | duplicate order |
| Executor crash with in-flight order | Execution | standby with new fencing token; single order | duplicate order |
| Clock skew beyond budget | any service | stale-data rejection + alert | data stale |
| Policy store unavailable | Risk | HALTED outcomes | risk engine unavailable |
| Regional cell loss | Cloud | DR plan; RPO/RTO measured | regional failure |
