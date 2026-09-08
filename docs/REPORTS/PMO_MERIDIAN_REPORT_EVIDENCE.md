# Meridian IT-PMO — the evidence half of the field report

**To:** the Product Owner of Meridian IT-PMO (mliad313sn/Meridian), through the request register mechanism they created (`docs/requests/rt365.json`).
**From:** the Program Orchestrator of Global AI-MCP RoboTrader (RT365), the first real programme Meridian carries.
**Companion:** the value half is written by this programme's Product Owner. This half is delivery management: what we did, what it cost, what broke.

| Owner | Reviewer (different line) | Approving body | Status |
|---|---|---|---|
| Program Orchestrator | *not yet assigned* — this document is not reviewed | Product Owner (filing upstream is H-31, a human act) | v1.0 — 2026-09-08 |

**Intended path.** This report was commissioned as `docs/PMO_MERIDIAN_REPORT_EVIDENCE.md`. The repository's write-scope guard (`scripts/agent_guard.py`, roster `.claude/agents/roster.json`) refuses that path to this role; it is written here, inside the Program Orchestrator's own `docs/REPORTS/` scope. Moving it to the commissioned path is an act for a role that owns it. [Measured: `agent_guard: agent 'program-orchestrator' may not edit docs/PMO_MERIDIAN_REPORT_EVIDENCE.md`]

## 0. How to read the tags, and what this report is not

Every statement carries one of three tags and nothing carries none.

- **[Measured]** — we ran it and this is the number, with the command or the file that produced it.
- **[Source]** — Meridian's own code, migration, register or changelog, cited by file and line where a line exists.
- **[Open]** — not verified. Named so it can be settled, with what would settle it.

This report does not claim a Meridian capability we have not seen in its code or its behaviour, and it does not claim a delivery outcome for RoboTrader. Nothing here promotes any environment; nothing here is a return, a forecast or a promise. Where our own ledgers and CI carry the truth and Meridian carries only the rhythm, this report says exactly that, and it corrects two places where our own earlier documents overstated a Meridian defect.

**Where the truth actually lives.** RoboTrader's engineering truth is in the repository ledgers, versioned with the code and evidenced by CI (`docs/RAID_LOG.md`, `docs/DECISION_LOG.md`, `docs/MISSING_ACTIONS.md`, `docs/REQUIREMENTS_TRACEABILITY.md`, `docs/AUDIT_EVIDENCE_INDEX.md`, `docs/TEST_CASES/`) [Source: docs/ADRs/ADR-017.md §Decision.1]. Meridian holds the portfolio view and the meeting rhythm, loaded one way from those ledgers. **Every management fact in Meridian arrived from a ledger; no gate, no control and no test in this programme reads Meridian.** That division is the honest frame for everything below: when we say Meridian "gave" us something, we mean it gave a view or a cadence over facts the repository already held.

---

## 1. What we actually did with it — the timeline, with numbers

All times UTC on 2026-09-08, from `git log --date=format:'%Y-%m-%d %H:%M'` in each repository. RT365 commits are on branch `claude/project-owner-agent-setup-hi3xqu`; Meridian commits are on its default branch in the working copy at commit `e352bc8`. [Measured]

| Time | Repo | Commit | What happened |
|---|---|---|---|
| 08:45 | RT365 | `12a20a8` | First load evidenced. `scripts/meridian_sync.py` (358 lines), `docs/PMO.md`, `docs/PMO_MERIDIAN_ASSESSMENT.md` v1.0 with findings M-01..M-12 and improvements I-1..I-12, ADR-017, D-049, RAID O-73..O-76, action H-28. Instance: Meridian **5.9.0** (`77c4b49`), PGlite, 449 tests pass. |
| 09:34 | RT365 | `7b11f79` | The twelve improvements recorded as upstream issues #1–#12. |
| 09:44 | RT365 | `25b0483` | The commit Meridian's register cites as the version of us it read. [Source: `docs/requests/rt365.json` `source.commit`] |
| 09:54 | Meridian | `b58f806` | **All twelve taken.** Version to 5.10.0; a Product Owner named with authority over the register and a standing duty to re-read this repository each round. |
| 10:09 | Meridian | `e352bc8` | Second round on the same day: 27 findings from two counsellors Meridian convened on its own release, fixed. |
| 14:09 | RT365 | `7d61bd1` | Re-test on 5.10.0 recorded: assessment v1.1, §7 the re-test, §8 requirements V-1..V-12. |
| 14:24 | RT365 | `3628fcd` | `docs/PMO.md` limits corrected; the Product Owner's weekly for the day written. |

**The strongest measured claim in the whole report.** From the commit that carried our twelve findings (`12a20a8`, 08:45) to the Meridian head that carried all twelve delivered (`e352bc8`, 10:09) is **84 minutes**. From the commit their register says it read (`25b0483`, 09:44) to their adoption commit (`b58f806`, 09:54) is **10 minutes**. We re-tested and confirmed on the same working day, 5 hours 24 minutes after the first load. [Measured: git timestamps in both repositories]

We are aware of what that claim is and is not. It is evidence that this product's maintainer reads field returns and acts on them at a speed no vendor process matches. It is **not** evidence that the twelve are correct, complete or safe in production — a 84-minute turnaround on twelve changes across five migrations is also a change-control observation, and we make it as one in §6.

### 1.1 Round one — Meridian 5.9.0 (`77c4b49`)

Instance: cloned, `npm install`, `npm run seed`, `npm run dev`, PGlite, on the seeded **demonstration book** (this matters — see §3, gap G-5). Test suite 449 pass. [Source: docs/PMO_MERIDIAN_ASSESSMENT.md §1; not re-measured by us on 5.9.0]

The first hour cost about 40 minutes to three setup defects, none of which was in the documented quick start: an in-memory book when `PGLITE_DIR` was unset, a non-recursive `mkdirSync` on the data directory, and `Cannot GET /` because `npm run dev` does not build the client. [Source: docs/PMO_MERIDIAN_ASSESSMENT.md §3 M-01..M-03, each marked [Verified] there against `server/src/db.js:152` and `server/src/index.js:172-189` on 5.9.0]

Load evidence: `docs/PMO/meridian_sync_2026-09-08.json`. Resulting state recorded in its `summary`: 16 projects, 10 milestones on the governance project, 86 RAID items. [Measured: the file]

**What the log actually records, and what it does not.** The `log` array holds **76 write requests, all of them against `/api/meetings/*`**: 48 `POST …/decisions` (201), 25 `POST …/actions` (201), one series, one occurrence, one open. There is **no creating write for a project, a milestone, a person or a RAID row anywhere in that file.** [Measured: `docs/PMO/meridian_sync_2026-09-08.json`, `log`]

So the file evidences the *state after* the first load and the *writes of one later run*, not the first load itself. It is our evidence defect, not Meridian's, and it is gap G-9 below. Two consequences we record rather than hide:

