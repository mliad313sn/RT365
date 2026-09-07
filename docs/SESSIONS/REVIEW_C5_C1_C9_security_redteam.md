# REVIEW — C5 Security & Privacy · C1/E01 Identity & Modes · C9/E12 Observability · E11 Audit

| Session type | Component(s) | Line(s) of defense | Approving body | Gate under review | Status |
|---|---|---|---|---|---|
| CHALLENGE + threat-model delta | C5, C1/E01, C9/E12, E11 | 1st (Security Architect, design owner) + 3rd (Red-Team & Pen-Test Lead) | Security & Privacy Board | B (Architecture) | Findings only — nothing remediated, nothing self-certified |

Scope of evidence reviewed: `docs/THREAT_MODEL.md`, `docs/SECURITY_PLAN.md`, `docs/RED_TEAM_PLAN.md`, `docs/PRIVACY_IMPACT.md`, `docs/COMMITTEE_DEEP_DIVE.md` (C1, C5, C9, C11), `.github/CODEOWNERS`, `.github/workflows/ci.yml`, `security/*`, `scripts/secret_scan.py`, `scripts/generate_sbom.py`, `scripts/check_network_policies.py`, `infra/kubernetes/*`, `infra/docker-compose.yml`, `infra/Dockerfile.bff`, `libs/core/rtcore/{planes,lines}.py`, `services/identity/identity_service/*.py`, `services/audit/audit_service/store.py`, `services/approval/approval_service/queue.py`, `services/compliance/compliance_engine/{jurisdiction,retention}.py`, `observability/rtobs/*.py`, `observability/alerts.yaml`, `apps/web/web_bff/{app,platform}.py`, `apps/web/static/index.html`, `test/quartets/test_tc_{id,aud,ob,cp}_*.py`, `test/e2e/test_journeys_and_bff.py`.

Commands run (read-only): `pytest test/quartets/test_tc_id_identity.py test/quartets/test_tc_aud_audit.py test/quartets/test_tc_ob_observability.py` → 12 passed. `scripts/secret_scan.py` → `OK secret scan: 0 files, no findings` (see F-08). `scripts/check_network_policies.py` → OK. `scripts/generate_sbom.py` → 69 components, run once to inspect output and the generated `security/sbom/` was removed again so the tree is unchanged. A proof-of-concept script (`scratchpad/poc.py`, not committed) exercised every exploit chain in §3–§4 against the in-memory `TestClient`; results are quoted verbatim as "PoC-n".

---

## 1. Roles

| Role | Line | Person/agent | Independence statement |
|---|---|---|---|
| Security Architect (author of this packet, owner of THREAT_MODEL.md / SECURITY_PLAN.md) | 1st | goals/13 | Did not write any code under review; the Backend Lead (goals/E01, E11, E12 build prompts) did. May not accept own residual risk — every acceptance below is routed to the Security & Privacy Board. |
| Red-Team & Pen-Test Lead (co-author, exploit scenarios, severity) | 3rd | goals/23 | Not part of delivery; will not remediate. Retest is owed before Gate C (RT-04/05), D and F. |
| Challenged party | 1st | Backend Lead (E01/E11/E12), Cloud Architect (infra), SRE Lead (C9) | Must answer each finding in DECISION_LOG or RAID. |
| Reviewer of this packet (≠ authors) | 2nd | MCP Security Agent (goals/14) for §4 B6 items; Privacy Lead for §4 redaction/retention items | Per SECURITY_PLAN.md reviewer column. |
| Approver | — | Security & Privacy Board; Independent Validation Agent holds veto at Gate B | Quorum = 1st-line owner + 2nd-line owner + IVA. |

Author ≠ reviewer ≠ approver holds for this packet. Nothing in it is self-certified.

## 2. Purpose

