"""Eligibility engine inputs/outputs [Source: 07; Committee C6 §2].

Council 2026-09-08 (compliance_legal P-2..P-4; product_director §4.4; D-045): the legal half of the dual key is a typed,
hashed reference; the customer profile carries disclosure acknowledgement, per-mode consent and classification evidence
so that eligibility can refuse at decision time. The shape of a legal record is a data-integrity control, not legal advice;
nothing here asserts a regulatory position [Open: H-04, Q-J06, Q-P03, Q-P04].
"""

from __future__ import annotations

import re
from datetime import date, datetime
from enum import Enum

from pydantic import Field, field_validator, model_validator

from rtcore.clock import ensure_utc
from rtcore.schemas.base import StrictModel
from rtcore.schemas.decision import EvaluatedCheck
from rtcore.world import is_user_assigned, is_valid_country

SIMULATED_RECORD_PREFIX = "SIM-"  # a legal record whose id starts with SIM- is a fixture: valid only on a simulated cell (D-012)
_RECORD_ID = re.compile(r"^[A-Z0-9][A-Z0-9._-]{2,63}$")
_SHA256_HEX = re.compile(r"^[0-9a-f]{64}$")
CONSENTABLE_MODES: frozenset[str] = frozenset({"PAPER", "SUPERVISED", "BOUNDED_AUTONOMOUS"})  # order-placing modes
CONSENT_REQUIRED_MODES: frozenset[str] = frozenset({"SUPERVISED", "BOUNDED_AUTONOMOUS"})  # explicit recorded consent per mode [Open: Q-P04]


class CustomerType(str, Enum):
    RETAIL = "RETAIL"
    PROFESSIONAL = "PROFESSIONAL"
    ELIGIBLE_COUNTERPARTY = "ELIGIBLE_COUNTERPARTY"
    INSTITUTIONAL = "INSTITUTIONAL"


class EligibilityOutcome(str, Enum):
    ELIGIBLE = "ELIGIBLE"
    INELIGIBLE = "INELIGIBLE"


class ClassificationBasis(str, Enum):
    """How a CustomerType was established. SELF_DECLARED exists so that it can be recorded and refused explicitly (D-045:
    customer type is never self-declared); which of the other bases counts in a given cell is a counsel question [Open: Q-P03]."""

    ASSESSOR_REVIEW = "ASSESSOR_REVIEW"  # a named human assessor reviewed the classification criteria
    DOCUMENTARY_EVIDENCE = "DOCUMENTARY_EVIDENCE"  # a document (e.g. regulatory register entry) supports the classification
    SELF_DECLARED = "SELF_DECLARED"  # the customer asserted it; never accepted by the engine


class DisclosureAcknowledgement(StrictModel):
    """The customer acknowledged the disclosure pack of a given version at a given time [Open: H-16 approved wording per cell]."""

    version: str = Field(min_length=1)
    acknowledged_at: datetime

    @field_validator("acknowledged_at")
    @classmethod
    def _tz(cls, v: datetime) -> datetime:
        return ensure_utc(v)


class ModeConsent(StrictModel):
    """Recorded consent to operate an account in one order-placing mode; one record per mode, never transitive."""

    mode: str
    consented_at: datetime
    consent_ref: str | None = None  # where the recorded consent lives (document / ticket); not verified here [Open]

    @field_validator("mode")
    @classmethod
    def _mode(cls, v: str) -> str:
        if v not in CONSENTABLE_MODES:
            raise ValueError(f"consent is only meaningful for an order-placing mode, not {v!r}")
        return v

    @field_validator("consented_at")
    @classmethod
    def _tz(cls, v: datetime) -> datetime:
        return ensure_utc(v)


class ClassificationEvidence(StrictModel):
    """Reference to how the CustomerType was established: by whom, when, on what basis. The assessor is never the customer."""

    evidence_ref: str = Field(min_length=1)
    assessed_by: str = Field(min_length=1)  # human assessor / entity of record; compared against customer_id by the engine
    assessed_at: datetime
    basis: ClassificationBasis

    @field_validator("assessed_at")
    @classmethod
    def _tz(cls, v: datetime) -> datetime:
        return ensure_utc(v)


