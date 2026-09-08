# BUILD_E12 — Observability truth: the probe that lied, the direction that was guessed, and eight indicators that could not be measured (F-14, F-07, F-03)

| Field | Value |
|---|---|
| Session | BUILD_E12, 2026-09-08 |
| Epic | E12 — Observability & SRE (`goals/build/E12_observability_sre.md`) |
| Findings addressed | **F-14** (SRE-R10), **F-07** (SRE-R2), **F-03** (SRE-R5, and part of SRE-R4) from `docs/SESSIONS/REVIEW_2026-09-08_capacity_sre.md`; concern **PO-S4** |
| Branch / commits | `build/e12-observability-truth` — `8f2258e` (tests first, then implementation), `beef208` (owned documents), plus this packet |
| Base | `caab32e` on `claude/project-owner-agent-setup-hi3xqu` |
| Environment | dev/sim only. Nothing here enables a market, a strategy, a venue or autonomy [Source: 00] |
| `make all` | green — lint, ruff format (150 files), mypy (105 source files), 21 event schemas, network policy, tool registry, 67 agents, secret scan (597 files), **228 tests passed** (220 before), evidence **208 records / 23 areas with a full quartet** |
| `rt365 probe --env sim` | exit 0, and its output is now true (§6) |
| Targets | **none set, none proposed.** Every `target:` in `observability/slis.yaml` remains `null` [Open: O-03] |

> This packet is a build recommendation. It approves nothing, closes no register item and signs no document. No SLO target, threshold, capacity figure, latency, recovery time, broker capability or regulatory status is asserted anywhere in it. Profit is an objective, never a promise [Source: 00].

---

## 1. Roles

| Role | Who | Line |
|---|---|---|
| Author (build) | Build agent E12 (AI), for the SRE Lead | 1st |
| Accountable lead | SRE Lead — owner of `observability/`, SLO_SLA, ALERT_CATALOG, DASHBOARDS, the runbooks | 1st |
| Reporter of the three defects | SRE Lead, reviewing the capacity model (`REVIEW_2026-09-08_capacity_sre.md` F-03, F-07, F-14) | 1st |
| Reviewer (required, **not obtained**) | ARB (2nd line) — the epic's named 2nd-line reviewer | 2nd |
| Reviewer (required, **not obtained**) | Chief Risk Agent — reviewer of record for `docs/SLO_SLA.md` and `docs/ALERT_CATALOG.md`; the breach direction is a risk control | 2nd |
| Reviewer (required, **not obtained**) | Backend Lead — `services/oms`, `services/strategy`, `services/backtest`, `services/reconciliation` and `apps/web` changed here | 1st (different owner) |
| Reviewer (required, **not obtained**) | Security Architect — reviewer of record for `docs/INCIDENT_RESPONSE.md` (RB-15 added) | 2nd |
| Assurance | Independent Validation Agent — may veto this evidence | 3rd |
| Approver | the human Product Owner (D-039). **No approval is recorded here** | — |

Author ≠ reviewer ≠ approver. `services/execution` and `services/risk` are protected paths and **were not touched** (§4, D-05).

---

## 2. Purpose

- **F-14 [Source: REVIEW_2026-09-08_capacity_sre.md §3].** `SimPlatform.synthetic_probe` keyed its spans on `probe-<timestamp>`, computed `missing_spans` under that id and **returned a different one** (`vi.correlation_id`). The operator was handed an id with zero spans while the verdict was computed elsewhere. The probe is the trace-completeness release criterion in `docs/DEPLOYMENT_RUNBOOK.md` step 7, so the criterion was being satisfied under an id no operator ever sees.
- **F-07 [Source: same §3].** `SliCatalog.evaluate` inferred the dangerous direction from the SLI's *name* — `>` for names containing "latency", "freshness" or "lag", `<` otherwise — so `alert_delivery_s` and `time_to_halt_s` were compared **inverted**: a fast halt would breach, a slow one would not. Latent only because every target is `null`. **It had to close before O-03 sets any target**, because a target plus an inverted comparison is worse than no target.
- **F-03 / PO-S4 [Source: same §3 and §10].** The capacity model listed a "measurement point" per SLI, taken faithfully from `observability/slis.yaml`; those entries named a **component**, not a measurement. Exactly one of nine emitted anything (`killswitch.time_to_halt_s`), and `alert_delivery_s` could not be computed even in principle. Instrumentation comes **before** the baseline programme, or every Gate C "baseline" will have been produced by a stopwatch in a test harness and quoted as a property of the platform.
- **The control this session adds** is not a metric. It is: **a report about a system says only what it can show, under the identifier it hands you** [Committee]. A probe that returns an untraceable id, a comparison that guesses which way danger lies, and a configuration file that names a component where a measurement should be are three forms of the same defect.
- **Not delivered here** and still open: no SLO target (O-03), no on-call or notification component (O-15), no telemetry export or backend (O-18), no bounded metric windows (SRE-R4), no trace-context carrier or exporter (SRE-R10 remainder), no bootstrap alert sink (SRE-R1), no bus and therefore no `event_lag_ms` (R-05). §5 states each precisely.

---

## 3. Decisions taken, with the alternatives considered

Recorded here for `docs/DECISION_LOG.md`; **ids are the Program Orchestrator's to assign and none is claimed**. No ADR is proposed: no standard changes — `observability/slis.yaml` gains fields and no existing field changes meaning.

