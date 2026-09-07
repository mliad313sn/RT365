# Session packet C08 — UX & Ergonomics (blueprint 09)

| Session | Date | Environment | Status | Documented by |
|---|---|---|---|---|
| C8 | 2026-09-07 | dev/sim only | Committee working draft; not a release artefact | Program Orchestrator (recommends, never approves) |

The console shipped in this build is a static HTML page over a FastAPI BFF, labelled "simulation environment — no market, strategy or autonomy is enabled". WCAG 2.2 AA is **not verified**: the Accessibility Lead has not run a pass [Open: O-23]. The Next.js/TypeScript PWA of the reference stack is **not built** [Open: O-24].

## 1 Roles

| Role in session | Person/role | Line |
|---|---|---|
| Accountable | Frontend Lead | 1st |
| Builder (code) | Frontend Lead — `apps/web/static/index.html`; Backend Lead — `apps/web/web_bff/app.py`, `reason_codes.py` | 1st |
| Consulted | Product Director, Trading Domain Lead, Support & Training Lead (co-owner of reason-code copy) | 1st |
| Challenger | Compliance Agent (reviewer of `docs/REASON_CODES.md`; checks no advice/return language) | 2nd |
| Assurance / IVA | Accessibility Lead (WCAG verification, blocks Gate F on critical a11y defects); usability testing with representative users; Independent Validation Agent | Assurance / 3rd |

Segregation: author != reviewer != approver; nothing here is self-certified. The Accessibility Lead has not reviewed anything yet, so every accessibility claim below is [Open].

## 2 Purpose

- [Source: 09] Dashboard with risk state more prominent than profit; progressive disclosure; plain-language rejection reasons; preview-before-submit; irreversible-action confirmation; accessible colours; keyboard navigation; localisation; role-specific workspaces; WCAG-aligned verification.
- [Committee] Information hierarchy: global status and Kill Switch → capital at risk/drawdown → exposure → positions/orders → PnL → alerts → data freshness; PnL never above risk state.
- [Committee] Reason-code dictionary with a "what you can do" line per code; irreversible actions use typed confirmation and, where maker-checker applies, a second approver.
- [Committee] Accessibility target WCAG 2.2 AA (blueprint says "WCAG-aligned" without version) — NFR-A11Y-01.
- [Open: O-14] launch locales; [Open: O-23] a11y verification; [Open: O-24] PWA and role workspaces.

## 3 Decisions and ADRs

| ID | Decision | Alternatives considered | Why chosen | Status |
|---|---|---|---|---|
| ADR-014 [Committee] | Hierarchy enforced by the BFF, not the client: `GET /v1/status` returns ordinal keys `1_global_status` … `7_data_freshness`; PnL carries the note "PnL is an outcome, never a promise" (`app.py` status handler) | (a) client-side ordering only; (b) separate per-persona dashboards first | (a) is unenforced and untestable server-side; (b) premature before personas' workspaces exist | Proposed, pending Product Council / ARB |
| ADR-015 [Committee] | Reason-code dictionary as code: `REASON_CODES` dict + `explain()` in `apps/web/web_bff/reason_codes.py`, rendered to `docs/REASON_CODES.md` by `scripts/export_reason_codes.py`, served at `GET /v1/reason-codes`, attached as `reasons_explained` on approvals and decisions | (a) documentation-only dictionary; (b) i18n message service | (a) drifts from engine codes; contract test `test_reason_codes_all_documented` (`test/contract/test_openapi_alignment.py`) keeps code and docs aligned; (b) deferred to O-14 | Proposed, pending Product Council |
| ADR-016 [Committee] | Kill Switch activation from the console requires typing `ACTIVATE` (`index.html` `#ks-confirm`) and server-side `Permission.ACTIVATE_KILL_SWITCH` + MFA header; deactivation is two-person on the server (`KillSwitchService.deactivate`) | (a) modal confirm only; (b) UI-level second approver | (a) too weak for an irreversible action; (b) the two-person rule already lives in the service and cannot be bypassed by any UI | Proposed, pending Security & Privacy Board |
| D-C8-1 [Committee] | Dev/sim console is static HTML + `manifest.webmanifest`, not the Next.js PWA | (a) build the Next.js PWA now; (b) API only, no UI | (a) needs design system and locale decisions (O-14); (b) operators could not exercise journeys J-03..J-06. Recorded as [Open: O-24] | Proposed, pending Product Council |
| D-C8-2 [Committee] | Human principal in dev/sim = `X-Actor-Id`/`X-Actor-Role`/`X-MFA: verified` headers standing in for an IdP session (`app.py` `human()`) | (a) full OIDC integration now; (b) no auth in dev | (a) is E01 human setup (IdP procurement); (b) would make RBAC tests meaningless. Must never leave dev/sim → R-06 | Proposed, pending Security Architect |

