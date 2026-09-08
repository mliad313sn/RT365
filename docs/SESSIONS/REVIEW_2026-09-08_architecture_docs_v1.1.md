# REVIEW 2026-09-08 — DATA_FLOWS v1.1 and CAPACITY_MODEL v0.2: applying the ARB conditions (O-129, D-061)

| Session | Date | Author | Line | Status |
|---|---|---|---|---|
| Data Architect applying C-DF-1..C-DF-6 and (as drafter, not owner) C-CM-1..C-CM-6 | 2026-09-08 | data-architect agent, at the direction of the Product Owner delegate's session on O-129 / D-061 | 1st | **artefact edit + proposals; no approval, no decision** |

> Nothing in this packet is a decision or an approval. DATA_FLOWS v1.1 is written by its owner and is **not accepted**: the Privacy Lead's review (different line), the Security & Privacy Board's classification review and the human Product Owner's decision (D-039) are all pending. CAPACITY_MODEL v0.2 and the CONTAINER_DIAGRAM correction are **proposed text for their owning roles** (see §6 — the write-scope guard refused the edit, correctly). No capacity figure, latency, price, vendor capability, licence term or regulatory status is asserted. Profit is an objective, never a promise [Source: 00]. Tags: [Source: NN], [Committee], [Open].

---

## 1. Roles

| Function | Role | Line | In this session |
|---|---|---|---|
| Author / owner of DATA_FLOWS | Data Architect (this agent) | 1st | wrote docs/DATA_FLOWS.md v1.1; approves nothing |
| Reviewer of record for DATA_FLOWS | **Privacy Lead** | 2nd | **pending** — must re-read the code paths named in §1 of the document at the commit that carries v1.1 |
| Classification half of DATA_FLOWS | **Security & Privacy Board** | 2nd | **pending** — every classification cell is a proposal |
| Owner of CAPACITY_MODEL and CONTAINER_DIAGRAM | **Enterprise Architect / Cloud Architect** | 1st | **must adopt or amend** the text proposed in Appendix A and B; this agent may not write those files |
| Reviewer of record for CAPACITY_MODEL | **SRE Lead** | 2nd | **pending** |
| Recommending body | ARB chair (COUNCIL_2026-09-08_gate_B_arb_docs.md) | 2nd | issued C-DF-1..C-DF-6 and C-CM-1..C-CM-6; has not seen v1.1 / v0.2 |
| Independent validation | Independent Validation Agent | 3rd | re-validation [Open] before any decision is recorded |
| Decision | **human Product Owner (D-039)** | — | decides; agents never record an approval |

## 2. Purpose and inputs

Apply the ARB conditions carried by **D-061** and tracked as **O-129**: DATA_FLOWS v1.0 not accepted, v1.1 must apply C-DF-1..C-DF-6; CAPACITY_MODEL accepted as a **structure only (v0.2)** with C-CM-1..C-CM-6 and **no number accepted, because none was presented** [Committee].

Read in full at commit `ded8e17`: docs/SESSIONS/COUNCIL_2026-09-08_gate_B_arb_docs.md, docs/SESSIONS/COUNCIL_2026-09-08_gate_B_arb.md (§4.3), docs/DATA_FLOWS.md v1.0, docs/CAPACITY_MODEL.md v0.1, docs/CONTAINER_DIAGRAM.md, docs/NFR.md, observability/slis.yaml (nine SLIs), observability/alerts.yaml, docs/ADRs/ADR-018, ADR-019, ADR-020, docs/RAID_LOG.md O-101..O-137, docs/DECISION_LOG.md D-055..D-062 [Committee]. Code read for the flow register: `libs/core/rtcore/{store,trust,signing}.py`, `services/audit/audit_service/{store,anchor}.py`, `services/execution/execution_gateway/{gateway,authorisation,lease}.py`, `services/oms/oms/{pipeline,outbox}.py`, `services/market-data/market_data/{service,store}.py`, `connectors/data-providers/data_providers/{base,simulated}.py`, `mcp/servers/mcp_servers/{tools,registry,allowlist}.py`, `apps/web/web_bff/{app,platform}.py`, `apps/cli/rt365_cli/main.py`, `installer/rt365.spec` [Committee].

## 3. Condition by condition

### 3.1 DATA_FLOWS (C-DF-1..C-DF-6) — all applied

