"""TC-OB — Observability [Source: 10; NFR-OBS-01, NFR-PRV-01]: correlation end to end, redaction, probes, alert delivery."""

from __future__ import annotations

from pathlib import Path

import pytest
from conftest import ACCOUNT
from rtobs.logging import redact
from rtobs.slis import SafetyAction, SliCatalog
from rtobs.tracing import PIPELINE_STAGES

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.tc("TC-OB-001")
@pytest.mark.req("NFR-OBS-01")
@pytest.mark.quartet("positive")
def test_correlation_id_end_to_end_and_probe_completeness(platform):  # type: ignore[no-untyped-def]
    """Synthetic intent probe traverses every pipeline stage with one correlation ID; missing span = defect."""
    out = platform.synthetic_probe()
    assert out["missing_spans"] == [] and out["final_state"] in ("ACKNOWLEDGED", "FILLED")
    corr = out["correlation_id"]
    assert len(platform.audit.by_correlation(corr)) >= 6 and platform.metrics.get("probe.runs") == 1.0
    assert set(PIPELINE_STAGES) == {"market_snapshot", "signal", "intent", "eligibility", "risk", "order_command", "broker_ack", "audit"}


@pytest.mark.tc("TC-OB-002")
@pytest.mark.req("NFR-PRV-01")
@pytest.mark.quartet("negative")
def test_redaction_at_emission():  # type: ignore[no-untyped-def]
    """Emails, bearer tokens, vault refs, long account numbers and secrets are redacted before a log line is emitted."""
    line = redact(
        'user john.doe@example.com token "Bearer abc.def-ghi" vault://brokers/x/creds acct 1234567890123456 password=hunter2hunter2hunter2'
    )
    assert (
        "example.com" not in line
        and "abc.def" not in line
        and "brokers/x" not in line
        and "1234567890123456" not in line
        and "hunter2" not in line
    )


@pytest.mark.tc("TC-OB-003")
@pytest.mark.req("NFR-OBS-01")
@pytest.mark.quartet("abuse")
def test_missing_span_is_detected(platform):  # type: ignore[no-untyped-def]
    """A pipeline run that skips a stage is reported as incomplete by the tracer (trace completeness check)."""
    platform.tracer.record("intent", "corr-x")
    platform.tracer.record("risk", "corr-x")
    assert set(platform.tracer.missing("corr-x")) == {"market_snapshot", "signal", "eligibility", "order_command", "broker_ack", "audit"}


@pytest.mark.tc("TC-OB-004")
@pytest.mark.req("NFR-OBS-01")
@pytest.mark.quartet("recovery")
def test_alert_delivery_and_slo_safety_semantics(platform):  # type: ignore[no-untyped-def]
    """Alerts reach every channel with the catalogue's severity/auto-action; SLO targets are unset (O-03) so evaluation is informational until set."""
    a = platform.alerts.raise_alert("slo.freshness_breach", {"account": ACCOUNT})
    assert a.severity == "S2" and a.auto_action == "autonomy_to_supervised"
    assert {ch for ch, al in platform.alerts.delivered if al is a} == {"pager", "email"}
    assert platform.accounts.get(ACCOUNT).autonomy_suspended
    cat = SliCatalog.load(ROOT / "observability" / "slis.yaml")
    assert len(cat.names()) == 9 and "time_to_halt_s" in cat.names() and cat.evaluate("risk_decision_latency_ms_p99", 10_000) == SafetyAction.NONE
    from rtobs.slis import Sli

    strict = SliCatalog(
        (Sli(name="risk_decision_latency_ms_p99", definition="d", measurement_point="m", target=500, safety_semantic="suspend_autonomy"),)
    )
    assert strict.evaluate("risk_decision_latency_ms_p99", 900) == SafetyAction.SUSPEND_AUTONOMY


@pytest.mark.tc("TC-OB-005")
@pytest.mark.req("NFR-OBS-01")
@pytest.mark.quartet("abuse")
def test_auto_action_without_required_payload_raises_s1(platform):  # type: ignore[no-untyped-def]
    """An auto-action whose payload lacks its required key never no-ops silently: an S1 alert.autoaction_failed fires (MCP review OBJ-3b)."""
    platform.alerts.raise_alert("plane.deny", {"source": "analytics", "destination": "execution", "channel": "x"})
    failed = platform.alerts.by_name("alert.autoaction_failed")
    assert failed and failed[-1].payload["missing"] == ["agent"]
