# Meridian IT-PMO — a consolidated field report, after two rounds and one correction of ourselves

**Prepared for the Product Owner of Meridian IT-PMO (`mliad313sn/Meridian`) by the Product Owner of
Global AI-MCP RoboTrader (RT365), the first real programme Meridian has carried.**

| Field | Value |
|---|---|
| Owner | RT365 Product Owner (delegate agent, under D-039 / D-040 / D-065) |
| Reviewer (different line) | **not assigned — this document has no second line, and §10.9 says so** |
| Supersedes | `docs/REPORTS/PMO_MERIDIAN_REPORT_VALUE.md` and `docs/REPORTS/PMO_MERIDIAN_REPORT_EVIDENCE.md` (the two halves), and `docs/PMO_MERIDIAN_ASSESSMENT.md` §§1–8 wherever they disagree with it |
| Machine-readable half | `docs/REPORTS/meridian_requests_v3.json` — `meridian-request-register/1`, **registerVersion 8** (round three; version 7 declared that schema and did not validate against it — §12.5). It **replaces** `docs/PMO/meridian_requests_v2.json`, which must not be filed (§7.1) |
| Subjects tested | **`main` @ `77c4b49`, version 5.9.0, 33 migrations** — what an adopter clones; and **`claude/meridian-rt365-feedback-d6vo3i` @ `cbe99ef`, version 5.10.0, 41 migrations** — where the work is |
| Status | v1.1 — 2026-09-09, §12 added (round three: building an installable Meridian). Body §§1–11 unchanged and still read at the commits they name. **Prepared, not filed.** Filing upstream is a human act on RT365's owner's account (H-31, open). This report recommends; it instructs nobody, decides nothing on Meridian's behalf and records no approval |

**Path note.** This was commissioned for `docs/PMO*`. RT365's write-scope guard
(`scripts/agent_guard.py`, roster `.claude/agents/roster.json`) refuses every `docs/PMO*` path to
the `product-owner` role — no role in the roster owns one — so this report and the register live in
`docs/REPORTS/`, which the role does own. That is also why the two half-reports and both rounds of
field evidence are there. It was not routed around. [Measured: the guard's refusal is recorded
verbatim in `docs/REPORTS/PMO/round2/GUARD_PROBE.md`]

**How to read the tags.** Every statement carries one and nothing carries none.
**[Measured]** — we ran it, and this is the number, with the file that holds the request and the
response. **[Source: path:line]** — Meridian's own code, migration, register or documentation, read
at the commit named, in a working copy that was not modified. **[Open]** — not verified, named so it
can be settled, with what would settle it.

**Where the two rounds disagree, round two wins, and this report says so each time.** Round two ran
on a **fresh clone with an empty book** carrying only this programme. Round one ran on a seeded
demonstration book and mixed our numbers with someone else's. No Meridian capability is asserted here
that was not seen in Meridian's code or behaviour. No benefit figure, price, market size or return
appears anywhere; profit is an objective and never a promise in our product, and we hold this
document to the same rule.

---

## 1. Executive summary

Meridian IT-PMO is the best-reasoned governance record we have used, and today it is not a product an
outsider can adopt. Both halves of that sentence are measured, and the second one is new.

The strength is real and specific. Given **one** programme declaration carrying a six-gate ladder and
sixteen project creations, Meridian built roughly **850 rows** of governance by itself — 96 gate
milestones, **517 gate criteria** split out of our own exit-evidence sentences, 96 evidence documents
and 128 activities — then generated a weekly agenda of **7 sections and 58 items**, marked our single
dated action overdue and put it first, and on close **froze the record**, produced a 38,806-character
minute and scheduled the next occurrence itself. It refused an invented reviewer, a criterion outside
our ladder, a stale edit, an edit with no version, a second approval on a completed change and a
decision added to a closed meeting. It backed itself up, refused to back up a running PGlite book
while naming the process holding it, restored elsewhere in **1.2 s** and re-counted every table, then
published the proven restore on `/api/health`. Across **307 loader writes and 334 hand-driven
requests** — median 16 ms, p95 105 ms — there was not one server error. [Measured]

The weakness is that almost none of this is reachable by anyone who follows the README. **The default
branch a new adopter clones today is 5.9.0.** All seven commits carrying the twelve improvements
Meridian built for us — and the request register itself — sit on one unmerged, untagged branch. On
`main`, the documented quick start still loses its own book to memory, still serves `Cannot GET /`,
and still refuses the published admin password: two first-hour defects we reported and Meridian fixed
on 2026-09-08 reproduce **verbatim**, because the fix was never merged. Round one of our own
assessment published those twelve as "delivered upstream". That was wrong, and §2.1 says so plainly.
[Measured]

**The single most important finding is theirs, and it is about what a sponsor is shown.** On an empty
book carrying only this programme — sixteen projects with no budget, no reported progress and no
measurement of any kind — the executive portfolio page reads **ON TRACK 100 %, 16 green, 0 amber,
0 red, SCHEDULE INDEX 1.00 "at or ahead of plan", COST INDEX 1.00 "inside the envelope"**, and the
exported status report prints **SPI 1.00 and CPI 1.00 on every project row**. In that same week this
programme's Security & Privacy Board did not accept its security plan, its Architecture Review Board
did not accept its data flows, no capacity number was presented, and **Gate B was not convened**. The
database holds `health: null, spi: null, cpi: null, budget: 0` on all sixteen; the green is
manufactured at read time by a zero budget satisfying the measurability test twice
(`pv >= bac * 0.02 && ac >= bac * 0.005`, both `0 >= 0`). A sponsor reading that page would believe
this programme is on schedule and inside its budget. It is neither: it is unstarted. Round one saw
the same thing at 82 %, diluted by demonstration data; on a clean book it is 100 %. §4 gives the
mechanism from Meridian's own code, and the fix is a derivation, not a new object. [Measured]
[Source: `shared/engine.js:166-168, 190-201`]

**We got things wrong too, and they are in this report at the same size as everything else.** Round
one published a Meridian defect that was ours — two gate ladders on every project — and round two
found it worse (twelve milestones, not ten) and still ours, caused by one line of our loader. Our own
risk register has no probability, impact, residual-target or review-date column, so every rating
Meridian displays for us is derived by a published rule rather than measured. Twenty-eight of our
twenty-nine open human acts carry no due date and fourteen name a committee where the tool needs a
person. One loader run aborted mid-flight against a correctly frozen record and, because our loader
writes its evidence file only on success, changed the book and produced **no evidence at all**. Two
screenshots in our own evidence pack were wrong before they were right, both from faults in our
capture script; had we filed either, it would have been the same failure as the gate ladder. §2.2 and
§6.2 keep all of that visible, because it is what makes the rest of this report worth reading.

**What we recommend.** Sequencing is in §8; the requirements are in §7 and in
`meridian_requests_v3.json`, de-duplicated against Meridian's own register (our V-1..V-12 are already
their REQ-20..REQ-31, so nothing is renumbered and only eight genuinely new items are added, from
REQ-32). **If only one thing gets done: merge the work to the default branch and push the tag
(REQ-32).** Every other line in this report is invisible to an evaluator until that is true. The one
thing after that is REQ-33 — stop reporting unmeasured as green — because it is the only finding here
that would make a sponsor believe something positive that is not true.

**And the honest frame.** This is one programme, in one shape, run for one day on a laptop-class
PGlite instance, by agents under a human owner. It is a load test, not a year of use. Nothing in
Meridian is read by any RT365 gate, control or test; our ledgers and CI still hold the engineering
truth (ADR-017), which is exactly why we could afford to try it. §9 is about what would take Meridian
from a very good governance record to the flagship its owner is aiming at, and the first four things
on that list are not features: a merged default branch, a tag, a second maintainer, and evidence that
somebody other than its author has run it.

---

## 2. Three corrections, in our own voice

### 2.1 We published that the twelve improvements were delivered upstream. On the branch an adopter clones, none of them exists.

Round one of our assessment states: *"The twelve improvements we filed were all taken"*, and our
`docs/IMPROVEMENT_REGISTER.md` §D marks every one of I-1..I-12 **"delivered upstream in Meridian
5.10.0"**. Round two cloned the repository fresh on 2026-09-08 and found: [Measured]

```
git rev-parse HEAD            -> 77c4b49aecacf3e3b4e3792c52939b2e51d38d76
git log -1 --date=iso HEAD    -> 2026-09-01 10:30:31 +0000
node -p require('./package.json').version -> 5.9.0
git symbolic-ref refs/remotes/origin/HEAD -> refs/remotes/origin/main
ls docs/requests/             -> no such directory
git tag | tail -1             -> v5.9.0
```

The seven commits that carry the twelve — `b58f806`, `e352bc8`, `985d6af`, `f5e0635`, `a5ba655`,
`125d16c`, `cbe99ef`, all authored 2026-09-08 — are on `claude/meridian-rt365-feedback-d6vo3i`,
**unmerged and untagged**. The default branch has not moved since 2026-09-01. [Measured]

What is true, stated precisely:

- The twelve **were built**, and we verified them running: 41 migrations, 520 tests passing in 102
  suites with zero failures, a write API by external id, a configurable gate ladder, gate criteria
  with a named independent reviewer, decision records with alternatives and dissent, a stakeholder
  register, a backup-and-restore drill that works. All of that is real and all of it is on the
  branch. [Measured]
- They **were not shipped**. They were pushed to a branch. Meridian's own release rule is that a
  request is `released` only when a tag carries it, and its register still reads `released: false` on
  all 31 lines. Its `channel.release` block says, honestly, that the `v5.10.0` tag is *"tagged
  locally on 985d6af; not pushed — a maintainer must push it"*. [Source:
  `docs/requests/rt365.json`]
