# Session packet — Meridian field report, evidence half (Program Orchestrator)

| Field | Value |
|---|---|
| Role | Program Orchestrator (1st line) |
| Date | 2026-09-08 |
| Branch | `docs/meridian-report-pm`, from `8fe02a7` |
| Artefact written | `docs/REPORTS/PMO_MERIDIAN_REPORT_EVIDENCE.md` |
| Reviewer | *none* — this packet is unreviewed; author ≠ reviewer ≠ approver is not satisfied |
| Approves | nothing. No gate convened, no evidence certified, no risk accepted |

## 1. Purpose

Produce the delivery-management half of a field report to the Product Owner of Meridian IT-PMO, measured and quoted throughout, actionable from a clean clone. [Source: owner instruction 2026-09-08] The value half is the Product Owner's, in parallel.

## 2. Write-scope refusals to record

| Path wanted | Refused by | Consequence |
|---|---|---|
| `docs/PMO_MERIDIAN_REPORT_EVIDENCE.md` | `scripts/agent_guard.py` — not in this role's owned paths | Written to `docs/REPORTS/PMO_MERIDIAN_REPORT_EVIDENCE.md`; moving it is an act for a role that owns the path |
| `docs/PMO.md` (§4 numbers wrong, §5 V-8 claim wrong) | not owned by this role | Corrections proposed below, not applied |
| `docs/PMO_MERIDIAN_ASSESSMENT.md` (§8 V-8) | not owned by this role | Same |
| `docs/RAID_LOG.md`, `docs/DECISION_LOG.md`, `docs/REQUIREMENTS_TRACEABILITY.md`, `docs/AUDIT_EVIDENCE_INDEX.md` | instructed not to edit in this session | RAID rows proposed below, not applied |

No path was routed around through Bash.

## 3. Decisions taken

None. This packet records evidence and proposes; it decides nothing. Two corrections to published documents are **proposed** and need their owners:

| # | Proposed correction | Owner of the path | Alternatives |
|---|---|---|---|
| C-1 | `docs/PMO.md` §4: "14 decisions and 21 open actions" → 48 and 25, per `docs/PMO/meridian_sync_2026-09-08.json` | PMO.md owner | (a) correct the number; (b) delete the sentence and cite the file; (c) leave it — rejected: the number is quoted onward |
| C-2 | Withdraw V-8 as a Meridian defect (`docs/PMO.md` §5, assessment §8) and re-file as E-1 (a book created before migration 036 cannot be migrated onto a programme ladder) | PMO.md and assessment owners | (a) withdraw and re-file narrower; (b) keep V-8 and add a caveat — rejected: the claim as written is contradicted by `wbs.js:113-120`; (c) keep as is — rejected |

## 4. RAID entries proposed (not written — `docs/RAID_LOG.md` is off-limits this session)

| Proposed | Type | Item | Owner | Needed by | Gate |
|---|---|---|---|---|---|
| P-1 | Gap | `docs/PMO.md` §4 publishes load counts contradicted by the evidence file (48/25, not 14/21) | Program Orchestrator | before the report leaves the repository | — |
| P-2 | Gap | V-8 filed as a Meridian defect is contradicted by `wbs.js:113-120` and `admin.js:632`; withdraw and re-file as E-1 | Program Orchestrator | same | — |
| P-3 | Gap | The third Meridian load (134 items, 17 writes) has no evidence file; loader logs carry no timings and no bodies | Program Orchestrator | next `make pmo-sync` | — |
| P-4 | Issue | The loader opens the Product Owner's weekly and never closes it; 59 decisions and 28 actions sit in an unfrozen room and the cadence never advances | Program Orchestrator | next weekly | — |
| P-5 | Issue | The loader writes as a human admin account; every portfolio write in Meridian's trail is attributed to "System Administrator (admin)" | Program Orchestrator | before H-28 (a real instance) | C |
| P-6 | Gap | Twelve upstream improvements delivered for us; none adopted in `scripts/meridian_sync.py` (ladder, criteria, `PUT /api/v1/*`, decision register) | Program Orchestrator | before the next load | — |
| P-7 | Risk | Meridian's portfolio view reports all sixteen RoboTrader projects GREEN at 0% measured; if quoted outside the room it states the opposite of the programme's status | Product Owner | now — treat as not quotable | — |
| P-8 | Assumption | Meridian 5.10.0 (`e352bc8`) carries no release tag; all thirteen register requests are `released: false`. We depend on an untagged commit | Product Owner | before anything a gate reads moves into Meridian | C |
| P-9 | Dependency | H-31 (file the value requirements upstream) and H-28 (a real instance) are human acts and gate everything this report can lead to | Product Owner (human) | H-28 before Gate C | C |

## 5. Threat-model delta

None. Meridian holds no trading control, no credential, no limit and no order route; no gate and no control in this programme reads it [Source: `docs/ADRs/ADR-017.md` §Decision.1]. One security observation, already in the report as E-2 and P-5: the loader holds a human administrator credential in its environment because sites, programmes and people are not writable through the scoped integration API. That is a credential-handling concern for the operator of the Meridian instance (H-28), not for the trading platform.

## 6. Control quartet

Not applicable — no control-bearing code was written or changed. `test/contract/test_meridian_sync.py` (2 tests) is unchanged.

## 7. Evidence

Listed in full in §8 of `docs/REPORTS/PMO_MERIDIAN_REPORT_EVIDENCE.md`. Re-measured in this session: Meridian `npm test` at `e352bc8` → 513 pass / 101 suites / 0 fail / 123.7 s; 39 migrations; 52 tables; 8 writable v1 collections of 52 tables; 183 route declarations of which 12 in `v1.js`; 11 git tags, newest `v5.9.0`; both sync logs decomposed request by request; 13 register requests, all `accepted: false` and `released: false`.

## 8. Assumptions, confidence, provenance

| Statement | Confidence | Provenance |
|---|---|---|
| The 84-minute loop happened as timed | high | git timestamps in both repositories, this session |
| The two ladders are our loader's doing, not a 5.10.0 defect | high | `wbs.js:113-120`, `admin.js:22,632`, `shared/engine.js:89`, CHANGELOG, and the same ten milestones on 5.9.0 before the feature existed |
| Value objects are not writable through v1 | high | `v1.js:100-107` (8 routes), `portfolio.js:1814+` (session routes only) |
| An unmeasured project renders GREEN | medium | screenshot plus the "no budget — outside EVM" and "not measured" captions; the derivation itself was not read in code |
| The executive tiles are book-wide regardless of the programme filter | **low — [Open]** | screenshot only; E-6 states what would settle it |
| A milestone PATCHed `done` does not render as accepted | **low — [Open]** | screenshot only; one `GET /api/bootstrap` would settle it, E-7 |
| 5.9.0 figures (449 tests, 40-minute first hour, 1,529-row archive) | medium | [Source: `docs/PMO_MERIDIAN_ASSESSMENT.md`], not re-run by us |

## 9. What this packet does not do

It does not approve, certify or file anything. Filing upstream is H-31, a human act. The report has no reviewer and needs one before it goes to Meridian's Product Owner.
