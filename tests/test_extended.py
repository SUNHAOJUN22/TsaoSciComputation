from __future__ import annotations

import json
import runpy
import sys
from pathlib import Path

import pytest

from tsao_computation import cli
from tsao_computation.adapters import get_adapter, probe_all
from tsao_computation.adapters.base import Adapter, CommandPlan
from tsao_computation.contracts import CalculationContract
from tsao_computation.errors import ContractError, SecurityError, StateTransitionError
from tsao_computation.execution import run_plan
from tsao_computation.project import initialize_project, validate_project
from tsao_computation.provenance import read_events
from tsao_computation.provenance.manifest import file_manifest
from tsao_computation.registries import clear_registry_caches
from tsao_computation.registries.loader import _load
from tsao_computation.routing import route_question
from tsao_computation.security import safe_run
from tsao_computation.security.process import _subprocess_environment
from tsao_computation.state import ScientificStateMachine
from tsao_computation.uncertainty import UncertaintyBudget, combine_independent
from tsao_computation.validation import acceptance_gate, convergence_check
from tsao_computation.workflows import WorkflowEngine


def test_adapter_build_command_and_parse(tmp_path: Path) -> None:
    source = tmp_path / "input.inp"
    source.write_text("data", encoding="utf-8")
    adapter = get_adapter("orca")
    plan = adapter.build_command(source, executable=sys.executable)
    assert plan.argv == (sys.executable, "input.inp")
    assert plan.cwd == tmp_path.resolve()
    parsed = adapter.parse("Normal termination; converged")
    assert parsed["completed"] is True
    assert parsed["converged"] is True
    assert parsed["validated"] is False


def test_adapter_build_rejects_missing_input(tmp_path: Path) -> None:
    with pytest.raises(ContractError):
        get_adapter("orca").build_command(tmp_path / "missing")


def test_adapter_build_rejects_unavailable(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    source = tmp_path / "input.inp"
    source.write_text("data", encoding="utf-8")
    adapter = Adapter({"slug": "none", "executables": ["definitely-not-a-real-executable"]})
    monkeypatch.setattr("shutil.which", lambda _: None)
    assert adapter.probe().available is False
    with pytest.raises(ContractError):
        adapter.build_command(source)


def test_adapter_unknown_and_worker_floor() -> None:
    with pytest.raises(KeyError):
        get_adapter("missing")
    assert len(probe_all(0)) == 27


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"question": "", "system": {"x": 1}, "target_observables": ("x",)}, "question"),
        ({"question": "q", "system": {}, "target_observables": ("x",)}, "system"),
        ({"question": "q", "system": {"x": 1}, "target_observables": ("",)}, "observables"),
    ],
)
def test_contract_rejects_invalid_fields(kwargs: dict[str, object], message: str) -> None:
    with pytest.raises(ContractError, match=message):
        CalculationContract(conditions={}, **kwargs)


def test_execution_plan_success_and_failure(tmp_path: Path) -> None:
    ok = CommandPlan((sys.executable, "-c", "print('ok')"), tmp_path, {}, "test")
    record = run_plan(ok, timeout=5)
    assert record.completed is True
    assert record.returncode == 0
    assert len(record.stdout_sha256) == 64
    failed = CommandPlan((sys.executable, "-c", "raise SystemExit(3)"), tmp_path, {}, "test")
    failed_record = run_plan(failed, timeout=5)
    assert failed_record.completed is False
    assert failed_record.returncode == 3


@pytest.mark.parametrize("argv", [[], [""], [sys.executable, 3]])
def test_safe_run_rejects_invalid_argv(tmp_path: Path, argv: list[object]) -> None:
    with pytest.raises(SecurityError):
        safe_run(argv, cwd=tmp_path)


def test_safe_run_validates_timeout_cwd_and_environment(tmp_path: Path) -> None:
    with pytest.raises(SecurityError):
        safe_run([sys.executable], cwd=tmp_path, timeout=0)
    with pytest.raises(SecurityError):
        safe_run([sys.executable], cwd=tmp_path / "missing")
    result = safe_run(
        [sys.executable, "-c", "import os; print(os.environ['TSAO_TEST'])"],
        cwd=tmp_path,
        timeout=5,
        env={"TSAO_TEST": "yes"},
    )
    assert result.stdout.strip() == "yes"


def test_subprocess_environment_is_minimal_on_posix() -> None:
    parent = {
        "PATH": "/usr/bin",
        "HOME": "/home/researcher",
        "TMPDIR": "/tmp/tsao",
        "LANG": "ja_JP.UTF-8",
        "SECRET_TOKEN": "must-not-leak",
    }
    environment = _subprocess_environment(
        {"LANG": "C", "TSAO_EXPLICIT": "yes"},
        parent=parent,
        platform_name="posix",
    )
    assert environment == {
        "PATH": "/usr/bin",
        "HOME": "/home/researcher",
        "TMPDIR": "/tmp/tsao",
        "LANG": "C",
        "TSAO_EXPLICIT": "yes",
    }