- Two of the defects we reported and Meridian fixed the same day — the silent in-memory book and the
  unbuilt client — **reproduce verbatim on `main`**, because the fix was never merged. Our round-one
  claim that they were closed rested on reading `server/src/env.js` on the branch; round two ran the
  documented quick start on the default branch and it failed. §6.1 D-7 has the transcript. [Measured]

**What this means for anyone else evaluating Meridian.** Round one's headline — twelve field findings
to a delivered release in 84 minutes — is a genuine and unusual fact about a maintainer's
responsiveness, and it is **not** a fact about a release. Measured from an adopter's chair, the loop
is: *file a finding, get an answer the same day, on a branch you must know to check out by name.* An
evaluator who clones the repository, reads the README and runs the quick start gets 5.9.0, a book
that vanishes at exit, a 404 at the documented URL and a rejected password. That is the first hour
they will report, and no amount of work on an unmerged branch changes it. We published otherwise, in
two documents, and we are correcting it here rather than in a footnote.

### 2.2 We published a Meridian defect that was ours. Round two found it worse, still ours, and found four more of our own.

**The gate ladder.** Round one filed, as V-8 and in `docs/PMO.md` §5, that Meridian 5.10.0 scaffolds
two gate ladders on every project. It does not. `server/src/wbs.js` selects exactly one — the
programme's `gate_model` if declared, otherwise the default four — and `POST /api/admin/programmes`
has accepted a `gateModel` since migration 036. Meridian's own answer to us had already said so
(*"declare A–F on programme RBT, then create the epics"*) and we filed it against them anyway. We
corrected it the same day; round two proves the correction was right and that the residue is also
ours. With the ladder now properly declared, RBT-GOV carries **twelve** milestones where six were
intended — worse than round one's ten — because one line of our loader names the ladder gates
`Gate A — Discovery` and then looks for and creates `Gate A`:
`scripts/meridian_sync.py:36-43` against `:311`. The names never match, so six plain milestones land
on top of six correctly scaffolded ones, on two different date lines. **Meridian is not implicated at
any point.** [Measured] [Source: `server/src/wbs.js`, `shared/engine.js#normaliseGateModel`,
`server/src/routes/admin.js:22,632`]

**The $51.3M.** Round one's executive tiles read `PORTFOLIO VALUE $51.3M · ON TRACK 82%` because we
ran `npm run seed` and left the demonstration bank's book in place. On an empty book: `PORTFOLIO
VALUE $0.00M · 0 funded projects · 16 strategy (no budget)`. Half of round one's E-6 dissolves.
Round one also implied the tiles do not count our programme, from `OPEN RISKS 45` against 122
register items; on the empty book the tile reads `OPEN RISKS 42` against 165 register items, which is
consistent with the tile counting only items typed *Risk*. We withdraw the implication and record it
as an open question instead (§6.3 Q-7). [Measured]

**Four further faults of our own, found by driving our ledgers into a tool that has the fields.**

1. **Our register states no probability and no impact.** `docs/RAID_LOG.md` has six columns — ID,
   Type, Item, Owner, Needed by, Status — and no probability, impact, residual-target or review-date
   column. Round one pushed a hard-coded `p:3, i:3` on all 122 items and reported that as its own
   worst finding. Round two refused to invent numbers and instead **derived** P and I by a published
   rule (R2-PI-1) from fields the ledger does state, writing that sentence into every item's own
   detail so no reader can mistake it for a measurement. The result is eight populated cells instead
   of one, and Meridian's escalation arithmetic finally says something. It is still derived. Until
   our ledger carries those columns, the only honest rating in Meridian is a derived one, and any
   screenshot of that register must carry the caveat. [Measured]
2. **Twenty-eight of our twenty-nine open human acts carry no due date**, and fourteen name a body —
   Executive Steering, Trading Risk Committee, Compliance & Legal Committee, *Finance + Privacy* —
   where `meeting_action.owner_id` is a foreign key to a person. The one act that did carry a date
   was rendered `OVERDUE` and put first on the agenda within seconds. The tool is not the problem
   here; our ledger is. [Measured]
3. **A loader run aborted and produced no evidence.** Between run 1 and run 3, another session added
   three decisions to `docs/DECISION_LOG.md`. Our loader correctly saw them, re-opened the day's
   occurrence — which by then returned the **closed** one — and got
   `409 This meeting is closed — its decisions are final`. Meridian refused exactly as it should. Our
   loader aborts on the first status ≥ 300 and writes its `--json` evidence file **only on success**,
   so it had already written nine register rows, then stopped, and left **no evidence file at all**.
   That is round one's own gap G-9 recurring in a new form, on the exact standard we apply to our own
   gates. [Measured]
4. **Two screenshots were wrong before they were right.** An early `#/risk` capture read
   `Nothing matches this filter · 0 shown · 167 open across the whole book`, and an early
   `#/meetings` capture rendered the risk page. Both were our capture script: hash-only navigation
   without a reload, and a coach-mark dismissal loop that matched the text "Close" and clicked the
   **"Closed"** filter chip. A DOM query returned 167 rows all along. Filing either from the
   screenshot would have been precisely the failure we committed with the gate ladder. [Measured]

We keep this visible because a supplier report that only lists the supplier's faults is worth
discounting, and because our own product owner would want to know that our first instinct in round
one was to blame the tool.

### 2.3 Our register numbering collides with theirs, and the file we prepared must not be filed.

Meridian's `docs/requests/rt365.json` is now at **registerVersion 6 with 31 requests**, and it
already carries **our V-1..V-12 verbatim as REQ-20..REQ-31**, with our own acceptance criteria copied
into their `remaining` field — all `status: "open"`, `delivered: []`. Their **REQ-14** is a different
request entirely, raised by their own standing review duty from our decision **D-057**, and delivered
(migration `040_milestone_basis.sql`, milestone `dateBasis`/`condition`, placeholders never read as
MISSED). REQ-15..REQ-19 come from a third-round integrator and are also open. [Source:
`docs/requests/rt365.json` @ `cbe99ef`, parsed]

Our prepared file `docs/PMO/meridian_requests_v2.json` numbered its items **REQ-14..REQ-28**. Filing
it would have overwritten a delivered request with a different one and duplicated twelve requests
that already exist. **It is withdrawn before filing.** Its replacement is
`docs/REPORTS/meridian_requests_v3.json`, described in §7.1: it references their existing ids without
changing a single status, restates REQ-27 (our V-8) with the defect claim withdrawn, and numbers only
genuinely new requests from **REQ-32**.

---

## 3. What Meridian is worth today, measured

### 3.1 The two rounds, side by side

| | Round 1 (2026-09-08, morning) | Round 2 (2026-09-08, afternoon) | Which is authoritative |
|---|---|---|---|
| Instance | 5.9.0 `77c4b49`, then 5.10.0 `e352bc8` | **`main` 5.9.0 `77c4b49`** and **branch 5.10.0 `cbe99ef`** | round 2 — it tested what an adopter gets |
| Book | `npm run seed` — the demonstration bank's portfolio **plus** ours | `npm run reset-book` — **empty**, ours only | round 2 |
| Portfolio tiles | `$51.3M · ON TRACK 82% · 23G 2A 3R` | `$0.00M · ON TRACK 100% · 16G 0A 0R · SPI 1.00 · CPI 1.00` | round 2; round 1's $51.3M was the demo book, ours |
| Loader writes | 256, all 2xx | **307**, all 2xx, 8,231 ms; second run **1 request, a 200, no creations** | round 2 |
| Hand-driven requests | none | **334**, median **16.1 ms**, p95 **104.8 ms**, max 204.1 ms, 8.3 s of server time; `200:237 · 201:55 · 400:17 · 404:13 · 409:10 · 428:2`; **no 5xx** | round 2 |
| Tests | 449 (5.9.0), 513 (`e352bc8`) | **449 / 80 suites / 111 s** on main; **520 / 102 suites / 134 s** on the branch; 0 fail, 0 `not ok` on both | round 2 |
| Migrations | 33 → 39 | **33** on main, **41** on the branch | round 2 |
| Gates | our six were plain milestones; `gate_criterion` could not touch them | **54 criteria on RBT-GOV** (517 book-wide), by gate `1:7 · 2:9 · 3:8 · 4:9 · 5:8 · 6:13`; **7 found met** by a named independent reviewer | round 2 |
| The meeting | left in session, nothing frozen | opened, agenda generated, minuted, **closed and frozen**, next occurrence scheduled by the tool | round 2 |
| Decisions | 59 as meeting decisions | **85**: 66 meeting + **19 decision records** with alternatives, dissent, council, provenance, ratifiedBy | round 2 |
| RAID | 122 items, all `p:3 i:3` | 165 items, then re-rated across **eight** P×I cells by a published derivation rule | round 2 |
| Value objects | 0 benefits, 0 business cases | **7 benefits, 3 business cases** — every one typed by a human, because no API can write them | round 2 |
| Archive | 1,529 rows / 47 tables | **803,561 bytes in 145 ms · 51 tables · 34 non-empty · 2,115 rows** | round 2 |
| Backup / restore | not run | backup **4609 KB**, restore elsewhere in **1.2 s**, every counted table matched, published on `/api/health` | round 2 |

### 3.2 The single best return on effort we saw

We wrote **one** `POST /api/admin/programmes` carrying the A–F ladder with its exit-evidence strings,
and sixteen `POST /api/projects`. With no further instruction Meridian created **96 milestones** (six
gates on every project, named from our ladder), **517 gate criteria** (it split our exit-evidence
sentences into criteria per gate per project — *Approved charter*, *Personas*, *Jurisdiction
hypothesis*), **96 evidence documents** (one per gate per project, `DRAFT`, owned by the project's
named lead), **128 activities** and 16 allocations. Our loader made 307 writes; the tool made roughly
850 rows from six lines of ladder. [Measured: `GET /api/bootstrap` before any hand drive]

