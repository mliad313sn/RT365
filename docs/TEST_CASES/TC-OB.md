# TC-OB — Observability, redaction, probes, alerts

Control: Observability, redaction, probes, alerts — Requirement: NFR-OBS-01 — RTM row: NFR-OBS-01 — Owner: SRE Lead — Reviewer (≠ owner): Chief Risk Agent — **signature pending** (generated evidence is never self-certified [Source: 00, 11])

Environment tag: dev/sim — Data version: `sim-policy-v0.1 | sim-feed seed=7 | tool_registry 0.1.0` — Generated 2026-09-09T09:43:42.983877+00:00 at `c8c97a94750e86aaf26543f6998f4c91e8e9ffda` (tree dirty, tested tree `4c0d9096ec3a`)

| Quartet | Test ID | Given/When/Then (docstring) | Expected | Actual | Evidence link |
|---|---|---|---|---|---|
| positive | TC-OB-001 | Synthetic intent probe traverses every pipeline stage with one correlation ID; missing span = defect. | pass | passed | `test/quartets/test_tc_ob_observability.py::test_correlation_id_end_to_end_and_probe_completeness` |
| positive | TC-OB-006 | F-14: one correlation ID end to end — the id the probe returns is the id its spans, audit rows and intent carry, and the verdict is computed under it. | pass | passed | `test/quartets/test_tc_ob_observability.py::test_probe_returns_the_id_its_spans_are_under` |
| positive | TC-OB-009 | F-07: every SLI declares its dangerous direction; alert_delivery_s and time_to_halt_s breach upward (a slow stop, not a fast one). | pass | passed | `test/quartets/test_tc_ob_observability.py::test_breach_direction_is_declared_not_inferred_from_the_name` |
| positive | TC-OB-011 | F-03: exercising the platform emits every metric slis.yaml claims; an SLI with no emission point declares none and states its gap. | pass | passed | `test/quartets/test_tc_ob_observability.py::test_every_sli_that_claims_an_emission_point_emits` |
| negative | TC-OB-002 | Emails, bearer tokens, vault refs, long account numbers and secrets are redacted before a log line is emitted. | pass | passed | `test/quartets/test_tc_ob_observability.py::test_redaction_at_emission` |
| negative | TC-OB-008 | A pipeline that correctly stops before execution reports the un-run stages as not reached, never as present; an earlier hole stays missing whatever is declared. | pass | passed | `test/quartets/test_tc_ob_observability.py::test_stage_not_reached_is_declared_and_cannot_hide_a_hole` |
| abuse | TC-OB-003 | A pipeline run that skips a stage is reported as incomplete by the tracer (trace completeness check). | pass | passed | `test/quartets/test_tc_ob_observability.py::test_missing_span_is_detected` |
| abuse | TC-OB-005 | An auto-action whose payload lacks its required key never no-ops silently: an S1 alert.autoaction_failed fires (MCP review OBJ-3b). | pass | passed | `test/quartets/test_tc_ob_observability.py::test_auto_action_without_required_payload_raises_s1` |
| abuse | TC-OB-007 | F-14 abuse: a verdict asked for an id that has no spans reports every stage missing — a probe can never call an untraced id complete. | pass | passed | `test/quartets/test_tc_ob_observability.py::test_an_id_with_no_spans_is_never_complete` |
| abuse | TC-OB-010 | F-07 abuse: an SLI added with no direction, or an unknown one, is refused at load — a direction is never guessed from the name. | pass | passed | `test/quartets/test_tc_ob_observability.py::test_an_sli_without_a_declared_direction_is_refused` |
| abuse | TC-OB-013 | SRE-R5 abuse: acknowledging an alert that was never raised is refused, so no alert_delivery_s can be produced without a raised alert. | pass | passed | `test/quartets/test_tc_ob_observability.py::test_an_acknowledgement_cannot_be_manufactured` |
| recovery | TC-OB-004 | Alerts reach every channel with the catalogue's severity/auto-action; SLO targets are unset (O-03) so evaluation is informational until set. | pass | passed | `test/quartets/test_tc_ob_observability.py::test_alert_delivery_and_slo_safety_semantics` |
| recovery | TC-OB-012 | SRE-R5: an alert carries the time it was raised and a per-channel delivery record; alert_delivery_s exists only once an operator acknowledges it. | pass | passed | `test/quartets/test_tc_ob_observability.py::test_alert_delivery_has_two_ends` |

Quartet complete: yes. Records: 13.
