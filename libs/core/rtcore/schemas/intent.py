"""Trade intent — the only write an AI/MCP agent may perform [Source: 00, 04].

Mirrors contracts/api/API_OPENAPI.yaml#/components/schemas/TradeIntent. Contract tests assert
the two stay aligned. An intent is immutable after SCHEMA_VALIDATED; any change is a new intent (P1).
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import Enum
from uuid import UUID

from pydantic import Field, field_validator, model_validator

from rtcore.clock import ensure_utc
from rtcore.schemas.base import StrictModel


class Side(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    SELL_SHORT = "SELL_SHORT"
    BUY_TO_COVER = "BUY_TO_COVER"


class OrderType(str, Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP = "STOP"
    STOP_LIMIT = "STOP_LIMIT"
    TRAILING_STOP = "TRAILING_STOP"
    CONDITIONAL = "CONDITIONAL"


class TimeInForce(str, Enum):
    DAY = "DAY"
    GTC = "GTC"
    IOC = "IOC"
    FOK = "FOK"
    GTD = "GTD"


_NEEDS_LIMIT = {OrderType.LIMIT, OrderType.STOP_LIMIT}
_NEEDS_STOP = {OrderType.STOP, OrderType.STOP_LIMIT, OrderType.TRAILING_STOP}


class TradeIntent(StrictModel):
    intent_id: UUID
    strategy_id: str = Field(min_length=1, max_length=64)
    strategy_version: str = Field(min_length=1, max_length=32)
    model_id: str = Field(min_length=1, max_length=64)
    model_version: str = Field(min_length=1, max_length=32)
    account_id: str = Field(min_length=1, max_length=64)
    venue: str = Field(min_length=1, max_length=32)
    instrument_id: str = Field(min_length=1, max_length=64)
    side: Side
    order_type: OrderType
    quantity: Decimal = Field(gt=0)
    notional: Decimal | None = Field(default=None, gt=0)
    limit_price: Decimal | None = Field(default=None, gt=0)
    stop_price: Decimal | None = Field(default=None, gt=0)
    time_in_force: TimeInForce
    thesis_code: str = Field(min_length=1, max_length=64)
    confidence: float = Field(ge=0.0, le=1.0)
    market_ts: datetime
    data_provenance: list[str] = Field(min_length=1, max_length=32)
    expiry: datetime
    protective_stop: Decimal | None = Field(default=None, gt=0)
    # Explainability contract [Source: 00; C3 §6]: evidence references travel with the intent.
    evidence_refs: list[str] = Field(default_factory=list, max_length=64)

    @field_validator("market_ts", "expiry")
    @classmethod
    def _tz(cls, v: datetime) -> datetime:
        return ensure_utc(v)

    @field_validator("data_provenance")
    @classmethod
    def _provenance(cls, v: list[str]) -> list[str]:
        allowed = {"licensed_feed", "news_adapter", "user_text", "internal_doc", "simulated"}
        bad = [p for p in v if p not in allowed]
        if bad:
            raise ValueError(f"unknown provenance labels: {bad}")
        return v

    @model_validator(mode="after")
    def _prices(self) -> TradeIntent:
        if self.order_type in _NEEDS_LIMIT and self.limit_price is None:
            raise ValueError(f"{self.order_type.value} requires limit_price")
        if self.order_type in _NEEDS_STOP and self.stop_price is None:
            raise ValueError(f"{self.order_type.value} requires stop_price")
        if self.order_type == OrderType.MARKET and (self.limit_price is not None or self.stop_price is not None):
            raise ValueError("MARKET orders carry no limit_price/stop_price")
        if self.expiry <= self.market_ts:
            raise ValueError("expiry must be after market_ts")
        return self


class ValidatedIntent(StrictModel):
    """Intent after SCHEMA_VALIDATED (P1). ``intent_hash`` is recomputed by every downstream engine."""

    intent: TradeIntent
    intent_hash: str
    correlation_id: str
    tenant_id: str
    submitted_by: str
    validated_at: datetime

    @field_validator("validated_at")
    @classmethod
    def _tz(cls, v: datetime) -> datetime:
        return ensure_utc(v)

    @classmethod
    def seal(
        cls, intent: TradeIntent, *, correlation_id: str, tenant_id: str, submitted_by: str, validated_at: datetime
    ) -> ValidatedIntent:
        return cls(
            intent=intent,
            intent_hash=intent.canonical_hash(),
            correlation_id=correlation_id,
            tenant_id=tenant_id,
            submitted_by=submitted_by,
            validated_at=validated_at,
        )

    def integrity_ok(self) -> bool:
        return self.intent.canonical_hash() == self.intent_hash
