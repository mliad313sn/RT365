# Build session — E11 durable audit and external anchoring (register B-5, delegation D-051)

| Field | Value |
|---|---|
| Date | 2026-09-08 |
| Epic | E11 Audit, surveillance, reporting |
| Register item | B-5 (external audit-anchor publication and an append-only durable audit interface) |
| Authority | D-051 (delegation), D-058 (raised B-5 in priority: control state became durable while its trail did not), Security & Privacy Board recommendation on O-110 |
| Branch | `build/e11-audit-anchoring` |
| Author | build agent E11 (AI) wrote `audit_service/anchor.py` and the TC-AUD-006..009 tests before the harness usage limit ended its run (RAID O-124); the Product Owner delegate implemented the store rewrite, the composition wiring, the alert entries, ADR-020 and this packet against those tests |
| Reviewer | pending — SRE Lead (2nd line), Security Architect, Independent Validation Agent |

## 1 Roles

Backend Lead and SRE Lead build; the Security Architect owns the integrity scheme; Internal Audit and the IVA are the readers this work exists for. No approval is recorded here: the human Product Owner decides every gate (D-039), the AI delegate decides delegated matters (D-040).

## 2 Purpose

Close the inconsistency D-058 created and the IVA had already named: control state survived a restart, its audit trail did not, and the anchors that were supposed to make truncation detectable were produced in the same process as the events (IVA-09, R-31, OBJ-3) [Committee]. The audited party cannot be its own witness.

## 3 Decisions and ADRs

ADR-020 (proposed, written with the change): three layers — the store seam, the audit hash chain, and an external anchor written by a different principal — with the audit trail in its own store file, the sequence allocated by the store, no update or delete path at any layer, a witness that may never contradict itself or be re-established automatically, and fail-closed verification with one incident row per outage. Alternatives (keyed HMAC, transparency log, blockchain anchor, TSA timestamps, backups) and consequences are in the ADR.

## 4 Proposed RTM row text (the Program Orchestrator edits the ledger)

| Req | Architecture element | Implementation owner | Control | Test IDs (quartet) | Evidence | Gate | Status |
|---|---|---|---|---|---|---|---|
| NFR-AUD-01 | Audit store on the `rtcore.store` seam in its own file (`audit_state.sqlite`), sealed heads witnessed by `audit_service.anchor.AnchorPublisher` in a separate directory owned by a different principal (ADR-020) | Backend Lead / SRE Lead | Append-only at every layer (no update or delete path exists); store-allocated sequence; chain verified at open and refused on any break; anchor records form their own hash chain; publication refused when it would contradict the last anchor or silently re-anchor a non-empty chain; verification fails closed with reason codes and one incident row; S1 alerts `audit.chain_verification_failed` (auto-action: platform Kill Switch) and `audit.anchor_missing` (page) | TC-AUD-001..009 | TEST_CASES/TC-AUD.md; ADRs/ADR-020.md | B/C | dev/sim: the anchor principal is a directory, not a separate identity [Open: O-54]; anchor cadence and retention are placeholders [Open: O-111]; WORM storage, replica and DR drill on real infrastructure [Open: H-19, R-05] |

## 5 Threat-model delta (proposed rows; the Security Architect owns the file and assigns the T-numbers)

| Threat | Boundary | Control | Test | Owner |
|---|---|---|---|---|
| The audit trail is lost or partly lost on a restart while control state survives, so an auditor cannot reconstruct what happened to durable state [Committee: D-058, ADR-020] | B4 | Audit events are durable rows on the seam in their own store; the chain and its seals are read back at open | TC-AUD-006 | Backend Lead |
| An actor rewrites audit rows and recomputes every unkeyed seam digest (the O-110 offline attacker) | B4 (host) | The audit hash chain is verified at open independently of the seam digests; the store is refused with `AuditIntegrityError` | TC-AUD-008 | Security Architect |
| The audit tail is truncated, or a stale backup is restored, and the store verifies against itself | B4 | The externally published anchor is compared with the chain: a shorter chain, a head mismatch, or a seal the witness does not carry all fail closed | TC-AUD-007 | SRE Lead |
| The external witness is edited, shortened, removed from the middle, or lost | B4, B7 | Anchor records form their own hash chain, verified before use; a missing or broken witness fails closed and alerts; no automatic re-anchoring | TC-AUD-007, TC-AUD-008 | SRE Lead |
| An anchor is published over a tampered or rolled-back chain, laundering it | B4 | A publication whose head contradicts the last published anchor is refused, whoever asks; a scheduled publication may never create the first anchor of a non-empty chain | TC-AUD-007, TC-AUD-008 | Backend Lead |
| The publisher principal, or anything holding its handle, reaches an audit write or delete path | B4, B6 | The publisher receives only a `ChainHead`; `AnchorHandle` exposes exactly `head` and `length`; no audit mutation API exists to reach | TC-AUD-008 | Security Architect |

