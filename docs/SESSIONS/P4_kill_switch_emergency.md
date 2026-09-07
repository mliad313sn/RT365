# Session packet P4 — Kill Switch and Emergency (blueprint 02, 05, 10)

| Session | Date | Environment | Status | Documented by |
|---|---|---|---|---|
| P4 | 2026-09-07 | dev/sim only | Committee working draft; not a release artefact | Program Orchestrator (recommends, never approves) |

Drill evidence in this build is in-process test evidence only. The quarterly drill on real infrastructure with named operators (H-19, Gate E) has not happened. Emergency policy beyond CANCEL_ONLY requires an approved liquidation policy [Open: O-08]; the service falls back to CANCEL_ONLY when none is referenced.

## 1 Roles

| Role in session | Person/role | Line |
|---|---|---|
| Accountable | Chief Risk Agent (kill policy, emergency/liquidation policy); SRE Lead (declares incidents; may activate) | 2nd / 1st |
| Builder (code) | Backend Lead — `services/killswitch/killswitch_service/service.py`, `services/risk/risk_engine/monitors.py`, hooks in `apps/web/web_bff/platform.py`, `mcp/servers/mcp_servers/identity.py` (`revoke_scope`) — protected path `/services/killswitch/` needs `@rt365/chief-risk-agent` + IVA per CODEOWNERS | 1st |
| Consulted | Compliance Agent (customer notification duty), Trading Domain Lead, MCP Security Agent (identity revocation) | 2nd / 1st / 2nd |
| Challenger | Compliance Agent (2nd line, distinct from the accountable Chief Risk Agent; challenges notification and evidence preservation) | 2nd |
| Assurance / IVA | Trading Risk Committee (kill policies); Independent Validation Agent (drill evidence, Gate E veto ground "halt tests not evidenced in paper/pilot") | 2nd / 3rd |

Segregation: author != reviewer != approver; nothing here is self-certified.

## 2 Purpose

- [Source: 02] Kill Switch levels: platform, tenant, account, strategy, asset, venue.
- [Source: 05] Runtime controls emit HALT; emergency policy where closing positions is not assumed universally safest; actions: block new risk, cancel open orders, apply emergency policy (CANCEL_ONLY default), revoke agent tool tokens, preserve evidence, notify operators and, where required, customers.
- [Source: 10] Runbooks "Kill Switch activation" and "credential compromise" feed activation; SLO safety semantics (C9) and reconciliation breaks (P6) are triggers.
- [Committee] Deactivation: two persons, different lines, logged reason, post-incident review before autonomy re-enable; quarterly drill evidenced for Gate E.
- [Open: O-08] liquidation policy; [Open: O-19] deputies; [Open: O-29] activator set ratification (C11); [Open: O-33], [Open: O-34] raised below.

## 3 Decisions and ADRs

| ID | Decision | Alternatives considered | Why chosen | Status |
|---|---|---|---|---|
| ADR-029 [Committee] | `KillSwitchService.activate` executes a fixed order with injected `KillSwitchHooks`: (1) the activation itself is the flag consulted by the risk engine (`RK-HALT-KS` via `AccountSnapshot.kill_switch`); (2) `cancel_open_orders` — `platform.cancel_open` pre-empts every affected executor lease (`leases.preempt(..., "killswitch")`) and calls `gateway.cancel_all` with fresh fencing tokens inside `Plane.CONTROL`; (3) `emergency_policy_for` — CANCEL_ONLY unless an account references an approved liquidation policy; (4) `revoke_agent_identities` → `IdentityIssuer.revoke_scope`; (5) `evidence_snapshot` hashed into `Activation.evidence_hash` (audit head, open orders, positions); ACCOUNT level also halts the account; (6) audit `killswitch.activated`, then `notify` | (a) flag-only switch with runbook steps performed by humans; (b) broker-side kill (broker API) | (a) leaves open orders live for minutes; (b) assumes broker capability, never assumed [Source: 00]. Injected hooks keep the service pure and testable | Proposed, pending Trading Risk Committee |
| ADR-030 [Committee] | Resumption needs four human acts: two-person different-line `deactivate` (`Activation.deactivation_first_by/line`) then two-person different-line `AccountRegistry.restore_from_halt` to a non-autonomous mode; identity scope restored separately by `restore_scope` | (a) single privileged role restores; (b) timed auto-restore | Human override and post-incident review outrank speed of resumption [Source: 00] | Proposed, pending Trading Risk Committee |
| ADR-031 [Committee] | Runtime monitors are a pure function `evaluate_runtime(account, policy, metrics, now) → HaltEvent[]` (`monitors.py`); `SimPlatform.evaluate_monitors` audits `risk.halt.v1` and activates the matching level under a `RUNTIME_MONITOR` system actor, idempotently per (level, target) | (a) monitors cancel at the broker directly; (b) monitors only alert | (a) bypasses the envelope and the evidence snapshot; (b) violates automatic halts [Source: 05] | Proposed, pending Trading Risk Committee (see R-11) |
| D-P4-1 [Committee] | Agent attempts to operate the switch raise `ControlDenied`, alert `killswitch.agent_attempt` (S1, auto-action `revoke_agent_identity`) and audit `killswitch.denied` | (a) silent deny; (b) deny without alert | An agent reaching for the switch is a compromise indicator (T-02) | Proposed, pending MCP Security Agent |

