from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.build_examples import SCENARIOS
from tsao_computation.cli import main
from tsao_computation.contracts import CalculationContract

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    "organic-dft",
    "surface-neb",
    "protein-md",
    "polymer-carbon-black",
    "polymerization-pbe",
    "pp-percolation",
    "extrusion-cfd",
    "cable-fem",
    "polymer-process",
    "aspen-dynamic",
    "dft-md-cfd",
    "failure-gate",
}


def test_required_scenario_set_is_exact() -> None:
    assert set(SCENARIOS) == EXPECTED


def test_every_scenario_contract_is_preflight_ready() -> None:
    for name in sorted(EXPECTED):
        path = ROOT / "examples" / name / "contract.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        contract = CalculationContract.from_dict(payload)
        contract.assert_ready_for_preflight()
        assert "example_observable" not in contract.target_observables
        assert contract.workflow


def test_every_scenario_explains_preparation_only_boundary() -> None:
    for name in sorted(EXPECTED):
        text = (ROOT / "examples" / name / "README.md").read_text(encoding="utf-8")
        assert "does not claim" in text
        assert "validate-contract" in text
        assert "--strict" in text


@pytest.mark.parametrize("name", sorted(EXPECTED))
def test_scenario_contracts_build_real_plans_without_external_execution(
    name: str, capsys: pytest.CaptureFixture[str]
) -> None:
    path = ROOT / "examples" / name / "contract.json"
    assert main(["plan", str(path), "--strict"]) == 0
    plan = json.loads(capsys.readouterr().out)
    assert plan["workflow"] == SCENARIOS[name]["workflow"]
    assert [method["slug"] for method in plan["methods"]] == SCENARIOS[name]["methods"]
    assert len(plan["steps"]) == 9
    assert "External" in plan["claim_boundary"]