The gate page then reads in our vocabulary, not its own: `CRITERIA FOR GATE D — SUPERVISED PILOT ·
0/9 FOUND MET`, `CRITERIA FOR GATE E — CAPPED AUTONOMY · 0/8 FOUND MET`, and Gate A badged
**AT RISK** because its evidence document is still a draft — which is correct. `POST /api/criteria
{"gate": 7}` on a six-gate ladder is refused: *"A criterion belongs to a gate 1..6 of this project's
programme."* [Measured]

### 3.3 The controls we would want, working

Every one of these was attempted and refused, with a message a person can act on: [Measured]

| Attempt | Response |
|---|---|
| Find a criterion met with no `reviewedBy` | `400 Finding a criterion met needs reviewedBy — the named person who checked it` |
| Find a criterion met by an invented person | same 400 — an invented reviewer is not a reviewer |
| A criterion at gate 7 of a six-gate ladder | `400 A criterion belongs to a gate 1..6 of this project's programme` |
| Add a decision to a closed meeting | `409 This meeting is closed — its decisions are final` |
| Edit with a stale version | `409 Someone else changed this record — reload and try again` |
| Edit with no version at all | `428 This edit did not say which version it is based on` |
| Approve a completed change request a second time | `409 This request is already decided` |
| An unknown integration scope | `400 Unknown scope(s): … Known: read:portfolio, read:audit, write:portfolio, write:meetings` |
| `npm run backup` with the server running | refused, naming the holding pid and the graceful-stop command |

It also **audits reads** (`Audit trail consulted`, `Decision register consulted` appear as events),
and it wrote its own break-glass down in words: a change request raised and signed through all four
steps by one administrator carries `BREAK-GLASS: administrator signing a request they raised` on
every step in the trail. That is documented, deliberate behaviour, not a defect — and it is a fact an
integrator must plan for, because our loader *is* an administrator (§6.2). [Measured]

### 3.4 The one-day improvement loop, stated accurately

From the RT365 commit carrying our twelve findings (`12a20a8`, 08:45) to the Meridian commit carrying
all twelve (`e352bc8`, 10:09) is **84 minutes**; from the commit their register says it read
(`25b0483`, 09:44) to their adoption commit (`b58f806`, 09:54) is **10 minutes**. Both figures stand.
[Measured: git timestamps in both repositories]

What round two changes is where those commits live. **All of them are on the unmerged branch.** So
the accurate sentence is: *Meridian turns a field return into working, tested code on a branch within
the hour, and has not yet turned that code into something an adopter can obtain.* Both halves matter.
The first half is the most unusual thing about this product and we have not seen it anywhere else.
The second half is why an evaluator would not believe the first.

Two further facts belong beside it, in fairness and in caution. In fairness: after `e352bc8` the
maintainer convened counsellors on their own release and fixed 27 further findings the same day, and
the tests grew 449 → 520 across the day with zero failures. In caution: twelve changes across six
migrations and a new public write API in 84 minutes is also a change-control observation, and we
cannot tell a fast maintainer from an unreviewed one from the outside. What we can say is that the
suite passes, the journey test replays the life of an organisation on every run, and every migration
header names the finding it answers. [Measured] [Source: the migration headers, e.g. `036` opens
*"L'ÉCHELLE DE JALONS DU PROGRAMME (I-3 · retour de terrain RT365, M-04)"*]

### 3.5 What it cost us

| Line | Measured |
|---|---|
| First hour, **branch** (5.10.0), empty book | **about six minutes** end to end, excluding the test run — install, seed, reset-book, build, boot, log in, change the password. The only lost time was one 400: the password field is `next`, not `new`, and there is no OpenAPI for session routes, so we read the source |
| First hour, **main** (5.9.0) | fails; three undocumented manual steps are required before the documented URL answers at all (§6.1 D-7) |
| The loader we maintain | 358 lines of Python, one dependency, covered by a contract test |
| Version upgrade 5.9.0 → 5.10.0 | **zero changes required** to our loader; six migrations, a new write API, a configurable ladder and a decision register landed without breaking one session route we call |
| Adoption of the new API | **4 of 626 audit events** went through `PUT /api/v1/*` with an integration key. The other 621 name one human administrator. The lag is ours, and the reason is D-5/REQ-17 |
| Operating it for real | **not paid.** Everything here is a laptop-class PGlite instance. A real instance (PostgreSQL, restore-tested backup on a real host, changed credentials, written security policy) is our open human act H-28 |

---

## 4. The finding that matters most, and it is theirs

**On an empty book carrying only this programme, Meridian reports it 100 % on track, all green, with
a schedule index and a cost index of exactly 1.00 — in the week two gate documents were refused and
the gate was not convened.**

### 4.1 What is on the screen

> **PORTFOLIO VALUE $0.00M** · 0 funded projects · 16 strategy (no budget) ·
> **ON TRACK 100%** · 16 green · 0 amber · 0 red ·
> **SCHEDULE INDEX 1.00** *at or ahead of plan* · **COST INDEX 1.00** *inside the envelope* ·
> FORECAST VARIANCE $0

Every one of the sixteen project rows reads `Initiation · GREEN · 0% reported · SPI — · CPI —`. The
status reporting page reads `SCHEDULE Green Portfolio SPI 1.00 · COST Green CPI 1.00 · SCOPE Green ·
RISK Red 167 open items`. Its per-project detail table — the one that prints and exports — carries a
column of **`SPI 1.00 · CPI 1.00 · EAC $0.00M`** on all sixteen rows. The evidence pack for RBT-GOV
prints `Health | G — SPI 1.00 and CPI 1.00 both inside tolerance`. [Measured:
`docs/REPORTS/PMO/round2/01_portfolio.png`, `05_reports_value.png`]

### 4.2 What the database says

`health: null, pct: null, spi: null, cpi: null, budget: 0` on all sixteen. **Nothing green is
stored.** The colour, the two indices and the sentence justifying them are produced at read time.
[Measured]

### 4.3 The mechanism, from their own code

[Source: `shared/engine.js:166-168` and `:190-201`, read at `cbe99ef`]

```js
const measurable = pv >= bac * 0.02 && ac >= bac * 0.005;   // bac = 0  ->  0 >= 0  ->  TRUE
const spi = !measurable ? 1 : pv > 0.0001 ? ev / pv : 1;    // pv = 0   ->  1
const cpi = !measurable ? 1 : ac > 0.0001 ? ev / ac : 1;    // ac = 0   ->  1
...
health(db, p, m) {
  if (m.measurable === false) return { rag: "G", derived: true, why: "Too early to measure — less than 2% of the plan has been spent" };
  ...
  return { rag: "G", derived: true, why: "SPI " + idx(s) + " and CPI " + idx(c) + " both inside tolerance" };
}
```

A zero-budget project satisfies `0 >= 0` twice, so it is classified **measurable**; its indices are
then computed as exactly 1.00; and `health()` asserts, in the product's own words, that they are
*"both inside tolerance"*. `Engine.roll()` counts these in `green`, which is where ON TRACK 100 %
comes from. `portfolio.js:333` permits only `G|A|R`, so there is no fourth state to fall into.

Two details make this worth fixing rather than arguing about. First, the honest branch **exists** —
`measurable === false` returns *"Too early to measure"* — and it is unreachable for a budget-less
project, and it is **also green**. So there is no code path today by which a project with nothing
measured is anything other than green. Second, the same three lines are on the default branch at
5.9.0 (`shared/engine.js:128-130`), so this is not an artefact of the new work; it is the oldest
behaviour in the product. [Source]

### 4.4 What a sponsor would wrongly believe, plainly

That the programme is **on schedule and inside its budget**, on the authority of two indices and a
colour. It is neither. It is unstarted, and unstarted is the state in which a portfolio office most
needs to see that nothing is measured. The absence of data is rendered as three positive assertions
on the one page an executive reads, and the assertions survive into the printable status report and
the evidence pack, which are the artefacts that leave the room.

The product gets the neighbouring cells right and that is what makes this a defect rather than a
philosophy: the PROGRESS cell says `0% reported`, the register's SPI and CPI cells say `—`, the
project page says *"not measured on a budget-less project"*, the pipeline says
*"16 project(s) carry no score, so the queue cannot rank them. They sort last rather than worst"*,
and the status page says *"No period has been closed yet… it will read differently tomorrow."* Every
one of those refuses to invent. Only health, the tiles and the exported indices do invent, and they
are the ones a sponsor reads.

### 4.5 What would close it

A `measurable` guard that treats `bac === 0` (or no reported progress) as **not** measurable rather
than trivially measurable; a fourth health state — *not measured* — counted separately in the tile
(`0 green · 0 amber · 0 red · 16 not measured`); and SPI and CPI printed as `—` wherever they are not
measured, on every page, print, export, evidence pack and `/api/v1` resource, exactly as the register
row already does. It is a derivation, not a new object. Filed as **REQ-33**, effort S, our
recommended priority **highest**. Reproduce: create one project with `budget: 0` and no activity
progress; read `#/portfolio`; compare the PROGRESS and SPI cells with the HEALTH cell and the
SCHEDULE INDEX tile.

**Our own consequence, which is not theirs.** Until REQ-33 lands or we stop feeding Meridian
budget-less projects, we treat the Meridian portfolio view as **not quotable outside this room**, and
we would rather write that down than discover it in a steering pack.

---

## 5. What the value model already gets right

Meridian has the best value data model we have seen in an open portfolio tool. These are design
choices, each written down with its reasoning in the migration that introduced it, and each one is a
thing most commercial PPM products get wrong. We list them at length because a report that only lists
faults gets discounted, and because §7 asks for *consequence*, not vocabulary — the nouns are already
right.