## 4 RTM rows

| Requirement | Architecture element | Implementation owner | Control | Test IDs | Evidence path | Gate |
|---|---|---|---|---|---|---|
| FR-17 (six levels) | `KillSwitchLevel`; `flags_for`/`blocks`; risk engine `RK-HALT-KS` | Backend Lead | Every level blocks matching intents (HALTED outcome) | TC-KS-005 `test_every_level_blocks_matching_intents` (PLATFORM, TENANT, STRATEGY, ASSET, VENUE); TC-KS-001 (ACCOUNT) | `test/quartets/test_tc_ks_killswitch.py` | C |
| FR-17 (activation actions) | ADR-029 hook chain | Backend Lead | Cancel, revoke, evidence hash, notify, halt account | TC-KS-001 `test_activation_blocks_new_risk_and_cancels_open_orders` | same | C |
| FR-17 (deactivation) | `deactivate` two-person different-line; `restore_from_halt` | Backend Lead | Single person / same line stays pending | TC-KS-003 `test_single_person_deactivation_stays_pending`; TC-KS-004 `test_two_person_deactivation_restores_with_audit`; TC-E2E-J05 `test_j05_kill_switch_via_api` | same; `test/e2e/test_journeys_and_bff.py` | C |
| FR-11 (runtime controls) | `evaluate_runtime` (RT-LOSS-*, RT-DRAWDOWN, RT-FREQ, RT-SLIPPAGE, RT-REJECTS, RT-LATENCY, RT-CONNECTIVITY, RT-DRIFT, RT-RECON, RT-VENUE) | Backend Lead | HALT events → Kill Switch without human action | TC-RK-016 `test_runtime_monitors_emit_halt_events`; TC-KS-006 `test_runtime_monitor_triggers_kill_switch` | `test/quartets/test_tc_rk_determinism.py`; `test_tc_ks_killswitch.py` | C / E (thresholds O-03/O-07) |
| [Source: 05] revoke agent tokens | `IdentityIssuer.revoke_scope` / `verify` | Backend Lead (MCP Security Agent approves) | Revoked scope → tool call `error_code == "IDENTITY"` | TC-KS-001 (`read_market_snapshot` denied after activation); TC-AI-004 `test_revocation_mid_session_and_registry_revocation` | `test/quartets/test_tc_ai_mcp.py` | C |
| [Source: 05] emergency policy | `emergency_policy_for`, `apply_liquidation` hook; `EmergencyPolicy` enum | Chief Risk Agent (policy) | CANCEL_ONLY default; fallback when no liquidation ref | TC-KS-001 (`emergency_policy_applied == "CANCEL_ONLY"`); `test_emergency_policy_reduce_without_liquidation_policy_falls_back` (untagged) | `test_tc_ks_killswitch.py` | E [Open: O-08] |
| NFR-CON-01 (no duplicate on cancel) | `cancel_open` pre-empts leases; stale executor token rejected | Backend Lead | Fencing on cancel path | TC-EX-003 `test_stale_fencing_token_rejected` (gateway side); TC-KS-001 | `test/quartets/test_tc_ex_execution.py` | C |
| FR-14 trigger (P6) | `on_break` S1 → `execution.duplicate_order` → `killswitch_account` | Backend Lead | Duplicate → account Kill Switch | TC-RC-003 `test_phantom_broker_order_is_s1_duplicate_and_kills_account` | `test/quartets/test_tc_rc_reconciliation.py` | C |
| FR-16 notify operators/customers | `notify` hook → `platform.notifications` (in-memory) | SRE Lead / Compliance Agent | Operators notified; customers where required | TC-KS-001 (operator notification present); customers GAP [Open: O-34] | — | F |

