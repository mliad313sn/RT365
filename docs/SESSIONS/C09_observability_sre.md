# Session packet C09 — Observability & SRE (blueprint 10)

| Session | Date | Environment | Status | Documented by |
|---|---|---|---|---|
| C9 | 2026-09-07 | dev/sim only | Committee working draft; not a release artefact | Program Orchestrator (recommends, never approves) |

SLO **targets are unset** [Open: O-03]: every entry in `observability/slis.yaml` carries `target: null` and `SliCatalog.evaluate` returns `SafetyAction.NONE` until a target exists. Runtime threshold numbers in `RuntimeThresholds` (`services/risk/risk_engine/monitors.py`) are sim fixtures [Open: O-03/O-07]. Nothing here is production telemetry.

## 1 Roles

| Role in session | Person/role | Line |
|---|---|---|
| Accountable | SRE Lead | 1st |
| Builder (code) | SRE Lead — `observability/rtobs/*`, `slis.yaml`, `alerts.yaml`; Backend Lead — hooks in `apps/web/web_bff/platform.py` (`synthetic_probe`, `evaluate_monitors`, `alerts.on(...)`) | 1st |
| Consulted | Cloud Architect, Backend Lead, Chief Risk Agent | Architecture / 1st / 2nd |
| Challenger | Chief Risk Agent (reviewer of `docs/SLO_SLA.md` and `docs/ALERT_CATALOG.md`; challenges safety semantics) | 2nd |
| Assurance / IVA | Architecture Review Board; Independent Validation Agent | 2nd / 3rd |

Segregation: author != reviewer != approver; nothing here is self-certified.

## 2 Purpose

- [Source: 10] SLO candidates (availability, data freshness, signal latency, risk-decision latency, order acknowledgement, event lag, reconciliation completeness, alert delivery); telemetry with shared correlation IDs and redaction; ten runbooks.
- [Committee] SLI definitions fixed now, targets deferred to measured baselines and business approval; error-budget breach of risk-decision latency or freshness suspends Bounded autonomous (drops to Supervised) — a runtime control feeding P4.
- [Committee] One correlation ID from snapshot → signal → intent → decision → order command → broker ack → fill → reconciliation → audit.
- [Open: O-03] baselines/targets; [Open: O-15] on-call model and support hours; [Open: O-18] RPO/RTO; [Open: O-25], [Open: O-26] raised below.

## 3 Decisions and ADRs

| ID | Decision | Alternatives considered | Why chosen | Status |
|---|---|---|---|---|
| ADR-017 [Committee] | SLIs as data with explicit null targets: `observability/slis.yaml` (8 SLIs) loaded by `SliCatalog` (`rtobs/slis.py`); `evaluate()` maps a breached *set* target to `SafetyAction` (suspend_autonomy, cancel_only_review, fail_closed, supervised_on_break) | (a) placeholder numeric targets now; (b) no catalogue until baselines | (a) would fabricate thresholds — prohibited by GOAL.md; (b) loses the fixed definitions the blueprint requires now | Proposed, pending ARB; targets pending Executive Steering (H-14) |
| ADR-018 [Committee] | Alert catalogue as data (`observability/alerts.yaml`, mirrors `docs/ALERT_CATALOG.md`) with `auto_action` names bound to hooks by `AlertRouter.on()`; every alert is "delivered" to every channel (`channels = ["pager","email"]`) | (a) actions hard-coded inside services; (b) external alert manager only | (a) hides safety semantics from review; (b) unavailable in sim. Data form lets the Chief Risk Agent review auto-actions as a table | Proposed, pending ARB |
| ADR-019 [Committee] | Trace completeness as a hard list: `PIPELINE_STAGES` and `Tracer.missing()` (`rtobs/tracing.py`); `SimPlatform.synthetic_probe` runs one intent per call through every stage and reports `missing_spans` | (a) OpenTelemetry SDK now; (b) sampled tracing | (a) not in `pyproject.toml`; adopt when infra exists (Cloud Architect); (b) sampling cannot prove a missing span is a defect | Proposed, pending ARB |
| D-C9-1 [Committee] | Redaction at emission: `JsonFormatter` applies `redact()` regexes (email, bearer token, `vault://` refs, 12–19-digit numbers, secret/password/api_key/token pairs) before any line is written (`rtobs/logging.py`) | (a) redaction at storage/SIEM; (b) allow-list of loggable fields | (a) leaks in transit; (b) too brittle for dev. NFR-PRV-01 | Proposed, pending Privacy Lead |
| D-C9-2 [Committee] | Correlation ID via `contextvars` (`rtobs/correlation.py`) and required in every audit append | (a) thread-local; (b) explicit parameter everywhere | async-safe and enforced at the audit boundary | Proposed, pending ARB |

