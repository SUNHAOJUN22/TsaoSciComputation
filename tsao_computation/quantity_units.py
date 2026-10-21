"""Versioned unit metadata; dimensions use (L, M, T, temperature, amount, I, luminosity)."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from types import MappingProxyType

REGISTRY_VERSION = "tsao.quantity-units/1"
DIMENSION_ORDER = ("length", "mass", "time", "temperature", "amount", "current", "luminosity")


@dataclass(frozen=True, slots=True)
class UnitDefinition:
    dimension: tuple[int, ...]
    scale: Decimal = Decimal(1)
    offset: Decimal = Decimal(0)
    kind: str = "linear"
    divisor: Decimal = Decimal(1)


def _build() -> dict[str, UnitDefinition]:
    groups = [
        (
            (0, 0, 0, 0, 0, 0, 0),
            {"1": "1", "fraction": "1", "percent": "0.01", "%": "0.01", "ppm": "0.000001"},
        ),
        (
            (1, 0, 0, 0, 0, 0, 0),
            {
                "m": "1",
                "cm": "0.01",
                "mm": "0.001",
                "um": "1e-6",
                "nm": "1e-9",
                "angstrom": "1e-10",
            },
        ),
        ((0, 1, 0, 0, 0, 0, 0), {"kg": "1", "g": "0.001", "mg": "1e-6"}),
        (
            (0, 0, 1, 0, 0, 0, 0),
            {
                "s": "1",
                "ms": "1e-3",
                "us": "1e-6",
                "ns": "1e-9",
                "ps": "1e-12",
                "fs": "1e-15",
                "min": "60",
                "h": "3600",
            },
        ),
        ((0, 0, 0, 0, 1, 0, 0), {"mol": "1", "mmol": "0.001", "kmol": "1000"}),
        (
            (-1, 1, -2, 0, 0, 0, 0),
            {"Pa": "1", "kPa": "1000", "MPa": "1000000", "bar": "100000", "atm": "101325"},
        ),
        ((-1, 1, -1, 0, 0, 0, 0), {"Pa*s": "1", "Pa.s": "1", "mPa*s": "0.001", "cP": "0.001"}),
        ((-3, 1, 0, 0, 0, 0, 0), {"kg/m3": "1", "g/cm3": "1000"}),
        ((2, 0, -1, 0, 0, 0, 0), {"m2/s": "1", "cm2/s": "0.0001"}),
        (
            (2, 1, -2, 0, 0, 0, 0),
            {"J": "1", "kJ": "1000", "eV": "1.602176634e-19", "hartree": "4.359744722206e-18"},
        ),
        ((2, 1, -2, 0, -1, 0, 0), {"J/mol": "1", "kJ/mol": "1000", "kcal/mol": "4184"}),
    ]
    result = {
        name: UnitDefinition(dim, Decimal(scale))
        for dim, units in groups
        for name, scale in units.items()
    }
    temperature = (0, 0, 0, 1, 0, 0, 0)
    result.update(
        {
            "K": UnitDefinition(temperature, kind="absolute-temperature"),
            "degC": UnitDefinition(
                temperature, offset=Decimal("273.15"), kind="absolute-temperature"
            ),
            "C": UnitDefinition(temperature, offset=Decimal("273.15"), kind="absolute-temperature"),
            "degF": UnitDefinition(
                temperature, Decimal(5), Decimal("459.67"), "absolute-temperature", Decimal(9)
            ),
            "delta_K": UnitDefinition(temperature, kind="temperature-interval"),
            "delta_degC": UnitDefinition(temperature, kind="temperature-interval"),
            "delta_degF": UnitDefinition(
                temperature, Decimal(5), kind="temperature-interval", divisor=Decimal(9)
            ),
        }
    )
    return result


UNIT_DEFINITIONS = MappingProxyType(_build())


def unit_definition(unit: object) -> UnitDefinition:
    if not isinstance(unit, str) or not unit.strip():
        raise ValueError("unit must be a non-empty string")
    try:
        return UNIT_DEFINITIONS[unit.strip()]
    except KeyError as exc:
        raise ValueError(f"unit is not in the controlled registry: {unit!r}") from exc
