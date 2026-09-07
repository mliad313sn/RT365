"""Common event envelope [Source: 03; docs/EVENT_CATALOG.md].

Every event carries event_id, correlation_id, tenant, account, market_ts (where applicable),
emitted_ts, schema_version, producer and payload_hash. Consumers are idempotent via inbox.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from rtcore.clock import utc_now
from rtcore.ids import hash_of, new_id


class EventEnvelope(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    event_id: str
    event_name: str
    schema_version: str
    correlation_id: str
    tenant: str
    account: str | None
    market_ts: datetime | None
    emitted_ts: datetime
    producer: str
    payload_hash: str
    payload: dict[str, Any] = Field(default_factory=dict)


def make_event(
    event_name: str,
    *,
    correlation_id: str,
    tenant: str,
    producer: str,
    payload: BaseModel | dict[str, Any],
    account: str | None = None,
    market_ts: datetime | None = None,
    emitted_ts: datetime | None = None,
    schema_version: str = "v1",
    event_id: str | None = None,
) -> EventEnvelope:
    body = payload.model_dump(mode="json") if isinstance(payload, BaseModel) else dict(payload)
    return EventEnvelope(
        event_id=event_id or new_id("evt"),
        event_name=event_name,
        schema_version=schema_version,
        correlation_id=correlation_id,
        tenant=tenant,
        account=account,
        market_ts=market_ts,
        emitted_ts=emitted_ts or utc_now(),
        producer=producer,
        payload_hash=hash_of(body),
        payload=body,
    )
