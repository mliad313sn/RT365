# CAPACITY_MODEL (Gate B exit evidence — structure only)

| Content owner | Write path (roster) | Reviewer (different line) | Approving body | First gate | Status |
|---|---|---|---|---|---|
| Enterprise Architect / Cloud Architect (as this document's header and the ARB conditions address the seat) | **Cloud Architect only** (`.claude/agents/roster.json`) — see the adoption note | SRE Lead | ARB (advisory) | B | **Structure v0.2, 2026-09-08 — reviewed, not accepted.** ARB recommends *accept with conditions as a structure* (C-CM-1..C-CM-6, advisory); conditions applied by the owner; **SRE Lead review pending**; **Independent Validation pending**; **human Product Owner decision pending (D-039)** |

**Status in full [Committee].** The ARB reviewed **v0.1** and recommended *ACCEPT WITH CONDITIONS as a structure (v0.2); no number is accepted, because none was presented* (docs/SESSIONS/COUNCIL_2026-09-08_gate_B_arb_docs.md §4.3, conditions C-CM-1..C-CM-6). **D-061** carried that recommendation as a Product Owner decision **on the structure**, accepted **no number**, and closed with the sentence that **no document status changes to "accepted" until its new version and reviewer signature exist**. This is that new version. It therefore stands as: structure recommended by the ARB, conditions applied by the owner, **SRE Lead review pending**, **Independent Validation pending**, **human Product Owner decision pending (D-039)**. It is **not accepted**, and no agent records an approval [Source: 13]. Numbers remain [Open: O-03 targets, O-87 storage terms, O-88 TSDB trigger].

**Adoption note — who wrote what, and why it took three seats [Committee] [Source: 13].** The text applying C-CM-1..C-CM-6 was **drafted by the Data Architect** (docs/SESSIONS/REVIEW_2026-09-08_architecture_docs_v1.1.md Appendix A), **adopted with fourteen amendments by the Enterprise Architect** as the content owner named in this header (docs/SESSIONS/REVIEW_2026-09-08_capacity_v0.2.md §3), and **adopted with further amendments and written to this file by the Cloud Architect**, who holds this write path in `.claude/agents/roster.json` (docs/SESSIONS/REVIEW_2026-09-08_capacity_v0.2_adopted.md §3). Each of the first two edits was refused by `scripts/agent_guard.py` and **neither role routed around the guard through Bash** — the gap that a Bash write would have exploited is recorded as O-131. The third seat read the text as its owner, not as a courier. Whether the roster should treat "Enterprise Architect / Cloud Architect" as one seat for this path is a control change and belongs to the human Product Owner, not to any architect [Open: RC-5 proposed in the packets above]. Drafter is not owner, owner is not reviewer, reviewer is not approver [Source: 13].

## 0. Rules that govern every cell [Committee]

- **A cell is filled only with a measured or quoted value and its evidence id. A blank cell is [Open], never an estimate** (ARB C-13-1, IVA-B-07). "Cell" in this rule means a table cell; the deployment sense is §1a.
- **No number in this document is a target.** The ARB recommends the **structure** at Gate B; **baselines are accepted at Gate C and targets at Gate E** (O-03). This replaces v0.1's "the ARB signs the model once baselines exist", which contradicted the document's role as Gate B exit evidence and D-057 (C-CM-1).
- A value read out of the source code is a **parameter**, not a decision and not a target; §7 lists them separately so that nobody later cites a code default as if it were a decided value (C-CM-3).
- **Capacity is never bought with a plane bypass** [Source: 03, 04] [Committee]. Every shed, autoscale and failover statement below is subject to the topology: the Analytics plane has no route to the Execution plane or to brokers, and no capacity argument may create one. Load is shed in the Analytics plane; the Control and Execution planes fail closed instead of shedding. The written form of this rule is enforced by `scripts/check_network_policies.py` rule 2 (no Analytics egress to `plane=execution`, `plane=security` or any `ipBlock`) and rule 7 (**no egress rule anywhere may use `0.0.0.0/0` or `::/0`**; the Execution plane's broker route is explicit CIDRs per certified adapter), tested by TC-NET-001..004.
- **Capacity is never bought by widening an egress rule either** [Committee] [Source: 04]. A throughput or cost argument that replaces per-adapter broker CIDRs with a wider block, or that adds an `ipBlock` to a non-Execution namespace, is refused by the checker before it is argued; the Execution namespace is the only namespace that may hold an `ipBlock` at all.
- **Every "per cell" statement in this document rests on ADR-007 (regional cell topology), whose status is still `Proposed`** and which appears in no entry of docs/DECISION_LOG.md [Committee]. The cell is the failure domain, cross-cell traffic is limited to audit replication and portfolio roll-up, and one cell is provisioned per venue cluster — all of that is a proposal, not a decision of record. Read every "per cell" below as "per cell *if* ADR-007 is decided as proposed" [Open: ADR-007 status].
- A CI test-suite timing is not a capacity baseline. ADR-018 records the suite at 9.5 s before and 8.9 s after on the memory default; that figure is deliberately **not** carried into this document, and no figure of that kind may be cited as a platform baseline [Committee] (COUNCIL_2026-09-08_gate_B_arb_docs.md §4.1).
- Every statement is tagged [Source: NN], [Committee] or [Open]. No cloud price, vendor capability, provider tick rate, licence term, throughput or latency is asserted anywhere in this document [Source: 00].
- Nothing here authorises an environment. **No cell is provisioned** — §1a states exactly what does and does not exist in `infra/` [Open: H-05, A-6, B-15] (C-CM-5).

## 1. What is fixed now [Committee] [Source: 03, 05]

| Dimension | Unit of scale | Partition key | Shed under load? |
|---|---|---|---|
| Analytics plane (market data, strategy, MCP servers, backtest) | per cell, autoscale on event lag | tenant / instrument | Yes — shed first [C2 §6] |
| Control plane (intent queue, eligibility, risk, approval, audit) | per cell, autoscale on risk-decision latency | tenant / account | Never — fails closed (HALTED) |
| Execution plane (OMS, gateway, adapters, reconciliation, portfolio) | one active executor per account (lease), standby per cell | account | Never — cancel-only on degradation |
| Audit WORM (target-state deployment concept) | append-only, replicated cross-cell (ADR-007); **the replication is not provisioned and has no manifest**, and its lag is the recovery-point input of §4a | tenant | Never |
| **Control-state store (ADR-018: lease, outbox/inbox, gateway indexes, Kill Switch activations)** | one store per service per cell from shadow (D-058 (a), O-115); in dev/sim one SQLite file | account (execution schema) / tenant (control schema) | **Never** — a `StoreError` is S1 and the gateway submits nothing |
| **Market-data store (D-056)** | per cell (PostgreSQL bitemporal plus an object-storage archive in the same cell); no cross-cell replication (ADR-007) | instrument / market_ts | never for decision-time reads; archive jobs shed first |
| **Audit store and its external witness (ADR-020)** — what exists in dev/sim, and the concrete form of the Audit WORM row above | its own store file per platform, never the control store's; an anchor directory owned by a different principal (a WORM bucket or replica in deployment) [Open: O-54] | tenant (reads) / chain sequence (writes) | **Never** — a failed chain or a missing witness fails closed and carries the `killswitch_platform` auto-action [Open: O-137] |
| **Outbox relay and event bus (ADR-005, docs/DATA_FLOWS.md DF-13)** — the deployment carrier of every cross-context event | undecided: no bus is deployed and no manifest exists; at-least-once with a consumer inbox is the contract, so the consumer side scales with duplicate handling, not with ordering | topic / tenant | control- and execution-plane events are never dropped; analytics topics shed first [Open: R-05] |

These are cardinality and shed-policy statements, not capacity figures [Committee].

**Neither the autoscaling nor the shedding in this table is implemented or configured anywhere** [Committee] [Open: O-03, H-05]. Three things are missing and each is a separate gap:

1. **No mechanism.** `infra/kubernetes` contains `Namespace` and `NetworkPolicy` objects only (§1a): there is no HorizontalPodAutoscaler, no KEDA scaler, no ResourceQuota, no LimitRange, no PriorityClass and no admission or queue-depth control. "Analytics sheds first" is a policy this project has written down and not yet built.
2. **No threshold.** An autoscaling trigger needs a threshold, and a threshold is a target: `observability/slis.yaml` carries `target: null` for all nine SLIs and targets are decided at Gate E [Open: O-03]. `event_lag_ms` cannot scale anything until someone decides at what lag it should.
3. **No signal for one of the two triggers.** `event_lag_ms` is measured at the bus, and no bus is deployed in any environment [Open: R-05].

## 1a. Cell topology and what a cell is provisioned with [Committee] [Source: 03, 04] — Cloud Architect

**What a cell is.** One regional cell per venue cluster; the cell is the failure domain; cross-cell traffic is limited to **audit replication and the portfolio roll-up**; market data does not leave its cell (ADR-007 — **`Proposed`**, §0). Each cell contains the five plane namespaces and the plane network policies. NFR-RES-01 (cells as failure domains, active/standby execution ownership) and NFR-DR-01 (RPO/RTO per cell) are stated against this shape.

**What exists in `infra/` today**, read at this commit [Committee] — this is an inventory of the repository, not of any environment:

| Object | Count / state | Where |
|---|---|---|
| `Namespace` | 5 — `analytics`, `control`, `execution`, `security`, `edge`, each labelled `plane:` | `infra/kubernetes/namespaces.yaml` |
| `NetworkPolicy` | 9, in 5 files (analytics, control, execution, mcp-servers, security); default-deny per plane plus explicit allows; broker egress is one placeholder `ipBlock` in the RFC 5737 documentation range, filled per certified adapter at deployment | `infra/kubernetes/network-policies/` |
| Any other Kubernetes object kind | **none** — no Deployment, StatefulSet, Service, HPA, ResourceQuota, LimitRange, PodDisruptionBudget, StorageClass, PersistentVolumeClaim, PriorityClass or Ingress exists | — |
| Terraform / Pulumi modules | **none** — "modules are added here once the cloud provider is chosen"; provisioning cloud accounts, vault/KMS, clusters and the egress gateway is a human act | `infra/iac/README.md`, H-05 |
| Dev/sim compose stack | 1 file (`bff`, `postgres`, `redpanda`); it is the dev/sim target for the Postgres and Kafka-compatible adapters and **connects to no broker**; it is not a cell and its resource settings are not a capacity statement | `infra/docker-compose.yml` |

**Therefore, from this seat, explicitly [Committee]:**

- **No cell is provisioned.** No cloud account, region, cluster, node pool, instance type, storage class, disk class, bus, vault or egress gateway is chosen or created. A reader must not infer a deployed component from this document, from `docs/CONTAINER_DIAGRAM.md`, or from the compose file [Open: H-05, A-6, B-15].
- **A cell therefore has no capacity.** There is no CPU, memory, IOPS, storage or network figure to state, because there is no thing to state it about; every per-cell dimension in §1 is a *shape*, and the numbers arrive only after H-05 (provisioning) and the Gate C baselines.
- **The plane boundary is real; the plane capacity boundary is not.** The network policies are enforced and tested (TC-NET-001..004), so no plane can *route* around another. But without ResourceQuota or LimitRange objects, nothing stops one plane's workload consuming a shared node's CPU or memory — noisy-neighbour containment is claimed by the cell topology and implemented by nothing today. Capacity isolation between planes is a Gate C design item, not a Gate B claim [Open].
- **The first cell's contents are the first capacity question a human must answer**, and it is not an architecture question: how many cells, in which regions, at what size, is H-05 plus Q-11-1 (the region whose price list applies) plus D-043 (one venue, cash equities/ETFs, first-party account) — see §8.
- **Cross-cell cost is not zero.** Audit replication is cross-cell **by design**, so cross-cell egress is a permanent cost term of this architecture, not an exception; it has no measurement and no quote (§2, §4a) [Open: O-87, H-05].

## 2. Storage cost model (O-13) — C-CM-2

Inserted per C-CM-2 from docs/SESSIONS/COUNCIL_2026-09-08_gate_B_arb.md §4.3 (the text agreed with D-056). Three deviations from a literal copy, all openly made by the owners [Committee]: (a) mathematical symbols are written in ASCII words so that the formula survives any encoding; (b) the "bytes/row (JSON)" status cell carries its **evidence ids and its scope**, because C-CM-2's own rule requires an evidence id in every filled cell and "[Verified, sim only]" alone does not name the evidence; (c) the "replication/egress" row no longer states a zero — see the row itself. No term or source was added or removed.

Cost per instrument-year = the sum over data classes *d* in {ticks, bars, snapshots, instrument-master versions, derived features} of
`rows_d/year x bytes_d/row x sum over tiers (months_in_tier x unit_price_tier)` + query/compute share + replication/egress share (audit replication is costed separately under the Audit WORM row).

| Term | How it is produced (measurement or source) | Source of truth | Status |
|---|---|---|---|
| rows_d/year per instrument | provider tick/bar rate per instrument class x sessions/year from `SessionCalendar` for the venue; measured on the licensed feed during shadow (PERFORMANCE_PLAN "Soak") | H-08 licence data sheet; F-4 calendars | [Open: H-08] |
| bytes/row (JSON) | `len(model_dump_json())` — 639 B for the sim `MarketSnapshot` with the embedded instrument row | schema + fixture; evidence ids: COUNCIL_2026-09-08_gate_B_arb.md §2 measurement (`RT_ENV=sim`, `build_sim_platform()`), **reproduced independently** by the Independent Validation Agent, REVIEW_2026-09-08_gate_B_iva.md §2 ("Reproductions of factual claims", at `1e8555e`) | measured, **sim fixture only** — a property of the schema and that fixture, not of any licensed feed, venue or deployed system |
| bytes/row (stored) | measured by the adapter's TC-MD-005 on the chosen encoding (row store versus columnar archive), with and without instrument denormalisation | adapter tests, Gate C | [Open] |
| tiers and months per tier | hot = decision-time window (freshness budget NFR-FRS-01 plus backtest look-back), warm = backtest horizon, cold = retention obligation; months per tier from the retention schedule per jurisdiction | RISK_POLICY freshness table; O-09/O-10 schedules | [Open: O-09, O-10] |
| unit price per tier per region | cloud provider price list for the first cell's region, quoted at budget approval; the region follows Q-11-1 | H-05 quote; A-1 | [Open: H-05, Q-11-1] |
| query/compute share | measured CPU/IO of `latest`/`series` under PERFORMANCE_PLAN "Load" and "Spike" on the adapter | Gate C baselines | [Open: O-03] |
| replication/egress | **market data** does not leave its cell (ADR-007), so no market-data egress term is expected — that is a topology statement, **not a measured or quoted zero**, and it lapses if a licence or DR requirement moves the data. **Audit replication is cross-cell by design and the formula defers it "to the Audit WORM row"; no such cost row exists in this sheet**, so the replication term of this model is unowned and unmeasured | ADR-007; DR_PLAN; §4a | [Open] — no number, and one missing row |
| instrument universe and tenants | first cell: one venue, cash equities/ETFs, first-party account (D-043); counts [Open] | D-043; H-05 inputs | [Open] |
| licence constraints on storage | redistribution or derived-data rights, retention obligations or deletion duties imposed by the licence | O-12; H-08 | [Open: O-12] |

Rule for the sheet: **a cell is filled only with a measured or quoted value and its evidence ID; a blank cell is [Open], never an estimate.** D-046 takes prices from this sheet; the sheet must never be back-solved from a price hypothesis (C-13-5) [Committee].

## 3. Control-state store measurement plan (ADR-018) [Committee] — C-CM-3

Growth drivers: every index write and every state transition is a journal row carrying the full value (docs/DATA_FLOWS.md DF-11), and `verify()` at open replays the journal, so it is O(journal) [Open: O-111].

| Measurement | Produced by | Status |
|---|---|---|
| journal rows and store bytes per order lifecycle (create, ack, fill or cancel) | a TC on the compose topology (id by the QA Lead) | [Open] |
| `verify()` time versus journal length (it sits on the restart path of the executor, so a long verify is a long failover) | a synthetic journal of known length in CI first, then PERFORMANCE_PLAN "Soak" | [Open] |
| fsync cost per commit (`synchronous=FULL`) on the target disk class — the disk class is itself unchosen (§1a) | PERFORMANCE_PLAN "Load" | [Open: H-05] |
| lease contention per account under two OS processes | the O-117 tests | [Open] |
| order-cache growth in a long-running process | PERFORMANCE_PLAN "Soak" | [Open] |
| **executor failover time end to end** (lease expiry or preempt, store open with `verify()`, cancel-on-restart of open orders) — the availability figure that NFR-RES-01 and NFR-DR-01 depend on; it is composed of the §7 lease-TTL parameter and the store verify time above, and **neither component is decided or measured**, so the composite is not estimated here | the O-117 tests plus a DR drill (DR_PLAN, O-18) | [Open: O-28, O-18] |
| **cell-level failover time end to end** — the same path preceded by restoring or promoting a standby cell whose stores must open and verify first; it is strictly larger than the in-cell figure above and is the RTO input, not a variant of it (§4a) | a DR drill (DR_PLAN, O-18) | [Open: O-18, O-28] |

## 4. Audit store and external witness measurement plan (ADR-020) [Committee]

The audit trail became durable and externally witnessed after the ARB reviewed this document (D-062). These properties are capacity-relevant and none has a baseline; no figure is invented here [Open].

| Measurement | Why it matters | Produced by | Status |
|---|---|---|---|
| audit chain verification time at open versus chain length (O(events); it runs on every start and gates opening the store) | it sits on the start-up path of the whole platform, next to the control store's `verify()` | a synthetic chain of known length in CI, then PERFORMANCE_PLAN "Soak" | [Open] |
| audit rows and bytes per order lifecycle, and per MCP call | the audit store is a second durable store to size, back up and replicate | a TC on the compose topology (id by the QA Lead) | [Open] |
| anchor records accumulated per unit of activity (one per explicit seal and one per `anchor_every` events), their bytes, and the cost of the anchor chain, which is re-verified on every read | anchor records accumulate without compaction; compaction and retention are owed with the control-store journal's (O-111) | the same TC, plus the O-133 cadence decision | [Open] |
| seal and publication latency, and the cost of an unavailable witness (the fail-closed path) | a missing or stale witness halts the platform via `killswitch_platform` [Open: O-137] | PERFORMANCE_PLAN "Load"; chaos drill per docs/CHAOS_PLAN.md | [Open] |
| restore-and-reverify time for the anchor directory (the documented recovery is to restore the replica, never to disable the check) | it is an input to the recovery time objective (O-134, DR_PLAN) [Open: O-18] | DR drill | [Open] |
| **cross-cell audit replication lag and volume** — the only market-data-free, permanently cross-cell traffic in the architecture (ADR-007) | it is the recovery-point input for the audit trail and the one egress term §2 cannot avoid | a DR drill plus a deployed second cell | [Open: O-18, O-87] |

## 4a. Recovery consequences: two O(n) checks on the start-up path [Committee] [Source: 03, 10] — Cloud Architect, O-18

This section is a **dependency statement, not a measurement**. It contains no number and proposes none.

Two verifications are now unconditional on process start, and both are linear in history:

- the **control store** replays its hash-chained journal at open and compares it with state — O(journal rows), and the journal is never compacted (ADR-018 §Consequences, O-111, O-55);
- the **audit store** verifies its whole chain at open, and the anchor chain is re-verified on every read — O(events) plus O(anchors), with anchors accumulating without compaction (ADR-020 §Consequences, O-133).

Both are the correct fail-closed design and neither should be weakened for speed: recovery is *restore then verify*, and disabling the check is never the fix (O-134). Their capacity and DR consequences are:

| Consequence | Why | Register |
|---|---|---|
| **Restart time grows with history, and restart time is how long an account has no executor.** The executor recovery path is lease expiry or preempt → store open with `verify()` → cancel-on-restart | the verify is on the critical path of every restart, planned or not | [Open: O-111, O-28] |
| **Cell failover inherits both checks, not one.** A standby cell that takes over must open a control store *and* an audit store, each verifying its own history, before trading can reopen — and `docs/DR_PLAN.md` already requires "verify chain before reopening trading" as step 2 of the cell-loss order of restoration. That step is now an unmeasured O(n) operation on the recovery-time path | the DR plan's order of restoration (identity/vault → audit → control → execution → analytics) puts the audit verification ahead of the control and execution planes | [Open: O-18] |
| **RPO/RTO candidates cannot honestly be proposed yet.** An RTO is a promise about a path whose two longest unmeasured steps are these verifications plus the restore itself; an RPO for the audit trail depends on the cross-cell replication lag of §4, which has no measurement and no provisioned replica | O-18 is therefore blocked on O-111, O-133 and a drill, not merely on a human choosing a number | [Open: O-18, O-111, O-133] |
| **The DR drill must measure, not assert.** The drill that settles O-18 has to record verify time against the actual journal and chain length at drill time, and state that length — otherwise the resulting RTO is valid only for an empty system and will be quoted for a full one | a drill on a fresh cell measures the best case and reads as the general case | [Open: O-18] |
| **Compaction and retention are the lever, and neither exists.** Journal compaction (O-111, O-55) and anchor/audit retention (O-133, O-135) are the only ways to bound these two costs, and both are decisions with integrity and legal consequences, not tuning knobs | shortening history to speed recovery is a change to the evidence, so it is the Security & Privacy Board's and Compliance's decision as much as the SRE Lead's | [Open: O-111, O-133, O-135] |
| **Availability consequence of the fail-closed witness.** A lost or corrupt witness halts the platform (`killswitch_platform`, O-137); the time to restore the anchor replica and re-verify is therefore a platform-wide outage duration, and it is unmeasured | this is the largest blast radius of any catalogued alert | [Open: O-134, O-137] |

`docs/DR_PLAN.md` carries the same dependency; its RPO/RTO candidates stay [Open: O-18] until these measurements and a drill exist. **A target is not evidence, and a drill on an empty system is not a baseline** [Committee].

## 5. Measurement plan — all nine SLIs of `observability/slis.yaml` [Committee] — C-CM-4

No target is set for any SLI; `slis.yaml` carries `target: null` for all nine, targets are [Open: O-03] and are decided at Gate E [Source: 10]. The safety-semantic column is the automatic action on breach, and it is why the SLI is a capacity input: it determines whether load is shed, autonomy suspended or the platform stopped. All nine are capacity-relevant; none is excluded.

| SLI | Baseline to measure | Measurement point (`slis.yaml`) | Safety semantic | Why it is capacity-relevant |
|---|---|---|---|---|
| `control_plane_availability` | successful control-plane decisions / total decision requests | `risk_engine` | fail_closed | the Control plane never sheds (NFR-AVL-01); its capacity headroom is the only thing standing between load and a HALTED platform |
| `market_data_freshness_s` | `market_ts` age at snapshot use | `risk_engine.RK-FRESH` | suspend_autonomy | sets the hot tier of §2 and the ingest budget of the market-data store (NFR-FRS-01) |
| `signal_latency_ms` | snapshot to signal | `strategy_service` | informational | sizes Analytics compute per instrument and strategy; it is **not** the autoscaling trigger — the Analytics plane autoscales on `event_lag_ms` (§1) |
| `risk_decision_latency_ms_p99` | intent enqueue to decision-record write, p99 per cell | `oms.pipeline` span | suspend_autonomy | the Control plane's autoscaling trigger (§1) |
| `order_ack_latency_ms` | order command to broker ack | `execution_gateway` | cancel_only_review | bounds how long one lease-holding executor is occupied per order, so it sizes the per-account serial path |
| `event_lag_ms` | produce to consume | `bus` — **this measurement point does not exist in any environment today**: no bus is deployed and dev/sim carries events in process after the outbox write | autoscale | the Analytics plane's autoscaling trigger and the health of the DF-13 relay; the one trigger in §1 that has neither a threshold nor a signal [Open: R-05] |
| `reconciliation_completeness_pct` | reconciled positions / total by EOD+T | `reconciliation_service` | supervised_on_break | sizes the reconciliation window and the batch capacity it needs to close by EOD+T |
| `time_to_halt_s` | Kill Switch engage to the last open-order cancel and identity revocation recorded (D-044) | `killswitch_service.activate` (metric `killswitch.time_to_halt_s`); the drill measures operator-action to engaged separately | informational | it scales with the number of open orders and identities per cell, so a capacity decision changes how long a stop takes [Source: 00] |
| `alert_delivery_s` | alert to operator ack | `notification` | tested_daily | bounds the auto-action paths of docs/DATA_FLOWS.md DF-18, including `killswitch_platform`; a slow path is a slow stop |

## 6. NFRs this document is the evidence for [Committee] [Source: 03, 10]

| NFR | What this document owes it | State |
|---|---|---|
| NFR-SCL-01 (scalability) | its evidence column in docs/NFR.md already names "Capacity model Gate B": the units of scale, partition keys and autoscaling triggers of §1. Note for the SRE Lead and the Enterprise Architect: NFR-SCL-01 says "stateless services", and §1 now carries **four stateful dimensions** (control store, market-data store, audit store, bus) — true of the service tier, not of the platform; NFR.md is not this document's to amend | structure present; no number; wording mismatch raised, not fixed |
| NFR-AVL-01 (planes never shed, fail closed) | the shed column of §1, `control_plane_availability` in §5, and §1's statement that no shedding mechanism is implemented | structure present; budget [Open: O-03]; mechanism [Open] |
| NFR-RES-01 (cells as failure domains, active/standby execution) | the cell view of §1a and the executor failover measurement of §3 | [Open: O-28, O-117]; and the cell topology itself is ADR-007 `Proposed` (§0) |
| NFR-DR-01 (RPO/RTO per cell) | §4a, the restore-and-reverify of §4 and the two failover rows of §3 | [Open: O-18, blocked on O-111 and O-133] |
| NFR-FRS-01 (freshness) | the hot tier of §2 and `market_data_freshness_s` in §5 | [Open: O-03] |
| NFR-CON-01 (idempotency under at-least-once) | the bus row of §1: duplicates are handled by the consumer inbox, so consumer capacity carries duplicate load | [Open: R-05] |
| NFR-SEC-01 (no analytics → execution route) | §0's two capacity rules (no plane bypass, no egress widening) and the checker rules that enforce them | enforced and tested (TC-NET-001..004); capacity may not weaken it |

## 7. Parameters that exist in code as defaults, not targets [Committee] — C-CM-3

These are read out of the source; none is a decision, a baseline or a target, and none may be cited as one. Citations are by module and symbol so they survive an edit.

| Parameter | Default in code | Where | Status |
|---|---|---|---|
| lease TTL | 30 s | `services/execution/execution_gateway/lease.py` (`LeaseStore.acquire`, `preempt`, `renew`) | [Open: O-28] — code default, not a target; it is **not** the executor failover time (§3) |
| store busy timeout, then `StoreError` (fail closed) | 5 s | `libs/core/rtcore/store.py` (`SqliteStore.__init__`) | [Open: O-117] — code default, not a target |
| command maximum age | 5 min | `services/execution/execution_gateway/gateway.py` (`COMMAND_MAX_AGE`, ADR-015 addendum) | [Open] — code default, not a target |
| audit anchor cadence `anchor_every` | 25 events | `services/audit/audit_service/store.py` (`DEFAULT_ANCHOR_EVERY`) | [Open: O-133] — dev/sim placeholder; it bounds how many events a consistent-rewrite attacker could reach, so it is a risk decision |
| audit anchor staleness ceiling `max_anchor_lag` | 200 events | `services/audit/audit_service/store.py` (`DEFAULT_MAX_ANCHOR_LAG`) | [Open: O-133] — dev/sim placeholder; it bounds how stale the witness may be |

## 8. Inputs that only humans can supply [Committee] — C-CM-5

- Expected intents per second per cell; number of tenants and accounts at launch; instrument universe size; cloud budget (docs/MISSING_ACTIONS.md H-05).
- Provider tick and bar rates and the licence's storage, redistribution and retention terms (H-08) [Open: O-12].
- The region whose price list applies (Q-11-1) and the price quote itself (H-05, A-1).
- The Finance seat that holds the cost sheet (A-5); the sheet is filled from measurements and quotes, never back-solved from a price hypothesis (C-13-5).
- Retention schedules per jurisdiction (O-09, O-10), which set the months per tier in §2.
- The second principal that owns the anchor directory, and the cadence values of §7 (O-54, O-133).
- The recovery point and recovery time objectives that the failover and restore measurements are compared against (O-18, DR_PLAN) — see §4a for what must be measured before they can be set.
- **The cell plan itself**: how many cells, in which regions, at what size, and whether ADR-007 is decided as proposed (§0, §1a). Nothing in this document chooses a provider, a region, an instance type or a storage class.

**No cell is provisioned and no storage, compute, scaling or bus manifest exists** (§1a); a reader must not infer a provisioned cell from this document [Open: H-05, A-6, B-15].

## 9. Conditions applied in v0.2 [Committee]

| Condition (ARB §4.3, carried by D-061) | Applied |
|---|---|
| C-CM-1 header status; "structure at Gate B, baselines at Gate C, targets at Gate E" replaces the ARB-signs sentence | **yes** — header and §0. The header records the ARB recommendation, D-061's conditional acceptance **of the structure**, and the SRE Lead review, Independent Validation and human PO decision as **pending**. It never reads "accepted" |
| C-CM-2 §Storage cost model inserted with the evidence-id rule | **yes** — §2, with three openly stated deviations from a literal copy. The only filled value is the 639 B sim measurement with two evidence ids |
| C-CM-3 control-state store row and measurement plan; code defaults listed as parameters | **yes** — §1 (row), §3 (five measurements plus two failover rows), §7 (five parameters, cited by symbol) |
| C-CM-4 measurement plan extended to all nine SLIs | **yes** — §5; all nine are capacity-relevant, so no exclusion reason is claimed |
| C-CM-5 human-input list extended; the line that no cell is provisioned | **yes** — §8 and §1a, which states the infrastructure inventory object kind by object kind |
| C-CM-6 SRE Lead review recorded in the header; AEI row; CONTAINER_DIAGRAM line 44 | **partly, and the remainder is not the owner's to close.** (a) the header records the SRE Lead review as **pending** — it has not happened and cannot be self-signed [Source: 13]; (b) the AEI row is **proposed, not written**, in docs/SESSIONS/REVIEW_2026-09-08_capacity_v0.2_adopted.md §7, because no owner writes the evidence index for his own artefact; (c) the CONTAINER_DIAGRAM correction **is applied** (v1.1) by the Enterprise Architect, and its reviewer of record — the Cloud Architect — has **not** reviewed it in this session |
| added by the owners, not ARB conditions | §0 plane-bypass, egress-widening, ADR-007-status and CI-timing rules; §1 outbox/bus row and the three-gap autoscaling note; §1a cell topology and infrastructure inventory; §3 executor and cell failover rows; §4a recovery consequences; §4 cross-cell replication row; §5 measurement-point and safety-semantic columns; §6 NFR mapping; §10 change log |
| new since the ARB review (not a condition) | §1 audit-store row, §4 audit measurement plan (ADR-020, D-062), the two anchor cadence parameters in §7 |

## 10. Change log [Committee]

| Version | Date | Change |
|---|---|---|
| v0.1 | earlier | skeleton: planes, shed policy, four SLIs, human inputs |
| v0.2 | 2026-09-08 | C-CM-1..C-CM-6 applied (§9). Drafted by the Data Architect (REVIEW_2026-09-08_architecture_docs_v1.1.md Appendix A); adopted with fourteen amendments by the Enterprise Architect (REVIEW_2026-09-08_capacity_v0.2.md §3); adopted with further amendments and written to this file by the Cloud Architect (REVIEW_2026-09-08_capacity_v0.2_adopted.md §3), who added §1a, §4a, the §1 autoscaling gaps, the ADR-007 status rule, the egress rule and the §2 replication correction. Still no number beyond the one measured, evidence-carrying cell in §2 |

## 11. Review record (Definition of Done for this document) [Committee] [Source: 13]

| Step | Role | State |
|---|---|---|
| Drafter | Data Architect | drafted the C-CM-1..C-CM-6 text; is neither owner nor reviewer |
| Content owner | Enterprise Architect | adopted with amendments, 2026-09-08; could not write this path |
| Owner of this write path | Cloud Architect | **v0.2 adopted, amended and written**, 2026-09-08 |
| Reviewer (different line) | SRE Lead | **pending** — no owner may sign for this row. §5 now carries all nine SLIs, including `time_to_halt_s` and `control_plane_availability` |
| Approving body (advisory) | ARB | structure recommended on v0.1 (C-CM-1..C-CM-6); has **not** seen v0.2; no number is accepted and none is presented |
| Independent validation | Independent Validation Agent | pending |
| Decision | **human Product Owner (D-039)** | **pending** — agents never record an approval |
