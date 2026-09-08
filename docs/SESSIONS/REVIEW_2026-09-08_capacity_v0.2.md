# REVIEW 2026-09-08 — CAPACITY_MODEL v0.2 adoption and CONTAINER_DIAGRAM line 44 (O-129, D-061, conditions C-CM-1..C-CM-6)

| Session | Date | Author | Line | Status |
|---|---|---|---|---|
| Enterprise Architect adopting the C-CM-1..C-CM-6 draft as the owning role | 2026-09-08 | enterprise-architect agent, at the direction of the Product Owner delegate's session on O-129 / D-061 | 1st | **one artefact edit applied (CONTAINER_DIAGRAM v1.1); CAPACITY_MODEL v0.2 text owner-adopted but refused by the write-scope guard — delivered here for the Cloud Architect; no approval, no decision** |

> Nothing in this packet is a decision or an approval. CONTAINER_DIAGRAM v1.1 is written by its owner and is **not accepted**: the Cloud Architect's review (different line) and the human Product Owner's decision (D-039) are pending. CAPACITY_MODEL v0.2 is **owner-reviewed text that could not be written to its file** (§2) and is offered in Appendix A for the Cloud Architect, who holds that path in `.claude/agents/roster.json`. No capacity figure, latency, throughput, price, vendor capability, licence term or regulatory status is asserted anywhere. Profit is an objective, never a promise [Source: 00]. Tags: [Source: NN], [Committee], [Open].

---

## 1. Roles

| Function | Role | Line | In this session |
|---|---|---|---|
| Owner of CONTAINER_DIAGRAM, and named co-owner of CAPACITY_MODEL in that document's header | Enterprise Architect (this agent) | 1st | applied CONTAINER_DIAGRAM line 44; adopted and amended the CAPACITY_MODEL v0.2 draft; **approves nothing** |
| Holder of the `docs/CAPACITY_MODEL.md` write path in the roster | **Cloud Architect** | 1st | **must paste Appendix A** (or amend it) — the guard reserves that file to this seat (§2) |
| Reviewer of record for CAPACITY_MODEL | **SRE Lead** | 2nd | **pending** — cannot be self-signed |
| Reviewer of record for CONTAINER_DIAGRAM | **Cloud Architect** | 2nd (for this document) | **pending** |
| Drafter of the v0.2 text | Data Architect (REVIEW_2026-09-08_architecture_docs_v1.1.md Appendix A/B) | 1st | drafted only; is neither owner nor reviewer |
| Recommending body | ARB chair (COUNCIL_2026-09-08_gate_B_arb_docs.md §4.3) | 2nd | issued C-CM-1..C-CM-6 on **v0.1**; has not seen v0.2 |
| Independent validation | Independent Validation Agent | 3rd | **pending** |
| Decision | **human Product Owner (D-039)** | — | decides; agents never record an approval |

## 2. Purpose, inputs and what actually happened [Committee]

**Purpose.** Close the CAPACITY_MODEL half of **O-129** by having the owning role adopt or amend the C-CM-1..C-CM-6 text that the Data Architect drafted but could not write, and apply the CONTAINER_DIAGRAM line-44 correction (C-CM-6).

**Read in full at `112ae2e`** [Committee]: docs/SESSIONS/REVIEW_2026-09-08_architecture_docs_v1.1.md (Appendices A and B, §10 PO-A), docs/SESSIONS/COUNCIL_2026-09-08_gate_B_arb_docs.md §4 (4.1 number audit, 4.2 findings a–h, 4.3 conditions), docs/SESSIONS/COUNCIL_2026-09-08_gate_B_arb.md §4.3–4.7, docs/CAPACITY_MODEL.md v0.1, docs/CONTAINER_DIAGRAM.md, docs/NFR.md, observability/slis.yaml (nine SLIs, all `target: null`), docs/ADRs/ADR-018.md, ADR-019.md, ADR-020.md, ADR-004.md, ADR-009.md, docs/DECISION_LOG.md D-055..D-062, docs/RAID_LOG.md (O-03, O-28, O-86, O-87, O-88, O-111, O-115, O-117, O-124, O-129, O-131, O-133), docs/IMPROVEMENT_REGISTER.md E-6, docs/PERFORMANCE_PLAN.md (stages Load / Spike / Soak), .claude/agents/roster.json, apps/cli/rt365_cli/agent_guard.py. Code checked by symbol, not by line: `services/execution/execution_gateway/lease.py` (`LeaseStore.acquire/preempt/renew`, 30 s), `libs/core/rtcore/store.py` (`SqliteStore.__init__`, `busy_timeout_s=5.0`), `services/execution/execution_gateway/gateway.py` (`COMMAND_MAX_AGE`, 5 min), `services/audit/audit_service/store.py` (`DEFAULT_ANCHOR_EVERY=25`, `DEFAULT_MAX_ANCHOR_LAG=200`).

**What happened.** CONTAINER_DIAGRAM was written (commit `5d97199`). The write to `docs/CAPACITY_MODEL.md` was **refused by `scripts/agent_guard.py`**:

```
agent_guard: agent 'enterprise-architect' may not edit docs/CAPACITY_MODEL.md;
owned paths: docs/CONTEXT_DIAGRAM.md, docs/CONTAINER_DIAGRAM.md, docs/COMPONENT_DIAGRAMS.md,
docs/SEQUENCE_DIAGRAMS.md, docs/ADRs/, docs/NFR.md, docs/SESSIONS/, docs/RAID_LOG.md,
docs/DECISION_LOG.md, docs/REQUIREMENTS_TRACEABILITY.md, docs/AUDIT_EVIDENCE_INDEX.md,
docs/MISSING_ACTIONS.md, docs/REPORTS/
```

The roster assigns `docs/CAPACITY_MODEL.md` to **`cloud-architect`** only, while the document's own header and the ARB's conditions address "Enterprise Architect / Cloud Architect" as one seat. **The guard was not routed around.** A `sed`/heredoc write through Bash would have evaded the hook — exactly the gap D-061 (11) recorded as **O-131** — so the adopted text is delivered in Appendix A instead, in the same way the Data Architect delivered it to this session. This is the second consecutive session in which a cross-owner condition set could not be finished by one agent (PO-A in the previous packet); §9 PO-1 puts the choice in front of the Product Owner rather than resolving it here.

## 3. What I adopted, and what I changed from the draft [Committee]

I read Appendix A as its content owner, not as a courier. **Adopted in substance**: the whole structure — the rules block, the seven dimension rows, the storage cost model, the two measurement plans, the nine-SLI plan, the code-parameter table, the human-input list, the conditions table and the review record. **The draft invents no number, and neither does the adopted text.** The single filled numeric cell (639 B, sim `MarketSnapshot`) is measured and carries its evidence id; the five code defaults are parameters with their symbol, not values anyone decided.

Amendments, each with its reason:

