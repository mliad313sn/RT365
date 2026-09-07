"""Deterministic Risk Engine [Source: 05; C4].

``decide`` is a pure function of (validated intent, account snapshot, market snapshot, policy,
now). No I/O, no randomness, no model call. Unavailable inputs -> HALTED (fail closed).
Protected path: 2nd-line CODEOWNER (Chief Risk Agent) approval required for changes.
"""

from risk_engine.engine import ENGINE_BUILD_HASH, decide
from risk_engine.monitors import HaltEvent, RuntimeMetrics, evaluate_runtime
from risk_engine.policy import Limit, LimitLevel, RiskPolicy, effective_limit, load_policy

__all__ = [
    "decide",
    "ENGINE_BUILD_HASH",
    "RiskPolicy",
    "Limit",
    "LimitLevel",
    "effective_limit",
    "load_policy",
    "evaluate_runtime",
    "HaltEvent",
    "RuntimeMetrics",
]
