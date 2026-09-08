"""TC-ARC-001..004 — ADR-009 condition C-04-3 (D-055): the engines are framework-free. No module under services/, libs/ or
mcp/servers imports the web framework, the ASGI server or an HTTP client; only apps/ (the BFF, the CLI) may."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
BANNED = ("fastapi", "starlette", "uvicorn", "httpx", "requests", "flask", "django", "aiohttp")
ENGINE_ROOTS = ("services", "libs", "mcp/servers", "connectors", "observability")
DYNAMIC_IMPORTERS = ("import_module", "__import__")


def banned_imports(source: str) -> list[str]:
    """Return the banned top-level packages a module imports, statically or through importlib/__import__ with a literal."""
    found: list[str] = []
    for node in ast.walk(ast.parse(source)):
        names: list[str] = []
        if isinstance(node, ast.Import):
            names = [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            names = [node.module]
        elif isinstance(node, ast.Call):
            func = node.func
            attr = func.attr if isinstance(func, ast.Attribute) else func.id if isinstance(func, ast.Name) else ""
            if attr in DYNAMIC_IMPORTERS and node.args and isinstance(node.args[0], ast.Constant):
                names = [str(node.args[0].value)]
        found.extend(n for n in names if n.split(".")[0] in BANNED)
    return found


def scan(roots: tuple[str, ...], base: Path = ROOT) -> list[str]:
    offenders: list[str] = []
    for root in roots:
        for f in sorted((base / root).rglob("*.py")):
            offenders.extend(f"{f.relative_to(base)}: {n}" for n in banned_imports(f.read_text(encoding="utf-8")))
    return offenders


@pytest.mark.tc("TC-ARC-001")
@pytest.mark.req("NFR-SEC-01")
@pytest.mark.quartet("negative")
def test_engines_do_not_import_the_web_framework() -> None:
    """Every module under the engine roots is free of fastapi/starlette/uvicorn/httpx/requests imports (ADR-009: framework at the edges only)."""
    assert scan(ENGINE_ROOTS) == []


@pytest.mark.tc("TC-ARC-002")
@pytest.mark.req("NFR-SEC-01")
@pytest.mark.quartet("positive")
def test_edges_may_import_the_framework_and_engines_use_only_the_kernel() -> None:
    """The BFF under apps/ imports FastAPI (the edge is where the framework lives) and the scanner reports it there only, never under the engine roots."""
    assert any("fastapi" in line for line in scan(("apps/web",)))
    assert banned_imports("from rtcore.schemas.compliance import JurisdictionCell\nimport json\n") == []


@pytest.mark.tc("TC-ARC-003")
@pytest.mark.req("NFR-SEC-01")
@pytest.mark.quartet("abuse")
def test_disguised_imports_are_caught() -> None:
    """Aliased, nested, dotted, try-guarded and importlib/__import__ literal imports of a banned package are all reported."""
    cases = {
        "import fastapi as fa": ["fastapi"],
        "from starlette.responses import JSONResponse": ["starlette.responses"],
        "def f():\n    import httpx\n": ["httpx"],
        "try:\n    import requests\nexcept ImportError:\n    requests = None\n": ["requests"],
        "import importlib\nm = importlib.import_module('uvicorn')\n": ["uvicorn"],
        "m = __import__('aiohttp')\n": ["aiohttp"],
    }
    for source, expected in cases.items():
        assert banned_imports(source) == expected, source


@pytest.mark.tc("TC-ARC-004")
@pytest.mark.req("NFR-SEC-01")
@pytest.mark.quartet("recovery")
def test_offender_is_located_and_removal_restores_green(tmp_path: Path) -> None:
    """A planted offender under a copy of an engine root is reported with its path; deleting the import restores an empty report."""
    pkg = tmp_path / "services" / "demo"
    pkg.mkdir(parents=True)
    (pkg / "__init__.py").write_text("")
    bad = pkg / "gateway.py"
    bad.write_text("import fastapi\nX = 1\n", encoding="utf-8")
    assert scan(("services",), tmp_path) == ["services/demo/gateway.py: fastapi"]
    bad.write_text("X = 1\n", encoding="utf-8")
    assert scan(("services",), tmp_path) == []