| # | Change from the draft | Why [Committee] |
|---|---|---|
| A1 | **Header status rewritten.** The draft said "no acceptance exists until it is recorded in docs/DECISION_LOG.md". Replaced by the precise position: the ARB recommended, **D-061 did accept the *structure* v0.2 with C-CM-1..C-CM-6 and accepted no number**, and D-061's own closing sentence is that *no document status changes to "accepted" until its new version and reviewer signature exist* | The draft's sentence is over-broad and would read as "the ARB and the Product Owner have said nothing", which is false. The honest statement is narrower and harder: a conditional decision on the structure exists; the document is still not accepted, and the SRE Lead has signed nothing. Never "accepted" in the header |
| A2 | **§2 no longer claims to be "verbatim, unchanged".** Two deviations are stated in the document itself: ASCII notation for the sums, and the "bytes/row (JSON)" status cell now naming its evidence id and scope instead of the bare tag "[Verified, sim only]" | C-CM-2 says *verbatim*; the text is not literally verbatim. Claiming otherwise in an exit-evidence document is the small dishonesty that costs an auditor's trust. C-CM-2's own rule requires an evidence id in a filled cell, so naming it is the condition being obeyed, not bent |
| A3 | **`signal_latency_ms` corrected.** The draft wrote that it "drives Analytics-plane autoscaling". `observability/slis.yaml` gives it `safety_semantic: informational`; the autoscaling trigger is `event_lag_ms` (`autoscale`), which is also what §1 says | A capacity model that contradicts its own §1 and the SLI file within two pages would be rejected by the SRE Lead, correctly. The corrected cell says it sizes Analytics compute and is not the trigger |
| A4 | **§5 gains a measurement-point column and a safety-semantic column**, both copied from `observability/slis.yaml`, and a capacity-relevance sentence per SLI | C-CM-4 asks for the measurement point *and* why the SLI is capacity-relevant. The safety semantic is the reason: it says whether a breach sheds load, suspends autonomy or stops the platform, which is precisely a capacity consequence |
| A5 | **New §1 row: outbox relay and event bus (ADR-005, DF-13)** with no unit of scale decided and [Open: R-05] | The deployment carrier of every cross-context event was the one stateful dimension nobody had drawn. Leaving it out would let a reader think the model covers the transport. No number added |
| A6 | **New §3 row: executor failover time end to end**, explicitly *not* estimated, and named as composed of the lease-TTL parameter and the store `verify()` time, neither decided nor measured | NFR-RES-01 and NFR-DR-01 depend on this figure and the ARB did not list it. Naming the composition without adding the numbers is the correct half-step: the reader can see why 30 s + O(journal) is not an answer |
| A7 | **New §0 rule: capacity is never bought with a plane bypass** [Source: 03, 04] | This is the Enterprise Architect's own standard. The failure mode I guard against is a capacity argument ("read the portfolio directly from analytics, it is cheaper") that quietly creates the route the topology forbids |
| A8 | **New §0 rule: a CI test-suite timing is not a capacity baseline** (ADR-018's 9.5 s / 8.9 s stays out) | The ARB verified that keeping it out was right; writing the rule down stops it being re-imported by a well-meaning editor |
| A9 | **New §6: the NFRs this document is the evidence for** (NFR-SCL-01, AVL-01, RES-01, DR-01, FRS-01, CON-01) | `docs/NFR.md` already names "Capacity model Gate B" as NFR-SCL-01's evidence. The traceability was one-way; the model should say which NFR each part serves so the RTM row is checkable |
| A10 | **§8 gains the RPO/RTO input (O-18, DR_PLAN)** to the human-input list | §4's restore-and-reverify and §3's failover measurement are compared against objectives that no human has set yet |
| A11 | **§10 change log and an Independent-Validation row in the review record** | v0.1 → v0.2 provenance, and the IVA is part of the chain (D-061 pattern), not an afterthought |
| A12 | **Code citations by module and symbol, not by line** (e.g. `SqliteStore.__init__`, `DEFAULT_ANCHOR_EVERY`) | The same amendment the Data Architect made openly in DATA_FLOWS v1.1: a line number dies at the next edit and then the evidence looks wrong |
| A13 | **CONTAINER_DIAGRAM (Appendix B) amended before applying**: the draft cited "ADR-004 rev.2" as if it existed. `docs/ADRs/ADR-004.md` is still **Status: Proposed**, "Deferred to ARB after cost model" — the decision of record is **D-056** and ADR-004 rev.2 is *owed by me*. The applied line cites D-056 and says the rev.2 is owed. I also added a sentence that nothing in the stack line is provisioned, and bumped the header to v1.1 with the reviews pending | Citing a document that does not exist is exactly how a Gate B pack fails an independent validation. See §4 D-2 for why I did not write ADR-004 rev.2 in this session |
| A14 | **Kept, deliberately unchanged**: the empty cells. Nothing was filled in to make the document look finished | The one rule that makes this document worth reading [Committee] |

## 4. Decisions taken in this session, with alternatives [Committee]

**D-1 — How to deliver the capacity text after the guard refusal.**

| | Option A — deliver the adopted text in this packet for the Cloud Architect (**chosen**) | Option B — write it through Bash (`cat > docs/CAPACITY_MODEL.md`) | Option C — edit `.claude/agents/roster.json` to add the path to this agent |
|---|---|---|---|
| Cost | one paste by the Cloud Architect | none | none |
| Risk | O-129 stays open one more hop; Gate B waits | evades a control of this project (O-131) and makes every later "the guard held" claim false | an agent widening its own write scope; the roster's subjects editing the roster is the exact weakness O-131 names |
| Reversibility | high | low — the bypass is in the history | low |
| Controls / tests affected | none | agent_guard, the CI path-ownership check (O-131), author≠reviewer | same, plus `make agents-check` |
| Verdict | **chosen** — the instruction for this session was explicit, and it matches what the Data Architect did | rejected | rejected; a roster change is the Product Owner's decision (§9 PO-1) |

Confidence: **high**. Evidence: the guard's own refusal message (§2), `apps/cli/rt365_cli/agent_guard.py`, D-061 (11), O-131.

**D-2 — Whether to write ADR-004 rev.2 in this session.**

| | Option A — write rev.2 now, so the CONTAINER_DIAGRAM citation resolves | Option B — cite D-056, mark rev.2 as owed, raise a RAID row (**chosen**) |
|---|---|---|
| Pros | closes a D-056 artefact debt that is mine; the stack line would cite a live ADR | the diagram stops citing a non-existent document today; rev.2 gets the alternatives, consequences, controls and tests D-056 requires, in a session that reviews it properly |
| Cons | an ADR written as a side-effect of a capacity session, unreviewed, with three alternatives (Postgres-first / TSDB-first / object-store-only) that the ARB already argued in COUNCIL §4.4 and that deserve to be transcribed faithfully | the debt stays open one more session |
| Risk | an under-reviewed ADR is worse than a missing one; ADRs without proper alternatives are a failure mode I guard against | low, and visible |
| Verdict | rejected | **chosen** — RAID row RC-2, §7 |

Confidence: **high** that ADR-004 is still the deferral (read at `112ae2e`); **medium** on the sequencing preference — a reviewer may reasonably want rev.2 immediately.

**No ADR is created or amended in this session.** No standard changed; the two additions to the capacity model's rule block (A7, A8) restate existing decisions ([Source: 03, 04]; ARB §4.1) rather than create new ones.

## 5. Condition by condition — C-CM-1..C-CM-6

| Condition (ARB §4.3, carried by D-061) | Applied? | Where / why not |
|---|---|---|
| **C-CM-1** header status; "structure at Gate B, baselines at Gate C, targets at Gate E" replaces "the ARB signs the model once baselines exist" | **applied in the adopted text; not yet in the file** | Appendix A header + §0. Amended per A1: the header records the ARB recommendation, D-061's conditional acceptance **of the structure**, the SRE Lead review **pending** and the human PO decision **pending**. It never reads "accepted" |
| **C-CM-2** §Storage cost model inserted with the evidence-id rule | **applied in the adopted text; not yet in the file** | Appendix A §2, with the two deviations from a literal copy stated in the document itself (A2). Every term keeps its ARB status; the only filled value is the 639 B sim measurement with its evidence id |
| **C-CM-3** control-state store row + five-measurement plan; the three code defaults as "[Open] parameters — code default, not a target" | **applied in the adopted text; not yet in the file** | Appendix A §1 (row), §3 (plan, plus the failover row A6), §7 (five parameters — the ARB's three plus the two ADR-020 anchor placeholders, all verified by symbol) |
| **C-CM-4** measurement plan extended to all nine SLIs, or a stated reason why an SLI is not capacity-relevant | **applied in the adopted text; not yet in the file** | Appendix A §5. All nine appear with baseline, measurement point, safety semantic and capacity relevance; **no SLI is claimed to be non-capacity-relevant**, so no exclusion reason is owed. `time_to_halt_s` and `control_plane_availability` — the two the SRE Lead required — are in |
| **C-CM-5** human-input list extended (H-08, Q-11-1, A-5, O-09/O-10); one line that no cell is provisioned | **applied in the adopted text; not yet in the file** | Appendix A §8 (plus O-18 per A10) and §0 last bullet |
| **C-CM-6** (a) SRE Lead review recorded in the header; (b) AEI reviewer column filled; (c) CONTAINER_DIAGRAM line 44 replaced by D-055/D-056 references | **(a) applied as "pending"; (b) not applied — proposed only; (c) APPLIED to the file** | (a) the review has not happened and cannot be self-signed [Source: 13]; the header records it as pending, which is the only truthful form. (b) the Enterprise Architect does not write docs/AUDIT_EVIDENCE_INDEX.md content for his own artefact — row text is proposed in §7 for the Program Orchestrator, and it should be created **only when v0.2 exists in the file**, so the reviewer signs the text that was reviewed. (c) **done: commit `5d97199`**, amended per A13 |

**Net: five and a half of six conditions are drafted and owner-adopted, one is applied to a file.** O-129 stays open for CAPACITY_MODEL until the Cloud Architect pastes Appendix A and the SRE Lead reviews it.

## 6. What remains [Open]

| Item | Register | What would settle it, and where it belongs |
|---|---|---|
| Every capacity number: throughput, latency, storage volume, cost | O-03, O-87, O-88 | Gate C baselines (PERFORMANCE_PLAN Load / Spike / Soak on the compose topology, then the deployed cell) and Gate E targets; quoted terms need H-05, H-08, Q-11-1, A-5 |
| Control-store `verify()` time versus journal length; journal rows and bytes per order lifecycle; fsync cost; lease contention across processes; order-cache growth | O-111, O-117, O-28 | a QA-owned TC on the compose topology (rows, bytes) and a synthetic journal in CI, then PERFORMANCE_PLAN "Soak" |
| Audit chain verification time at open versus chain length; audit bytes per lifecycle; anchor accumulation; seal/publication latency; restore-and-reverify | O-133, O-134, O-135, O-18 | CI synthetic chain, the same compose TC, a CHAOS_PLAN witness-loss drill and a DR drill |
| Executor failover time end to end | O-28, O-117, O-18 | the O-117 multi-process tests plus a DR drill; it is not the lease TTL and must not be quoted as such |
| Bus unit of scale and `event_lag_ms` baseline | R-05 | a deployed Kafka-compatible bus; today dev/sim carries events in process after the outbox write |
| The anchor principal, its credential, and the cadence values | O-54, O-133 | a human decision with the retention rules; the code values 25 / 200 are dev/sim placeholders |
| ADR-004 rev.2 | new row RC-2 (§7) | an ARB session on the D-056 text with the three alternatives of COUNCIL §4.4 |
| Whether the roster should treat "Enterprise Architect / Cloud Architect" as one seat for this file | O-131 lineage; new row RC-1 (§7) | the Product Owner (§9 PO-1) |
| SRE Lead review, Cloud Architect review, IVA re-validation, PO decision | O-129 | the reviewers themselves; nothing in this session substitutes for them |

## 7. Proposed ledger rows — **not written by me** (I do not edit RAID_LOG, DECISION_LOG, RTM or AUDIT_EVIDENCE_INDEX in this session)

**RAID (Program Orchestrator):**

| Ref | Type | Entry | Owner | Gate |
|---|---|---|---|---|
| RC-1 | Gap | CAPACITY_MODEL v0.2 is owner-adopted text (Appendix A of docs/SESSIONS/REVIEW_2026-09-08_capacity_v0.2.md) but **still not in docs/CAPACITY_MODEL.md**: `.claude/agents/roster.json` reserves that path to `cloud-architect` while the document header and the ARB conditions address "Enterprise Architect / Cloud Architect" as one seat. The Enterprise Architect did not route around the guard. Needs: the Cloud Architect to paste or amend Appendix A, then the SRE Lead review. **O-129 stays open for CAPACITY_MODEL** | Cloud Architect; SRE Lead | B |
| RC-2 | Gap | **ADR-004 rev.2 is owed** (D-056 artefact table, Enterprise Architect): ADR-004 is still "Proposed — deferred to ARB after cost model" while D-056 decided the architecture. CONTAINER_DIAGRAM v1.1 now cites D-056 and states the debt instead of citing a rev.2 that does not exist. The three alternatives are already argued in COUNCIL_2026-09-08_gate_B_arb.md §4.4 | Enterprise Architect | B |
| RC-3 | Gap | Executor failover time end to end (lease expiry or preempt → store open with `verify()` → cancel-on-restart) is the availability figure NFR-RES-01 and NFR-DR-01 depend on and it has never been measured; it must not be quoted as the 30 s lease-TTL code default. Added to CAPACITY_MODEL §3 as [Open] | SRE Lead; Backend Lead | C |
| RC-4 | Observation | CAPACITY_MODEL §1 now carries the outbox/bus dimension (ADR-005, DF-13) with **no unit of scale decided**: no bus is deployed, dev/sim carries events in process after the outbox write, so `event_lag_ms` has no measurement point yet (R-05) | Cloud Architect; Integration Architect | C |
| RC-5 | Decision | Should the roster treat `docs/CAPACITY_MODEL.md` as jointly owned (Enterprise + Cloud Architect), or should cross-owner condition sets always be finished by draft-and-paste? Two sessions in a row have stopped at this boundary. A roster change is a control change and belongs to the Product Owner, not to either architect | Product Owner (D-039); Program Orchestrator | B |

**AUDIT_EVIDENCE_INDEX (Program Orchestrator):** create a row **"CONTAINER_DIAGRAM.md v1.1"** — owner Enterprise Architect, reviewer **Cloud Architect (pending)**, approving body ARB (advisory), IVA column blank, location `docs/CONTAINER_DIAGRAM.md` at commit `5d97199`, note "stack line corrected to D-055/D-056 per C-CM-6". Create the row **"CAPACITY_MODEL.md v0.2"** *only when the version exists in the file*, with reviewer **SRE Lead (pending)** — so the reviewer signs the text that was reviewed, not an appendix.

**REQUIREMENTS_TRACEABILITY (QA Lead / Program Orchestrator):** requirement → architecture → owner → control → test → evidence → gate

| Requirement | Architecture | Owner | Control | Test | Evidence | Gate |
|---|---|---|---|---|---|---|
| NFR-SCL-01 (scalability: partition by tenant/account/instrument; autoscale on lag/latency) | CAPACITY_MODEL §1 (eight dimensions, units of scale, partition keys, shed policy) and §5 (nine SLIs) | Enterprise Architect / Cloud Architect; reviewer SRE Lead | a cell is filled only with a measured or quoted value and its evidence id; a blank cell is [Open], never an estimate; structure at Gate B, baselines at Gate C, targets at Gate E | measurements named in §3, §4, §5, each [Open] with the stage that produces it (PERFORMANCE_PLAN Load / Spike / Soak; CI synthetic journal and chain; DR and chaos drills) | Appendix A of this packet **until the Cloud Architect applies it**; then docs/CAPACITY_MODEL.md v0.2 | B (structure) / C (baselines) / E (targets) |
| NFR-AVL-01 (planes never shed; fail closed) | CAPACITY_MODEL §1 shed column; §0 "capacity is never bought with a plane bypass"; CONTAINER_DIAGRAM network-policy line | Enterprise Architect | Analytics sheds first; Control fails closed (HALTED); Execution cancel-only; no analytics→execution route may be created for capacity | `control_plane_availability` baseline [Open: O-03]; network-policy checker rule 2 (TC-NET-001..004) | docs/CAPACITY_MODEL.md §0/§1; docs/CONTAINER_DIAGRAM.md | B (structure) / C |
| NFR-RES-01, NFR-DR-01 (cells, active/standby execution, RPO/RTO) | CAPACITY_MODEL §3 executor failover row; §4 restore-and-reverify | SRE Lead / Backend Lead | one active executor per account by lease with a fencing token; cancel-on-restart; recovery is restore-then-verify, never disable-the-check | O-117 multi-process tests; DR drill (DR_PLAN); TC-AUD-007/009 | [Open] — no measurement exists; RC-3 | C |
| O-04 / O-13 architecture citations in the C4 view | CONTAINER_DIAGRAM stack line (D-055 ADR-009; D-056 market-data store) | Enterprise Architect; reviewer Cloud Architect | the diagram cites decisions of record only, and states what is owed (ADR-004 rev.2) and what is not provisioned | docs review; `make all` green at `5d97199` (not a review [Source: 13]) | docs/CONTAINER_DIAGRAM.md v1.1 | B |

**PO_DECISION_QUEUE (Program Orchestrator):** "CAPACITY_MODEL v0.2 is owner-adopted but unwritable by its named owner — instruct the Cloud Architect to paste or amend Appendix A of REVIEW_2026-09-08_capacity_v0.2.md, then the SRE Lead review (RC-1)"; "decide RC-5: joint roster ownership of docs/CAPACITY_MODEL.md, or draft-and-paste as the standing answer"; "ADR-004 rev.2 is owed before Gate B (RC-2)".

## 8. Threat-model delta [Committee] — proposed to the Security Architect, who owns THREAT_MODEL

| Candidate | Where it comes from | Statement |
|---|---|---|
| capacity as a plane-bypass argument | CAPACITY_MODEL §0 (new rule A7) | a future scaling proposal ("serve portfolio state to Analytics directly, the read model is expensive") would create the Analytics→Execution route the topology forbids; the control is checker rule 2 plus this written rule, and the abuse test is a NetworkPolicy/`analytics.yaml` test that fails when such a route is added [Source: 03, 04] |
| start-up amplification | CAPACITY_MODEL §3, §4 (ADR-018 `verify()`, ADR-020 chain verification) | both verifications are O(n) on the same start-up and failover path; an attacker who can inflate the journal or the chain lengthens every restart, and a long restart is a long window with no executor. Neither has a baseline, so nobody can say when it stops being cheap [Open: O-111, O-133] |
| anchor accumulation as a slow denial | CAPACITY_MODEL §4 | anchor records accumulate without compaction and the anchor chain is re-verified on every read; growth is a capacity fact with an availability consequence [Open: O-133] |

## 9. Control quartet [Committee] — ids by the QA Lead; nothing here claims a test exists

| Control | Positive | Negative | Abuse | Recovery |
|---|---|---|---|---|
| **"A blank cell is [Open], never an estimate"** (the rule that makes this document usable as evidence) | a filled cell names a measurement or a quote **and** its evidence id (§2 bytes/row, 639 B, sim fixture) | a cell with no measurement stays empty and carries its register id, and the document is still complete as a *structure* | a plausible-looking figure inserted "for planning" — caught by review because it has no evidence id; the D-046 price sheet must never be back-solved from a price hypothesis (C-13-5) | strike the figure, restore [Open] with its register id, and record who quoted it and where it travelled. **No test exists for this control — it is a review control, and the reviewer is the SRE Lead, not the author** [Open] |
| **Code default ≠ target** (§7) | each parameter cites module and symbol and is tagged "code default, not a target" | a reader looking for the lease-TTL *decision* finds O-28, not 30 s | 30 s quoted as a failover objective in a gate pack, or 25/200 quoted as decided anchor cadence | the parameter table is the single place these values may be read from; §3's failover row states explicitly that the composite is not the TTL [Open: O-28, O-133] |
| **Plane separation under capacity pressure** (§0 rule A7) | scaling changes stay inside a plane; Analytics sheds first | a Control-plane overload halts (HALTED), it does not spill into Execution | a capacity proposal that adds an Analytics→Execution route is refused by checker rule 2 (TC-NET-001..004) before it is refused by the ARB | remove the route, re-run the checker; an accepted route would need an ADR and the ARB — **and the Enterprise Architect may not grant himself that exception** [Source: 13] |

## 10. Evidence list mapped to docs/

| Artefact | State after this session |
|---|---|
| docs/CONTAINER_DIAGRAM.md | **v1.1 written** (commit `5d97199`): stack line cites D-055 / D-056, states the ADR-004 rev.2 debt, states that nothing is provisioned; header records Cloud Architect review **pending**, PO decision **pending**; **not accepted** |
| docs/CAPACITY_MODEL.md | **unchanged (guard refusal, §2)**; owner-adopted v0.2 text in Appendix A for the Cloud Architect |
| docs/SESSIONS/REVIEW_2026-09-08_capacity_v0.2.md | this packet |
| docs/RAID_LOG.md, docs/DECISION_LOG.md, docs/REQUIREMENTS_TRACEABILITY.md, docs/AUDIT_EVIDENCE_INDEX.md, docs/MISSING_ACTIONS.md | **not edited**; rows proposed in §7 |
| docs/ADRs/ | **not edited**; ADR-004 rev.2 owed (RC-2) |
| docs/NFR.md | **not edited**; the adopted §6 maps six NFRs onto this model, which is a read of NFR.md, not a change to it |
| observability/slis.yaml | read only; all nine SLIs carried into the plan, `target: null` for all nine |

## 11. Concerns for the Product Owner

- **PO-1 The same boundary stopped the same document twice in one day.** The Data Architect could not write `docs/CAPACITY_MODEL.md`; nor can the Enterprise Architect. The roster gives that path to `cloud-architect` alone, while the document's header, the ARB's conditions and your own session brief all address "Enterprise Architect / Cloud Architect" as a single seat. I adopted and amended the text as its content owner and stopped at the file, because the alternative was a Bash write that evades the hook — the precise gap D-061 (11) records as O-131, and a bypass would make every future "the guard held" statement in this repository worth less. You now have three choices and they are yours, not the architects': make the ownership joint in the roster, appoint the Cloud Architect as the single owner of the capacity model and correct the document header, or keep draft-and-paste as the standing answer and accept one extra hop per cross-owner condition set. Until then **O-129 stays open for CAPACITY_MODEL and Gate B cannot be convened on it** [Committee].
- **PO-2 The capacity model still contains almost no numbers, and that is the correct state, not a deficiency.** One cell is filled: 639 bytes for a simulated market snapshot, measured on a sim fixture, carrying its evidence id — a property of a schema and a test fixture, not of any licensed feed, any broker, any venue or any deployed system. Everything else is [Open] with the measurement and the stage that would produce it. If anyone asks this project for a capacity, cost or throughput figure before Gate C, the honest answer is that none exists and none may be quoted. Please resist the temptation to have one estimated, including "just for planning": the moment an estimate enters this document it will be cited back at you as evidence [Source: 00] [Committee].
- **PO-3 Two O(n) checks now sit on the start-up and failover path, unmeasured.** The control store replays its journal at open (ADR-018) and the audit store verifies its whole chain at open (ADR-020); anchor records accumulate and the anchor chain is re-verified on every read. Both are the correct fail-closed design. Both mean that restart time grows with history, and restart time is how long an account has no executor. Nobody has measured any of it, so nobody knows where the knee is — and neither compaction nor retention is decided (O-111, O-133). This is the single technical unknown I would put first at Gate C [Open].
- **PO-4 "Executor failover time" does not exist as a number, and the 30-second lease TTL is not it.** I added the row to the model precisely so that the code default cannot be mistaken for the answer. The real figure is lease expiry or preempt, plus opening a store that verifies O(journal), plus cancelling open orders on restart. If a broker, a regulator or an investor asks how quickly the platform recovers an account, the answer today is "unmeasured" (RC-3) [Open: O-28, O-18].
- **PO-5 The container diagram was citing a document that does not exist.** The draft line-44 text cited "ADR-004 rev.2"; ADR-004 is still the one-line deferral, because D-056 decided the architecture and the rev.2 was never written — by me. I applied the line citing D-056 and stating the debt rather than citing a phantom, and I did **not** write the ADR in this session, because an ADR produced as a side-effect of a capacity session, with alternatives copied in haste and no review, is worse than an honest gap (RC-2). It is a Gate B item and it is mine [Committee].
- **PO-6 Nothing here is approved, and `make all` being green is not a review.** The Cloud Architect has not reviewed the container diagram, the SRE Lead has not reviewed the capacity model, the ARB has not seen v0.2, the Independent Validation Agent has signed nothing, and I do not approve my own documents. D-061 accepted a *structure* with conditions and closed with the sentence that no document becomes "accepted" until its new version and its reviewer's signature exist. Both halves of that sentence are still outstanding [Source: 13].

## 12. Assumptions, confidence, provenance

- **Assumptions:** the ARB conditions carried by D-061 are the instruction set; D-055, D-056, D-058, D-060, D-061, D-062 stand as recorded; the tree at `112ae2e` is the code that ships in dev/sim; the roster at `112ae2e` is the write-scope of record [Committee].
- **Confidence:** **high** that the adopted text satisfies C-CM-1..C-CM-5 and the applicable parts of C-CM-6 as text, and that its five code parameters match the tree by symbol (each was read); **high** that ADR-004 is still the deferral; **none** on any capacity number (none is proposed); **none** on any price, licence term, provider rate, broker capability, vendor capability or regulatory status (none is assumed anywhere in this session).
- **Provenance:** [Source: 00, 03, 04, 05, 10, 13] as transmitted by the repository artefacts; [Committee] for this session's reasoning and for the ARB/council packets cited; [Open] items carry their register ids.
- **Independence:** the author of CONTAINER_DIAGRAM v1.1 is its owner, not its reviewer and not its approver. The adopter of the capacity text is its content owner and neither its drafter nor its reviewer. No agent recorded an approval or a decision in a ledger during this session.

---

## Appendix A — `docs/CAPACITY_MODEL.md` v0.2, owner-adopted, for the Cloud Architect to paste (or amend)

This is the Enterprise Architect's adopted-and-amended version of the Data Architect's draft (changes in §3 above). It is ready to replace the whole of `docs/CAPACITY_MODEL.md`. If the Cloud Architect amends it further, §3 of this packet is the record of what was already changed and why.

```markdown
# CAPACITY_MODEL (Gate B exit evidence — structure only)

| Owner | Reviewer (different line) | Approving body | First gate | Status |
|---|---|---|---|---|
| Enterprise Architect / Cloud Architect | SRE Lead | ARB (advisory) | B | **Structure v0.2, 2026-09-08 — owner-adopted; SRE Lead review pending; human Product Owner decision pending (D-039). Not accepted as a document.** |

**Status in full [Committee].** The ARB reviewed **v0.1** and recommended *ACCEPT WITH CONDITIONS as a structure (v0.2); no number is accepted, because none was presented* (docs/SESSIONS/COUNCIL_2026-09-08_gate_B_arb_docs.md §4.3, conditions C-CM-1..C-CM-6). **D-061** carried that recommendation as a Product Owner decision on the *structure* and closed with the sentence that **no document status changes to "accepted" until its new version and reviewer signature exist**. This is that new version. It therefore stands as: structure reviewed by the ARB, conditions applied by the owner, **SRE Lead review pending**, **Independent Validation pending**, **human Product Owner decision pending (D-039)**. Numbers remain [Open: O-03 targets, O-87 storage terms, O-88 TSDB trigger]. No agent records an approval [Source: 13].

**Adoption note [Committee].** The text applying C-CM-1..C-CM-6 was drafted by the **Data Architect** at the direction of the Product Owner delegate's session of 2026-09-08 and delivered as Appendix A of docs/SESSIONS/REVIEW_2026-09-08_architecture_docs_v1.1.md, because the write-scope guard correctly refused a Data Architect edit to this file. It was **adopted with amendments by the Enterprise Architect** on 2026-09-08 and pasted by the Cloud Architect, who holds the write path; the amendments and their reasons are listed in docs/SESSIONS/REVIEW_2026-09-08_capacity_v0.2.md §3. Drafter is not owner, owner is not reviewer, reviewer is not approver [Source: 13].

## 0. Rules that govern every cell [Committee]

- **A cell is filled only with a measured or quoted value and its evidence id. A blank cell is [Open], never an estimate** (ARB C-13-1, IVA-B-07).
- **No number in this document is a target.** The ARB accepts the **structure** at Gate B; **baselines are accepted at Gate C and targets at Gate E** (O-03). This replaces v0.1's "the ARB signs the model once baselines exist", which contradicted the document's role as Gate B exit evidence and D-057 (C-CM-1).
- A value read out of the source code is a **parameter**, not a decision and not a target; §7 lists them separately so that nobody later cites a code default as if it were a decided value (C-CM-3).
- **Capacity is never bought with a plane bypass** [Source: 03, 04] [Committee]. Every shed, autoscale and failover statement below is subject to the topology: the Analytics plane has no route to the Execution plane or to brokers, and no capacity argument may create one. Load is shed in the Analytics plane; the Control and Execution planes fail closed instead of shedding.
- A CI test-suite timing is not a capacity baseline. ADR-018 records the suite at 9.5 s before and 8.9 s after on the memory default; that figure is deliberately **not** carried into this document, and no figure of that kind may be cited as a platform baseline [Committee] (COUNCIL_2026-09-08_gate_B_arb_docs.md §4.1).
- Every statement is tagged [Source: NN], [Committee] or [Open]. No cloud price, vendor capability, provider tick rate, licence term, throughput or latency is asserted anywhere in this document [Source: 00].
- Nothing here authorises an environment. **No cell is provisioned**: `infra/kubernetes` holds namespaces and network policies only, `infra/iac/README.md` says modules are added once the provider is chosen, and no storage, bus, stateful-set or autoscaling manifest exists [Open: H-05, A-6, B-15] (C-CM-5).

## 1. What is fixed now [Committee] [Source: 03, 05]

| Dimension | Unit of scale | Partition key | Shed under load? |
|---|---|---|---|
| Analytics plane (market data, strategy, MCP servers, backtest) | per cell, autoscale on event lag | tenant / instrument | Yes — shed first [C2 §6] |
| Control plane (intent queue, eligibility, risk, approval, audit) | per cell, autoscale on risk-decision latency | tenant / account | Never — fails closed (HALTED) |
| Execution plane (OMS, gateway, adapters, reconciliation, portfolio) | one active executor per account (lease), standby per cell | account | Never — cancel-only on degradation |
| Audit WORM | append-only, replicated cross-cell | tenant | Never |
| **Control-state store (ADR-018: lease, outbox/inbox, gateway indexes, Kill Switch activations)** | one store per service per cell from shadow (D-058 (a), O-115); in dev/sim one SQLite file | account (execution schema) / tenant (control schema) | **Never** — a `StoreError` is S1 and the gateway submits nothing |
| **Market-data store (D-056)** | per cell (PostgreSQL bitemporal plus an object-storage archive in the same cell); no cross-cell replication (ADR-007) | instrument / market_ts | never for decision-time reads; archive jobs shed first |
| **Audit store and its external witness (ADR-020)** | its own store file per platform, never the control store's; an anchor directory owned by a different principal (a WORM bucket or replica in deployment) [Open: O-54] | tenant (reads) / chain sequence (writes) | **Never** — a failed chain or a missing witness fails closed and carries the `killswitch_platform` auto-action [Open: O-137] |
| **Outbox relay and event bus (ADR-005, docs/DATA_FLOWS.md DF-13)** — the deployment carrier of every cross-context event | undecided: no bus is deployed and no manifest exists; at-least-once with a consumer inbox is the contract, so the consumer side scales with duplicate handling, not with ordering | topic / tenant | control- and execution-plane events are never dropped; analytics topics shed first [Open: R-05] |

These are cardinality and shed-policy statements, not capacity figures [Committee].

## 2. Storage cost model (O-13) — C-CM-2

Inserted per C-CM-2 from docs/SESSIONS/COUNCIL_2026-09-08_gate_B_arb.md §4.3 (the text agreed with D-056). Two deviations from a literal copy, both openly made by the owner [Committee]: (a) mathematical symbols are written in ASCII words so that the formula survives any encoding; (b) the "bytes/row (JSON)" status cell now carries its **evidence id and its scope**, because C-CM-2's own rule requires an evidence id in every filled cell and "[Verified, sim only]" alone does not name the evidence. No term, value or source was added, removed or changed.

Cost per instrument-year = the sum over data classes *d* in {ticks, bars, snapshots, instrument-master versions, derived features} of
`rows_d/year x bytes_d/row x sum over tiers (months_in_tier x unit_price_tier)` + query/compute share + replication/egress share (audit replication is costed separately under the Audit WORM row).

| Term | How it is produced (measurement or source) | Source of truth | Status |
|---|---|---|---|
| rows_d/year per instrument | provider tick/bar rate per instrument class x sessions/year from `SessionCalendar` for the venue; measured on the licensed feed during shadow (PERFORMANCE_PLAN "Soak") | H-08 licence data sheet; F-4 calendars | [Open: H-08] |
| bytes/row (JSON) | `len(model_dump_json())` — 639 B for the sim `MarketSnapshot` with the embedded instrument row | schema + fixture; evidence id: COUNCIL_2026-09-08_gate_B_arb.md §2 measurement (`RT_ENV=sim`, `build_sim_platform()`) | measured, **sim fixture only** — a property of the schema and that fixture, not of any licensed feed |
| bytes/row (stored) | measured by the adapter's TC-MD-005 on the chosen encoding (row store versus columnar archive), with and without instrument denormalisation | adapter tests, Gate C | [Open] |
| tiers and months per tier | hot = decision-time window (freshness budget NFR-FRS-01 plus backtest look-back), warm = backtest horizon, cold = retention obligation; months per tier from the retention schedule per jurisdiction | RISK_POLICY freshness table; O-09/O-10 schedules | [Open: O-09, O-10] |
| unit price per tier per region | cloud provider price list for the first cell's region, quoted at budget approval; the region follows Q-11-1 | H-05 quote; A-1 | [Open: H-05, Q-11-1] |
| query/compute share | measured CPU/IO of `latest`/`series` under PERFORMANCE_PLAN "Load" and "Spike" on the adapter | Gate C baselines | [Open: O-03] |
| replication/egress | cross-cell traffic is limited to audit replication and the portfolio roll-up (ADR-007); market data does not leave its cell — 0 by design unless a licence or DR requirement says otherwise | ADR-007; DR_PLAN | [Committee] |
| instrument universe and tenants | first cell: one venue, cash equities/ETFs, first-party account (D-043); counts [Open] | D-043; H-05 inputs | [Open] |
| licence constraints on storage | redistribution or derived-data rights, retention obligations or deletion duties imposed by the licence | O-12; H-08 | [Open: O-12] |

Rule for the sheet: **a cell is filled only with a measured or quoted value and its evidence ID; a blank cell is [Open], never an estimate.** D-046 takes prices from this sheet; the sheet must never be back-solved from a price hypothesis (C-13-5) [Committee].

## 3. Control-state store measurement plan (ADR-018) [Committee] — C-CM-3

Growth drivers: every index write and every state transition is a journal row carrying the full value (docs/DATA_FLOWS.md DF-11), and `verify()` at open replays the journal, so it is O(journal) [Open: O-111].

| Measurement | Produced by | Status |
|---|---|---|
| journal rows and store bytes per order lifecycle (create, ack, fill or cancel) | a TC on the compose topology (id by the QA Lead) | [Open] |
| `verify()` time versus journal length (it sits on the restart path of the executor, so a long verify is a long failover) | a synthetic journal of known length in CI first, then PERFORMANCE_PLAN "Soak" | [Open] |
| fsync cost per commit (`synchronous=FULL`) on the target disk class | PERFORMANCE_PLAN "Load" | [Open] |
| lease contention per account under two OS processes | the O-117 tests | [Open] |
| order-cache growth in a long-running process | PERFORMANCE_PLAN "Soak" | [Open] |
| **executor failover time end to end** (lease expiry or preempt, store open with `verify()`, cancel-on-restart of open orders) — the availability figure that NFR-RES-01 and NFR-DR-01 depend on; it is composed of the §7 lease-TTL parameter and the store verify time above, and **neither component is decided or measured**, so the composite is not estimated here | the O-117 tests plus a DR drill (DR_PLAN, O-18) | [Open: O-28, O-18] |

## 4. Audit store and external witness measurement plan (ADR-020) [Committee]

The audit trail became durable and externally witnessed after the ARB reviewed this document (D-062). These properties are capacity-relevant and none has a baseline; no figure is invented here [Open].

| Measurement | Why it matters | Produced by | Status |
|---|---|---|---|
| audit chain verification time at open versus chain length (O(events); it runs on every start and gates opening the store) | it sits on the start-up path of the whole platform, next to the control store's `verify()` | a synthetic chain of known length in CI, then PERFORMANCE_PLAN "Soak" | [Open] |
| audit rows and bytes per order lifecycle, and per MCP call | the audit store is a second durable store to size, back up and replicate | a TC on the compose topology (id by the QA Lead) | [Open] |
| anchor records accumulated per unit of activity (one per explicit seal and one per `anchor_every` events), their bytes, and the cost of the anchor chain, which is re-verified on every read | anchor records accumulate without compaction; compaction and retention are owed with the control-store journal's (O-111) | the same TC, plus the O-133 cadence decision | [Open] |
| seal and publication latency, and the cost of an unavailable witness (the fail-closed path) | a missing or stale witness halts the platform via `killswitch_platform` [Open: O-137] | PERFORMANCE_PLAN "Load"; chaos drill per docs/CHAOS_PLAN.md | [Open] |
| restore-and-reverify time for the anchor directory (the documented recovery is to restore the replica, never to disable the check) | it is an input to the recovery time objective (O-134, DR_PLAN) [Open: O-18] | DR drill | [Open] |

## 5. Measurement plan — all nine SLIs of `observability/slis.yaml` [Committee] — C-CM-4

No target is set for any SLI; `slis.yaml` carries `target: null` for all nine, targets are [Open: O-03] and are decided at Gate E [Source: 10]. The safety-semantic column is the automatic action on breach, and it is why the SLI is a capacity input: it determines whether load is shed, autonomy suspended or the platform stopped. All nine are capacity-relevant; none is excluded.

| SLI | Baseline to measure | Measurement point (`slis.yaml`) | Safety semantic | Why it is capacity-relevant |
|---|---|---|---|---|
| `control_plane_availability` | successful control-plane decisions / total decision requests | `risk_engine` | fail_closed | the Control plane never sheds (NFR-AVL-01); its capacity headroom is the only thing standing between load and a HALTED platform |
| `market_data_freshness_s` | `market_ts` age at snapshot use | `risk_engine.RK-FRESH` | suspend_autonomy | sets the hot tier of §2 and the ingest budget of the market-data store (NFR-FRS-01) |
| `signal_latency_ms` | snapshot to signal | `strategy_service` | informational | sizes Analytics compute per instrument and strategy; it is **not** the autoscaling trigger — the Analytics plane autoscales on `event_lag_ms` (§1) |
| `risk_decision_latency_ms_p99` | intent enqueue to decision-record write, p99 per cell | `oms.pipeline` span | suspend_autonomy | the Control plane's autoscaling trigger (§1) |
| `order_ack_latency_ms` | order command to broker ack | `execution_gateway` | cancel_only_review | bounds how long one lease-holding executor is occupied per order, so it sizes the per-account serial path |
| `event_lag_ms` | produce to consume | bus | autoscale | the Analytics plane's autoscaling trigger and the health of the DF-13 relay; unmeasurable until a bus is deployed [Open: R-05] |
| `reconciliation_completeness_pct` | reconciled positions / total by EOD+T | `reconciliation_service` | supervised_on_break | sizes the reconciliation window and the batch capacity it needs to close by EOD+T |
| `time_to_halt_s` | Kill Switch engage to the last open-order cancel and identity revocation recorded (D-044) | `killswitch_service.activate` (metric `killswitch.time_to_halt_s`); the drill measures operator-action to engaged separately | informational | it scales with the number of open orders and identities per cell, so a capacity decision changes how long a stop takes [Source: 00] |
| `alert_delivery_s` | alert to operator ack | `notification` | tested_daily | bounds the auto-action paths of docs/DATA_FLOWS.md DF-18, including `killswitch_platform`; a slow path is a slow stop |

## 6. NFRs this document is the evidence for [Committee] [Source: 03, 10]

| NFR | What this document owes it | State |
|---|---|---|
| NFR-SCL-01 (scalability) | its evidence column in docs/NFR.md already names "Capacity model Gate B": the units of scale, partition keys and autoscaling triggers of §1 | structure present; no number |
| NFR-AVL-01 (planes never shed, fail closed) | the shed column of §1 and `control_plane_availability` in §5 | structure present; budget [Open: O-03] |
| NFR-RES-01 (cells, active/standby execution) | the executor failover measurement of §3 | [Open: O-28, O-117] |
| NFR-DR-01 (RPO/RTO per cell) | restore-and-reverify of §4 and the failover measurement of §3 | [Open: O-18, DR_PLAN] |
| NFR-FRS-01 (freshness) | the hot tier of §2 and `market_data_freshness_s` in §5 | [Open: O-03] |
| NFR-CON-01 (idempotency under at-least-once) | the bus row of §1: duplicates are handled by the consumer inbox, so consumer capacity carries duplicate load | [Open: R-05] |

## 7. Parameters that exist in code as defaults, not targets [Committee] — C-CM-3

These are read out of the source; none is a decision, a baseline or a target, and none may be cited as one. Citations are by module and symbol so they survive an edit.

| Parameter | Default in code | Where | Status |
|---|---|---|---|
| lease TTL | 30 s | `services/execution/execution_gateway/lease.py` (`LeaseStore.acquire`, `preempt`, `renew`) | [Open: O-28] — code default, not a target |
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
- The recovery point and recovery time objectives that the failover and restore measurements are compared against (O-18, DR_PLAN).

**No cell is provisioned and no storage or bus manifest exists**; a reader must not infer a provisioned cell from this document [Open: H-05, A-6, B-15].

## 9. Conditions applied in v0.2 [Committee]

| Condition (ARB §4.3, carried by D-061) | Applied |
|---|---|
| C-CM-1 header status; "structure at Gate B, baselines at Gate C, targets at Gate E" replaces the ARB-signs sentence | yes — header and §0 |
| C-CM-2 §Storage cost model inserted with the evidence-id rule | yes — §2, with the two openly stated deviations |
| C-CM-3 control-state store row and measurement plan; code defaults listed as parameters | yes — §1, §3, §7 |
| C-CM-4 measurement plan extended to all nine SLIs | yes — §5; all nine are capacity-relevant, so no exclusion reason is claimed |
| C-CM-5 human-input list extended; the line that no cell is provisioned | yes — §8, §0 |
| C-CM-6 SRE Lead review recorded in the header; AEI row; CONTAINER_DIAGRAM line 44 | partly — the header records the SRE Lead review as **pending** (it has not happened and cannot be self-signed); the AEI row is **proposed**, not written, in docs/SESSIONS/REVIEW_2026-09-08_capacity_v0.2.md §7 (the owner does not write the evidence index for his own artefact); the CONTAINER_DIAGRAM correction **is applied** (v1.1) |
| added by the owner, not an ARB condition | §0 plane-bypass and CI-timing rules; §1 outbox/bus row; §3 executor failover row; §5 measurement-point and safety-semantic columns; §6 NFR mapping; §10 change log |
| new since the ARB review (not a condition) | §1 audit-store row, §4 audit measurement plan (ADR-020, D-062), the two anchor cadence parameters in §7 |

## 10. Change log [Committee]

| Version | Date | Change |
|---|---|---|
| v0.1 | earlier | skeleton: planes, shed policy, four SLIs, human inputs |
| v0.2 | 2026-09-08 | C-CM-1..C-CM-6 applied (§9); drafted by the Data Architect (REVIEW_2026-09-08_architecture_docs_v1.1.md Appendix A), adopted with amendments by the Enterprise Architect (REVIEW_2026-09-08_capacity_v0.2.md §3), pasted by the Cloud Architect. Still no number beyond the one measured, evidence-carrying cell in §2 |

## 11. Review record (Definition of Done for this document) [Committee] [Source: 13]

| Step | Role | State |
|---|---|---|
| Owner | Enterprise Architect / Cloud Architect | **v0.2 adopted** on 2026-09-08 (drafted by the Data Architect at the delegate's direction; amended by the Enterprise Architect; written to the file by the Cloud Architect) |
| Reviewer (different line) | SRE Lead | **pending** — the SRE Lead will not review a model that omits `time_to_halt_s`; §5 now carries all nine SLIs |
| Approving body (advisory) | ARB | structure recommended on v0.1 (C-CM-1..C-CM-6); has **not** seen v0.2; no number is accepted and none is presented |
| Independent validation | Independent Validation Agent | pending |
| Decision | **human Product Owner (D-039)** | pending |
```

## Appendix B — `docs/CONTAINER_DIAGRAM.md` line 44: **applied** (commit `5d97199`)

Applied with the amendments of §3 A13 (ADR-004 rev.2 is owed, not existing; ADR-005/R-05 on the bus; a closing sentence that nothing is provisioned; header bumped to v1.1 with the reviews pending). The text now in the file:

```
Stack [Source: 03]: Next.js/TypeScript PWA; FastAPI with Pydantic v2 strict models at the edges, engines framework-free and importable without the web stack (ADR-009 Accepted, D-055; the Execution-plane host language is re-decided at Gate C on measured baselines, never on a date — O-86); PostgreSQL; bitemporal market-data store = PostgreSQL per regional cell plus an object-storage archive in the same cell, with a dedicated time-series database only on a measured trigger (D-056; **ADR-004 still records the deferral — its rev.2 is owed by the Enterprise Architect**; no cost figure is decided, every CAPACITY_MODEL §Storage term stays [Open: O-87, O-88]); object storage (evidence); Redis (controlled cache); Kafka-compatible bus + schema registry (ADR-005; dev/sim carries events in process after the outbox write, no bus is deployed) [Open: R-05]; containers, IaC, mesh where justified, vault/HSM/KMS, WAF, SIEM, tracing, feature flags.

Nothing in that line is provisioned [Committee]: `infra/kubernetes` holds namespaces and network policies only and `infra/iac/README.md` says modules are added once the provider is chosen; a reader must not infer a deployed component from the stack line [Open: H-05, A-6, B-15].
```
