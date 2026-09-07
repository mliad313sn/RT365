"""pytest plugin: writes the evidence index [Source: 11] from tc/env/quartet/req markers.

Evidence record fields: requirement ID, environment, data version, expected (docstring), actual
(outcome), evidence link (nodeid), owner, reviewer. The reviewer field is always "pending" here:
a human reviewer != owner signs in docs/AUDIT_EVIDENCE_INDEX.md; the plugin never self-certifies.
"""

from __future__ import annotations

import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path

import pytest

RECORDS: list[dict[str, object]] = []
DATA_VERSION = "sim-policy-v0.1 | sim-feed seed=7 | tool_registry 0.1.0"


def _marker_arg(item: pytest.Item, name: str, default: str | None = None) -> str | None:
    m = item.get_closest_marker(name)
    return str(m.args[0]) if m and m.args else default


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo[None]):  # type: ignore[no-untyped-def]
    outcome = yield
    rep = outcome.get_result()
    if rep.when != "call":
        return
    tc = _marker_arg(item, "tc")
    if tc is None:
        return
    RECORDS.append(
        {
            "test_id": tc,
            "requirement": _marker_arg(item, "req", "-"),
            "quartet": _marker_arg(item, "quartet", "-"),
            "environment": _marker_arg(item, "env", "dev"),
            "data_version": DATA_VERSION,
            "expected": (item.function.__doc__ or "").strip().splitlines()[0]
            if getattr(item, "function", None) and item.function.__doc__
            else item.name,
            "actual": rep.outcome,
            "evidence_link": item.nodeid,
            "duration_s": round(rep.duration, 4),
            "owner": "Backend Lead (author of code and test)",
            "reviewer": "pending — QA Lead / 2nd-line reviewer must sign in docs/AUDIT_EVIDENCE_INDEX.md",
        }
    )


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    out = Path(session.config.rootpath) / "test" / "evidence" / "evidence_index.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    try:
        sha = (
            subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=session.config.rootpath).stdout.strip()
            or "uncommitted"
        )
    except Exception:  # noqa: BLE001
        sha = "unknown"
    out.write_text(
        json.dumps(
            {"generated_at": datetime.now(tz=UTC).isoformat(), "git_sha": sha, "exit_status": exitstatus, "records": RECORDS}, indent=2
        )
        + "\n"
    )
