"""Write-path guard for generated Claude Code agents (PreToolUse hook) [Source: 13; ADR-016].

Each agent in ``.claude/agents/`` is generated from a ``goals/`` prompt that states what the role owns. The
roster (``.claude/agents/roster.json``) records, per agent, the repository paths it may edit. This hook denies
``Edit``/``Write`` calls outside those paths so that a 2nd-line agent cannot author the code it reviews and a
3rd-line agent cannot touch an artefact under validation (author != reviewer != approver).

It is a guard rail for the agent harness, not a security control: CODEOWNERS, branch protection and CI stay
the controls of record (SECURITY_PLAN.md). Fail closed: unknown agent, missing roster or unreadable input -> deny.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROSTER_RELATIVE = Path(".claude") / "agents" / "roster.json"
ALWAYS_DENIED: tuple[str, ...] = (".github/CODEOWNERS",)  # human-only: maps roles to teams (O-20)
WRITE_TOOLS = frozenset({"Edit", "Write", "MultiEdit", "NotebookEdit"})


class GuardError(Exception):
    pass


def load_roster(root: Path) -> dict[str, list[str]]:
    path = root / ROSTER_RELATIVE
    if not path.is_file():
        raise GuardError(f"roster missing at {path}; run scripts/generate_agents.py (fail closed)")
    data = json.loads(path.read_text(encoding="utf-8"))
    agents = data.get("agents")
    if not isinstance(agents, dict):
        raise GuardError("roster has no agents map")
    return {name: list(spec.get("allowed_paths", [])) for name, spec in agents.items()}


def _relative(root: Path, file_path: str) -> str | None:
    p = Path(file_path)
    if not p.is_absolute():
        p = root / p
    try:
        return p.resolve(strict=False).relative_to(root.resolve()).as_posix()
    except ValueError:
        return None


def decide(agent: str, file_path: str, roster: dict[str, list[str]], root: Path) -> tuple[bool, str]:
    """(allowed, reason). Prefixes ending in '/' match a directory; other prefixes match a file or a name prefix (e.g. SESSIONS/REVIEW_)."""
    rel = _relative(root, file_path)
    if rel is None:
        return False, f"{file_path} is outside the repository"
    if rel in ALWAYS_DENIED:
        return False, f"{rel} is human-only"
    allowed = roster.get(agent)
    if allowed is None:
        return False, f"agent {agent!r} is not in the roster (fail closed)"
    for prefix in allowed:
        if rel == prefix.rstrip("/") or rel.startswith(prefix if prefix.endswith("/") else prefix):
            return True, f"{rel} is within {prefix} owned by {agent}"
    return False, f"agent {agent!r} may not edit {rel}; owned paths: {', '.join(allowed) or 'none'}"


def main(argv: list[str] | None = None, stdin: str | None = None) -> int:
    parser = argparse.ArgumentParser(prog="agent_guard")
    parser.add_argument("--agent", required=True)
    parser.add_argument("--root", default=".")
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()
    try:
        payload = json.loads(stdin if stdin is not None else sys.stdin.read() or "{}")
        tool = str(payload.get("tool_name", ""))
        if tool not in WRITE_TOOLS:
            return 0
        tool_input = payload.get("tool_input") or {}
        file_path = tool_input.get("file_path") or tool_input.get("notebook_path")
        if not file_path:
            print("agent_guard: write tool without a file path; denied (fail closed)", file=sys.stderr)
            return 2
        allowed, reason = decide(args.agent, str(file_path), load_roster(root), root)
    except (GuardError, ValueError, OSError) as exc:
        print(f"agent_guard: {exc}; denied (fail closed)", file=sys.stderr)
        return 2
    if not allowed:
        print(f"agent_guard: {reason}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
