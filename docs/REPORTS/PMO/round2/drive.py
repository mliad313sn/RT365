#!/usr/bin/env python3
"""Round-2 hand drive of the RoboTrader programme into Meridian IT-PMO.

Goes beyond scripts/meridian_sync.py (which is our base loader and is not in this role's
write scope, so it is run unmodified). Everything here is done by hand through the API that
the web client uses, and every request is recorded with a timestamp, a status code and a
duration into a machine-readable evidence file.

Usage:
  MERIDIAN_URL=... MERIDIAN_EMAIL=... MERIDIAN_PASSWORD=... python3 drive.py --out evidence.json
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Any

import httpx

ROOT = Path(__file__).resolve().parents[4]  # /home/user/RT365
PROGRAMME = "RBT"
SITE = "RTX"
GATE_LETTERS = ("A", "B", "C", "D", "E", "F")


# ---------------------------------------------------------------- evidence ---
class Ev:
    """Every request and response, with timing and status. Nothing is summarised away."""

    def __init__(self, url: str) -> None:
        self.c = httpx.Client(base_url=url, timeout=60)
        self.records: list[dict[str, Any]] = []
        self.section = "start"
        self.seq = 0

    def mark(self, section: str) -> None:
        self.section = section
        print(f"\n=== {section} ===", flush=True)

    def call(self, method: str, path: str, body: Any = None, note: str = "",
             headers: dict[str, str] | None = None) -> tuple[int, Any]:
        self.seq += 1
        t0 = time.perf_counter()
        at = datetime.now(tz=UTC).isoformat()
        try:
            r = self.c.request(method, path, json=body, headers=headers)
            ms = round((time.perf_counter() - t0) * 1000, 1)
            status = r.status_code
            try:
                resp = r.json()
            except Exception:
                resp = r.text[:400]
        except Exception as e:  # transport failure is evidence too
            ms = round((time.perf_counter() - t0) * 1000, 1)
            status, resp = -1, {"transport_error": repr(e)[:400]}
        self.records.append({
            "seq": self.seq, "section": self.section, "at": at, "method": method, "path": path,
            "request": _trunc(body), "status": status, "ms": ms, "response": _trunc(resp),
            "note": note,
        })
        return status, resp

    def dump(self, out: Path, summary: dict[str, Any]) -> None:
        out.write_text(json.dumps({"summary": summary, "requests": self.records}, indent=1,
                                  ensure_ascii=False), encoding="utf-8")


def _trunc(o: Any, n: int = 700) -> Any:
    if o is None:
        return None
    s = json.dumps(o, ensure_ascii=False) if not isinstance(o, str) else o
    return s if len(s) <= n else s[:n] + f"…<+{len(s) - n} chars>"


# ------------------------------------------------------------ ledger readers ---
def rows(path: Path, prefix: str) -> list[list[str]]:
    return [[c.strip() for c in ln.strip().strip("|").split("|")]
            for ln in path.read_text(encoding="utf-8").splitlines() if ln.startswith(prefix)]


def gate_num(text: str) -> int | None:
    """The gate a ledger row names, as a ladder position 1..6. Stated, not derived."""
    m = re.search(r"\b([A-F])\b", (text or "").upper())
    return GATE_LETTERS.index(m.group(1)) + 1 if m else None


# Rule R2-PI-1. docs/RAID_LOG.md states NO probability and NO impact (six columns:
# ID, Type, Item, Owner, Needed by, Status). A constant 3x3 carries no information; an
# invented number carries false information. So P and I are DERIVED, by this published rule,
# from fields the ledger does state, and every item says so in its own detail text.
def derive_pi(kind: str, status: str, gate: int | None) -> tuple[int, int, int | None, int | None]:
    s = (status or "").lower()
    if s.startswith("reopened"):
        p = 5
    elif s.startswith(("open", "requested", "deviation")):
        p = 4
    elif s.startswith(("partial", "p-2")):
        p = 3
    elif s.startswith(("remediated", "decided", "rule recorded", "accepted", "closed")):
        p = 2
    else:
        p = 3
    base = {"Risk": 4, "Issue": 4, "Gap": 3, "Dependency": 3,
            "Assumption": 2, "Observation": 2, "Decision": 2, "Open item": 3}.get(kind, 3)
    i = min(5, base + (1 if gate is not None and gate <= 3 else 0))
    # Target residual: what the item is being driven to, one notch below on both axes,
    # never below 1. Stated as a target, not as a measurement.
    return p, i, max(1, p - 2), max(1, i - 1)


RAID_KIND = {"Risk": "Risk", "Issue": "Issue", "Assumption": "Assumption", "Dependency": "Dependency",
             "Gap": "Issue", "Decision": "Assumption", "Open item": "Issue",
             "Observation": "Assumption", "Risk (accepted)": "Risk"}
RESPONSE = {"Risk": "Mitigate", "Issue": "Fix", "Assumption": "Monitor", "Dependency": "Monitor"}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    url = os.environ["MERIDIAN_URL"]
    ev = Ev(url)
    today = date.today()
    summary: dict[str, Any] = {"url": url, "at": datetime.now(tz=UTC).isoformat(), "steps": {}}

    # ------------------------------------------------------------------ login
    ev.mark("login")
    st, _ = ev.call("POST", "/api/auth/login",
                    {"email": os.environ["MERIDIAN_EMAIL"], "password": os.environ["MERIDIAN_PASSWORD"]})
    if st != 200:
        print("login failed", st)
        return 2
    st, boot = ev.call("GET", "/api/bootstrap", note="read the book back")
    db = boot["db"]
    people = {p["name"]: p["id"] for p in db["people"]}
    projects = {p["name"]: p["id"] for p in db["projects"] if p.get("programme") == PROGRAMME}
    by_epic = {n.split(" ")[0]: i for n, i in projects.items()}
    gov = by_epic.get("RBT-GOV")
    po = people.get("Product Owner")
    orch = people.get("Program Orchestrator")
    iva = people.get("Independent Validation Agent")
    ms_gov = {m["name"]: m for m in db["milestones"] if m.get("project") == gov}
    summary["directory"] = {"people": len(people), "projects": len(projects), "gov": gov,
                            "gov_milestones": sorted(ms_gov)}

    # ---------------------------------------------- 1. gate criteria + evidence
    # Our six gates are the programme's ladder (positions 1..6), so gate criteria bind to
    # them. Round 1 could not do this at all: the six gates were plain milestones.
    ev.mark("1. gate criteria on gates A-F, with an independent reviewer")
    GATE_EXIT = {
        1: ["Charter approved by the Product Owner with the conditions of D-048 recorded",
            "Personas and measurable outcomes stated; profit is an objective, never a promise",
            "Jurisdiction hypothesis written and challenged by the Compliance council"],
        2: ["THREAT_MODEL v1.1 accepted by the Security & Privacy Board",
            "DATA_FLOWS accepted by the Architecture Review Board with boundaries B9/B10/B11",
            "Capacity model presented with numbers and accepted",
            "Control ownership named for every critical control"],
        3: ["Broker sandbox certification passed in both dedupe modes",
            "Deterministic risk tests green: control quartet on every critical control",
            "Reconciliation clean-run rule proven before any restore",
            "Audit and support workflows exercised end to end"],
        4: ["Independent quant validation signed by a reviewer who did not build the model",
            "Security assessment closed with no unresolved critical",
            "Compliance sign-off on the jurisdiction set actually served",
            "Operators trained and a rollback drill evidenced"],
        5: ["Capital envelope set and enforced by the deterministic Execution Gateway",
            "Runtime monitoring and automatic halts proven by drill",
            "Incident command rota named with a deputy"],
        6: ["No unresolved critical finding on any register",
            "SLO, DR, accessibility, support, disclosures and legal terms evidenced",
            "Release dossier assembled and reviewed by Independent Validation"],
    }
    crit_ids: dict[int, list[str]] = {}
    existing = {c["text"]: c for c in db.get("criteria", []) if c.get("project") == gov}
    summary["steps"]["criteria_scaffolded_by_meridian"] = {
        "total_book": len(db.get("criteria", [])), "on_gov": len(existing),
        "sample": [c["text"] for c in db.get("criteria", []) if c.get("project") == gov][:8]}
    for g, texts in GATE_EXIT.items():
        for t in texts:
            if t in existing:
                crit_ids.setdefault(g, []).append(existing[t]["id"])
                continue
            st, r = ev.call("POST", "/api/criteria", {"project": gov, "gate": g, "text": t})
            if st == 201:
                crit_ids.setdefault(g, []).append(r["id"])
    summary["steps"]["criteria_created"] = sum(len(v) for v in crit_ids.values())

    # Gate A passed with conditions (D-048): find its criteria met by a named reviewer who
    # does not own the evidence. Author != reviewer is the whole point of REQ-04.
    met = 0
    for cid in crit_ids.get(1, []):
        st, _ = ev.call("PATCH", f"/api/criteria/{cid}",
                        {"met": True, "reviewedBy": iva, "version": 1,
                         "note": "Found met by Independent Validation; evidence owned by the "
                                 "Product Owner and the Program Orchestrator, not by the reviewer."})
        met += st == 200
    summary["steps"]["criteria_met_gate_A"] = met

    # An evidence reference on a criterion: try the typed external reference V-10/REQ-29 asked
    # for, then fall back to the note. Recorded either way.
    if crit_ids.get(2):
        ev.call("PATCH", f"/api/criteria/{crit_ids[2][0]}",
                {"externalRef": {"repo": "RT365", "commit": "b912249",
                                 "artefact": "docs/THREAT_MODEL.md", "sha256": "unverified"},
                 "version": 1},
                note="V-10/REQ-29 probe: does a criterion accept a typed external reference?")

    # ------------------------------------- 2. RAID with a derived, published rating
    ev.mark("2. RAID re-rated off the constant 3x3, by published rule R2-PI-1")
    st, boot = ev.call("GET", "/api/bootstrap", note="read the RAID back")
    raid_live = {r["title"]: r for r in boot["db"].get("raid", [])}
    ledger: dict[str, list[str]] = {}
    for c in rows(ROOT / "docs" / "RAID_LOG.md", "| O-") + rows(ROOT / "docs" / "RAID_LOG.md", "| R-"):
        if len(c) >= 6 and re.match(r"^[OR]-\d+$", c[0]):
            ledger[c[0]] = c
    rated = 0
    dist: dict[str, int] = {}
    for title, item in raid_live.items():
        m = re.match(r"^\[([OR]-\d+)\]", title)
        if not m or m.group(1) not in ledger:
            continue
        c = ledger[m.group(1)]
        kind, owner_txt, needed, status = c[1], c[3], c[4], c[5]
        g = gate_num(needed)
        p, i, tp, ti = derive_pi(kind, status, g)
        dist[f"{p}x{i}"] = dist.get(f"{p}x{i}", 0) + 1
        body: dict[str, Any] = {
            "p": p, "i": i, "tp": tp, "ti": ti,
            "response": RESPONSE[RAID_KIND.get(kind, "Issue")],
            "review": (today + timedelta(days=14 if p >= 4 else 42)).isoformat(),
            "version": item.get("version", 1),
            "detail": (item.get("detail", "") +
                       f" | P={p} I={i} target {tp}x{ti} DERIVED by rule R2-PI-1 from the stated "
                       f"Type={kind}, Status={status}, Needed by={needed}. "
                       f"docs/RAID_LOG.md states no probability and no impact.")[:4000],
        }
        if g:
            body["gate"] = g
        st, _ = ev.call("PATCH", f"/api/raid/{item['id']}", body,
                        note=f"{m.group(1)} {kind}/{status[:20]} gate={g}")
        rated += st == 200
    summary["steps"]["raid_rated"] = rated
    summary["steps"]["raid_pi_distribution"] = dict(sorted(dist.items()))

    # ------------------------------- 3. decisions as decision records, not minutes
    ev.mark("3. D-039..D-066 as decision records (migration 034/039), with alternatives and dissent")
    dec_rows = [c for c in rows(ROOT / "docs" / "DECISION_LOG.md", "| D-0") if len(c) >= 7]
    wanted = [c for c in dec_rows if 39 <= int(c[0].split("-")[1]) <= 66]
    made: dict[str, str] = {}
    first = True
    for c in wanted:
        did, when, headline, body, alts, prov, evid = c[0], c[1], c[2], c[3], c[4], c[5], c[6]
        # Dissent: the ledger writes it inside the alternatives column as "rejected by/…".
        dissent = " · ".join(re.findall(r"\(rejected[^)]*\)", alts)) or (
            "No dissent recorded in docs/DECISION_LOG.md for this decision." )
        council = ""
        cm = re.search(r"(Product Owner|Trading Risk Committee|Architecture Review Board|CAB|"
                       r"Security & Privacy Board|Independent Validation)", body)
        if cm:
            council = cm.group(1)
        payload: dict[str, Any] = {
            "headline": f"{did}: {headline}"[:1000],
            "rationale": body[:4000],
            "alternatives": alts[:4000],
            "dissent": dissent[:2000],
            "provenance": prov[:200],
            "council": council,
            "decidedBy": po,
            "decidedOn": when,
            "projectId": gov,
            "status": "Ratified",
            "ratifiedBy": "Product Owner (human), per D-039",
        }
        if first:
            # Probe: our evidence is a repository path, not a URL. Does the record take it?
            ev.call("POST", "/api/decisions", {**payload, "evidenceUri": evid[:200]},
                    note="probe: evidenceUri as a repository path, not http(s)")
            first = False
        st, r = ev.call("POST", "/api/decisions", payload, note=did)
        if st == 201:
            made[did] = r["id"]
    summary["steps"]["decision_records"] = len(made)

    # Supersession: D-066 amends ADR-018/ADR-020 territory opened by D-064 if present.
    if "D-066" in made and "D-064" in made:
        ev.call("POST", "/api/decisions", {
            "headline": "D-066 amendment: composition verifies the published audit anchor at start-up",
            "rationale": "Recorded as a superseding record so the earlier ruling stays readable.",
            "alternatives": "Leave the earlier record as the only one (rejected: the trail must show the change).",
            "decidedBy": po, "decidedOn": today.isoformat(), "projectId": gov,
            "supersedes": made["D-064"], "council": "Product Owner", "status": "Proposed",
        }, note="supersedes probe")

    # --------------------------------------- 4. actions with real owners and dates
    ev.mark("4. open human acts as actions with the ledger's own owner and due date")
    st, series = ev.call("GET", "/api/meetings/series")
    sid = next((s["id"] for s in series.get("series", []) if "RoboTrader weekly" in s["name"]), None)
    st, occs = ev.call("GET", f"/api/meetings/series/{sid}/occurrences")
    occ = next((o["id"] for o in occs.get("occurrences", []) if o["status"] == "open"), None)
    summary["steps"]["series"], summary["steps"]["occurrence"] = sid, occ
    st, acts = ev.call("GET", "/api/meetings/actions")
    have = {a["title"]: a for a in acts.get("actions", [])}
    owned, dated, unmapped = 0, 0, []
    for c in rows(ROOT / "docs" / "MISSING_ACTIONS.md", "| H-"):
        if len(c) < 9 or c[8].lower().startswith("closed"):
            continue
        title = f"{c[0]}: {c[1]}"[:300]
        a = have.get(title)
        owner_txt, due = c[3], c[7]
        pid = people.get(owner_txt) or next((v for k, v in people.items() if k in owner_txt), None)
        if pid is None:
            unmapped.append(f"{c[0]}={owner_txt}")
        d = re.search(r"\d{4}-\d{2}-\d{2}", due)
        body = {"version": a["version"] if a else 1}
        if pid:
            body["ownerId"] = pid
        if d:
            body["dueDate"] = d.group(0)
        if a and (pid or d):
            st, _ = ev.call("PATCH", f"/api/meetings/actions/{a['id']}", body,
                            note=f"{c[0]} owner={owner_txt} due={due[:20]}")
            owned += st == 200 and bool(pid)
            dated += st == 200 and bool(d)
    summary["steps"]["actions_owned"] = owned
    summary["steps"]["actions_dated"] = dated
    summary["steps"]["action_owners_not_in_directory"] = unmapped

    # ------------------------------------------ 5. business case and benefits x3
    ev.mark("5. business case and benefits — the value half (V-1/REQ-20 is open upstream)")
    CASES = {
        "RBT-GOV": ("Run one auditable gate ladder for the whole programme so that no rung is "
                    "promoted past what its gate authorises. The payer is buying the right to stop.",
                    "The basis is the blueprint's environment ladder and D-039: one accountable "
                    "decision-maker, councils advisory. No revenue is claimed at any gate."),
        "E13": ("Security and privacy controls that a regulator and an external assessor can "
                "re-derive from evidence, not from assertion.",
                "Basis: THREAT_MODEL v1.1 and the control quartet standard. Cost is engineering "
                "time already committed; no external spend is assumed."),
        "E11": ("An audit and surveillance record that survives a hostile replay, so a decision "
                "taken in March can be re-read in December.",
                "Basis: ADR-018/ADR-020 and TC-DUR-007. The benefit is the avoided cost of an "
                "unreconstructable trail, not a trading return."),
    }
    BENEFITS = {
        "RBT-GOV": [
            ("Compliance", "Every gate decision is re-derivable from evidence",
             "Gate decisions with a complete exit-evidence set at the time of decision",
             "% of gates", 0, 100, None, 1),
            ("Risk", "No promotion past the authorised rung",
             "Environment promotions above the gate's authority", "count", 0, 0, 0, 6),
            ("Compliance", "Author != reviewer != approver holds on every gate criterion",
             "Criteria found met by a reviewer who owns the evidence", "count", 0, 0, 0, 3),
        ],
        "E13": [
            ("Risk", "No unresolved critical security finding at market release",
             "Open critical findings on the security register", "count", 6, 0, None, 6),
            ("Compliance", "Control quartet coverage on every critical control",
             "Critical controls with positive/negative/abuse/recovery tests", "% of controls",
             0, 100, None, 4),
        ],
        "E11": [
            ("Compliance", "Audit chain verifiable from genesis against an off-box anchor",
             "Chain verifications passing against the published anchor", "% of runs", 0, 100, None, 3),
            ("Availability", "Reconciliation breaks detected within one cycle",
             "Breaks detected in the cycle they occur", "% of breaks", 0, 95, None, 5),
        ],
    }
    gate_dates = {1: "2026-09-08", 2: "2026-10-30", 3: "2026-12-18",
                  4: "2027-02-26", 5: "2027-04-30", 6: "2027-06-30"}
    cases, bens = 0, 0
    for key, (summ, basis) in CASES.items():
        pid = by_epic.get(key)
        if not pid:
            continue
        # expectedCost/expectedBenefit are in millions and we have no cost model (O-13 open),
        # so they are deliberately omitted rather than invented. The route requires only summary.
        st, _ = ev.call("PUT", f"/api/projects/{pid}/case", {"summary": summ, "basis": basis},
                        note=f"{key} — no cost figure: O-13 open, a number here would be invented")
        cases += st in (200, 201)
        for kind, title, measure_title, unit, base, target, actual, g in BENEFITS[key]:
            b: dict[str, Any] = {"project": pid, "kind": kind, "title": title,
                                 "measure": measure_title, "unit": unit, "baseline": base,
                                 "target": target, "owner": po, "realiseOn": gate_dates[g],
                                 "detail": "Objective, not a promise. Stated in its own unit; "
                                           "no money conversion is claimed."}
            if actual is not None:
                b["actual"] = actual
            st, _ = ev.call("POST", "/api/benefits", b, note=f"{key} benefit")
            bens += st == 201
    summary["steps"]["business_cases"] = cases
    summary["steps"]["benefits"] = bens

    # Reconfirm the case at the gate that has passed (Gate A).
    if by_epic.get("RBT-GOV"):
        ev.call("POST", f"/api/projects/{gov}/case/reconfirm",
                {"gate": 1, "note": "Reconfirmed at Gate A with the conditions of D-048."},
                note="V-3/REQ-22 probe: is reconfirmation enforced at a gate?")

    # Is the value half reachable by an integration, as V-1 asked? Measure it.
    ev.mark("5b. V-1/REQ-20 probe: value objects through the v1 write API")
    st, key = ev.call("POST", "/api/admin/integrations",
                      {"name": "RT365 field loader (round 2)",
                       "purpose": "Load the RoboTrader programme from the repository ledgers",
                       "scopes": "read:portfolio write:portfolio write:meetings read:audit"})
    token = (key or {}).get("key") or (key or {}).get("secret") or (key or {}).get("token")
    if token:
        h = {"Authorization": f"Bearer {token}"}
        ev.call("GET", "/api/v1/portfolio", None, headers=h, note="the integration can read")
        for coll, extid in (("business-case", "RBT-GOV"), ("benefits", "BEN-EXT-1"),
                            ("programmes", "RBT"), ("people", "PO"), ("sites", "RTX"),
                            ("stakeholders", "STK-1"), ("lessons", "LSN-1")):
            ev.call("PUT", f"/api/v1/{coll}/{extid}", {"title": "probe"}, headers=h,
                    note=f"V-1/E-2 probe: is {coll} writable through v1?")
        # And what IS writable, to show the contrast, with idempotency.
        ev.call("PUT", "/api/v1/raid/RT365-O-999", {
            "project": gov, "type": "Risk", "title": "[RT365 probe] v1 write by external id",
            "detail": "Written by the integration key, to see whose name lands in the audit trail.",
            "p": 2, "i": 2, "response": "Monitor"},
            headers={**h, "Idempotency-Key": "rt365-round2-probe-1"},
            note="v1 write that IS supported")
        ev.call("PUT", "/api/v1/raid/RT365-O-999", {
            "project": gov, "type": "Risk", "title": "[RT365 probe] v1 write by external id",
            "detail": "Written by the integration key, to see whose name lands in the audit trail.",
            "p": 2, "i": 2, "response": "Monitor"},
            headers={**h, "Idempotency-Key": "rt365-round2-probe-1"},
            note="same Idempotency-Key, second time")
    summary["steps"]["integration_key_created"] = bool(token)

    # ---------------------------------- 6. stakeholders, comms, lessons, tolerance
    ev.mark("6. stakeholders, communication plan, lessons, tolerances")
    STAKE = [
        ("Product Owner (repository owner)", "RT365", "Decides every human decision and gate (D-039)",
         5, 5, "Supportive", "Manage closely", po),
        ("Independent Validation", "RT365 3rd line", "Vetoes become findings the owner may override in writing",
         5, 4, "Neutral", "Manage closely", iva),
        ("Trading Risk Committee", "RT365 council", "Advisory on limit policy and exposure caps (O-46 open)",
         4, 3, "Neutral", "Consult", None),
        ("Security & Privacy Board", "RT365 council", "Did not accept SECURITY_PLAN v1.0; Gate B blocked",
         5, 4, "Critical", "Manage closely", None),
        ("Architecture Review Board", "RT365 council", "Did not accept DATA_FLOWS v1.0; O-139 open",
         4, 4, "Critical", "Manage closely", None),
        ("Prospective broker (unnamed)", "External", "No relationship assumed; no market access assumed",
         2, 5, "Unknown", "Monitor", None),
        ("Prospective regulator (unnamed jurisdiction)", "External",
         "No permission assumed; the jurisdiction hypothesis is unchallenged", 1, 5, "Unknown", "Monitor", None),
    ]
    stakes = 0
    for name, org, role, interest, influence, att, eng, person in STAKE:
        st, _ = ev.call("POST", "/api/stakeholders",
                        {"project": gov, "name": name, "organisation": org, "role": role,
                         "interest": interest, "influence": influence, "attitude": att,
                         "engagement": eng, "person": person, "owner": orch,
                         "note": "Recorded from docs/RACI.md and the gate charters."})
        stakes += st == 201
    comms = 0
    for aud, purpose, chan, freq, nxt in [
        ("Product Owner", "The weekly: what is off track, what needs a decision, what is owed",
         "Meridian weekly occurrence + docs/SESSIONS packet", "Weekly", (today + timedelta(days=7)).isoformat()),
        ("Councils (advisory)", "Gate exit evidence for challenge before the owner decides",
         "Gate report circulated from docs/GATE_REPORTS/", "Per gate", "2026-10-30"),
        ("Independent Validation", "Release dossier for the gate under review",
         "docs/RELEASE_CHECKLIST.md + evidence index", "Per gate", "2026-10-30"),
    ]:
        st, _ = ev.call("POST", "/api/comms", {"project": gov, "audience": aud, "purpose": purpose,
                                               "channel": chan, "frequency": freq, "nextOn": nxt,
                                               "owner": orch})
        comms += st == 201
    lessons = 0
    LESSONS = [
        (2, "A finding written from a screenshot instead of from the code is a false defect",
         "Round 1 published a Meridian gate-ladder defect that our own loader caused.",
         "The screenshot showed two ladders; nobody read wbs.js, which scaffolds one.",
         "Read the supplier's code before filing a defect against it."),
        (1, "A number published in prose and not re-derivable fails our own gate standard",
         "docs/PMO.md stated 14 decisions and 21 actions; the evidence file said 48 and 25.",
         "The load evidence had no timings, no bodies and no second-run file.",
         "Every published count cites a machine-readable evidence file that produced it."),
        (6, "An unmeasured project reported GREEN is worse than no report",
         "Sixteen projects read GREEN at 0% in a week when two gate documents were refused.",
         "Health derives from schedule and cost; with neither, the default is the colour that means fine.",
         "Never quote a portfolio health tile that has no measured input behind it."),
    ]
    for g, title, what, why, rec in LESSONS:
        st, _ = ev.call("POST", "/api/lessons",
                        {"project": gov, "gate": g, "category": "Governance", "title": title,
                         "whatHappened": what, "why": why, "recommendation": rec},
                        note=f"lesson tagged to gate {g} of a six-gate ladder")
        lessons += st == 201
    st, _ = ev.call("PUT", f"/api/projects/{gov}/tolerance",
                    {"scheduleDays": 14, "costPct": 0, "benefitPct": 10,
                     "note": "No budget is set (O-13 open), so the cost tolerance is zero by "
                             "construction, not by generosity. Schedule tolerance is two weeks "
                             "on a gate date; beyond that the Product Owner decides."})
    summary["steps"].update({"stakeholders": stakes, "comms": comms, "lessons": lessons,
                             "tolerance": st})

    # ------------------------------------------- 7. change request, work, waves
    ev.mark("7. change request with segregation of duties, work items, rollout waves")
    st, cr = ev.call("POST", "/api/change",
                     {"project": gov, "title": "Move Gate B to 2026-11-27 — two exit documents refused",
                      "desc": "The Security & Privacy Board did not accept SECURITY_PLAN v1.0 and the "
                              "Architecture Review Board did not accept DATA_FLOWS v1.0; no capacity "
                              "number was presented. Gate B was not convened.",
                      "weeks": 4, "cost": 0, "funding": "Contingency", "riskDelta": "0"})
    crid = (cr or {}).get("id")
    if crid:
        ev.call("POST", f"/api/change/{crid}/approve", {"note": "Self-approval attempt by the raiser."},
                note="SoD probe: can the raiser sign their own change?")
    work, waves = 0, 0
    for title, state in [("Gate B evidence set: reconcile THREAT_MODEL and DATA_FLOWS boundaries (O-146)", "Doing"),
                         ("Capacity model with numbers, for the Gate B pack (O-17)", "To do"),
                         ("Control quartet coverage report per critical control", "Doing")]:
        st, _ = ev.call("POST", "/api/workitems", {"project": gov, "title": title, "state": state})
        work += st == 201
    for seq, when, note in [(1, "2027-02-26", "Supervised pilot — Gate D authorises this rung only"),
                            (2, "2027-04-30", "Capped autonomous pilot — Gate E"),
                            (3, "2027-06-30", "Controlled GA — Gate F")]:
        st, _ = ev.call("POST", "/api/waves", {"project": gov, "site": SITE, "seq": seq,
                                               "plannedOn": when, "note": note})
        waves += st == 201
    summary["steps"].update({"change_request": crid, "work_items": work, "waves": waves})

    # ------------------------------------------------ 8. the weekly, and its close
    ev.mark("8. the weekly: agenda, minutes, and the close that freezes the record")
    st, ag = ev.call("GET", f"/api/meetings/occurrences/{occ}", note="the agenda Meridian generated")
    if isinstance(ag, dict):
        agenda = ag.get("agenda") or {}
        summary["steps"]["agenda_sections"] = [
            {"title": s.get("title"), "items": len(s.get("items", [])), "timebox": s.get("timeboxMin")}
            for s in agenda.get("sections", [])]
    ev.call("POST", f"/api/meetings/occurrences/{occ}/attendance",
            {"present": [po, orch, iva]}, note="who was in the room")
    ev.call("GET", f"/api/meetings/occurrences/{occ}/minutes", note="minutes before the close")
    st, closed = ev.call("POST", f"/api/meetings/occurrences/{occ}/close", {
        "notes": "Gate B was not convened: SECURITY_PLAN v1.0 and DATA_FLOWS v1.0 were not accepted "
                 "by their boards and no capacity number was presented. Nothing was promoted. "
                 "The portfolio health colour on this programme is not quotable outside this room."},
        note="the close round 1 never performed")
    summary["steps"]["close"] = {"status": st, "next": closed if st == 200 else None}
    ev.call("GET", f"/api/meetings/occurrences/{occ}/minutes", note="minutes after the close")
    ev.call("POST", f"/api/meetings/occurrences/{occ}/decisions",
            {"headline": "Probe: can a decision be added after the record is frozen?",
             "decidedBy": po}, note="frozen-record probe")

    # ------------------------------------------------- 9. what the tool did alone
    ev.mark("9. what Meridian did on its own")
    for path, note in [("/api/health", "instance identity, backup drill state"),
                       ("/api/admin/posture", "day-one security posture"),
                       ("/api/decisions/log", "the decision register as a register"),
                       (f"/api/projects/{gov}/evidence", "gate evidence view"),
                       (f"/api/projects/{gov}/lessons/relevant", "lessons offered at a gate"),
                       ("/api/adoption", "adoption telemetry"),
                       ("/api/digest", "the digest it composes itself"),
                       ("/api/collections", "what it thinks it holds"),
                       ("/api/demand", "unfunded demand"),
                       ("/api/periods", "reporting periods")]:
        ev.call("GET", path, note=note)
    ev.call("POST", "/api/admin/notifications/sweep", {}, note="the sweep it runs on a schedule")
    st, boot = ev.call("GET", "/api/bootstrap", note="final read-back")
    if isinstance(boot, dict) and "db" in boot:
        d = boot["db"]
        summary["final"] = {k: len(v) for k, v in d.items() if isinstance(v, list)}

    Path(args.out).write_text("", encoding="utf-8")
    ev.dump(Path(args.out), summary)
    print("\n" + json.dumps(summary, indent=1, ensure_ascii=False)[:4000])
    bad = [r for r in ev.records if r["status"] >= 400 or r["status"] < 0]
    print(f"\nrequests={len(ev.records)}  non-2xx/3xx={len(bad)}")
    for r in bad:
        print(f"  {r['status']:4d} {r['method']} {r['path']}  :: {str(r['response'])[:150]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
