#!/usr/bin/env python3
"""Write requirements.lock.txt from the declared dependency closure only (never the ambient environment) [B-15; O-23].

The previous lock was a `pip freeze` of the whole interpreter and carried unrelated system packages (dbus-python,
conan, PyGObject ...) that pip-audit could not resolve, which is why SCA stayed advisory. This walks the closure of
pyproject's runtime dependencies through the installed distributions, the same way scripts/generate_sbom.py does.
"""

from __future__ import annotations

import re
import sys
import tomllib
from importlib import metadata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
declared = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]["dependencies"]


def base(req: str) -> str:
    return re.split(r"[<>=!~\[ ;]", req, maxsplit=1)[0].strip().lower()


seen: dict[str, str] = {}
stack = [base(d) for d in declared]
missing: list[str] = []
while stack:
    name = stack.pop()
    if name in seen:
        continue
    try:
        dist = metadata.distribution(name)
    except metadata.PackageNotFoundError:
        missing.append(name)
        continue
    seen[name] = dist.version
    for req in dist.requires or []:
        if "extra ==" in req:
            continue
        marker_ok = True
        if ";" in req:
            from packaging.markers import Marker

            try:
                marker_ok = Marker(req.split(";", 1)[1].strip()).evaluate()
            except Exception:  # noqa: BLE001
                marker_ok = True
        if marker_ok:
            stack.append(base(req))
if missing:
    print(f"FAIL: declared dependencies not installed: {missing} (run make install)")
    sys.exit(1)
out = ROOT / "requirements.lock.txt"
out.write_text("".join(f"{n}=={v}\n" for n, v in sorted(seen.items())))
print(f"wrote {out.name}: {len(seen)} pinned distributions from the declared closure")
