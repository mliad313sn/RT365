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


@pytest.mark.tc("TC-PMO-001")
@pytest.mark.req("NFR-GOV-01")
@pytest.mark.quartet("positive")
@pytest.mark.env("dev")
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


@pytest.mark.tc("TC-PMO-003")
@pytest.mark.req("NFR-GOV-01")
@pytest.mark.quartet("abuse")
@pytest.mark.env("dev")
def test_refuses_to_run_without_credentials(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    for var in ("MERIDIAN_EMAIL", "MERIDIAN_PASSWORD", "MERIDIAN_ALLOW_DEMO"):
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setattr(sys, "argv", ["meridian_sync"])
    assert ms.main([]) == 2
    assert "MERIDIAN_EMAIL" in capsys.readouterr().err


@pytest.mark.tc("TC-PMO-002")
@pytest.mark.req("NFR-GOV-01")
@pytest.mark.quartet("negative")
@pytest.mark.env("dev")
def test_the_programme_declares_our_gate_ladder_so_projects_are_not_born_with_meridian_defaults():
    """The programme payload carries the six gates A..F as Meridian's `gateModel` contract requires (names, strictly increasing positions in the open interval, evidence), because a programme that does not declare a ladder gets Meridian's default four-gate one and every project is then born with two ladders."""
    ladder = ms.PROGRAMME["gateModel"]
    assert len(ladder) == 6, ladder
    positions = [g["at"] for g in ladder]
    assert all(0 < at < 1 for at in positions), positions
    assert positions == sorted(set(positions)), positions  # strictly increasing, as normaliseGateModel requires
    for gate, letter in zip(ladder, "ABCDEF", strict=True):
        assert gate["name"].startswith(f"Gate {letter}"), gate
        assert gate["evidence"] == ms.GATE_EVIDENCE[letter]
        assert gate["owner"]


@pytest.mark.tc("TC-PMO-004")
@pytest.mark.req("NFR-GOV-01")
@pytest.mark.quartet("recovery")
@pytest.mark.env("dev")
def test_a_reloaded_portfolio_converges_and_no_secret_reaches_the_evidence_file(tmp_path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """The loader is a one-way projection of the ledgers (ADR-017): re-reading them yields the same rows, so an interrupted load is recovered by running it again; and the evidence file it writes carries no credential, because that file is committed."""
    first = {e[0]: e for e in ms.epics()}
    second = {e[0]: e for e in ms.epics()}
    assert first == second and len(first) == 15  # pure projection: no id is minted per run, so a re-run cannot duplicate
    raid_a = ms.rows(ROOT / "docs" / "RAID_LOG.md", "| O-")
    raid_b = ms.rows(ROOT / "docs" / "RAID_LOG.md", "| O-")
    assert raid_a == raid_b and raid_a
    monkeypatch.delenv("MERIDIAN_EMAIL", raising=False)
    monkeypatch.delenv("MERIDIAN_PASSWORD", raising=False)
    for name in ("meridian_sync_2026-09-08.json", "meridian_sync_2026-09-08_5.10.0.json"):
        evidence = (ROOT / "docs" / "PMO" / name).read_text(encoding="utf-8")
        assert ms.DEMO[1] not in evidence and "password" not in evidence.lower()