- `docs/PMO.md` §4 says the first load put "14 decisions and 21 open actions" on the weekly. The evidence file says **48 and 25**. At commit `12a20a8` the ledgers held 49 `| D-0` rows and 26 open `| H-` rows — consistent with 48/25 and not with 14/21. **The number published in our own PMO guide is wrong.** [Measured: `git show 12a20a8:docs/DECISION_LOG.md | grep -c '^| D-0'` → 49; the same for MISSING_ACTIONS → 28 rows, 26 open]
- Because the projects and RAID were skipped as already-present while a *new* meeting series was created, the same run re-wrote every decision and action onto a fresh occurrence. That is the loader's design (`existing_decisions` checks only the current occurrence; `open_occurrence` always POSTs a new one) and it means "the second run made no creating writes" is true for the portfolio and **false for the meeting**. [Measured: `scripts/meridian_sync.py:200-215`, and the 76-write log]

### 1.2 Round two — Meridian 5.10.0 (`e352bc8`), the re-test

Test suite, re-run by us in this session on the working copy, not quoted from anyone:

```
# tests 513   # suites 101   # pass 513   # fail 0   # cancelled 0   # skipped 0   # todo 0
# duration_ms 123665.5        real 2m3.9s
```
[Measured: `npm test` at `e352bc8`, this session. Independently confirms the 513/101/128s figure in docs/PMO_MERIDIAN_ASSESSMENT.md §7.]

Schema: **39 migrations**, `001…039`, of which `034_decision_register`, `035_write_api`, `036_gate_ladder`, `037_gate_criteria`, `038_stakeholders_comms`, `039_decision_record` are the six added for our twelve findings. [Measured: `ls server/migrations/*.sql | wc -l` → 39; [Source] each migration header names the RT365 finding it answers, e.g. `036` opens "`036 · L'ÉCHELLE DE JALONS DU PROGRAMME (I-3 · retour de terrain RT365, M-04)`"]

First hour on 5.10.0: `server/src/env.js:29` defines `DEFAULT_PGLITE_DIR = join(ROOT, "server", ".data", "pgdata")` and line 82 is `fs.mkdirSync(abs, { recursive: true })`; `server/test/firsthour.test.js` exists as the regression. All three of M-01..M-03 are closed in code. [Source: those files, read at `e352bc8`] Our own first hour on this working copy was zero minutes, because the clone arrived seeded. [Open: we did not re-run a clean-clone first hour ourselves on 5.10.0; the clean-clone claim in docs/PMO.md §4 stands on the earlier session, not on this one.]

Load evidence: `docs/PMO/meridian_sync_2026-09-08_5.10.0.json`, **256 writes, every one a 2xx**. The full decomposition, which is the honest picture of what a "portfolio load" costs in requests:

| Requests | Route | What |
|---|---|---|
| 122 | `POST /api/raid` | one per open RAID row |
| 59 | `POST /api/meetings/occurrences/{occ}/decisions` | one per `D-0nn` |
| 28 | `POST /api/meetings/occurrences/{occ}/actions` | one per open `H-nn` |
| 16 | `POST /api/projects` | E01–E15 plus RBT-GOV |
| 14 | `POST /api/admin/people` | the accountable roles as a directory |
| 6 | `POST /api/milestones` | Gate A–F |
| 6 | `PATCH /api/milestones/PRJ-147-M4…M9` | acceptance criteria; `done`+`acceptedBy` on Gate A |
| 1 each | `POST /api/admin/sites`, `/api/admin/programmes`, `/api/meetings/series`, `…/occurrences`, `…/open` | the structure and the room |
| **256** | | 250 POST (249×201, 1×200), 6 PATCH (200) |

[Measured: parsed from the `log` array of that file]

**Second run: 1 request, a 200, no creating writes** for the portfolio. [Source: docs/PMO.md §4 and §6; the second-run log was not kept as a file — gap G-9.]

### 1.3 Round three — the incremental load

After the E01/E07/E11/E13 merges and decisions D-058..D-062: **134 RAID items, 17 incremental writes** — the loader wrote only what the ledgers had changed. [Source: docs/PMO.md §6 and docs/SESSIONS/WEEKLY_2026-09-08_product_owner.md header]

**There is no evidence file for this load.** `ls docs/PMO/*.json` returns two files; the third load has none. The 17-write claim is therefore uncorroborated in the evidence base, which is exactly the standard this programme applies to its own gates and did not apply to itself here. [Measured: `ls docs/PMO/*.json` → 2 files] Gap G-9.

### 1.4 What broke, and what was silent

**Nothing returned an error.** Across both recorded loads, 332 write requests, **zero non-2xx responses**. [Measured: both `log` arrays] The loader is written to abort on the first status ≥ 300 (`meridian_sync.py:_write`), so a single 4xx would have stopped the run; none did.

What was silent is more interesting than what broke:

- **Silent duplication of the gate ladder.** Six `POST /api/milestones` produced a project carrying **ten** milestones. Nothing warned. §3, gap G-1.
- **Silent flattening of the register.** All 122 RAID rows were written with a hard-coded `"p": 3, "i": 3` (`meridian_sync.py:167`), because `docs/RAID_LOG.md` has six columns — ID, Type, Item, Owner, Needed by, Status — and no probability, impact or review date to map from. Meridian accepted every one. The portfolio's Risk posture panel then reports **OPEN ITEMS 145 · HIGH 136 · AT PMO LEVEL 136** — a number with no information in it. [Measured: the loader source; `docs/PMO/meridian_decisions_5.10.0.png`, Risk posture panel; `grep -n '^|' docs/RAID_LOG.md` header row]
- **Silent loss of the action owner and the due date.** `POST /api/meetings/occurrences/:id/actions` accepts `ownerId`, `projectId` and `dueDate` (`server/src/routes/meetings.js:591-611`). Our loader passes `ownerId: <Product Owner>` for every action and never passes `dueDate`; the ledger's real owner is flattened into the free-text detail. The agenda therefore reads "Owner Product Owner · **no date** · Open" on H-01, H-03, H-04, H-05. [Measured: `docs/PMO/meridian_meeting_5.10.0.png`; [Source] meetings.js:607-610] Ours, not theirs.
- **Silent truncation of decisions.** Headlines are cut at 300 characters by the loader; the Decision register renders them mid-sentence — "…tenant identifiers are addressable, not confidential;", "…chooses keyed HMAC or", "…**no cost". Markdown emphasis from the ledger is rendered literally. [Measured: `docs/PMO/meridian_decisions_5.10.0.png`]
- **Silent non-closure of the meeting.** The loader opens the occurrence and never closes it. The screenshot badge reads **IN SESSION** and Meridian's own guidance in that panel says "closing is what freezes the record". Fifty-nine decisions and twenty-eight actions sit in an unfrozen room; the cadence never advanced, because Meridian schedules the next occurrence on close. [Measured: `docs/PMO/meridian_meeting_5.10.0.png`; `meridian_sync.py:open_occurrence` has no close call] Ours, not theirs.
- **Silent attribution to one human.** Every one of the 256 writes went over the session API under the account we logged in with. The portfolio's "This week" panel attributes `RSK-79`, `RSK-78`, `RSK-77` to "**System Administrator (admin)**". [Measured: `docs/PMO/meridian_portfolio_5.10.0.png`] Meridian shipped audit-under-the-integration's-name in `035_write_api.sql`; we get none of it, for the reason in §3 gap G-3.

---

## 2. What it demonstrably gave this programme

