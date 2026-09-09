# DR_PLAN

| Owner | Reviewer (different line) | Approving body | First gate | Status |
|---|---|---|---|---|
| Cloud Architect | SRE Lead | ARB, Executive Steering | E | **Draft v1.2, 2026-09-09 — the corrective version D-067 required** (docs/DECISION_LOG.md:75). The SRE Lead reviewed v1.1 **SIGN WITH FINDINGS**: two blocking (D-01 order of restoration, D-02 who holds which credential) and four non-blocking (D-03..D-06), docs/SESSIONS/REVIEW_2026-09-08_capacity_sre.md §3. Corrections applied by the owner; **re-review by the SRE Lead pending**; **Independent Validation pending**; **Product Owner decision pending (D-039)**. **Not accepted**, and no agent records an approval [Source: 13] |

**No RPO or RTO figure is stated or implied anywhere in this document, and none is proposed here** [Source: 00] [Open: O-18].

**What changed in v1.2, and why [Committee].** This version answers the five findings the SRE Lead returned on v1.1 in docs/SESSIONS/REVIEW_2026-09-08_capacity_sre.md §3, and D-067's ruling that each author issues the corrective version his reviewer named before the AUDIT_EVIDENCE_INDEX rows are filled and before Gate B is convened (docs/DECISION_LOG.md:75). **None of the five needed a number and none was invented.** (a) **D-01, blocking** — step 2 of the cell-loss order was the single word "audit" for what is two stores with an ordering constraint between them, whose most natural mistake halts the platform being recovered; it is now an ordered unit with the length relationship stated (§3). (b) **D-02, blocking** — "two-person restore" is now connected to the property the second person protects, the anchor directory is named as its own restore unit with its own credential, and the case where one person held both is required to be stated rather than left quietly true (§4). (c) **D-03** — "verify chain" named one word for two different checks; the plan now says which, and requires both (§3 step 2d, §5). (d) **D-04 / F-11** — the drill sentence said "the history length"; there are three lengths and they grow at different rates, so the record requirement is now the triple plus the phase split (§6). (e) **D-05** — the bus row is tagged [Open: R-05] as the capacity model tags its bus row (§5). (f) **D-06** — restore units are now named, including the statement that identity and control state are **one** unit today (§2). Two behaviours that did not exist when v1.1 was written are also recorded, because a DR plan that describes the wrong system is worse than a short one: the audit store now refuses to open when a witness it recorded is gone (D-068), and composition asks the published witness at start-up (D-066). Nothing here is accepted and nothing here is a target.

---

## 1. Scope and the dependency that blocks O-18

**Scope:** regional deployment-cell loss, data-store corruption, vault loss, bus loss. RPO/RTO candidates [Open: O-18] are set after drill baselines, at Gate E, with business approval — never from this document [Source: 10].

**"Cell" here means a deployment cell** (ADR-007, `Status: Proposed`, docs/ADRs/ADR-007.md:3), not a `JurisdictionCell`; the two are unrelated and neither implies the other [Source: docs/NFR.md:38]. Every "per cell" statement below is conditional on ADR-007 being decided as proposed; ADR-007 rev.1 is recorded in D-069 (docs/DECISION_LOG.md:77) as the version to decide on, **not** as the decision [Open: ADR-007 status].

**Why O-18 cannot be answered yet [Committee] — added 2026-09-08 with CAPACITY_MODEL §4a, carried forward.** Two verifications are unconditional on process start and both are linear in history: the control store replays its uncompacted journal at open (ADR-018, O(journal), O-111 — `SqliteStore.verify()` reads the whole journal, libs/core/rtcore/store.py:358) and the audit store verifies its whole chain at open (ADR-020, O(events), O-133 — services/audit/audit_service/store.py:265), with the anchor file re-verified in full on every read *and* on every publication (services/audit/audit_service/anchor.py:164, 190-209). Both are correct fail-closed design and neither may be weakened for speed — recovery is *restore then verify*, and disabling the check is never the fix (O-134); there is deliberately no flag that disables either (D-066, O-165). Both are also **O(n) in memory, not only in time**: the control-store verify materialises the journal (store.py:358) and the audit store keeps every event resident for the life of the process (services/audit/audit_service/store.py:235, 278-282), and no `ResourceQuota` or `LimitRange` exists anywhere to size that against (O-160). A restore too large to fit in memory does not recover slowly; it does not recover at all. Consequently: the verification step of §3 is an unmeasured O(n) operation on the recovery-time path; a standby cell inherits **both** verifications, not one; and no RPO/RTO candidate may be proposed until they are measured against **stated** journal, chain and anchor lengths. **A drill on a fresh cell measures the best case and will be quoted as the general case.** O-18 is blocked on O-111, O-133, O-156 and a drill — not merely on a human choosing a number [Open: O-18, O-111, O-133, O-156].

