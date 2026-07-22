from __future__ import annotations

import argparse
import subprocess  # nosec B404
import sys


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
    return subprocess.run(  # nosec B603
        [sys.executable, "-m", "coverage", "report", "--fail-under=95"], check=False
    ).returncode


if __name__ == "__main__":
    raise SystemExit(main())
