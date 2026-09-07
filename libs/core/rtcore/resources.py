"""Resource-root resolution for source checkouts, installed wheels and frozen executables [Source: 16; ADR-016].

Every policy the control envelope loads at start (signed tool registry, allowlists, egress and runtime
policy, risk policy, alert and SLI catalogues, dashboard assets) is a file under one root directory laid
out exactly like the repository. The root is resolved once, fail closed: a candidate is accepted only if it
carries the signed registry ``MARKER``; an explicit ``RT365_HOME`` that lacks it is an error, never a
silent fallback to another location (TC-PKG-003).
"""

from __future__ import annotations

import os
import sys
from importlib.util import find_spec
from pathlib import Path

from rtcore.errors import RTError

ENV_VAR = "RT365_HOME"
MARKER = "mcp/policies/tool_registry.signed.json"


class ResourceRootMissing(RTError):
    """No resource root carries the signed registry; nothing can be served."""


def candidates() -> list[tuple[str, Path]]:
    """Ordered candidates. An explicit override is the only candidate when set."""
    override = os.environ.get(ENV_VAR)
    if override:
        return [("RT365_HOME", Path(override))]
    out: list[tuple[str, Path]] = []
    frozen_dir = getattr(sys, "_MEIPASS", None)  # PyInstaller one-file bundle extraction directory
    if frozen_dir:
        out.append(("frozen bundle", Path(str(frozen_dir))))
    spec = find_spec("rt365_cli")
    if spec is not None and spec.origin:
        out.append(("installed bundle", Path(spec.origin).resolve().parent / "_bundle"))
    out.append(("source checkout", Path(__file__).resolve().parents[3]))
    return out


def resource_root() -> Path:
    tried: list[str] = []
    for label, path in candidates():
        if (path / MARKER).is_file():
            return path.resolve()
        tried.append(f"{label}: {path}")
    raise ResourceRootMissing(
        f"no resource root carries {MARKER}; tried " + "; ".join(tried) + f". Set {ENV_VAR} to a complete resource bundle (fail closed)."
    )
