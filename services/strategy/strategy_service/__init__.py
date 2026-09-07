"""Strategy registry, lifecycle (P2), pre-registration and signal contract [Source: 04, 08; E08]."""

from strategy_service.registry import PreRegistration, StrategyRegistry, StrategyStatus, StrategyVersion
from strategy_service.signals import Signal, SmaCrossoverStrategy, Strategy, intent_from_signal

__all__ = [
    "StrategyRegistry",
    "StrategyStatus",
    "StrategyVersion",
    "PreRegistration",
    "Signal",
    "Strategy",
    "SmaCrossoverStrategy",
    "intent_from_signal",
]
