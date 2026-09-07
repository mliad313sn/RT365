# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for the one-file rt365 executable (rt365.exe on Windows) [ADR-016].

Bundles the Python packages plus the resource bundle at the repository-relative layout that
rtcore.resources.resource_root() expects (mcp/policies, observability catalogues, risk policy,
dashboard assets). Build with: pyinstaller installer/rt365.spec  (or `make exe`).
"""

import sys
from pathlib import Path

ROOT = Path(SPECPATH).resolve().parent
BUNDLE = [
    "mcp/policies",
    "observability/alerts.yaml",
    "observability/slis.yaml",
    "services/risk/policies",
    "apps/web/static",
]
datas = []
for rel in BUNDLE:
    src = ROOT / rel
    dest = rel if src.is_dir() else str(Path(rel).parent)
    datas.append((str(src), dest))

PKG_DIRS = [
    "libs/core", "services/market-data", "services/strategy", "services/backtest", "services/portfolio",
    "services/risk", "services/compliance", "services/approval", "services/oms", "services/execution",
    "services/reconciliation", "services/audit", "services/killswitch", "services/identity",
    "mcp/servers", "connectors/brokers", "connectors/data-providers", "observability", "apps/web", "apps/cli",
]
pathex = [str(ROOT / p) for p in PKG_DIRS]
hiddenimports = [
    "rtcore", "rtcore.schemas", "market_data", "strategy_service", "backtest_engine", "portfolio_service",
    "risk_engine", "compliance_engine", "approval_service", "oms", "execution_gateway", "reconciliation_service",
    "audit_service", "killswitch_service", "identity_service", "mcp_servers", "mcp_servers.stdio", "broker_adapters",
    "data_providers", "rtobs", "web_bff", "web_bff.app", "web_bff.platform", "rt365_cli", "rt365_cli.main",
    "uvicorn.logging", "uvicorn.loops.auto", "uvicorn.protocols.http.auto", "uvicorn.protocols.websockets.auto",
    "uvicorn.lifespan.on", "anyio._backends._asyncio", "pydantic.deprecated.decorator",
]

a = Analysis(
    [str(ROOT / "installer" / "rt365_launcher.py")],
    pathex=pathex,
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=["tkinter", "pytest", "hypothesis", "mypy", "ruff", "PyInstaller"],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="rt365",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
