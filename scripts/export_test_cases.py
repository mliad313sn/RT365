#!/usr/bin/env python3
"""Generate docs/TEST_CASES/TC-<AREA>.md (one quartet file per area) from the evidence index and test docstrings."""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AREAS = {
    "ID": ("Identity, privileged access, maker-checker, mode ladder", "FR-01", "Backend Lead", "Security Architect"),
    "BR": ("Broker adapter certification", "FR-02", "Broker-Connector Lead", "Trading Domain Lead"),
    "MD": ("Market data provenance, freshness, look-ahead", "FR-03", "Data Engineering Lead", "Data Architect"),
    "AI": ("MCP governance and injection defence", "FR-09", "Backend Lead", "MCP Security Agent"),
    "RK": ("Deterministic risk engine", "FR-11", "Backend Lead", "Chief Risk Agent"),
    "AP": ("Human approval, maker != checker", "FR-12", "Backend Lead", "Chief Risk Agent"),
    "EX": ("Execution gateway: idempotency, fencing, failover", "FR-13", "Backend Lead", "Trading Domain Lead / Integration Architect"),
    "RC": ("Reconciliation and break management", "FR-14", "Backend Lead", "Trading Domain Lead"),
    "CP": ("Compliance eligibility, dual key, surveillance, retention", "FR-15", "Backend Lead", "Compliance Agent"),
    "KS": ("Kill Switch", "FR-17", "Backend Lead", "Chief Risk Agent"),
    "NET": ("Plane topology / network policy", "NFR-SEC-01", "Cloud Architect", "Security Architect"),
    "OB": ("Observability, redaction, probes, alerts", "NFR-OBS-01", "SRE Lead", "Chief Risk Agent"),
    "AUD": ("Immutable audit", "NFR-AUD-01", "SRE Lead", "IVA"),
    "BT": ("Backtest single code path and strategy lifecycle", "FR-08", "Quant Research Lead", "Model Risk Lead"),
    "E2E": ("Journeys through the BFF", "FR-16", "Frontend Lead", "QA Lead"),
}
src = ROOT / "test" / "evidence" / "evidence_index.json"
data = json.loads(src.read_text())
by_area: dict[str, list[dict]] = defaultdict(list)
for r in data["records"]:
    by_area[r["test_id"].split("-")[1]].append(r)
for area, records in sorted(by_area.items()):
    title, req, owner, reviewer = AREAS.get(area, (area, "-", "Backend Lead", "pending"))
    quartet = {k: [r for r in records if r["quartet"] == k] for k in ("positive", "negative", "abuse", "recovery")}
    lines = [f"# TC-{area} — {title}", "", f"Control: {title} — Requirement: {req} — RTM row: {req} — Owner: {owner} — Reviewer (≠ owner): {reviewer} — **signature pending** (generated evidence is never self-certified [Source: 00, 11])", "", f"Environment tag: dev/sim — Data version: `{records[0]['data_version']}` — Generated {data['generated_at']} at `{data['git_sha']}`", "", "| Quartet | Test ID | Given/When/Then (docstring) | Expected | Actual | Evidence link |", "|---|---|---|---|---|---|"]
    for kind in ("positive", "negative", "abuse", "recovery"):
        rows = quartet[kind] or [None]
        for r in rows:
            if r is None:
                lines.append(f"| {kind} | — | **GAP** | | | |")
            else:
                lines.append(f"| {kind} | {r['test_id']} | {r['expected'].replace('|', '/')} | pass | {r['actual']} | `{r['evidence_link']}` |")
    lines += ["", f"Quartet complete: {'yes' if all(quartet.values()) else 'NO'}. Records: {len(records)}."]
    (ROOT / "docs" / "TEST_CASES" / f"TC-{area}.md").write_text("\n".join(lines) + "\n")
print(f"wrote {len(by_area)} TEST_CASES files")
