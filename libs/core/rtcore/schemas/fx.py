"""FX snapshot — the third input of a cross-currency valuation and of the deterministic risk decision [Source: 05; F-3].

A snapshot is a point-in-time set of rates from one named source, with provenance, an as-of instant and an
identifier derived from its own content: an edited rate, an added pair or a forged id is refused when the snapshot
re-enters the schema boundary. The platform ingests snapshots through the bitemporal ``fx`` store only; no agent,
MCP tool or trade intent can supply or override a rate (analytics plane has no write path here, ADR-001).

Rate convention: the key ``A/B`` with rate ``r`` means one unit of A is r units of B. Rates are Decimal; a float
never enters. ``rtcore.money.convert`` is the only consumer that turns a snapshot into money.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import field_validator, model_validator

from rtcore.clock import ensure_utc
from rtcore.ids import deterministic_id
from rtcore.provenance import Provenance
from rtcore.schemas.base import StrictModel
from rtcore.world import is_currency

_ID_PREFIX = "fx"


def _content_id(base_currency: str, pairs: tuple[tuple[str, str], ...], as_of: datetime, source: str, provenance: str) -> str:
    """Identifier derived only from the content, so two ingests of the same rates collide instead of duplicating."""
    body = ";".join(f"{pair}={rate}" for pair, rate in sorted(pairs))
    return deterministic_id(_ID_PREFIX, base_currency, as_of.isoformat(), source, provenance, body)


class FxRate(StrictModel):
    """One quoted pair. ``pair`` is ``AAA/BBB`` (two distinct ISO 4217 codes); ``rate`` is a finite, positive Decimal."""

    pair: str
    rate: Decimal

    @field_validator("rate", mode="before")
    @classmethod
    def _decimal_only(cls, v: object) -> object:
        # A float is refused rather than coerced: binary rounding must never reach a valuation [NFR-DET-01].
        if isinstance(v, bool) or isinstance(v, float):
            raise ValueError("FX rates must be Decimal or a decimal string, never a float")
        return v

    @field_validator("rate")
    @classmethod
    def _finite_positive(cls, v: Decimal) -> Decimal:
        if not v.is_finite():
            raise ValueError("FX rate must be finite (NaN and Infinity are refused)")
        if v <= Decimal("0"):
            raise ValueError("FX rate must be greater than zero (a zero or negative rate is never a price)")
        return v

    @field_validator("pair")
    @classmethod
    def _iso_pair(cls, v: str) -> str:
        parts = v.split("/")
        if len(parts) != 2:
            raise ValueError(f"FX pair must be 'AAA/BBB': {v!r}")
        left, right = parts
        if not is_currency(left) or not is_currency(right):
            raise ValueError(f"FX pair must name two known ISO 4217 currencies (upper case, not XXX): {v!r}")
        if left == right:
            raise ValueError(f"FX pair must name two different currencies: {v!r}")
        return v


class FxSnapshot(StrictModel):
    snapshot_id: str
    base_currency: str
    rates: tuple[FxRate, ...]
    as_of: datetime
    source: str
    provenance: Provenance

    @field_validator("as_of")
    @classmethod
    def _tz(cls, v: datetime) -> datetime:
        return ensure_utc(v)

    @field_validator("base_currency")
    @classmethod
    def _base(cls, v: str) -> str:
        if not is_currency(v):
            raise ValueError(f"base currency must be a known ISO 4217 code (upper case, not XXX): {v!r}")
        return v

    @field_validator("source")
    @classmethod
    def _source(cls, v: str) -> str:
        if not v:
            raise ValueError("an FX snapshot must name its source (provenance is evidence, not decoration)")
        return v

    @model_validator(mode="after")
    def _content_bound(self) -> FxSnapshot:
        pairs = tuple((r.pair, str(r.rate)) for r in self.rates)
        if len({p for p, _ in pairs}) != len(pairs):
            raise ValueError("duplicate FX pair in one snapshot: the rate for a pair must be unambiguous")
        expected = _content_id(self.base_currency, pairs, self.as_of, self.source, self.provenance.value)
        if self.snapshot_id != expected:
            raise ValueError(f"snapshot_id does not match the snapshot content (expected {expected}, got {self.snapshot_id!r})")
        return self

    @classmethod
    def build(
        cls,
        *,
        base_currency: str,
        rates: dict[str, Decimal],
        as_of: datetime,
        source: str,
        provenance: Provenance,
    ) -> FxSnapshot:
        """Construct a snapshot and derive its id from its content. Every rule above still runs on the result."""
        base = str(base_currency).strip()
        src = str(source).strip()
        when = ensure_utc(as_of)
        prov = provenance.value if isinstance(provenance, Provenance) else str(provenance)
        pairs = tuple((str(pair).strip(), str(rate)) for pair, rate in rates.items())
        return cls(
            snapshot_id=_content_id(base, pairs, when, src, prov),
            base_currency=base,
            rates=tuple(FxRate(pair=pair, rate=rate) for pair, rate in rates.items()),
            as_of=when,
            source=src,
            provenance=provenance,
        )

    def rate_map(self) -> dict[str, Decimal]:
        return {r.pair: r.rate for r in self.rates}

    def audit_payload(self) -> dict[str, Any]:
        """What the audit row carries: identity and provenance, plus the pair names — never a promise about a price."""
        return {
            "snapshot_id": self.snapshot_id,
            "base_currency": self.base_currency,
            "as_of": self.as_of.isoformat(),
            "source": self.source,
            "provenance": self.provenance.value,
            "pairs": [r.pair for r in self.rates],
            "pair_count": len(self.rates),
        }
