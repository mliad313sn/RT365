#!/usr/bin/env python3
"""Generate a CycloneDX 1.5 JSON SBOM for the Python service set [Source: 06; SBOM.md]."""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from importlib import metadata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
out_dir = ROOT / "security" / "sbom"
out_dir.mkdir(parents=True, exist_ok=True)
components = []
for dist in sorted(metadata.distributions(), key=lambda d: d.metadata["Name"].lower()):
    name = dist.metadata["Name"]
    components.append({"type": "library", "name": name, "version": dist.version, "purl": f"pkg:pypi/{name.lower()}@{dist.version}"})
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
