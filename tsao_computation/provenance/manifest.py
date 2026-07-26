from __future__ import annotations

import hashlib
import heapq
import os
from collections.abc import Iterator
from pathlib import Path

EXCLUDED_DIRS = {
    ".git",
    ".hypothesis",
    ".mypy_cache",
    ".nox",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    ".tsao-computation",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "dist-a",
    "dist-b",
    "htmlcov",
    "venv",
}
EXCLUDED_FILES = {".coverage"}


def is_excluded_path(relative: Path) -> bool:
    return (
        relative.name in EXCLUDED_FILES
        or relative.name.startswith(".coverage.")
        or any(part in EXCLUDED_DIRS or part.endswith(".egg-info") for part in relative.parts)
    )


def iter_repository_entries(root: Path) -> Iterator[Path]:
    root = root.resolve()
    pending: list[tuple[str, Path, Path, bool, bool]] = []

    def enqueue(directory: Path, relative_directory: Path) -> None:
        with os.scandir(directory) as scan:
            for entry in scan:
                relative = relative_directory / entry.name
                if is_excluded_path(relative):
                    continue
                heapq.heappush(
                    pending,
                    (
                        relative.as_posix(),
                        relative,
                        Path(entry.path),
                        entry.is_symlink(),
                        entry.is_dir(follow_symlinks=False),
                    ),
                )

    enqueue(root, Path())
    while pending:
        _, relative, path, is_symlink, is_directory = heapq.heappop(pending)
        if is_symlink:
            yield path
        elif is_directory:
            enqueue(path, relative)
        else:
            yield path


def file_manifest(root: Path) -> list[dict[str, str | int]]:
    root = root.resolve()
    records: list[dict[str, str | int]] = []
    for path in iter_repository_entries(root):
        relative = path.relative_to(root)
        if path.is_symlink():
            raise ValueError(f"repository manifest contains symlink: {relative.as_posix()}")
        if not path.is_file():
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
