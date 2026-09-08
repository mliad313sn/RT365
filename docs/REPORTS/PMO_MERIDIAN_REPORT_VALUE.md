# Meridian IT-PMO — what it is worth to a real programme, and what would make it drive value

**A report prepared for the Product Owner of Meridian IT-PMO (mliad313sn/Meridian), by the Product Owner of Global AI-MCP RoboTrader (RT365).**

| Field | Value |
|---|---|
| Owner | RT365 Product Owner (delegate agent, under D-039/D-040/D-065) |
| Reviewer (different line) | RT365 Program Orchestrator (measured-evidence half of this report) |
| Addressed to | Meridian's Product Owner (named upstream in commit b58f806; charter `docs/33-retour-terrain-rt365.md#1`) [Source: Meridian `docs/requests/rt365.json` → `productOwner.charter`] |
| Subject version | Meridian 5.10.0, commit e352bc8, migrations 001–039 |
| Status | v1.0 — 2026-09-08. **Prepared, not filed.** Filing upstream is a human act on the owner's account (H-31). This report recommends; it decides nothing on Meridian's behalf and records no approval. |
| Machine-readable half | `docs/REPORTS/meridian_requests_v2.json` — `meridian-request-register/1`, REQ-14…REQ-28 |

**Intended filename.** This document was asked for at `docs/PMO_MERIDIAN_REPORT_VALUE.md` and the register at `docs/PMO/meridian_requests_v2.json`. The repository's agent write-scope guard (`scripts/agent_guard.py`, roster `.claude/agents/roster.json`) refuses both paths to the `product-owner` role — neither `docs/PMO_MERIDIAN_REPORT_VALUE.md` nor `docs/PMO/` is in its owned set, and **no** role in the roster owns any `docs/PMO*` path. Both files are therefore written in `docs/REPORTS/`, which the role does own. Moving them to the requested paths is a one-line roster change or a commit by the owning role; it was not routed around. [Measured: the guard refused the write with `agent_guard: agent 'product-owner' may not edit docs/PMO_MERIDIAN_REPORT_VALUE.md`.]

**How to read the tags.** [Measured] — we ran it and the number is ours, with the ledger that records the run. [Source: path] — read in Meridian's own code or documents at commit e352bc8, cited by file and, where it matters, by line. [Open] — not established; the source that would settle it is named. Nothing here asserts a Meridian capability that was not read in its code. No benefit figure, price or return is invented anywhere in this report, and none is implied.

---

## 1. The verdict a sponsor needs

Meridian at 5.10.0 is a governance and rhythm system that a real programme can run on today, and — uniquely among the portfolio tools we have used — one whose gaps close at the speed its users report them: we filed twelve field findings on 2026-09-08 and all twelve were delivered upstream the same day, on a release that also fixed 27 findings raised by two counsellors its own owner convened, with 513 tests passing in 101 suites and a request register (`docs/requests/rt365.json`) created so that the next field report has somewhere to land [Measured: docs/PMO_MERIDIAN_ASSESSMENT.md §7; Source: Meridian commits b58f806, e352bc8, `docs/requests/rt365.json`]. On the narrow question a sponsor actually asks — *will this tool make my programme deliver business value, or only prove it was run tidily?* — the honest answer is that Meridian has the **best value data model we have seen in an open portfolio tool and almost none of the machinery that makes such a model bite**: a business case with its cost, its benefit, the basis for both and a reconfirmation act; benefits that are not forced into money, carry their own measure and unit, and separate the measurement from the verdict; a closure that refuses to complete without a named benefits owner; tolerances that include a benefit dimension and an hourly sweep that raises exceptions nobody has to be brave enough to escalate [Source: `server/migrations/008_benefits.sql`, `028_business_case.sql`, `026_tolerance.sql`, `server/src/routes/portfolio.js:370`, `server/src/exceptions.js`]. What is missing is not vocabulary but consequence: value facts cannot be written through the integration API that delivery facts now flow through, no gate is blocked by an unreconfirmed case, no date on a benefit ever summons anyone, an unmeasured benefit is arithmetically indistinguishable from a benefit inside tolerance, and forecast and realised sit in two tables that the product never confronts. That is a small, well-defined amount of work — most of it days, not releases — on a foundation that is already right, and the one-day loop is the reason to believe it will actually get done.

---

## 2. What the value model already gets right

These are design choices, not accidents; each is written down with its reasoning in the migration that introduced it, and each is one that most commercial PPM tools get wrong.

**2.1 Value is not forced into money.** `benefit` carries `kind` (Production, Availability, Cost, Risk, Compliance), its own `measure` and `unit`, and holds `baseline`, `target` and `actual` *in that unit* — with an explicit instruction that these numbers are never divided by 1e6 like the money elsewhere in the product [Source: `server/migrations/008_benefits.sql`, header and columns]. A tool that demands a currency for every benefit gets a currency for every benefit, invented. Meridian refuses to make people invent, and says so in the schema comment: *"Value here is spoken in production, plant availability, hours and cost per ounce as often as in currency."* This is the single most important decision in the whole value model and it is correct.

**2.2 The verdict is separated from the measurement.** A project manager records what was measured (`benefit.write`); whether that counts as met is a group-level act (`benefit.review`, a `GROUP_ONLY` write), by the same independence rule that stops the raiser of a change deciding it [Source: `shared/rbac.js:37,86-99`; `server/src/routes/portfolio.js:1871`]. The post-implementation verdict is a distinct route, refuses a verdict short of "Met" without a written reason, and is audited with before/after images [Source: `server/src/routes/portfolio.js` `PATCH /projects/:id/review`]. This is the difference between a benefits register and a benefits *claim*.

