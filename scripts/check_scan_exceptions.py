#!/usr/bin/env python3
"""Validate security/scan_exceptions.yaml [D-054]: every entry has tool, id, location, justification, owner, decision (D-nnn)
and an expiry no later than 90 days after the decision date recorded in docs/DECISION_LOG.md; expired entries fail."""

from __future__ import annotations

import re
import sys
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
data = yaml.safe_load((ROOT / "security" / "scan_exceptions.yaml").read_text()) or {}
entries = data.get("exceptions") or []
log = (ROOT / "docs" / "DECISION_LOG.md").read_text()
today = datetime.now(tz=UTC).date()
problems: list[str] = []
for i, e in enumerate(entries):
    for key in ("tool", "id", "location", "justification", "owner", "decision", "expires"):
        if not e.get(key):
            problems.append(f"entry {i}: missing {key}")
    dec = str(e.get("decision", ""))
    m = re.search(rf"^\| {re.escape(dec)} \| (\d{{4}}-\d{{2}}-\d{{2}}) \|", log, re.M)
    if not m:
        problems.append(f"entry {i}: decision {dec!r} not found in DECISION_LOG.md")
        continue
    decided = date.fromisoformat(m.group(1))
    expires = e["expires"] if isinstance(e["expires"], date) else date.fromisoformat(str(e["expires"]))
    if expires > decided + timedelta(days=90):
        problems.append(f"entry {i}: expiry {expires} is more than 90 days after decision {dec} ({decided})")
    if expires < today:
        problems.append(f"entry {i}: expired on {expires}")
# Inline suppressions are forbidden (D-054): every exception lives in the YAML file with a decision reference.
SELF = Path(__file__).resolve()
NEEDLES = ("# " + "nosec", "--ignore" + "-vuln")
for root in ("libs", "services", "mcp", "connectors", "observability", "apps", "scripts"):
    for f in (ROOT / root).rglob("*.py"):
        if f.resolve() == SELF:
            continue
        for n, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            if any(needle in line for needle in NEEDLES):
                problems.append(f"{f.relative_to(ROOT)}:{n}: inline suppression forbidden (use security/scan_exceptions.yaml)")
if problems:
    print("FAIL scan exceptions:\n - " + "\n - ".join(problems))
    sys.exit(1)
print(f"OK scan exceptions: {len(entries)} entries, none expired")
