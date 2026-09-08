# Meridian IT-PMO — field round 2: an empty book, the whole programme, and what it cost

**From:** the Program Orchestrator of Global AI-MCP RoboTrader (RT365).
**Purpose:** the measured half. A separate session writes the letter to Meridian's Product Owner from this.
**Not filed upstream.** Filing is a human act (H-31, open). Nothing here was sent to anyone.

| Owner | Reviewer (different line) | Approving body | Status |
|---|---|---|---|
| Program Orchestrator | *not assigned — this document is not reviewed* | Product Owner (D-039) | v1.0 — 2026-09-08 |

**Commissioned path refused.** This was commissioned as `docs/PMO/round2/`. `scripts/agent_guard.py`
refuses that path to this role, verbatim: `agent_guard: agent 'program-orchestrator' may not edit
docs/PMO/round2/GUARD_PROBE.md; owned paths: … docs/REPORTS/`. All round-2 evidence is therefore in
`docs/REPORTS/PMO/round2/`. It was not routed around through Bash. Moving it is an act for a role
that owns `docs/PMO/` (`GUARD_PROBE.md`). [Measured]

**Tags.** `[Measured]` = we ran it, with the file that holds the request and the response.
`[Source: path:line]` = their code, read at the commit named. `[Open]` = not verified, with what
would settle it. Nothing is untagged. No Meridian capability is asserted that was not seen in its
code or its behaviour. Nothing here promotes an environment, states a return or promises anything.

---

## 0. The headline, in four sentences

1. **The current default branch of Meridian is 5.9.0, and none of the twelve improvements it built
   for us is on it.** They live on an unmerged branch. Round 1 reported them as shipped; on the
   evidence of a fresh clone today, they are not shipped, they are *pushed to a branch*. [Measured]
2. On an **empty book** with **only our programme**, the executive page reads
   **ON TRACK 100% · 16 green · 0 amber · 0 red · SCHEDULE INDEX 1.00 "at or ahead of plan" ·
   COST INDEX 1.00 "inside the envelope"** — in a week when two Gate B exit documents were refused
   by their boards and no gate was convened. Round 1's most important finding is not only still
   true, it is **worse without the demonstration data diluting it** (round 1: 82%). [Measured]
3. **Almost everything else worked.** 307 loader writes and 334 hand-driven requests, median 16 ms,
   no server error; the six gates that actually govern this programme now carry 54 criteria found
   met by a *named independent reviewer*; the weekly was opened, minuted, **closed and frozen**, and
   the next occurrence scheduled itself; the register carries a real probability × impact
   distribution instead of round 1's constant 3×3; 85 decisions, 19 of them as decision records with
   alternatives, dissent, council and provenance. [Measured]
4. **Two things round 1 blamed on Meridian were ours, and one of them is still ours.** The
   duplicated gate ladder is entirely our loader's — and it got *worse* this round (12 milestones
   where 6 were meant), because our loader names the ladder gates one way and the milestones
   another. The `$51.3M` executive tile was the demonstration book we failed to remove. Both are
   corrected in §7. [Measured]

---

## 1. The instance and the version tested

### 1.1 What a fresh clone of the default branch gives you today

```
git clone https://github.com/mliad313sn/Meridian    # 2026-09-08
git rev-parse HEAD            → 77c4b49aecacf3e3b4e3792c52939b2e51d38d76
git log -1 --date=iso HEAD    → 2026-09-01 10:30:31 +0000
                                "Comité de recette des processus — le parcours, et ce qu'il a trouvé (5.9.0)"
node -p require('./package.json').version → 5.9.0
git symbolic-ref refs/remotes/origin/HEAD → refs/remotes/origin/main
git log --oneline e352bc8..HEAD → (empty)
```
[Measured] The last line is empty **because `main` is an ancestor of `e352bc8`, not because nothing
has shipped.** The default branch has not moved since 2026-09-01.

### 1.2 Where the twelve improvements actually are

```
git ls-remote https://github.com/mliad313sn/Meridian
  77c4b49…  refs/heads/main
  cbe99ef…  refs/heads/claude/meridian-rt365-feedback-d6vo3i
git log --oneline main..origin/claude/meridian-rt365-feedback-d6vo3i
  cbe99ef 2026-09-08 Claude :: The tag boundary, established a fourth time, with the maintainer's command
  125d16c 2026-09-08 Claude :: RT365 re-tested 5.10.0 and filed twelve more: V-1..V-12 read in as REQ-20..REQ-31
  a5ba655 2026-09-08 Claude :: The committee reviews 5.10.0 as built, and stops the tag five times
  f5e0635 2026-09-08 Claude :: The review is scheduled, and the tag waits on a maintainer (D-33.18)
  985d6af 2026-09-08 Claude :: Third re-read of RT365 — a request with no id (REQ-14, 5.10.0)
  e352bc8 2026-09-08 Claude :: Second round of the RT365 return — what two counsellors found, fixed (5.10.0)
  b58f806 2026-09-08 Claude :: Le retour de terrain RT365 — douze lignes prises, un Product Owner nommé (5.10.0)
git tag | tail -1 → v5.9.0
```
[Measured] Seven commits, all authored `Claude <noreply@anthropic.com>` on 2026-09-08, **not merged
to `main`, and not tagged.** Their own release rule is that a request is `released` only when a tag
carries it, and their register still says `released: false` for all 31. Round 1's E-5 stands and is
now sharper: it is not only untagged, it is **unmerged**, so the version an adopter gets by
following the README is 5.9.0 with none of the twelve.

### 1.3 Have they shipped since we last looked, and does it answer anything we filed?

Yes, five commits after `e352bc8`. `git diff --stat e352bc8 cbe99ef` → 31 files, +1706/−144, two new
migrations. [Measured]

| What changed | Answers what we filed? |
|---|---|
| `040_milestone_basis.sql` — `milestone.date_basis` / `condition`; placeholders never read as MISSED; `gateStatus` gains `Unscheduled` | **Yes.** REQ-14, raised from our **D-057**. Their `answerToSource`: "D-057's placeholders can be typed as `dateBasis: placeholder`". Status `done`. [Source: `docs/requests/rt365.json`] |
| `041_decision_versioned.sql` — `row_version` on decisions | Housekeeping for REQ-07 |
| `docs/requests/rt365.json` `registerVersion` 2 → **6**, 13 → **31** requests | **Yes, as a register.** Our **V-1..V-12 were read in as REQ-20..REQ-31**, verbatim, with our acceptance criteria as their `remaining`. |
| `v1write.js` +178, `rbac.js` +40, `writeapi.test.js` +112, `gates.test.js` +55 | REQ-14/REQ-15 groundwork |

**But:** REQ-20..REQ-31 (our V-1..V-12) are every one of them `status: "open"`, `delivered: []`.
REQ-15..REQ-19 (from a "third round" integrator) are also all `open`. So the answer to "does it
answer anything we filed" is: **it answers one line (REQ-14, from D-057) and it registers twelve
more without delivering any of them.** [Measured: the register, parsed]

### 1.4 The two instances actually stood up

| | Instance A | Instance B |
|---|---|---|
| What it is | the default branch — what an adopter gets | the unmerged branch — where the twelve live |
| Commit | `77c4b49` (`main`) | `cbe99ef` (`claude/meridian-rt365-feedback-d6vo3i`) |
| `package.json` | 5.9.0 | 5.10.0 |
| Migrations | 33 | 41 |
| Book | demo seed (in memory — see §2) | **empty** (`npm run reset-book`) |
| Port / data | 4173, no persistent dir | 4183, `server/.data/pgdata` (31 MB) |
| Used for | the first hour, and to prove M-01/M-03 are alive | the whole programme drive |

Instance A was stopped after the first hour. The previous round's instance was stopped first, by pid
from its pid file (`6531`, plus its children `6549`/`6556`); no pattern kill was used. [Measured]

