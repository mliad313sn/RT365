# TC-OB — Observability, redaction, probes, alerts

Control: Observability, redaction, probes, alerts — Requirement: NFR-OBS-01 — RTM row: NFR-OBS-01 — Owner: SRE Lead — Reviewer (≠ owner): Chief Risk Agent — **signature pending** (generated evidence is never self-certified [Source: 00, 11])

Environment tag: dev/sim — Data version: `sim-policy-v0.1 | sim-feed seed=7 | tool_registry 0.1.0` — Generated 2026-09-08T14:50:09.780336+00:00 at `e829294f4f98492e2f6077167ac213843282c737` (tree dirty, tested tree `b18928e89e8d`)

| Quartet | Test ID | Given/When/Then (docstring) | Expected | Actual | Evidence link |
|---|---|---|---|---|---|
| positive | TC-OB-001 | Synthetic intent probe traverses every pipeline stage with one correlation ID; missing span = defect. | pass | passed | `test/quartets/test_tc_ob_observability.py::test_correlation_id_end_to_end_and_probe_completeness` |
| negative | TC-OB-002 | Emails, bearer tokens, vault refs, long account numbers and secrets are redacted before a log line is emitted. | pass | passed | `test/quartets/test_tc_ob_observability.py::test_redaction_at_emission` |
| abuse | TC-OB-003 | A pipeline run that skips a stage is reported as incomplete by the tracer (trace completeness check). | pass | passed | `test/quartets/test_tc_ob_observability.py::test_missing_span_is_detected` |
| abuse | TC-OB-005 | An auto-action whose payload lacks its required key never no-ops silently: an S1 alert.autoaction_failed fires (MCP review OBJ-3b). | pass | passed | `test/quartets/test_tc_ob_observability.py::test_auto_action_without_required_payload_raises_s1` |
| recovery | TC-OB-004 | Alerts reach every channel with the catalogue's severity/auto-action; SLO targets are unset (O-03) so evaluation is informational until set. | pass | passed | `test/quartets/test_tc_ob_observability.py::test_alert_delivery_and_slo_safety_semantics` |

Quartet complete: yes. Records: 5.
