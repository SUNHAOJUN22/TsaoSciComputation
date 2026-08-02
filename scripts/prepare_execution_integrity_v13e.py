from __future__ import annotations

import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def patch_generator() -> None:
    path = ROOT / "scripts/apply_execution_integrity_v13.py"
    text = path.read_text(encoding="utf-8")
    old = r'(tmp_path / "shadow_probe.py").write_text("VALUE = 1\n", encoding="utf-8")'
    new = r'(tmp_path / "shadow_probe.py").write_text("VALUE = 1\\n", encoding="utf-8")'
    if text.count(old) != 1:
        raise SystemExit("execution-integrity generator escape anchor mismatch")
    path.write_text(text.replace(old, new, 1), encoding="utf-8", newline="\n")


def patch_types() -> None:
    runner_path = ROOT / "tsao_computation/execution/runner.py"
    runner = runner_path.read_text(encoding="utf-8")
    old_runner = """    if candidate.is_absolute() or candidate.parent != Path("."):
        found = str(candidate)
    else:
        found = shutil.which(argv0)
"""
    new_runner = """    found: str | None
    if candidate.is_absolute() or candidate.parent != Path("."):
        found = str(candidate)
    else:
        found = shutil.which(argv0)
"""
    if runner.count(old_runner) != 1:
        raise SystemExit("runner type anchor mismatch")
    runner_path.write_text(
        runner.replace(old_runner, new_runner, 1), encoding="utf-8", newline="\n"
    )

    planner_path = ROOT / "tsao_computation/orchestration/planner.py"
    planner = planner_path.read_text(encoding="utf-8")
    old_planner = "            environment=command.environment,\n"
    new_planner = "            environment=dict(command.environment),\n"
    if planner.count(old_planner) != 1:
        raise SystemExit("planner environment type anchor mismatch")
    planner_path.write_text(
        planner.replace(old_planner, new_planner, 1), encoding="utf-8", newline="\n"
    )


def patch_fail_closed_tests() -> None:
    path = ROOT / "tests/test_fail_closed_coverage_regressions.py"
    text = path.read_text(encoding="utf-8")
    import_anchor = "from tsao_computation.routing import router\n"
    import_line = (
        "from tsao_computation.security import process as process_security\n"
    )
    if import_line not in text:
        if text.count(import_anchor) != 1:
            raise SystemExit("security process import anchor mismatch")
        text = text.replace(import_anchor, import_anchor + import_line, 1)

    old = '''def test_module_probe_returns_declared_modules_when_process_cannot_start(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    modules = ("required_module",)

    def fail_to_start(*_args: object, **_kwargs: object) -> subprocess.CompletedProcess[str]:
        raise OSError("unavailable interpreter")

    monkeypatch.setattr(adapter_base.subprocess, "run", fail_to_start)
    assert adapter_base._missing_python_modules(sys.executable, modules) == modules


@pytest.mark.parametrize("stdout", ["not-json", "{}"])
def test_module_probe_fails_closed_on_malformed_output(
    monkeypatch: pytest.MonkeyPatch, stdout: str
) -> None:
    modules = ("required_module",)

    def malformed(*_args: object, **_kwargs: object) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess([], 1, stdout=stdout, stderr="")

    monkeypatch.setattr(adapter_base.subprocess, "run", malformed)
    assert adapter_base._missing_python_modules(sys.executable, modules) == modules
'''
    new = '''def test_module_probe_returns_declared_modules_when_process_cannot_start(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    modules = ("required_module",)

    def fail_to_start(*_args: object, **_kwargs: object) -> subprocess.CompletedProcess[str]:
        raise OSError("unavailable interpreter")

    monkeypatch.setattr(process_security, "_run_sanitized", fail_to_start)
    assert process_security.probe_python_modules(sys.executable, modules) == modules
    assert adapter_base._missing_python_modules(sys.executable, modules) == modules


@pytest.mark.parametrize("stdout", ["not-json", "{}"])
def test_module_probe_fails_closed_on_malformed_output(
    monkeypatch: pytest.MonkeyPatch, stdout: str
) -> None:
    modules = ("required_module",)

    def malformed(*_args: object, **_kwargs: object) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess([], 1, stdout=stdout, stderr="")

    monkeypatch.setattr(process_security, "_run_sanitized", malformed)
    assert process_security.probe_python_modules(sys.executable, modules) == modules
    assert adapter_base._missing_python_modules(sys.executable, modules) == modules
'''
    if text.count(old) != 1:
        raise SystemExit("legacy module-probe regression block mismatch")
    path.write_text(text.replace(old, new, 1), encoding="utf-8", newline="\n")


def patch_changelog() -> None:
    path = ROOT / "CHANGELOG.md"
    text = path.read_text(encoding="utf-8")
    anchor = "## Unreleased\n"
    release = """## Unreleased

## 3.0.4 — 2026-08-03

- Disabled direct execution through the legacy low-level process API; external computation now requires a sealed, hash-bound authorization created for the exact command plan.
- Bound every authorized run to the current executable SHA-256, declared input-file SHA-256 and normalized subprocess environment immediately before launch.
- Separated fixed, allowlisted read-only hardware discovery from scientific computation execution and repaired default accelerator probing on real systems.
- Routed Python-module availability probes through the sanitized environment and made adapter command-plan environments immutable.
- Added execution-integrity fault injection, machine evidence and bilingual documentation for the strengthened boundary.
"""
    if text.count(anchor) != 1:
        raise SystemExit("CHANGELOG Unreleased anchor mismatch")
    path.write_text(text.replace(anchor, release, 1), encoding="utf-8", newline="\n")


def write_report() -> None:
    (ROOT / "reports/EXECUTION_INTEGRITY_V13.md").write_text(
        """# Execution Integrity V13

This audit closes the public low-level process bypass, separates fixed read-only probes from computation execution, binds authorization to the current executable and declared input contents, and hashes the normalized subprocess environment.

External solver execution remains plan-only until a matching authorization is created through `authorize_plan`; scientific acceptance remains a separate gate.
""",
        encoding="utf-8",
        newline="\n",
    )


def main() -> int:
    patch_generator()
    runpy.run_path(str(ROOT / "scripts/apply_execution_integrity_v13.py"), run_name="__main__")
    patch_types()
    patch_fail_closed_tests()
    patch_changelog()
    (ROOT / "VERSION").write_text("3.0.4\n", encoding="utf-8", newline="\n")
    write_report()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
