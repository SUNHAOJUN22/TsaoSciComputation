from __future__ import annotations

import json
import os
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "package_release.py"


def _source_tree(root: Path) -> None:
    root.mkdir()
    (root / "VERSION").write_text("0.0.0-test\n", encoding="utf-8")
    (root / "source.txt").write_text("fixed source\n", encoding="utf-8")


def _build(root: Path, output: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--output-dir", str(output)],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
        env={**os.environ, "SOURCE_DATE_EPOCH": "1700000000"},
    )


@pytest.mark.parametrize("location", ["nested", "outside", "parent"])
def test_repeated_release_build_excludes_its_output_tree(tmp_path: Path, location: str) -> None:
    root = tmp_path / "source"
    _source_tree(root)
    output = (root if location == "nested" else tmp_path) / "release-artifacts"
    if location == "parent":
        output = root.parent
    first = _build(root, output)
    assert first.returncode == 0, first.stderr
    before = {path.name: path.read_bytes() for path in output.iterdir() if path.is_file()}

    second = _build(root, output)

    assert second.returncode == 0, second.stderr
    assert json.loads(first.stdout)["file_count"] == json.loads(second.stdout)["file_count"] == 2
    assert {path.name: path.read_bytes() for path in output.iterdir() if path.is_file()} == before
    with zipfile.ZipFile(output / "TsaoSciComputation-0.0.0-test.zip") as archive:
        assert archive.namelist() == [
            "TsaoSciComputation-0.0.0-test/VERSION",
            "TsaoSciComputation-0.0.0-test/source.txt",
        ]


@pytest.mark.parametrize("alias", ["direct", "dotdot", "symlink"])
def test_release_rejects_source_root_output_without_mutation(tmp_path: Path, alias: str) -> None:
    root = tmp_path / "source"
    _source_tree(root)
    output = root
    if alias == "dotdot":
        nested = root / "child"
        nested.mkdir()
        output = nested / ".."
    elif alias == "symlink":
        output = tmp_path / "source-alias"
        try:
            output.symlink_to(root, target_is_directory=True)
        except OSError as error:
            pytest.skip(f"directory symlink is unavailable: {error}")
    before = {path.name: path.read_bytes() for path in root.iterdir() if path.is_file()}

    result = _build(root, output)

    assert result.returncode != 0
    assert "output directory must not be the source root" in result.stderr
    assert {path.name: path.read_bytes() for path in root.iterdir() if path.is_file()} == before


def test_release_resolves_output_alias_before_excluding_generated_subtree(tmp_path: Path) -> None:
    root = tmp_path / "source"
    _source_tree(root)
    output = root / "custom-artifacts"
    output.mkdir()
    alias = tmp_path / "artifact-alias"
    try:
        alias.symlink_to(output, target_is_directory=True)
    except OSError as error:
        pytest.skip(f"directory symlink is unavailable: {error}")
    assert _build(root, output).returncode == 0
    before = {path.name: path.read_bytes() for path in output.iterdir()}

    result = _build(root, alias)

    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["file_count"] == 2
    assert {path.name: path.read_bytes() for path in output.iterdir()} == before
