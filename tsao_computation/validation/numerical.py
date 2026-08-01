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
    count = 0
    previous = 0.0
    current = 0.0
    try:
        for value in values:
            converted = float(value)
            if not math.isfinite(converted):
                return {"passed": False, "delta": float("inf"), "threshold": absolute}
            previous, current = current, converted
            count += 1
    except (TypeError, ValueError, OverflowError):
        return {"passed": False, "delta": float("inf"), "threshold": absolute}
    if count < 2:
        return {"passed": False, "delta": float("inf"), "threshold": absolute}

    delta = abs(current - previous)
    if not math.isfinite(delta):
        return {"passed": False, "delta": float("inf"), "threshold": absolute}
    scale = max(abs(current), abs(previous), 1.0)
    relative_threshold = relative * scale
    if not math.isfinite(relative_threshold):
        raise ValueError("relative tolerance produces a non-finite convergence threshold")
    threshold = max(absolute, relative_threshold)
    return {"passed": delta <= threshold, "delta": delta, "threshold": threshold}
