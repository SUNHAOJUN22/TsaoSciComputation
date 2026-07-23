from __future__ import annotations

import math
from collections.abc import Iterable


def finite_values(values: Iterable[float]) -> bool:
    try:
        return all(math.isfinite(float(value)) for value in values)
    except (TypeError, ValueError, OverflowError):
        return False


def _finite_non_negative(value: float, *, name: str) -> float:
    converted = float(value)
    if not math.isfinite(converted) or converted < 0:
        raise ValueError(f"{name} must be finite and non-negative")
    return converted


def convergence_check(
    values: Iterable[float], *, absolute_tolerance: float, relative_tolerance: float = 0.0
) -> dict[str, float | bool]:
    absolute = _finite_non_negative(absolute_tolerance, name="absolute_tolerance")
    relative = _finite_non_negative(relative_tolerance, name="relative_tolerance")
    try:
        seq = tuple(float(value) for value in values)
    except (TypeError, ValueError, OverflowError):
        seq = ()
    if len(seq) < 2 or not finite_values(seq):
        return {"passed": False, "delta": float("inf"), "threshold": absolute}
    delta = abs(seq[-1] - seq[-2])
    scale = max(abs(seq[-1]), abs(seq[-2]), 1.0)
    threshold = max(absolute, relative * scale)
    return {"passed": delta <= threshold, "delta": delta, "threshold": threshold}