## 2. Restore units, and which artefacts belong to which [Committee] — D-06

A reader who plans a partial restore needs to know what is separable. Today, less is separable than the order of restoration implies.

| Restore unit | Artefacts | Principal / credential | State today |
|---|---|---|---|
| Identity and control state — **one unit today** | the control-state store file (lease, outbox/inbox, gateway indexes, Kill Switch activations) **and** the MCP revocation and nonce journals | the platform's own store identity | the revocation and nonce journals default into the **same** `store_dir` as the control store (apps/web/web_bff/platform.py:793-794), deliberately, so that a restored activation is never paired with forgotten revocations (O-118). "Identity/vault" and "control" are therefore **not separable restore units today**; O-118 separates them from shadow, and O-136 requires the control and audit stores to have different owners and different backup schedules from shadow [Open: O-118, O-136] |
| Audit trail | the audit store file, on its own store seam | the audit workload | separate from the control store by design, never one file (ADR-020, D-062) |
| **External witness** | the anchor directory (`audit_anchors.jsonl`, services/audit/audit_service/anchor.py:31) | **a principal the audit workload cannot assume** | **[Open: O-54] — it does not exist.** `FileAnchorPublisher` stamps `principal="audit-anchor-publisher"` into each record (services/audit/audit_service/anchor.py:33, 144), which is a **label written by the same process**, not a separate deployment identity with its own write credential. Until O-54 is a real identity, the two-principal property of §4 is modelled, not evidenced |
| Vault / KMS | broker credentials and key material | vault/HSM identity | **no vault, HSM or KMS is provisioned in any environment**; provisioning is a human act [Open: H-05] (docs/CAPACITY_MODEL.md §1a) |
| Market-data store | bitemporal store plus archive, per cell | per-cell data identity | per cell, not replicated cross-cell (ADR-007); no manifest exists [Open: H-05] |

**No deployment cell is provisioned**, so every restore below is a procedure, not a rehearsed capability: no cloud account, region, cluster, storage class, disk class, bus, vault or egress gateway is chosen or created [Open: H-05, A-6, B-15] (docs/CAPACITY_MODEL.md §1a).

## 3. Cell loss — the order of restoration [Committee] — D-01 (blocking finding, closed here)

Strategy: active/standby deployment cell; audit replicated cross-cell; portfolio roll-up. The order matters more than the strategy, because **the most natural error in step 2 halts the platform being recovered.**

1. **Identity / vault** — one unit with control state today (§2). Do not plan a partial restore across that boundary.
2. **Audit trail and its witness, as one ordered unit.** Not "audit": two stores with a length relationship between them.
   1. **Restore the audit store first.**
   2. **Confirm its length is at least the length of the last published anchor, before the anchor directory is attached.** A chain shorter than the surviving witness verifies as `AUD-CHAIN-TRUNCATED` (services/audit/audit_service/store.py:774-782). That reason is **not** an anchor reason (store.py:56), so it raises **`audit.chain_verification_failed`**, whose catalogued auto-action is **`killswitch_platform`** (docs/ALERT_CATALOG.md:20, observability/alerts.yaml:16) — a platform-wide halt, during a recovery, caused by the platform's own correct control. Since D-066 the composition root runs that published verification **at start-up**, after the auto-actions are bound (apps/web/web_bff/platform.py:1421-1422), so the halt arrives at boot rather than at the next scheduled publication. The Kill Switch on a chain failure is inherited rather than deliberately chosen and is still owed a Trading Risk Committee confirmation [Open: O-137].
   3. **Attach or restore the anchor directory — by the witness's own principal, never by the audit workload's identity** (§4) [Open: O-54].
   4. **Run an explicit published verification** (`AuditStore.verify()`, whose `published` argument defaults to true, store.py:721-745). This is **not** what start-up did: the open-time verification is chain-only (`verify(published=False)`, store.py:265). A process that started is evidence of the chain check and **is not evidence that the witness is intact** (D-03).
   5. **Only then seal.** Never publish over a chain you have not verified. The design refuses the tempting shortcuts: a broken anchor chain refuses publication (anchor.py:208-209), a rollback or a fork at the same length is refused (anchor.py:211-215), an ordinary seal may not create the first anchor for a non-empty chain (`AUD-SEAL-UNWITNESSED`, store.py:63, 422-429), and a seal contradicting a head this store recorded witnessing is refused (`AUD-SEAL-BELOW-FLOOR`, store.py:62, 554-571).
   6. **If the witness is genuinely gone, the store does not open at all.** A store whose own records name a witness the anchor store no longer holds (or cannot read) raises `WitnessLostError` after alerting `audit.anchor_missing` with reason `AUD-WITNESS-LOST` / `AUD-WITNESS-UNREADABLE`, and **writes nothing** — a refusal, not a Kill Switch, because a Kill Switch activation writes to the store under suspicion (store.py:271, 592-632; D-068, docs/DECISION_LOG.md:76). Recovery is the named, attested operator act `AuditStore.reestablish(...)`, which is refused unless the witness really is absent and the attestation names the actor, the reason, a correlation id and the chain's exact length, head hash and last recorded anchor sequence (store.py:634-706). It is never automatic, it writes its own audit row, and **there is no flag that disables the check** (D-066, O-165).
   7. **Restore the control store and the audit store as a matched set.** The control store's journal head is written into the audit chain on every commit touching a control invariant and is checked at open (`JournalAnchor.start()`, libs/core/rtcore/journal_anchor.py:314-338; ADR-018 amendment 1, D-066), so a control store restored against an audit chain that does not carry its head is refused as `StoreIntegrityError`. Runbook: docs/INCIDENT_RESPONSE.md RB-13.