## 5 Threat-model delta

| Threat | Boundary | Control in this build | Test | Residual / owner |
|---|---|---|---|---|
| T-02 Excessive agency — agent operates the switch | agent → control plane | `ActorKind.AGENT` denied, S1 alert, audit | TC-KS-002 | None. MCP Security Agent |
| T-09 Duplicate order during/after halt | control → execution | Leases pre-empted with fencing tokens on cancel; old executor token stale; fresh lease required to resume (`cancel_open` comment) | TC-KS-001, TC-EX-003 | Resume path re-leasing is not drilled end to end after a kill. Integration Architect |
| T-P4-1 Token revocation gap at ASSET/VENUE level (new) | Kill Switch → identity | `revoke_scope`/`verify` handle PLATFORM, TENANT, ACCOUNT, STRATEGY only (`identity.py` lines 78–85, 93–102); ASSET/VENUE activations revoke nothing | TC-KS-005 shows intents are still HALTED by the risk engine | Agents keep live tokens during an asset/venue halt; defence in depth only → R-12. Backend Lead |
| T-P4-2 Platform-wide halt by an automated monitor (new) | monitor → Kill Switch | `RT-LATENCY` and `RT-VENUE` emit level PLATFORM/VENUE with target `*`; `evaluate_monitors` activates PLATFORM under a system actor | TC-RK-016 | A single latency probe can stop the whole platform; also a DoS vector via spoofed `RuntimeMetrics` → R-11. Chief Risk Agent |
| T-P4-3 Unsafe flatten (new) | emergency policy | `CANCEL_AND_FLATTEN` without `liquidation_policy_ref` → fallback CANCEL_ONLY, recorded in `emergency_policy_applied` | untagged fallback test | Liquidation policy content [Open: O-08]. Trading Risk Committee |
| T-12 Evidence loss on activation | all | `evidence_snapshot` hashed into the activation and audited with `audit_head` | TC-KS-001 (`evidence_hash`), TC-KS-004 (`audit.verify().ok`) | Snapshot is in-memory JSON; no WORM copy. SRE Lead |
| T-07 Collusion on deactivation | humans | Two persons, different lines; same person / same line refused | TC-KS-003 | Deputies unnamed (O-19). Program Orchestrator |

## 6 Control quartet per critical control

| Control | Positive | Negative | Abuse | Recovery |
|---|---|---|---|---|
| Activation blocks new risk and cancels open orders | TC-KS-001; TC-KS-005 (five levels) | TC-KS-003 (still HALTED while pending) | TC-KS-002 `test_agent_cannot_activate_or_deactivate` (agent; trader without authority) | TC-KS-004 (deactivate + restore → APPROVED again) |
| Two-person different-line deactivation | TC-KS-004; TC-E2E-J05 | TC-KS-003 (same person; same line) | TC-KS-002 (agent deactivate) | TC-KS-004 (`account.restored`, chain intact) |
| Runtime monitor → automatic halt | TC-KS-006 (RT-LOSS-DAILY → account switch); TC-RK-016 | TC-RK-016 (no breach → no event) | GAP — spoofed/forged `RuntimeMetrics` | TC-KS-004 (manual restore); no automatic clear |
| Agent token revocation on activation | TC-KS-001 (`IDENTITY` error after activation) | TC-KS-004 (`restore_scope` re-enables) | TC-AI-004 (revoked mid-session) | TC-KS-004 |
| Emergency policy (CANCEL_ONLY default, no unsafe flatten) | TC-KS-001 (`CANCEL_ONLY`) | untagged `test_emergency_policy_reduce_without_liquidation_policy_falls_back` | GAP — forged `liquidation_policy_ref` | GAP |
| Evidence snapshot and notification | TC-KS-001 (`evidence_hash`, `killswitch.activated` notification) | GAP | GAP — tampered snapshot | GAP — WORM copy |
| Quarterly drill on real infrastructure | GAP [Open: O-33] | GAP | GAP | GAP |

