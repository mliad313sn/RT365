# BUILD E11 2026-09-08 — a platform that had a witness and no longer has one does not open (Red-Team Case B), and no publication witnesses a chain below the floor (Case C)

| Session | Date | Author | Line | Status |
|---|---|---|---|---|
| Build agent E11 closing the Red-Team Lead's Case B and Case C on the Product Owner's decision | 2026-09-08 | build agent E11 (AI) | 1st line (build), for the Backend Lead | **built and tested in dev/sim; nothing approved, no gate passed, no ledger id assigned** |

> This packet is a **build record**, not an approval, not a decision and not a gate. I write and test; I never approve, certify or promote [Source: 13]. Register item **E-6**, branch `build/e11-witness-cases-b-c`, worked from `48650ed`. Commits: `1527937` (tests, red), `4823984` (implementation), `01b4575` (ADR-020 amendment 3 and regenerated evidence). `make all` green, `make security-scan` clean. **235 tests pass (227 before), 24/24 quartet areas complete.** Two existing tests were changed and **both were strengthened, neither weakened** — §8 states exactly what changed and why. I state no capacity figure, latency, throughput, cost, SLO target, broker capability, data entitlement or regulatory status, and I claim no return. Every statement is tagged [Source: NN], [Committee] or [Open].
>
> **Read at `48650ed`** [Committee]: `docs/PENTEST/probes/rt_probe_01_audit_witness.py` and the six other probes, `docs/ADRs/ADR-020.md` including amendments 1 and 2, `docs/DECISION_LOG.md` D-066, `docs/RAID_LOG.md` (R-31, O-54, H-21, O-110, O-128, O-133, O-164, O-165), `services/audit/audit_service/store.py` and `anchor.py`, `libs/core/rtcore/store.py` and `journal_anchor.py`, `apps/web/web_bff/platform.py` and `app.py`, `observability/alerts.yaml`, and the quartets `test/quartets/test_tc_aud_audit.py` and `test_tc_dur_durability.py`.

---

## 1. Roles

