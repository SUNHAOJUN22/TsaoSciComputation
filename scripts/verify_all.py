from __future__ import annotations

import argparse
import json
import os
import subprocess  # nosec B404
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable
CLAIM_BOUNDARY = (
    "This validates local orchestration, contracts, deterministic evidence and packaging. "
    "It does not claim external solver execution or production HPC performance."
)
_TIMING_RECORDS: list[dict[str, object]] = []


@dataclass(frozen=True, slots=True)
class CommandResult:
    index: int
    label: str
    command: tuple[str, ...]
    returncode: int
    output: str
    elapsed_seconds: float


def _command(script: str, *arguments: str) -> list[str]:
    return [PYTHON, script, *arguments]


def _module(module: str, *arguments: str) -> list[str]:
    return [PYTHON, "-m", module, *arguments]


def verification_workers(task_count: int) -> int:
    if task_count < 1:
        raise ValueError("task_count must be positive")
    configured = os.environ.get("TSAO_VERIFY_WORKERS")
    if configured is not None:
        try:
            workers = int(configured)
        except ValueError as error:
            raise ValueError("TSAO_VERIFY_WORKERS must be an integer") from error
        if workers < 1:
            raise ValueError("TSAO_VERIFY_WORKERS must be positive")
        return min(workers, task_count)
    return min(task_count, max(1, min(3, os.cpu_count() or 1)))


def _record_timing(label: str, command: Sequence[str], elapsed: float, mode: str) -> None:
    _TIMING_RECORDS.append(
        {
            "label": label,
            "command": list(command),
            "elapsed_seconds": round(elapsed, 6),
            "mode": mode,
        }
    )


def run(label: str, command: Sequence[str], *, env: dict[str, str] | None = None) -> int:
    print(f"\n==> {label}", flush=True)
    print("    " + " ".join(command), flush=True)
    started = time.perf_counter()
    returncode = subprocess.run(  # nosec B603
        list(command), cwd=ROOT, env=env, check=False
    ).returncode
    _record_timing(label, command, time.perf_counter() - started, "sequential")
    return returncode


