#!/usr/bin/env python3
"""Static invariants over infra/kubernetes/network-policies (TC-NET). Exit 1 on violation.

Invariants [Source: 00, 03, 04; ADR-001]:
 1. analytics namespace has a default-deny policy for Ingress and Egress.
 2. No analytics egress rule targets plane=execution, plane=security (vault) or any ipBlock.
 3. Only the execution namespace has an ipBlock egress (broker route).
 4. Vault ingress admits only control and execution planes.
 5. MCP server egress targets only analytics pods and the control intent-queue.
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
POL = ROOT / "infra" / "kubernetes" / "network-policies"


def load_all() -> list[dict]:
    docs = []
    for f in sorted(POL.glob("*.yaml")):
        docs.extend(d for d in yaml.safe_load_all(f.read_text()) if d)
    return docs


def peers(rule: dict, key: str) -> list[dict]:
    return rule.get(key, []) or []


def check() -> list[str]:
    problems: list[str] = []
    docs = load_all()
    by_ns: dict[str, list[dict]] = {}
    for d in docs:
        by_ns.setdefault(d["metadata"]["namespace"], []).append(d)
    for ns in ("analytics", "control", "execution"):
        dd = [
            d
            for d in by_ns.get(ns, [])
            if d["spec"].get("podSelector") == {}
            and set(d["spec"].get("policyTypes", [])) == {"Ingress", "Egress"}
            and "ingress" not in d["spec"]
            and "egress" not in d["spec"]
        ]
        if not dd:
            problems.append(f"{ns}: missing default-deny policy")
    for d in by_ns.get("analytics", []):
        for rule in d["spec"].get("egress", []) or []:
            for peer in peers(rule, "to"):
                if "ipBlock" in peer:
                    problems.append(f"analytics/{d['metadata']['name']}: ipBlock egress (broker/web route) forbidden")
                plane = (peer.get("namespaceSelector") or {}).get("matchLabels", {}).get("plane")
                if plane in ("execution", "security"):
                    problems.append(f"analytics/{d['metadata']['name']}: egress to plane={plane} forbidden")
                if plane == "control":
                    app = (peer.get("podSelector") or {}).get("matchLabels", {}).get("app")
                    if app != "intent-queue":
                        problems.append(f"analytics/{d['metadata']['name']}: control egress must target intent-queue only (got {app})")
    for ns, dd in by_ns.items():
        if ns == "execution":
            continue
        for d in dd:
            for rule in d["spec"].get("egress", []) or []:
                if any("ipBlock" in p for p in peers(rule, "to")):
                    problems.append(f"{ns}/{d['metadata']['name']}: only execution may hold an ipBlock (broker) egress")
    exec_has_broker = any(
        "ipBlock" in p for d in by_ns.get("execution", []) for rule in d["spec"].get("egress", []) or [] for p in peers(rule, "to")
    )
    if not exec_has_broker:
        problems.append("execution: no broker egress route defined")
    for d in by_ns.get("security", []):
        for rule in d["spec"].get("ingress", []) or []:
            for peer in peers(rule, "from"):
                plane = (peer.get("namespaceSelector") or {}).get("matchLabels", {}).get("plane")
                if plane not in ("control", "execution"):
                    problems.append(f"security/{d['metadata']['name']}: vault ingress from plane={plane} forbidden")
    for d in by_ns.get("analytics", []):
        if (d["spec"].get("podSelector") or {}).get("matchLabels", {}).get("component") == "mcp-server":
            for rule in d["spec"].get("egress", []) or []:
                for peer in peers(rule, "to"):
                    ns_lbl = (peer.get("namespaceSelector") or {}).get("matchLabels", {})
                    plane = ns_lbl.get("plane")
                    if plane == "control" and (peer.get("podSelector") or {}).get("matchLabels", {}).get("app") != "intent-queue":
                        problems.append("mcp-servers: control egress must be intent-queue only")
                    if plane in ("execution", "security", "edge"):
                        problems.append(f"mcp-servers: egress to plane={plane} forbidden")
    return problems


if __name__ == "__main__":
    probs = check()
    if probs:
        print("FAIL:\n - " + "\n - ".join(probs))
        sys.exit(1)
    print("OK: network policies satisfy plane invariants (TC-NET)")
