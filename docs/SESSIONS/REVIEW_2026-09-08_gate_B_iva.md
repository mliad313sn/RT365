# REVIEW 2026-09-08 — Gate B (Architecture): Independent Validation finding on the ARB and Security & Privacy Board packets

| Council | Date | Member | Line | Status |
|---|---|---|---|---|
| Gate B — Architecture (ARB and Security & Privacy Board advisory; Product Owner decides per D-039, delegate under D-040) | 2026-09-08 | Independent Validation Agent (AI) | 3rd | independent validation of COUNCIL_2026-09-08_gate_B_arb.md and COUNCIL_2026-09-08_gate_B_security_privacy.md; findings per item; no decision recorded |

> This is a 3rd-line finding, not a decision and not an approval of any artefact. I own none of the artefacts under review and edited only this file. The delegate asked for `docs/SESSIONS/COUNCIL_2026-09-08_gate_B_iva.md`; my roster scope at the validated commit is `docs/GATE_REPORTS/`, `docs/SESSIONS/REVIEW_`, `docs/RAID_LOG.md` [Verified: `.claude/agents/roster.json`], so the packet is written here through the guarded Write path rather than around the guard (see O-96 in §8). Passing Gate B authorises development and simulation only; nothing here implies any market, broker, data entitlement, regulatory status, price or return. Profit is an objective, never a promise [Source: 00]. Tags: [Verified] = re-read or executed by me at the commit in §0; [Source: NN] = blueprint section as transmitted by the repository artefacts; [Committee] = council reasoning; [Open] = not verifiable from the tree.

---

## 0. Provenance, tree state, independence