## 4 RTM rows

| Requirement | Architecture element | Implementation owner | Control | Test IDs | Evidence path | Gate |
|---|---|---|---|---|---|---|
| FR-12 | `GET /v1/approvals` with `reasons_explained`; `POST /v1/approvals/{id}/approve|decline` (reason ≥ 3 chars) | Backend Lead | Maker ≠ checker; role without `APPROVE_ORDER` → 403 | TC-E2E-J03 `test_j03_supervised_order_end_to_end` | `test/e2e/test_journeys_and_bff.py` | D |
| FR-16 (audit explorer, reason codes) | `GET /v1/audit`, `/v1/audit/verify`, `/v1/reason-codes`; `GET /v1/decisions/{id}` | Backend Lead | Every reason code documented; auditor read-only via `Permission.VIEW_AUDIT` | TC-E2E-J03; `test_reason_codes_all_documented` (contract, untagged) | same; `test/contract/test_openapi_alignment.py` | C |
| FR-17 (UI path) | `POST /v1/killswitch`, `/deactivate`; console form with typed confirmation | Frontend Lead / Backend Lead | Trader 403; missing MFA 401; two-person deactivate | TC-E2E-J05 `test_j05_kill_switch_via_api` | same | C |
| FR-09 (schema at edge) | `POST /v1/intents` agent path through `ToolRuntime` (allowlist, signature, schema) | Backend Lead | Unknown field 400; research-only identity 403; bad signature 403 | TC-E2E-SCHEMA `test_schema_violation_and_non_allowlisted_agent` | same | D |
| FR-14 (ops workspace) | `/v1/reconciliation/*`, `/v1/limits/*` | Backend Lead | Two-person ticket resolution; maker-checker limits | TC-E2E-J06 `test_j06_break_ticket_via_api` | same | C |
| [Source: 09] risk before profit | `GET /v1/status` ordinal keys; `index.html` sections 1–7 | Frontend Lead | First key is `1_global_status`; `5_pnl` present and later | TC-E2E-J03 (`list(status)[0] == "1_global_status"`) | same | C |
| NFR-A11Y-01 | `index.html` uses `lang="en"`, `<section aria-labelledby>`, `role="status"` banners with `aria-live`, labelled inputs | Frontend Lead | WCAG 2.2 AA verified by Accessibility Lead | GAP — no TC-A11Y tests; no audit run | — | F [Open: O-23] |
| O-14 localisation | `explain()` English only | Frontend Lead / Support Lead | Localised reason text | GAP | — | F |

## 5 Threat-model delta

| Threat | Boundary | Control in this build | Test | Residual / owner |
|---|---|---|---|---|
| T-06 Account takeover | B1 (edge) | Header stand-in for IdP; MFA header mandatory (401 otherwise); RBAC via `identity_service.rbac.authorize` | TC-E2E-J05, TC-E2E-SCHEMA | Headers are forgeable by design in dev/sim → R-06. Security Architect |
| T-07 Insider misuse | B2 | Maker ≠ checker in approvals (`p.approve` → `ApprovalQueue`), limits maker-checker via `/v1/limits/{id}/check` (403 for proposer) | TC-E2E-J03, TC-E2E-J06 | None in scope beyond E01 PIM. Backend Lead |
| R-04 Return-implying language | UI copy | Section 5 titled "PnL (outcome, never a promise)"; disclaimer on backtest report; reason texts avoid advice | `test_reason_codes_all_documented` (presence only) | No linguistic review of copy by Compliance/GTM yet. GTM Lead, Compliance Agent |
| T-C8-1 CSRF / clickjacking on the console (new) | browser → BFF | None (no CSRF token, no frame-ancestors header); role kept in `localStorage` | GAP | Acceptable only because auth is header-based dev stand-in; must be closed with the PWA build (O-24). Frontend Lead |
| T-C8-2 Unknown reason code shown to a user (new) | engine → UI | `explain()` returns "No dictionary entry for this code (defect…)" and contract test fails the build if a code is undocumented | `test_reason_codes_all_documented` | Low. Frontend Lead |
| T-13 Data exfiltration via UI | B6 | Depth fields absent unless entitled (`ingest`), account state masked on the agent path (TC-AI-001) | TC-AI-001 | Screen-level masking per persona not built (O-24). Privacy Lead |

