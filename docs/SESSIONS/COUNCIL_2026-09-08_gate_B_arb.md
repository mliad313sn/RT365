# COUNCIL 2026-09-08 — Gate B (Architecture): ARB chair packet for O-04, O-13, O-17

| Council | Date | Member | Line | Status |
|---|---|---|---|---|
| Architecture Review Board (advisory; convened by the Product Owner delegate under D-040/D-051 for the Gate B decisions in the ARB scope) | 2026-09-08 | ARB chair (`approve-arb-chair`, independent approver per D-039) hearing enterprise-architect, data-architect, cloud-architect, integration-architect, security-architect, sre-lead; counsel-broker-integration, counsel-platform-reliability | 2nd (approver within delegated scope) | recommendation, decision pending |

> Nothing in this packet is a decision. The ARB verdicts in §7 are technical approvals within the delegated scope (ADRs, standards, contracts, NFRs, capacity model, topology, distribution); the Product Owner (human; delegate agent under D-040) decides and records D-nnn. No environment is authorised, no market, broker, data entitlement, price, throughput figure or regulatory status is asserted. Profit is an objective, never a promise [Source: 00]. Every statement is tagged [Source: NN] (blueprint section as transmitted by the repository artefacts; the blueprint itself is not in the tree), [Committee] (council reasoning), [Verified] (re-read or executed by me at the commit named in §0) or [Open].

---

## 0. Provenance, tree state, independence and scope check

| Item | Value |
|---|---|
| Head at the start of the session | `d1ccb21596456977a7d1b69d4694eb4724546445`, working tree dirty (docs/IMPROVEMENT_REGISTER.md, docs/PMO_MERIDIAN_ASSESSMENT.md, docs/PO_DECISION_QUEUE.md, docs/RAID_LOG.md modified by a concurrent agent; `.claude/worktrees/` untracked) [Verified: `git rev-parse HEAD`, `git status --short`] |
| Head at the close of the session | `7b11f796a1a7ffb910ffbb28890c6daf5e29dfb8` "Guard hook at project level with payload identity (O-58 probe), declared-closure lock and clean SCA (idna 3.19), Meridian issues #1-#12 recorded, concerns channel to the Product Owner"; tree clean after I restored the evidence files that my own `make all` regenerated (`git checkout -- docs/TEST_CASES`) [Verified] |
| Consequence | The tree moved during the session (another agent committed). Every check in §2 was run twice; the results quoted are those at `7b11f79`. A Product Owner decision on these items should cite `7b11f79` or a later CI-evidenced commit (O-65) [Committee] |
| Files I edited | only this file. I ran `make all`, `scripts/export_event_schemas.py --check`, `scripts/check_network_policies.py`, a targeted pytest selection and one measurement script in the session scratchpad (§4.3). RAID rows, AEI rows and queue text are **proposed** in §8–§9 for the owning roles because the convening instruction limits this session to this file [Verified] |
| Author ≠ reviewer ≠ approver (procedure step 1) | ADR-009: author Enterprise Architect (D-006 "Enterprise Architect (pending ARB)"), consulted Backend Lead, Integration Architect, Security Architect [Verified: ADR-009 header; DECISION_LOG D-006]. ADR-004: no author decision (deferred) [Verified]. CAPACITY_MODEL: owner Enterprise/Cloud Architect, reviewer SRE Lead, approving body ARB [Verified]. ROADMAP: owner Product Director, reviewer Program Orchestrator, approving bodies Product Council and Executive Steering [Verified]. I authored none of them and reviewed none of them; I do not recuse. **Caveat:** this packet contains both the council option analysis (§3–§5, [Committee] chair synthesis) and the verdict (§7). The verdict is on the artefacts named above, not on my own recommendation; the recommendation is advice to the Product Owner. The Independent Validation Agent has **not** been heard in this session (procedure step 3) — its finding is [Open] and requested in §9 before any decision is recorded |
| Scope check (delegated scope: ADRs, standards and exceptions, contracts, NFRs, capacity model, topology and infrastructure design, distribution and packaging design) | O-04 — in scope (ADR-009; contracts; packaging). O-13 — in scope (ADR-004; capacity model; topology; residency) with Finance for the cost sheet; the Finance seat is unstaffed and held by the owner (H-01, A-5) [Verified: PRODUCT_OWNER.md §Relationship; IMPROVEMENT_REGISTER A-5]. O-17 — **partly outside scope**: the roadmap calendar belongs to the Product Council / Executive Steering (ROADMAP.md header; the queue names the Product Council). My verdict on O-17 covers only what is in scope — the capacity-model dependency and the form of the roadmap (gate-driven sequencing); on the calendar itself I give a recommendation, not an approval [Committee] |
| Council members | Separate member packets were not written in this session; §6 records each member's option analysis and the different-line challenge as chair synthesis from the role prompts and the artefacts they own, tagged [Committee]. Any member may file a dissenting packet `COUNCIL_2026-09-08_gate_B_<role>.md` before the decision is recorded |

---

## 1. Roles

| Function | Role | Line | Contribution |
|---|---|---|---|
| Decision authority | Product Owner (human, GitHub `mliad313sn`); delegate `product-owner` agent under D-040 | 1st | decides O-04, O-13, O-17; records D-nnn with alternatives and dissent |
| Approver within delegated scope | ARB chair (this packet) | 2nd | verdicts §7; conditions; recommendation |
| Members heard | enterprise-architect (ADR-009, CAPACITY_MODEL owner), data-architect (DATA_MODEL, DATA_FLOWS owner), cloud-architect (infra, DR_PLAN owner), integration-architect (contracts), security-architect (SECURITY_PLAN, THREAT_MODEL), sre-lead (reviewer of NFR and CAPACITY_MODEL) | 1st/2nd | option analyses §6 |
| Counsel | counsel-broker-integration, counsel-platform-reliability | advisory | different-line challenges §6 |
| Independent validation | Independent Validation Agent | 3rd | **not heard — [Open]**; finding requested §9 |
| Owning roles for the artefact edits | Enterprise Architect (ADR-009, ADR-004 rev.2, CAPACITY_MODEL), Data Architect (DATA_MODEL, DATA_FLOWS), Product Director (ROADMAP), Program Orchestrator (DECISION_LOG, RAID, AEI, queue) | 1st/2nd | execute §3.6, §4.6, §5.6 after the decision |

---

## 2. Evidence read and checks run

