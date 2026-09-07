from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field


def _key(name: str, labels: dict[str, str] | None) -> str:
    if not labels:
        return name
    return name + "{" + ",".join(f"{k}={v}" for k, v in sorted(labels.items())) + "}"


@dataclass
class MetricsRegistry:
    counters: dict[str, float] = field(default_factory=lambda: defaultdict(float))
    histograms: dict[str, list[float]] = field(default_factory=lambda: defaultdict(list))

    def inc(self, name: str, value: float = 1.0, **labels: str) -> None:
        self.counters[_key(name, labels)] += value

    def observe(self, name: str, value: float, **labels: str) -> None:
        self.histograms[_key(name, labels)].append(value)

    def get(self, name: str, **labels: str) -> float:
        return self.counters.get(_key(name, labels), 0.0)

    def percentile(self, name: str, p: float, **labels: str) -> float | None:
        values = sorted(self.histograms.get(_key(name, labels), []))
        if not values:
            return None
        idx = min(len(values) - 1, max(0, int(round(p / 100 * (len(values) - 1)))))
        return values[idx]

    def snapshot(self) -> dict[str, object]:
        return {
            "counters": dict(self.counters),
            "histograms": {
                k: {"count": len(v), "p50": self.percentile_raw(v, 50), "p99": self.percentile_raw(v, 99)}
                for k, v in self.histograms.items()
            },
        }

    @staticmethod
    def percentile_raw(values: list[float], p: float) -> float | None:
        if not values:
            return None
        s = sorted(values)
        return s[min(len(s) - 1, max(0, int(round(p / 100 * (len(s) - 1)))))]
