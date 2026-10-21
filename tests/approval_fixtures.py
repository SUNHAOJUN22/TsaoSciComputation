"""Synthetic signatures for local contract tests; no scientific certification."""

from __future__ import annotations

from tsao_computation.validation.acceptance import REQUIRED
from tsao_computation.validation.approval_attestation import (
    APPROVAL_SCHEMA_VERSION,
    sign_approval_attestation,
)

TEST_KEYS = {"synthetic-local-review": b"fixture-only-key-not-an-operational-credential"}


def verified_record(digest: str = "a" * 64, *, governance: bool = False) -> dict[str, object]:
    record: dict[str, object] = {key: True for key in REQUIRED}
    record.update({"artifact_sha256": digest, "expert_reviewed": True})
    scopes = [("scientific-result-acceptance", "independent-domain-reviewer")]
    if governance:
        record.update(
            {
                "decision_scope": "synthetic fixture decision",
                "decision_scope_confirmed": True,
                "safety_review_completed": True,
                "independent_reproduction": True,
            }
        )
        scopes.extend(
            [
                ("engineering-decision", "independent-domain-reviewer"),
                ("safety-review", "safety-reviewer"),
                ("independent-reproduction", "independent-reproducer"),
            ]
        )
    record["approvals"] = [
        sign_approval_attestation(
            {
                "schema_version": APPROVAL_SCHEMA_VERSION,
                "issuer": "test-fixture",
                "approver": f"reviewer-{i}",
                "requester": "fixture-requester",
                "role": role,
                "scope": scope,
                "artifact_sha256": digest,
                "issued_at": "2020-01-01T00:00:00+00:00",
                "expires_at": "2100-01-01T00:00:00+00:00",
                "nonce": f"synthetic-nonce-{i:04d}",
                "key_id": "synthetic-local-review",
                "decision_scope": "synthetic fixture decision",
            },
            secret_key=TEST_KEYS["synthetic-local-review"],
        )
        for i, (scope, role) in enumerate(scopes)
    ]
    return record