**Their clone was not modified.** `npm install`, `npm run seed`, `npm run reset-book`, `npm run
build` and a `git worktree` checkout of a published ref are the only things done to it. No file was
edited, nothing was committed, nothing was pushed.

---

## 2. Test counts, verbatim

```
=== instance A (main 77c4b49, 5.9.0) npm test exit=0 elapsed=111s ===
# tests 449          # suites 80    # pass 449   # fail 0
# cancelled 0        # skipped 0    # todo 0     # duration_ms 110965.903869

=== instance B (cbe99ef, 5.10.0 unmerged branch) npm test exit=0 elapsed=134s ===
# tests 520          # suites 102   # pass 520   # fail 0
# cancelled 0        # skipped 0    # todo 0     # duration_ms 133619.726821
```
[Measured: `test_counts.txt`, `npm_test_*_summary.txt`] `not ok` lines on B: **0**.

`npm install`: 161 packages, 162 audited, **1 moderate severity vulnerability**, on both. 6 s and 3 s
(warm npm cache; not a cold-network figure). `npm run build`: exit 0, "built in 1.52 s". [Measured]

`README.md:89` on `main` says `npm test  # 413 tests`. Measured: 449. A small doc drift, and it is on
the branch an adopter reads. [Measured]

---

## 3. The first hour, exactly — every step the documentation did not name

### 3.1 Instance A: the documented quick start, on the default branch, verbatim

The README says (`README.md:9`): "`npm install && npm run seed && npm run dev` and it is running on
your machine in about a minute", and (`:70-71`) `npm run dev  # http://localhost:4173`.

```
$ npm run seed
  … migrated 001…033 …
  seeded 12 projects · 10 users · 7 meeting series        exit=0, 4 s
$ ls -la server/.data
  ls: cannot access 'server/.data': No such file or directory
$ npm run dev
  Meridian IT-PMO listening on http://localhost:4173  (pglite)
$ curl -o /dev/null -w '%{http_code}' http://localhost:4173/
  404      Cannot GET /
$ curl -X POST …/api/auth/login -d '{"email":"admin@meridian.example","password":"meridian-admin-2026"}'
  401
```
[Measured: `firsthour_A_main_5.9.0.txt`]

**The seed reported success and wrote nothing to disk.** The cause, in their code at `77c4b49`:
`server/src/db.js:152` `const pglite = dataDir ? new PGlite(dataDir) : new PGlite();` and `:226`
`openPglite(opts.dataDir ?? process.env.PGLITE_DIR ?? null)`. Nothing in `server/src/` loads a
`.env`; `.env.example:4` sets `PGLITE_DIR=./server/.data/pgdata` and is not loaded by anything.
[Source] So the seed built a book in memory, the process exited, and the server started empty — and
the login failed with the *published* password because the account it seeded no longer exists.

**M-01 and M-03, reported on 2026-09-08 and fixed the same day, reproduce verbatim on the default
branch, because the fix was never merged.** This is the first-hour test round 1 said it had not run
on a clean clone (§7 item 1). It is now run, and it fails.

**Manual steps a newcomer must take that the documentation does not name** (instance A):
1. `export PGLITE_DIR=…` or create a `.env` **and load it yourself** — otherwise the book is lost.
2. `mkdir -p server/.data` — `PGlite`'s `mkdirSync` is not recursive at this commit.
3. `npm run build` before `npm run dev` — otherwise the documented URL is `Cannot GET /`.

### 3.2 Instance B: an empty book, a changed password, a free port

| # | Step | Result | Documented? |
|---|---|---|---|
| 1 | `npm install` | 3 s, exit 0 | yes |
| 2 | `npm run seed`, **no `.env`, no `PGLITE_DIR`** | migrations 001–041; `server/.data/pgdata` 31 MB on disk | yes — and REQ-01 makes it true |
| 3 | `npm run reset-book` | `cleared 2 stale lock file(s) from a previous run` · `Book reset. Removed 12 projects / 8 sites / 28 people; 1 active account(s) remain.` | partly — **the README does not say you must seed first**; `reset-book` keeps `app_user` and needs the admin to already exist |
| 4 | `npm run build` | 1.52 s | yes |
| 5 | `PORT=4183 node server/src/index.js` | boot printed the data directory **and** `! 1 demonstration account(s) still open with the published password — change them from Administration before this instance carries anything real`; `GET /` → **200** | port choice is **not** documented; the README names only :4173 |
| 6 | `POST /api/auth/login` with the published password | 200, `mustChangePassword: true` | yes |
| 7 | `POST /api/auth/password {"current":…,"new":…}` | **400** `Current and new password are both required` | **no** — the field is `next`, not `new` (`server/src/routes/auth.js:203`). There is no OpenAPI for session routes; I had to read the source. |
| 8 | `POST /api/auth/password {"current":…,"next":…}` | 200 `{ok:true}`; old password → **401**; new password → **200**; `/api/admin/posture` → `demoAccountsLive: []` | — |

[Measured: `firsthour_B_branch_5.10.0.txt`] Elapsed for the whole of instance B's first hour,
excluding the test run: **about six minutes**, of which the only lost time was step 7.

`GET /api/health` on the empty book:
`{"ok":true,"version":"5.10.0","build":"sources","engine":"pglite","instance":{"org":"MERIDIAN","id":null,"migrations":41},"backup":{"lastDrillAt":null,"lastAttemptAt":null,"ok":null}}`
— REQ-06's instance identity and last-proven-restore are there, and honestly `null` because we have
run no drill. [Measured]

---

## 4. What we drove in, and by which route

`scripts/meridian_sync.py` is our base loader. It is **not in this role's write scope**, so it was
run unmodified. Everything beyond it was done by hand through the session API, with every request
recorded with a timestamp, a status code, a duration and both bodies.

### 4.1 The loader, run twice

| Run | Requests | Wall | Composition | Result state |
|---|---|---|---|---|
| 1 | **307**, all 2xx | 8,231 ms | 165 `POST /api/raid` · 66 `POST …/decisions` · 29 `POST …/actions` · 16 `POST /api/projects` · 14 `POST /api/admin/people` · 6 `POST /api/milestones` · 6 `PATCH /api/milestones/{id}` · 1 each site, programme, series, occurrence, open | 16 projects, **165 RAID**, 12 milestones on RBT-GOV |
| 2 | **1**, a 200 | 1,367 ms | `POST /api/meetings/series/{id}/occurrences` → 200 (the occurrence for today already exists) | unchanged |

[Measured: `load_1_meridian_sync_run1.json`, `load_2_meridian_sync_run2.json`]

**What the second run writes: nothing.** One request, a 200, no creations, no updates. The
portfolio *and* the meeting are idempotent — an improvement on round 1, where a second run re-posted
every decision and action onto a fresh occurrence. The reason is that the occurrence is keyed by
date; **on a different day the loader would open a new occurrence and re-post all 66 decisions and
29 actions**, because `existing_decisions()` only looks at the current occurrence
[Source: `scripts/meridian_sync.py:existing_decisions`, `open_occurrence`]. That latent defect is
ours and is unchanged.

### 4.1b A third run, after the record was frozen — the loader stops

Run three, after the hand drive and after the weekly was closed:

```
POST /api/meetings/occurrences/MS-SUWK22-20260908/decisions -> 409:
  {"error":"This meeting is closed — its decisions are final"}
exit=1, 1,246 ms
```
[Measured: `load_4_meridian_sync_run3_aborted.txt`]

**Why, exactly, and it is not a Meridian defect.** Between run 1 (16:00) and run 3 (16:22) this
repository's `docs/DECISION_LOG.md` gained three rows — **D-067, D-068, D-069** (commit `c18e3a5`,
16:06, written by another session working in the same tree, §15). The loader correctly saw three
decisions it had not yet published, re-opened the day's occurrence — which now returns the **closed**
one — and posted into it. Meridian refused, exactly as it should. `meridian_sync.py::_write` aborts
on the first status ≥ 300, so the whole run stopped.

