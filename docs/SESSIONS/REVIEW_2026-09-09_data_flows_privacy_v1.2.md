# REVIEW 2026-09-09 — DATA_FLOWS v1.2: Privacy Lead re-review (2nd line) of the six blocking findings

| Session | Date | Author | Line | Status |
|---|---|---|---|---|
| Privacy Lead re-review of docs/DATA_FLOWS.md v1.2 (reviewer of record, D-067, C-DF-6 / D-061 (3) / O-106, O-129) | 2026-09-09 | privacy-lead agent | 2nd | **review packet — findings and proposals; no approval, no decision, no acceptance** |

> This packet reviews a document; it accepts nothing. DATA_FLOWS v1.2 remains **not accepted** until the human Product Owner records a decision (D-039) and the Security & Privacy Board records the classification half. I edited **one file — this packet**. I did not edit docs/DATA_FLOWS.md (I am the reviewer, not the author), nor docs/RAID_LOG.md, docs/DECISION_LOG.md, docs/REQUIREMENTS_TRACEABILITY.md, docs/AUDIT_EVIDENCE_INDEX.md or docs/PRIVACY_IMPACT.md in this session; rows for those files are **proposed** here for their owning roles. I state no jurisdiction's legal requirement anywhere: where the answer is law, I name the question and the seat that must answer it, and that seat is external counsel through a human act (H-04 scope H-25, O-10) [Committee]. Profit is an objective, never a promise [Source: 00]. Tags: **[Source: path:line]** or **[Source: NN]**, **[Committee]**, **[Open]**.

**Read at** `178da8b` (worktree head; `docs/DATA_FLOWS.md` v1.2 is committed there, one commit above `442cebd`, the commit at which v1.2 says it re-read the code). I re-read **every `path:line` v1.2 cites**, at that tree, and I report where the citation and the tree differ. Where v1.2 asserts a **negative** ("no code does X"), I did not accept a docstring as proof: I searched the tree for the thing said not to exist [Committee].

**Documents in flight I did not treat as settled.** docs/THREAT_MODEL.md, docs/SECURITY_PLAN.md, docs/CAPACITY_MODEL.md and docs/DR_PLAN.md are being edited by other roles in this same worktree as I write. I did not read them as evidence and I take no position that depends on them; where my v1.1 findings referenced them (NF-2, NF-4), I say so and leave them open [Committee].

---

## 1. Roles

| Function | Role | Line | In this session |
|---|---|---|---|
| Author / owner of DATA_FLOWS | Data Architect | 1st | wrote v1.2; not the reviewer, not the approver |
| **Reviewer of record** | **Privacy Lead (this agent)** | **2nd** | this packet; re-reviews PF-1..PF-6 against the tree, the four new open items, and what was deliberately not actioned; **does not approve security architecture** |
| Classification decision | Security & Privacy Board | 2nd | **pending** — every classification cell in §1/§2 of DATA_FLOWS is still a proposal |
| Register ids for the four new items | Program Orchestrator | — | **pending** — see §5 and §9; the items exist only inside the document today |
| Retention duty and record classes in law | Compliance Agent + Legal Agent + external counsel | 2nd/3rd | **pending** — O-09, O-10, H-04/H-25 |
| Decision | **human Product Owner** (D-039, D-067) | — | **pending** |
| Reviewer of *this* packet | Security Architect and the Board chair | 2nd | pending; I never self-certify [Source: 00, 13] |

## 2. Purpose, method, and what I read

**Purpose.** D-067 decided that each author issues the small corrective version their reviewer named, that the AUDIT_EVIDENCE_INDEX rows are not filled until those versions exist, and that Gate B is not convened before them [Source: docs/DECISION_LOG.md:75]. v1.2 is the Data Architect's answer on DATA_FLOWS. This packet answers one question: **is each of my six blocking findings actually corrected in the tree's terms, or has one unevidenced claim been swapped for another?**

**Method.** For each of PF-1..PF-6: (a) restate the finding; (b) read the new cell; (c) open every `path:line` it cites and check the tree says what the cell claims; (d) test the *negatives* independently by search, because an absence cannot be proved by a docstring; (e) look for anything the new text asserts that I did not ask for and that is not true.

**Read.** docs/DATA_FLOWS.md v1.2 (§0, §1 all 22 rows, §2, §3, §4, §5.1, §6, §7); my own docs/SESSIONS/REVIEW_2026-09-08_data_flows_privacy.md (§3.1 PF-1..PF-6, §3.2 NF-1..NF-15, F-22, F-23, §5, §6, §7, §9); docs/DECISION_LOG.md D-063, D-066, D-067; docs/RAID_LOG.md (O-09, O-54, O-55, O-106, O-111, O-118, O-128, O-129, O-135, O-137, O-156, O-160..O-169); docs/MISSING_ACTIONS.md (H-05); docs/PRIVACY_IMPACT.md (my own draft v1.1, read as the object of a citation, not edited); docs/TEST_CASES/TC-OB.md; docs/SESSIONS/REVIEW_2026-09-08_architecture_docs_v1.1.md (RD-1). Code at `178da8b`: `libs/core/rtcore/store.py`; `services/audit/audit_service/store.py`, `anchor.py`, `reestablish.py`; `services/compliance/compliance_engine/retention.py`; `apps/web/web_bff/platform.py`, `app.py`; `apps/cli/rt365_cli/main.py`; `observability/rtobs/logging.py`; `mcp/servers/mcp_servers/tools.py`, `revocation.py`, `identity.py`; `services/identity/identity_service/accounts.py`; `libs/core/rtcore/schemas/order.py`; `test/quartets/test_tc_cp_eligibility.py`, `test_tc_aud_audit.py` [Committee].

