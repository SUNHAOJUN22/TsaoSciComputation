"""Focused tests for strict scientific-computation contracts."""

import pytest

from tsao_computation.scientific_contracts_v16 import (
    ExecutionCapability,
    ScientificDatum,
    acceptance_status,
    convergence,
    issue_capability,
    verify_capability,
)


def length(value: float, unit: str, scale: float) -> ScientificDatum:
    return ScientificDatum(value, unit, "length", scale)


def test_convergence_is_unit_representation_invariant() -> None:
    metres = convergence(
        length(1.0, "m", 1.0),
        length(1.0001, "m", 1.0),
        atol=length(0.0002, "m", 1.0),
        rtol=0.0,
    )
    millimetres = convergence(
        length(1000.0, "mm", 0.001),
        length(1000.1, "mm", 0.001),
        atol=length(0.2, "mm", 0.001),
        rtol=0.0,
    )
    assert metres == millimetres


def test_nonfinite_and_boolean_data_are_rejected() -> None:
    with pytest.raises(TypeError):
        ScientificDatum(True, "m", "length", 1.0).canonical()
    with pytest.raises(ValueError):
        ScientificDatum(float("inf"), "m", "length", 1.0).canonical()


def test_execution_capability_is_signed_short_lived_and_one_time() -> None:
    digest = "0" * 64
    unsigned = ExecutionCapability(
        digest,
        digest,
        digest,
        "worker",
        "execute",
        "tsao-scicomputation",
        100,
        200,
        "nonce-1",
        "key-1",
    )
    key = b"x" * 32
    capability = issue_capability(unsigned, key)
    used: set[str] = set()
    verify_capability(
        capability,
        key=key,
        expected_subject="worker",
        expected_scope="execute",
        now=150,
        used_nonces=used,
    )
    with pytest.raises(ValueError):
        verify_capability(
            capability,
            key=key,
            expected_subject="worker",
            expected_scope="execute",
            now=150,
            used_nonces=used,
        )


def test_acceptance_requires_independent_approval() -> None:
    assert (
        acceptance_status(
            executed=True,
            converged=True,
            numerically_checked=True,
            physically_validated=True,
            independent_approval=False,
        )
        == "PHYSICALLY_VALIDATED_ACCEPTANCE_HOLD"
    )