**And it wrote nine rows before it stopped.** The register ledger also grew during the session; run 3
posted **9 of the 10 new RAID rows**, then hit the decision 409 and aborted. Meridian's tagged rows
went 165 → 174 while the ledger's open rows went 165 → 175. `meridian_sync.py` writes its `--json`
evidence file **only on success**, so a partial load leaves the book changed and produces **no
evidence file at all** — round 1's own gap G-9 recurring in a new form, and ours. [Measured:
`GET /api/bootstrap` before and after]

**The consequence a real integrator must plan for:** *the day the record is frozen is the day the
one-way loader stops being able to land new facts.* Our loader has no notion of a closed occurrence
and no route to the next one. This is our defect, and it is the exact shape of Meridian's own
**REQ-16 — "raise an action into the next scheduled occurrence, without opening it"** — registered,
`status: open`, `answerToSource: "D-33.14 holds: the API still never OPENS a meeting."`
Freezing the record and keeping a one-way sync alive are, today, in tension.

### 4.2 The hand drive and the probes

**334 requests · median 16.1 ms · p95 104.8 ms · max 204.1 ms · 8.3 s of server time.**
Statuses: `200: 237 · 201: 55 · 400: 17 · 404: 13 · 409: 10 · 428: 2`. No 5xx, no transport failure.
[Measured: `load_3_hand_drive.json`, `probe_1.json`, `probe_2.json` — every request has
`at`, `method`, `path`, `request`, `status`, `ms`, `response`, `note`]

Slowest calls, all reads: `GET …/minutes` 204 ms, `GET …/occurrences/{next}` 176 ms,
`GET …/pack` 149 ms, `GET /api/bootstrap` 141 ms.

### 4.3 What went in, object by object

| What | Count | Route | Surface | Note |
|---|---|---|---|---|
| Site, programme (with the **A–F ladder**), 14 people | 1 / 1 / 14 | `POST /api/admin/{sites,programmes,people}` | **session only** | not in v1 — §5 D-5 |
| Projects: 15 epics + governance | 16 | `POST /api/projects` | session | v1 route exists |
| Gate milestones | 6 by us, **96 by Meridian** | `POST /api/milestones` + the ladder | session | §6 |
| RAID register | **165**, then re-rated | `POST /api/raid`, `PATCH /api/raid/{id}` | session | real P×I, §4.4 |
| Decisions in the room | 66 | `POST …/occurrences/{id}/decisions` | session | the loader's route |
| **Decision records** | **19** | `POST /api/decisions` | session (v1 route exists) | alternatives, dissent, council, provenance, ratifiedBy — §4.5 |
| Actions | 29 raised, **15 given a real owner, 1 a real due date** | `PATCH /api/meetings/actions/{id}` | session | §4.6 |
| **Gate criteria** | **54 on RBT-GOV** (517 book-wide), **7 found met by a named independent reviewer** | `POST/PATCH /api/criteria` | session | §4.7 |
| **Business cases** | **3** (RBT-GOV, E13, E11) | `PUT /api/projects/{id}/case` | **session only** | **404 on v1** |
| **Benefits** | **7** | `POST /api/benefits` | **session only** | **404 on v1** |
| Case reconfirmation at Gate A | 1 | `POST /api/projects/{id}/case/reconfirm` | session only | §5 D-2 |
| Stakeholders | 7 | `POST /api/stakeholders` | session only | interest/influence/attitude/engagement |
| Communication plan | 3 | `POST /api/comms` | session only | audience, purpose, channel, frequency, next date |
| Lessons | 2 of 3 | `POST /api/lessons` | session only | **the third was refused** — §5 D-1 |
| Tolerance | 1 (14 d / 0 % / 10 pt, then 1/1/1) | `PUT /api/projects/{id}/tolerance` | session only | |
| Change request | 1, four steps signed | `POST /api/change`, `…/approve` | session only | §6.4 |
| Work items | 3 | `POST /api/workitems` | session (v1 route exists) | |
| Rollout waves | **1 of 3** | `POST /api/waves` | session only | **two refused** — §5 D-3 |
| Meeting: open → agenda → attendance → minutes → **close** | 1 | `POST …/close` | session only | §6.2 |
| Exceptions | **0** | — | — | none raised itself — §5 Q-2 |

### 4.4 The RAID rating — answering our own criticism honestly

Round 1 pushed a hard-coded `p: 3, i: 3` on all 122 items and reported it as our own worst finding.
The brief asked for "real probabilities and impacts where the ledger states them".

**`docs/RAID_LOG.md` states neither.** Its columns are `ID | Type | Item | Owner | Needed by |
Status`; a grep for probability/likelihood/exposure returns four incidental prose hits and no
column. [Measured] Inventing numbers would be worse than a constant, so P and I were **derived by a
published rule from fields the ledger does state**, and every item now carries that sentence in its
own `detail` so nobody reading Meridian can mistake it for a measurement:

> `P=4 I=4 target 2x3 DERIVED by rule R2-PI-1 from the stated Type=Gap, Status=Open, Needed by=Gate B.
> docs/RAID_LOG.md states no probability and no impact.`

Rule R2-PI-1 (`drive.py::derive_pi`): probability from `Status` (Reopened 5, Open 4, Partial 3,
Remediated/Decided/Closed 2); impact from `Type` (Risk/Issue 4, Gap/Dependency 3, Assumption/
Observation/Decision 2) **+1** where the stated `Needed by` gate is A, B or C; residual target one to
two notches lower; `gate` set from the stated gate; review date 14 days if p ≥ 4, else 42.

Result — **eight populated cells instead of one**, and the tool's own escalation arithmetic now says
something: `3×3: 5 · 3×4: 12 · 3×5: 19 · 4×2: 1 · 4×3: 35 · 4×4: 73 · 4×5: 19 · 5×4: 1`.
Meridian derived from it, unprompted: **113 at steering level · 54 at PMO level**, response mix
Mitigate 40 / Monitor 33 / Fix 94, highest exposure 25, and five escalated dependencies on the
weekly agenda. [Measured: `03_raid_register.png`, `08_programme.png`]

**Open, and ours:** `docs/RAID_LOG.md` has no probability, impact, residual-target or review-date
column. Until it does, the only honest rating in Meridian is a derived one. Recorded as a RAID entry
in §9; I am not permitted to edit `docs/RAID_LOG.md` this round.

### 4.5 The decisions, as decision records

`GET /api/decisions/log?limit=500` → **85 decisions**: 66 `kind: "meeting"` (the loader's) and
**19 `kind: "standalone"`** written to `POST /api/decisions`, the object migrations 034/039 built for
us. All 19 carry alternatives, dissent and provenance; 18 carry a council. One example, read back:

```
id: DEC-086   headline: "D-057: O-17: roadmap form — gate-driven sequencing …"
alternatives: "Fixed calendar now (rejected: no basis); no roadmap until Gate C (rejected: the owner's acts need dates)"
dissent:      "(rejected: no basis) · (rejected: the owner's acts need dates)"
council: "Product Owner"   provenance: "[Committee] / [Open: O-17 residual → ROADMAP v1.1 …]"
status: "Ratified"   ratifiedBy: "Product Owner (human), per D-039"   decidedOn: 2026-09-08
```
[Measured]

**19 of the 28 D-039..D-066, not 28.** The other nine (**D-058..D-066**) have only five columns in
`docs/DECISION_LOG.md` — no Provenance, no Evidence — where D-039..D-057 have seven. That is a
defect in **our** ledger, found by driving it into a tool that has the fields. `supersedes` was
therefore never exercised (the probe depended on D-064 being present): **[Open]**.

### 4.6 The actions

29 open human acts. **15 were given the ledger's own owner**; 14 could not be, because their stated
owner is a body and not a person: `Executive Steering`, `Finance + Privacy`, `Finance + Broker-
Connector`, `Finance + Legal`, `Trading Risk Committee`, `Support & Training Lead`, `C&L Committee`,
`Trading Risk Committee + Exec Steering` … Meridian's `meeting_action.owner_id` is a foreign key to
`person`; there is no committee owner. **One** action carried a parseable due date (H-03,
2026-09-08), and Meridian immediately rendered it `due 08 Sep 26 · OVERDUE` on the agenda and put it
first. The other 28 read "no date". [Measured: `04_meeting_frozen.png`]

Both halves are ours: our ledger names committees where the tool wants people, and 28 of our 29 open
acts have no date. That is a finding about this programme, not about Meridian.

### 4.7 The gates — the thing round 1 could not do at all

Round 1's G-2 was that our six gates were plain milestones, so `gate_criterion` (which binds to a
ladder position, `CHECK (gate BETWEEN 1 AND 12)`) could not touch them. With the ladder declared on
the programme, our gates **are** positions 1..6, and the criteria bind:

