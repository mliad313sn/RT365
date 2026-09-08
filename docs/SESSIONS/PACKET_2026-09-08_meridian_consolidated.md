# Session packet — the consolidated Meridian field report (2026-09-08)

| Field | Value |
|---|---|
| Session | RT365 Product Owner (delegate agent), under D-039 / D-040 / D-065 |
| Branch | `docs/meridian-consolidated`, from the head of `claude/project-owner-agent-setup-hi3xqu` (`92b223a`) |
| Produced | `docs/REPORTS/PMO_MERIDIAN_CONSOLIDATED_REPORT.md`, `docs/REPORTS/meridian_requests_v3.json` |
| Reviewer (different line) | **not assigned.** This packet and the report it accompanies have no second line; nothing here gates a decision or convenes anything |
| Approving body | Product Owner (human), D-039 — **no approval is recorded by this session** |
| Status | v1.0, prepared, not filed. Filing upstream is H-31, a human act, still open |

## 1. Roles

Author: RT365 Product Owner delegate agent. Sources read: the round-two field evidence written by the
Program Orchestrator (`docs/REPORTS/PMO/round2/`), the two half-reports, round one
(`docs/PMO_MERIDIAN_ASSESSMENT.md` §§1–8), `docs/PMO.md`, `docs/ADRs/ADR-017.md`,
`docs/IMPROVEMENT_REGISTER.md` §D/§D2, `docs/MISSING_ACTIONS.md` H-31, and Meridian's own code and
register at `77c4b49` (`main`, 5.9.0) and `cbe99ef` (branch, 5.10.0), read-only.

## 2. Purpose

