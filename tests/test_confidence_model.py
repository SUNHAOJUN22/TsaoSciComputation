from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest
from approval_fixtures import TEST_KEYS, verified_record

from tsao_computation.validation import assess_confidence
from tsao_computation.validation.approval_attestation import sign_approval_attestation


def evidence_through_c5() -> dict[str, object]:
    return verified_record(governance=True)


def test_unassessed_and_c0_are_distinct() -> None:
    assert assess_confidence({}).level == "UNASSESSED"
    assert assess_confidence({"completed": True}).level == "C0"


def test_levels_are_strictly_sequential() -> None:
    record = evidence_through_c5()
    expected = {
        "C0": {"parsed": False},
        "C1": {"physically_validated": False},
        "C2": {"uncertainty_quantified": False},
        "C3": {"expert_reviewed": False},
        "C4": {"decision_scope_confirmed": False},
    }
    for level, changes in expected.items():
        candidate = dict(record)
        candidate.update(changes)
        assert assess_confidence(candidate, trusted_approval_keys=TEST_KEYS).level == level


def test_c5_requires_all_decision_governance_evidence() -> None:
    assessment = assess_confidence(evidence_through_c5(), trusted_approval_keys=TEST_KEYS)
    assert assessment.level == "C5"
    assert assessment.engineering_decision_ready is True
    assert assessment.next_level is None
    assert assessment.missing_for_next == ()


@pytest.mark.parametrize("unrelated_first", (True, False))
@pytest.mark.parametrize(
    "delta",
    (
        {"scope": "download-artifact"},
        {"role": "request-author"},
        {"decision_scope": "another decision"},
    ),
)
def test_ineligible_governance_approval_cannot_reserve_nonce(
    unrelated_first: bool, delta: dict[str, str]
) -> None:
    record = evidence_through_c5()
    approvals = list(record["approvals"])
    valid = approvals[1]
    unrelated = sign_approval_attestation(
        {**valid, **delta}, secret_key=TEST_KEYS["synthetic-local-review"]
    )
    approvals.insert(1 if unrelated_first else 2, unrelated)
    record["approvals"] = approvals

    assessment = assess_confidence(record, trusted_approval_keys=TEST_KEYS)

    assert assessment.level == "C5"
    assert assessment.engineering_decision_ready is True


@pytest.mark.parametrize("duplicate_first", (True, False))
def test_eligible_governance_scopes_cannot_share_nonce(duplicate_first: bool) -> None:
    record = evidence_through_c5()
    approvals = list(record["approvals"])
    approvals[2] = sign_approval_attestation(
        {**approvals[2], "nonce": approvals[1]["nonce"]},
        secret_key=TEST_KEYS["synthetic-local-review"],
    )
    if duplicate_first:
        approvals[1], approvals[2] = approvals[2], approvals[1]
    record["approvals"] = approvals

    assessment = assess_confidence(record, trusted_approval_keys=TEST_KEYS)

    assert assessment.level == "C4"
    assert assessment.engineering_decision_ready is False
    assert len(assessment.missing_for_next) == 1


def test_malformed_approvals_fail_closed() -> None:
    for approvals in (None, [], [""], ["   "], "reviewed"):
        record = evidence_through_c5()
        record["approvals"] = approvals
        assessment = assess_confidence(record)
        assert assessment.level == "C3"
        assert "approvals" in assessment.missing_for_next


def test_missing_lower_evidence_cannot_be_skipped() -> None:
    record = evidence_through_c5()
    record["converged"] = False
    assert assess_confidence(record).level == "C0"


def test_input_must_be_mapping() -> None:
    with pytest.raises(TypeError):
        assess_confidence([("completed", True)])  # type: ignore[arg-type]


def test_assessment_validates_against_schema() -> None:
    schema = json.loads(
        Path("schemas/confidence-assessment.schema.json").read_text(encoding="utf-8")
    )
    payload = assess_confidence(evidence_through_c5(), trusted_approval_keys=TEST_KEYS).to_dict()
    jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker()).validate(
        payload
    )


def test_schema_rejects_unexpected_fields() -> None:
    schema = json.loads(
        Path("schemas/confidence-assessment.schema.json").read_text(encoding="utf-8")
    )
    payload = assess_confidence({"completed": True}).to_dict()
    payload["invented"] = True
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(schema).validate(payload)
