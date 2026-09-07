"""Typed payloads for events that are not already a first-class record (docs/EVENT_CATALOG.md)."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from rtcore.schemas.base import StrictModel


class OrderEvent(StrictModel):
    order_id: str
    client_order_id: str
    state: str
    fencing_token: int
    idempotency_key: str
    intent_id: str
    decision_id: str
    broker_order_ref: str | None = None
    reason: str | None = None
    fill_quantity: Decimal | None = None
    fill_price: Decimal | None = None
    fill_ref: str | None = None
    retry: bool = False
    broker_dedupe: bool = False


class ReconciliationCompleted(StrictModel):
    account_id: str
    as_of: datetime
    positions_compared: int
    orders_compared: int
    break_count: int


class ModelDrift(StrictModel):
    model_id: str
    model_version: str
    metric: str
    value: Decimal
    threshold: Decimal
    observed_at: datetime


class LimitChanged(StrictModel):
    change_id: str
    metric: str
    level: str
    scope_id: str
    old_threshold: Decimal | None
    new_threshold: Decimal
    maker: str
    checker: str
    cooling_period_end: datetime
    policy_version: str
