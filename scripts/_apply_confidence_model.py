from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def write(relative: str, content: str) -> None:
    path = ROOT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if new in text:
        return
    if old not in text:
        raise RuntimeError(f"expected anchor not found in {path.relative_to(ROOT)}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def main() -> int:
    write(
        "tsao_computation/validation/confidence.py",
        '''from __future__ import annotations

from collections.abc import Mapping
from dataclasses import asdict, dataclass
from typing import Any

LEVEL_ORDER = ("C0", "C1", "C2", "C3", "C4", "C5")
LEVEL_REQUIREMENTS: dict[str, tuple[str, ...]] = {
    "C0": ("completed",),
    "C1": ("completed", "parsed", "converged"),
    "C2": ("completed", "parsed", "converged", "physically_validated"),
    "C3": (
        "completed",
        "parsed",
        "converged",
        "physically_validated",
        "uncertainty_quantified",
        "applicability_confirmed",
        "evidence_bound",
    ),
    "C4": (
        "completed",
        "parsed",
        "converged",
        "physically_validated",
        "uncertainty_quantified",
        "applicability_confirmed",
        "evidence_bound",
        "expert_reviewed",
        "approvals",
    ),
    "C5": (
        "completed",
        "parsed",
        "converged",
        "physically_validated",
        "uncertainty_quantified",
        "applicability_confirmed",
        "evidence_bound",
        "expert_reviewed",
        "approvals",
        "decision_scope_confirmed",
        "safety_review_completed",
        "independent_reproduction",
    ),
}

CLAIM_BOUNDARIES = {
    "UNASSESSED": "No completed result is available; no scientific claim is supported.",
    "C0": "Process completion only; parsing, convergence, and scientific validity are not established.",
    "C1": "Numerically completed and converged; physical validity and applicability are not established.",
    "C2": "Numerical and physical checks passed; uncertainty and applicability remain incomplete.",
    "C3": "Research evidence is bounded by quantified uncertainty and applicability; expert acceptance is not established.",
    "C4": "Expert-reviewed scientific acceptance; engineering or safety-critical authorization is not implied.",
    "C5": "Decision scope, safety review, and independent reproduction are recorded; use remains limited to the documented applicability domain.",
}


@dataclass(frozen=True, slots=True)
class ConfidenceAssessment:
    schema_version: str
    level: str
    level_rank: int
    satisfied_requirements: tuple[str, ...]
    next_level: str | None
    missing_for_next: tuple[str, ...]
    engineering_decision_ready: bool
    claim_boundary: str

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["satisfied_requirements"] = list(self.satisfied_requirements)
        payload["missing_for_next"] = list(self.missing_for_next)
        return payload


def _valid_approvals(value: object) -> bool:
    return (
        isinstance(value, (list, tuple))
        and bool(value)
        and all(isinstance(item, str) and bool(item.strip()) for item in value)
    )


def _requirement_satisfied(record: Mapping[str, Any], requirement: str) -> bool:
    if requirement == "approvals":
        return _valid_approvals(record.get(requirement))
    return record.get(requirement) is True


def assess_confidence(record: Mapping[str, Any]) -> ConfidenceAssessment:
    if not isinstance(record, Mapping):
        raise TypeError("confidence input must be a mapping")

    level = "UNASSESSED"
    satisfied: tuple[str, ...] = ()
    for candidate in LEVEL_ORDER:
        requirements = LEVEL_REQUIREMENTS[candidate]
        if all(_requirement_satisfied(record, item) for item in requirements):
            level = candidate
            satisfied = requirements
        else:
            break

    rank = LEVEL_ORDER.index(level) if level in LEVEL_ORDER else -1
    next_level = LEVEL_ORDER[rank + 1] if rank + 1 < len(LEVEL_ORDER) else None
    missing = (
        tuple(
            item
            for item in LEVEL_REQUIREMENTS[next_level]
            if not _requirement_satisfied(record, item)
        )
        if next_level is not None
        else ()
    )
    return ConfidenceAssessment(
        schema_version="1.0",
        level=level,
        level_rank=rank,
        satisfied_requirements=satisfied,
        next_level=next_level,
        missing_for_next=missing,
        engineering_decision_ready=level == "C5",
        claim_boundary=CLAIM_BOUNDARIES[level],
    )
''',
    )

    init_path = ROOT / "tsao_computation" / "validation" / "__init__.py"
    write(
        "tsao_computation/validation/__init__.py",
        '''from .acceptance import acceptance_gate
from .confidence import ConfidenceAssessment, assess_confidence
from .numerical import convergence_check, finite_values
from .physical import balance_check, unit_known

__all__ = [
    "finite_values",
    "convergence_check",
    "balance_check",
    "unit_known",
    "acceptance_gate",
    "ConfidenceAssessment",
    "assess_confidence",
]
''',
    )

    write(
        "schemas/confidence-assessment.schema.json",
        json.dumps(
            {
                "$id": "https://github.com/SUNHAOJUN22/TsaoSciComputation/schemas/confidence-assessment.schema.json",
                "$schema": "https://json-schema.org/draft/2020-12/schema",
                "title": "Scientific confidence assessment",
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "schema_version",
                    "level",
                    "level_rank",
                    "satisfied_requirements",
                    "next_level",
                    "missing_for_next",
                    "engineering_decision_ready",
                    "claim_boundary",
                ],
                "properties": {
                    "schema_version": {"const": "1.0"},
                    "level": {"enum": ["UNASSESSED", "C0", "C1", "C2", "C3", "C4", "C5"]},
                    "level_rank": {"type": "integer", "minimum": -1, "maximum": 5},
                    "satisfied_requirements": {
                        "type": "array",
                        "items": {"type": "string", "minLength": 1},
                        "uniqueItems": True,
                    },
                    "next_level": {
                        "oneOf": [
                            {"enum": ["C0", "C1", "C2", "C3", "C4", "C5"]},
                            {"type": "null"},
                        ]
                    },
                    "missing_for_next": {
                        "type": "array",
                        "items": {"type": "string", "minLength": 1},
                        "uniqueItems": True,
                    },
                    "engineering_decision_ready": {"type": "boolean"},
                    "claim_boundary": {"type": "string", "minLength": 20},
                },
                "allOf": [
                    {
                        "if": {"properties": {"level": {"const": "C5"}}, "required": ["level"]},
                        "then": {
                            "properties": {
                                "engineering_decision_ready": {"const": True},
                                "next_level": {"type": "null"},
                                "missing_for_next": {"maxItems": 0},
                            }
                        },
                    },
                    {
                        "if": {
                            "properties": {
                                "level": {"enum": ["UNASSESSED", "C0", "C1", "C2", "C3", "C4"]}
                            },
                            "required": ["level"],
                        },
                        "then": {"properties": {"engineering_decision_ready": {"const": False}}},
                    },
                ],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )

    write(
        "docs/scientific-confidence.md",
        '''# Scientific confidence levels

TsaoSciComputation uses a fail-closed C0–C5 scale. The scale records the highest evidence level actually satisfied; it does not infer missing evidence from a successful process exit, parser result, or solver claim.

| Level | Minimum evidence | Permitted interpretation |
|---|---|---|
| UNASSESSED | No completed result | No scientific claim. |
| C0 | Completed | Process completion only. |
| C1 | Parsed and numerically converged | Numerical result only; physical validity is not established. |
| C2 | Physical validation added | Numerical and physical checks passed; uncertainty is incomplete. |
| C3 | Uncertainty, applicability, and evidence lineage added | Bounded research evidence; no expert acceptance is implied. |
| C4 | Named expert review and structured approvals added | Expert-reviewed scientific acceptance; no engineering authorization is implied. |
| C5 | Decision scope, safety review, and independent reproduction added | Engineering-decision readiness only within the documented applicability domain. |

The assessment is sequential. A record cannot reach C3 by supplying uncertainty while omitting convergence, and malformed or empty approvals cannot satisfy C4. C5 is deliberately strict and remains separate from ordinary scientific publication.

```python
from tsao_computation.validation import assess_confidence

assessment = assess_confidence(record)
print(assessment.to_dict())
```

Machine-readable assessments validate against `schemas/confidence-assessment.schema.json`. High-risk reactor, control, runaway, digital-twin, plant-safety, and commercial decisions still require qualified domain governance outside this software.
''',
    )

    validation_path = ROOT / "docs" / "scientific-validation.md"
    validation = validation_path.read_text(encoding="utf-8")
    confidence_section = '''

## Result confidence

Reference benchmarks test internal analytical, conservation, and invariant behavior. Individual calculation results are separately assessed using the fail-closed [C0–C5 confidence model](scientific-confidence.md); benchmark success does not automatically raise a user result to any confidence level.
'''
    if "## Result confidence" not in validation:
        validation_path.write_text(validation.rstrip() + confidence_section + "\n", encoding="utf-8")

    write(
        "tests/test_confidence_model.py",
        '''from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest

from tsao_computation.validation import assess_confidence


def evidence_through_c5() -> dict[str, object]:
    return {
        "completed": True,
        "parsed": True,
        "converged": True,
        "physically_validated": True,
        "uncertainty_quantified": True,
        "applicability_confirmed": True,
        "evidence_bound": True,
        "expert_reviewed": True,
        "approvals": ["Dr. Reviewer — domain review"],
        "decision_scope_confirmed": True,
        "safety_review_completed": True,
        "independent_reproduction": True,
    }


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
        assert assess_confidence(candidate).level == level


def test_c5_requires_all_decision_governance_evidence() -> None:
    assessment = assess_confidence(evidence_through_c5())
    assert assessment.level == "C5"
    assert assessment.engineering_decision_ready is True
    assert assessment.next_level is None
    assert assessment.missing_for_next == ()


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
    schema = json.loads(Path("schemas/confidence-assessment.schema.json").read_text(encoding="utf-8"))
    payload = assess_confidence(evidence_through_c5()).to_dict()
    jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker()).validate(payload)


def test_schema_rejects_unexpected_fields() -> None:
    schema = json.loads(Path("schemas/confidence-assessment.schema.json").read_text(encoding="utf-8"))
    payload = assess_confidence({"completed": True}).to_dict()
    payload["invented"] = True
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(schema).validate(payload)
''',
    )

    readme = ROOT / "README.md"
    replace_once(
        readme,
        "[Scientific validation](docs/scientific-validation.md) · [Architecture]",
        "[Scientific validation](docs/scientific-validation.md) · [Confidence](docs/scientific-confidence.md) · [Architecture]",
    )
    text = readme.read_text(encoding="utf-8")
    row = "| Scientific reference benchmarks | 8/8 passed |\n"
    if "| Scientific confidence model |" not in text:
        if row not in text:
            raise RuntimeError("English README scientific benchmark row not found")
        text = text.replace(row, row + "| Scientific confidence model | C0–C5 fail-closed |\n", 1)
    readme.write_text(text, encoding="utf-8")

    chinese = ROOT / "README.zh-CN.md"
    replace_once(
        chinese,
        "[科学验证](docs/scientific-validation.md) · [架构]",
        "[科学验证](docs/scientific-validation.md) · [可信等级](docs/scientific-confidence.md) · [架构]",
    )
    text = chinese.read_text(encoding="utf-8")
    row = "| 科学参考基准 | 8/8 通过 |\n"
    if "| 科学可信等级 |" not in text:
        if row not in text:
            raise RuntimeError("Chinese README scientific benchmark row not found")
        text = text.replace(row, row + "| 科学可信等级 | C0–C5，缺项拒绝升级 |\n", 1)
    chinese.write_text(text, encoding="utf-8")

    changelog = ROOT / "CHANGELOG.md"
    text = changelog.read_text(encoding="utf-8")
    heading = "## 3.0.2 — 2026-07-24\n\n"
    bullet = "- Added a machine-readable, fail-closed C0–C5 scientific-confidence assessment with sequential evidence requirements, JSON Schema validation, and explicit engineering-decision boundaries.\n"
    if bullet not in text:
        if heading not in text:
            raise RuntimeError("v3.0.2 changelog heading not found")
        text = text.replace(heading, heading + bullet, 1)
    changelog.write_text(text, encoding="utf-8")

    release = ROOT / "docs" / "releases" / "v3.0.2.md"
    text = release.read_text(encoding="utf-8")
    anchor = "## Highlights\n\n"
    bullet = "- Adds a machine-readable, fail-closed C0–C5 result-confidence model that separates completion, convergence, physical validation, bounded research evidence, expert acceptance, and engineering-decision readiness.\n"
    if bullet not in text:
        if anchor not in text:
            raise RuntimeError("v3.0.2 release highlights heading not found")
        text = text.replace(anchor, anchor + bullet, 1)
    release.write_text(text, encoding="utf-8")

    print(json.dumps({"confidence_model": "C0-C5", "tests_added": 8}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
