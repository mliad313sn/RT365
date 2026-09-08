# DASHBOARDS

| Owner | Reviewer (different line) | Approving body | First gate | Status |
|---|---|---|---|---|
| SRE Lead | Frontend Lead | ARB | C | Draft v1.1, 2026-09-08 — what each panel can be fed today recorded against the instrumentation that now exists (F-03); **reviewer signature pending**; not accepted |

| Dashboard | Audience | Panels (risk before profit [Source: 09]) |
|---|---|---|
| Global status | all | Kill Switch state per level, mode per account, data freshness, broker health |
| Risk | Risk officer | capital at risk, drawdown, exposure vs limits, HALT events, decision latency |
| Execution | Ops | intent funnel (created→filled), rejects by reason code, duplicates (must be 0), acks |
| Reconciliation | Ops | breaks by type/severity, ageing |
| Model/MCP | Model Risk, MCP Security | drift, tool calls by tool/tenant, denied calls, injection detections |
| SLOs | SRE | all SLIs with error budgets and safety-semantic status |
| Audit | Auditor | correlation-ID search, hash-chain verification status |

**What these panels can be fed today** [Committee], read against the tree at `8f2258e`. A dashboard is a claim that a number exists; these are the numbers that exist.

| Panel | Source that exists | What cannot be drawn yet |
|---|---|---|
| SLOs | eight of nine SLIs emit into the in-process `MetricsRegistry` (`observability/slis.yaml` names the metric per SLI) | **no error budget and no status**: an error budget needs a target, and every target is `null` (O-03). **No exporter and no backend**: the values live in one process's memory and are visible only through that process's own endpoint — a panel outside it has nothing to read [Open: O-18, SRE-R4]. `event_lag_ms` has no emission point at all [Open: R-05] |
| Risk — decision latency | `pipeline.risk_decision_latency_ms` (enqueue → decision write, monotonic, in process) | a p99 over a window: histograms are unbounded lists sorted per query, so the figure is lifetime-to-date and gets more expensive the longer the process runs [Open: SRE-R4] |
| Global status — data freshness | `pipeline.market_data_freshness_s`, observed where a decision used the snapshot | freshness for instruments nothing decided on; ingest-side staleness of an unused feed |
| Execution — acks | `pipeline.order_ack_latency_ms`, measured by the caller around lease + submit | a broker-side round trip: in dev/sim this measures the simulator, and the gateway itself is a protected path |
| Reconciliation | `reconciliation.completeness_pct` per run, conservative, `None` when nothing was compared | "by EOD+T": there is no scheduler and no deadline in the tree |
| Alerts / paging | `alerts.alert_dispatch_s` per channel, `AlertRouter.unacknowledged()`, and `alerts.alert_delivery_s` once an acknowledgement exists | a delivery-time panel with data in it: **nothing acknowledges an alert** — no notification component and no operator acknowledgement path exist, so the honest panel today is "alerts outstanding", not "time to acknowledge" [Open: SRE-R5, O-15] |
| Audit — correlation-ID search | one correlation id per request end to end; the synthetic probe now returns the id its spans are under (F-14) | a **trace** view across services: the tracer is in-process only, with no propagation carrier and no exporter [Open: SRE-R10] |

No panel may display a target, a threshold or an error budget until O-03 closes; a panel that shows a red/green status against a number nobody approved is an invented threshold [Source: 10].