def test_subprocess_environment_preserves_windows_bootstrap_state() -> None:
    parent = {
        "Path": r"C:\Windows\System32",
        "SystemRoot": r"C:\Windows",
        "windir": r"C:\Windows",
        "ComSpec": r"C:\Windows\System32\cmd.exe",
        "PATHEXT": ".COM;.EXE;.BAT;.CMD",
        "TEMP": r"C:\Temp",
        "TMP": r"C:\Temp",
        "SECRET_TOKEN": "must-not-leak",
    }
    environment = _subprocess_environment(
        {"path": r"D:\ScientificTools", "TSAO_EXPLICIT": "yes"},
        parent=parent,
        platform_name="nt",
    )
    assert environment["SYSTEMROOT"] == r"C:\Windows"
    assert environment["WINDIR"] == r"C:\Windows"
    assert environment["COMSPEC"] == r"C:\Windows\System32\cmd.exe"
    assert environment["TEMP"] == r"C:\Temp"
    assert environment["path"] == r"D:\ScientificTools"
    assert environment["TSAO_EXPLICIT"] == "yes"
    assert "PATH" not in environment
    assert "SECRET_TOKEN" not in environment


def test_project_validation_errors(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        initialize_project(tmp_path, name="bad name", question="q")
    with pytest.raises(ValueError):
        initialize_project(tmp_path, name="valid", question=" ")
    target = initialize_project(tmp_path, name="valid", question="q")
    (target / "tasks").rmdir()
    (target / "events.jsonl").unlink()
    assert validate_project(target) == ["missing directory: tasks", "missing file: events.jsonl"]


def test_manifest_and_registry_cache(tmp_path: Path) -> None:
    (tmp_path / "a.txt").write_text("a", encoding="utf-8")
    (tmp_path / "__pycache__").mkdir()
    (tmp_path / "__pycache__" / "x.pyc").write_bytes(b"x")
    records = file_manifest(tmp_path)
    assert [record["path"] for record in records] == ["a.txt"]
    clear_registry_caches()
    assert len(_load("capabilities.json")) == 164
    with pytest.raises(ValueError):
        _load("../outside.json")


def test_routing_empty_and_explanation() -> None:
    with pytest.raises(ValueError):
        route_question(" ")
    decision = route_question("LAMMPS polymer molecular dynamics")
    assert decision.score > 0
    assert decision.matched_terms
    assert len(decision.alternatives) == 3


def test_state_invalid_initial_and_can_transition() -> None:
    with pytest.raises(StateTransitionError):
        ScientificStateMachine("unknown")
    machine = ScientificStateMachine()
    assert machine.can_transition("planned") is True
    assert machine.can_transition("accepted") is False


def test_uncertainty_budget_and_invalid_components() -> None:
    assert UncertaintyBudget(3, 4, 0, "K").combined == 5
    with pytest.raises(ValueError):
        UncertaintyBudget(-1, 0, 0, "K")
    with pytest.raises(ValueError):
        combine_independent()


def test_validation_edge_cases() -> None:
    assert convergence_check([1.0], 0.1)["converged"] is False
    with pytest.raises(ValueError):
        convergence_check([1.0, 1.0], 0)
    with pytest.raises(ValueError):
        acceptance_gate({"completed": True}, required=("",))


def test_workflow_engine_select_and_unknown() -> None:
    engine = WorkflowEngine()
    contract = CalculationContract("Use DFT", {"material": "Si"}, {}, ("energy",))
    assert engine.select(contract)["slug"] == "electronic-structure"
    with pytest.raises(KeyError):
        engine.get("missing")


def test_cli_commands_and_main(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    contract_path = tmp_path / "contract.json"
    contract_path.write_text(
        json.dumps(
            {
                "question": "Use DFT",
                "system": {"material": "Si"},
                "conditions": {},
                "target_observables": ["energy"],
            }
        ),
        encoding="utf-8",
    )
    assert cli.main(["route", "Use DFT"]) == 0
    assert cli.main(["validate-contract", str(contract_path), "--strict"]) == 0
    assert cli.main(["probe"]) == 0
    output = capsys.readouterr().out
    assert "electronic-structure" in output
    assert "valid" in output
    assert "adapters" in output


def test_module_entrypoint(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "argv", ["tsao-computation", "route", "Use MD"])
    with pytest.raises(SystemExit) as error:
        runpy.run_module("tsao_computation", run_name="__main__")
    assert error.value.code == 0