| Item | Value |
|---|---|
| Commits during this session | `e674364` (dirty: the two council packets, `scripts/check_scan_exceptions.py`, `security/scan_exceptions.yaml` untracked; ci.yml, Makefile, .gitignore, DECISION_LOG, MISSING_ACTIONS, PO_DECISION_QUEUE, RAID_LOG modified) → `25b0483` "Gate B councils: D-052..D-054 … recorded; SAST/SCA now gating …; IVA convened" → `1e8555e` "Builders may write every code root (policy paths stay 2nd-line); regenerate roster" [Verified: `git rev-parse HEAD` three times, `git log`, `git status --short`] |
| Commit of record for this finding | **`1e8555eb5e680250e890268e40acfcf34c2dad06`, working tree clean (`git status --short` → 0 lines)** before and after every check in §2. Checks first run at `e674364`+dirty tree gave identical results; only the `1e8555e` results are quoted [Verified] |
| Consequence | The tree moved three times while being validated (as it did for the ARB chair, §0 of its packet, and for me on 2026-09-07, IVA-18). Any decision recorded on these packets must cite a commit and its CI run (O-65); I could not observe CI from this environment (§4, O-98) |
| Independence | I authored none of ADR-004/009/010/011/015/016, CAPACITY_MODEL, DATA_FLOWS, THREAT_MODEL, ROADMAP, ci.yml, Makefile, the scan scripts or either council packet [Verified: file headers; `git log` authorship carries the delegate's session trailer]. **Limit:** this validation ran on the same machine and inside the same harness session as the authoring agents (HEAD's `Claude-Session` trailer is this session's) [Verified: `git log -1 --format=%B`]. The mandate "separate infrastructure" is not met; the only separate runner is GitHub CI, which I could not read. Recorded as O-100 |
| What I did not do | Did not edit any ledger, ADR, test or workflow; did not record a decision; did not run `make certify-broker` / `make evidence` (they rewrite docs/). `make security-scan` writes `security/scans/*.json`, which is git-ignored (`.gitignore` line 19), so the tree stayed clean [Verified] |
| Harness permission | A direct re-run of `RT_ENV=production … verify_tool_registry.py` and `RT_ENV=shadow …` was **blocked by the harness permission classifier**; the CI form (`--production` flag alone) ran; the other three configurations quoted by the Board are covered by TC-AI-010/011, which pass at `1e8555e` [Verified] |

---

## 1. Roles

| Role | Line | Contribution |
|---|---|---|
| Product Owner (human `mliad313sn`); delegate `product-owner` under D-040 | 1st | decides O-04, O-13, O-17; may amend D-052..D-054 |
| ARB chair | 2nd | packet COUNCIL_2026-09-08_gate_B_arb.md (O-04, O-13, O-17) |
| Security & Privacy Board chair | 2nd | packet COUNCIL_2026-09-08_gate_B_security_privacy.md (O-05, O-22, O-23, E-1/E-2) |
| Independent Validation Agent (this packet) | 3rd | evidence review; APPROVE / APPROVE WITH CONDITIONS / VETO per item; no artefact ownership |
| Owning roles for proposed edits | 1st/2nd | Program Orchestrator (ledgers, AEI), Security Architect (THREAT_MODEL), Enterprise/Data Architect (ADRs, CAPACITY_MODEL, DATA_FLOWS), Cloud Architect (ci.yml), MCP Security Agent (registry, roster), Delivery Orchestrator (roster generator) |

---

## 2. Checks run at `1e8555e` (verbatim)

```
$ git rev-parse HEAD
1e8555eb5e680250e890268e40acfcf34c2dad06
$ git status --short | wc -l
0

$ make lint agents-check policy-check secret-scan
ruff check .
All checks passed!
ruff format --check .
137 files already formatted
python3 scripts/generate_agents.py --check
OK: 67 agents in .claude/agents match goals/
python3 scripts/check_network_policies.py
OK: network policies satisfy plane invariants (TC-NET)
python3 scripts/verify_tool_registry.py
NOTE: registry is a sim FIXTURE (approvals pending); it embodies no approval and is refused outside dev/sim
OK: registry 0.1.0 (dev key), 6 tools, policies consistent
python3 scripts/secret_scan.py
OK secret scan: 549 files, no findings
EXIT=0

$ make security-scan
mkdir -p security/scans
python3 scripts/check_scan_exceptions.py
OK scan exceptions: 0 entries, none expired
python3 -m bandit -q -r libs services mcp connectors observability apps -x test -lll -ii -f json -o security/scans/bandit.json
python3 -m bandit -q -r libs services mcp connectors observability apps -x test -lll -ii
python3 -m pip_audit -r requirements.lock.txt -f json -o security/scans/pip-audit.json
No known vulnerabilities found
python3 -m pip_audit -r requirements.lock.txt
No known vulnerabilities found
EXIT=0

$ python3 scripts/check_scan_exceptions.py
OK scan exceptions: 0 entries, none expired
EXIT=0

$ RT_ENV=sim python3 -m pytest -q -p no:cacheprovider test/quartets/test_tc_ai_mcp.py test/quartets/test_tc_net_planes.py test/quartets/test_tc_agt_agent_guard.py test/quartets/test_tc_glo_global.py
.......................                                                  [100%]
EXIT=0
  (with -rA: PASSED=23 FAILED/ERROR=0 — 11 TC-AI, 4 TC-NET, 4 TC-AGT, 4 TC-GLO; the pytest summary line is suppressed
   by the evidence plugin, so the count is from the -rA PASSED lines)

$ RT_ENV=sim python3 -m pytest -q -p no:cacheprovider -rA        (full suite)
PASSED=171 FAILED/ERROR=0
  (one DeprecationWarning from starlette/testclient.py:53 "anyio.abc.BlockingPortal alias is deprecated" — O-89)

$ python3 scripts/verify_tool_registry.py --production            (exact ci.yml step)
FAIL: dev signing key / fixture registry refused for production: no RT_MCP_REGISTRY_KEY configured and RT_ENV='production' is not a dev/sim environment; refusing the dev key
exit=1
```

**Reproductions of factual claims in the packets (scratchpad only, `RT_ENV=sim`, `build_sim_platform()`) [Verified]:**

| Claim | Packet | Result |
|---|---|---|
| Sim `MarketSnapshot` for `SIMEQ1`: 14 fields, 639 bytes JSON, 31 seeded rows | ARB §2, §4.3 | 14 fields, 639 bytes, 31 rows — **reproduced exactly** |
| `BitemporalStore` 63 lines, 7-method interface | ARB §4.2 | 63 lines; `put, latest, series, market_timestamps, count, next_after, snapshot_id_for_range` — reproduced |
| `apps/web/web_bff/app.py` 421 lines, 23 route decorators; no `fastapi`/`starlette` under `services/`, `libs/`, `mcp/`, `connectors/` | ARB §3.2 | 421 lines, 23 decorators; grep → none — reproduced |
| No test asserts the engine import ban (TC-ARC-001 absent) | ARB C-04-3 | `grep -rl TC-ARC-001 test/` → 0 files — confirmed |
| compose names `postgres:16` and `redpandadata/redpanda:v24.1.1`; no Kubernetes storage manifest | ARB §4.2 | confirmed (infra/kubernetes = namespaces.yaml + 5 network policies) |
| Verifier accepts any `algorithm` string when the HMAC matches (R-50) | S&P §2.1 | a registry re-signed with the dev key and `algorithm="NOT-AN-ALGORITHM"` **loaded** (`key_id dev-key-v0`) — confirmed, sim only, in-memory copy |
| `--production` refusal in four configurations | S&P §0.3 | CI form reproduced (exit 1); `RT_ENV=shadow` and `RT_ENV=production`+dev-key runs blocked by the harness permission; covered by TC-AI-010/011 passing |
| `requirements.lock.txt` has no hashes; CI installs `pip install -e ".[dev]" bandit pip-audit`, not from the lock; actions by major tag (`@v4`, `@v5`, `@v2`); release artefacts unsigned with `.sha256`; installers verify SHA-256 only; no cosign; `security/signing/README.md` describes a KMS target, not a state | S&P §3.1 | all confirmed at `1e8555e` (lock: 23 pins, 0 `sha256`; ci.yml, release.yml lines 14-15, 69, 82-93; install.sh line 16; install.ps1 lines 25-28) |
| `EgressPolicy` loaded but not called on any path (F-20) | S&P §1.1 | only construction site found: `apps/web/web_bff/platform.py:717`; no call site outside `mcp_servers/egress.py` found by grep — consistent with the claim (limits of grep noted) |
| `# nosec` / `--ignore-vuln` forbidden by a CI grep (C-23-2) | S&P §3.4 | **no such grep exists** in Makefile, ci.yml or scripts/ — the rule is stated, not enforced |
| The harness instructs agents to write files through Bash (R-46 is the default path) | S&P §4.1 | the same auto-mode instruction is in my own session prompt — confirmed |
| Threat-row test IDs that do not exist (IVA-12) | my 2026-09-07 report | still absent: TC-SEC-001, TC-PERF-004, TC-TEN-003, TC-SC-001/002, TC-NET-006 (0 files each) |
| Proposed artefacts on the tree | both packets | ABSENT: ADR-018, `mcp/policies/trust/`, `docs/TEST_CASES/TC-SC.md`, `security/signing/ceremonies/`, `scripts/check_authorship.py`, TC-AI-016..023, TC-MD-005..008, TC-ARC-001; PRESENT: `security/scan_exceptions.yaml` (0 entries), `scripts/check_scan_exceptions.py`, gating `security-scan` target (no `\|\| true` anywhere in ci.yml/Makefile) |

---

## 3. Decision-pack standard per item (question 1)

Standard applied: what the blueprint fixes and leaves open; ≥ 2 options with pros/cons/cost/risk/reversibility; recommendation with confidence and provenance; no invented numbers or vendor facts; human actions listed; author ≠ reviewer ≠ approver.

| Item | Blueprint fixed/open | Options (cost/risk/reversibility) | Recommendation + confidence | Invented numbers / vendor facts | Human actions | External assertions without evidence | Standard met? |
|---|---|---|---|---|---|---|---|
| O-04 (ARB §3) | yes, [Source: 03, 05, 16] with [Open] row | 3 (A/B/C), all columns filled | Option A, high/medium | none — the only numbers are code counts I reproduced; Option B/C speed claims tagged [Open] | §3.7 (none external) | none found | **Yes** |
| O-13 (ARB §4) | yes, [Source: 03, 06, 08] with [Open] row | 3 (A/B/C), all columns filled; dissent recorded (counsel-platform-reliability) | Option A, medium-high structure / none numbers | none — the 639 B / 31 rows measurement reproduced; every cost term [Open]; "bitemporal query is plain SQL" is a generic property, not a vendor claim | §4.7 table | none found; note the proposed threat row is numbered **T-25, which already exists** (intent-flood row) — ID collision, §5 | **Yes**, with the ID defect |
| O-17 (ARB §5) | yes, [Source: 00, 12, 14] with [Open] row | 3 (A/B/C), all columns filled | Option B + C mechanics, high form / none dates | none (no date proposed; "Gate A: 2 days" is a ledger fact I verified against D-048 and `git log`) | §5.7 | none; the ARB correctly limits its verdict to the in-scope part and defers the calendar to the Product Council | **Yes**; the recommendation **changes the D-003/D-042 sentence** "dates set once the Gate B capacity model exists" — the decision line must say it supersedes that sentence |
| O-05 (S&P §1) | yes, [Source: 00, 04, 06] | 4 (0/A/B/C), all columns filled; 3rd-line challenge recorded | Option B, medium-high posture / none vendor | none on providers, prices or regions; Q-05-1..14 are questions with the source to consult | §1.9 | **Soft assertions:** Q-05-3 names transfer instruments ("adequacy decision, standard contractual clauses, UK addendum/IDTA, Swiss addendum, Brazil LGPD transfer clauses") and Q-05-8 names countries "commonly cited" for localisation — both framed as examples/questions for counsel, not as applicable law; acceptable, but the DPIA must not inherit them as facts (condition on C-05-3) | **Yes**, with the note |
| O-22 (S&P §2) | yes, [Source: 04, 06]; D-008/ADR-011 cited | 3 (A/B/C), all columns filled; challenge recorded | Option B, high design / medium schedule | rotation 12 months / overlap 30 days labelled proposals; KMS algorithm support [Open: Q-22-1] | §2.8 | none; the R-50 weakness it names is real (reproduced §2) | **Yes** |
| O-23 (S&P §3) | yes, [Source: 06]; D-038/ADR-016 cited | 3 (A/B/C), all columns filled; challenge recorded | Option A, high gating / medium signing / none vendor | thresholds and CVSS mapping labelled policy proposals; Q-23-1..3 [Open] | §3.10 | none; the verified-state paragraph matches the tree | **Yes** |

Segregation (procedure step 1): both chairs state they authored none of the artefacts; I confirmed ADR authorship headers (D-006 for ADR-009; "Delivery Orchestrator (AI)" for ADR-015/016; MCP Security Agent presenting for ADR-011) [Verified]. Both packets record member positions as chair synthesis, not member packets — disclosed honestly; it weakens the "council heard" claim but does not breach the standard. The **Model Risk Lead / Model Risk Committee**, named decision owner of the O-05 pack and co-approving body in the queue, was not heard at all (S&P assumption A-1 defers it) [Verified: goals/decisions/O-05_decision_pack.md "Decision owner: Model Risk Lead, Privacy Lead"; PO_DECISION_QUEUE row O-05].

---

## 4. Findings (question 3)

### 4.1 D-052..D-054 already recorded — evidence-ground objections?

**No objection on evidence grounds to the substance of D-052, D-053 or D-054.** Each records a posture/design with the vendor facts, prices, keys and thresholds left [Open] or labelled proposals; the build items are recorded as open gaps (O-79..O-85), and my §2 reproduction contradicts none of the "verified state" statements the Board relied on. Nothing in the three decisions authorises an environment, a provider, a key or a claim that a control exists that does not.

Corrections the delegate should make (amend, not reverse):

| # | Decision | Defect [Verified] | Amendment |
|---|---|---|---|
| a | D-052 | Artefacts column contains the literal "this packet; PRIVACY_IMPACT …" copied from the draft — in a ledger "this packet" is ambiguous | replace with `COUNCIL_2026-09-08_gate_B_security_privacy.md §1` |
| b | D-052 | Council column names only the S&P Board; the queue names "Security & Privacy Board + Model Risk Committee" and the pack names the Model Risk Lead as decision owner; D-054 already carries "ARB view pending" for its joint item, D-052 does not | add "Model Risk Committee view pending (joint item, S&P A-1)"; MRC hears the evaluation-harness and champion/challenger aspects before any provider is wired |
| c | D-052 | C-05-3 (PRIVACY_IMPACT columns) must not import Q-05-3/Q-05-8 example instruments/countries as applicable law | note "transfer mechanism and localisation per cell are counsel answers (H-04), examples in Q-05 are not findings" |
| d | D-053 | RAID row O-22 title says "dev HMAC key retired"; D-053 keeps the dev HMAC key lawful in dev/sim (C-22-3 renames it) | RAID O-22 text aligned to D-053 |
| e | D-053 / D-054 / D-052 | RAID rows O-05, O-22, O-23 still read `Open` at `1e8555e` while the queue reads "Adopted (D-052/053/054)" | status → "Decided (D-05x) — build O-79/O-81/O-83 open" |
| f | D-054 | The decision text describes the target ("hash-pinned lock installed with --require-hashes; actions pinned by SHA; cosign …"); at `1e8555e` only bandit/pip-audit gating and the exceptions file exist (O-83 "Partial" is correct). CI comments already say "gating per D-054" | no change to the decision; **no gate evidence may call the SCA "gating" until C-23-4 lands** (R-52 below) |
| g | D-054 | C-23-2 second half ("inline suppressions forbidden … CI enforces it") is not enforced: no `# nosec`/`--ignore-vuln` grep exists | add to O-83 scope (R-53) |

### 4.2 O-04 — Service framework (ADR-009)

**Finding: APPROVE WITH CONDITIONS.** Evidence: FastAPI confined to one module; engines framework-free by grep; contract and schema-drift tests pass; 171/171 at `1e8555e`; ADR-009 has three alternatives with "why not"; author (Enterprise Architect, D-006) ≠ approver (ARB chair) ≠ decider (PO). The ARB's re-evaluation trigger is a measurement, not a date, which is the correct form under [Source: 12].
Conditions (mine; they subsume ARB C-04-1..4):
- **IVA-B-01** TC-ARC-001 (engine import ban) exists and passes before ADR-009 is marked Accepted — the "engines framework-free" property is currently a grep, not a test; a regression would be invisible to CI. Owner Backend Lead; before `gate-b` convening.
- **IVA-B-02** The decision line cites the **renumbered** RAID row (O-86, not O-77 as in the ARB draft §3.5/§3.6) [Verified: RAID O-86 = execution-plane host re-evaluation].
- **IVA-B-03** ADR-009 status flips only after D-05x is recorded and cites it; "Re-evaluation trigger" section names `order_ack_latency_ms` and `risk_decision_latency_ms_p99` with the budget [Open: O-03].

### 4.3 O-13 — Storage architecture and cost-model structure (ADR-004 rev.2)

**Finding: APPROVE WITH CONDITIONS** on the architecture direction and the cost-sheet *structure*; **nothing numeric is approved** (none is presented; the one measurement is a sim-fixture property I reproduced). The recommendation is consistent with ADR-007 (cell = failure domain), ADR-010 (adapters before Gate C), ADR-011/R-03 (look-ahead at the store) and NFR-GLO-01/F-7 (residency at storage) [Verified: those artefacts]. The dissent is recorded with a measured trigger — correct practice.
Conditions (subsume ARB C-13-1..6):
- **IVA-B-04** The new threat row is **not T-25** (taken by the intent-flood row). Allocate the next free IDs: T-52 = durable market-data store read bypassing knowledge time or tenant/region scope; the S&P Board's proposed provider-boundary row becomes T-53 with boundary B9. Owner Security Architect; before `gate-b`.
- **IVA-B-05** ADR-004 rev.2 exists as the artefact of record (Context, Decision, three alternatives, controls/tests, threat delta T-52) before `gate-b` convening; until then the Gate B exit criterion "ADRs" is not met for the store.
- **IVA-B-06** Decision line cites O-87 (numbers) and O-88 (TSDB trigger), not the ARB draft's O-78/O-79 [Verified: RAID renumbering].
- **IVA-B-07** CAPACITY_MODEL §Storage table carries the "how measured / source / status" column and the rule "a blank cell is [Open], never an estimate" verbatim; D-046 prices stay [Open] (C-13-5).

### 4.4 O-17 — Roadmap after the capacity model

**Finding: APPROVE WITH CONDITIONS** on the in-scope part (gate-driven form; calendar decoupled from capacity numbers; no calendar date for C–F). I verified the premise: no team size, budget, contract date or capacity number exists on the tree; a calendar now would be invented [Verified: CAPACITY_MODEL "No number in this document is set"; MISSING_ACTIONS H-01/H-05 Open]. Setting dates would create exactly the date pressure [Source: 12] prohibits.
Conditions (subsume ARB C-17-1..4):
- **IVA-B-08** The decision line states that it **supersedes the sentence in ROADMAP.md / D-003 (ratified D-042)** "Dates are set by Executive Steering once Gate B capacity model exists"; otherwise two ratified rules conflict.
- **IVA-B-09** Product Council endorsement (Product Director chair) is recorded in the Council column before D-05z is recorded — the ARB has no authority over the calendar and says so.
- **IVA-B-10** ROADMAP v1.1 row B lists the Gate B convening predecessors exactly as the §5 list below; the "what produces a date" column must never carry an estimate.

### 4.5 Agent guard, R-46, O-58 (S&P §4) — evidence check, no verdict requested

- TC-AGT-001..004 pass, including the `agent_type` payload case [Verified: test file lines 56-59].
- RAID O-58 "Closed 2026-09-08" cites **`SESSIONS/PROBE_O58`, which does not exist** in docs/SESSIONS (the only file mentioning `agent_type` is the S&P packet) [Verified]. The closure rests on a transcript that is not in the tree → by the gate rule it is an assertion, not evidence. O-95 below.
- The auto-mode harness instruction directs every agent to change files through Bash — I received it too. R-46 is therefore the default path, and the Board is right that TC-AGT must never be cited as segregation evidence. My own packet is written through the guarded Write tool for that reason.
- At `1e8555e` the roster was widened ("Builders may write every code root") [Verified: commit message and roster diff]; the S&P Board approved the roster at the previous shape (C-AGT-1). The MCP Security Agent should re-review the widened roster (O-97 part).

---

## 5. Gate B readiness (question 4)

Entry criterion: Gate A passed — **MET** (D-048 at `2edc87d`) with GA-C1..GA-C3 to be re-tested by the IVA before Gate B; O-66 (Q-11-1) and O-67 (AEI reviewer columns) still Open, O-68 Closed [Verified].

| Exit criterion [Source: 12] | Evidenced on `1e8555e` | Remaining | Status |
|---|---|---|---|
| Threat model | THREAT_MODEL.md T-01..T-51 with control/test/owner; TC-NET/TC-AI/TC-AGT/TC-PKG tests behind the boundary rows pass | S&P Board has **not** approved the document (its §5.3); AEI row 2 reviewer blank; six rows cite tests that do not exist (IVA-12 unchanged); T-52/T-53 to add | PARTIAL |
| Data flows | DATA_FLOWS.md DF-01..DF-09; DF-04/05/06 behaviours verified 2026-09-07 | DF-05 still "Idempotency, fencing token" — not updated for command authorisation (ADR-015, IVA-02 closure); DF-01/02 residency note (C-13); processor column for the AI-context flow (C-05-3); AEI 2b reviewer blank | PARTIAL |
| ADRs | ADR-001..017 present, each with ≥ 2 alternatives | **all 17 Proposed** [Verified]; ARB ratification of ADR-009 pending PO decision; ADR-004 rev.2, ADR-011 amendment, ADR-018 absent; ADR-015/016 reviewer "pending" | PARTIAL |
| Capacity model | skeleton (units of scale, partition keys, shed policy, SLI plan) | §Storage table (C-13-1); numbers [Open] by design — the Product Owner must record that Gate B accepts *structure with numbers [Open]* as the standard, or the criterion is unmet | PARTIAL |
| Control ownership (veto minimum) | RACI names a 2nd-line role for every critical control; CODEOWNERS protects the control paths | teams are placeholders (O-20); persons unappointed (H-01); the question "does *named owner* mean a person?" I raised on 2026-09-07 is still undecided (O-99) | MET at role level — **no veto ground today** |
| Registry signed (AEI 10), network invariants (AEI 11), SBOM (AEI 12) | `verify_tool_registry.py` OK and `--production` FAIL; `check_network_policies.py` OK; SBOM present | AEI reviewer/IVA columns blank; SBOM unsigned (D-054 build O-83) | MET dev/sim, unsigned |

**Ordered list before the `gate-b` convening** (owner; gate rule that makes it necessary):
1. Delegate records D-055..D-057 for O-04/O-13/O-17 with the RAID IDs mapped (O-86..O-91), the D-003 supersession (IVA-B-08) and the Product Council endorsement (IVA-B-09); amends D-052 (a–c) and the RAID status rows (d–e). — Program Orchestrator / delegate.
2. Owning-role artefact edits: ADR-009 Accepted + trigger section; ADR-004 rev.2; ADR-011 amendment; ADR-018; CAPACITY_MODEL §Storage; DATA_FLOWS DF-05/DF-01/DF-02/AI-context; THREAT_MODEL T-52, T-53 (no ID collision) with test IDs that will exist. — Enterprise/Data/Security Architects.
3. Tests-first build items the decisions made Gate B conditions: TC-ARC-001 (O-86/C-04-3); TC-AI-020..023 + algorithm allowlist + trust set (O-81, closes R-50); TC-SC-001..003 + install from the lock with hashes + SHA-pinned actions + `# nosec` grep + cosign/provenance (O-83, closes R-52/R-53); PRIVACY_IMPACT columns (O-80); ceremony template (O-82); `check_authorship.py` (O-85). — Backend Lead, Cloud Architect, Security Architect, Privacy Lead.
4. Board approvals of the *documents*: S&P Board on THREAT_MODEL and SECURITY_PLAN; ARB on DATA_FLOWS and CAPACITY_MODEL; AEI rows 2, 2b, 10, 11, 12 reviewer columns filled by 2nd-line roles; AEI rows for the two council packets, this finding and the first gated scan outputs (CI artifact, since `security/scans/` is git-ignored). — chairs, Program Orchestrator.
5. Evidence hygiene: O-58 probe transcript filed or O-58 reopened (O-95); GA-C1..GA-C3 re-test; CI run URL for the commit cited (O-65/O-98); MCP Security Agent re-review of the widened roster at `1e8555e`. — MCP Security Agent, IVA, Program Orchestrator.
6. Human acts that Gate B itself names: A-1 (Q-11-1), A-5 (seats, Finance owner of the cost sheet), A-6/H-05 (budget — or the PO records that quoted storage terms move to Gate C), H-24 (Windows evidence), H-27 (owner-authored merge, GA-C3). — Product Owner (human).
7. IVA re-validation at the final commit on the CI-evidenced tree → `gate-b` convening with the RELEASE_CHECKLIST row B evidence links.

**Would passing Gate B on dev/sim evidence risk a later veto ground?** Passing authorises only dev/sim, which already exist, so the authorisation itself is low-risk. The risk is in the *record*: if Gate B is passed while (i) the SCA is called "gating" although CI does not install the scanned lock (R-52), (ii) THREAT_MODEL/CAPACITY_MODEL are recorded as "approved" without board minutes, (iii) TC-AGT is cited as segregation evidence, or (iv) NetworkPolicies (IVA-11), in-memory durability (R-05) and the unanchored audit head (IVA-09) are not carried forward as explicit Gate C conditions — then Gate C inherits a false baseline and I would veto at Gate C on those grounds. Recording each as a carried condition with owner and re-review date (procedure step 4) removes that risk.

---

## 6. Control quartet coverage of the controls touched by the six items [Verified]

| Control | Positive | Negative | Abuse | Recovery | Gap |
|---|---|---|---|---|---|
| Signed registry, dev-key boundary (O-22) | TC-AI-005/010 | TC-AI-010 (wrong env), TC-AI-011 (dev key outside sim) | tampered field (TC-AI-005) | revocation restart (TC-AI-007/008) | **algorithm confusion, key_id substitution, trust-set swap, rotation overlap** — TC-AI-020..023 absent (R-50 reproduced) |
| Plane topology (O-04/O-13 residency reads) | TC-NET-001 | TC-NET-002 | TC-NET-003 | TC-NET-004 | cluster conformance [Open: H-05]; durable-store bypass TC-MD-007 absent |
| Agent write-scope guard (E-1/E-2) | TC-AGT-001 (incl. payload case) | TC-AGT-002 | TC-AGT-003 | TC-AGT-004 | Bash path uninspected by design (R-46); guard rail only |
| Global cells (D-050, residency input to O-13) | TC-GLO-001 | TC-GLO-002 | TC-GLO-003 | TC-GLO-004 | residency enforcement at storage (F-7) absent until the adapter |
| CI supply-chain gate (O-23) | `make security-scan` exit 0 on a clean tree | — | — | — | **TC-SC-001..003 absent**: no negative (injected HIGH / fixable CVE fails), no abuse (tampered hash, unpinned action, `--ignore-vuln`, fork-signed artefact), no recovery (exception with expiry); the exception checker has no test |
| Model provider boundary (O-05) | — | — | — | — | nothing exists (no LLM wired); TC-AI-016..019 absent — acceptable because no provider may be wired before them (C-05-1/2) |

---

## 7. Evidence list (mapped to docs/)

| Evidence | Location | Status |
|---|---|---|
| ARB packet | docs/SESSIONS/COUNCIL_2026-09-08_gate_B_arb.md (committed `25b0483`) | reviewed; §2 claims reproduced |
| S&P Board packet | docs/SESSIONS/COUNCIL_2026-09-08_gate_B_security_privacy.md (committed `25b0483`) | reviewed; §2 claims reproduced |
| Decisions D-040..D-054 | docs/DECISION_LOG.md lines 48-62 | read; amendments a–g proposed |
| RAID rows O-04/05/13/17/22/23/53/56/58/65/77..91, R-46/50/51 | docs/RAID_LOG.md | read; status defects noted |
| Gate B prompt, checklist row B, AEI rows 2/2b/10/11/12 | goals/gate_B_architecture.md; docs/RELEASE_CHECKLIST.md; docs/AUDIT_EVIDENCE_INDEX.md | read; reviewer columns blank |
| Prior IVA reports | docs/GATE_REPORTS/GATE_B_2026-09-07.md; REVALIDATION_2026-09-07_0cbc895.md | IVA-11/12/13/14 status re-checked: 12 and 13 unchanged; 14 partly closed (gating scanners), signing open |
| Command outputs and probes | §2 of this file; scratchpad script (not committed) | reproduced at `1e8555e` |
| CI run for `1e8555e` / `25b0483` | GitHub Actions | **[Open]** — `gh` not installed and no GitHub tool available to this agent; O-98 |

---

## 8. Proposed RAID rows and threat-model delta (question 5; the delegate integrates — IDs from O-92 / R-52 upward)

| ID | Type | Entry | Owner | Gate |
|---|---|---|---|---|
| O-92 | Issue | D-052 ledger hygiene: Artefacts column literal "this packet"; Model Risk Committee view not heard on a joint item; RAID O-05/O-22/O-23 status rows still `Open` after D-052..D-054 | Program Orchestrator / delegate | before D-055 |
| O-93 | Issue | Threat-model ID collision: ARB packet proposes "T-25" (exists: intent-flood) and the S&P packet "T-52"; allocate T-52 (durable store bypass) and T-53 (provider boundary B9) | Security Architect | B |
| O-94 | Issue | ARB draft decision lines and §3.6/§4.6 cite O-77..O-82, renumbered to O-86..O-91 in RAID; D-055..D-057 must cite the mapped IDs | delegate | before D-055 |
| O-95 | Issue | O-58 "Closed" cites `SESSIONS/PROBE_O58`, absent from the tree; file the probe transcript (hook payload with `agent_type`, denial exit 2) or reopen O-58 | MCP Security Agent | B |
| O-96 | Gap | IVA roster scope (`docs/GATE_REPORTS/`, `docs/SESSIONS/REVIEW_`, `docs/RAID_LOG.md`) excludes `docs/SESSIONS/COUNCIL_`; the Gate A IVA packet was written to a COUNCIL_ path (commit `cd7417e`, before enforcement) and this one to REVIEW_; decide the convention (recommended: IVA council findings are `REVIEW_`) and regenerate the roster/AEI references | Product Owner delegate, Delivery Orchestrator | B |
| O-97 | Gap | Gate B exit-evidence documents unapproved by their boards (THREAT_MODEL, SECURITY_PLAN, DATA_FLOWS, CAPACITY_MODEL); AEI rows 2/2b/10/11/12 reviewer columns blank; DF-05 not updated for ADR-015; roster widened at `1e8555e` after the Board's C-AGT-1 approval — re-review | chairs, Program Orchestrator, MCP Security Agent | B |
| O-98 | Dependency | CI evidence for the decision commit unverifiable from the agent environment (no `gh`, no GitHub tool); O-65 requires gate decisions to cite the CI-evidenced commit — the delegate attaches the run URL | Program Orchestrator | before D-055 |
| O-99 | Decision | Define "named 2nd-line owner" for the Gate B veto ground: role (met today) or person (H-01/O-20 open); raised 2026-09-07, still undecided | Product Owner | B |
| O-100 | Deviation | IVA validation ran on the same machine and harness session as the authoring agents (HEAD trailer); "separate infrastructure" unmet; GitHub CI is the only separate runner; Gate D backtest reproduction must be on separate infrastructure | Product Owner (accept for dev/sim or provide a runner) | B (record) / D |
| R-52 | Risk | The SCA gate scans `requirements.lock.txt` while CI installs from pyproject ranges without hashes; the gate proves the lock clean, not the tested closure; any gate evidence calling SCA "gating" before C-23-4 (install from the lock, `--require-hashes`) is an assertion | Cloud Architect | B |
| R-53 | Risk | `check_scan_exceptions.py` binds an exception to any existing D-nnn without checking the decision names the exception; no CI grep forbids `# nosec` / `--ignore-vuln` (C-23-2 stated, not enforced); the checker has no quartet | Security Architect | B |
| R-54 | Risk | The harness auto-mode instruction directs every agent to change files through Bash, making the R-46 bypass the default path; segregation of record must rest on authorship review (O-85) and CODEOWNERS/branch protection (O-20), never on TC-AGT | MCP Security Agent, Product Owner | B |
| R-55 | Risk | CI step "registry must NOT be deployable to production" asserts fixture refusal; H-20's exit ("`--production` passes") inverts its meaning once a ceremony key exists; TC-AI-020..023 must define both states so the assertion is not silently weakened | Backend Lead, MCP Security Agent | B / C |

**Threat-model delta (for the Security Architect):** T-52 durable market-data store read bypassing knowledge time or tenant/region scope (B4/B7; controls adapter-only access, DB roles per plane, row-level policy; tests TC-MD-005..008) — replaces the ARB's "T-25"; T-53 provider-side retention/training on masked context, region drift on failover, credential exposure via prompt or log (new boundary B9 gateway↔provider; tests TC-AI-016..019) — replaces the S&P "T-52"; T-10 (dependency compromise) control column gains "SCA on the installed closure (`--require-hashes`), not on a side file" with test TC-SC-001 abuse case; T-48 (agent guard) note "harness Bash instruction makes the bypass the default path; control of record = authorship check O-85".

---

## 9. Verdict summary

| Item | Finding | Conditions |
|---|---|---|
| D-052 (O-05) | no evidence-ground objection; amend (a), (b), (c) | MRC view recorded before any provider is wired |
| D-053 (O-22) | no evidence-ground objection; amend (d), (e); R-50 reproduced | TC-AI-020..023 with algorithm allowlist before Gate B sign-off (R-55 both states) |
| D-054 (O-23) | no evidence-ground objection; amend (e), (f), (g) | no "gating SCA" claim in gate evidence until C-23-4 (R-52); `# nosec` grep (R-53) |
| O-04 | **APPROVE WITH CONDITIONS** | IVA-B-01..03 |
| O-13 | **APPROVE WITH CONDITIONS** (structure only; no number) | IVA-B-04..07 |
| O-17 | **APPROVE WITH CONDITIONS** (in-scope part; no date) | IVA-B-08..10 |
| Gate B | not yet convenable as "exit evidence approved": four of five criteria PARTIAL on document approval, one MET at role level; **no veto ground under the stated minimum today** | ordered list §5 |

Confidence: high on every [Verified] row (reproduced at `1e8555e`); medium on the packets' member-position synthesis (not independently heard); none on CI state, vendor facts, prices, regulatory status (all [Open]). Nothing here is self-certified; nothing here is the Product Owner's decision.

## 10. Sign-off

| Role | Name | Line | Signature | Date |
|---|---|---|---|---|
| Author | Independent Validation Agent (AI) | 3rd | — (AI output; never self-certifies) | 2026-09-08 |
| Reviewer | pending (2nd-line chair) | | | |
| Decision | Product Owner (human) / delegate under D-040 | 1st | pending | |
