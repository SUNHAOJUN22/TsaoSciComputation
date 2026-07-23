from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import subprocess  # nosec B404
import sys
import tempfile
from collections.abc import Callable, Sequence
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable
CODE_PATHS = ("tsao_computation", "scripts", "tests")
SOURCE_ARTIFACTS = (
    "TsaoSciComputation-3.0.0.zip",
    "TsaoSciComputation-3.0.0.tar.gz",
)


def run(label: str, command: Sequence[str], *, env: dict[str, str] | None = None) -> int:
    print(f"\n==> {label}", flush=True)
    print("    " + " ".join(command), flush=True)
    return subprocess.run(  # nosec B603
        list(command), cwd=ROOT, env=env, check=False
    ).returncode


def run_commands(commands: Sequence[tuple[str, Sequence[str]]]) -> int:
    for label, command in commands:
        returncode = run(label, command)
        if returncode:
            print(f"\nFAILED: {label} (exit {returncode})", file=sys.stderr)
            return returncode
    return 0


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_core() -> int:
    return run_commands(
        (
            ("tests and coverage", (PYTHON, "scripts/run_tests.py", "--coverage")),
            ("repository audit", (PYTHON, "scripts/validate_repository.py")),
            ("schema validation", (PYTHON, "scripts/validate_schemas.py")),
            ("packaged registry assets", (PYTHON, "scripts/sync_package_assets.py", "--check")),
            ("adapter metadata", (PYTHON, "scripts/validate_adapter_metadata.py")),
            ("capability index", (PYTHON, "scripts/build_capability_index.py", "--check")),
            ("adapter documentation", (PYTHON, "scripts/build_adapter_docs.py", "--check")),
            ("workflow documentation", (PYTHON, "scripts/build_workflow_docs.py", "--check")),
            ("repository manifest", (PYTHON, "scripts/build_manifest.py", "--check")),
        )
    )


def verify_quality() -> int:
    return run_commands(
        (
            ("repository quality rules", (PYTHON, "scripts/quality_check.py")),
            ("Ruff lint", (PYTHON, "-m", "ruff", "check", *CODE_PATHS)),
            ("Ruff formatting", (PYTHON, "-m", "ruff", "format", "--check", *CODE_PATHS)),
            (
                "Mypy",
                (PYTHON, "-m", "mypy", "--python-version", "3.13", "tsao_computation", "scripts"),
            ),
            ("Bandit", (PYTHON, "-m", "bandit", "-q", "-r", "tsao_computation", "scripts")),
            ("repository security scan", (PYTHON, "scripts/security_scan.py")),
            ("controlled mutation gate", (PYTHON, "scripts/run_mutation_gate.py")),
        )
    )


def verify_package() -> int:
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    artifacts = tuple(name.replace("3.0.0", version) for name in SOURCE_ARTIFACTS)
    environment = dict(os.environ)
    environment["SOURCE_DATE_EPOCH"] = "1700000000"
    shutil.rmtree(ROOT / "dist", ignore_errors=True)

    with tempfile.TemporaryDirectory(prefix="tsao-source-build-") as temporary:
        temporary_root = Path(temporary)
        first = temporary_root / "first"
        second = temporary_root / "second"
        for label, output in (("source build A", first), ("source build B", second)):
            returncode = run(
                label,
                (PYTHON, "scripts/package_release.py", "--output-dir", str(output)),
                env=environment,
            )
            if returncode:
                return returncode

        for artifact in artifacts:
            first_hash = sha256(first / artifact)
            second_hash = sha256(second / artifact)
            if first_hash != second_hash:
                print(f"FAILED: non-reproducible source artifact: {artifact}", file=sys.stderr)
                return 1

        destination = ROOT / "dist"
        destination.mkdir(exist_ok=True)
        for path in first.iterdir():
            if path.is_file():
                shutil.copy2(path, destination / path.name)

    returncode = run("wheel rebuild and isolated install", (PYTHON, "scripts/verify_wheel.py"))
    if returncode:
        return returncode
    print("\nPASS: source archives and wheel are reproducible; isolated install succeeded.")
    return 0


def verify_benchmark() -> int:
    return run("orchestration microbenchmark", (PYTHON, "scripts/benchmark.py"))


PROFILE_FUNCTIONS: dict[str, Callable[[], int]] = {
    "core": verify_core,
    "quality": verify_quality,
    "package": verify_package,
    "benchmark": verify_benchmark,
}
RELEASE_PROFILE_NAMES = ("quality", "core", "package")


def selected_verifications(profile: str) -> tuple[Callable[[], int], ...]:
    if profile == "all":
        return tuple(PROFILE_FUNCTIONS[name] for name in RELEASE_PROFILE_NAMES)
    try:
        return (PROFILE_FUNCTIONS[profile],)
    except KeyError as error:
        raise ValueError(f"unknown verification profile: {profile}") from error


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the canonical TsaoSciComputation verification profiles."
    )
    parser.add_argument(
        "--profile",
        choices=(*PROFILE_FUNCTIONS, "all"),
        default="all",
        help=(
            "all runs the deterministic release gates (quality, core, package); "
            "benchmark remains separate because it is environment-specific"
        ),
    )
    args = parser.parse_args()

    for verification in selected_verifications(args.profile):
        returncode = verification()
        if returncode:
            return returncode
    print(f"\nPASS: verification profile '{args.profile}' completed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
