from __future__ import annotations

import sys
from pathlib import Path

import pytest

from tsao_computation.adapters import get_adapter, probe_all
from tsao_computation.contracts import CalculationContract, HandoffRecord
from tsao_computation.errors import ContractError, SecurityError, StateTransitionError
from tsao_computation.project import initialize_project, validate_project
from tsao_computation.provenance import append_event, read_events
from tsao_computation.repository_audit import audit_repository
from tsao_computation.routing import route_question
from tsao_computation.security import atomic_write_text, confined_path, safe_run
from tsao_computation.state import ScientificStateMachine
from tsao_computation.uncertainty import combine_independent
from tsao_computation.validation import (
    acceptance_gate,
    balance_check,
    convergence_check,
    finite_values,
    unit_known,
)
from tsao_computation.workflows import WorkflowEngine


@pytest.mark.integration
def test_001_contract_roundtrip():
    c = CalculationContract("q", {"molecule": "H2"}, {"temperature": 298}, ("energy",))
    assert CalculationContract.from_dict(c.to_dict()) == c


@pytest.mark.integration
def test_002_contract_missing():
    with pytest.raises(ContractError):
        CalculationContract.from_dict({})


@pytest.mark.integration
def test_003_contract_empty_observable():
    with pytest.raises(ContractError):
        CalculationContract("q", {"x": 1}, {}, ())


@pytest.mark.integration
def test_004_handoff_valid():
    assert (
        HandoffRecord(
            "a", "b", "q", 1, "1", {}, "r", 0, 0, "d", "identity", "validated"
        ).validation_status
        == "validated"
    )


@pytest.mark.integration
def test_005_handoff_invalid():
    with pytest.raises(ContractError):
        HandoffRecord("a", "b", "q", 1, "1", {}, "r", 0, 0, "d", "identity", "accepted")


@pytest.mark.integration
def test_006_state_happy_path():
    m = ScientificStateMachine()
    for s in (
        "planned",
        "prepared",
        "submitted",
        "running",
        "completed",
        "parsed",
        "converged",
        "validated",
        "accepted",
    ):
        m.transition(s, evidence=s)
    assert m.state == "accepted" and len(m.events) == 9


@pytest.mark.integration
def test_007_state_skip_rejected():
    with pytest.raises(StateTransitionError):
        ScientificStateMachine().transition("accepted", evidence="x")


@pytest.mark.integration
def test_008_state_evidence_required():
    with pytest.raises(StateTransitionError):
        ScientificStateMachine().transition("planned", evidence="")


@pytest.mark.integration
def test_009_route_quantum():
    assert route_question("ORCA molecular frequency calculation").workflow == "quantum-chemistry"


@pytest.mark.integration
def test_010_route_cfd():
    assert route_question("OpenFOAM CFD turbulence heat transfer").workflow == "cfd"


@pytest.mark.integration
def test_011_route_process():
    assert route_question("Aspen process flowsheet recycle").workflow == "process-simulation"


@pytest.mark.integration
def test_012_route_fallback():
    assert route_question("ambiguous scientific request").workflow == "scale-selection"


@pytest.mark.integration
def test_013_numerical_finite():
    assert finite_values([1, 2, 3]) and (not finite_values([1, float("nan")]))


@pytest.mark.integration
def test_014_convergence():
    assert convergence_check([1, 1.001], absolute_tolerance=0.01)["passed"] is True


@pytest.mark.integration
def test_015_balance():
    assert balance_check(10, 9, 1)["passed"] is True


@pytest.mark.integration
def test_016_units():
    assert unit_known("MPa") and (not unit_known("banana"))


@pytest.mark.integration
def test_017_acceptance_fail_closed():
    assert acceptance_gate({"completed": True})["accepted"] is False


@pytest.mark.integration
def test_018_acceptance_pass():
    r = {
        k: True
        for k in (
            "completed",
            "parsed",
            "converged",
            "physically_validated",
            "uncertainty_quantified",
            "applicability_confirmed",
            "evidence_bound",
        )
    }
    assert acceptance_gate(r)["accepted"] is True


@pytest.mark.integration
def test_019_uncertainty():
    assert combine_independent(3, 4) == 5


@pytest.mark.integration
def test_020_confined_path(tmp_path):
    assert confined_path(tmp_path, "a/b").is_relative_to(tmp_path)


@pytest.mark.integration
def test_021_confined_escape(tmp_path):
    with pytest.raises(SecurityError):
        confined_path(tmp_path, "../x")


@pytest.mark.durability
def test_022_atomic_write(tmp_path):
    p = tmp_path / "x"
    atomic_write_text(p, "a")
    atomic_write_text(p, "b")
    assert p.read_text() == "b"


@pytest.mark.durability
def test_023_safe_process(tmp_path):
    r = safe_run([sys.executable, "-c", "print(7)"], cwd=tmp_path, timeout=5)
    assert r.returncode == 0 and r.stdout.strip() == "7"


@pytest.mark.durability
def test_024_project_init(tmp_path):
    p = initialize_project(tmp_path, name="demo", question="q")
    assert validate_project(p) == []


@pytest.mark.durability
def test_025_ledger(tmp_path):
    p = tmp_path / "e.jsonl"
    append_event(p, {"kind": "x"})
    assert read_events(p)[0]["kind"] == "x"


def test_026_adapter_registry():
    assert get_adapter("orca").slug == "orca" and len(probe_all(2)) == 27


def test_027_workflow_engine():
    c = CalculationContract("OpenFOAM flow", {"domain": "pipe"}, {}, ("pressure_drop",))
    assert WorkflowEngine().select(c)["slug"] == "cfd"


def test_028_repository_audit():
    assert audit_repository(Path("."))["passed"] is True