- **54 criteria on RBT-GOV**, by gate `1:7 · 2:9 · 3:8 · 4:9 · 5:8 · 6:13`; 517 across the book.
- **7 found met**, each stamped `reviewedBy: PE-42` (Independent Validation Agent),
  `reviewedOn: 2026-09-08`.
- The page renders `CRITERIA FOR GATE D — SUPERVISED PILOT · 0/9 FOUND MET`,
  `CRITERIA FOR GATE E — CAPPED AUTONOMY · 0/8 FOUND MET` — **our gate names, our ladder.**
- `POST /api/criteria {"gate": 7}` → `400 A criterion belongs to a gate 1..6 of this project's
  programme`. The ladder is respected exactly.

[Measured: `probe_2.json` Q1, `02_project_governance.png`]

---

## 5. What it refused, what it silently dropped, and what we could not express

### 5.1 Refusals that are controls working (positive)

| Attempt | Response |
|---|---|
| Find a criterion met with **no** `reviewedBy` | `400 Finding a criterion met needs reviewedBy — the named person who checked it` |
| Find a criterion met by `PER-NOBODY` | same 400 — an invented reviewer is not a reviewer |
| Criterion at gate 7 of a six-gate ladder | `400 A criterion belongs to a gate 1..6 of this project's programme` |
| Add a decision to the **closed** meeting | `409 This meeting is closed — its decisions are final` |
| Raise an action into the closed meeting | `409 This meeting is closed` |
| Edit with a stale `version` | `409 Someone else changed this record — reload and try again` |
| Edit with **no** version | `428 This … edit did not say which version it is based on` |
| Second `POST /api/change/{id}/approve` after the chain completed | `409 This request is already decided` |
| An unknown integration scope | `400 Unknown scope(s): … Known: read:portfolio, read:audit, write:portfolio, write:meetings` |

[Measured] Every one of these is a control we would want. The optimistic-concurrency 409s in our own
logs are re-run artefacts of our driver, not defects.

### 5.2 Refusals that are defects — see §8 for reproductions

- **`POST /api/lessons {"gate": 5}` → `400 A gate is 1, 2, 3 or 4`** on a six-gate ladder (D-1).
- **`POST /api/projects/{id}/case/reconfirm {"gate": 6}` → `400 Reconfirmation happens at a gate —
  1 to 4`** (D-2).
- **`POST /api/waves` second wave to the same site → `409 That record already exists`** (D-3).
- **Thirteen collections `404 No such endpoint` on the v1 write API** (D-4, D-5).
- **`PATCH /api/criteria/{id} {"externalRef": {...}}` → `400 Nothing recognisable to change`** —
  a criterion takes a `document`, never a typed external reference to a commit or a checksum (D-8).
- **`POST /api/decisions {"evidenceUri": "docs/PRODUCT_OWNER.md v2.0; GOAL.md …"}` → `400 The
  evidence link is an http(s) address`.** Our evidence is repository paths and commits. A
  self-hosted PMO sitting beside a git repository cannot cite it (D-8, same root).

### 5.3 What it accepted and silently dropped

Two, and both are the same class as **REQ-19**, filed by another integrator and still open:

1. **`PATCH /api/projects/{id}/health {"health": "U", "note": "…", "version": n}` → `200
   {"version": 3}`.** The recognised field is `rag` (`portfolio.js:333`), and the allowed values are
   `G|A|R`. An unknown field was accepted, an audit row was written saying **"Project status returned
   to automatic"**, and the thing the caller asked for did not happen. A caller who does not diff the
   response believes they set a status. [Measured]
2. **`POST /api/meetings/occurrences/{id}/attendance {"present": [3 ids]}` → `200 {"ok": true}`**,
   audited "**0 present of 0**". The recognised shape is `{attendance: [{personId, state}]}`
   (`meetings.js:501`). The attendance list stayed empty and the frozen record now says nobody was
   in the room. [Measured: `probe_2.json` Q3 `attendance: []`]

Both are ours in the sense that we sent the wrong field. Both are Meridian's in the sense that a
write API which returns 200 for a body it did not understand cannot be integrated against safely —
which is exactly what REQ-19 says, in their own register, unaddressed.

### 5.4 What we could not express at all

| We wanted to say | Why we could not |
|---|---|
| A probability and an impact that are **stated**, not derived | **Ours.** `docs/RAID_LOG.md` has no such columns. |
| "This control is proven by test TC-RK-018, in commit `b912249`, run by CI" | **Meridian's boundary.** No requirement, test-case or evidence object; no link to a commit, a PR or a CI run. M-06/M-07 stand and ADR-017 is right to keep this in the ledgers. |
| Evidence as a repository path or a commit hash | `evidence_uri` must be `http(s)`; criteria cite a `document` row. V-10/REQ-29, open. |
| An action owned by a **committee** | `meeting_action.owner_id → person`. 14 of 29 of our acts. |
| A benefit that deliberately states **no number** | The schema allows null baseline/target, but the value page then reads identically to "promising nothing" — and 13 of our 16 projects do read that way. |
| A project health meaning **"not measured"** | `G|A|R` only. §6.1. |
| A **cost** in the business case | **Ours.** O-13 (cost model) is open; a figure here would be invented. We left it null deliberately and said so in the `basis`. |
| A **superseding** decision | Our own D-058..D-066 rows are too short to load, so the predecessor was absent. **[Open]** |

---

## 6. What Meridian did on its own

This is the section that changed most from round 1, and it is the strongest thing in the report.

### 6.1 It built most of the book from one declaration

We wrote **one** `POST /api/admin/programmes` carrying the A–F ladder and its exit-evidence strings,
and 16 `POST /api/projects`. From that, with no further instruction, Meridian created:

- **96 milestones** — six gates on every one of the sixteen projects, named `Gate A — Discovery` …
  `Gate F — Market release`, dated from the `at` fractions we gave;
- **517 gate criteria** — it split our exit-evidence sentences into criteria per gate per project
  (`Approved charter`, `Personas`, `Jurisdiction hypothesis`, `Measurable outcomes …`);
- **96 documents** — one evidence document per gate per project, `DRAFT`, owner = the project's lead;
- **128 activities** and 16 allocations.

[Measured: `GET /api/bootstrap` counts before any hand drive] Our loader made 307 writes; the tool
made roughly 850 rows from six lines of ladder. That is the single best return on effort we saw.

### 6.2 It ran the meeting

- Generated an agenda from portfolio state: **7 sections, 58 items**, "26 of 25 minutes allocated",
  with the printed rule "Sections with nothing to report are left out rather than shown empty".
  Sections: Actions carried forward 29 · Decisions requested 7 · Milestones 6 · Risks & issues for
  escalation 5 · Register items due for review 6 · Resource pressure 1 · Next up 4.
