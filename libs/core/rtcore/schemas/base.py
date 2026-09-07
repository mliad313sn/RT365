from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from rtcore.ids import hash_of


class StrictModel(BaseModel):
    """Frozen, forbids unknown fields, hashable by canonical JSON."""

    model_config = ConfigDict(frozen=True, extra="forbid", str_strip_whitespace=True)

    def canonical_hash(self) -> str:
        return hash_of(self)