## 7 Evidence list

| Evidence | Path |
|---|---|
| Kill Switch service, activation record, hooks | `services/killswitch/killswitch_service/service.py` |
| Runtime monitors and fixture thresholds | `services/risk/risk_engine/monitors.py`; consultation in `services/risk/risk_engine/engine.py` (`RK-HALT-KS`, `HALT_CODES`) |
| Wiring: cancel with fencing, emergency policy, evidence, halt account, monitor loop, S1 break trigger | `apps/web/web_bff/platform.py` (`cancel_open`, `emergency_policy`, `evidence`, `halt_account`, `evaluate_monitors`, `on_break`, `alerts.on("killswitch_account")`) |
| Identity revocation by scope | `mcp/servers/mcp_servers/identity.py` (`revoke_scope`, `restore_scope`, `verify`) |
| Emergency authority and two-person restore | `libs/core/rtcore/lines.py` (`KILL_SWITCH_ACTIVATORS`); `services/identity/identity_service/accounts.py` (`halt`, `restore_from_halt`) |
| BFF endpoints and console confirmation | `apps/web/web_bff/app.py` (`/v1/killswitch`); `apps/web/static/index.html` |
| Tests and evidence records (2026-09-07T17:28:57Z, 104 passed, env `dev`) | `test/quartets/test_tc_ks_killswitch.py`; `test/quartets/test_tc_rk_determinism.py`; `test/quartets/test_tc_rc_reconciliation.py`; `test/e2e/test_journeys_and_bff.py`; `test/evidence/evidence_index.json` |
| Docs and drills | `docs/RISK_POLICY.md`; `docs/INCIDENT_RESPONSE.md` (runbook "Kill Switch activation"); `docs/ALERT_CATALOG.md`; `docs/ROLLBACK_PLAN.md`; `goals/external/dr_and_halt_drills.md`; `docs/MISSING_ACTIONS.md` H-13, H-15, H-19 |

## 8 RAID entries, assumptions, confidence, provenance

| ID | Type | Item | Owner | Needed by | Status |
|---|---|---|---|---|---|
| O-33 | Gap | Quarterly Kill Switch drill on real infrastructure with named operators not performed; only in-process tests exist; Gate E veto ground "halt tests not evidenced in paper/pilot" is currently met | SRE Lead (H-19) | Gate E | Open |
| O-34 | Gap | Customer notification "where required" [Source: 05] not implemented; `notify` writes to an in-memory list; jurisdiction-specific duty unknown until O-11/H-04 | Compliance Agent, Support Lead | Gate F | Open |
| R-11 | Risk | Automated PLATFORM-level activation by the runtime monitor (RT-LATENCY, threshold fixture 500 ms) and VENUE `*` activation are not ratified kill policies; spoofed or noisy `RuntimeMetrics` could halt the platform (availability) — policy must define which monitors may act at which level | Chief Risk Agent / Trading Risk Committee | Gate C | Open |
| R-12 | Risk | `revoke_scope` ignores ASSET and VENUE levels; agent identities remain valid during asset/venue halts (intents are still blocked by `RK-HALT-KS`, so exposure is bounded, but the [Source: 05] action "revoke agent tool tokens" is incomplete) | Backend Lead (MCP Security Agent reviews) | Gate C | Open |
| O-08, O-19, O-29 | carried | liquidation policy; deputies; activator set | Trading Risk Committee; Program Orchestrator; Chief Risk Agent | E / C / C | Open |

Assumptions: the `RUNTIME_MONITOR` role acting as an activator is intended (blueprint 05) and awaits ratification (O-29). Confidence: high for the activation/deactivation semantics asserted by TC-KS-001..006; none for latency of activation (unmeasured, O-03) or for behaviour against a real broker. Provenance: code read on 2026-09-07; evidence index sha `HEAD`. Reviewer: Compliance Agent pending; approver: Trading Risk Committee pending; IVA verdict pending.