---

## 3. Verdict — **SIGN WITH FINDINGS** (one residual blocking, narrow)

**In one paragraph, for a non-specialist.** v1.2 is a real correction and not a cosmetic one. I opened every file and line it cites and the tree says what the document now says: the legal-hold clause has been taken out of the audit trail's controls and replaced with a plain statement that no hold, retention or deletion path exists there, with the unwired decision helper described exactly as it is; "no PII" is gone from both rows and replaced with the customer-identifying formula I asked for; the telemetry control now states the filter's pattern list *and* its deliberate limit; the journal row now says that deleting a row does not erase the value and that the store cannot be compacted without refusing to open; the MCP journals are reclassified as Personal (actor id); and the anchor row withdraws "no identifier", names the publisher principal and the caller-supplied correlation id, and says plainly that no residency map exists and that my own PRIVACY_IMPACT is an unreviewed draft. **Six of six corrections verified at the file and line cited.** The scope discipline is also right: the diff against v1.1 touches only the six rows, the two §2 rows they imply, the §4 bullet, and the change/review records — nothing else was quietly edited. **One thing still blocks, and it is one clause.** DF-22 now states the constraint I asked for — the seal correlation id must be system-generated — and supports it with "the two publications the platform makes for itself are already system-generated" and "no shipped route or CLI calls `seal()`". There is a **third** publication path: the attested witness re-establishment publishes an anchor carrying a correlation id **typed by a named human operator during an incident** [Source: services/audit/audit_service/store.py:699; services/audit/audit_service/reestablish.py:106-119]. That is the one path where a person is most likely to paste the incident's own request correlation id into a store we deliberately hold outside our own systems, and both the DF-22 constraint and the §6 open item are scoped to `seal()` only, so an implementer who enforces exactly what the document says will leave it open. **Action:** one errata clause in DF-22 and in its §6 row (RF-1 below); everything else I found this round is non-blocking and is carried as residual items and proposed register rows. Nothing here authorises anything beyond dev/sim, and no flow in this document is evidence for a deployed environment [Committee] [Source: 00, 12].

### 3.1 Residual blocking finding (must be corrected before the Product Owner records acceptance)

| # | Where | What v1.2 says | What the tree says | What would clear it |
|---|---|---|---|---|
| **RF-1** | DF-22 Controls; §6 row "new in v1.2, no register id yet (PF-6 ii)" | "the two publications the platform makes for itself are already system-generated (`anchor:genesis`, `anchor:scheduled:<n>`) … and no shipped route or CLI calls `seal()` in this tree"; the constraint and the open item are both written about **`AuditStore.seal()`** | Both cited facts are true [Source: services/audit/audit_service/store.py:275, 346, 394]. But there is a **third** path that writes an `AnchorRecord` into `audit_anchors.jsonl`: `AuditStore._reestablish` publishes with `correlation_id=attestation.correlation_id` [Source: services/audit/audit_service/store.py:699], where `WitnessAttestation.correlation_id` is a free string supplied by a **named human operator** and only checked for non-emptiness [Source: services/audit/audit_service/store.py:194-199, 670]. Its entry point `reestablish_witness` is shipped product code, not a test helper [Source: services/audit/audit_service/reestablish.py:106-119] (its only callers today are tests [Source: test/quartets/test_tc_aud_audit.py:931, 941, 954, 1078, 1118]). So the enumeration "the two publications the platform makes for itself" is incomplete, and the constraint as written does not bind the one path where a human types the value | Replace the enumeration with three paths, and widen the constraint and the §6 item to: "**the correlation id written to the witness — on `AuditStore.seal()` and on `WitnessAttestation.correlation_id` in the attested re-establishment — must be system-generated and never derived from a customer request or session; nothing in the code refuses either today**" [Source: services/audit/audit_service/store.py:394, 699; services/audit/audit_service/reestablish.py:106-119]. This is a wording and scope fix, not a design change; any second reader can check it against those two cites, and it does not need a further full re-review from me |

### 3.2 Residual non-blocking findings (v1.2)