Named management acts, each tied to evidence. Where the ledgers did the work and Meridian only mirrored it, that is said.

| # | Management act | Evidence | Honest attribution |
|---|---|---|---|
| **B-1** | **A weekly with an agenda nobody wrote.** The Product Owner's weekly exists as a room with a generated agenda: "6 sections · 25 of 25 minutes allocated · Generated from portfolio state as at 08 Sep 26. Sections with nothing to report are left out rather than shown empty." Section 1 is "Actions carried forward, 5 min", listing H-01/H-03/H-04/H-05. | `docs/PMO/meridian_meeting_5.10.0.png` [Measured] | **Meridian did this.** The ledger holds the actions; the sectioning, the timeboxing and the "leave out what is empty" rule are the tool's. This is the one place where Meridian produced something the repository could not. |
| **B-2** | **A decision register that reads like a decision register.** D-055..D-059 render with full rationale, the decider ("Product Owner"), the room ("RoboTrader weekly — Product Owner") and the project (PRJ-147), newest first, under "consequential decisions". | `docs/PMO/meridian_decisions_5.10.0.png` [Measured] | **Shared.** `docs/DECISION_LOG.md` is the truth and is diffable; Meridian gives it a register view with the decider and the room attached, which a Markdown table does not. This is the direct product of REQ-07/I-7, a request we filed, delivered in migrations 034 and 039. |
| **B-3** | **A register of 122–134 items with a search, a type and an exposure, in one place, without a spreadsheet.** The project overview shows "Open RAID 122 items" beside the milestones. | `docs/PMO/meridian_project_5.10.0.png` [Measured] | **Mirror.** Every row came from `docs/RAID_LOG.md`. The gain is a view and a filter; the loss is described in §1.4 (constant 3×3). |
| **B-4** | **Sixteen epics as sixteen projects with a named accountable lead, visible next to twelve unrelated projects in one register.** E01 · PRJ-150 · Backend Lead; E02 · PRJ-153 · Data Engineering Lead; E08 · PRJ-171 · Quant Research Lead, and so on. | `docs/PMO/meridian_portfolio_5.10.0.png` [Measured] | **Mirror**, and a real one: `docs/BACKLOG.md` holds the leads; Meridian is the first place they appear as a portfolio row that a sponsor who does not read Markdown can scan. |
| **B-5** | **An append-only audit of who changed the portfolio, with before/after images, exportable.** `GET /api/audit` returned every load action with actor and detail; archive export produced 1,529 rows across 47 tables. | [Source: docs/PMO_MERIDIAN_ASSESSMENT.md §2, marked [Verified] on the 5.9.0 run] | **Meridian did this**, and it is the capability we would most miss. Not re-measured by us on 5.10.0 — [Open]. |
| **B-6** | **A reversible commitment.** `GET /api/admin/archive` and `npm run restore` mean the book leaves without the vendor; the whole thing is Apache-2.0 and self-hosted. | [Source: assessment §2; LICENSE in the clone] | **Meridian.** This is why ADR-017 could be taken at all: adopting it risks a rhythm, not a hostage. |
| **B-7** | **A route from a field finding to a shipped release, with a register that tracks it.** `docs/requests/rt365.json` carries 13 requests, REQ-01..REQ-13, each with `origin` naming our I-n/M-nn/O-nn identifiers, a `delivered` file list, a `measure` naming the test file, a `remaining` field and a `history` array. REQ-01's `answerToSource` reads: "O-73 can be closed; delete the workaround in docs/PMO.md §2." | [Measured: parsed the register — 13 requests; [Source] the file] | **Meridian did this**, and it is the most unusual thing in this report. A tool that answers its user's register item by identifier, in the user's own numbering, and tells them which of their RAID rows they may now close, is not a normal open-source posture. |
| **B-8** | **Nine of our twelve improvements are visible in the code we read, not only asserted.** `PUT /api/v1/{projects,milestones,raid,activities,workitems,criteria}` under `write:portfolio` and `{decisions,actions}` under `write:meetings`, each behind `idempotent()` (`server/src/routes/v1.js:100-107`); `programme.gate_model` (`036`); `gate_criterion` with a named independent reviewer (`037`); `DEFAULT_PGLITE_DIR` + recursive mkdir (`env.js:29,82`); `docs/openapi.v1.json` version `5.10.0` matching `package.json`, describing 12 paths. | [Measured: read at `e352bc8`; `openapi.v1.json` info.version `5.10.0`, 12 paths] | **Meridian.** M-05 (read-only API) and M-09 (version drift between `package.json` 5.9.0 and OpenAPI 5.3.0) are closed **in code**. Whether they are closed *for us* is §3, gap G-3. |

**What it did not give that we half-expected it to.** Nothing in Meridian caused a management decision on this programme. Every decision D-049..D-065 was taken from the ledgers and written to the ledgers; Meridian received them. The tool changed *how the week is convened*, not *what was decided*. That is a real but modest claim and it is the accurate one.

---

## 3. What it demonstrably did not give — and what a project manager did by hand

### G-1 · Our sixteen projects carry two gate ladders — and the cause is ours, not theirs

**Observed.** `RBT-GOV` carries **ten** milestones where six were intended: `Gate A`, `Gate 1 — Mandate`, `Gate B`, `Gate 2 — Design authority`, `Gate C`, `Gate 3 — Readiness`, `Gate D`, `Gate E`, `Gate 4 — Benefits`, `Gate F`. The project header reads "**Milestones & gates — Gate 1 — Mandate is next**" and badges Gate 1 **AT RISK**. Our own six show no owner and no evidence count; Meridian's four show "Product Owner · 01 Oct 26 · evidence 0/1" and a "see evidence" link. [Measured: `docs/PMO/meridian_project_5.10.0.png`; both sync files list the same ten milestone names]

**Why it matters.** The one question a portfolio must answer is *which gate is next*. Meridian answers it with a gate that has no authority in this programme. Our gates are `A…F` (dev → sim → shadow → paper → supervised pilot → capped autonomous pilot → controlled GA); `Gate 1 — Mandate` authorises nothing here. A sponsor reading the project page is told the wrong thing, with a red badge.

**We must correct our own record.** `docs/PMO.md` §5 and `docs/PMO_MERIDIAN_ASSESSMENT.md` §8 V-8 call this "a defect, not a preference" in Meridian 5.10.0. **On the code we read, it is not a Meridian defect.** `server/src/wbs.js:113-120` selects *one* ladder — the programme's `gate_model` if set, otherwise the default `GATES` — and `POST /api/admin/programmes` accepts a `gateModel` body field (`server/src/routes/admin.js:632`, via `gateModelOf` at line 22, validated by `normaliseGateModel` in `shared/engine.js:89`, max 12 gates). The CHANGELOG states it plainly: "a project is born with its programme's gates". Our loader sends `POST /api/admin/programmes {"id": "RBT", "name": "Global AI-MCP RoboTrader"}` with **no `gateModel`** (`meridian_sync.py:31`), takes the default four, and then adds six ordinary milestones on top. The same ten milestones appear in the **5.9.0** load, before the ladder was configurable — which proves the duplication predates the feature and was not introduced by it. [Measured: both sync files; [Source] the four code sites above] Their register said so already: REQ-03 `answerToSource` reads "O-75 can be closed; **declare A–F on programme RBT, then create the epics**."