## 6 Control quartet per critical control

| Control | Positive | Negative | Abuse | Recovery |
|---|---|---|---|---|
| Risk-before-profit ordering | TC-E2E-J03 (first key `1_global_status`, `5_pnl` present) | GAP — no test that PnL can never precede risk in the rendered page | GAP | GAP |
| Plain-language reasons with "what you can do" | TC-E2E-J03 (`reasons_explained[0].what_you_can_do` non-empty) | `test_reason_codes_all_documented` (every engine code has an entry) | GAP — undocumented-code fallback text untested | GAP |
| Irreversible action: Kill Switch from console | TC-E2E-J05 (risk officer → 202, listed) | TC-E2E-J05 (trader → 403) | TC-E2E-J05 (MFA header absent → 401); TC-KS-002 `test_agent_cannot_activate_or_deactivate` | TC-E2E-J05 (two-person different-line deactivate → `active: false`) |
| Maker ≠ checker in the approval queue | TC-E2E-J03 (PM approves → FILLED) | TC-E2E-J03 (OPS → 403); TC-AP-002 `test_maker_cannot_check_own_intent` | TC-AP-003 `test_agent_cannot_approve_and_cannot_enqueue_approved_decisions` | TC-AP-004 `test_expired_or_killed_intent_not_executed_after_approval` |
| Schema validation at the edge | TC-E2E-J03 (valid intent 202) | TC-E2E-SCHEMA (unknown field 400) | TC-E2E-SCHEMA (research-only identity, bad signature → 403) | GAP |
| Keyboard-only / screen-reader / contrast (WCAG 2.2 AA) | GAP | GAP | GAP | GAP — [Open: O-23] |

## 7 Evidence list

| Evidence | Path |
|---|---|
| BFF endpoints, principal handling, status ordering | `apps/web/web_bff/app.py` |
| Reason-code dictionary (code) and rendered doc | `apps/web/web_bff/reason_codes.py`; `docs/REASON_CODES.md`; `scripts/export_reason_codes.py` |
| Console (static), manifest | `apps/web/static/index.html`; `apps/web/static/manifest.webmanifest`; `apps/admin/` (empty) |
| Dashboard catalogue, journeys, personas | `docs/DASHBOARDS.md`; `docs/JOURNEYS.md`; `docs/PERSONAS.md` |
| E2E journeys J-03, J-05, J-06 and schema abuse | `test/e2e/test_journeys_and_bff.py`; records in `test/evidence/evidence_index.json` |
| Contract alignment of reason codes and OpenAPI | `test/contract/test_openapi_alignment.py`; `contracts/api/API_OPENAPI.yaml` |
| Governance | `docs/COMMITTEE_DEEP_DIVE.md` §C8; `docs/NFR.md` NFR-A11Y-01; `goals/build/E10_dashboard_mobile.md`; `goals/22_accessibility_lead.md` |

## 8 RAID entries, assumptions, confidence, provenance

| ID | Type | Item | Owner | Needed by | Status |
|---|---|---|---|---|---|
| O-23 | Gap | WCAG 2.2 AA not verified: no Accessibility Lead pass, no automated contrast/keyboard/screen-reader evidence, no TC-A11Y tests | Accessibility Lead | Gate F (blocks) | Open |
| O-24 | Gap | Next.js/TypeScript PWA, design system and role workspaces (trader, risk officer, compliance analyst, operations, auditor, tenant admin, support) not built; static console only; `apps/admin` empty | Frontend Lead | Gate C (E10 first gate) | Open |
| R-06 | Risk | Header-based human principal (`X-Actor-*`, `X-MFA`) is forgeable; if the BFF were deployed beyond dev/sim every RBAC control would be bypassable | Security Architect (Backend Lead fixes with E01 IdP integration) | Gate B/C | Open |
| O-14, R-04 | carried | locales; return-implying language review | Product Director; GTM Lead, Compliance Agent | Gate F | Open |

Assumptions: usability sessions per persona have not occurred; no usability report exists. Confidence: high for BFF behaviour asserted by TC-E2E tests; none for accessibility or usability (unverified). Provenance: `apps/web` read on 2026-09-07; evidence index generated 2026-09-07T17:28:57Z (104 records passed, env `dev`). Reviewer: Compliance Agent (copy) and Accessibility Lead (a11y) pending; approver: Product Council pending.
