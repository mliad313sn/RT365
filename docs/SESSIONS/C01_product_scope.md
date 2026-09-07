# Session C1 — Product Charter & Functional Scope (blueprint 01, 02)

**Environment:** dev/sim only. Nothing in this packet enables a market, a strategy, autonomy, or implies regulatory status, broker capability or returns. Documented by the Program Orchestrator (1st line, recommends, never approves).

## 1 Roles

| Function | Role (line) | Basis |
|---|---|---|
| Accountable | Product Director (1st line, Domain Lead) | COMMITTEE_DEEP_DIVE §C1 |
| Consulted | Trading Domain Lead, Compliance & Legal Agents, Finance Lead, GTM Lead | COMMITTEE_DEEP_DIVE §C1 |
| Builder | Backend Lead (1st line) — `services/identity/identity_service/{accounts.py,rbac.py}` | RACI: Backend Lead owns `/services/*` |
| Challenger (different line) | Compliance Agent (2nd line) — challenged persona × mode default and out-of-scope enforcement | Protocol §1.4 rule 4 |
| Assurance / IVA | Independent Validation Agent (3rd line) — evidence review, veto at Gate A/B | COMMITTEE_DEEP_DIVE §C1 |
| Documenter | Program Orchestrator (1st line) | GOAL.md |

Statement: author != reviewer != approver. The Backend Lead wrote code and tests (`test/evidence/evidence_index.json` records `owner: Backend Lead (author of code and test)`, `reviewer: pending`); the Compliance Agent challenges; the IVA reviews evidence; the Product Council approves. Nothing here is self-certified, and this packet is a recommendation to the Product Council, not an approval.

## 2 Purpose

- [Source: 01] A modular trading operating system converting governed AI insights into controlled execution; ten personas; six operating modes (Observe, Backtest, Paper, Supervised, Bounded autonomous, Halted); custody, deposits/withdrawals, market making, copy trading, personalised advice, unlicensed solicitation, unsupported jurisdictions and manipulation-capable strategies are out of scope without separate approval.
- [Source: 02] Seventeen functional requirement groups, given IDs FR-01..FR-17 in `docs/PRD.md` and mapped to epics E01–E15.
- [Committee] Modes are an exposure-ordered ladder; promotion is one step at a time gated by release-gate evidence; Halted is reachable from any mode and left only by a two-person action from different lines. Out-of-scope capabilities are enforced technically as absent permission flags (`docs/SCOPE.md`).
- [Committee] Autonomy ships disabled for every persona until the Compliance & Legal Committee enables it per cell. [Open: O-01]
- [Open: O-02] Pricing and billing scope (E14). [Open: O-11] First launch jurisdiction — the build uses `JURISDICTION = "ZZ"` (ISO 3166 user-assigned) in `apps/web/web_bff/platform.py:74` so no real jurisdiction is implied. [Open: O-16] Gate A measurable targets.

## 3 Decisions and ADRs

| # | Decision | Alternatives compared | Why chosen | Evidence |
|---|---|---|---|---|
| C1-D1 | Mode ladder as a monotonic, one-step state machine with gate evidence per step: `MODE_LADDER` (`libs/core/rtcore/schemas/account.py`), `MODE_GATE` and `AccountRegistry.promote` (`services/identity/identity_service/accounts.py`). Entering PAPER/SUPERVISED/BOUNDED_AUTONOMOUS needs a `GateRecord` with `passed=True` and `iva_verdict == "APPROVE"`; bounded autonomy also needs a capital envelope. | (a) Free-form mode field set by admin UI; (b) ladder with skip allowed for "emergency demotion" only; (c) chosen: strict one-step promotion, free demotion, HALTED via `halt()` only. | (a) is untestable and lets configuration bypass gates; (b) was adopted for demotion (any authorised human may demote or halt) but not for promotion because skipping a step skips a gate. | TC-ID-003, TC-ID-004 |
| C1-D2 | Out-of-scope capabilities are absent from the `Permission` enum (`services/identity/identity_service/rbac.py`): no CUSTODY, MONEY_MOVEMENT, MARKET_MAKING, COPY_TRADING, PERSONAL_ADVICE, MODIFY_AUDIT, DISABLE_MONITORING member exists. | (a) Feature flags defaulting to off; (b) a "disabled capabilities" denylist; (c) chosen: enum-absent, so no configuration path can grant them. | Flags and denylists are configuration and can drift; an absent enum member cannot be granted by any RBAC edit. Strategy-level scope exclusions are additionally screened at registration (`screen_strategy_declaration`, see C6). | TC-ID-003 negative loop over absent members |
| C1-D3 | Persona × mode: agents (`ActorKind.AGENT`) can never change modes; `MODE_CHANGERS` limits humans to risk, compliance, SRE, trading-domain and portfolio-manager roles. | (a) Any tenant admin may change mode; (b) chosen: named roles only, humans only; (c) mode changes through maker-checker. | (a) contradicts [Source: 00] human-override precedence; (c) is heavier than needed for demotion, but promotion already requires a gate record — the committee asks the ARB whether promotion should additionally route through `MakerChecker` (see RAID R-05). | TC-ID-003 |
| C1-D4 | Leaving HALTED requires two humans from different lines and can never target BOUNDED_AUTONOMOUS (`restore_from_halt`). | (a) Single privileged restore with PIM; (b) chosen: two-person, different-line, non-autonomous target. | [Source: 00] human override and two-person restore; re-enabling autonomy needs post-incident review (P4). | TC-ID-004, TC-KS-004 |

