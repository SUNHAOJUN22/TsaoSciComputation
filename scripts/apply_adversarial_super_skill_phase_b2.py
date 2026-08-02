from __future__ import annotations

import re
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def write(relative: str, content: str) -> None:
    path = ROOT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(content).lstrip(), encoding="utf-8", newline="\n")


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise ValueError(f"expected one {label}, found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8", newline="\n")


verify = ROOT / "scripts/verify_all.py"
text = verify.read_text(encoding="utf-8")
text = text.replace(
    'def _record_timing(label: str, command: Sequence[str], elapsed: float, mode: str) -> None:\n',
    'def _record_timing(\n    label: str, command: Sequence[str], elapsed: float, mode: str, returncode: int\n) -> None:\n',
    1,
)
text = text.replace(
    '            "mode": mode,\n',
    '            "mode": mode,\n            "returncode": returncode,\n            "status": "PASS" if returncode == 0 else "FAIL",\n',
    1,
)
old_run = '''    returncode = subprocess.run(  # nosec B603
        list(command), cwd=ROOT, env=env, check=False
    ).returncode
    _record_timing(label, command, time.perf_counter() - started, "sequential")
    return returncode
'''
new_run = '''    try:
        returncode = subprocess.run(  # nosec B603
            list(command), cwd=ROOT, env=env, check=False
        ).returncode
    except OSError:
        returncode = 127
    _record_timing(
        label,
        command,
        time.perf_counter() - started,
        "sequential",
        returncode,
    )
    return returncode
'''
if text.count(old_run) != 1:
    raise ValueError("sequential timing block not found exactly once")
text = text.replace(old_run, new_run, 1)
old_parallel = '_record_timing(result.label, result.command, result.elapsed_seconds, "parallel")\n'
new_parallel = '''_record_timing(
            result.label,
            result.command,
            result.elapsed_seconds,
            "parallel",
            result.returncode,
        )
'''
if text.count(old_parallel) != 1:
    raise ValueError("parallel timing block not found exactly once")
verify.write_text(text.replace(old_parallel, new_parallel, 1), encoding="utf-8", newline="\n")