**What is still theirs.** Migration `036` states in its own header that an amended ladder does not rewrite existing projects — "changer l'échelle d'un programme en cours est une décision, pas un réglage". Our sixteen projects already exist on the default ladder. There is no documented path to migrate a book created before the ladder was declared, and no way to see from the API that a project is on a ladder its programme no longer uses. The half of V-8 that stands is: **an existing book migrating without duplicates.**

**What the project manager does by hand.** Reads six milestone names out of ten on every project page and ignores the "is next" line, the "AT RISK" badge and the four "evidence 0/1" counters. Sixteen projects, every week.

### G-2 · The gates that govern this programme cannot carry gate criteria

**Observed.** `037_gate_criteria.sql` creates `gate_criterion (project_id, gate integer CHECK (gate BETWEEN 1 AND 12), …)` — a criterion binds to a **position in the ladder**, not to a milestone id. Our Gate A–F are plain milestones created by `POST /api/milestones`; they hold no ladder position, no evidence document and no criteria. The screenshot confirms it: Meridian's four gates show "evidence 0/1", ours show nothing. [Measured: the screenshot; [Source] `server/migrations/037_gate_criteria.sql`, `server/src/wbs.js:52-66`]

**Why it matters.** REQ-04 — a criterion posed in advance, found met by a **named reviewer who does not own the evidence cited** — is the single most valuable thing Meridian built for us, because it is the shape of our own control model (author ≠ reviewer ≠ approver). It is unreachable for the six gates that actually govern this programme. Same root cause as G-1, same fix.

**By hand.** Gate exit evidence lives in `docs/GATE_REPORTS/`, `docs/RELEASE_CHECKLIST.md` and `docs/AUDIT_EVIDENCE_INDEX.md`, reviewed in the repository. Meridian's gate criteria are not used at all.

### G-3 · The write API v1 cannot carry a load — because structure is not in it

**Observed.** The v1 write surface is **8 collections**: projects, milestones, raid, activities, workitems, criteria (scope `write:portfolio`), decisions, actions (scope `write:meetings`) (`server/src/routes/v1.js:100-107`). The schema has **52 tables** (`grep -rhoiE 'create table' server/migrations/`). Sites, programmes and people are not among the eight; the register states it: REQ-02 `remaining` = "structure (sites, programmes, people) stays on the session API and CSV import — D-33.4". [Measured: 8 of 52 = 15%; [Source] v1.js and the register]

**Why it matters to a real programme.** The **first three writes of any first load** are a site, a programme and fourteen people. An integration that cannot create them must hold a session login, which means:
- it authenticates as a **human account with `user.manage`** rather than as a scoped integration key;
- every write in the trail is attributed to that human — measured: "System Administrator (admin)" on `RSK-79/78/77` in the portfolio's This-week panel;
- the audit-under-the-integration's-name that `035_write_api.sql` delivered is unreachable for us;
- there are **171 session route declarations against 12 documented v1 paths** (`grep -rhoE '^r\.(get|post|patch|put|delete)\(' server/src/routes/*.js` → 183 total, 12 in `v1.js`), and the OpenAPI describes only the twelve, so the contract we depend on for 171 of our calls does not exist.

That is why our loader still uses session routes after REQ-02 shipped: **not because the write API is unfinished for delivery objects, but because a first load cannot start.** [Measured] Meridian's own `answerToSource` on REQ-02 says "meridian_sync.py can move to `PUT /api/v1/*` with its own ids and **unpin the commit**" — on the routes as shipped, it cannot fully, because the run would still need a session for its first three writes.

**By hand.** We keep a human account's credentials in the loader's environment and accept a trail that names a person for machine writes.

### G-4 · The value objects are readable and not writable — measured as zero

**Observed.** `GET /api/v1/portfolio` returns `counts.benefits` and `counts.lessons` (`v1.js:52-59`), so benefits **are** in the read contract. There is no `PUT /api/v1/benefits/:externalId` and no `PUT /api/v1/business-case/:externalId`; benefits are written only by the session routes `POST/PATCH/DELETE /api/benefits` (`server/src/routes/portfolio.js:1814,1842,1887`), with `benefit.review` a group-only act (line 1909). The same holds for `business_case`, `lesson`, `stakeholder`, `comms_plan`, `rollout_wave`, `project_tolerance`, `project_exception` and `demand` — nine objects, none writable through v1. [Measured: route inventory; [Source] those lines]

**What that produced, measured.** Status reporting → **Value position: BENEFITS PROMISED 0 · MEASURED 0 · ATTAINMENT — · MET — · PROMISING NOTHING 28 projects with no stated benefit.** [Measured: `docs/PMO/meridian_decisions_5.10.0.png`]

Sixteen of those twenty-eight are ours. The first real programme this tool carries states **no benefit at all**, on the page built to ask whether it was worth doing — and it states none because our loader, which pushed 256 delivery writes without a human touching a keyboard, **cannot push a single benefit**.

**By hand.** Nothing was typed in. We chose not to hand-enter value data that would go stale the same week, which is precisely the failure mode V-1 predicts. RoboTrader's outcome measures live in `GOAL.md` and the gate charters and are not in Meridian.

### G-5 · The executive numbers mix our programme with the demonstration book

**Observed.** Portfolio header: **PORTFOLIO VALUE $51.3M · 12 funded projects · 16 strategy (no budget) · ON TRACK 82% · 23 green · 2 amber · 3 red · SCHEDULE INDEX 0.95 · COST INDEX 1.00 · FORECAST VARIANCE −$782K · OPEN RISKS 45 (2 above the escalation threshold) · Decisions owed 36 open**. The "16 strategy (no budget)" are ours. All six "Decisions owed" entries shown are demo change requests (CR-223, CR-221, CR-218) and escalations from PRJ-140/PRJ-104/PRJ-125 — none of ours. [Measured: `docs/PMO/meridian_portfolio_5.10.0.png`]

Half of this is ours: we ran `npm run seed` (the demo book) rather than `npm run reset-book`. Half is a question for them: the header carries a **PROGRAMME** filter set to "All programmes", and it is [Open] whether selecting `RBT` rescopes the five KPI tiles or only the register beneath them. Nothing we ran settles it.

**Why it matters anyway.** Also measured on that page: **OPEN RISKS 45**, while the register we loaded holds **122**. Whatever the tiles count, they do not count what our programme actually carries — and a sponsor reads tiles.

**By hand.** Every headline number on the executive page is discarded and the sixteen rows are read individually.

### G-6 · Sixteen projects reported GREEN in a week when two of four gate documents were refused

**Observed.** All sixteen: **Initiation · GREEN · "0% reported" · SPI — · CPI —**, and on the project page "no budget — outside EVM and cost roll-ups", "0% reported by the source system", "not measured on a budget-less project". [Measured: both screenshots]

In the same week, `docs/SESSIONS/WEEKLY_2026-09-08_product_owner.md` §2 records that the Security & Privacy Board did not accept SECURITY_PLAN v1.0, the Architecture Review Board did not accept DATA_FLOWS v1.0, and no number in the capacity model was accepted because none was presented — so Gate B was not convened. [Measured: that file]

