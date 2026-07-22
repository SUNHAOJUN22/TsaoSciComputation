from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess  # nosec B404
import sys
import tempfile
import venv
from pathlib import Path

import _bootstrap  # noqa: F401


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_once(root: Path, output: Path, epoch: str) -> Path:
    output.mkdir(parents=True)
    env = dict(os.environ)
    env["SOURCE_DATE_EPOCH"] = epoch
    subprocess.run(  # nosec B603
        [
            sys.executable,
            "-m",
            "pip",
            "wheel",
            ".",
            "--no-deps",
            "--no-build-isolation",
            "--wheel-dir",
            str(output),
        ],
        cwd=root,
        env=env,
        check=True,
    )
    wheels = list(output.glob("*.whl"))
    if len(wheels) != 1:
        raise RuntimeError(f"expected one wheel, found {len(wheels)}")
    return wheels[0]


def main() -> int:
    root = Path(".").resolve()
    dist = root / "dist"
    dist.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="tsao-wheel-") as temporary:
        temporary_root = Path(temporary)
        first = build_once(root, temporary_root / "first", "1700000000")
        second = build_once(root, temporary_root / "second", "1700000000")
        first_hash = sha256(first)
        second_hash = sha256(second)
        if first_hash != second_hash:
            raise SystemExit("wheel builds are not byte-identical")
        destination = dist / first.name
        shutil.copy2(first, destination)

        environment = temporary_root / "venv"
        venv.EnvBuilder(with_pip=True, clear=True).create(environment)
        python = environment / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
        subprocess.run(  # nosec B603
            [str(python), "-m", "pip", "install", "--no-index", str(destination)],
            cwd=temporary_root,
            check=True,
        )
        verification = subprocess.check_output(  # nosec B603
            [
                str(python),
                "-c",
                "from tsao_computation import __version__; "
                "from tsao_computation.registries import capabilities,adapters,workflows; "
                "print(__version__,len(capabilities()),len(adapters()),len(workflows()))",
            ],
            cwd=temporary_root,
            text=True,
        ).strip()
        if verification != "3.0.0 164 27 20":
            raise SystemExit(f"isolated wheel verification failed: {verification}")

    report = {
        "schema_version": "1.0",
        "artifact": destination.name,
        "sha256": sha256(destination),
        "bytes": destination.stat().st_size,
        "byte_identical_rebuild": True,
        "isolated_install": True,
        "verification": "3.0.0 164 27 20",
    }
    (dist / "WHEEL_VERIFICATION.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