**2.3 Unmeasured is not zero.** `Engine.attainment` returns null unless baseline, target and actual are all present, with the reason written in the code: *"an unmeasured benefit is not a zero, and showing it as one is how a portfolio lies"* [Source: `shared/engine.js:552-561,646-651`]. The portfolio page follows through: it shows `uncased`, the count of projects promising nothing at all, described in the view code as *"the number that says whether this programme is governed by value or only by cost"* [Source: `web/src/views/index.js:790-806`, `shared/engine.js` `valueProfile`]. A tool that puts the embarrassing number on the front page is a tool built by someone who has run a portfolio.

**2.4 Closure is refused without a named benefits owner.** Advancing to `Closed` requires both a named operations owner and a named benefits owner, both verified to be active people in the directory, with the reason in the code — *"benefits realise AFTER closure"* [Source: `server/src/routes/portfolio.js:365-380`]. Every organisation loses benefits at exactly this moment; almost no tool defends it at the write path.

**2.5 The case carries its basis and a reconfirmation.** `business_case` holds `summary`, `expected_cost`, `expected_benefit`, and `basis` — *"a number without its basis gets argued about; a number with its basis gets checked"* — plus `reconfirmed_gate`, `reconfirmed_on`, `reconfirmed_by` as a *distinct act* from editing the case, one case per project enforced by `UNIQUE` so two competing justifications for the same money cannot coexist [Source: `server/migrations/028_business_case.sql`]. Better still: the reconfirm route clears `updated_on`, and the serialiser derives `staleSinceReconfirm` from the ordering of the two, so a case reconfirmed and then quietly revised *shows as stale* rather than as confirmed — encoded by event order, not by comparing two same-day dates [Source: `server/src/routes/portfolio.js` `POST /projects/:id/case/reconfirm`; `server/src/portfolio.js:356-372`]. That is a subtle failure mode caught deliberately.

**2.6 Exceptions are found, not raised.** Tolerances are set by the level above (`tolerance.set` is a group write), a sweep constates breaches hourly on the same numbers the screen shows, one open exception per project per dimension is guaranteed by a partial unique index at the database, and an exception never closes by itself — the forecast may drift back inside the margin, the exception stays open until someone answers with one of the four PRINCE2 responses [Source: `server/migrations/026_tolerance.sql`; `server/src/exceptions.js`]. The stated reason — *"what depends on a bearer of bad news does not travel"* — is the correct reason.

**2.7 The value objects are already readable by machines.** `/api/v1/portfolio` returns benefits and business cases through the same serialiser the screen uses (*"nothing in the API that the screen does not show"*), and the `reporting.benefits` and `reporting.business_cases` views give a BI tool a stable contract without a connector [Source: `server/src/routes/v1.js:49-62`; `server/migrations/029_reporting_views.sql:83,106`]. Half the integration problem for value is therefore already solved — the read half.

**2.8 The period snapshot already counts benefits.** `report_snapshot` is append-only at the database (rules refuse UPDATE and DELETE) and already carries `benefits_promised`, `benefits_measured`, `benefits_met` per project per closed period [Source: `server/migrations/009_periods.sql:42-79`]. A claim made in one period can already be re-read in another. This is the foundation V-11 below extends, not replaces.

**2.9 Prioritisation exists and is honest about its limits.** `demand` and `project` both carry `fit`, `value`, `risk`, `effort` scores (1–5, "few enough to hold in a room"), plus a hand-placed `rank_seq` for when the room overrules the model; `Engine.prioritise` orders a slate against a capex envelope, marks where the money runs out, and refuses to invent a constraint when no envelope is set — and an unscored project sorts to the bottom rather than pretending to be worst [Source: `server/migrations/011_demand_and_priority.sql`; `shared/engine.js:496-549`; `web/src/views/index.js:2713`]. **Our own earlier assessment said "Meridian ranks nothing today; `demand` carries no score." That was wrong, and this report corrects it.** The gap in prioritisation is narrower and different from what we wrote (see V-5).

**2.10 The evidence model is stronger than "a document link".** A document carries a `uri`, required and host-checked at approval; the SHA-256 of that URI is locked at approval and changing the link afterwards drops the document back to "In review"; `supersedes` records lineage instead of a suffix convention; and a probe checks liveness without ever changing a document's state, because *"a satellite link going down must not un-approve a gate"* [Source: `server/migrations/014_evidence.sql`, `020_evidence_probe.sql`]. Our earlier phrasing — "evidence is a document link" — undersold this, and V-10 below is restated accordingly.

---

## 3. The gap: the objects exist, and nothing makes them bite

This is the argument of the report. Everything in §2 is a *noun*. Value gets realised by *verbs* — a write that happens automatically, a gate that refuses, a date that summons someone, a number that is confronted with another number, a queue that is ordered. Five verbs are missing, and each is missing in a way that can be pointed at in the code.

**3.1 Delivery facts sync; value facts are typed.** REQ-02 gave `PUT /api/v1/{projects,milestones,raid,activities,workitems,criteria}` under `write:portfolio` and `{decisions,actions}` under `write:meetings`, with external ids and `Idempotency-Key` [Source: `server/src/routes/v1.js:100-107`]. `business-case` and `benefits` are not among them; both are session-only routes (`PUT /projects/:id/case`, `POST /benefits`) [Source: `server/src/routes/portfolio.js`]. The measured consequence in this programme: our loader pushed **256 writes** covering 16 projects, 10 milestones and 122 RAID items, with a second run making **no creating writes at all**, and could not push a single benefit or business case [Measured: docs/PMO_MERIDIAN_ASSESSMENT.md §7; docs/PMO.md §4]. So the delivery half of the portfolio is fresh to the hour and the value half is as fresh as the last person who remembered to open a form. The one thing an executive reads is the one thing that goes stale. That is not a small asymmetry; it is the mechanism by which value reporting decays in every organisation that has ever tried it.