- Marked H-03 **OVERDUE** from the one due date we supplied, and put it first.
- On `POST …/close`: **froze the agenda** (`frozen: true`), stamped
  `closedAt 2026-09-08T16:04:41.840Z`, `closedBy U-ADMIN`, kept our closing note, produced a
  **38,806-character** minute, and **scheduled the next occurrence itself** —
  `MS-SUWK22-20260914`, 14 Sep 2026, with the agenda already built.
- The page then reads: **"CLOSED · Frozen — this is the record · The pack is frozen: it reads today
  exactly as it read in the room, and it can be produced again."**

[Measured: `probe_2.json` Q3, `04_meeting_frozen.png`] Round 1 left the room in session and froze
nothing. That gap is closed, and it was ours.

### 6.3 It computed governance from our data

Escalation bands and "heard by" levels from the derived P×I (113 steering / 54 PMO); response mix;
highest exposure 25; five escalated dependencies onto the agenda; "DECISIONS OWED 130, 113 urgent";
"VALUE PROMISED 7 · 13 project(s) promise nothing". [Measured: `08_programme.png`]

It routed the change request by itself: **"ROUTING RULE Steering committee — $0K / 4 wk exceeds the
$250K or 2-week threshold."** [Measured: `06_change_control.png`]

### 6.4 It wrote the break-glass down, in words

The change request was raised and then signed through all four steps — Project manager, Change
authority, Finance, Steering committee — by **one** account. The audit trail says so, on every step:

```
Change step signed      | System Administrator (admin) | Project manager      — BREAK-GLASS: administrator signing a request they raised
Change step signed      | System Administrator (admin) | Change authority     — BREAK-GLASS: administrator signing a request they raised
Change step signed      | System Administrator (admin) | Finance              — BREAK-GLASS: administrator signing a request they raised
Change request approved | System Administrator (admin) | Steering committee   — BREAK-GLASS: administrator signing a request they raised
```
[Measured] This is documented, deliberate behaviour (`/api/admin/posture` `breakGlass`), not a
defect. It is still a fact this programme must act on: **our loader runs as an administrator, so
segregation of duties is bypassable for anyone holding that credential, and the only defence is that
every bypass is labelled.**

### 6.5 It audits reads, and it names an integration when it can

`GET /api/audit` shows `Audit trail consulted` and `Decision register consulted` rows — consultation
is a recorded act. [Measured]

And the number that matters most for integration:

| Actor on the whole trail | Events |
|---|---|
| `System Administrator (admin)` | **621** |
| `RT365 loader probe 160756 (service)` | **4** |
| `system` | 1 |
| **total** | **626** |

The four are the only writes that went through `PUT /api/v1/*` with an integration key — and they
are labelled **"(service)"**, exactly as `035_write_api.sql` promised. **The capability is real; it
covered 0.6 % of our load, because structure and value are not in v1.** [Measured]

### 6.5b It got the book out, and it proved a restore

Two things round 1 recorded as `[Source]` from the 5.9.0 run and left `[Open]` on 5.10.0. Both are
now measured on this book.

**Export.** `GET /api/admin/archive` → **200, 803,561 bytes, 145 ms**, `format`/`classification`/
`generatedAt`/`issuedTo`/`engine`/`order` in the envelope: **51 tables, 34 non-empty, 2,115 rows**
(largest: `audit_event` 640, `gate_criterion` 519, `raid_item` 176, `activity` 128, `milestone` 102,
`document` 96, `meeting_decision` 85). The book leaves without the vendor. [Measured]

**Backup, with the server running:**
```
$ npm run backup
  process 3195 holds …/server/.data/pgdata and this book is PGlite — stop it first
  (bash scripts/restart.sh stops gracefully), then run again          exit=2
```
It **refuses** rather than copying a live PGlite directory, and it names the pid and the remedy.
A real operating constraint, honestly enforced: **on PGlite, a backup requires downtime.**

**Backup and restore drill, server stopped by `SIGTERM` on its pid:**
```
$ npm run backup
  pglite → …/server/.data/backups/meridian-2026-09-08T16-27-52.tar.gz  (4609 KB)     exit=0, 1 s
  PGlite: this backup was taken with the server stopped — keep it that way for the next one.
$ npm run restore-drill -- server/.data/backups/meridian-2026-09-08T16-27-52.tar.gz
  restored … ELSEWHERE in 1.2s
  every counted table matches the live book — recorded as the last proven restore   exit=0, 2 s
```
And the instance then reports it to anyone who asks:
```
GET /api/health → "backup":{"lastDrillAt":"2026-09-08T16:28:00.594Z","lastAttemptAt":"…",
                            "ok":true,"restoreSeconds":1.2}
```
The book survived the stop and start intact (16 projects, 176 register items, 519 criteria, 102
milestones, 96 documents, 85 decisions, 7 benefits, 3 business cases). [Measured:
`backup_and_restore_drill.txt`]

**This is REQ-06 working, measured rather than read.** It is also the first time this programme has
evidence for the operational blocker in H-28: a restore proven by re-counting, on a real book,
timed. It does **not** discharge H-28 — that needs PostgreSQL, a second instance, changed
credentials on a real host and a written security policy, and it is a human act.

### 6.6 What it did *not* do on its own

**No exception was raised.** A tolerance of 1 day was set on RBT-GOV, a baseline finish was recorded
(2027-06-30) and the finish was slipped four months (2027-10-31). `exceptions: []` throughout.
`sweepExceptions()` runs on an **hourly** `setInterval` (`server/src/index.js:428`) with no immediate
first pass and no route to trigger it, so nothing could be observed inside the session. **[Open —
what would settle it: leave the instance running past a sweep tick, or add a manual trigger.]**
`Engine.tolerance` also needs `p.baselineFinish` for a schedule breach and `bac > 0` for a cost
breach [Source: `shared/engine.js:585-615`], so on a budget-less programme the cost dimension is
inert by construction.

---

## 7. Where round 1 blamed Meridian for something that was ours

### 7.1 The gate ladder — ours, and it got worse

Round 1 published this as a Meridian defect (`docs/PMO.md` §5, assessment §8 V-8), then corrected
itself the same day. **The correction was right, and round 2 proves the residue is also ours.**

With the ladder now declared, `RBT-GOV` carries **twelve** milestones where six were intended:

```
Gate A                    2026-09-08   done=true  acceptedBy=PE-29   gate=null   ← our loader's plain milestone
Gate A — Discovery        2026-10-18   done=false                    gate=1      ← the programme's ladder
Gate B                    2026-11-27 … Gate B — Architecture   2026-11-29 …
Gate C                    2026-12-18 … Gate C — Paper readiness 2027-01-12 …
… and so on to Gate F
```
[Measured] The cause is one line of **our** code: `GATE_LADDER` names the gates
`"Gate A — Discovery"` while `ensure_milestone(gov, f"Gate {g}", …)` looks for and creates
`"Gate A"`. The names never match, so the loader adds six more on top of the six Meridian
scaffolded. Round 1 had ten (4 default + 6 ours); round 2 has **twelve**, with *different dates* on
the two ladders. `shared/engine.js` and `server/src/wbs.js` scaffold exactly one ladder and always
did. **Meridian is not implicated at any point.**

The part of round 1's E-1 that survives is narrower and still true: a book created **before** the
ladder was declared cannot be migrated onto it. Ours was created after, so we cannot test it here.

### 7.2 The $51.3M — ours

Round 1's tiles read `PORTFOLIO VALUE $51.3M · ON TRACK 82%` because we ran `npm run seed` and left
the demonstration bank's book in place. On an empty book: **`PORTFOLIO VALUE $0.00M · 0 funded
projects · 16 strategy (no budget)`**. Half of round 1's E-6 dissolves. [Measured]

### 7.3 E-6 "do the executive tiles rescope to a programme?" — partly answered

There **is** a per-programme page (`#/programmes`) with its own tiles: ON TRACK 100 %, VALUE $0.00M,
DECISIONS OWED 130, RISK POSTURE 167, VALUE PROMISED 7. Whether the *portfolio* tiles narrow when
the `PROGRAMME` select changes is **[Open]** — we had only one programme, so the question does not
arise on this book. What would settle it: load a second programme and compare.

