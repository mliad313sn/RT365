"""``rt365`` sub-commands. Every command resolves the resource root and the environment label first (fail closed)."""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections.abc import Sequence
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Any

import yaml
from rtcore.clock import utc_now
from rtcore.errors import PlaneViolation
from rtcore.planes import Plane, PlaneGuard
from rtcore.resources import ResourceRootMissing, resource_root

from rt365_cli import __version__

# Directories/files (repository-relative) that an installed or frozen build must carry under its resource root.
BUNDLED_RELATIVE_PATHS: tuple[str, ...] = (
    "mcp/policies",
    "observability/alerts.yaml",
    "observability/slis.yaml",
    "services/risk/policies",
    "apps/web/static",
)
SERVABLE_ENVIRONMENTS = frozenset({"sim"})
ALLOWED_TOOLS = frozenset(
    {"read_market_snapshot", "read_account_state", "calculate_indicator", "run_simulation", "get_strategy_docs", "submit_trade_intent"}
)


class CliError(Exception):
    def __init__(self, message: str, code: int = 1) -> None:
        super().__init__(message)
        self.code = code


def _label(args: argparse.Namespace) -> str:
    env = args.env or os.environ.get("RT_ENV")
    if not env:
        raise CliError(
            "RT_ENV is not set: pass --env sim or export RT_ENV=sim. An unlabelled environment fails closed (IVA-06, RAID R-40).", 2
        )
    os.environ["RT_ENV"] = env
    return env


def _servable(env: str) -> None:
    if env not in SERVABLE_ENVIRONMENTS:
        raise CliError(
            f"environment {env!r} cannot be served by the dev/sim build: only sim is servable (dev header auth, ADR-012; RAID R-06)", 2
        )


def _root() -> Any:
    try:
        return resource_root()
    except ResourceRootMissing as exc:
        raise CliError(f"resource root: FAIL — {exc}", 1) from exc


# --- commands ---------------------------------------------------------------------------------------------------------
def cmd_version(args: argparse.Namespace) -> int:
    print(f"rt365 {__version__} (dev/sim build of the Global AI-MCP RoboTrader control envelope; nothing here is authorised beyond sim)")
    try:
        print(f"resource root: {resource_root()}")
    except ResourceRootMissing as exc:
        print(f"resource root: none ({exc})")
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    env = _label(args)
    root = _root()
    print(f"resource root: {root}")
    print(f"environment label: {env}")
    from mcp_servers.registry import RegistryUnsigned, load_registry

    try:
        reg = load_registry(root / "mcp" / "policies" / "tool_registry.signed.json")
    except RegistryUnsigned as exc:
        raise CliError(f"registry: FAIL — refused: {exc}", 1) from exc
    print(
        f"registry: OK — version {reg.registry_version}, {len(reg.tools)} tools, "
        f"{'dev key' if reg.dev_key_in_use else 'configured key'}, {'sim FIXTURE (approvals pending; refused outside dev/sim)' if reg.fixture else 'approved'}"
    )
    problems: list[str] = []
    if set(reg.tools) - ALLOWED_TOOLS:
        problems.append(f"tools outside the six allowed capabilities: {sorted(set(reg.tools) - ALLOWED_TOOLS)}")
    if [t.name for t in reg.tools.values() if t.tool_class == "write"] != ["submit_trade_intent"]:
        problems.append("only submit_trade_intent may be write-class")
    egress = yaml.safe_load((root / "mcp" / "policies" / "egress.yaml").read_text())
    for host in egress.get("allowed_hosts", []):
        if any(bad in host for bad in ("vault", "execution", "broker")) or host.strip() in ("*", "0.0.0.0/0"):
            problems.append(f"egress allowlist contains forbidden host: {host}")
    runtime = yaml.safe_load((root / "mcp" / "policies" / "runtime.yaml").read_text())
    for key, expected in (("filesystem", "read-only"), ("shell", "absent"), ("secrets_mount", "none")):
        if str(runtime.get(key, "")).split()[0] != expected:
            problems.append(f"runtime.yaml {key} must be {expected}")
    if not runtime.get("registry_signature_required"):
        problems.append("runtime.yaml must require registry signature")
    if problems:
        raise CliError("policies: FAIL\n - " + "\n - ".join(problems), 1)
    print("policies: OK — egress and runtime invariants hold")
    guard = PlaneGuard()
    for destination, channel in ((Plane.EXECUTION, "order_command"), (Plane.VAULT, "broker_credentials"), (Plane.BROKER, "broker_adapter")):
        try:
            guard.check(Plane.ANALYTICS, destination, channel)
            problems.append(f"analytics -> {destination.value}:{channel} crossing was not denied")
        except PlaneViolation:
            pass
    if len(guard.denies) != 3:
        problems.append("plane guard did not record every denied crossing")
    if problems:
        raise CliError("planes: FAIL\n - " + "\n - ".join(problems), 1)
    print("planes: OK — analytics cannot reach execution or the vault in-process")
    if env in ("dev", "sim"):
        from web_bff.platform import build_sim_platform

        p = build_sim_platform()
        v = p.audit.verify()
        if not v.ok:
            raise CliError(f"audit chain: FAIL — {v}", 1)
        print(f"audit chain: OK — {len(p.audit)} events, hash chain intact after composition")
    else:
        print("audit chain: skipped — the sim composition root is not built outside dev/sim")
    print("check: OK (dev/sim evidence only; no gate is passed by this command)")
    return 0


