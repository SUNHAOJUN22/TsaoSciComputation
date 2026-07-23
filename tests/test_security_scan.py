from __future__ import annotations

import runpy
from pathlib import Path
from typing import Callable, cast


def load_scan() -> Callable[[Path], dict[str, object]]:
    namespace = runpy.run_path("scripts/security_scan.py", run_name="security_scan_test")
    return cast(Callable[[Path], dict[str, object]], namespace["scan"])


def test_security_scan_ignores_generated_directories_and_reports_findings(
    tmp_path: Path,
) -> None:
    dangerous_text = "e" + "val('x')\n"
    (tmp_path / "source.txt").write_text("safe", encoding="utf-8")
    (tmp_path / "unsafe.py").write_text(dangerous_text, encoding="utf-8")
    for directory in (
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        "__pycache__",
        "dist",
        "dist-a",
        "dist-b",
        "build",
        "tsao_scicomputation.egg-info",
    ):
        path = tmp_path / directory
        path.mkdir()
        (path / "generated.txt").write_text(dangerous_text, encoding="utf-8")
    (tmp_path / ".coverage").write_text("ignored", encoding="utf-8")

    report = load_scan()(tmp_path)

    assert report["files_scanned"] == 2
    assert report["findings"] == [{"path": "unsafe.py", "rule": "dangerous_eval", "offset": 0}]
