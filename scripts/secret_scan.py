#!/usr/bin/env python3
"""Lightweight secret scan for CI (T-05). Real deployments add a dedicated scanner; this one blocks obvious leaks."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATTERNS = [
    re.compile(r"(?i)(aws_secret_access_key|aws_access_key_id)\s*[=:]\s*['\"]?[A-Za-z0-9/+=]{16,}"),
    re.compile(r"-----BEGIN (RSA|EC|OPENSSH|PGP) PRIVATE KEY-----"),
    re.compile(r"(?i)(api[_-]?key|secret|password|token)\s*[=:]\s*['\"][A-Za-z0-9_\-]{20,}['\"]"),
    re.compile(r"sk-[A-Za-z0-9]{32,}"),
    re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}"),
]
allow = [
    line.strip()
    for line in (ROOT / "security" / "secret_scan_allowlist.txt").read_text().splitlines()
    if line.strip() and not line.startswith("#")
]
files = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.split()
findings = []
for rel in files:
    p = ROOT / rel
    if not p.is_file() or p.suffix in {".png", ".jpg", ".zip", ".pdf"}:
        continue
    try:
        text = p.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        continue
    for i, line in enumerate(text.splitlines(), 1):
        for pat in PATTERNS:
            if pat.search(line) and not any(a.split(":", 1)[0] == rel and a.split(":", 1)[1] in line for a in allow if ":" in a):
                findings.append(f"{rel}:{i}: {line.strip()[:80]}")
if findings:
    print("FAIL secret scan:\n - " + "\n - ".join(findings))
    sys.exit(1)
print(f"OK secret scan: {len(files)} files, no findings")