| # | Decision | Alternatives considered | Why this one |
|---|---|---|---|
| **D-01** | **One correlation id end to end, and print both ids.** The probe mints `probe_<uuid>` first, carries it into the intent (so the audit rows and events are under it), records every span under it, computes the verdict under it and returns it. It **also** returns `trace_correlation_id`, and the CLI exits non-zero if the two ever differ | (a) keep two ids and report both explicitly — honest, but it leaves an operator holding two ids at 03:00 and asks a human to do the join a machine can do; (b) key spans on the intent's correlation id, minted inside the queue — the market-snapshot and signal spans happen *before* the intent exists, so the first two stages would be unattributable; (c) return the span id and leave the audit rows under another — moves the lie rather than removing it | One id is the property the runbook actually needs ("take this id to the trace view"). Printing both is cheap defence in depth: if the two ever diverge again the probe says so in its own output and fails, instead of a reviewer having to reproduce it by hand. `IntentQueue.submit` already accepted `correlation_id`; only the composition root did not pass it |
| **D-02** | **"Not reached" is an allowlist, not a caller's word.** `Tracer.verdict(..., not_reached=...)` forgives a declared stage only if it is in `CONDITIONAL_STAGES = ("order_command", "broker_ack")`, is not recorded, and no *later* conditional stage ran | (a) forgive anything the caller declares — turns the completeness check into a self-certification and trains operators to ignore it, which is exactly what F-14 warned about; (b) forgive any stage after the last recorded stage — fails on this pipeline, because `audit` runs on every path and sits after both conditional stages, so the tail rule would forgive nothing; (c) keep `missing()` as it was and let a correct fail-closed refusal report missing spans — the status quo the reviewer identified as teaching operators to ignore the signal | Only two stages may legitimately not exist: a refusal authorises no order, so there is no command and no ack. Everything else runs on every path, so its absence is a defect. A `broker_ack` without an `order_command` is still a hole. `missing()` is unchanged, so TC-OB-003 still tests the strict form |
| **D-03** | **`direction` is a required, declared field** (`higher_is_worse` / `lower_is_worse`) on every SLI; an SLI that omits it or names an unknown value is refused at load | (a) optional with a default — a default *is* a guess, and the guess would be wrong for exactly the two SLIs F-07 named; (b) keep name inference and special-case the two — leaves the next SLI to be judged by a substring; (c) a comparator expression per SLI (`breach_when: "value > target"`) — more expressive and more dangerous: an expression in a config file is code nobody reviews as code | A safety direction is a safety property, so it is declared and it fails closed when absent. Two words are reviewable by a risk officer who does not read Python |
| **D-04** | **Instrument inside the services, through no-op hooks**, and wire them in the composition root | (a) instrument in `apps/web/web_bff/platform.py` only — quickest, but the measurement would live in the sim composition and would not travel with the component to any other deployment, which is the "stopwatch in a harness" the reviewer refused; (b) give the services a metrics dependency — couples engines to an observability package and breaks the framework-free rule's spirit | The pattern already exists (`KillSwitchHooks.observe`). Defaults are no-ops, so a caller that wires nothing behaves exactly as before, and nothing an engine does depends on a metric existing |
| **D-05** | **`order_ack_latency_ms` is measured by the caller**, around lease acquisition and `gateway.submit` | (a) instrument inside `ExecutionGateway` — the natural place and a **protected path** (`services/execution`, .github/CODEOWNERS); this build agent may not touch it; (b) leave it uninstrumented until the gateway's owner instruments it — leaves the SLI unmeasurable for another cycle | The caller-side measurement is real and its limits are stated in the SLI's `gap:` (includes the lease, is an in-process call, and in dev/sim measures the simulator). If the gateway's owner later instruments it properly, this becomes the outer bound of that measurement |
| **D-06** | **`alert_delivery_s` gets two real ends and no synthetic second end.** `raised_at` on the alert, a `Delivery` record per channel, `acknowledge()` that refuses an unraised alert and emits the metric, `unacknowledged()` as the meanwhile view; `alert_dispatch_s` is emitted separately and is **not** the SLI | (a) emit `alert_delivery_s` at dispatch — makes the SLI "computable" today and measures the wrong thing: dispatch to an in-process list, reported as time-to-operator, in the flattering direction; (b) default an unacknowledged alert to zero seconds — a missing measurement read as zero, which hides an outage; (c) leave it uncomputable and write a paragraph — leaves the SLI that bounds every auto-action path with no first end either | The half that is code now exists and is tested; the half that is an operator and a notification component is stated as missing rather than simulated. `unacknowledged()` gives the on-call something true to look at before O-15 exists |
| **D-07** | **Reconciliation completeness is a derived property on the result, observed by the caller**; it is deliberately conservative and is `None` when nothing was compared | (a) add `positions_reconciled` to the event payload — drifts `contracts/events/reconciliation.completed.v1.json`, a contract change for a metric; (b) count only quantity/price breaks — would report a higher completeness than the operator's view of the same run | A percentage that errs downward is the safe direction for an SLI whose safety semantic is `supervised_on_break`. An empty comparison reporting 100% would be the most quotable false number in the system |
| **D-08** | **`signal_latency_ms` is emitted by a wrapper (`timed_signal`) around any strategy call, labelled with the runner**, and emits nothing when no signal is produced | (a) leave it uninstrumented — it is the one SLI whose component has no live caller, so this was defensible; (b) time the probe's `signal` span — the probe's "signal" is a fixture intent, not a strategy: that would be a fabricated measurement of the very kind PO-S4 warns about; (c) time every call including the ones that produce nothing — a zero-length "signal latency" for a bar that produced no signal is a measurement of something that did not happen | The wrapper is where a real signal loop would emit when one exists. Until then, every observation carries `runner=backtest` and the SLI's `gap:` says so in one sentence |
| **D-09** | **Latency is measured on a monotonic clock, never the business clock** (`IntentTracker` keeps an in-process `perf_counter` stamp outside `IntentStatus`) | (a) use `validated_at` → decision `now` — both come from the fixture clock, so sim and backtest would report 0 ms and a backtest could report negative or hour-long latencies; (b) add the stamp to `IntentStatus` — puts a measurement into an audited, tenant-visible control record | A number that is zero because the clock did not move is worse than no number. The stamp is never audited, never returned by an API and never a decision input |

