"""TC-OB — Observability [Source: 10; NFR-OBS-01, NFR-PRV-01]: correlation end to end, redaction, probes, alert delivery."""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest
from conftest import ACCOUNT, SRE
from killswitch_service.service import KillSwitchLevel
from pydantic import ValidationError
from rtobs.logging import redact
from rtobs.metrics import MetricsRegistry
from rtobs.slis import Direction, SafetyAction, Sli, SliCatalog
from rtobs.tracing import PIPELINE_STAGES

ROOT = Path(__file__).resolve().parents[2]
SLIS = ROOT / "observability" / "slis.yaml"


def _sli(**overrides: object) -> Sli:
    """A complete SLI record; every field an SLI must declare, so a test never relies on a default direction."""
    base: dict[str, object] = {
        "name": "risk_decision_latency_ms_p99",
        "definition": "d",
        "measurement_point": "m",
        "emission_point": "e",
        "metrics": ("pipeline.risk_decision_latency_ms",),
        "direction": "higher_is_worse",
        "target": None,
        "safety_semantic": "suspend_autonomy",
        "gap": None,
    }
    return Sli.model_validate({**base, **overrides})


def _emitted(registry: MetricsRegistry, metric: str) -> bool:
    """True when the registry holds the metric, with or without labels (``name{label=value}``)."""
    keys = (*registry.counters.keys(), *registry.histograms.keys())
    return any(k == metric or k.startswith(metric + "{") for k in keys)


@pytest.mark.tc("TC-OB-001")
@pytest.mark.req("NFR-OBS-01")
@pytest.mark.quartet("positive")
def test_correlation_id_end_to_end_and_probe_completeness(platform):  # type: ignore[no-untyped-def]
    """Synthetic intent probe traverses every pipeline stage with one correlation ID; missing span = defect."""
    out = platform.synthetic_probe()
    assert out["missing_spans"] == [] and out["final_state"] in ("ACKNOWLEDGED", "FILLED")
    corr = out["correlation_id"]
    # F-14: the verdict must be the verdict for the id the operator is handed, so the spans are asserted under *that* id.
    assert set(platform.tracer.stages(corr)) == set(PIPELINE_STAGES) and out["trace_complete"] is True
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
    cat = SliCatalog.load(SLIS)
    assert (
        len(cat.names()) == 9
        and "time_to_halt_s" in cat.names()
        and cat.evaluate("risk_decision_latency_ms_p99", 10_000) == SafetyAction.NONE
    )
    strict = SliCatalog((_sli(target=500),))
    assert strict.evaluate("risk_decision_latency_ms_p99", 900) == SafetyAction.SUSPEND_AUTONOMY


@pytest.mark.tc("TC-OB-005")
@pytest.mark.req("NFR-OBS-01")
@pytest.mark.quartet("abuse")
def test_auto_action_without_required_payload_raises_s1(platform):  # type: ignore[no-untyped-def]
    """An auto-action whose payload lacks its required key never no-ops silently: an S1 alert.autoaction_failed fires (MCP review OBJ-3b)."""
    platform.alerts.raise_alert("plane.deny", {"source": "analytics", "destination": "execution", "channel": "x"})
    failed = platform.alerts.by_name("alert.autoaction_failed")
    assert failed and failed[-1].payload["missing"] == ["agent"]


@pytest.mark.tc("TC-OB-006")
@pytest.mark.req("NFR-OBS-01")
@pytest.mark.quartet("positive")
def test_probe_returns_the_id_its_spans_are_under(platform):  # type: ignore[no-untyped-def]
    """F-14: one correlation ID end to end — the id the probe returns is the id its spans, audit rows and intent carry, and the verdict is computed under it."""
    out = platform.synthetic_probe()
    corr = out["correlation_id"]
    assert platform.tracer.stages(corr), "the returned correlation id must lead somewhere"
    assert tuple(out["stages_recorded"]) == PIPELINE_STAGES and out["missing_spans"] == [] and out["failed_spans"] == []
    # every span in the process belongs to the returned id: no second, undisclosed probe id exists
    assert {s.correlation_id for s in platform.tracer.spans} == {corr}
    assert platform.audit.by_correlation(corr) and platform.tracker.get(out["intent_id"]).correlation_id == corr


