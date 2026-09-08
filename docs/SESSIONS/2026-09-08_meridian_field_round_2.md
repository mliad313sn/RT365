# Session packet — Meridian IT-PMO field round 2

**Date:** 2026-09-08 · **Branch:** `docs/meridian-round-2` · **Evidence:** `docs/REPORTS/PMO/round2/`

## 1. Roles

| Role | Who | Act |
|---|---|---|
| Author | Program Orchestrator (this session) | ran the round, wrote `docs/REPORTS/PMO/round2/EVIDENCE.md` |
| Reviewer (different line) | **not assigned** | required before this leaves the programme |
| Approver | Product Owner (D-039) | filing upstream is H-31, a human act, not performed |
| Subject | Meridian IT-PMO, `mliad313sn/Meridian` | not modified, not written to, nothing filed |

Author = reviewer = approver here. Nothing in this packet certifies evidence, convenes a gate or
records an approval.

## 2. Purpose

Re-clone the current Meridian, stand it up on an **empty** book, drive the whole RoboTrader
programme into it through its real API, use it for one Product Owner cycle, and hand back measured
evidence. Round 1 was run on the demonstration book with a loader that had adopted none of the
twelve improvements; both weaknesses were to be removed [Source: docs/PMO_MERIDIAN_ASSESSMENT.md §7,
docs/REPORTS/PMO_MERIDIAN_REPORT_EVIDENCE.md].

**Removed:** the book is empty (`npm run reset-book`; portfolio value $0.00M, not $51.3M)
[Measured]; the ladder is declared on the programme, so gate criteria bind to Gates A–F [Measured];
the register carries a real P×I distribution [Measured]; the weekly was closed and frozen
[Measured]; business cases, benefits, stakeholders, a communication plan, lessons, a tolerance, a
change request, work items and a rollout wave went in [Measured].

**Not removed:** the loader still authenticates as a human administrator, because structure is not
in the v1 write API [Measured: 621 of 626 audit events name one account].

## 3. Decisions taken in this session

No programme decision was taken. Three method decisions were made and are recorded with their
alternatives so a reviewer can overturn them.

### S-1 · Evidence path
- **Question.** The commissioned path `docs/PMO/round2/` is refused to this role by
  `scripts/agent_guard.py`.
- **A (taken).** Write to `docs/REPORTS/PMO/round2/`, inside this role's scope, and record the
  refusal verbatim. *Pro:* the guard holds; the evidence exists. *Con:* the evidence is not where it
  was asked for; a later act must move it. *Reversible:* fully, by a role that owns `docs/PMO/`.
- **B (rejected).** Write the path through Bash, which the guard does not police.
  *Rejected:* it is the exact prohibition in the brief, and a control that is routed around is not a
  control.
- **Confidence:** high. **Evidence:** `GUARD_PROBE.md`.

### S-2 · Probability and impact on 165 RAID rows
- **Question.** The brief asks for real probabilities and impacts. `docs/RAID_LOG.md` states none.
- **A (taken).** Derive both from stated fields (`Type`, `Status`, `Needed by`) by a published rule
  **R2-PI-1**, and write that sentence into every item's own detail in Meridian. *Pro:* the tool's
  escalation, exposure and agenda arithmetic becomes meaningful (113 steering / 54 PMO); the
  derivation is visible to any reader. *Con:* a derived rating can still be mistaken for a
  measurement by someone reading only the table.
- **B (rejected).** Keep the constant 3×3. *Rejected:* it was round 1's own worst finding and it
  carries no information.
- **C (rejected).** Assign ratings by judgement, item by item. *Rejected:* that invents numbers,
  which the programme's rules forbid, and it is not reproducible.
- **Confidence:** medium — the rule is defensible, the choice of it is not evidenced.
  **Evidence:** `drive.py::derive_pi`, `load_3_hand_drive.json`.

### S-3 · Which instance to drive
- **Question.** The default branch is 5.9.0 with none of the twelve improvements; 5.10.0 exists only
  on an unmerged branch.
- **A (taken).** Measure the first hour on the **default branch** (what an adopter gets) and drive
  the programme into the **branch head** (where the features exist), labelling both. *Pro:* answers
  "what does the product do today" and "what did our findings produce"; the merge state becomes a
  finding instead of an assumption. *Con:* two instances, two test runs, more to keep straight.