Replace two half-reports and two rounds of field evidence with one document a Product Owner can act
on from the first page; correct three things this programme published incorrectly; and produce a
request register that can be handed upstream without colliding with Meridian's own numbering.
[Measured: the two rounds] [Source: Meridian's code and `docs/requests/rt365.json`]
[Open: H-31 — nothing has been filed]

## 3. Decisions taken in this session

None that bind the programme. Three editorial positions were taken and are recorded here rather than
in `docs/DECISION_LOG.md`, which this session may not edit; the proposed decision rows are in §5.

1. **Round two supersedes round one wherever they disagree**, because it ran on a fresh clone of the
   default branch with an empty book, and round one ran on a seeded demonstration book.
   *Alternative considered:* present both and let the reader choose — rejected, because two of round
   one's headline numbers (`$51.3M`, `ON TRACK 82%`) are artefacts of demonstration data we failed to
   remove, and reprinting them beside the truth would repeat the error.
2. **`docs/PMO/meridian_requests_v2.json` is withdrawn before filing.** It numbers items
   REQ-14..REQ-28, colliding with Meridian's delivered REQ-14 (raised from our D-057) and duplicating
   our own V-1..V-12, which are already their REQ-20..REQ-31. *Alternative considered:* file it and
   let their Product Owner renumber — rejected, because the collision would overwrite a delivered
   request with a different one, and the cost of the mistake falls entirely on them.
3. **New requests are numbered from REQ-32, and no status on any of their existing lines is changed
   by our file.** *Alternative considered:* propose `open` on the twelve of ours they have registered
   — rejected: opening a line in their register is theirs to do, and `accepted` stays false even on
   REQ-06, which we have now measured working, because filing an acceptance is a human act (H-31).

## 4. RTM rows proposed (this session may not edit `docs/REQUIREMENTS_TRACEABILITY.md`)

None. The consolidated report creates no RT365 requirement, no architecture element, no control and
no test. Meridian holds no fact that any RT365 gate, control or test reads; the ledgers and CI hold
the engineering truth (ADR-017 §Decision.1). The one RTM-adjacent statement worth recording is a
negative and it is already in ADR-017: **no gate criterion, control or test in this programme reads
Meridian.** If the owning role wishes a row for the PMO integration itself, the existing coverage is
`test/contract/test_meridian_sync.py` (the ledger readers and the credential rule) and TC-PMO-002
(the ladder declaration), both unchanged by this session.

## 5. Ledger rows proposed for the owning roles

This session may not edit `docs/RAID_LOG.md`, `docs/DECISION_LOG.md`,
`docs/REQUIREMENTS_TRACEABILITY.md` or `docs/AUDIT_EVIDENCE_INDEX.md` under its instructions, so the
rows are proposed here. Ids are indicative only — the current heads are O-180, R-57, D-069, H-31.

### 5.1 RAID (`docs/RAID_LOG.md`) — for the Program Orchestrator

| Type | Item | Owner | Needed by | Status |
|---|---|---|---|---|
| Risk | Meridian's default branch is 5.9.0. Every improvement this programme reported as delivered is on an unmerged, untagged branch, so ADR-017's "pin the commit" is the only option and the pin is to a branch head that may be rebased. Our own published claim that the twelve were delivered upstream is corrected in `docs/REPORTS/PMO_MERIDIAN_CONSOLIDATED_REPORT.md` §2.1 | Program Orchestrator | Gate B | Open |
| Gap | `docs/RAID_LOG.md` states no probability, impact, residual target or review date. Any rating shown outside this repository is derived (rule R2-PI-1) and must carry that sentence | Program Orchestrator | Gate B | Open |
| Gap | `docs/DECISION_LOG.md` D-058..D-066 carry five columns where the ledger's own header declares seven; nine decisions cannot be published as decision records, and `supersedes` could not be exercised | Program Orchestrator | Gate B | Open |
| Gap | 14 of 29 open human acts name a committee, not a person, and 28 of 29 carry no due date; neither can be tracked by any tool | Product Owner | Gate B | Open |
| Issue | `scripts/meridian_sync.py` declares the ladder as `Gate A — Discovery` and creates `Gate A`, so every load adds six milestones on top of the six Meridian scaffolds — twelve gates on the governance project, on two date lines | Program Orchestrator (script owned elsewhere) | Gate B | Open |
| Issue | `scripts/meridian_sync.py` aborts on the first status ≥ 300 and writes its `--json` evidence only on success, so a partial load changes the book and leaves no evidence at all. Observed: nine register rows written, then a correct 409 against a frozen meeting, then abort | Program Orchestrator | Gate B | Open |
| Risk | The loader authenticates as an administrator, so Meridian's documented break-glass exemption lets it sign every step of a change request; 621 of 626 audit events name one human account whose password lives in the loader's environment | Security Architect | Gate C | Open |
| Risk | Meridian reports this programme GREEN and 100 % on track with SPI and CPI 1.00. The portfolio view is not quotable outside this room until the upstream defect (their REQ-33 as proposed) is closed or we stop feeding it budget-less projects | Product Owner | Gate B | Open |
| Assumption | A supplier claim is verified from a clean clone of the **default branch**, not from a checkout already in hand. Round one verified code on a ref a stranger cannot obtain | Product Owner | Gate B | Open |

### 5.2 Decision rows (`docs/DECISION_LOG.md`) — for the owning role, if the human Product Owner takes them

| Proposed decision | Alternatives | Provenance |
|---|---|---|
| Round two of the Meridian field assessment supersedes round one wherever the two disagree; round one's `$51.3M` and `ON TRACK 82%` are withdrawn as demonstration-book artefacts, and the claim that the twelve improvements were delivered upstream is corrected to "built on an unmerged, untagged branch" | (a) publish both rounds side by side — rejected, it reprints known artefacts; (b) silently amend round one — rejected, the correction must be as visible as the original claim | [Measured: `docs/REPORTS/PMO/round2/EVIDENCE.md`] / [Source: Meridian `main` @ `77c4b49`] |
| `docs/PMO/meridian_requests_v2.json` is withdrawn before filing; `docs/REPORTS/meridian_requests_v3.json` replaces it | (a) file v2 and let Meridian renumber — rejected, it would overwrite their delivered REQ-14; (b) file nothing — rejected, twelve of our requests are already in their register and round two changed the evidence under several | [Source: `docs/requests/rt365.json` registerVersion 6, parsed] |
| The Meridian portfolio view is not quotable outside this programme until the unmeasured-reads-green defect is closed upstream or this programme stops loading budget-less projects | (a) quote it with a caveat — rejected, a colour outruns its caveat; (b) stop loading until fixed — rejected, the rest of the record is useful and honest | [Measured: `01_portfolio.png`, `05_reports_value.png`] / [Source: `shared/engine.js:166-168, 190-201`] |

### 5.3 `docs/MISSING_ACTIONS.md` — for the owning role

H-31 should be restated: the pack to file is now
`docs/REPORTS/PMO_MERIDIAN_CONSOLIDATED_REPORT.md` and `docs/REPORTS/meridian_requests_v3.json`
(REQ-32..REQ-39 new; REQ-06, REQ-09, REQ-16, REQ-17, REQ-19, REQ-20..REQ-31 referenced with no status
change), on branch `docs/meridian-consolidated`. The previously named pack
(`docs/REPORTS/PMO_MERIDIAN_REPORT_VALUE.md` and `docs/PMO/meridian_requests_v2.json`) is superseded
and the register file **must not be filed**. H-28 (a real Meridian instance) remains open and is not
discharged by the restore drill measured in round two, which was PGlite on a laptop.

### 5.4 `docs/AUDIT_EVIDENCE_INDEX.md` — for the owning role

Nothing to add. No artefact produced by this session is gate evidence for any RT365 control. The
round-two evidence pack is management evidence about a third-party tool and is indexed inside the
consolidated report §11.

## 6. Threat-model delta

None. Meridian holds no broker route, no secret of this programme's, no limit write path, no audit
delete path and no way to change mode; no AI or MCP component gained any capability in this session;
no environment was promoted. One pre-existing exposure is restated rather than created: the loader
holds a human administrator credential for Meridian in its environment (§5.1, Security Architect,
Gate C). It is an exposure in the PMO integration, not in the trading system.

## 7. Control quartet

Not applicable. This session produced no control-bearing code. The nearest thing to a control
exercised is the repository's own write-scope guard, and it behaved correctly: it refused every
`docs/PMO*` path to this role, the refusal is recorded verbatim in
`docs/REPORTS/PMO/round2/GUARD_PROBE.md`, and it was not routed around — the report and the register
were written where the role owns the path. The instruction not to edit `RAID_LOG`, `DECISION_LOG`,
the RTM and the audit index was honoured by proposing rows in §5 rather than writing them.

## 8. Evidence produced by this session

| Artefact | What it holds |
|---|---|
| `docs/REPORTS/PMO_MERIDIAN_CONSOLIDATED_REPORT.md` | the consolidated report: executive summary, three corrections, what Meridian is worth measured, the finding that matters most, what the value model gets right, defects split theirs/ours/open, 25 consolidated requirements, sequencing, what "flagship" would require, concerns |
| `docs/REPORTS/meridian_requests_v3.json` | `meridian-request-register/1`, registerVersion 7, 25 requests: 17 referencing their ids with no status change, 8 new from REQ-32 |
| this packet | proposed ledger rows, RAID entries, and the assumptions below |

## 9. Assumptions, confidence and provenance

- **Assumption:** the round-two evidence pack is a faithful record of what was run. It was written by
  a different role (Program Orchestrator) and carries per-request timings, bodies and status codes;
  this session re-read Meridian's code independently at both commits and confirmed every [Source]
  citation used in the consolidated report. Confidence **high**.
- **Assumption:** Meridian's register at `cbe99ef` is its current register. Confidence **high** — it
  was parsed, not read. [Open: it may move; `registerVersion` is the check.]
- **Confidence high** that every defect in the report exists as described; **medium** on effort
  estimates and priorities, which are ours; **[Open]** on Q-1..Q-9 in §6.3 of the report.
- **Nothing in this session** promotes an environment, states a return, a price or a market claim,
  certifies evidence as complete, convenes a gate, or records an approval — on our behalf or on
  Meridian's.
