#!/usr/bin/env python3
"""Load the RoboTrader project lifecycle into a Meridian IT-PMO instance (https://github.com/mliad313sn/Meridian) [ADR-017].

Meridian holds the portfolio view: one programme (RBT), one governance project carrying gates A–F as milestones,
one project per epic E01..E15, the RAID register, the open human acts as meeting actions and the decision log
as meeting decisions of the Product Owner's weekly. The repository ledgers stay the source of truth; this script
is idempotent (re-runs update what exists by name/id) and never deletes anything in Meridian.

Usage:
  MERIDIAN_URL=http://localhost:4173 MERIDIAN_EMAIL=admin@meridian.example MERIDIAN_PASSWORD=... \
      python3 scripts/meridian_sync.py [--dry-run] [--json out.json]
Credentials come from the environment only (never from the repository). The demo credentials of a seeded
instance are refused unless MERIDIAN_ALLOW_DEMO=1 (they are public).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx

ROOT = Path(__file__).resolve().parents[1]
SITE = {"id": "RTX", "city": "RoboTrader (remote, dev/sim)"}
PROGRAMME = {"id": "RBT", "name": "Global AI-MCP RoboTrader"}
DEMO = ("admin@meridian.example", "meridian-admin-2026")
# Planning horizon per gate. Dates are placeholders until O-17 (roadmap dates after the capacity model) is decided.
GATE_DATES = {"A": "2026-09-08", "B": "2026-10-30", "C": "2026-12-18", "D": "2027-02-26", "E": "2027-04-30", "F": "2027-06-30"}
GATE_EVIDENCE = {
    "A": "approved charter, personas, jurisdiction hypothesis, measurable outcomes (passed with conditions D-048)",
    "B": "threat model, data flows, ADRs, capacity model, control ownership",
    "C": "broker sandbox certification, deterministic risk tests, reconciliation, audit and support workflows",
    "D": "independent quant validation, security assessment, compliance sign-off, trained operators, rollback drill",
    "E": "capital envelope, runtime monitoring, automatic halts, model thresholds, incident command",
    "F": "no unresolved critical; SLO, DR, accessibility, support, disclosures, legal terms, release dossier",
}
PEOPLE = [
    "Product Owner",
    "Program Orchestrator",
    "Backend Lead",
    "SRE Lead",
    "Security Architect",
    "Compliance Agent",
    "Legal Agent",
    "Chief Risk Agent",
    "Quant Research Lead",
    "Frontend Lead",
    "Broker-Connector Lead",
    "Data Engineering Lead",
    "MCP Security Agent",
    "Independent Validation Agent",
]
RAID_KIND = {
    "Risk": "Risk",
    "Issue": "Issue",
    "Assumption": "Assumption",
    "Dependency": "Dependency",
    "Gap": "Issue",
    "Decision": "Assumption",
    "Open item": "Issue",
    "Observation": "Assumption",
    "Risk (accepted)": "Risk",
}
RAID_RESPONSE = {"Risk": "Mitigate", "Issue": "Fix", "Assumption": "Monitor", "Dependency": "Monitor"}


class Meridian:
    def __init__(self, url: str, dry: bool) -> None:
        self.c = httpx.Client(base_url=url, timeout=30)
        self.dry = dry
        self.log: list[str] = []
        self.db: dict[str, Any] = {}

    def login(self, email: str, password: str) -> None:
        r = self.c.post("/api/auth/login", json={"email": email, "password": password})
        if r.status_code != 200:
            raise SystemExit(f"login failed ({r.status_code}): {r.text[:200]}")
        self.refresh()

    def refresh(self) -> None:
        self.db = self.c.get("/api/bootstrap").json()["db"]

    def _write(self, method: str, path: str, body: dict[str, Any]) -> dict[str, Any]:
        if self.dry:
            self.log.append(f"DRY {method} {path} {json.dumps(body)[:120]}")
            return {"id": "dry"}
        r = self.c.request(method, path, json=body)
        if r.status_code >= 300:
            raise SystemExit(f"{method} {path} -> {r.status_code}: {r.text[:300]}")
        self.log.append(f"{method} {path} -> {r.status_code}")
        return r.json() if r.content else {}

    # --- structure ------------------------------------------------------------------------------------------
    def ensure_site(self) -> None:
        if any(s["id"] == SITE["id"] for s in self.db["sites"]):
            return
        self._write("POST", "/api/admin/sites", SITE)

    def ensure_programme(self) -> None:
        if any(p["id"] == PROGRAMME["id"] for p in self.db["programmes"]):
            return
        self._write("POST", "/api/admin/programmes", PROGRAMME)

    def ensure_people(self) -> dict[str, str]:
        ids: dict[str, str] = {}
        for name in PEOPLE:
            found = next((p for p in self.db["people"] if p["name"] == name and p.get("site") == SITE["id"]), None)
            if found:
                ids[name] = found["id"]
                continue
            out = self._write("POST", "/api/admin/people", {"name": name, "site": SITE["id"], "role": name, "fte": 1})
            ids[name] = out.get("person", {}).get("id") or out.get("id", "dry")
        return ids

    def ensure_project(self, name: str, *, pm: str | None, start: str, finish: str, desc: str, level: str = "group") -> str:
        found = next((p for p in self.db["projects"] if p["name"] == name and p.get("programme") == PROGRAMME["id"]), None)
        if found:
            return found["id"]
        out = self._write(
            "POST",
            "/api/projects",
            {
                "name": name,
                "programme": PROGRAMME["id"],
                "site": SITE["id"],
                "governanceLevel": level,
                "pm": pm,
                "method": "Hybrid",
                "start": start,
                "finish": finish,
                "desc": desc,
                "budget": 0,
                "contingency": 0,
            },
        )
        return out.get("id", "dry")

    def ensure_milestone(self, project_id: str, name: str, date: str, criteria: str, done: bool, accepted_by: str | None) -> None:
        proj = next((p for p in self.db["projects"] if p["id"] == project_id), None)
        found = next((m for m in self.db["milestones"] if m.get("project") == project_id and m["name"] == name), None)
        if not found:
            if proj is None and not self.dry:
                return
            self._write(
                "POST", "/api/milestones", {"project": project_id, "name": name, "date": date, "version": (proj or {}).get("version", 1)}
            )
            if self.dry:
                return
            self.refresh()
            found = next((m for m in self.db["milestones"] if m.get("project") == project_id and m["name"] == name), None)
        if found and (found.get("acceptanceCriteria") != criteria or (done and not found.get("done"))):
            body: dict[str, Any] = {"acceptanceCriteria": criteria, "version": found["version"]}
            if done:
                body.update({"done": True, "acceptedBy": accepted_by})
            self._write("PATCH", f"/api/milestones/{found['id']}", body)

    # --- registers ------------------------------------------------------------------------------------------
    def ensure_raid(self, project_id: str, item_id: str, kind: str, title: str, detail: str, owner: str | None) -> None:
        tag = f"[{item_id}]"
        if any(r.get("title", "").startswith(tag) for r in self.db.get("raid", [])):
            return
        k = RAID_KIND.get(kind, "Issue")
        self._write(
            "POST",
            "/api/raid",
            {
                "type": k,
                "project": project_id,
                "title": f"{tag} {title}"[:300],
                "detail": detail[:4000],
                "p": 3,
                "i": 3,
                "response": RAID_RESPONSE[k],
                "owner": owner,
            },
        )

    def ensure_series(self, name: str, chair: str | None) -> str:
        found = next((s for s in self.db.get("meetingSeries", self.db.get("series", [])) if s["name"] == name), None)
        if found:
            return found["id"]
        r = self.c.get("/api/meetings/series")
        for s in r.json().get("series", []) if r.status_code == 200 else []:
            if s["name"] == name:
                return s["id"]
        out = self._write(
            "POST",
            "/api/meetings/series",
            {
                "name": name,
                "scopeKind": "programme",
                "programmeId": PROGRAMME["id"],
                "cadence": "weekly",
                "chairId": chair,
                "weekday": 1,
                "timeboxMin": 25,
            },
        )
        return out.get("id", "dry")

    def open_occurrence(self, series_id: str, date: str) -> str:
        out = self._write("POST", f"/api/meetings/series/{series_id}/occurrences", {"meetsOn": date})
        occ = out.get("id", "dry")
        if not self.dry:
            o = self.c.get(f"/api/meetings/occurrences/{occ}").json()
            status = (o.get("occurrence") or o).get("status")
            if status == "scheduled":
                self._write("POST", f"/api/meetings/occurrences/{occ}/open", {})
        return occ

    def existing_decisions(self, occ: str) -> set[str]:
        if self.dry:
            return set()
        o = self.c.get(f"/api/meetings/occurrences/{occ}").json()
        return {d.get("headline", "") for d in o.get("decisions", [])}

    def existing_actions(self) -> set[str]:
        if self.dry:
            return set()
        r = self.c.get("/api/meetings/actions")
        return {a.get("title", "") for a in (r.json().get("actions", []) if r.status_code == 200 else [])}


# --- ledger readers ----------------------------------------------------------------------------------------------------
def rows(path: Path, prefix: str) -> list[list[str]]:
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith(prefix):
            out.append([c.strip() for c in line.strip().strip("|").split("|")])
    return out


def epics() -> list[tuple[str, str, str, str]]:
    out = []
    for c in rows(ROOT / "docs" / "BACKLOG.md", "| E"):
        m = re.match(r"(E\d\d) (.+)", c[0])
        if m and len(c) >= 5:
            out.append((m.group(1), m.group(2), c[1], c[3]))  # id, title, lead, gate
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--json", help="write a summary of what exists after the run")
    args = ap.parse_args(argv)
    url = os.environ.get("MERIDIAN_URL", "http://localhost:4173")
    email, password = os.environ.get("MERIDIAN_EMAIL", ""), os.environ.get("MERIDIAN_PASSWORD", "")
    if not email or not password:
        if os.environ.get("MERIDIAN_ALLOW_DEMO") == "1":
            email, password = DEMO
        else:
            print("set MERIDIAN_EMAIL and MERIDIAN_PASSWORD (or MERIDIAN_ALLOW_DEMO=1 for a seeded demo instance only)", file=sys.stderr)
            return 2
    m = Meridian(url, args.dry_run)
    m.login(email, password)
    today = datetime.now(tz=UTC).date().isoformat()

    m.ensure_site()
    m.ensure_programme()
    if not m.dry:
        m.refresh()
    people = m.ensure_people()
    if not m.dry:
        m.refresh()
    po = people.get("Product Owner")

    gov = m.ensure_project(
        "RBT-GOV Programme governance — gates A–F",
        pm=po,
        start="2026-09-07",
        finish=GATE_DATES["F"],
        desc="Gate ladder dev→sim→shadow→paper→supervised pilot→capped autonomous pilot→controlled GA; each gate authorises only the next rung. Product Owner decides (D-039/D-040); councils advisory. Dates are placeholders until O-17.",
    )
    projects: dict[str, str] = {"GOV": gov}
    for eid, title, lead, gate in epics():
        finish = GATE_DATES.get(gate[0], GATE_DATES["F"])
        projects[eid] = m.ensure_project(
            f"{eid} {title}",
            pm=people.get(lead.split(" /")[0].replace("Broker-Connector Lead", "Broker-Connector Lead")),
            start="2026-09-07",
            finish=finish,
            desc=f"Epic {eid}; accountable {lead}; first gate {gate}; build prompt goals/build/{eid}_*.md",
        )
    if not m.dry:
        m.refresh()
    for g, date in GATE_DATES.items():
        m.ensure_milestone(gov, f"Gate {g}", date, GATE_EVIDENCE[g], done=(g == "A"), accepted_by=po)

    # RAID: every open O-/R- row of docs/RAID_LOG.md onto the governance project (epic mapping is a later refinement)
    for c in rows(ROOT / "docs" / "RAID_LOG.md", "| O-") + rows(ROOT / "docs" / "RAID_LOG.md", "| R-"):
        if len(c) < 6 or not re.match(r"^[OR]-\d+$", c[0]):
            continue
        item_id, kind, item, owner, needed, status = c[0], c[1], c[2], c[3], c[4], c[5]
        if status.lower().startswith(
            ("closed", "decided", "remediated", "accepted", "pack ready", "rule recorded", "reopened")
        ) and not status.lower().startswith("reopened"):
            continue
        m.ensure_raid(gov, item_id, kind, item, f"Owner: {owner}. Needed by: {needed}. Status: {status}. Source: docs/RAID_LOG.md", po)

    # Weekly of the Product Owner: decisions and open human acts
    series = m.ensure_series("RoboTrader weekly — Product Owner", po)
    occ = m.open_occurrence(series, today)
    have = m.existing_decisions(occ)
    for c in rows(ROOT / "docs" / "DECISION_LOG.md", "| D-0"):
        if len(c) < 3 or not c[0].startswith("D-0"):
            continue
        headline = f"{c[0]}: {c[2]}"[:300]
        if headline in have:
            continue
        m._write(
            "POST",
            f"/api/meetings/occurrences/{occ}/decisions",
            {"headline": headline, "rationale": (c[5] if len(c) > 5 else "")[:4000], "projectId": gov, "decidedBy": po},
        )
    have_actions = m.existing_actions()
    for c in rows(ROOT / "docs" / "MISSING_ACTIONS.md", "| H-"):
        if len(c) < 9 or c[8].lower().startswith("closed"):
            continue
        title = f"{c[0]}: {c[1]}"[:300]
        if title in have_actions:
            continue
        m._write(
            "POST",
            f"/api/meetings/occurrences/{occ}/actions",
            {
                "title": title,
                "detail": f"Category {c[2]}; owner {c[3]}; blocks gate {c[4]}; prepared by {c[5]}; evidence when done: {c[6]}"[:2000],
                "ownerId": po,
                "projectId": gov,
            },
        )

    if not m.dry:
        m.refresh()
    summary = {
        "url": url,
        "at": today,
        "dry_run": m.dry,
        "projects": [p["name"] for p in m.db["projects"] if p.get("programme") == PROGRAMME["id"]],
        "milestones": [mm["name"] for mm in m.db["milestones"] if mm.get("project") == gov],
        "raid_items": sum(1 for r in m.db.get("raid", []) if r.get("project") == gov),
        "writes": len([line for line in m.log if not line.startswith("DRY")]),
    }
    print(json.dumps(summary, indent=2))
    if args.json:
        Path(args.json).write_text(json.dumps({"summary": summary, "log": m.log}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