| # | Where | Finding |
|---|---|---|
| RF-2 | DF-08 Controls | The corrected cell says redaction is "applied to the message and to every extra field" (true [Source: observability/rtobs/logging.py:37, 42]) and, two clauses later, that "neither free-text fields nor any identifier that matches no pattern are covered". Read literally the two disagree: a free-text field **is** scanned, and an e-mail address inside it **is** replaced. The precise statement is "**every string is scanned; only what matches a pattern is removed, so an identifier or a free-text phrase that matches no pattern is emitted as written**". My own v1.1 wording carried the same looseness and I am correcting myself here too [Committee] |
| RF-3 | §3 against §1/§2 | v1.2 introduces three composite labels the classification scheme does not define: "**customer-identifying**" (DF-03, DF-05, §2), "**+ Personal (actor id)**" (DF-12, §2) and "**+ pseudonymous identifier and timing metadata**" (DF-22, §2). §3 still lists seven single classes and the Board's classification review is the next step. Either add the qualifiers to the §3 table with their handling consequence, or state that a cell may carry a base class plus a qualifier and what the qualifier obliges. A Board asked to decide a column should be given the vocabulary it is deciding in [Committee] |
| RF-4 | §6 row 3 (PF-5) | "no register id yet" is half-right: the free-text `reason` minimisation is genuinely new, but "neither MCP journal has a retention rule" is inside the scope of **O-09** — and the DF-12 row itself already tags that clause [Open: O-09] [Source: docs/RAID_LOG.md:17]. Cross-reference O-09 (and, for the erasure half, O-135) from the §6 row so the Program Orchestrator allocates one new id and does not open a duplicate |
| RF-5 | DF-07 and DF-22 Controls cells | Both cells now carry several sentences of *target* and *negative* narrative inside a column the document's own rule reserves for controls with a code path and a test id (§0, C-DF-1..C-DF-5). Nothing there is credited as a control — each is explicitly marked as a target or an absence with its [Open], so the rule is met in letter — but the audit row's controls are now hard to find in the prose around them. Recommend a "Targets and open items" sub-cell in the next full version, not now [Committee] |
| RF-6 | §4 bullets 1 and 2 | Bullet 1 (new in v1.2) is exactly right: residency is not answerable for any flow, and `Tenant.residency_region` is declared [Source: services/identity/identity_service/accounts.py:41-44] and set to `"sim"` [Source: apps/web/web_bff/platform.py:942] and read by no code (I searched: those two lines are the only occurrences outside `build/`). Bullet 2, unchanged from v1.1, still asserts in the present tense that "market data is stored in the tenant's regional cell … and there is no cross-cell market-data replication (D-056)". The contradiction is pre-existing, not introduced, but bullet 1 now makes it loud. Mark bullet 2 as a **target** of D-056, as I asked in my v1.1 §4 DF-01 row |
| RF-7 | header and §7 | The header and review record correctly say the Privacy Lead has **not** reviewed v1.2 — true when written, and now superseded by this packet. Whoever issues the next version should record "v1.2 re-reviewed 2026-09-09, SIGN WITH FINDINGS, one residual blocking (RF-1), packet docs/SESSIONS/REVIEW_2026-09-09_data_flows_privacy_v1.2.md". **I record no acceptance and no approval, and my signature is not one** [Source: 13] |

---

## 4. The six, re-checked at the file and line v1.2 cites

Legend: **pass** = the correction is made and every citation supporting it says in the tree what the cell claims.

### PF-1 — DF-07, the credited legal hold — **pass**

| Claim in v1.2 | Cited | Tree at `178da8b` |
|---|---|---|
| "No hold, retention or deletion logic exists in this flow"; the service's own contract | services/audit/audit_service/store.py:15 | Line 15 reads "There is no update and no delete path here, at any layer, for any caller." That is a **docstring**, so I did not rely on it: I searched the whole service for hold/retention/deletion logic and found only prose in docstrings — `services/audit/audit_service/{store.py, anchor.py, __init__.py, journal_witness.py}` contain no hold, schedule or delete code path. The claim is true; the *evidence* for it is the search, not the sentence [Committee] |
| `RetentionService` schedules and holds are in-memory `dict`s | services/compliance/compliance_engine/retention.py:39-43 | `class RetentionService` at 39, `__init__` at 40, `self._schedules: dict[...]` and `self._holds: dict[...]` at 41-42, audit hook at 43. Exact |
| `request_deletion` returns an outcome and deletes nothing; `DELETED` is a returned enum value | retention.py:32-36, 62-92 | 32-36 is `class DeletionOutcome` with `DELETED` and the three `SUPPRESSED_*` members; 62-92 is `request_deletion`, which selects an outcome, calls the audit hook and returns it. **No deletion of anything occurs anywhere in the file.** Exact |
| constructed in the composition root with an audit hook | apps/web/web_bff/platform.py:1074, 180, 1161 | 1074 `retention = RetentionService(audit_hook=audit2)`; 180 the `Platform` field; 1161 `retention=retention`. Exact |
| "called by no route, no scheduler and no CLI in this tree — the only callers are tests" | test/quartets/test_tc_cp_eligibility.py:254-278 | Verified independently by search: the only references to `RetentionService`/`retention.` outside the module and `build/lib` are `platform.py:43, 180, 1074, 1161` and `test/quartets/test_tc_cp_eligibility.py`. The cited range holds two of the three `request_deletion` calls and `place_hold`; the third call and the audit assertion run to line 288 — a range that stops one call short, which I note only so the next reader is not surprised |
| "a placed hold does not survive a restart, because the hold register is not on the durable seam" | (follows from 39-43) | Correct: `self._holds` is a plain dict, constructed per platform build; nothing writes it to `Store` |
| the retention/hold flow "is not drawn in this document" [Open] | — | Correct, and now stated where a reader will meet it. F-23 stays owed; see §6 |

**Judgment.** This is the finding I called the sharpest and it is fixed properly: the clause is not softened, it is withdrawn and replaced by the negative, with the helper described as it is. The one improvement I would still make is presentational (RF-5).

### PF-2 — DF-03 and DF-05, "no PII" — **pass**

| Claim in v1.2 | Cited | Tree |
|---|---|---|
| `account_ref` is `"acct:" + HMAC-SHA256(masking_key(tenant), account_id)` truncated to 16 hex | mcp/servers/mcp_servers/tools.py:35-37, 78 | 35-37 is `_pseudonym` with `hmac.new(tenant_key…, sha256).hexdigest()[:16]`; 78 is `"account_ref": _pseudonym(masking_key(p.tenant_id), acct.account_id)`. Exact |
| balances rounded | tools.py:31-32, 80, 85 | 31-32 `_round_balance` (granularity 1000); 80 `nav_rounded`; 85 `exposure_rounded`. Exact |
| the sim masking key is a derivable default | tools.py:49 | `masking_key: Callable[[str], str] = lambda tenant: "sim-masking-key-" + tenant`. Exact |
| an order row embeds the whole `OrderCommand` with `tenant_id` and `account_id` | libs/core/rtcore/schemas/order.py:33-53 | `class OrderCommand` at 33; `tenant_id` 40, `account_id` 41, instrument/side/quantity/prices, `decision_id` 38, `correlation_id` 52. Exact |
| the replacement wording | — | Both rows now read: no **direct** identifier (name, address, contact, document number) crosses; the tenant and account identifiers are **customer-identifying** and are personal data wherever the account holder is a natural person, so retention, subject rights and residency apply. That is the sentence I required, in both rows, and v1.1's phrase is explicitly **withdrawn** rather than deleted quietly |

