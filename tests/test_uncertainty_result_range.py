"""Finite component validation alone does not guarantee a finite result."""

import math
from decimal import Decimal
from fractions import Fraction

import pytest

from tsao_computation.uncertainty.model import UncertaintyBudget, combine_independent


def test_unrepresentable_combined_uncertainty_fails_closed() -> None:
    with pytest.raises(ValueError, match="combined uncertainty"):
        combine_independent(1.5e308, 1.5e308)
    with pytest.raises(ValueError, match="combined uncertainty"):
        _ = UncertaintyBudget(1.5e308, 1.5e308, 0.0, "K").combined


def test_large_representable_and_subnormal_results_are_retained() -> None:
    result = combine_independent(1e308, 1e308)
    assert math.isfinite(result)
    assert result / 1e308 == pytest.approx(math.sqrt(2))
    assert combine_independent(5e-324, 5e-324) > 0
    assert combine_independent(3, 4) == 5
    assert combine_independent() == 0


@pytest.mark.parametrize(
    "component",
    [
        "1e-400",
        "-1e-400",
        b"1e-400",
        bytearray(b"-1e-400"),
        memoryview(b"1e-400"),
        Decimal("1e-400"),
        Decimal("-1e-400"),
        Fraction(1, 10**400),
        Fraction(-1, 10**400),
    ],
)
def test_nonzero_components_cannot_become_exact_zero_uncertainty(component: object) -> None:
    with pytest.raises(ValueError, match="underflow"):
        combine_independent(component, 0.0)  # type: ignore[arg-type]
    # Retaining other finite components must not silently discard this source.
    with pytest.raises(ValueError, match="underflow"):
        combine_independent(3.0, component, 4.0)  # type: ignore[arg-type]
    for field in ("statistical", "model", "numerical"):
        components = {"statistical": 0.0, "model": 0.0, "numerical": 0.0}
        components[field] = component  # type: ignore[assignment]
        with pytest.raises(ValueError, match="underflow"):
            UncertaintyBudget(**components, unit="K")


@pytest.mark.parametrize(
    "component",
    [0, -0.0, "0e-400", "-0e-400", b"-0.0", Decimal("-0e-400"), Fraction(0, 10**400)],
)
def test_exact_zero_components_remain_valid(component: object) -> None:
    assert combine_independent(component) == 0.0  # type: ignore[arg-type]
    assert UncertaintyBudget(component, 0, 0, "K").combined == 0.0  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "component", [math.ulp(0.0), Decimal(str(math.ulp(0.0))), Fraction(1, 2**1074)]
)
def test_representable_subnormal_components_are_preserved(component: object) -> None:
    assert combine_independent(component) == math.ulp(0.0)  # type: ignore[arg-type]
    assert UncertaintyBudget(component, 0, 0, "K").combined == math.ulp(0.0)  # type: ignore[arg-type]