## 6 Control quartet

| Control | Positive | Negative | Abuse | Recovery |
|---|---|---|---|---|
| Durable, witnessed audit (TC-AUD, NFR-AUD-01) | **TC-AUD-006** events, seals and anchors written by one process are read back by a rebuilt platform; the sealed head still matches; scheduled publication continues; tenant-partitioned reads and the memory default are unchanged | **TC-AUD-007** a rollback that satisfies the seam fails against the witness (`AUD-CHAIN-TRUNCATED`, then `AUD-CHAIN-HEAD-MISMATCH` once the platform appends onto the truncated prefix, with the S1 alert engaging the platform Kill Switch); an anchor staler than the ceiling (`AUD-ANCHOR-STALE`) and a lost witness (`AUD-ANCHOR-MISSING`) fail closed; a restart fabricates no fresh anchor | **TC-AUD-008** an edited row is refused by the seam, and by the chain after every seam digest is recomputed; an edited, mid-removed or shortened anchor file is caught (`AUD-ANCHOR-CHAIN-BROKEN`, `AUD-ANCHOR-TAIL-REMOVED`); rollback and fork anchors are refused whoever asks; the publisher and the handle carry no audit write path; no seal is possible while the witness chain is broken | **TC-AUD-009** after the corrupt anchor directory is replaced by the last good copy, verification passes; the incident and its recovery are audit rows sharing the alert's correlation id; a second failing verify re-alerts but opens no second incident; the next seal puts the incident rows under a published anchor and a restart sees them |

Existing tests: none weakened. TC-AUD-001..005 pass unchanged, including the "no update or delete API exists" check, which now also holds for the anchor publisher and its handle.

## 7 Evidence

- `make all` at the committed tree: lint and format clean, mypy `Success: no issues found in 101 source files`, 21 event schemas unchanged, network policies OK, registry OK, 67 agents match `goals/`, secret scan clean, **211 passed**; `make evidence` wrote 191 records, **22/22 areas with a full quartet**.
- New: `services/audit/audit_service/anchor.py`, `docs/ADRs/ADR-020.md`; alert `audit.anchor_missing` added to `observability/alerts.yaml` and `docs/ALERT_CATALOG.md` (S1, no auto-action, runbook "Kill Switch activation").
- Rewritten: `services/audit/audit_service/store.py` (seam-backed, sequence from the store, seals persisted, anchor policy, reason codes, incident handling, alert sink).
- Modified: `apps/web/web_bff/platform.py` (`anchor_dir`, `anchor_every`, `max_anchor_lag`, `AUDIT_STORE_FILENAME`, alert sink wired after the router exists), `test/quartets/test_tc_aud_audit.py` (TC-AUD-006..009).
- Completion note: the build agent's run ended at the harness usage limit with the tests and the anchor module written and the store not yet rewritten (RAID O-124). The delegate implemented against those tests without weakening them; three implementation facts they encode — the sequence is allocated from the store, the witness may not contradict itself, and a scheduled publication may not re-anchor a non-empty chain — were found by making the tests pass honestly rather than by changing them.

## 8 Proposed RAID updates (the author does not edit the ledger)