**Judgment.** Pass, and better than the minimum: DF-03 also states that a keyed pseudonym is not anonymised data and names the masking key as the re-identification key. Residual: the qualifier is not defined in §3 (RF-3).

### PF-3 — DF-08, "telemetry is redacted" — **pass**

| Claim in v1.2 | Cited | Tree |
|---|---|---|
| fixed-pattern redaction at emission, list of patterns | observability/rtobs/logging.py:13-28 | `_PATTERNS` at 13-22 in exactly the order the cell lists (e-mail, `bearer`, `vault://`, 12–19-digit numbers, `acct-`/`cust-`/`tenant-` ids, IBAN, IPv4, secret/password/api_key/token key-values); `redact()` at 25-28. Exact |
| applied to the message and to every extra field | logging.py:37, 42 | 37 `"msg": redact(record.getMessage())`; 42 `payload.update({k: redact(str(v)) …})`. Exact |
| the actor/principal identifier is **not** redacted | — | Correct: no pattern matches a bare actor id of the form used in this tree (e.g. `legal.agent`, `ops.*`); only `acct-`/`cust-`/`tenant-` prefixed ids are caught (line 18). The cell states the limit as a deliberate accountability choice and opens purpose/retention/access [Open: PI-6], which is what I asked |
| TC-OB-002 | docs/TEST_CASES/TC-OB.md:13 | The test id exists and covers "emails, bearer tokens, vault refs, long account numbers and secrets", i.e. the patterns, not the actor id. The cell does not overclaim it |

**Judgment.** Pass. One wording precision left (RF-2), and the quartet gap I named in v1.1 §11 (a test that asserts the known limit) is still owed by the QA Lead.

### PF-4 — DF-11, `delete()` does not erase — **pass**

| Claim in v1.2 | Cited | Tree |
|---|---|---|
| `delete()` appends a `delete` entry and removes the `kv` row, while every prior `put` keeps the full value in the journal | libs/core/rtcore/store.py:277-289, 301-314 | 277-289 `_append` inserts `(seq, op, tbl, key, value, correlation_id, at, prev, digest)` — the **full value** — into `journal`; 301-309 `put`; 311-314 `delete`, which appends `("delete", …, "")` and deletes only from `kv`. Exact |
| the journal cannot be compacted, redacted or truncated without breaking `verify()`, which replays from genesis and raises `StoreIntegrityError` (fail closed) at open | store.py:355-383, 42 | 355-383 `verify()` replays the journal in sequence, recomputes each `journal_digest`, raises on any chain break, rebuilds the expected state and raises on any difference; 42 is `class StoreIntegrityError`. Exact. I also checked "at open" independently, because the cell asserts it: `open_store` constructs the store with `verify=False` then calls `store.verify()` and re-raises after the catalogued alert — "the alert is a notification, never permission to continue" [Source: apps/web/web_bff/platform.py:759-785]; `SqliteStore.__init__` verifies as well [Source: libs/core/rtcore/store.py:210]. True |
| "there is therefore no erasure path in this store today, and adding one is a design change to the integrity scheme, not a configuration" | [Open: O-111, O-128, O-135] | Correct and correctly tagged |
| the journal is a **derived record**, carried as a reviewer's recommendation, not a decision | docs/SESSIONS/REVIEW_2026-09-08_data_flows_privacy.md §5 | Correctly attributed to me and correctly marked as a recommendation to the Board, with O-09/O-106/O-135 open. The author did **not** promote my recommendation into a decision, which is the right handling [Source: 13] |

**Judgment.** Pass, and it answers the Board's question in the row without deciding it.

### PF-5 — DF-12, revocation and nonce journals — **pass**

| Claim in v1.2 | Cited | Tree |
|---|---|---|
| each revocation carries `kind`, `target`, `by` (the human actor who revoked), `at` and a free-text `reason` | mcp/servers/mcp_servers/revocation.py:17-22, 46-51 | 17-22 `class Revocation` with exactly those fields (`reason: str = ""`); 46-51 `revoke(...)` writing the record to the JSONL file. Exact |
| each nonce record carries `agent_id`, `nonce`, `issued_at` | mcp/servers/mcp_servers/identity.py:93-98 | `_remember_nonce` writes `{"agent_id", "nonce", "issued_at"}` to the journal. Exact |
| reclassified Internal **+ Personal (actor id)**; no retention rule for either file; `reason` needs minimisation | [Open: O-09, O-55, O-118, PI-4] | The reclassification is made in DF-12 **and** in the §2 data-at-rest table, which is what I asked; the register ids used all exist [Source: docs/RAID_LOG.md:71, 72, 179] |

**Judgment.** Pass. Residual: RF-4 on the §6 duplication with O-09.

### PF-6 — DF-22 and §4 — **pass on (i), (iii), (iv); (ii) delivered as asked but incomplete against the tree (RF-1)**

