"""Decimal helpers and the pure FX conversion. Quantities, prices and rates are Decimal end to end; floats never
enter a decision, and a missing rate is an error rather than a silent 1.0 [Source: 02 FR-05; F-3]."""

from __future__ import annotations

from datetime import datetime
from decimal import ROUND_DOWN, ROUND_HALF_EVEN, Decimal, InvalidOperation
from typing import TYPE_CHECKING

from rtcore.clock import age_seconds_decimal
from rtcore.errors import FxBudgetUndefined, FxPairUnknown, FxSnapshotMissing, FxSnapshotStale
from rtcore.world import currency_minor_units, is_currency

if TYPE_CHECKING:  # pragma: no cover - import cycle: the schema validates itself with the helpers below
    from rtcore.schemas.fx import FxSnapshot

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


# --- currencies and FX ------------------------------------------------------------------------------------------
def is_iso4217(code: object) -> bool:
    """True only for an exact upper-case ISO 4217 code the platform knows. ``XXX`` is "no currency" and is False."""
    return isinstance(code, str) and is_currency(code)


def minor_units(currency: str) -> int:
    """ISO 4217 exponent for ``currency`` (JPY 0, USD 2, KWD 3, CLF 4); raises for an unknown code (fail closed)."""
    if not is_iso4217(currency):
        raise ValueError(f"unknown ISO 4217 currency: {currency!r}")
    return currency_minor_units(currency)


def quantize_money(value: Decimal, currency: str) -> Decimal:
    """Round a monetary amount to the currency's minor units, banker's rounding (no drift across many conversions)."""
    return value.quantize(ONE.scaleb(-minor_units(currency)), rounding=ROUND_HALF_EVEN)


def _leg(amount: Decimal, frm: str, to: str, rates: dict[str, Decimal]) -> Decimal | None:
    """One hop. ``A/B = r`` means one unit of A is r units of B; the reverse hop divides. Returns None if absent."""
    direct = rates.get(f"{frm}/{to}")
    if direct is not None:
        return amount * direct
    inverse = rates.get(f"{to}/{frm}")
    if inverse is not None:
        return amount / inverse
    return None


def convert(
    amount: Decimal,
    frm: str,
    to: str,
    fx: FxSnapshot | None,
    *,
    now: datetime | None,
    max_age_s: Decimal | None,
) -> Decimal:
    """Convert ``amount`` from ``frm`` to ``to`` using ``fx``; pure, Decimal only, and fails closed.

    Rules [Source: 02 FR-05; F-3]: an identity conversion needs no snapshot and no budget; anything else needs a
    snapshot (``FxSnapshotMissing``), a decision time and a freshness budget (``FxBudgetUndefined`` — undefined is
    never "unlimited"), a snapshot that is neither older than the budget nor dated in the future
    (``FxSnapshotStale``), and a rate for the pair either directly, inverted, or by triangulation through the
    snapshot's base currency **only when both legs are present** (``FxPairUnknown``). There is no default rate.
    The result is rounded once, at the end, to the minor units of ``to``.
    """
    if not is_iso4217(frm) or not is_iso4217(to):
        raise ValueError(f"unknown ISO 4217 currency in conversion {frm!r} -> {to!r}")
    if frm == to:
        return amount
    if fx is None:
        raise FxSnapshotMissing(f"no FX snapshot for {frm}->{to}")
    if now is None or max_age_s is None:
        raise FxBudgetUndefined(f"no FX freshness budget defined for {frm}->{to} (snapshot {fx.snapshot_id})")
    age = age_seconds_decimal(fx.as_of, now)
    if age < ZERO or age > max_age_s:
        raise FxSnapshotStale(
            f"FX snapshot {fx.snapshot_id} age {age}s outside budget [0, {max_age_s}]s at {now.isoformat()} ({frm}->{to})"
        )
    rates = fx.rate_map()
    converted = _leg(amount, frm, to, rates)
    if converted is None:
        via = fx.base_currency
        first = None if via in (frm, to) else _leg(amount, frm, via, rates)
        converted = None if first is None else _leg(first, via, to, rates)
    if converted is None:
        raise FxPairUnknown(f"FX snapshot {fx.snapshot_id} has no rate for {frm}->{to} (base {fx.base_currency})")
    return quantize_money(converted, to)