3. **Control plane.**
4. **Execution plane — Supervised mode only.** Recovery is not transparent to the account: the control-plane intent tracker and the decision index are still in memory, so after a restart the permission oracle refuses every pre-restart intent as unknown to the control plane (fail closed, TC-EX-011) and an in-flight order can be **cancelled but not resumed** (docs/ADRs/ADR-018.md:31). An RTO that does not say what is lost is half an objective [Committee].
5. **Analytics plane.**

**Evidence:** drill report per §6. **[Open: O-18]** — this order has never been executed; no drill has run, and no deployment cell exists to run one in [Open: H-05].

## 4. Two-person restore, and what the second person is protecting [Committee] — D-02 (blocking finding, closed here)

ADR-020's guarantee is that truncating the audit trail requires write access to **two stores owned by two principals** (O-54). **A recovery performed by one operator holding both credentials dissolves that guarantee for exactly the window an investigation will later care most about** — and a disaster is the one routine occasion on which that concentration looks reasonable.

Therefore, for any restore that touches the audit trail:

- the **anchor directory is its own restore unit with its own credential** (§2) and is restored by an identity that is **not** the identity restoring the audit store;
- **both identities are recorded in the recovery record**, by name, with the times they acted;
- **if one person held both credentials, the recovery record must say so**, in the record itself and not in a covering note: the restored window is then **not independently witnessed**, and Internal Audit is told rather than left to discover it;
- the acts that re-establish or re-seal a witness are attested operator acts, so the actor and reason are already inside the audit chain (§3 step 2f, store.py:634-706) — the recovery record must agree with them.

**Today the two principals are one** [Open: O-54]: the anchor principal is a string written by the publishing process (anchor.py:33, 144), not an identity with its own credential. Until O-54 is closed, two-person restore is a **procedural control over a single credential**, and the recovery record must state that too. Two-person restore is not a formality here; it is the control [Committee].

## 5. Scenarios

| Scenario | Strategy | Order of restoration | Evidence |
|---|---|---|---|
| **Deployment-cell loss** | active/standby cell; audit replicated cross-cell; portfolio roll-up (ADR-007, `Proposed`) | **§3 in full** — 1 identity/vault (one unit with control state today, §2) · 2 audit trail **then** witness, as the ordered unit of §3 step 2 · 3 control plane · 4 execution, Supervised mode, in-flight intents not resumed · 5 analytics | drill report per §6 [Open: O-18, H-05] |
| **Audit store corruption** | restore from the last good copy and re-verify; never repair in place | **both verifications, named separately (D-03):** the open-time chain verification is automatic and refuses the process (`verify(published=False)`, store.py:265 → `AuditIntegrityError`); the **published** verification (chain *and* witness) happens only when something calls it (store.py:721-745). **The process starting is evidence of the first and never of the second.** Both must pass before trading reopens; then reconcile (§7) | verification log; docs/INCIDENT_RESPONSE.md RB-12, RB-13 |
| **Audit witness lost, stale or corrupt** | restore the anchor directory from the last good copy **by the anchor principal**; never re-anchor to "fix" it | if the store recorded a witness and it is gone, the store **refuses to open** (`WitnessLostError`, store.py:592-632; D-068) — recovery is the attested `reestablish` act. If the witness is merely absent, stale, broken or tail-removed at a published verify, the alert is `audit.anchor_missing`, S1, **auto-action `none`: a page, deliberately no automatic halt**, because the chain itself may be intact (docs/ALERT_CATALOG.md:19, observability/alerts.yaml:15) | incident correlation id and the four-reason verdict; docs/INCIDENT_RESPONSE.md RB-12 [Open: O-54] |
| **Vault / KMS loss** | HSM-backed key escrow per policy | rotate broker credentials post-restore | rotation log. **[Open: H-05]** — no vault, HSM or KMS is provisioned, no escrow exists and no broker credential exists in any environment; this row is design intent, not a rehearsed procedure |
| **Bus loss** | replay from outbox tables; consumers idempotent | **[Open: R-05] — there is no bus to lose and no replay to run.** A Kafka-compatible broker runs in the dev/sim compose stack (infra/docker-compose.yml), but `Outbox.relay(fn)` takes a callback and **no caller in the tree passes a producer** (services/oms/oms/outbox.py:55-67), so events stay in process after the outbox write. This row states the intended contract only (D-05) | dedupe evidence [Open: R-05] |