| Part | Claim in v1.2 | Cited | Tree |
|---|---|---|---|
| (i) data cell | an `AnchorRecord`: `anchor_seq`, `length`, `head_hash`, `sealed_at`, `published_at`, publisher `principal`, `correlation_id`, `prev_hash`, `hash`; "no identifier" **withdrawn** | services/audit/audit_service/anchor.py:52-63, 208-232 | 52-63 is `class AnchorRecord` with exactly those nine fields; 208-232 is `publish()`, which writes `principal=self._principal` and `correlation_id=correlation_id` into the record appended to the JSONL. Exact — **pass** |
| (ii) constraint | the seal correlation id must be system-generated and never request-derived; the platform's own publications are system-generated; nothing in the code refuses a caller-supplied value | store.py:275, 346, 394 | 275 `correlation_id="anchor:genesis"`; 346 `correlation_id=f"anchor:scheduled:{len(self._events)}"`; 394 `def seal(self, correlation_id: str = "-")`. All exact, and "no shipped route or CLI calls `seal()`" is true (only `test/` callers). **But the enumeration of publication paths is incomplete — see RF-1** [Source: services/audit/audit_service/store.py:699] |
| (iii) residency of the witness | unanswered, and unanswered **by design**, because the store is deliberately outside our own storage | [Open: O-54, O-10] | Correct, correctly tagged, and the honest form of the point — **pass** |
| (iv) §4 | "There is no residency and transfer map per tenant today, and v1.1's pointer to one is withdrawn"; PRIVACY_IMPACT carries four generic category rows; its data-at-rest section is **Draft v1.1**, reviewer and Board pending; `residency_region` is read by no code; "the honest answer … is **no, for any flow**" | docs/PRIVACY_IMPACT.md:5, 13-19, 20-29; services/identity/identity_service/accounts.py:41-44; apps/web/web_bff/platform.py:942 | PRIVACY_IMPACT:5 is the header row carrying "Draft v1.1, 2026-09-08"; 13-19 is the four-row data-category table whose residency cells read "per tenant"/"per cell"; 20-29 is the data-at-rest section with PI-1..PI-4. accounts.py:43 declares `residency_region`; platform.py:942 sets it to `"sim"`; those are the only two occurrences in the tree outside `build/`. Exact. The old pointer line is **deleted**, not softened — **pass**. I note with approval that the author cited *my* draft's status against me rather than leaning on it [Committee] |

---

## 5. The four items §6 records as new, with no register id yet

| # | As stated in v1.2 | Correctly stated? |
|---|---|---|
| 1 | "legal hold is unwired and non-durable: `RetentionService` holds live in memory, nothing deletes, and the deletion/hold flow is not drawn in this document — drawing it, putting the hold register on the durable seam and building a deletion executor are all owed" — Compliance Agent, Backend Lead, Data Architect (the flow); gate "C, ahead of any environment with real data" | **Yes, and it matches my proposed O-P2 in scope, owner and gate.** Verified above at retention.py:39-43, 62-92 and platform.py:1074. Two refinements: cross-reference **O-09** (the duty) and **O-135** (erasure against the chain) so the Program Orchestrator does not allocate a duplicate (RF-4); and note that the item has **three** distinct deliverables (draw the flow / durable hold register / deletion executor) which will not all land at one gate |
| 2 | "the actor/principal identifier is deliberately unredacted in telemetry: its purpose, retention and access rule are undecided" — Privacy Lead, SRE Lead; gate C | **Yes.** Verified at logging.py:13-28, 37, 42. It matches PI-6 in my PRIVACY_IMPACT draft, and the ownership split (mine for the rule, SRE for the emission) is right. It should also name **NFR-PRV-01**, which is the RTM row it will be tested under [Source: docs/SESSIONS/REVIEW_2026-09-08_data_flows_privacy.md §9] |
| 3 | "free-text `reason` in the revocation journal is unminimised, and neither MCP journal has a retention rule" — MCP Security Agent, Privacy Lead; gate C | **Half new.** The minimisation half is new and correct (revocation.py:17-22, 46-51). The retention half is **already** O-09 and is already tagged as such in the DF-12 row itself [Source: docs/RAID_LOG.md:17]. Split the row: one new id for free-text minimisation, an O-09 reference for the schedule (RF-4). I add, from this session's reading, that the same free-text exposure exists in a worse place: `WitnessAttestation.reason` is typed by a human and written **into the append-only audit chain** as event payload [Source: services/audit/audit_service/store.py:195, 684-696], where §7 of my v1.1 packet applies and nothing can be withdrawn. That is a **new** observation, not a v1.2 defect — see §7 |
| 4 | "nothing refuses a caller-supplied, request-derived correlation id at `AuditStore.seal()`; the constraint is written here and unenforced in code" — Backend Lead, Security Architect; gate C | **Correct about `seal()`, and under-scoped.** The attested re-establishment path publishes with a human-supplied correlation id [Source: services/audit/audit_service/store.py:699; reestablish.py:106-119]. The register item must be written about **the correlation id written to the witness**, not about one method. This is RF-1 |

**One structural point about all four.** They exist only inside DATA_FLOWS §6. Nothing in docs/RAID_LOG.md carries them: the register has no row for hold durability, for unredacted actor ids, for `reason` minimisation or for the witness correlation id (I searched). The document did the right thing by naming them rather than absorbing them, but **an open item that lives only in the document it was found in is one edit away from disappearing**. Allocating the ids is the Program Orchestrator's act, not the author's and not mine (I may not write RAID_LOG in this session); I make it a condition on the *Gate B convening*, not on this document [Committee] [Open].

---

## 6. What v1.2 deliberately did not action — is leaving it acceptable for Gate B?

v1.2 says plainly that it does not act on NF-1..NF-15, F-22 or F-23, and why. I agree with the principle: a corrective version should correct what was blocking and not absorb a reviewer's advisory notes silently. My assessment item by item:

| Not actioned | My position for Gate B |
|---|---|
| **F-23 — a retention and legal-hold flow of its own** (deletion request → `RetentionService` → outcome → audit) | **Acceptable for Gate B, on one condition.** It is now *stated* in DF-07 that the flow is not drawn, with an [Open], so the document no longer hides it; dev/sim deletes nothing and holds no real person's data [Source: 12]. The condition is that the item receives a register id before Gate B convenes (§5). It becomes **blocking before any environment holding a real person's data**, together with hold durability and a deletion executor — earlier than the Gate D marker O-09 carries, because a hold that vanishes on restart is only harmless while nothing deletes [Committee] |
| **NF-1 / F-22 — D-063 records "23 flows", the document has 22** | **Not blocking on the document; blocking on the evidence index.** I recounted: DF-01..DF-22, twenty-two rows, DF-03a named but not drawn. D-067 says the AUDIT_EVIDENCE_INDEX rows are not filled until the corrective versions exist [Source: docs/DECISION_LOG.md:75]; when that row is filled it must not say "23 flows". Program Orchestrator's fix, not the author's |
| **NF-4 — DF-02 masking versus THREAT_MODEL T-88** | **Still owed, still not blocking on v1.2, and I cannot close it this session:** THREAT_MODEL is being edited by another role in this worktree right now and I will not read it as settled. Both documents are Gate B exit evidence, so the reconciliation must be done before Gate B convenes, by the Data Architect with the Security Architect [Open] |
| **NF-2 — B10 not drawn; no backup/restore flow anywhere** | **Not blocking for Gate B (dev/sim); blocking before any backup of a real store exists.** Backup, restore and copy are processing operations with their own residency, retention and access questions. Unchanged from v1.1 |
| **NF-3 — no shipped entry point creates these files** | **Re-verified as still true at `178da8b`:** `create_app` calls `build_sim_platform()` with no `store_dir` [Source: apps/web/web_bff/app.py:90] and so do the CLI commands [Source: apps/cli/rt365_cli/main.py:142, 159, 196]; only tests and the pentest probes pass the directories. Not blocking — but it matters *more* in v1.2 than in v1.1, because v1.2 leans harder on the data-at-rest rows. Adding it to the Status cells stays my recommendation, so no gate report reads DF-10/11/21/22 as production behaviour |
| **NF-5..NF-15** (masking-key custody, no confidentiality control at DF-10, real broker statements, alert-channel export, prompt content, unsalted digests, at-least-once copies, Kill Switch retention, the ADR-020 "Consulted" line) | **Non-blocking, unchanged, and none has become blocking.** They belong to other owners' artefacts or to the register; I re-affirm them as written on 2026-09-08 and do not re-argue them here |

**Summary of §6:** nothing the author declined to action has become blocking on **this document**. Two of them (the four register ids; the DF-02/T-88 reconciliation) are conditions on **convening Gate B**, and they belong to the Program Orchestrator and the Security Architect respectively.

---

## 7. Did v1.2 make anything worse than v1.1?

I diffed v1.2 against the committed v1.1 and read every changed line.

1. **Scope discipline holds.** The change touches the header, §0 (one new evidence rule), the six rows, the two §2 rows implied by PF-5/PF-6, one §4 bullet (the withdrawn pointer, replaced), §5.1, §6 and §7. No other flow row, no classification cell and no control was altered, and no statement was quietly softened. I found nothing removed that should have stayed except the line that had to go (the PRIVACY_IMPACT pointer) [Committee].
2. **No new unevidenced claim replaced an old one.** Every corrected cell added citations rather than adjectives, and each citation resolves. The one incomplete statement is RF-1, and it is incomplete by omission of a third code path, not by invention.
3. **Two things are mildly worse in readability, not in truth:** the DF-07 and DF-22 controls cells are now long enough that the actual controls are hard to find (RF-5), and §4's new first bullet makes the untouched second bullet's present-tense residency claim read as a contradiction (RF-6).
4. **One thing is worse in precision:** DF-08's "neither free-text fields … are covered" is looser than the code (RF-2), and it is looser than v1.1 was silent — v1.1 said nothing here, so this is a new sentence that a reader could misread as "free-text is not scanned". Small, and I inherited the phrasing from my own review.
5. **New information I found this round that is nobody's regression**, and that I raise as proposed register items rather than as findings against v1.2: (a) the attested re-establishment path writes a **named human operator's** id and a **free-text `reason`** into the audit chain payload [Source: services/audit/audit_service/store.py:194-195, 684-696], which is personal data in the one store with no erasure path — §7 of my v1.1 packet applies to it in full; (b) `reestablish_witness` is shipped product code with no route or CLI in front of it [Source: services/audit/audit_service/reestablish.py:106-119], so the *procedural* controls around who may perform the attested act and what they may type are documentation today, not mechanism.

---

## 8. Evidence list (what a reader can check, and where)