### 7.4 E-7 "does a milestone marked done read as accepted?" — settled, and it is Meridian's

`PRJ-147-M4` reads `done: true, acceptedBy: "PE-29", acceptedOn: "2026-09-08"`. The project page
renders it **`PLANNED`**. The cause, in their code:

```js
// web/src/views/index.js:1108
const state = g ? g.state : ms.dateBasis === "placeholder" ? "Unscheduled" : (late ? "Cleared" : "Planned");
```
For a milestone that is not a ladder gate, the state is derived from the date alone; `done` and
`acceptedBy` are never consulted. `server/src/routes/portfolio.js:486-523` goes to real trouble to
refuse `done` without a named accepter — and the page does not show the result. Round 1 left this
[Open]; it is now measured. Low severity, but it is precisely "the control exists in the table and
not in the room". Filed as D-9.

### 7.5 One thing round 1 said that is now *more* true, not less

"Sixteen projects reported GREEN at 0 % in a week when two gate documents had been refused." On an
empty book with real data it is **ON TRACK 100 %, 16 green, 0 amber, 0 red.** §8 D-6.

---

## 8. Defects, each with a reproduction from a clean clone

Common preamble for every entry:

```bash
git clone https://github.com/mliad313sn/Meridian && cd Meridian
git checkout cbe99ef6910fd1d16a9d4ccec5fa4cb7b498704c   # the unmerged branch; main is 5.9.0
npm install && npm run seed && npm run reset-book && npm run build
PORT=4183 node server/src/index.js
# log in as admin@meridian.example / meridian-admin-2026, change it, then:
POST /api/admin/programmes {"id":"X","name":"X","gateModel":[6 gates with name/at/owner/evidence]}
POST /api/projects {"name":"P","programme":"X","site":"…","budget":0}
```

---

### D-6 · An unmeasured project is GREEN, and its SPI and CPI are asserted as 1.00 — **severity: high**

**Observed, on an empty book carrying only this programme.** Executive portfolio view:

> **PORTFOLIO VALUE $0.00M** · 0 funded projects · 16 strategy (no budget) ·
> **ON TRACK 100%** · 16 green · 0 amber · 0 red ·
> **SCHEDULE INDEX 1.00** *at or ahead of plan* · **COST INDEX 1.00** *inside the envelope* ·
> FORECAST VARIANCE $0 · OPEN RISKS 42, 38 above the escalation threshold

and every one of the sixteen project rows `Initiation · GREEN · 0% reported · — · —`. Status
reporting: `SCHEDULE Green Portfolio SPI 1.00 · COST Green CPI 1.00`. The evidence pack for RBT-GOV
prints `Health | G — SPI 1.00 and CPI 1.00 both inside tolerance`. [Measured:
`01_portfolio.png`, `05_reports_value.png`]

**What the database says.** `health: null, pct: null, spi: null, cpi: null, budget: 0` on all
sixteen. The colour is produced at read time, not stored. [Measured]

**Why, exactly.** [Source: `shared/engine.js:166-168, 191-201`]

```js
const measurable = pv >= bac * 0.02 && ac >= bac * 0.005;   // bac = 0 → 0 >= 0 → TRUE
const spi = !measurable ? 1 : pv > 0.0001 ? ev / pv : 1;    // pv = 0 → 1
const cpi = !measurable ? 1 : ac > 0.0001 ? ev / ac : 1;    // ac = 0 → 1
…
return { rag: "G", derived: true, why: "SPI " + idx(s) + " and CPI " + idx(c) + " both inside tolerance" };
```

A zero-budget project satisfies `0 >= 0` twice, so it is classified **measurable**, its indices are
computed as exactly 1.00, and the health reason asserts they are "both inside tolerance". This is
not "too early to measure" — that branch exists (`measurable === false` also returns `"G"`) and is
never reached. `Engine.roll()` then counts these in `green`, which is where `ON TRACK 100%` comes
from. The allowed health values are `G|A|R` (`portfolio.js:333`); there is no fourth.

**Why it matters.** Every project is unmeasured at the start, which is exactly when a portfolio
office most needs to see that it is unmeasured. Here, absence of data is rendered as three positive
assertions — a colour, a schedule index and a cost index — on the page a sponsor reads. In the same
week, this programme's Security & Privacy Board did not accept `SECURITY_PLAN v1.0`, its Architecture
Review Board did not accept `DATA_FLOWS v1.0`, no capacity number was presented, and Gate B was not
convened. Meridian reports 100 % on track.

**Reproduce.** Create one project with `budget: 0` and no activity progress. Read `#/portfolio`.
Compare the PROGRESS cell (`0% reported`, honest) and the SPI/CPI cells on the row (`—`, honest)
with the HEALTH cell (`GREEN`) and the SCHEDULE INDEX tile (`1.00 at or ahead of plan`).

**What would close it.** A fourth state — `Unmeasured` / grey — set when `bac === 0` or when no
progress has been reported, counted separately in the tile ("16 not measured"), and a `measurable`
guard that treats `bac === 0` as not measurable rather than trivially measurable. It is a
derivation, not a new object.

---

### D-4 · No value object is writable through the v1 API — **severity: high** (their REQ-20 / our V-1)

**Observed.** With an integration key scoped `read:portfolio,write:portfolio,write:meetings,read:audit`:

| `PUT /api/v1/{coll}/RT365-PROBE-X` | Result |
|---|---|
| projects, milestones, raid, activities, workitems, criteria, decisions, actions | route exists (201 or 400 on body) |
| **business-case, benefits**, sites, programmes, people, stakeholders, comms, lessons, tolerances, waves, changes, documents, exceptions | **`404 No such endpoint`** — thirteen |

[Measured: `probe_2.json` `Q2_v1_write_routes`] Meanwhile `GET /api/v1/portfolio` returns
`counts: {projects:16, sites:1, programmes:1, risks:165, benefits:7, lessons:4}` — **benefits are in
the read contract and not in the write contract.**

**Consequence, measured.** Our three business cases and seven benefits went in by hand over a human
session. They are the only facts in this book that no automated loader can refresh, and they are the
facts the executive page is built on. Round 1 measured `BENEFITS PROMISED 0`; we now have 7, and the
only reason is that a person typed them.

**Reproduce.** `POST /api/admin/integrations` → `PUT /api/v1/benefits/EXT-1` → 404. Then
`GET /api/v1/portfolio` → `counts.benefits` present.

**Their own position.** REQ-20 is registered, `status: open`, `delivered: []`.

---

### D-5 · A first load cannot be done by an integration key — **severity: high** (their REQ-17)

**Observed.** The first three writes of any first load are `POST /api/admin/sites`,
`POST /api/admin/programmes` and 14 × `POST /api/admin/people`. None exists under `/api/v1`
(`sites`, `programmes`, `people` all `404`). So the loader holds a session for a human administrator.

**Measured cost:** of 626 audit events, **621 name `System Administrator (admin)`** and **4 name the
integration**. The audit-under-the-integration's-name that `035_write_api.sql` delivered covered
0.6 % of this programme's record. A field repository must keep a human admin password in its
loader's environment, which is a worse security posture than the spreadsheet it replaced.

**Reproduce.** As D-4, then `PUT /api/v1/sites/RTX` → 404.

**Their own position.** REQ-17, `status: open`, `answerToSource`: "To be put to the interoperability
committee first, as D-33.4 said."

---

### D-1 · A lesson cannot be tagged to gate 5 or 6 of a six-gate ladder — **severity: medium**

**Observed.** `POST /api/lessons {"project": …, "gate": 5}` → `400 A gate is 1, 2, 3 or 4`. Same at
6. Gate 4 succeeds. [Measured]

