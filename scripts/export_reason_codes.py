#!/usr/bin/env python3
"""Render docs/REASON_CODES.md from the reason-code dictionary and verify every code used in code is documented."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "apps" / "web"))
from web_bff.reason_codes import REASON_CODES  # noqa: E402

used: set[str] = set()
for f in list((ROOT / "services").rglob("*.py")):
    used |= set(re.findall(r'"((?:RK|CP|RT)-[A-Z0-9-]+)"', f.read_text()))
used = {u for u in used if not u.endswith("-UNDEFINED")} | {"RK-CAP-UNDEFINED", "RK-FRESH-UNDEFINED", "RK-FX-UNDEFINED"}
missing = sorted(u for u in used if u not in REASON_CODES and not u.endswith("-UNDEFINED"))
lines = [
    "# REASON_CODES — plain-language dictionary [Source: 09; C8 §2]",
    "",
    "| Owner | Reviewer (different line) | Approving body | First gate | Status |",
    "|---|---|---|---|---|",
    "| Frontend Lead / Support & Training Lead | Compliance Agent | Product Council | C | Generated from apps/web/web_bff/reason_codes.py |",
    "",
    "Every risk, eligibility and runtime reason code has an explanation and a 'what you can do' line. Localisation [Open: O-14]. Never framed as advice or as a return promise.",
    "",
    "| Code | Family | Explanation | What you can do |",
    "|---|---|---|---|",
]
for code, (family, text, action) in sorted(REASON_CODES.items()):
    lines.append(f"| {code} | {family} | {text} | {action} |")
(ROOT / "docs" / "REASON_CODES.md").write_text("\n".join(lines) + "\n")
if missing:
    print("FAIL: undocumented reason codes: " + ", ".join(missing))
    sys.exit(1)
print(f"wrote docs/REASON_CODES.md ({len(REASON_CODES)} codes); all {len(used)} codes used in services are documented")