| Function | Role | Line | In this session |
|---|---|---|---|
| **Builder** | **build agent E11 (this agent)** | 1st | measured the attacks, wrote the quartets first (red), then the change; **approved nothing** |
| Accountable owner of the change | Backend Lead | 1st | owner of `services/audit/` and the composition root |
| **Author of the findings (Case B, Case C)** | Red-Team & Pen-Test Lead | 3rd | the probe is the specification of the attack; I did not edit it, and I did not make my tests easier than it |
| 2nd-line reviewer of this build | **Compliance Agent** | 2nd | **pending — review requested with this packet** |
| Reviewer of ADR-020 amendment 3 | Red-Team Lead (as the findings' author), SRE Lead, Security Architect | 3rd / 1st / 2nd | **pending** |
| Owner of `docs/THREAT_MODEL.md` | Security Architect | 2nd | addressee of §5; **ids are his** |
| Owner of `docs/RUNBOOKS.md` / RB-13 and of the availability model | SRE Lead / Cloud Architect | 1st | addressees of §6; **I did not edit their documents** |
| Owner of the ledgers (RAID, RTM, DECISION_LOG) | Program Orchestrator | — | addressee of §4 and §7; **I assigned no id and wrote no ledger row**, as instructed |
| Independent validation | Independent Validation Agent | 3rd | pending. TC-AUD-015..022 are **my** adversary model, modelled on the Red-Team Lead's probe; they are not independent validation (O-144) |
| **Decision** | **human Product Owner (D-039)** | — | decided the two behaviours on 2026-09-08; **approval of this build is pending — agents never record an approval** |

---

## 2. Purpose, and what was measured first

I ran `RT_ENV=sim python3 docs/PENTEST/probes/rt_probe_01_audit_witness.py` at `48650ed` before designing anything. Verbatim:

```
=== Case B: the external witness is deleted, platform restarted, nobody calls verify() ===
  audit_anchors.jsonl deleted (the witness a WORM medium would hold)
  the platform STARTED without a witness: 61 events, latest anchor=None
  an intent ran: final_state=FILLED, broker submissions=1
  alerts raised without calling verify(): ['audit.anchor_missing']
  verify(): ok=False reason=AUD-ANCHOR-MISSING
  alert audit.anchor_missing severity=S1 auto_action=none            (x4)
  kill switch active levels after verify(): []

=== Case C: truncate the chain, delete the witness, then let an operator seal ===
  five events removed from a chain sealed at length 39; the witness file deleted
  verify() before the operator acts: ok=False reason=AUD-ANCHOR-MISSING
  after a plain operator seal: published anchor length=56, verify() ok=True reason=''
  the truncation is now witnessed as if it had never happened
```

**The Product Owner's decision** [Committee, PO 2026-09-08]: the response is a refusal, not a Kill Switch — a platform that had a witness and no longer has one must not open, in the same way and for the same reason that a control store whose head cannot be confirmed does not open: refuse, alert, write nothing. D-066 stands and the `auto_action: none` on `audit.anchor_missing` stays: a Kill Switch activation is itself a store row and would write to the store under suspicion. And: a seal must never witness a chain shorter than what this store has already sealed; re-establishing a witness after a genuine loss must be an explicit, audited operator act that cannot be reached by accident or by repeating the ordinary seal.

**One measurement changed the design, and the Product Owner should know it.** The decision named the store's `SealRecord`s as the evidence that a witness existed ("the store already persists its seals with their anchor sequence, so it knows which case it is in"). I measured that against the probe's own rollback and it does not survive it:

```
p1 seals: [(39, 3)]            seal rows before rollback: 1
                               seal rows after rollback:  0
p2 events: 56  seals: []       (sealed length was 39)
```

A seal is written **after** the events it seals, so a rollback that removes those events removes the seal record with them. Taken literally, the decision would have closed Case B and left Case C open. So the seal ledger is kept **and** the fact "this store has been witnessed" is additionally written **into the hash chain itself**, as an `audit.anchor.published` row after every genesis and scheduled publication. The genesis mark is the first event of the chain: no tail truncation that leaves a non-empty chain can remove it, and removing it breaks the chain at sequence 0. That is what refuses Case C — measured after the change, Case C is refused *on the mark* (`anchor 2 (mark)`), because its seal record is indeed gone.

**What this is not.** It enables no market, no strategy and no autonomy; it moves nothing along the environment ladder; it removes, relaxes or skips no verification and adds no way to disable one (O-165 stands); `services/execution` and `services/risk` were not touched; and no AI or MCP component gains a path — the checks live in the audit store's constructor and publication path, the operator act is a library entry point that the composition root cannot reach, and there is still no update and no delete API at any layer (TC-AUD-002 unchanged and green).

---

## 3. The design, and the alternatives (ADR-020 amendment 3 is the artefact of record)

`docs/ADRs/ADR-020.md` now carries **amendment 3 (Proposed)** with eight decision points and six alternatives in a table. In brief:

1. **Witness continuity at open.** `AuditStore.__init__`, after the chain verifies and before anything may be written, asks: do this store's own records name a witness (a `SealRecord` with an anchor sequence, or an `audit.anchor.published` row)? If they do and the anchor store holds no readable record, it raises the catalogued S1 `audit.anchor_missing` with `AUD-WITNESS-LOST` (nothing there) or `AUD-WITNESS-UNREADABLE` (there but broken) under the start-up correlation id, and then raises `WitnessLostError`. **It writes nothing** — no incident row, no publication, no activation. Composition already closes the handles and re-raises, so no platform object is ever returned.
2. **The genesis case is left alone.** No records naming a witness → open, exactly as ADR-020 always did. This is the honest distinction the Product Owner asked for and it is asserted positively (TC-AUD-015) and negatively (TC-AUD-016), not assumed.
3. **The floor.** Before *any* publication — operator seal, scheduled publication, or the attested act — the chain is checked against every head this store recorded witnessing. A contradiction is `AUD-SEAL-BELOW-FLOOR`, S1 `audit.chain_verification_failed`, nothing published. It is applied to automatic publications too, because the *worst* version of Case C needs no operator at all: trim the witness's tail to match the truncated chain and the next scheduled publication would have re-anchored the refilled chain by itself (this is TC-AUD-020, and it is a stronger attack than the probe's).
4. **An ordinary seal can no longer create the first anchor for a non-empty chain** (`AUD-SEAL-UNWITNESSED`). This is the sentence in ADR-020 rule 3 that Case C used, closed.
5. **The named act.** `audit_service/reestablish.py` — a read-only `inspect_chain` (opens no `AuditStore`, returns values only) and `reestablish_witness`, refused unless the witness is genuinely absent, the attestation states actor, reason, and the exact length, head hash and last recorded anchor sequence, and the chain clears the floor. One `audit.witness.reestablished` row under the operator's correlation id, then an anchor over the head **that includes that row**. `build_sim_platform` has no `attestation` parameter and a test asserts it.

