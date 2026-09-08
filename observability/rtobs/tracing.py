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


# The only stages a correct run may legitimately never reach: a fail-closed refusal authorises no order, so no
# command is issued and no ack comes back. Every other stage runs on every path, so its absence is a defect [F-14].
CONDITIONAL_STAGES: tuple[str, ...] = ("order_command", "broker_ack")


@dataclass(frozen=True)
class TraceVerdict:
    """The completeness answer for exactly one correlation id — the id it was asked about and no other [F-14]."""

    correlation_id: str
    recorded: tuple[str, ...]
    missing: tuple[str, ...]
    failed: tuple[str, ...]
    not_reached: tuple[str, ...]
    complete: bool


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

    def failed(self, correlation_id: str) -> tuple[str, ...]:
        return tuple(s.name for s in self.spans if s.correlation_id == correlation_id and not s.ok)

    def missing(self, correlation_id: str, required: tuple[str, ...] = PIPELINE_STAGES) -> tuple[str, ...]:
        have = set(self.stages(correlation_id))
        return tuple(r for r in required if r not in have)

    def verdict(
        self, correlation_id: str, *, required: tuple[str, ...] = PIPELINE_STAGES, not_reached: tuple[str, ...] = ()
    ) -> TraceVerdict:
        """Completeness for **one** correlation id, always the id asked for [F-14, SRE-R10].

        ``not_reached`` is the caller's declaration that the pipeline stopped before those stages — a fail-closed
        rejection produces no order and therefore no ``order_command``/``broker_ack`` span, and that is not a defect.
        The declaration is accepted **only** for ``CONDITIONAL_STAGES`` and only while no later conditional stage
        ran: every other stage runs on every path, so declaring one "not reached" can never hide a hole, and a
        broker ack without an order command is still a hole. A span recorded ``ok=False`` is present and failed;
        it never counts as completeness.
        """
        have = self.stages(correlation_id)
        recorded = tuple(r for r in required if r in set(have))
        last_conditional = max((CONDITIONAL_STAGES.index(r) for r in recorded if r in CONDITIONAL_STAGES), default=-1)
        forgiven = tuple(
            r
            for r in required
            if r in set(not_reached)
            and r not in set(recorded)
            and r in CONDITIONAL_STAGES
            and CONDITIONAL_STAGES.index(r) > last_conditional
        )
        missing = tuple(r for r in required if r not in set(recorded) and r not in set(forgiven))
        failed = tuple(r for r in required if r in set(self.failed(correlation_id)))
        return TraceVerdict(
            correlation_id=correlation_id,
            recorded=recorded,
            missing=missing,
            failed=failed,
            not_reached=forgiven,
            complete=not missing and not failed,
        )