class CustomerProfile(StrictModel):
    customer_id: str
    tenant_id: str
    customer_type: CustomerType
    jurisdiction: str  # ISO country
    product_permissions: tuple[str, ...]  # asset classes the customer may trade
    appropriateness_assessed: bool = False
    complex_products_allowed: bool = False
    short_selling_allowed: bool = False
    disclosure_acknowledgement: DisclosureAcknowledgement | None = None  # None: nothing acknowledged (CP-DISCL)
    mode_consents: tuple[ModeConsent, ...] = ()  # modes the customer consented to; SUPERVISED/BOUNDED need one (CP-MODE-CONSENT)
    classification_evidence: ClassificationEvidence | None = None  # None or self-declared: CP-CLASS


class LegalRecordRef(StrictModel):
    """Typed reference to a stored legal record: id, signing counsel/entity, signature date and document hash (council P-2, O-71).

    Shape only: the engine can tell a fabricated string from a reference to a document that exists and can be hashed; it does
    not read the document and asserts nothing about its content. A record id prefixed SIM- is a fixture for a simulated cell.
    """

    record_id: str
    signing_entity: str = Field(min_length=2)  # counsel of record / signing legal entity, as written on the document
    signed_on: date
    document_sha256: str

    @field_validator("record_id")
    @classmethod
    def _record_id(cls, v: str) -> str:
        if not _RECORD_ID.match(v):
            raise ValueError("legal record id must be 3-64 upper-case letters, digits, '.', '_' or '-'")
        return v

    @field_validator("signing_entity")
    @classmethod
    def _entity(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("signing entity must be named")
        return v

    @field_validator("document_sha256")
    @classmethod
    def _sha(cls, v: str) -> str:
        if not _SHA256_HEX.match(v):
            raise ValueError("document hash must be 64 lower-case hex characters (SHA-256)")
        return v

    @property
    def simulated(self) -> bool:
        return self.record_id.startswith(SIMULATED_RECORD_PREFIX)

    def short(self) -> str:
        return f"{self.record_id}@{self.document_sha256[:12]}"


class JurisdictionCell(StrictModel):
    """One row of COMPLIANCE_MATRIX. Live only with legal record AND technical flag by different persons."""

    country: str  # ISO 3166-1 alpha-2 (rtcore.world) or a user-assigned code, which marks the cell simulated (D-050)
    customer_type: CustomerType
    broker: str
    venue: str
    asset_class: str
    feature: str  # operating mode: PAPER | SUPERVISED | BOUNDED_AUTONOMOUS
    simulated: bool = False  # user-assigned country code: exercisable in sim, never a legal basis
    legal_record_ref: LegalRecordRef | None = None
    legal_signed_by: str | None = None
    technical_flag: bool = False
    flag_activated_by: str | None = None
    activated_at: datetime | None = None
    required_disclosure_version: str | None = None  # disclosure pack version customers must have acknowledged [Open: H-16]

    @field_validator("activated_at")
    @classmethod
    def _tz(cls, v: datetime | None) -> datetime | None:
        return None if v is None else ensure_utc(v)

    @model_validator(mode="after")
    def _labels_are_truthful(self) -> JurisdictionCell:
        # The simulated label cannot be forged: a user-assigned code is always simulated, an ISO country never (D-012, D-050).
        if is_valid_country(self.country):  # registry first: XK (Kosovo) is a registry row spelled with a user-assigned code
            if self.simulated:
                raise ValueError(f"{self.country!r} is an ISO 3166-1 country: the cell cannot be labelled simulated")
        elif is_user_assigned(self.country) and not self.simulated:
            raise ValueError(f"{self.country!r} is a user-assigned code: the cell must be labelled simulated")
        # A SIM- legal record belongs only on a simulated cell, and a simulated cell carries only SIM- records (council X-6).
        if self.legal_record_ref is not None and self.legal_record_ref.simulated != self.simulated:
            raise ValueError("legal record label mismatch: SIM- records only on simulated cells, and only SIM- records there")
        return self

    @property
    def key(self) -> tuple[str, str, str, str, str, str]:
        return (self.country, self.customer_type.value, self.broker, self.venue, self.asset_class, self.feature)

    @property
    def correlation_id(self) -> str:
        """Deterministic correlation for every audit row about this cell (proposal, legal record, flag changes)."""
        return "jurisdiction:" + "/".join(self.key)

    def dual_key_satisfied(self) -> bool:
        return (
            self.legal_record_ref is not None
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
