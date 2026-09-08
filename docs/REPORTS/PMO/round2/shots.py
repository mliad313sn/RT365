#!/usr/bin/env python3
"""Round-2 screenshots: the six screens a Product Owner would actually open."""
import os
import re
import sys
import time

from playwright.sync_api import sync_playwright

URL = os.environ.get("MERIDIAN_URL", "http://localhost:4183")
PW = os.environ["MERIDIAN_PASSWORD"]
OUT = "/home/user/RT365/docs/REPORTS/PMO/round2"
SHOTS = [
    ("#/risk", "03_raid_register.png", "the RAID register"),
    ("#/reports", "05_reports_value.png", "status reporting and the value position"),
]


def main() -> int:
    with sync_playwright() as p:
        b = p.chromium.launch(
            executable_path="/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
            args=["--no-sandbox"])
        ctx = b.new_context(viewport={"width": 1500, "height": 1150})
        r = ctx.request.post(URL + "/api/auth/login",
                             data={"email": "admin@meridian.example", "password": PW})
        print("login", r.status, flush=True)
        pg = ctx.new_page()
        pg.on("pageerror", lambda e: print("  pageerror:", str(e)[:120]))
        for route, name, why in SHOTS:
            pg.goto(f"{URL}/{route}")
            pg.reload()
            try:
                pg.wait_for_load_state("networkidle", timeout=15000)
            except Exception:
                pass
            time.sleep(2.5)
            # dismiss any first-run coach mark
            for label in ("Don't show this again", "Ne plus afficher"):
                try:
                    el = pg.get_by_text(label, exact=False).first
                    if el.is_visible(timeout=700):
                        el.click(timeout=1500)
                        time.sleep(0.4)
                except Exception:
                    pass
            try:
                pg.keyboard.press("Escape")
            except Exception:
                pass
            time.sleep(0.6)
            pg.screenshot(path=f"{OUT}/{name}", full_page=True)
            txt = re.sub(r"\s+", " ", pg.inner_text("body"))[:1400]
            print(f"\n### {name} · {route} · {why}\n{txt}\n", flush=True)
        b.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
