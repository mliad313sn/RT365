"""The six allowed capabilities [Source: 04]. Only ``submit_trade_intent`` writes, and only to the intent queue.

Review remedies: F-07 (strategy_version pinned; entitlement-filtered reads; docs scoped to the identity's
strategy), F-16 (keyed pseudonyms), F-18 (bounded indicator reads), OBJ-1 (simulation template/strategy validation).
"""

from __future__ import annotations

import hmac
from collections.abc import Callable
from datetime import datetime, timedelta
from decimal import Decimal
from hashlib import sha256
from typing import Any

from market_data.store import BitemporalStore
from oms.intent_queue import IntentQueue
from rtcore.errors import SchemaViolation
from rtcore.money import ZERO
from rtcore.planes import Plane, enter
from rtcore.schemas.account import AccountSnapshot
from strategy_service.registry import StrategyRegistry, StrategyStatus

from mcp_servers.identity import Principal
from mcp_servers.runtime import Handler, ToolDenied

APPROVED_SIMULATION_TEMPLATES = frozenset({"sma_crossover_replay"})
SIMULATABLE_STATUSES = frozenset({s for s in StrategyStatus if s not in (StrategyStatus.REJECTED, StrategyStatus.RETIRED)})


def _round_balance(value: Decimal, granularity: Decimal = Decimal("1000")) -> str:
    return str((value / granularity).quantize(Decimal("1")) * granularity)


def _pseudonym(tenant_key: str, value: str) -> str:
    """Keyed pseudonym (HMAC with a per-tenant key held outside the analytics plane) instead of a bare hash (F-16)."""
    return "acct:" + hmac.new(tenant_key.encode(), value.encode(), sha256).hexdigest()[:16]


