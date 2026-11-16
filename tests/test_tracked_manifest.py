from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

from tsao_computation.provenance.manifest import tracked_file_manifest


def _git(root: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True)


def test_tracked_manifest_ignores_untracked_runtime_files(tmp_path: Path) -> None:
    _git(tmp_path, "init", "-q")
    tracked = tmp_path / "tracked.txt"
    tracked.write_text("stable\n", encoding="utf-8")
    _git(tmp_path, "add", "tracked.txt")

    before = tracked_file_manifest(tmp_path)
    (tmp_path / "runtime-output.json").write_text("{}\n", encoding="utf-8")
    (tmp_path / ".pytest_cache").mkdir()
    (tmp_path / ".pytest_cache" / "state").write_text("generated", encoding="utf-8")

    assert tracked_file_manifest(tmp_path) == before
    assert [record["path"] for record in before] == ["tracked.txt"]


def test_tracked_manifest_fails_when_indexed_file_is_missing(tmp_path: Path) -> None:
    _git(tmp_path, "init", "-q")
    tracked = tmp_path / "tracked.txt"
    tracked.write_text("stable\n", encoding="utf-8")
    _git(tmp_path, "add", "tracked.txt")
    tracked.unlink()

    with pytest.raises(FileNotFoundError, match="tracked.txt"):
        tracked_file_manifest(tmp_path)


@pytest.mark.parametrize("external", [False, True])
def test_tracked_manifest_rejects_symlinked_parent_before_hashing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, external: bool
) -> None:
    from tsao_computation.provenance import manifest

    root = tmp_path / "repository"
    root.mkdir()
    _git(root, "init", "-q")
    nested = root / "nested"
    nested.mkdir()
    (nested / "source.txt").write_text("original", encoding="utf-8")
    _git(root, "add", "nested/source.txt")
    shutil.rmtree(nested)
    target = (tmp_path if external else root) / "replacement"
    target.mkdir()
    (target / "source.txt").write_text("untrusted replacement", encoding="utf-8")
    nested.symlink_to(target, target_is_directory=True)

    def unexpected_read(path: Path) -> tuple[int, str]:
        pytest.fail(f"manifest must not hash through a symlinked ancestor: {path}")

    monkeypatch.setattr(manifest, "_file_size_and_sha256", unexpected_read)
    with pytest.raises(ValueError, match="contains symlink"):
        tracked_file_manifest(root)
