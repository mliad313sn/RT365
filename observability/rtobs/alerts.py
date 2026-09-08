from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml
from rtcore.ids import new_id


def _now() -> datetime:
    return datetime.now(tz=UTC)


@dataclass(frozen=True)
class Alert:
    name: str
    severity: str
    auto_action: str
    payload: dict[str, Any]
    alert_id: str = ""  # assigned by the router; the join key between an alert, its deliveries and its acknowledgement
    raised_at: datetime | None = None  # the first end of alert_delivery_s [SRE-R5]; None only for a hand-built alert


@dataclass
class Delivery:
    """One alert on one channel: raised -> dispatched -> (later, if ever) acknowledged by an operator [SRE-R5].

    ``delivery_s`` is the SLI ``alert_delivery_s`` and stays ``None`` until an acknowledgement exists. An
    unacknowledged alert has no delivery time; it is never recorded as zero, because a missing measurement
    read as zero is a measurement in the safe-looking direction.
    """

    alert_id: str
    alert_name: str
    channel: str
    raised_at: datetime
    delivered_at: datetime
    dispatch_s: float
    acknowledged_at: datetime | None = None
    acknowledged_by: str | None = None
    delivery_s: float | None = None


@dataclass
class AlertRouter:
    catalog: dict[str, dict[str, str]]
    actions: dict[str, Callable[[Alert], object]] = field(default_factory=dict)
    required_keys: dict[str, tuple[str, ...]] = field(default_factory=dict)
    fired: list[Alert] = field(default_factory=list)
    delivered: list[tuple[str, Alert]] = field(default_factory=list)
    deliveries: list[Delivery] = field(default_factory=list)
    channels: list[str] = field(default_factory=lambda: ["pager", "email"])
    clock: Callable[[], datetime] = _now  # wall clock: an acknowledgement may arrive long after the process that raised it
    observe: Callable[[str, float], object] = lambda name, value: None

    @classmethod
    def load(cls, path: Path) -> AlertRouter:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        return cls(catalog={a["name"]: a for a in data["alerts"]})

    def on(self, auto_action: str, fn: Callable[[Alert], object], *, required: tuple[str, ...] = ()) -> None:
        """Bind an auto-action; ``required`` payload keys make a silent no-op impossible (MCP review OBJ-3b)."""
        self.actions[auto_action] = fn
        self.required_keys[auto_action] = required

    def _dispatch(self, alert: Alert) -> None:
        """Fan the alert out to every channel and record when each copy left, so alert_delivery_s has a first end."""
        started = time.perf_counter()
        raised = alert.raised_at or self.clock()
        for ch in self.channels:
            self.delivered.append((ch, alert))
            elapsed = time.perf_counter() - started
            self.deliveries.append(
                Delivery(
                    alert_id=alert.alert_id,
                    alert_name=alert.name,
                    channel=ch,
                    raised_at=raised,
                    delivered_at=self.clock(),
                    dispatch_s=elapsed,
                )
            )
            self.observe("alerts.alert_dispatch_s", elapsed)

    def raise_alert(self, name: str, payload: dict[str, Any]) -> Alert:
        spec = self.catalog.get(name, {"severity": "S2", "auto_action": "none"})
        alert = Alert(
            name=name,
            severity=str(spec.get("severity", "S2")),
            auto_action=str(spec.get("auto_action", "none")),
            payload=payload,
            alert_id=new_id("alert"),
            raised_at=self.clock(),
        )
        self.fired.append(alert)
        self._dispatch(alert)
        fn = self.actions.get(alert.auto_action)
        if alert.auto_action != "none":
            missing = [k for k in self.required_keys.get(alert.auto_action, ()) if payload.get(k) in (None, "")]
            if fn is None or missing:
                failed = Alert(
                    name="alert.autoaction_failed",
                    severity="S1",
                    auto_action="none",
                    payload={"alert": name, "auto_action": alert.auto_action, "missing": missing, "unbound": fn is None},
                    alert_id=new_id("alert"),
                    raised_at=self.clock(),
                )
                self.fired.append(failed)
                self._dispatch(failed)
                return alert
            fn(alert)
        return alert

    def acknowledge(self, alert_id: str, *, by: str, at: datetime | None = None) -> Delivery:
        """Record an operator acknowledgement — the second end of ``alert_delivery_s`` [SRE-R5].

        An acknowledgement for an alert that was never raised is refused (``KeyError``): a delivery time can
        never be manufactured without the raise it is measured from. The first acknowledgement stands; a second
        one neither rewrites the recorded time nor re-observes the metric.
        """
        rows = [d for d in self.deliveries if d.alert_id == alert_id]
        if not rows:
            raise KeyError(f"no alert {alert_id} was raised; nothing to acknowledge")
        acked = [d for d in rows if d.acknowledged_at is not None]
        if acked:
            return acked[0]
        when = at or self.clock()
        for d in rows:
            d.acknowledged_at = when
            d.acknowledged_by = by
            d.delivery_s = max(0.0, (when - d.raised_at).total_seconds())
        self.observe("alerts.alert_delivery_s", rows[0].delivery_s or 0.0)
        return rows[0]

    def unacknowledged(self) -> tuple[Alert, ...]:
        """Alerts with no acknowledgement recorded — the operational half of the SLI, visible before any target exists."""
        open_ids = {d.alert_id for d in self.deliveries if d.acknowledged_at is None}
        return tuple(a for a in self.fired if a.alert_id in open_ids)

    def by_name(self, name: str) -> tuple[Alert, ...]:
        return tuple(a for a in self.fired if a.name == name)