def _run_captured(
    index: int,
    label: str,
    command: Sequence[str],
    env: dict[str, str] | None,
) -> CommandResult:
    started = time.perf_counter()
    try:
        completed = subprocess.run(  # nosec B603
            list(command),
            cwd=ROOT,
            env=env,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        returncode = completed.returncode
        output = completed.stdout
    except OSError as error:
        returncode = 127
        output = f"ERROR: {error}\n"
    return CommandResult(
        index=index,
        label=label,
        command=tuple(command),
        returncode=returncode,
        output=output,
        elapsed_seconds=time.perf_counter() - started,
    )


def run_parallel(
    tasks: Sequence[tuple[str, Sequence[str], dict[str, str] | None]],
    *,
    group_label: str,
) -> int:
    if not tasks:
        return 0
    workers = verification_workers(len(tasks))
    print(f"\n==> {group_label} ({workers} workers)", flush=True)
    results: list[CommandResult | None] = [None] * len(tasks)
    with ThreadPoolExecutor(max_workers=workers, thread_name_prefix="tsao-verify") as executor:
        futures = {
            executor.submit(_run_captured, index, label, command, env): index
            for index, (label, command, env) in enumerate(tasks)
        }
        for future in as_completed(futures):
            result = future.result()
            results[result.index] = result

    overall = 0
    for result in results:
        if result is None:
            raise RuntimeError("parallel verification result is missing")
        print(f"\n==> {result.label} [parallel]", flush=True)
        print("    " + " ".join(result.command), flush=True)
        if result.output:
            print(result.output, end="" if result.output.endswith("\n") else "\n", flush=True)
        print(f"    elapsed={result.elapsed_seconds:.3f}s", flush=True)
        _record_timing(result.label, result.command, result.elapsed_seconds, "parallel")
        if result.returncode and overall == 0:
            overall = result.returncode
    return overall


def _quality_tasks(*, refresh: bool) -> list[tuple[str, Sequence[str], dict[str, str] | None]]:
    check = [] if refresh else ["--check"]
    return [
        ("repository quality rules", _command("scripts/quality_check.py"), None),
        ("Ruff lint", _module("ruff", "check", "tsao_computation", "scripts", "tests", "_bootstrap.py"), None),
        ("Ruff format", _module("ruff", "format", "--check", "tsao_computation", "scripts", "tests", "_bootstrap.py"), None),
        ("mypy", _module("mypy", "tsao_computation", "scripts", "_bootstrap.py"), None),
        ("Bandit", _module("bandit", "-q", "-r", "tsao_computation", "scripts", "-x", "tests"), None),
        ("version metadata", _command("scripts/sync_version_metadata.py", *check), None),
        ("packaged registry assets", _command("scripts/sync_package_assets.py", *check), None),
        ("capability index", _command("scripts/build_capability_index.py", *check), None),
        ("adapter documentation", _command("scripts/build_adapter_docs.py", *check), None),
        ("workflow documentation", _command("scripts/build_workflow_docs.py", *check), None),
        ("scenario examples", _command("scripts/build_examples.py", *check), None),
    ]


def run_quality(*, refresh: bool) -> int:
    for label, command, env in _quality_tasks(refresh=refresh):
        code = run(label, command, env=env)
        if code:
            print(f"\nFAILED: {label} (exit {code})", file=sys.stderr)
            return code
    if refresh:
        code = run("repository manifest", _command("scripts/build_manifest.py"))
        if code:
            return code
    return run("repository manifest", _command("scripts/build_manifest.py", "--check"))


def run_core() -> int:
    coverage_env = dict(os.environ)
    coverage_env.setdefault("TSAO_COVERAGE_JSON", str(Path(tempfile.gettempdir()) / "tsao-current-coverage.json"))
    code = run("tests and coverage", _command("scripts/run_tests.py", "--coverage"), env=coverage_env)
    if code:
        return code
    tasks = [
        ("scientific reference benchmarks", _command("scripts/run_scientific_benchmarks.py"), None),
        ("critical coverage policy", _command("scripts/check_critical_coverage.py"), None),
        ("version metadata", _command("scripts/sync_version_metadata.py", "--check"), None),
        ("repository audit", _command("scripts/validate_repository.py"), None),
        ("schema validation", _command("scripts/validate_schemas.py"), None),
        ("packaged registry assets", _command("scripts/sync_package_assets.py", "--check"), None),
        ("adapter metadata", _command("scripts/validate_adapter_metadata.py"), None),
        ("capability index", _command("scripts/build_capability_index.py", "--check"), None),
        ("adapter documentation", _command("scripts/build_adapter_docs.py", "--check"), None),
        ("workflow documentation", _command("scripts/build_workflow_docs.py", "--check"), None),
        ("scenario examples", _command("scripts/build_examples.py", "--check"), None),
    ]
    code = run_parallel(tasks, group_label="bounded parallel verification")
    if code:
        return code
    return run("repository manifest", _command("scripts/build_manifest.py", "--check"))


def run_package() -> int:
    with tempfile.TemporaryDirectory(prefix="tsao-package-") as temporary:
        temp_root = Path(temporary)
        tasks = [
            ("source archive first build", _command("scripts/package_release.py", "--output", str(temp_root / "source-first")), None),
            ("source archive second build", _command("scripts/package_release.py", "--output", str(temp_root / "source-second")), None),
        ]
        code = run_parallel(tasks, group_label="deterministic source package builds")
        if code:
            return code
        first = next((temp_root / "source-first").glob("*.zip"), None)
        second = next((temp_root / "source-second").glob("*.zip"), None)
        if first is None or second is None:
            print("missing deterministic source archive", file=sys.stderr)
            return 1
        if first.read_bytes() != second.read_bytes():
            print("source archives are not byte-identical", file=sys.stderr)
            return 1
    code = run("deterministic wheel verification", _command("scripts/verify_wheel.py"))
    if code:
        return code
    code = run("SBOM generation", _command("scripts/build_sbom.py"))
    if code:
        return code
    code = run("release manifest", _command("scripts/build_release_manifest.py"))
    if code:
        return code
    return run("repository manifest", _command("scripts/build_manifest.py", "--check"))


def run_benchmark() -> int:
    code = run("scientific reference benchmarks", _command("scripts/run_scientific_benchmarks.py"))
    if code:
        return code
    return run("performance benchmark", _command("scripts/benchmark.py"))


def _write_timing_report(path: Path, profile: str, returncode: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": "1.0",
        "profile": profile,
        "status": "PASS" if returncode == 0 else "FAIL",
        "claim_boundary": CLAIM_BOUNDARY,
        "stages": _TIMING_RECORDS,
        "total_recorded_seconds": round(
            sum(float(record["elapsed_seconds"]) for record in _TIMING_RECORDS), 6
        ),
    }
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--profile", choices=("quality", "core", "package", "benchmark", "all"), default="all"
    )
    parser.add_argument("--timing-json", type=Path)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    _TIMING_RECORDS.clear()
    if args.profile == "quality":
        code = run_quality(refresh=True)
    elif args.profile == "core":
        code = run_core()
    elif args.profile == "package":
        code = run_package()
    elif args.profile == "benchmark":
        code = run_benchmark()
    else:
        code = run_quality(refresh=True)
        if code == 0:
            code = run_core()
        if code == 0:
            code = run_package()
    if args.timing_json is not None:
        _write_timing_report(args.timing_json, args.profile, code)
    if code:
        print(f"\nValidation failed (exit {code}).", file=sys.stderr)
        return code
    print(f"\nValidation profile '{args.profile}' passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