write(
    "scripts/build_super_skill_audit.py",
    r'''
    from __future__ import annotations

    import argparse
    import json
    import re
    import statistics
    import time
    from collections.abc import Mapping
    from pathlib import Path
    from typing import Any

    from tsao_computation import __version__
    from tsao_computation.contracts import CalculationContract
    from tsao_computation.orchestration import (
        acceleration_strategies,
        build_orchestration_plan,
        execute_trusted_callable,
        list_invocations,
        methods,
    )
    from tsao_computation.registries import adapters, capabilities, workflows

    STATEMENT_COVERAGE_MIN = 95.0
    BRANCH_COVERAGE_MIN = 90.0
    REQUIRED_VERIFICATION_LABELS = frozenset(
        {
            "tests and coverage",
            "scientific reference benchmarks",
            "controlled mutation gate",
            "repository security scan",
            "source build A",
            "source build B",
            "wheel rebuild and isolated install",
            "deterministic SPDX and CycloneDX SBOMs",
            "release manifest and checksums",
        }
    )


    def _read_json(path: Path | None) -> Any:
        if path is None or not path.is_file():
            return None
        return json.loads(path.read_text(encoding="utf-8"))


    def _test_summary(path: Path | None) -> tuple[int | None, int | None]:
        if path is None or not path.is_file():
            return None, None
        text = path.read_text(encoding="utf-8")
        passed = [int(value) for value in re.findall(r"(\d+) passed", text)]
        failed = [int(value) for value in re.findall(r"(\d+) failed", text)]
        errors = [int(value) for value in re.findall(r"(\d+) errors?", text)]
        return (max(passed) if passed else None, max(failed + errors, default=0))


    def _vulnerabilities(payload: Any) -> int | None:
        if payload is None:
            return None
        records = payload if isinstance(payload, list) else payload.get("dependencies", [])
        if not isinstance(records, list):
            return None
        return sum(
            len(item.get("vulns", []))
            for item in records
            if isinstance(item, Mapping) and isinstance(item.get("vulns", []), list)
        )


    def _contract() -> CalculationContract:
        return CalculationContract(
            question="Plan a validated multiscale polymer computation",
            system={"material": "polymer", "composition": "declared"},
            conditions={"temperature_K": 300.0},
            target_observables=("transport_property",),
            workflow="molecular-dynamics",
            assumptions=("declared model",),
            acceptance_criteria={"relative_error_max": 0.05},
            model_object={"type": "periodic cell"},
            scales=("atomistic", "continuum"),
            methods=("molecular-dynamics",),
            boundary_conditions={"periodic": True},
            initial_conditions={"temperature_K": 300.0},
            parameter_sources=({"name": "parameters", "source": "declared"},),
            convergence_plan={"declared": True},
            validation_plan={"reference": "declared"},
            uncertainty_sources=("sampling", "model-form"),
            compute_resources={"gpu": "preferred", "workload": "long trajectory"},
            expected_artifacts=("trajectory", "evidence"),
            human_approval_nodes=("scientific_acceptance",),
        )


    def _median(operation: Any, loops: int) -> float:
        samples: list[float] = []
        for _ in range(7):
            started = time.perf_counter()
            for _ in range(loops):
                operation()
            samples.append((time.perf_counter() - started) / loops)
        return statistics.median(samples)


    def _verification_status(payload: Any) -> tuple[bool | None, set[str]]:
        if not isinstance(payload, Mapping):
            return None, set()
        steps = payload.get("steps", [])
        labels = {
            str(item.get("label"))
            for item in steps
            if isinstance(item, Mapping) and item.get("status") == "PASS"
        }
        passed = (
            payload.get("profile") == "all"
            and payload.get("status") == "PASS"
            and REQUIRED_VERIFICATION_LABELS <= labels
        )
        return passed, labels


    def build(
        *,
        test_log: Path | None,
        coverage_json: Path | None,
        dependency_json: Path | None,
        security_json: Path | None,
        verification_json: Path | None,
    ) -> dict[str, Any]:
        method_catalog = methods()
        invocations = list_invocations()
        strategies = acceleration_strategies()
        plan = build_orchestration_plan(_contract())
        coverage = _read_json(coverage_json)
        security = _read_json(security_json)
        verification = _read_json(verification_json)
        tests_passed, tests_failed = _test_summary(test_log)
        vulnerabilities = _vulnerabilities(_read_json(dependency_json))
        trusted = [item for item in invocations if item.trusted_local_execution]
        totals = coverage.get("totals", {}) if isinstance(coverage, Mapping) else {}
        statement_coverage = totals.get("percent_statements_covered")
        branch_coverage = totals.get("percent_branches_covered")
        findings = security.get("findings", []) if isinstance(security, Mapping) else None
        security_findings = len(findings) if isinstance(findings, list) else None
        verification_passed, verification_labels = _verification_status(verification)

        missing: list[str] = []
        failures: list[str] = []
        evidence = {
            "test_log": tests_passed is not None and tests_failed is not None,
            "coverage": isinstance(statement_coverage, (int, float))
            and isinstance(branch_coverage, (int, float)),
            "dependency_audit": vulnerabilities is not None,
            "security_scan": security_findings is not None,
            "verification_profile": verification_passed is not None,
        }
        missing.extend(name for name, present in evidence.items() if not present)
        if tests_failed not in (None, 0):
            failures.append(f"tests_failed={tests_failed}")
        if isinstance(statement_coverage, (int, float)) and statement_coverage < STATEMENT_COVERAGE_MIN:
            failures.append(f"statement_coverage<{STATEMENT_COVERAGE_MIN}")
        if isinstance(branch_coverage, (int, float)) and branch_coverage < BRANCH_COVERAGE_MIN:
            failures.append(f"branch_coverage<{BRANCH_COVERAGE_MIN}")
        if vulnerabilities not in (None, 0):
            failures.append(f"dependency_vulnerabilities={vulnerabilities}")
        if security_findings not in (None, 0):
            failures.append(f"security_findings={security_findings}")
        if verification_passed is False:
            failures.append("verification_profile_failed_or_incomplete")
        status = "FAILED" if failures else ("CANDIDATE" if missing else "VALIDATED")

        plan_seconds = _median(lambda: build_orchestration_plan(_contract()), 200)
        invocation_seconds = _median(
            lambda: execute_trusted_callable(
                "balance-check",
                {"inputs": 10.0, "outputs": 9.0, "accumulation": 1.0},
            ),
            500,
        )
        performance_reports: dict[str, Any] = {}
        for name in ("MATH_PERFORMANCE_AUDIT_V10.json", "MATH_PERFORMANCE_AUDIT_V11.json"):
            path = Path("reports") / name
            if path.is_file():
                payload = _read_json(path)
                performance_reports[name] = {
                    "status": payload.get("status"),
                    "claim_boundary": payload.get("claim_boundary"),
                    "speedups": payload.get("speedups"),
                }

        return {
            "schema_version": "1.1",
            "audit_generation": "adversarial-computation-super-skill-v2",
            "status": status,
            "validation_missing_evidence": sorted(missing),
            "validation_failures": sorted(failures),
            "version": __version__,
            "branch": "main",
            "supported_platforms": {
                "windows": "core",
                "linux": "compatible",
                "macos": "not supported or release-qualified",
            },
            "commit_binding": "Exact final commit and production workflows are recorded in GitHub Issue #61.",
            "architecture": {
                "methods": len(method_catalog),
                "method_slugs": [item.slug for item in method_catalog],
                "invocation_kinds": sorted({item.kind.value for item in invocations}),
                "invocation_targets": len(invocations),
                "trusted_local_callables": len(trusted),
                "external_plan_only_targets": len(invocations) - len(trusted),
                "capabilities": len(capabilities()),
                "adapters": len(adapters()),
                "workflows": len(workflows()),
                "acceleration_strategies": len(strategies),
                "orchestration_stages": len(plan.steps),
            },
            "execution_policy": {
                "trusted_local_callables_may_execute": True,
                "external_targets_default_to_plan_only": True,
                "external_process_execution_requires_hash_bound_authorization": True,
                "arbitrary_python_import_execution": False,
                "arbitrary_shell_execution": False,
                "remote_api_contact_by_registration": False,
                "skill_handoff_requires_available_authorized_runtime": True,
            },
            "telemetry": {
                "orchestration_plan_median_seconds": plan_seconds,
                "trusted_balance_invocation_median_seconds": invocation_seconds,
                "claim_boundary": "Same-host repository-local orchestration latency only; no external solver or GPU speedup is measured.",
            },
            "quality": {
                "tests_passed": tests_passed,
                "tests_failed": tests_failed,
                "statement_coverage_percent": statement_coverage,
                "branch_coverage_percent": branch_coverage,
                "controlled_mutation": "PASS" if "controlled mutation gate" in verification_labels else None,
                "scientific_benchmarks": "PASS" if "scientific reference benchmarks" in verification_labels else None,
                "repository_security_findings": security_findings,
                "dependency_vulnerabilities": vulnerabilities,
                "verification_profile_passed": verification_passed,
                "source_and_wheel_reproducible": (
                    verification_passed is True
                    and {"source build A", "source build B", "wheel rebuild and isolated install"}
                    <= verification_labels
                ),
            },
            "performance_evidence": performance_reports,
            "remaining_limitations": [
                "No external scientific solver, commercial license, remote API, container runtime, scheduler, GPU kernel or production HPC system is bundled or implicitly authorized.",
                "Adapter detection and command construction do not prove solver build features, numerical speedup, convergence or physical validity.",
                "Acceleration recommendations are guidance unless cited isolated evidence explicitly marks them measured.",
                "High-risk engineering or safety decisions still require expert, approval and independent-reproduction gates.",
            ],
            "claim_boundary": "The Skill computes with registered trusted local functions and plans, routes, probes, configures and evidences external functions, tools, solvers and Skills. External execution and scientific acceptance remain separate, explicit and fail-closed.",
            "temporary_branch_created": False,
            "created_pull_request": False,
        }


    def main() -> int:
        parser = argparse.ArgumentParser()
        parser.add_argument("--test-log", type=Path)
        parser.add_argument("--coverage-json", type=Path)
        parser.add_argument("--dependency-json", type=Path)
        parser.add_argument("--security-json", type=Path)
        parser.add_argument("--verification-json", type=Path)
        parser.add_argument(
            "--output",
            type=Path,
            default=Path("reports/ULTIMATE_COMPUTATION_SUPER_SKILL_AUDIT.json"),
        )
        args = parser.parse_args()
        payload = build(
            test_log=args.test_log,
            coverage_json=args.coverage_json,
            dependency_json=args.dependency_json,
            security_json=args.security_json,
            verification_json=args.verification_json,
        )
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        print(json.dumps(payload, sort_keys=True))
        return 0


    if __name__ == "__main__":
        raise SystemExit(main())
    ''',
)

