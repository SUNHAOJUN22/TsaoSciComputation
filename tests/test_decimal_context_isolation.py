from __future__ import annotations

from decimal import (
    ROUND_DOWN,
    ROUND_UP,
    Context,
    Decimal,
    Inexact,
    Rounded,
    localcontext,
)

import pytest

from tsao_computation.contracts.handoff import HandoffRecord
from tsao_computation.errors import ContractError
from tsao_computation.scientific_quantity import ScientificQuantity

TEMPERATURE = (0, 0, 0, 1, 0, 0, 0)
PRESSURE = (-1, 1, -2, 0, 0, 0, 0)


def _handoff(value: object, unit: str) -> HandoffRecord:
    return HandoffRecord(
        source_model="measurement",
        target_model="thermal-model",
        quantity="temperature",
        value=value,
        unit=unit,
        conditions={"pressure_Pa": 101325},
        reference_state="declared reference",
        statistical_uncertainty=0.1,
        model_uncertainty=0.0,
        applicability="software boundary regression",
        transformation="identity",
        validation_status="checked",
    )


@pytest.mark.parametrize("rounding", [ROUND_UP, ROUND_DOWN])
@pytest.mark.parametrize(
    ("unit", "valid", "invalid"),
    [
        ("K", "0.01", "0"),
        ("degC", "-272", "-279"),
        ("C", "-273.14", "-273.15"),
        ("degF", "-459.66", "-459.67"),
    ],
)
def test_absolute_zero_boundary_is_exact_in_any_decimal_context(
    rounding: str, unit: str, valid: str, invalid: str
) -> None:
    with localcontext() as context:
        context.prec = 2
        context.rounding = rounding
        quantity = ScientificQuantity(
            value=Decimal(valid), unit=unit, dimension=TEMPERATURE, source_id="temperature"
        )
        assert quantity.value == Decimal(valid)
        assert _handoff(float(valid), unit).value == float(valid)
        with pytest.raises(ValueError, match="above zero kelvin"):
            ScientificQuantity(
                value=Decimal(invalid),
                unit=unit,
                dimension=TEMPERATURE,
                source_id="temperature",
            )
        with pytest.raises(ContractError, match="above zero kelvin"):
            _handoff([float(valid), float(invalid)], unit)


@pytest.mark.parametrize(
    "ambient",
    [
        Context(prec=2, rounding=ROUND_UP),
        Context(prec=2, rounding=ROUND_DOWN),
        Context(prec=3, Emin=-2, Emax=2, clamp=1),
        Context(prec=7, traps=[Inexact, Rounded]),
    ],
    ids=["round-up", "round-down", "restricted-exponent", "inexact-traps"],
)
def test_conversion_and_digest_do_not_depend_on_the_callers_decimal_context(
    ambient: Context,
) -> None:
    source = ScientificQuantity(
        value=Decimal("1"),
        unit="delta_degF",
        dimension=TEMPERATURE,
        source_id="interval-observation",
        uncertainty=Decimal("0.1"),
    )
    reference = source.convert(unit="delta_K", dimension=TEMPERATURE)
    # 5/9 rounded to 50 significant decimal digits with ties-to-even.
    assert reference.value == Decimal("0." + "5" * 49 + "6")
    assert reference.uncertainty == Decimal("0.0" + "5" * 49 + "6")
    with localcontext(ambient) as context:
        original = context.copy()
        converted = source.convert(unit="delta_K", dimension=TEMPERATURE)
        assert converted.canonical_payload() == reference.canonical_payload()
        assert converted.digest == reference.digest
        assert converted.source_quantity_digest == source.digest
        assert str(context) == str(original)
        assert context.flags == original.flags


def test_restricted_ambient_exponents_do_not_change_valid_pressure_conversion() -> None:
    source = ScientificQuantity(
        value=Decimal("1.25"),
        unit="MPa",
        dimension=PRESSURE,
        source_id="pressure-observation",
        uncertainty=Decimal("0.05"),
    )
    with localcontext() as context:
        context.Emin, context.Emax = -2, 2
        converted = source.convert(unit="Pa", dimension=PRESSURE)
    assert converted.value == Decimal("1250000")
    assert converted.uncertainty == Decimal("50000")


def test_valid_temperature_checks_do_not_set_the_callers_decimal_flags() -> None:
    with localcontext() as context:
        context.prec = 2
        context.traps[Inexact] = True
        context.traps[Rounded] = True
        assert _handoff(25.0, "degC").value == 25.0
        quantity = ScientificQuantity(
            value=Decimal("25"), unit="degC", dimension=TEMPERATURE, source_id="temperature"
        )
        assert quantity.convert(unit="K", dimension=TEMPERATURE).value == Decimal("298.15")
        assert not any(context.flags.values())