## 4 RTM rows

| Requirement | Architecture element | Implementation owner | Control | Test IDs | Evidence path | Gate |
|---|---|---|---|---|---|---|
| NFR-OBS-01 | `Tracer`, `PIPELINE_STAGES`, `synthetic_probe`, `AuditStore.by_correlation` | SRE Lead | Correlation ID end to end; missing span = defect | TC-OB-001 `test_correlation_id_end_to_end_and_probe_completeness`; TC-OB-003 `test_missing_span_is_detected` | `test/quartets/test_tc_ob_observability.py` | C |
| NFR-PRV-01 | `rtobs/logging.py` `redact()` | SRE Lead (Privacy Lead co-signs) | Redaction at emission | TC-OB-002 `test_redaction_at_emission` | same | D |
| [Source: 10] alert delivery | `AlertRouter.raise_alert` → `fired`, `delivered`, auto-action hook | SRE Lead | Every channel receives; catalogue severity/auto-action applied | TC-OB-004 `test_alert_delivery_and_slo_safety_semantics` | same | C |
| NFR-LAT-01, NFR-FRS-01 | `SliCatalog.evaluate`; `evaluate_runtime` RT-LATENCY (fixture 500 ms) | SRE Lead / Backend Lead | Breach → autonomy suspended / halt | TC-OB-004 (strict catalogue → SUSPEND_AUTONOMY); TC-RK-016 `test_runtime_monitors_emit_halt_events`; TC-KS-006 `test_runtime_monitor_triggers_kill_switch` | same; `test/quartets/test_tc_rk_determinism.py`, `test_tc_ks_killswitch.py` | E (targets) |
| NFR-AVL-01 | Fail-closed outcomes (RK-HALT-INPUT / CP-HALT-INPUT); SLI `control_plane_availability` safety `fail_closed` | Backend Lead | Never fail open | TC-RK-004 `test_engine_restart_same_decision_and_fail_closed_on_missing_inputs`; `test_fail_closed_for_every_missing_input` (property) | `test/property/test_risk_determinism_property.py` | C |
| [Source: 10] reconciliation completeness | SLI `reconciliation_completeness_pct` (safety `supervised_on_break`); `alerts.on("account_to_supervised")` | SRE Lead | Break → Supervised | TC-RC-002 `test_break_moves_account_to_supervised` | `test/quartets/test_tc_rc_reconciliation.py` | C |
| FR-16 notifications / incident centre | `platform.notifications` list; `INCIDENT_RESPONSE.md` runbook index | SRE Lead | Operators notified | GAP — in-memory list only; no channel integration | — | C |
| NFR-DR-01 | `docs/DR_PLAN.md` | Cloud Architect | RPO/RTO per cell | GAP [Open: O-18] | — | E |

## 5 Threat-model delta

| Threat | Boundary | Control in this build | Test | Residual / owner |
|---|---|---|---|---|
| T-12 Audit tampering | all | `audit.chain_verification_failed` alert (S1, `auto_action: killswitch_platform`) in `alerts.yaml`; `GET /v1/audit/verify` | TC-AUD-003 `test_tampering_detected_by_hash_chain` | `killswitch_platform` has **no hook bound** in `platform.py` (only `account_to_supervised`, `autonomy_to_supervised`, `killswitch_account`, `revoke_agent_identity`, `revoke_tool_for_tenant`) → R-07. SRE Lead |
| T-13 Exfiltration via logs | B6/B2 | Redaction at emission | TC-OB-002 | Regex-based; structured PII classes beyond email/tokens/numbers not covered. Privacy Lead |
| T-11 Denial of service | B1/B7 | None in sim (backpressure/shedding is C2 §6) | GAP (TC-PERF-004 referenced in `docs/THREAT_MODEL.md` does not exist) | Performance & Chaos Leads |
| T-C9-1 Alert channel failure (new) | platform → operator | `AlertRouter.channels` in-memory; `alert_delivery_s` SLI defined, target null | TC-OB-004 (in-memory only) | No pager/email integration; on-call model [Open: O-15] → O-25. SRE Lead |
| T-C9-2 Correlation ID forgery or loss (new) | any service | contextvar set by `correlation()`; audit requires ID | TC-OB-001, TC-AUD-001 | No test for a forged/duplicated correlation ID. SRE Lead |
| T-C9-3 Catalogue/code drift (new) | yaml ↔ hooks | `AlertRouter.raise_alert` defaults unknown names to S2/none | GAP | Unknown alert names silently degrade; add a contract test that every `auto_action` in `alerts.yaml` is bound → R-07 |

## 6 Control quartet per critical control

