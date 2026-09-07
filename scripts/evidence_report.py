#!/usr/bin/env python3
"""Build docs/TEST_CASES/EVIDENCE_REPORT.md from test/evidence/evidence_index.json: quartet coverage per control."""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
src = ROOT / "test" / "evidence" / "evidence_index.json"
if not src.exists():
    print("no evidence index; run pytest first")
    sys.exit(1)
data = json.loads(src.read_text())
by_area: dict[str, dict[str, list[dict]]] = defaultdict(lambda: defaultdict(list))
for r in data["records"]:
    area = r["test_id"].split("-")[1]
    by_area[area][r["quartet"]].append(r)
lines = [
    "# TEST_CASES — Evidence report (generated)",
    "",
    f"Generated {data['generated_at']} at base commit `{data['git_sha']}` (the working tree at generation time; CI regenerates this report at the pushed commit); pytest exit status {data['exit_status']}. Environment tag: dev/sim. Data version: `{data['records'][0]['data_version'] if data['records'] else '-'}`.",
    "",
    "Reviewer column is **pending** by construction: the author never certifies their own evidence [Source: 00, 11]. The QA Lead and the 2nd-line owner sign rows in docs/AUDIT_EVIDENCE_INDEX.md.",
    "",
    "## Control-quartet coverage per area",
    "",
    "| Area | positive | negative | abuse | recovery | full quartet | tests | failed |",
    "|---|---|---|---|---|---|---|---|",
]
full = 0
for area in sorted(by_area):
    q = by_area[area]
    counts = {k: len(q.get(k, [])) for k in ("positive", "negative", "abuse", "recovery")}
    complete = all(counts.values())
    full += complete
    total = sum(len(v) for v in q.values())
    failed = sum(1 for v in q.values() for r in v if r["actual"] != "passed")
    lines.append(
        f"| TC-{area} | {counts['positive']} | {counts['negative']} | {counts['abuse']} | {counts['recovery']} | {'yes' if complete else 'NO'} | {total} | {failed} |"
    )
lines += [
    "",
    f"Areas with a full quartet: {full}/{len(by_area)}.",
    "",
    "## Evidence records",
    "",
    "| Test ID | Requirement | Quartet | Env | Expected | Actual | Evidence link | Owner | Reviewer |",
    "|---|---|---|---|---|---|---|---|---|",
]
for r in sorted(data["records"], key=lambda x: (x["test_id"], x["evidence_link"])):
    lines.append(
        f"| {r['test_id']} | {r['requirement']} | {r['quartet']} | {r['environment']} | {r['expected'].replace('|', '/')} | {r['actual']} | `{r['evidence_link']}` | {r['owner']} | {r['reviewer']} |"
    )
(ROOT / "docs" / "TEST_CASES" / "EVIDENCE_REPORT.md").write_text("\n".join(lines) + "\n")
print(f"wrote docs/TEST_CASES/EVIDENCE_REPORT.md: {len(data['records'])} records, {full}/{len(by_area)} areas with full quartet")
