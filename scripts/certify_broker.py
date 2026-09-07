#!/usr/bin/env python3
"""Run the sandbox certification harness against the simulated broker and write the evidence file."""

from __future__ import annotations

import sys
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for p in ("libs/core", "connectors/brokers"):
    sys.path.insert(0, str(ROOT / p))
from broker_adapters.certification import certification_markdown, run_certification  # noqa: E402
from broker_adapters.simulated import SimulatedBroker  # noqa: E402

now = datetime(2026, 9, 7, 14, 0, tzinfo=UTC)
broker = SimulatedBroker(known_instruments={"SIMEQ1": "EQUITY"}, venues=("SIMX",))
broker.set_reference_price("SIMEQ1", Decimal("100"), now=now)
rows = run_certification(broker, account_id="acct-sim-001", instrument_id="SIMEQ1", venue="SIMX", now=now, price=Decimal("100"))
md = certification_markdown("sim-broker", rows, run_at=now, run_by="broker-connector-lead (harness)")
(ROOT / "docs" / "BROKER_CERTIFICATIONS" / "sim-broker.md").write_text(md)
passed = sum(r.passed for r in rows)
print(f"certification rows: {len(rows)}, passed: {passed}, open: {len(rows) - passed} -> docs/BROKER_CERTIFICATIONS/sim-broker.md")
