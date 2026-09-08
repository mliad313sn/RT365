"""Eligibility engine inputs/outputs [Source: 07; Committee C6 §2]."""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import Field, field_validator

from rtcore.clock import ensure_utc
from rtcore.schemas.base import StrictModel
from rtcore.schemas.decision import EvaluatedCheck


class CustomerType(str, Enum):
    RETAIL = "RETAIL"
    PROFESSIONAL = "PROFESSIONAL"
    ELIGIBLE_COUNTERPARTY = "ELIGIBLE_COUNTERPARTY"
    INSTITUTIONAL = "INSTITUTIONAL"


class EligibilityOutcome(str, Enum):
    ELIGIBLE = "ELIGIBLE"
    INELIGIBLE = "INELIGIBLE"


class CustomerProfile(StrictModel):
    customer_id: str
    tenant_id: str
    customer_type: CustomerType
    jurisdiction: str  # ISO country
    product_permissions: tuple[str, ...]  # asset classes the customer may trade
    appropriateness_assessed: bool = False
    complex_products_allowed: bool = False
    short_selling_allowed: bool = False


class JurisdictionCell(StrictModel):
    """One row of COMPLIANCE_MATRIX. Live only with legal record AND technical flag by different persons."""

    country: str  # ISO 3166-1 alpha-2 (rtcore.world) or a user-assigned code, which marks the cell simulated (D-050)
    customer_type: CustomerType
    broker: str
    venue: str
    asset_class: str
    feature: str  # operating mode: PAPER | SUPERVISED | BOUNDED_AUTONOMOUS
    simulated: bool = False  # user-assigned country code: exercisable in sim, never a legal basis
    legal_record_ref: str | None = None
    legal_signed_by: str | None = None
    technical_flag: bool = False
    flag_activated_by: str | None = None
    activated_at: datetime | None = None

    @field_validator("activated_at")
    @classmethod
    def _tz(cls, v: datetime | None) -> datetime | None:
        return None if v is None else ensure_utc(v)

    @property
    def key(self) -> tuple[str, str, str, str, str, str]:
        return (self.country, self.customer_type.value, self.broker, self.venue, self.asset_class, self.feature)

    def dual_key_satisfied(self) -> bool:
        return (
            bool(self.legal_record_ref)
            and bool(self.legal_signed_by)
            and self.technical_flag
            and bool(self.flag_activated_by)
            and self.flag_activated_by != self.legal_signed_by
        )


class RestrictedLists(StrictModel):
    policy_version: str
    restricted_instruments: tuple[str, ...] = ()
    restricted_issuers: tuple[str, ...] = ()
    restricted_venues: tuple[str, ...] = ()
    short_sale_banned_instruments: tuple[str, ...] = ()
    whitelist_instruments: tuple[str, ...] | None = None  # None = no whitelist in force
    surveillance_watch: tuple[str, ...] = Field(default_factory=tuple)


class EligibilityDecision(StrictModel):
    decision_id: str
    intent_id: str
    outcome: EligibilityOutcome
    policy_version: str
    reason_codes: tuple[str, ...]
    evaluated: tuple[EvaluatedCheck, ...]
    decided_at: datetime
    engine_build_hash: str
    correlation_id: str
    intent_hash: str

    @field_validator("decided_at")
    @classmethod
    def _tz(cls, v: datetime) -> datetime:
        return ensure_utc(v)