ci = ROOT / ".github/workflows/ci.yml"
text = ci.read_text(encoding="utf-8")
if text.count("os: [ubuntu-latest, windows-latest, macos-latest]") != 2:
    raise ValueError("expected two CI platform matrices")
ci.write_text(
    text.replace(
        "os: [ubuntu-latest, windows-latest, macos-latest]",
        "os: [ubuntu-latest, windows-latest]",
    ),
    encoding="utf-8",
    newline="\n",
)

pyproject = ROOT / "pyproject.toml"
text = pyproject.read_text(encoding="utf-8")
text = text.replace('  "Operating System :: MacOS",\n', "")
pyproject.write_text(text, encoding="utf-8", newline="\n")

platform_files = (
    ROOT / "SKILL.md",
    ROOT / "README.md",
    ROOT / "README.zh-CN.md",
    ROOT / "docs/release.md",
    ROOT / "CHANGELOG.md",
)
replacements = {
    "Linux, macOS, or Windows": "Windows or Linux",
    "Linux, Windows, and macOS": "Windows and Linux",
    "Linux, Windows and macOS": "Windows and Linux",
    "Windows, macOS and Linux": "Windows and Linux",
    "Windows, macOS, and Linux": "Windows and Linux",
    "Ubuntu/Windows/macOS": "Ubuntu/Windows",
    "Ubuntu, Windows and macOS": "Ubuntu and Windows",
    "Ubuntu, Windows, and macOS": "Ubuntu and Windows",
    "Linux/Windows/macOS": "Windows/Linux",
    "macOS/Linux/Windows": "Windows/Linux",
}
for path in platform_files:
    text = path.read_text(encoding="utf-8")
    for old, new in replacements.items():
        text = text.replace(old, new)
    path.write_text(text, encoding="utf-8", newline="\n")

