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


class Sli(StrictModel):
    name: str
    definition: str
    measurement_point: str
    target: float | None
    safety_semantic: str


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

    def evaluate(self, name: str, value: float) -> SafetyAction:
        """Returns the safety action when a *set* target is breached; targets are None until O-03 closes."""
        sli = self._slis[name]
        if sli.target is None:
            return SafetyAction.NONE
        breached = value > sli.target if "latency" in name or "freshness" in name or "lag" in name else value < sli.target
        if not breached:
            return SafetyAction.NONE
        mapping = {
            "suspend_autonomy": SafetyAction.SUSPEND_AUTONOMY,
            "cancel_only_review": SafetyAction.CANCEL_ONLY_REVIEW,
            "fail_closed": SafetyAction.FAIL_CLOSED,
            "supervised_on_break": SafetyAction.SUPERVISED_ON_BREAK,
        }
        return mapping.get(sli.safety_semantic, SafetyAction.NONE)