ADR references: ADR-001 (planes) contextualises FR-07/FR-09. **Proposed new ADRs [Committee, pending ARB]:** ADR-015 "Operating-mode ladder, GateRecord evidence and enum-absent out-of-scope enforcement" (this session); ADR-010 "In-process/in-memory stores for dev/sim" (proposed in C02; `AccountRegistry` is a dict-backed store that a persistent identity store replaces before Gate B); ADR-012 "Static HTML console served by the BFF pending the Next.js/TypeScript PWA" (proposed in C02; the console at `apps/web/static/index.html` is labelled "(simulation)").

## 4 RTM rows

| Requirement | Architecture element | Implementation owner | Control | Test IDs | Evidence path | Gate |
|---|---|---|---|---|---|---|
| FR-01 (privileged access, RBAC/ABAC, MFA, sessions) | Identity service: `rbac.py` (`authorize`, `PRIVILEGED`, PIM window), `makerchecker.py` | Backend Lead | RBAC + MFA + PIM elevation; maker != checker, different line, cooling period | TC-ID-001, TC-ID-002 | `test/quartets/test_tc_id_identity.py`; `test/evidence/evidence_index.json` | B |
| FR-01 (mode ladder, human override) | `AccountRegistry.promote/halt/restore_from_halt` | Backend Lead | One-step promotion with GateRecord; agents denied; two-person restore | TC-ID-003, TC-ID-004 | same | B |
| [Source: 01] out-of-scope capabilities | `Permission` enum (absent members); `StrategyDeclaration` screen | Backend Lead | Enum-absent flags; registration screen (C6) | TC-ID-003, TC-CP-005 | `docs/SCOPE.md`, `test/quartets/test_tc_cp_eligibility.py` | A/B |
| FR-12 (maker-checker on approvals) | `services/approval/approval_service/queue.py` | Backend Lead | Approver != maker/strategy owner; agents cannot approve | TC-AP-001..004 | `test/quartets/test_tc_ap_approval.py` | D |
| FR-17 (Halted mode) | `halt()`, Kill Switch account-level hook `halt_account` | Backend Lead | HALTED blocks new risk (`RK-HALT-MODE`) | TC-KS-001, TC-RK-010[RK-HALT-MODE] | `test/quartets/test_tc_ks_killswitch.py` | C |
| NFR-AUD-01 (mode changes audited) | `AccountRegistry._save` audit hook | Backend Lead | `account.mode.changed`, `account.halted`, `account.restored` events | TC-ID-004, TC-AUD-001 | `test/quartets/test_tc_aud_audit.py` | C |

## 5 Threat-model delta

| Threat | Boundary | Control | Test | Owner |
|---|---|---|---|---|
| T-06 Account takeover | B1 | MFA required in `authorize`; PIM window for privileged permissions | TC-ID-002 | Backend Lead |
| T-07 Insider misuse | B2 | Maker != checker, different-line rule, cooling period; two-person un-halt | TC-ID-001, TC-ID-004 | Security & Privacy Board |
| T-02 Excessive agency (mode change by agent) | B3 | `promote` rejects non-human actors; `MakerChecker.propose` rejects agents | TC-ID-003 | MCP Security Agent |
| NEW T-14 Gate-record forgery (a fabricated `GateRecord` passed to `promote`) | B2 | Not yet controlled: `GateRecord` is an unsigned value object; needs linkage to `docs/GATE_REPORTS/` and DECISION_LOG signature | GAP (see O-22) | Program Orchestrator |
| NEW T-15 Configuration drift re-introducing an out-of-scope permission | B8 | Enum-absent check in CI via TC-ID-003; `/services/*` review by 2nd-line CODEOWNER only for protected paths — `identity_service` is not a protected path | TC-ID-003 (partial) | Security Architect |

