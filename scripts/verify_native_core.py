from __future__ import annotations

import json
import shutil
import subprocess  # nosec B404
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _run(command: tuple[str, ...]) -> dict[str, object]:
    completed = subprocess.run(  # nosec B603
        command,
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=180,
    )
    return {
        "command": list(command),
        "returncode": completed.returncode,
        "stdout_tail": "\n".join(completed.stdout.splitlines()[-80:]),
        "stderr_tail": "\n".join(completed.stderr.splitlines()[-80:]),
    }


def main() -> int:
    cmake = shutil.which("cmake")
    ctest = shutil.which("ctest")
    problems: list[str] = []
    required = (
        ROOT / "native/CMakeLists.txt",
        ROOT / "native/include/tsao/capi.h",
        ROOT / "native/src/capi.cpp",
        ROOT / "native/tests/native_smoke.cpp",
    )
    for path in required:
        if not path.is_file():
            problems.append(f"missing native source file: {path.relative_to(ROOT).as_posix()}")
    if cmake is None:
        problems.append("cmake executable is unavailable")
    if ctest is None:
        problems.append("ctest executable is unavailable")

    steps: list[dict[str, object]] = []
    if not problems and cmake is not None and ctest is not None:
        with tempfile.TemporaryDirectory(prefix="tsao-native-core-") as temporary:
            build = Path(temporary) / "build"
            commands = (
                (
                    cmake,
                    "-S",
                    str(ROOT / "native"),
                    "-B",
                    str(build),
                    "-DCMAKE_BUILD_TYPE=Release",
                    "-DBUILD_TESTING=ON",
                ),
                (cmake, "--build", str(build), "--config", "Release", "--parallel", "2"),
                (
                    ctest,
                    "--test-dir",
                    str(build),
                    "--output-on-failure",
                    "-C",
                    "Release",
                ),
            )
            for command in commands:
                result = _run(command)
                steps.append(result)
                if result["returncode"] != 0:
                    problems.append(f"native verification command failed: {' '.join(command)}")
                    break

    report = {
        "schema_version": "1.0",
        "status": "PASS" if not problems else "FAIL",
        "problems": problems,
        "steps": steps,
        "claim_boundary": (
            "This compiles and smoke-tests the source-only C++20 CPU/OpenMP discovery ABI. "
            "It does not claim a CUDA, HIP, SYCL, external-solver, numerical-performance, "
            "convergence, physical-validity, applicability, or authorization result."
        ),
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if not problems else 1


if __name__ == "__main__":
    raise SystemExit(main())
