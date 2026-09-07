#!/usr/bin/env python3
"""Export JSON Schemas for every event in docs/EVENT_CATALOG.md to contracts/events/<name>.json.

--check: fail if the committed schemas differ from the models (schema drift, ADR-005).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for p in (
    "libs/core",
    "services/risk",
    "services/compliance",
    "services/approval",
    "services/killswitch",
    "services/identity",
    "services/strategy",
    "services/reconciliation",
    "connectors/brokers",
):
    sys.path.insert(0, str(ROOT / p))
from approval_service.queue import ApprovalRecord  # noqa: E402
from identity_service.makerchecker import PendingChange  # noqa: E402
from killswitch_service.service import Activation  # noqa: E402
from reconciliation_service.reconcile import Break  # noqa: E402
from risk_engine.monitors import HaltEvent  # noqa: E402
from rtcore.envelope import EventEnvelope  # noqa: E402
from rtcore.schemas.compliance import EligibilityDecision, JurisdictionCell  # noqa: E402
from rtcore.schemas.decision import DecisionRecord  # noqa: E402
from rtcore.schemas.events import ModelDrift, OrderEvent, ReconciliationCompleted  # noqa: E402
from rtcore.schemas.intent import ValidatedIntent  # noqa: E402
from rtcore.schemas.market import MarketSnapshot  # noqa: E402
from rtcore.schemas.order import OrderCommand  # noqa: E402
from strategy_service.signals import Signal  # noqa: E402

CATALOG = {
    "envelope.v1": EventEnvelope,
    "market.snapshot.v1": MarketSnapshot,
    "strategy.signal.v1": Signal,
    "intent.submitted.v1": ValidatedIntent,
    "eligibility.decided.v1": EligibilityDecision,
    "risk.decided.v1": DecisionRecord,
    "approval.recorded.v1": ApprovalRecord,
    "order.command.v1": OrderCommand,
    "order.submitted.v1": OrderEvent,
    "order.acked.v1": OrderEvent,
    "order.rejected.v1": OrderEvent,
    "order.filled.v1": OrderEvent,
    "order.cancelled.v1": OrderEvent,
    "reconciliation.completed.v1": ReconciliationCompleted,
    "reconciliation.break.v1": Break,
    "risk.halt.v1": HaltEvent,
    "killswitch.activated.v1": Activation,
    "killswitch.deactivated.v1": Activation,
    "limit.changed.v1": PendingChange,
    "model.drift.v1": ModelDrift,
    "jurisdiction.flag.changed.v1": JurisdictionCell,
}

out_dir = ROOT / "contracts" / "events"
check = "--check" in sys.argv
drift = []
for name, model in CATALOG.items():
    schema = model.model_json_schema()
    schema["$id"] = f"https://rt365.example/contracts/events/{name}.json"
    schema["title"] = name
    text = json.dumps(schema, indent=2, sort_keys=True) + "\n"
    target = out_dir / f"{name}.json"
    if check:
        if not target.exists() or target.read_text() != text:
            drift.append(name)
    else:
        target.write_text(text)
if check:
    if drift:
        print("FAIL schema drift: " + ", ".join(drift) + " (run scripts/export_event_schemas.py and have the Integration Architect review)")
        sys.exit(1)
    print(f"OK: {len(CATALOG)} event schemas match the models")
else:
    print(f"wrote {len(CATALOG)} schemas to contracts/events/")
