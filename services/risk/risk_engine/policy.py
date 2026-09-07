"""Risk policy and limit hierarchy [Source: 05; RISK_POLICY.md, LIMIT_MATRIX.md].

Hierarchy platform > tenant > account > strategy > instrument; effective limit = minimum
across the levels that apply [Committee]. Limits change only via maker-checker with a cooling
period (identity_service.makerchecker); no agent/MCP write path exists [Source: 00].
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import Enum
from pathlib import Path
from typing import Any

import yaml
from pydantic import Field, field_validator
from rtcore.clock import ensure_utc
from rtcore.schemas.base import StrictModel


class LimitLevel(str, Enum):
    PLATFORM = "PLATFORM"
    TENANT = "TENANT"
    ACCOUNT = "ACCOUNT"
    STRATEGY = "STRATEGY"
    INSTRUMENT = "INSTRUMENT"


class Metric(str, Enum):
    MAX_NOTIONAL_PER_ORDER = "max_notional_per_order"
    MAX_POSITION_PER_INSTRUMENT = "max_position_per_instrument"
    GROSS_EXPOSURE_PCT_NAV = "gross_exposure_pct_nav"
    NET_EXPOSURE_PCT_NAV = "net_exposure_pct_nav"
    CONCENTRATION_SINGLE_NAME_PCT = "concentration_single_name_pct"
    CONCENTRATION_SECTOR_PCT = "concentration_sector_pct"
    CONCENTRATION_COUNTRY_PCT = "concentration_country_pct"
    CONCENTRATION_CURRENCY_PCT = "concentration_currency_pct"
    LEVERAGE_X = "leverage_x"
    DAILY_LOSS_LIMIT_PCT = "daily_loss_limit_pct"
    WEEKLY_LOSS_LIMIT_PCT = "weekly_loss_limit_pct"
    MONTHLY_LOSS_LIMIT_PCT = "monthly_loss_limit_pct"
    MAX_DRAWDOWN_PCT = "max_drawdown_pct"
    ORDERS_PER_MINUTE = "orders_per_minute"
    OPEN_ORDER_COUNT = "open_order_count"
    PRICE_COLLAR_PCT = "price_collar_pct"
    MAX_ORDER_PCT_ADV = "max_order_pct_adv"
    FRESHNESS_BUDGET_S = "freshness_budget_s"
    VOLATILITY_REGIME_PCT = "volatility_regime_pct"
    CORRELATED_GROUP_PCT_NAV = "correlated_group_pct_nav"


class Limit(StrictModel):
    level: LimitLevel
    scope_id: str  # "*" for platform; tenant/account/strategy/instrument id otherwise
    tenant_id: str | None = None  # STRATEGY/INSTRUMENT limits are tenant-qualified so they never leak across tenants (review P20)
    metric: Metric
    threshold: Decimal
    unit: str = ""
    version: str = "0"
    maker: str = ""
    checker: str = ""
    effective_from: datetime | None = None

    @field_validator("effective_from")
    @classmethod
    def _tz(cls, v: datetime | None) -> datetime | None:
        return None if v is None else ensure_utc(v)


class FailAction(str, Enum):
    REJECT = "REJECT"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"


class RiskPolicy(StrictModel):
    policy_version: str
    environment_tag: str  # dev | sim | shadow | paper | pilot | production
    approved_for_production: bool = False  # [Open: O-07] numeric thresholds per asset class/jurisdiction
    limits: tuple[Limit, ...]
    freshness_budget_s_by_asset_class: dict[str, Decimal] = Field(default_factory=dict)
    concentration_action: FailAction = FailAction.REJECT
    liquidity_action: FailAction = FailAction.REJECT
    protective_stop_required: bool = True
    protective_stop_action: FailAction = FailAction.REJECT
    allow_pre_open_limit_orders: bool = False
    risk_reducing_orders_exempt_exposure_caps: bool = True  # [Committee] proposal to the Trading Risk Committee (review P4)
    max_protective_stop_distance_pct: Decimal = Decimal("10")  # [Open: O-07]
    account_snapshot_max_age_s: Decimal = Decimal("5")  # [Open: O-03]
    approved_liquidation_policies: tuple[str, ...] = ()  # [Open: O-08] empty = reduce/flatten fall back to CANCEL_ONLY
    complex_asset_classes: tuple[str, ...] = ("OPTION", "FUTURE", "CRYPTO")
    maker: str = ""
    checker: str = ""
    cooling_period_end: datetime | None = None

    @field_validator("cooling_period_end")
    @classmethod
    def _tz(cls, v: datetime | None) -> datetime | None:
        return None if v is None else ensure_utc(v)

    def limits_for(self, metric: Metric) -> tuple[Limit, ...]:
        return tuple(limit for limit in self.limits if limit.metric == metric)


class LimitScope(StrictModel):
    tenant_id: str
    account_id: str
    strategy_id: str
    instrument_id: str

    def id_for(self, level: LimitLevel) -> str:
        return {
            LimitLevel.PLATFORM: "*",
            LimitLevel.TENANT: self.tenant_id,
            LimitLevel.ACCOUNT: self.account_id,
            LimitLevel.STRATEGY: self.strategy_id,
            LimitLevel.INSTRUMENT: self.instrument_id,
        }[level]


class EffectiveLimit(StrictModel):
    metric: Metric
    threshold: Decimal | None
    source_level: LimitLevel | None
    considered: tuple[Limit, ...]


def effective_limit(policy: RiskPolicy, metric: Metric, scope: LimitScope, as_of: datetime | None = None) -> EffectiveLimit:
    """Effective = min over applicable levels [Committee]. None when no level defines the metric."""
    applicable: list[Limit] = []
    for limit in policy.limits_for(metric):
        if limit.scope_id != scope.id_for(limit.level):
            continue
        if limit.tenant_id is not None and limit.tenant_id != scope.tenant_id:
            continue
        if limit.level in (LimitLevel.STRATEGY, LimitLevel.INSTRUMENT) and limit.tenant_id is None and scope.tenant_id != "*":
            # tenant-qualification is mandatory below the tenant level; unqualified strategy/instrument limits are ignored
            continue
        if as_of is not None and limit.effective_from is not None and limit.effective_from > as_of:
            continue
        applicable.append(limit)
    if not applicable:
        return EffectiveLimit(metric=metric, threshold=None, source_level=None, considered=())
    best = min(applicable, key=lambda lim: (lim.threshold, list(LimitLevel).index(lim.level)))
    return EffectiveLimit(metric=metric, threshold=best.threshold, source_level=best.level, considered=tuple(applicable))


def _coerce(raw: dict[str, Any]) -> dict[str, Any]:
    data = dict(raw)
    data["limits"] = tuple(
        Limit(
            level=LimitLevel(item["level"]),
            scope_id=str(item.get("scope_id", "*")),
            metric=Metric(item["metric"]),
            threshold=Decimal(str(item["threshold"])),
            tenant_id=item.get("tenant_id"),
            unit=str(item.get("unit", "")),
            version=str(item.get("version", "0")),
            maker=str(item.get("maker", "")),
            checker=str(item.get("checker", "")),
            effective_from=item.get("effective_from"),
        )
        for item in raw.get("limits", [])
    )
    data["freshness_budget_s_by_asset_class"] = {k: Decimal(str(v)) for k, v in raw.get("freshness_budget_s_by_asset_class", {}).items()}
    return data


def load_policy(path: Path) -> RiskPolicy:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    return RiskPolicy.model_validate(_coerce(raw))


def policy_from_dict(raw: dict[str, Any]) -> RiskPolicy:
    return RiskPolicy.model_validate(_coerce(raw))


def apply_limit_change(
    policy: RiskPolicy,
    *,
    level: str,
    scope_id: str,
    metric: str,
    threshold: Decimal,
    tenant_id: str | None,
    maker: str,
    checker: str,
    change_id: str,
    effective_from: datetime,
) -> RiskPolicy:
    """Produce the successor policy version from an EFFECTIVE maker-checker change (identity_service.makerchecker).

    This is the only supported write path to limits: no agent, MCP server or strategy can call it with an
    effective change, because effective changes exist only after a human maker and a different-line checker.
    """
    new_limit = Limit(
        level=LimitLevel(level),
        scope_id=scope_id,
        metric=Metric(metric),
        threshold=threshold,
        tenant_id=tenant_id,
        version=change_id,
        maker=maker,
        checker=checker,
        effective_from=effective_from,
    )
    remaining = tuple(
        lim
        for lim in policy.limits
        if not (
            lim.level == new_limit.level
            and lim.scope_id == new_limit.scope_id
            and lim.metric == new_limit.metric
            and lim.tenant_id == new_limit.tenant_id
        )
    )
    return policy.model_copy(
        update={
            "limits": (*remaining, new_limit),
            "policy_version": f"{policy.policy_version.split('+')[0]}+{change_id[-8:]}",
            "maker": maker,
            "checker": checker,
        }
    )
