from __future__ import annotations

from ..registries import units


def unit_known(unit: str) -> bool:
    return any(unit in record["accepted"] for record in units().values())


def balance_check(
    inputs: float, outputs: float, accumulation: float = 0.0, *, tolerance: float = 1e-08
) -> dict[str, float | bool]:
    residual = float(inputs) - float(outputs) - float(accumulation)
    scale = max(abs(float(inputs)), abs(float(outputs)), abs(float(accumulation)), 1.0)
    normalized = abs(residual) / scale
    return {
        "passed": normalized <= tolerance,
        "residual": residual,
        "normalized_residual": normalized,
        "tolerance": tolerance,
    }
