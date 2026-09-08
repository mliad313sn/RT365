"""Contract test for the Meridian PMO sync (docs/PMO.md, ADR-017): the ledger readers see every epic, gate and open item,
and the script refuses to run without credentials (demo credentials only by explicit opt-in)."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("meridian_sync", ROOT / "scripts" / "meridian_sync.py")
ms = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(ms)


def test_ledger_readers_cover_the_lifecycle() -> None:
    epics = ms.epics()
    assert [e[0] for e in epics] == [f"E{i:02d}" for i in range(1, 16)]
    assert all(e[3][0] in "ABCDEF" for e in epics)
    assert set(ms.GATE_DATES) == set("ABCDEF") and set(ms.GATE_EVIDENCE) == set("ABCDEF")
    import re

    raid = [
        c
        for c in ms.rows(ROOT / "docs" / "RAID_LOG.md", "| O-") + ms.rows(ROOT / "docs" / "RAID_LOG.md", "| R-")
        if re.match(r"^[OR]-\d+$", c[0])
    ]
    assert sum(1 for c in raid if len(c) >= 6) > 60  # rows in other tables (renumbering map) are shorter and ignored by the sync
    acts = ms.rows(ROOT / "docs" / "MISSING_ACTIONS.md", "| H-")
    assert len(acts) >= 27 and all(len(c) >= 9 for c in acts)
    decisions = ms.rows(ROOT / "docs" / "DECISION_LOG.md", "| D-0")
    assert len(decisions) >= 48


def test_refuses_to_run_without_credentials(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    for var in ("MERIDIAN_EMAIL", "MERIDIAN_PASSWORD", "MERIDIAN_ALLOW_DEMO"):
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setattr(sys, "argv", ["meridian_sync"])
    assert ms.main([]) == 2
    assert "MERIDIAN_EMAIL" in capsys.readouterr().err
