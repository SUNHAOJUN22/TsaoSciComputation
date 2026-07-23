from __future__ import annotations

import math

from ..registries import units


def unit_known(unit: str) -> bool:
    if not isinstance(unit, str) or not unit.strip():
        return False
    candidate = unit.strip()
    return any(candidate in record["accepted"] for record in units().values())


def balance_check(
    inputs: float, outputs: float, accumulation: float = 0.0, *, tolerance: float = 1e-08
) -> dict[str, float | bool]:
    values = tuple(float(value) for value in (inputs, outputs, accumulation, tolerance))
    if not all(math.isfinite(value) for value in values):
        raise ValueError("balance inputs and tolerance must be finite")
    input_value, output_value, accumulation_value, tolerance_value = values
    if tolerance_value < 0:
        raise ValueError("tolerance must be non-negative")
    residual = input_value - output_value - accumulation_value
    if not math.isfinite(residual):
        raise ValueError("balance residual must be finite")
    scale = max(abs(input_value), abs(output_value), abs(accumulation_value), 1.0)
    normalized = abs(residual) / scale
    return {
        "passed": normalized <= tolerance_value,
        "residual": residual,
        "normalized_residual": normalized,
        "tolerance": tolerance_value,
    }
