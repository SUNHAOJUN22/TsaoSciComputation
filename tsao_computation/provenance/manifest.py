from __future__ import annotations

import hashlib
from pathlib import Path

EXCLUDED_DIRS = {
    ".git",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "__pycache__",
    "dist",
    "dist-a",
    "dist-b",
    "build",
}
EXCLUDED_FILES = {".coverage"}


def file_manifest(root: Path) -> list[dict[str, str | int]]:
    records: list[dict[str, str | int]] = []
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if not path.is_file():
            continue
        if path.name in EXCLUDED_FILES:
            continue
        if any(part in EXCLUDED_DIRS or part.endswith(".egg-info") for part in relative.parts):
            continue
        data = path.read_bytes()
        records.append(
            {
                "path": relative.as_posix(),
                "bytes": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
            }
        )
    return records
