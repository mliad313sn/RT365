# REVIEW 2026-09-08 — ADR-007 applied, NFR-SCL-01 amended, NFR-RES-01 split, and the ADR status lines reconciled

| Author (owner of the edited files) | Reviewers (different line) | Recommending body | Approver | Gate |
|---|---|---|---|---|
| Enterprise Architect (owns `docs/ADRs/`, `docs/NFR.md`, the C4 diagrams) | **Cloud Architect** for `docs/ADRs/ADR-007.md` (C-007-10; he is the finder, CA-R1/O-159); **SRE Lead** for `docs/NFR.md` (named reviewer in the file header, C-007-7); **Independent Validation Agent** for the status reconciliation of §4 | ARB (advisory, D-039/D-040) | **the Product Owner** (D-039/D-040) | **B** |

Branch `docs/adr-007-and-status`, from `worktree-agent-a3d50cbe36ebbf805` at `202378f`. **This packet records no decision and no approval, and no agent may record one** (D-039, D-065). Every status line changed in §4 quotes a decision that already exists in `docs/DECISION_LOG.md`; **no status was created by this session**. `docs/RAID_LOG.md`, `docs/DECISION_LOG.md`, `docs/REQUIREMENTS_TRACEABILITY.md` and `docs/AUDIT_EVIDENCE_INDEX.md` were **read and not edited**; every row this packet proposes for them is written here as text for its owner [Source: 13].

## 0. How to read this packet

Every statement carries **[Source: NN]** (blueprint section as transmitted by the repository artefacts), **[Committee]** (this session's or a cited council's reasoning) or **[Open]** (unresolved, with the register id that would settle it). **[Verified]** is used only where this session re-read a file or ran a command in this worktree and quotes the result. No capacity, latency, throughput, cost, price, provider capability, broker capability, venue capability, licence term or regulatory status is asserted anywhere [Source: 00]. **A target is never evidence. Profit is an objective, never a promise.**

## 1. Purpose

Three tasks, all arising from `docs/SESSIONS/COUNCIL_2026-09-08_arb_adr_007.md` (the ARB's recommendation on O-159, a Gate B entry condition) [Committee]:

1. **Apply the board's amended ADR-007** (§7 of that packet) to `docs/ADRs/ADR-007.md`, with the conditions that fall to me — C-007-1 (write "deployment cell" in full) and C-007-2 (the no-cell-plan sentence in the **Decision**, not a footnote, which is the Cloud Architect's stated condition for supporting a decision at all). **Status stays `Proposed`**: the delegate fills it from the decision record and I record no decision [Source: 13].
2. **Amend NFR-SCL-01 and split NFR-RES-01** (§9 of that packet, condition C-007-7, register item O-163). The requirement was written before this platform had durable state; the architecture is right and the requirement is wrong, unanimously [Committee: §4.4].
3. **Reconcile the ADR status lines**, scoped by what the Gate B evidence set cites, ADR-001 first (PO-7). A Gate B reader must be able to tell an undecided decision from a stale status line by reading the ADR [Committee: §12].

Confirmation of the state that made this work necessary [Verified 2026-09-08, this worktree]: `make all` is green — 222 tests pass, 21 event schemas match the models, the network-policy checker passes, 67 agents match `goals/`, secret scan clean. **None of that evidences anything about a deployment cell, and none of it evidences that an ADR is decided.** The regenerated `docs/TEST_CASES/` files are QA-owned and were reverted, not committed.

---

## 2. What I applied, and what I changed from the board's §7 text, with reasons

The board's §7 is a **recommendation to the owner of the file, not a dictation**. I applied it as its author. What I did not change: the residency-first **definition** (item 2), the closed directional **four-item list** (item 4), the **witness-outside-the-cell** rule (item 5), execution ownership per account (item 6), a tenant spanning cells (item 7), all five alternatives, and the Consequences. Those are the substance and I accept them [Committee].

| # | Change from the board's amended text | Reason |
|---|---|---|
| **1** | **The proposed "Accepted …" status wording is not written into the ADR.** The board's box ended with a status line "proposed for the delegate". I wrote the literal word `Proposed` in the Status field, added a sentence saying the ADR **is undecided and no decision-log entry accepts it**, and moved the proposed wording into §9.2 of this packet | Task 3 exists because a Gate B reader cannot tell a decision from a status line. An ADR file containing the sentence "Accepted as a constraint set with conditions" **anywhere in it** reproduces exactly the ADR-017 ambiguity I was asked to remove. The delegate writes the status from the ledger; the wording is available to him here [Committee] [Source: 13] |
| **2** | **C-007-2 applied literally.** Decision item 8 now *opens* with the sentence "This ADR decides no cell plan; no deployment cell is provisioned; a deployment cell has no capacity because there is no deployment cell." The board's item 8 said all three things, spread across the paragraph | The Cloud Architect made his support conditional on **that sentence** being in the Decision text. A condition on a sentence is met by the sentence, not by its sense [Committee: §4.3] |
| **3** | **C-007-1 applied more strictly than the board's own box.** "Deployment cell" is written in full throughout the ADR, including "deployment-cell boundary"; the bare word "cell" survives only inside `JurisdictionCell`, inside quoted prior text ("cell plan", "cell per venue cluster" as the rejected alternative's name) and in "cell-local" | The board's box uses the bare word roughly twenty times while imposing C-007-1 on five other documents. The condition should bind its own author's text first. The homonym sits under a **dual-key control** (NFR-GLO-01, D-050): the failure mode is a sentence about provisioning being read as a sentence about market enablement [Committee: F-7, F-8] |
| **4** | **The ADR-021 citation is annotated.** Item 4 now says ADR-021 is proposed in `docs/SESSIONS/BUILD_E04_2026-09-08_fx_decision_input.md` and that **no ADR-021 file exists in `docs/ADRs/`** [Open: O-171 proposed] | The board cited "ADR-021, D-064" as if it were a readable ADR. It is not: `docs/ADRs/` ends at ADR-020 [Verified]. A cross-reference a reader cannot follow is the same defect class as a status line he cannot trust |
| **5** | **`NFR-RES-01` → `NFR-RES-01b`** wherever the board's text meant the deployment-cell half, and `ADR-010`, `ADR-014`, `ADR-018` re-keyed to `NFR-RES-01a` | C-007-7 requires the NFR split **in the same working session**. Applying the split and leaving the ADR set pointing at a requirement id that no longer exists would have created a second broken reference while fixing the first |
| **6** | **`[Open: UX, O-122]` → `[Open: O-122]`** in the Consequences | "UX" is not a register id. An `[Open]` tag whose id cannot be looked up is decoration. O-122 is the real row (multi-account API contract) |
| **7** | **Register ids completed**: `Q-11-1` now reads `Q-11-1 / O-66` (the RAID row that carries it); `O-156` and `O-167` added to the DR consequence; `O-165` added beside `O-134` in item 5 | O-156 and O-167 are the two rows that actually measure and bound the O(n) start-up work the consequence describes; O-165 is the "no flag to disable the check" ruling that makes restore-then-verify the only recovery (D-066) |
| **8** | **"the human Product Owner decides" → "the Product Owner decides"** in the header, keeping "the Product Owner (D-039)" as approver | D-065 (2026-09-08) corrected this framing explicitly: all authority is delegated, the delegate decides every queue item and gate under D-039/D-040, and only the five acts of D-040 remain human. The board's phrasing predates that correction in this file [Source: D-065] |
| **9** | **The "Controls and tests affected" table now says ADR-001 is itself `Proposed`** and no decision accepts it | The board's row cited ADR-001 as the delivering control while its own §12 says ADR-001 is a proposal under a larger part of the Gate B pack than ADR-007. Both facts belong in the same table, or the table overstates its foundation [Committee: §12] |
| **10** | **A closing line points at C-007-1..C-007-10 and at §3 of this packet** for their application state | A condition set that lives only in a council packet is not tracked. The ADR now names where its conditions are tracked |

