from __future__ import annotations

import math
from decimal import Decimal
from fractions import Fraction

import pytest

from tsao_computation.validation import balance_check, convergence_check, finite_values


@pytest.mark.parametrize(
    "value",
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
def test_nonzero_inputs_cannot_become_zero_convergence_evidence(value: object) -> None:
    assert finite_values([value, 0.0]) is False  # type: ignore[list-item]
    result = convergence_check([value, 0.0], absolute_tolerance=0.0)  # type: ignore[list-item]
    assert result == {"passed": False, "delta": math.inf, "threshold": 0.0}


@pytest.mark.parametrize("field", ["inputs", "outputs", "accumulation", "tolerance"])
def test_balance_rejects_nonzero_underflow_in_each_scalar_field(field: str) -> None:
    arguments: dict[str, object] = {
        "inputs": 0.0,
        "outputs": 0.0,
        "accumulation": 0.0,
        "tolerance": 0.0,
    }
    arguments[field] = Decimal("1e-400")
    with pytest.raises(ValueError, match="underflow"):
        balance_check(**arguments)  # type: ignore[arg-type]


@pytest.mark.parametrize("field", ["absolute_tolerance", "relative_tolerance"])
def test_convergence_rejects_nonzero_underflowed_tolerances(field: str) -> None:
    arguments = {"absolute_tolerance": 0.0, "relative_tolerance": 0.0}
    arguments[field] = "1e-400"  # type: ignore[assignment]
    with pytest.raises(ValueError, match="finite and non-negative"):
        convergence_check([1.0, 1.0], **arguments)


@pytest.mark.parametrize(
    "value",
    [0, -0.0, "0e-400", "-0e-400", b"-0.0", Decimal("-0e-400"), Fraction(0, 10**400)],
)
def test_true_zero_is_not_misclassified_as_underflow(value: object) -> None:
    assert finite_values([value]) is True  # type: ignore[list-item]
    result = convergence_check([value, 0.0], absolute_tolerance=0.0)  # type: ignore[list-item]
    assert result == {"passed": True, "delta": 0.0, "threshold": 0.0}
    assert balance_check(value, 0.0, tolerance=0.0)["passed"] is True  # type: ignore[arg-type]


@pytest.mark.parametrize("sign", [1, -1])
def test_representable_subnormals_remain_valid_and_nonzero(sign: int) -> None:
    smallest = sign * math.ulp(0.0)
    assert finite_values([smallest, Decimal(str(smallest))]) is True  # type: ignore[list-item]
    result = convergence_check([smallest, 0.0], absolute_tolerance=0.0)
    assert result == {"passed": False, "delta": math.ulp(0.0), "threshold": 0.0}
    balance = balance_check(smallest, 0.0, tolerance=0.0)
    assert balance["passed"] is False
    assert balance["residual"] == smallest


def test_normalized_residual_cannot_underflow_into_an_exact_balance() -> None:
    with pytest.raises(ValueError, match="underflow"):
        balance_check(1e308, 1e308, math.ulp(0.0), tolerance=0.0)