**3.2 No gate is blocked by the business case.** `Engine.canAdvance` checks two things: outstanding evidence documents and criteria not yet found met [Source: `shared/engine.js:338-352`]. It does not read `business_case` at all. So a project can pass every gate in its ladder with a case written once at inception, never reconfirmed, or reconfirmed and then revised — and the product *knows* this last state, because `staleSinceReconfirm` is computed and displayed (§2.5). The field exists, the staleness is computed, the screen shows it, and nothing stops. A stop/continue decision at each gate is the highest-value control a PMO owns and the one most often skipped; here the data to enforce it is already sitting in the row.

**3.3 Nothing chases a benefit review.** `benefit.realise_on` is stored, serialised as `realiseOn`, and rendered on the project page as `due <date>`. That is its entire life: it is written, and it is displayed [Source: `server/src/portfolio.js:288`; `web/src/views/index.js:3534,3607`; no other reader in `server/src`, `shared/` or `web/src`]. Nothing schedules anything when it passes. The meeting generator's only benefits section lists projects in Closure or closed and reports how many *Gate 4 documents* are approved — a document count, not a benefit review [Source: `shared/meetings.js:369-385`]. Benefits realise after closure, when the team has dispersed and the project has stopped appearing in anyone's week; a date that summons nobody is how the last mile of value reporting is lost.

**3.4 An unmeasured benefit is invisible to the mechanism designed to catch it.** The benefit tolerance dimension exists, and it is computed as the shortfall of *the weakest benefit that has an attainment* — and attainment is null unless baseline, target and actual are all present. If no benefit on the project has been measured, `out.benefit` is never set, so `breaches()` returns nothing on that dimension and the sweep raises no exception [Source: `shared/engine.js:611-627,646-651`; `server/src/exceptions.js`]. Additionally, the sweep only considers projects that have an *active tolerance* at all, and returns immediately if none exists. The result is exactly backwards for value: a project that measures its benefits and misses them raises an exception; a project that never measures anything raises nothing and reads as compliant. §2.3's principle — unmeasured is not zero — is correct in the arithmetic and unfinished in the governance, because *not measured* also is not *within tolerance*.