**Why it is a defect.** Migration 036 made the ladder configurable to twelve, and
`POST /api/criteria` honours it (`ladderLength(p.id)`, refusing gate 7 with "gate 1..6 of **this
project's programme**"). `POST /api/lessons` hard-codes `if (gateN !== null && !(gateN >= 1 && gateN
<= 4)) bad("A gate is 1, 2, 3 or 4")` [Source: `server/src/routes/portfolio.js:2154-2166`]. REQ-03
was not carried through to `lesson`.

**Why it matters to us.** V-7/REQ-26 asks for lessons to be offered as a checklist at the same gate
on later projects. The two gates where this programme carries the most risk — capped autonomous
pilot and controlled GA — cannot hold a lesson at all.

**Reproduce.** Declare a six-gate ladder, then `POST /api/lessons {"gate": 5}`.

---

### D-2 · A business case cannot be reconfirmed beyond gate 4 — **severity: medium**

**Observed.** `POST /api/projects/{id}/case/reconfirm {"gate": 6, "version": n}` →
`400 Reconfirmation happens at a gate — 1 to 4`. Gate 1 succeeds. [Measured] Same root cause as D-1.

**Why it matters.** V-3/REQ-22 asks that a gate refuse to pass without a reconfirmed case. On a
six-gate ladder, the last two gates — the ones that authorise capped autonomy and market release —
are exactly the ones where "is it still worth doing?" is most expensive to skip, and they cannot
record the answer.

---

### D-3 · `rollout_wave` has a sequence number it forbids you to use — **severity: medium**

**Observed.** Three waves to one site (seq 1, 2, 3) → the first 201, the second and third
`409 That record already exists`. [Measured]

**Why.** `CREATE TABLE rollout_wave (… seq integer NOT NULL DEFAULT 1, … UNIQUE (project_id,
site_id))` [Source: `server/migrations/010_plant_and_sites.sql:64-76`]. A project may have at most
one wave per site, so `seq` can only ever be 1 for any given site — the column is unusable for the
thing it names. A phased rollout to one site (our supervised pilot → capped autonomous pilot →
controlled GA) cannot be expressed.

**Reproduce.** Two `POST /api/waves` with the same `project` and `site` and different `seq`.

---

### D-8 · A gate criterion cannot cite a commit; a decision cannot cite a repository path — **severity: medium** (their REQ-29 / our V-10)

**Observed.** `PATCH /api/criteria/{id} {"externalRef": {"repo":"RT365","commit":"b912249",
"artefact":"docs/THREAT_MODEL.md"}}` → `400 Nothing recognisable to change — check the field names`.
`POST /api/decisions {"evidenceUri": "docs/PRODUCT_OWNER.md v2.0; GOAL.md …"}` →
`400 The evidence link is an http(s) address`. [Measured]

**Why it matters.** A criterion cites a `document` row, which is mutable, and a decision cites a URL.
This programme's evidence is a path and a commit hash in a repository beside the tool. Nineteen
decision records went in with an empty `evidenceUri` because the true evidence could not be
expressed. REQ-29 is registered and open.

---

### D-9 · A milestone marked done, with a named accepter and a date, renders as `PLANNED` — **severity: low**

Settled from round 1's [Open]. Data: `done: true, acceptedBy: "PE-29", acceptedOn: "2026-09-08"`.
Page: `PLANNED`. Cause: `web/src/views/index.js:1108` derives a non-gate milestone's state from the
date alone. **Reproduce:** `POST /api/milestones`, `PATCH` it `{"acceptanceCriteria": …}`, `PATCH`
it `{"done": true, "acceptedBy": …}`, read `#/project/{id}`.

---

### D-7 · The version an adopter gets is 5.9.0 — **severity: high, and it is the frame for everything above**

Reproduce: `git clone https://github.com/mliad313sn/Meridian && node -p "require('./package.json').version"`
→ `5.9.0`; `git tag | tail -1` → `v5.9.0`. The 5.10.0 work is on
`claude/meridian-rt365-feedback-d6vo3i`, unmerged and untagged. On the default branch, M-01 and M-03
reproduce (§3.1), there is no write API, no configurable ladder, no gate criteria, no decision
record, no stakeholder register — none of the twelve.

**All the defects above are against the branch.** Against what an adopter actually gets, they do not
apply, because the features do not exist.

---

### D-10 · Two silent acceptances — **severity: medium** (their REQ-19)

`PATCH /projects/{id}/health {"health": …}` and `POST …/attendance {"present": […]}` both return 200
for a body the route did not understand, and both write an audit row describing something the caller
did not ask for. §5.3.

---

## 9. Genuine questions, not defects

| # | Question | Why it is a question |
|---|---|---|
| Q-1 | Should `reset-book` be reachable without seeding first? | It keeps `app_user` by design (append-only audit, finding I-19) and needs an admin to survive. Documenting "seed, then reset" may be the whole answer. |
| Q-2 | Can a tolerance breach ever raise an exception on a budget-less, baseline-less programme? | The cost dimension needs `bac > 0`; we set a baseline and slipped four months against a one-day tolerance and saw nothing inside the session, because the sweep is hourly with no first pass. **[Open]** |
| Q-3 | Is the administrator break-glass acceptable for a machine loader? | It is documented, deliberate and labelled on every use. But our loader *is* an administrator, so SoD is bypassable by whoever holds that credential. This is a question for us as much as for them. |
| Q-4 | Do the portfolio tiles rescope with the PROGRAMME selector? | Unanswerable on a one-programme book. **[Open]** |
| Q-5 | Should a decision record be able to supersede one loaded from an external ledger? | We could not exercise `supersedes` because our own ledger rows were short. **[Open]** |
| Q-6 | `#/pipeline` renders `#` and SCORE as `NaN` for unscored projects. | It says plainly "16 project(s) carry no score, so the queue cannot rank them. They sort last rather than worst." The `NaN` is cosmetic; whether it is a defect or an unfinished view is theirs to say. |

---

## 10. The screenshots, and what each would make a sponsor believe

| File | What it shows | What a sponsor would wrongly believe |
|---|---|---|
| `01_portfolio.png` | `PORTFOLIO VALUE $0.00M · ON TRACK 100% · 16 green · 0 amber · 0 red · SCHEDULE INDEX 1.00 "at or ahead of plan" · COST INDEX 1.00 "inside the envelope"`; sixteen rows all `GREEN 0% reported` | **That the programme is on schedule and on budget.** It is neither measured nor unmeasured — it is unstarted. In the same week two Gate B documents were refused. **This is the one screen that must never leave the room.** |
| `02_project_governance.png` | `CRITERIA FOR GATE D — SUPERVISED PILOT · 0/9 FOUND MET`, `GATE E — CAPPED AUTONOMY · 0/8`; Gate A "evidence 0/1 · criteria 7/7 · 1 open register item(s) against it · **AT RISK**" | Mostly the truth, and it is the best screen in the product. But twelve milestones are listed where six exist, on two different date lines, because of our loader (§7.1) — a reader would believe this programme has twelve gates. The `AT RISK` badge is **correct**: the evidence document is still a draft. |
| `03_raid_register.png` | 167 items with real `P × I`, exposure bands, "heard by", owners and review dates; matrix across eight cells | That the ratings are measurements. They are **derived** (rule R2-PI-1); the ledger states none. Every row says so in its detail, but the table does not. |
| `04_meeting_frozen.png` | `CLOSED · Frozen — this is the record · it reads today exactly as it read in the room` | That the room was attended. **Attendance is empty** because we sent the wrong field and got a 200 (§5.3). A frozen record that silently records nobody present is worse than an open one. |
| `05_reports_value.png` | `SCHEDULE Green SPI 1.00 · COST Green CPI 1.00 · SCOPE Green · RISK Red 167 open items, highest exposure 25` | That three of four dimensions are healthy. Only the red one is measured. The page also says, correctly and to its credit, "No period has been closed yet… it will read differently tomorrow." |
| `06_change_control.png` | CR-224 `APPROVED`, four steps ✓ Project manager, ✓ Change authority, ✓ Finance, ✓ Steering committee | **That four bodies approved a four-week gate slip.** One administrator signed all four. The audit trail says `BREAK-GLASS` on every step; the change page does not. |
| `07_documents_evidence.png` | 96 documents, one per gate per project, all `DRAFT`, owned by the named lead | That a gate evidence set exists. The documents are placeholders Meridian created from our ladder text; not one has a file behind it. |
| `08_programme.png` | `ON TRACK 100% 16G·0A·0R · DECISIONS OWED 130 (113 urgent) · RISK POSTURE 167 · VALUE PROMISED 7 · 13 project(s) promise nothing` | Same green problem; but "13 promise nothing" is honest and is the number a sponsor should act on. |
| `09_my_week.png` | "This account is not linked to a person, so nothing is owed to you by name"; the week's writes, including `RISK RAISED · RSK-86 · RT365 loader probe 160756 (service)` | That the Product Owner has nothing to do. The admin account is not a person; the 29 open acts belong to people it cannot see. |
| `10_pipeline.png` | `# NaN · SCORE unscored · 16 project(s) carry no score, so the queue cannot rank them` | Nothing false — the page refuses to rank rather than inventing an order. The `NaN` is a rendering bug. |