## 6. What a drill record must state before it may be cited [Committee] — D-04 / F-11

A drill that does not state what it ran against is not evidence, and the drill that settles O-18 is the most quotable artefact this programme will produce. The SRE Lead's requirement (docs/INCIDENT_RESPONSE.md RB-14, docs/SESSIONS/REVIEW_2026-09-08_capacity_sre.md §5) is adopted here as a **precondition of citation**, not a wish:

1. **Three history lengths, separately** — control-store journal rows, audit chain events, and anchor records. They grow at different rates (anchors accrue one per explicit seal plus one per `anchor_every` events), so the third is not derivable from the second, and a single "length" invites a reader to assume they move together.
2. **The wall-clock split across the phases**, never one total: restore · control-store `verify()` · audit-chain verify · anchor verify · reconciliation before reopen. A total conceals which phase to attack.
3. **Peak resident memory during each verification** — the term that decides whether a large restore completes at all (§1) [Open: O-156, O-160].
4. **What did not come back** — in-flight intents are cancelled, not resumed (§3 step 4, ADR-018:31).
5. **The environment and the disk class**, with the explicit statement that **none is chosen** [Open: H-05].
6. **Whether the cell was fresh or aged**, and if fresh, the sentence *"this is a best case and may not be quoted as a general recovery time"* in the record itself.
7. **Who acted** — the identities that restored the audit store and the anchor directory, and whether they were different people (§4).

The drill is run **twice**, once on a fresh cell and once on an aged one, for the reason in item 6. A drill record missing item 1, 2 or 6 produces no O-18 input [Committee].

## 7. Reopening trading

Reopening trading after DR requires **reconciliation against broker statements first** [Source: 03], **both audit verifications passed** (§5, D-03), **a Chief Risk Agent decision before any account resumes**, and **a two-person restore whose two identities are recorded** (§4). The resumption is itself a two-person act (docs/INCIDENT_RESPONSE.md RB-13 exit criteria). **Nothing in this document authorises an environment, promotes a mode, or states a recovery time** [Source: 00] [Open: O-18].

## 8. Change log [Committee]

| Version | Date | Change |
|---|---|---|
| v1.0 | earlier | scope, four scenarios, one-line order of restoration, closing two-person sentence |
| v1.1 | 2026-09-08 | the O(n) start-up dependency of O-18 recorded against CAPACITY_MODEL §4a; no figure stated |
| **v1.2** | **2026-09-09** | **the corrective version required by D-067** (docs/DECISION_LOG.md:75) after the SRE Lead's review of v1.1, docs/SESSIONS/REVIEW_2026-09-08_capacity_sre.md: D-01 (ordered restore of audit trail then witness, with the length relationship and the `killswitch_platform` hazard stated) and D-02 (the anchor directory as its own restore unit with its own credential, both identities recorded, the single-credential case disclosed) closed as **blocking**; D-03 (which verification), D-04 (three lengths and the phase split), D-05 (the bus row tagged [Open: R-05]) and D-06 (restore units, identity and control being one unit today) closed as non-blocking. Behaviours added because the tree changed after the review: witness-loss refusal at open (D-068) and the published verification at start-up (D-066). **No RPO, RTO or other figure added; every absent figure is [Open] with the act that would produce it** |

## 9. Review record (Definition of Done) [Committee] [Source: 13]

| Step | Role | State |
|---|---|---|
| Author / owner | Cloud Architect | **v1.2 written 2026-09-09**; author is never the sole approver |
| Reviewer (different line) | SRE Lead | reviewed v1.1 **SIGN WITH FINDINGS** (D-01..D-06), docs/SESSIONS/REVIEW_2026-09-08_capacity_sre.md; **re-review of v1.2 pending** — no owner signs for this row |
| Approving body (advisory) | ARB, Executive Steering | has not seen v1.2 |
| Independent validation | Independent Validation Agent | pending |
| Decision | **Product Owner (D-039)** | **pending** — agents never record an approval |
