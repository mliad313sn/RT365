#!/usr/bin/env python3
"""Round-2 follow-up probes: the things the first drive could not settle.

Each probe states what it asks, and the answer is the recorded status and body.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import UTC, date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from drive import Ev  # noqa: E402

URL = os.environ["MERIDIAN_URL"]
OUT = Path(sys.argv[1])


def main() -> int:
    ev = Ev(URL)
    today = date.today().isoformat()
    res: dict = {"at": datetime.now(tz=UTC).isoformat(), "answers": {}}
    ev.call("POST", "/api/auth/login",
            {"email": os.environ["MERIDIAN_EMAIL"], "password": os.environ["MERIDIAN_PASSWORD"]})
    st, boot = ev.call("GET", "/api/bootstrap")
    db = boot["db"]
    people = {p["name"]: p["id"] for p in db["people"]}
    gov = next(p["id"] for p in db["projects"] if p["name"].startswith("RBT-GOV"))
    po, iva = people["Product Owner"], people["Independent Validation Agent"]
    crit = [c for c in db["criteria"] if c["project"] == gov]

    # ---- P1 · REQ-04: does the independent-reviewer control actually hold? ----
    ev.mark("P1 · gate criteria found met by a named independent reviewer (REQ-04)")
    g1 = [c for c in crit if c["gate"] == 1 and not c["met"]]
    metc = 0
    for c in g1[:6]:
        st, _ = ev.call("PATCH", f"/api/criteria/{c['id']}",
                        {"met": True, "reviewedBy": iva, "version": c["version"],
                         "note": "Gate A passed with the conditions of D-048; found met by "
                                 "Independent Validation, who owns none of the evidence cited."},
                        note=f"gate 1 · {c['text'][:60]}")
        metc += st == 200
    res["answers"]["P1_gate_A_criteria_met"] = metc
    # abuse case: found met with no named reviewer at all
    if len(g1) > 6:
        c = g1[6]
        ev.call("PATCH", f"/api/criteria/{c['id']}", {"met": True, "version": c["version"]},
                note="ABUSE: found met with no named reviewer")
        ev.call("PATCH", f"/api/criteria/{c['id']}",
                {"met": True, "reviewedBy": "PER-DOES-NOT-EXIST", "version": c["version"]},
                note="ABUSE: found met by a person who is not in the directory")
    # can a criterion be posed beyond the six-gate ladder?
    ev.call("POST", "/api/criteria", {"project": gov, "gate": 7, "text": "Beyond the ladder"},
            note="boundary: gate 7 on a six-gate ladder")
    ev.call("POST", "/api/criteria", {"project": gov, "gate": 6, "text":
            "Release dossier reviewed by Independent Validation before any market release"},
            note="boundary: gate 6 IS reachable for a criterion")

    # ---- P2 · the lesson gate ceiling ----
    ev.mark("P2 · a lesson on a six-gate ladder")
    for g in (4, 5, 6):
        ev.call("POST", "/api/lessons",
                {"project": gov, "gate": g, "category": "Governance",
                 "title": f"Probe: can a lesson be tagged to gate {g}?",
                 "whatHappened": "Probe", "why": "Probe", "recommendation": "Probe"},
                note=f"lesson at gate {g} of six")

    # ---- P3 · V-1/REQ-20 and E-2: what an integration key can and cannot write ----
    ev.mark("P3 · the v1 write API with a real integration key")
    st, key = ev.call("POST", "/api/admin/integrations",
                      {"name": "RT365 field loader round 2",
                       "purpose": "Load the RoboTrader programme from the repository ledgers",
                       "scopes": "read:portfolio,write:portfolio,write:meetings,read:audit"})
    tok = None
    if isinstance(key, dict):
        tok = key.get("key") or key.get("secret") or key.get("token") or key.get("apiKey")
    res["answers"]["P3_key_fields"] = sorted(key.keys()) if isinstance(key, dict) else None
    if tok:
        h = {"Authorization": f"Bearer {tok}"}
        ev.call("GET", "/api/v1/portfolio", None, headers=h, note="the integration reads")
        for coll in ("business-case", "businesscase", "benefits", "benefit", "cases",
                     "sites", "programmes", "people", "stakeholders", "comms", "lessons",
                     "tolerances", "waves", "change", "documents"):
            ev.call("PUT", f"/api/v1/{coll}/RT365-PROBE", {"title": "probe", "project": gov},
                    headers=h, note=f"is {coll} writable through v1?")
        ev.call("PUT", "/api/v1/raid/RT365-PROBE-1", {
            "project": gov, "type": "Risk", "title": "[RT365 probe] written by the integration key",
            "detail": "Whose name lands in the audit trail for this row?",
            "p": 2, "i": 2, "response": "Monitor"},
            headers={**h, "Idempotency-Key": "rt365-r2-1"}, note="v1 write that IS supported (1st)")
        ev.call("PUT", "/api/v1/raid/RT365-PROBE-1", {
            "project": gov, "type": "Risk", "title": "[RT365 probe] written by the integration key",
            "detail": "Whose name lands in the audit trail for this row?",
            "p": 2, "i": 2, "response": "Monitor"},
            headers={**h, "Idempotency-Key": "rt365-r2-1"}, note="same body, same Idempotency-Key (2nd)")
        ev.call("PUT", "/api/v1/raid/RT365-PROBE-1", {
            "project": gov, "type": "Risk", "title": "[RT365 probe] written by the integration key",
            "detail": "Changed body, same external id, no idempotency key.",
            "p": 4, "i": 4, "response": "Mitigate"}, headers=h, note="changed body, same external id")
        # does the trail name the integration or the human?
        ev.call("GET", "/api/v1/audit?limit=5", None, headers=h, note="whose name is on the write?")
        # and a decision through v1
        ev.call("PUT", "/api/v1/decisions/RT365-D-PROBE", {
            "projectId": gov, "headline": "Probe: a decision record written by an integration",
            "decidedBy": po, "decidedOn": today, "alternatives": "none", "dissent": "none"},
            headers={**h, "Idempotency-Key": "rt365-r2-d1"}, note="v1 decision write")

    # ---- P4 · business case reconfirmation at a gate (V-3/REQ-22) ----
    ev.mark("P4 · does a gate enforce business-case reconfirmation?")
    st, cases = ev.call("GET", "/api/bootstrap", note="read the case version")
    bc = next((c for c in cases["db"]["businessCases"] if c.get("project") == gov), None)
    if bc:
        ev.call("POST", f"/api/projects/{gov}/case/reconfirm",
                {"gate": 1, "version": bc.get("version", 1),
                 "note": "Reconfirmed at Gate A with the conditions of D-048."})
        ev.call("POST", f"/api/projects/{gov}/case/reconfirm",
                {"gate": 6, "version": bc.get("version", 1) + 1,
                 "note": "Probe: reconfirm at a gate not yet reached."},
                note="can a case be reconfirmed at a future gate?")
    # a project with no case at all: does anything refuse its gate?
    e01 = next((p["id"] for p in db["projects"] if p["name"].startswith("E01")), None)
    ms = [m for m in db["milestones"] if m.get("project") == e01 and m["name"].startswith("Gate A")]
    if ms:
        ev.call("PATCH", f"/api/milestones/{ms[0]['id']}",
                {"done": True, "acceptedBy": po, "version": ms[0]["version"]},
                note="ABUSE: pass a gate on a project with no business case and no criteria met")

    # ---- P5 · tolerance breach: does an exception raise itself? ----
    ev.mark("P5 · does a tolerance breach raise an exception on its own?")
    st, _ = ev.call("PUT", f"/api/projects/{gov}/tolerance",
                    {"scheduleDays": 1, "costPct": 1, "benefitPct": 1,
                     "note": "Tightened to one day so a known slip breaches it."})
    gb = next((m for m in db["milestones"] if m.get("project") == gov and m["name"] == "Gate B"), None)
    if gb:
        ev.call("PATCH", f"/api/milestones/{gb['id']}",
                {"date": "2026-11-27", "version": gb["version"]},
                note="slip Gate B by four weeks against a one-day tolerance")
    ev.call("PATCH", f"/api/projects/{gov}/health", {"health": "R", "note": "Gate B not convened"},
            note="state the health by hand")
    st, b2 = ev.call("GET", "/api/bootstrap", note="did an exception appear?")
    res["answers"]["P5_exceptions"] = b2["db"]["exceptions"] if isinstance(b2, dict) else None

    # ---- P6 · rollout waves: the sequence the schema forbids ----
    ev.mark("P6 · a sequenced rollout to one site")
    ev.call("POST", "/api/waves", {"project": gov, "site": "RTX", "seq": 2,
                                   "plannedOn": "2027-04-30", "note": "Capped autonomous pilot"},
            note="second wave, same site — UNIQUE (project_id, site_id)")

    # ---- P7 · the frozen record ----
    ev.mark("P7 · what the close froze, and what the next occurrence carries")
    st, occ = ev.call("GET", "/api/meetings/occurrences/MS-SUWK22-20260908")
    if isinstance(occ, dict):
        o = occ.get("occurrence", occ)
        res["answers"]["P7_closed"] = {
            "status": o.get("status"), "closedAt": o.get("closedAt"), "closedBy": o.get("closedBy"),
            "frozen_agenda_items": len(occ.get("agendaItems") or occ.get("agenda", {}).get("items") or []),
            "keys": sorted(occ.keys()),
        }
    ev.call("GET", "/api/meetings/occurrences/MS-SUWK22-20260908/pack", note="the pack of a closed meeting")
    ev.call("POST", "/api/meetings/occurrences/MS-SUWK22-20260908/actions",
            {"title": "Probe: an action raised into a closed meeting", "ownerId": po},
            note="ABUSE: write into a frozen record")
    ev.call("GET", "/api/meetings/occurrences/MS-SUWK22-20260914", note="the next occurrence it scheduled")

    # ---- P8 · segregation of duties on the change request ----
    ev.mark("P8 · SoD on the change request")
    cr = next((c["id"] for c in db.get("crs", [])), None) or "CR-224"
    ev.call("POST", f"/api/change/{cr}/approve", {"note": "Raiser signs their own change."},
            note="ABUSE: the raiser approves their own CR")
    ev.call("GET", "/api/bootstrap", note="CR state after the attempt")

    # ---- P9 · the executive numbers, on an empty book with only our programme ----
    ev.mark("P9 · the executive tiles, and whether they rescope to a programme")
    for p in ("/api/bootstrap", "/api/digest", "/api/adoption",
              "/api/export/dataset?programme=RBT", "/api/decisions/log"):
        ev.call("GET", p, note="what a sponsor's page is built from")

    ev.dump(OUT, res)
    print(json.dumps(res, indent=1, ensure_ascii=False)[:3000])
    bad = [r for r in ev.records if r["status"] >= 400 or r["status"] < 0]
    print(f"\nrequests={len(ev.records)}  non-2xx/3xx={len(bad)}")
    for r in bad:
        print(f"  {r['status']:4d} {r['method']} {r['path']}\n        note: {r['note']}\n        {str(r['response'])[:170]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
