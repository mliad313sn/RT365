# PERFORMANCE_PLAN

| Owner | Reviewer (different line) | Approving body | First gate | Status |
|---|---|---|---|---|
| Performance & Chaos Lead | SRE Lead | ARB | C | Draft v1.0 |

Objectives: produce baselines for NFR targets [Open: O-03] and prove no shedding of Control/Execution planes.
| Test | Scenario | SLI measured | Pass criterion |
|---|---|---|---|
| Load | steady intents at N× expected per cell | risk-decision p99, event lag | no fail-open; latency within budget once set |
| Spike | 10× burst of market events | freshness, shedding order | analytics shed first; control/execution intact |
| Soak | 24h | memory, lag drift | no degradation |
| Latency | broker sandbox round-trip | order ack | baseline recorded per broker |
| Failover | executor lease transfer under load | duplicate orders | zero duplicates |
| Capacity | scale to cell limit | autoscale on lag/latency | capacity model validated (Gate B) |
