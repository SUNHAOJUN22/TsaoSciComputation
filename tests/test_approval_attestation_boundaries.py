from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any

import pytest

from tsao_computation.validation import (
    APPROVAL_SCHEMA_VERSION,
    acceptance_gate,
    sign_approval_attestation,
    verify_approval_attestation,
)
from tsao_computation.validation.acceptance import REQUIRED

ARTIFACT = "a" * 64
KEY = b"independent-review-key-material"
NOW = datetime(2026, 9, 1, 12, 0, tzinfo=timezone.utc)


def unsigned_approval(**overrides: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "schema_version": APPROVAL_SCHEMA_VERSION,
        "issuer": "institutional-review-service",
        "approver": "domain-expert-02",
        "requester": "calculation-author-01",
        "role": "independent-domain-reviewer",
        "scope": "scientific-result-acceptance",
        "artifact_sha256": ARTIFACT,
        "issued_at": "2026-09-01T00:00:00Z",
        "expires_at": "2026-09-02T00:00:00Z",
        "nonce": "approval-nonce-0001",
        "key_id": "review-key-1",
    }
    payload.update(overrides)
    return payload


def signed_approval(**overrides: Any) -> dict[str, Any]:
    return sign_approval_attestation(unsigned_approval(**overrides), secret_key=KEY)


def ready_record(*approvals: object, artifact_sha256: object = ARTIFACT) -> dict[str, object]:
    record: dict[str, object] = {key: True for key in REQUIRED}
    record["artifact_sha256"] = artifact_sha256
    record["approvals"] = list(approvals)
    return record


@pytest.mark.parametrize("secret_key", (b"", "not-bytes", bytearray(b"bytes")))
def test_signing_requires_non_empty_bytes(secret_key: object) -> None:
    with pytest.raises(ValueError, match="secret_key"):
        sign_approval_attestation(unsigned_approval(), secret_key=secret_key)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("overrides", "message"),
    (
        ({"schema_version": "unsupported"}, "schema_version"),
        ({"issuer": ""}, "issuer"),
        ({"artifact_sha256": "not-a-digest"}, "artifact_sha256"),
        ({"nonce": "too-short"}, "nonce"),
        ({"approver": "calculation-author-01"}, "independent"),
        ({"issued_at": "not-a-date"}, "ISO-8601"),
        ({"issued_at": "2026-09-01T00:00:00"}, "timezone-aware"),
        ({"expires_at": "2026-09-01T00:00:00Z"}, "later than"),
    ),
)
def test_signing_rejects_every_structural_boundary(
    overrides: dict[str, object], message: str
) -> None:
    with pytest.raises(ValueError, match=message):
        sign_approval_attestation(unsigned_approval(**overrides), secret_key=KEY)


def test_signing_is_canonical_and_does_not_mutate_the_input() -> None:
    original = unsigned_approval()
    snapshot = deepcopy(original)
    first = sign_approval_attestation(original, secret_key=KEY)
    reordered = {key: original[key] for key in reversed(tuple(original))}
    second = sign_approval_attestation(reordered, secret_key=KEY)
    assert original == snapshot
    assert first["signature"] == second["signature"]
    assert "signature" not in original


@pytest.mark.parametrize(
    ("approval", "trusted_keys", "artifact", "now", "reason"),
    (
        ("not-an-object", {"review-key-1": KEY}, ARTIFACT, NOW, "approval_not_an_object"),
        (
            {"schema_version": "unsupported"},
            {"review-key-1": KEY},
            ARTIFACT,
            NOW,
            "approval_structure_invalid",
        ),
        (
            signed_approval(),
            {"review-key-1": KEY},
            "b" * 64,
            NOW,
            "approval_artifact_mismatch",
        ),
        (
            {**signed_approval(), "signature": "invalid"},
            {"review-key-1": KEY},
            ARTIFACT,
            NOW,
            "approval_signature_invalid",
        ),
        (
            signed_approval(),
            {},
            ARTIFACT,
            NOW,
            "approval_key_untrusted",
        ),
        (
            signed_approval(),
            {"review-key-1": b""},
            ARTIFACT,
            NOW,
            "approval_key_untrusted",
        ),
        (
            signed_approval(),
            {"review-key-1": KEY},
            ARTIFACT,
            datetime(2026, 9, 1, 12, 0),
            "approval_now_not_timezone_aware",
        ),
        (
            signed_approval(),
            {"review-key-1": KEY},
            ARTIFACT,
            datetime(2026, 8, 31, 23, 59, tzinfo=timezone.utc),
            "approval_not_yet_valid",
        ),
        (
            signed_approval(),
            {"review-key-1": KEY},
            ARTIFACT,
            datetime(2026, 9, 2, tzinfo=timezone.utc),
            "approval_expired",
        ),
    ),
)
def test_verification_returns_stable_fail_closed_reason_codes(
    approval: object,
    trusted_keys: dict[str, bytes],
    artifact: str,
    now: datetime,
    reason: str,
) -> None:
    valid, actual = verify_approval_attestation(
        approval,
        trusted_keys=trusted_keys,
        artifact_sha256=artifact,
        now=now,
    )
    assert valid is False
    assert actual == reason


def test_verification_detects_a_well_formed_signature_mismatch() -> None:
    approval = signed_approval()
    approval["scope"] = "tampered-scope"
    valid, reason = verify_approval_attestation(
        approval,
        trusted_keys={"review-key-1": KEY},
        artifact_sha256=ARTIFACT,
        now=NOW,
    )
    assert valid is False
    assert reason == "approval_signature_mismatch"


def test_verification_accepts_only_the_bound_independent_attestation() -> None:
    valid, reason = verify_approval_attestation(
        signed_approval(),
        trusted_keys={"review-key-1": KEY},
        artifact_sha256=ARTIFACT,
        now=NOW,
    )
    assert valid is True
    assert reason == "verified"


def test_acceptance_rejects_invalid_artifact_binding_and_reports_readiness() -> None:
    result = acceptance_gate(
        ready_record(signed_approval(), artifact_sha256="not-a-digest"),
        trusted_approval_keys={"review-key-1": KEY},
        now=NOW,
    )
    assert result["software_ready"] is True
    assert result["accepted"] is False
    assert "artifact_binding" in result["missing"]
    assert "approval_artifact_mismatch" in result["approval_failures"]


def test_acceptance_detects_reused_nonce_without_discarding_first_valid_approval() -> None:
    approval = signed_approval()
    result = acceptance_gate(
        ready_record(approval, dict(approval)),
        trusted_approval_keys={"review-key-1": KEY},
        now=NOW,
    )
    assert result["accepted"] is True
    assert result["verified_approval_count"] == 1
    assert result["approval_failures"] == ["approval_nonce_reused"]


def test_acceptance_keeps_software_readiness_separate_from_acceptance() -> None:
    record = ready_record(signed_approval())
    record["converged"] = False
    result = acceptance_gate(
        record,
        trusted_approval_keys={"review-key-1": KEY},
        now=NOW,
    )
    assert result["software_ready"] is False
    assert result["accepted"] is False
    assert "converged" in result["missing"]
    assert result["verified_approval_count"] == 1