**Read [Verified]:** GOAL.md; docs/PRODUCT_OWNER.md; docs/PO_DECISION_QUEUE.md (rows O-04, O-13, O-17, §B2, §B3, §C); goals/decisions/O-04, O-13, O-17 decision packs; docs/ADRs/ADR-004, 005, 007, 009, 010, 011, 016; docs/CAPACITY_MODEL.md; docs/ROADMAP.md; docs/DATA_MODEL.md; docs/DATA_FLOWS.md; docs/NFR.md; docs/GLOBAL_COMPATIBILITY.md; docs/RAID_LOG.md rows O-03, O-04, O-05, O-09, O-10, O-12, O-13, O-14, O-15, O-17, O-18, O-19, O-22, O-23, O-24, O-26..O-28, O-54..O-56, O-62..O-76, R-03, R-05, R-23, R-31, R-48; docs/DECISION_LOG.md D-006, D-024, D-035, D-040..D-051; docs/IMPROVEMENT_REGISTER.md §A, §B, §C, §F, §Execution; docs/MISSING_ACTIONS.md H-01, H-04..H-08, H-20, H-21, H-24..H-29; docs/PERFORMANCE_PLAN.md; docs/DR_PLAN.md; docs/RELEASE_CHECKLIST.md; docs/PROJECT_EXECUTION_PLAN.md phases 2–7; docs/GATE_REPORTS/GATE_A_2026-09-08.md (conditions GA-C1..GA-C8) and GATE_B_2026-09-07.md (IVA-13, capacity model PARTIAL); docs/REQUIREMENTS_TRACEABILITY.md rows FR-03, FR-08, NFR-DET-01, NFR-TEN-01, NFR-PRV-01, NFR-DIST-01; docs/THREAT_MODEL.md T-12..T-24; docs/CONTAINER_DIAGRAM.md line 44; docs/SESSIONS/C02_architecture.md (C2-D6, C2-D7, O-24, O-26) and C07_data_quant_validation.md (ADR-011 bitemporal row, FR-03/FR-08 RTM rows); docs/AUDIT_EVIDENCE_INDEX.md rows 1, 1b, 2b; pyproject.toml; infra/docker-compose.yml; infra/kubernetes (namespaces, network-policies); services/market-data/market_data/store.py; libs/core/rtcore/schemas/market.py; apps/web/web_bff/app.py (route table); contracts/api/API_OPENAPI.yaml and contracts/events/*.json (21 schemas); test/contract/test_openapi_alignment.py; test/quartets/test_tc_md_marketdata.py.

**Checks run at `7b11f79` [Verified, verbatim]:**

```
$ make all                                   (exit=0, 11.9 s)
ruff check .                                 All checks passed!
ruff format --check .                        136 files already formatted
python3 -m mypy libs services mcp connectors observability apps
                                             Success: no issues found in 97 source files
python3 scripts/export_event_schemas.py --check
                                             OK: 21 event schemas match the models
python3 scripts/check_network_policies.py    OK: network policies satisfy plane invariants (TC-NET)
python3 scripts/verify_tool_registry.py      NOTE: registry is a sim FIXTURE (approvals pending); it embodies no approval and is refused outside dev/sim
                                             OK: registry 0.1.0 (dev key), 6 tools, policies consistent
python3 scripts/generate_agents.py --check   OK: 67 agents in .claude/agents match goals/
python3 scripts/secret_scan.py               OK secret scan: 545 files, no findings
python3 -m pytest                            171 passed, 2 warnings in 8.10s
python3 scripts/evidence_report.py           wrote docs/TEST_CASES/EVIDENCE_REPORT.md: 151 records, 18/18 areas with full quartet
python3 scripts/export_test_cases.py         wrote 18 TEST_CASES files
```

The two pytest warnings are `StarletteDeprecationWarning: Using httpx with starlette.testclient is deprecated; install httpx2 instead` and `DeprecationWarning: The anyio.abc.BlockingPortal alias is deprecated` — both from the FastAPI/Starlette test client, relevant to O-04 condition C-04-2 [Verified].

```
$ RT_ENV=sim python3 -m pytest -q -p no:cacheprovider -W ignore -k "tc_net or tc_ex or tc_pkg or openapi or tc_md" -rA
PASSED test/contract/test_openapi_alignment.py::test_trade_intent_matches_openapi
PASSED test/contract/test_openapi_alignment.py::test_decision_record_matches_openapi
PASSED test/contract/test_openapi_alignment.py::test_killswitch_levels_match_openapi
PASSED test/contract/test_openapi_alignment.py::test_event_schemas_have_no_drift
PASSED test/contract/test_openapi_alignment.py::test_event_catalog_lists_every_schema
PASSED test/contract/test_openapi_alignment.py::test_tool_registry_policy_invariants
PASSED test/contract/test_openapi_alignment.py::test_reason_codes_all_documented
PASSED test/contract/test_openapi_alignment.py::test_bff_routes_match_openapi_paths
PASSED test/quartets/test_tc_ex_execution.py  (17 tests, TC-EX-001..017)
PASSED test/quartets/test_tc_md_marketdata.py (4 tests, TC-MD-001..004)
PASSED test/quartets/test_tc_net_planes.py    (4 tests, TC-NET-001..004)
PASSED test/quartets/test_tc_pkg_cli.py       (4 tests, TC-PKG-001..004)
```
(run first at `d1ccb21`+dirty tree, repeated at `7b11f79`; identical results.)

**Measurement (scratchpad script, `RT_ENV=sim`, `build_sim_platform()`) [Verified]:** one sim `MarketSnapshot` for `SIMEQ1` has 14 top-level fields, serialises to **639 bytes** of JSON (`model_dump_json()`, compact form identical), and the sim feed seeds **31 rows** for that instrument. This is a property of the sim fixture and the schema, not of any licensed feed; it is the only storage number in this packet and it is used solely as the "bytes per row (JSON, sim)" measurement in §4.3.

**Evidence rows [Verified]:** AUDIT_EVIDENCE_INDEX row 2b (Gate B: data flows, ADRs, capacity model, control ownership) has a location, no reviewer, no IVA verification. No AEI row exists for O-04, O-13 or O-17. TEST_CASES/EVIDENCE_REPORT.md at head names the tested tree and the base commit (B-18 delivered in `d1ccb21`).

---

## 3. O-04 — Service framework choice (decision pack)

### 3.1 What the blueprint fixes and what it leaves open
| Fixed | Source |
|---|---|
| Reference stack lists "FastAPI or typed service framework" alongside PostgreSQL, time-series store, Redis, Kafka-compatible bus, schema registry, vault/HSM/KMS | [Source: 03] via CONTAINER_DIAGRAM.md line 44 and C02 §Sources |
| Core guarantees the framework must not weaken: idempotency, monotonic state, outbox/inbox, correlation IDs, stale-data detection, exactly-once business effect | [Source: 03] |
| Risk/eligibility decisions are pure functions of inputs + policy version, identical across replicas | [Source: 05]; NFR-DET-01 |
| Three planes; no analytics→execution route; contracts are the boundary | [Source: 00, 03]; ADR-001, TC-NET |
| Repository layout: one package per bounded context; protected paths | [Source: 16]; pyproject.toml |
| Installable, fail-closed distribution (wheel, one-file executable) | [Committee, ADR-016]; NFR-DIST-01 |
| **Open** | which typed framework; whether the Execution plane later moves to another language/runtime for latency; the performance envelope (NFR-LAT-01/02 targets [Open: O-03]) |

### 3.2 Current state [Verified at `7b11f79`]
- FastAPI is used in exactly one module, `apps/web/web_bff/app.py` (421 lines, `create_app()`, 23 route decorators), implementing `contracts/api/API_OPENAPI.yaml`; `test_bff_routes_match_openapi_paths` fails on drift.
- `grep -rl "fastapi|starlette" services/ libs/` returns nothing: every engine, store and gateway is framework-free, as ADR-009 claims. No test asserts that ban (only `mcp_servers` has an import-ban test per ADR-016) — see condition C-04-3.
- Contracts: Pydantic v2 `StrictModel` (frozen, `extra="forbid"`) is the schema source; the 21 event schemas are exported from the models and checked in CI (`OK: 21 event schemas match the models`).
- Dependencies: `pydantic>=2.6`, `fastapi>=0.110`, `uvicorn>=0.27`, `httpx>=0.27` (pyproject.toml); `requirements.lock.txt` exists and was re-locked in `7b11f79` ("clean SCA (idna 3.19)"); SAST/SCA still advisory (O-23).
- Packaging: the one-file executable bundles FastAPI/uvicorn; TC-PKG-001..004 pass; Windows evidence H-24 open.
- No latency baseline exists (PERFORMANCE_PLAN first gate C; O-03 numbers Gate E).

### 3.3 Options [Committee]
| | Option A — ratify ADR-009: FastAPI + Pydantic v2 strict at the edges; engines framework-free; execution-plane host re-evaluated on measured baselines | Option B — switch the Python edge to another typed framework (e.g. an ASGI framework built on a faster serialiser) | Option C — Go/gRPC for the Execution plane edge now (Python elsewhere) |
|---|---|---|---|
| Pros | Matches the code that carries all 171 tests and 18/18 quartets; single language for engines and edges; OpenAPI contract test exists; event schemas exported from the same models; packaging proven (TC-PKG); largest ecosystem for SCA data | Comparable typing; claimed serialisation speed [Open — vendor claims, unmeasured, not relied upon] | Static binaries; lower per-request latency expected [Open — unmeasured]; language boundary doubles as a plane boundary |
| Cons | Python GIL on the latency path is unmeasured; Starlette/httpx deprecation warnings already visible; dependency surface for SCA | Rewrites the BFF, the contract test, the PyInstaller spec and the e2e journeys for no evidenced gain; the engines gain nothing | Two languages for one control envelope; the strict-schema invariants (unknown fields rejected, Decimal money, injective command digest TC-EX-015, fencing/idempotency TC-EX-001..004) must be re-proven in a second implementation; two SBOMs and two SCA pipelines; the OpenAPI/event contract tests need a second binding; slower schema evolution |
| Cost | none (already built); condition work S | M (rewrite) | L (second toolchain, second quartet set) |
| Risk | low in dev/sim; latency risk deferred to a measurement with a recorded decision point (C-04-1) | medium — churn before Gate B with no measured driver | high before baselines; splits evidence across languages; blueprint 03 does not require it |
| Reversibility | high — one module; engines untouched | high but wasteful | low once adapters and certification runs exist in the second language |
| Controls / tests affected | FR-11, FR-15, NFR-DET-01, NFR-DIST-01, NFR-SEC-02; TC-RK-001, TC-PKG-001..004, test_openapi_alignment (8), TC-E2E | same plus every BFF-bound TC | FR-13, NFR-CON-01, NFR-SEC-01/02; TC-EX-001..017 and TC-NET-* re-evidenced in the new binding; THREAT_MODEL B2/B5 |

### 3.4 Recommendation
**Option A** — ratify ADR-009 with the conditions in §7 (re-evaluation trigger recorded as a measurement, dependency hygiene under the gating SCA, an engine import-ban test). Confidence: **high** for the dev/sim edges and the contract layer; **medium** for the Execution-plane host beyond paper, where the decision point is the PERFORMANCE_PLAN "Latency" (broker sandbox round-trip) and "Load" (risk-decision p99) baselines at Gate C — not a guess now. Provenance: [Verified] code and tests above; [Source: 03, 05]; [Committee] option analysis; [Open: O-03 targets].

### 3.5 Draft DECISION_LOG line (number assigned by the delegate)
```
| D-05x | 2026-09-08 | O-04: service framework — ADR-009 ratified: FastAPI + Pydantic v2 strict models (frozen, extra=forbid) for every contract and service edge; risk, eligibility, execution and audit engines remain framework-free pure functions (no fastapi/starlette import under services/ or libs/, enforced by test); the Execution-plane host language is re-evaluated at Gate C on the PERFORMANCE_PLAN latency and load baselines (decision point recorded in RAID), never on a date; fastapi/starlette/uvicorn pinned in requirements.lock.txt and covered by the gating SCA (O-23) before any environment beyond sim | Product Owner agent under D-040 · Council: ARB APPROVE WITH CONDITIONS C-04-1..C-04-4 (COUNCIL_2026-09-08_gate_B_arb.md) · IVA: [Open] · Dissent: none recorded | Another Python typed framework (rejected: rewrite without a measured driver); Go/gRPC Execution edge now (rejected: two languages for one control envelope before any baseline; re-open at Gate C if the baseline requires it) | [Source: 03, 05] / [Committee] / [Open: O-03] | ADR-009 Accepted; RAID O-04 Decided; CONTAINER_DIAGRAM line 44; AEI row 2b |
```

### 3.6 Artefact edits implied (owning role executes after the decision)
| Artefact | Edit | Owner |
|---|---|---|
| docs/ADRs/ADR-009.md | Status → `Accepted (ARB 2026-09-08, conditions C-04-1..C-04-4; PO decision D-05x)`; add section "Re-evaluation trigger": the Execution-plane host is re-decided at Gate C if the measured `order_ack_latency_ms` or `risk_decision_latency_ms_p99` baseline exceeds the budget set under O-03 — the budget is [Open], the measurement is fixed; add "Engine purity guard: TC-ARC-001" | Enterprise Architect |
| docs/DECISION_LOG.md | D-006 row: mark "closed by D-05x" | Program Orchestrator |
| docs/RAID_LOG.md | O-04 → Decided (D-05x); new O-77 (Execution-plane host re-evaluation at Gate C, owner Enterprise Architect + Performance & Chaos Lead) | Program Orchestrator |
| docs/CONTAINER_DIAGRAM.md line 44; docs/SESSIONS/C02 line 22 | remove `[Open: O-04]`, cite D-05x | Enterprise Architect |
| docs/NFR.md NFR-SEC-02 | note: fastapi/starlette/uvicorn/httpx in the declared closure are pinned and scanned by the gating SCA (O-23) | Enterprise Architect |
| test/ (new) | TC-ARC-001 import ban: no module under `services/`, `libs/core/rtcore` imports `fastapi`, `starlette` or `uvicorn` (positive: BFF may; negative: engine may not; abuse: transitive import via a helper; recovery: n/a — record as a static check) | Backend Lead (E13) |
| docs/REQUIREMENTS_TRACEABILITY.md NFR-DET-01 | add TC-ARC-001 to the test column | QA Lead |
| docs/PO_DECISION_QUEUE.md row O-04 | Council status "convened 2026-09-08: COUNCIL_2026-09-08_gate_B_arb.md"; Recommendation = §9 text | product-owner delegate |
| docs/AUDIT_EVIDENCE_INDEX.md row 2b | Reviewer column: "ARB chair — agent approval with conditions C-04, C-13, C-17; human PO decision pending" | Program Orchestrator |

### 3.7 Human actions
None external (no contract, licence or credential). The Product Owner records the decision; A-5 (Backend Lead seat) remains open in §A of the register; O-23 (gating SCA) is already a Gate B queue item and becomes a condition here.

---

## 4. O-13 — Time-series / snapshot storage cost model (decision pack)

### 4.1 What the blueprint fixes and what it leaves open
| Fixed | Source |
|---|---|
| Reference stack: PostgreSQL, a time-series store, object storage (evidence), Redis (controlled cache), Kafka-compatible bus with schema registry | [Source: 03] via CONTAINER_DIAGRAM.md line 44 |
| Bitemporal snapshots (as-of and knowledge time); point-in-time instrument universe including delisted names; reproducible data snapshot reference for backtests | [Source: 08]; DATA_MODEL MarketSnapshot, Instrument; `snapshot_id_for_range` |
| Market data is licensed, non-personal; provenance stamp, freshness SLA, entitlement at ingest; derived/redistribution rights are a licence question | [Source: 03, 06]; DF-01, DF-02; O-12, H-08 |
| Residency per tenant region; retention schedules per jurisdiction; legal hold; audit WORM replicated cross-cell | [Source: 06, 00]; NFR-PRV-01, NFR-GLO-01, DF-07; CAPACITY_MODEL "Audit WORM" |
| Regional cell = failure domain; cross-cell traffic limited to audit replication and portfolio roll-up | [Committee, ADR-007] |
| Dev/sim in-memory stores with narrow interfaces; Postgres / Kafka-compatible / WORM adapters replace them before Gate C; durability re-evidenced on the deployed topology | [Committee, ADR-010]; R-05, B-1 |
| Billing prices come from the cost model; billing never gates a control | D-046; NFR-BIL-01 |
| **Open** | the store (ADR-004 "Deferred"); cost per instrument-year of ticks/bars/snapshots; retention per data class; hot/warm/cold tiering; whether the first cell needs tick-level data at all (strategy set [Open: Gate C]); every price and rate (H-05, H-08) |

### 4.2 Current state [Verified at `7b11f79`]
- `BitemporalStore` (services/market-data/market_data/store.py, 63 lines): `dict[instrument_id, list[MarketSnapshot]]`; `put` appends and re-sorts by `(market_ts, ingest_ts)`; `latest` is a linear scan with `LookAheadViolation` when `as_of > knowledge_ts`; interface = `put, latest, series, market_timestamps, count, next_after, snapshot_id_for_range` (7 methods). Tests TC-MD-001..004, TC-BT-001..003 pass; R-03 defence is structural in this class (C07 ADR-011 row, "Proposed, pending ARB").
- `MarketSnapshot` embeds the full `InstrumentAttributes` row (13 fields) in every snapshot; 639 bytes JSON per sim row (§2). Denormalising the instrument to a versioned reference is a storage-layer choice that changes no contract (event `market.snapshot.v1` stays as exported) — see §4.6.
- infra/docker-compose.yml names `postgres:16` and `redpanda v24.1.1` as the replacement targets; no adapter exists (O-24, B-1); no Kubernetes storage manifest exists (infra/kubernetes has namespaces and network policies only).
- CAPACITY_MODEL: "No number in this document is set"; the inputs it needs (tick rates, instrument universe, tenants, budget) are human-supplied (H-05, H-08).
- Retention per jurisdiction: O-09/O-10 Gate D; `holds_for` fails closed without a schedule (D-025). Residency at storage: F-7 Gate D (Cloud Architect, Privacy Lead).
- No THREAT_MODEL row names the market-data store (T-12/T-16 cover audit; T-17 cross-tenant BFF reads). A durable store reachable by SQL introduces a look-ahead bypass path (read without knowledge time) and a cross-region replication path — no threat row, no test → condition C-13-3.

### 4.3 Cost model structure (no number is set; each term names the measurement that produces it)
Cost per instrument-year = Σ over data classes *d* ∈ {ticks, bars, snapshots, instrument-master versions, derived features} of
`rows_d/year × bytes_d/row × Σ_tier (months_in_tier × unit_price_tier)` + query/compute share + replication/egress share (audit replication is costed separately under the Audit WORM row).

| Term | How it is produced (measurement or source) | Source of truth | Status |
|---|---|---|---|
| rows_d/year per instrument | provider tick/bar rate per instrument class × sessions/year from `SessionCalendar` for the venue; measured on the licensed feed during shadow (PERFORMANCE_PLAN "Soak") | H-08 licence data sheet; F-4 calendars | [Open: H-08] |
| bytes/row (JSON) | `len(model_dump_json())` — 639 B for the sim snapshot with embedded instrument row (§2) | schema + fixture | [Verified, sim only] |
| bytes/row (stored) | measured by the adapter's TC-MD-005 on the chosen encoding (row store vs columnar archive), with and without instrument denormalisation | adapter tests, Gate C | [Open] |
| tiers and months per tier | hot = decision-time window (freshness budget NFR-FRS-01 plus backtest look-back), warm = backtest horizon, cold = retention obligation; months per tier from the retention schedule per jurisdiction | RISK_POLICY freshness table; O-09/O-10 schedules | [Open: O-09, O-10] |
| unit price per tier per region | cloud provider price list for the first cell's region, quoted at budget approval; region follows Q-11-1 | H-05 quote; A-1 | [Open: H-05, Q-11-1] |
| query/compute share | measured CPU/IO of `latest`/`series` under PERFORMANCE_PLAN "Load" and "Spike" on the adapter | Gate C baselines | [Open: O-03] |
| replication/egress | cross-cell traffic is limited to audit replication and portfolio roll-up (ADR-007); market data does not leave its cell — 0 by design unless a licence or DR requirement says otherwise | ADR-007; DR_PLAN | [Committee] |
| instrument universe and tenants | first cell: one venue, cash equities/ETFs, first-party account (D-043); counts [Open] | D-043; H-05 inputs | [Open] |
| licence constraints on storage | redistribution/derived-data rights, retention obligations or deletion duties imposed by the licence | O-12; H-08 | [Open: O-12] |

Rule for the sheet: **a cell is filled only with a measured or quoted value and its evidence ID; a blank cell is [Open], never an estimate.** D-046 takes prices from this sheet; the sheet must never be back-solved from a price hypothesis (C-13-5).

### 4.4 Options [Committee]
| | Option A — Postgres-first bitemporal store per cell + object-storage archive; TSDB decided by a measured trigger | Option B — dedicated time-series database for ticks/bars from the start (Postgres for control-plane records) | Option C — object storage only (immutable daily columnar files per instrument, index in Postgres) |
|---|---|---|---|
| Design | One Postgres instance per regional cell (ADR-007) with a `market_snapshot` table partitioned by instrument and market_ts, unique on `(instrument_id, market_ts, ingest_ts)`, index on `(instrument_id, market_ts DESC, ingest_ts)`; the adapter implements the 7-method interface and raises `LookAheadViolation` exactly as the in-memory store; instrument attributes stored once per version and joined; closed daily partitions exported to an open columnar file format in the cell's object store (WORM-capable) which also yields the reproducible `snapshot_id_for_range`; the docker-compose target already exists | Second store with its own ingest, compaction, retention policies; knowledge time modelled as a column and enforced by the adapter (bitemporality is not assumed native — vendor capability [Open], must be proven by TC) | All reads at decision time served from files plus a hot cache (Redis) |
| Pros | One durable store already in ADR-010/compose; residency = the cell's instance (ADR-007, F-7); bitemporal query is plain SQL; single backup/restore and DR story (DR_PLAN); tenant partitioning by row-level policy (NFR-TEN-01); cheapest path to Gate C; the archive tier gives cold cost and WORM for backtest reproducibility | Purpose-built ingest and compaction; retention policies native | Cheapest cold storage; immutability and snapshot ids trivial |
| Cons | Vanilla row store may not sustain tick-level ingest for a large universe — unmeasured [Open]; partition maintenance | Second store to secure, back up, replicate and drill (NFR-DR-01, NFR-RES-01); licence/terms [Open]; more operations before any environment exists; capability claims must be proven | Intraday knowledge time and sub-second `latest` reads for RK-FRESH are poor; the cache becomes the real store; not suitable as the decision-time store |
| Cost | no new licence; infra per H-05 quote; adapter effort M (already B-1) | M–L (store + ops + adapter + drills) | M (adapter + cache + index) |
| Risk | medium only if the first cell requires tick-level data at high rates — the first-cell hypothesis (cash equities, PAPER, first-party) does not establish that; the strategy set at Gate C does [Open] | high before any measured need; vendor dependence | high for decision-time freshness |
| Reversibility | high: the interface is 7 methods; the archive format is open; a TSDB can be added behind the same interface later | medium (data migration and drills) | medium |
| Controls / tests affected | FR-03, FR-08, R-03; NFR-TEN-01, NFR-PRV-01, NFR-RES-01, NFR-DR-01, NFR-SCL-01; TC-MD-001..004 and TC-BT-001..003 re-run against the adapter; new TC-MD-005..008 (§7 C-13-2); THREAT_MODEL new row (C-13-3) | same plus second-store DR/backup TCs and NFR-DR-01 | same plus cache-consistency TCs |

### 4.5 Recommendation
**Option A** as the Gate C adapter and the baseline of the cost sheet, with Option C's object-storage archive as the cold tier and Option B as a **re-decision trigger defined as a measurement**: "adopt a dedicated time-series store for a data class *d* when the Postgres adapter's measured sustained ingest or query latency under PERFORMANCE_PLAN Spike/Soak fails the budget set under O-03, or when the measured cost per instrument-year of *d* under Option A exceeds the quoted alternative by a margin Finance sets" — both thresholds [Open]. This respects ADR-010 (Postgres/Kafka-compatible adapters before Gate C), ADR-007 and NFR-GLO-01 (the store lives in the tenant's regional cell; market data never crosses cells), and ADR-011/R-03 (look-ahead enforced at the store, not by convention). Confidence: **medium-high** for the structure and the interface; **none** for any number — no number is recommended. Provenance: [Verified] store.py, schema, compose, RTM/threat rows; [Source: 03, 06, 08]; [Committee]; [Open: H-05, H-08, O-03, O-09, O-10, O-12, Q-11-1].

### 4.6 Draft DECISION_LOG line and artefact edits
```
| D-05y | 2026-09-08 | O-13: storage architecture and cost-model structure adopted — ADR-004 rev.2: bitemporal market-data store = PostgreSQL per regional cell (partitioned by instrument/market_ts; unique (instrument_id, market_ts, ingest_ts); LookAheadViolation enforced by the adapter; instrument attributes versioned, not duplicated) plus an object-storage archive of closed daily partitions in an open columnar format inside the same cell (cold tier, WORM-capable, source of snapshot_id_for_range); no cross-cell market-data replication (ADR-007); a dedicated time-series store is adopted for a data class only when a measured trigger (PERFORMANCE_PLAN Spike/Soak or the cost sheet) exceeds a budget set under O-03/Finance. Cost per instrument-year = CAPACITY_MODEL §Storage cost model with every term [Open] until measured or quoted; no cost figure is recorded; D-046 prices remain [Open] | Product Owner agent under D-040 · Council: ARB APPROVE WITH CONDITIONS C-13-1..C-13-6 (COUNCIL_2026-09-08_gate_B_arb.md); counsel-platform-reliability dissent-with-trigger on tick-level ingest (§6) · IVA: [Open] | Dedicated TSDB from the start (rejected: second store without a measured need; capability claims unproven); object storage only (rejected: decision-time freshness reads) | [Source: 03, 06, 08] / [Committee] / [Open: H-05, H-08, O-03, O-09, O-10, O-12, Q-11-1] | ADR-004 rev.2; CAPACITY_MODEL §Storage; RAID O-13 Decided (structure), O-78 (numbers) |
```

| Artefact | Edit | Owner |
|---|---|---|
| docs/ADRs/ADR-004.md | rev.2 per the decision line: Context, Decision, three alternatives with "why not", consequences (adapter before Gate C = B-1 scope; residency per cell; archive tier), controls/tests (FR-03, FR-08, NFR-TEN-01, NFR-PRV-01, NFR-DR-01; TC-MD-001..008, TC-BT-001..003), threat-model delta (new row); Status `Accepted (ARB, conditions C-13-*)` after the PO decision | Enterprise Architect with Data Architect |
| docs/CAPACITY_MODEL.md | new section "Storage cost model (O-13)" = the table of §4.3 verbatim, plus a row "Market-data store" in "What is fixed now" (unit of scale: per cell; partition key: instrument / market_ts; shed: never for decision-time reads, archive jobs shed first); status stays "numbers [Open]" | Enterprise Architect / Cloud Architect; reviewer SRE Lead |
| docs/DATA_MODEL.md | MarketSnapshot note: "stored with an instrument version reference; the contract keeps the embedded attributes"; Instrument: `version` key | Data Architect |
| docs/DATA_FLOWS.md | DF-01/DF-02 controls: "+ stored in the tenant's regional cell; knowledge-time enforced at the store; no cross-cell replication" | Data Architect |
| docs/THREAT_MODEL.md | new row T-25: direct read of the durable market-data store bypassing knowledge time (look-ahead) or tenant/region scope; controls: adapter-only access, DB role without table read for analytics pods, row-level policy; tests TC-MD-007 (abuse) [Open] | Security Architect / Data Architect |
| docs/NFR.md | NFR-FRS-01 note: freshness reads served by the cell-local store; NFR-PRV-01: residency enforced at storage (F-7) — no new NFR needed | Enterprise Architect |
| docs/BACKLOG.md E02/E07 | story "Postgres bitemporal adapter + archive export" with the quartet TC-MD-005..008 and the measurement stories for §4.3 terms | Backend Lead / Data Engineering Lead |
| docs/REQUIREMENTS_TRACEABILITY.md FR-03, FR-08 | evidence column: adapter TCs at Gate C | QA Lead |
| docs/RAID_LOG.md | O-13 → Decided (structure, D-05y); new O-78 "storage cost numbers" (owner Finance seat = Product Owner until A-5; Gate C for measured terms, H-05 for quoted terms); new O-79 "TSDB trigger thresholds" (owner Performance & Chaos Lead; Gate C/E with O-03) | Program Orchestrator |
| docs/MISSING_ACTIONS.md | H-05: add "storage unit prices per tier for the first-cell region"; H-08: add "tick/bar rates and storage/derived-data terms per licence" | Program Orchestrator |

### 4.7 Human actions
| Act | Who | Why | Gate |
|---|---|---|---|
| Supply Q-11-1 (country) so the cell region and price list are determinate | Product Owner (A-1) | region of the store | B |
| Budget approval with a storage price quote per tier for that region | Product Owner + Cloud Architect (A-6, H-05) | unit prices | B |
| Licence data sheet: tick/bar rates, storage and derived-data rights, retention duties | Finance + Legal (A-9, H-08, O-12) | rows/year; licence constraints | C |
| Retention schedule per jurisdiction | Legal Agent, Privacy Lead (O-09, O-10) | months per tier | D |
| Name the Finance owner of the cost sheet or record that the owner holds the seat | Product Owner (A-5) | accountability for numbers | B |

---

## 5. O-17 — Roadmap dates after the capacity model (decision pack)

### 5.1 What the blueprint fixes and what it leaves open
| Fixed | Source |
|---|---|
| Environment ladder dev → sim → shadow → paper → supervised pilot → capped autonomous pilot → controlled GA; a gate authorises only the next rung | [Source: 00]; PO_DECISION_QUEUE §C |
| Gate exit evidence and approving bodies A–F; no date-driven waivers of critical findings | [Source: 12]; RELEASE_CHECKLIST; gate prompts |
| Epics per phase; phase exits only when its gate passes and its MISSING_ACTIONS are closed | [Source: 14]; ROADMAP; PROJECT_EXECUTION_PLAN; GOAL.md work plan 5 |
| Roadmap is gate-driven, not date-driven; dates set once the Gate B capacity model exists | D-003 (ratified D-042); ROADMAP.md |
| Human-only acts and build gaps with the gate each blocks | IMPROVEMENT_REGISTER §A (A-1..A-20), §B (B-1..B-18), §C, §F |
| Executive Steering's date-setting role is held by the Product Owner | D-039/D-040; PRODUCT_OWNER.md |
| **Open** | the calendar for B–F; team size (H-01/A-5: seats held by the owner); budget (H-05); every external lead time (counsel, broker, licences, pen-test) |

### 5.2 Current state [Verified]
- No measured basis for a calendar exists: no team size, no budget, no contract dates, no capacity numbers (the capacity model's numbers arrive at Gate C baselines and Gate E targets — O-03 is a Gate E item; O-13 numbers are Gate C/H-05). The premise "dates after the capacity model" therefore cannot be met literally before Gate C; waiting for it would postpone all planning past the point where the plan is needed [Committee].
- The one measured internal cadence is the ledger itself: Gate A was convened, conditioned and passed on 2026-09-07/08 with 171 tests and 18/18 quartets at head; this measures agent-driven build/council throughput in dev/sim only and says nothing about external acts, which dominate Gates C–F (A-3, A-4, A-6..A-15) [Verified: git log; DECISION_LOG D-048].
- Meridian holds the schedule mirror but is a demo instance until H-28 (Gate C); its four-gate machine is not authorisation (D-049, O-75).

### 5.3 Options [Committee]
| | Option A — set calendar dates for B–F now | Option B — gate-driven sequencing with earliest-possible conditions; a date attaches to a gate only when every human-only predecessor has a committed date from its owner | Option C — rolling short planning windows: dates only for the next gate and the internal build items, re-baselined weekly; external acts carry an "ask date", never a completion date |
|---|---|---|---|
| Pros | Reads like a plan | Honest; complies with D-003 and the [Source: 12] prohibition; makes the human-only acts the visible critical path; measurable once contracts exist | Gives the Product Owner a near-term commitment (Gate B convening) without inventing far dates |
| Cons | No measured basis; every date would be invented; invites date-driven waivers (prohibited); would be re-baselined at once | Produces no calendar until owners commit dates (that is the point) | Far gates remain undated |
| Cost | S (and rework) | S (roadmap columns) | S per week (standing loop C-4 already exists) |
| Risk | governance risk: dates become pressure on controls | none to controls | low |
| Reversibility | high | high | high |
| Controls / tests affected | none directly; indirect pressure on every gate | none | none |

### 5.4 Recommendation
**Option B, with Option C's mechanics for the next gate only.** Decouple the roadmap from the capacity numbers: the capacity model gates Gate E's targets (O-03) and Gate C's baselines, not the calendar. Publish ROADMAP v1.1 with, per gate: environment authorised; internal predecessors (§B/§C/§F items and decision packs); human-only predecessors (§A items); the earliest-possible condition; and the measurement that produces a date. No calendar date is recommended for any gate; the Gate B **convening condition** is stated below and can be dated by the Product Owner alone because its predecessors are all owner acts or agent work. Confidence: **high** for the form; **none** for dates (none proposed). Provenance: [Verified] register and ledgers; [Source: 00, 12, 14]; [Committee].

**Proposed ROADMAP v1.1 rows (sequencing and earliest-possible conditions; no dates)**

| Gate | Authorises | Internal predecessors (agents) | Human-only predecessors (§A) | Earliest-possible condition | What produces a date |
|---|---|---|---|---|---|
| B — Architecture | development, simulation | C-1 (IVA re-validation on the committed head), C-5 ledger hygiene, B-2, B-3, B-15 (Gate B parts), B-18 (done in `d1ccb21`), F-1 (agent part); decisions O-04, O-05, O-13, O-17, O-22, O-23; ADR-001..016 accepted or explicitly deferred; AEI 2b reviewer and IVA columns filled | A-1 (Q-11-1), A-2 (owner authorship), A-3 (counsel scope only), A-5 (seats), A-6 (budget), A-7 (provider terms — or O-05 decided as "no provider before Gate C"), A-18 (Windows evidence, signing decision), A-20 | all predecessors closed in the ledgers; IVA APPROVE on the CI-evidenced commit | the Product Owner's own committed dates for A-1, A-2, A-5, A-6, A-7, A-18, A-20 (all owner acts) + measured council cycle time (Gate A: 2 days for four packs, dev/sim only) |
| C — Paper readiness | shadow, paper | B-1 (durable stores incl. the O-13 adapter), B-4, B-5, B-6, B-7, B-8, B-9, F-3, F-4, F-5; PERFORMANCE_PLAN baselines; TC-RK/TC-EX/TC-KS/TC-NET on the deployed topology (R-05); decisions O-07, O-12, O-19 | A-4 deputy, A-8 broker signed + sandbox certified, A-9 data licences, A-10 numeric limits, A-11 KMS, A-12 WORM anchor, A-19 Meridian real | Gate B passed; cluster provisioned (A-6); broker and data contracts signed; limits filled | contract signature dates from the counterparties (unknown until asked) + certification run duration measured on the sandbox |
| D — Supervised pilot | supervised pilot | B-10, B-11, B-12, B-13 (part), B-14 (part), B-16 (metering), F-2, F-7, F-8, F-9 (part); decisions O-06, O-09, O-10; independent backtest reproduction; drills | A-3 counsel answers, A-4 dual-key humans, A-13 pen-test/red team, A-14 operators + drills, A-15 legal record + DPIA + disclosures | Gate C passed; legal record for the cell; pen-test report; drill evidence | counsel opinion date, pen-test vendor schedule, drill dates (all external) |
| E — Capped autonomy | capped autonomous pilot | runtime halts evidenced in paper and pilot; O-03 targets from baselines; O-08, O-18; B-9 liquidation hook; B-14 SLO targets | A-16 capital envelope, liquidation policy, SLO sign-off | Gate D passed; measured paper/pilot record long enough to set targets (length [Open: Trading Risk Committee]) | the measured observation window, not a date |
| F — Market release | controlled GA (one cell) | E15 (B-17), F-6, F-10, B-13/B-16 remainder; decisions O-14, O-15; release dossier from AEI | A-15 second-person flag, A-17 launch decision | Gate E passed; no open critical; highs risk-accepted in writing | the launch decision itself |

### 5.5 Draft DECISION_LOG line
```
| D-05z | 2026-09-08 | O-17: roadmap remains gate-driven — ROADMAP v1.1 carries, per gate, the internal and human-only predecessors (IMPROVEMENT_REGISTER §A/§B/§C/§F), the earliest-possible condition and the measurement that produces a date; no calendar date is set for Gates C–F; a date attaches to a gate only when every human-only predecessor has a committed date from its owner, and it is re-baselined in the weekly loop (C-4) and mirrored to Meridian (H-28 before it is the schedule of record); the capacity model does not gate the calendar — its numbers gate Gate C baselines and Gate E targets (O-03); the Gate B convening condition is the predecessor set of ROADMAP v1.1 row B, datable by the Product Owner's own acts | Product Owner agent under D-040 · Council: Product Council to confirm (roadmap owner); ARB APPROVE WITH CONDITIONS C-17-1..C-17-4 on the capacity-model dependency and the form (COUNCIL_2026-09-08_gate_B_arb.md) · IVA: [Open] | Calendar dates now (rejected: no measured basis; invites date-driven waivers, prohibited by blueprint 12); wait for capacity numbers (rejected: they arrive at Gates C/E) | [Source: 00, 12, 14] / [Committee] | ROADMAP v1.1; RAID O-17 Decided; PROJECT_EXECUTION_PLAN cross-reference |
```

### 5.6 Artefact edits implied
| Artefact | Edit | Owner |
|---|---|---|
| docs/ROADMAP.md | v1.1: replace "Dates are set by Executive Steering once Gate B capacity model exists [Open: O-17]" with the rule in D-05z; add the §5.4 table (columns: internal predecessors, human-only predecessors, earliest-possible condition, what produces a date); status row reviewer = Program Orchestrator; approving body = Product Council (Executive Steering seat = Product Owner) | Product Director |
| docs/CAPACITY_MODEL.md | header status: "numbers [Open: O-03, O-78]" (O-17 removed — the calendar no longer depends on this document) | Enterprise Architect |
| docs/PROJECT_EXECUTION_PLAN.md | Phase 2 line "Decision packs O-04, O-05, O-13, O-17" — add "(O-17 sets sequencing, not dates)" | Program Orchestrator |
| docs/PMO.md / Meridian | milestones carry conditions, not dates, until H-28 (already rule 5 of PMO.md §3) | Program Orchestrator |
| docs/RAID_LOG.md | O-17 → Decided (D-05z); O-76 "dates placeholders until O-17" → "conditions per ROADMAP v1.1" | Program Orchestrator |

### 5.7 Human actions
The Product Owner commits dates for its own acts A-1, A-2, A-5, A-6, A-7, A-18, A-20 (these alone date Gate B's convening); asks the counterparties for the dates that gate C–F (counsel, broker, data, pen-test) so the ledger can carry committed dates instead of blanks; confirms that the Product Council (Product Director chair) endorses ROADMAP v1.1 since the roadmap is its artefact.

---

## 6. Council option analyses, different-line challenges and dissent [Committee — chair synthesis; members may file their own packets]

| Member | Line | O-04 | O-13 | O-17 |
|---|---|---|---|---|
| enterprise-architect (author of ADR-009 and CAPACITY_MODEL; presents, does not approve) | 1st | Option A; asks that the re-evaluation be a measurement, not a date | Option A; owns ADR-004 rev.2 and the CAPACITY_MODEL section | Option B; decouple the calendar from the capacity numbers |
| data-architect | 2nd | no objection; contracts stay the model source | Option A with two insistences: knowledge-time enforcement at the store (ADR-011 row of C07, R-03) and instrument attributes versioned rather than copied into every row; residency per cell per NFR-GLO-01; wants T-25 and TC-MD-007 before Gate C | Option B |
| cloud-architect | 2nd | no objection; notes the PyInstaller bundle carries uvicorn — Windows evidence H-24 | Option A: one store per regional cell is the only design that keeps residency simple (ADR-007); price quote is H-05, region needs Q-11-1; no Kubernetes storage manifest exists yet — add to B-15/B-1 | Option B; A-6 is the critical path for anything beyond sim |
| integration-architect | 2nd | Option A; a second-language gateway would have to re-prove the injective digest (TC-EX-015) and the fencing/idempotency set (TC-EX-001..004) — not before baselines | Option A; the 7-method interface is the contract; the adapter must pass the existing TC-MD/TC-BT set unchanged | Option B |
| security-architect | 2nd | Option A **conditional** on dependency hygiene: the SCA is advisory (O-23) and two Starlette/httpx deprecation warnings are already in the run; wants the gating SCA before any environment beyond sim and an engine import-ban test | Option A; DB roles per plane (analytics pods must not hold table read on the store); threat row T-25 | Option B; no date-driven waivers |
| sre-lead (reviewer of NFR and CAPACITY_MODEL) | 2nd | Option A; latency baseline at Gate C | Option A; one backup/restore drill story; a second store before any drill exists is unjustified | Option B; the weekly re-baseline is the existing standing loop |
| counsel-broker-integration | advisory | no objection; broker adapters are FIX/REST and independent of the edge framework | no objection; notes licence terms may forbid storing derived data (O-12) | dates for Gate C depend on broker certification, which cannot be scheduled before a signed sandbox agreement |
| counsel-platform-reliability (**different-line challenge**) | advisory | challenge: "FastAPI is being ratified because it is what exists, not because it was measured" — answered: the engines are framework-free and the edge is one module; ratification is of the contract layer, and the latency question is deliberately deferred to a measurement with a recorded decision point (C-04-1). Accepted | **dissent with trigger:** "a vanilla row store will not sustain tick-level ingest for a large universe" — answered: the first-cell hypothesis does not establish tick-level need; the trigger (§4.5) is a measurement, and the interface makes the TSDB additive. **Recorded as dissent** so the Product Owner sees it | challenge: "a plan without dates is not a plan" — answered: a plan with invented dates is worse under blueprint 12; the plan is the predecessor graph plus committed owner dates. Accepted |
| Independent Validation Agent | 3rd | **[Open] — not heard** | **[Open] — not heard** | **[Open] — not heard** |

---

## 7. ARB verdicts

### O-04 — **APPROVE WITH CONDITIONS** (technical approval of ADR-009 within the delegated scope; human PO decision pending)
Reasons: the artefact under approval exists, has two alternatives with "why not", is implemented in one module, is protected by a contract test and the event-schema export check, and leaves the engines framework-free [Verified §2, §3.2]. The latency question is not a reason to reject: no environment beyond sim is authorised by this decision and the decision point is fixed as a measurement.
Conditions (owner, due):
- **C-04-1** ADR-009 gains a "Re-evaluation trigger" section naming the two SLIs (`order_ack_latency_ms`, `risk_decision_latency_ms_p99`) and the PERFORMANCE_PLAN tests that produce them; RAID O-77 opened for the Gate C decision point — Enterprise Architect, before Gate B is convened.
- **C-04-2** fastapi, starlette, uvicorn, httpx pinned in `requirements.lock.txt` (already) **and** covered by the gating SCA of O-23 before any environment beyond sim; the two deprecation warnings tracked as a RAID observation — Security Architect / Cloud Architect, O-23 (Gate B).
- **C-04-3** TC-ARC-001 import-ban test (no `fastapi`/`starlette`/`uvicorn` import under `services/` and `libs/core/rtcore`) added and cited on RTM NFR-DET-01 — Backend Lead (E13), before Gate B is convened.
- **C-04-4** Ledger edits of §3.6 executed by the owning roles; AEI row 2b reviewer column filled with a 2nd-line role, IVA column by the IVA — Program Orchestrator, Gate B.

### O-13 — **APPROVE WITH CONDITIONS** on the storage architecture (ADR-004 rev.2 direction) and the cost-model structure; **no cost figure is approved** (none is presented, and none may be until measured or quoted)
Reasons: Option A is the only option consistent with ADR-010 (adapters before Gate C), ADR-007/NFR-GLO-01 (residency per cell) and ADR-011/R-03 (look-ahead enforced structurally), and it keeps a single durability and DR story for Gate C. The control quartet for the durable store does not yet exist and no threat row covers the store — hence conditions, not rejection, because the artefact is a design decision for Gate C build, not a claim of durability today.
Conditions:
- **C-13-1** CAPACITY_MODEL §Storage cost model carries the §4.3 table with a "how measured / source / status" column; no cell is filled without an evidence ID — Enterprise Architect / Cloud Architect; reviewer SRE Lead; Gate B.
- **C-13-2** Adapter quartet TC-MD-005..008 (positive: put/latest/series with knowledge time on Postgres; negative: `LookAheadViolation` raised by the adapter; abuse: cross-tenant and cross-region read denied, direct-table read by an analytics role denied; recovery: restore from the archive tier and `snapshot_id_for_range` equality) written first and passing on the compose topology before Gate C; TC-MD-001..004 and TC-BT-001..003 re-run unchanged against the adapter — Backend Lead / Data Engineering Lead (B-1, E02/E07), Gate C.
- **C-13-3** THREAT_MODEL row T-25 (durable store read bypassing knowledge time or tenant/region scope) with its test — Security Architect / Data Architect, Gate B (row) / Gate C (test).
- **C-13-4** The TSDB re-decision trigger is written as a measurement (PERFORMANCE_PLAN Spike/Soak SLIs and the cost sheet) with thresholds [Open: O-03, O-79]; never as a vendor claim — Performance & Chaos Lead, Gate C.
- **C-13-5** D-046 billing prices stay [Open] until the sheet has measured/quoted values; the sheet is never back-solved from a price hypothesis — Finance seat (Product Owner until A-5), Gate D.
- **C-13-6** Licence terms on stored and derived data (O-12, H-08) are recorded before any retention beyond sim — Legal Agent / Data Architect, Gate C.

### O-17 — **APPROVE WITH CONDITIONS** on what is in the ARB scope (the capacity-model dependency and the gate-driven form); **REJECT** any calendar date for Gates C–F at this time; **recommendation** (not approval) to the Product Council and Product Owner: Option B with the §5.4 rows
Reasons: no measured basis for a calendar exists [Verified §5.2]; setting dates would contradict D-003 and invite the date-driven waivers blueprint 12 prohibits; the capacity model's numbers arrive at Gates C/E, so tying the calendar to it is a category error the roadmap should drop.
Conditions:
- **C-17-1** ROADMAP v1.1 with the predecessor, condition and measurement columns of §5.4; Product Council endorsement recorded — Product Director, Gate B.
- **C-17-2** A date attaches to a gate only when every human-only predecessor has a committed date from its owner in MISSING_ACTIONS; internal lead times are measured from the ledger, not estimated — Program Orchestrator, standing.
- **C-17-3** Meridian becomes the schedule of record only after H-28; until then it mirrors conditions — Program Orchestrator / SRE Lead, Gate C.
- **C-17-4** Weekly re-baseline in the standing loop (C-4) with the RAID delta reported — Program Orchestrator, weekly.

---

## 8. RAID entries proposed (for the Program Orchestrator; this session edits only this file)

| ID (proposed) | Type | Entry | Owner | Gate |
|---|---|---|---|---|
| O-77 | Decision point | Execution-plane host language re-evaluation on the Gate C latency/load baselines (ADR-009 §Re-evaluation trigger; C-04-1) | Enterprise Architect, Performance & Chaos Lead | C |
| O-78 | Gap | Storage cost-model numbers: every term of CAPACITY_MODEL §Storage [Open] until measured (adapter TCs, PERFORMANCE_PLAN) or quoted (H-05, H-08); feeds D-046 prices | Finance seat (Product Owner until A-5) | C (measured) / B (quoted) |
| O-79 | Gap | TSDB re-decision trigger thresholds for the market-data store (C-13-4) | Performance & Chaos Lead | C/E with O-03 |
| O-80 | Observation | Two Starlette/httpx deprecation warnings in the test run at `7b11f79`; track under dependency hygiene (C-04-2, O-23) | Security Architect | B |
| O-81 | Gap | THREAT_MODEL row T-25 (durable market-data store bypass) and TC-MD-005..008 absent (C-13-2, C-13-3) | Security Architect, Backend Lead | B (row) / C (tests) |
| O-82 | Issue | IVA not heard on O-04/O-13/O-17 in this convening; finding required before the decision is recorded (procedure step 3) | Independent Validation Agent | before the decision |
| O-04, O-13, O-17 | status | "Pack ready — ARB APPROVE WITH CONDITIONS (COUNCIL_2026-09-08_gate_B_arb.md); PO decision pending" | Program Orchestrator | B |

**AEI row proposed (row 2b, reviewer column):** "ARB chair — agent approval with conditions C-04-1..4, C-13-1..6, C-17-1..4 (COUNCIL_2026-09-08_gate_B_arb.md); human PO decision pending" — the IVA column stays blank until the IVA signs.

---

## 9. Decision requests to the Product Owner (one line each, for PO_DECISION_QUEUE rows)

- **O-04:** ARB: APPROVE WITH CONDITIONS — ratify ADR-009 (FastAPI + Pydantic v2 strict at the edges; engines framework-free; Execution-plane host re-decided at Gate C on measured latency; gating SCA and engine import-ban test as conditions). Confidence high (edges) / medium (gateway host). **Decision request:** ratify ADR-009 with C-04-1..C-04-4? IVA finding [Open] first.
- **O-13:** ARB: APPROVE WITH CONDITIONS on the architecture (Postgres bitemporal store per regional cell + object-storage archive; TSDB only by measured trigger) and on the cost-model structure; **no cost number approved**; counsel-platform-reliability dissent on tick-level ingest recorded with the trigger. Confidence medium-high (structure) / none (numbers). **Decision request:** adopt ADR-004 rev.2 and CAPACITY_MODEL §Storage with C-13-1..C-13-6, keeping D-046 prices [Open]? IVA finding [Open] first.
- **O-17:** ARB (in-scope part): APPROVE WITH CONDITIONS the decoupling from the capacity numbers and the gate-driven form; REJECT calendar dates for C–F; recommendation to the Product Council: ROADMAP v1.1 with predecessors, earliest-possible conditions and the measurement that produces a date; Gate B convening is datable by the owner's own acts (A-1, A-2, A-5, A-6, A-7, A-18, A-20). Confidence high (form) / none (dates). **Decision request:** adopt ROADMAP v1.1 as sequencing without dates and commit dates for the owner's own Gate B acts? Product Council endorsement and IVA finding [Open] first.

---

## 10. Human actions required (consolidated)

| # | Act | Who | Register ref | Needed for |
|---|---|---|---|---|
| 1 | Hear the IVA finding on this packet before recording any of the three decisions | Product Owner delegate convenes; IVA | O-82 (proposed) | procedure step 3 |
| 2 | Supply Q-11-1 (operating entity's country) | Product Owner (human) | A-1, GA-C1 | store region and price list (O-13); regulator pointer |
| 3 | Approve budget with a storage price quote per tier for the first-cell region | Product Owner + Cloud Architect | A-6, H-05 | O-13 quoted terms; anything beyond sim |
| 4 | Name or hold the Finance seat for the cost sheet; name remaining seats | Product Owner | A-5, H-01 | O-13 numbers accountability |
| 5 | Commit dates for the owner's own Gate B acts (A-1, A-2, A-5, A-6, A-7, A-18, A-20) | Product Owner | §A | the only datable part of O-17 |
| 6 | Ask counterparties for dates: counsel scope (A-3), broker sandbox (A-8), data licence data sheet with tick/bar rates and storage/derived rights (A-9, H-08, O-12), pen-test (A-13) | Product Owner / Legal / Finance | §A | Gate C–F conditions |
| 7 | Decide O-23 (gating SCA and artefact signing) — condition C-04-2 depends on it | Product Owner with Security & Privacy Board + ARB | O-23 | O-04 condition |
| 8 | Product Council endorsement of ROADMAP v1.1 (Product Director chair) | Product Owner delegate convenes | ROADMAP header | O-17 |

---

## 11. Assumptions, confidence, provenance

- Assumptions: the blueprint text is as transmitted by the repository artefacts [Source: 03, 05, 06, 08, 12, 14, 16]; the first-cell hypothesis D-043 (cash equities/ETFs, first party, PAPER first) stands; no vendor capability, price, throughput figure or licence term is assumed anywhere in this packet — every such value is [Open] with the measurement or source that produces it.
- Confidence: O-04 high/medium as stated; O-13 medium-high for structure, none for numbers; O-17 high for form, none for dates.
- Provenance: [Verified] items were re-read or executed at `d1ccb21` (dirty tree) and `7b11f79` (clean) on 2026-09-08; [Committee] items are this council's reasoning; the IVA finding is [Open]; the Product Owner's decision is [Open].
- Independence: I authored none of ADR-004, ADR-009, CAPACITY_MODEL or ROADMAP and reviewed none of them; I edited only this file; the regenerated evidence files from my `make all` were restored to the committed state. Nothing here is self-certified; nothing here is the Product Owner's decision.