@pytest.mark.tc("TC-OB-007")
@pytest.mark.req("NFR-OBS-01")
@pytest.mark.quartet("abuse")
def test_an_id_with_no_spans_is_never_complete(platform):  # type: ignore[no-untyped-def]
    """F-14 abuse: a verdict asked for an id that has no spans reports every stage missing — a probe can never call an untraced id complete."""
    platform.synthetic_probe()
    verdict = platform.tracer.verdict("corr_nothing_is_under_this")
    assert verdict.recorded == () and verdict.missing == PIPELINE_STAGES and verdict.complete is False
    # and a failed span is not a present span: an audit stage recorded ok=False is not completeness
    platform.tracer.record("audit", "corr-failed", ok=False)
    failed = platform.tracer.verdict("corr-failed", not_reached=tuple(s for s in PIPELINE_STAGES if s != "audit"))
    assert failed.failed == ("audit",) and failed.complete is False


@pytest.mark.tc("TC-OB-008")
@pytest.mark.req("NFR-OBS-01")
@pytest.mark.quartet("negative")
def test_stage_not_reached_is_declared_and_cannot_hide_a_hole(platform):  # type: ignore[no-untyped-def]
    """A pipeline that correctly stops before execution reports the un-run stages as not reached, never as present; an earlier hole stays missing whatever is declared."""
    for stage in ("market_snapshot", "signal", "intent", "eligibility", "risk", "audit"):
        platform.tracer.record(stage, "corr-stopped")
    stopped = platform.tracer.verdict("corr-stopped", not_reached=("order_command", "broker_ack"))
    assert stopped.missing == () and stopped.not_reached == ("order_command", "broker_ack") and stopped.complete is True
    # abuse: declaring an *earlier* stage not reached while later stages ran cannot suppress it
    platform.tracer.record("risk", "corr-hole")
    platform.tracer.record("audit", "corr-hole")
    hole = platform.tracer.verdict("corr-hole", not_reached=("signal", "order_command", "broker_ack"))
    assert "signal" in hole.missing and hole.complete is False


@pytest.mark.tc("TC-OB-009")
@pytest.mark.req("NFR-OBS-01")
@pytest.mark.quartet("positive")
def test_breach_direction_is_declared_not_inferred_from_the_name():  # type: ignore[no-untyped-def]
    """F-07: every SLI declares its dangerous direction; alert_delivery_s and time_to_halt_s breach upward (a slow stop, not a fast one)."""
    cat = SliCatalog.load(SLIS)
    assert cat.get("alert_delivery_s").direction is Direction.HIGHER_IS_WORSE
    assert cat.get("time_to_halt_s").direction is Direction.HIGHER_IS_WORSE
    assert cat.get("control_plane_availability").direction is Direction.LOWER_IS_WORSE
    assert cat.get("reconciliation_completeness_pct").direction is Direction.LOWER_IS_WORSE
    # a fixture target (never a platform target: O-03 is not closed) proves the comparison runs the declared way
    up = SliCatalog(
        (
            _sli(name="time_to_halt_s", direction="higher_is_worse", target=30, safety_semantic="cancel_only_review"),
            _sli(name="alert_delivery_s", direction="higher_is_worse", target=60, safety_semantic="fail_closed"),
        )
    )
    assert up.evaluate("time_to_halt_s", 31) == SafetyAction.CANCEL_ONLY_REVIEW and up.evaluate("time_to_halt_s", 29) == SafetyAction.NONE
    assert up.evaluate("alert_delivery_s", 61) == SafetyAction.FAIL_CLOSED and up.evaluate("alert_delivery_s", 1) == SafetyAction.NONE
    down = SliCatalog((_sli(name="control_plane_availability", direction="lower_is_worse", target=99, safety_semantic="fail_closed"),))
    assert down.evaluate("control_plane_availability", 98) == SafetyAction.FAIL_CLOSED
    assert down.evaluate("control_plane_availability", 100) == SafetyAction.NONE
    assert all(cat.get(n).target is None for n in cat.names()), "no SLO target may be set outside O-03"


@pytest.mark.tc("TC-OB-010")
@pytest.mark.req("NFR-OBS-01")
@pytest.mark.quartet("abuse")
def test_an_sli_without_a_declared_direction_is_refused():  # type: ignore[no-untyped-def]
    """F-07 abuse: an SLI added with no direction, or an unknown one, is refused at load — a direction is never guessed from the name."""
    with pytest.raises(ValidationError):
        Sli.model_validate({k: v for k, v in _sli().model_dump().items() if k != "direction"})
    with pytest.raises(ValidationError):
        _sli(direction="whichever")
    # the name no longer decides: a name containing "latency" declared lower_is_worse is judged low, not high
    inverted = SliCatalog((_sli(name="signal_latency_ms", direction="lower_is_worse", target=100, safety_semantic="fail_closed"),))
    assert inverted.evaluate("signal_latency_ms", 99) == SafetyAction.FAIL_CLOSED
    assert inverted.evaluate("signal_latency_ms", 101) == SafetyAction.NONE