**5.1 Value is not forced into money.** `benefit` carries `kind` (Production, Availability, Cost,
Risk, Compliance), its own `measure` and `unit`, and holds baseline, target and actual *in that unit*,
with an explicit instruction that these are never divided by 1e6 like the money elsewhere. The schema
comment says why: *"Value here is spoken in production, plant availability, hours and cost per ounce
as often as in currency."* A tool that demands a currency for every benefit gets a currency for every
benefit, invented. This is the single most important decision in the model and it is correct.
[Source: `server/migrations/008_benefits.sql`]

**5.2 The verdict is separated from the measurement.** A project manager records what was measured
(`benefit.write`); whether that counts as met is a group-level act (`benefit.review`, `GROUP_ONLY`),
by the same independence rule that stops the raiser of a change deciding it. The post-implementation
verdict is a distinct route, refuses anything short of "Met" without a written reason, and is audited
with before/after images. That is the difference between a benefits register and a benefits *claim*.
[Source: `shared/rbac.js:37,86-99`; `server/src/routes/portfolio.js:1871`]

**5.3 Unmeasured is not zero.** `Engine.attainment` returns null unless baseline, target and actual
are all present, with the reason in the code: *"an unmeasured benefit is not a zero, and showing it
as one is how a portfolio lies."* The portfolio follows through and prints `uncased` — the count of
projects promising nothing — described in the view code as *"the number that says whether this
programme is governed by value or only by cost"*. On our book it printed **`VALUE PROMISED 7 · 13
project(s) promise nothing`**, unprompted, and 13 is the honest number a sponsor should act on. A
tool that puts the embarrassing number on the front page was built by someone who has run a
portfolio. [Source: `shared/engine.js:552-561,646-651`; `web/src/views/index.js:790-806`] [Measured:
`08_programme.png`]

**5.4 Closure is refused without a named benefits owner.** Advancing to `Closed` requires a named
operations owner *and* a named benefits owner, both verified active in the directory, with the reason
in the code — *"benefits realise AFTER closure"*. Every organisation loses benefits at exactly this
moment and almost no tool defends it at the write path. [Source: `server/src/routes/portfolio.js:365-380`]

**5.5 The case carries its basis, and a reconfirmation that can go stale.** `business_case` holds
summary, expected cost, expected benefit and `basis` — *"a number without its basis gets argued
about; a number with its basis gets checked"* — plus reconfirmation as a **distinct act**, one case
per project enforced by `UNIQUE`. Better: the reconfirm route clears `updated_on`, and the serialiser
derives `staleSinceReconfirm` from the ordering of the two, so a case reconfirmed and then quietly
revised reads as **stale** rather than confirmed — encoded by event order, not by comparing two
same-day dates. That is a subtle failure mode caught deliberately. [Source:
`server/migrations/028_business_case.sql`; `server/src/portfolio.js:356-372`]

**5.6 Exceptions are found, not raised.** Tolerances are set by the level above, a sweep constates
breaches on the same numbers the screen shows, one open exception per project per dimension is
guaranteed by a partial unique index at the database, and an exception never closes by itself — the
forecast may drift back inside the margin, the exception stays open until someone answers with one of
the four PRINCE2 responses. The stated reason, *"what depends on a bearer of bad news does not
travel"*, is the correct reason. [Source: `server/migrations/026_tolerance.sql`;
`server/src/exceptions.js`]

**5.7 The meeting engine is the strongest working part of the product.** From portfolio state alone
it produced an agenda of **7 sections, 58 items**, *"26 of 25 minutes allocated"*, with the printed
rule *"Sections with nothing to report are left out rather than shown empty"*; it marked our one
dated action OVERDUE and put it first; on close it froze the agenda, stamped `closedAt`/`closedBy`,
produced a 38,806-character minute, scheduled `MS-SUWK22-20260914` with its agenda already built, and
printed *"CLOSED · Frozen — this is the record · The pack is frozen: it reads today exactly as it
read in the room, and it can be produced again."* Round one left the room in session; that gap was
ours and it is closed. [Measured: `04_meeting_frozen.png`]

**5.8 It computes governance from data rather than asking for it.** From the register alone it
derived escalation bands (113 at steering level, 54 at PMO), a response mix (Mitigate 40 / Monitor 33
/ Fix 94), the highest exposure (25), five escalated dependencies onto the agenda, and
`DECISIONS OWED 130, 113 urgent`. It routed a change request by itself with the rule printed:
*"ROUTING RULE Steering committee — $0K / 4 wk exceeds the $250K or 2-week threshold."* [Measured:
`03_raid_register.png`, `06_change_control.png`, `08_programme.png`]

**5.9 Reversibility is real, and it is why we could adopt it at all.** Apache-2.0, self-hosted, and
the whole book leaves in one call: `GET /api/admin/archive` → 200, 803,561 bytes in 145 ms, 51
tables, 34 non-empty, 2,115 rows, with format, classification, generatedAt, issuedTo, engine and
order in the envelope. The backup refuses to copy a live PGlite directory and names the pid and the
remedy; stopped, it backs up in a second and restores **elsewhere** in 1.2 s with every counted table
matching, and the instance then publishes the proven restore on `/api/health`. That is REQ-06
working, measured rather than read. [Measured: `backup_and_restore_drill.txt`]

**5.10 The evidence model is stronger than "a document link".** A document's URI is required and
host-checked at approval; the SHA-256 of that URI is locked at approval and changing the link
afterwards drops the document back to *In review*; `supersedes` records lineage rather than a suffix
convention; and a liveness probe never changes a document's state, because *"a satellite link going
down must not un-approve a gate"*. Our round-one phrasing — "evidence is a document link" — undersold
this, and §7's V-10/REQ-29 is narrowed accordingly: it asks for one more citation type, not a
rebuild. [Source: `server/migrations/014_evidence.sql`, `020_evidence_probe.sql`]

**5.11 The request register itself.** A tool that answers a field repository's findings *by the field
repository's own identifiers*, tells it which of its RAID rows it may now close, and — unprompted —
raises a new request (their REQ-14) from a decision in our log that carried no request id at all, is
not a normal open-source posture. It is the most unusual capability in the product and §9 argues it
is the one to make reusable. [Source: `docs/requests/rt365.json`]

**5.12 It is honest in the places that cost it something.** `GET /api/health` returned
`backup:{lastDrillAt:null, ok:null}` before we ran a drill. The pipeline refuses to rank unscored
projects rather than inventing an order. The status page says no period has been closed. The break-
glass exemption is written into the audit trail on every use. This is a product that would rather
show an awkward `null` than a comfortable number — everywhere except the one place in §4.

---

## 6. Defects and gaps, reproducible from a clean clone

Common preamble for every entry marked *branch*:

```bash
git clone https://github.com/mliad313sn/Meridian && cd Meridian
git checkout cbe99ef6910fd1d16a9d4ccec5fa4cb7b498704c   # the unmerged branch; main is 5.9.0
npm install && npm run seed && npm run reset-book && npm run build
PORT=4183 node server/src/index.js
# log in as the published admin, change the password, then:
POST /api/admin/programmes {"id":"X","name":"X","gateModel":[6 gates: name/at/owner/evidence]}
POST /api/projects {"name":"P","programme":"X","site":"…","budget":0}
```

### 6.1 Theirs

| # | Defect | Severity | Where it is filed |
|---|---|---|---|
| **D-7** | **The version an adopter gets is 5.9.0.** A fresh clone gives `main` @ `77c4b49`, 5.9.0, 33 migrations, **no `docs/requests/` directory at all**; newest tag `v5.9.0`. On main the documented quick start fails: `npm run seed` reports success and writes nothing to disk (`server/src/db.js:152` `const pglite = dataDir ? new PGlite(dataDir) : new PGlite();`, `:226` `openPglite(opts.dataDir ?? process.env.PGLITE_DIR ?? null)`; nothing in `server/src` loads a `.env`, and `.env.example:4` is the only place `PGLITE_DIR` is set), `GET /` answers `404 Cannot GET /`, and the published admin password answers 401 because the seeded account no longer exists. Three manual steps the documentation does not name are required. `README.md:89` says `npm test # 413 tests`; measured 449. **This is the frame for every entry below: against what an adopter actually gets, none of the others applies, because the features do not exist.** | **high** | **REQ-32** (new) |
| **D-6** | **An unmeasured project is GREEN, and its SPI and CPI are asserted as 1.00.** Full treatment in §4. Present on `main` at 5.9.0 as well (`shared/engine.js:128-130`). | **high** | **REQ-33** (new) |
| **D-4** | **No value object is writable through v1.** With a key scoped `read:portfolio, write:portfolio, write:meetings, read:audit`: `PUT /api/v1/{business-case,benefits}/X` → `404 No such endpoint`, along with eleven more (sites, programmes, people, stakeholders, comms, lessons, tolerances, waves, changes, documents, exceptions) — **thirteen 404s against eight routes that exist** (`server/src/routes/v1.js:100-107`). Meanwhile `GET /api/v1/portfolio` returns `counts.benefits`. Measured consequence: our three business cases and seven benefits are the only facts on this book no loader can refresh, and they exist only because a person typed them. | **high** | their **REQ-20** (open) |
| **D-5** | **A first load cannot be done by an integration key.** The first three writes of any first load are a site, a programme and fourteen people; none exists under `/api/v1`. Measured cost: **621 of 626 audit events name one human administrator; 4 name the integration** — the audit-under-the-integration's-name that `035_write_api.sql` delivered covered **0.6 %** of this programme's record. A field repository must keep a human admin password in its loader's environment. | **high** | their **REQ-17** (open) |
| **D-1** | **A lesson cannot be tagged to gate 5 or 6 of a six-gate ladder.** `POST /api/lessons {"gate":5}` → `400 A gate is 1, 2, 3 or 4`; gate 4 succeeds. `server/migrations/024_lessons.sql:40`; `server/src/routes/portfolio.js:2163,2209`. Migration 036 freed the ladder and `gate_criterion` honours it (`037:29`, `CHECK (gate BETWEEN 1 AND 12)`); `lesson` did not travel with it. | medium | **REQ-34** (new) |
| **D-2** | **A business case cannot be reconfirmed beyond gate 4.** `POST /api/projects/{id}/case/reconfirm {"gate":6}` → `400 Reconfirmation happens at a gate — 1 to 4`; gate 1 succeeds. `server/migrations/028_business_case.sql:52`; `portfolio.js:2119`. Same root cause. The two gates where "is it still worth doing?" is most expensive to skip — capped autonomy, market release — cannot record the answer. | medium | **REQ-34** (new) |
| **D-3** | **`rollout_wave` has a sequence number it forbids you to use.** Three waves to one site (seq 1, 2, 3) → 201, `409 That record already exists`, 409, because `UNIQUE (project_id, site_id)` (`server/migrations/010_plant_and_sites.sql:64-76`). A phased rollout to one site — ours is supervised pilot → capped autonomous pilot → controlled GA — cannot be expressed. | medium | **REQ-37** (new) |
| **D-8** | **A gate criterion cannot cite a commit; a decision cannot cite a repository path.** `PATCH /api/criteria/{id} {"externalRef":{…}}` → `400 Nothing recognisable to change`. `POST /api/decisions {"evidenceUri":"docs/PRODUCT_OWNER.md v2.0; …"}` → `400 The evidence link is an http(s) address`. Nineteen decision records went in with an empty `evidenceUri` because the true evidence could not be expressed. | medium | their **REQ-29** (open) |
| **D-10** | **Two silent acceptances.** `PATCH /projects/{id}/health {"health":…}` → 200 (the field is `rag`; `portfolio.js:333`), audit row written saying *"Project status returned to automatic"*, the caller's intent not performed. `POST …/attendance {"present":[…]}` → 200 (the shape is `{attendance:[{personId,state}]}`; `meetings.js:501`), audited *"0 present of 0"* — so the **frozen** minute now records that nobody was in the room. Our bodies were wrong in both cases; the fault is a 200 for a body the route did not understand, and on the second it is now inside a record designed to be final. | medium | their **REQ-19** (open) |
| **D-9** | **A milestone marked done, with a named accepter and a date, renders as `PLANNED`.** Data: `done:true, acceptedBy:"PE-29", acceptedOn:"2026-09-08"`. `web/src/views/index.js:1108` derives a non-gate milestone's state from the date alone. `portfolio.js:486-523` goes to real trouble to refuse `done` without a named accepter and the page never shows the result: the control exists in the table and not in the room. | low | **REQ-38** (new) |

