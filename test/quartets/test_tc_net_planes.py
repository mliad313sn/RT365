"""TC-NET — Plane topology [Source: 00, 03; NFR-SEC-01; ADR-001]: analytics->control via queue only; no analytics->execution route."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest
from rtcore.errors import PlaneViolation
from rtcore.planes import ALLOWED_ROUTES, GUARD, Plane, enter

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.tc("TC-NET-001")
@pytest.mark.req("NFR-SEC-01")
@pytest.mark.quartet("positive")
def test_analytics_to_control_via_intent_queue_allowed(platform):  # type: ignore[no-untyped-def]
    """Analytics plane may reach the Control plane only through the intent queue channel."""
    vi = platform.submit_intent(platform.make_intent(), plane=Plane.ANALYTICS)
    assert vi.intent_hash and not platform.guard.denies
    GUARD.check(Plane.CONTROL, Plane.EXECUTION, "order_command")
    GUARD.check(Plane.EXECUTION, Plane.BROKER, "broker_adapter")


@pytest.mark.tc("TC-NET-002")
@pytest.mark.req("NFR-SEC-01")
@pytest.mark.quartet("negative")
def test_analytics_to_execution_denied_with_alert(platform):  # type: ignore[no-untyped-def]
    """A call from the Analytics plane to the Execution gateway is denied and raises an S1 plane.deny alert."""
    r = platform.run_intent(platform.make_intent())
    cmd = r.order.command.model_copy(update={"idempotency_key": "k-analytics"})
    with enter(Plane.ANALYTICS), pytest.raises(PlaneViolation):
        platform.gateway.submit(cmd, executor_id="rogue", fencing_token=1, now=platform.now)
    assert platform.guard.denies and platform.alerts.by_name("plane.deny")[0].severity == "S1"
    assert platform.broker.submissions_received == 1
    with pytest.raises(PlaneViolation):  # unattributed callers are treated as analytics (fail closed)
        platform.gateway.submit(cmd, executor_id="rogue", fencing_token=1, now=platform.now)


@pytest.mark.tc("TC-NET-003")
@pytest.mark.req("NFR-SEC-01")
@pytest.mark.quartet("abuse")
def test_mcp_to_vault_and_broker_denied():  # type: ignore[no-untyped-def]
    """No route exists from Analytics (MCP) to the vault or brokers, in-process and in the Kubernetes policies."""
    assert (Plane.ANALYTICS, Plane.VAULT) not in ALLOWED_ROUTES and (Plane.ANALYTICS, Plane.BROKER) not in ALLOWED_ROUTES
    for dst, ch in (
        (Plane.VAULT, "broker_credentials"),
        (Plane.BROKER, "broker_adapter"),
        (Plane.EXECUTION, "order_command"),
        (Plane.EXECUTION, "api_read"),
    ):
        with pytest.raises(PlaneViolation):
            GUARD.check(Plane.ANALYTICS, dst, ch)
    out = subprocess.run([sys.executable, str(ROOT / "scripts" / "check_network_policies.py")], capture_output=True, text=True, cwd=ROOT)
    assert out.returncode == 0, out.stdout + out.stderr


@pytest.mark.tc("TC-NET-004")
@pytest.mark.req("NFR-SEC-01")
@pytest.mark.quartet("recovery")
def test_policy_change_detected_and_restore(tmp_path):  # type: ignore[no-untyped-def]
    """A policy edit that opens analytics->execution fails the invariant check; restoring the file passes again."""
    import shutil

    src = ROOT / "infra" / "kubernetes" / "network-policies"
    work = tmp_path / "network-policies"
    shutil.copytree(src, work)
    script = (
        (ROOT / "scripts" / "check_network_policies.py")
        .read_text()
        .replace('POL = ROOT / "infra" / "kubernetes" / "network-policies"', f'POL = Path("{work}")')
    )
    runner = tmp_path / "check.py"
    runner.write_text(script)
    assert subprocess.run([sys.executable, str(runner)], capture_output=True, text=True, cwd=ROOT).returncode == 0
    bad = work / "analytics.yaml"
    bad.write_text(
        bad.read_text().replace(
            "podSelector: {matchLabels: {app: intent-queue}}",
            "podSelector: {matchLabels: {app: intent-queue}}\n        - namespaceSelector: {matchLabels: {plane: execution}}",
        )
    )
    res = subprocess.run([sys.executable, str(runner)], capture_output=True, text=True, cwd=ROOT)
    assert res.returncode == 1 and "plane=execution" in res.stdout
    shutil.copy(src / "analytics.yaml", bad)
    assert subprocess.run([sys.executable, str(runner)], capture_output=True, text=True, cwd=ROOT).returncode == 0
    # in-process: after a denied crossing, a correctly attributed call still works (no sticky state)
    with enter(Plane.CONTROL):
        GUARD.check_caller(Plane.EXECUTION, "order_command")
