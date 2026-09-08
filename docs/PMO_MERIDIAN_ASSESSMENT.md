# Meridian IT-PMO — real-case efficiency to drive a project, and what to improve

| Owner | Reviewer (different line) | Approving body | First gate | Status |
|---|---|---|---|---|
| Product Owner (delegate agent, with the CAB chair and counsel-platform-reliability views) | Program Orchestrator | Product Owner (D-049) | A | v1.0 — 2026-09-08 |

Assessed by **using it**, not by reading it: Meridian 5.9.0 (commit 77c4b49) was cloned, tested, seeded, run, loaded with this programme through its API (16 projects, gates A–F, 86 RAID items, 14 decisions, 21 actions), exported and screenshotted (docs/PMO.md §4). Every statement below is [Verified] on that run, [Source: Meridian docs/NN] when it comes from Meridian's own committee record, or [Committee] when it is our judgement.

## 1. Verdict in one paragraph
Meridian is an unusually well-governed piece of software for a portfolio office: authority is data (group/site/admin/viewer decided server-side), every mutation is audited inside its own transaction, segregation of duties is enforced on change requests and gates, tolerances and exceptions exist, meetings are generated from the portfolio state and their decisions and actions land back on projects, and an ordered end-to-end journey test replays the life of a new organisation on every `npm test` (449 tests pass) [Verified; Source: Meridian docs/32]. **To drive a real project it is efficient as the governance record and meeting engine at programme and site level, and inefficient as the place where engineering delivery actually happens**: its process model is fixed (four gates, six phases), its public API is read-only, it has no traceability, evidence or work-tracking concepts, and its own market committee states that it has never run a real portfolio for a year and has no vendor, backup or second instance [Source: Meridian docs/24 §7, SECURITY.md]. For RoboTrader that division is exactly right: the ledgers and CI hold the engineering truth, Meridian holds the portfolio rhythm (ADR-017).

## 2. What it does well (measured)
| Capability | Evidence | Value for a real project |
|---|---|---|
| Authority as data; SoD on change control and gates | `shared/rbac.js`; PR-03 fix in 5.9.0; journey test §7 | The raiser can never approve their own change; a site cannot decide its own demand — real controls, not conventions |
| Append-only audit with before/after images | `server/src/audit.js`; `GET /api/audit` returned every load action with actor and detail | An auditor can replay how the portfolio got there; a change that is not audited does not commit |
| Generated meetings | `Meetings & decisions`: our weekly appeared with 16 projects, agenda built from actions overdue, projects off track, RAID reviews | Removes the deck-writing week; the minutes are the data |
| Stage gates with evidence, tolerances, business case reconfirmation, closure with named owners, lessons | migrations 024–033; docs/26 PM-01..PM-08 closed | PRINCE2/ISO 21502 discipline that most trackers lack |
| Idempotent, versioned writes | `row_version` + 409 on stale writes; PR-02 refuses a PATCH with no recognised field | Two writers never silently overwrite; our sync could be made idempotent on top of it |
| Reversibility | `GET /api/admin/archive` (1,529 rows / 47 tables on our book), `npm run restore` | Data gets out without the vendor |
| Self-contained | PGlite (PostgreSQL in WASM) with no server to install; Windows service installer | A PMO can run it on a laptop or a VM in an hour |

