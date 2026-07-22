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
    if any(x < 0 or not math.isfinite(x) for x in components):
        raise ValueError("uncertainty components must be finite and non-negative")
    return math.sqrt(sum(x * x for x in components))
