"""Minimal tracer: one span per pipeline stage, keyed by correlation ID; completeness check = missing span -> defect."""

from __future__ import annotations

import time
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Span:
    correlation_id: str
    name: str
    started: float
    ended: float
    ok: bool


PIPELINE_STAGES: tuple[str, ...] = ("market_snapshot", "signal", "intent", "eligibility", "risk", "order_command", "broker_ack", "audit")


@dataclass
class Tracer:
    spans: list[Span] = field(default_factory=list)

    @contextmanager
    def span(self, name: str, correlation_id: str) -> Iterator[None]:
        started = time.perf_counter()
        ok = True
        try:
            yield
        except Exception:
            ok = False
            raise
        finally:
            self.spans.append(Span(correlation_id, name, started, time.perf_counter(), ok))

    def record(self, name: str, correlation_id: str, ok: bool = True) -> None:
        now = time.perf_counter()
        self.spans.append(Span(correlation_id, name, now, now, ok))

    def stages(self, correlation_id: str) -> tuple[str, ...]:
        return tuple(s.name for s in self.spans if s.correlation_id == correlation_id)

    def missing(self, correlation_id: str, required: tuple[str, ...] = PIPELINE_STAGES) -> tuple[str, ...]:
        have = set(self.stages(correlation_id))
        return tuple(r for r in required if r not in have)
