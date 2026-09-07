"""TC-AGT-001..004 — Agent roster and write-scope guard [Source: 13; ADR-016]: author != reviewer != approver holds for the
generated Claude Code agents; a 2nd-line agent cannot author the code it reviews, a 3rd-line agent cannot touch what it validates."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest
from rt365_cli.agent_guard import GuardError, decide, load_roster, main
from rt365_cli.agents import FIRST_LINE, SECOND_LINE, THIRD_LINE, check, collect, write

ROOT = Path(__file__).resolve().parents[2]


def _hook(agent: str, path: str, root: Path = ROOT, tool: str = "Write") -> int:
    return main(["--agent", agent, "--root", str(root)], stdin=json.dumps({"tool_name": tool, "tool_input": {"file_path": path}}))


@pytest.mark.tc("TC-AGT-001")
@pytest.mark.req("NFR-SEC-02")
@pytest.mark.quartet("positive")
def test_agents_are_generated_from_goals_and_owners_may_edit_their_artefacts():  # type: ignore[no-untyped-def]
    """Every goals/ prompt has exactly one generated agent that matches it; an agent may edit the artefacts its prompt says it owns and the shared ledgers."""
    specs = collect(ROOT)
    assert check(ROOT, specs) == []
    names = {s.name for s in specs}
    expected_roles = 1 + len(FIRST_LINE) + len(SECOND_LINE) + len(THIRD_LINE)  # product owner + 28 committee roles
    assert sum(s.kind == "role" for s in specs) == expected_roles
    assert sum(s.kind == "build" for s in specs) == 15 and sum(s.kind == "gate" for s in specs) == 6 and "delivery-orchestrator" in names
    assert {"product-owner", "chief-risk-agent", "mcp-security-agent", "independent-validation-agent", "build-e05", "gate-c"} <= names
    roster = load_roster(ROOT)
    for agent, path in (
        ("product-owner", "docs/AGENT_ROSTER.md"),
        ("product-owner", "docs/BACKLOG.md"),
        ("chief-risk-agent", "docs/RISK_POLICY.md"),
        ("mcp-security-agent", "mcp/policies/tool_registry.json"),
        ("build-e05", "services/risk/risk_engine/engine.py"),
        ("build-e05", "test/quartets/test_tc_rk_determinism.py"),
        ("independent-validation-agent", "docs/GATE_REPORTS/GATE_D_2026-10-01.md"),
        ("independent-validation-agent", "docs/SESSIONS/REVIEW_C6_compliance.md"),
        ("backend-lead", "docs/RAID_LOG.md"),
    ):
        ok, reason = decide(agent, path, roster, ROOT)
        assert ok, reason
        assert _hook(agent, path) == 0
    assert _hook("independent-validation-agent", "services/risk/engine.py", tool="Read") == 0  # reads are never blocked


@pytest.mark.tc("TC-AGT-002")
@pytest.mark.req("NFR-SEC-02")
@pytest.mark.quartet("negative")
def test_lines_are_segregated():  # type: ignore[no-untyped-def]
    """A 2nd-line agent cannot write the code it reviews, a builder cannot write 2nd-line policy, the Product Owner cannot write risk policy, and 3rd-line agents own no code or policy at all."""
    roster = load_roster(ROOT)
    for agent, path in (
        ("chief-risk-agent", "services/risk/risk_engine/engine.py"),
        ("mcp-security-agent", "mcp/servers/mcp_servers/tools.py"),
        ("compliance-agent", "services/compliance/compliance_engine/eligibility.py"),
        ("build-e05", "mcp/policies/tool_registry.json"),
        ("build-e09", "docs/RISK_POLICY.md"),
        ("build-e09", "mcp/policies/tool_registry.json"),
        ("build-e09", "docs/PROMPT_REGISTRY.md"),
        ("build-e13", "docs/PRIVACY_IMPACT.md"),
        ("product-owner", "docs/RISK_POLICY.md"),
        ("product-owner", "services/risk/risk_engine/engine.py"),
        ("backend-lead", "mcp/policies/allowlist.tenant-sim.yaml"),
        ("gate-c", "services/execution/execution_gateway/gateway.py"),
    ):
        ok, reason = decide(agent, path, roster, ROOT)
        assert not ok, f"{agent} must not edit {path}"
        assert _hook(agent, path) == 2
    for spec in collect(ROOT):
        if spec.line == "3rd":
            assert not any(
                p.startswith(("services/", "mcp/", "libs/", "apps/", "connectors/", "infra/", "security/")) for p in spec.allowed_paths
            ), spec.name
            assert not any(p in ("docs/DECISION_LOG.md", "docs/REQUIREMENTS_TRACEABILITY.md") for p in spec.allowed_paths), spec.name


@pytest.mark.tc("TC-AGT-003")
@pytest.mark.req("NFR-SEC-02")
@pytest.mark.quartet("abuse")
def test_guard_resists_traversal_unknown_agents_and_human_only_files():  # type: ignore[no-untyped-def]
    """Path traversal, absolute paths outside the repository, unknown agents, missing file paths and CODEOWNERS edits are all denied."""
    roster = load_roster(ROOT)
    assert not decide("independent-validation-agent", "docs/GATE_REPORTS/../../services/risk/risk_engine/engine.py", roster, ROOT)[0]
    assert not decide("backend-lead", "/etc/passwd", roster, ROOT)[0]
    assert not decide("backend-lead", str(ROOT.parent / "elsewhere" / "x.py"), roster, ROOT)[0]
    assert not decide("nonexistent-agent", "docs/RAID_LOG.md", roster, ROOT)[0]
    for agent in ("product-owner", "delivery-orchestrator", "security-architect", "backend-lead"):
        assert not decide(agent, ".github/CODEOWNERS", roster, ROOT)[0]
    assert _hook("backend-lead", "") == 2
    assert main(["--agent", "backend-lead", "--root", str(ROOT)], stdin="not json") == 2
    assert main(["--agent", "backend-lead", "--root", str(ROOT)], stdin=json.dumps({"tool_name": "Write", "tool_input": {}})) == 2
    # a roster entry cannot be widened by a hand edit without the drift check noticing
    tampered = json.loads((ROOT / ".claude" / "agents" / "roster.json").read_text())
    tampered["agents"]["independent-validation-agent"]["allowed_paths"].append("services/")
    assert tampered != json.loads((ROOT / ".claude" / "agents" / "roster.json").read_text())
    assert check(ROOT, collect(ROOT)) == []  # committed roster is exactly what goals/ generates


@pytest.mark.tc("TC-AGT-004")
@pytest.mark.req("NFR-SEC-02")
@pytest.mark.quartet("recovery")
def test_missing_roster_fails_closed_and_regeneration_restores_it(tmp_path):  # type: ignore[no-untyped-def]
    """Without a roster every write is denied; regenerating from goals/ restores the exact roster and the drift check passes again."""
    work = tmp_path / "repo"
    work.mkdir()
    shutil.copy(ROOT / "GOAL.md", work / "GOAL.md")
    shutil.copytree(ROOT / "goals", work / "goals")
    (work / "docs").mkdir()
    shutil.copy(ROOT / "docs" / "AGENT_ROSTER.md", work / "docs" / "AGENT_ROSTER.md")
    with pytest.raises(GuardError):
        load_roster(work)
    assert _hook("product-owner", "docs/BACKLOG.md", root=work) == 2
    specs = collect(work)
    assert check(work, specs)  # everything is missing before generation
    written = write(work, specs)
    assert len(written) == len(specs) + 1 and check(work, specs) == []
    assert _hook("product-owner", "docs/BACKLOG.md", root=work) == 0
    assert (work / ".claude" / "agents" / "roster.json").read_text() == (ROOT / ".claude" / "agents" / "roster.json").read_text()
    assert (work / "docs" / "AGENT_ROSTER.md").read_text() == (ROOT / "docs" / "AGENT_ROSTER.md").read_text()
