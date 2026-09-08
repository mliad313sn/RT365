#!/usr/bin/env python3
"""Round-2 probes, second pass: the ones the first pass could not reach."""
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

    # Q1 · what the independent-reviewer control actually recorded
    crit = [c for c in db["criteria"] if c["project"] == gov]
    res["answers"]["Q1_criteria_on_gov"] = {
        "total": len(crit),
        "by_gate": {g: sum(1 for c in crit if c["gate"] == g) for g in range(1, 7)},
        "met": sum(1 for c in crit if c["met"]),
        "met_rows": [{"id": c["id"], "gate": c["gate"], "text": c["text"][:70],
                      "reviewedBy": c["reviewedBy"], "reviewedOn": c["reviewedOn"]}
                     for c in crit if c["met"]],
    }
    # abuse: find a criterion met with no reviewer, and with a reviewer who is not real
    unmet = [c for c in crit if not c["met"] and c["gate"] == 2]
    if unmet:
        c = unmet[0]
        ev.call("PATCH", f"/api/criteria/{c['id']}", {"met": True, "version": c["version"]},
                note="ABUSE: found met with no named reviewer")
        ev.call("PATCH", f"/api/criteria/{c['id']}",
                {"met": True, "reviewedBy": "PER-NOBODY", "version": c["version"]},
                note="ABUSE: reviewer who is not in the directory")
        st, _ = ev.call("PATCH", f"/api/criteria/{c['id']}",
                        {"met": True, "reviewedBy": iva, "version": c["version"],
                         "note": "Gate B criterion — not actually met; probe only, reopened below."},
                        note="named reviewer, Gate B")
        if st == 200:
            ev.call("PATCH", f"/api/criteria/{c['id']}", {"met": False, "version": c["version"] + 1},
                    note="reopened — a criterion found met can be un-found")

    # Q2 · the v1 write API with a fresh integration key
    ev.mark("Q2 · v1 write API")
    st, key = ev.call("POST", "/api/admin/integrations",
                      {"name": f"RT365 loader probe {datetime.now(tz=UTC).strftime('%H%M%S')}",
                       "purpose": "Measure what an integration can and cannot write",
                       "scopes": "read:portfolio,write:portfolio,write:meetings,read:audit"})
    tok = None
    if isinstance(key, dict):
        for k in ("key", "secret", "token", "apiKey", "value"):
            if key.get(k):
                tok = key[k]
                break
    res["answers"]["Q2_key_response_fields"] = sorted(key.keys()) if isinstance(key, dict) else key
    if tok:
        h = {"Authorization": f"Bearer {tok}"}
        st, port = ev.call("GET", "/api/v1/portfolio", None, headers=h, note="the integration reads")
        res["answers"]["Q2_v1_portfolio_keys"] = sorted(port.keys()) if isinstance(port, dict) else None
        if isinstance(port, dict) and isinstance(port.get("counts"), dict):
            res["answers"]["Q2_v1_counts"] = port["counts"]
        writable, refused = [], []
        for coll in ("projects", "milestones", "raid", "activities", "workitems", "criteria",
                     "decisions", "actions", "business-case", "benefits", "sites", "programmes",
                     "people", "stakeholders", "comms", "lessons", "tolerances", "waves",
                     "changes", "documents", "exceptions"):
            st, body = ev.call("PUT", f"/api/v1/{coll}/RT365-PROBE-X",
                               {"title": "probe", "project": gov}, headers=h,
                               note=f"is {coll} writable through v1?")
            (refused if st == 404 else writable).append(f"{coll}:{st}")
        res["answers"]["Q2_v1_write_routes"] = {"reached": writable, "404": refused}
        # idempotency, and whose name lands in the trail
        body = {"project": gov, "type": "Risk",
                "title": "[RT365 probe] written by an integration key",
                "detail": "Whose name lands in the audit trail for this row?",
                "p": 2, "i": 2, "response": "Monitor"}
        ev.call("PUT", "/api/v1/raid/RT365-PROBE-1", body,
                headers={**h, "Idempotency-Key": "rt365-r2-a"}, note="1st write")
        ev.call("PUT", "/api/v1/raid/RT365-PROBE-1", body,
                headers={**h, "Idempotency-Key": "rt365-r2-a"}, note="2nd, same key, same body")
        ev.call("PUT", "/api/v1/raid/RT365-PROBE-1", {**body, "p": 5, "i": 5},
                headers=h, note="3rd, same external id, changed body, no key")
        st, aud = ev.call("GET", "/api/v1/audit?limit=6", None, headers=h,
                          note="whose name is on the write?")
        if isinstance(aud, dict):
            ent = aud.get("events") or aud.get("audit") or []
            res["answers"]["Q2_audit_actors"] = [
                {"action": e.get("action"), "actor": e.get("actor") or e.get("actorName"),
                 "entity": e.get("entity")} for e in ent[:6]]

    # Q3 · what froze when the meeting closed
    ev.mark("Q3 · the frozen record")
    st, occ = ev.call("GET", "/api/meetings/occurrences/MS-SUWK22-20260908")
    if isinstance(occ, dict):
        o = occ.get("occurrence", {})
        ag = occ.get("agenda") or {}
        res["answers"]["Q3_closed_occurrence"] = {
            "status": o.get("status"), "closedAt": o.get("closedAt"), "closedBy": o.get("closedBy"),
            "notes": (o.get("notes") or "")[:200],
            "frozen": ag.get("frozen"), "agenda_keys": sorted(ag.keys()),
            "sections": [{"title": s.get("title"), "items": len(s.get("items", []))}
                         for s in ag.get("sections", [])],
            "decisions": len(occ.get("decisions", [])),
            "actionsRaisedHere": len(occ.get("actionsRaisedHere", [])),
            "attendance": occ.get("attendance"),
        }
    st, mins = ev.call("GET", "/api/meetings/occurrences/MS-SUWK22-20260908/minutes")
    if isinstance(mins, dict):
        md = mins.get("markdown") or mins.get("minutes") or ""
        res["answers"]["Q3_minutes_chars"] = len(md)
        res["answers"]["Q3_minutes_head"] = md[:900]
    st, nxt = ev.call("GET", "/api/meetings/occurrences/MS-SUWK22-20260914")
    if isinstance(nxt, dict):
        res["answers"]["Q3_next_occurrence"] = {
            "status": nxt.get("occurrence", {}).get("status"),
            "agenda_sections": [{"title": s.get("title"), "items": len(s.get("items", []))}
                                for s in (nxt.get("agenda") or {}).get("sections", [])]}

    # Q4 · segregation of duties on the change request, and the break-glass
    ev.mark("Q4 · SoD and break-glass")
    crs = db.get("crs", [])
    res["answers"]["Q4_crs"] = [{"id": c.get("id"), "status": c.get("status"),
                                 "raisedBy": c.get("raisedBy"), "steps": c.get("steps")}
                                for c in crs]
    if crs:
        cid = crs[0]["id"]
        for i in range(4):
            st, r = ev.call("POST", f"/api/change/{cid}/approve",
                            {"note": f"Break-glass probe, step {i}: the raiser signs."},
                            note=f"ABUSE: raiser approves own CR, step {i}")
            if st >= 400:
                break
        st, b2 = ev.call("GET", "/api/bootstrap")
        c2 = next((c for c in b2["db"]["crs"] if c["id"] == cid), None)
        res["answers"]["Q4_cr_after"] = c2
    st, post = ev.call("GET", "/api/admin/posture")
    res["answers"]["Q4_posture"] = post

    # Q5 · health, and whether an unmeasured project can say so
    ev.mark("Q5 · health on a budget-less, unmeasured project")
    p = next(x for x in db["projects"] if x["id"] == gov)
    res["answers"]["Q5_gov_project_before"] = {k: p.get(k) for k in
                                               ("health", "healthNote", "pct", "spi", "cpi",
                                                "budget", "phase", "status", "version")}
    ev.call("PATCH", f"/api/projects/{gov}/health",
            {"health": "R", "note": "Gate B was not convened: two exit documents were refused.",
             "version": p.get("version", 1)}, note="state the truth by hand")
    for other in [x for x in db["projects"] if x["id"] != gov][:3]:
        res["answers"].setdefault("Q5_other_projects", []).append(
            {"name": other["name"], "health": other.get("health"), "pct": other.get("pct"),
             "spi": other.get("spi"), "cpi": other.get("cpi"), "budget": other.get("budget"),
             "healthNote": other.get("healthNote")})
    # is there any health value meaning "not measured"?
    ev.call("PATCH", f"/api/projects/{gov}/health",
            {"health": "U", "note": "probe: is there an unmeasured state?",
             "version": p.get("version", 1) + 1}, note="probe: health = U (unmeasured)")

    # Q6 · exceptions: does anything raise one by itself?
    ev.mark("Q6 · exceptions")
    st, b3 = ev.call("GET", "/api/bootstrap")
    res["answers"]["Q6_exceptions"] = b3["db"]["exceptions"]
    res["answers"]["Q6_tolerances"] = b3["db"]["tolerances"]
    res["answers"]["Q6_final_counts"] = {k: len(v) for k, v in b3["db"].items() if isinstance(v, list)}

    ev.dump(OUT, res)
    print(json.dumps(res, indent=1, ensure_ascii=False)[:6000])
    bad = [r for r in ev.records if r["status"] >= 400 or r["status"] < 0]
    print(f"\nrequests={len(ev.records)}  non-2xx/3xx={len(bad)}")
    for r in bad:
        print(f"  {r['status']:4d} {r['method']} {r['path']}\n        note: {r['note']}\n        {str(r['response'])[:160]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