| Statement | Evidence |
|---|---|
| The six corrections and their citations | docs/DATA_FLOWS.md v1.2 §1 rows DF-03, DF-05, DF-07, DF-08, DF-11, DF-12, DF-22; §2; §4; §5.1 |
| PF-1 verified | services/compliance/compliance_engine/retention.py:32-36, 39-43, 62-92; apps/web/web_bff/platform.py:180, 1074, 1161; services/audit/audit_service/store.py:15; test/quartets/test_tc_cp_eligibility.py:250-288 |
| PF-2 verified | mcp/servers/mcp_servers/tools.py:31-32, 35-37, 49, 78, 80, 85; libs/core/rtcore/schemas/order.py:33-53 |
| PF-3 verified | observability/rtobs/logging.py:13-28, 37, 42; docs/TEST_CASES/TC-OB.md:13 |
| PF-4 verified | libs/core/rtcore/store.py:42, 210, 277-289, 301-314, 355-383; apps/web/web_bff/platform.py:759-785 |
| PF-5 verified | mcp/servers/mcp_servers/revocation.py:17-22, 46-51; mcp/servers/mcp_servers/identity.py:93-98 |
| PF-6 verified | services/audit/audit_service/anchor.py:52-63, 208-232; services/audit/audit_service/store.py:275, 346, 394; docs/PRIVACY_IMPACT.md:5, 13-19, 20-29; services/identity/identity_service/accounts.py:41-44; apps/web/web_bff/platform.py:942 |
| RF-1 (the third publication path) | services/audit/audit_service/store.py:194-199, 670, 682-701; services/audit/audit_service/reestablish.py:106-119; test/quartets/test_tc_aud_audit.py:931, 941, 954, 1078, 1118 |
| NF-3 still true | apps/web/web_bff/app.py:90; apps/cli/rt365_cli/main.py:142, 159, 196 |
| The mandate this version answers | docs/DECISION_LOG.md:75 (D-067); docs/DECISION_LOG.md:71 (D-063, the 23-flow discrepancy) |
| My v1.1 findings | docs/SESSIONS/REVIEW_2026-09-08_data_flows_privacy.md §3.1, §3.2, §5, §6, §7, §9 |

## 9. Proposed rows for files I may not edit in this session

*RAID (Program Orchestrator; ids to be allocated).* **(a)** hold durability and a deletion executor, plus the undrawn retention/hold flow (my O-P2; cross-reference O-09, O-135) — Compliance Agent, Backend Lead, Data Architect; C, ahead of any environment with real data. **(b)** actor/principal identifiers deliberately unredacted in telemetry: purpose, retention, access rule (PI-6, NFR-PRV-01) — Privacy Lead, SRE Lead; C. **(c)** free-text minimisation for `Revocation.reason` **and** `WitnessAttestation.reason` (the latter is written into the append-only chain) — MCP Security Agent, Privacy Lead, Security Architect; C. **(d)** the correlation id written to the external witness must be system-generated on **both** publication paths (`seal()` and the attested re-establishment) and nothing refuses either today — Backend Lead, Security Architect; C. **(e)** my earlier O-P1 (v1.2 owed) is satisfied except for RF-1; O-P4..O-P8 stand as filed.

