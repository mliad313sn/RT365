from __future__ import annotations

from enum import Enum
from pathlib import Path

import yaml
from rtcore.schemas.base import StrictModel


class SafetyAction(str, Enum):
    NONE = "none"
    SUSPEND_AUTONOMY = "suspend_autonomy"
    CANCEL_ONLY_REVIEW = "cancel_only_review"
    FAIL_CLOSED = "fail_closed"
    SUPERVISED_ON_BREAK = "supervised_on_break"


class Direction(str, Enum):
    """Which way a breach lies. Declared per SLI, never inferred from the name [F-07, SRE-R2]."""

    HIGHER_IS_WORSE = "higher_is_worse"
    LOWER_IS_WORSE = "lower_is_worse"


class Sli(StrictModel):
    name: str
    definition: str
    measurement_point: str  # the component the SLI belongs to (design intent)
    emission_point: str  # where a measurement is actually emitted in this tree, or the literal "none" [F-03]
    metrics: tuple[str, ...]  # the metric names emitted at that point; empty when there is no emission point
    direction: Direction  # required: a safety direction is a safety property, so it is declared, not guessed
    target: float | None
    safety_semantic: str
    gap: str | None  # what is missing when there is no emission point, or what the emission does not yet cover


class SliCatalog:
    def __init__(self, slis: tuple[Sli, ...]) -> None:
        self._slis = {s.name: s for s in slis}

    @classmethod
    def load(cls, path: Path) -> SliCatalog:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        return cls(tuple(Sli.model_validate(item) for item in data["slis"]))

    def names(self) -> tuple[str, ...]:
        return tuple(self._slis)

    def get(self, name: str) -> Sli:
        return self._slis[name]

    def emitting(self) -> tuple[str, ...]:
        """SLIs with an emission point in this tree today; the rest cannot be baselined by running the system [F-03]."""
        return tuple(n for n, s in self._slis.items() if s.emission_point != "none")

    def without_emission(self) -> tuple[str, ...]:
        return tuple(n for n, s in self._slis.items() if s.emission_point == "none")

    def evaluate(self, name: str, value: float) -> SafetyAction:
        """Returns the safety action when a *set* target is breached; targets are None until O-03 closes.

        The breach direction is the SLI's declared ``direction`` — never inferred from its name (F-07): a
        name-inferred direction judged ``alert_delivery_s`` and ``time_to_halt_s`` inverted, so a fast halt
        would have breached and a slow one would not.
        """
        sli = self._slis[name]
        if sli.target is None:
            return SafetyAction.NONE
        breached = value > sli.target if sli.direction is Direction.HIGHER_IS_WORSE else value < sli.target
        if not breached:
            return SafetyAction.NONE
        mapping = {
            "suspend_autonomy": SafetyAction.SUSPEND_AUTONOMY,
            "cancel_only_review": SafetyAction.CANCEL_ONLY_REVIEW,
            "fail_closed": SafetyAction.FAIL_CLOSED,
            "supervised_on_break": SafetyAction.SUPERVISED_ON_BREAK,
        }
        return mapping.get(sli.safety_semantic, SafetyAction.NONE)
