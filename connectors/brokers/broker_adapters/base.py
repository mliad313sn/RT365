from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import Field
from rtcore.errors import RTError
from rtcore.schemas.base import StrictModel
from rtcore.schemas.intent import OrderType, Side, TimeInForce


class BrokerUnavailable(RTError):
    """Connectivity or credential failure. The gateway treats it as retryable with the same idempotency key."""


class Capabilities(StrictModel):
    """Capability discovery [Source: 02 FR-02]: unsupported order types are rejected before submission."""

    broker: str
    venues: tuple[str, ...]
    asset_classes: tuple[str, ...]
    order_types: tuple[OrderType, ...]
    time_in_force: tuple[TimeInForce, ...]
    supports_partial_fills: bool
    supports_cancel_replace: bool
    dedupes_client_order_id: bool  # ADR-002: not all brokers dedupe; fencing covers the rest
    sandbox: bool


class VaultRef(StrictModel):
    """Reference to a credential in the vault. The raw secret never enters application memory here."""

    path: str
    version: int = 1


class BrokerHealth(StrictModel):
    connected: bool
    latency_ms: Decimal
    last_heartbeat: datetime
    credential_version: int
    credential_rotation_due: bool = False


class SubmitRequest(StrictModel):
    client_order_id: str
    account_id: str
    venue: str
    instrument_id: str
    side: Side
    order_type: OrderType
    quantity: Decimal = Field(gt=0)
    limit_price: Decimal | None = None
    stop_price: Decimal | None = None
    time_in_force: TimeInForce


class AckStatus(str, Enum):
    ACKNOWLEDGED = "ACKNOWLEDGED"
    REJECTED = "REJECTED"
    DUPLICATE = "DUPLICATE"
    CANCELLED = "CANCELLED"
    REPLACED = "REPLACED"


class BrokerAck(StrictModel):
    client_order_id: str
    broker_order_ref: str | None
    status: AckStatus
    reason: str | None = None
    ts: datetime


class BrokerFill(StrictModel):
    fill_ref: str
    client_order_id: str
    broker_order_ref: str
    quantity: Decimal = Field(gt=0)
    price: Decimal = Field(gt=0)
    fee: Decimal = Decimal("0")
    ts: datetime


class OrderStatus(StrictModel):
    """Broker-side view of one order; ``known=False`` means the broker never received it."""

    client_order_id: str
    known: bool
    broker_order_ref: str | None = None
    status: str | None = None  # OPEN | PARTIAL | FILLED | CANCELLED | REJECTED
    filled_quantity: Decimal = Decimal("0")


class StatementPosition(StrictModel):
    instrument_id: str
    quantity: Decimal
    average_price: Decimal


class StatementOrder(StrictModel):
    client_order_id: str
    broker_order_ref: str
    status: str
    filled_quantity: Decimal


class BrokerStatement(StrictModel):
    """Broker statement is the final external truth [Source: 03]."""

    broker: str
    account_id: str
    as_of: datetime
    cash: Decimal
    positions: tuple[StatementPosition, ...]
    orders: tuple[StatementOrder, ...]
    fills: tuple[BrokerFill, ...]


class BrokerAdapter(ABC):
    name: str

    @abstractmethod
    def capabilities(self) -> Capabilities: ...

    @abstractmethod
    def connect(self, vault_ref: VaultRef, *, now: datetime) -> None: ...

    @abstractmethod
    def disconnect(self) -> None: ...

    @abstractmethod
    def rotate_credentials(self, vault_ref: VaultRef, *, now: datetime) -> None: ...

    @abstractmethod
    def health(self, *, now: datetime) -> BrokerHealth: ...

    @abstractmethod
    def submit(self, request: SubmitRequest, *, now: datetime) -> BrokerAck: ...

    @abstractmethod
    def cancel(self, client_order_id: str, *, now: datetime) -> BrokerAck: ...

    @abstractmethod
    def replace(self, client_order_id: str, *, quantity: Decimal | None, limit_price: Decimal | None, now: datetime) -> BrokerAck: ...

    @abstractmethod
    def poll_fills(self, *, now: datetime) -> tuple[BrokerFill, ...]: ...

    @abstractmethod
    def query_order(self, client_order_id: str, *, now: datetime) -> OrderStatus: ...

    @abstractmethod
    def statement(self, account_id: str, *, as_of: datetime) -> BrokerStatement: ...

    def supports(self, order_type: OrderType, tif: TimeInForce, asset_class: str, venue: str) -> tuple[bool, str]:
        c = self.capabilities()
        if order_type not in c.order_types:
            return False, f"order type {order_type.value} unsupported by {c.broker}"
        if tif not in c.time_in_force:
            return False, f"time in force {tif.value} unsupported by {c.broker}"
        if asset_class not in c.asset_classes:
            return False, f"asset class {asset_class} unsupported by {c.broker}"
        if venue not in c.venues:
            return False, f"venue {venue} unsupported by {c.broker}"
        return True, "ok"
