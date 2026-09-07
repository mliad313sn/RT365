"""rtcore — shared primitives for the Global AI-MCP RoboTrader platform.

Everything here is plane-neutral: identifiers, canonical hashing, clock helpers, the
plane guard that enforces the Analytics -> Control -> Execution topology [Source: 00, 03],
monotonic state machines [Source: 03] and the strict schemas [Source: 00].
"""

from rtcore.errors import (
    ControlDenied,
    FailClosed,
    PlaneViolation,
    RTError,
    SchemaViolation,
    TransitionError,
)

__all__ = [
    "RTError",
    "PlaneViolation",
    "TransitionError",
    "ControlDenied",
    "FailClosed",
    "SchemaViolation",
]