| Control | Positive | Negative | Abuse | Recovery |
|---|---|---|---|---|
| Correlation ID end to end | TC-OB-001 (`missing_spans == []`, ≥ 6 audit events per correlation) | TC-OB-003 (skipped stages reported) | GAP — forged/duplicate correlation ID | GAP |
| Redaction at emission | TC-OB-002 (email, bearer, vault ref, number, password removed) | TC-OB-002 (same assertion, negative form) | GAP — obfuscated secret formats | GAP |
| Alert delivery and safety semantics | TC-OB-004 (S2, `autonomy_to_supervised`, pager+email) | TC-OB-004 (null target → `SafetyAction.NONE`) | GAP — alert storm / suppression abuse | TC-OB-004 (`autonomy_suspended` set); TC-RC-002 |
| Runtime monitor → automatic halt | TC-RK-016; TC-KS-006 (`RT-LOSS-DAILY` → Kill Switch account) | TC-RK-016 (thresholds not breached → no event, per test body) | GAP — spoofed `RuntimeMetrics` | TC-KS-004 `test_two_person_deactivation_restores_with_audit` |
| Synthetic probe each minute | TC-OB-001 (`probe.runs == 1`) | GAP — probe failure raises alert | GAP | GAP — scheduler not built (on-demand only) |
| Fail closed on missing inputs | TC-RK-004; `test_fail_closed_for_every_missing_input` | TC-RK-013 `test_undefined_limit_fails_closed` | TC-RK-003 `test_tampered_intent_hash_rejected` | TC-MD-004 `test_feed_restored_next_intent_passes` |

## 7 Evidence list

| Evidence | Path |
|---|---|
| Library: alerts, correlation, logging/redaction, metrics, SLIs, tracing | `observability/rtobs/alerts.py`, `correlation.py`, `logging.py`, `metrics.py`, `slis.py`, `tracing.py` |
| SLI and alert catalogues (data) | `observability/slis.yaml`; `observability/alerts.yaml` |
| Wiring: probe, monitors, alert auto-actions | `apps/web/web_bff/platform.py` (`synthetic_probe`, `evaluate_monitors`, `alerts.on(...)` block) |
| Runtime monitors and fixture thresholds | `services/risk/risk_engine/monitors.py` |
| Docs (owner SRE Lead, reviewer Chief Risk Agent / Security Architect) | `docs/SLO_SLA.md`; `docs/ALERT_CATALOG.md`; `docs/INCIDENT_RESPONSE.md`; `docs/DASHBOARDS.md`; `docs/DEPLOYMENT_RUNBOOK.md`; `docs/ROLLBACK_PLAN.md`; `docs/DR_PLAN.md` |
| Tests and evidence records | `test/quartets/test_tc_ob_observability.py`; `test/evidence/evidence_index.json` (2026-09-07T17:28:57Z, 104 passed, env `dev`) |
| Governance | `docs/COMMITTEE_DEEP_DIVE.md` §C9; `goals/build/E12_observability_sre.md`; `goals/decisions/O-03_decision_pack.md`; `goals/external/dr_and_halt_drills.md` |

## 8 RAID entries, assumptions, confidence, provenance

| ID | Type | Item | Owner | Needed by | Status |
|---|---|---|---|---|---|
| O-25 | Gap | No real alert channels or on-call rota: `AlertRouter.channels` is an in-memory list; `alert_delivery_s` cannot be measured; links O-15 | SRE Lead, Support Lead | Gate E | Open |
| O-26 | Gap | Runbooks exist only as index rows in `docs/INCIDENT_RESPONSE.md`; no per-runbook procedure with trigger, first action, escalation and evidence-to-capture; no synthetic-probe scheduler | SRE Lead | Gate C | Open |
| R-07 | Risk | Catalogue/code drift: `auto_action` values `killswitch_platform`, `cancel_only`, `suspend_signals` exist in `alerts.yaml` but no hook is bound in `platform.py`; an S1 `audit.chain_verification_failed` or `risk.fail_open_attempt` would fire without automatic action; unknown alert names default silently to S2/none | SRE Lead (Chief Risk Agent reviews) | Gate C | Open |
| O-03, O-15, O-18 | carried | targets from baselines; on-call; RPO/RTO | SRE Lead; Cloud Architect | E / F / E | Open |

Assumptions: metrics (`MetricsRegistry`) and traces are process-local; no exporter exists. Confidence: high for the in-process behaviour asserted by TC-OB-001..004; none for latency, freshness or availability numbers (unmeasured by design until O-03). Provenance: files read on 2026-09-07; evidence index sha `HEAD`. Reviewer: Chief Risk Agent pending; approver: ARB pending; IVA verdict pending.
