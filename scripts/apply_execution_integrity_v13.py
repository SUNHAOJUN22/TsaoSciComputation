from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def patch_extended_tests() -> None:
    path = ROOT / "tests/test_extended.py"
    text = path.read_text(encoding="utf-8")
    old = '''@pytest.mark.parametrize("argv", [[], [""], [sys.executable, 3]])
def test_safe_run_rejects_invalid_argv(tmp_path: Path, argv: list[object]) -> None:
    with pytest.raises(SecurityError):
        safe_run(argv, cwd=tmp_path, allow_process_execution=True)


def test_safe_run_validates_timeout_cwd_and_environment(tmp_path: Path) -> None:
    with pytest.raises(SecurityError):
        safe_run([sys.executable], cwd=tmp_path, timeout=0, allow_process_execution=True)
    with pytest.raises(SecurityError):
        safe_run([sys.executable], cwd=tmp_path / "missing", allow_process_execution=True)
    result = safe_run(
        [sys.executable, "-c", "import os; print(os.environ['TSAO_TEST'])"],
        cwd=tmp_path,
        timeout=5,
        env={"TSAO_TEST": "yes"},
        allow_process_execution=True,
    )
    assert result.stdout.strip() == "yes"
'''
    new = '''@pytest.mark.parametrize("argv", [[], [""], [sys.executable, 3]])
def test_safe_run_rejects_direct_execution(tmp_path: Path, argv: list[object]) -> None:
    with pytest.raises(SecurityError, match="direct process execution is disabled"):
        safe_run(argv, cwd=tmp_path, allow_process_execution=True)


def test_authorized_plan_validates_timeout_cwd_and_environment(tmp_path: Path) -> None:
    with pytest.raises(SecurityError, match="direct process execution is disabled"):
        safe_run([sys.executable], cwd=tmp_path, timeout=0, allow_process_execution=True)
    with pytest.raises(SecurityError, match="direct process execution is disabled"):
        safe_run([sys.executable], cwd=tmp_path / "missing", allow_process_execution=True)
    with pytest.raises(SecurityError, match="unsafe subprocess environment"):
        safe_run(
            [sys.executable],
            cwd=tmp_path,
            env={"PYTHONPATH": "attacker"},
            allow_process_execution=True,
        )

    plan = CommandPlan(
        (
            sys.executable,
            "-c",
            "import os; from pathlib import Path; Path('env.txt').write_text(os.environ['TSAO_TEST'])",
        ),
        tmp_path,
        {"TSAO_TEST": "yes"},
        "test",
    )
    authorization = authorize_plan(
        plan,
        authorized_by="pytest",
        purpose="authorized environment regression",
        explicit_authorization=True,
    )
    record = run_plan(plan, authorization=authorization, timeout=5)
    assert record.completed is True
    assert (tmp_path / "env.txt").read_text(encoding="utf-8") == "yes"
'''
    if text.count(old) != 1:
        raise SystemExit("legacy safe_run test block was not found exactly once")
    path.write_text(text.replace(old, new, 1), encoding="utf-8", newline="\n")


def write_execution_integrity_tests() -> None:
    path = ROOT / "tests/test_execution_integrity_v13.py"
    path.write_text(
        '''from __future__ import annotations

import hashlib
import shutil
import sys
from pathlib import Path

import pytest

from tsao_computation.adapters.base import CommandPlan
from tsao_computation.errors import SecurityError
from tsao_computation.execution import ExecutionAuthorization, authorize_plan, run_plan
from tsao_computation.security import safe_run
from tsao_computation.security.process import probe_command_output, probe_python_modules


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_public_low_level_process_api_never_executes(tmp_path: Path) -> None:
    with pytest.raises(SecurityError, match="direct process execution is disabled"):
        safe_run(
            (sys.executable, "-c", "raise SystemExit('must not run')"),
            cwd=tmp_path,
            allow_process_execution=True,
        )


def test_execution_authorization_constructor_is_sealed() -> None:
    with pytest.raises(SecurityError, match="created by authorize_plan"):
        ExecutionAuthorization("a" * 64, "b" * 64, None, "user", "purpose", True, object())


def test_authorization_rejects_changed_input(tmp_path: Path) -> None:
    source = tmp_path / "input.dat"
    source.write_text("first", encoding="utf-8")
    plan = CommandPlan(
        (sys.executable, "-c", "print('ok')"),
        tmp_path,
        {},
        "test",
        input_sha256=_sha256(source),
        input_path=source,
    )
    authorization = authorize_plan(
        plan,
        authorized_by="pytest",
        purpose="input binding regression",
        explicit_authorization=True,
    )
    source.write_text("second", encoding="utf-8")
    with pytest.raises(SecurityError, match="input file does not match|input content changed"):
        run_plan(plan, authorization=authorization)


def test_authorization_rejects_changed_executable(tmp_path: Path) -> None:
    copied = tmp_path / Path(sys.executable).name
    shutil.copy2(sys.executable, copied)
    plan = CommandPlan((str(copied), "--version"), tmp_path, {}, "test")
    authorization = authorize_plan(
        plan,
        authorized_by="pytest",
        purpose="executable binding regression",
        explicit_authorization=True,
    )
    with copied.open("ab") as handle:
        handle.write(b"execution-integrity-mutation")
    with pytest.raises(SecurityError, match="does not match|executable content changed"):
        run_plan(plan, authorization=authorization)


def test_command_plan_environment_is_immutable(tmp_path: Path) -> None:
    plan = CommandPlan((sys.executable, "--version"), tmp_path, {"TSAO_TEST": "yes"}, "test")
    with pytest.raises(TypeError):
        plan.environment["TSAO_TEST"] = "changed"  # type: ignore[index]


def test_python_module_probe_drops_parent_pythonpath(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (tmp_path / "shadow_probe.py").write_text("VALUE = 1\n", encoding="utf-8")
    monkeypatch.setenv("PYTHONPATH", str(tmp_path))
    assert probe_python_modules(sys.executable, ("shadow_probe",)) == ("shadow_probe",)
    assert probe_python_modules(sys.executable, ("json",)) == ()
    with pytest.raises(SecurityError, match="dotted identifiers"):
        probe_python_modules(sys.executable, ("bad-name",))


def test_hardware_probe_rejects_arbitrary_executable() -> None:
    with pytest.raises(SecurityError, match="unsupported read-only probe command"):
        probe_command_output(sys.executable, ("--version",))


def test_authorized_execution_records_runtime_hashes(tmp_path: Path) -> None:
    plan = CommandPlan((sys.executable, "-c", "print('ok')"), tmp_path, {}, "test")
    authorization = authorize_plan(
        plan,
        authorized_by="pytest",
        purpose="runtime hash evidence",
        explicit_authorization=True,
    )
    record = run_plan(plan, authorization=authorization, timeout=5)
    assert record.completed is True
    assert record.executable_sha256 == authorization.executable_sha256
    assert record.input_sha256 is None
    assert len(record.authorization_sha256) == 64
''',
        encoding="utf-8",
        newline="\n",
    )


def normalize_core_test() -> None:
    path = ROOT / "tests/test_core.py"
    text = path.read_text(encoding="utf-8")
    text = text.replace(
        'CommandPlan([sys.executable, "-c", "print(7)"], tmp_path, {}, "test")',
        'CommandPlan((sys.executable, "-c", "print(7)"), tmp_path, {}, "test")',
    )
    path.write_text(text, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    patch_extended_tests()
    write_execution_integrity_tests()
    normalize_core_test()
