# COUNCIL_2026-09-08_gate_B_spb_docs — Security & Privacy Board: THREAT_MODEL and SECURITY_PLAN (O-106), O-110, O-118, O-120, O-121, O-123, T-60..T-68 and the write-scope guard state

| Council | Date | Member | Line | Status |
|---|---|---|---|---|
| Security & Privacy Board (advisory; convened on the Product Owner delegate's instruction under D-040/D-051 for RAID O-106) | 2026-09-08 | Board chair (`approve-security-privacy-board-chair`, generated from goals/approvers/A5_security_privacy_board_chair.md; AI) hearing security-architect (presenting), privacy-lead, mcp-security-agent, red-team-pentest-lead; counsel: counsel-ai-safety, counsel-platform-reliability; Independent Validation finding quoted from its own report | approver (independent chair, 2nd/3rd-line view) | recommendation; every decision pending with the Product Owner |

> This packet builds on COUNCIL_2026-09-08_gate_B_security_privacy.md (O-05, O-22, O-23, guard position C-AGT-1..4) and does not repeat it. It is a technical recommendation within the Board's delegated scope (threat-model acceptance, security plan, residual-risk recommendations, secrets and signing keys, agent roster and write-scope guard). It records no decision: the human Product Owner decides every gate and risk acceptance (D-039) and the AI delegate decides under D-040; this Board recommends. Nothing here promotes any environment beyond dev/sim [Source: 12]. No vendor capability, regulatory status or threshold is asserted; every such point is [Open]. Profit is an objective, never a promise [Source: 00].

## 0. Roles, scope, inputs, checks

### 0.1 Roles and segregation (procedure step 1) [Verified]
| Item under review | Author of record | Transcriber / last editor [Verified: `git log -- docs/THREAT_MODEL.md`] | Reviewer (header) | Approver recommended by | Distinct? |
|---|---|---|---|---|---|
| docs/THREAT_MODEL.md Draft v1.0 (T-01..T-68) | Security Architect (header) | T-14..T-37 Delivery Orchestrator (AI) per footnote; T-38..T-46 IVA remediation commits; T-47..T-50 f5baf2b; T-51..T-57 cd7417e/f22834d; T-58..T-59 724be37; T-60..T-63 d8cef0e; T-64..T-68 a90b1ae — all committed by the Product Owner delegate session | Red-Team & Pen-Test Lead (3rd line), pending | Board chair | yes for the chair; **author of record is ambiguous** (§1.3 F-TM-1) |
| docs/SECURITY_PLAN.md Draft v1.0 | Security Architect | last edited f5baf2b (ADR-016 rows) | MCP Security Agent (2nd line), pending | Board chair | yes |
| O-110, O-118 (D-058 b/e), O-120, O-121, O-123 (D-059) | build-e07 / build-e01 agents (packets), Product Owner delegate (decisions) | — | ARB / Trading Risk Committee / IVA pending | Board chair | yes |
| Guard state (R-46, R-54, O-58) | Delivery Orchestrator (generator), Product Owner delegate (probe, settings hook) | — | MCP Security Agent (2nd line) | Board chair | yes |

**Recusal.** [Verified] The chair's previous packet (§1.8) proposed the provider-boundary row that the delegate transcribed as **T-59** and proposed SECURITY_PLAN row text for the model-provider boundary and key ceremony. The chair therefore **recuses from recommending on T-59** and from the SECURITY_PLAN rows that would be derived from its own packet; for those the red-team-pentest-lead's and the IVA's positions are recorded as the Board's view (§1.6, §2.4). The chair authored, reviewed or specified nothing else in this packet [Verified: roster.json write scope of the chair is docs/SESSIONS/, RAID, AEI, PO_DECISION_QUEUE; only this file is written on the convener's instruction].

### 0.2 Scope [Committee]
In scope: the two documents as Gate B exit evidence (AEI row 2; row 2b only for DATA_FLOWS consistency, the ARB owns it); the delegate's security decisions of this week that name this Board (D-058 b and e → O-110, O-118; D-059 → O-120, O-121, O-123; threat rows T-60..T-68); the write-scope guard state (E-1). Out of scope: DATA_FLOWS/CAPACITY_MODEL acceptance (ARB), R-57 (Trading Risk Committee; the Board gives a view in §7), O-113 (TRC), the Postgres/Kafka topology (R-05, Cloud Architect).

### 0.3 Read [Verified: file reads 2026-09-08 in the worktree at a90b1ae, clean tree]
CLAUDE.md; GOAL.md; goals/approvers/A5_security_privacy_board_chair.md; goals/13_security_architect.md, 14_mcp_security_agent.md, 23_red_team_pentest_lead.md, 24_privacy_lead.md; docs/THREAT_MODEL.md (all 68 rows and the footnote); docs/SECURITY_PLAN.md; docs/PRIVACY_IMPACT.md; docs/DATA_FLOWS.md; docs/ADRs/ADR-015.md, ADR-016.md, ADR-018.md; docs/SESSIONS/COUNCIL_2026-09-08_gate_B_security_privacy.md (§0–§5); BUILD_E07_2026-09-08_durable_stores.md §1, §5, §10, §11; BUILD_E01_2026-09-08_tenant_isolation.md §1, §6, §10; PROBE_O58_2026-09-08.md; REVIEW_2026-09-08_gate_B_iva.md (independence row, IVA-B-04, readiness table, veto reasoning, proposed delta); docs/GATE_REPORTS/GATE_B_2026-09-07.md IVA-12; docs/RAID_LOG.md rows R-05, R-06, R-22, R-23, R-46, R-51, R-52, R-54, R-56, R-57, O-20, O-33, O-53, O-54, O-55, O-58, O-79..O-83, O-85, O-102, O-106, O-110, O-112..O-123; docs/DECISION_LOG.md D-039, D-040, D-051..D-054, D-058, D-059; docs/PO_DECISION_QUEUE.md (O-05/O-22/O-23 rows, PC-7, PC-E07-3/14/15, PC-E01-1/2/7, gate table); docs/AUDIT_EVIDENCE_INDEX.md rows 2, 2b, 10, 11, 12, 26, 37, 39; docs/AGENT_ROSTER.md; .claude/agents/roster.json; .claude/agents/approve-security-privacy-board-chair.md (frontmatter); .claude/settings.json; .github/CODEOWNERS; pyproject.toml protected-path comment; security/README.md; security/scan_exceptions.yaml; scripts/check_scan_exceptions.py; scripts/agent_guard.py; apps/cli/rt365_cli/agent_guard.py; libs/core/rtcore/store.py; services/audit/audit_service/store.py; mcp/servers/mcp_servers/revocation.py (append path), identity.py (nonce path); apps/web/web_bff/platform.py lines 129, 593–608, 771, 864–869; docs/MCP_TOOL_CATALOG.md §Servers; mcp/policies/README.md, runtime.yaml, egress.yaml; docs/RED_TEAM_PLAN.md; docs/ALERT_CATALOG.md rows `mcp.tenant_revoked`, `execution.store_unavailable`; docs/REQUIREMENTS_TRACEABILITY.md NFR-CON-01, NFR-SEC-01/02, NFR-AUD-01, NFR-TEN-01; docs/TEST_CASES/EVIDENCE_REPORT.md header, TC-DUR.md, TC-AGT.md; test/quartets/test_tc_dur_durability.py (TC-DUR-003 body), test_tc_agt_agent_guard.py (payload case).

### 0.4 Checks run (verbatim) [Verified 2026-09-08, worktree at a90b1ae]
```
$ RT_ENV=sim python3 scripts/verify_tool_registry.py
NOTE: registry is a sim FIXTURE (approvals pending); it embodies no approval and is refused outside dev/sim
OK: registry 0.1.0 (dev key), 6 tools, policies consistent
exit=0
$ python3 scripts/verify_tool_registry.py --production
FAIL: dev signing key / fixture registry refused for production: no RT_MCP_REGISTRY_KEY configured and RT_ENV='production' is not a dev/sim environment; refusing the dev key
exit=1
$ RT_ENV=shadow python3 scripts/verify_tool_registry.py
FAIL: no RT_MCP_REGISTRY_KEY configured and RT_ENV='shadow' is not a dev/sim environment; refusing the dev key
exit=1
$ python3 scripts/check_scan_exceptions.py
OK scan exceptions: 0 entries, none expired
exit=0
$ RT_ENV=sim make lint policy-check agents-check secret-scan
All checks passed!
141 files already formatted
OK: network policies satisfy plane invariants (TC-NET)
OK: registry 0.1.0 (dev key), 6 tools, policies consistent
OK: 67 agents in .claude/agents match goals/
OK secret scan: 563 files, no findings
exit=0
$ RT_ENV=sim python3 -m pytest test/quartets/test_tc_dur_durability.py test/quartets/test_tc_ten_tenancy.py test/quartets/test_tc_agt_agent_guard.py test/quartets/test_tc_ai_mcp.py test/quartets/test_tc_ai_stdio.py -p no:cacheprovider -o addopts="" -q
27 passed, 1 warning in 1.94s
$ RT_ENV=sim make test
203 passed, 2 warnings in 11.01s
exit=0
```
Test-ID existence check for every TC id cited in THREAT_MODEL.md (`grep -rl` over test/ and docs/TEST_CASES/) [Verified]: **absent** — TC-AI-016 (T-59, tagged [Open]), TC-ID-007 (T-15, [Open]), TC-ID-008 (T-18, [Open]), TC-MD-005 (T-58, [Open]), TC-NET-006 (T-21, [Open]), TC-PERF-004 (T-11 **untagged**; T-25 [Open]), TC-SC-001 (T-10 **untagged**), TC-SC-002 (T-04 **untagged**), TC-SEC-001 (T-05 **untagged**), TC-SEC-003 (T-22, [Open]), TC-SEC-MCP (T-35, [Open], non-standard id), TC-AI-020..023 (D-053, not yet cited). Every other cited id exists in the test tree, the TC documents and EVIDENCE_REPORT. The `--production` refusal required by the Board's evidence list holds [Verified]. `make all` was not run in full (typecheck, evidence regeneration and package targets are outside this review); the four gating targets and the full pytest suite were.

### 0.5 Method [Committee]
Discover (security-architect presents each document and each decision) → Challenge (privacy-lead, mcp-security-agent from the 2nd line; red-team-pentest-lead from the 3rd; counsel) → Validate (Independent Validation's written finding; the chair's own file reads and command runs). Members speak from the artefacts their role owns and from their prior packets; where a member has not written on a point the chair says so. Dissent is recorded verbatim in the member's words as heard.

---

## 1. docs/THREAT_MODEL.md — review

### 1.1 Presentation (security-architect, 1st line) [Committee]
"Sixty-eight rows over eight declared boundaries. Every row names a control, a test id and an owner. Fifty-six rows cite tests that exist and pass in the 203-test suite; twelve cite tests tagged [Open]. The rows added this week, T-47..T-68, transcribe the ADR-016, E06, E07 and E01 packets; T-60..T-63 carry the durable-store quartet (TC-DUR-001..004, TC-EX-011, TC-KS-010) and T-64..T-68 the tenant quartet (TC-TEN-001..004). The document is a dev/sim baseline: it claims nothing about a deployed topology." [Verified: the counts match §0.4 except that four untagged rows cite tests that do not exist — the presenter's "every row names a test id" is true, "cite tests that exist" is not for T-04, T-05, T-10, T-11.]

### 1.2 Completeness against the boundaries of DATA_FLOWS [Verified; Committee]
| DATA_FLOWS flow | Boundary in THREAT_MODEL | Rows | Gap |
|---|---|---|---|
| DF-01 Provider → Market Data | B7 | T-03, T-11, T-58 | Entitlement/licence leakage (DF-01 "entitlement check", DF-02 "masking of unlicensed fields") has no threat row; T-03 is poisoning, T-13 is generic exfiltration |
| DF-02 Market Data → Strategy/AI; DF-03 Portfolio → AI | B3 | T-01, T-02, T-28, T-54, T-55 | covered |
| DF-04 AI → Intent queue | B3/B6 | T-02, T-31, T-43, T-47 | covered |
| DF-05 Control → Execution | B4 | T-08, T-09, T-26, T-38, T-39, T-45, T-46, T-60, T-63 | DATA_FLOWS DF-05 still reads "Idempotency, fencing token" and omits the command authorisation MAC and the permission oracle (ADR-015) — a DATA_FLOWS defect (IVA REVIEW_2026-09-08 readiness table), owner Data Architect, not a THREAT_MODEL defect |
| DF-06 Execution ↔ Broker | B5 | T-05, T-21, T-27, T-44, T-62 | covered |
| DF-07 All → Audit | "all" | T-12, T-16 | durable control state without a durable audit trail (BUILD_E07 C-10, B-5) has no row; tenant `-` platform rows invisible to tenant auditors (O-121) has no row |
| DF-08 Users ↔ BFF | B1, B2 | T-06, T-07, T-14, T-15, T-17, T-22, T-23, T-24, T-25, T-33, T-36, T-41, T-56, T-64 | covered; platform-operator path (O-120) has no row |
| DF-09 Platform → Regulatory adapters | **no boundary** | none (T-19 concerns the jurisdiction flag, not the adapter) | a forged, replayed or unauthorised regulatory report has no boundary and no row |
| (not in DATA_FLOWS) model gateway ↔ provider | **B9 used by T-59 but not declared** in the boundary list | T-59 | declare B9 in DATA_FLOWS (DF-new) and in the boundary list |
| (not in DATA_FLOWS) host/OS ↔ store and journal files | **"B4 (host)" in T-61, undeclared** | T-61, T-62, T-63 | declare a host boundary (control-store file, revocation and nonce JSONL, audit JSONL) in both documents |
| (not in DATA_FLOWS) CI/agent harness ↔ repository | B8 | T-04, T-10, T-29, T-42, T-48, T-49, T-50 | covered; T-48 must state the Bash limit and the roster widening (§3.7) |

Conclusion: the eight declared boundaries cover DF-01..DF-08; DF-09, the provider boundary (B9) and the host/file boundary are used or implied but not declared. Boundary declaration is a condition (TM-C1).

### 1.3 Row-by-row findings [Verified unless tagged]
**F-TM-1 Author of record.** The header names the Security Architect as owner; the footnote says the T-14..T-37 delta was "compiled by the Delivery Orchestrator (AI); reviewer: pending; approver: pending" and says nothing about T-38..T-68, all transcribed and committed by the Product Owner delegate session (§0.1). The same delegate decides acceptance under D-040. Author of record, transcriber and decider must be distinguishable in the document before the reviewer signs (TM-C2).

**F-TM-2 Rows claiming a control or a test that is not evidenced, without an [Open] tag:**
| Row | Claim | Fact | Required change |
|---|---|---|---|
| T-04 | "Signed model artefacts, registry, SBOM" / TC-SC-002 | TC-SC-002 does not exist; no model artefact signing exists (MODEL_CARDS/rule-sma is a fixture); SBOM exists unsigned | test → "[Open: O-83 TC-SC-002]"; control → "SBOM (delivered, unsigned); artefact signing [Open: D-054/O-83]; model artefact signing [Open]" |
| T-05 | "Vault/HSM, workload identity, rotation" / TC-SEC-001 | TC-SEC-001 does not exist; no vault/HSM (H-20, O-53); `VaultRef` is a type; secret scan exists (`scripts/secret_scan.py`) | test → "secret scan (CI); TC-SEC-001 [Open]"; control → "interim: no secret literal in tree (secret scan), `VaultRef` indirection, `secrets_mount: none`; target: vault/HSM [Open: H-20]" |
| T-06 | "MFA/passkeys, session controls" / TC-ID-003 | R-06 records hard-coded `mfa_enrolled=True` and `privileged_until=+1y`; TC-ID-003 exists but exercises the primitive, not an IdP | control → "interim (R-06); target IdP/OIDC" as T-14 already does |
| T-07 | "PIM, maker-checker, immutable logs" / TC-ID-004 | PIM window is hard-coded (R-06); immutable logs are in-memory/JSONL (O-54) | same interim/target split |
| T-10 | "SCA, signed images, SBOM" / TC-SC-001 | TC-SC-001 does not exist; pip-audit gating delivered on the installed lock (O-83 partial, R-52 remediated); no images built, none signed | test → "CI `sca-gate` (delivered); TC-SC-001 [Open: O-83]"; control → add "SCA on the installed closure (`--require-hashes` [Open])" per the IVA delta |
| T-11 | "WAF/DDoS, backpressure" / TC-PERF-004 | TC-PERF-004 does not exist; no WAF exists (H-05 infrastructure) | tag [Open]; owner unchanged |
| T-12 | "WORM, hash chain, restricted delete (none)" / TC-AUD-003 | no WORM; hash chain and sealed head exist (TC-AUD-001..005); off-box anchor [Open: O-54]; audit store in memory/JSONL (B-5) | control → "hash chain + sealed head (delivered); WORM and off-box anchor [Open: O-54, B-5]" |
| T-37 | "fallback test without a TC id [Open]" | honest, but a row without a test id cannot be indexed | allocate the TC id or keep [Open] with a RAID reference |
| T-68 | control column reads "Not mitigated by design" / test TC-TEN-003 | the column holds a design decision, not a control; TC-TEN-003 evidences the deactivation refusal only, not the blast radius | rewrite as §4.1 proposes (accepted risk R-57 with the compensating control and the missing test tagged [Open]) |

**F-TM-3 Test columns that are stale (tests now exist or ids changed meaning):**
- T-14 cites "TC-ID-005/006 [Open]" — both exist and pass [Verified]; keep the interim/target wording, drop [Open] on the ids.
- T-19 cites "TC-CP-007 [Open]" — exists and passes (dual-key fix, AEI row 31) [Verified].
- T-23 cites "TC-CP-008 [Open]" for hold release; T-52 and T-53 cite TC-CP-008 as the delivered legal-record test. One id, two meanings: the hold-release test needs its own id (TM-C4).
- T-35 cites "TC-SEC-MCP [Open]" — not a valid id form; allocate.
- T-17 and T-13 were updated for E01 [Verified]; correct.

**F-TM-4 Wrong or undeclared boundaries:**
- T-19 (jurisdiction flag disabled by an agent) is B2 (BFF↔services), not B7 (provider↔ingest).
- T-42 (environment label, dev key via environment variable) is B8 (CI↔production), not "B1/B5".
- T-43 (tool-call replay after issuer restart) is B6/B3, not B5.
- T-59 uses B9, which the boundary list does not declare (chair recused on the row itself; the boundary declaration is a document-level condition).
- T-61 "B4 (host)", T-62 "B5", T-63 "B4": the store file and the journals sit on a host boundary that the list does not declare.

**F-TM-5 Cross-reference defects:**
- ADR-018 §Threat-model delta names "T-52 (state loss), T-53 (offline edit), T-54 (store unavailable)"; in THREAT_MODEL those are T-60, T-61, T-62 and T-52..T-54 are the legal-record rows [Verified: ADR-018 line 39]. The ADR must be corrected by its owner (Enterprise Architect / build-e07) — an AEI reader following the ADR lands on the wrong threats.
- T-61 tags "[Open: O-110]"; RAID types O-110 as "Risk" under an O- id. Cosmetic; the delegate should align the type or the id.
- The footnote covers T-14..T-37 only; provenance of T-38..T-68 (which packet, which reviewer) is absent.

### 1.4 Duplicate or contradictory rows [Committee]
Families that overlap without cross-reference (not contradictions; each names a different layer, so the Board asks for a "see also" rather than a merge): replay — T-08 (intent), T-31 (tool call), T-43 (after issuer restart), T-45 (authorised command); duplicate orders — T-09, T-26, T-27; cap evasion by splitting — T-34 (exposure) and T-40 (position: "committed position = positions + open orders") — these two are close enough that a reader may treat one as closing the other; audit tampering — T-12 (generic, owner SRE Lead) and T-16 (specific, owner SRE Lead / Security Architect); cross-tenant — T-17 (reads) and T-64 (forged header); excessive agency — T-02 and T-28; provider credential — T-05 and T-59.
Contradictions: (i) T-23 vs T-52/T-53 on TC-CP-008 (F-TM-3); (ii) T-12 "restricted delete (none)" alongside T-16's admission that the in-process list can be mutated — T-12 overstates; (iii) the footnote "Each row carries the control quartet in TEST_CASES/" is false for the twelve rows whose tests do not exist and for T-68 whose test evidences a different property.

### 1.5 Missing threats (which) [Committee; Verified where a file is cited]
| # | Missing threat | Boundary | Evidence that it is real | Proposed row in §4.1 |
|---|---|---|---|---|
| M-1 | Revocation and nonce journals are plain append-only JSONL with no digest or chain: deleting a line un-revokes a tool/identity/tenant grant or re-enables a replayed nonce | host / B6 | `mcp_servers/revocation.py` opens the file in append mode and validates records only [Verified]; `identity.py` nonce journal likewise; neither is behind `rtcore.store` (O-55) | row A |
| M-2 | Restore of the control store from a backup without the matching revocation/nonce journals (or vice versa) re-opens consumed grants and revoked identities — restore is a replay | host / B4 | the co-location rationale of D-058 e / O-118 is exactly this failure; no row names it | row B |
| M-3 | Platform-wide human actions reach the service/CLI path without an IdP-bound human principal (no platform-operator on the BFF, R-56) | B1/B2 | BUILD_E01 C-2; O-120 "decided as an IdP claim, design owed" | row C |
| M-4 | Platform-auditor unfiltered read used as a cross-tenant exfiltration channel or an unmapped cross-region transfer | B2 | O-121 decided "yes, design owed"; PRIVACY_IMPACT has no row for it | row D |
| M-5 | A pending first-person Kill Switch deactivation now persists indefinitely; a second hand completes it long after the context changed (no TTL) | B2/B4 | BUILD_E07 C-9; R-23 "pending-deactivation TTL prioritised" | row E |
| M-6 | A stuck or malicious writer holding the store lock makes every gateway submit/cancel fail closed (`busy_timeout` 5 s then StoreError): a denial of the Execution plane's cancel path | host / B4 | `SqliteStore` busy timeout [Verified]; O-117 | row F |
| M-7 | Control state survives a restart while the audit trail of how it got there does not (audit store in memory / JSONL): state without provenance | DF-07 | BUILD_E07 C-10; B-5 | row G |
| M-8 | The delivery-agent guard is editable by its subjects: every build agent's roster entry includes `scripts/` and `apps/`, where both guard modules live; build-e13 includes `security/` | B8 | roster.json at 1e8555e [Verified, §3.7] | extend T-48 |
| M-9 | The command-authorisation key is supplied to the composition root at start-up (`authorisation_key`) and could leak through process environment or logs | B4 | platform.py line 771 [Verified]; O-53 | extend T-39 |
| M-10 | Forged, replayed or unauthorised regulatory report through DF-09 | new boundary | DATA_FLOWS DF-09 "dual-key enabled" has no threat row | row H |
| M-11 | Second-tenant fixture (`second_tenant=True`) loaded in a non-test build | B8 | O-123; whether the flag is refused outside dev/sim was not verified by the chair [Open] | RAID row, not a threat row until verified |
| M-12 | Licensed data leaves the entitlement boundary (unlicensed field reaches an AI context or an export) | B7/B3 | DF-01/DF-02 controls named; no row | row I |

### 1.6 Challenges heard, validation, dissent [Committee]
- **privacy-lead (2nd line):** "T-24 still says TC-OB-002 'not yet extended'; the redaction of ids, IBAN and IP is delivered but structured field-level redaction is not (R-35). I object to T-68's control column and to any platform-auditor path (O-121) being built before its row exists here and in PRIVACY_IMPACT: an unfiltered read is a cross-tenant disclosure by design and, for a tenant in another region, a transfer. I also want M-12 as a row because DF-01's 'entitlement check' is a control the threat model never tests." Accepted (rows D and I; TM-C6).
- **mcp-security-agent (2nd line):** "T-47 is right; T-48 is not — it says 'PreToolUse write guard' as if it inspected writes. The roster was widened at 1e8555e after the Board's C-AGT-1 approval so that fifteen build agents may edit `scripts/` and `apps/`, where the guard lives. T-48's control column must say: Edit/Write only; Bash uninspected; guard code inside the builders' scope; CODEOWNERS placeholders. Otherwise the row certifies a control that its own subjects can remove. And M-1: the revocation journal is the emergency-revocation record of `runtime.yaml`; with no digest, a deleted line is a silent un-revocation. That row is mine to own." Accepted (row A; T-48 rewrite; §3.7).
- **red-team-pentest-lead (3rd line, reviewer of record for this document):** "I have not reviewed T-38..T-68; my signature is pending on the header. Two things before I sign: first, IVA-12 from 2026-09-07 named T-04, T-05, T-10, T-11 as citing tests that do not exist and they still do; second, TC-DUR-003 edits a row, deletes a row and deletes journal lines — it never attempts the consistent rewrite that T-61 admits is undetectable, so T-61's test column proves the easy half. RT-05 (audit tamper) will attempt the consistent rewrite of both store and journal; until then T-61 must say 'TC-DUR-003 (inconsistent edits only)'. **Different-line challenge:** why accept the document at all at Gate B when four rows are unevidenced? Because Gate B authorises dev/sim, which the document describes honestly once the [Open] tags are put where the tests are missing; refusing the whole document would not create a single test." Accepted as conditions TM-C3 and TM-C5.
- **counsel-ai-safety:** "T-01/T-02/T-28 stand; T-59 must not be recommended by the chair who drafted it." Recorded (recusal §0.1).
- **counsel-platform-reliability:** "M-6 and M-7 are reliability threats with a security face: a fail-closed gateway with no cancel path is a position that cannot be flattened. Both need rows and a chaos case (O-117)." Accepted (rows F, G).
- **Independent Validation (3rd line), quoted:** "S&P Board has **not** approved the document (its §5.3); AEI row 2 reviewer blank; six rows cite tests that do not exist (IVA-12 unchanged); T-52/T-53 to add" [Source: REVIEW_2026-09-08_gate_B_iva readiness table]; and on the record risk: "if Gate B is passed while … THREAT_MODEL/CAPACITY_MODEL are recorded as 'approved' without board minutes, … TC-AGT is cited as segregation evidence" [Source: same, veto reasoning]. The ID collision the IVA raised is closed as T-58/T-59 (O-102) [Verified]; the ADR-018 cross-reference is not (F-TM-5).
- **Dissent:** none on the verdict. One recorded reservation, red-team-pentest-lead, verbatim: "Accepting with conditions is right only if the conditions are applied *before* my signature goes on the header, not after Gate B is recorded."

### 1.7 Recommendation on docs/THREAT_MODEL.md
**RECOMMEND ACCEPT WITH CONDITIONS** as the Gate B dev/sim baseline (v1.1), the conditions to be applied by the Security Architect and signed by the Red-Team & Pen-Test Lead before AEI row 2's reviewer column is filled:

| Condition | Row(s) changed | Exact change |
|---|---|---|
| TM-C1 Boundaries declared | "Trust boundaries" line | add B9 model gateway↔provider; a host/OS↔store-and-journal-files boundary; a platform↔regulatory-adapter boundary (ids allocated by the owner, mirrored in DATA_FLOWS by the Data Architect) |
| TM-C2 Author of record | header + footnote | header gains "Author of record: Security Architect; rows transcribed from build/council packets by the Product Owner delegate (T-38..T-68), reviewer pending"; footnote lists the packet of origin per row range |
| TM-C3 [Open] where no test exists | T-04, T-05, T-10, T-11, T-37 | test columns tagged [Open] with the RAID reference (O-83 for TC-SC-*, new gap rows for TC-SEC-001 and TC-PERF-004); control columns split interim/target per §1.3 F-TM-2 |
| TM-C4 Interim/target split and stale ids | T-06, T-07, T-12, T-14, T-19, T-23, T-35 | as §1.3 F-TM-2/F-TM-3; T-23's hold-release test gets its own id; T-35's id made valid |
| TM-C5 T-61 honesty | T-61 | test column "TC-DUR-003 (edit, delete, journal drop; consistent rewrite not attempted — RT-05 [Open])"; control column ends "[Open: O-110 — Board recommendation §3.1]" |
| TM-C6 T-68 rewrite | T-68 | control column per §4.1 row T-68; test column "TC-TEN-003 (deactivation refusal only); blast-radius and platform-operator cases [Open]" |
| TM-C7 T-48 rewrite | T-48 | control column per §4.1 row T-48 (Edit/Write only; Bash uninspected; guard code within builders' scope; CODEOWNERS placeholders O-20; CI authorship check O-85 [Open]) |
| TM-C8 Boundary corrections | T-19, T-42, T-43, T-61, T-62, T-63 | B2; B8; B6/B3; host boundary from TM-C1 |
| TM-C9 Missing rows | new rows A–I of §4.1 | added with owner and [Open] tests; M-8 and M-9 folded into T-48 and T-39 |
| TM-C10 Cross-references | ADR-018 §Threat-model delta (owner: Enterprise Architect / build-e07); T-61 O-110 type | ADR-018 names T-60..T-62; RAID aligns O-110's type or id |
| TM-C11 "See also" links | T-08/T-31/T-43/T-45; T-09/T-26/T-27; T-34/T-40; T-12/T-16; T-17/T-64; T-02/T-28; T-05/T-59 | one cross-reference per family so no row is read as closing another |
| TM-C12 T-59 | T-59 | reviewed and signed by the Red-Team & Pen-Test Lead and the IVA (chair recused); test column stays [Open: TC-AI-016..019, O-79] |

Not a condition, an observation: the document's value is the traceability from threat to test; the twelve [Open] tests are the honest state of a dev/sim build and are acceptable at Gate B because Gate B authorises nothing beyond dev/sim [Source: 12]. Confidence: high that the conditions are complete for the rows read; medium that no further missing threat exists (the Board read the code of the store, the guard and the audit chain, not every service).

---

## 2. docs/SECURITY_PLAN.md — review

### 2.1 Presentation (security-architect) [Committee]
"Twelve control rows from blueprint 06, each with an implementation, an owner and a verifier. It is the plan, not the state: rows describe what the control will be." [Verified: the header says "Draft v1.0"; no column distinguishes plan from state; no row carries an evidence link.]

### 2.2 Row-by-row: what the row says, what exists, what verifies it [Verified]
| Row | Says | Exists in the tree (dev/sim) | "Verified by" says | Actual verification available |
|---|---|---|---|---|
| Zero trust, mTLS | mesh on Control/Execution planes (ADR-006), workload identity | `PlaneGuard` in-process; NetworkPolicy manifests; no mesh, no cluster (H-05) | Pen-Test | none exists (H-10); TC-NET-001..004 and `check_network_policies.py` are the evidence; cluster conformance [Open: IVA-11/O-42] |
| MFA/passkeys, PIM, separation of duties | identity service, maker-checker primitive | maker-checker and role checks exist (TC-ID-004/005/006, TC-AP-005); MFA and PIM hard-coded (R-06) | Red-Team | no exercise yet; tests above |
| Signed artefacts, SBOM, SAST/DAST/SCA, secret scanning | CI gates; unsigned deploy refused | secret scan gates; bandit/pip-audit gate (O-83 partial); SBOM unsigned; no cosign, no hash-pinned install, no SHA-pinned actions, no DAST; nothing refuses an unsigned deploy | QA | `check_scan_exceptions.py` OK (0 entries); TC-SC-001..003 [Open] |
| Encryption, tokenisation | KMS-managed keys; tokenised identifiers in analytics | no KMS (H-20); masking per tool (TC-AI-004); registry HMAC dev key; command HMAC in-process (O-53) | Pen-Test | none; D-053 design accepted, not built (O-81, O-82) |
| Tenant isolation | partitioned streams/storage/caches | application-level tenant predicate and per-tenant allowlists (TC-TEN-001..004); no partitioned streams/storage (single SQLite file, in-memory audit) | Red-Team | RT-03 executed as TC-TEN in dev/sim; deployed run [Open] |
| Secure SDLC | DoR/DoD security items, protected paths | DoD exists; CODEOWNERS with placeholder teams (O-20); branch protection [Open: H-01] | IVA | IVA reads authorship; no branch-level check (O-85) |
| Fail-closed distribution | marker check, env label, fixture refused, SHA-256; signing [Open: O-23] | delivered (TC-PKG-001..005); tag should now read [Open: D-054/O-83] | TC-PKG quartet; release workflow | correct |
| Agent segregation | roster + PreToolUse guard; CODEOWNERS control of record | Edit/Write hook only; Bash uninspected (R-46, R-54); roster widened 1e8555e; guard code within builders' scope | TC-AGT quartet; IVA | TC-AGT proves roster consistency and the Edit/Write path only |
| WAF/DDoS, egress control | edge + per-plane egress allowlists | no edge; NetworkPolicy manifests; registry egress check; in-process `EgressPolicy` loaded but not called (REVIEW_C3 F-20) | Chaos/Perf | TC-NET-003; TC-PERF-004 [Open] |
| Immutable logs | WORM audit with hash chain | hash chain, sealed head, monotonic time (TC-AUD-001..005); in-memory/JSONL, no WORM, no off-box anchor (O-54, B-5) | IVA | IVA-09 "not closed" |
| Backup/restore, incident response | DR_PLAN, INCIDENT_RESPONSE | documents; no drill (H-19) | drill evidence | none |
| Red teaming, independent pen-test | before Gate D and F | RED_TEAM_PLAN v1.0; RT-03 run in dev/sim; H-10 | Security & Privacy Board | — |

Eight of twelve rows describe a control that does not exist in the form stated, without an [Open] tag; the "Verified by" column names verifiers (Pen-Test, Red-Team, Chaos/Perf, drill) that have not run; no row links evidence. Under the Board's rule ("APPROVE only on evidence links, never on assertions") the document as written cannot be recommended for acceptance.

### 2.3 Missing rows [Committee]
| Missing control row | Source | Owner |
|---|---|---|
| Durable control-state integrity (per-row digest, chained journal, verify at open; keyed/anchored [Open: O-110]) | ADR-018, D-058 | Security Architect / Backend Lead |
| Model-provider boundary (gateway-only credential, region pin, egress in code and NetworkPolicy, redaction at the boundary, fail closed to Observe) | D-052, O-79 | Security Architect (row text proposed by the Board's prior packet — chair recused; IVA to review) |
| Signing keys: custody, ceremony, rotation, one key per purpose (registry, command, policy) | D-053, O-81, O-82, H-20 | Security Architect (same recusal) |
| Scanner exceptions and risk acceptance process (`security/scan_exceptions.yaml`, `check_scan_exceptions.py`, 90-day expiry, decision reference) | D-054 | Security Architect |
| Platform-operator and platform-auditor principals (IdP claims, separate paths, PIM window, audit of every unfiltered read) | D-059, O-120, O-121 | Backend Lead / Security Architect |
| Privacy-safe telemetry and structured redaction (TC-OB-002; R-35) | T-24, PRIVACY_IMPACT | SRE Lead / Privacy Lead |
| Replay defence: nonces, one-shot grants, durable nonce/revocation journals (O-55) | T-31, T-43, T-45 | Backend Lead |
| Rate limiting per principal (T-25) | REVIEW_C5 F-06 | SRE Lead |
| Kill Switch listener isolation from MCP handlers (T-35) | REVIEW_C3 F-05 | Backend Lead / SRE Lead |
| Environment ladder enforcement (RT_ENV exact match, fixture refusal, `--production` refusal) as a control in its own right | T-42, T-50 | Security Architect |

### 2.4 Challenges, validation, dissent [Committee]
- **mcp-security-agent (reviewer of record):** "I will not sign v1.0. The 'Agent segregation' row cites TC-AGT and IVA as verification; TC-AGT verifies the roster, not segregation, and the IVA has said so in writing. The registry row is missing entirely — the signed registry, the `--production` refusal and the egress check are the controls this plan should be proudest of and it does not list them. Add 'MCP registry and egress' as a row with `verify_tool_registry.py` and TC-AI-005/010/011 as evidence."
- **privacy-lead:** "No row for telemetry redaction, retention or legal hold; the plan and PRIVACY_IMPACT do not reference each other. A security plan in financial services without a data-handling row will not survive a DPIA review (O-10)."
- **red-team-pentest-lead:** "'Verified by: Pen-Test' three times, and there is no pen-test until H-10. Write 'target verifier' and 'current evidence' as two columns or the row misleads. **Different-line challenge:** is DO NOT ACCEPT proportionate when the fix is columns and tags? Yes — a plan that presents targets as implementation is the one document an auditor will hold against us; a v1.1 can be re-presented within days."
- **counsel-platform-reliability:** "Backup/restore row: with SQLite state and JSONL journals a restore is a replay (M-2); the row must say which files are restored together and that `verify()` runs before the platform serves."
- **security-architect (presenting) in reply:** "The plan was written as blueprint 06's checklist before any code existed. I accept a v1.1 with state, target, evidence and gate columns and the ten missing rows; I ask that the Board's own prior proposals (provider boundary, ceremony) be reviewed by someone other than the chair." Agreed (recusal stands).
- **Independent Validation, quoted:** "Board approvals of the *documents*: S&P Board on THREAT_MODEL and SECURITY_PLAN; … AEI rows 2, 2b, 10, 11, 12 reviewer columns filled by 2nd-line roles" [Source: REVIEW_2026-09-08_gate_B_iva §readiness actions]. The IVA does not assess the plan's content beyond that.
- **Dissent:** none on the verdict. Reservation, security-architect, verbatim: "DO NOT ACCEPT on a draft that says Draft in its header should not be recorded as a failure of the control set; the controls that exist are evidenced in the threat model."

### 2.5 Recommendation on docs/SECURITY_PLAN.md
**RECOMMEND DO NOT ACCEPT v1.0; re-present v1.1** with the following, after which the Board expects to recommend acceptance without a further council if the reviewer (MCP Security Agent) has signed:

| Condition | Row(s) changed | Exact change |
|---|---|---|
| SP-C1 Four columns | whole table | columns become: Control · Target (blueprint 06) · Delivered in dev/sim (with test ids and file paths) · Gap [Open: id] · Target verifier · Current evidence · First gate |
| SP-C2 Honest state per row | Zero trust; MFA/PIM; Signed artefacts; Encryption; Tenant isolation; Secure SDLC; WAF/egress; Immutable logs; Backup/restore | "Delivered" and "Gap" filled per §2.2, each gap with its RAID id (H-05, R-06, O-83, H-20/O-53/O-81/O-82, R-06/R-56, O-20/H-01/O-85, F-20/TC-PERF-004, O-54/B-5, H-19) |
| SP-C3 Agent segregation row | Agent segregation | text per §4.2; TC-AGT described as "roster consistency and Edit/Write path"; Bash limit, roster widening and guard-in-scope stated; control of record = CODEOWNERS + branch protection [Open: O-20] + CI authorship check [Open: O-85] |
| SP-C4 Missing rows | new rows of §2.3 | added, each with evidence or [Open] |
| SP-C5 MCP registry and egress row | new row | signed registry, `--production` refusal, egress check, per-tenant allowlists, revocation drill (`runtime.yaml`) — evidence `verify_tool_registry.py` output, TC-AI-005/010/011, TC-AI-012..015 |
| SP-C6 Data-handling cross-reference | new row | telemetry redaction, retention, legal hold, subject rights → PRIVACY_IMPACT rows; DPIA [Open: O-10] |
| SP-C7 Distribution row tag | Fail-closed distribution | "signing [Open: O-23]" → "[Open: D-054 → O-83; H-30]"; add TC-PKG-005 |
| SP-C8 Rows derived from Board packets | Model-provider boundary; Signing keys | drafted by the Security Architect from D-052/D-053, reviewed by the MCP Security Agent and the IVA (chair recused) |
| SP-C9 Reviewer signature | header | MCP Security Agent's review packet (docs/SESSIONS/REVIEW_…) cited in the header before AEI row 2 is signed |

Gate consequence [Committee]: the Board does **not** recommend withholding dev/sim on this account (dev/sim is the current state and needs no authorisation); it recommends that the Product Owner record v1.1 of the SECURITY_PLAN as a Gate B exit condition in the same way GA-C1..C8 were recorded at Gate A, so that the AEI row is signed on the re-issued document and not on v1.0.

---

## 3. Decisions in scope taken this week — Board recommendations

### 3.1 O-110 — integrity of the durable control store before shadow (D-058 condition b)
**Facts [Verified: store.py].** `SqliteStore` computes `row_digest(table, key, value, seq)` and a journal chain `journal_digest(prev, seq, op, table, key, value, correlation_id, at)` with SHA-256 and no key; `verify()` replays the journal at open and compares it with the state; the journal head is stored nowhere but in the file; `at` is wall-clock and not checked for monotonicity; `MemoryStore.verify()` is a no-op. TC-DUR-003 proves detection of an edited row, a deleted row and dropped journal lines; it does not attempt a consistent rewrite of rows plus journal, which the scheme cannot detect by construction (ADR-018 alternatives; BUILD_E07 C-3). The audit chain (`AuditStore`) has the same shape: SHA-256 chain, sealed `ChainHead` produced in-process, off-box anchor [Open: O-54], JSONL opened in append mode, no WORM.

**Options (each must survive the Postgres adapter that replaces SQLite before shadow, R-05) [Committee]:**
| Option | What it defends against | What it does not | Cost / new secret | Portability to Postgres | Reversibility |
|---|---|---|---|---|---|
| A. Keyed HMAC over rows and journal with a vault-held key | an actor with file write access who does not hold the key | an actor who reads the key from the process (the verifier must hold it: the O-22 objection to symmetric schemes applies); key custody, rotation and re-keying of the whole journal on rotation; a new secret inside the Execution plane, where `secrets_mount: none` and O-53 already keep the only secret small | KMS key + ceremony (H-20 extension); re-digest on rotation | yes (application-level) | medium |
| **B. Anchor the journal head into the audit chain, whose head is anchored off-box by a different principal (O-54)** | consistent rewrite of the store (rows + journal) — the attacker must also rewrite the audit chain, which is a different store, written by a different principal and anchored off-box; truncation after the last anchor; silent restore of a stale backup (the anchor no longer matches) | rows written since the last anchor (bounded by anchoring on every transaction that touches a control table); does nothing until the audit store is durable (B-5) and O-54's off-box anchor exists — which shadow already requires | no new secret; one audit append per control-table transaction; `verify()` gains an anchor parameter (the `AuditStore.verify(anchor=)` pattern already exists) | yes (journal table exists in every adapter) | high |
| C. OS-level immutability and file permissions (dedicated OS user, mode 0600, directory not writable by other services, append-only attribute where the OS offers it) | casual or accidental edits by other services on the host | a privileged actor; nothing once the store is a Postgres database (the mechanism does not exist there) | none | no | trivial |

**Recommendation: Option B (anchor the journal head with the audit head), with C as mandatory hygiene and A not adopted.** Reasons [Committee; Source: 06 immutable logs; 03 stack]: (1) B removes the class of attack ADR-018 admits (consistent rewrite) without adding a secret to the Execution plane; A moves the problem to key custody and still fails against an actor who can read the process. (2) B converges on controls shadow already requires — durable audit (B-5) and an off-box anchor written by a different principal (O-54) — so it adds no new prerequisite, it makes two existing ones load-bearing. (3) B survives the change of store technology; C does not. (4) B gives the auditor one chain of custody: control-state journal head → audit event `store.journal.sealed` (seq, head digest, correlation_id) → audit head → off-box anchor. Design points for the owner (not thresholds; proposals): seal on every transaction commit that writes `killswitch.activations`, `execution.consumed_authorisations`, `execution.by_decision`, the lease table or a sequence; `verify()` at open compares the journal head with the last `store.journal.sealed` event and refuses the store on mismatch (fail closed, `StoreIntegrityError`); a periodic monitor re-verifies and raises S1 on drift; journal `at` checked monotonic. **Residual after B:** the window since the last seal; the strength of the off-box anchor (O-54: WORM/replica written by a principal that cannot write the audit JSONL); dev/sim still runs both stores on one host under one principal, so the residual in dev/sim is "tamper-evident against inconsistent edits only" — acceptable in dev/sim (D-058 b), not beyond. Quartet to write first: positive (seal present, verify passes after restart), negative (journal head differs from the last seal → refused), abuse (rows and journal rewritten consistently, audit chain untouched → refused; stale backup restored → refused), recovery (audit store restored from the anchored replica, verify passes). Owner: Security Architect (design) / Backend Lead (build); reviewer: Integration Architect (seam), IVA; before shadow (Gate C entry evidence). Confidence: high on the choice, medium on schedule (B-5 and O-54 are human-dependent, H-05).

### 3.2 O-118 — co-location of the MCP revocation and nonce journals with the control store (D-058 condition e)
**Facts [Verified: platform.py 605–608; revocation.py; identity.py].** With `store_dir`, `revocations.jsonl` and `nonces.jsonl` default to the control store's directory; both are append-only JSONL without digest or chain (M-1); the rationale is that a restore of the control store must never be paired with forgotten revocations (M-2).
**Recommendation: accept co-location for dev/sim only (as decided), and resolve O-118 before shadow by moving both journals onto the `Store` seam inside the Control-plane store, not by moving files.** Reasons: (1) the consistency argument is correct — the two facts (an activation, and the revocation that must outlive it) must be restored together; separating them into two directories reintroduces the failure D-058 e avoided; (2) O-115 separates the Execution-plane store from the Control-plane store from shadow; the MCP journals belong on the Control side, so "MCP journals in the Control-plane store, execution state in the Execution-plane store" satisfies O-115 and O-118 at once; (3) on the seam the journals inherit the digests, the chained journal and, with §3.1, the anchor — closing M-1. Condition: the revocation and nonce tables are named control tables for the seal rule of §3.1; the Kill Switch activations that reference revoked grants and the revocations are restored as one unit (backup/restore row of SECURITY_PLAN v1.1). Owner: Backend Lead (build), MCP Security Agent (owner of the revocation semantics); before shadow. Residual in dev/sim: an actor who can edit the control store can un-revoke by deleting a JSONL line with no detection — acceptable only because dev/sim has no real tenant and no real credential [Source: 12].

### 3.3 O-120 — platform-operator principal as an IdP claim (D-059)
**Recommendation: agree with the decision (IdP claim, never a header) and set the design envelope:** (1) the claim is tenant-less (`tenant = '-'`) and time-bound (PIM window from the IdP, R-06), never derived from a header, a roster fixture or a CLI flag; (2) its actions are the platform-wide ones only (PLATFORM/TENANT Kill Switch levels, platform limits, tenant suspension/restore) and run on a separate route family or listener from the tenant BFF so that the tenant path never carries a platform capability; (3) deactivation of platform-wide levels keeps the two-person rule with a second distinct human (D-039); (4) every action is audited with tenant `-` and correlation id, which is why O-121 must land with it; (5) until R-06 exists there is no human platform-operator on the BFF — the service path (monitors, auto-actions) is not a human path and must not be dressed as one, and the CLI must not grow a header-style platform identity as a stop-gap (M-3). Quartet before code: positive (IdP claim engages PLATFORM Kill Switch), negative (tenant-bound principal 403 unchanged), abuse (claim asserted in a header or in `_meta`; expired PIM window; agent identity), recovery (claim expiry mid-session ends the capability; audit shows the boundary). Owner: Backend Lead / Security Architect; Gate C entry. Residual: none new in dev/sim (fail closed today, R-56).

### 3.4 O-121 — platform-auditor unfiltered read (D-059)
**Recommendation: agree that a 3rd-line platform-auditor principal exists, with a privacy envelope the Privacy Lead sets before any build:** (1) IdP claim as in §3.3, read-only, no export of payloads beyond the tenant auditors' view unless an investigation or legal-hold reference is supplied and audited; (2) every unfiltered read is itself an audit event (`audit.platform_read`, with the reason and the tenant set touched) so the chain records who saw whose rows; (3) the view respects residency: rows of a tenant whose `residency_region` differs from the reader's location are a transfer question for the DPIA (O-10) and stay [Open] until answered; (4) payloads are pseudonymised in the platform view by default (T-24 field-level redaction) and revealed only under (1); (5) chain-wide `verify` and the export head hash stay available to every auditor, as today. Owner: Backend Lead / IVA (consumer) / Privacy Lead (envelope); Gate C. Residual: a platform auditor is by construction a cross-tenant reader — the envelope above is the control, not a mitigation of the concept.

### 3.5 O-123 — second tenant policy under mcp/policies
**Recommendation: keep the second tenant a test fixture; do not ship a second `allowlist.<tenant>.yaml` under `mcp/policies` until a tenant onboarding process exists.** Reasons: (1) a per-tenant allowlist is an approval record for that tenant (MCP_TOOL_CATALOG registration process); a fixture tenant B in the frozen bundle would be an unapproved policy inside a signed distribution — the very thing T-49/T-50 refuse for the registry; (2) the loader's suffix/content cross-check and duplicate refusal (BUILD_E01 BD-1) already make the fixture safe for tests; (3) the tenant-escape evidence (RT-03 as TC-TEN) needs two tenants in tests, not in the bundle. Conditions: `build_sim_platform(second_tenant=True)` must be refused outside `RT_ENV` dev/sim (not verified by the chair — [Open], one negative test); the registry signature should cover per-tenant allowlists when real tenants exist (design with D-053, O-81). Owner: MCP Security Agent; Gate C.

### 3.6 T-60..T-68 — row verdicts (input to §1.7)
| Row | Board view |
|---|---|
| T-60 | sound; add "intent tracker and decision index still in memory — pre-restart intents refused, not resumed [Open: O-33/O-113]" so the row does not over-claim |
| T-61 | sound as far as it goes; TM-C5 wording; control ends with the §3.1 recommendation reference |
| T-62 | sound; alert `execution.store_unavailable` catalogued S1 (O-112) [Verified: alerts.yaml line 29]; add M-6 as a sibling row |
| T-63 | sound; O-117 tag correct; boundary from TM-C1 |
| T-64, T-65, T-66 | sound; tests exist and pass [Verified: 27 passed] |
| T-67 | sound; `mcp.tenant_revoked` S2 catalogued [Verified: alerts.yaml line 28]; owner MCP Security Agent correct |
| T-68 | rewrite (TM-C6); the Board's view for the Trading Risk Committee: cross-tenant halting is fail-safe for capital and unsafe for availability; keep activation with the tenant, but alert `killswitch.cross_tenant_scope` (S2) when a tenant-bound principal engages an ASSET/VENUE/STRATEGY level that other tenants trade, and let the platform operator (O-120) narrow it |

### 3.7 Guard state — E-1 (enforce beyond Edit/Write, or replace by CI branch-level path-ownership checks)
**Facts [Verified].** The project-level hook in `.claude/settings.json` matches `Edit|Write|MultiEdit|NotebookEdit` and calls `scripts/agent_guard.py`; the guard reads `agent_type` from the payload (PROBE_O58 B/C; TC-AGT-001 payload case at test lines 56–60) and returns 0 for the main session. Bash is not matched; the harness's auto-mode instruction routes edits through Bash for the main session (R-54) and, in the E07 session, for the build agent as well (BUILD_E07 C-14). Since 1e8555e every build agent's roster entry includes `scripts/`, `apps/`, `services/` and `test/` (build-e13 also `security/`): the two guard modules, every protected service path and the tests are inside the write scope of the agents the guard constrains; `product-owner` may edit `.claude/agents/` (the roster the guard reads). CODEOWNERS team handles are placeholders (O-20); branch protection is not enabled (H-01). No `scripts/check_authorship.py` exists (O-85 open). Commits carry a `Claude-Session` trailer, not an agent name [Verified: `git log -1 --format=%B a90b1ae`].
**Recommendation: E-1 = replace, not extend.** (1) Do not extend the hook to Bash as a control: command parsing (redirects, `sed -i`, `tee`, `python -c`, git plumbing) is a heuristic that an agent working in auto mode will trip on constantly and that closes nothing (the previous packet §4.2 said the same; the roster widening now makes the point moot — the subjects can edit the guard). A best-effort Bash matcher that only blocks `sed -i`/redirect writes into `services/risk`, `services/compliance`, `services/execution`, `services/killswitch`, `mcp/policies`, `security`, `contracts` is acceptable as friction, never as evidence. (2) The control of record is branch-level: `scripts/check_authorship.py` in CI reads a declared agent per commit (an `Agent:` trailer that generated agents add, or the PR's declared agent) and fails when a changed path is outside that agent's `allowed_paths`; missing or unknown agent → fail for protected paths, warn elsewhere; human commits exempt but must be human-authored (GA-C3/H-27). The check trusts a self-declared trailer, so it is only as strong as CODEOWNERS + branch protection behind it — O-20/H-01 remain the closure of R-46. (3) Narrow the roster back: build agents get their epic's paths plus the shared kernel they need, never `scripts/`, `apps/cli/rt365_cli/agent_guard.py` or `security/`; the guard's own files and `.claude/` become ALWAYS_DENIED for every generated agent, like CODEOWNERS today. (4) Nothing in a gate record may cite TC-AGT as segregation evidence (IVA's words). Residual accepted for dev/sim only: author ≠ reviewer for agents rests on the honesty of the session record, CODEOWNERS placeholders and IVA authorship review. Owner: Product Owner delegate (roster, generator), MCP Security Agent (2nd-line review), Cloud Architect (CI step); due: CI check before Gate B sign-off (C-AGT-2 of the previous packet stands), roster narrowing in the same change, branch protection at Gate C (H-01).
**Dissent (mcp-security-agent), verbatim:** "I would go further and make the guard fail closed for the main session on protected paths now; the chair's position that the harness behaviour is unknown no longer holds — PROBE_O58 showed the payload. Record that I asked for it." Chair's reply: recorded; it is a proposal for the MCP Security Agent's own change under CODEOWNERS review, not a Board condition, because the main session is the human Product Owner's seat (D-040) and denying it is a Product Owner choice.

---

## 4. Proposed row text (owners apply; no ids assigned here)

### 4.1 docs/THREAT_MODEL.md (owner: Security Architect; reviewer: Red-Team & Pen-Test Lead)
Boundary line: `B1 user↔BFF · B2 BFF↔services · B3 Analytics↔Control · B4 Control↔Execution · B5 Execution↔broker · B6 MCP server↔tool · B7 provider↔ingest · B8 CI/agent harness↔repository/production · B9 model gateway↔provider (D-052) · B-next host/OS↔control-store and journal files (ADR-018) · B-next platform↔regulatory adapters (DF-09)`.

| Row | Proposed text (ID · Threat · Boundary · Control · Test · Owner) |
|---|---|
| T-48 (rewrite) | A delivery agent authors an artefact it reviews or approves, or edits the guard that constrains it [Committee: ADR-016; roster 1e8555e] · B8 · Generated roster + PreToolUse hook on Edit/Write/MultiEdit/NotebookEdit with the harness-supplied `agent_type` (PROBE_O58); **Bash writes uninspected (R-46, R-54); guard modules and protected service paths inside every builder's roster scope [Open: roster narrowing]**; controls of record: CODEOWNERS (placeholder teams, O-20), branch protection [Open: H-01], CI authorship check [Open: O-85]; IVA authorship review · TC-AGT-001..004 (roster consistency and the Edit/Write path only) · Product Owner / MCP Security Agent |
| T-39 (extend control) | … append: "authorisation key supplied at start-up (`authorisation_key`) — never logged, never in an agent context; vault/KMS supply and rotation [Open: O-53]" |
| T-61 (per TM-C5) | test: TC-DUR-003 (edit, delete, journal drop; consistent rewrite not attempted — RT-05 [Open]); control ends: "journal head anchored in the audit chain and off-box [Open: O-110 → COUNCIL_2026-09-08_gate_B_spb_docs §3.1]" |
| T-68 (rewrite) | Cross-tenant blast radius of ASSET/VENUE/STRATEGY halts engaged by a tenant-bound principal (denial of service between tenants) [Committee: BUILD_E01 C-3] · B2 · Accepted risk R-57 (halting is fail-safe for capital; Trading Risk Committee to confirm); compensating: deactivation of platform-wide levels refused for tenant principals (delivered); platform-operator narrowing [Open: O-120]; alert on cross-tenant scope activation [Open] · TC-TEN-003 (deactivation refusal only); blast-radius case [Open] · Chief Risk Agent |
| new row A | Revocation or nonce journal line deleted or rewritten: a revoked tool, identity or tenant grant silently returns; a consumed nonce is replayable [Committee: this packet M-1] · host / B6 · Interim: append-only JSONL, restart reload; target: journals on the `Store` seam in the Control-plane store with digests, chain and anchor (O-55, O-118, O-110) · [Open] (quartet with O-55) · MCP Security Agent / Backend Lead |
| new row B | Control store restored from a backup without the matching revocation/nonce journals (or the reverse): consumed grants and revoked identities re-opened — restore is a replay [Committee: D-058 e] · host / B4 · Journals and control tables restored as one unit; `verify()` against the last anchor refuses a stale restore (§3.1) · [Open] (recovery case of the O-110 quartet) · SRE Lead / Backend Lead |
| new row C | Platform-wide human action (PLATFORM/TENANT halt, platform limit, tenant suspension) attempted through a header-style or CLI identity instead of an IdP-bound platform-operator claim [Committee: BUILD_E01 C-2, D-059] · B1/B2 · Tenant BFF refuses platform levels for every tenant-bound principal (delivered, 403); platform-operator claim with PIM window and separate path [Open: O-120]; no CLI stop-gap identity · TC-TEN-003 (refusal); platform-operator quartet [Open] · Backend Lead / Security Architect |
| new row D | Platform-auditor unfiltered read used to exfiltrate another tenant's rows or to move personal data across a residency boundary [Committee: BUILD_E01 C-7, D-059] · B2 · Read-only IdP-bound 3rd-line claim; every unfiltered read audited with reason; pseudonymised payloads unless an investigation/hold reference; residency rule per DPIA [Open: O-121, O-10] · [Open] · Backend Lead / Privacy Lead |
| new row E | A pending first-person Kill Switch deactivation persists across restarts indefinitely; a second hand completes it long after the context changed [Committee: BUILD_E07 C-9] · B2/B4 · Pending-deactivation TTL with audit of expiry [Open: R-23]; PIR reference for PLATFORM/TENANT deactivation · [Open] · Backend Lead / Chief Risk Agent |
| new row F | A stuck or hostile writer holding the store lock makes every gateway submit, retry and cancel fail closed (`busy_timeout` then StoreError): the Execution plane cannot flatten a position [Committee: BUILD_E07 C-7/C-13] · host / B4 · S1 `execution.store_unavailable` (delivered); lock-holder identification and cancel-path priority [Open: O-117]; Execution-plane store separate from shadow (O-115) · TC-DUR-003 (fail closed); chaos case [Open: O-117] · SRE Lead / Performance & Chaos Lead |
| new row G | Control state survives a restart while its audit trail does not (audit store in memory / JSONL): an activation or a consumed grant without the events that produced it [Committee: BUILD_E07 C-10] · DF-07 · Durable, anchored audit store before shadow (B-5, O-54); journal rows carry correlation_id but are not the audit · TC-AUD-001..005 (chain); durable-audit quartet [Open: B-5] · SRE Lead |
| new row H | Forged, replayed or unauthorised regulatory report or submission through a regulatory adapter [Source: 06; DATA_FLOWS DF-09] · B-next (platform↔regulatory adapters) · Per-jurisdiction adapter enabled by dual key; report signed by a human Compliance role; idempotent submission [Open] · [Open] · Compliance Agent / Integration Architect |
| new row I | Licensed or unlicensed market-data field leaves the entitlement boundary into an AI context, an export or a second tenant [Source: DATA_FLOWS DF-01/DF-02] · B7/B3 · Entitlement check at ingest, masking of unlicensed fields at DF-02 (documented, not tested) [Open: TC-MD entitlement case] · [Open] · Data Architect / Data Engineering Lead |
| footnote | "Rows T-14..T-37: review cycle 1 delta (Delivery Orchestrator, AI). T-38..T-46: IVA remediation commits. T-47..T-50: ADR-016. T-51..T-57: Gate A council and E06. T-58..T-59: IVA ID allocation (O-102). T-60..T-63: E07 (ADR-018). T-64..T-68: E01. Transcribed by the Product Owner delegate; reviewer: Red-Team & Pen-Test Lead (signature: <REVIEW_ packet>); Board recommendation: COUNCIL_2026-09-08_gate_B_spb_docs; decision: pending (Product Owner). A test id tagged [Open] does not exist yet; twelve rows carry one." |

### 4.2 docs/SECURITY_PLAN.md v1.1 (owner: Security Architect; reviewer: MCP Security Agent)
Header: `| Security Architect | MCP Security Agent | Security & Privacy Board (recommends), Product Owner (decides, D-039) | B | v1.1 — state, target, evidence and gate per control; re-presented after COUNCIL_2026-09-08_gate_B_spb_docs |`
Columns: `| Control | Target [Source: 06] | Delivered in dev/sim (tests, paths) | Gap [Open] | Target verifier | Current evidence | First gate |`
Example rows (owner fills the rest from §2.2):
- `| Agent segregation (three lines for delivery agents) | roster-generated agents, segregation machine-checked | generated roster (67 agents, make agents-check); PreToolUse hook on Edit/Write with harness agent_type (PROBE_O58); TC-AGT-001..004 (roster consistency, Edit/Write path) | Bash writes uninspected (R-46, R-54); guard modules and protected services inside builders' roster scope (1e8555e); CODEOWNERS placeholders (O-20); no branch protection (H-01); no CI authorship check (O-85) | IVA authorship review; CI authorship check | TEST_CASES/TC-AGT.md; PROBE_O58; this packet §3.7 | B (guard rail), C (control of record) |`
- `| Durable control-state integrity | keyed or anchored tamper-proof control state | rtcore.store: per-row SHA-256 digest, hash-chained journal, verify() at open, fail closed (TC-DUR-001..004, TC-EX-011, TC-KS-010) | unkeyed, unanchored (O-110 → journal head anchored in the audit chain, off-box via O-54; recommendation §3.1); consistent rewrite undetected; MCP journals plain JSONL (O-55/O-118) | IVA; RT-05 | TEST_CASES/TC-DUR.md; ADR-018 | B (dev/sim), C (anchored) |`
- `| MCP registry and egress | signed registry, forbidden capabilities structurally impossible, egress allowlist | HMAC dev-key registry with envelope, fixture flag, environment tag, --production refusal (TC-AI-005/010/011); stdio transport identity bound by host (TC-AI-012..015); per-tenant allowlists (TC-TEN-001..004); NetworkPolicy checker (TC-NET) | asymmetric trust set (D-053, O-81); in-process EgressPolicy not on the call path (F-20); cluster conformance (IVA-11) | MCP Security Agent; pen-test (H-10) | verify_tool_registry.py output (this packet §0.4) | B |`
- `| Backup and restore of control state | restore never replays | — | control tables and revocation/nonce journals restored as one unit; verify() against the last anchor before serving (§3.1, §3.2); drill (H-19) | SRE drill; IVA | [Open] | C |`
- `| Platform-operator and platform-auditor principals | IdP claims, PIM window, separate paths | tenant BFF refuses platform levels (TC-TEN-003) | O-120, O-121 designs; every unfiltered read audited; residency rule (O-10) | Security Architect; Privacy Lead | [Open] | C |`
Rows for the model-provider boundary (D-052) and signing-key custody (D-053) drafted by the owner from the decision text; the chair recused from their wording.

### 4.3 docs/RAID_LOG.md (owner: Program Orchestrator / delegate; ids by the owner)
| Type | Proposed text | Owner | Gate |
|---|---|---|---|
| Gap | THREAT_MODEL v1.1 per conditions TM-C1..C12 (boundaries, author of record, [Open] tags on T-04/T-05/T-10/T-11/T-37, interim/target split, T-48/T-61/T-68 rewrites, rows A–I, ADR-018 cross-reference); Red-Team & Pen-Test Lead signature before AEI row 2 | Security Architect | B |
| Gap | SECURITY_PLAN v1.1 per SP-C1..C9 (four-column state/target/evidence/gate, ten missing rows, MCP registry row, data-handling row); MCP Security Agent signature; recorded as a Gate B exit condition | Security Architect | B |
| Decision (O-110 update) | Board recommends anchoring the store journal head in the audit chain with the audit head anchored off-box by a different principal (O-54), OS-level file hygiene as mandatory but non-evidential, keyed HMAC not adopted; quartet first; B-5 and O-54 become load-bearing before shadow | Security Architect / Backend Lead | C (shadow) |
| Decision (O-118 update) | Board recommends resolving co-location by moving the revocation and nonce journals onto the `Store` seam in the Control-plane store (O-55), restored as one unit with activations; not by separate directories | Backend Lead / MCP Security Agent | C (shadow) |
| Risk | Revocation and nonce journals are plain JSONL without digest or chain: a deleted line un-revokes or re-enables replay undetected (row A) | MCP Security Agent | C |
| Risk | Every build agent's roster includes `scripts/` and `apps/` (guard modules) and `services/` (protected paths); build-e13 includes `security/`; the guard is editable by its subjects through the guarded tools (1e8555e) | Product Owner delegate / MCP Security Agent | B |
| Gap | Roster narrowing: builders limited to their epic's paths plus named shared modules; guard files and `.claude/` ALWAYS_DENIED for generated agents | Delivery Orchestrator (generator) | B |
| Gap | `scripts/check_authorship.py` CI step (declared agent per commit vs roster; fail closed on protected paths) — O-85 made concrete; roster narrowing in the same change | Cloud Architect / MCP Security Agent | B |
| Gap | Verify that `build_sim_platform(second_tenant=True)` is refused outside dev/sim (one negative test) (O-123) | Backend Lead | C |
| Gap | DATA_FLOWS: DF-05 updated for command authorisation and the oracle (ADR-015); new flows for the model gateway (B9), the control-store/journal files (host boundary) and residency notes on DF-01/DF-02 — ARB item, noted here for consistency | Data Architect | B |
| Gap | ADR-018 §Threat-model delta cites T-52..T-54; the rows are T-60..T-62 | Enterprise Architect / build-e07 | B |
| Assumption | The Postgres adapter (R-05) carries the journal table and the anchor; the O-110 design is validated on that adapter, not only on SQLite | Cloud Architect | C |

---

## 5. Definition of Done for the two documents' approval records [Committee]
1. **Segregation:** author of record (Security Architect) ≠ transcriber (Product Owner delegate, named in the footnote) ≠ reviewer (THREAT_MODEL: Red-Team & Pen-Test Lead; SECURITY_PLAN: MCP Security Agent) ≠ recommender (Board chair; recused rows reviewed by the IVA) ≠ decider (human Product Owner, or the AI delegate under D-040 with the human's confirmation recorded). No person or agent appears twice for one document.
2. **Reviewer signature = a packet, not a column entry:** the reviewer writes `docs/SESSIONS/REVIEW_<date>_<doc>_<role>.md` citing the commit hash of the version reviewed and listing each condition TM-C*/SP-C* as met or not; the header's reviewer cell links it.
3. **AEI rows:** row 2 (Threat model approved) reviewer column = "Red-Team & Pen-Test Lead (agent) — REVIEW_…; Board: RECOMMEND ACCEPT WITH CONDITIONS, COUNCIL_2026-09-08_gate_B_spb_docs §1.7; agent approval — human PO decision pending"; location column names the commit of v1.1; the IVA column is filled only by the IVA. Row 2b (DATA_FLOWS, ADRs, capacity, ownership) belongs to the ARB chair; this Board's consistency findings (§1.2, §4.3 DATA_FLOWS row) are referenced there. Row 10 (registry signed and policy-consistent): owner MCP Security Agent, so the reviewer must be another role — Security Architect or the Board chair, citing the `--production` refusal output of §0.4 and the commit. Row 11 (network policy invariants): owner Cloud Architect, reviewer Security Architect, citing `check_network_policies.py` output and IVA-11 open. Row 12 (SBOM): owner Security Architect, reviewer Cloud Architect or IVA, citing `security/sbom/sbom.cdx.json` "unsigned [Open: O-83]". A new AEI row for this packet with the Board chair in the reviewer column marked "agent approval — human PO decision pending".
4. **Document status:** the header Status changes to "v1.1 — accepted for dev/sim (D-nnn)" only after the decision is in DECISION_LOG; until then "v1.1 — reviewed, Board recommendation issued, decision pending".
5. **Evidence provenance:** every test id cited as delivered exists in `docs/TEST_CASES/` and in the CI-generated EVIDENCE_REPORT at the pushed commit (the current report was generated on a dirty tree at 9e78104, tested tree 4e3e1c9 — O-65); rows whose tests do not exist carry [Open] and a RAID id.
6. **Gate record:** the Gate B report cites the AEI rows, not the documents' own status lines; TC-AGT is never cited as segregation evidence; the environment tag stays dev/sim.
7. **PMO:** `make pmo-sync` after the ledger changes (ADR-017).

---

## 6. Consolidated recommendations and decision requests

### 6.1 Verdicts
| Item | Board recommendation | Conditions | Decision requested of the Product Owner |
|---|---|---|---|
| docs/THREAT_MODEL.md | RECOMMEND ACCEPT WITH CONDITIONS (dev/sim baseline v1.1) | TM-C1..C12 | accept v1.1 as Gate B evidence once the reviewer has signed; record the transcriber/author distinction |
| docs/SECURITY_PLAN.md | RECOMMEND DO NOT ACCEPT v1.0; re-present v1.1 | SP-C1..C9 | record v1.1 as a Gate B exit condition; do not sign AEI row 2 on v1.0 |
| O-110 | Anchor the journal head in the audit chain (Option B); OS hygiene mandatory; HMAC not adopted | quartet first; B-5 and O-54 before shadow | adopt as the D-058 (b) choice |
| O-118 | Co-location dev/sim only; resolve by moving journals onto the seam in the Control-plane store (O-55) | restore as one unit; anchor rule covers the journals | confirm |
| O-120 | IdP claim, tenant-less, PIM-bound, separate path; no CLI stop-gap identity | quartet before code | confirm the envelope |
| O-121 | Yes, under the privacy envelope of §3.4 | Privacy Lead sets the envelope; DPIA input | confirm the envelope and the "pseudonymised by default" rule |
| O-123 | Keep the second tenant a test fixture; no bundle policy without onboarding | negative test for `second_tenant` outside dev/sim | confirm |
| T-60..T-68 | sound except T-68 (rewrite) and T-61 (honest test wording) | TM-C5, TM-C6 | — |
| Guard state (E-1) | Replace: CI authorship check + roster narrowing + branch protection; Bash matcher as friction only | §3.7 (1)–(4) | accept R-46/R-54 for dev/sim explicitly (D-nnn) with O-85 and roster narrowing due before Gate B sign-off |

### 6.2 One-line decision requests (proposed text for docs/PO_DECISION_QUEUE.md; the delegate records)
- O-106 (THREAT_MODEL): "Accept THREAT_MODEL v1.1 as Gate B dev/sim evidence after TM-C1..C12 and the Red-Team Lead's signature?" — Board: RECOMMEND ACCEPT WITH CONDITIONS.
- O-106 (SECURITY_PLAN): "Record SECURITY_PLAN v1.1 (SP-C1..C9) as a Gate B exit condition and withhold AEI row 2 until it is signed?" — Board: DO NOT ACCEPT v1.0.
- O-110: "Adopt journal-head anchoring in the audit chain with off-box anchoring (O-54) as the store integrity scheme before shadow; keyed HMAC not adopted?" — Board: RECOMMEND.
- O-118: "Resolve MCP-journal co-location by moving both journals onto the Store seam in the Control-plane store before shadow?" — Board: RECOMMEND.
- O-120 / O-121: "Confirm the platform-operator and platform-auditor envelopes of §3.3/§3.4 (IdP claim, PIM window, separate path, audited and pseudonymised unfiltered reads, residency via DPIA)?" — Board: RECOMMEND.
- O-123: "Keep the second tenant a test fixture until a tenant onboarding process exists?" — Board: RECOMMEND.
- R-46/R-54/E-1: "Accept the Bash bypass for dev/sim explicitly, with the CI authorship check and roster narrowing due before Gate B sign-off and branch protection at Gate C?" — Board: RECOMMEND WITH CONDITIONS.

### 6.3 Proposed AUDIT_EVIDENCE_INDEX row (reviewer column text)
`| next | B | Security & Privacy Board review of THREAT_MODEL and SECURITY_PLAN (O-106), O-110/O-118/O-120/O-121/O-123, T-60..T-68 and the guard state | council packet + verbatim checks | docs/SESSIONS/COUNCIL_2026-09-08_gate_B_spb_docs.md (§0.4: --production refusal, 27 quartet tests, 203-test suite, lint/policy/agents/secret-scan OK at a90b1ae) | Board chair (approver agent) | Board chair — agent approval, human PO decision pending; IVA review requested | 2026-09-08 | |`

---

## 7. Concerns for the Product Owner
Numbered so each can be answered; none is a decision, each names the decision it needs.

- **SPB-PO-1 The security plan cannot be accepted on evidence.** [Verified] SECURITY_PLAN v1.0 has no evidence column, eight of twelve rows present a target as an implementation, and its verifiers (pen-test, red team, drills) have not run. The fix is columns, tags and ten rows — days, not weeks — but AEI row 2 must not be signed on v1.0. Decide: v1.1 as a Gate B exit condition (recommended) or a Gate B pass on v1.0 with the Board's objection recorded.
- **SPB-PO-2 Choosing anchoring for O-110 makes two human-dependent items load-bearing.** [Committee] The Board recommends anchoring the store journal head in the audit chain rather than a keyed HMAC because it adds no secret to the Execution plane and survives the move to Postgres. It only works once the audit store is durable (B-5) and its head is anchored off-box by a different principal (O-54) — both need infrastructure (H-05). Until then the store is tamper-evident against inconsistent edits only. Decide: adopt, and accept that B-5 and O-54 are shadow entry conditions.
- **SPB-PO-3 The agent guard is now editable by the agents it guards.** [Verified: roster.json at 1e8555e] Every build agent may edit `scripts/` and `apps/` (both guard modules), `services/` (all protected paths) and `test/`; build-e13 may edit `security/`; Bash writes are uninspected and are the default path under auto mode. The only segregation of record is CODEOWNERS with placeholder teams and no branch protection. Decide: accept this explicitly for dev/sim (a D- entry, not an implicit state), with roster narrowing and the CI authorship check before Gate B sign-off and H-01/O-20 at Gate C.
- **SPB-PO-4 Author, transcriber and decider overlap on the threat model.** [Verified: git history] The Security Architect is the owner of record but T-38..T-68 were transcribed and committed by the Product Owner delegate, who also decides acceptance under D-040. The Board asks that the human Product Owner sign AEI row 2 personally, or name a distinct reviewer in the header (TM-C2), so the record does not show one AI seat authoring and accepting the same rows.
- **SPB-PO-5 The Board's own proposals are entering the documents it reviews.** [Verified] T-59 and two SECURITY_PLAN rows originate in the chair's previous packet; the chair has recused on them and asks the IVA to review those rows. Decide whether that is sufficient, or whether Board packets should stop proposing row text and only state conditions.
- **SPB-PO-6 A platform auditor is a cross-tenant reader by design.** [Committee] O-121 was decided "yes"; the Board agrees only under the envelope of §3.4 (IdP claim, every unfiltered read audited with a reason, pseudonymised payloads unless an investigation reference, residency answered by the DPIA). Decide the envelope before any build, and treat the residency question as [Open: O-10] — no assertion is made about any jurisdiction's law.
- **SPB-PO-7 Platform-wide human actions have no human path until an IdP exists.** [Verified: R-56] That is fail closed and acceptable in dev/sim; it must be an explicit Gate C entry condition (O-120 built on R-06), and no header- or CLI-based platform identity may be added as a stop-gap.
- **SPB-PO-8 Cross-tenant halts (R-57) are a security property too.** [Committee] The Trading Risk Committee decides; the Board asks it to hear §3.6: keep activation with the tenant, alert on cross-tenant scope, let the platform operator narrow it.
- **SPB-PO-9 Evidence of record is generated on a dirty tree.** [Verified: EVIDENCE_REPORT header] The report cited by every row was generated at base 9e78104 with tested tree 4e3e1c9; approvals should cite the CI-generated report at the pushed commit (O-65). The checks in §0.4 ran on the clean worktree at a90b1ae.
- **SPB-PO-10 Twelve threat rows and ten plan rows carry [Open] tests.** [Verified] That is the honest state of a dev/sim build and does not block Gate B, which authorises nothing beyond dev/sim; it does mean no statement of the form "the threat model is covered by tests" may appear in the Gate B report. Every threshold in this packet (seal cadence, 90-day exceptions, PIM windows) is a proposal; no vendor capability, regulatory status or performance figure is asserted.

---

## 8. Assumptions, confidence, provenance
- A-1 [Committee]: the ARB reviews DATA_FLOWS/CAPACITY_MODEL (AEI 2b) separately; this packet's DATA_FLOWS findings are consistency notes for it.
- A-2 [Committee]: the Trading Risk Committee hears R-57 and O-113; the Board's §3.6 view is advisory to it.
- A-3 [Open]: whether `build_sim_platform(second_tenant=True)` is refused outside dev/sim was not verified.
- A-4 [Source: 12]: Gate B authorises development and simulation only; nothing here promotes any environment.
- Confidence: THREAT_MODEL conditions high; SECURITY_PLAN verdict high; O-110 choice high / schedule medium; O-118 high; O-120/O-121 envelopes medium-high (IdP facts depend on R-06's design); O-123 high; guard state high on facts, [Open] on harness changes.
- Provenance: every [Verified] statement is a file read or a command run on 2026-09-08 in the worktree at a90b1ae (clean); every [Committee] statement is a council position heard in this session or a prior packet cited by name; every vendor, regulatory or infrastructure fact is [Open]; nothing in this packet is a Product Owner decision.
