"""Strict, schema-first models [Source: 00, 03]. ``extra='forbid'`` everywhere: unknown fields are rejected."""

from rtcore.schemas.account import (
    AccountMode,
    AccountSnapshot,
    EmergencyPolicy,
    KillSwitchFlags,
    OpenOrder,
    Position,
    TradingStatus,
)
from rtcore.schemas.base import StrictModel
from rtcore.schemas.compliance import (
    CustomerProfile,
    CustomerType,
    EligibilityDecision,
    EligibilityOutcome,
    JurisdictionCell,
    RestrictedLists,
)
from rtcore.schemas.decision import CheckResult, DecisionRecord, EvaluatedCheck, Outcome
from rtcore.schemas.intent import OrderType, Side, TimeInForce, TradeIntent, ValidatedIntent
from rtcore.schemas.market import DataQuality, InstrumentAttributes, MarketSnapshot, SessionState
from rtcore.schemas.order import ExecutionTarget, Fill, OrderCommand, OrderRecord, OrderState

__all__ = [
    "StrictModel",
    "AccountMode",
    "AccountSnapshot",
    "EmergencyPolicy",
    "KillSwitchFlags",
    "OpenOrder",
    "Position",
    "TradingStatus",
    "CustomerProfile",
    "CustomerType",
    "EligibilityDecision",
    "EligibilityOutcome",
    "JurisdictionCell",
    "RestrictedLists",
    "CheckResult",
    "DecisionRecord",
    "EvaluatedCheck",
    "Outcome",
    "OrderType",
    "Side",
    "TimeInForce",
    "TradeIntent",
    "ValidatedIntent",
    "DataQuality",
    "InstrumentAttributes",
    "MarketSnapshot",
    "SessionState",
    "ExecutionTarget",
    "Fill",
    "OrderCommand",
    "OrderRecord",
    "OrderState",
]
