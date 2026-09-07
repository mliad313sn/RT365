"""Plane topology guard [Source: 00, 03; ADR-001].

The authoritative pipeline is enforced by topology: Analytics plane -> Control plane (only via
the trade-intent queue) -> Execution plane -> Broker. In deployment this is a Kubernetes
network policy (infra/kubernetes/network-policies). In-process, the same rule is enforced by
``PlaneGuard`` so that unit and contract tests can prove the denial (TC-NET-001..004) and so a
single-process dev/sim build cannot accidentally wire an analytics component to execution.
"""

from __future__ import annotations

import contextvars
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from enum import Enum

from rtcore.errors import PlaneViolation


class Plane(str, Enum):
    EDGE = "edge"
    ANALYTICS = "analytics"
    CONTROL = "control"
    EXECUTION = "execution"
    BROKER = "broker"
    VAULT = "vault"


# (source, destination) -> allowed channels. Anything absent is denied.
ALLOWED_ROUTES: dict[tuple[Plane, Plane], frozenset[str]] = {
    (Plane.ANALYTICS, Plane.CONTROL): frozenset({"intent_queue"}),
    (Plane.CONTROL, Plane.EXECUTION): frozenset({"order_command", "cancel_command"}),
    (Plane.EXECUTION, Plane.BROKER): frozenset({"broker_adapter"}),
    (Plane.EXECUTION, Plane.CONTROL): frozenset({"events"}),
    (Plane.EXECUTION, Plane.VAULT): frozenset({"broker_credentials"}),
    (Plane.CONTROL, Plane.VAULT): frozenset({"signing_keys"}),
    (Plane.EDGE, Plane.CONTROL): frozenset({"api", "intent_queue"}),
    (Plane.EDGE, Plane.ANALYTICS): frozenset({"api"}),
    (Plane.EDGE, Plane.EXECUTION): frozenset({"api_read"}),
    (Plane.CONTROL, Plane.ANALYTICS): frozenset({"revocation", "events"}),
}

_current_plane: contextvars.ContextVar[Plane | None] = contextvars.ContextVar("rt_plane", default=None)


@dataclass(frozen=True)
class DenyEvent:
    source: Plane
    destination: Plane
    channel: str
    detail: str


@dataclass
class PlaneGuard:
    """Records every denied crossing; an alert hook receives S1 deny events (ALERT_CATALOG)."""

    denies: list[DenyEvent] = field(default_factory=list)
    alert_hook: Callable[[DenyEvent], object] | None = None

    def check(self, source: Plane, destination: Plane, channel: str) -> None:
        if source == destination:
            return
        allowed = ALLOWED_ROUTES.get((source, destination), frozenset())
        if channel not in allowed:
            event = DenyEvent(source, destination, channel, f"{source.value}->{destination.value}:{channel} denied")
            self.denies.append(event)
            if self.alert_hook is not None:
                self.alert_hook(event)
            raise PlaneViolation(event.detail)

    def check_caller(self, destination: Plane, channel: str) -> None:
        """Check the plane recorded in the current context against ``destination``."""
        source = _current_plane.get()
        if source is None:
            # Unattributed callers are treated as the least trusted plane. Fail closed.
            source = Plane.ANALYTICS
        self.check(source, destination, channel)


GUARD = PlaneGuard()


def current_plane() -> Plane | None:
    return _current_plane.get()


@contextmanager
def enter(plane: Plane) -> Iterator[None]:
    token = _current_plane.set(plane)
    try:
        yield
    finally:
        _current_plane.reset(token)