def cmd_probe(args: argparse.Namespace) -> int:
    env = _label(args)
    _servable(env)
    _root()
    from web_bff.platform import build_sim_platform

    p = build_sim_platform()
    result = p.synthetic_probe()
    for k, v in result.items():
        print(f"{k}: {json.dumps(v) if isinstance(v, list | dict) else v}")
    return 0 if not result["missing_spans"] else 1


def cmd_serve(args: argparse.Namespace) -> int:
    env = _label(args)
    _servable(env)
    _root()
    import uvicorn

    print(f"rt365 serve: sim dashboard/BFF on http://{args.host}:{args.port} (dev header auth; RAID R-06)", file=sys.stderr)
    uvicorn.run("web_bff.app:create_app", factory=True, host=args.host, port=args.port, log_level="info")
    return 0


def cmd_mcp_serve(args: argparse.Namespace) -> int:
    env = _label(args)
    _servable(env)
    _root()
    from mcp_servers.stdio import build_stdio_server
    from web_bff.platform import build_sim_platform

    p = build_sim_platform()
    started = utc_now()
    ident = p.issue_agent(agent_id=args.agent_id, ttl=timedelta(hours=args.session_hours))

    def now() -> datetime:
        return p.now + (utc_now() - started)  # sim clock advances with wall time from the fixture base

    def call(tool: str, arguments: dict[str, Any]) -> Any:
        return p.tool_call(ident, tool, arguments, now=now())

    server = build_stdio_server(p.registry, call)
    print(
        f"rt365 mcp-serve: MCP stdio server for agent {args.agent_id} (tenant-sim, {ident.strategy_id}@{ident.strategy_version}); "
        f"{len(p.registry.tools)} tools; identity expires {ident.expires_at.isoformat()}",
        file=sys.stderr,
    )
    server.serve(sys.stdin, sys.stdout)
    return 0


def cmd_certify_broker(args: argparse.Namespace) -> int:
    _label(args)
    from broker_adapters.certification import certification_markdown, run_certification
    from broker_adapters.simulated import SimulatedBroker

    now = datetime(2026, 9, 7, 14, 0, tzinfo=UTC)
    broker = SimulatedBroker(known_instruments={"SIMEQ1": "EQUITY"}, venues=("SIMX",))
    broker.set_reference_price("SIMEQ1", Decimal("100"), now=now)
    rows = run_certification(broker, account_id="acct-sim-001", instrument_id="SIMEQ1", venue="SIMX", now=now, price=Decimal("100"))
    md = certification_markdown("sim-broker", rows, run_at=now, run_by="rt365 certify-broker (harness)")
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(md)
        print(f"wrote {args.out}: {sum(r.passed for r in rows)}/{len(rows)} rows passed (reviewer signature pending)")
    else:
        print(md)
    return 0


# --- parser -------------------------------------------------------------------------------------------------------------
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="rt365", description="Global AI-MCP RoboTrader — dev/sim control envelope")
    sub = parser.add_subparsers(dest="command", required=True)

    def env_opt(p: argparse.ArgumentParser) -> None:
        p.add_argument("--env", help="environment label (RT_ENV); required unless RT_ENV is exported. Only 'sim' is servable.")

    sub.add_parser("version", help="print the version and the resolved resource root").set_defaults(fn=cmd_version)
    p = sub.add_parser("check", help="verify signed registry, policy invariants, plane guard and audit chain")
    env_opt(p)
    p.set_defaults(fn=cmd_check)
    p = sub.add_parser("probe", help="run the synthetic intent probe end to end (sim)")
    env_opt(p)
    p.set_defaults(fn=cmd_probe)
    p = sub.add_parser("serve", help="serve the sim dashboard/BFF")
    env_opt(p)
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=8080)
    p.set_defaults(fn=cmd_serve)
    p = sub.add_parser("mcp-serve", help="serve the six MCP tools over stdio for an agent host (sim)")
    env_opt(p)
    p.add_argument("--agent-id", default="agent-claude-code")
    p.add_argument("--session-hours", type=int, default=8)
    p.set_defaults(fn=cmd_mcp_serve)
    p = sub.add_parser("certify-broker", help="run the sandbox certification harness against the simulated broker")
    env_opt(p)
    p.add_argument("--out", help="write the Markdown evidence file here instead of stdout")
    p.set_defaults(fn=cmd_certify_broker)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    previous = os.environ.get("RT_ENV")
    try:
        return int(args.fn(args))
    except CliError as exc:
        print(str(exc), file=sys.stderr)
        return exc.code
    finally:  # the CLI labels the environment for its own process only
        if previous is None:
            os.environ.pop("RT_ENV", None)
        else:
            os.environ["RT_ENV"] = previous


if __name__ == "__main__":
    sys.exit(main())
