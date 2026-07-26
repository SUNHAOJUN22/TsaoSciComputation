from __future__ import annotations

from pathlib import Path

import pytest

from scripts.sync_readme_visual_atlas_v7 import NEW_VISUALS, synchronize


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _fixture(root: Path) -> None:
    _write(
        root / "README.md",
        "# Demo\n\n## Solver-aware ecosystem\n\n"
        "The 36 illustrations in `assets/visuals/` are explanatory.\n",
    )
    _write(
        root / "README.zh-CN.md",
        "# 演示\n\n## 求解器感知型生态\n\n"
        "`assets/visuals/` 中的 36 幅图片用于说明。\n",
    )
    _write(
        root / "assets" / "visuals" / "README.md",
        "# README visual assets\n\n## Asset set\n\n"
        "- `existing.svg` — existing\n\n"
        "Run `python -m pytest tests/test_readme_visuals.py -q`.\n",
    )
    _write(root / "CHANGELOG.md", "# Changelog\n\n## Unreleased\n")


def test_synchronize_generates_idempotent_bilingual_v7_atlas(tmp_path: Path) -> None:
    _fixture(tmp_path)

    changed = synchronize(tmp_path)
    assert changed
    assert synchronize(tmp_path) == []
    synchronize(tmp_path, check=True)

    english = (tmp_path / "README.md").read_text(encoding="utf-8")
    chinese = (tmp_path / "README.zh-CN.md").read_text(encoding="utf-8")
    inventory = (tmp_path / "assets" / "visuals" / "README.md").read_text(encoding="utf-8")
    changelog = (tmp_path / "CHANGELOG.md").read_text(encoding="utf-8")

    assert "The 42 illustrations" in english
    assert "42 幅图片" in chinese
    assert "thirty-six to forty-two" in changelog
    for spec in NEW_VISUALS:
        relative = f"assets/visuals/{spec.filename}"
        assert relative in english
        assert relative in chinese
        assert spec.filename in inventory
        assert (tmp_path / relative).exists()


def test_check_rejects_unsynchronized_v7_documents(tmp_path: Path) -> None:
    _fixture(tmp_path)
    with pytest.raises(ValueError, match="V7 visual atlas is not synchronized"):
        synchronize(tmp_path, check=True)