---

## 4. What was fixed, and what could not be

### 4.1 Fixed

| Finding | State before (`caab32e`) | State now (`8f2258e`) | Proof |
|---|---|---|---|
| **F-14** | probe returned `vi.correlation_id`; spans lived under `probe-<timestamp>`; `missing_spans` computed under the second id; `tracer.stages(returned_id)` empty | one id from the first span to the audit row; the verdict is computed under the id returned; both ids printed; the CLI exits non-zero on divergence, on any missing span and on any failed span | TC-OB-006 (all spans under the returned id, and **no other id exists in the tracer**), TC-OB-001 (completeness asserted for the returned id), TC-PKG-001 (the printed verdict belongs to the printed id) |
| **F-14 (second half)** | `missing()` judged all eight stages, so a correct fail-closed refusal reported missing `order_command`/`broker_ack` | `stages_not_reached` is reported separately, for those two stages only, and only when no later conditional stage ran | TC-OB-008 (both halves: a correct stop is complete; an earlier hole cannot be declared away) |
| **F-07** | direction inferred from the name; `alert_delivery_s` and `time_to_halt_s` inverted | `direction` is a required declared field on all nine; evaluation uses it; an SLI without one is refused at load | TC-OB-009 (both SLIs judged upward, both directions exercised), TC-OB-010 (absent and unknown direction refused; a "latency" name declared `lower_is_worse` is judged low) |
| **F-03** | one of nine SLIs emitted; `slis.yaml` named components as if they were measurements | eight of nine emit; `slis.yaml` separates component / emission point / metrics / direction / **gap**, and says "none" plainly where there is no emission point | TC-OB-011 (every metric the file claims is emitted by exercising the platform; every SLI with no emission point declares no metric and states its gap) |
| **F-03 (`alert_delivery_s`)** | not computable in principle: no timestamp, no acknowledgement, no notification component | both ends exist in code; the second end has no producer, and that is stated rather than simulated | TC-OB-012 (two ends, nothing invented for an unacknowledged alert), TC-OB-013 (an acknowledgement cannot be manufactured) |

### 4.2 Could not be fixed here, and why

