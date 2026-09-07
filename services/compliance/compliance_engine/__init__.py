"""Compliance / Eligibility engine [Source: 07; C6]. Deterministic like the risk engine.

Protected path: 2nd-line CODEOWNER (Compliance Agent) approval required for changes.
"""

from compliance_engine.eligibility import ELIGIBILITY_BUILD_HASH, decide_eligibility
from compliance_engine.jurisdiction import JurisdictionRegistry
from compliance_engine.retention import LegalHold, RetentionSchedule, RetentionService
from compliance_engine.surveillance import SurveillanceAlert, screen_strategy_declaration, surveil

__all__ = [
    "decide_eligibility",
    "ELIGIBILITY_BUILD_HASH",
    "JurisdictionRegistry",
    "RetentionService",
    "RetentionSchedule",
    "LegalHold",
    "surveil",
    "SurveillanceAlert",
    "screen_strategy_declaration",
]
