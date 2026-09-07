# REVIEW — C5 Security & Privacy, C1/E01 Identity, C9/E12 Observability, E11 Audit

> Editorial note (Delivery Orchestrator, 2026-09-07): IDs allocated in this review are local to it; the global IDs are in docs/RAID_LOG.md §Review ID renumbering map. The reviewer's text below is unchanged.

CHALLENGE and threat-model-delta session. Findings only; no code changed. Read-only PoCs run against
the in-process `TestClient` build. `python3 -m pytest test/quartets/test_tc_id_identity.py
test_tc_aud_audit.py test_tc_ob_observability.py -q` → all pass; `secret_scan.py` → "OK … 0 files"
(false green, see F-13); `check_network_policies.py` → OK (misses F-11).

---

## 1) Roles

| Function | Line | Held here | Independence caveat |
|---|---|---|---|
| Security Architect (design owner of THREAT_MODEL.md, SECURITY_PLAN.md, security/) | 1st | This review | Independent of Backend Lead who built the code |
| Red-Team & Pen-Test Lead (adversarial assurance) | 3rd | This review | May not remediate; may not join delivery |

Conflict note [Committee]: one author holding a 1st-line design role and a 3rd-line assurance role is a
separation-of-duties compression. Per goal 13 ("may not accept your own residual risk") and goal 23
("may not remediate findings yourself"), this packet **proposes** findings and threat-model deltas; it
does **not** self-accept residual risk and does not sign off remediation. The Security & Privacy Board
plus Independent Validation must ratify. Recorded as RAID A-SEC-00.

## 2) Purpose

- Threat-model every trust boundary B1–B8 and map blueprint-06 threats T-01..T-13 to control/test/owner. **[Source: 06]**
- Challenge C5 (security/privacy), C1/E01 (identity, modes, maker-checker), C9/E12 (observability, redaction), E11 (audit) from a different line than the builder. **[Committee]**
- Attack the implemented dev/sim build adversarially (injection, escalation, tenant, replay, audit, supply chain) and produce a threat-model delta and RAID. **[Source: 06, 11]**
- Residual/undecided items are tagged **[Open]** and pushed to RAID with owner + gate.

## 3) Three strongest objections