### 6.2 Ours

Each of these is a fault in this programme, found by driving it into a tool that has the fields. None
is a Meridian defect and none should be read as one.

1. **The duplicated gate ladder** — twelve milestones where six were intended, `meridian_sync.py:36-43`
   against `:311`. Published in round one as a Meridian defect; withdrawn (§2.2). **Worse this round,
   not better.**
2. **The `$51.3M` executive tile** in round one — the demonstration book we failed to remove.
3. **`docs/RAID_LOG.md` states no probability, impact, residual target or review date.** Every rating
   Meridian shows for us is derived by rule R2-PI-1 and says so in each item's own detail — but the
   table does not, so a screenshot of that register is misleading without the caveat.
4. **`docs/DECISION_LOG.md` D-058..D-066 carry five columns where D-039..D-057 carry seven.** Nine
   decisions could not be published as decision records at all, and `supersedes` could never be
   exercised because the predecessor was absent. [Open]
5. **Fourteen of twenty-nine open acts name a committee where the tool needs a person; twenty-eight of
   twenty-nine carry no due date.** Neither can be tracked by any tool, ours included.
6. **The loader would re-post 66 decisions and 29 actions on any day after the first**, because
   `existing_decisions()` only looks at the current occurrence.
7. **A partial load left the book changed and produced no evidence file**, because the loader writes
   its `--json` evidence only on success (§2.2.3).
8. **We sent `health` and `present` where the routes want `rag` and `attendance`** — which is how we
   found D-10, and is also why our frozen minute records an empty room.
9. **Two screenshot artefacts caught before filing** (§2.2.4).
10. **We adopted almost none of what Meridian built for us.** Four of 626 audit events used the write
    API. Twelve improvements delivered in 84 minutes; four writes adopted in the working day since.
    The asymmetry is ours to answer.

### 6.3 Genuine open questions

