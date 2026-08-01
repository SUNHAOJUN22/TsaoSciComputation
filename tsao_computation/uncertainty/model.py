from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class UncertaintyBudget:
    statistical: float
    model: float
    numerical: float
    unit: str

    @property
    def combined(self) -> float:
        return combine_independent(self.statistical, self.model, self.numerical)


def combine_independent(*components: float) -> float:
    if any(value < 0 or not math.isfinite(value) for value in components):
        raise ValueError("uncertainty components must be finite and non-negative")
    return math.hypot(*components)