**Alternatives I weighed and rejected** (full table in the ADR): a Kill Switch auto-action instead of a refusal (rejected by D-066 — it writes to the store under suspicion, and a halted platform is still an open one); the seal ledger alone (rejected **on measurement**, above); a new alert name (rejected — `audit.anchor_missing` is already catalogued as "absent, stale beyond the ceiling, broken or ahead of the published witness", so `observability/alerts.yaml` and `docs/ALERT_CATALOG.md`, which I may not write, still agree); a CLI verb for the recovery (rejected — a library entry point is harder to reach by accident than a shipped command, and the operator surface belongs to the SRE Lead); a flag "for operations" (ruled out by the Product Owner and by CLAUDE.md); and **writing the audit chain's length into the control store** so that a rollback of one file is caught by the other — not built, because it is a new write direction the owner has not decided, and it is the single most valuable next step (§7 R-a, §11).

---

## 4. Proposed RTM rows — for the QA Lead / Program Orchestrator, **not written by me, no ids assigned**

| Requirement | Architecture | Owner | Control | Test | Evidence | Gate |
|---|---|---|---|---|---|---|
| NFR-AUD-01 | `services/audit/audit_service/store.py` (`_open_witness_check`, `witness_floor`, `_floor_violation`), `apps/web/web_bff/platform.py` (composition fails closed on `WitnessLostError`) | Backend Lead (build), SRE Lead (run) | A platform whose own records name an external witness that is absent or unreadable does not open: refuse, alert `audit.anchor_missing` S1 with `AUD-WITNESS-LOST`/`AUD-WITNESS-UNREADABLE` and the start-up correlation id, write nothing | TC-AUD-015 (positive), TC-AUD-016 (negative), TC-AUD-017 (abuse — Red-Team Case B), TC-AUD-018 (recovery) | `docs/TEST_CASES/TC-AUD.md`; probe 01 Case B before/after in §9 | D (dev/sim only) |
| NFR-AUD-01 | `services/audit/audit_service/store.py` (`_publish`, `seal`, `_verify_published`), `services/audit/audit_service/reestablish.py` | Backend Lead (build), SRE Lead (run) | No publication witnesses a chain that contradicts a head this store recorded witnessing (`AUD-SEAL-BELOW-FLOOR`, S1 `audit.chain_verification_failed`); an ordinary seal cannot establish a first anchor (`AUD-SEAL-UNWITNESSED`); re-establishment is an attested, audited act | TC-AUD-019 (positive), TC-AUD-020 (negative), TC-AUD-021 (abuse — Red-Team Case C), TC-AUD-022 (recovery) | `docs/TEST_CASES/TC-AUD.md`; probe 01 Case C before/after in §9 | D (dev/sim only) |
| FR-16 (audit explorer, unchanged) | `apps/web/web_bff/app.py` | Frontend/Backend Lead | `/v1/audit/verify` still reports the start-up verdict; no new endpoint and no new HTTP surface was added by this change | TC-AUD-010, TC-AUD-014 (unchanged, green) | `docs/TEST_CASES/TC-AUD.md` | D |

