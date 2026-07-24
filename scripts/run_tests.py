from __future__ import annotations

import argparse
import os
import subprocess  # nosec B404
import sys
import tempfile
from pathlib import Path


def coverage_json_path() -> Path:
    configured = os.environ.get("TSAO_COVERAGE_JSON")
    if configured:
        return Path(configured).expanduser().resolve()
    return Path(tempfile.gettempdir()) / "tsao-current-coverage.json"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--coverage", action="store_true")
    parser.add_argument("--marker")
    args = parser.parse_args()

    pytest_command = [sys.executable, "-m", "pytest", "-vv" if args.verbose else "-q"]
    if args.marker:
        pytest_command.extend(["-m", args.marker])
    if not args.coverage:
        return subprocess.run(pytest_command, check=False).returncode  # nosec B603

    coverage_command = [sys.executable, "-m", "coverage", "run", "--branch", "-m", "pytest", "-q"]
    if args.marker:
        coverage_command.extend(["-m", args.marker])
    result = subprocess.run(coverage_command, check=False)  # nosec B603
    if result.returncode != 0:
        return result.returncode

    output = coverage_json_path()
    output.parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(  # nosec B603
        [sys.executable, "-m", "coverage", "json", "-o", str(output)], check=False
    )
    if result.returncode != 0:
        return result.returncode
    return subprocess.run(  # nosec B603
        [sys.executable, "-m", "coverage", "report", "--fail-under=95"], check=False
    ).returncode


if __name__ == "__main__":
    raise SystemExit(main())
