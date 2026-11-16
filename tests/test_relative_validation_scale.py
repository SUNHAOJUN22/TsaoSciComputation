from __future__ import annotations

import math
from fractions import Fraction

import pytest

from tsao_computation.validation import balance_check, convergence_check


@pytest.mark.parametrize("basis", [1.0e-12, 1.0e-3, 1.0, 1.0e9])
@pytest.mark.parametrize("sign", [-1.0, 1.0])
def test_relative_convergence_rejects_half_scale_changes_in_every_unit_basis(
    basis: float, sign: float
) -> None:
    previous, current = sign * basis, sign * 2.0 * basis
    exact_relative_change = abs(Fraction(current) - Fraction(previous)) / max(
        abs(Fraction(previous)), abs(Fraction(current))
    )
    assert exact_relative_change == Fraction(1, 2)
    result = convergence_check([previous, current], absolute_tolerance=0.0, relative_tolerance=0.01)
    assert result["passed"] is False


@pytest.mark.parametrize("basis", [1.0e-12, 1.0e-3, 1.0, 1.0e9])
def test_relative_convergence_accepts_small_fractional_changes(basis: float) -> None:
    result = convergence_check(
        [basis, 1.001 * basis], absolute_tolerance=0.0, relative_tolerance=0.01
    )
    assert result["passed"] is True
    assert result["threshold"] == pytest.approx(0.01 * 1.001 * basis, rel=1.0e-12, abs=0.0)


@pytest.mark.parametrize("basis", [1.0e-12, 1.0, 1.0e12])
def test_absolute_tolerance_is_explicit_and_has_the_input_unit(basis: float) -> None:
    result = convergence_check(
        [basis, 2.0 * basis], absolute_tolerance=1.01 * basis, relative_tolerance=0.0
    )
    assert result["passed"] is True


@pytest.mark.parametrize("basis", [1.0e-12, 1.0e-3, 1.0, 1.0e9])
@pytest.mark.parametrize("sign", [-1.0, 1.0])
def test_balance_rejects_complete_flux_loss_in_every_unit_basis(basis: float, sign: float) -> None:
    result = balance_check(sign * basis, 0.0, tolerance=0.01)
    assert result["passed"] is False
    assert result["normalized_residual"] == 1.0


@pytest.mark.parametrize("basis", [1.0e-12, 1.0e-3, 1.0, 1.0e9])
def test_balance_accepts_relative_closure_with_explicit_accumulation(basis: float) -> None:
    result = balance_check(basis, 0.75 * basis, 0.249 * basis, tolerance=0.002)
    assert result["passed"] is True
    assert result["normalized_residual"] == pytest.approx(0.001)


def test_zero_scale_is_an_exact_balance_and_converged_pair() -> None:
    assert balance_check(0.0, -0.0, 0.0, tolerance=0.0) == {
        "passed": True,
        "residual": 0.0,
        "normalized_residual": 0.0,
        "tolerance": 0.0,
    }
    assert convergence_check([0.0, -0.0], absolute_tolerance=0.0, relative_tolerance=0.01) == {
        "passed": True,
        "delta": 0.0,
        "threshold": 0.0,
    }


def test_representable_trace_scale_retains_positive_and_negative_controls() -> None:
    smallest = math.ulp(0.0)
    assert balance_check(smallest, smallest, tolerance=0.0)["passed"] is True
    assert balance_check(smallest, 0.0, tolerance=0.01)["passed"] is False
    assert (
        convergence_check([smallest, smallest], absolute_tolerance=0.0, relative_tolerance=0.0)[
            "passed"
        ]
        is True
    )
    assert (
        convergence_check(
            [smallest, 2.0 * smallest], absolute_tolerance=0.0, relative_tolerance=0.49
        )["passed"]
        is False
    )
    assert (
        convergence_check(
            [smallest, 2.0 * smallest], absolute_tolerance=0.0, relative_tolerance=0.5
        )["passed"]
        is True
    )
