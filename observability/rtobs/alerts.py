from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class Alert:
    name: str
    severity: str
    auto_action: str
    payload: dict[str, Any]


@dataclass
class AlertRouter:
    catalog: dict[str, dict[str, str]]
    actions: dict[str, Callable[[Alert], object]] = field(default_factory=dict)
    required_keys: dict[str, tuple[str, ...]] = field(default_factory=dict)
    fired: list[Alert] = field(default_factory=list)
    delivered: list[tuple[str, Alert]] = field(default_factory=list)
    channels: list[str] = field(default_factory=lambda: ["pager", "email"])

    @classmethod
    def load(cls, path: Path) -> AlertRouter:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        return cls(catalog={a["name"]: a for a in data["alerts"]})

    def on(self, auto_action: str, fn: Callable[[Alert], object], *, required: tuple[str, ...] = ()) -> None:
        """Bind an auto-action; ``required`` payload keys make a silent no-op impossible (MCP review OBJ-3b)."""
        self.actions[auto_action] = fn
        self.required_keys[auto_action] = required

    def raise_alert(self, name: str, payload: dict[str, Any]) -> Alert:
        spec = self.catalog.get(name, {"severity": "S2", "auto_action": "none"})
        alert = Alert(
            name=name, severity=str(spec.get("severity", "S2")), auto_action=str(spec.get("auto_action", "none")), payload=payload
        )
        self.fired.append(alert)
        for ch in self.channels:
            self.delivered.append((ch, alert))
        fn = self.actions.get(alert.auto_action)
        if alert.auto_action != "none":
            missing = [k for k in self.required_keys.get(alert.auto_action, ()) if payload.get(k) in (None, "")]
            if fn is None or missing:
                failed = Alert(
                    name="alert.autoaction_failed",
                    severity="S1",
                    auto_action="none",
                    payload={"alert": name, "auto_action": alert.auto_action, "missing": missing, "unbound": fn is None},
                )
                self.fired.append(failed)
                for ch in self.channels:
                    self.delivered.append((ch, failed))
                return alert
            fn(alert)
        return alert

    def by_name(self, name: str) -> tuple[Alert, ...]:
        return tuple(a for a in self.fired if a.name == name)