- **[Source: 06]** Threat-model every trust boundary B1–B8; map each blueprint-06 threat to control → test → owner; specify vault/HSM, workload identity, mTLS, signed artefacts, SAST/DAST/SCA, secret scanning, egress control, immutable logs.
- **[Source: 00]** Verify the non-negotiables in code, not prose: AI/MCP never hold credentials, never approve their own changes, never suppress audit or disable monitoring; human override and Kill Switch supersede everything; author ≠ reviewer ≠ approver.
- **[Source: 11, 12]** Gate B exit needs a threat model with every critical control owned by a named 2nd-line owner; Gate C needs RT-04/RT-05 (replay, audit tamper) retested; Gate D needs the security assessment and red-team of AI/MCP paths.
- **[Committee]** This session is the CHALLENGE step of the operating loop for C5/C1/C9/E11 after the E01/E11/E12 build; the outputs are a threat-model delta, quartet gaps, RTM rows, RAID entries and a Gate B verdict.
- **[Open]** No IdP, KMS, WORM store, SIEM, or CI security tooling exists yet (MISSING_ACTIONS H-06/H-07/H-10; security/signing/README.md). Every finding below that says "before any non-dev environment" is therefore a Gate C entry condition, not a Gate B blocker, *unless* the dev/sim build can be mistaken for a control. Several can (F-01, F-08, F-09).

---

## 3. Three strongest objections

### OBJ-1 — The BFF's entire human trust model is client-asserted, and the identity "controls" it feeds are faked at the boundary (B1, B2)

**Severity: CRITICAL** (for any environment beyond a developer laptop; HIGH as a design-debt item at Gate B because tests and docs present it as evidence of FR-01).

**Where.**
- `apps/web/web_bff/app.py:75-88` — `human()` builds `Actor(actor_id=x_actor_id, role=Role(x_actor_role), kind=ActorKind.HUMAN, tenant_id=TENANT)` purely from three request headers. Nothing binds `X-Actor-Id` to a session, a signature, an IdP subject or a tenant.
- `apps/web/web_bff/app.py:90-99` — `require()` constructs `User(... mfa_enrolled=True, privileged_until=p.now.replace(year=+1))` and calls `authorize(..., mfa_verified=True)`. PIM elevation, MFA enrolment and MFA verification — the three things `identity_service.rbac.authorize` (`rbac.py:141-148`) exists to check — are hard-coded to pass. TC-ID-002 tests `authorize()` in isolation; nothing tests the BFF path, so the RTM row "FR-01 → Maker-checker, MFA → TC-ID-001..004" is evidence of a library, not of the product.
- `libs/core/rtcore/lines.py:105-110` — `Actor.kind` defaults to `HUMAN` and is caller-declared; `lines.py:55, 97` — `Role.STRATEGY_AGENT` and `Role.RUNTIME_MONITOR` are ordinary `Role` values accepted by `Role(x_actor_role)`.
- `apps/web/static/index.html:63` — the console reads actor id and role from `localStorage` and sends `X-MFA: verified` unconditionally. Anyone who can open DevTools is any role.
- `app.py:6` — the only warning is a module docstring; `/healthz` (`app.py:372`) reports `environment: sim` but nothing refuses to start with header auth outside `RT_ENV=sim`.

**Exploit (as run, PoC-1/2/3/6).**
1. `POST /v1/intents` with `X-Actor-Id: agent:rogue`, `X-Actor-Role: strategy_agent`, `X-MFA: verified` → **202**. An AI agent (or anyone) submits a trade intent as a "human" with the *agent's* role, bypassing the whole MCP runtime (signed identity, allowlist, quota, input/output schema, canary check, tamper log). The non-negotiable "AI/MCP submit typed intents only through the controlled path" is void at B1.
2. `POST /v1/killswitch {level: PLATFORM}` with `X-Actor-Role: runtime_monitor` → **202**. A header-asserted "runtime monitor" halts the platform; undoing it needs two humans from different lines. Trivial platform-wide DoS with