changelog = ROOT / "CHANGELOG.md"
text = changelog.read_text(encoding="utf-8")
entry = '''## 3.0.3 — 2026-08-02

- Added hash-bound, explicit authorization for all external process execution while retaining plan-only defaults for solvers, APIs, containers, schedulers and Skills.
- Made calculation contracts and registry snapshots deeply immutable and fail-closed for unknown methods, workflows, adapters and ambiguous routing.
- Bound acceleration plans to validated resource, precision, determinism, device, memory, fallback and request-hash contracts.
- Hardened audit certification so only complete zero-defect evidence can produce VALIDATED status.
- Restricted release qualification to Windows and Linux; macOS is not a supported platform or release gate.

'''
if "## 3.0.3 — 2026-08-02" not in text:
    text = text.replace("## Unreleased\n\n", "## Unreleased\n\n" + entry, 1)
changelog.write_text(text, encoding="utf-8", newline="\n")

write(
    "tests/test_adversarial_audit_evidence.py",
    r'''
    from __future__ import annotations

    import json
    from pathlib import Path

    from scripts import build_super_skill_audit


    def dump(path: Path, value: object) -> Path:
        path.write_text(json.dumps(value), encoding="utf-8")
        return path


    def evidence(tmp_path: Path, *, vulnerabilities: int = 0, security_findings: int = 0) -> dict[str, Path]:
        test_log = tmp_path / "tests.log"
        test_log.write_text("742 passed in 1.0s\n", encoding="utf-8")
        coverage = dump(
            tmp_path / "coverage.json",
            {"totals": {"percent_statements_covered": 96.0, "percent_branches_covered": 91.0}},
        )
        dependencies = dump(
            tmp_path / "dependencies.json",
            [{"name": "package", "vulns": [{} for _ in range(vulnerabilities)]}],
        )
        security = dump(
            tmp_path / "security.json",
            {"findings": [{} for _ in range(security_findings)]},
        )
        steps = [
            {"label": label, "status": "PASS", "returncode": 0}
            for label in build_super_skill_audit.REQUIRED_VERIFICATION_LABELS
        ]
        verification = dump(
            tmp_path / "verification.json",
            {"profile": "all", "status": "PASS", "steps": steps},
        )
        return {
            "test_log": test_log,
            "coverage_json": coverage,
            "dependency_json": dependencies,
            "security_json": security,
            "verification_json": verification,
        }


    def test_missing_evidence_never_self_certifies() -> None:
        payload = build_super_skill_audit.build(
            test_log=None,
            coverage_json=None,
            dependency_json=None,
            security_json=None,
            verification_json=None,
        )
        assert payload["status"] == "CANDIDATE"
        assert payload["validation_missing_evidence"]
        assert payload["quality"]["source_and_wheel_reproducible"] is False


    def test_bad_evidence_is_failed_not_validated(tmp_path: Path) -> None:
        payload = build_super_skill_audit.build(
            **evidence(tmp_path, vulnerabilities=1, security_findings=1)
        )
        assert payload["status"] == "FAILED"
        assert payload["quality"]["dependency_vulnerabilities"] == 1
        assert payload["quality"]["repository_security_findings"] == 1
        assert payload["validation_failures"]


    def test_complete_zero_defect_evidence_is_validated(tmp_path: Path) -> None:
        payload = build_super_skill_audit.build(**evidence(tmp_path))
        assert payload["status"] == "VALIDATED"
        assert payload["validation_missing_evidence"] == []
        assert payload["validation_failures"] == []
        assert payload["quality"]["source_and_wheel_reproducible"] is True
        assert payload["quality"]["controlled_mutation"] == "PASS"
        assert payload["quality"]["scientific_benchmarks"] == "PASS"
    ''',
)

