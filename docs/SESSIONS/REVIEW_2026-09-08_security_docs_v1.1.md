# REVIEW_2026-09-08_security_docs_v1.1 — THREAT_MODEL v1.1 and SECURITY_PLAN v1.1 against the Security & Privacy Board's conditions (O-129, D-061)

| Session | Date | Author | Line | Status |
|---|---|---|---|---|
| Security Architect applying TM-C1..TM-C12 and SP-C1..SP-C9 | 2026-09-08 | security-architect (1st line, owner of both documents) | 1st line | **not an approval**; the reviewer is the Red-Team & Pen-Test Lead (THREAT_MODEL) and the MCP Security Agent (SECURITY_PLAN); the human Product Owner decides (D-039) |

## 1. Roles and segregation [Verified: `.claude/agents/roster.json` write scope; D-061 §5 DoD]
| Role | Seat | This session |
|---|---|---|
| Author of record, both documents | Security Architect | wrote v1.1 of both files and this packet |
| Transcriber of T-38..T-79 | Product Owner delegate | named in the THREAT_MODEL footnote (TM-C2); did not act here |
| Reviewer, THREAT_MODEL | Red-Team & Pen-Test Lead (3rd line) | **pending** — no packet exists |
| Reviewer, SECURITY_PLAN | MCP Security Agent (2nd line) | **pending** — no packet exists |
| Reviewer of the recused rows (T-59, model-provider boundary, signing-key custody) | Independent Validation Agent | **requested, pending** (TM-C12, SP-C8) |
| Recommender | Security & Privacy Board chair | COUNCIL_2026-09-08_gate_B_spb_docs §1.7, §2.5 |
| Decider | Product Owner (human, D-039); AI delegate under D-040 | pending |

The author of these documents does not approve them, does not accept their residual risk, and does not sign off a penetration test it scoped. No approval, gate pass or risk acceptance is recorded anywhere in this packet [Source: 00; Committee: D-039].

## 2. Purpose and scope
Apply, exactly, the Board's conditions on the two Gate B exit-evidence documents (RAID O-129; decision D-061 (1) and (2)) and fold in what changed in the codebase **after** the Board reviewed: ADR-019 / D-060 (asymmetric signing with a public trust set, rows T-69..T-73) and ADR-020 / D-062 (durable, externally witnessed audit, rows T-74..T-79 — the second half of the Board's Option B for O-110) [Verified: `git log`, ADR files, test tree at this commit]. In scope: `docs/THREAT_MODEL.md`, `docs/SECURITY_PLAN.md`. Out of scope and not edited: RAID_LOG, DECISION_LOG, REQUIREMENTS_TRACEABILITY, AUDIT_EVIDENCE_INDEX, DATA_FLOWS, PRIVACY_IMPACT, ADR-018 — rows for those are **proposed** in §7 for their owners. Nothing here promotes any environment beyond dev/sim [Source: 12]. Profit is an objective, never a promise [Source: 00].

**Status convention applied to both files** [Committee: D-061 closing sentence]: `v1.1 — reviewed, Board recommendation issued, decision pending`. D-061 exists in DECISION_LOG and records the Product Owner's position, but it says in terms that *no document status changes to "accepted" until its new version and its reviewer signature exist*. Neither reviewer signature exists at this commit, so neither document says "accepted".

