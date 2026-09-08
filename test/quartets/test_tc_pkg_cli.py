"""TC-PKG-001..005 — Distribution: the ``rt365`` command, resource-root resolution for installed and frozen builds,
and the fail-closed rules that survive packaging [Source: 06, 16; NFR-SEC-02; ADR-016]."""

from __future__ import annotations

import io
import json
import shutil
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import pytest
from rt365_cli.main import BUNDLED_RELATIVE_PATHS, main
from rtcore.resources import MARKER, ResourceRootMissing, resource_root
from rtobs.tracing import PIPELINE_STAGES

ROOT = Path(__file__).resolve().parents[2]


def _cli(*argv: str) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        try:
            code = main(list(argv))
        except SystemExit as exc:  # argparse errors
            code = int(exc.code or 0)
    return code, out.getvalue(), err.getvalue()


@pytest.mark.tc("TC-PKG-001")
@pytest.mark.req("NFR-SEC-02")
@pytest.mark.quartet("positive")
def test_cli_version_check_and_probe_run_in_sim(monkeypatch):  # type: ignore[no-untyped-def]
    """`rt365 version`, `rt365 check --env sim` and `rt365 probe --env sim` succeed against the source checkout; check reports the registry as a sim fixture and the audit chain intact."""
    monkeypatch.delenv("RT365_HOME", raising=False)
    code, out, _ = _cli("version")
    assert code == 0 and "rt365" in out and "0.1.0" in out
    code, out, _ = _cli("check", "--env", "sim")
    assert code == 0, out
    assert "registry: OK" in out and "FIXTURE" in out and "audit chain: OK" in out and "planes: OK" in out
    code, out, _ = _cli("probe", "--env", "sim")
    assert code == 0 and "final_state" in out and "missing_spans: []" in out
    # F-14: the operator is handed one id, and the completeness verdict printed beside it is the verdict for that id
    printed = dict(line.split(": ", 1) for line in out.splitlines() if ": " in line)
    assert printed["trace_complete"] == "True" and printed["trace_correlation_id"] == printed["correlation_id"]
    assert json.loads(printed["stages_recorded"]) == list(PIPELINE_STAGES) and json.loads(printed["failed_spans"]) == []


@pytest.mark.tc("TC-PKG-002")
@pytest.mark.req("NFR-SEC-02")
@pytest.mark.quartet("negative")
def test_cli_refuses_unlabelled_or_non_sim_environments(monkeypatch):  # type: ignore[no-untyped-def]
    """Without an explicit --env or RT_ENV the CLI refuses to serve or check (IVA-06: unlabelled environment fails closed); a production label refuses the fixture registry."""
    monkeypatch.delenv("RT_ENV", raising=False)
    monkeypatch.delenv("RT365_HOME", raising=False)
    for cmd in ("serve", "check", "probe", "mcp-serve"):
        code, out, err = _cli(cmd)
        assert code == 2 and "RT_ENV" in (out + err), cmd
    code, out, err = _cli("check", "--env", "production")
    assert code != 0 and ("refused" in (out + err) or "FAIL" in (out + err))
    code, out, err = _cli("serve", "--env", "paper")
    assert code == 2 and "sim" in (out + err)


@pytest.mark.tc("TC-PKG-003")
@pytest.mark.req("NFR-SEC-02")
@pytest.mark.quartet("abuse")
def test_resource_root_never_falls_back_silently(monkeypatch, tmp_path):  # type: ignore[no-untyped-def]
    """A resource root pointed at a directory without the signed registry (or with a tampered one) fails closed: no silent fallback to the source tree, no service, no MCP server."""
    monkeypatch.setenv("RT365_HOME", str(tmp_path))
    with pytest.raises(ResourceRootMissing):
        resource_root()
    code, out, err = _cli("check", "--env", "sim")
    assert code != 0 and "resource root" in (out + err)
    code, out, err = _cli("mcp-serve", "--env", "sim")
    assert code != 0 and "resource root" in (out + err)
    # a root that has the marker but a tampered registry is also refused at load time
    for rel in BUNDLED_RELATIVE_PATHS:
        src = ROOT / rel
        dst = tmp_path / rel
        if src.is_dir():
            shutil.copytree(src, dst, dirs_exist_ok=True)
        else:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(src, dst)
    marker = tmp_path / MARKER
    marker.write_text(marker.read_text().replace('"registry_version": "0.1.0"', '"registry_version": "9.9.9"'))
    code, out, err = _cli("check", "--env", "sim")
    assert code != 0 and "signature" in (out + err).lower()


@pytest.mark.tc("TC-PKG-004")
@pytest.mark.req("NFR-SEC-02")
@pytest.mark.quartet("recovery")
def test_resource_root_override_restores_service_for_installed_builds(monkeypatch, tmp_path):  # type: ignore[no-untyped-def]
    """An installed or frozen build without a source tree recovers by pointing RT365_HOME at a complete resource bundle: the same signed policies, same checks, same probe result."""
    for rel in BUNDLED_RELATIVE_PATHS:
        src = ROOT / rel
        dst = tmp_path / rel
        if src.is_dir():
            shutil.copytree(src, dst, dirs_exist_ok=True)
        else:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(src, dst)
    monkeypatch.setenv("RT365_HOME", str(tmp_path))
    assert resource_root() == tmp_path.resolve()
    code, out, _ = _cli("check", "--env", "sim")
    assert code == 0 and str(tmp_path) in out
    code, out, _ = _cli("probe", "--env", "sim")
    assert code == 0 and "missing_spans: []" in out


@pytest.mark.tc("TC-PKG-005")
@pytest.mark.req("NFR-GLO-01")
@pytest.mark.quartet("recovery")
def test_venue_calendars_resolve_zones_without_a_system_tz_database(monkeypatch):  # type: ignore[no-untyped-def]
    """With no system time-zone database (Windows, frozen builds) IANA zones still resolve from the bundled tzdata package, so `rt365 check` builds the venue calendars; the spec bundles that package (release run 34213524352 regression)."""
    import zoneinfo

    import tzdata  # noqa: F401  — declared runtime dependency; the executable ships it

    monkeypatch.setattr(zoneinfo, "TZPATH", ())
    zoneinfo.reset_tzpath(to=[])
    zoneinfo.ZoneInfo.clear_cache()
    try:
        assert zoneinfo.ZoneInfo("UTC").key == "UTC"
        assert zoneinfo.ZoneInfo("America/New_York").key == "America/New_York"
        code, out, _ = _cli("check", "--env", "sim")
        assert code == 0 and "check: OK" in out
    finally:
        zoneinfo.reset_tzpath()
        zoneinfo.ZoneInfo.clear_cache()
    spec = (ROOT / "installer" / "rt365.spec").read_text(encoding="utf-8")
    assert 'collect_data_files("tzdata")' in spec
    assert "tzdata" in (ROOT / "requirements.lock.txt").read_text(encoding="utf-8")