class _StubStrategy:
    """A strategy that returns a signal without computing one: what is under test is the timing wrapper, not the strategy."""

    strategy_id = "stub"
    version = "0"

    def on_snapshot(self, history, *, position_qty, nav):  # type: ignore[no-untyped-def]
        return object()


@pytest.mark.tc("TC-OB-011")
@pytest.mark.req("NFR-OBS-01")
@pytest.mark.quartet("positive")
def test_every_sli_that_claims_an_emission_point_emits(platform):  # type: ignore[no-untyped-def]
    """F-03: exercising the platform emits every metric slis.yaml claims; an SLI with no emission point declares none and states its gap."""
    from strategy_service.signals import timed_signal

    platform.run_intent(platform.make_intent())
    platform.reconcile()
    a = platform.alerts.raise_alert("limit.changed", {"account": ACCOUNT})
    platform.alerts.acknowledge(a.alert_id, by="sre.lead")
    platform.killswitch.activate(KillSwitchLevel.ACCOUNT, ACCOUNT, reason="observability drill", actor=SRE, now=platform.now)
    timed_signal(_StubStrategy(), (), position_qty=Decimal("0"), nav=Decimal("1000"), observe=platform.metrics.observe, runner="test")

    cat = SliCatalog.load(SLIS)
    for name in cat.names():
        sli = cat.get(name)
        if sli.emission_point == "none":
            assert sli.metrics == () and sli.gap, f"{name}: an SLI with no emission point must say so and say why"
            continue
        assert sli.metrics, f"{name}: an emission point must name the metric it emits"
        for metric in sli.metrics:
            assert _emitted(platform.metrics, metric), f"{name}: slis.yaml claims {metric} and nothing emitted it"
    assert platform.metrics.get("control_plane.decision_requests") == platform.metrics.get("control_plane.decisions_recorded")


@pytest.mark.tc("TC-OB-012")
@pytest.mark.req("NFR-OBS-01")
@pytest.mark.quartet("recovery")
def test_alert_delivery_has_two_ends(platform):  # type: ignore[no-untyped-def]
    """SRE-R5: an alert carries the time it was raised and a per-channel delivery record; alert_delivery_s exists only once an operator acknowledges it."""
    a = platform.alerts.raise_alert("limit.changed", {"account": ACCOUNT})
    assert a.raised_at is not None and a.alert_id
    d = [x for x in platform.alerts.deliveries if x.alert_id == a.alert_id]
    assert {x.channel for x in d} == {"pager", "email"} and all(x.dispatch_s >= 0.0 for x in d)
    # unacknowledged is unacknowledged: no delivery time is invented, and the alert is reportable as outstanding
    assert all(x.acknowledged_at is None and x.delivery_s is None for x in d)
    assert a.alert_id in {x.alert_id for x in platform.alerts.unacknowledged()}
    ack = platform.alerts.acknowledge(a.alert_id, by="sre.lead")
    assert ack.acknowledged_by == "sre.lead" and ack.delivery_s is not None and ack.delivery_s >= 0.0
    assert _emitted(platform.metrics, "alerts.alert_delivery_s") and not platform.alerts.unacknowledged()


@pytest.mark.tc("TC-OB-013")
@pytest.mark.req("NFR-OBS-01")
@pytest.mark.quartet("abuse")
def test_an_acknowledgement_cannot_be_manufactured(platform):  # type: ignore[no-untyped-def]
    """SRE-R5 abuse: acknowledging an alert that was never raised is refused, so no alert_delivery_s can be produced without a raised alert."""
    with pytest.raises(KeyError):
        platform.alerts.acknowledge("alert_never_raised", by="sre.lead")
    assert not _emitted(platform.metrics, "alerts.alert_delivery_s")
    a = platform.alerts.raise_alert("limit.changed", {"account": ACCOUNT})
    platform.alerts.acknowledge(a.alert_id, by="sre.lead")
    first = [x.acknowledged_at for x in platform.alerts.deliveries if x.alert_id == a.alert_id]
    platform.alerts.acknowledge(a.alert_id, by="someone.else")  # a second ack never rewrites the first delivery time
    assert [x.acknowledged_at for x in platform.alerts.deliveries if x.alert_id == a.alert_id] == first