| Gap | Why it is not a code change I could make | Register |
|---|---|---|
| **`event_lag_ms` has no emission point** | It needs two ends that do not exist: no code publishes to or consumes from the broker in the compose stack; `Outbox.relay(fn)` takes a callback and no caller passes a producer. Instrumenting a relay nobody calls would add a metric that can never fire and would read, in a file, as if lag were measured | [Open: R-05] |
| **Nothing acknowledges an alert** | The second end of `alert_delivery_s` is an operator and a notification channel. There is no notification component, no pager integration and no on-call model. Building an acknowledgement UI or a pager route is a component and a human-process decision, not an SRE code fix | [Open: SRE-R5, **O-15**] |
| **No telemetry export, no backend** | Every emission is in-process. There is nowhere to send a metric and nothing to read it in; choosing a backend is a platform and funding decision | [Open: **O-18**, and the delivery gap named in the epic's "not delivered" list] |
| **Histograms are unbounded and unwindowed** | `MetricsRegistry.percentile` sorts the whole list per query, so `risk_decision_latency_ms_p99` gets more expensive the longer the process runs and is lifetime-to-date, not windowed. Bounding it means choosing a window and a retention policy — a decision with memory and evidence consequences that belongs with the soak measurement (step 4), not with a build agent's default | [Open: SRE-R4] |
| **The tracer has no propagation carrier and no exporter** | Spans use `perf_counter` timestamps that cannot be joined across processes, and there is no trace-context header. A probe is therefore evidence about **one process**, however honest it now is. Adding a carrier changes the cross-service contract and needs the Integration Architect | [Open: SRE-R10 remainder] |
| **Start-up integrity failures still emit no alert** | Both store verifications run inside the constructors, before the alert router is wired. Not in scope of these three findings, and the fix belongs with the Backend Lead at the composition root | [Open: SRE-R1] |
| **No SLO target for anything** | A target needs a measured baseline and business approval. **Not mine, at any point, for any SLI** | [Open: O-03] |
| **`services/execution` and `services/risk` uninstrumented** | Protected paths. `order_ack_latency_ms` is measured from the caller instead; `control_plane_availability` and `market_data_freshness_s` are emitted at the pipeline, which is where the request and the snapshot use actually are | .github/CODEOWNERS |

---

## 5. The nine indicators: what is measurable now, and what is not

Read against the tree at `8f2258e`. **"Emits" never means "has a baseline".** Every emission below is in-process, unwindowed and unexported; collecting a baseline is Gate C work and no baseline exists. The authoritative per-SLI limits are the `gap:` field of `observability/slis.yaml`; this table is a summary of it and softens nothing.

| # | SLI | Before | Now | Emission point | Metric(s) | Direction (declared) | What it still does **not** measure |
|---|---|---|---|---|---|---|---|
| 1 | `control_plane_availability` | no counter anywhere | **emits** | `oms.pipeline.TradePipeline._process` / `on_approval` | `control_plane.decision_requests`, `control_plane.decisions_recorded`, `control_plane.decision_unavailable` | lower is worse | not windowed (since process start); no aggregation across processes or cells; a refusal counts as a **successful** decision — availability counts answers, not approvals |
| 2 | `market_data_freshness_s` | computed ad hoc for one dashboard field, never observed | **emits** | `TradePipeline._observe_freshness`, at the snapshot the decision used | `pipeline.market_data_freshness_s` | higher is worse | an instrument nothing decides on is never observed; ingest-side staleness of an unused feed is invisible; age is measured against the decision clock, which in sim/backtest is the fixture clock |
| 3 | `signal_latency_ms` | a probe span whose duration was never observed | **emits, from one caller only** | `strategy_service.signals.timed_signal` (label `runner=`) | `strategy.signal_latency_ms` | higher is worse | there is **no live signal loop**: the only caller in the tree is the backtest runner, so every observation is a property of a backtest run, not of a deployed platform. A bar that produces no signal emits nothing (never a zero) |
| 4 | `risk_decision_latency_ms_p99` | no span duration observed | **emits the underlying histogram** | `TradePipeline._observe_decision_latency` (monotonic, from `IntentTracker.create`) | `pipeline.risk_decision_latency_ms` | higher is worse | the **p99 is not windowed** and gets more expensive per query as the process runs [SRE-R4]; "per cell" does not exist; an intent enqueued in another process or before a restart yields no measurement |
| 5 | `order_ack_latency_ms` | nothing | **emits, caller side** | `TradePipeline._authorise_and_execute`, around lease + `gateway.submit` | `pipeline.order_ack_latency_ms` | higher is worse | not the gateway's own view (protected path); includes lease acquisition; an in-process call, not a network round trip; against the simulated broker it measures the simulator; an order that reaches no ack state emits nothing |
| 6 | `event_lag_ms` | nothing, and no producer or consumer | **still nothing — declared `emission_point: none`** | — | — | higher is worse | everything: there is no producer and no consumer to measure between. A Kafka-compatible broker runs in the dev/sim compose stack and **nothing is wired to it** [Open: R-05] |
| 7 | `reconciliation_completeness_pct` | nothing | **emits, per run** | `ReconciliationResult.completeness_pct`, observed by the caller (`SimPlatform.reconcile`) | `reconciliation.completeness_pct` | lower is worse | **"by EOD+T" is unmeasured** — there is no scheduler and no deadline in the tree. Conservative by construction (any break naming an instrument counts it unreconciled); a run that compared nothing reports no percentage rather than 100% |
| 8 | `time_to_halt_s` | **emitted** (the only one) | emits, unchanged | `KillSwitchService.activate` via `KillSwitchHooks.observe` | `killswitch.time_to_halt_s` | higher is worse — **this was inverted until F-07 closed** | operator-action → engaged (only a drill measures that); it measures one process against the simulated broker; **no baseline** [Open: Q-16-1] |
| 9 | `alert_delivery_s` | **not computable in principle**: no timestamp, no ack, no notification component | **computable, but nothing produces the second end** | `AlertRouter.acknowledge` (SLI); `AlertRouter._dispatch` emits `alerts.alert_dispatch_s`, which is **not** the SLI | `alerts.alert_delivery_s` | higher is worse — **this was inverted until F-07 closed** | **nothing acknowledges an alert outside a test**: no notification component, no operator path, no on-call model. "Delivered" means handed to an in-process channel list — evidence that the platform tried, never that a human was reached [Open: SRE-R5, O-15] |

**Baseline readiness, stated plainly for the gate: 0 of 9 have a baseline.** Seven can now have one collected inside a single process (1, 2, 4, 5, 7, 8, and 3 only from a backtest); **2 cannot be baselined at all** — `event_lag_ms` (no producer, no consumer) and `alert_delivery_s` (no acknowledgement producer). §9 PO-C1 states what that means for the gate.

---

## 6. Executability

```
$ rt365 probe --env sim
correlation_id: probe_b47fc026271a4768be3b80d8d563fea4
trace_correlation_id: probe_b47fc026271a4768be3b80d8d563fea4
intent_id: 6969b103-b9a9-4add-9883-84cd31a84b10
snapshot: mks_c102bd48bae9a00010f7839821a93131
final_state: ACKNOWLEDGED
stages_recorded: ["market_snapshot", "signal", "intent", "eligibility", "risk", "order_command", "broker_ack", "audit"]
stages_not_reached: []
missing_spans: []
failed_spans: []
trace_complete: True
exit=0
```

The two ids are the same id, the eight stages are under it, and the audit rows for that id exist (asserted by TC-OB-006, not by this transcript). Before this change the first line was a `corr_…` id under which `tracer.stages()` returned nothing.

---

## 7. Control quartet

Per control, with the test ids as generated into `docs/TEST_CASES/TC-OB.md` and `TC-PKG.md`. Existing tests were extended, never weakened (§8).

| Control | Positive | Negative | Abuse | Recovery |
|---|---|---|---|---|
| **A probe reports the verdict for the id it returns** (F-14) | **TC-OB-006** — one id covers spans, audit rows and the intent; the tracer holds no other id. **TC-OB-001** (extended) — completeness asserted for the **returned** id. **TC-PKG-001** (extended) — the printed verdict belongs to the printed id | **TC-OB-008** — a pipeline that correctly stopped reports `stages_not_reached`, not missing spans, and is complete | **TC-OB-007** — an id with no spans reports every stage missing and is never complete; a span recorded `ok=False` is present **and failed**, and failure is not completeness | **RB-15** (INCIDENT_RESPONSE): record the id first, classify split-id vs missing vs failed, never re-run before recording, never widen what counts as complete. The CLI exits non-zero, so a red probe stops a deploy step |
| **A stage may be "not reached" only where a refusal is why** (F-14) | **TC-OB-008** first half — `order_command`/`broker_ack` forgiven after a correct stop | **TC-OB-003** (unchanged) — the strict `missing()` form still reports six missing stages for a two-stage trace | **TC-OB-008** second half — declaring an *earlier* stage not reached while later stages ran does not suppress it; only `CONDITIONAL_STAGES` may ever be forgiven, and only with no later conditional stage recorded | the allowlist is in code, not in a caller's argument: a future caller cannot widen it without changing `rtobs.tracing` and its reviewer |
| **The dangerous direction is declared, not guessed** (F-07) | **TC-OB-009** — all nine declare a direction; `alert_delivery_s` and `time_to_halt_s` breach **upward**; both directions exercised with fixture targets | **TC-OB-009** — a value on the safe side of a fixture target returns `SafetyAction.NONE` in both directions; **TC-OB-004** (unchanged behaviour) — with every real target `null`, evaluation stays `NONE` | **TC-OB-010** — an SLI with no direction, or an unknown one, is **refused at load** (fail closed); a name containing "latency" declared `lower_is_worse` is judged low, so the name no longer decides | the file is the source of truth: a wrong direction is a one-word review fix in `slis.yaml`, caught by a reviewer who does not read Python. **TC-OB-009 also asserts every real target is still `null`** — the guard against a target arriving with the direction |
| **An indicator claims only what it emits** (F-03) | **TC-OB-011** — exercising the platform emits every metric `slis.yaml` claims, for every SLI that claims an emission point | **TC-OB-011** — an SLI with `emission_point: none` must declare **no** metric and **must** state its gap; a claim with no emission fails the test | **TC-OB-011** is the abuse case for the file itself: adding a metric name to `slis.yaml` that nothing emits turns the suite red, so the file cannot drift back into naming components as measurements | if an emission is removed, the test names the SLI and the metric that went silent; the recovery is to restore the emission or to state the gap — never to delete the claim quietly |
| **A delivery time has two real ends** (SRE-R5) | **TC-OB-012** — `raised_at` and a per-channel delivery record exist for every alert; an acknowledgement records the time and emits `alerts.alert_delivery_s` | **TC-OB-012** — an unacknowledged alert has `delivery_s is None` (never 0.0) and appears in `unacknowledged()` | **TC-OB-013** — acknowledging an alert that was never raised is **refused** (`KeyError`), and no metric is emitted; a second acknowledgement never rewrites the first recorded time | `unacknowledged()` is the operational view until a notification component exists; the gap is written into `slis.yaml`, ALERT_CATALOG and SLO_SLA rather than closed by a synthetic number |
| **An alert may tighten, never widen** (standing rule, unchanged) | **TC-OB-004** — `slo.freshness_breach` → autonomy suspended, delivered on every channel | **TC-OB-004** — every real target `null`, so no auto-action fires from an SLI today | **TC-OB-005** — an auto-action with an incomplete payload raises S1 `alert.autoaction_failed`; no silent no-op | nothing in the new delivery path can trigger an auto-action: `raised_at`, `Delivery` and `acknowledge` are records, not routes |

---

## 8. What changed in existing tests, and why

Two existing tests were **strengthened**; one existing helper construction was updated to a stricter model. No assertion was removed, relaxed or made conditional.

| Test | Change | Why |
|---|---|---|
| **TC-OB-001** (`test_correlation_id_end_to_end_and_probe_completeness`) | **added** two assertions: `set(platform.tracer.stages(corr)) == set(PIPELINE_STAGES)` and `out["trace_complete"] is True`, where `corr` is the **returned** id. Every previous assertion is untouched | This is the property that was missing and the reason the defect survived: the test asserted `missing_spans == []` (a verdict computed under the hidden id) and then used the returned id only for the audit lookup. It would have passed with the split id forever |
| **TC-PKG-001** (`test_cli_version_check_and_probe_run_in_sim`) | **added**: parse the probe's printed output and assert `trace_complete == True`, `trace_correlation_id == correlation_id`, `stages_recorded == PIPELINE_STAGES`, `failed_spans == []`. The existing `missing_spans: []` and exit-code assertions are untouched | The CLI is what a gate report cites. The output an operator reads is now asserted, not just the exit code |
| **TC-OB-004** (`test_alert_delivery_and_slo_safety_semantics`) | the inline `Sli(...)` fixture was replaced by the `_sli(target=500)` helper, which supplies the fields the model now requires (`emission_point`, `metrics`, `direction`, `gap`). The assertion is unchanged and still proves that a set target with a `suspend_autonomy` semantic returns `SUSPEND_AUTONOMY` | `Sli` gained required fields, so the old positional fixture no longer constructs. The helper exists so that no test can accidentally rely on a default direction — there is none |

Everything else in the suite is untouched: **220 tests before, 228 after; all 220 still pass**; 23/23 quartet areas complete (208 evidence records).

---

## 9. Concerns for the Product Owner

- **PO-C1 Two of the nine service levels still cannot be baselined at all, and one can only be baselined from a backtest.** Instrumentation is done as far as code can take it: seven of the nine now emit a real measurement at a real point, and you can have baselines collected for them at Gate C. Two cannot. *Event lag* has no producer and no consumer — a message broker runs in the development stack and nothing is wired to it, so there is nothing to measure between; that is a build item, not a counter. *Alert delivery* now has both ends in code, but the second end is a human: nothing acknowledges an alert, because there is no notification component, no pager route and no on-call model. I have deliberately **not** made it look measurable by timing the alert's journey to an in-process list and calling that "time to operator" — that would have produced a flattering number for the SLI that bounds every automatic stop this platform can perform, including the platform-wide Kill Switch. And *signal latency* emits only from the backtest runner, because there is no live signal loop; every observation of it today is a property of a backtest, and the file says so. What this means at the gate: **do not accept a Gate C pack that shows nine baselines. Nine is not available. Seven is, one of them qualified, and two are honestly absent** [Committee].

- **PO-C2 The command a gate report cites as proof that we can trace a request was giving out an identifier that led nowhere.** The synthetic probe returned one correlation id and computed its "trace complete" verdict under a different one. An operator taking the returned id to a trace view would have found nothing and reported total trace loss; a gate reader taking the verdict at face value would have been told the pipeline is traceable end to end on evidence that never referred to the id in front of them. It is fixed — one id from the first step to the audit record, both ids printed so any future divergence is visible in the output itself, and the command now fails rather than warns. But I want the general point on the record, because it is the second time this shape of defect has appeared: **a report about a system must state what it can show, under the identifier it hands you**. The check was not weak; it was measuring the wrong thing while looking green [Committee].

- **PO-C3 A comparison that was pointing the wrong way is now closed *before* any target is set, which is why it cost nothing.** Two of the nine service levels — how long a stop takes, and how long an alert takes to reach a person — were judged in the inverted direction by code that guessed the dangerous direction from the indicator's *name*. With no targets set, nothing had gone wrong yet. Had a target been set first, the platform would have raised an alarm when a stop was **fast** and stayed silent when it was **slow**, and it would have looked correct on the dashboard. Each indicator now declares its direction in two words that a risk officer can review without reading code, and an indicator that omits it is refused. I am telling you this mainly as evidence for a sequencing rule I would like to hold: **the direction of a control must be settled before the number it compares against**, and the same applies to the rest of O-03 [Committee].

- **PO-C4 I set no target, and I want to be clear that instrumenting is not measuring.** Every target in the file is still empty, and I made none. What exists now is the ability to observe; what does not exist is any observation you may quote. Every measurement lives inside one running process, in memory, with no export and nowhere to send it — so "watch the service levels during the soak" still means someone reading a registry inside a single process. The percentile the capacity model names as an autoscaling trigger is computed over the process's whole lifetime rather than a window, and gets slower the longer the process runs. Before any of these becomes a number in a pack, three things are owed that are not mine: somewhere to send telemetry (O-18), bounded windows with a retention decision (SRE-R4), and the baseline programme itself at Gate C [Committee].

- **PO-C5 The one thing a green probe still cannot tell you.** It now tells the truth about the process it ran in. It cannot tell you anything about a deployed cell, because the tracer is in-process only: there is no trace-context carried between services and no exporter, so "the request was traced end to end" is a statement about one operating-system process running the whole pipeline in memory. In a deployed topology that sentence has not been tested at all. I would not let the deployment runbook's trace-completeness step be cited as shadow-readiness evidence until a propagation carrier exists, and I have written that limitation into the runbook step itself rather than leaving it to be discovered [Open: SRE-R10, R-05].

- **PO-C6 Nothing here is approved, including my own documents.** I changed five documents I own (SLO_SLA, DASHBOARDS, ALERT_CATALOG, DEPLOYMENT_RUNBOOK, INCIDENT_RESPONSE) and reviewed none of them; their reviewers of record are the Chief Risk Agent, the Frontend Lead, the Backend Lead and the Security Architect, and all are pending. I edited no register: every RAID and RTM row below is **proposed** and carries no id, because ids are the Program Orchestrator's to assign. I touched neither protected path. The three findings this session addresses were raised by the SRE Lead against someone else's document and are fixed in his own code — which is the separation working, and is worth noticing, because two of the three were only visible to someone who read the code rather than the document that described it [Source: 13].

---

## 10. Proposed ledger rows — **not written by me**

### 10.1 RAID (Program Orchestrator) — updates to existing proposals; **no ids assigned**

| Ref | Proposed change | Owner |
|---|---|---|
| **SRE-R10** (F-14) | **Partly closeable.** The split correlation id is fixed at `8f2258e` with TC-OB-006/007/008 and TC-PKG-001; "stage not reached vs span missing" is fixed. **Keep open** for the remainder: the tracer is in-process only, with no propagation carrier and no exporter, so trace completeness cannot be checked across a deployed cell | SRE Lead, Integration Architect |
| **SRE-R2** (F-07) | **Closeable.** `direction` is a required declared field; the name inference is gone; TC-OB-009/010 prove both directions and the fail-closed refusal. **Note in the closing row that it closed before O-03, as required** | SRE Lead, reviewer Chief Risk Agent |
| **SRE-R5** | **Partly closeable.** Both ends now exist in code (`raised_at`, per-channel `Delivery`, `acknowledge` that refuses an unraised alert). **Keep open** for the missing producer: no notification component and no operator acknowledgement path — which makes it a dependency of **O-15** (on-call model), not only of instrumentation | SRE Lead, + whoever owns O-15 |
| **SRE-R4** | **Unchanged, and now the binding constraint on the p99.** Histograms remain unbounded and sorted per query. Deliberately not fixed here: the window and retention are a decision, and the soak (step 4) is what should size them | SRE Lead, Performance & Chaos Lead |
| **New (Issue) — proposed** | **Instrumentation exists; a telemetry destination does not.** All nine SLIs are emitted into an in-process registry with no exporter and no backend, so no measurement can be read outside the process that produced it and none can be aggregated across processes or cells. Blocks the Gate C baseline programme as surely as the missing counters did | SRE Lead, Cloud Architect (**O-18**) |
| **New (Gap) — proposed** | **`alert_delivery_s` has no acknowledging party.** Not a counter and not a code defect: it needs a notification component and a named on-call rota (**O-15**). Until then `AlertRouter.unacknowledged()` is the honest view and the SLI emits only in tests | SRE Lead |
| **R-05** | Add the observability consequence: with no producer or consumer on the bus, `event_lag_ms` is the one SLI that **cannot** be instrumented, and the Analytics plane's autoscaling trigger therefore still has neither a signal nor a threshold nor a mechanism | Integration Architect, SRE Lead |
| **O-03** | Note as a **precondition now satisfied**: the declared-direction defect (SRE-R2) is closed, so a target set after this commit will at least be compared the right way. The other preconditions — a measured baseline and business approval — are untouched, and **two SLIs still cannot be baselined at all** | Chief Risk Agent, Executive Steering |

### 10.2 RTM (QA Lead / Program Orchestrator) — requirement → architecture → owner → control → test → evidence → gate

| Requirement | Architecture | Owner | Control | Test | Evidence | Gate |
|---|---|---|---|---|---|---|
| NFR-OBS-01 (correlation id end to end; trace completeness) | `rtobs.tracing` (`Tracer.verdict`, `CONDITIONAL_STAGES`); `SimPlatform.synthetic_probe`; `rt365 probe` | SRE Lead; reviewers ARB (2nd), Backend Lead (1st) | one correlation id from first span to audit row; the verdict is computed under the id returned; a missing or failed span exits non-zero; only a refusal's two stages may be declared not reached | TC-OB-001 (extended), TC-OB-006, TC-OB-007, TC-OB-008, TC-PKG-001 (extended) | `docs/TEST_CASES/TC-OB.md`, `TC-PKG.md`; INCIDENT_RESPONSE RB-15; DEPLOYMENT_RUNBOOK step 7 | C |
| NFR-OBS-01 (SLI catalogue; safety semantics) | `observability/slis.yaml`, `rtobs.slis` (`Direction`, `Sli`, `SliCatalog.evaluate`) | SRE Lead; reviewer Chief Risk Agent (2nd) | the dangerous direction is a declared property; an SLI without one is refused at load; no target is set | TC-OB-009, TC-OB-010, TC-OB-004 | `docs/SLO_SLA.md` v1.2; `observability/slis.yaml` (all `target: null`) | C for the control; **E for any target (O-03)** |
| NFR-OBS-01 (measurement exists where the catalogue says it does) | `oms.pipeline`, `oms.lifecycle`, `strategy_service.signals`, `reconciliation_service.reconcile`, `rtobs.alerts`, wired in `apps/web/web_bff/platform.py` | SRE Lead with Backend Lead; reviewer ARB | a claimed emission point emits; an absent one is declared absent with its gap; measurement is never a decision input | TC-OB-011, TC-OB-012, TC-OB-013 | `docs/SLO_SLA.md` v1.2 table; `docs/DASHBOARDS.md` v1.1; `observability/slis.yaml` `gap:` fields | C (entry condition for the baseline programme) |
| NFR-PRV-01 (redaction) | `rtobs.logging` | SRE Lead | unchanged this session | TC-OB-002 | `docs/TEST_CASES/TC-OB.md` | C |
| NFR-AVL-01 / NFR-SCL-01 (the SLIs the capacity model depends on) | CAPACITY_MODEL §5; `observability/slis.yaml` | Cloud Architect (document), SRE Lead (instrumentation) | §5's measurement-point column can now be split into component and emission point, with **eight** rows having one and one row having none | §5 of this packet | this packet §5; `observability/slis.yaml` | B (F-03 correction), C (baselines) |

### 10.3 For the owner of `docs/CAPACITY_MODEL.md` (Cloud Architect) — F-03 is now closeable with facts, not caveats

The blocking finding F-03 asked for the §5 column to be split into **"component named in `slis.yaml`"** and **"emission point in the tree today"**, with the second `[Open]` for eight of nine. That split can now be filled in the other direction: **eight of nine have an emission point** and **one (`event_lag_ms`) has none**, with each row's limits stated. §5 of this packet is offered as the source text; `observability/slis.yaml` is the authority. I did not edit the capacity model — I do not own it.

### 10.4 AUDIT_EVIDENCE_INDEX (Program Orchestrator)

Add rows for **SLO_SLA.md v1.2** (owner SRE Lead, reviewer Chief Risk Agent **pending**, "no SLO target set or changed"), **DASHBOARDS.md v1.1** (reviewer Frontend Lead **pending**), **ALERT_CATALOG.md v1.1** (reviewer Chief Risk Agent **pending**, "no alert, severity or auto-action added, removed or changed"), **DEPLOYMENT_RUNBOOK.md v1.2** and **INCIDENT_RESPONSE.md v1.2** (reviewers Backend Lead / Security Architect **pending**), and this packet as the build evidence for TC-OB-006..013.

---

## 11. Threat-model delta [Committee] — proposed to the Security Architect, who owns THREAT_MODEL

None of these is a new control; each is a way an existing control could report itself healthy while failing.

| Candidate | Where it comes from | Statement |
|---|---|---|
| **A verdict issued under an identifier the operator was not given** | F-14 | The probe judged completeness under an id it kept and returned another. Any check that computes a verdict under one key and reports another can be green while the thing it names is empty, and the discrepancy is invisible to everyone downstream. Control: one id end to end, both ids returned, non-zero exit on divergence. Abuse test: ask the tracer for an id with no spans and assert it can never be complete (TC-OB-007) |
| **"Not reached" as a suppression primitive** | F-14 second half | A completeness check that accepts the caller's word for which stages were skipped can be satisfied by declaring the missing ones away — and the pressure to do so arrives exactly when a stage stops recording. Control: only `order_command`/`broker_ack` may ever be forgiven, only when no later conditional stage ran; the allowlist lives in `rtobs.tracing`, not in the caller's argument. Abuse test: TC-OB-008 second half |
| **A safety comparison inferred from a string** | F-07 | The direction of danger was derived from a substring of the indicator's name, so an indicator whose name did not match the pattern was compared backwards. An actor never has to attack this; a well-meaning rename does it. Control: a declared, required, refused-if-absent direction. Abuse test: TC-OB-010 |
| **A measurement invented in the flattering direction** | SRE-R5 | The cheapest way to close a measurement gap is to measure a nearer, easier event and give it the harder event's name: time-to-dispatch reported as time-to-operator, or an unacknowledged alert defaulted to zero seconds. Both make an outage look fast. Control: `alert_dispatch_s` and `alert_delivery_s` are separate metrics; `delivery_s` stays `None` until a real acknowledgement; an acknowledgement for an alert never raised is refused. Abuse test: TC-OB-013 |
| **Instrumentation as a new read path into the control plane** | D-04, D-09 | Metrics hooks are a way for a component to observe another; if an engine ever *read* one back, a measurement would become a control input and could be moved by whoever can move load. Control: every hook is write-only (`count` / `observe`), defaults are no-ops, the enqueue stamp is outside `IntentStatus`, is never audited and is never returned by an API. Nothing an AI or MCP component can call touches any of this, and no route, secret, limit or mode path was added |

---

## 12. Evidence

| Artefact | What it is |
|---|---|
| `test/quartets/test_tc_ob_observability.py` | TC-OB-001..013 — the quartet for this epic, written before the implementation |
| `test/quartets/test_tc_pkg_cli.py` | TC-PKG-001 extended: the printed verdict belongs to the printed id |
| `docs/TEST_CASES/TC-OB.md`, `docs/TEST_CASES/TC-PKG.md`, `docs/TEST_CASES/EVIDENCE_REPORT.md` | generated by `make evidence` — 208 records, 23/23 areas with a full quartet; **signature pending, never self-certified** |
| `observability/slis.yaml` | the nine indicators with component, emission point, metrics, declared direction and gap; **all targets `null`** |
| `observability/rtobs/{tracing,slis,alerts}.py` | `TraceVerdict` / `CONDITIONAL_STAGES`; `Direction` and the declared-direction evaluation; `raised_at`, `Delivery`, `acknowledge`, `unacknowledged` |
| `services/oms/oms/{pipeline,lifecycle}.py` | the four control-plane emissions and the monotonic enqueue stamp |
| `services/strategy/strategy_service/signals.py`, `services/backtest/backtest_engine/runner.py` | `timed_signal` and its only caller |
| `services/reconciliation/reconciliation_service/reconcile.py` | `positions_reconciled`, `completeness_pct` |
| `apps/web/web_bff/platform.py`, `apps/cli/rt365_cli/main.py` | one-id probe, the hooks wired to the registry, the CLI verdict and exit code |
| `docs/SLO_SLA.md` v1.2, `docs/DASHBOARDS.md` v1.1, `docs/ALERT_CATALOG.md` v1.1, `docs/DEPLOYMENT_RUNBOOK.md` v1.2, `docs/INCIDENT_RESPONSE.md` v1.2 (RB-15) | the owned documents, restated against what now emits; **all reviewer signatures pending** |

---

## 13. Assumptions, confidence, provenance

- **Assumptions:** the tree at `caab32e` is what the SRE Lead reviewed and what ships in dev/sim; `observability/slis.yaml` and `observability/alerts.yaml` are the source of truth for the indicators and for what an alert does; `.github/CODEOWNERS` at this commit defines the protected paths; D-039 stands, so no agent may accept any document or close any register item; the findings F-03, F-07 and F-14 are stated correctly by their author (I reproduced all three before changing anything) [Committee].
- **Confidence — high:** that the probe returned an id with no spans before this change and returns the id its spans are under after it (reproduced both ways, and asserted by TC-OB-006 including "no second id exists in the tracer"); that the direction inference was inverted for `alert_delivery_s` and `time_to_halt_s` and is now declared (TC-OB-009/010); that every metric `slis.yaml` claims is emitted by exercising the platform (TC-OB-011 iterates the file, so the claim and the test cannot drift apart); that `event_lag_ms` cannot be instrumented without a producer and a consumer; that no assertion in any existing test was removed or relaxed (§8); that `services/execution` and `services/risk` are unmodified (`git diff --stat`).
- **Confidence — medium:** that the emission points I chose are the ones a deployed topology would use. `control_plane_availability` and `market_data_freshness_s` are emitted at the pipeline rather than in the risk engine (a protected path) and `order_ack_latency_ms` from the caller rather than inside the gateway (also protected); these are the right *events* measured at the nearest permitted place, and a later owner of those services may want to move them. Also medium: that "conservative" is the right definition of reconciliation completeness — it errs downward on purpose, and the reconciliation owner may prefer a break-type-aware definition.
- **Confidence — none, and none claimed:** on any baseline, target, capacity figure, latency, throughput, memory figure, recovery time, cost, vendor or broker capability, data entitlement or regulatory status. None is asserted anywhere in this packet. **No SLO target is set or proposed. No threshold was invented.** The one transcript in §6 is a dev/sim command output, not a measurement of anything [Source: 00].
- **Provenance:** [Source: 00, 10, 13] as carried by the repository artefacts; [Committee] for this session's reasoning and for the review packet it answers; [Open] items carry their register ids.
- **Independence:** I am the author of this code and of these documents and the reviewer of none of them. **I recorded no approval, edited no register, set no target and closed no finding** — F-03, F-07 and F-14 are addressed here and are closed by their reviewer, not by me [Source: 13].
