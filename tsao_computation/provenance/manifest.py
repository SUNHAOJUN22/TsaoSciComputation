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
_SMALL_FILE_LIMIT = 1024 * 1024
_HASH_CHUNK_SIZE = 1024 * 1024


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


def _file_size_and_sha256(path: Path) -> tuple[int, str]:
    with path.open("rb") as handle:
        size = os.fstat(handle.fileno()).st_size
        if size <= _SMALL_FILE_LIMIT:
            return size, hashlib.sha256(handle.read()).hexdigest()
        digest = hashlib.sha256()
        for chunk in iter(lambda: handle.read(_HASH_CHUNK_SIZE), b""):
            digest.update(chunk)
        return size, digest.hexdigest()


def file_manifest(root: Path) -> list[dict[str, str | int]]:
    root = root.resolve()
    records: list[dict[str, str | int]] = []
    for path in iter_repository_entries(root):
        relative = path.relative_to(root)
        if path.is_symlink():
            raise ValueError(f"repository manifest contains symlink: {relative.as_posix()}")
        if not path.is_file():
            continue
        size, digest = _file_size_and_sha256(path)
        records.append(
            {
                "path": relative.as_posix(),
                "bytes": size,
                "sha256": digest,
            }
        )
    return records