**3.5 Forecast and realised are never confronted.** `business_case.expected_benefit` (money, whole units, divided by 1e6 for display) lives in one table; `benefit.actual` (in the benefit's own unit, never divided) lives in another [Source: `server/migrations/028_business_case.sql`, `008_benefits.sql`; `server/src/portfolio.js` `toM`/`fromM`]. `Engine.valueProfile` — the closest thing to a value report — reads `db.benefits` only, and never looks at the case [Source: `shared/engine.js:652-680`]. So the product can tell you how many benefits were promised, measured and met, and it can tell you what the case expected, and it never puts the two on the same line. That confrontation is the report a sponsor wants and the only one that changes behaviour. (It must be done carefully: the two are not addable — see the acceptance criterion of V-4.)

**3.6 Nothing is prioritised by value.** The ranking that exists (§2.9) scores `value` as a bare 1–5 judgement typed by the PMO, orders against a *money* envelope only, uses a fixed weighting (`fit + value + (6−risk) + (6−effort)`) that is not displayed as a policy or adjustable, and never reads the business case, the benefits, the RAID exposure or the people capacity that `Engine.capacity` already computes [Source: `shared/engine.js:496-549,382-400`]. So the score that decides what gets done is disconnected from every value and risk fact the product holds. And the promise itself is dropped at the moment the money is committed: `POST /demand/:id/convert` copies the four scores, `est_cost` into `budget` and `detail` into `description`, but **not** `demand.benefit_note` — the field whose own schema comment is *"what it is FOR, in the sponsor's words"* — and creates no business case at all [Source: `server/src/routes/portfolio.js:1542-1582`; `server/migrations/011_demand_and_priority.sql:27`]. The chain the product's own design intends (demand → case → benefit → review, stated in the header of migration 028) is broken at its first link by the route that creates the project.

**3.7 And one thing that blocks the fixes.** The gate ladder became programme data at 036 and `gate_criterion.gate` accepts 1–12 [Source: `server/migrations/036_gate_ladder.sql`, `037_gate_criteria.sql`]. But `business_case.reconfirmed_gate` is `CHECK (reconfirmed_gate BETWEEN 1 AND 4)`, the reconfirm route rejects anything outside 1–4, and `lesson.gate_n` is `CHECK (gate_n BETWEEN 1 AND 4)` [Source: `server/migrations/028_business_case.sql`, `024_lessons.sql`; `server/src/routes/portfolio.js` reconfirm route]. Our programme runs a six-gate ladder (A–F). On such a ladder, a case **cannot** be reconfirmed at gates 5 and 6, and a lesson **cannot** be tagged to them. The value and learning objects were built against the fixed four-gate model and did not travel with the ladder when it was set free. This is a one-migration defect that silently caps two of the three highest-value requirements below.

---

## 4. The requirements, refined

V-1…V-12 restate the list from `docs/PMO_MERIDIAN_ASSESSMENT.md` §8, corrected where reading 5.10.0's code changed what is true (V-4, V-5, V-10 and V-11 are materially narrower than we first wrote, because more of them already exists). V-13, V-14 and V-15 are **new**, found in this reading. Effort: S = days, M = weeks, L = a release — our estimate of the work as we would scope it, not a commitment on Meridian's side. Priority is our recommendation to Meridian's Product Owner, not a decision.

---

### V-1 — Value objects in the write API v1 · REQ-14 · S · **highest** · no dependency

**Requirement.** `PUT /api/v1/business-case/{externalId}` and `PUT /api/v1/benefits/{externalId}` under `write:portfolio`, with the same external-id, idempotency, versioning and audit rules the delivery collections already have, and enforcing the same business rules the session routes enforce (`benefit.review` stays a group-level act; a status change through the API is refused to an integration key that does not carry that authority).

**User-visible behaviour.** A field repository's loader keeps the business case and the benefits as fresh as the RAID log — one command, no forms. The audit trail names the integration, so "who last changed the expected benefit" is answerable.

**Why a real programme needs it.** [Measured] Our loader makes 256 writes and cannot write one benefit (§3.1). Every hour that the delivery half is fresher than the value half, the executive view is a cost report wearing a value report's title.

**Acceptance criterion.** An integration key with `write:portfolio` creates one business case and three benefits by external id on a project it may see; a second identical run returns 200 with zero creating writes; both appear in `GET /api/v1/portfolio` and in `GET /api/v1/audit` under the integration's name; a key without the scope is refused; a status transition requiring `benefit.review` is refused to a key that lacks it, with a named reason.

**Evidence.** [Source: `server/src/routes/v1.js:100-107` (collections), `server/src/v1write.js`, `server/src/routes/portfolio.js` (`/benefits`, `/projects/:id/case`)]

---

### V-2 — The benefit review is a scheduled act · REQ-15 · M · **highest** · depends on V-14 for the exception half

**Requirement.** When `benefit.realise_on` passes without a review, an agenda item appears on the owning board's next occurrence, and the benefit joins an overdue-review list on the portfolio; recording the review clears it, and the trail keeps who reviewed, when, and against which measurement.

**User-visible behaviour.** A benefits owner named at closure receives the meeting item that makes them accountable, months after the project team has gone. The board's agenda gains a section that is about value rather than about document counts.

**Why a real programme needs it.** `realise_on` is written and displayed and read by nothing (§3.3). The meeting engine is the strongest thing Meridian has; the benefit review is the act most likely to be forgotten. Connecting the two is the highest-leverage use of a mechanism that already works.

**Acceptance criterion.** A benefit whose `realise_on` is in the past and whose status is still `Forecast` appears automatically in the next generated agenda of the board that owns its project, and in an overdue list on the portfolio page and on `/api/v1`; recording a `benefit.review` removes it from both; the audit row names the reviewer, the date and the `actual`/`measured_on` it was ruled against; a benefit with no `realise_on` is listed separately as *undated* rather than silently omitted.

**Evidence.** [Source: `shared/meetings.js:369-385` (present benefits section is a Gate-4 document count); `web/src/views/index.js:3534`; `server/src/portfolio.js:288`]

---

### V-3 — The business case is reconfirmed at every gate, and the gate cannot pass without it · REQ-16 · S · **highest** · depends on V-13

**Requirement.** Extend `Engine.canAdvance` so a project whose ladder declares a gate as case-bearing cannot advance while its case is missing, unreconfirmed at that gate, or `staleSinceReconfirm`; the gate record keeps the case version, the delta in expected cost and expected benefit against the previous reconfirmation, and who reconfirmed. Which gates are case-bearing is part of the programme's `gate_model` (default: all of them), and the existing override path with a written reason remains the escape hatch.

**User-visible behaviour.** At every gate the room is asked, and must answer on the record, "is this still worth doing?" — with the two numbers and how far they have moved since last time. An override is possible and leaves a reason a committee can read back.

**Why a real programme needs it.** The fields exist, the staleness is computed, the screen shows it, and nothing stops (§3.2). Continuous justification is what separates a portfolio from a project list, and it fails by omission, never by refusal.

**Acceptance criterion.** With gate locking on, advancing a project whose case has not been reconfirmed at the gate being left is refused with a named reason; reconfirming then advancing succeeds; editing the case after reconfirmation makes the advance fail again; the audit and the gate record carry the case id, its `row_version`, the expected-cost and expected-benefit delta against the previous reconfirmation, and the reconfirmer; an override still requires `overrideWhy`.

**Evidence.** [Source: `shared/engine.js:338-352`; `server/src/routes/portfolio.js` reconfirm route and `staleSinceReconfirm` in `server/src/portfolio.js:356-372`]

---

### V-4 — Forecast versus realised, as one report · REQ-17 · M · **high** · depends on V-1

**Requirement.** One value report per programme and per project confronting what the case promised with what the benefits measured — **without converting units**. Per project: expected cost and expected benefit with their basis and reconfirmation state; each benefit's baseline, target, actual and unit, its attainment, its status, its review age; the count of projects carrying no case and no benefit. Money benefits may be totalled against the case; non-money benefits are listed, never summed into it.

**User-visible behaviour.** One page and one `/api/v1` resource that answer "what did we promise, what did we get, and what do we not yet know" for a slate of projects.

**Why a real programme needs it.** The two halves exist in two tables that the product never puts on the same line (§3.5). This is the report the sponsor asks for and the only one that changes behaviour, because it is the one that makes a forecast a claim someone will be read back.

**Acceptance criterion.** For a programme with mixed benefit units, the report shows per project the case figures and each benefit in its own unit with its attainment and review age; the totals row sums money-denominated benefits only and states explicitly how many non-money benefits are excluded and in which units; a project with a case and no benefits, and a project with benefits and no case, are each visible as such rather than absent; the same object is served on `/api/v1` and matches the page field for field; **no derived currency conversion appears anywhere**.

**Evidence.** [Source: `shared/engine.js:652-680` (`valueProfile` reads benefits only); `server/migrations/028_business_case.sql` vs `008_benefits.sql` (money-in-millions vs own-unit)]

---

### V-5 — Prioritisation that reads the value and risk the product already holds · REQ-18 · M · **high** · depends on V-4

**Requirement.** *Restated: the ranking exists (§2.9); this extends it, and does not build it.* Show, next to the typed `value` score, the case's expected benefit and its confidence signal (has a basis, reconfirmed at the current gate, not stale); show the project's RAID exposure using the existing `Engine.exposure` bands; add a second constraint line for **people capacity** beside the money envelope, using `Engine.capacity`; make the weighting an explicit, displayed, editable and audited policy rather than a fixed expression in `Engine.priority`.

**User-visible behaviour.** The prioritisation screen shows why each item sits where it does, and where both the money and the people run out. Changing the weighting is a governed act with a trail, so a room can argue about the policy rather than about the arithmetic.

**Why a real programme needs it.** Choosing what not to do is where a portfolio creates the most value, and today that choice is made on four hand-typed numbers with a hidden fixed weighting, disconnected from the case, the benefits and the risks in the same database (§3.6).

**Acceptance criterion.** The ranked list shows, per row: score with each input, hand rank if set, budget, expected benefit from the case (or "no case"), a confidence flag derived from basis/reconfirmation/staleness, RAID exposure band, and FTE demand; two cut lines are drawn, one where the money envelope is exhausted and one where committed capacity is; changing a weight re-ranks the list, is refused below group level, and is audited with before/after; an unscored item still sorts to the bottom and is never treated as worst.

**Evidence.** [Source: `shared/engine.js:496-549` (`priority`, `prioritise`), `382-400` (`capacity`), `355-368` (`exposure`); `web/src/views/index.js:2713`]

---

### V-6 — Adoption per rollout wave, linked to the benefits it should move · REQ-19 · M · **medium** · depends on V-1

**Requirement.** `rollout_wave` gains a measured adoption figure with its source, unit and date, a threshold, and a link from a wave to the benefits it is expected to move; adoption below a wave's own threshold after go-live raises an exception like a tolerance breach.

**User-visible behaviour.** A benefit's page shows the adoption trend of the waves feeding it. A wave that went live and is not being used says so, months before the benefit's realisation date.

**Why a real programme needs it.** `rollout_wave` today holds sequence, site, planned and actual dates and a status, and nothing about use [Source: `server/migrations/010_plant_and_sites.sql:64-77`]. A delivered change nobody adopts realises nothing, and adoption is the earliest available signal that a forecast benefit is in trouble.

**Acceptance criterion.** A wave carries an adoption measure, unit, source and date, and a threshold; a wave in `Live` whose latest adoption is below its threshold appears in the exception list and on the next agenda; each benefit page lists its feeding waves with their adoption trend; a wave with no adoption measure reads as *not measured*, never as zero adoption.

---

### V-7 — Lessons become a checklist at the gate · REQ-20 · S · **medium** · depends on V-13

**Requirement.** At a gate, the reviewer is shown the adopted lessons tagged to that gate from closed projects of the same programme or site, and records considered / not-applicable per lesson; the gate record keeps that list.

**User-visible behaviour.** The lesson register stops being an archive and becomes a two-minute checklist at the only moment it can change an outcome.

**Why a real programme needs it.** `lesson` already carries `gate_n`, an adoption act by the group level, and an index built for exactly this query (`lesson_relevance_idx ON lesson(status, programme_id, site_id)`) — the schema was designed for this use and the use was never built [Source: `server/migrations/024_lessons.sql`].

**Acceptance criterion.** Opening the gate review on a project shows every `Adopted` lesson tagged to that gate number in the same programme or site, excluding the project's own; each is recorded considered or not-applicable with an optional note; the gate record and the audit keep the list and the reviewer; with no lessons tagged, the gate behaves exactly as before.

---

### V-8 — One ladder per project · REQ-21 · S · **high** · no dependency (defect)

**Requirement.** When a programme declares a `gate_model`, project scaffolding creates that ladder only, and does not also scaffold the four default gates.

**User-visible behaviour.** "Which gate is this project at" has one answer.

**Why a real programme needs it.** [Measured] After 036 our sixteen projects carry both Gate A–F and Gate 1–4: the load produced **10 milestones where 6 were intended** [Measured: docs/PMO_MERIDIAN_ASSESSMENT.md §7; docs/PMO.md §5]. Two competing ladders make the one question a portfolio must answer unanswerable, and evidence, criteria and phase advancement bind to whichever one the code happened to read.

**Acceptance criterion.** A project created under a programme with a declared ladder carries exactly that programme's gates and no others; an existing book migrates without duplicating or destroying dated milestones and their evidence; a field repository's second load still makes no creating writes.

**Evidence.** [Source: `server/migrations/036_gate_ladder.sql`; `scaffoldProject` in `server/src/routes/portfolio.js`]

---

### V-9 — Governance quality signals · REQ-22 · S · **medium** · no dependency

**Requirement.** Five metrics computed from timestamps that already exist, per programme, with their trend, on the portfolio page and on `/api/v1`: decision latency (raised to decided), action ageing, gate cycle time, RAID review compliance, open-exception age.

**User-visible behaviour.** The PMO can see its own throughput, and a programme that is quietly stalling shows it before a milestone slips.

**Why a real programme needs it.** These are the leading indicators of a stalling programme, and none of them exists today — there is no latency, cycle-time or ageing computation anywhere in `shared/`, `server/src` or `web/src` [Source: searched at e352bc8; the only match for "latency" is a seed-data work-item title]. No new data entry is required to produce any of them.

**Acceptance criterion.** Each metric is computed from existing rows with no new field, shown per programme with a period-on-period trend, available on `/api/v1`, and defined in one place in the documentation with the timestamps it uses; a programme with too few closed items shows *insufficient data* rather than a misleading number.

---

### V-10 — Evidence provenance for gate criteria · REQ-23 · M · **medium** · no dependency

**Requirement.** *Restated: the document model is stronger than we first credited (§2.10); this asks for one more citation type, not a rebuild.* A `gate_criterion` may cite a typed **external artefact reference** — kind, locator (repository, workflow run, artefact), a content digest supplied by the citing system, and the date — in addition to, or instead of, `document_id`. Changing a cited reference after the gate creates a new version and never edits the old one.

**User-visible behaviour.** "Which test proves this criterion" is answerable with a commit and a digest, not only with a link to a file that may have been rewritten.

**Why a real programme needs it.** `gate_criterion` can cite only `document_id` [Source: `server/migrations/037_gate_criteria.sql`], and a document's locked hash is the SHA-256 **of the URI string**, not of the artefact: `const uriHash = (uri) => crypto.createHash("sha256").update(String(uri)).digest("hex")` [Source: `server/src/routes/portfolio.js:2330,2464`]. That is a real and well-designed control against a swapped link, and it is not a control against changed content at a stable address. A regulated programme's gates read CI-evidenced commits.

**Acceptance criterion.** A criterion carries a typed external reference with a locator and a digest supplied by the citing system; the gate record shows what was cited, by whom and when; replacing it after the gate creates a new version with `supersedes` lineage and leaves the old one readable; the independence rule of 037 (the reviewer is not the owner of what is cited) still holds; Meridian never fetches or re-computes the digest and does not claim to have verified it — it records what was cited [Open: whether Meridian should probe such references at all, by analogy with 020].

---

### V-11 — A value dashboard, snapshotted per period · REQ-24 · M · **medium** · depends on V-4

**Requirement.** *Restated: `report_snapshot` already exists and already counts benefits (§2.8); this extends the snapshot and adds the page.* One printable page per portfolio — spend against case, benefits by status, overdue reviews, top risks by exposure, gates due, exceptions open — generated with no manual entry, and the period close extends `report_snapshot` with the case figures, attainment and overdue-review count so a claim made in March can be re-read in December.

**User-visible behaviour.** A sponsor without the tool open can be handed one page that answers "is it worth it", and a later reader can reproduce exactly what that page said at the time.

**Why a real programme needs it.** The current portfolio view answers "on time and on budget" with one value tile beside it (§2.3). The append-only period machinery is already there and already carries three benefit counts; adding the case figures makes the historical record complete rather than starting a second one.

**Acceptance criterion.** The page is generated from existing objects with no manual entry and prints on one sheet per programme; closing a period writes the extended snapshot; reopening a closed period is refused as it is today; the page rendered from a past snapshot equals what the page showed at that close, field for field.

---

### V-12 — Publish the field-repository loop as a reusable pattern · REQ-25 · S · **high** · no dependency

**Requirement.** Publish `meridian-request-register/1` as an actual JSON Schema with the register file's location configurable, make the id vocabulary the field repository declares (rather than a regex of one repository's conventions), and document the round: field repository writes a register → `scripts/…-review.mjs` reads every branch → the Product Owner triages → statuses and deliveries flow back into the register.

