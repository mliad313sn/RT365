"""pytest plugin: writes the evidence index [Source: 11] from tc/env/quartet/req markers.

Evidence record fields: requirement ID, environment, data version, expected (docstring), actual
(outcome), evidence link (nodeid), owner, reviewer. The reviewer field is always "pending" here:
a human reviewer != owner signs in docs/AUDIT_EVIDENCE_INDEX.md; the plugin never self-certifies.
"""

from __future__ import annotations

import json
import os
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
    root = session.config.rootpath

    def git(*args: str) -> str:
        try:
            return subprocess.run(["git", *args], capture_output=True, text=True, cwd=root).stdout.strip()
        except Exception:  # noqa: BLE001
            return ""

    # Provenance (O-65): the base commit, whether the working tree differed from it, and a hash of the tree that was
    # actually tested (index + working tree), so a gate can tell "evidence at commit X" from "evidence on a dirty tree".
    sha = git("rev-parse", "HEAD") or "uncommitted"
    dirty = bool(git("status", "--porcelain", "--untracked-files=no"))
    tested_tree = "unknown"
    if sha != "uncommitted":
        try:
            env = {**os.environ, "GIT_INDEX_FILE": str(out.parent / ".evidence_index_tmp")}
            subprocess.run(["git", "read-tree", "HEAD"], capture_output=True, text=True, cwd=root, env=env, check=True)
            subprocess.run(["git", "add", "-A", "--", ":!test/evidence"], capture_output=True, text=True, cwd=root, env=env, check=True)
            tested_tree = subprocess.run(
                ["git", "write-tree"], capture_output=True, text=True, cwd=root, env=env, check=True
            ).stdout.strip()
        except Exception:  # noqa: BLE001
            tested_tree = "unknown"
        finally:
            (out.parent / ".evidence_index_tmp").unlink(missing_ok=True)
    out.write_text(
        json.dumps(
            {
                "generated_at": datetime.now(tz=UTC).isoformat(),
                "git_sha": sha,
                "working_tree_dirty": dirty,
                "tested_tree": tested_tree,
                "exit_status": exitstatus,
                "records": RECORDS,
            },
            indent=2,
        )
        + "\n"
    )