**Reason codes added** (audit-internal, not customer-facing, so not in the generated `docs/REASON_CODES.md`, which covers `RK-`/`CP-`/`RT-` families): `AUD-WITNESS-LOST`, `AUD-WITNESS-UNREADABLE`, `AUD-SEAL-BELOW-FLOOR`, `AUD-SEAL-UNWITNESSED`, `AUD-WITNESS-PRESENT`, `AUD-ATTESTATION-MISMATCH`. If the Compliance Agent wants them in a dictionary, they belong beside the existing `AUD-CHAIN-*`/`AUD-ANCHOR-*` codes, wherever those are finally published.

---

## 5. Threat-model delta [Committee] — proposed to the Security Architect; **ids are his**

| Proposed row | Asset / boundary | Adversary | Before (measured `48650ed`) | After (measured, this branch) | Residual |
|---|---|---|---|---|---|
| **"Deleting the witness is a better attack than editing the chain"** | Audit chain + anchor replica, boundary B10 (host file write) | Actor who can stop the process and write host files | Platform started with no witness; an intent ran to FILLED; one order reached the broker; S1 with `auto_action: none` | Platform does not open (`WitnessLostError`); no intent, no order; S1 delivered on pager+email; nothing written to the store | An actor who rewrites the **whole** chain from genesis (O-110's attacker) and deletes the witness leaves no evidence a witness existed → opens. An actor who deletes **both** stores gets a clean slate (probe 05, unchanged) |
| **"The recovery destroys the evidence it protects"** | The operator's own remediation | Operator under pressure, or an actor impersonating one | A plain seal re-anchored a truncated chain; "witnessed as if it had never happened" | Refused: `AUD-SEAL-UNWITNESSED` for the ordinary seal, `AUD-SEAL-BELOW-FLOOR` when the chain contradicts our own record — including for **automatic** publications | The attested act is available to an actor who owns both stores. What it costs them is a permanent `audit.witness.reestablished` row naming an actor and a reason (pinned by TC-AUD-021) |
| **"The witness that agrees because it was trimmed to agree"** (new, found while building) | Anchor replica tail | Same actor, more careful | Not previously modelled: trimming the anchor tail to match a truncated chain would have been re-anchored by the **next scheduled publication**, with no operator involved | Start-up verification returns `AUD-SEAL-BELOW-FLOOR`, the catalogued auto-action halts the platform, and no publication is made | Depends on a surviving seal record or mark; an attacker who removes both and trims the witness is back to the "full forge" residual above |

---

## 6. Text I propose for documents I do not own (I did not edit them, and did not route around the write-scope guard)

**For the SRE Lead, `docs/RUNBOOKS.md` RB-13 (or a new RB):**
> *Audit witness lost (`AUD-WITNESS-LOST` / `AUD-WITNESS-UNREADABLE`, S1 `audit.anchor_missing`, auto-action none).* The platform will not start. The chain itself may be perfectly intact — what is missing is the witness. **Do not** delete or overwrite the anchor store, and do not seal: an ordinary seal is refused, and it would be the wrong thing to do if it were not. In order: (1) treat the two stores as evidence and take a copy of both as found; (2) restore the anchor replica from the last good copy and restart — this is the normal fix and it is TC-AUD-009/014; (3) only when no copy exists, run the attested re-establishment (`audit_service.reestablish`), which requires a named human, a reason, and the exact length, head hash and last anchor sequence read from the store, and which writes a permanent row saying it happened.

**For the Cloud Architect, `docs/CAPACITY_MODEL.md` / availability:**
> The anchor store is now a **start-up dependency** of the platform, of the same rank as the control store: if it is unreachable or empty when a platform that has been witnessed starts, the platform refuses to start. This is deliberate (ADR-020 amendment 3). Its availability target and its restore-time objective must be set with, not below, the control store's, and the DR runbook's ordered restore (DR_PLAN D-01) now applies to it as a prerequisite rather than an improvement.

---

## 7. Proposed RAID rows — **not written by me**; ids are the Program Orchestrator's

| Kind | Proposed text | Owner | Why now |
|---|---|---|---|
| **R-a (risk)** | An attacker who rewrites the entire audit chain from genesis *and* deletes the witness leaves a store with no evidence it was ever witnessed, and it opens. The only structural answer is a witness the audit process cannot write or delete (a WORM object lock or a replica written by a separate principal) — H-21/O-54 — or a second store that records the audit chain's length (the control store, the reverse direction of D-061 (5)). | Security Architect / Backend Lead | Named by amendment 3 as what it does not close |
| **R-b (risk)** | The attested re-establishment is, by construction, a laundering path for an actor who owns both stores. Recommend **two-person control** on the act (a second named human, as for Kill Switch deactivation, O-19) before shadow. | Product Owner / Security Architect | The control the Product Owner asked to be "impossible by accident" is not, and does not claim to be, impossible on purpose |
| **R-c (risk)** | A witness-store outage is now a platform outage. Availability and DR targets for the anchor store must be set before any environment above sim. | Cloud Architect / SRE Lead | Consequence of the decision, stated in §6 |
| **O-d (open)** | The `audit.anchor.published` mark is written for genesis and scheduled publications only (an operator seal is recorded in the seals table). A store first given a publisher *after* it already had events has no mark and no seal, so it is treated as never witnessed. Decide whether adopting a witness for an existing chain must also be an attested act. | Backend Lead / Product Owner | Found while building; today the attested act is the only way to adopt one, which is the safe side, but it is not written down anywhere as a rule |
| **O-e (open)** | Chain growth: one extra row per `anchor_every` events plus one at birth. Belongs with the compaction/retention question O-111 and the cadence O-133. | SRE Lead | Consequence, small, but it is a real number |
| **Link to H-21 / O-54 / R-31** | This change makes the *absence* of the H-21 replica principal materially more expensive to exploit, and it does **not** deliver H-21, O-54 or O-30. Those stay open and I closed none of them. | Program Orchestrator | Instructed not to close them, and I did not |

---

## 8. Control quartet

Two behaviours, four cases each, plus the two probe scenarios run as the probe runs them.

| Behaviour | Quartet | Test ID | What it holds |
|---|---|---|---|
| Witness continuity | positive | **TC-AUD-015** | A witnessed platform opens, restarts and trades; the genesis publication is recorded as the first row of the chain with a correlation id; an operator seal is recorded as a `SealRecord` with its anchor sequence; a chain that was **never** witnessed still opens (genesis case); memory platforms unchanged |
| Witness continuity | negative | **TC-AUD-016** | Witness deleted, corrupt, or its directory removed → `WitnessLostError`; S1 `audit.anchor_missing` with `AUD-WITNESS-LOST`/`AUD-WITNESS-UNREADABLE`, `auto_action: none`, start-up correlation id, **delivered** on pager+email; the audit row count is identical before and after each refused attempt; a crash loop changes nothing |
| Witness continuity | abuse | **TC-AUD-017** | The Red-Team Lead's **Case B**, step for step as the probe runs it: no platform, no intent, no order. Plus the variant where the attacker also rolls the store back (0 seal rows survive — asserted) and is still refused, on the chain's publication mark |
| Witness continuity | recovery | **TC-AUD-018** | The ordinary seal is refused (`AUD-SEAL-UNWITNESSED`) and publishes nothing; the read-only inspection; five wrong attestations refused (`AUD-ATTESTATION-MISMATCH`), each publishing nothing; the named act writes one row under the operator's correlation id and the anchor covers that row; a repeat is refused (`AUD-WITNESS-PRESENT`); the platform opens again; `build_sim_platform` has no `attestation` parameter |
| Seal floor | positive | **TC-AUD-019** | Repeated seals on a growing chain publish as before; the floor rises with each; the floor is durable across a restart |
| Seal floor | negative | **TC-AUD-020** | Chain truncated **and** witness trimmed to agree: start-up verification returns `AUD-SEAL-BELOW-FLOOR`, the catalogued auto-action halts the platform, the operator's seal is refused with the same reason and the S1 is delivered, nothing is published and no `SealRecord` is written; the attested path is refused too |
| Seal floor | abuse | **TC-AUD-021** | The Red-Team Lead's **Case C**, step for step: the restart is refused, so the operator seal never happens and the anchor store stays empty. The residual is pinned: an actor who takes the attested path leaves a permanent row naming them, asserted after a restart |
| Seal floor | recovery | **TC-AUD-022** | A genuine replica loss (chain intact) is re-established; the platform opens, verifies and trades; the floor after the recovery is the re-established head, and a truncation below it is still refused a seal |

**Existing tests changed — both strengthened, neither weakened:**

* **TC-AUD-007** last two lines: was `p4 = build_sim_platform(...); assert p4.audit.latest_anchor() is None and not p4.audit.verify().ok  # a restart does not fabricate a fresh anchor`. Now `with pytest.raises(WitnessLostError): build_sim_platform(...)` plus the same "nothing fabricated an anchor" assertion on the publisher. The old line asserted that the platform **started** and that `verify()` said no; the new one asserts it does not start. Everything else in TC-AUD-007 is byte-for-byte as I found it.
* **TC-AUD-013**: the alert is now selected by reason (`[a for a in fired if a.payload["reason"] == sv.reason][-1]`) instead of `[-1]`, because the forged chain also contradicts the surviving seal record and the floor refuses the scheduled publication *earlier in the same start-up*. Every original assertion is kept and one is added (that the floor alert fired too). No assertion was dropped or loosened.

All other TC-AUD, TC-DUR, TC-E2E and TC-RC tests are untouched and green.

---

## 9. The seven probes, before and after

Run with `RT_ENV=sim python3 docs/PENTEST/probes/rt_probe_0N_*.py` at `48650ed` (before) and at `01b4575` (after). **I did not edit any probe.** After the change, probe 01 raises out of `build_sim_platform` in Case B, so its own `__main__` never reaches Case C; I ran Case B and Case C separately, through a throwaway driver that imports the probe unmodified, and both results are below.

| Probe | Before | After | Verdict |
|---|---|---|---|
| **00** test ids vs threat model | 88 threat rows, 79 cited ids, 13 ids absent from the test tree, 26 rows tagged [Open] | identical, unchanged | **unchanged** — this probe is a documentation gap, not an attack; the 13 absent ids are still absent |
| **01 Case A** truncate the chain, restart | platform started on the truncated chain; intent `HALTED`; **0 broker submissions**; kill switch `PLATFORM` | identical (`41` events instead of `39`, because of the publication marks); intent `HALTED`; **0 submissions**; kill switch `PLATFORM` | **still closed** (closed by the previous session) |
| **01 Case B** delete the witness, restart | *"the platform STARTED without a witness … final_state=FILLED, broker submissions=1"* | `WitnessLostError: AUD-WITNESS-LOST: this store recorded witnessing length 41 as anchor 3 (seal), and the anchor store holds no record: a platform that had a witness and no longer has one does not open (fail closed)` — the probe cannot reach its own next line | **closed** |
| **01 Case C** truncate + delete the witness + operator seal | *"after a plain operator seal: published anchor length=56, verify() ok=True … the truncation is now witnessed as if it had never happened"* | `WitnessLostError: AUD-WITNESS-LOST: this store recorded witnessing length 25 as anchor 2 (mark), and the anchor store holds no record … (fail closed)` — refused **on the chain mark**, because the rollback took the seal record; the operator seal never happens | **closed** |
| **02** control-store rows deleted out of band while running | in-memory reads go stale until the next open; **no alert**; the store is refused at the next open | identical, unchanged | **still open** — a running platform does not notice an out-of-band delete of a Kill Switch activation or a consumed-authorisation row until it is restarted. Not this change's subject |
| **03** consistent rewrite of the control store | refused at start-up: `STORE-JOURNAL-ROLLBACK … (fail closed)` | identical, unchanged | **still closed** |
| **04** tool-registry trust anchor | *"forged registry ACCEPTED: key_id=attacker-key-v1 … quota_per_minute=100000, masking=none"*; refused only when the trust set is present | identical, unchanged | **still open** — the shipped dev registry is a fixture whose signature key is not pinned by a trust set in the default path. **Not mine to fix** (MCP/registry owner); it is the most serious of the still-open probes |
| **05** clean slate (both stores emptied) | fresh platform starts, trades, `verify().ok=True`, no alerts | identical, unchanged | **still open** — nothing survives to remember that anything existed. This is exactly H-21/O-54: a witness the audit process cannot delete |
| **06** consumed grants visible through the seam | 1 consumed-authorisation row after one fill; a consistent rewrite that removes it re-opens the replay window | identical, unchanged | **still open** — same class as probe 03's residual |

**Plainly: after this change, of the seven probes, 01 Case B and 01 Case C are closed; 01 Case A and 03 remain closed; 02, 04, 05 and 06 still succeed** — none of them is what the Product Owner asked me to close, and none of them is in E11's write scope except 05, whose answer is H-21, which I must not close on my own.

---

## 10. Evidence

| Artefact | Path |
|---|---|
| Implementation | `services/audit/audit_service/store.py` (witness continuity, floor, marks, attested act), `services/audit/audit_service/reestablish.py` (new: read-only inspection + the named act), `services/audit/audit_service/__init__.py` |
| Tests | `test/quartets/test_tc_aud_audit.py` TC-AUD-015..022 (new), TC-AUD-007 and TC-AUD-013 (strengthened) |
| Generated evidence | `docs/TEST_CASES/TC-AUD.md` (22 records, quartet complete), `docs/TEST_CASES/EVIDENCE_REPORT.md` (217 records, 24/24 areas) |
| Decision record | `docs/ADRs/ADR-020.md` amendment 3 (**Proposed**; reviewer and approver pending) |
| This packet | `docs/SESSIONS/BUILD_E11_2026-09-08_witness_cases_b_c.md` |
| Gates run | `make all` green (lint, typecheck, schema drift, policy checks, agents-check, secret scan, 235 tests, evidence); `make security-scan` clean (bandit HIGH@MEDIUM+: none; pip-audit: no known vulnerabilities) |
| Commits | `1527937` tests red · `4823984` implementation · `01b4575` ADR + evidence, on `build/e11-witness-cases-b-c` from `48650ed` (not pushed) |

---

## 11. Concerns for the Product Owner

**What an attacker can still do after this change.**

1. **Forge the whole chain and delete the witness.** An actor with offline write access who rebuilds the audit chain from genesis — recomputing every event hash, exactly the O-110 attacker TC-AUD-013 already models — can omit the `audit.anchor.published` marks and the seal records. The store then has no evidence it was ever witnessed, so it is indistinguishable from a chain that never was, and it **opens**. Nothing inside a single file can prevent this: any evidence the attacker can read, the attacker can rewrite. Only a witness that the audit process cannot write or delete (H-21/O-54) or a *second* store that records the audit chain's length closes it. This is the most important thing in this packet.
2. **Delete both stores.** Probe 05 is untouched: with the audit store and the anchor store both gone, a fresh platform starts, trades and verifies clean. There is nothing left to be suspicious with.
3. **Take the attested path.** An actor who owns both stores can perform the re-establishment: type a name, type a reason, read the numbers out of the store they just truncated, and get a witness over it. The refusal chain makes them leave an indelible `audit.witness.reestablished` row naming an actor and a claim — I pinned that with a test rather than hiding it — but it is a deterrent and an audit trail, **not a control**. If you want it to be a control, it needs a second human (proposed RAID row R-b) and, ultimately, a witness store the platform's own principal cannot write.
4. **Trim rather than delete.** Cutting the witness's tail so the remainder agrees with a truncated chain is now caught by the floor and by `AUD-ANCHOR-TAIL-REMOVED` — but only while a seal record or a mark above the cut survives. An attacker who removes those and trims the witness is back at (1).
5. **Stop the alert leaving the host.** Unchanged and still true (SRE-R5): the alert router has no acknowledgement and no external delivery, so an actor who can reach the process still controls whether the page is seen. The refusal does not depend on the alert being delivered — the platform does not start either way — but your *knowing* about it does.

**What an operator can still do by mistake.**

1. **Cause an outage by unmounting a volume.** The anchor directory is now a start-up dependency. A witness store that is merely unreachable — an unmounted volume, a network replica down, a permissions change — stops a platform that would previously have started and paged. That is the decision working as intended, and it is a new way to be down. It needs to be in the runbook and in the availability targets (§6) before anything above sim.
2. **Reach for the re-establishment instead of the restore.** The right first move is almost always to restore the replica from the last good copy (TC-AUD-009/014). The attested act asks for a name, a reason and three numbers read out of the store, which is friction on purpose, but an operator at 3am with an outage and a runbook can still use it when a restore would have been correct — and it is irreversible: it makes the current chain the witnessed one for ever. A two-person rule would fix this and the outage-pressure case together.
3. **Adopt a witness for an old chain without meaning to.** A store that ran without an anchor directory and is later given one has no marks and no seals, so it is treated as never witnessed and opens; establishing its first witness then requires the attested act. That is the safe behaviour, but it is not written down as a rule anywhere yet (proposed open item O-d).
4. **Read `AUD-WITNESS-LOST` as "the chain was tampered with".** It is not. It says the *witness* is missing; the chain may be perfectly intact. The two have opposite recoveries and the alert text says so, but the runbook has to say it too.

**One thing I want to be explicit about**: I did not close O-30, O-54, R-31 or H-21, and this change does not deliver any of them. It makes the missing H-21 replica more expensive to exploit, which is not the same thing.

---

## 12. Assumptions, confidence and provenance

**Assumptions.** (a) The Product Owner's decision as given to me is the decision — I built the refusal and the floor and did not soften either [Committee]. (b) Where the decision's stated *mechanism* (seal records) did not survive its own attack, I kept the mechanism and added one that does, rather than reporting the gap and stopping; if that was the wrong call the fix is to remove the chain marks, and Case C re-opens [Committee, flagged here for the record]. (c) `FileAnchorPublisher` models the WORM/replica principal; it does not evidence it [Open: O-54, H-21]. (d) `docs/ALERT_CATALOG.md` is not mine to write, so I introduced no alert name; the two names used are already catalogued for these conditions.

**Confidence.** High that Cases B and C, as the probe performs them, now fail: measured, and pinned by tests that model the probe's steps. High that nothing existing regressed: 235/235 pass, 24/24 quartet areas, `make all` and `make security-scan` clean, and the two changed tests are quoted in §8 for the reviewer to judge. Medium on the operational consequences (§11 "by mistake"): they follow from the design, but they have not been drilled, and the drill is the SRE Lead's. Low — deliberately — on anything about deployment: the separate principal, the WORM medium and the anchor cadence remain [Open].

**Provenance.** [Source: 03 stack, 06 immutable logs; NFR-AUD-01; FR-16] · [Committee: Product Owner decision 2026-09-08; D-066; ADR-020 and amendments 1–2; `docs/PENTEST/probes/rt_probe_01_audit_witness.py` (Red-Team & Pen-Test Lead)] · [Open: O-54, H-21, O-110, O-111, O-128, O-133, R-31, O-30]. Everything measured in this packet was produced by the commands named in §2, §9 and §10, in dev/sim, on this branch.
