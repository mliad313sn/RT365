"""Account snapshot — the second input of the deterministic risk decision [Source: 05]."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import Field, field_validator, model_validator

from rtcore.clock import ensure_utc
from rtcore.schemas.base import StrictModel
from rtcore.schemas.intent import Side


class AccountMode(str, Enum):
    """Operating modes ordered by exposure [Source: 01; Committee C1 §1]."""

    OBSERVE = "OBSERVE"
    BACKTEST = "BACKTEST"
    PAPER = "PAPER"
    SUPERVISED = "SUPERVISED"
    BOUNDED_AUTONOMOUS = "BOUNDED_AUTONOMOUS"
    HALTED = "HALTED"


MODE_LADDER: tuple[AccountMode, ...] = (
    AccountMode.OBSERVE,
    AccountMode.BACKTEST,
    AccountMode.PAPER,
    AccountMode.SUPERVISED,
    AccountMode.BOUNDED_AUTONOMOUS,
)


class TradingStatus(str, Enum):
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    CLOSED = "CLOSED"


class EmergencyPolicy(str, Enum):
    CANCEL_ONLY = "CANCEL_ONLY"
    CANCEL_AND_REDUCE = "CANCEL_AND_REDUCE"
    CANCEL_AND_FLATTEN = "CANCEL_AND_FLATTEN"


class NavStatus(str, Enum):
    """Is the base-currency value of this account known at all? [F-3]

    ``UNKNOWN`` is a first-class outcome, not a zero: when a rate needed to value the book is missing or stale the
    platform says so and the deterministic engine fails closed. A number is never invented to fill the gap.
    """

    KNOWN = "KNOWN"
    UNKNOWN = "UNKNOWN"


class Valuation(StrictModel):
    """The base-currency value of the book and *why* it is or is not known [Source: 02 FR-05; F-3].

    ``value`` is None exactly when ``status`` is UNKNOWN, and then ``reason_code`` names the cause (RK-FX-MISSING,
    RK-FX-STALE, RK-FX-UNDEFINED) and ``detail`` carries the values and thresholds for the audit row. Displayed
    below the risk state; never a promise about a return.
    """

    status: NavStatus
    currency: str
    value: Decimal | None = None
    reason_code: str | None = None
    detail: str = ""
    fx_snapshot_id: str | None = None

    @model_validator(mode="after")
    def _known_means_a_number(self) -> Valuation:
        if self.status == NavStatus.KNOWN and (self.value is None or self.reason_code is not None):
            raise ValueError("a KNOWN valuation carries a value and no reason code")
        if self.status == NavStatus.UNKNOWN and (self.value is not None or not self.reason_code):
            raise ValueError("an UNKNOWN valuation carries no value and must name a reason code")
        return self


class Position(StrictModel):
    instrument_id: str
    quantity: Decimal  # signed: negative = short
    average_price: Decimal = Field(ge=0)
    market_value: Decimal  # signed, in ``currency`` (the instrument's own currency)
    # Same value in the account base currency, converted from an FX snapshot; None when no trustworthy rate existed
    # (F-3). Exposure and concentration are measured on this field, never on a sum of mixed currencies.
    base_market_value: Decimal | None = None
    sector: str = "UNKNOWN"
    country: str = "UNKNOWN"
    currency: str = "USD"

    @property
    def base_value(self) -> Decimal:
        """Base-currency value; falls back to ``market_value`` only for a single-currency book (they are equal)."""
        return self.market_value if self.base_market_value is None else self.base_market_value


class OpenOrder(StrictModel):
    order_id: str
    instrument_id: str
    side: Side
    quantity: Decimal = Field(gt=0)
    notional: Decimal = Field(ge=0)  # in ``currency``
    currency: str = ""  # the instrument's currency; empty means "the account base currency" (single-currency book)
    submitted_at: datetime

    @field_validator("submitted_at")
    @classmethod
    def _tz(cls, v: datetime) -> datetime:
        return ensure_utc(v)


class KillSwitchFlags(StrictModel):
    """Kill Switch state applicable to this account at snapshot time [Source: 02, 05]."""

    platform: bool = False
    tenant: bool = False
    account: bool = False
    strategies: tuple[str, ...] = ()
    assets: tuple[str, ...] = ()
    venues: tuple[str, ...] = ()

    def any_active(self) -> bool:
        return self.platform or self.tenant or self.account or bool(self.strategies or self.assets or self.venues)


class AccountSnapshot(StrictModel):
    snapshot_id: str
    tenant_id: str
    account_id: str
    as_of: datetime
    mode: AccountMode
    trading_status: TradingStatus
    jurisdiction: str
    customer_type: str
    base_currency: str
    authorised_strategies: tuple[str, ...]
    cash: Decimal  # base-currency cash only; other currencies are in cash_by_currency
    cash_by_currency: dict[str, Decimal] = Field(default_factory=dict)
    buying_power: Decimal
    nav: Decimal  # base currency; ZERO and not a number when valuation.status is UNKNOWN (fail closed, F-3)
    valuation: Valuation | None = None  # None only for a book built before F-3; readers treat it as UNKNOWN
    peak_nav: Decimal
    daily_pnl: Decimal = Decimal("0")
    weekly_pnl: Decimal = Decimal("0")
    monthly_pnl: Decimal = Decimal("0")
    positions: tuple[Position, ...] = ()
    open_orders: tuple[OpenOrder, ...] = ()
    orders_last_minute: int = 0
    recent_intent_hashes: tuple[str, ...] = ()
    recent_order_signatures: tuple[str, ...] = ()  # instrument|side|type|qty|limit within the duplicate window
    kill_switch: KillSwitchFlags = KillSwitchFlags()
    emergency_policy: EmergencyPolicy = EmergencyPolicy.CANCEL_ONLY
    capital_envelope: Decimal | None = None
    capital_in_use: Decimal = Decimal("0")
    correlation_groups: dict[str, tuple[str, ...]] = Field(default_factory=dict)
    autonomy_suspended: bool = False  # SLO safety semantics [Committee C9 §3]
    liquidation_policy_ref: str | None = None  # [Open: O-08]

    @field_validator("as_of")
    @classmethod
    def _tz(cls, v: datetime) -> datetime:
        return ensure_utc(v)

    def position_for(self, instrument_id: str) -> Position | None:
        for p in self.positions:
            if p.instrument_id == instrument_id:
                return p
        return None

    @property
    def gross_exposure(self) -> Decimal:
        """Base currency: mixed-currency market values are never summed [F-3]."""
        return sum((abs(p.base_value) for p in self.positions), Decimal("0"))

    @property
    def net_exposure(self) -> Decimal:
        return sum((p.base_value for p in self.positions), Decimal("0"))