## 3. Condition-by-condition
### 3.1 THREAT_MODEL (TM-C1..TM-C12)
| Condition | Status | What was changed |
|---|---|---|
| TM-C1 Boundaries declared | **applied** | Boundary line gains **B9** model gateway↔model provider (D-052), **B10** host/OS↔control-store, audit-store and journal files (ADR-018, ADR-020), **B11** platform↔regulatory adapters (DF-09); a note says the DATA_FLOWS mirror is owed by the Data Architect [Open: O-129] |
| TM-C2 Author of record | **applied** | Header table now has separate "Author of record", "Transcriber", "Reviewer", "Recommending body", "Decider" columns; the footnote lists the packet of origin per row range (T-01..T-13, T-14..T-37, T-38..T-46, T-47..T-50, T-51..T-57, T-58..T-59, T-60..T-63, T-64..T-68, T-69..T-73, T-74..T-79, T-80..T-88) and states plainly that the transcriber also decides under D-040 (SPB-PO-4) |
| TM-C3 [Open] where no test exists | **applied** | T-04 → `[Open: TC-SC-002 — O-83]` with the control split into unsigned SBOM delivered / artefact and model-artefact signing open; T-05 → secret scan delivered, `[Open: TC-SEC-001]`; T-10 → CI `security-scan` delivered, `[Open: TC-SC-001 — O-83]`; T-11 → `[Open: TC-PERF-004 — R-35, H-05]`; T-37 → fallback exercised by an unindexed unit test, `[Open: TC-KS-011]` (id allocated, test absent) |
| TM-C4 Interim/target split and stale ids | **applied** | T-06, T-07, T-12, T-14 split interim/target; T-14 and T-19 no longer tag TC-ID-005/006 and TC-CP-007 as `[Open]` (they exist and pass); T-23's hold-release case gets its own id `TC-CP-013` `[Open]` and the row says explicitly that TC-CP-008 is the T-52/T-53 legal-record test; T-35's invalid `TC-SEC-MCP` replaced by `TC-SEC-004` `[Open]` |
| TM-C5 T-61 honesty | **applied, amended** | Test column now reads "TC-DUR-003 (edit, delete, journal drop; **the consistent rewrite is not attempted** — RT-05 [Open])". The control column ends with the **decision** rather than the recommendation, because the decision landed after the Board wrote: D-061 (5) / O-128 chose journal-head anchoring into the audit chain; the audit half is delivered (ADR-020/D-062) and **the anchoring itself is not implemented** [Verified: no `journal.sealed` or journal-head anchor exists in `libs/core/rtcore/store.py` or `services/audit/`] |
| TM-C6 T-68 rewrite | **applied** | Control column now states the accepted risk R-57 (with "not accepted by its author"), the delivered compensating control, the platform-operator narrowing [Open: O-120] and the `killswitch.cross_tenant_scope` alert as **[Open: O-132] — proposed, not catalogued, does not exist** [Verified: absent from `observability/alerts.yaml` and ALERT_CATALOG]; test column limited to the deactivation refusal |
| TM-C7 T-48 rewrite | **applied** | Edit/Write-only guard, Bash uninspected (R-46/R-54), guard modules and protected services inside builders' roster scope, CODEOWNERS placeholders (O-20), branch protection (H-01), CI path-ownership check (O-85/O-131), "nothing in a gate record may cite TC-AGT as proof that segregation is enforced" |
| TM-C8 Boundary corrections | **applied** | T-19 → B2; T-42 → B8; T-43 → B6/B3; T-61, T-62, T-63 → B10 (host) plus B4; T-59 → B9 |
| TM-C9 Missing rows | **applied** | Rows A–I added as **T-80..T-88** (see §4); M-8 folded into T-48, M-9 into T-39 |
| TM-C10 Cross-references | **partially applied — the rest is not mine** | The defect is recorded in the THREAT_MODEL "Coverage and honesty statement" so a reader is warned. `docs/ADRs/ADR-018.md` is owned by the Enterprise Architect / build-e07 and is outside my write scope; RAID id/type alignment for O-110 belongs to the ledger owner. Both are proposed in §7 |
| TM-C11 "See also" links | **applied** | Replay family (T-08/T-31/T-43/T-45/T-80); duplicate orders (T-09/T-26/T-27); caps (T-34 exposure vs T-40 position, each saying it does not close the other); audit (T-12/T-16/T-74..T-79/T-86); cross-tenant (T-17/T-64, T-13/T-83); agency (T-02/T-28); credentials (T-05/T-59/T-69..T-73) |
| TM-C12 T-59 | **partially applied — the signature is not mine to give** | Test column stays `[Open: TC-AI-016..019 — O-79]`; the control column says the design is decided and **not built**, with no provider, terms or capability asserted; the footnote records that T-59 and the B9 wording originate in the chair's packet, that the chair recused, and that the IVA is asked to review the row with the Red-Team Lead |

