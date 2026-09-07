"""Decimal helpers. Quantities and prices are Decimal end to end; floats never enter a decision."""

from __future__ import annotations

from decimal import ROUND_DOWN, ROUND_HALF_EVEN, Decimal, InvalidOperation

ZERO = Decimal("0")
ONE = Decimal("1")


def D(value: object) -> Decimal:  # noqa: N802 - conventional short constructor
    if isinstance(value, Decimal):
        return value
    if isinstance(value, float):
        # floats are converted through repr to avoid binary artefacts; callers should prefer str
        return Decimal(repr(value))
    try:
        return Decimal(str(value))
    except InvalidOperation as exc:  # pragma: no cover - defensive
        raise ValueError(f"not a decimal: {value!r}") from exc


def quantize(value: Decimal, step: Decimal, rounding: str = ROUND_HALF_EVEN) -> Decimal:
    if step <= ZERO:
        return value
    return (value / step).quantize(ONE, rounding=rounding) * step


def round_down_to_lot(quantity: Decimal, lot: Decimal) -> Decimal:
    return quantize(quantity, lot, ROUND_DOWN)


def pct(part: Decimal, whole: Decimal) -> Decimal:
    if whole == ZERO:
        return Decimal("Infinity") if part != ZERO else ZERO
    return (part / whole) * Decimal("100")