| # | Question | Why it is a question, and what would settle it |
|---|---|---|
| Q-1 | Should `reset-book` be reachable without seeding first? | It keeps `app_user` by design (append-only audit) and needs an admin to survive. Documenting *"seed, then reset"* may be the whole answer. |
| Q-2 | Can a tolerance breach ever raise an exception on a budget-less, baseline-less programme? | We set a one-day tolerance, recorded a baseline finish and slipped it four months, and saw `exceptions: []` throughout. `sweepExceptions()` runs on an **hourly** `setInterval` (`server/src/index.js:428`) with no immediate first pass and no route to trigger it, so nothing could be observed inside a session. **[Open — leave an instance running past a sweep tick, or add a manual trigger.]** Separately, `Engine.tolerance` needs `bac > 0` for a cost breach (`shared/engine.js:585-615`), so on a budget-less programme that dimension is inert by construction. |
| Q-3 | Is the administrator break-glass acceptable for a machine loader? | Documented, deliberate and labelled on every use — and our loader *is* an administrator, so segregation of duties is bypassable by whoever holds that credential. This is a question for us at least as much as for them. |
| Q-4 | Do the portfolio tiles rescope with the PROGRAMME selector? | There **is** a per-programme page with its own tiles. Whether the *portfolio* tiles narrow is unanswerable on a one-programme book. **[Open — load a second programme and compare.]** |
| Q-5 | Can a decision record supersede one loaded from an external ledger? | Untested: our own ledger rows were too short to load the predecessor. **[Open]** |
| Q-6 | Can a book created **before** its programme declared a ladder be migrated onto it? | This is the only half of REQ-27 that survives, and **we cannot test it** — our book was created after. Their `answerToSource` offers `adopt` on `PUT /api/v1/milestones` as the interim (`server/src/v1write.js:161-213`), which we have not adopted. **[Open]** |
| Q-7 | What does the `OPEN RISKS` tile count? | Round one implied the tiles ignore our programme, from `OPEN RISKS 45` against 122 register items. On the empty book it reads `42` against 165 register items, consistent with counting only items typed *Risk*. We withdraw the implication. **[Open — one read of the tile's derivation would settle it.]** |
| Q-8 | Is `# NaN` in the pipeline rank column a defect or an unfinished view? | The page refuses to rank unscored projects and says so, which is right. The `NaN` is cosmetic. Theirs to classify; we do not file it. |
| Q-9 | Has anyone other than its author exercised the 5.10.0 work? | The register's `accepted` is false on all 31 lines, and the rule is *"the requester said so on the issue"* — so the loop is open on **our** side, not theirs. **[Open — and §9 argues it is the most valuable thing to close.]** |

---

## 7. The requirements, consolidated

### 7.1 The register file, and why the previous one must not be filed

`docs/REPORTS/meridian_requests_v3.json` — `meridian-request-register/1`, `registerVersion: 7`, 25
requests. It parses, and every request object uses their field names (`id`, `origin`, `title`,
`status`, `version`, `decidedOn`, `delivered`, `measure`, `remaining`, `answerToSource`, `issue`,
`accepted`, `released`, `observed`, `history`), plus `priority` — which their own REQ-20..REQ-27
already carry — and two additive keys, `effort` and `rt365`, which a reader may drop without loss.

Three rules govern it, and they exist because our previous file broke all three:

1. **Their ids are theirs.** REQ-06, REQ-09, REQ-16, REQ-17, REQ-19 and REQ-20..REQ-31 appear with
   `id`, `status`, `delivered`, `issue`, `accepted` and `released` copied from their registerVersion
   6 **unchanged**. We add measured evidence in `observed`, a recommended `priority`/`effort`, and one
   `history` row. **No status on any of their lines is changed by this file**, and `accepted` stays
   false everywhere — including on REQ-06, which we have now measured working — because filing an
   acceptance is a human act (H-31) and no agent may record one on the owner's behalf.
2. **What round two changed is restated, not re-filed.** REQ-27 (our V-8) carries the withdrawal in
   full: the duplication was our loader; the delivered half is now confirmed by measurement; only the
   migration clause remains, and we cannot test it.
3. **New requests start at REQ-32.** Our prepared `docs/PMO/meridian_requests_v2.json` numbered items
   REQ-14..REQ-28 — colliding with their delivered REQ-14 (raised from our D-057) and duplicating
   REQ-20..REQ-31. It is **withdrawn before filing**, and the v3 file records that in
   `source.supersedes`.

### 7.2 The consolidated list

Effort: S = days, M = weeks, L = a release — our estimate of the work as we would scope it, not a
commitment on Meridian's side. Priority is our recommendation, not a decision.

| REQ | Requirement, and the user-visible behaviour it creates | Measurable acceptance criterion | Effort | Priority | Depends on |
|---|---|---|---|---|---|
| **REQ-32** *(new)* | **The default branch carries what the register calls done, and there is a tag to clone.** An evaluator who follows the README gets the product the register describes, and can name the version they run to an auditor. | A clone of the default branch with no flags reports the version the register names, contains `docs/requests/rt365.json`, completes the README quick start unaided (the seed persists to disk, `/` answers 200, the documented first login succeeds), states its own test count correctly, and carries a tag naming that version; a CI check fails when any request marked `done` names files the default branch does not contain. | S | **highest** | — |
| **REQ-33** *(new)* | **Unmeasured is not green.** A project with nothing measured reads as *not measured*, and no schedule or cost index of 1.00 is asserted for it anywhere. | On a book of N budget-less projects with no reported progress the tile reads `0 green · 0 amber · 0 red · N not measured`, the health cell reads *not measured* with its reason, and no index of 1.00 appears for those projects on any page, print, export or `/api/v1` resource; a project with a budget and reported progress is unchanged; a project below the 2 % spend threshold reads *too early to measure*. | S | **highest** | — |
| **REQ-34** *(new, was our V-13)* | **Value and learning objects follow the programme's ladder.** On a six-gate ladder a case can be reconfirmed at gate 6 and a lesson tagged to gate 5. | A case is reconfirmed at gate 6 and a lesson tagged to gate 5 on a six-gate programme; a gate outside the declared ladder is refused with a named reason; four-gate books are unaffected; the migration alters no stored value. | S | **highest** | — |
| **REQ-20** *(theirs, open)* | **Value objects in the write API v1.** A field repository keeps the business case and the benefits as fresh as the register — one command, no forms — and the audit names the integration. | An integration key with `write:portfolio` creates one case and three benefits by external id; a second identical run makes zero creating writes; both appear in `/api/v1/portfolio` and in the audit under the integration's name; a key without the scope is refused; a transition requiring `benefit.review` is refused to a key lacking it, with a named reason. | S | **highest** | — |
| **REQ-22** *(theirs, open; our V-3)* | **The gate cannot pass without a reconfirmed case.** At every gate the room is asked, on the record, *"is this still worth doing?"*, with both numbers and how far they have moved. An override remains, with a reason. | Advancing a project whose case is unreconfirmed at the gate being left is refused with a named reason; reconfirming then advancing succeeds; editing the case after reconfirmation makes the advance fail again; the gate record carries the case id, its `row_version`, the expected-cost and expected-benefit delta and the reconfirmer; an override still requires `overrideWhy`. | S | **highest** | REQ-34 |
| **REQ-21** *(theirs, open; our V-2)* | **The benefit review is a scheduled act.** A benefits owner named at closure receives the meeting item that makes them accountable, months after the team has dispersed. | A benefit past `realise_on` and still `Forecast` appears automatically in the next generated agenda of the board owning its project and in an overdue list on the portfolio and on `/api/v1`; recording a `benefit.review` clears both; the audit names the reviewer, the date and the measurement ruled against; a benefit with no `realise_on` is listed separately as *undated*. | M | **highest** | REQ-35 for the exception half |
| **REQ-31** *(theirs, open; our V-12)* | **Publish the field-repository loop as a reusable pattern.** A second field repository files its findings and sees them tracked, without either side writing code for the other. | A JSON Schema for `meridian-request-register/1` exists in the repository and the register validates against it in CI; the review script takes the register path and the id vocabulary as configuration; a second fixture repository is reviewed end to end in a test; the round is documented in English on one page. | S | **highest** *(raised from high — §9)* | REQ-32 |
| **REQ-35** *(new, was our V-14)* | **Not measured is not within tolerance.** A project that never measures its benefits stops reading as a project inside its margin. | A project whose benefits are all unmeasured with realisation dates passed raises an exception naming how many and since when; it carries its two numbers and closes only by an answer; the display distinguishes *no margin set*, *nothing measured* and *within margin*; a project with no benefits raises no duplicate. | S | high | — |
| **REQ-23** *(theirs, open; our V-4)* | **Forecast versus realised, as one report, without converting units.** One page and one `/api/v1` resource answering *"what did we promise, what did we get, what do we not yet know"*. | Per project: case figures with basis and reconfirmation state; each benefit's baseline/target/actual in its own unit, attainment, status, review age; totals sum money-denominated benefits only and state how many non-money benefits are excluded and in which units; a case with no benefits and benefits with no case are each visible as such; **no derived currency conversion anywhere**. | M | high | REQ-20, REQ-33 |
| **REQ-24** *(theirs, open; our V-5)* | **Prioritisation reads the value and risk the product already holds.** The screen shows why each item sits where it does, and where both the money and the people run out; the weighting becomes a governed, auditable policy. | Each row shows score with every input, hand rank, budget, expected benefit or *no case*, a confidence flag from basis/reconfirmation/staleness, RAID exposure band and FTE demand; two cut lines are drawn, money and capacity; changing a weight re-ranks, is refused below group level and is audited before/after; an unscored item still sorts last and is never treated as worst. | M | high | REQ-23 |
| **REQ-28** *(theirs, open; our V-9)* | **Governance quality signals**: decision latency, action ageing, gate cycle time, register review compliance, open-exception age — all from timestamps that already exist. | Each metric computed from existing rows with no new field, shown per programme with a period-on-period trend, available on `/api/v1`, defined in one place with the timestamps it uses; too few closed items shows *insufficient data* rather than a number. | S | medium *(the best small win if a spare week appears early)* | — |
| **REQ-17** *(theirs, open)* | **A public write for structure**, under a scope an administrator grants, so a machine writes as a machine from the first call. | An integration key with a structure scope creates a site, a programme with its `gateModel`, and people; a first load completes with no human session; the audit names the integration on every row; the scope can be granted separately from `write:portfolio`. | M | medium | — |
| **REQ-29** *(theirs, open; our V-10)* | **Evidence provenance for gate criteria.** *"Which test proves this criterion"* is answerable with a commit and a digest, not only a link. | A criterion carries a typed external reference with a locator and a digest supplied by the citing system; the gate record shows what was cited, by whom and when; replacing it after the gate creates a new version with `supersedes` lineage; 037's independence rule still holds; Meridian never fetches or re-computes the digest and does not claim to have verified it. | M | medium | — |
| **REQ-26** *(theirs, open; our V-7)* | **Lessons become a checklist at the gate**, not an archive. | Opening the gate review shows every `Adopted` lesson tagged to that gate in the same programme or site, excluding the project's own; each is recorded considered or not-applicable with an optional note; the gate record and audit keep the list and the reviewer; with no lessons tagged the gate behaves exactly as before. | S | medium | REQ-34 |
| **REQ-37** *(new)* | **A phased rollout to one site can be recorded.** | Three waves with different `seq` are recorded against the same project and site and read back in order; existing one-wave books are unaffected; if one-per-site is the intended design, `seq` is removed and the 409 says so. | S | medium | — |
| **REQ-25** *(theirs, open; our V-6)* | **Adoption per rollout wave, linked to the benefits it should move.** A wave that went live and is not being used says so, months before the realisation date. | A wave carries adoption measure, unit, source, date and threshold; a `Live` wave below its threshold appears in the exception list and on the next agenda; each benefit page lists its feeding waves with their trend; a wave with no measure reads *not measured*, never zero. | M | medium | REQ-20, REQ-37 |
| **REQ-30** *(theirs, open; our V-11)* | **A value dashboard, snapshotted per period.** A sponsor without the tool open is handed one page; a later reader reproduces exactly what it said at the time. | Generated from existing objects with no manual entry, prints on one sheet per programme; closing a period writes the extended snapshot; reopening a closed period is refused as today; the page rendered from a past snapshot equals what it showed at that close, field for field. | M | medium | REQ-23, REQ-33 |
| **REQ-36** *(new, was our V-15)* | **Carry the promise across the conversion.** The sponsor's own words about what the thing is *for* survive into the project that spends the money. | Converting an approved demand creates a case carrying `benefit_note` and `est_cost` and citing the demand id; it appears on the project immediately; conversion is refused without a case where the programme requires one, with a named reason; a demand with no `benefit_note` still converts and the case is visibly a draft, never a fabricated justification. | S | medium | — |
| **REQ-39** *(new)* | **An action can be owned by a body, not only a person.** | An action is created with a body as owner and appears on that body's agenda; closing it still records a named person; person-owned actions are unchanged; a body with no scheduled meeting is reported as such rather than silently unowned. | M | medium | — |
| **REQ-19** *(theirs, open)* | **A write refuses a body it does not understand** rather than returning 200 and auditing something else. | An unrecognised field is refused with a named reason on both v1 and session write routes; a body with no recognised field is refused; no audit row is written for an operation not performed. | S | medium | — |
| **REQ-16** *(theirs, open)* | **Raise an action or a decision into the next scheduled occurrence, without opening it.** A one-way integrator keeps working on the day the record is frozen. | With the current occurrence closed, an action or decision posted to the series lands in the next scheduled occurrence; the closed occurrence is unchanged; the API still never opens a meeting. | M | medium | — |
| **REQ-38** *(new)* | **An accepted milestone reads as accepted.** | A milestone patched done with a named accepter renders as accepted, with the accepter and the date, on the project page and in the evidence pack; a milestone marked done without an accepter is still refused at the write path. | S | low | — |
| **REQ-06, REQ-09, REQ-27** | Referenced with measured evidence, no new requirement. REQ-06 is confirmed working; REQ-09 is confirmed built and not reachable from the default branch (hence REQ-32); REQ-27 is restated with our defect claim withdrawn. | — | — | — | — |

### 7.3 What we are deliberately **not** asking for

- **An OKR object.** `business_case` and `benefit` already carry objective, measure, unit, baseline,
  target and actual. A second vocabulary splits the truth and doubles the data entry; whichever is
  easier to fill in becomes the one nobody trusts. The gap is enforcement, not vocabulary.
- **A money-normalised portfolio value.** Migration 008 is right that value is not always money-
  shaped, and a conversion factor from tonnes or availability points to currency is a number somebody
  invents and everybody then quotes. REQ-23's acceptance criterion forbids it explicitly.
- **Any AI or model-driven feature** — no risk prediction, no benefit forecasting, no meeting
  summarisation, no assistant. The worth of this product is that its record is trustworthy, and every
  requirement above is arithmetic on data a named human entered or a named integration wrote.
  Introducing a probabilistic step into a governance record whose whole value is that it is not
  probabilistic would be a mistake. This is our own standing rule and we hold ourselves to it.
- **Requirements, tests, traceability or work tracking inside Meridian.** Our engineering truth stays
  in a repository evidenced by CI (ADR-017); REQ-29 asks only that a criterion be able to *cite* it.
  A portfolio tool that becomes the delivery system competes with the tools the teams already use and
  loses.
- **A portfolio-of-portfolios level, a second ladder concept, or per-benefit workflow configuration.**
  Each is a plausible enterprise ask and each adds configuration surface to a product whose current
  strength is that a PMO can hold the whole model in their head.

---

## 8. Sequencing

**Round 0 — before anything else, and it is not a feature: REQ-32.** Merge to the default branch and
push the tag. Days, if that. Until it is done, an evaluator's first hour is a 5.9.0 book that
vanishes at exit, and none of the twenty-four other lines in §7 exists for anybody outside the
maintainer's checkout.

**Round 1 — the two that change what a page asserts and what a room decides: REQ-33, then
REQ-34 + REQ-22.** REQ-33 stops the product asserting a positive it cannot support, on the page a
sponsor reads; it is a derivation, S. REQ-34 is one migration and one validation and it unblocks two
of the three highest-value requests already open in the register. REQ-22 then turns a field that
already exists, whose staleness is already computed and already displayed, into a control at the
moment a room is assembled and already deciding — the cheapest possible place to add the highest-value
question.

**Round 2 — the plumbing that stops the value half going stale: REQ-20, then REQ-21 with REQ-35.**
REQ-20 makes value facts as syncable as delivery facts, which is what makes every later report worth
reading. REQ-21 and REQ-35 close the other end: the review that must happen after closure, and the
arithmetic that stops *never measured* reading as *within margin*.

**Round 3 — the confrontation, and making the loop reusable: REQ-23, REQ-30, REQ-31.** With the data
fresh, the gates enforcing and the reviews chased, forecast-versus-realised finally has something
true to show, and the period snapshot makes it re-readable a year later. REQ-31 in the same round
because it is S and because it is what turns one remarkable day into a repeatable capability for the
next field repository.

**Then, as capacity allows:** REQ-17 and REQ-19 (so a machine writes as a machine, and a write that
is not understood is refused), REQ-28 (five metrics, no new data entry — the best small win on the
list if a spare week appears earlier), REQ-24, REQ-36, REQ-26, REQ-37, REQ-25, REQ-39, REQ-38.

**If only one thing gets done: REQ-32.** We considered recommending REQ-33, which is the more
interesting engineering problem and the finding we care most about. We recommend REQ-32 instead
because it is the only item whose absence makes every other item unobservable. A defect that an
evaluator cannot reach is not a defect they will report; a strength they cannot reach is not a
strength they will believe. Confidence **high** — it is a merge and a tag, and their own register
already names both as pending a maintainer.

**If two things get done: REQ-32 then REQ-33.** Confidence **high** on the technical claim (the code
path is three lines and a fourth enum value) and **medium** on the value claim, because we have not
yet watched a sponsor read a corrected page — that is exactly what our Gate B and Gate C would
evidence, and we would report the result back. [Open]

---

## 9. What "flagship" would require

The owner's stated aim is a flagship product. On the evidence of two rounds, the distance between
what Meridian is and what a flagship is consists mostly of things that are not features. We rank them
by how much each would change an evaluator's mind, which is not the same as how hard each is.

**1. A default branch that carries the product, and a tag. [Measured — this is the whole of §2.1.]**
Rank 1 because it is the only item that gates every other item. Today the sentence an honest
evaluator writes is: *"the improvements exist on a branch you must know to ask for."* Effort: a merge
and a push. Nothing on this list is cheaper or worth more.

**2. Evidence that anyone but its author has run it. [Open — Q-9.]** Their register's `accepted` is
false on all 31 lines because the rule is *"the requester said so on the issue"*, and the requester —
us — has not said so, because saying so is a human act in our programme. So the loop is open on our
side. But the deeper version of this is not about us: **we cannot tell, from outside, a fast
maintainer from an unreviewed one.** The suite passes (520/102/0 fail) and the journey test replays
the life of an organisation on every run, which is real evidence of care. It is not evidence of a
second pair of eyes. One named person who is not the author, reviewing one release and saying so in
public, would change more minds than five features. Rank 2.

**3. A second maintainer. [Measured: 621 of 626 audit events on our book name one account; every one
of the seven branch commits has one author.]** Every requirement in §7 is worth less than the answer
to *"what happens to this register when you are unavailable for a month"*. This is the item we would
most like to see and the one we can least help with. Rank 3.

**4. Someone else's programme, in a different shape. [Measured: we are one programme, sixteen
projects, 176 register items, one weekly, one day.]** We are a regulated trading programme: our
ladder is six long, our evidence is CI-shaped, our tolerance for an unenforced control is low, and
our "benefits" are things we deliberately decline to quantify. Some of what we ask for is universal
(REQ-32, REQ-33, REQ-20, REQ-34). Some is our shape talking (REQ-29 in particular, and the strictness
in REQ-22). A second, differently-shaped field repository — an industrial rollout, a public-sector
programme, anything with real money and real adoption curves — is worth more to Meridian than
anything on our list, and REQ-31 is what makes that cheap. Rank 4.

