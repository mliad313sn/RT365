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


class FxUnavailable(FailClosed):
    """No trustworthy rate for a required conversion: the amount is unknown, never assumed [F-3].

    Carries the reason code the account snapshot and the risk decision publish, so the ledger, the BFF and the
    engine all name the same cause. Subclasses exist so a caller can distinguish *why* without parsing text.
    """

    reason_code = "RK-FX-MISSING"

    def __init__(self, detail: str, *, reason_code: str | None = None) -> None:
        super().__init__(detail)
        self.detail = detail
        if reason_code is not None:
            self.reason_code = reason_code


class FxSnapshotMissing(FxUnavailable):
    """A conversion was required and no FX snapshot was supplied."""

    reason_code = "RK-FX-MISSING"


class FxPairUnknown(FxUnavailable):
    """The snapshot carries no rate for the pair, directly or through its base currency."""

    reason_code = "RK-FX-MISSING"


class FxSnapshotStale(FxUnavailable):
    """The snapshot is older than the freshness budget, or dated in the future (clock anomaly)."""

    reason_code = "RK-FX-STALE"


class FxBudgetUndefined(FxUnavailable):
    """No FX freshness budget is defined: an undefined budget is never "unlimited" [Open: O-07]."""

    reason_code = "RK-FX-UNDEFINED"
