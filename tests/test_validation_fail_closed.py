from __future__ import annotations

import math

import pytest

from scripts.run_mutation_gate import state_mutants
from tsao_computation.validation import (
    acceptance_gate,
    balance_check,
    convergence_check,
    finite_values,
    unit_known,
)
from tsao_computation.validation.acceptance import REQUIRED


def complete_record() -> dict[str, object]:
    return {key: True for key in REQUIRED}


def test_non_numeric_values_fail_finite_and_convergence_checks() -> None:
    assert finite_values([1.0, "invalid"]) is False  # type: ignore[list-item]
    result = convergence_check([1.0, "invalid"], absolute_tolerance=0.1)  # type: ignore[list-item]
    assert result["passed"] is False
    assert result["delta"] == float("inf")


@pytest.mark.parametrize(
    ("absolute", "relative"),
    ((-1.0, 0.0), (0.1, -1.0), (math.nan, 0.0), (0.1, math.inf)),
)
def test_convergence_tolerances_must_be_finite_and_non_negative(
    absolute: float, relative: float
) -> None:
    with pytest.raises(ValueError, match="finite and non-negative"):
        convergence_check(
            [1.0, 1.1], absolute_tolerance=absolute, relative_tolerance=relative
        )


@pytest.mark.parametrize(
    ("inputs", "outputs", "accumulation", "tolerance"),
    (
        (math.inf, 1.0, 0.0, 1e-8),
        (1.0, math.nan, 0.0, 1e-8),
        (1.0, 1.0, 0.0, -1.0),
    ),
)
def test_balance_inputs_and_tolerance_are_guarded(
    inputs: float, outputs: float, accumulation: float, tolerance: float
) -> None:
    with pytest.raises(ValueError):
        balance_check(inputs, outputs, accumulation, tolerance=tolerance)


def test_unit_lookup_is_exact_after_whitespace_normalization() -> None:
    assert unit_known(" MPa ") is True
    assert unit_known("Pascal") is False
    assert unit_known(3) is False  # type: ignore[arg-type]


@pytest.mark.parametrize("approvals", ("expert", [], [""], ["expert", ""]))
def test_human_approval_requires_a_nonempty_string_array(approvals: object) -> None:
    record = complete_record()
    record["human_approval_required"] = True
    record["approvals"] = approvals
    result = acceptance_gate(record)
    assert result["accepted"] is False
    assert "human_approval" in result["missing"]


def test_structured_human_approval_can_pass_the_final_gate() -> None:
    record = complete_record()
    record["human_approval_required"] = True
    record["approvals"] = ["domain-expert:approved"]
    assert acceptance_gate(record)["accepted"] is True


def test_state_mutation_probes_use_the_actual_illegal_transition() -> None:
    probes = state_mutants()
    assert len(probes) == 8
    assert all(probe() for _, probe in probes)
