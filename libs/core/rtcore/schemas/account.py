"""Account snapshot — the second input of the deterministic risk decision [Source: 05]."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import Field, field_validator

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


class Position(StrictModel):
    instrument_id: str
    quantity: Decimal  # signed: negative = short
    average_price: Decimal = Field(ge=0)
    market_value: Decimal  # signed
    sector: str = "UNKNOWN"
    country: str = "UNKNOWN"
    currency: str = "USD"


class OpenOrder(StrictModel):
    order_id: str
    instrument_id: str
    side: Side
    quantity: Decimal = Field(gt=0)
    notional: Decimal = Field(ge=0)
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
    cash: Decimal
    buying_power: Decimal
    nav: Decimal
    peak_nav: Decimal
    daily_pnl: Decimal = Decimal("0")
    weekly_pnl: Decimal = Decimal("0")
    monthly_pnl: Decimal = Decimal("0")
    positions: tuple[Position, ...] = ()
    open_orders: tuple[OpenOrder, ...] = ()
    orders_last_minute: int = 0
    recent_intent_hashes: tuple[str, ...] = ()
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
        return sum((abs(p.market_value) for p in self.positions), Decimal("0"))

    @property
    def net_exposure(self) -> Decimal:
        return sum((p.market_value for p in self.positions), Decimal("0"))