### 3.2 SECURITY_PLAN (SP-C1..SP-C9)
| Condition | Status | What was changed |
|---|---|---|
| SP-C1 Four columns | **applied** (seven columns as the Board's own text specifies) | `Control · Target [Source: 06] · Delivered in dev/sim (tests, paths) · Gap [Open: id] · Target verifier · Current evidence · First gate` |
| SP-C2 Honest state per row | **applied** | All nine named rows rewritten with the delivered/gap split and the RAID ids of §2.2 (H-05, R-06/R-30, O-83/O-84/H-30, H-20/O-53/O-125..O-127, O-115/O-136/R-57, O-20/H-01/O-85/O-65, F-20/R-32/R-35, O-54/O-133..O-137, H-19) |
| SP-C3 Agent segregation row | **applied** | TC-AGT described as "roster consistency and the Edit/Write path only"; Bash limit, roster widening and guard-in-scope stated; control of record named as CODEOWNERS + branch protection + CI check, "none of which is complete"; first gate split B (guard rail) / C (control of record) |
| SP-C4 Missing rows | **applied** | All ten §2.3 rows added: durable control-state integrity; model-provider boundary; signing keys; scanner exceptions; platform-operator and platform-auditor principals; data handling and privacy-safe telemetry; replay defence; rate limiting per principal; Kill Switch listener isolation; environment-ladder enforcement |
| SP-C5 MCP registry and egress row | **applied** | Signed registry, `--production` refusal, stdio identity binding, per-tenant allowlists, network-policy checker, revocation drill; evidence = the `verify_tool_registry.py` output quoted in the Board packet §0.4 plus TC-AI-005/010/011, TC-AI-012..015, TC-NET, TC-SIG |
| SP-C6 Data-handling cross-reference | **applied** | New row linking retention, legal hold, subject rights and telemetry redaction to PRIVACY_IMPACT, with DPIA `[Open: O-10]` and erasure-against-an-append-only-chain `[Open: O-135]` |
| SP-C7 Distribution row tag | **applied** | "signing [Open: O-23]" replaced by `[Open: D-054 → O-83; H-30]`; TC-PKG-005 added |
| SP-C8 Rows derived from Board packets | **applied** | Model-provider boundary and signing-key custody drafted by the Security Architect from D-052 and D-053/ADR-019; the provenance section records the chair's recusal and asks the IVA to review both rows alongside the MCP Security Agent |
| SP-C9 Reviewer signature | **applied as far as the author can** | The header names the MCP Security Agent and the expected packet path, marked `[Open: not yet written]`. The signature itself is the reviewer's act, and AEI row 2 must not be signed before it exists |

### 3.3 Conditions not applied, and why
1. **TM-C10 (ADR-018 cross-reference correction)** — `docs/ADRs/` is not in this role's write scope and the ADR's author is the Enterprise Architect / build-e07. Recorded in the document and proposed as a RAID row (§7). Also not applied by me: the RAID id/type alignment for O-110 (ledger owner).
2. **TM-C12 and SP-C9 signatures** — a reviewer signature is a reviewer's act. Applied only to the extent of naming the reviewer, the expected packet and the `[Open]` state.
3. **Nothing else was declined.**

### 3.4 Amendments to the Board's proposed row text (§4.1/§4.2), and why
| Board text | Amendment | Reason |
|---|---|---|
| Row G "Durable, anchored audit store before shadow (B-5, O-54) … durable-audit quartet [Open: B-5]" | Rewritten as **T-86**: remediated in dev/sim by ADR-020/D-062, tests **TC-AUD-006..009 exist and pass**; residuals are the deployment anchor principal (O-54) and O-135 | The Board reviewed before B-5 landed; leaving the row as an open gap would understate the delivery and misstate the test position |
| Row A/B target text | Cites D-061 (6) and O-128 as decisions, not as Board recommendations | The Product Owner decided after the packet was written |
| T-61 control column "[Open: O-110 — Board recommendation §3.1]" | "[Open: O-110, O-128]" with the delivered/undelivered halves separated | Same reason; and the row must not read as if the anchoring is built |
| T-48 "[Open: roster narrowing]" | "[Open: roster narrowing, O-131]" | O-131 now exists in RAID as the E-1 resolution |
| — | **Additional corrections not asked for by the Board**: T-13's test column (v1.0 cited TC-AI-004, which is the revocation-recovery case and evidences neither egress nor canary tokens → now TC-AI-003, TC-AI-005, TC-TEN-003); T-11 and T-35 (the MCP handler deadline exists in code but **no test covers the timeout** — TC-AI-010 covers handler errors only [Verified: RAID R-20 remediation row and `docs/TEST_CASES/TC-AI.md`]) | The hard rule "never claim a control that has no test" applies to every row, not only to the rows the Board sampled |

## 4. Rows added or rewritten
**Added (TM-C9).** T-80 revocation/nonce journal line deleted or rewritten (M-1) · T-81 restore of the control store without its journals is a replay (M-2) · T-82 platform-wide human action through a header or CLI identity (M-3) · T-83 platform-auditor unfiltered read as exfiltration or an unmapped transfer (M-4) · T-84 pending Kill Switch deactivation with no TTL (M-5) · T-85 store-lock starvation denies the cancel path (M-6) · T-86 control state without its audit trail (M-7, now remediated in dev/sim) · T-87 forged or replayed regulatory report (M-10) · T-88 licensed field leaving the entitlement boundary (M-12).

**Rewritten.** T-04, T-05, T-06, T-07, T-10, T-11, T-12, T-13, T-14, T-15, T-16, T-17, T-18, T-19, T-21, T-22, T-23, T-24, T-25, T-29, T-34, T-35, T-37, T-39, T-40, T-42, T-43, T-48, T-58, T-59, T-60, T-61, T-62, T-63, T-68, T-69, T-72, T-73, T-76, T-77 — plus header, boundary line, a new "Coverage and honesty statement" and the provenance footnote.

**M-11 not made a threat row** [Committee: the Board's own instruction]: whether `build_sim_platform(second_tenant=True)` is refused outside dev/sim was not verified, so it is a gap for the ledger (§7) and appears only as a gap cell in the SECURITY_PLAN environment-ladder row, never as a claimed control.

**SECURITY_PLAN**: all twelve v1.0 rows rewritten and eleven rows added (23 rows total).

## 5. Threat-model delta (summary for the RTM and the AEI reader)
| Delta | Rows | Boundary | Evidence state |
|---|---|---|---|
| Signing (ADR-019/D-060) reflected in rows that mention keys | T-05, T-29, T-39, T-45, T-69..T-73 | B4, B5, B6, B8 | TC-SIG-001..004 exist and pass; ceremony, production key and registry re-signing [Open: H-20, O-127] |
| Audit (ADR-020/D-062) reflected in rows that mention the chain or the store | T-07, T-12, T-16, T-74..T-79, T-86 | B4, B10 | TC-AUD-001..009 exist and pass; WORM medium and deployment anchor principal [Open: O-54] |
| Store integrity (O-110 → O-128) | T-61, T-62, T-63, T-80, T-81, T-85 | B4, B10 | TC-DUR-001..004 exist; **journal-head anchoring not implemented** [Open: O-128]; consistent rewrite untested [Open: RT-05] |
| New boundaries | B9, B10, B11 | — | DATA_FLOWS mirror owed [Open: O-129] |

## 6. Control quartet for the critical control that changed this week
**Control: control-store journal head anchored in the audit chain (O-128, the resolution of O-110).** Not built; this is the quartet owed **before** the code, per the Board's §3.1 and D-061 (5). No test id is claimed; ids are for the builder to allocate.
- **Positive** — a control-table transaction commits, a `store.journal.sealed` audit event carries the sequence, the head digest and the correlation id; after a restart `verify()` matches the journal head to the last sealed event and the platform serves.
- **Negative** — the journal head does not match the last sealed event → the store is refused (`StoreIntegrityError`), nothing reaches a broker, the catalogued S1 alert fires.
- **Abuse** — rows *and* journal are rewritten consistently while the audit chain is untouched → refused; a stale backup is restored → refused because the anchor no longer matches; an attempt to seal over a contradicting head → refused (already evidenced for the audit side by TC-AUD-007/008).
- **Recovery** — the audit store is restored from the anchored replica, `verify()` passes, and the incident and its recovery are audit rows sharing one correlation id (the shape TC-AUD-009 already proves for the audit chain).
Residual after the control exists: the window since the last seal; the strength of the off-box anchor (O-54); in dev/sim both stores still sit on one host under one principal, so the residual stays "tamper-evident against inconsistent edits only" — acceptable in dev/sim (D-058 b), not beyond. **The author of this quartet is not its approver.**

## 7. Rows proposed for ledgers this session may not edit
**docs/RAID_LOG.md** (owner: Program Orchestrator / Product Owner delegate; ids by the owner)
| Type | Proposed text | Owner | Gate |
|---|---|---|---|
| Gap | `docs/ADRs/ADR-018.md` §Threat-model delta cites T-52..T-54; the rows are **T-60..T-62** (T-52..T-54 are the legal-record rows). An AEI reader following the ADR lands on the wrong threats (TM-C10) | Enterprise Architect / build-e07 | B |
| Gap | No test covers the MCP handler timeout (`future.result(timeout=spec.timeout_s)` → `mcp.handler_timeout`); TC-AI-010 covers handler errors only. THREAT_MODEL T-11 and T-35 and SECURITY_PLAN now say so (R-20 residual) | Backend Lead / SRE Lead | C |
| Gap | `TC-SEC-001` (secret custody), `TC-PERF-004` (rate limit and denial of service) and `TC-SC-001..003` are cited by THREAT_MODEL rows and do not exist; the Board asked for gap rows for the first two (TM-C3) | Security Architect / SRE Lead / Cloud Architect | B/C |
| Gap | Test ids allocated in THREAT_MODEL v1.1 with no test behind them: TC-CP-013 (legal-hold release abuse), TC-SEC-004 (Kill Switch listener isolation), TC-KS-011 (liquidation-policy fallback) | Backend Lead | C |
| Gap | THREAT_MODEL v1.1 declares boundaries B9, B10, B11; DATA_FLOWS v1.1 must mirror them (model gateway flow, host/file flow, DF-05 command authorisation and oracle, residency notes on DF-01/DF-02) | Data Architect | B |
| Risk | O-79 describes the model gateway as "ADR-018"; ADR-018 is the durable control store. The model-gateway decision is D-052 and no ADR exists for it | Security Architect / Enterprise Architect | B |
| Note | O-110 is typed "Risk" under an O- id; align the type or the id (TM-C10) | Program Orchestrator | B |

**docs/DECISION_LOG.md** — nothing proposed. D-061 already records the Product Owner's position on both documents; this session records no decision and no approval.

**docs/REQUIREMENTS_TRACEABILITY.md** (owner: Program Orchestrator) — proposed rows, one per new control-bearing gap:
| Requirement | Architecture | Owner | Control | Test | Evidence | Gate |
|---|---|---|---|---|---|---|
| NFR-SEC-01 (integrity of control state) | `rtcore.store` journal head anchored in the audit chain (O-128) | Security Architect (design) / Backend Lead (build) | fail-closed `verify()` against the last seal | quartet of §6 [Open] | ADR-018, ADR-020, this packet | C (shadow) |
| NFR-AUD-01 (immutable audit) | durable audit on the seam with an external anchor chain (ADR-020) | SRE Lead | no update/delete path; anchor comparison fails closed | TC-AUD-006..009 | `docs/TEST_CASES/TC-AUD.md` | B (dev/sim), C (deployment witness) |
| NFR-SEC-02 (signing) | public trust set, verify-only handles, overlap-then-retire (ADR-019) | Security Architect | algorithm allowlist, domain separation, absolute retirement | TC-SIG-001..004 | `docs/TEST_CASES/TC-SIG.md` | B (code path), C (ceremony) |
| NFR-TEN-01 (tenant isolation) | server-side tenant binding, per-tenant allowlists | Backend Lead | forged header refused and audited | TC-TEN-001..004 | `docs/TEST_CASES/TC-TEN.md` | B |

**docs/AUDIT_EVIDENCE_INDEX.md** (owner: Program Orchestrator; reviewer columns filled by the reviewing role, never by the author) — proposed row 2 text once the reviewer has signed: `Threat model — v1.1 at commit <hash of this branch's head>; reviewer: Red-Team & Pen-Test Lead (agent) — REVIEW_<date>_threat_model_red_team.md; Board: RECOMMEND ACCEPT WITH CONDITIONS (COUNCIL_2026-09-08_gate_B_spb_docs §1.7); agent approval — human PO decision pending`. **Row 2 must not be signed on v1.0, and must not be signed at all until the reviewer packet exists.** A separate row for SECURITY_PLAN v1.1 with the MCP Security Agent as reviewer.

## 8. What remains [Open], and why
| Item | Why it is still open | What would settle it |
|---|---|---|
| Reviewer signatures on both documents | A reviewer signature is a different-line act; neither packet exists | `REVIEW_<date>_threat_model_red_team.md` and `REVIEW_<date>_security_plan_mcp_security_agent.md` citing this commit and listing each condition met/not met (D-061 §5.2) |
| Twenty threat rows and twelve plan rows carry a test that does not exist | Dev/sim build state; Gate B authorises dev/sim only | The named quartets being written; until then no gate report may say the control set is verified |
| O-128 journal-head anchoring | Decided (D-061 (5)), audit half delivered (D-062), the anchoring itself not implemented | The quartet of §6 and the build; before shadow |
| O-54 anchor principal, O-133 cadence, O-134 runbook | Deployment identity and operational values need infrastructure and a decision, not code | H-05 spend, the O-54 decision, the retention rules |
| H-20 key ceremony, O-127 registry re-signing, O-126 trust-set distribution, O-125 verifier performance | Human acts and infrastructure | H-20 with three named humans; then the registry re-signed under a real key |
| H-10 external pen-test and red team, RT-05 | Not contracted; and the Security Architect must not scope and sign off the same test | Procurement (H-10) and a scope written by the Red-Team Lead |
| ADR-018 cross-reference, O-110 id/type, DATA_FLOWS mirror, O-79's "ADR-018" mis-citation | Owned by other roles | The rows proposed in §7 |
| Whether `second_tenant=True` is refused outside dev/sim (M-11) | Not verified by the Board, not verified here | One negative test (O-123) |
| Erasure and legal hold against an append-only audit chain | No mechanism exists (payload minimisation or crypto-shredding) | Privacy Lead and Compliance Agent (O-135); DPIA (O-10) |

## 9. Evidence list mapped to docs/
| Claim in v1.1 | Evidence |
|---|---|
| Signing controls | `docs/TEST_CASES/TC-SIG.md` (TC-SIG-001..004), `docs/ADRs/ADR-019.md`, `security/signing/README.md`, `security/signing/trust_set.schema.json`, `security/signing/ceremonies/TEMPLATE.md` |
| Audit durability and witness | `docs/TEST_CASES/TC-AUD.md` (TC-AUD-001..009), `docs/ADRs/ADR-020.md`, `docs/ALERT_CATALOG.md` (`audit.anchor_missing`) |
| Control-state durability | `docs/TEST_CASES/TC-DUR.md`, `docs/ADRs/ADR-018.md` |
| Tenant isolation | `docs/TEST_CASES/TC-TEN.md`, `docs/RED_TEAM_PLAN.md` RT-03 |
| Registry, transport, egress | `docs/TEST_CASES/TC-AI.md`, `TC-NET.md`, `scripts/verify_tool_registry.py` output in COUNCIL_2026-09-08_gate_B_spb_docs §0.4 |
| Distribution | `docs/TEST_CASES/TC-PKG.md` |
| Agent guard rail (never segregation evidence) | `docs/TEST_CASES/TC-AGT.md`, `docs/SESSIONS/PROBE_O58_2026-09-08.md` |
| Scanners and exceptions | `.github/workflows/ci.yml`, `security/scan_exceptions.yaml`, `scripts/check_scan_exceptions.py`, `security/sbom/sbom.cdx.json` (unsigned) |
| Conditions applied | `docs/SESSIONS/COUNCIL_2026-09-08_gate_B_spb_docs.md` §1.7, §2.5, §4; `docs/DECISION_LOG.md` D-061 |

## 10. Concerns for the Product Owner

- **SA-PO-1 Neither document is accepted, and neither says it is.** [Verified] Both headers read "v1.1 — reviewed, Board recommendation issued, decision pending". D-061 records your position, but it also says no document status changes to "accepted" until its new version *and* its reviewer signature exist. The Red-Team & Pen-Test Lead has not signed the threat model and the MCP Security Agent has not signed the security plan. **Decide:** commission those two review packets now, and do not let AUDIT_EVIDENCE_INDEX row 2 be filled before they exist.
- **SA-PO-2 The store-integrity decision is now half-built, and the half that is missing is the half that protects the store.** [Verified: no journal-head anchoring exists in the code] D-061 (5) chose Option B: anchor the control-store journal head into the audit chain. D-062 delivered the audit chain and its external witness. Nothing yet anchors the *control store's* journal head into it, so T-61 remains "tamper-evident against inconsistent edits only". **Decide:** treat the O-128 build (with the quartet in §6 written first) as a shadow entry condition and accept that O-54 and the anchor cadence (O-133) become load-bearing with it.
- **SA-PO-3 Twenty threat rows and twelve plan rows name a test that does not exist.** [Verified] That is the honest state of a dev/sim build and does not block Gate B, which authorises nothing beyond dev/sim. It does mean **no gate report, board minute or investor-facing statement may say the threat model or the security plan is covered by tests**. **Decide:** accept that wording constraint explicitly, so nobody has to interpret it later.
- **SA-PO-4 I own two documents whose residual risk I am not allowed to accept, and one of the largest residuals is mine to build.** [Committee: the role's own constraint] The Security Architect authored these rows, proposes the O-128 design and would scope RT-05 — the very test that would prove or disprove T-61. **Decide:** name a different seat to accept the residual risk of the store-integrity control and to sign off RT-05, or record that the external pen-test supplier (H-10) does both.
- **SA-PO-5 The agent guard is editable by the agents it guards, and that is now written into both documents.** [Verified: roster at 1e8555e] Bash writes are uninspected and are the default path under harness auto mode; the guard modules and the protected service paths sit inside every builder's roster scope; CODEOWNERS handles are placeholders and branch protection is off. D-061 (11) resolved this as "replace, not extend" (O-131). **Decide:** record the acceptance for dev/sim explicitly as a decision rather than as an implicit state, with the roster narrowing and the CI path-ownership check due before Gate B sign-off.
- **SA-PO-6 Three ADR and ledger cross-references point readers at the wrong thing, and I cannot fix them.** [Verified] ADR-018 §Threat-model delta cites T-52..T-54 for what are T-60..T-62; RAID O-79 calls the model gateway "ADR-018", which is the durable control store; O-110 is typed "Risk" under an O- id. Each is a one-line fix by its owner (§7). **Decide:** route them, because an auditor following an ADR to the wrong threat row is a finding about the record, not about the code.
- **SA-PO-7 The model-provider boundary is a decided design with nothing built and nothing signed.** [Verified] D-052 decided the posture; no gateway service, no provider, no terms, no region mapping and no TC-AI-016..019 exist, and the Model Risk Committee has not been heard (O-101). The plan row says so in those words. **Decide:** keep "no provider is wired before the Board sees signed terms and the region mapping" as a hard gate, and note that nothing in these documents asserts any provider's capability, retention policy or price.
- **SA-PO-8 A platform auditor is a cross-tenant reader by construction, and its envelope is unwritten.** [Committee: D-059, D-061 (7)] T-83 and the platform-principals plan row state the envelope as a target: audited unfiltered reads, pseudonymised payloads, residency answered by the DPIA. No jurisdiction's law is asserted anywhere. **Decide:** have the Privacy Lead write the envelope before any build, and treat the residency question as open (O-10).
- **SA-PO-9 Two documents changed; four other artefacts still carry the old picture.** [Verified] DATA_FLOWS v1.0 does not know boundaries B9/B10/B11 or the ADR-015 command authorisation; PRIVACY_IMPACT has no platform-auditor row; `docs/SBOM.md` still says artefacts are "Signed by: release key" when the SBOM is unsigned; the evidence report of record was generated on a moving tree (O-65). **Decide:** sequence those with DATA_FLOWS v1.1 (O-129) so the Gate B evidence set is internally consistent — a reviewer who compares the two boundary lists today will find them different.
- **SA-PO-10 Nothing in this session promoted anything.** [Source: 12] Every statement is dev/sim; no threshold, regulatory status, licence, broker capability or vendor term is asserted; every such point is `[Open]` with the human act or decision that would settle it. Profit remains an objective, never a promise [Source: 00].

## 11. Assumptions, confidence, provenance
- A-1 [Committee]: D-061 governs the status convention; the reviewer signature, not the decision entry, is what unlocks "accepted".
- A-2 [Verified]: ADR-019 and ADR-020 landed after the Board reviewed; TC-SIG-001..004 and TC-AUD-006..009 exist in `docs/TEST_CASES/` and in `test/quartets/`.
- A-3 [Verified]: no control-store journal-head anchoring exists at this commit (searched `libs/core/rtcore/store.py`, `services/audit/`, `apps/web/web_bff/platform.py`).
- A-4 [Open]: whether `build_sim_platform(second_tenant=True)` is refused outside dev/sim — not verified here either.
- A-5 [Open]: whether every remaining v1.0 row that this session did not sample cites a test that exists; the id-existence check was re-run for every id newly asserted in v1.1 and for the ids the Board named, not for the whole tree a second time.
- Confidence: **high** that TM-C1..C9, C11 and SP-C1..C8 are applied as written; **high** that no row now claims an unevidenced control among the rows checked; **medium** that no further missing threat exists (the code of the store, the audit chain, the signing modules and the guard was read; not every service).
- Provenance: every `[Verified]` statement is a file read or a command run on 2026-09-08 in this worktree; every `[Committee]` statement is a council position or a ledger entry cited by name; every vendor, regulatory, infrastructure or pricing point is `[Open]`. This packet records no approval and no decision.