def build_tools(
    *,
    store: BitemporalStore,
    account_state: Callable[[str, datetime], AccountSnapshot | None],
    registry: StrategyRegistry,
    intent_queue: IntentQueue,
    run_simulation: Callable[[dict[str, Any], Principal, datetime], dict[str, Any]] | None = None,
    depth_entitled: Callable[[str], bool] = lambda tenant: False,
    instrument_entitled: Callable[[str, str], bool] = lambda tenant, instrument: True,
    masking_key: Callable[[str], str] = lambda tenant: "sim-masking-key-" + tenant,
) -> dict[str, Handler]:
    def _require_entitled(p: Principal, instrument_id: str) -> None:
        if not instrument_entitled(p.tenant_id, instrument_id):
            raise ToolDenied("NOT_ENTITLED", "instrument outside tenant entitlement")

    def read_market_snapshot(p: Principal, args: dict[str, Any], now: datetime) -> dict[str, Any]:
        _require_entitled(p, args["instrument_id"])
        snap = store.latest(args["instrument_id"], as_of=now, knowledge_ts=now)
        if snap is None:
            raise ToolDenied("NOT_FOUND", "no snapshot within entitlement")
        depth = depth_entitled(p.tenant_id)
        return {
            "instrument_id": snap.instrument.instrument_id,
            "market_ts": snap.market_ts.isoformat(),
            "last_price": str(snap.last_price),
            "provenance": snap.provenance.value,
            "quality": snap.quality.value,
            "bid": str(snap.bid) if depth and snap.bid is not None else None,
            "ask": str(snap.ask) if depth and snap.ask is not None else None,
        }

    def read_account_state(p: Principal, args: dict[str, Any], now: datetime) -> dict[str, Any]:
        if args["account_id"] != p.account_id:
            raise ToolDenied("SCOPE", "identity is not scoped to this account")
        acct = account_state(args["account_id"], now)
        if acct is None or acct.tenant_id != p.tenant_id:
            raise ToolDenied("NOT_FOUND", "account state unavailable")
        return {
            "account_ref": _pseudonym(masking_key(p.tenant_id), acct.account_id),
            "mode": acct.mode.value,
            "nav_rounded": _round_balance(acct.nav),
            "positions": [
                {
                    "instrument_id": pos.instrument_id,
                    "side": "LONG" if pos.quantity > ZERO else "SHORT",
                    "exposure_rounded": _round_balance(abs(pos.market_value)),
                }
                for pos in acct.positions
            ],
        }

    def calculate_indicator(p: Principal, args: dict[str, Any], now: datetime) -> dict[str, Any]:
        _require_entitled(p, args["instrument_id"])
        n = int(args["window"])
        rows = store.series(args["instrument_id"], start=now - timedelta(minutes=n * 3), end=now, knowledge_ts=now)
        prices = [s.last_price for s in rows][-n * 3 :]
        value: Decimal | None = None
        if len(prices) >= n:
            if args["indicator"] == "sma":
                value = sum(prices[-n:], ZERO) / Decimal(n)
            elif args["indicator"] == "ema":
                k = Decimal(2) / Decimal(n + 1)
                ema = sum(prices[:n], ZERO) / Decimal(n)
                for px in prices[n:]:
                    ema = px * k + ema * (1 - k)
                value = ema
            elif args["indicator"] == "rsi":
                gains = [max(prices[i] - prices[i - 1], ZERO) for i in range(1, len(prices))][-n:]
                losses = [max(prices[i - 1] - prices[i], ZERO) for i in range(1, len(prices))][-n:]
                ag, al = sum(gains, ZERO) / Decimal(n), sum(losses, ZERO) / Decimal(n)
                value = Decimal(100) if al == ZERO else Decimal(100) - Decimal(100) / (1 + ag / al)
        return {"indicator": args["indicator"], "value": None if value is None else f"{value:.6f}", "as_of": now.isoformat()}

    def run_simulation_tool(p: Principal, args: dict[str, Any], now: datetime) -> dict[str, Any]:
        if run_simulation is None:
            raise ToolDenied("NOT_AVAILABLE", "no approved simulation template wired")
        if args["template"] not in APPROVED_SIMULATION_TEMPLATES:
            raise ToolDenied("SCOPE", "simulation template not approved")
        if args["strategy_id"] != p.strategy_id or args["strategy_version"] != p.strategy_version:
            raise ToolDenied("SCOPE", "simulation must target the identity's own strategy version")
        try:
            sv = registry.get(args["strategy_id"], args["strategy_version"])
        except KeyError as exc:
            raise ToolDenied("SCOPE", "strategy version not registered") from exc
        if sv.status not in SIMULATABLE_STATUSES:
            raise ToolDenied("SCOPE", f"strategy status {sv.status.value} cannot be simulated")
        _require_entitled(p, args["instrument_id"])
        return run_simulation(args, p, now)

    def get_strategy_docs(p: Principal, args: dict[str, Any], now: datetime) -> dict[str, Any]:
        if args["strategy_id"] != p.strategy_id:
            raise ToolDenied("SCOPE", "docs limited to the identity's strategy")
        return {"strategy_id": args["strategy_id"], "docs": registry.docs_for(args["strategy_id"])[:4000]}

    def submit_trade_intent(p: Principal, args: dict[str, Any], now: datetime) -> dict[str, Any]:
        raw = dict(args["intent"])
        # The identity pins account/strategy/version/model: an agent cannot submit on behalf of another scope.
        if (
            raw.get("account_id") != p.account_id
            or raw.get("strategy_id") != p.strategy_id
            or raw.get("strategy_version") != p.strategy_version
        ):
            raise ToolDenied("SCOPE", "intent scope differs from agent identity")
        raw["model_id"], raw["model_version"] = p.model_id, p.model_version
        try:
            with enter(Plane.ANALYTICS):
                vi = intent_queue.submit(raw, tenant_id=p.tenant_id, submitted_by=f"agent:{p.agent_id}", now=now)
        except SchemaViolation as exc:
            raise ToolDenied("INTENT_SCHEMA", str(exc)[:300]) from exc
        return {
            "intent_id": str(vi.intent.intent_id),
            "intent_hash": vi.intent_hash,
            "correlation_id": vi.correlation_id,
            "state": "SCHEMA_VALIDATED",
        }

    return {
        "read_market_snapshot": read_market_snapshot,
        "read_account_state": read_account_state,
        "calculate_indicator": calculate_indicator,
        "run_simulation": run_simulation_tool,
        "get_strategy_docs": get_strategy_docs,
        "submit_trade_intent": submit_trade_intent,
    }
