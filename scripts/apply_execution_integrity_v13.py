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


def patch_audit_generator() -> None:
    path = ROOT / "scripts/build_super_skill_audit.py"
    text = path.read_text(encoding="utf-8")
    replacements = {
        '"schema_version": "1.1"': '"schema_version": "1.2"',
        '"audit_generation": "adversarial-computation-super-skill-v2"': '"audit_generation": "execution-integrity-v13"',
        '"commit_binding": "Exact final commit and production workflows are recorded in GitHub Issue #61."': '"commit_binding": "Exact final commit and production workflows are recorded in GitHub Issue #85."',
    }
    for old, new in replacements.items():
        if text.count(old) != 1:
            raise SystemExit(f"audit replacement anchor mismatch: {old}")
        text = text.replace(old, new, 1)
    anchor = '            "external_process_execution_requires_hash_bound_authorization": True,\n'
    addition = anchor + (
        '            "direct_low_level_process_execution_disabled": True,\n'
        '            "read_only_probe_commands_allowlisted": True,\n'
        '            "authorization_binds_executable_sha256": True,\n'
        '            "authorization_binds_input_sha256": True,\n'
        '            "python_module_probes_use_sanitized_environment": True,\n'
    )
    if text.count(anchor) != 1:
        raise SystemExit("execution-policy audit anchor mismatch")
    path.write_text(text.replace(anchor, addition, 1), encoding="utf-8", newline="\n")


def patch_documentation() -> None:
    english_path = ROOT / "README.md"
    english = english_path.read_text(encoding="utf-8")
    english_anchor = (
        "Acceleration guidance covers algorithm, memory, backend, execution and model-reduction choices. "
        "A recommendation is not presented as measured speedup unless isolated machine evidence says so."
    )
    english_note = (
        "\n\nExecution integrity is fail-closed: the legacy low-level process API never executes, "
        "hardware probes are restricted to fixed read-only commands, and every authorized external run "
        "is rebound to the current executable and declared input SHA-256 before launch."
    )
    if english_note.strip() not in english:
        if english_anchor not in english:
            raise SystemExit("English README execution-integrity anchor missing")
        english = english.replace(english_anchor, english_anchor + english_note, 1)
        english_path.write_text(english, encoding="utf-8", newline="\n")

    chinese_path = ROOT / "README.zh-CN.md"
    chinese = chinese_path.read_text(encoding="utf-8")
    chinese_anchor = "加速建议覆盖算法、内存、后端、执行方式和降阶模型；只有隔离机器证据明确标注实测时，才会表述为实测加速。"
    chinese_note = (
        "\n\n执行完整性采用缺项拒绝推进：旧低层进程接口永久禁止直接执行，硬件探测仅允许固定只读命令；"
        "每次外部执行在启动前都会重新绑定当前可执行文件与声明输入文件的 SHA-256。"
    )
    if chinese_note.strip() not in chinese:
        if chinese_anchor not in chinese:
            raise SystemExit("Chinese README execution-integrity anchor missing")
        chinese = chinese.replace(chinese_anchor, chinese_anchor + chinese_note, 1)
        chinese_path.write_text(chinese, encoding="utf-8", newline="\n")

    skill_path = ROOT / "SKILL.md"
    skill = skill_path.read_text(encoding="utf-8")
    skill_anchor = (
        "Only registered trusted repository-local callables may execute through this interface. "
        "Adapters, modules, CLI tools, APIs, containers, schedulers, commercial solvers and other Skills "
        "remain plan-only until availability, authorization, input/output contracts and evidence requirements are satisfied."
    )
    skill_note = (
        "\n\nDirect low-level subprocess execution is disabled. Read-only hardware discovery is command-allowlisted, "
        "and authorized external execution must revalidate the executable and declared input content hashes immediately before launch."
    )
    if skill_note.strip() not in skill:
        if skill_anchor not in skill:
            raise SystemExit("SKILL execution-integrity anchor missing")
        skill = skill.replace(skill_anchor, skill_anchor + skill_note, 1)
        skill_path.write_text(skill, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    patch_extended_tests()
    write_execution_integrity_tests()
    normalize_core_test()
    patch_audit_generator()
    patch_documentation()