| Condition | What changed | Where |
|---|---|---|
| C-DF-1 | DF-05 replaced: nine controls in order (plane guard, command authorisation with one-shot grant and max age, idempotency inbox, one live order per intent, fencing token, permission oracle with its precedence, one-transaction registration, fail-closed on store error, cancel-on-restart), carrier (dev/sim in-process after the outbox write; bus in deployment), tests TC-EX-001..011, TC-DUR-001..004, TC-SIG-001..004, TC-NET-001..004, and the in-memory intent-tracker/decision-index caveat | DATA_FLOWS §1 DF-05 |
| C-DF-2 | DF-03 now states that no direct Analytics↔Execution route exists or may exist (`analytics.yaml`, `execution.yaml`, checker rule 2), names the two admissible carriers (Control-plane read model or `portfolio.*` bus event), recommends the read model as DF-03a, and marks the row as **not evidence for any deployed environment** until the carrier is agreed with the Cloud Architect | DATA_FLOWS §1 DF-03; RAID row RD-1 proposed in §7 |
| C-DF-3 | Store-seam flows drawn: DF-10 control-state store, DF-11 journal, DF-12 MCP revocation/nonce journals, DF-13 outbox relay, DF-14 command authorisation key — each with plane, carrier, classification, controls, code path, tests and the D-058 conditions (O-115 separation, O-118 journals apart, O-110 integrity, O-111 compaction/retention) | DATA_FLOWS §1, §2 |
| C-DF-4 | DF-15 tenant binding, DF-17 Kill Switch fan-out, DF-18 alert auto-actions, DF-16 AI context with an explicit processor cell ([Open: H-06] — no provider chosen), DF-19 reconciliation and portfolio roll-up (drawn, at the owner's discretion) | DATA_FLOWS §1 |
| C-DF-5 | D-056 residency and knowledge-time note on DF-01/DF-02 and in §4; DF-06 mTLS, DF-07 WORM and DF-09 written as targets with their [Open] references | DATA_FLOWS §1, §4 |
| C-DF-6 | Header Status: reviewed by the ARB chair, recommendation issued, Privacy Lead and Board reviews pending, **human Product Owner decision pending**, and the explicit sentence that the document is not accepted until DECISION_LOG says so. The AEI row is **proposed** in §7 — the Data Architect does not write the evidence index | DATA_FLOWS header, §7 |

Amendment made openly: the ARB's proposed rows cite line numbers; v1.1 cites **module and symbol** so that the citation survives an edit [Committee].

### 3.2 CAPACITY_MODEL (C-CM-1..C-CM-6) — text produced, edit refused by the write-scope guard

| Condition | Text produced | Applied to the file? |
|---|---|---|
| C-CM-1 | header status ("Structure v0.2 … numbers [Open: O-03, O-87, O-88]; human PO decision pending"), and "the ARB accepts the structure at Gate B; baselines at Gate C; targets at Gate E" replacing the ARB-signs sentence | **no — Appendix A** |
| C-CM-2 | §Storage cost model (O-13) inserted verbatim from COUNCIL_2026-09-08_gate_B_arb.md §4.3, including the rule that a blank cell is [Open], never an estimate, and the single measured cell (639 B, sim fixture) carrying its evidence id | **no — Appendix A §2** |
| C-CM-3 | "Control-state store (ADR-018)" row in What is fixed now; the five-measurement plan; the code defaults listed as parameters, not targets | **no — Appendix A §1, §3, §6** |
| C-CM-4 | measurement plan extended to all nine SLIs of observability/slis.yaml, each with its measurement point and why it is capacity-relevant (`time_to_halt_s` and `control_plane_availability` included, as the SRE Lead required) | **no — Appendix A §5** |
| C-CM-5 | human-input list extended (H-08 tick rates and licence storage terms, Q-11-1 region, A-5 Finance seat, O-09/O-10 retention); the line that no cell is provisioned and no storage or bus manifest exists | **no — Appendix A §7, §0** |
| C-CM-6 | SRE Lead review recorded in the header as **pending** (it has not happened; it cannot be self-signed); AEI row proposed in §7; **CONTAINER_DIAGRAM line 44** replacement citing D-055 and D-056 | **no — Appendix A header, Appendix B** |
| new since the review | audit-store dimension row; the ADR-020 measurement plan (chain verification at open is O(events); anchor records accumulate); the two anchor cadence parameters — **all [Open], no number invented** | **no — Appendix A §1, §4, §6** |

## 4. Flows added in v1.1

| Flow | Why |
|---|---|
| DF-10 control-state store (data at rest) | the first persistent data-at-rest flow of the control envelope (ADR-018); C-DF-3 |
| DF-11 store journal | a second, unbounded copy of every Confidential value, with no retention rule; C-DF-3 |
| DF-12 MCP revocation and nonce journals | dev/sim co-location with Execution-plane state; apart from shadow (O-118); C-DF-3 |
| DF-13 outbox relay to the bus | the deployment carrier of DF-05 and of every event; at-least-once; C-DF-3 |
| DF-14 command authorisation key | the platform's second secret, undrawn until now; C-DF-3 |
| DF-15 tenant binding | NFR-TEN-01 is a data flow with its own controls and quartet; C-DF-4 |
| DF-16 AI context to a model provider | D-052; processor column with no provider chosen; C-DF-4 |
| DF-17 Kill Switch fan-out | the switch supersedes every other flow [Source: 00]; C-DF-4 |
| DF-18 alert auto-actions | a machine path that can engage the Kill Switch; C-DF-4 |
| DF-19 reconciliation and portfolio roll-up | drawn at the owner's discretion; C-DF-4 |
| **DF-20 public trust set** (`mcp/policies/trust/registry_keys.json` → registry loader, `rt365 check`, MCP servers, installers) | **new since the ARB review** (ADR-019, D-060): a public data-at-rest artefact that every verifier reads, absent = empty = refuse everything |
| **DF-21 audit store file** (`audit_state.sqlite`) | **new since the ARB review** (ADR-020, D-062): a second store file, never the control store's file, transaction domain or restore unit |
| **DF-22 audit chain head → anchor directory** | **new since the ARB review** (ADR-020, D-062): a cross-boundary flow to a directory written by a **different principal**; heads only, no event content |

## 5. Threat-model delta [Committee] — proposed to the Security Architect, who owns THREAT_MODEL

| Candidate | Flow | Statement |
|---|---|---|
| journal as a second copy | DF-11 | an attacker or an erasure obligation meets a second, unbounded copy of every Confidential value with no retention, no compaction and unkeyed digests [Open: O-110, O-111, O-09] |
| co-located MCP journals | DF-12 | MCP-side state in the same directory as Execution-plane state; the compromise of one file path reaches both [Open: O-118] |
| cross-schema read after O-115 | DF-10 | once the stores split, a control-plane role reading the execution schema is a plane bypass by database grant rather than by network route [Open: O-115] |
| alert payload to auto-action | DF-18 | attacker-chosen alert fields reaching `killswitch_platform` or `revoke_tool_for_scope` (D-034 generalised) [Open: O-137] |
| **trust set as a denial surface** | DF-20 | an absent, truncated or replaced trust set refuses everything (fail closed by design) — availability abuse; and a trust set that is silently *added to* is a forging surface if the review step is missing [Open: O-126] |
| **witness starvation** | DF-22 | making the anchor directory unwritable or stale halts the platform through `audit.chain_verification_failed` → `killswitch_platform`; the documented recovery is to restore the replica, never to disable the check [Open: O-134, O-137] |
| **anchor as a metadata channel** | DF-22 | anchor records carry length and time, so they leak activity timing to whoever holds the witness store; they carry no business content by construction [Committee] |

## 6. Conditions not applied, and why [Committee]

1. **CAPACITY_MODEL v0.2 and the CONTAINER_DIAGRAM line-44 correction were not written to their files.** `scripts/agent_guard.py` refused the edit: those files are owned by the Enterprise Architect / Cloud Architect and are outside the data-architect write scope in `.claude/agents/roster.json`. The guard is a control of this project and this agent did not route around it (a Bash write would have evaded the hook, which is precisely the gap RAID **O-131** records). The complete, ready-to-apply text is in **Appendix A** and **Appendix B**; applying it is one paste each for the owning role, followed by the SRE Lead's review. **The conditions are therefore *drafted*, not *applied*, and O-129 stays open for CAPACITY_MODEL.**
2. **C-DF-2 is applied as a constraint, not as a carrier decision.** Choosing between a Control-plane read model and a bus event is an architecture choice with a privacy consequence; it needs the Cloud Architect (and, on the second copy of account state, the Board). DF-03 therefore names the constraint, recommends the read model and is marked as not evidence for any deployed environment until the choice is made (RD-1 in §7).
3. **No reviewer column was filled and no AEI or RAID row was written.** The Data Architect neither reviews nor approves this document, and the ledgers are the Program Orchestrator's; rows are proposed in §7.
4. **No number was added anywhere.** ADR-020's chain verification at open is O(events) and its anchor records accumulate; both are in the measurement plan as [Open] with the test or PERFORMANCE_PLAN stage that would produce a baseline. Inventing a figure would have been worse than leaving the cell empty [Committee].

## 7. Proposed ledger rows (for the owning roles; no id is assigned here)

**RAID (Program Orchestrator):**

| Ref | Type | Entry | Owner | Gate |
|---|---|---|---|---|
| RD-1 | Decision | DF-03 deployed carrier: Control-plane read model (recommended, drawn as DF-03a) or `portfolio.*` bus event; a read model is a second copy of account state and needs its own classification, residency and retention. No direct Analytics↔Execution route exists or may exist (checker rule 2) | Data Architect with Cloud Architect; Security & Privacy Board consulted | B/C |
| RD-2 | Gap | DATA_FLOWS v1.1 exists (C-DF-1..C-DF-6 applied) but is **not accepted**: Privacy Lead review, Board classification review and the Product Owner's decision are pending; the classification of the store journal (DF-11) as a "record" under PRIVACY_IMPACT is the first question for the Privacy Lead | Privacy Lead; S&P Board chair | B |
| RD-3 | Gap | CAPACITY_MODEL v0.2 text is drafted (Appendix A of this packet) but not applied to docs/CAPACITY_MODEL.md, and the CONTAINER_DIAGRAM line-44 correction (Appendix B) is not applied, because the drafting agent has no write scope on those files; owner adoption plus SRE Lead review outstanding — O-129 stays open for CAPACITY_MODEL | Enterprise Architect / Cloud Architect; SRE Lead | B |
| RD-4 | Gap | THREAT_MODEL rows owed for the trust set as a denial and forging surface (DF-20), witness starvation (DF-22), the anchor as a metadata channel (DF-22), in addition to the four rows the ARB already listed | Security Architect | B (rows) / C (tests) |
| RD-5 | Observation | The trust-set file `mcp/policies/trust/registry_keys.json` does not exist in the tree; the loader treats absent as empty and refuses everything asymmetric (fail closed). DATA_FLOWS DF-20 draws it as a deployment artefact with its owner and review step still owed (O-126) | MCP Security Agent; Cloud Architect | C |

**AUDIT_EVIDENCE_INDEX (Program Orchestrator):** a dedicated row "DATA_FLOWS.md v1.1" — owner Data Architect, reviewer **Privacy Lead (pending)**, classification review **Security & Privacy Board (pending)**, approving body ARB (recommendation only), IVA column blank until the IVA signs, location docs/DATA_FLOWS.md at the commit that carries v1.1; and a row "CAPACITY_MODEL.md v0.2" created **only when the version exists**, so the reviewer signs the text that was reviewed.

**REQUIREMENTS_TRACEABILITY (QA Lead / Program Orchestrator):** proposed rows, requirement → architecture → owner → control → test → evidence → gate:

| Requirement | Architecture | Owner | Control | Test | Evidence | Gate |
|---|---|---|---|---|---|---|
| NFR-AUD-01 (audit integrity) | DF-07, DF-21, DF-22: audit chain on the store seam in its own file, heads witnessed by a different principal | Backend Lead / SRE Lead | no update or delete path; chain verified at open; witness contradiction and silent re-anchoring refused; fail closed with S1 | TC-AUD-006..009 | docs/DATA_FLOWS.md DF-21/DF-22; docs/ADRs/ADR-020.md | B (dev/sim) |
| NFR-SEC-* (signature verification) | DF-20: public trust set read by the registry loader, the CLI and the installers | Security Architect / MCP Security Agent | verifiers hold public material only; algorithm allowlist; retired key verifies nothing; absent trust set refuses everything | TC-SIG-001..004, TC-AI-005, TC-PKG-001..005 | docs/DATA_FLOWS.md DF-20; docs/ADRs/ADR-019.md | B (dev/sim) |
| NFR-RES-01 / NFR-CON-01 (durable control state) | DF-10, DF-11, DF-13 | Backend Lead | one transaction domain, digests, chained journal, fail closed; at-least-once relay with a consumer inbox | TC-DUR-001..004, TC-EX-011, TC-KS-010 | docs/DATA_FLOWS.md DF-10/DF-11/DF-13; ADR-018 | B (dev/sim) |
| NFR-TEN-01 (tenant isolation) | DF-15, DF-03, DF-08 | Backend Lead / Security Architect | server-side tenant fact; 404/403 semantics; per-tenant allowlist and quota; masking before the Analytics boundary | TC-TEN-001..004 | docs/DATA_FLOWS.md DF-15 | B (dev/sim) |
| SLI/capacity row (line 39) | CAPACITY_MODEL §5 (nine SLIs), §3 and §4 measurement plans | Enterprise Architect / SRE Lead | a blank cell is [Open], never an estimate; structure at Gate B, baselines at Gate C, targets at Gate E | measurements listed as [Open] with the stage that produces them | Appendix A of this packet until adopted | B structure / C baselines |

**PO_DECISION_QUEUE (Program Orchestrator):** "DATA_FLOWS v1.1 is written; instruct the Privacy Lead review and the Board classification review, then decide"; "CAPACITY_MODEL v0.2 text is drafted but unowned — instruct the Enterprise/Cloud Architect to adopt or amend Appendix A and the CONTAINER_DIAGRAM correction, then the SRE Lead review"; "DF-03 carrier (RD-1)"; "confirm whether the write-scope guard should have been overridden for this session, or whether drafting-in-packet is the standing answer (O-131)".

## 8. Control quartet for the controls this version newly documents [Committee] — ids by the QA Lead

| Control | Positive | Negative | Abuse | Recovery |
|---|---|---|---|---|
| **External audit witness (DF-22)** | events, seals and anchors survive a rebuild and verify against the published anchor (TC-AUD-006) | a consistently rolled-back store fails verification against the anchor; a stale or missing anchor fails closed with S1 (TC-AUD-007) | edited, shortened or mid-removed anchor files are detected; the publisher and its handle expose no audit write path; rollback and fork anchors refused (TC-AUD-008) | a corrupt anchor directory restored from the last good copy verifies again; incident and recovery rows share the alert's correlation id; one incident only (TC-AUD-009) |
| **Public trust set (DF-20)** | a command signed by the pipeline verifies with a public-key-only verifier; a registry signed with Ed25519 loads through the trust set (TC-SIG-001) | wrong key, altered payload, unknown `key_id`, retired key refused, fail closed (TC-SIG-002) | no private material reachable from the gateway verifier, the MCP runtime or the registry; algorithm and `key_id` confusion; HMAC registry outside dev/sim refused (TC-SIG-003, TC-AI-005) | rotation overlap then retire; re-signed registry loads and the predecessor's file is refused; trust set round-trips through its JSON file (TC-SIG-004) |
| **Audit store as its own file (DF-21)** | a platform rebuilt from `store_dir` reads back events, seals and anchors (TC-AUD-006) | an edited row is refused by the seam digest (TC-AUD-008) | after a consistent digest rewrite the audit chain still refuses (TC-AUD-008) | export, reload and verify in a fresh store (TC-AUD-004) |
| **Store journal retention (DF-11)** — **owed, no test exists** | [Open] a retention/compaction policy keeps `verify()` bounded at open | [Open] a read after compaction still verifies from the checkpoint | [Open] a deletion demand against a journal that cannot delete (O-135) | [Open] restore from a checkpoint plus journal tail | 

The last row is deliberately empty of evidence: the control does not exist yet, so no quartet may claim it does [Committee] [Open: O-111, O-135].

## 9. Evidence list mapped to docs/

| Artefact | State after this session |
|---|---|
| docs/DATA_FLOWS.md | **v1.1 written** (this session); reviewer and Board columns pending; not accepted |
| docs/CAPACITY_MODEL.md | **unchanged**; v0.2 text drafted in Appendix A for the owning role |
| docs/CONTAINER_DIAGRAM.md | **unchanged**; line-44 replacement in Appendix B |
| docs/SESSIONS/REVIEW_2026-09-08_architecture_docs_v1.1.md | this packet |
| docs/RAID_LOG.md, docs/DECISION_LOG.md, docs/REQUIREMENTS_TRACEABILITY.md, docs/AUDIT_EVIDENCE_INDEX.md | **not edited**; rows proposed in §7 |
| docs/ADRs/ADR-018, ADR-019, ADR-020 | read, not edited; ADR-018's adapter contract remains owed (O-130) |

## 10. Concerns for the Product Owner

- **PO-A The capacity model still has no owner's hand on it.** The ARB's conditions C-CM-1..C-CM-6 were drafted in full in this session, but the write-scope guard correctly refused a Data Architect edit to docs/CAPACITY_MODEL.md and docs/CONTAINER_DIAGRAM.md. O-129 therefore stays open for the capacity model, and Gate B cannot be convened on it until the Enterprise/Cloud Architect adopts Appendix A and the SRE Lead reviews it. If you want a single agent to be able to finish a cross-owner condition set in one session, that is a change to the roster (and to the review chain), and it is your decision, not the drafter's [Committee].
- **PO-B Two of the three new flows did not exist when the ARB reviewed.** ADR-019's trust set and ADR-020's audit store and anchor directory landed after the review that produced the conditions. The pattern the ARB flagged as PO-1 — decisions recorded faster than the owning roles update the exit-evidence artefacts — repeated inside a single week. Making "owning-role artefact edit applied and reviewed" a condition inside each D-nnn would have caught it [Committee].
- **PO-C The platform can now be stopped by losing a file.** An absent or malformed trust set refuses every asymmetric signature (DF-20) and a missing, stale or corrupt witness raises `audit.chain_verification_failed`, whose catalogued auto-action is `killswitch_platform` (DF-18, DF-22). Both are the correct fail-closed direction and both are new single points of *availability* failure whose recovery is "restore the file, then verify", never "disable the check". The runbook and incident-response entries are owed (O-126, O-134) and the platform-wide blast radius of the audit auto-action is a Trading Risk Committee question (O-137) [Committee].
- **PO-D The store journal is still a second, unbounded copy of Confidential data (DF-11), and now there is a third store.** `control_state.sqlite` plus its journal, `audit_state.sqlite`, the anchor directory and the two MCP JSONL files are five artefacts at rest with, between them, no retention rule, no backup schedule, no owner split and no residency statement. The Privacy Lead's first question should be whether the journal is a *record* under PRIVACY_IMPACT, because the answer sets its retention and legal-hold behaviour, and an append-only chain that cannot delete meets an erasure duty head-on (O-135) [Open].
- **PO-E DF-03 is drawn on a route that must not exist.** Portfolio (Execution) → AI (Analytics) has no NetworkPolicy path and must not have one. v1.1 states the constraint and marks the row as not evidence for any deployed environment, but the carrier — a Control-plane read model or a bus event — is still undecided, and either choice creates a second copy of account state that the Board should see (RD-1) [Committee].
- **PO-F No number was added to the capacity model, and two new O(n) costs were added to its unknowns.** ADR-020 verifies the whole audit chain when the store is opened and accumulates anchor records; both sit next to the control store's `verify()` on the start-up and failover path. They are in the drafted measurement plan as [Open] with the stage that would produce a baseline. Nobody has measured any of them, so nobody should quote one [Open: O-03, O-111, O-133].
- **PO-G Nothing in this session is an approval.** DATA_FLOWS v1.1 is the owner's own text; the Privacy Lead, the Security & Privacy Board, the SRE Lead and the Independent Validation Agent have signed nothing, and `make all` being green is not a review [Source: 13].

## 11. Assumptions, confidence, provenance

- Assumptions: the ARB packet's conditions are the instruction set; D-055..D-062 stand as recorded; the code read at `ded8e17` is the code that ships in dev/sim [Committee].
- Confidence: **high** that the code-path, carrier and test cells of DATA_FLOWS v1.1 match the tree at `ded8e17` (each was read); **high** that the capacity structure satisfies C-CM-1..C-CM-5 as text; **none** on any classification decision (the Board's), **none** on any number (none is proposed), **none** on any licence, broker capability or regulatory status (none is assumed).
- Provenance: [Source: 00, 03, 04, 05, 06, 08, 10, 13] as transmitted by the repository artefacts; [Committee] for this session's reasoning; [Open] items carry their register ids.
- Independence: the author of DATA_FLOWS v1.1 is its owner, not its reviewer and not its approver; the drafter of Appendix A is neither the owner nor the reviewer of the capacity model.

---

## Appendix A — proposed docs/CAPACITY_MODEL.md v0.2 (for the Enterprise Architect / Cloud Architect to adopt or amend)

```markdown
# CAPACITY_MODEL (Gate B exit evidence — structure only)

| Owner | Reviewer (different line) | Approving body | First gate | Status |
|---|---|---|---|---|
| Enterprise Architect / Cloud Architect | SRE Lead | ARB | B | **Structure v0.2, 2026-09-08 — structure recommended by the ARB (COUNCIL_2026-09-08_gate_B_arb_docs.md §4.3, conditions C-CM-1..C-CM-6, carried by D-061: ACCEPT WITH CONDITIONS, structure only, *no number accepted because none was presented*); numbers [Open: O-03 targets, O-87 storage terms, O-88 TSDB trigger]; SRE Lead review **pending**; **human Product Owner decision pending (D-039)**. Not accepted: no acceptance exists until it is recorded in docs/DECISION_LOG.md.** |

> **Drafting note [Committee].** C-CM-1..C-CM-6 were drafted by the Data Architect at the direction of the Product Owner delegate's session of 2026-09-08 (docs/SESSIONS/REVIEW_2026-09-08_architecture_docs_v1.1.md). The text is the Enterprise Architect's and Cloud Architect's to adopt or amend; it is not adopted until they say so, and the SRE Lead's review (different line) is required before it can be offered as Gate B exit evidence. The drafter is not the owner, not the reviewer and not the approver [Source: 13].

## 0. Rules that govern every cell [Committee]

- **A cell is filled only with a measured or quoted value and its evidence id. A blank cell is [Open], never an estimate** (ARB C-13-1, IVA-B-07).
- **No number in this document is a target.** The ARB accepts the **structure** at Gate B; **baselines are accepted at Gate C and targets at Gate E** (O-03). This replaces v0.1's "the ARB signs the model once baselines exist", which contradicted the document's role as Gate B exit evidence and D-057 (C-CM-1).
- A value read out of the source code is a **parameter**, not a decision and not a target; §6 lists them separately so that nobody later cites a code default as if it were a decided value (C-CM-3).
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
| **Market-data store (D-056)** | per cell (Postgres bitemporal plus an object-storage archive); no cross-cell replication (ADR-007) | instrument / market_ts | never for decision-time reads; archive jobs shed first |
| **Audit store and its external witness (ADR-020)** | its own store file per platform, never the control store's; an anchor directory owned by a different principal (a WORM bucket or replica in deployment) [Open: O-54] | tenant (reads) / chain sequence (writes) | **Never** — a failed chain or a missing witness fails closed and carries the `killswitch_platform` auto-action [Open: O-137] |

These are cardinality and shed-policy statements, not capacity figures [Committee].

## 2. Storage cost model (O-13)

Inserted per C-CM-2 from COUNCIL_2026-09-08_gate_B_arb.md §4.3 (the text agreed with D-056), unchanged:

Cost per instrument-year = the sum over data classes *d* in {ticks, bars, snapshots, instrument-master versions, derived features} of
`rows_d/year x bytes_d/row x sum over tiers (months_in_tier x unit_price_tier)` + query/compute share + replication/egress share (audit replication is costed separately under the Audit WORM row).

| Term | How it is produced (measurement or source) | Source of truth | Status |
|---|---|---|---|
| rows_d/year per instrument | provider tick/bar rate per instrument class x sessions/year from `SessionCalendar` for the venue; measured on the licensed feed during shadow (PERFORMANCE_PLAN "Soak") | H-08 licence data sheet; F-4 calendars | [Open: H-08] |
| bytes/row (JSON) | `len(model_dump_json())` — 639 B for the sim snapshot with the embedded instrument row | schema + fixture; evidence id: COUNCIL_2026-09-08_gate_B_arb.md §2 measurement (`RT_ENV=sim`) | measured, **sim fixture only** — a property of the schema and the fixture, not of any licensed feed |
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

## 4. Audit store and external witness measurement plan (ADR-020) [Committee]

The audit trail became durable and externally witnessed after the ARB reviewed this document (D-062). Two properties are capacity-relevant and neither has a baseline; no figure is invented here [Open].

| Measurement | Why it matters | Produced by | Status |
|---|---|---|---|
| audit chain verification time at open versus chain length (O(events); it runs on every start and gates opening the store) | it sits on the start-up path of the whole platform, next to the control store's `verify()` | a synthetic chain of known length in CI, then PERFORMANCE_PLAN "Soak" | [Open] |
| audit rows and bytes per order lifecycle, and per MCP call | the audit store is a second durable store to size, back up and replicate | a TC on the compose topology (id by the QA Lead) | [Open] |
| anchor records accumulated per unit of activity (one per explicit seal and one per `anchor_every` events), their bytes, and the cost of the anchor chain, which is re-verified on every read | anchor records accumulate without compaction; compaction and retention are owed with the control-store journal's (O-111) | the same TC, plus the O-133 cadence decision | [Open] |
| seal and publication latency, and the cost of an unavailable witness (the fail-closed path) | a missing or stale witness halts the platform via `killswitch_platform` [Open: O-137] | PERFORMANCE_PLAN "Load"; chaos drill per docs/CHAOS_PLAN.md | [Open] |
| restore-and-reverify time for the anchor directory (the documented recovery is to restore the replica, never to disable the check) | it is an input to the recovery time objective (O-134, DR_PLAN) [Open: O-18] | DR drill | [Open] |

## 5. Measurement plan — all nine SLIs of `observability/slis.yaml` [Committee] — C-CM-4

No target is set for any SLI; targets are [Open: O-03] and are decided at Gate E [Source: 10].

| SLI | Baseline to measure | Where measured |
|---|---|---|
| `control_plane_availability` | successful control-plane decisions / total decision requests | `risk_engine`; capacity-relevant because the plane never sheds and fails closed (NFR-AVL-01) |
| `market_data_freshness_s` | `market_ts` age at snapshot use | `risk_engine.RK-FRESH` |
| `signal_latency_ms` | snapshot to signal | `strategy_service`; drives Analytics-plane autoscaling |
| `risk_decision_latency_ms_p99` | intent enqueue to decision-record write, p99 per cell | `oms.pipeline` span |
| `order_ack_latency_ms` | order command to broker ack | `execution_gateway` |
| `event_lag_ms` | produce to consume | bus (after the ADR-005 deployment) [Open: R-05] |
| `reconciliation_completeness_pct` | reconciled positions / total by EOD+T | `reconciliation_service`; sizes the reconciliation window |
| `time_to_halt_s` | Kill Switch engage to the last open-order cancel and identity revocation recorded (D-044) | `killswitch_service.activate`; produced by the Kill Switch drill (TC-KS-009) and sized by the number of open orders and identities per cell |
| `alert_delivery_s` | alert to operator ack | notification path; bounds the auto-action paths of docs/DATA_FLOWS.md DF-18 |

## 6. Parameters that exist in code as defaults, not targets [Committee] — C-CM-3

These are read out of the source; none is a decision, a baseline or a target, and none may be cited as one.

| Parameter | Default in code | Where | Status |
|---|---|---|---|
| lease TTL | 30 s | `services/execution/execution_gateway/lease.py` (`acquire`, `preempt`, `renew`) | [Open: O-28] — code default, not a target |
| store busy timeout, then `StoreError` (fail closed) | 5 s | `libs/core/rtcore/store.py` (`SqliteStore`) | [Open: O-117] — code default, not a target |
| command maximum age | 5 min | `services/execution/execution_gateway/gateway.py` (`COMMAND_MAX_AGE`, ADR-015 addendum) | [Open] — code default, not a target |
| audit anchor cadence `anchor_every` | 25 events | `services/audit/audit_service/store.py` | [Open: O-133] — dev/sim placeholder; it bounds how many events a consistent-rewrite attacker could reach, so it is a risk decision |
| audit anchor staleness ceiling `max_anchor_lag` | 200 events | `services/audit/audit_service/store.py` | [Open: O-133] — dev/sim placeholder; it bounds how stale the witness may be |

## 7. Inputs that only humans can supply [Committee] — C-CM-5

- Expected intents per second per cell; number of tenants and accounts at launch; instrument universe size; cloud budget (docs/MISSING_ACTIONS.md H-05).
- Provider tick and bar rates and the licence's storage, redistribution and retention terms (H-08) [Open: O-12].
- The region whose price list applies (Q-11-1) and the price quote itself (H-05, A-1).
- The Finance seat that holds the cost sheet (A-5); the sheet is filled from measurements and quotes, never back-solved from a price hypothesis (C-13-5).
- Retention schedules per jurisdiction (O-09, O-10), which set the months per tier in §2.
- The second principal that owns the anchor directory, and the cadence values of §6 (O-54, O-133).

**No cell is provisioned and no storage or bus manifest exists**; a reader must not infer a provisioned cell from this document [Open: H-05, A-6, B-15].

## 8. Conditions applied in v0.2 [Committee]

| Condition (ARB §4.3, carried by D-061) | Applied |
|---|---|
| C-CM-1 header status; "structure at Gate B, baselines at Gate C, targets at Gate E" replaces the ARB-signs sentence | yes — header and §0 |
| C-CM-2 §Storage cost model inserted with the evidence-id rule | yes — §2 |
| C-CM-3 control-state store row and measurement plan; code defaults listed as parameters | yes — §1, §3, §6 |
| C-CM-4 measurement plan extended to all nine SLIs | yes — §5 |
| C-CM-5 human-input list extended; the line that no cell is provisioned | yes — §7, §0 |
| C-CM-6 SRE Lead review recorded in the header; AEI row; CONTAINER_DIAGRAM line 44 | the header records the review as **pending** (it has not happened and cannot be self-signed); the AEI row is proposed in docs/SESSIONS/REVIEW_2026-09-08_architecture_docs_v1.1.md; the CONTAINER_DIAGRAM correction is Appendix B of that packet |
| new since the ARB review (not a condition) | §1 audit-store row, §4 audit measurement plan (ADR-020, D-062), the two anchor cadence parameters in §6 |

## 9. Review record (Definition of Done for this document) [Committee] [Source: 13]

| Step | Role | State |
|---|---|---|
| Owner | Enterprise Architect / Cloud Architect | adoption pending (drafted by the Data Architect at the delegate's direction) |
| Reviewer (different line) | SRE Lead | pending — the SRE Lead will not review a model that omits `time_to_halt_s`; §5 now carries it |
| Approving body (advisory) | ARB | structure recommended on v0.1; no number is accepted and none is presented |
| Decision | **human Product Owner (D-039)** | pending |
```

## Appendix B — proposed docs/CONTAINER_DIAGRAM.md line 44 (C-CM-6; Enterprise Architect)

Current line 44:

```
Stack [Source: 03]: Next.js/TypeScript PWA; FastAPI or typed service framework [Open: O-04]; PostgreSQL; time-series store [Open: O-13]; object storage (evidence); Redis (controlled cache); Kafka-compatible bus + schema registry; containers, IaC, mesh where justified, vault/HSM/KMS, WAF, SIEM, tracing, feature flags.
```

Proposed replacement:

```
Stack [Source: 03]: Next.js/TypeScript PWA; FastAPI with Pydantic v2 strict models at the edges, engines framework-free and importable without the web stack (ADR-009, D-055; the Execution-plane host language is re-decided at Gate C on measured baselines, O-86); PostgreSQL; bitemporal market-data store = PostgreSQL per regional cell plus an object-storage archive in the same cell, with a dedicated time-series database only on a measured trigger (ADR-004 rev.2, D-056; no cost figure decided, O-87/O-88); object storage (evidence); Redis (controlled cache); Kafka-compatible bus + schema registry [Open: R-05]; containers, IaC, mesh where justified, vault/HSM/KMS, WAF, SIEM, tracing, feature flags.
```