## 6 Control quartet per critical control

| Control | Positive | Negative | Abuse | Recovery |
|---|---|---|---|---|
| Mode ladder promotion | TC-ID-003 `test_agent_cannot_change_mode_or_skip_steps_and_out_of_scope_flags_absent` (promotion with Gate D record succeeds) | TC-ID-003 (no gate / vetoed gate / skip a step -> denied) | TC-ID-003 (agent attempts promotion -> `ControlDenied`) | TC-ID-004 `test_return_from_halted_requires_two_persons_different_lines` |
| Out-of-scope enforcement | TC-CP-005 `test_surveillance_patterns_and_registration_screen` (clean declaration registers) | TC-ID-003 (absent enum members asserted) | TC-CP-005 (market-making / copy-trading / advice declarations rejected) | GAP — no test that a removed capability cannot be re-added by configuration at runtime |
| Privileged access (RBAC/MFA/PIM) | TC-ID-002 `test_rbac_mfa_and_pim` (elevated user passes) | TC-ID-002 (missing MFA, missing permission, expired elevation denied) | GAP — no session-hijack / replay of `X-Actor-*` headers test (BFF headers are a sim stand-in, `apps/web/web_bff/app.py:3-8`) | GAP — no elevation-revocation test |
| Maker-checker on privileged changes | TC-ID-001 `test_privileged_change_needs_second_approver_from_different_line` | TC-ID-001 (same person / same line denied) | TC-ID-003 (agent cannot propose) | TC-ID-001 (cooling period elapses -> EFFECTIVE) |

## 7 Evidence list

- `docs/PRODUCT_CHARTER.md`, `docs/SCOPE.md`, `docs/PRD.md` (FR-01..FR-17), `docs/PERSONAS.md`, `docs/JOURNEYS.md`
- `services/identity/identity_service/accounts.py`, `rbac.py`, `makerchecker.py`; `libs/core/rtcore/schemas/account.py`; `libs/core/rtcore/lines.py`
- `test/quartets/test_tc_id_identity.py` (TC-ID-001..004); `test/quartets/test_tc_ap_approval.py`; `test/evidence/evidence_index.json`
- `docs/REQUIREMENTS_TRACEABILITY.md` row FR-01; `docs/DECISION_LOG.md` D-001..D-004; `docs/RAID_LOG.md` O-01, O-02, O-11, O-16

## 8 RAID entries, assumptions, confidence, provenance

| ID | Type | Item | Owner | Gate |
|---|---|---|---|---|
| O-22 | Gap | `GateRecord` is an unsigned fixture; no binding to `docs/GATE_REPORTS/` (empty) or a signed DECISION_LOG entry, so T-14 is uncontrolled | Program Orchestrator, IVA | B |
| O-23 | Gap | Dev/sim human authentication is header-based (`X-Actor-Id`, `X-MFA`); IdP/MFA/passkey integration is a human setup act (E01) | Backend Lead, Security Architect | B |
| R-05 | Risk | `MODE_CHANGERS` includes PORTFOLIO_MANAGER (1st line) so a 1st-line role can promote an account with a gate record; committee asks whether promotion should route through `MakerChecker` with a 2nd-line checker | Product Director, Chief Risk Agent | B |
| R-06 | Risk | `identity_service` is not a CODEOWNERS-protected path; a change to `Permission` or `MODE_CHANGERS` needs only a 1st-line reviewer | Security Architect | B |

Assumptions: dev/sim tenant `tenant-sim`, account `acct-sim-001`, jurisdiction `ZZ` are fixtures; persona × mode policy remains disabled by default (O-01); pricing (O-02) is out of this build.

Confidence: **medium-high** for the mode ladder and enum-absent scope enforcement (code and quartet tests exist and were read); **low** for persona-level suitability, because no jurisdiction cell is real (O-11) and no IdP exists (O-23).

Provenance: [Source: 00, 01, 02, 12, 13] for posture, personas, modes, gates; [Committee] for the ladder mechanics, GateRecord, enum-absent enforcement and proposed ADR-015; [Open] O-01, O-02, O-11, O-16, O-22, O-23. Evidence is the code and tests cited by path; reviewer fields in the evidence index are "pending" until the IVA signs.