**User-visible behaviour.** A second field repository can file its findings and see them tracked, without either side writing code for the other.

**Why a real programme needs it.** The strongest thing this product now has is the demonstrated ability to turn a real programme's findings into a release in a day, and today that capability is one script whose register path (`docs/requests/rt365.json`) is hard-coded and whose id pattern is RT365's ledger vocabulary — `M-\d{2}|I-\d{1,2}|O-\d{2,3}|H-\d{2}|D-\d{3}|ADR-\d{3}|PR-\d{2}` — while `--repo` alone is parameterised [Source: `scripts/rt365-review.mjs:2-24,45`]. There is no published schema for `meridian-request-register/1` anywhere in the repository; the string appears only in the register file itself [Source: searched at e352bc8]. That makes a capability look like an anecdote.

**Acceptance criterion.** A JSON Schema for `meridian-request-register/1` exists in the repository, the register validates against it in CI, the review script takes the register path and the id vocabulary as configuration, a second (fixture) field repository is reviewed end to end in a test, and the round is documented in English in one page.

---

### V-13 — **New.** The value and learning objects must follow the configurable ladder · REQ-26 · S · **highest** · blocks V-3 and V-7

**Requirement.** Replace the 1–4 gate ceilings in `business_case.reconfirmed_gate` and `lesson.gate_n` (and the reconfirm route's validation) with the range the programme's ladder actually declares, aligned with `gate_criterion`'s 1–12.

**User-visible behaviour.** On a six-gate ladder, a case can be reconfirmed at gates 5 and 6 and a lesson can be tagged to them.

**Why a real programme needs it.** 036 freed the ladder; the value objects did not travel with it. `business_case.reconfirmed_gate CHECK (BETWEEN 1 AND 4)`, `if (!(g >= 1 && g <= 4)) bad("Reconfirmation happens at a gate — 1 to 4")`, `lesson.gate_n CHECK (BETWEEN 1 AND 4)`, while `gate_criterion.gate CHECK (BETWEEN 1 AND 12)` [Source: `server/migrations/028_business_case.sql`, `024_lessons.sql`, `037_gate_criteria.sql`; `server/src/routes/portfolio.js` reconfirm route]. Our own six-gate programme is the first real portfolio in the tool and hits this at Gate E. Silently capping the two highest-value controls at gate 4 is worse than not having the ladder configurable at all, because the failure is invisible until someone tries.

**Acceptance criterion.** On a programme with a six-gate ladder, a case is reconfirmed at gate 6 and a lesson is tagged to gate 5; a gate number outside the programme's declared ladder is refused with a named reason; existing four-gate books are unaffected; the migration does not alter any stored value.

---

### V-14 — **New.** Not measured is not within tolerance · REQ-27 · S · **high** · pairs with V-2

**Requirement.** Distinguish, in the benefit tolerance and in the sweep, three states rather than two: *within margin*, *breached*, and *nothing measured*. A benefit past its `realise_on` with no `actual` raises its own exception kind, independently of whether a benefit tolerance has been set on the project.

**User-visible behaviour.** A project that never measures its benefits stops reading as a project inside its margin.

**Why a real programme needs it.** `Engine.tolerance` sets `out.benefit` only when at least one benefit on the project has an attainment, and attainment is null unless baseline, target and actual are all present; `breaches()` therefore returns nothing, and `sweepExceptions` returns early for any project without an active tolerance [Source: `shared/engine.js:611-627,646-651`; `server/src/exceptions.js`]. The result is precisely inverted for value: measuring and missing is visible; never measuring is not (§3.4). The product's own principle — "an unmeasured benefit is not a zero" — is correct and must extend to "and it is not compliance either".

**Acceptance criterion.** A project whose benefits are all unmeasured and whose realisation dates have passed raises an exception naming how many benefits are unmeasured and since when; the exception carries its two numbers like every other and closes only by an answer; the benefit tolerance display distinguishes *no margin set*, *nothing measured* and *within margin* as three different statements; a project with no benefits at all is reported by the existing `uncased` count and does not raise a duplicate exception.

---

### V-15 — **New.** Carry the promise across the conversion · REQ-28 · S · **medium** · pairs with V-5

**Requirement.** When an approved demand becomes a project, seed the business case from the demand: `benefit_note` into the case summary or basis, `est_cost` into `expected_cost`, and record the demand id the case came from; where a programme requires it, refuse to convert without at least a draft case.

**User-visible behaviour.** The sponsor's own words about what the thing is *for* survive into the project that spends the money, and the case can be read back to the request that justified it.

**Why a real programme needs it.** `POST /demand/:id/convert` copies the four scores, `est_cost → budget` and `detail → description`, and drops `benefit_note` — the field whose schema comment is "what it is FOR, in the sponsor's words" — and creates no `business_case` [Source: `server/src/routes/portfolio.js:1542-1582`; `server/migrations/011_demand_and_priority.sql:27`]. Migration 028's own header describes the intended chain demand → case → benefit → review; the conversion route is where that chain breaks, at the exact moment the money is committed and the justification is freshest.

**Acceptance criterion.** Converting an approved demand creates a business case carrying its `benefit_note` and `est_cost` and citing the demand id; the case appears on the new project immediately; conversion is refused without a case where the programme requires one, with a named reason; converting a demand with no `benefit_note` still succeeds and the case is visibly a draft, never a fabricated justification.

---

### What we are deliberately **not** asking for

- **An OKR object.** The business case already carries the objective and its two numbers, and `benefit` already carries measure, unit, baseline, target and actual. A second vocabulary for the same facts splits the truth and doubles the data entry; whichever one is easier to fill in becomes the one nobody trusts. The gap is enforcement, not vocabulary.
- **A money-normalised portfolio value (a single "portfolio NPV" or a currency conversion of every benefit).** Migration 008 is right that value is not always money-shaped, and a normalisation factor from tonnes or availability points to currency is a number somebody invents and everybody then quotes. We would rather read four benefits in four units than one wrong total. V-4's acceptance criterion forbids it explicitly.
- **Any AI or model-driven feature** — no risk prediction, no benefit forecasting, no meeting summarisation, no assistant. The value of this product is that its record is trustworthy, and every requirement above is arithmetic on data a named human entered or a named integration wrote. Nothing in this list needs a model, and introducing one would put a probabilistic step inside a governance record whose whole worth is that it is not probabilistic. (This is also our own product's standing rule, and we hold ourselves to it.)
- **Work tracking, requirements, tests or a traceability matrix inside Meridian.** We asked for none of it. Our engineering truth stays in a repository evidenced by CI (ADR-017), and V-10 asks only that a gate criterion be able to *cite* it. A portfolio tool that tries to become the delivery system competes with the tools the teams already use and loses.
- **A second gate ladder concept, a portfolio-of-portfolios level, or per-benefit workflow configuration.** Each is a plausible enterprise ask and each would add configuration surface to a product whose current strength is that a PMO can hold the whole model in their head.

---

## 5. Sequencing — the largest value change per unit of work

**First (days, and everything else stands on it): V-13, V-1, V-8.** V-13 is one migration and one validation, and until it is done, V-3 and V-7 cannot be built for any programme that used the feature 5.10.0 just shipped. V-1 makes value facts as syncable as delivery facts, which is what stops the value half going stale and what makes every later report worth reading. V-8 is a measured defect in the current release and gets cheaper to fix the fewer books carry the duplicate ladders. All three are S; together they are the plumbing and the two defects.

**Second (the verbs): V-3, then V-2 with V-14.** V-3 turns the reconfirmation field into a control at the moment a room is already assembled and already deciding — the cheapest possible place to add the highest-value question. V-2 and V-14 together close the other end: the review that must happen after closure, and the arithmetic that stops "never measured" reading as "within margin". V-3 is S; V-2 is M; V-14 is S.

**Third (the confrontation, and making the loop reusable): V-4, V-11, V-12.** With the data fresh (V-1), the gates enforcing (V-3) and the reviews chased (V-2), the forecast-versus-realised report finally has something true to show, and the period snapshot makes it re-readable a year later. V-12 in the same round because it is S and because it is what turns one good day into a repeatable capability for the next field repository.

**Then, as capacity allows:** V-5 and V-15 (prioritisation reading the value the product holds), V-9 (five metrics, no new data entry — the best small win on the list if a spare week appears earlier), V-7, V-6, V-10.

**If you could do only one thing: V-3 — the gate cannot pass without a reconfirmed business case — with the one-line V-13 fix it needs.** It is days of work; every field it uses already exists and is already displayed; it requires no new data entry and no new object; and it is the only item on this list that changes what a room *decides* rather than what a page *shows*. Everything else on this list makes value visible. V-3 makes it consequential. Our confidence is **high** for the technical claim (the code path is `Engine.canAdvance`, which reads two things and could read a third) and **medium** for the value claim, because we have not yet run a gate in Meridian under such a rule — that is exactly what our Gate B and Gate C would evidence, and we would report the result back [Open].

---

## 6. The register file

`docs/REPORTS/meridian_requests_v2.json` — `$schema: "meridian-request-register/1"`, matching the shape of `docs/requests/rt365.json` field for field: `source` (repository, branch, commit, documents, reviewedAt), `productOwner`, `channel`, `registerVersion`, and `requests[]` with `id`, `origin[]`, `title`, `status`, `version`, `decidedOn`, `delivered[]`, `measure`, `remaining`, `issue`, `accepted`, `released`, `history[]`.

Three notes for the ingesting Product Owner:

1. **REQ-14…REQ-28**, one per requirement V-1…V-15, all `status: "proposed"`. We used `"proposed"` rather than `"open"` because we are not in a position to open anything in your register — your existing values (`done`, `partial`, `open`) are yours to assign, and the first thing you may want to do is re-status these to `open` or reject them. Nothing in this file records a decision on your behalf.
2. **`measure` carries the acceptance criterion**, following the way REQ-05 and REQ-10 use the field: for a delivered request it names the test that measures it, and for a proposed one it states the criterion that would. When one of these is built, `measure` becomes the test path.
3. **`priority` and `effort` are two fields your register does not yet have.** They are ours — our recommendation and our estimate, not a commitment on your side — and are additive; a reader that ignores them loses nothing. If you would rather they lived elsewhere, dropping the two keys leaves the file valid against your existing shape.

`source.commit` names the commit on branch `docs/meridian-report-value` of this repository that carries this report. `issue` is `null` on every request: filing them as issues is a human act on our owner's account, still open (H-31).

---

## 7. Concerns for the Product Owner

These are ours, held as our own product owner would hold them about our own product — offered because a report that only asks for features is worth less than one that says what worries it.

1. **The one-day loop is your strongest asset and your largest single point of failure.** Twelve findings to a release in a day is the best evidence we have ever had that a tool can be driven by its users, and it was achieved by one maintainer with no vendor, no on-call and no second person. Every requirement in §4 is worth less than the answer to "what happens to this register when you are unavailable for a month". We would rather see V-12 done and a second maintainer named than see all fifteen delivered fast.

2. **Velocity is now the product's main correctness risk.** Two of the three defects in this report (V-8, V-13) were created by the feature that closed our own M-04 in the same release: the ladder became configurable, and the projects grew two ladders while the case and the lesson stayed capped at gate 4. Nothing was careless — but a change that frees a dimension has to be followed through every table that assumed it was fixed, and one day is not long enough to find them all. A "what else assumed this was constant" step in the release checklist would have caught both.

3. **The value model is the best part of the product and the least defended part of the API.** Delivery collections now have external ids, idempotency and scoped keys; the business case and the benefits have none. Whatever is easiest to write becomes what is written, and a portfolio whose delivery data is machine-fresh and whose value data is hand-typed drifts toward being a cost report with a value tab — which is precisely what migration 008 was written to prevent.

4. **We are your first real portfolio, and that is a thin evidence base for both of us.** Sixteen projects, 134 RAID items and one weekly is a load test, not a year of use [Measured: docs/PMO.md §6]. Our numbers are honest and they are one programme, in one shape, run by agents under a human owner. Please weigh them as one field report and not as a market. We would treat a second, differently-shaped field repository as more valuable than anything on our own list — which is the other reason V-12 is ranked as it is.

5. **Beware of us as a requirements source.** We are a regulated trading programme; our gate ladder is six long, our evidence is CI-shaped and our tolerance for an unenforced control is low. Some of what we ask for is universal (V-1, V-2, V-3, V-13). Some is our shape talking (V-10 in particular, and the strictness in V-3). If a requirement here only makes sense for a programme like ours, we would rather you say so and decline it than carry it as debt in your register — a declined request with a reason is a better artefact than an open one nobody intends to build.

6. **Do not let this list crowd out your own committees' backlog.** Your `docs/26` register still carries PM-07, PM-10 and PM-12, and REQ-05 and REQ-10 are `partial` by your own record. Fifteen more requests from an enthusiastic field repository is a way to lose your own roadmap. We would trade any five of the medium-priority items above for the closure of REQ-05, because progress with provenance is what stops every number in the portfolio being typed by hand.

7. **On our side, and it affects you: nothing in this repository formally owns the Meridian relationship.** `docs/PMO.md`, `docs/PMO_MERIDIAN_ASSESSMENT.md` and `docs/IMPROVEMENT_REGISTER.md` have no owning role in our agent roster, which is why this report is in `docs/REPORTS/` rather than where it was asked for, and why V-13…V-15 could not be added to our own `IMPROVEMENT_REGISTER.md` §D2 in this session. We are raising that on our side. Until it is fixed, treat this document — not our improvement register — as the current statement of what we are asking of Meridian.

---

**Provenance and confidence.** Everything in §2, §3 and §4 marked [Source] was read in Meridian's own code at commit e352bc8 in a working copy that was not modified. Everything marked [Measured] was run by this programme and is recorded in `docs/PMO_MERIDIAN_ASSESSMENT.md` §7, `docs/PMO.md` §4 and §6. Confidence: **high** that the gaps in §3 exist as described (each is a named file and, where it matters, a named line); **medium** on the effort estimates, which are ours and made without knowledge of your codebase's internal conventions; **medium** on the priorities, which are one programme's judgement; **[Open]** on whether V-3 changes decisions in practice, which only running gates under the rule will show, and which we would report back. Profit is an objective and never a promise in our product; by the same discipline, no benefit figure, price or return appears anywhere in this report.