## 3. Where it is not yet fit for a real project (measured or stated by its own committees)
| # | Finding | Evidence | Consequence for a real project |
|---|---|---|---|
| M-01 | The one-minute quick start (`npm install && npm run seed && npm run dev`) gives an **in-memory** book: without `PGLITE_DIR` (only set in `.env.example`, which nothing loads) `openPglite(null)` creates `new PGlite()` in memory, so the seed is lost and the server starts empty | [Verified] `server/src/db.js:152`; login refused after seed until `PGLITE_DIR` was exported | First-hour failure for every newcomer; data loss if someone runs a real book that way |
| M-02 | With `PGLITE_DIR` set on a fresh clone, PGlite `mkdirSync` is not recursive: `ENOENT … server/.data/pgdata` until `server/.data` is created by hand | [Verified] seed and server both crash | Same as M-01 |
| M-03 | `npm run dev` before `npm run build` serves `Cannot GET /` (static mount is skipped when `web/dist` is absent); the README says the app is on :4173 | [Verified] `server/src/index.js:172-189` | Confusing first run; a `dev` script should build or proxy |
| M-04 | **Fixed process model**: four gates (Mandate, Design authority, Readiness, Benefits) and six phases are scaffolded on every project and cannot be replaced by the organisation's gate ladder; our six gates had to be added as plain milestones next to Meridian's four | [Verified] `shared/engine.js` GATES/PHASES; screenshot docs/PMO/meridian_project.png | Any organisation with its own gate model runs two models in parallel; evidence and phase advancement bind to the wrong one |
| M-05 | **Public API is read-only** (`/api/v1/portfolio`, `/api/v1/audit`); every write goes through undocumented session routes (144 of them) that the web client uses. No OpenAPI for them, no upsert, no external-id field on RAID/milestones/decisions, so an integrator encodes identity in titles (`[O-11] …`) | [Verified] docs/openapi.v1.json (4 paths); our sync | Bidirectional integration (Jira, ADO, CI, ledgers like ours) is not possible without scraping internal routes; INT-01/INT-13 open [Source: docs/27] |
| M-06 | No traceability, test-evidence or requirement concept; "evidence" is a document link per gate | [Verified] schema: `document`, no requirement/test tables | Regulated engineering programmes keep RTM and evidence elsewhere; Meridian cannot answer "which test proves this gate criterion" |
| M-07 | Work tracking is a light board (`work_item`) with no link to commits, PRs or CI; progress is "reported by the source system" | [Verified] screenshot: completion 0% "reported" | Progress must be typed in; EVM reads typed percentages |
| M-08 | Zero real usage, no vendor, no on-call; three blocking operational findings are the operator's (tested backup G-01, second instance, written security policy); PGlite is single-connection and a hard kill can leave the data directory unopenable | [Source: docs/24 §2 and §6, SECURITY.md, README "Do not hard-kill"] | A real portfolio needs PostgreSQL, backups proven by restore, and someone accountable on a Sunday |
| M-09 | Single maintainer, no releases or tags, `package.json` 5.9.0 while the published OpenAPI says 5.3.0; `verify.yml` is the only CI | [Verified] git log, docs/openapi.v1.json | Key-person risk; version drift between artefacts |
| M-10 | Demo credentials seeded by default and public; SoD admin exemption is deliberate break-glass | [Source: SECURITY.md] | Must be changed on day one; admins can self-approve |
| M-11 | Half the documentation (committee records, the "why") is French; UI bilingual | [Source: README] | Slower adoption outside francophone teams |
| M-12 | Capacity is FTE-only (no skills), no stakeholder register, no contract/supplier performance, no communication plan, finish-to-start dependencies only | [Source: docs/26 PM-05, PM-07, PM-10, PM-11, PM-12 open] | Adequate for an IT PMO; thin for industrial or vendor-heavy programmes |

## 4. Efficiency judgement for driving a project (real case)
| Question a sponsor asks | Answer with Meridian today |
|---|---|
| Can I see the portfolio, what is off track and what needs a decision this week, without a deck? | **Yes** — the executive view, the generated weekly and the decisions-owed panel do this well [Verified] |
| Can the governance trail survive an audit? | **Yes** for what is in Meridian (append-only audit, SoD, versioned rows); **no** for engineering evidence, which lives elsewhere |
| Can delivery teams work in it day to day? | **No** — it sits above the team tools by design; without INT-10/INT-11/INT-13 progress and cost are typed in |
| Can I plug it into what I already run (Jira, ADO, ERP, CI, a repo of ledgers like ours)? | **Read only**: BI tools via `reporting.*` views and `/api/v1`; writes need the session API or CSV import (projects, people, milestones) |
| Can I trust it in production? | Not yet as shipped: PGlite in memory by default, no backup story, single maintainer, no vendor [Source: docs/24]. With PostgreSQL, a restore-tested backup and a second instance, the software itself is sound (449 tests, nine static gates, journey test) |
| Time to first useful state | About one hour once the four setup traps above are known (M-01..M-03 cost this assessment ~40 minutes); loading 16 projects, 86 RAID rows and a weekly by API took under a minute |