| ID | Proposed change |
|---|---|
| R-31 | Status → "Remediated in dev/sim (ADR-020): the audit chain is durable on the seam in its own store, tail truncation is detected against an externally published anchor, and `seal()` is no longer produced only in-process. Open: the anchor principal is a directory rather than a separate identity (O-54), WORM storage and the DR drill on real infrastructure." |
| O-54 | Add: "the publication seam exists (`AnchorPublisher`, `FileAnchorPublisher`); what remains is the deployment identity — a WORM bucket or replica written by a principal the audit process cannot assume — and the cadence and retention of anchor records." |
| O-110 | Add: "the Board's Option B now has its second half: the audit chain is durable and externally witnessed (ADR-020), so anchoring the control-store journal head into it is implementable. Sequencing: control-store journal head → audit chain → external anchor." |
| O-111 | Add: "anchor records accumulate at one per explicit seal plus one per `anchor_every` events; their compaction and retention belong with the control-store journal's." |
| new | Gap: `anchor_every` (25) and `max_anchor_lag` (200) are dev/sim placeholders, not measured or decided values; the real cadence comes from the O-54 decision and the retention rules. |
| new | Gap: a lost or corrupt witness is a fail-closed condition that stops the platform. `docs/DEPLOYMENT_RUNBOOK.md` and `docs/INCIDENT_RESPONSE.md` must carry the recovery (restore the replica from the last good copy, verify, then seal) and state that disabling the check is not the fix. |
| new | Open item: the audit store now has its own file, so `store_dir` holds two SQLite files with different owners in deployment (O-115 separation applies to this pair as well). |

## 9 Definition of Done — self-assessment

- [ ] Reviewer ≠ author; protected paths approved by a 2nd-line CODEOWNER — pending (SRE Lead, Security Architect, IVA)
- [x] Control quartet passes for the control touched (TC-AUD-006..009); no existing test weakened
- [x] Evidence record written (`docs/TEST_CASES/TC-AUD.md`; reviewer column pending by construction)
- [x] Observability delivered — `audit.anchor_missing` catalogued S1 in both the YAML and the catalogue; every incident row carries a correlation id shared with the alert
- [x] Security scans clean; no dependency added
- [x] Rollback verified in the lowest environment: without `store_dir` and `anchor_dir` the store is in memory with no publisher and every prior outcome is unchanged
- [ ] Documentation and RTM updated — ADR-020 written; RTM/RAID/THREAT_MODEL rows proposed above for the ledger owners
- [x] Not promoted beyond the environment the current gate authorises (dev/sim)

## 10 Concerns for the Product Owner

- **C-1 The "different principal" is a directory, not an identity.** [Open: O-54] `FileAnchorPublisher` writes to a separate directory; in this process the same code can still reach it. What makes the control real in deployment is a WORM bucket or a replica whose write credential the audit workload does not hold. The seam is built for that; the identity is a human/infra act.
- **C-2 The cadence numbers are placeholders.** [Open] Publishing every 25 events and failing beyond a lag of 200 are dev/sim defaults, not decided values. They bound how much an attacker could reach and how stale the witness may be, so they are a risk decision, not a tuning knob.
- **C-3 A lost witness now stops the platform.** [Committee] That is the intended fail-closed behaviour and it is drilled (TC-AUD-007), but it is a new operational failure mode. The runbook must say that restoring the replica is the fix and that turning the check off is not. Until that runbook exists, an operator meeting this at 03:00 has no instruction.
- **C-4 Two stores under one directory.** [Open: O-115] The audit trail deliberately has its own file, so `store_dir` now holds two. From shadow they should have different owners and different backup schedules, which is the same argument O-115 makes for the Execution plane.
- **C-5 Retention, legal hold and the right to erasure meet an append-only chain.** [Open] Nothing here can delete, by design. How that coexists with retention schedules and any erasure obligation is a Privacy Lead and Compliance question that this build does not answer and must not pre-empt; the usual answer is payload minimisation plus crypto-shredding of referenced payloads, and neither exists yet.
- **C-6 Anchors accumulate without compaction.** [Open: O-111] Same situation as the control-store journal and the nonce journal. Fine at dev/sim size; a policy is owed before shadow.
- **C-7 What is not verified.** [Open] Behaviour across OS processes and hosts, a power-loss mid-transaction, WORM semantics of a real object store, and the performance of chain verification at open once the trail is large (it is O(events) on every open — at dev/sim sizes invisible, at a year's volume it is not).
- **C-8 The platform Kill Switch fires on a chain failure.** [Committee] `audit.chain_verification_failed` is catalogued with `killswitch_platform`, so a corrupted audit store halts trading platform-wide. That is the right direction for a control envelope and it is also the largest blast radius any of these alerts has; the Trading Risk Committee may want to confirm it deliberately rather than inherit it.