**Two screenshots in this set were wrong before they were right, and both faults were mine.** An
early `#/risk` capture read `Nothing matches this filter · 0 shown · 167 open across the whole book`,
and an early `#/meetings` capture rendered the risk page. The causes were my own script: hash-only
navigation without a reload, and a coach-mark dismissal loop that matched the text "Close" and
clicked the **"Closed"** filter chip. A DOM query returned 167 rows all along. Had I filed either as
a Meridian defect from the screenshot, it would have been the exact failure round 1 committed with
the gate ladder. They are recorded here instead.

---

## 11. Separation: theirs, ours, and open

### Meridian's
D-1 lesson gate ceiling · D-2 case-reconfirmation gate ceiling · D-3 `rollout_wave` unique
constraint · **D-4 no value object writable through v1** · **D-5 structure not writable through v1** ·
**D-6 unmeasured reads GREEN with SPI/CPI 1.00** · **D-7 the default branch is 5.9.0** ·
D-8 no typed external evidence reference · D-9 an accepted milestone renders PLANNED ·
D-10 silent acceptance of unrecognised fields.

### Ours
The duplicated gate ladder, worse this round (12 milestones) — §7.1 · the demonstration book behind
round 1's `$51.3M` — §7.2 · `docs/RAID_LOG.md` has no probability, impact, residual or review
columns — §4.4 · `docs/DECISION_LOG.md` D-058..D-066 carry five columns where D-039..D-057 carry
seven, so nine decisions could not be loaded as records — §4.5 · 14 of 29 open acts name a committee
where the tool needs a person, and 28 of 29 have no date — §4.6 · the loader would re-post 66
decisions on any day after the first — §4.1 · we sent `health`/`present` where the routes want
`rag`/`attendance` — §5.3 · two screenshot artefacts caught before filing — §10.

### Open
Q-1..Q-6 in §9, plus: whether anyone other than the author has exercised the 5.10.0 branch; whether
the exception sweep fires on this book; whether the portfolio tiles rescope; whether a pre-036 book
can be migrated onto a ladder.

---

## 12. RAID entries this round opens

To be transcribed into `docs/RAID_LOG.md` by a role permitted to write it — this session was
instructed not to edit that ledger.

| Proposed | Type | Item | Owner | Needed by | Status |
|---|---|---|---|---|---|
| O-r2-1 | Risk | Meridian's default branch is 5.9.0; every improvement this programme depends on is on an unmerged, untagged branch. ADR-017's "pin the commit" is not caution, it is the only option, and the pin is to a branch head that may be rebased | Program Orchestrator | Gate B | Open |
| O-r2-2 | Gap | `docs/RAID_LOG.md` states no probability, impact, residual target or review date. Any rating shown outside this repository is derived (rule R2-PI-1) and must say so | Program Orchestrator | Gate B | Open |
| O-r2-3 | Gap | `docs/DECISION_LOG.md` D-058..D-066 carry five columns where the ledger's own header declares seven; nine decisions cannot be published as decision records | Program Orchestrator | Gate B | Open |
| O-r2-4 | Gap | 14 of 29 open human acts name a committee, not a person, and 28 of 29 carry no due date; neither can be tracked by any tool | Product Owner | Gate B | Open |
| O-r2-5 | Issue | `scripts/meridian_sync.py` creates six milestones whose names do not match the ladder it declares, producing twelve gates on every load | Program Orchestrator (script owned elsewhere) | Gate B | Open |
| O-r2-6 | Risk | Our loader authenticates as an administrator, so Meridian's break-glass exemption lets it sign every step of a change request. 621 of 626 audit events name one human account | Security Architect | Gate C | Open |
| O-r2-7 | Risk | Meridian reports this programme GREEN and 100 % on track. The portfolio view is not quotable outside this room until D-6 is closed or we stop feeding it budget-less projects | Product Owner | Gate B | Open |

---

## 13. Evidence index

| File | What it holds |
|---|---|
| `GUARD_PROBE.md` | the write-scope refusal, verbatim |
| `firsthour_A_main_5.9.0.txt` | the documented quick start on the default branch, failing |
| `firsthour_B_branch_5.10.0.txt` | the empty book, the password change, the free port |
| `test_counts.txt`, `npm_test_*_summary.txt` | 449/80 and 520/102, verbatim |
| `load_1_meridian_sync_run1.json` | 307 loader writes |
| `load_2_meridian_sync_run2.json` | the second run: one request, a 200 |
| `load_3_hand_drive.json` | 262 hand-driven requests with timings, status codes and bodies |
| `probe_1.json`, `probe_2.json` | 72 probes: v1 surface, ladder ceilings, the frozen record, SoD, health |
| `drive.py`, `probes.py`, `probes2.py`, `shots.py` | exactly what was run |
| `01…10 *.png`, `screens_text.txt` | the ten screens and their rendered text |

Meridian working copies (not in this repository):
`…/scratchpad/meridian-round2` (`main`, 77c4b49) and `…/scratchpad/meridian-round2-b`
(`cbe99ef`), the latter still running on :4183 with the empty book.

---

## 15. A caveat about the measurement environment

This repository was being written by other sessions while this round ran. `docs/DECISION_LOG.md`
gained D-067..D-069 at 16:06 (commit `c18e3a5`) and `docs/RAID_LOG.md` was touched at 16:04, both
*after* loader run 1 at 16:00; commit `4c57d15` ("Round-2 Meridian follow-up probes (work in
progress)") was made by another session over this session's in-progress files. All round-2 evidence
files are present and unaltered at `HEAD`, and every count in this document is the count at the
moment its evidence file was written — but two figures are snapshots of a moving ledger and are
labelled here rather than silently reconciled:

- **66 decisions loaded** (§4.1) was the whole of `docs/DECISION_LOG.md` at 16:00; the file held 69
  rows by 16:22.
- **165 RAID items** (§4.1) was the open register at 16:00.

The three-decision drift is what produced §4.1b, so it is evidence rather than noise. Nothing else
in this document depends on a ledger read after its evidence file was written.

## 14. What this document is not

It is not reviewed — author, reviewer and approver are the same person here, which this programme
forbids for anything that gates a decision, and nothing here gates a decision. It certifies no
evidence as complete. It convenes no gate. It states no return, no forecast and no promise. It has
not been filed upstream, and filing it is a human act (H-31). Meridian holds no fact that any RT365
gate, control or test reads; the ledgers and CI still hold the engineering truth (ADR-017).
