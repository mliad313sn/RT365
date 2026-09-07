"""Decision record [Source: 05]: outcome, policy version, reason codes, evaluated values, thresholds, timestamp."""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import field_validator

from rtcore.clock import ensure_utc
from rtcore.schemas.base import StrictModel


class Outcome(str, Enum):
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    REQUIRES_HUMAN_APPROVAL = "REQUIRES_HUMAN_APPROVAL"
    HALTED = "HALTED"


class CheckResult(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    NOT_EVALUATED = "NOT_EVALUATED"


class EvaluatedCheck(StrictModel):
    check: str
    value: str
    threshold: str
    result: CheckResult
    reason_code: str | None = None


class DecisionRecord(StrictModel):
    decision_id: str
    intent_id: str
    outcome: Outcome
    policy_version: str
    reason_codes: tuple[str, ...]
    evaluated: tuple[EvaluatedCheck, ...]
    account_snapshot_id: str
    market_snapshot_id: str
    decided_at: datetime
    engine_build_hash: str
    correlation_id: str
    intent_hash: str

    @field_validator("decided_at")
    @classmethod
    def _tz(cls, v: datetime) -> datetime:
        return ensure_utc(v)
