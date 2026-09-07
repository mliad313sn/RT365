"""Platform error types. Control-plane code fails closed: an error never yields APPROVED."""


class RTError(Exception):
    """Base class for platform errors."""


class PlaneViolation(RTError):
    """A call crossed a plane boundary that the topology denies [Source: 00, 03; ADR-001]."""


class TransitionError(RTError):
    """A state machine was asked for a non-monotonic transition [Source: 03]."""


class ControlDenied(RTError):
    """A control (maker-checker, two-person rule, allowlist, Kill Switch) denied the action."""


class FailClosed(RTError):
    """An input required by a deterministic engine was unavailable; the outcome is HALTED."""


class SchemaViolation(RTError):
    """Strict schema validation failed (unknown field, invalid value, stale data)."""
