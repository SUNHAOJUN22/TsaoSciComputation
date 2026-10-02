"""Finite component validation alone does not guarantee a finite result."""

import math

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