**5. An operated instance, by somebody, for a quarter. [Measured: everything in this report is a
laptop-class PGlite instance; our own H-28 is open.]** The product refuses PGlite in production,
ships a runbook, proves a restore and publishes it on `/api/health` — the kit is there and nobody has
paid the operating cost. The number a PMO considering it actually wants — what it costs to run as a
system of record for a year — nobody can report. Rank 5.

**6. Then, and only then, the features that make value bite.** REQ-33, REQ-34, REQ-22, REQ-20,
REQ-21, REQ-23. Everything in §5 is a **noun**: a case, a benefit, a tolerance, an exception, a
lesson, a reconfirmation. Value gets realised by **verbs**: a write that happens automatically, a
gate that refuses, a date that summons someone, a number confronted with another number, a queue that
is ordered. Meridian has more of the right nouns than any open portfolio tool we have seen and almost
none of the verbs. That is a small, well-defined amount of work — most of it days — on a foundation
that is already right. Rank 6, and it is a compliment: this is the easy part, and it is last only
because the five above it decide whether anyone is looking.

**What we would not call flagship, and would advise against.** A wider surface. The product's current
strength is that a PMO can hold the whole model in their head and that every refusal has a sentence
attached. Fifteen more configuration options, a plugin system, a second ladder concept or an AI
assistant would each buy a demo and cost the thing that is actually rare here — that its record is
trustworthy and that its author can explain every derivation on the screen.

---

## 10. Concerns for the Product Owner

*These are ours, held as our own product owner would hold them about our own product, and offered
because a report that only asks for features is worth less than one that says what worries it.*

**1. We published that twelve improvements were shipped, and they were pushed to a branch.** That is
our error, not Meridian's, and it is the most serious thing in this report about us. It happened
because we verified the code and did not verify the *distribution* — we read `server/src/env.js` on a
checkout we already had, and never asked what a stranger would get. We would refuse a gate for
exactly that: evidence read at the wrong commit, on the wrong ref, by the party who wanted it to be
true. The rule we are taking from it is that a supplier claim is verified from a clean clone of the
default branch or it is not verified.

**2. We are their first real portfolio, and we are a thin evidence base for both of us.** Sixteen
projects, 176 register items, one weekly, one day, one shape, run by agents under a human owner. Our
numbers are honest and they are one programme. Please weigh this as one field report and not as a
market. We would treat a second, differently-shaped field repository as more valuable to Meridian
than anything on our own list — which is the other reason REQ-31 is ranked as it is.

**3. Beware of us as a requirements source.** We are a regulated trading programme; our gate ladder
is six long, our evidence is CI-shaped, our tolerance for an unenforced control is low, and our
benefits are things we deliberately decline to quantify. If a requirement in §7 only makes sense for
a programme like ours, we would rather it were declined with a reason than carried as debt in their
register. A declined request with a reason is a better artefact than an open one nobody intends to
build.

**4. Velocity is now the product's main correctness risk, and we contributed to it.** Two of the
defects in this report (D-1, D-2) were created by the very feature that closed our own finding in the
same release: the ladder became configurable, and the case and the lesson stayed capped at gate 4.
Nothing was careless — but a change that frees a dimension has to be followed through every table
that assumed it was fixed, and one day is not long enough to find them all. We filed twelve findings
before lunch and a maintainer shipped all twelve before the afternoon; we should ask ourselves
whether that was a good thing to do to someone.

**5. Meridian says this programme is green, and it must not leave this room.** Sixteen projects,
100 % on track, SPI and CPI 1.00, in a week when Gate B was not convened and two of its exit
documents were refused. The tool is not lying — health derives from schedule and cost, we gave it
neither, and its default for nothing is green. But if anyone quotes the portfolio page instead of the
session packet, they will report the opposite of the truth about this programme, in colour, to a
sponsor. Until REQ-33 lands or we stop feeding it budget-less projects, the Meridian portfolio view
is **not quotable outside this room**, and I would rather say that out loud than find it in a
steering pack.

**6. Our own ledgers are the weaker half of this integration, and driving them into a tool proved
it.** Our register states no probability and no impact, so every rating on the screen is derived.
Nine of our decision rows are too short to be published as decision records. Twenty-eight of our
twenty-nine open human acts have no date, and fourteen name a committee rather than a person. None of
that is Meridian's fault and all of it is a finding about how we govern. The tool did us the service
of making it visible in one afternoon.

