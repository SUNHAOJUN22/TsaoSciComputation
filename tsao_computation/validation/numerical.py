from __future__ import annotations

import math
from collections.abc import Iterable


def finite_values(values: Iterable[float]) -> bool:
    return all(math.isfinite(float(x)) for x in values)


def convergence_check(
    values: Iterable[float], *, absolute_tolerance: float, relative_tolerance: float = 0.0
) -> dict[str, float | bool]:
    seq = tuple(float(x) for x in values)
    if len(seq) < 2 or not finite_values(seq):
        return {"passed": False, "delta": float("inf"), "threshold": absolute_tolerance}
    delta = abs(seq[-1] - seq[-2])
    scale = max(abs(seq[-1]), abs(seq[-2]), 1.0)
    threshold = max(float(absolute_tolerance), float(relative_tolerance) * scale)
    return {"passed": delta <= threshold, "delta": delta, "threshold": threshold}
