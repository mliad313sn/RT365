"""Point-in-time instrument master [Source: 08; C7 §2]: universes as of a date include delisted names."""

from __future__ import annotations

from datetime import datetime

from rtcore.schemas.market import InstrumentAttributes


class InstrumentMaster:
    def __init__(self) -> None:
        self._rows: dict[str, list[InstrumentAttributes]] = {}

    def add(self, inst: InstrumentAttributes) -> None:
        self._rows.setdefault(inst.instrument_id, []).append(inst)
        self._rows[inst.instrument_id].sort(key=lambda i: i.valid_from)

    def delist(self, instrument_id: str, *, at: datetime) -> None:
        rows = self._rows[instrument_id]
        last = rows[-1]
        rows[-1] = last.model_copy(update={"valid_to": at, "tradable": last.tradable})

    def get(self, instrument_id: str, *, as_of: datetime) -> InstrumentAttributes | None:
        for row in reversed(self._rows.get(instrument_id, [])):
            if row.valid_at(as_of):
                return row
        return None

    def universe(self, *, as_of: datetime, include_delisted: bool = True) -> tuple[InstrumentAttributes, ...]:
        out: list[InstrumentAttributes] = []
        for rows in self._rows.values():
            for row in rows:
                if row.valid_at(as_of) or (include_delisted and row.valid_to is not None and row.valid_from <= as_of):
                    out.append(row)
                    break
        return tuple(out)

    def all_ids(self) -> tuple[str, ...]:
        return tuple(self._rows)