**Why it matters.** Health is derived from schedule and cost. With no budget and no measured progress there is nothing to derive, and the value shown is **GREEN**, not "unknown". A portfolio tool whose default for an unmeasured project is the colour that means "fine" reports the opposite of the truth for every project that has not yet been instrumented — which is every project at the start, when the reporting matters most. This is M-07 unresolved (REQ-05 is `partial`: `PUT /api/v1/activities` carries `pct, source, measuredAt`, but the connectors are not built).

**By hand.** The weekly's honest status is written in the session packet in this repository. Meridian's green is not quoted anywhere.

### G-7 · No traceability, no test evidence, no CI

`gate_criterion` cites a document; there is no requirement, test-case or evidence-record object, and no link from anything to a commit, a PR or a CI run. [Source: the 52-table inventory; assessment M-06/M-07; REQ-04 delivered a criterion with a reviewer, not a traceability model]

This is why ADR-017 puts the engineering truth in the ledgers and why it should stay there. It is stated as a boundary, not a complaint: `docs/REQUIREMENTS_TRACEABILITY.md`, `docs/TEST_CASES/`, the control-quartet coverage and `docs/AUDIT_EVIDENCE_INDEX.md` answer "which test proves this control", and Meridian does not try to.

**By hand.** All of it — and correctly so.

### G-8 · The version we depend on is not released

`git tag` in the clone returns **11 tags, the newest `v5.9.0`**. `package.json` says `5.10.0`; the CHANGELOG has a `## [5.10.0] — 2026-09-08` section and `## [Unreleased]` says "Nothing yet"; the CHANGELOG's own rule is "Unreleased work sits under `## [Unreleased]` until it is tagged". Their register marks all thirteen requests `"released": false` and `"accepted": false`, with `channel.acceptance.released = "a version tag carries it"` and REQ-09 `remaining = "tags are pushed by a maintainer"`. [Measured: `git tag`, `package.json`, `CHANGELOG.md`; [Source] the register]

**Why it matters.** Every one of the twelve improvements this programme depends on sits on an untagged default branch. Our integration pins a commit hash. "Pin the Meridian commit" in `docs/PMO.md` §5 is not caution, it is the only option available.

### G-9 · Our own evidence of the loads is incomplete (ours, and it belongs in a report about evidence)

- The 5.9.0 file logs 76 meeting writes and no portfolio creations; it does not evidence the load it is named for (§1.1).
- `docs/PMO.md` §4 publishes "14 decisions and 21 open actions"; the file says 48 and 25 (§1.1).
- The third load (134 RAID items, 17 writes) has **no evidence file** (§1.3).
- No second-run log was kept, so "second run: no creating writes" rests on prose.
- The log lines are `"POST /api/raid -> 201"` — **no timing, no request body, no returned id**. The assessment's "under a minute" cannot be re-derived from the evidence, and a failed write could not be replayed.

A programme that refuses a gate because a document lacks evidence should not publish a load number it cannot re-derive. This is the finding in this report we are least comfortable with and it is entirely ours.

---

## 4. Cost of ownership, as measured

| Line | Measured | Note |
|---|---|---|
| **First hour, 5.9.0** | ~40 minutes lost to three setup defects | [Source: assessment §4] — an in-memory book, a non-recursive mkdir, a missing build |
| **First hour, 5.10.0** | Zero manual steps in code: `DEFAULT_PGLITE_DIR` (`env.js:29`), recursive mkdir (`env.js:82`), `scripts/dev.mjs`, regression test `server/test/firsthour.test.js` | [Source: read at `e352bc8`]. [Open]: we did not run a clean-clone first hour in this session; our working copy arrived seeded |
| **Test suite as an operator's confidence signal** | **513 pass / 101 suites / 0 fail / 123.7 s** (`real 2m3.9s`), re-run by us | [Measured] — 449 on 5.9.0 [Source]. A 14% growth in tests across one day of changes |
| **Schema surface** | 39 migrations, 52 tables | [Measured] |
| **The loader we had to write** | **358 lines of Python**, one third-party dependency (`httpx`), covered by `test/contract/test_meridian_sync.py` (43 lines, 2 tests: the ledger readers, the credential rule) | [Measured: `wc -l`] |
| **What the loader has to do because of the API shape** | Log in as a **human** (`POST /api/auth/login`); pull the **entire book** on `GET /api/bootstrap` and again after each structural phase (`refresh()` is called 5 times per run) to do its own client-side deduplication; encode identity in **titles** (`[O-11] …`, `D-0nn: …`, `H-nn: …`) because RAID, decisions and actions had no external id when it was written; match by exact string on `name`/`title`/`headline` | [Measured: `meridian_sync.py` lines 78-86, 120-121, 161-163, 202-215] |
| **Cost of a title-keyed identity** | Rewording a RAID item in `docs/RAID_LOG.md` creates a **duplicate** in Meridian rather than updating the row: `ensure_raid` matches on the `[O-nn]` prefix only, so the prefix saves us — but decisions and actions match on the **whole** string, so editing a decision headline in the ledger creates a second decision | [Measured: the same lines. Not yet triggered in a recorded load — [Open]] |
| **Cost of pinning a commit** | We depend on `e352bc8`, which carries no tag (G-8). Upgrading means diffing a default branch, not reading release notes; there is no supported version to report to an auditor, and no security-patch line to follow | [Measured: `git tag`] |
| **What a version upgrade did to our integration** | **5.9.0 → 5.10.0: zero changes required.** The same 358-line loader ran unmodified against 5.10.0 and produced 256 writes, all 2xx. Six migrations, a new write API, a configurable ladder and a decision register landed without breaking a single session route we call | [Measured: both sync logs; the loader is unchanged between `12a20a8` and `7d61bd1`] |
| **What the upgrade did *not* give us** | Also zero. We adopted none of the eight new `PUT /api/v1/*` routes, the programme ladder, the gate criteria or the decision register API. **Twelve improvements delivered in 84 minutes; nought adopted in our loader as of this commit.** The lag is entirely on our side | [Measured: the loader is byte-identical across the re-test commit] |
| **Operating for real** | Not paid. `docs/MISSING_ACTIONS.md` H-28 (a real instance: PostgreSQL, restore-tested backup, changed credentials, security policy) is **open**. Everything in this report was measured on a laptop-class PGlite instance seeded with a demonstration book | [Measured: H-28 open; the weekly §4 lists it among the twelve human acts outstanding] |