- **B (rejected).** Drive into the default branch only. *Rejected:* no write API, no ladder, no
  criteria, no decision record — most of the brief would be unexecutable and the report would say
  nothing about the twelve.
- **Confidence:** high. **Evidence:** §1 of EVIDENCE.md.

## 4. Proposed RTM rows

Not written to `docs/REQUIREMENTS_TRACEABILITY.md` — this session was instructed not to edit it.
Proposed for the owning act.

| Requirement | Architecture | Owner | Control | Test | Evidence | Gate |
|---|---|---|---|---|---|---|
| The portfolio record mirrors the ledgers one way; no gate reads Meridian | ADR-017 | Program Orchestrator | one-way sync; ledgers are the source | TC-PMO-002 (loader declares the ladder) | `load_1_meridian_sync_run1.json` (307 writes), `load_2…run2.json` (1 write) | B |
| A second identical load creates nothing | `scripts/meridian_sync.py` idempotency | Program Orchestrator | title/id keying, `row_version` | TC-PMO-002 | `load_2_meridian_sync_run2.json` | B |
| Gate exit evidence is stated in advance and found met by a reviewer who does not own it | Meridian `gate_criterion` (037) — **advisory mirror only** | Product Owner | author ≠ reviewer ≠ approver | `probe_2.json` Q1 (abuse: no reviewer → 400; unknown reviewer → 400) | `probe_2.json`, `02_project_governance.png` | B |
| No portfolio health colour is quoted outside the room without a measured input | — | Product Owner | manual rule until D-6 closes upstream | none — this is a rule, not a control | `01_portfolio.png`, `EVIDENCE.md` §8 D-6 | B |
| The programme record is reversible without the vendor | `GET /api/admin/archive`, `npm run backup`/`restore-drill`, Apache-2.0 | Program Orchestrator | export + a restore proven by re-count | archive 51 tables / 2,115 rows / 145 ms; restore drill 1.2 s, every counted table matched | `backup_and_restore_drill.txt`, `/api/health` `backup.ok true` | C |

## 5. Threat-model delta

Nothing in RoboTrader's own trust boundaries changed: Meridian holds no credential, no limit, no
mode and no broker route, and no gate, control or test reads it. Two observations that belong to the
security line rather than to me:

| # | Observation | Evidence |
|---|---|---|
| TM-r2-a | The loader authenticates as a **human administrator with `user.manage`**, because sites, programmes and people are not in the v1 write API. Its credential is in the loader's environment. If that credential leaks, an attacker can rewrite the portfolio record and, through the documented break-glass exemption, sign every step of a change request alone. | `probe_2.json` Q2 (13 × 404), `EVIDENCE.md` §6.4, §8 D-5 |
| TM-r2-b | The break-glass path is **labelled, not prevented**: every self-signed step wrote `BREAK-GLASS: administrator signing a request they raised` into the append-only trail. Detection exists; prevention does not. | audit trail, four rows, `06_change_control.png` |

Neither is a change to the RoboTrader threat model. Both are conditions on ADR-017 that the Security
Architect should rule on before anything a gate reads moves into Meridian.

## 6. Control quartet — the one control this round actually exercised

