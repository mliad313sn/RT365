"""Contract tests: models stay aligned with contracts/api/API_OPENAPI.yaml and the event schemas [Source: 03; ADR-005]."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest
import yaml
from killswitch_service.service import KillSwitchLevel
from rtcore.schemas.decision import DecisionRecord, Outcome
from rtcore.schemas.intent import OrderType, Side, TimeInForce, TradeIntent

ROOT = Path(__file__).resolve().parents[2]
SPEC = yaml.safe_load((ROOT / "contracts" / "api" / "API_OPENAPI.yaml").read_text())


def test_trade_intent_matches_openapi():  # type: ignore[no-untyped-def]
    schema = SPEC["components"]["schemas"]["TradeIntent"]
    model_fields = TradeIntent.model_fields
    assert set(schema["properties"]) == set(model_fields), set(schema["properties"]) ^ set(model_fields)
    required = {n for n, f in model_fields.items() if f.is_required()}
    assert set(schema["required"]) == required
    assert schema["additionalProperties"] is False and TradeIntent.model_config["extra"] == "forbid"
    assert schema["properties"]["side"]["enum"] == [s.value for s in Side]
    assert schema["properties"]["order_type"]["enum"] == [o.value for o in OrderType]
    assert schema["properties"]["time_in_force"]["enum"] == [t.value for t in TimeInForce]


def test_decision_record_matches_openapi():  # type: ignore[no-untyped-def]
    schema = SPEC["components"]["schemas"]["DecisionRecord"]
    assert set(schema["required"]) <= set(DecisionRecord.model_fields)
    assert schema["properties"]["outcome"]["enum"] == [o.value for o in Outcome]
    assert set(schema["properties"]["evaluated"]["items"]["required"]) == {"check", "value", "threshold", "result"}


def test_killswitch_levels_match_openapi():  # type: ignore[no-untyped-def]
    assert SPEC["components"]["schemas"]["KillSwitchRequest"]["properties"]["level"]["enum"] == [lv.value for lv in KillSwitchLevel]


def test_event_schemas_have_no_drift():  # type: ignore[no-untyped-def]
    out = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "export_event_schemas.py"), "--check"], capture_output=True, text=True, cwd=ROOT
    )
    assert out.returncode == 0, out.stdout + out.stderr


def test_event_catalog_lists_every_schema():  # type: ignore[no-untyped-def]
    catalog = (ROOT / "docs" / "EVENT_CATALOG.md").read_text()
    for f in (ROOT / "contracts" / "events").glob("*.v1.json"):
        name = f.name[: -len(".json")]
        base = name.rsplit(".v1", 1)[0]
        assert base.split(".")[0] in catalog, f"{name} not in EVENT_CATALOG"


def test_tool_registry_policy_invariants():  # type: ignore[no-untyped-def]
    out = subprocess.run([sys.executable, str(ROOT / "scripts" / "verify_tool_registry.py")], capture_output=True, text=True, cwd=ROOT)
    assert out.returncode == 0, out.stdout
    prod = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "verify_tool_registry.py"), "--production"], capture_output=True, text=True, cwd=ROOT
    )
    assert prod.returncode == 1 and "dev signing key" in prod.stdout  # dev key must be refused for production


def test_reason_codes_all_documented():  # type: ignore[no-untyped-def]
    out = subprocess.run([sys.executable, str(ROOT / "scripts" / "export_reason_codes.py")], capture_output=True, text=True, cwd=ROOT)
    assert out.returncode == 0, out.stdout


@pytest.mark.tc("TC-E2E-API")
@pytest.mark.req("FR-16")
@pytest.mark.quartet("positive")
def test_bff_routes_match_openapi_paths():  # type: ignore[no-untyped-def]
    """Every BFF route is in contracts/api/API_OPENAPI.yaml and vice versa (path parameter names normalised)."""
    import re

    from web_bff.app import create_app
    from web_bff.platform import build_sim_platform

    def norm(path: str) -> str:
        return re.sub(r"\{[^}]+\}", "{}", path)

    app = create_app(build_sim_platform())
    served: set[tuple[str, str]] = set()
    for route in app.routes:
        path = getattr(route, "path", "")
        methods = getattr(route, "methods", None) or set()
        if not path.startswith("/v1/"):
            continue
        for m in methods:
            if m in ("GET", "POST", "PUT", "DELETE"):
                served.add((m, norm(path)))
    declared = {(m.upper(), norm(path)) for path, ops in SPEC["paths"].items() for m in ops if m in ("get", "post", "put", "delete")}
    assert served == declared, {"undeclared": sorted(served - declared), "unserved": sorted(declared - served)}