**Net:** Meridian is efficient as the *governance and rhythm layer* of a real programme (it replaces the spreadsheet, the deck and the untraceable meeting) and, at this version, not sufficient as the *delivery system*; it needs a write API and integrations to stop being a place where truth is re-typed.

## 5. Improvement points, ordered by value for real projects (proposed upstream)
| # | Improvement | Why first | Effort (estimate) |
|---|---|---|---|
| I-1 | **Fix the first hour**: load `.env` (or default `PGLITE_DIR` to `server/.data/pgdata`), `mkdir -p` the data directory, make `npm run dev` build or proxy the client, and refuse to start a non-training instance in memory without an explicit `--ephemeral` flag | M-01..M-03 are the only defects a newcomer meets, and one of them loses data | S |
| I-2 | **Write API v1 with idempotency and external ids**: `PUT /api/v1/{projects,milestones,raid,decisions,actions}` keyed by `externalId`, `Idempotency-Key`, scoped integration keys (INT-02 exists), OpenAPI generated from the same routes | Turns every integration (ours included) from scraping into a contract; prerequisite for INT-10..INT-13 | M |
| I-3 | **Configurable gate ladder and phases per programme** (name, order, evidence required, authorising body), with Meridian's four gates as the default template | M-04: organisations already have a gate model; running two is the fastest way to lose one | M |
| I-4 | **Evidence and traceability objects**: a requirement/criterion table per gate, evidence rows with type, link, hash, owner, reviewer, date; a gate cannot pass with an unreviewed criterion | M-06; makes "see evidence 0/1" a real control instead of a document link | M |
| I-5 | **Progress and cost from source systems**: inbound events (INT-13) for work-item state, commit/PR/CI status and ERP actuals, stamped with provenance; EVM on measured, not typed, progress | M-07; the committees' own top integration lines | L |
| I-6 | **Operate-for-real kit**: `pg_dump` backup with restore drill (G-01/SaaS-03), second instance/failover note, PostgreSQL required for non-training instances, health with instance identity (SaaS-04), fleet runbook (SaaS-05) | M-08; the three blockers its SECURITY.md hands to the operator | M |
| I-7 | **Decisions as first-class records**: a decision register outside meetings (D-nnn with alternatives, dissent, linked change/gate/RAID), so a decision taken by an accountable owner between meetings is still in the trail | Our D-035..D-048 had to be recorded as meeting decisions of an artificial occurrence | S |
| I-8 | **RAID linked to gates and to change requests**, with review dates driving agenda items; residual P×I already exists (PM-06) | Closes the loop RAID → decision → gate condition, which is how we drive RoboTrader | S |
| I-9 | **Release discipline**: tags/releases per version, changelog check in CI, OpenAPI version = package version, signed installer (S-16) | M-09 | S |
| I-10 | **Stakeholders, skills, suppliers, communication plan** (PM-05, PM-12, PM-10, PM-11) | Docs/26 gaps; needed for industrial and vendor-heavy programmes | M–L |
| I-11 | **English translation of the committee record** (docs/16–32) | M-11; the "why" is the product's best asset and half the world cannot read it | S |
| I-12 | **Day-one security posture**: force the demo accounts off (or seed without them) when `NODE_ENV=production`, ship a security-policy template, document the admin break-glass exemption in the UI | M-10 | S |

Effort key: S = days, M = weeks, L = a release. Filed upstream on 2026-09-08 as issues #1–#12 of https://github.com/mliad313sn/Meridian (I-n = issue #n).

## 6. What we do meanwhile (RoboTrader)
Use Meridian as ADR-017 states: portfolio and rhythm system, loaded one way from the ledgers by `make pmo-sync`, on an instance run with PostgreSQL, a restore-tested backup and changed credentials before anything real (H-28). Revisit the split when I-2 and I-4 exist.