`gate_criterion` found met by a named independent reviewer (Meridian's REQ-04, our I-4). Exercised
as an **advisory mirror**; the programme's real control is in the repository.

| Case | Attempt | Result |
|---|---|---|
| **Positive** | `PATCH /api/criteria/{id} {"met":true,"reviewedBy":"PE-42","version":n}` | **200**; stored `reviewedBy: PE-42`, `reviewedOn: 2026-09-08`; 7 criteria on Gate A |
| **Negative** | `met:true` with **no** `reviewedBy` | **400** `Finding a criterion met needs reviewedBy — the named person who checked it` |
| **Abuse** | `met:true` with `reviewedBy: "PER-NOBODY"` | **400**, same message — an invented reviewer is not a reviewer |
| **Recovery** | `PATCH {"met":false,"version":n}` | **200**; `met`, `reviewedBy` and `reviewedOn` cleared; a finding can be un-found |

[Measured: `probe_2.json`] Their code also refuses a reviewer who owns the cited document
(`portfolio.js:3426`); we could not exercise that case because our criteria cite no document —
**[Open]**, settled by attaching a document owned by the reviewer and re-running the positive case.

**Coverage this round: one control, four cases.** No RoboTrader critical control was tested here;
this session touched no product code.

## 7. Evidence list

All under `docs/REPORTS/PMO/round2/`:

`EVIDENCE.md` (the report) · `GUARD_PROBE.md` · `firsthour_A_main_5.9.0.txt` ·
`firsthour_B_branch_5.10.0.txt` · `test_counts.txt` · `npm_test_A_main_5.9.0_summary.txt` ·
`npm_test_B_branch_5.10.0_summary.txt` · `load_1_meridian_sync_run1.json` (307 writes) ·
`load_2_meridian_sync_run2.json` (1 write) · `load_3_hand_drive.json` (262 requests, timed) ·
`load_4_meridian_sync_run3_aborted.txt` · `probe_1.json`, `probe_2.json` (72 probes) ·
`drive.py`, `probes.py`, `probes2.py`, `shots.py` · `screens_text.txt` ·
`01_portfolio.png` … `10_pipeline.png`.

`backup_and_restore_drill.txt` — the archive export (51 tables, 2,115 rows, 145 ms) and a **proven
restore** (backup 4.6 MB with the server stopped, restored elsewhere in 1.2 s, every counted table
matching, reported by `/api/health`). Round 1's B-5/B-6 are settled on this version.

Not produced, and named so: no second programme, so the tile-rescoping question is unanswered; no
exception observed; no PostgreSQL instance, so H-28 is not discharged.

## 8. RAID entries this session opens

Proposed for `docs/RAID_LOG.md` by a role permitted to write it — this session was instructed not to
edit that ledger. The full table is `EVIDENCE.md` §12: **O-r2-1** Meridian's default branch is 5.9.0
and our dependency is an unmerged, untagged branch · **O-r2-2** our RAID ledger states no
probability, impact, residual or review date · **O-r2-3** D-058..D-066 carry five columns where the
header declares seven · **O-r2-4** 14 of 29 open acts name a committee and 28 of 29 carry no date ·
**O-r2-5** the loader creates six milestones whose names do not match the ladder it declares ·
**O-r2-6** the loader runs as an administrator, so break-glass applies to it · **O-r2-7** Meridian
reports this programme GREEN and 100 % on track.

## 9. Assumptions, confidence and provenance

| # | Assumption | Confidence | If wrong |
|---|---|---|---|
| A-1 | `origin/main` is Meridian's default branch and is what an adopter clones | **high** — `git symbolic-ref refs/remotes/origin/HEAD` → `refs/remotes/origin/main` [Measured] | the 5.9.0 headline changes entirely |
| A-2 | `cbe99ef` is the newest state of the RT365 feedback branch | **high** — `git ls-remote` [Measured] | measurements are against a stale branch |
| A-3 | R2-PI-1 is a defensible management rating and not a fabricated threshold | **medium** [Committee] | the register's ratings must be withdrawn, not corrected |
| A-4 | The 16 projects reading GREEN is a derivation, not stored data | **high** — `health: null` in the row; `engine.js:191-201` [Measured + Source] | D-6 is a data problem, not a rendering one |
| A-5 | No exception can be raised on a budget-less, baseline-poor programme inside one session | **medium** — sweep is hourly with no first pass [Source: `index.js:428`]; not observed | Q-2 resolves in Meridian's favour |
| A-6 | Nothing this session did reached Meridian's repository or its maintainer | **high** — clone read-only, no push, no issue [Measured] | H-31 would have been performed without authority |

**Provenance.** Meridian behaviour: the two working copies at `77c4b49` and `cbe99ef`. Meridian
intent: `docs/requests/rt365.json` (registerVersion 6, 31 requests), `CHANGELOG.md`, migration
headers. RoboTrader facts: `docs/BACKLOG.md`, `docs/RAID_LOG.md`, `docs/DECISION_LOG.md`,
`docs/MISSING_ACTIONS.md` as they stood at 16:00Z on 2026-09-08 — the ledgers moved during the
session and the drift is recorded in `EVIDENCE.md` §14.

## 10. What this session did not do

Approve anything. Certify any evidence as complete. Convene or recommend a gate. Edit
`docs/RAID_LOG.md`, `docs/DECISION_LOG.md`, `docs/REQUIREMENTS_TRACEABILITY.md` or
`docs/AUDIT_EVIDENCE_INDEX.md`. Modify Meridian's clone. File anything upstream. Push any branch.
Claim, imply or forecast a return.