### OBJ-1 — Human authentication and MFA/PIM are fully client-asserted; separation-of-duties collapses. CRITICAL
**File:** `apps/web/web_bff/app.py:75-99` (`human()` and `require()`), `apps/web/static/index.html:63`.
**Boundary:** B1 (user↔BFF), amplifies B2, and defeats T-06/T-07.
`human()` trusts `X-Actor-Id`, `X-Actor-Role`, `X-MFA` headers with no signature, session, or IdP check
(`if x_mfa != "verified"` is a string the client sends). `require()` then builds
`User(..., mfa_enrolled=True, privileged_until=p.now.replace(year=p.now.year + 1))` and calls
`authorize(..., mfa_verified=True)` — i.e. it **hard-codes a one-year PIM elevation and a passed MFA for
every caller**, bypassing the entire RBAC+MFA+PIM control in `rbac.authorize` (`rbac.py:141-147`) that
C1/E01 relies on. The dashboard picks the actor from `localStorage` (default `risk_officer.demo`), so there
is no authentication at all.
**Exploit (red-team):**
```
# any client, no credential:
curl -XPOST /v1/killswitch -H 'X-Actor-Id: eve' -H 'X-Actor-Role: runtime_monitor' -H 'X-MFA: verified' \
     -d '{"level":"PLATFORM","target_id":"*","reason":"halt everything","actor":"eve"}'   # PoC2 -> 202
```
PoC confirmed: a header-declared `strategy_agent` submits an intent through the human path (202, bypassing
the MCP runtime's allowlist/quota/canary); a header-declared `runtime_monitor` activates a PLATFORM Kill
Switch (202); a header-declared `risk_officer` deactivates a Kill Switch — a `PRIVILEGED` permission —
with **no real elevation** (202, PoC3). The docstring calls this "dev/sim", but **nothing enforces that**:
`RT_ENV`/`RT_MCP_REGISTRY_KEY` are never read by the app, so the same binary in any environment accepts
these headers.
**Remedy:** (a) fail-closed refusal to start unless a real IdP/mTLS session verifier is wired when
`RT_ENV != sim`; (b) derive actor identity, roles, MFA and PIM window from a signed session/OIDC token,
never from request headers; (c) delete the hard-coded `mfa_enrolled=True`/`privileged_until=+1yr`; (d) put
this in MISSING_ACTIONS as a Gate-B blocking human action with a loud `RED_TEAM`/IVA retest gate.

### OBJ-2 — Two-person rules and maker-checker are bypassable by one human asserting a second actor-id. CRITICAL
**File:** `services/approval/approval_service/queue.py:81-89`; `services/killswitch/killswitch_service/service.py:127-139`; `services/identity/identity_service/accounts.py:132-138`; `services/reconciliation/reconciliation_service/tickets.py:63-66`. All fed by `app.py:88` where `actor_id` = `X-Actor-Id`.
**Boundary:** B1→B2; defeats T-07 (insider misuse) and the C1 §1 / C11 two-person guarantees.
Every "author ≠ approver", "different line", and "two-person" check compares `actor.actor_id` and
`actor.line` — **both derived from attacker-controlled headers**. The same human sends the first action as
`X-Actor-Id: alice / risk_officer` and the second as `X-Actor-Id: alice2 / sre_lead`.
**Exploit (red-team):** PoC6 — the intent maker approves their **own** intent to `FILLED` by changing the
`X-Actor-Id` header on the approve call (200/FILLED). PoC3 — one human completes a two-person Kill-Switch
**deactivation** by presenting a second id and a different-line role header (`active: false`). The maker-
checker cooling period and `require_different_line` (`platform.py:544`) are real, but rest entirely on
identity the caller forges.
**Remedy:** bind actor identity to an authenticated principal (OBJ-1); additionally record and compare a
**verified subject** (IdP `sub`) plus a device/session, not a free-text id; enforce that maker and checker
resolve to distinct authenticated humans and distinct sessions; add TC-ID and TC-AP abuse cases that
attempt the same-human/two-id bypass.

### OBJ-3 — Audit is not tamper-evident against tail truncation, is mutable in-process, and accepts caller-supplied timestamps; no external WORM anchor. CRITICAL
**File:** `services/audit/audit_service/store.py:75-128,146-167`; append signature `ts: datetime | None` at `store.py:95,102`.
**Boundary:** all (T-12 audit tampering).
The hash chain detects payload edits and mid-chain deletion (seq gap), but **cannot detect truncation of
the tail**: dropping the last N events leaves a shorter, fully valid chain. PoC7: `verify(events[:-5]).ok ==
True`, and `store._events.pop()` succeeds then `verify().ok == True`. The "append-only" store is a plain
mutable Python `list` with a public `all()`/`_events`; there is no monotonic external counter, no signed
head-hash notarised off-box, and the file backend is opened `"a"` but the OS never enforces WORM. Worse,
`append(ts=...)` lets any caller **backdate or post-date** an event (PoC8 wrote an event dated 400 days ago
into a valid chain), and the kill-switch/approval free-text `reason` (client-controlled) is stored verbatim.
This means T-12's "restricted delete (none)" and the audit-immutability claim behind FR-16/NFR-AUD-01 are
**not met by the implementation**, and TC-AUD-003 gives false comfort because it never tests truncation.
**Exploit (red-team):** an insider (or a process with heap access after OBJ-1) trims the last events that
record a rogue order, or backdates a fabricated approval; `/v1/audit/verify` still returns `ok: true`, so
downstream monitoring (`alerts.yaml` `audit.chain_verification_failed`) never fires.
**Remedy:** (a) periodically anchor the head hash to an external WORM/notary (e.g. signed, sequence-stamped
checkpoints replicated per DR_PLAN) and verify **expected length ≥ last checkpoint**; (b) reject
caller-supplied `ts` (server clock only) or record both server-received and event ts and hash the server
ts; (c) make `_events` truly append-only behind an interface with no pop/slice write path; (d) add
TC-AUD-005 truncation-abuse and TC-AUD-006 backdating-abuse quartet cases.

## 4) Additional findings across trust boundaries B1–B8

**B1 user↔BFF**
- **F-04 `/process` silently discards the queue.** `app.py:152-158`: `pop()` loops until the id matches,
  permanently dropping every non-matching `ValidatedIntent`; guarded only by `VIEW_DASHBOARD` (a read
  permission gating a destructive drain). PoC4: three queued intents wiped by one bogus-id call. Integrity/DoS. **[Open]**
- **F-05 Stored XSS + log injection via `X-Actor-Id`.** `app.py:88` copies the header into `actor_id`;
  it surfaces unescaped as `maker_id` in `/v1/approvals` (`app.py` list_approvals) and is rendered with
  `innerHTML` in the dashboard (`index.html:77` `maker ${a.maker_id}`). PoC5 confirmed the `<img onerror>`
  payload is stored and echoed. No `Content-Security-Policy` header anywhere. Newlines in the id/reason are
  not stripped before logging (`rtobs/logging.py` redacts patterns but not control chars) → forged log
  lines. Error bodies echo the role header (PoC12: `unknown role <script>x</script>`). **[Open]**
- **F-06 No CORS policy, no rate limiting, audit amplification DoS.** No `CORSMiddleware` (default same-origin
  — make it explicit and deny cross-origin before cookie/session auth lands). `/v1/intents` has no throttle;
  PoC14: 200 malformed intents (all 400) still wrote **414 audit events** (tracker.create + REJECTED
  transition each audit) — an unauthenticated amplification channel that floods audit/log storage. T-11 DoS
  has no in-app control and no TC-PERF-004 test exists. **[Open]**
- **F-07 `/healthz` unauthenticated info leak.** `app.py:372` returns `audit_length` to anyone (PoC13). Minor. **[Open]**

**B2 BFF↔services / tenancy**
- **F-08 Tenant isolation is a hard-coded constant, and read queries are not tenant-scoped.** `app.py` pins
  `tenant_id=TENANT` everywhere (`:88,:93,:141,:308`). A header cannot set a different tenant **today** — but
  neither is tenant an authenticated claim, and the read paths have **no tenant predicate**: `get_decision`
  (`app.py:180-188`) scans **all** audit events; `account(account_id)` (`app.py:261`) returns any account by
  id; `audit_search`/`audit_export` filter only by `correlation_id`. The moment tenant becomes request-derived
  (multi-tenant, per plan NFR-TEN-01), these become cross-tenant reads. There is **no TC-TEN test at all**
  (T-13 references TC-TEN-003 which does not exist). RED_TEAM RT-03 cannot pass because the control is unbuilt. **[Open]**

**B3 Analytics↔Control / agent spoofing**
- **F-09 `ActorKind` is caller-declared.** `rtcore/lines.py:105-119`: any code can construct
  `Actor(kind=ActorKind.HUMAN, role=RISK_OFFICER)` and satisfy `is_human` (PoC11). The human-only guarantees
  in maker-checker (`makerchecker.py:48`), approvals (`queue.py:78`), kill switch (`service.py:72,122`) and
  jurisdiction (`jurisdiction.py:41`) rely on this field being trustworthy. In the BFF the agent path is sound
  (bearer→`ToolRuntime`, identity-bound account/strategy/tenant, `tools.py:52,103`), but the actor model
  itself has no cryptographic binding of kind→credential. **[Open]**
- **F-10 Agent actor can disable a live jurisdiction flag (dual-key rollback gap).** `jurisdiction.py:54-60`
  `disable_flag` performs **no `is_human`, role, or two-person check** — comment says "single person may
  disable (ROLLBACK_PLAN)". PoC10: an `ActorKind.AGENT` actor disabled a live cell (`is_live → False`),
  turning off market access. This contradicts blueprint-00 "AI/MCP … never … disable monitoring or bypass
  controls". Disabling market eligibility is a control action agents must never take. **[Open]**

**B4 Control↔Execution / B5 Execution↔broker (network)**
- **F-11 MCP egress restriction is nullified by policy union.** `analytics.yaml:11-25`
  (`analytics-allow-intent-queue`) selects `podSelector: {}` (**all** analytics pods, including the
  `component: mcp-server` pods) and allows egress to **every** analytics pod plus intent-queue plus DNS.
  Kubernetes NetworkPolicies are additive (allow-union), so the tighter `mcp-servers-egress`
  (`mcp-servers.yaml`) does **not** constrain MCP pods — they inherit the broad allowance. The intended "MCP
  reaches only market-data/strategy/backtest + intent-queue" (deep-dive C5, security/README) is not enforced.
  `check_network_policies.py:71-80` inspects only the mcp-server-labelled policy and reports OK, so the gate is
  falsely green. **[Open]**
- **F-12 Execution egress is 0.0.0.0/0, and edge reads the execution plane.** `execution.yaml:31`:
  `ipBlock cidr: 0.0.0.0/0 except RFC1918` on :443 — egress to the **entire public internet**, not an
  allowlist of broker CIDRs (the comment "allowlisted per adapter" is unimplemented). This is a data-
  exfiltration channel out of the plane that holds broker credentials (T-13). Separately, `execution.yaml:20-21`
  and `planes.py` (`EDGE→EXECUTION: api_read`) let the BFF read order/position state directly from the
  execution plane on :8444 — a B4 crossing the three-plane narrative does not advertise. Also DNS egress to
  kube-dns is allowed from analytics/MCP (`analytics.yaml:22-25`, `mcp-servers.yaml:16-18`) with no monitoring
  — a classic DNS-tunnelling exfil path. **[Open]**

**B8 CI↔production / supply chain**
- **F-13 Secret scan is weak and reports a false green on an uncommitted tree.** `scripts/secret_scan.py`
  scans only `git ls-files`; in this working tree nothing is committed, so it prints "OK … 0 files, no
  findings" — it scanned nothing. Pattern coverage misses: PKCS8 `BEGIN PRIVATE KEY` (no algo), GitHub `ghp_`,
  bare AWS `AKIA…` ids, JWTs, Google `AIza…`, Slack webhooks, and unquoted long secrets (all MISSED in a
  pattern test). The allowlist teaches it to ignore the dev registry key and the compose password. **[Open]**
- **F-14 SBOM is inaccurate and unsigned.** `scripts/generate_sbom.py` enumerates the **ambient installed
  environment** (69 comps incl `conan`, `dbus-python`, `PyGObject`, `launchpadlib` — OS packages, not app
  deps), not the pinned dependency closure; no component hashes, no signature, no vulnerability field.
  SBOM.md claims "signed" and "SCA" — neither happens. **[Open]**
- **F-15 CI is missing SAST, DAST, SCA, and artefact/image signing.** `.github/workflows/ci.yml` runs lint,
  typecheck, schema, policy-check, secret-scan, tests, SBOM-generate. SECURITY_PLAN.md:12, NFR-SEC-02,
  DEFINITION_OF_DONE.md:12 and DEPLOYMENT_RUNBOOK.md ("refuse unsigned") require SAST/DAST/SCA + signed
  images + "unsigned deploy refused". None is implemented; the generated SBOM is never scanned. T-04/T-10
  "signed images, SCA" have tests TC-SC-001/002 that **do not exist**. This is the RED_TEAM RT-06 objective
  (deploy unsigned image) and it would succeed. **[Open]**
- **F-16 Dependencies unpinned; build non-reproducible.** `pyproject.toml:10-17` all deps are `>=` floors,
  no lockfile, no hashes, `Dockerfile.bff:1` base image unpinned by digest, `pip install .` with no
  `--require-hashes`. Dependency-confusion / malicious-release exposure (T-10). **[Open]**
- **F-17 docker-compose plaintext password and unhardened data services.** `infra/docker-compose.yml:14`
  `POSTGRES_PASSWORD: sim-only` (allowlisted). The `bff` service is hardened (`read_only`, `no-new-privileges`)
  but `postgres` and `redpanda` are not; redpanda advertises a PLAINTEXT listener; ports are bound to the host.
  Acceptable only under a **loud** "sim-only, never a template for non-dev" label; the allowlist entry
  normalises ignoring a secret class. **[Open]**

**Identity/privacy (C1/C5)**
- **F-18 Legal-hold scope mismatch causes fail-open deletion; release is unauthorised.**
  `retention.py:56-66`: `holds_for(scope)` is an exact-string match, so a hold placed at **tenant** scope does
  **not** suppress a **customer**-scoped deletion (PoC9 — tenant hold, customer deletion → not covered), and a
  missing `(record_class, jurisdiction)` schedule defaults to `DELETED` (**fail-open** destruction).
  `release_hold(hold_id, released_by)` (`retention.py:49-51`) takes a self-asserted string, with **no actor,
  role, or two-person authorisation** — anyone can lift a litigation hold. Directly the O-09 risk. **[Open]**
- **F-19 Redaction gaps (NFR-PRV-01) leak account ids, payloads, reasons, and more.** `rtobs/logging.py:13-19`
  redacts only email, `Bearer`, `vault://`, 12–19-digit numbers, and quoted `secret/password/api_key/token`.
  PoC redact confirmed **not** redacted: account ids (`acct-sim-001`), customer ids, IBANs, phone numbers, IPs
  (despite PIA row "IP/user redacted"), JWTs, bare AWS keys, and **intent/strategy payloads**
  (`strategy_params … secret_sauce` passed through), and **kill-switch/approval free-text reasons** (which
  carry client names). Redaction runs on the message string only; structured `extra_fields` are stringified
  then pattern-redacted, so nested payloads mostly escape. **[Open]**

## 5) Threat-model delta

| ID | New/changed threat | Boundary | Missing/weak control | Test to add | Owner |
|---|---|---|---|---|---|
| T-14 | Header-asserted human identity/role/MFA (no IdP) | B1 | Signed session/OIDC + mTLS; refuse start in non-sim without verifier | TC-ID-005 (abuse: forged headers), TC-SEC-002 | Backend Lead / Security Architect |
| T-15 | Fake PIM elevation + MFA in BFF `require()` | B1,B2 | Derive `privileged_until`/MFA from IdP; drop hard-code | TC-ID-006 (privileged w/o elevation) | Backend Lead |
| T-16 | Two-person/maker-checker bypass via 2nd actor-id | B1,B2 | Compare authenticated subjects + sessions | TC-ID-007, TC-AP-005 (abuse) | Backend Lead / Chief Risk |
| T-17 | Audit tail truncation / mutable store / caller ts | all | External WORM anchor + length check; server-only ts; append-only iface | TC-AUD-005/006 | SRE Lead / Security Architect |
| T-18 | Tenant reads not scoped; tenant not an authn claim | B2 | Tenant predicate on every query; authenticated tenant | TC-TEN-001..004 | Backend Lead |
| T-19 | Agent/system actor spoof (`ActorKind` declared) | B3,B6 | Bind kind→credential; verify at control boundary | TC-ID-008, TC-AI-006 | MCP Security / Backend Lead |
| T-20 | Agent/non-two-person disables jurisdiction flag | B7,control | `is_human`+role+optional dual check on `disable_flag` | TC-CP-007 (abuse) | Compliance / Backend Lead |
| T-21 | MCP egress un-restricted via NetworkPolicy union | B4,B6 | Scope broad analytics policy off mcp-server pods; test union | TC-NET-005 | Security Architect / Cloud Architect |
| T-22 | Execution egress 0.0.0.0/0 (exfil) + DNS tunnel | B5,B6 | Broker CIDR allowlist; DNS egress monitoring | TC-NET-006, TC-TEN-003 | Cloud Architect |
| T-23 | Stored XSS / log injection via actor id & reason | B1 | Output-encode; CSP; strip control chars; no `innerHTML` | TC-SEC-003 | Frontend / Backend Lead |
| T-24 | Legal-hold scope miss → fail-open deletion; unauthorised release | B2 | Hierarchical scope match; default-suppress; authorise release | TC-CP-008 | Privacy Lead / Legal |
| T-25 | Redaction misses account/payload/reason/IP | B2,B9 | Structured field-level redaction allowlist | TC-OB-005 | SRE Lead / Privacy Lead |
| T-26 | Intent-flood audit amplification (no rate limit) | B1 | Per-principal rate limit; don't audit pre-validation floods | TC-PERF-004 | SRE Lead |
| T-27 | CI lacks SAST/DAST/SCA/signing; SBOM inaccurate | B8 | Add gates; scan SBOM; sign+verify images | TC-SC-001/002 | Cloud Architect |

## 6) Control-quartet gaps

| Quartet | Positive | Negative | Abuse | Recovery | Verdict |
|---|---|---|---|---|---|
| **TC-ID** (identity/maker-checker/mode) | TC-ID-001 | TC-ID-002 | TC-ID-003 | TC-ID-004 | Quartet present but **all rest on trusted `actor_id`/`ActorKind`**; add abuse cases T-14/15/16/19 (forged headers, fake PIM, 2nd-id bypass, kind spoof). Not "tested" until added. |
| **TC-AUD** (immutable audit) | TC-AUD-001 | TC-AUD-002 | TC-AUD-003 | TC-AUD-004 | Abuse covers modify + mid-delete but **not tail truncation or backdated ts**; recovery does not test external anchor. Add TC-AUD-005/006. |
| **TC-SEC** (secrets/credential theft, T-05) | — | — | — | — | **File does not exist.** 0/4. Blocks the T-05 row and RED_TEAM RT-02. |
| **TC-TEN** (tenant isolation, T-13) | — | — | — | — | **File does not exist.** 0/4. Blocks NFR-TEN-01 and RED_TEAM RT-03. |
| **TC-SC** (supply chain, T-04/T-10) | — | — | — | — | Referenced by threat rows; **no test file**. 0/4. Blocks RED_TEAM RT-06. |
| **TC-PERF-004** (DoS, T-11) | — | — | — | — | Does not exist. |

## 7) RTM rows (proposed additions)

| Req | Architecture element | Owner | Control | Test IDs (quartet) | Evidence | Gate |
|---|---|---|---|---|---|---|
| NFR-SEC-03 | BFF authN (IdP/mTLS session, no header trust) | Backend Lead | Signed session; refuse non-sim start w/o verifier | TC-ID-005/006, TC-SEC-002 | this review; MISSING_ACTIONS | B |
| NFR-TEN-01 | Tenant scoping on all reads + authenticated tenant | Backend Lead | Tenant predicate; partition | TC-TEN-001..004 | — | B/C |
| NFR-AUD-01 | External WORM anchor + length monotonicity | SRE Lead | Notarised head-hash; server-only ts | TC-AUD-005/006 | DR_PLAN | C |
| NFR-SEC-02 | CI SAST/DAST/SCA + image signing | Cloud Architect | Gates; unsigned deploy refused; SBOM scanned+signed | TC-SC-001/002 | ci.yml, SBOM.md | B |
| NFR-PRV-01 | Field-level redaction (accounts/payloads/reasons/IP) | SRE Lead/Privacy | Structured redaction | TC-OB-005 | this review | C |
| NFR-SEC-04 | Network policy union correctness + broker CIDR allowlist | Security/Cloud Architect | Scoped policies; egress allowlist; DNS monitor | TC-NET-005/006 | check_network_policies.py | B |

## 8) RAID entries

| ID | Type | Item | Severity | Owner | Gate |
|---|---|---|---|---|---|
| A-SEC-00 | Assumption | One author holds 1st+3rd line here; Board+IVA must ratify; no self-accept | — | Security & Privacy Board | B |
| R-SEC-01 | Risk | Header-asserted auth + fake PIM/MFA (OBJ-1) | Critical | Backend Lead | B |
| R-SEC-02 | Risk | Two-person / maker-checker bypass via 2nd actor-id (OBJ-2) | Critical | Backend Lead / Chief Risk | B |
| R-SEC-03 | Risk | Audit tail-truncation + mutable store + caller ts (OBJ-3) | Critical | SRE Lead / Security Architect | B |
| R-SEC-04 | Risk | Tenant reads unscoped; no TC-TEN (F-08) | High | Backend Lead | B |
| R-SEC-05 | Risk | MCP egress union bug + execution 0.0.0.0/0 (F-11,F-12) | High | Cloud/Security Architect | B |
| R-SEC-06 | Risk | CI missing SAST/DAST/SCA/signing; SBOM inaccurate (F-14,F-15) | High | Cloud Architect | B |
| R-SEC-07 | Risk | Agent disables jurisdiction flag; ActorKind spoof (F-09,F-10) | High | Compliance / MCP Security | C |
| R-SEC-08 | Risk | Legal-hold scope fail-open + unauthorised release (F-18) | High | Privacy Lead / Legal | D (O-09) |
| R-SEC-09 | Risk | Stored XSS/log injection; no CSP (F-05) | High | Frontend / Backend Lead | B |
| R-SEC-10 | Risk | Redaction gaps (F-19); DoS/no rate limit (F-06) | Medium | SRE Lead / Privacy | C |
| I-SEC-11 | Issue | Secret scan false-green + weak patterns (F-13) | Medium | Security Architect | B |
| I-SEC-12 | Issue | `/process` discards queue; `/healthz` leak (F-04,F-07) | Medium | Backend Lead | C |
| D-SEC-13 | Dependency | External pen-test + red team (H-10, MISSING_ACTIONS) before Gate D | — | Procurement / Security | D |

## 9) Verdict — Security & Privacy Board, Gate B

**REJECT for Gate B**, pending remediation or authorised risk-acceptance of R-SEC-01..03 (the three
criticals) and a credible plan for R-SEC-04..06.

Rationale: Gate B's IVA veto ground is "any critical control without a named 2nd-line owner"; here three
*critical controls that C1/C5 depend on* — authenticated identity, two-person separation of duties, and
audit immutability (T-06/T-07/T-12) — are **defeated in the implementation**, and five blueprint-06 threat
rows (T-04, T-05, T-10, T-11, T-13) name tests (TC-SC-001/002, TC-SEC-001, TC-PERF-004, TC-TEN-003) that
**do not exist**, so control coverage cannot be evidenced. The threat-model *design* (boundaries B1–B8,
plane topology, dual-key, hash-chain concept) is sound and largely well built on the deterministic pipeline;
several criticals are labelled "dev/sim" but **no runtime guard enforces that boundary**, which is itself
the defect. The path to ACCEPT WITH CONDITIONS is: land IdP/mTLS session auth (kills OBJ-1/OBJ-2), external
WORM anchoring + server-only ts (kills OBJ-3), tenant-scoped reads + TC-TEN, fix the NetworkPolicy union and
execution egress allowlist, and add SAST/DAST/SCA/signing gates + TC-SEC/TC-SC quartets — then RED_TEAM
retest (RT-01..06) and IVA re-review.

**Confidence:** High for OBJ-1/2/3 and F-04..F-19 (each reproduced by read-only PoC or direct source cite);
Medium for F-11 (NetworkPolicy union is correct per the k8s allow-union model but unverified against a live
cluster in this session).

**Provenance:** THREAT_MODEL.md, SECURITY_PLAN.md, RED_TEAM_PLAN.md, PRIVACY_IMPACT.md, COMMITTEE_DEEP_DIVE.md
(C1/C5/C9/C11), and the cited source at `apps/web/web_bff/app.py`, `static/index.html`,
`libs/core/rtcore/{planes,lines}.py`, `services/{identity,audit,approval,compliance,reconciliation,killswitch}/…`,
`observability/rtobs/*`, `infra/kubernetes/network-policies/*`, `infra/{docker-compose.yml,Dockerfile.bff}`,
`.github/workflows/ci.yml`, `.github/CODEOWNERS`, `scripts/{secret_scan,generate_sbom,check_network_policies}.py`,
`pyproject.toml`, and tests `test/quartets/test_tc_{id,aud,ob,cp}_*.py`, `test/e2e/test_journeys_and_bff.py`.
Tests run green; PoCs executed against the in-process TestClient; no tracked file modified. Tagged
[Source: 06]/[Committee]/[Open] throughout. This packet does not self-accept residual risk (goal 13) and does
not remediate (goal 23).
