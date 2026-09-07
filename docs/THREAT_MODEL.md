# THREAT_MODEL

| Owner | Reviewer (different line) | Approving body | First gate | Status |
|---|---|---|---|---|
| Security Architect | Red-Team & Pen-Test Lead | Security & Privacy Board | B | Draft v1.0 |

## Trust boundaries [Committee]
B1 user↔BFF · B2 BFF↔services · B3 Analytics↔Control plane · B4 Control↔Execution plane · B5 Execution↔broker · B6 MCP server↔tool · B7 data provider↔ingest · B8 CI↔production.

## Threats [Source: 06] → control → test → owner
| ID | Threat | Boundary | Control | Test ID | Owner |
|---|---|---|---|---|---|
| T-01 | Prompt/tool injection | B6 | Provenance labels, delimited untrusted text, allowlisted tools, output schema | TC-AI-002/003 | MCP Security Agent |
| T-02 | Excessive agency | B3, B6 | Write-class tool writes to queue only; no broker route | TC-NET-003 | MCP Security Agent |
| T-03 | Poisoned market data | B7 | Source contracts, outlier policy, cross-source check, freshness | TC-MD-003 | Data Architect |
| T-04 | Model supply-chain compromise | B8 | Signed model artefacts, registry, SBOM | TC-SC-002 | Model Risk Lead |
| T-05 | Credential theft | B5 | Vault/HSM, workload identity, rotation, no secrets in agent context | TC-SEC-001 | Security Architect |
| T-06 | Account takeover | B1 | MFA/passkeys, session controls, anomaly alerts | TC-ID-003 | Backend Lead |
| T-07 | Insider misuse | B2 | Separation of duties, PIM, maker-checker, immutable logs | TC-ID-004 | Security & Privacy Board |
| T-08 | Replay | B3, B4 | Signed intents with expiry, idempotency | TC-EX-003 | Integration Architect |
| T-09 | Duplicate orders / race | B4, B5 | Executor lease + fencing token | TC-EX-002/004 | Integration Architect |
| T-10 | Dependency compromise | B8 | SCA, signed images, SBOM | TC-SC-001 | Cloud Architect |
| T-11 | Denial of service | B1, B7 | WAF/DDoS, backpressure shedding analytics first | TC-PERF-004 | SRE Lead |
| T-12 | Audit tampering | all | WORM, hash chain, restricted delete (none) | TC-AUD-003 | SRE Lead |
| T-13 | Data exfiltration | B6, B2 | Egress allowlist, canary tokens, tenant isolation | TC-AI-004, TC-TEN-003 | Security Architect |
| T-14 | Client-asserted human identity, role, MFA and PIM in the BFF (`X-Actor-*` headers; hard-coded `mfa_enrolled`/`privileged_until`) [Committee: REVIEW_C5 OBJ-1] | B1, B2 | Interim: non-human roles refused on the human path, start refused outside `RT_ENV=sim`; target: OIDC/mTLS session with PIM window from the IdP (R-06) | TC-E2E-AUTH (interim); TC-ID-005/006 [Open] | Backend Lead / Security Architect |
| T-15 | Two-person / maker-checker bypass by one human presenting a second actor id and line [Committee: REVIEW_C5 OBJ-2] | B1, B2 | Compare authenticated subject plus session; distinct humans, distinct sessions (R-30) | TC-ID-007, TC-AP-005 [Open] | Backend Lead / Chief Risk Agent |
| T-16 | Audit tail truncation, in-process list mutation, backdated events [Committee: REVIEW_C5 OBJ-3] | all | Sealed chain head (`AuditStore.seal` / `verify(anchor=)`), monotonic timestamps; off-box anchor [Open] (R-31, D-024) | TC-AUD-005 | SRE Lead / Security Architect |
| T-17 | Cross-tenant reads: BFF queries carry no tenant predicate; tenant is not an authenticated claim [Committee: REVIEW_C5 F-08] | B2 | Tenant predicate on every read; tenant from the session; tenant-qualified limits (delivered) (R-22) | TC-RK-018 (limits); TC-TEN-001..004 [Open] | Backend Lead |
| T-18 | `ActorKind`/role spoof — in-process construction of a HUMAN actor by agent code [Committee: REVIEW_C5 F-09] | B3, B6 | Bind kind to credential at every control boundary (R-33; depends on R-06) | TC-ID-008 [Open] | MCP Security Agent / Backend Lead |
| T-19 | Agent or unauthorised actor disables a live jurisdiction flag (market access switched off) [Committee: REVIEW_C5 F-10] | B7 | `disable_flag` requires a human Compliance/Legal role (delivered, R-33) | TC-CP-007 [Open] | Compliance Agent / Backend Lead |
| T-20 | NetworkPolicy allow-union grants MCP pods the namespace-wide analytics egress [Committee: REVIEW_C3 F-19, REVIEW_C5 F-11] | B4, B6 | MCP pods excluded from the broad rule; effective-union checker (delivered, R-18) | TC-NET-003; cluster conformance [Open: H-05, O-42] | Security Architect / Cloud Architect |
| T-21 | Execution-plane egress to the whole internet; DNS tunnelling; edge reads the execution plane [Committee: REVIEW_C5 F-12] | B5, B6 | Per-adapter broker CIDRs (placeholder delivered; checker refuses 0.0.0.0/0); DNS monitoring [Open] (R-32) | TC-NET-006 [Open] | Cloud Architect |
| T-22 | Stored XSS / log injection via actor id and free-text reason [Committee: REVIEW_C5 F-05] | B1 | Output encoding in the console (delivered); CSP and control-character stripping [Open] (R-34) | TC-SEC-003 [Open] | Frontend Lead / Backend Lead |
| T-23 | Legal-hold scope miss causing fail-open deletion; unauthorised hold release [Committee: REVIEW_C5 F-18] | B2 | Enclosing-scope hold match; no schedule → suppressed; human Legal/Compliance release (delivered, O-09, D-025) | TC-CP-006; TC-CP-008 [Open] | Privacy Lead / Legal Agent |
| T-24 | Redaction misses account/customer ids, IBAN, IP, payloads, reasons [Committee: REVIEW_C5 F-19] | B2 | id/IBAN/IP patterns (delivered); structured field-level redaction [Open] (R-35) | TC-OB-002 (not yet extended) [Open] | SRE Lead / Privacy Lead |
| T-25 | Intent-flood audit amplification without a rate limit [Committee: REVIEW_C5 F-06] | B1 | Per-principal rate limit; no audit of pre-validation floods [Open] (R-35); MCP path: deny bucket plus quota (delivered) | TC-PERF-004 [Open]; TC-AI-003 (MCP quota) | SRE Lead |
| T-26 | Second live order for one intent via policy-version re-evaluation or Control-plane replay [Committee: REVIEW_C2 OBJ-1] | B4 | Gateway per-intent live-order invariant with S1 alert; reconciliation groups live orders by intent (R-02, ADR-014, D-015) | TC-EX-007, TC-RC-003 | Integration Architect / Backend Lead |
| T-27 | Ambiguous submit failure: resubmit to a non-deduping broker duplicates; the orphan is never cancelled [Committee: REVIEW_C2 OBJ-2] | B5 | Broker query before resubmit; local cancel of never-seen orders; STATUS breaks (R-09, ADR-014, D-016) | TC-EX-008, TC-RC-005 | Backend Lead / Broker-Connector Lead |
| T-28 | Agent-callable `run_simulation` reaches live monitoring/execution state (global guard, alert hook, deny evidence) [Committee: REVIEW_C3 OBJ-1] | B6, B3 | Private per-platform `PlaneGuard`; template/strategy/version validation (ADR-013, R-16, D-027); worker isolation [Open] | TC-AI-006 | MCP Security Agent / Backend Lead |
| T-29 | Registry trust root: a forged registry signed with the public dev key accepted; signature issued before approval [Committee: REVIEW_C3 OBJ-2; C03 packet local "T-18"] | B8, B6 | Dev key only in explicit dev/sim; envelope-signed metadata; fixture flag; CI asserts production refusal (O-22, O-35); KMS asymmetric key [Open] | TC-AI-005, TC-AI-010 | MCP Security Agent / Security Architect |
| T-30 | Tenant-wide revocation as denial of service by a low-privilege agent; alert storm; silent no-op auto-actions [Committee: REVIEW_C3 OBJ-3; C03 packet local "T-19"] | B3, B6 | Scoped grant revocation; denials counted against quota; `alert.autoaction_failed` S1 (R-17, D-018) | TC-AI-003, TC-OB-005 | Backend Lead / SRE Lead |
| T-31 | Replay of a signed tool call within the token TTL (tool-call layer of T-08) [Committee: REVIEW_C3 F-01] | B6, B3 | Nonce plus issued_at in the signature; per-token nonce cache; queue refuses a replayed `intent_id` (R-15, D-019) | TC-AI-009, TC-RK-015 | Backend Lead / Integration Architect |
| T-32 | Kill Switch engagement failure: a hook exception leaves the switch disengaged and unrecorded [Committee: REVIEW_C4 Objection 1] | B4 | Persist-first activation; per-hook failure capture; `killswitch.hook_failed` S1 (R-23, D-020) | TC-KS-007 | Backend Lead / SRE Lead |
| T-33 | Fail-open defaults after the risk decision (missing snapshot → LIVE, unknown mode → LIVE, stale snapshot, tenant mismatch) [Committee: REVIEW_C4 Objection 2] | B2, B4 | Explicit mode→target map; re-decision at approval; snapshot age, tenant and NAV checks (R-24) | TC-RK-018, TC-RK-019 | Backend Lead / Chief Risk Agent |
| T-34 | Exposure-cap evasion by splitting orders across instruments; trapped over-limit book [Committee: REVIEW_C4 Objection 3] | B3 | Open orders projected into exposure; risk-reducing exemption (R-25, D-022; TRC decision O-46) | TC-RK-017 | Backend Lead / Trading Risk Committee |
| T-35 | Hung MCP handler blocks the BFF event loop including `/v1/killswitch` [Committee: REVIEW_C3 F-05] | B1, B6 | Pre-emptive handler deadline; BFF calls the runtime off the event loop (R-20); isolated Kill Switch listener [Open] | TC-SEC-MCP [Open] | Backend Lead / SRE Lead |
| T-36 | Halt/restore cycle used as an ungated promotion; agent sets trading status or halts an account [Committee: REVIEW_C4 F-02, F-03] | B2 | Restore ceiling = enabled feature, never autonomy; human-only status/halt (R-28, D-021) | TC-KS-004; agent abuse case [Open] | Backend Lead |
| T-37 | Liquidation executed under an unapproved `liquidation_policy_ref` [Committee: REVIEW_C4 F-01] | B4 | Approved-policy registry gate with CANCEL_ONLY fallback (R-27); maker-checker on the fields [Open: O-08] | fallback test without a TC id [Open] | Backend Lead / Trading Risk Committee |
Each row carries the control quartet (positive/negative/abuse/recovery) in TEST_CASES/. Rows T-14..T-37 are the committee review cycle 1 delta (2026-09-07): local threat IDs in the review packets map to these via docs/RAID_LOG.md §Review ID renumbering map; a test ID marked [Open] does not exist yet. Delta compiled by the Delivery Orchestrator (AI); reviewer: pending (Red-Team & Pen-Test Lead); approver: pending (Security & Privacy Board).
