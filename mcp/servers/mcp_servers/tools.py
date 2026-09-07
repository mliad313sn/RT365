"""The six allowed capabilities [Source: 04]. Only ``submit_trade_intent`` writes, and only to the intent queue."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from decimal import Decimal
from typing import Any

from market_data.store import BitemporalStore
from oms.intent_queue import IntentQueue
from rtcore.errors import SchemaViolation
from rtcore.ids import sha256_hex
from rtcore.money import ZERO
from rtcore.planes import Plane, enter
from rtcore.schemas.account import AccountSnapshot
from strategy_service.registry import StrategyRegistry

from mcp_servers.identity import AgentIdentity
from mcp_servers.runtime import Handler, ToolDenied


def _round_balance(value: Decimal, granularity: Decimal = Decimal("1000")) -> str:
    return str((value / granularity).quantize(Decimal("1")) * granularity)


def build_tools(
    *,
    store: BitemporalStore,
    account_state: Callable[[str, datetime], AccountSnapshot | None],
    registry: StrategyRegistry,
    intent_queue: IntentQueue,
    run_simulation: Callable[[dict[str, Any], AgentIdentity, datetime], dict[str, Any]] | None = None,
    depth_entitled: Callable[[str], bool] = lambda tenant: False,
) -> dict[str, Handler]:
    def read_market_snapshot(ident: AgentIdentity, args: dict[str, Any], now: datetime) -> dict[str, Any]:
        snap = store.latest(args["instrument_id"], as_of=now, knowledge_ts=now)
        if snap is None:
            raise ToolDenied("NOT_FOUND", "no snapshot within entitlement")
        depth = depth_entitled(ident.tenant_id)
        return {
            "instrument_id": snap.instrument.instrument_id,
            "market_ts": snap.market_ts.isoformat(),
            "last_price": str(snap.last_price),
            "provenance": snap.provenance.value,
            "quality": snap.quality.value,
            "bid": str(snap.bid) if depth and snap.bid is not None else None,
            "ask": str(snap.ask) if depth and snap.ask is not None else None,
        }

    def read_account_state(ident: AgentIdentity, args: dict[str, Any], now: datetime) -> dict[str, Any]:
        if args["account_id"] != ident.account_id:
            raise ToolDenied("SCOPE", "identity is not scoped to this account")
        acct = account_state(args["account_id"], now)
        if acct is None:
            raise ToolDenied("NOT_FOUND", "account state unavailable")
        return {
            "account_ref": "acct:" + sha256_hex(acct.account_id)[:12],
            "mode": acct.mode.value,
            "nav_rounded": _round_balance(acct.nav),
            "positions": [
                {
                    "instrument_id": p.instrument_id,
                    "side": "LONG" if p.quantity > ZERO else "SHORT",
                    "exposure_rounded": _round_balance(abs(p.market_value)),
                }
                for p in acct.positions
            ],
        }

    def calculate_indicator(ident: AgentIdentity, args: dict[str, Any], now: datetime) -> dict[str, Any]:
        rows = [s for s in store.series(args["instrument_id"], start=datetime.min.replace(tzinfo=now.tzinfo), end=now, knowledge_ts=now)]
        prices = [s.last_price for s in rows][-int(args["window"]) * 3 :]
        n = int(args["window"])
        value: Decimal | None = None
        if len(prices) >= n:
            if args["indicator"] == "sma":
                value = sum(prices[-n:], ZERO) / Decimal(n)
            elif args["indicator"] == "ema":
                k = Decimal(2) / Decimal(n + 1)
                ema = prices[0]
                for p in prices[1:]:
                    ema = p * k + ema * (1 - k)
                value = ema
            elif args["indicator"] == "rsi":
                gains = [max(prices[i] - prices[i - 1], ZERO) for i in range(1, len(prices))][-n:]
                losses = [max(prices[i - 1] - prices[i], ZERO) for i in range(1, len(prices))][-n:]
                ag, al = sum(gains, ZERO) / Decimal(n), sum(losses, ZERO) / Decimal(n)
                value = Decimal(100) if al == ZERO else Decimal(100) - Decimal(100) / (1 + ag / al)
        return {"indicator": args["indicator"], "value": None if value is None else f"{value:.6f}", "as_of": now.isoformat()}

    def run_simulation_tool(ident: AgentIdentity, args: dict[str, Any], now: datetime) -> dict[str, Any]:
        if run_simulation is None:
            raise ToolDenied("NOT_AVAILABLE", "no approved simulation template wired")
        return run_simulation(args, ident, now)

    def get_strategy_docs(ident: AgentIdentity, args: dict[str, Any], now: datetime) -> dict[str, Any]:
        return {"strategy_id": args["strategy_id"], "docs": registry.docs_for(args["strategy_id"])}

    def submit_trade_intent(ident: AgentIdentity, args: dict[str, Any], now: datetime) -> dict[str, Any]:
        raw = dict(args["intent"])
        # The identity pins strategy/account/model: an agent cannot submit on behalf of another scope.
        if raw.get("account_id") != ident.account_id or raw.get("strategy_id") != ident.strategy_id:
            raise ToolDenied("SCOPE", "intent scope differs from agent identity")
        raw["model_id"], raw["model_version"] = ident.model_id, ident.model_version
        try:
            with enter(Plane.ANALYTICS):
                vi = intent_queue.submit(raw, tenant_id=ident.tenant_id, submitted_by=f"agent:{ident.agent_id}", now=now)
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
