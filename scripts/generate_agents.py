#!/usr/bin/env python3
"""Generate .claude/agents/ (one agent per goals/ prompt) and the roster; --check fails on drift [ADR-016]."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "apps" / "cli"))
from rt365_cli.agents import check, collect, write  # noqa: E402

specs = collect(ROOT)
if "--check" in sys.argv:
    problems = check(ROOT, specs)
    if problems:
        print("FAIL agent roster drift (run scripts/generate_agents.py):\n - " + "\n - ".join(problems))
        sys.exit(1)
    print(f"OK: {len(specs)} agents in .claude/agents match goals/")
else:
    written = write(ROOT, specs)
    print(f"wrote {len(written)} files under .claude/agents ({len(specs)} agents)")