**7. Our loader is an administrator, and that is a security posture we should not keep.** 621 of 626
audit events name one human account, whose password lives in the loader's environment; Meridian's
documented break-glass then let that one account sign all four steps of a change request. Every step
is labelled `BREAK-GLASS` in the trail, which is the tool behaving well. It is still a credential
this programme holds, in a place this programme has not threat-modelled, for a system that carries
none of our controls. REQ-17 would fix the tool's half; the other half is ours and it is open.

**8. We adopted almost nothing that was built for us.** Four of 626 audit events used the write API.
The loader is byte-identical across the upgrade. Twelve improvements arrived in 84 minutes; a working
day later we had taken up four writes' worth. Some of that is D-5 (a first load cannot start on the
public contract), and some of it is simply that we asked and did not follow through. A supplier who
answers that fast and gets no adoption back will, quite reasonably, stop answering that fast.

**9. This document has no reviewer, and it should not travel without one.** I wrote it; I own several
of the ledgers it draws on; the rule in this programme is author ≠ reviewer ≠ approver. Nothing here
is certified, no evidence is declared complete, no gate is convened, no environment is promoted and
no approval is recorded on anyone's behalf. It needs a second line before it goes to Meridian's
Product Owner, and **filing it upstream is a human act on our owner's account (H-31), not mine to
perform.**

**10. And the thing I would say to their Product Owner if I could say only one thing.** You have
built the most carefully reasoned governance record I have used, and you have not yet shipped it. The
gap between those two facts is a merge and a tag. Everything else in this report can wait behind that.

---

## 11. Evidence index and provenance

**Round two (authoritative), `docs/REPORTS/PMO/round2/`:** `EVIDENCE.md` (the measured half, 960
lines) · `GUARD_PROBE.md` (the write-scope refusal, verbatim) · `firsthour_A_main_5.9.0.txt` (the
documented quick start on the default branch, failing) · `firsthour_B_branch_5.10.0.txt` (the empty
book, six minutes) · `test_counts.txt`, `npm_test_A_main_5.9.0_summary.txt`,
`npm_test_B_branch_5.10.0_summary.txt` (449/80 and 520/102, verbatim) ·
`load_1_meridian_sync_run1.json` (307 writes) · `load_2_meridian_sync_run2.json` (the second run: one
request, a 200) · `load_3_hand_drive.json` (262 hand-driven requests with timings, bodies and status
codes) · `load_4_meridian_sync_run3_aborted.txt` (the 409 against the frozen record) ·
`probe_1.json`, `probe_2.json` (72 probes: the v1 surface, the ladder ceilings, the frozen record,
segregation of duties, health) · `backup_and_restore_drill.txt` ·
`01_portfolio.png` … `10_pipeline.png` and `screens_text.txt` · `drive.py`, `probes.py`,
`probes2.py`, `shots.py` (exactly what was run).

**Superseded halves:** `docs/REPORTS/PMO_MERIDIAN_REPORT_VALUE.md`,
`docs/REPORTS/PMO_MERIDIAN_REPORT_EVIDENCE.md`. **Round one:** `docs/PMO_MERIDIAN_ASSESSMENT.md`
§§1–8 (M-01..M-12, I-1..I-12, V-1..V-15), `docs/PMO.md`, `docs/PMO/*.json`, `docs/PMO/*.png`.
**Our side of the relationship:** `docs/ADRs/ADR-017.md`, `docs/IMPROVEMENT_REGISTER.md` §D and §D2,
`docs/MISSING_ACTIONS.md` H-28 and H-31. **Proposed ledger rows:**
`docs/SESSIONS/PACKET_2026-09-08_meridian_consolidated.md` — this session may not edit `RAID_LOG`,
`DECISION_LOG`, the RTM or the audit evidence index, so the rows are proposed there for the owning
roles.

**Meridian working copies, read-only, not modified:** `main` @ `77c4b49` and the branch @ `cbe99ef`.
`npm install`, `npm run seed`, `npm run reset-book`, `npm run build`, `npm test`, `npm run backup`,
`npm run restore-drill` and a checkout of a published ref are the only things done to either. No file
was edited, nothing was committed, nothing was pushed.

**Confidence.** **High** that every defect in §6.1 exists as described — each is a named file and,
where it matters, a named line, and each has a reproduction. **High** on the round-two measurements;
they were taken on an empty book with the request and the response recorded. **Medium** on the effort
estimates, which are ours and made without knowledge of Meridian's internal conventions. **Medium**
on the priorities, which are one programme's judgement. **[Open]** on Q-1..Q-9, on whether REQ-22
changes what a room decides in practice, and on whether anyone but the author has exercised the
5.10.0 work.

**A caveat about the measurement environment.** This repository was being written by other sessions
while round two ran; `docs/DECISION_LOG.md` gained three rows at 16:06, after the 16:00 load. That
drift is what produced the frozen-record finding (§2.2.3), so it is evidence rather than noise. Two
figures are snapshots of a moving ledger and are labelled where they appear: 66 decisions and 165
register items were the state at 16:00.

**What this document is not.** It certifies no evidence as complete. It convenes no gate. It promotes
no environment. It states no return, no forecast, no price and no market claim. It has not been filed
upstream. It records no approval, on our behalf or on Meridian's.


---

## 12. Round three, 2026-09-09 — what happened when we tried to install it

Rounds one and two read Meridian and ran it from a clone. Round three tried
to do the ordinary thing an adopting organisation does: **obtain an
installable Meridian and install it.** The full record, with commands and
hashes, is `docs/REPORTS/PMO/round3/PACKAGING_EVIDENCE.md`.

### 12.1 First, the good news, and it is substantial

Read on their `claude/meridian-rt365-feedback-d6vo3i` branch at `453d331`
(version **5.14.0**, register **v12**, 47 migrations): of the eight requests
RT365 proposed in registerVersion 7, **seven are marked done** — REQ-32,
REQ-33, REQ-34, REQ-35, REQ-36, REQ-37, REQ-38. Only **REQ-39** remains open.
Their register also carries nine further lines of their own (REQ-40..REQ-48)
that we did not ask for and have not measured. [Source: their
`docs/requests/rt365.json`, registerVersion 12, read at `453d331`]

That is a fast, complete answer to a field report, and it is the strongest
single piece of evidence in this document that Meridian's team can absorb
external findings. §1 said the loop was the product's best feature; this
round is the loop working.

### 12.2 REQ-39 is no longer a prediction

REQ-39 — the default branch carries what the register calls done, and there
is something to download — is the one line still open, and this round paid
its cost instead of estimating it. There is **no GitHub release at all** on
`mliad313sn/Meridian`; the newest tag is `v5.9.0`, which is the default
branch. Everything in §12.1 is invisible to anyone who has not cloned a
feature branch.

So the package this programme now runs on had to be **built from source**.
That is the finding: not that building is hard, but that in 2026 an adopter's
first act cannot be a download.

### 12.3 Three defects in the packaging path, one in the portfolio

| Id | What | Why it matters |
|---|---|---|
| REQ-49 | `build-exe.mjs` copies `process.execPath` as the SEA injection target, so a Windows package needs a Windows host | One environment variable removes it — and with it the last obstacle to the release REQ-39 asks for. We built a working Windows package on Linux to prove it |
| REQ-50 | The offline install promises the embedded engine; the packaged binary exits 2 without `DATABASE_URL` and never reads `PGLITE_DIR` | An air-gapped install **completes, reports success, and leaves a service that will never start**. The document and the binary disagree, and the document is the one people follow |
| REQ-51 | The executable is unsigned — injection invalidates node.exe's Authenticode signature — and no hash is published | Nothing lets a user tell a real artefact from a substituted one. RT365 carries the same defect (H-30); this is a shared problem, not a lecture |
| REQ-52 | `caseReconfirmations` is assigned twice in the same object literal in `server/src/portfolio.js`; the second wins silently | It is REQ-22's re-confirmation data — a value object, not a cosmetic field |

None is architectural. All four are a release workflow away.

### 12.4 What was verified, and what was not

The Windows executable was cross-built by injecting the SEA blob into the
official `node-v22.22.2-win-x64` binary, whose SHA-256 was checked against
`nodejs.org` before use; the artefact carries one `NODE_SEA_BLOB` resource
and a flipped fuse. Because a PE cannot run on the build host, the **same**
blob was injected into the host's own Node and booted: 47 migrations applied
against PostgreSQL, `/api/health` answering
`{"ok":true,"version":"5.14.0","build":"packaged","engine":"postgres"}`, the
client served, an unauthenticated API read refused. **[Measured]**

**[Open]** and stated wherever the package is handed over: the Windows
service registration, `prepare-db.ps1`, and SmartScreen behaviour. Those need
a Windows host, and this report claims nothing about them.

### 12.5 A third correction of ourselves

The register we handed over with v1.0 of this report declared
`"$schema": "meridian-request-register/1"` and **failed that schema in 55
places**: `proposed` is not one of its four statuses; `accepted: false` is
forbidden on an open line by an explicit rule — and was wrong in our own
words, since no agent here may record an acceptance at all (H-31); and every
history row we wrote omitted the required `status`. `registerVersion 8` is
the first version that validates clean, and nothing was re-stated to get
there.

The defect was ours. The reason it reached them is not: Meridian validates
the copy **it** holds, and the side that writes the register has no published
way to check the file first. Filed as **REQ-53**, and it belongs in §9's list
of what "flagship" requires — a contract with a validator on only one end is
a contract that bounces late.

### 12.6 What this changes in the recommendation

Nothing, except its urgency. §1 said: if only one thing gets done, merge to
the default branch and publish the tag. Round three found that the cheapest
path to that release is one environment variable (REQ-49), and that the first
thing an adopter without a network would hit afterwards is a service that
never starts (REQ-50). Those two, then the tag, is the whole of it.
