from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENTRY = re.compile(r"^- `([^`]+\.svg)` — ", re.MULTILINE)


def _inventory_names() -> tuple[str, ...]:
    inventory = (ROOT / "assets" / "visuals" / "README.md").read_text(encoding="utf-8")
    names = tuple(ENTRY.findall(inventory))
    assert len(names) == len(set(names))
    return names


def test_readme_visuals_are_self_contained_accessible_and_referenced() -> None:
    readmes = [
        (ROOT / "README.md").read_text(encoding="utf-8"),
        (ROOT / "README.zh-CN.md").read_text(encoding="utf-8"),
    ]
    manifest_in = (ROOT / "MANIFEST.in").read_text(encoding="utf-8")
    assert "recursive-include assets *.md *.svg" in manifest_in

    names = _inventory_names()
    assert len(names) >= 36
    visual_root = ROOT / "assets" / "visuals"
    assert {path.name for path in visual_root.glob("*.svg")} == set(names)

    titles: set[str] = set()
    descriptions: set[str] = set()
    namespace = {"svg": "http://www.w3.org/2000/svg"}
    for name in names:
        relative = f"assets/visuals/{name}"
        text = (visual_root / name).read_text(encoding="utf-8")
        assert text.startswith('<svg xmlns="http://www.w3.org/2000/svg"')
        assert " viewBox=" in text
        assert "<script" not in text.lower()
        assert "<image" not in text.lower()
        assert "<foreignobject" not in text.lower()
        assert "onload=" not in text.lower()
        assert "onclick=" not in text.lower()
        assert 'href="http' not in text.lower()
        assert 1_000 <= len(text.encode("utf-8")) <= 30_000

        root = ET.fromstring(text)
        title = root.find("svg:title", namespace)
        description = root.find("svg:desc", namespace)
        assert title is not None and title.text and title.text.strip()
        assert description is not None and description.text and description.text.strip()
        assert title.text.strip() not in titles
        assert description.text.strip() not in descriptions
        titles.add(title.text.strip())
        descriptions.add(description.text.strip())

        assert all(relative in readme for readme in readmes)
