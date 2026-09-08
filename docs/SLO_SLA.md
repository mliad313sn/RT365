# SLO_SLA

| Owner | Reviewer (different line) | Approving body | First gate | Status |
|---|---|---|---|---|
| SRE Lead | Chief Risk Agent | ARB, Executive Steering | E | Draft v1.0 |

SLIs fixed now; targets after measured baselines and business approval [Source: 10] [Open: O-03].
| SLO candidate [Source: 10] | SLI definition | Measurement point | Target | Safety semantic [Committee] |
|---|---|---|---|---|
| Availability | successful control-plane decisions / total | Risk service | TBD | fail closed, never fail open |
| Market-data freshness | market_ts age at snapshot use | Risk RK-FRESH | TBD | breach → autonomy suspended |
| Signal latency | snapshot → signal | Strategy | TBD | informational |
| Risk-decision latency | intent enqueue → decision write, p99 per cell | Risk | TBD | breach → autonomy suspended |
| Order acknowledgement | command → broker ack | Execution | TBD | breach → cancel-only review |
| Time-to-halt (D-044) | Kill Switch engage → last cancel and revocation recorded; 100% of later approvals blocked | Kill Switch service (`killswitch.time_to_halt_s`), drill for operator-action → engaged | [Open: Q-16-1, set at the first drill] | informational; block rate is a hard assertion (TC-KS-009) |
| Event lag | produce → consume | bus | TBD | autoscale trigger |
| Reconciliation completeness | reconciled positions / total by EOD+T | Reconciliation | TBD | break → Supervised |
| Alert delivery | alert → operator ack | Notification | TBD | tested daily |
