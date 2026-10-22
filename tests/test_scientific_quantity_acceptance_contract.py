from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

import pytest

from tsao_computation import acceptance_is_verified, require_verified_acceptance
from tsao_computation.scientific_quantity import (
    AcceptanceEnvelope,
    ScientificQuantity,
)


def test_scientific_quantity_rejects_bare_or_dimensionless_payloads() -> None:
    with pytest.raises(ValueError, match="missing fields"):
        ScientificQuantity.from_mapping({"value": 12.0})
    with pytest.raises(ValueError, match="dimension"):
        ScientificQuantity(value=Decimal("12"), unit="MPa", dimension=(), source_id="run-1")


def test_quantity_conversion_requires_dimension_compatibility() -> None:
    value = ScientificQuantity(
        value=Decimal("1.25"),
        unit="MPa",
        dimension=(-1, 1, -2, 0, 0, 0, 0),
        source_id="solver-output:42",
        uncertainty=Decimal("0.05"),
    )
    converted = value.convert(
        factor=Decimal("1000000"),
        unit="Pa",
        dimension=value.dimension,
    )
    assert converted.value == Decimal("1250000.00")
    assert converted.uncertainty == Decimal("50000.00")
    with pytest.raises(ValueError, match="incompatible"):
        value.convert(factor=1, unit="K", dimension=(0, 0, 0, 1, 0, 0, 0))


def test_boolean_self_attestation_is_always_held() -> None:
    assert not acceptance_is_verified({"accepted": True})
    assert not acceptance_is_verified({"accepted": True}, verifier=lambda *_: True)


def test_acceptance_requires_external_signature_verification() -> None:
    payload = {
        "decision": "ACCEPTED",
        "reviewer_id": "reviewer:qualified:7",
        "reviewed_at": datetime.now(timezone.utc).isoformat(),
        "evidence_digest": "a" * 64,
        "signature": "external-signature",
        "signature_scheme": "EXTERNAL-DETACHED-V1",
    }
    assert not acceptance_is_verified(payload)
    assert acceptance_is_verified(
        payload,
        verifier=lambda message, signature, reviewer: (
            bool(message)
            and signature == "external-signature"
            and reviewer == "reviewer:qualified:7"
        ),
    )
    envelope = AcceptanceEnvelope.from_mapping(payload)
    assert envelope.decision == "ACCEPTED"


def _signature_payload() -> dict[str, object]:
    return {
        "decision": "ACCEPTED",
        "reviewer_id": "reviewer:qualified:7",
        "reviewed_at": "2026-10-22T06:00:00+00:00",
        "evidence_digest": "a" * 64,
        "signature": "external-signature",
        "signature_scheme": "EXTERNAL-DETACHED-V1",
    }


@pytest.mark.parametrize(
    "result", ["false", "REJECTED", {"valid": False}, [False], 1, 0, 1.0, float("nan"), None]
)
def test_public_signature_hooks_reject_non_boolean_verifier_results(result: object) -> None:
    payload = _signature_payload()

    def verifier(*_: object) -> object:
        return result

    assert acceptance_is_verified(payload, verifier=verifier) is False  # type: ignore[arg-type]
    with pytest.raises(PermissionError, match="verified human acceptance"):
        require_verified_acceptance(payload, verifier=verifier)  # type: ignore[arg-type]


def test_public_signature_hooks_never_coerce_a_verifier_result() -> None:
    class TruthinessTrap:
        evaluations = 0

        def __bool__(self) -> bool:
            self.evaluations += 1
            return True

    result = TruthinessTrap()

    def verifier(*_: object) -> object:
        return result

    payload = _signature_payload()
    assert acceptance_is_verified(payload, verifier=verifier) is False  # type: ignore[arg-type]
    with pytest.raises(PermissionError):
        require_verified_acceptance(payload, verifier=verifier)  # type: ignore[arg-type]
    assert result.evaluations == 0


@pytest.mark.parametrize("decision", [False, True])
def test_public_signature_hooks_preserve_explicit_boolean_decisions(decision: bool) -> None:
    payload = _signature_payload()
    envelope = AcceptanceEnvelope.from_mapping(payload)
    observed: list[tuple[bytes, str, str]] = []

    def verifier(message: bytes, signature: str, reviewer: str) -> bool:
        observed.append((message, signature, reviewer))
        return decision

    assert acceptance_is_verified(payload, verifier=verifier) is decision
    if decision:
        assert require_verified_acceptance(payload, verifier=verifier) == envelope
    else:
        with pytest.raises(PermissionError):
            require_verified_acceptance(payload, verifier=verifier)
    assert (
        observed == [(envelope.canonical_bytes(), "external-signature", "reviewer:qualified:7")] * 2
    )


def test_public_signature_hooks_fail_closed_when_verification_raises() -> None:
    def verifier(*_: object) -> bool:
        raise RuntimeError("external verification unavailable")

    payload = _signature_payload()
    assert acceptance_is_verified(payload, verifier=verifier) is False
    with pytest.raises(PermissionError):
        require_verified_acceptance(payload, verifier=verifier)
