# SLO_SLA

| Owner | Reviewer (different line) | Approving body | First gate | Status |
|---|---|---|---|---|
| SRE Lead | Chief Risk Agent | ARB, Executive Steering | E | Draft v1.1, 2026-09-08 — measurement readiness recorded per SLI; **no target set or changed**; **reviewer signature pending**; not accepted |

SLIs fixed now; targets after measured baselines and business approval [Source: 10] [Open: O-03].

**Measurement readiness [Committee], read against the tree at `40bcb51`.** The "measurement point" column names the **component** an SLI belongs to. It has never named an emission point, and only one of the nine has one: a search of the whole non-test tree finds six metric call sites, of which one is an SLI (`killswitch.time_to_halt_s`). The new column below records that fact per row so that no gate reader assumes these baselines can be collected by running the system. **Instrumentation is a prerequisite of the Gate C baseline programme, not part of it** (docs/SESSIONS/REVIEW_2026-09-08_capacity_sre.md §4 step 0). Nothing here is a target and no target cell is changed [Open: O-03].

| SLO candidate [Source: 10] | SLI definition | Measurement point (component) | Emission point in the tree today | Target | Safety semantic [Committee] |
|---|---|---|---|---|---|
| Availability | successful control-plane decisions / total | Risk service | **none** — no decision counter is recorded [Open] | TBD | fail closed, never fail open |
| Market-data freshness | market_ts age at snapshot use | Risk RK-FRESH | **none** — freshness is computed ad hoc for one dashboard field and never observed as a metric [Open] | TBD | breach → autonomy suspended |
| Signal latency | snapshot → signal | Strategy | **none** — a `signal` span exists in the synthetic probe only; its duration is never observed [Open] | TBD | informational |
| Risk-decision latency | intent enqueue → decision write, p99 per cell | Risk | **none** — no span duration is observed; and the registry's histograms are unbounded lists sorted per query, so a p99 is not windowed [Open: SRE-R4] | TBD | breach → autonomy suspended |
| Order acknowledgement | command → broker ack | Execution | **none** [Open] | TBD | breach → cancel-only review |
| Time-to-halt (D-044) | Kill Switch engage → last cancel and revocation recorded; 100% of later approvals blocked | Kill Switch service (`killswitch.time_to_halt_s`), drill for operator-action → engaged | **yes** — the only SLI emitted anywhere (`KillSwitchHooks.observe`) | [Open: Q-16-1, set at the first drill] | informational; block rate is a hard assertion (TC-KS-009) |
| Event lag | produce → consume | bus | **none, and no producer or consumer exists**: a Kafka-compatible broker runs in the dev/sim compose stack but nothing publishes to or consumes from it [Open: R-05] | TBD | autoscale trigger |
| Reconciliation completeness | reconciled positions / total by EOD+T | Reconciliation | **none** [Open] | TBD | break → Supervised |
| Alert delivery | alert → operator ack | Notification | **none, and not computable as defined**: the alert router records `(channel, alert)` with no timestamp, there is no acknowledgement path and no notification component exists [Open: SRE-R5] | TBD | tested daily |

**Direction is a safety property and must be declared, not inferred** [Committee] [Open: SRE-R2]. `observability/rtobs/slis.py` currently infers which way a breach lies from the SLI's *name* (greater-than for names containing "latency", "freshness" or "lag", less-than otherwise), so `alert_delivery_s` and `time_to_halt_s` would be compared inverted once a target existed — a fast halt breaching and a slow one not. This is latent only because every target is `null`. A declared `direction:` field with a control quartet is owed **before O-03 closes**, not with it: the first target set on an inferred direction is the first inverted alarm. **No target may be set from this seat: a target needs a measured baseline and business approval** (O-03) [Source: 10].
