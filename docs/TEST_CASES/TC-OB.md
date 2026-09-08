# TC-OB — Observability, redaction, probes, alerts

Control: Observability, redaction, probes, alerts — Requirement: NFR-OBS-01 — RTM row: NFR-OBS-01 — Owner: SRE Lead — Reviewer (≠ owner): Chief Risk Agent — **signature pending** (generated evidence is never self-certified [Source: 00, 11])

Environment tag: dev/sim — Data version: `sim-policy-v0.1 | sim-feed seed=7 | tool_registry 0.1.0` — Generated 2026-09-08T15:39:11.217658+00:00 at `13c6d8ef4f9585ab8e0bcfaa587bd8d96fae7ba3` (tree dirty, tested tree `3657d6a6bd42`)

| Quartet | Test ID | Given/When/Then (docstring) | Expected | Actual | Evidence link |
|---|---|---|---|---|---|
| positive | TC-OB-001 | Synthetic intent probe traverses every pipeline stage with one correlation ID; missing span = defect. | pass | passed | `test/quartets/test_tc_ob_observability.py::test_correlation_id_end_to_end_and_probe_completeness` |
| negative | TC-OB-002 | Emails, bearer tokens, vault refs, long account numbers and secrets are redacted before a log line is emitted. | pass | passed | `test/quartets/test_tc_ob_observability.py::test_redaction_at_emission` |
| abuse | TC-OB-003 | A pipeline run that skips a stage is reported as incomplete by the tracer (trace completeness check). | pass | passed | `test/quartets/test_tc_ob_observability.py::test_missing_span_is_detected` |
| abuse | TC-OB-005 | An auto-action whose payload lacks its required key never no-ops silently: an S1 alert.autoaction_failed fires (MCP review OBJ-3b). | pass | passed | `test/quartets/test_tc_ob_observability.py::test_auto_action_without_required_payload_raises_s1` |
| recovery | TC-OB-004 | Alerts reach every channel with the catalogue's severity/auto-action; SLO targets are unset (O-03) so evaluation is informational until set. | pass | passed | `test/quartets/test_tc_ob_observability.py::test_alert_delivery_and_slo_safety_semantics` |

Quartet complete: yes. Records: 5.
