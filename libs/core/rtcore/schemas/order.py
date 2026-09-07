"""Authorised order command, order record and fills [Source: 03; ADR-002, ADR-003]."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import Field, field_validator

from rtcore.clock import ensure_utc
from rtcore.ids import canonical_json, sha256_hex
from rtcore.schemas.base import StrictModel
from rtcore.schemas.intent import OrderType, Side, TimeInForce


class ExecutionTarget(str, Enum):
    SIM = "SIM"  # backtest / simulation broker
    PAPER = "PAPER"  # live data, virtual capital
    LIVE = "LIVE"  # certified broker; only after Gate D/E and cell enablement


def idempotency_key(intent_id: str, account_id: str, policy_version: str) -> str:
    """ADR-003: idempotency_key = hash(intent_id, account, policy_version)."""
    return sha256_hex(f"{intent_id}|{account_id}|{policy_version}")


def client_order_id(key: str) -> str:
    """Broker client-order-id derived from the idempotency key (ADR-003)."""
    return f"RT{key[:24]}"


class OrderCommand(StrictModel):
    command_id: str
    idempotency_key: str
    intent_id: str
    intent_hash: str
    decision_id: str
    approval_id: str | None
    tenant_id: str
    account_id: str
    strategy_id: str
    venue: str
    instrument_id: str
    side: Side
    order_type: OrderType
    quantity: Decimal = Field(gt=0)
    limit_price: Decimal | None = None
    stop_price: Decimal | None = None
    time_in_force: TimeInForce
    policy_version: str
    correlation_id: str
    authorised_at: datetime
    authorised_by: str
    execution_target: ExecutionTarget
    # Control-plane authorisation MAC over authorised_digest(); the execution gateway verifies it and refuses
    # commands that did not come through the risk/approval pipeline (IVA V-C2). Empty = unauthorised.
    authorisation: str = ""

    def authorised_digest(self) -> str:
        """Canonical digest of every field that authorisation binds (everything except the MAC itself)."""
        fields = self.model_dump(mode="json", exclude={"authorisation"})
        return sha256_hex(canonical_json(fields))  # canonical JSON is injective over the field set (IVA-20)

    @field_validator("authorised_at")
    @classmethod
    def _tz(cls, v: datetime) -> datetime:
        return ensure_utc(v)


class OrderState(str, Enum):
    CREATED = "CREATED"
    SUBMITTED = "SUBMITTED"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    BROKER_REJECTED = "BROKER_REJECTED"
    EXPIRED = "EXPIRED"


class Fill(StrictModel):
    fill_id: str
    order_id: str
    client_order_id: str
    quantity: Decimal = Field(gt=0)
    price: Decimal = Field(gt=0)
    fee: Decimal = Decimal("0")  # broker-reported fee: costs live inside the single code path (ADR-008)
    fill_ts: datetime
    broker_ref: str

    @field_validator("fill_ts")
    @classmethod
    def _tz(cls, v: datetime) -> datetime:
        return ensure_utc(v)


class OrderRecord(StrictModel):
    order_id: str
    client_order_id: str
    command: OrderCommand
    state: OrderState
    fencing_token: int
    filled_quantity: Decimal = Decimal("0")
    fills: tuple[Fill, ...] = ()
    broker_order_ref: str | None = None
    reject_reason: str | None = None
    history: tuple[tuple[str, str], ...] = ()  # (state, iso ts)
    updated_at: datetime

    @field_validator("updated_at")
    @classmethod
    def _tz(cls, v: datetime) -> datetime:
        return ensure_utc(v)

    @property
    def remaining_quantity(self) -> Decimal:
        return self.command.quantity - self.filled_quantity
