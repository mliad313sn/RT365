#!/usr/bin/env python3
"""Generate a CycloneDX 1.5 JSON SBOM for the Python service set [Source: 06; SBOM.md]."""

from __future__ import annotations

import json
import re
import sys
import tomllib
from datetime import UTC, datetime
from importlib import metadata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
out_dir = ROOT / "security" / "sbom"
out_dir.mkdir(parents=True, exist_ok=True)

# Walk the declared dependency closure only, never the ambient environment (review F-14)
declared = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]["dependencies"]
roots = [re.split(r"[<>=!~\[ ;]", d, maxsplit=1)[0].strip().lower() for d in declared]
seen: dict[str, str] = {}
stack = list(roots)
while stack:
    name = stack.pop()
    if name in seen:
        continue
    try:
        dist = metadata.distribution(name)
    except metadata.PackageNotFoundError:
        seen[name] = "MISSING"
        continue
    seen[name] = dist.version
    for req in dist.requires or []:
        if "extra ==" in req:
            continue
        stack.append(re.split(r"[<>=!~\[ ;]", req, maxsplit=1)[0].strip().lower())
components = [{"type": "library", "name": n, "version": v, "purl": f"pkg:pypi/{n}@{v}"} for n, v in sorted(seen.items())]
bom = {
    "bomFormat": "CycloneDX",
    "specVersion": "1.5",
    "version": 1,
    "metadata": {
        "timestamp": datetime.now(tz=UTC).isoformat(),
        "component": {"type": "application", "name": "rt365-robotrader", "version": "0.1.0"},
        "tools": [{"name": "scripts/generate_sbom.py"}],
    },
    "components": components,
}
(out_dir / "sbom.cdx.json").write_text(json.dumps(bom, indent=2) + "\n")
print(f"wrote security/sbom/sbom.cdx.json with {len(components)} components")
sys.exit(0)