**The honest cost sentence.** Meridian cost us roughly one working day to evaluate, load, assess and re-test, and 358 lines of code to keep loaded. It has cost nothing to run, because we have not run it for real. The number that would matter to a PMO considering it — the cost of operating it as a system of record for a year — **we cannot report, because nobody has [Source: assessment M-08; Meridian's own committee record states it has never run a real portfolio for a year and has no vendor, backup or second instance].** This programme is the first real portfolio it carries, and it has carried it for one day.

---

## 5. Defect and gap list, in Meridian's terms

For their Product Owner's register. Each entry: what we did · what we observed · what we expected · why it matters to a real programme · how to reproduce from a clean clone. Suggested register ids continue from REQ-13. Severity is ours and advisory.

Reproduction preamble, common to all entries:
```
git clone https://github.com/mliad313sn/Meridian && cd Meridian && git checkout e352bc8
npm install && npm run seed && npm run build && npm run dev     # http://localhost:4173
```

---

### E-1 · A book created before `036` cannot be migrated onto a programme ladder — severity: high

- **What we did.** On 5.9.0 we created programme `RBT` and sixteen projects, then added `Gate A…F` as ordinary milestones. On 5.10.0 we re-ran the same loader.
- **What we observed.** Ten milestones on `RBT-GOV`; the project header reads "Gate 1 — Mandate is next"; Gate 1 badged AT RISK. Identical on both versions.
- **What we expected.** After `036` shipped, a documented way to say "this programme's ladder is A–F" and have the existing sixteen projects reflect it.
- **Why it matters.** `036`'s own header says an amended ladder does not rewrite existing projects — a deliberate and correct rule. But a real organisation adopts a portfolio tool with projects already in it. Without a migration path, every early adopter is permanently on the default ladder, and "which gate is next" is permanently wrong for them.
- **Reproduce.** `POST /api/admin/programmes {"id":"X","name":"X"}` (no `gateModel`) → create a project under X → four default gates. Now `PATCH /api/admin/programmes/X {"gateModel":[…6 gates…],"version":1}` → read the project's milestones: still the four. Nothing in the API or the UI reports that the project is on a ladder its programme no longer declares.
- **What would close it.** Either a migration act ("re-scaffold the ladder on N projects", audited, refusing where a gate is already accepted), or — cheaper — a read-side signal: expose `project.gateModelVersion` and flag projects whose ladder differs from their programme's.
- **We correct our own record here.** `docs/PMO.md` §5 and assessment §8 V-8 state that 5.10.0 scaffolds both ladders. It does not: `wbs.js:113-120` scaffolds one. The duplication in our book is our loader's. V-8 should be re-filed as this narrower request.

---

### E-2 · A first load cannot be done by an integration key — severity: high

- **What we did.** Wrote `scripts/meridian_sync.py` to load a programme from a repository of Markdown ledgers.
- **What we observed.** The run's first three writes are `POST /api/admin/sites`, `POST /api/admin/programmes`, 14 × `POST /api/admin/people` — none of which exists under `/api/v1`. The run therefore holds a session for a human account with `user.manage`, and all 256 writes are attributed to "System Administrator (admin)" in the audit trail and the This-week panel.
- **What we expected.** After REQ-02, an integration key with `write:portfolio` able to establish the structure it then populates — and an audit trail naming the integration, which `035` explicitly built.
- **Why it matters.** The value of REQ-02 is not the eight routes; it is that a machine writes as a machine. As shipped, the *first* load — the one that matters, the one a new adopter does — cannot use it at all, and every subsequent load has to keep the human credential alive anyway because ledgers grow new people. A field repository that stores a human admin password in CI is a worse security posture than the one it replaced.
- **Reproduce.** With an integration key scoped `write:portfolio`, attempt to create a site, a programme or a person under `/api/v1`. `grep -n 'r.put' server/src/routes/v1.js` → 8 routes, none of them structure. Then `PUT /api/v1/projects/EXT-1` referencing a programme that does not exist.
- **What would close it.** `PUT /api/v1/{sites,programmes,people}/:externalId` under a distinct scope such as `write:directory`, so that structure and delivery can be granted separately. Their register already knows this as D-33.4; we are recording what it costs a real integrator.

---

### E-3 · No value object is writable through v1; the first real programme's value page reads zero — severity: high

- **What we did.** Loaded 16 projects, 6 gates, 122 RAID items, 59 decisions and 28 actions by API. Attempted no benefit, because there is no route.
- **What we observed.** Status reporting → Value position: **BENEFITS PROMISED 0 · MEASURED 0 · ATTAINMENT — · MET — · PROMISING NOTHING 28**.
- **What we expected.** The same external-id, idempotency and audit rules for `business_case` and `benefit` as for `raid` and `milestones`.
- **Why it matters.** The asymmetry is the defect: delivery facts sync automatically and stay fresh; value facts must be typed by a human and go stale. That guarantees the executive page — the only page a sponsor reads — is the least trustworthy page in the product. Meridian already has the better half of a value model that most portfolio tools lack (`business_case` with expected cost, expected benefit, basis and a reconfirmation gate; `benefit` with kind, measure, unit, baseline, target, actual, owner, realisation date and a status separate from the measurement; a closure that refuses without a named benefits owner at `portfolio.js:370`). Not exposing it to integrations is what wastes it.
- **Reproduce.** `curl -H 'Authorization: Bearer <key with write:portfolio>' -X PUT $URL/api/v1/benefits/EXT-B1 -d '{...}'` → 404. Then `GET /api/v1/portfolio` → `counts.benefits` is present in the response body (`v1.js:57`). Readable, not writable.
- **What would close it.** `PUT /api/v1/business-case/:externalId` and `PUT /api/v1/benefits/:externalId`. This is V-1 in our register and it is the highest-value single line we have.

---

### E-4 · An unmeasured project is GREEN, not "not measured" — severity: high

- **What we did.** Created sixteen projects with `budget: 0`, `contingency: 0` and no progress reporting (our epics have no cost model yet — O-13 open on our side).
- **What we observed.** All sixteen: **GREEN**, "0% reported", SPI —, CPI —, "no budget — outside EVM and cost roll-ups", "not measured on a budget-less project". Portfolio tile: ON TRACK 82%. In the same week two of four gate documents had been refused by their boards and the gate was not convened.
- **What we expected.** A health state that distinguishes "measured and fine" from "nothing measured". The SPI/CPI cells already do this correctly — they show "—" and say why. Health does not.
- **Why it matters.** Every project is unmeasured at the start, which is when a portfolio office most needs to see that it is unmeasured. A default of GREEN converts absence of data into positive assurance, and it does so on the tile a sponsor reads. This is the one finding in this report that could mislead an executive rather than merely inconvenience an integrator.
- **Reproduce.** Create a project with `budget: 0` and no activity progress; read health on the register and the ON TRACK tile. Compare with the SPI cell on the same row, which correctly refuses to state a number.
- **What would close it.** A fourth health value — `UNMEASURED` / grey — set when neither schedule nor cost has a measurable input, counted separately in the ON TRACK tile ("23 green · 2 amber · 3 red · 16 not measured"). Cheap: it is a derivation, not a new object.

---

### E-5 · The version an adopter depends on carries no tag — severity: medium

- **What we did.** Pinned our integration to `e352bc8` and looked for the release it belongs to.
- **What we observed.** `git tag` → 11 tags, newest `v5.9.0`. `package.json` → `5.10.0`. `CHANGELOG.md` → a full `## [5.10.0] — 2026-09-08` section, and `## [Unreleased]` saying "Nothing yet". Their register: 13/13 requests `"released": false`; REQ-09 `remaining`: "tags are pushed by a maintainer".
- **What we expected.** REQ-09 ("release discipline: one version everywhere") delivered — and the OpenAPI/package drift really is fixed (`openapi.v1.json` info.version is `5.10.0`) — so a tag.
- **Why it matters.** An adopter cannot state which version they run to an auditor, cannot follow a patch line, and must diff a moving branch to upgrade. Their own acceptance rule says a request is `released` only when a tag carries it; by that rule **none of the twelve improvements is released**, including the release-discipline improvement.
- **Reproduce.** `git tag --list 'v5.10*'` → empty. `head -21 CHANGELOG.md` → the Unreleased rule. `python3 -c "import json;print(json.load(open('docs/requests/rt365.json'))['requests'][8])"` → REQ-09 with `released: false`.
- **What would close it.** `git tag -a v5.10.0` and a `verify.yml` check refusing a `package.json` version bump whose CHANGELOG section is not tagged within N commits.

---

### E-6 · [Open] Do the executive tiles rescope to a selected programme? — severity: medium, unverified

- **What we did.** Loaded our programme into a book that already held the seeded demonstration portfolio.
- **What we observed.** PORTFOLIO VALUE $51.3M, ON TRACK 82%, OPEN RISKS 45, Decisions owed 36 — all with the PROGRAMME filter on "All programmes". Our register alone holds 122 items, so 45 is not our count under any reading.
- **What we expected.** Selecting programme `RBT` narrows the five tiles as well as the register beneath them.
- **Why it matters.** A multi-programme instance is the normal case for a PMO. If the tiles are book-wide regardless of the filter, no programme director can read their own numbers, and the "no benefit stated" and "open risks" counts a Product Owner would act on are meaningless.
- **Reproduce.** Seed the demo book, load a second programme, select it in the PROGRAMME filter, compare the five tiles before and after.
- **[Open].** We did not run this. It is stated as a question, not a defect. Half the cause is ours: we should have used `npm run reset-book`.

---

### E-7 · [Open] A milestone marked done with a named accepter does not read as accepted — severity: low, unverified

- **What we did.** `PATCH /api/milestones/PRJ-147-M4 {"acceptanceCriteria": "...", "version": 1, "done": true, "acceptedBy": "<Product Owner id>"}` → **200**.
- **What we observed.** The project overview renders `Gate A` as **PLANNED**, "— · 08 Sep 26", with no accepter and no acceptance date, alongside Meridian's own gates which render owner, date and evidence count.
- **What we expected.** `portfolio.js:492-505` honours `done` and `accepted_by` and stamps `accepted_on`, and refuses `done` without a named accepter when criteria exist — so an accepted milestone should show as accepted, with the name.
- **Why it matters.** PM-04's whole point is that acceptance names a person. If it does not surface on the page where the gate is read, the control exists in the table and not in the room.
- **Reproduce.** Create a milestone, PATCH it with `acceptanceCriteria`, then PATCH `done: true` + `acceptedBy`, then `GET /api/bootstrap` and compare the milestone row with the project overview rendering.
- **[Open].** We did not re-query the row after the PATCH; the screenshot is our only evidence and may be rendering a different concept ("planned/actual" rather than "done"). Settled by one `GET`.

---

### E-8 · [Open] Does a decision or action written twice with the same text create two rows? — severity: low, unverified

- **What we did.** Keyed decisions on the whole headline string and actions on the whole title string (`meridian_sync.py:211,222`), because neither had an external id when the loader was written.
- **What we observed.** In the 5.9.0 log, 48 decisions and 25 actions were POSTed onto a **new** occurrence in a run that created no projects and no RAID — so the meeting half of the load is not idempotent across occurrences.
- **What we expected.** After REQ-02, `PUT /api/v1/decisions/:externalId` closes this for us. We have not adopted it.
- **Why it matters.** Not much to them, a lot to us — it is the clearest measure of the cost of a title-keyed identity, and it is the argument for their own external-id design.
- **[Open].** Whether re-posting the same headline into the *same* open occurrence duplicates is untested; our loader guards it client-side.

---

### E-9 · Request register: `accepted` cannot become true without us, and we have not said so — severity: process, for their PO

- **Observed.** All 13 requests carry `"accepted": false`. Their rule: `accepted` = "the requester said so on the issue".
- **Why it matters to them.** Their register is designed to close the loop with a named requester, and the loop is open on **our** side, not theirs. Nine of the twelve we can confirm from the code (§2, B-8); three we cannot confirm without adopting them (REQ-02 in a real integration, REQ-04 on a real gate, REQ-05 with a connector). We have not filed acceptance because filing upstream is a human act in this programme (H-31, open).
- **Suggested register mechanic.** Distinguish `accepted: false` ("requester has not answered") from `accepted: null` ("requester cannot answer yet — feature not adopted"). Today they read the same, and a Product Owner scanning the register cannot tell a silent user from a blocked one.

---

## 6. Concerns for the Product Owner

*(Ours — this programme's Product Owner. These are the things I would put on the table before the next gate, in the order I would raise them.)*

**PC-M-1 · We changed a supplier's roadmap in 84 minutes and we have no idea whether that was good.** Twelve findings we wrote before lunch were all delivered, across six migrations and a new public write API, before the afternoon. I record it as the strongest measured fact in this report and I also record that I cannot tell a fast maintainer from an unreviewed one from the outside. What I can measure is that the test suite grew from 449 to 513 and passes, and that the maintainer convened two counsellors on their own release and fixed 27 further findings the same day. What I cannot measure is whether any of it has been run by anyone but its author. Before we depend on Meridian for anything a gate reads — and today we depend on it for nothing a gate reads — I want that distinction settled, not assumed. It is not a criticism of the maintainer; it is the difference between a tool we like and a tool we are entitled to rely on.

**PC-M-2 · We published a number we cannot re-derive, and we would refuse a gate for that.** `docs/PMO.md` §4 states the first load put fourteen decisions and twenty-one actions on the weekly. The evidence file says forty-eight and twenty-five, and the ledgers at that commit agree with the file. The third load's "134 items, 17 writes" has no evidence file at all. This programme refused Gate B convening because two documents lacked what their boards asked for. I hold our own PMO record to the same standard and it fails: the numbers are in prose, the logs carry no timings and no bodies, and the file named for the first load does not contain the first load. I would like this corrected before the report goes anywhere, and I cannot correct `docs/PMO.md` myself — the write-scope guard refuses me that file, correctly.

**PC-M-3 · We called something a supplier defect that our own loader caused, in two published documents.** `docs/PMO.md` §5 and the assessment's V-8 say Meridian 5.10.0 scaffolds both gate ladders. It does not — `wbs.js` scaffolds one, chosen by the programme's `gate_model`, and `POST /api/admin/programmes` has accepted a `gateModel` since `036`. Our loader never sends it. Meridian's own answer to us said so plainly ("declare A–F on programme RBT, then create the epics") and we filed it as their defect anyway. That is the failure mode I am paid to prevent: a finding written from a screenshot instead of from the code. I want V-8 withdrawn and re-filed as the narrower, genuine request (E-1: a book created before the feature cannot be migrated), and I want the correction to be as visible as the original claim was.

**PC-M-4 · Twelve improvements were delivered for us and we have adopted none of them.** The loader is byte-identical before and after the upgrade. We still authenticate as a human admin, still encode identity in titles, still write through session routes, still push a constant 3×3 on every risk, still post actions with no owner and no due date, still leave the weekly open so the record is never frozen, and still create our six gates as ordinary milestones — which is why the gate-criteria feature we asked for, and got, cannot touch the six gates that actually govern this programme. The supplier turned our findings round in 84 minutes; we have taken none of them up in the working day since. The asymmetry is ours to answer.

**PC-M-5 · Meridian says this programme is green.** Sixteen projects, all GREEN, all 0%, in a week when two of four Gate B exit documents were refused by their own boards and the gate was not convened. The tool is not lying — health derives from schedule and cost, we gave it neither, and its default for nothing is green. But if anyone ever quotes the portfolio page instead of the session packet, they will report the opposite of the truth about this programme, in colour, to a sponsor. Until E-4 is fixed upstream or we stop feeding it budget-less projects, I would treat the Meridian portfolio view as **not quotable outside this room**, and I would rather say that out loud than discover it in a steering pack.

**PC-M-6 · The value page of the first real programme this tool carries reads zero, and that is partly a choice we made.** "Benefits promised: 0. Measured: 0. Promising nothing: 28 projects." Sixteen of those are ours. The proximate cause is that benefits are not writable through the integration API (E-3), so our loader cannot push one. The deeper cause is that this programme has not written its benefits down in a form anything could push. Profit is an objective and never a promise, and I would not want a number in that table that implies otherwise — but "we decline to state a benefit" and "we have not decided what benefit we are pursuing" look identical from outside, and only one of them is defensible at a gate.

**PC-M-7 · We are running a portfolio system on a laptop, seeded with someone else's demonstration data, and we have not paid the operating cost.** Every measurement in this report comes from a PGlite instance holding the demo book alongside ours; that is why the executive tiles report $51.3M of value we do not have. H-28 — a real instance on PostgreSQL, with a restore-tested backup, changed credentials and a written security policy — is open, and it is a human act. Until it is done, nothing in Meridian is a record; it is a rehearsal. I would rather we said that in the report than let "the first real portfolio it carries" imply more than one day on a laptop.

**PC-M-8 · We depend on an untagged commit of a single-maintainer project, and our own ADR says pin it.** No `v5.10.0` tag exists. By their own acceptance rule, none of the twelve improvements is released. That is survivable precisely because ADR-017 keeps the truth in the ledgers and the export path out is real (Apache-2.0, `GET /api/admin/archive`, 1,529 rows across 47 tables recovered on the first book). It stops being survivable the moment anything a gate reads moves into Meridian. I would like that line written into ADR-017 as a condition rather than left as a consequence — and I cannot write ADR-017 either.

**PC-M-9 · This report has no reviewer.** I wrote it, I own the RAID and decision ledgers it draws on, and the rule in this programme is author ≠ reviewer ≠ approver. Nothing here is certified, no evidence is declared complete, and no gate is convened by it. It needs a second line before it goes to Meridian's Product Owner, and filing it upstream is a human act (H-31), not mine to perform.

---

## 7. What this report did not verify

Named so that the next round can settle them, each with what would settle it.

| # | Not verified | What would settle it |
|---|---|---|
| 1 | A clean-clone first hour on 5.10.0, timed by us | `git clone && npm install && npm run seed && npm run build && npm run dev` on a fresh machine, with a stopwatch |
| 2 | Whether the executive tiles rescope to a selected programme (E-6) | Load two programmes into an empty book (`npm run reset-book`) and compare the tiles under each filter |
| 3 | Whether a milestone PATCHed `done` reads as accepted (E-7) | One `GET /api/bootstrap` after the PATCH |
| 4 | Whether a loader rewritten onto `PUT /api/v1/*` can complete a first load | Attempt it with an integration key; expect the first three writes to fail (E-2) |
| 5 | Whether declaring `gateModel` on `RBT` before creating projects yields six milestones and criteria-capable gates | A load into an empty book with `gateModel` in the programme body |
| 6 | Wall-clock duration of any load | Timestamps per request in the loader's log (G-9) |
| 7 | The 5.9.0 measurements (449 tests, the 40-minute first hour, the 1,529-row archive, `GET /api/audit` behaviour) | Not re-run by us; they are [Source: docs/PMO_MERIDIAN_ASSESSMENT.md] and rest on the earlier session |
| 8 | Whether Meridian's 5.10.0 changes have been exercised by anyone other than their author (PC-M-1) | Their register's `released` and `accepted` fields turning true, by someone |

## 8. Evidence index for this report

| Claim area | Evidence in this repository | Evidence in the Meridian working copy (`e352bc8`) |
|---|---|---|
| Timeline (§1) | `git log` on `claude/project-owner-agent-setup-hi3xqu`: `12a20a8`, `7b11f79`, `25b0483`, `7d61bd1`, `3628fcd` | `git log`: `77c4b49` (5.9.0), `b58f806`, `e352bc8` |
| Load 1 | `docs/PMO/meridian_sync_2026-09-08.json` (76 writes) | — |
| Load 2 | `docs/PMO/meridian_sync_2026-09-08_5.10.0.json` (256 writes) | — |
| Load 3 | *none* — G-9 | — |
| Screens | `docs/PMO/meridian_portfolio_5.10.0.png`, `meridian_project_5.10.0.png`, `meridian_meeting_5.10.0.png`, `meridian_decisions_5.10.0.png`, `meridian_raid_5.10.0.png`, `meridian_archive_5.10.0.png`; first-load: `meridian_portfolio.png`, `meridian_project.png`, `meridian_meetings.png` | — |
| The loader | `scripts/meridian_sync.py` (358 lines), `test/contract/test_meridian_sync.py`, `Makefile:64` | — |
| The decision to adopt | `docs/ADRs/ADR-017.md`, `docs/DECISION_LOG.md` D-049 | — |
| Ledgers loaded | `docs/RAID_LOG.md`, `docs/DECISION_LOG.md`, `docs/MISSING_ACTIONS.md`, `docs/BACKLOG.md` | — |
| The week's honest status | `docs/SESSIONS/WEEKLY_2026-09-08_product_owner.md` §2, §4, §5 | — |
| Their register | — | `docs/requests/rt365.json` (13 requests, `registerVersion` 2) |
| Write API surface | — | `server/src/routes/v1.js:100-107`, `server/src/v1write.js`, `docs/openapi.v1.json` (12 paths, v5.10.0) |
| Gate ladder | — | `server/migrations/036_gate_ladder.sql`, `server/src/wbs.js:113-120`, `shared/engine.js:76-108`, `server/src/routes/admin.js:22,632` |
| Gate criteria | — | `server/migrations/037_gate_criteria.sql`, `server/src/routes/portfolio.js:3360-3430` |
| Benefits and closure | — | `server/src/routes/portfolio.js:370-377, 1804-1912` |
| Milestone acceptance | — | `server/src/routes/portfolio.js:478-523` |
| Meeting actions | — | `server/src/routes/meetings.js:591-614` |
| First hour | — | `server/src/env.js:29,76,82`, `server/test/firsthour.test.js` |
| Test run | — | 513/513, 101 suites, 123.7 s, this session |
| Release state | — | `git tag` (11, newest `v5.9.0`), `package.json` `5.10.0`, `CHANGELOG.md:19-25` |
