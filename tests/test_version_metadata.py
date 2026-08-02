from __future__ import annotations

from pathlib import Path

import pytest

from scripts import sync_version_metadata
from tsao_computation import __version__


def test_canonical_version_metadata_is_consistent() -> None:
    version = Path("VERSION").read_text(encoding="utf-8").strip()
    assert version == sync_version_metadata.read_version()
    assert __version__ == version
    assert sync_version_metadata.consistency_problems() == []


def test_rendered_metadata_is_idempotent() -> None:
    release_date = sync_version_metadata.citation_release_date()
    rendered = sync_version_metadata.rendered_metadata(Path(".").resolve(), release_date)
    assert rendered
    for path, expected in rendered.items():
        assert path.read_text(encoding="utf-8") == expected


def test_invalid_version_is_rejected(tmp_path: Path) -> None:
    (tmp_path / "VERSION").write_text("release-latest\n", encoding="utf-8")
    with pytest.raises(ValueError, match="invalid VERSION"):
        sync_version_metadata.read_version(tmp_path)
