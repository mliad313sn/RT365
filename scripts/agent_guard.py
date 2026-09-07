#!/usr/bin/env python3
"""PreToolUse hook for generated agents: deny Edit/Write outside the agent's owned paths (see rt365_cli.agent_guard)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "apps" / "cli"))
from rt365_cli.agent_guard import main  # noqa: E402

sys.exit(main(sys.argv[1:] + ["--root", str(ROOT)]))