write(
    "tests/test_verify_all_timing_evidence.py",
    r'''
    from __future__ import annotations

    import json
    from pathlib import Path
    from types import SimpleNamespace

    from scripts import verify_all


    def test_sequential_timing_records_success_and_failure(monkeypatch) -> None:
        results = iter((0, 7))

        def fake_run(*args, **kwargs):
            del args, kwargs
            return SimpleNamespace(returncode=next(results))

        monkeypatch.setattr(verify_all.subprocess, "run", fake_run)
        verify_all._TIMING_RECORDS.clear()
        assert verify_all.run("ok", ("tool",)) == 0
        assert verify_all.run("bad", ("tool",)) == 7
        assert [item["status"] for item in verify_all._TIMING_RECORDS] == ["PASS", "FAIL"]
        assert [item["returncode"] for item in verify_all._TIMING_RECORDS] == [0, 7]


    def test_timing_report_contains_recorded_steps(tmp_path: Path) -> None:
        verify_all._TIMING_RECORDS[:] = [
            {
                "label": "source build A",
                "command": ["python"],
                "elapsed_seconds": 1.0,
                "mode": "sequential",
                "returncode": 0,
                "status": "PASS",
            }
        ]
        output = tmp_path / "timing.json"
        verify_all._write_timing_report(output, "all", 1.1, 0)
        payload = json.loads(output.read_text(encoding="utf-8"))
        assert payload["status"] == "PASS"
        assert payload["steps"][0]["status"] == "PASS"
        assert payload["total_recorded_seconds"] == 1.0
    ''',
)

write(
    "tests/test_supported_platform_policy.py",
    r'''
    from __future__ import annotations

    from pathlib import Path

    ROOT = Path(__file__).resolve().parents[1]


    def test_release_platforms_are_windows_and_linux_only() -> None:
        ci = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
        assert "windows-latest" in ci
        assert "ubuntu-latest" in ci
        assert "macos-latest" not in ci
        pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        assert "Operating System :: MacOS" not in pyproject
        for relative in ("SKILL.md", "README.md", "README.zh-CN.md", "docs/release.md"):
            text = (ROOT / relative).read_text(encoding="utf-8")
            assert "macOS" not in text
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        assert "Windows" in skill and "Linux" in skill
    ''',
)

print("final evidence and platform governance candidate applied")