*DECISION_LOG (Program Orchestrator, on the Product Owner's decision).* A row recording, when it is decided: "DATA_FLOWS v1.2 accepted / not accepted; Privacy Lead re-review docs/SESSIONS/REVIEW_2026-09-09_data_flows_privacy_v1.2.md (SIGN WITH FINDINGS; PF-1..PF-6 verified corrected at the cited lines; one residual blocking, RF-1); Board classification review <ref>". **I record no acceptance and no approval** [Source: 13].

*AUDIT_EVIDENCE_INDEX (Program Orchestrator).* When the row is filled: "DATA_FLOWS.md **v1.2** — reviewer Privacy Lead, re-review performed 2026-09-09, **SIGN WITH FINDINGS (RF-1 residual blocking)**, packet docs/SESSIONS/REVIEW_2026-09-09_data_flows_privacy_v1.2.md; classification review Security & Privacy Board **pending**; Product Owner decision **pending**; the flow count is **22** (D-063 says 23 — correct one of the two first)". Evidence submitted, not evidence accepted [Source: 00].

*REQUIREMENTS_TRACEABILITY (QA Lead / Program Orchestrator).* NFR-PRV-01, NFR-PRV-02 and NFR-PRV-03 as filed on 2026-09-08, unchanged, plus a test the corrected DF-08 now invites: **[Open]** a negative case asserting the *known limit* of redaction (a bare actor id is emitted), so the limit is a tested fact rather than a sentence.

*PO_DECISION_QUEUE (Program Orchestrator).* "DATA_FLOWS v1.2: six of six corrections verified in the tree; one residual blocking clause on the witness correlation id (RF-1)"; "four open items live only inside DATA_FLOWS §6 and have no register id — allocate before Gate B is convened"; "D-063 says 23 flows, the document has 22".

## 10. Threat-model delta (proposed to the Security Architect, who owns THREAT_MODEL — which I did not read as settled)

| Candidate | Boundary | Statement |
|---|---|---|
| Human-typed identifier reaches the external witness | B10 | The attested re-establishment publishes an anchor with an operator-supplied `correlation_id` and is performed exactly when an incident is in progress, which is when a person is most likely to paste a request-scoped id. The value leaves for a store deliberately outside our storage and cannot be withdrawn [Source: services/audit/audit_service/store.py:699] [Open: RF-1] |
| Free text into an unerasable chain | B4 | `WitnessAttestation.reason` is uncontrolled free text by a named human, written into the audit chain payload; §7 of the 2026-09-08 packet (no erasure path, an attempted redaction halts the platform) applies to it [Source: services/audit/audit_service/store.py:195, 684-696] |
| The three deltas filed on 2026-09-08 | — | Erasure attempt as denial of service; legal hold lost on restart; hash as a de-identification illusion — all unchanged and all still open |

## 11. Control quartet for the control RF-1 asks for (ids by the QA Lead; **none exists today**)

| Control | Positive | Negative | Abuse | Recovery |
|---|---|---|---|---|
| **System-generated witness correlation id** | a scheduled and a genesis publication carry `anchor:*` ids and verify | a `seal()` or an attestation carrying a request-shaped correlation id is **refused with a reason code**, on both paths | an operator pastes a customer request id into the attestation under incident pressure; a caller supplies a tenant- or account-derived value | the refusal is itself audited, the act can be repeated with a system-generated id, and no record with the refused value reaches the anchor file |

---

## 12. Concerns for the Product Owner

- **PC-1 The corrections are real.** I opened every line the author cited and the tree says what the document says. The two statements I called the most dangerous in v1.1 — a legal-hold control credited to the audit trail, and "no PII" written about customer-identifying data — are withdrawn and replaced with the plain negative and the customer-identifying formula. That is what a corrective version should look like.
- **PC-2 One clause still blocks, and it is cheap.** The document tells an implementer to constrain the correlation id at one method; there is a second path, used by a human during an incident, that writes the same field to the same outside store (RF-1). Fixing the sentence now costs a line; discovering it after a request id has been published to a witness we do not own cannot be undone.
- **PC-3 Four open items live only inside the document.** Hold durability, unredacted actor ids, free-text minimisation and the witness correlation id have no register row. That is the Program Orchestrator's allocation, and I would make it a condition of convening Gate B rather than a condition on the Data Architect.
- **PC-4 Nothing has changed in what the platform can honestly say.** There is still no erasure path in the control store or the audit chain; a deletion still leaves the value in the journal for ever; an attempted redaction would still make the store refuse to open. No gate report, DPIA, customer document or marketing statement may say the platform can honour an erasure request. The chain-format decision (pseudonymous actor and account at first write; payload outside the hashed record) remains my Gate C entry recommendation, ahead of the first environment with a real person's data.
- **PC-5 I am one seat.** The classification column is the Security & Privacy Board's; record classes and retention periods are Compliance's with external counsel through a human act (H-04, scope H-25); the document is yours. **This packet is a review, not an approval, and no acceptance exists until it is in docs/DECISION_LOG.md** [Source: 00, 13].

---

## 13. Assumptions, confidence, provenance, independence

- **Assumptions:** the tree at `178da8b` is the code v1.2 describes (v1.2 states it read at `442cebd`, its parent; I re-read at `178da8b` and found no code change between them affecting any cited line); dev/sim holds no real person's data [Source: 12]; D-025, D-056, D-058..D-067 stand as recorded; THREAT_MODEL, SECURITY_PLAN, CAPACITY_MODEL and DR_PLAN are mid-edit by other roles and are not evidence in this packet [Committee].
- **Confidence:** **high** on every pass/fail in §4 and on RF-1 — each was opened at the cited line and, for every negative claim, searched for independently; **high** on the scope claim in §7 (read from the diff against the committed v1.1); **medium** on the completeness of my personal-data sweep of the *unchanged* rows, which I did not re-do this round beyond the free-text paths I stumbled on; **none** on any legal characterisation, retention period, lawful basis, jurisdictional requirement, notification duty or DPIA outcome — those are [Open: O-09, O-10] and belong to Compliance and external counsel through a human act (H-04, H-25); **none** on any security-architecture verdict (integrity scheme, key custody, WORM, network), which is not my seat.
- **Provenance:** [Source: path:line] for every code and document fact, read at `178da8b`; [Source: NN] for blueprint principles as transmitted by the repository artefacts; [Committee] for this session's reasoning; [Open] items carry their register ids or are named as unallocated.
- **Independence:** I am not the author of DATA_FLOWS, I did not write any of the code I examined, I did not edit the document I reviewed, and I approve nothing here. Author != reviewer != approver [Source: 13].

---

## 14. Verdict

**SIGN WITH FINDINGS.**

- **PF-1 pass** — legal hold removed from the audit trail's controls and replaced by the verified negative; the helper described as it is.
- **PF-2 pass** — "no PII" withdrawn in both rows; the customer-identifying formula applied verbatim in DF-03 and DF-05.
- **PF-3 pass** — the redaction control stated as built, with its pattern list and its deliberate limit.
- **PF-4 pass** — `delete()` does not erase; the journal cannot be compacted without the store refusing to open; no erasure path exists.
- **PF-5 pass** — DF-12 and §2 reclassified Internal + Personal (actor id); free-text `reason` and the missing retention rule opened.
- **PF-6 pass on (i), (iii), (iv); (ii) delivered as asked but incomplete against the tree** — see RF-1.

**Still blocking:** **RF-1** only. DF-22 and its §6 row scope the witness-correlation-id constraint to `AuditStore.seal()` and assert that the platform makes two publications of its own; a third path publishes an anchor carrying a **human-supplied** correlation id [Source: services/audit/audit_service/store.py:699; services/audit/audit_service/reestablish.py:106-119].

**What clears it:** an errata in DF-22 and in the matching §6 row stating that **the correlation id written to the external witness — on `AuditStore.seal()` and on `WitnessAttestation.correlation_id` in the attested re-establishment — must be system-generated and never derived from a customer request or session, and that nothing in the code refuses either today**, cited to `services/audit/audit_service/store.py:394, 699` and `services/audit/audit_service/reestablish.py:106-119`. Any second reader can verify that against those lines; it does not need a further full re-review from me.

**Recommended, not blocking:** RF-2 (DF-08 wording), RF-3 (define the composite classification qualifiers in §3 before the Board reviews the column), RF-4 (cross-reference O-09/O-135 from §6 and split row 3), RF-5 (move target narrative out of the Controls cells in the next full version), RF-6 (mark §4 bullet 2 as a D-056 target), RF-7 (record this re-review in the header and §7).

**Conditions on convening Gate B that are not the author's to fix:** allocate register ids for the four §6 items (Program Orchestrator); reconcile the flow count with D-063 (Program Orchestrator); reconcile DF-02 with the THREAT_MODEL masking row when that document's corrective version lands (Security Architect with the Data Architect).

**This signature is not an approval and records no acceptance. Only the human Product Owner, or the delegate under D-040, records acceptance, and only in docs/DECISION_LOG.md** [Source: 00, 13] [Committee].
