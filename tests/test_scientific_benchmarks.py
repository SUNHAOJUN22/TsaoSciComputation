from __future__ import annotations

import json
from pathlib import Path

import pytest

from tsao_computation.validation.scientific_benchmarks import assess, run_all, write_report


def test_scientific_reference_suite_passes() -> None:
    results = run_all()
    assert len(results) == 8
    assert len({result.benchmark_id for result in results}) == 8
    assert all(result.passed for result in results)
    assert {result.domain for result in results} >= {
        "heat-transfer",
        "fluid-dynamics",
        "reaction-engineering",
        "molecular-dynamics",
        "polymer-statistical-mechanics",
        "electrostatics",
        "multiphysics",
    }


def test_scientific_report_is_deterministic(tmp_path: Path) -> None:
    first = tmp_path / "first.json"
    second = tmp_path / "second.json"
    first_payload = write_report(first)
    second_payload = write_report(second)
    assert first.read_bytes() == second.read_bytes()
    assert first_payload == second_payload
    payload = json.loads(first.read_text(encoding="utf-8"))
    assert payload["passed"] == 8
    assert payload["failed"] == 0
    assert "no third-party solver execution" in payload["claim_boundary"]


@pytest.mark.parametrize(
    ("observed", "expected", "tolerance"),
    [
        (float("nan"), 0.0, 1.0),
        (0.0, float("inf"), 1.0),
        (0.0, 0.0, -1.0),
    ],
)
def test_invalid_benchmark_values_fail_closed(
    observed: float, expected: float, tolerance: float
) -> None:
    with pytest.raises(ValueError):
        assess("invalid", "test", observed, expected, tolerance, "invalid")
