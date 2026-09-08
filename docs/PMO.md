# PMO — managing the RoboTrader lifecycle in Meridian IT-PMO

| Owner | Reviewer (different line) | Approving body | First gate | Status |
|---|---|---|---|---|
| Product Owner (Program Orchestrator operates) | CAB chair | Product Owner (D-049; ADR-017) | A | v1.0 — 2026-09-08, first load evidenced |

Meridian IT-PMO (https://github.com/mliad313sn/Meridian, Apache-2.0, self-hosted) is the **portfolio and rhythm system** of this delivery: the programme, one project per epic, the gate ladder as milestones, the RAID register, and the Product Owner's weekly whose agenda Meridian generates from the portfolio and whose decisions and actions land back on the projects. The repository ledgers remain the **source of truth** for everything a gate reads, because they are versioned with the code and evidenced by CI; Meridian is loaded from them, never the other way round (ADR-017). Meridian's own real-case efficiency and the improvements it needs are assessed in docs/PMO_MERIDIAN_ASSESSMENT.md.

## 1. What lives where
| Lifecycle element | Repository (truth) | Meridian (portfolio view and rhythm) |
|---|---|---|
| Programme, epics E01–E15 | docs/BACKLOG.md, goals/build/ | programme `RBT`, site `RTX`, projects `E01…E15` (PM = accountable lead; finish = first gate horizon), `RBT-GOV` governance project |
| Gates A–F | goals/gate_*.md, docs/GATE_REPORTS/, docs/RELEASE_CHECKLIST.md | milestones `Gate A…F` on `RBT-GOV` with the exit evidence as acceptance criteria; Gate A ticked after D-048 |
| RAID | docs/RAID_LOG.md (O-/R- rows) | RAID items `[O-nn] …` / `[R-nn] …` on `RBT-GOV` (Risk / Issue / Assumption / Dependency) |
| Decisions | docs/DECISION_LOG.md (D-0nn) | decisions of the weekly `RoboTrader weekly — Product Owner` |
| Human acts | docs/MISSING_ACTIONS.md (H-nn) | actions of the weekly, owned by the Product Owner, on `RBT-GOV` |
| Evidence, RTM, quartets | docs/AUDIT_EVIDENCE_INDEX.md, docs/REQUIREMENTS_TRACEABILITY.md, docs/TEST_CASES/ | not modelled (Meridian has no traceability or test-evidence concept) — link from milestone criteria |
| Who changed what | git history | Meridian audit trail (append-only, before/after images) |

## 2. Running it
```bash
# Meridian (from its own checkout; Node 22+)
npm install
mkdir -p server/.data && cp .env.example .env          # persistent PGlite; without PGLITE_DIR the book is in-memory and lost at exit
PGLITE_DIR=./server/.data/pgdata npm run seed             # demo book (or `npm run reset-book` for an empty one — then change the admin password)
npm run build                                             # the server serves the built client; without it "/" answers 404
PGLITE_DIR=./server/.data/pgdata npm run dev              # http://localhost:4173

# RoboTrader → Meridian (from this repository)
MERIDIAN_URL=http://localhost:4173 MERIDIAN_EMAIL=<account> MERIDIAN_PASSWORD=<secret> make pmo-sync
# demo instance only: MERIDIAN_ALLOW_DEMO=1 make pmo-sync
```
`make pmo-sync` is idempotent: it creates what is missing, updates milestone criteria, never deletes. Run it after every ledger change (the weekly at least). Use a group-level account, never the demonstration credentials, on anything but a throwaway instance.

## 3. The weekly loop (Product Owner, delegate agent operates)
1. `make all` green on the branch; ledgers updated by the session packets.
2. `make pmo-sync` — new RAID rows, decisions and open human acts appear on the weekly's agenda; Meridian adds the items its rules generate (gates due, RAID reviews, actions overdue, referrals).
3. Open the weekly in Meridian (`Meetings → RoboTrader weekly — Product Owner`), run it from the generated agenda, record the decisions and actions there **as well** (they are the minutes), close it — Meridian schedules the next one.
4. Anything decided in the room that is not yet in the ledgers goes into docs/DECISION_LOG.md / RAID_LOG.md / MISSING_ACTIONS.md in the same session, then `make pmo-sync` again.
5. Gates: convene with the `gate-x` agent on a commit; on a pass, tick the `Gate X` milestone in Meridian with the decider named (acceptance criteria = exit evidence). Meridian's own four-gate phase machine is not used for authorisation; our six gates are.

## 4. First load, 2026-09-08 (evidence)
Instance: Meridian 5.9.0 (commit 77c4b49), PGlite, `npm test` 449/449 pass. Load: `docs/PMO/meridian_sync_2026-09-08.json` — 16 projects, milestones Gate A–F (Gate A done), 86 RAID items, 14 decisions and 21 open actions on the weekly; second run 0 creating writes. Archive export: 1,529 rows across 47 tables. Screens: `docs/PMO/meridian_portfolio.png`, `meridian_project.png`, `meridian_meetings.png`.

## 5. Limits to know
- Meridian's public API (`/api/v1`) is read-only; the sync uses the session routes the web client uses (undocumented, may change between versions — pin the Meridian commit).
- Dates in Meridian are planning placeholders until O-17; budgets are 0 until the cost model (O-13).
- Meridian scaffolds its own four gates (Mandate, Design authority, Readiness, Benefits) on every project; they coexist with `Gate A…F` on `RBT-GOV` and are ignored for authorisation.
- Operating Meridian for real needs what its SECURITY.md lists: a tested backup, a second instance, a written security policy, changed demo credentials, PostgreSQL rather than PGlite (assessment §3).