**What I did not do, deliberately.** I did not create ADR-021. I did not write ADR-004 rev.2 (O-158 — it is owed and it is mine, but it is a market-data storage ADR and writing it as a side-effect of a topology session is how one-sentence ADRs get made in the first place). I did not touch `docs/CONTAINER_DIAGRAM.md` (step 6 of the board's change order: it is a **v1.2** that must draw the deployment-cell frame, and it is a separate piece of work with a pending Cloud Architect review of v1.1 attached to it). I did not touch `docs/DR_PLAN.md`, `docs/CAPACITY_MODEL.md`, `docs/DATA_FLOWS.md`, `infra/iac/README.md` or `docs/PRIVACY_IMPACT.md` — they belong to the Cloud Architect, the Data Architect and the Privacy Lead, and the write-scope guard is right to hold me out of them.

**My own criticism of my own document, for the record [Committee].** I own `docs/ADRs/` and `docs/NFR.md`, and I let a one-sentence Decision with a six-word Consequences section become the foundation of two NFRs and three Gate B documents for a year. The right criticism is not that ADR-007 was wrong; it is that an ADR whose Consequences section is six words long cannot carry a Gate B document, and the Cloud Architect found that before I did.

---

## 3. Conditions C-007-1..C-007-10 as they now stand

| # | Condition (abridged) | Owner | State after this session | Evidence |
|---|---|---|---|---|
| **C-007-1** | "Deployment cell" in full; the bare word not used where `JurisdictionCell` could be meant, in ADR-007, CAPACITY_MODEL, DR_PLAN, CONTAINER_DIAGRAM, DATA_FLOWS, `infra/iac/README.md`; PRIVACY_IMPACT rows 13–14 disambiguated by the Privacy Lead | Enterprise Architect; Cloud Architect; Data Architect; Privacy Lead | **Applied in `docs/ADRs/ADR-007.md` and in `docs/NFR.md`** (Decision item 1; the "cell" note under the NFR table). **Owed elsewhere**: CAPACITY_MODEL, DR_PLAN, CONTAINER_DIAGRAM v1.2, DATA_FLOWS, `infra/iac/README.md`, PRIVACY_IMPACT | this commit; [Open: O-168 proposed] |
| **C-007-2** | The no-cell-plan sentence sits in the **Decision** section | Enterprise Architect | **Applied verbatim**, opening Decision item 8 | ADR-007 item 8 |
| **C-007-3** | The cross-cell list is the closed, directional four-item table; a fifth item needs a new ADR and this board | Enterprise Architect; Integration Architect at review | **Applied** (Decision item 4, including the sentence that no throughput, cost or availability argument may add one) | ADR-007 item 4 |
| **C-007-4** | `docs/DR_PLAN.md` amended before Gate B: the anchor directory is an input the standby **reaches**, never restored from inside the failed cell; the un-liftable-halt consequence stated; **no RPO/RTO figure** | **Cloud Architect** (owner), SRE Lead (reviewer) | **Not mine and not done.** ADR-007's Consequences names it as owed to DR_PLAN v1.2 | [Open: O-18; C-007-4] |
| **C-007-5** | Every venue-proximity, latency or connectivity statement is marked [Open] against a measured baseline or a contracted input | Enterprise Architect; counsel-broker-integration at review | **Applied** (Decision item 3; alternative (c)). No broker, venue or provider capability is asserted anywhere in the ADR | ADR-007 item 3 |
| **C-007-6** | The roll-up's **residency question** goes to the Privacy Lead and the Compliance & Legal Committee before any carrier is designed | **Privacy Lead; Compliance & Legal Committee** | **Not mine.** Stated in ADR-007 item 4(iii) as their question, not the ARB's | [Open: O-09, O-10, F-7; O-173 proposed] |
| **C-007-7** | NFR-SCL-01 amended and NFR-RES-01 split in the same working session | Enterprise Architect (owner); SRE Lead (reviewer) | **Applied** — `docs/NFR.md` v1.1, §5 below. **The SRE Lead's review is pending and this packet does not supply it** | this commit; [Open: O-129] |
| **C-007-8** | O-160 stays open and visible in the Gate B pack; the decision must not be read as delivering resource isolation | Cloud Architect; SRE Lead | **Applied in the ADR** (Context, first bullet; Consequences) . The Gate B pack's visibility is the Program Orchestrator's | ADR-007 Context; [Open: O-160] |
| **C-007-9** | The decision record states that it supplies **no reviewer signature** | delegate drafting the decision row; SRE Lead's condition | **Not mine to write.** Carried into the proposed DECISION_LOG row at §9.1, and restated at §11 (PO-3) | [Open: O-129] |
| **C-007-10** | Author ≠ reviewer ≠ approver on the amendment: the Enterprise Architect applies, the Cloud Architect reviews, the chair applies nothing, the Product Owner decides | Enterprise Architect; Cloud Architect; delegate | **Held.** I applied it; **I approve nothing**; the Cloud Architect's review is pending; the ARB chair's declared interest (§1 of the council packet) belongs in the decision row | this packet's header; [Open: Cloud Architect review] |

---

## 4. ADR status reconciliation, scoped by what the Gate B evidence set cites

**The rule I applied, and it is the whole of it [Committee] [Source: 13; CLAUDE.md "the ledgers stay the truth"]:** a status line may say "Accepted" only if an entry of `docs/DECISION_LOG.md` accepts that ADR, and it must cite the decision id and date. **No status was changed without an entry to cite.** An ADR that is genuinely undecided stays visibly undecided — and now says so in one line, so that a reader need not go to the ledger to discover it.

**Count [Verified 2026-09-08, `grep` of every `docs/ADRs/ADR-0*.md` status line].** Twenty ADR files exist (ADR-001..ADR-020; `ADR-000-template.md` is a template and is out of scope). Before this session, **eighteen** status lines began with the word `Proposed` — seventeen plainly, plus ADR-017's `Proposed (decided …)` hybrid — and two cited a decision (ADR-009, ADR-018). I record that this figure differs from both prior counts in circulation: the council packet says "sixteen of twenty" (§F-4, §12) and my brief says "nineteen of twenty". Neither matches the files. **After this session: fifteen read `Proposed`, five cite a decision.** ADR-018's amendment 1 carries its own status line and is listed separately.

| ADR | Title | Status **before** | Status **after** | Decision cited, or **owed** | Cited by the Gate B evidence set at |
|---|---|---|---|---|---|
| **ADR-001** | Three-plane topology | Proposed | `Proposed` + undecided note | **owed.** D-004 records "ADR-001..008 **proposed** to ARB" and D-042 ratified D-004 — that ratifies the *act of proposing*, not the ADRs. No entry accepts ADR-001 | AEI row 2b (gate B); NFR-SEC-01; every file in `infra/kubernetes/network-policies/`; `scripts/check_network_policies.py`; TC-NET-001..004; THREAT_MODEL B3/B4 |
| **ADR-002** | Executor lease with fencing token | Proposed | `Proposed` + note | **owed** (the other half of NFR-RES-01a) | AEI row 2b |
| **ADR-003** | Idempotency key derivation | Proposed | `Proposed` + note | **owed.** D-015 explicitly left the key derivation "unchanged pending ARB" (O-26) | AEI row 2b |
| **ADR-004** | Time-series store selection | Proposed | `Proposed` + note + **stale note** | **owed, and stale.** D-056 decided O-13; the ADR was never revised and still reads as the one-line deferral. **Rev.2 is owed first** (O-158) | AEI row 2b |
| **ADR-005** | Event bus and schema registry | Proposed | `Proposed` + note | **owed.** No bus is deployed in any environment [Open: R-05] | AEI row 2b |
| **ADR-006** | Service mesh justification | Proposed | `Proposed` + note | **owed.** No mesh exists in the build | AEI row 2b |
| **ADR-007** | Regional deployment cell as the failure and residency domain | Proposed | `Proposed`, amended text, with an explicit "This ADR is undecided" line | **owed.** The ARB recommends DECIDE WITH AMENDMENTS; the proposed decision row is at §9.1 | AEI row 2b; NFR-RES-01b, NFR-DR-01, CONTAINER_DIAGRAM v1.1, DR_PLAN v1.1, CAPACITY_MODEL v0.2, DATA_FLOWS v1.1 (O-159) |
| **ADR-008** | Single code path for backtest and production | Proposed | `Proposed` + note | **owed** | AEI row 2b |
| **ADR-009** | Typed service framework (FastAPI + Pydantic v2) | Accepted 2026-09-08 … (D-055) | **unchanged** | **D-055, 2026-09-08** (with D-040); conditions O-86, gating SCA | AEI row 2b; O-04 |
| **ADR-010** | In-process composition root, in-memory stores for dev/sim | Proposed | `Proposed` + note | **owed.** D-007 records it *pending ARB*, which is not an acceptance | AEI row 2b |
| **ADR-011** | Tool-registry signing: HMAC-SHA256 | Proposed | `Proposed` + note + **superseded note** | **owed, and superseded in substance.** D-053 moved registry signing to an asymmetric signature; D-060 accepted ADR-019. The "ADR-011 amendment" named in D-053's evidence column **does not exist** [Open: O-170 proposed] | AEI row 2b |
| **ADR-012** | Operator console: static dashboard now, PWA at E10 | Proposed | `Proposed` + note | **owed.** D-009 records it *pending Product Council* | AEI row 2b |
| **ADR-013** | Per-platform plane guard and simulation isolation | Proposed | `Proposed` + note | **owed.** D-027 records the approver as *pending* | AEI row 15 (gate B/D) |
| **ADR-014** | Per-intent live-order invariant; broker query before resubmit | Proposed | `Proposed` + note | **owed.** D-015..D-017 record the approver as *pending (ARB)* | AEI rows 14, 18 (gates B/C) |
| **ADR-015** | Execution gateway as last control point | Proposed | `Proposed` + note | **owed.** D-028, D-029 record the approver as *pending* | AEI rows 22, 24 (gates B/C) |
| **ADR-016** | Delivery agents, one MCP transport, fail-closed distribution | Proposed | `Proposed` + note | **owed.** D-036..D-038 record the approver as *pending* | AEI rows 26, 28 (gate B); NFR-GOV-01, NFR-DIST-01 |
| **ADR-017** | Meridian IT-PMO as the portfolio system of record | **`Proposed (decided by the Product Owner agent under D-040, D-049)`** — the hybrid | **`Accepted 2026-09-08 by the Product Owner agent under D-040 (D-049; ledgers stay the source of truth; Meridian's phase machine is not used for authorisation) [Open: O-73..O-76]`** | **D-049, 2026-09-08** | AEI row 33 (gate A); CLAUDE.md; `docs/PMO.md` |
| **ADR-018** | Durable control stores on the store seam | Accepted for dev/sim with conditions (D-058) | **unchanged** | **D-058, 2026-09-08** | AEI row 37 (gate C) |
| **ADR-018 amendment 1** | Journal head anchored into the audit chain | Proposed (2026-09-08) | `Proposed` + note | **owed.** D-066 decided the amendment's one open question and **still calls the amendment proposed**; no entry accepts the amendment as such | AEI row 47 (gate C) |
| **ADR-019** | Asymmetric signing with a public trust set | **Proposed** | **`Accepted for dev/sim with conditions (D-060, 2026-09-08; O-125, O-126, O-127/H-20, O-53, protected-path approvals at Gate C)`** | **D-060, 2026-09-08** | AEI row 40 (gate B) |
| **ADR-020** | Durable audit witnessed by an external anchor | **Proposed** | **`Accepted for dev/sim with conditions (D-062, 2026-09-08; O-54, O-133, O-134, O-135, O-137)`; amended in effect by D-066** | **D-062, 2026-09-08** (and D-066) | AEI row 42 (gate B) |
| **ADR-021** | FX as a deterministic decision input | **the file does not exist** | unchanged — **not created by this session** | **owed.** D-064 accepted the E04 build and calls ADR-021 "proposed (in the packet)". ADR-007 item 4 and `docs/DATA_FLOWS.md` cite it [Open: O-171 proposed] | cited by ADR-007 and by BUILD_E04 |

### 4.1 The councils owed a recommendation, so that nothing above sits unattributed [Committee]

| Owed ADR(s) | Advisory body that would recommend | Note |
|---|---|---|
| ADR-001, ADR-013 | **ARB with the Security & Privacy Board** | ADR-001 first: it is the foundation of NFR-SEC-01, of every network policy and of the checker. **The four passing plane tests conform to a proposal** |
| ADR-002, ADR-014, ADR-015 | **ARB with the Trading Risk Committee** (ADR-015 also the Security & Privacy Board) | lease policy O-28; O-26 (ADR-003 rev.2) is open |
| ADR-003, ADR-005, ADR-006, ADR-010 | **ARB** (ADR-005 with the Integration Architect) | ADR-005 and ADR-006 describe things that exist in no environment |
| ADR-004 | **ARB with the Data Architect** | **rev.2 first** (O-158); a status question on the pre-D-056 text is not answerable |
| ADR-007 | **ARB — already convened**; recommendation DECIDE WITH AMENDMENTS | the decision row is drafted at §9.1 |
| ADR-008 | **ARB with the Model Risk Lead** | |
| ADR-011 | **Security & Privacy Board** | an amendment or a supersession note, not an acceptance |
| ADR-012 | **Product Council with the ARB and the Accessibility Lead** | |
| ADR-016 | **ARB with the Security & Privacy Board and Executive Steering** | |
| ADR-018 amendment 1, ADR-021 | **ARB with the Security & Privacy Board** (amendment 1); **ARB with the Trading Risk Committee** (ADR-021) | both are text owed, not decisions owed |

---

## 5. The NFR changes (`docs/NFR.md` → v1.1)

Applied from §9 of the council packet. **Owner: Enterprise Architect. Reviewer (different line): SRE Lead — pending. Approving body: ARB (advisory). Decision: the Product Owner. No target, threshold or figure is added** [Committee] [Source: 13].

| Row | Before | After |
|---|---|---|
| **NFR-SCL-01** | "Stateless services; partition by tenant/account/instrument; autoscale on lag/latency" — target "Capacity model Gate B" | **Three assertions someone can fail**: the service tier holds no request state; all durable state lives in named stores each with a declared unit of scale and partition key; the platform scales by adding partitions. Each store is named with its register ids. Target is a **structure** reference to CAPACITY_MODEL §1/§3/§4/§7, "never a threshold"; baselines Gate C; targets Gate E |
| **NFR-SCL-02** (new) | — | Partition keys are the ones in CAPACITY_MODEL §1 and are **not restated**, so they cannot drift |
| **NFR-RES-01** | one row: "Regional cells as failure domains; active/standby execution ownership" — one target, "Failover with in-flight order test" | **split.** **NFR-RES-01a** executor lease and fencing token, TC-EX-003/004, TC-DUR-002, TC-EX-011, dev/sim [Open: O-117]. **NFR-RES-01b** the deployment cell as failure domain — **no test exists and none can exist until a second deployment cell is provisioned**; gate **E** |
| **NFR-DR-01** | "RPO/RTO per cell" | per **deployment cell**; names the two unmeasured O(n) verifications a standby inherits and the requirement that it reach an anchor directory that survived the failed cell. **No figure added** |
| **NFR-LAT-01** | "p99 per cell" | "p99 per **deployment cell**" (C-007-1) |
| **note under the table** (new) | — | (i) which requirements mean a **deployment cell** and which means a **`JurisdictionCell`**, with the sentence that provisioning enables no market and enablement provisions nothing; (ii) **why "stateless" went**, and the six named stateful dimensions |

**Why the requirement changed and not the architecture, in one paragraph [Committee: §4.4, unanimous].** NFR-SCL-01 was written before this platform had any durable state. It now has a control store, a market-data store, an audit store, an anchor directory, the MCP journals and an undeployed bus — and those stores are precisely why the platform can **fail closed across a restart**, which the delegate accepted deliberately in D-058 and D-062. Amending a requirement to match a correct architecture is not weakening a control. Leaving it would mean the Gate B pack contains a requirement its own capacity model contradicts (`docs/CAPACITY_MODEL.md` §6 raised the mismatch and correctly refused to fix another owner's file — CA-R6/O-163).

**Two things the new text does that the old one did not [Committee]:**

- **It refuses to read as an achievement.** The Security Architect's caution is carried verbatim into the file: "stateless" was doing security work by accident — people read it as *nothing persists, so nothing leaks* — and in fact four of these stores hold **Confidential data at rest with no file permissions, backup, residency or retention today** (`docs/DATA_FLOWS.md` DF-10) [Open: O-111, O-136, F-7]. The row says so, and the note says each store is a new thing to protect.
- **It names the stateful dimensions with their register ids instead of counting them.** The existing risk row O-163 says "four" (control store, audit store, anchor directory, MCP journals) and CAPACITY_MODEL §6 says "four" (control store, market-data store, audit store, bus). **They are different sets and their union is six.** A requirement that counts invites the next reader to count differently; a requirement that names does not.

---

## 6. Threat-model delta (proposed for the Security Architect; `docs/THREAT_MODEL.md` is his file and was not edited)

| # | Delta | Why it is new or changed | Existing rows it touches |
|---|---|---|---|
| **TD-1** | **A new trust boundary must be drawn: the deployment-cell boundary**, with exactly four crossings and their directions (ADR-007 item 4). It is *not* the plane boundary (B3/B4) | The boundary was implicit while there was one hypothetical cell. The amended ADR makes it explicit, directional and closed — and **nothing enforces it**: `scripts/check_network_policies.py` checks plane invariants within a cell, and no cell-boundary checker exists | B3, B4; T-53, T-57 |
| **TD-2** | **Witness co-location converts a bounded regional loss into an unbounded platform halt.** If the anchor directory sits in the cell it witnesses, the audited party and its witness die together; the standby cannot verify; restore-then-verify is the only recovery (O-134, O-165) and disabling the check is deliberately impossible | Follows from ADR-020's own text plus `killswitch_platform` (O-137). It needs no provisioned cell to be true. Remedy is ADR-007 item 5 (applied) plus DR_PLAN v1.2 (C-007-4, Cloud Architect) | T-61, T-74..T-79; [Open: O-172 proposed] |
| **TD-3** | **The portfolio roll-up is a cross-residency data path**, not merely a read model: position data leaving its region into a view served elsewhere. ADR-007 constrains it to read-only, derived, never-decides, never-on-a-recovery-path; it does **not** answer whether it is lawful | The constraint is architectural; the lawfulness is the Privacy Lead's and counsel's (C-007-6). The carrier is undecided [Open: R-05] | T-58; [Open: O-09, O-10, F-7; O-173 proposed] |
| **TD-4** | **Homonym as an attack surface, not just a confusion**: a change described as "provisioning a cell" being read, approved or audited as "enabling a cell", where enablement requires a **dual key** and a legal record (NFR-GLO-01, D-050) | T-53/T-57 cover the eligibility tuple; they do not cover the reviewer who mis-reads a provisioning change as an enablement change. The disambiguation is the control (C-007-1) | T-53, T-57; [Open: O-168 proposed] |
| **TD-5** | **Six stateful dimensions are now named in an NFR**, four holding Confidential data at rest with no permissions, backup, residency or retention | The naming does not create the exposure; it removes the sentence ("stateless services") that was hiding it | T-61, T-63; [Open: O-111, O-136, F-7] |
| **TD-6** | **A stale or asserted ADR status line is a governance-integrity weakness**: it lets a reviewer or an auditor believe a control's foundation was decided when it was not | ADR-020 read `Proposed` after D-062 accepted it, and ADR-017 read `Proposed (decided …)`. Both were record defects rather than code defects — and both are the kind of defect that only shows up at an audit | [Open: O-169 proposed] |

---

## 7. Control quartet for each critical control this session touches

Per the house rule, each control-bearing statement needs positive / negative / abuse / recovery. **Where no test exists I say so; a proposed test is never evidence** [Source: 00, 11].

**C1 — The closed, directional cross-cell list (ADR-007 item 4).**
- *Positive*: each of the four permitted crossings occurs in its stated direction with its stated property (audit replication outbound and append-only; anchor publication outbound to an outside principal; roll-up outbound into a read model; trust set inbound as a distributed signed artefact).
- *Negative*: a fifth crossing — any Control- or Execution-plane request, order, command, decision, approval, limit, lease, Kill Switch state, market-data row or FX rate — is refused at the boundary.
- *Abuse*: a throughput, cost or availability argument is used to add a crossing without an ADR; a "temporary" cross-cell read is added to a decision path.
- *Recovery*: the crossing is removed and the ADR is amended by this board; a boundary checker rule refuses the manifest.
- **State: no test exists and none can exist until a manifest and a second deployment cell exist.** Proposed: extend `scripts/check_network_policies.py` with a cell-boundary rule when the first manifest exists (owner: **Cloud Architect**) [Open: O-160, H-05].

**C2 — The witness lives outside the deployment cell it witnesses (ADR-007 item 5).**
- *Positive*: the standby that takes over a lost cell reaches the anchor directory and verifies the chain.
- *Negative*: a configuration placing the anchor directory inside the cell it witnesses is refused.
- *Abuse*: the check is disabled, or the anchor is "re-anchored" from a restored replica, to lift a halt.
- *Recovery*: restore-then-verify, only (O-134, O-165); there is deliberately no disable flag; the incident row and the S1 alert stand.
- **State**: TC-AUD-006..009 exercise the chain and the missing witness **in dev/sim, where the witness is a local directory, not a second principal** [Open: O-54]. The *placement* rule has no test; it is a DR drill owed with O-18 [Open: H-05]. **Existing evidence must not be described as covering it.**

**C3 — Deployment cell ≠ `JurisdictionCell` (ADR-007 item 1; the NFR note).**
- *Positive*: an enablement change requires the dual key and the legal record (NFR-GLO-01, D-050), regardless of any provisioning change.
- *Negative*: a provisioning change grants no enablement; an enablement grants no infrastructure.
- *Abuse*: a change described as "adding a cell" is approved by someone who believes he is approving infrastructure while he is approving a market — or the reverse.
- *Recovery*: the terms are disambiguated in every document that discusses both (C-007-1); PRIVACY_IMPACT rows 13–14 are corrected by the Privacy Lead.
- **State**: TC-GLO-001..004 test the enablement side. **The homonym itself is a documentation control with no test**; the honest mitigation is the wording [Open: O-168 proposed].

**C4 — Status-line integrity (new, and this session is its first application).**
- *Positive*: every ADR whose status says "Accepted" cites a decision id that exists in `docs/DECISION_LOG.md` with a matching date.
- *Negative*: an ADR with no decision-log entry reads `Proposed` and says it is undecided.
- *Abuse*: a status line is asserted to unblock a gate — the option the council rejected "without discussion" — or a hybrid ("Proposed (decided …)") is used to have it both ways.
- *Recovery*: the ledger is the truth; the status line is re-derived from it, never the reverse.
- **State: no test exists.** Proposed as a documentation lint in `make all` — for each `docs/ADRs/ADR-*.md`, if the status line names a `D-0xx`, that entry must exist in `docs/DECISION_LOG.md`; if it does not name one, the status must be `Proposed`. Owner: **Program Orchestrator** with **QA Lead** (test id to be allocated by QA; this packet does not allocate one) [Open: O-169 proposed].

---

## 8. Evidence produced by this session, mapped to `docs/`

| Artefact | What it evidences | What it does **not** evidence | Reviewer (different line) |
|---|---|---|---|
| `docs/ADRs/ADR-007.md` (rev.1) | the amended constraint set: residency-first definition, closed directional four-item list, witness outside the cell, per-account execution ownership, tenant spanning cells, and the explicit statement that no cell plan is decided | **that any decision was taken**; that a deployment cell exists; any capacity, latency, cost, provider, broker or venue figure | **Cloud Architect** — pending (C-007-10) |
| `docs/NFR.md` (v1.1) | NFR-SCL-01 replaced, NFR-SCL-02 added, NFR-RES-01 split into 01a/01b, NFR-DR-01 amended, the "cell" and "stateless" notes added | any threshold or target; the SRE Lead's review | **SRE Lead** — pending (O-129) |
| `docs/ADRs/ADR-017.md`, `ADR-019.md`, `ADR-020.md` | three status lines now agree with D-049, D-060 and D-062 | any new decision — each quotes an entry that already existed | **Independent Validation Agent** — pending |
| `docs/ADRs/` (fourteen files + ADR-018 amendment 1) | that each is undecided, in one line, with the ledger as the authority | that anyone has decided them; the note is a **record correction**, not a decision | **Independent Validation Agent** — pending |
| `docs/ADRs/ADR-010.md`, `ADR-014.md`, `ADR-018.md` | references re-keyed to NFR-RES-01a after the split | any change of substance | Cloud Architect / SRE Lead as applicable |
| this packet | what was applied, what was changed from the board's text and why, the condition state, the status table, the proposed ledger rows | any approval; **I approve nothing and record no decision** | Cloud Architect, SRE Lead, IVA, and the Product Owner decides |
| `make all` [Verified] | 222 tests pass; 21 event schemas match; network policies satisfy the plane invariants; 67 agents match `goals/`; secret scan clean | **nothing about deployment cells**, and nothing about whether an ADR is decided. The regenerated `docs/TEST_CASES/` files are QA-owned and were reverted |  |

---

## 9. Rows proposed for the ledgers — text only; **this session edited no ledger**

### 9.1 `docs/DECISION_LOG.md` (owner: the delegate, on the Product Owner's decision; reviewer: IVA)

The council's proposed row is adopted as drafted, with two amendments of mine: requirement ids `NFR-RES-01a`/`NFR-RES-01b` in place of `NFR-RES-01`, and the status-reconciliation finding kept **out** of it, because it needs no decision (§9.2).

> | D-0xx | 2026-09-08 | O-159: ADR-007 **regional deployment cell topology decided as amended** — the deployment cell is defined by the residency region it serves (venues are an attribute, not the definition; venue placement re-decided at Gate C on measured baselines); the deployment cell is the failure domain; the cross-cell list is **closed, explicit and directional** with exactly four items (audit replication out, audit anchor publication out to a principal outside the cell, portfolio roll-up as a read-only derived view that never decides, public trust set inbound as a distributed signed artefact); market data, FX, orders, commands, decisions, approvals, limits, leases and Kill Switch state never cross a deployment-cell boundary; **the audit witness lives outside the deployment cell it witnesses**, because a co-located witness turns a regional loss into an un-liftable platform halt; a tenant is not a deployment unit and may span cells with nothing authoritative across them; the term "deployment cell" is disambiguated from `JurisdictionCell`. **No cell plan, count, region, size, provider or capacity figure is decided; no deployment cell is provisioned; a deployment cell has no capacity because there is no deployment cell** (H-05, Q-11-1/O-66, D-043). Conditions C-007-1..C-007-10. This decision supplies **no reviewer signature**: the SRE Lead's review of NFR.md, CAPACITY_MODEL v0.2 and DR_PLAN v1.1, the Cloud Architect's review of CONTAINER_DIAGRAM v1.1 and of ADR-007 rev.1, the Privacy Lead's review of DATA_FLOWS v1.1 and the Independent Validation finding all remain **pending** (O-129) | Product Owner (D-039/D-040) · Council: **ARB recommends DECIDE WITH AMENDMENTS** (`docs/SESSIONS/COUNCIL_2026-09-08_arb_adr_007.md`), unanimous to amend, cloud-architect dissent-with-condition recorded verbatim, ARB chair's declared interest at §1 · Applied by the Enterprise Architect (`docs/SESSIONS/REVIEW_2026-09-08_adr_007_and_status.md`) · IVA: [Open] | Decide as proposed (rejected: undefined unit "venue cluster", witness blast-radius defect, falsified closed list, "cell" homonym under a dual-key control); replace (rejected: the invariant is sound and correctly relied on in five documents); do not decide (held as the fallback if the amendment is declined) | [Source: 03] / [Committee] / [Open: H-05, Q-11-1/O-66, O-18, O-54, O-160, O-161, R-05] | ADR-007 rev.1; NFR v1.1 (NFR-SCL-01/02, NFR-RES-01a/01b, NFR-DR-01); DR_PLAN v1.2; CONTAINER_DIAGRAM v1.2; CAPACITY_MODEL v0.3; DATA_FLOWS v1.2; `infra/iac/README.md`; RAID O-159, O-163 |

**Status line for the delegate to write into `docs/ADRs/ADR-007.md`, only after that entry exists** (it is deliberately not in the ADR today):

> **Status:** Accepted as a constraint set with conditions (D-0xx, 2026-09-08; conditions C-007-1..C-007-10 of `docs/SESSIONS/COUNCIL_2026-09-08_arb_adr_007.md`). **No cell plan, cell count, region, size, provider or capacity figure is decided by this ADR** — those remain a human act under H-05, Q-11-1 and D-043. Venue placement is re-decided at Gate C on measured baselines (item 3).

### 9.2 Whether the status reconciliation needs a decision row [Committee]

**My view: no, and it should not have one.** Correcting a status line to agree with an existing decision is a *record* act, not a decision; giving it a D-number would create a decision about a decision and invite the belief that D-060 and D-062 needed a second acceptance. If the Product Owner prefers a trace, the honest form is a one-line note appended to the existing D-060, D-062 and D-049 evidence columns ("ADR status line corrected 2026-09-08, commit `<hash>`"), which the delegate owns.

### 9.3 `docs/RAID_LOG.md` (owner: Program Orchestrator). Ids are **proposed**; O-167 is the highest in use [Verified]

| Proposed id | Type | Text | Owner | Needed by |
|---|---|---|---|---|
| **O-159** (update) | Issue | Append: "ARB convened 2026-09-08; recommendation DECIDE WITH AMENDMENTS with conditions C-007-1..C-007-10. **Amended text applied to `docs/ADRs/ADR-007.md` on 2026-09-08 by the Enterprise Architect** (`docs/SESSIONS/REVIEW_2026-09-08_adr_007_and_status.md`); status remains `Proposed` pending the decision entry. Cloud Architect review pending. Closes on the decision **and** on steps 4–10 of the council's change order" | Enterprise Architect, Cloud Architect | B |
| **O-163** (update) | Gap | Append: "**Closed on the edit side 2026-09-08**: `docs/NFR.md` v1.1 replaces NFR-SCL-01, adds NFR-SCL-02, splits NFR-RES-01 into 01a/01b and amends NFR-DR-01; the stateful dimensions are **named with register ids, not counted** — this row's four and CAPACITY_MODEL §6's four were different sets whose union is six. Row stays open until the SRE Lead's review (O-129) and until CAPACITY_MODEL §6's mismatch note is closed against the amended text" | Enterprise Architect, SRE Lead | B |
| **O-168** (new) | Gap | "'Cell' has two incompatible meanings, one of them a typed, tested code object under a **dual-key** control: the **deployment cell** (ADR-007, CAPACITY_MODEL, DR_PLAN, `infra/iac`) and the **`JurisdictionCell`** (`compliance_engine.eligibility.find_cell`; NFR-GLO-01, D-050; THREAT_MODEL T-53/T-57). Disambiguated in ADR-007 and `docs/NFR.md` on 2026-09-08; **owed** in CAPACITY_MODEL, DR_PLAN, CONTAINER_DIAGRAM, DATA_FLOWS, `infra/iac/README.md` and `docs/PRIVACY_IMPACT.md` rows 13–14, which say 'per cell' without saying which. C-007-1" | Cloud Architect, Data Architect, Privacy Lead | B |
| **O-169** (new) | Issue | "**ADR status lines and the decision log disagreed.** Of twenty ADRs, eighteen status lines began `Proposed` (seventeen plainly, plus ADR-017's hybrid). ADR-017, ADR-019 and ADR-020 were corrected on 2026-09-08 against D-049, D-060 and D-062; **fifteen remain `Proposed` with no decision-log entry to cite**, including **ADR-001 (three-plane topology)**, the foundation of NFR-SEC-01, of every network policy, of `scripts/check_network_policies.py` and of TC-NET-001..004 — the four passing plane tests conform to a proposal. Each now carries a one-line undecided note. **What is owed is the recommendations themselves** (councils listed at REVIEW §4.1), and a documentation lint that fails when a status line names a `D-0xx` that does not exist or claims acceptance without one" | Enterprise Architect, Program Orchestrator, QA Lead | B |
| **O-170** (new) | Gap | "**ADR-011's Decision is superseded and the ADR was never amended.** D-053 moved tool-registry signing to an asymmetric signature with a public trust set and D-060 accepted ADR-019 for dev/sim; ADR-011 still reads as the HMAC decision, and the 'ADR-011 amendment' named in D-053's evidence column does not exist. A reader of ADR-011 alone is misled" | Security Architect / MCP Security Agent (Security & Privacy Board), Enterprise Architect | B |
| **O-171** (new) | Gap | "**ADR-021 (FX as a deterministic decision input) has no file in `docs/ADRs/`.** D-064 accepted the E04 build and calls ADR-021 'proposed (in the packet)'; ADR-007 item 4 and DATA_FLOWS cite it. A cross-reference a reader cannot follow" | Enterprise Architect, Backend Lead (E04) | B |
| **O-172** (new) | Risk | "**A witness co-located with the deployment cell it witnesses converts a regional loss into a platform-wide halt that cannot honestly be lifted.** ADR-020 makes a missing or stale anchor fail closed with `killswitch_platform` (O-137); O-134 and O-165 forbid disabling the check. Remedy: ADR-007 item 5 (applied 2026-09-08) plus DR_PLAN v1.2 (C-007-4). **No drill and no measurement exists**" | Security Architect, Cloud Architect, SRE Lead | B (design) / C (drill) |
| **O-173** (new) | Open item | "The cross-cell portfolio roll-up moves position data across a residency boundary. Lawfulness is per jurisdiction and belongs to the Privacy Lead and the Compliance & Legal Committee, not the ARB. No roll-up carrier may be designed before it is answered (C-007-6); the carrier itself is [Open: R-05]" | Privacy Lead, Compliance & Legal Committee | C |
| **O-158** (update) | Gap | Append: "Restated 2026-09-08 in ADR-004 itself: the file now says in its own header that D-056 decided O-13 and that **rev.2 is owed before a status question is answerable**" | Enterprise Architect | B |

*If the Program Orchestrator allocates different ids, the references `[Open: O-168..O-173 proposed]` written into `docs/ADRs/` and `docs/NFR.md` must be updated with them; they are marked "proposed" in the text for that reason [Committee].*

### 9.4 `docs/REQUIREMENTS_TRACEABILITY.md` (owner: Program Orchestrator; reviewer: IVA)

Row 37 must be re-keyed and row 39 split. Requirement → architecture → owner → control → test → evidence → gate:

| Requirement | Architecture | Owner | Control | Test | Evidence | Gate |
|---|---|---|---|---|---|---|
| **NFR-RES-01a** | ADR-002 lease + fencing token; ADR-018 store-allocated sequence | Backend Lead | one active executor per account; a stale token is refused; the token strictly increases across preemption, expiry and restart | TC-EX-003, TC-EX-004, TC-DUR-002, TC-EX-011 | `docs/SESSIONS/BUILD_E07_2026-09-08_durable_stores.md`; AEI row 37 | **C** [Open: O-117 — two connections in one process stand in for two processes] |
| **NFR-RES-01b** | ADR-007 items 4, 5, 6 | Cloud Architect | closed directional cross-cell list; witness outside the cell; one cell per account at a time | **none — and none can exist until a second deployment cell is provisioned** | a DR drill, owed with O-18; no evidence today | **E** [Open: O-18, H-05, A-6, B-15] |
| **NFR-SCL-01** | ADR-018, D-056, ADR-020, ADR-005 | Enterprise Architect (requirement) / Cloud Architect (shape) | no request state in the service tier; a named unit of scale and partition key per store; scale by partition | **none** — structure only; no scaler, admission control or threshold exists [Open: O-162] | `docs/CAPACITY_MODEL.md` §1, §3, §4, §7 — **a structure reference, never a threshold** | **B** (structure) / C (baselines) / E (targets) [Open: O-03] |
| **NFR-SCL-02** | CAPACITY_MODEL §1 | Data Architect | partition keys declared once and not restated | **none** — a drift check would be the honest test | CAPACITY_MODEL §1 | **B** |
| **NFR-DR-01** | ADR-007 item 5; ADR-018; ADR-020 | Cloud Architect / SRE Lead | the standby reaches an anchor directory that survived the failed cell; two O(n) verifications on the start-up path | **none** | `docs/DR_PLAN.md` v1.2 (owed, C-007-4) | **E** [Open: O-18, O-111, O-133, O-156, O-167] |

### 9.5 `docs/AUDIT_EVIDENCE_INDEX.md` (owner: Program Orchestrator)

| Gate | Item | Type | Reference | Owner | Reviewer | Date |
|---|---|---|---|---|---|---|
| B | ADR-007 rev.1 — the deployment cell as failure and residency domain, amended per the ARB | ADR + session packet | `docs/ADRs/ADR-007.md`; `docs/SESSIONS/REVIEW_2026-09-08_adr_007_and_status.md`; council packet `COUNCIL_2026-09-08_arb_adr_007.md` | Enterprise Architect | **Cloud Architect (pending)** | 2026-09-08 |
| B | NFR v1.1 — NFR-SCL-01 replaced, NFR-SCL-02 added, NFR-RES-01 split, NFR-DR-01 amended (O-163, C-007-7) | requirements document | `docs/NFR.md` | Enterprise Architect | **SRE Lead (pending)** | 2026-09-08 |
| B | ADR status reconciliation against the decision log (O-169) | record correction | `docs/ADRs/` (twenty files); §4 of this packet | Enterprise Architect | **Independent Validation Agent (pending)** | 2026-09-08 |

**Rule I applied to these rows**: the reviewer column stays **pending** and is filled by the reviewer, not by me. A row whose reviewer column I filled myself would be self-certification [Source: 00, 13].

---

## 10. Assumptions, confidence, provenance

- **Assumptions.** The tree at `202378f` is the repository of record for this session; D-039, D-040, D-043, D-049..D-066 stand as recorded; `.claude/agents/roster.json` at this commit is the write scope of record; the council packet's facts F-1..F-16 are its own and were re-checked here only where this packet re-states them [Committee].
- **Confidence.** **High** that no decision-log entry accepts ADR-007, ADR-001 or the other thirteen listed as owed, and that D-049, D-060 and D-062 accept ADR-017, ADR-019 and ADR-020 — each was read in the ledger [Verified]. **High** that the ADR status count is eighteen-of-twenty before and fifteen-of-twenty after, by the method stated in §4. **High** that the six stateful dimensions exist and that the two prior lists of "four" disagree. **Medium-high** on the residency-first definition — it follows from D-056, NFR-PRV-01 and NFR-GLO-01 but has never met a second deployment cell, because none exists. **Medium** that my reading of D-004/D-042 (they ratify the *act of proposing* ADR-001..008, not the ADRs) is the only available reading; it is the conservative one, and it is exactly the kind of question the IVA should settle [Open]. **None** on any capacity, latency, cost, provider, broker or venue figure: none is stated, implied or derivable from anything I wrote.
- **Provenance.** [Source: 00, 03, 04, 06, 10, 13] as transmitted by the repository artefacts; [Committee] for the ARB packet's reasoning and for mine; [Verified] only for file reads and command output quoted here; [Open] items carry their register ids.
- **Independence.** Author of the amendment and of the NFR edit: Enterprise Architect (me), who owns both files. Reviewers, in different lines: Cloud Architect (ADR-007), SRE Lead (NFR), Independent Validation Agent (the status reconciliation). Approver: **the Product Owner** (D-039/D-040). **I approved nothing, signed nothing and recorded no decision in any ledger. `docs/RAID_LOG.md`, `docs/DECISION_LOG.md`, `docs/REQUIREMENTS_TRACEABILITY.md` and `docs/AUDIT_EVIDENCE_INDEX.md` were read and not edited** [Source: 13].

---

## 11. Concerns for the Product Owner

- **PO-1 The amended ADR-007 is now in the file, and it is still a proposal — deliberately, and I need you to see why that is not fence-sitting.** I applied the board's text as its author, including the sentence the Cloud Architect made his support conditional on: *this ADR decides no cell plan; no deployment cell is provisioned; a deployment cell has no capacity because there is no deployment cell.* It opens Decision item 8, not a footnote. What I did **not** do is write the proposed "Accepted…" wording anywhere into the ADR, even as a labelled suggestion, because the third task you gave me exists precisely because a reader cannot tell a decision from a status line. The wording is waiting for the delegate in §9.1 of this packet. **You decide; I apply.**

- **PO-2 The status reconciliation found the record in worse shape than the count that prompted it, and the direction of the error matters.** The council said sixteen of twenty ADRs read `Proposed`; my brief said nineteen; the files say **eighteen** — seventeen plainly, plus ADR-017's hybrid. Three status lines have now been corrected against decisions that already existed (ADR-017 → D-049, ADR-019 → D-060, ADR-020 → D-062). **Fifteen remain undecided, and each now says so in its own first lines.** Among them is **ADR-001, the three-plane topology**: NFR-SEC-01, every network policy, the policy checker and TC-NET-001..004 are written against a proposal, and the four green plane tests in every packet this week test conformance to a proposal. I did not change it, because there is no decision to cite and inventing one is the failure mode I was asked to remove. **What is owed is not a status edit — it is the ARB and the Security & Privacy Board actually recommending on ADR-001, and you deciding.** It is one meeting, and it is a larger part of the Gate B pack than ADR-007 was.

- **PO-3 Two ADRs are worse than undecided: they are actively misleading, and both are cited by the Gate B evidence set.** **ADR-011** still reads as the HMAC tool-registry decision, although D-053 moved registry signing to an asymmetric signature and D-060 accepted ADR-019; the "ADR-011 amendment" that D-053's own evidence column names **does not exist**. **ADR-004** still reads as a one-line deferral although D-056 decided the market-data storage architecture; its rev.2 is mine and is owed (O-158). A reader of either file alone gets a wrong answer, and neither is fixed by a status line. I have annotated both rather than quietly rewriting them, because rewriting a superseded decision hides that it was superseded. I have opened O-170 and restated O-158.

- **PO-4 The NFR change is a correction to a requirement, not a relaxation of a control, and I want to be precise about what it exposes.** "Stateless services" was written before this platform had durable state. It now has six named stateful dimensions — the control store, the market-data store, the audit store, the anchor directory, the MCP journals and an **undeployed** bus — and those stores are exactly why the platform can fail closed across a restart, which you accepted deliberately in D-058 and D-062. But the Security Architect is right that the word was doing security work by accident: people read "stateless" as *nothing persists, so nothing leaks*, and in fact **four of these stores hold Confidential data at rest with no file permissions, no backup, no residency and no retention today**. That was true yesterday too; the old wording hid it. The new text says it in the requirement itself. I also stopped the counting: the RAID row and the capacity model each said "four" and meant different sets whose union is six, so the requirement now **names** each dimension with its register id.

- **PO-5 One defect in the old text could have turned a regional failure into a permanent halt, and the fix is now in the Decision.** If the anchor directory sits inside the deployment cell it witnesses, losing that region destroys the audited party and its witness together; the standby cannot verify the chain; restore-then-verify is the only recovery (O-134, O-165) and there is deliberately no flag to disable the check. The honest outcome is a platform-wide halt nobody can lift without destroying the evidence. ADR-007 item 5 now puts the witness outside the cell as a **decision item, not a runbook line**, because a runbook is not a control. It follows from ADR-020's own text and needs no provisioned cell to be true. **What it still needs is DR_PLAN v1.2 (C-007-4), which is the Cloud Architect's, and a drill, which nobody can run.** I have opened O-172.

- **PO-6 Nothing I wrote creates, authorises or measures anything.** No capacity, latency, throughput, cost, price, provider, broker or venue figure appears in the amended ADR or in the NFR, and none can be derived from them. NFR-SCL-01's target column points at the capacity model as a **structure**, never a threshold; NFR-RES-01b and NFR-DR-01 carry **no test and no figure** and gate at E. `make all` is green — 222 tests — and it evidences nothing whatever about a deployment cell, because there is no cell object to test, no manifest to check and no environment to check it in.

- **PO-7 This packet supplies no reviewer signature, and I would rather say so than let you infer it from a green build.** The Cloud Architect has not reviewed ADR-007 rev.1; the SRE Lead has not reviewed `docs/NFR.md` v1.1 — nor v1.0, nor the capacity model, nor the DR plan; the Independent Validation Agent has not looked at the status reconciliation, and one of its findings ought to be whether my reading of D-004/D-042 is right, because if D-042's ratification does reach ADR-001..008 then eight of my "owed" rows become status edits instead of council meetings. **I am the author of every file this session touched, so I am disqualified from reviewing any of it.** Deciding a foundation does not review the buildings, and applying an amendment does not approve it.

- **PO-8 The last thing this leaves you, plainly.** Six documents still have to change before the Gate B pack is internally consistent, and only two of them were mine: DR_PLAN v1.2, CAPACITY_MODEL v0.3 and `infra/iac/README.md` (Cloud Architect), DATA_FLOWS v1.2 (Data Architect), PRIVACY_IMPACT rows 13–14 (Privacy Lead) and CONTAINER_DIAGRAM v1.2 (mine — it draws planes and never draws the deployment-cell frame at all, so it cannot show the amended boundary; that is a version, not an erratum, and I did not fake it into this session). The RTM needs row 37 re-keyed and row 39 split, which is the Program Orchestrator's. **If you decline the amended text, the council's recorded fallback is DO NOT DECIDE YET and Gate B is not convened** — and I would support that over deciding the old sentence, because deciding "one cell per venue cluster" would convert a provisioning rule with no evidence, no definition and no owner into a decision of record.
