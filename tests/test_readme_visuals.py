from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENTRY = re.compile(r"^- `([^`]+\.svg)` — ", re.MULTILINE)
FONT_SIZE = re.compile(r"font-size:\s*([0-9]+)px")
HEX_COLOR = re.compile(r"#[0-9A-Fa-f]{6}")
LAYOUT = re.compile(r'data-layout="([a-z]+)"')
DESIGN_SYSTEM = "uiux-pro-max-scientific-swiss-v2"
EXPECTED_LAYOUTS = {
    "hero": 1,
    "bento": 7,
    "workflow": 23,
    "loop": 5,
    "risk": 6,
}
ALLOWED_COLORS = {
    "#0B1220",
    "#111827",
    "#172033",
    "#334155",
    "#F8FAFC",
    "#CBD5E1",
    "#94A3B8",
    "#3B82F6",
    "#06B6D4",
    "#14B8A6",
    "#22C55E",
    "#F59E0B",
    "#F97316",
    "#EF4444",
}
BANNED_DECORATIVE_COLORS = {"#8B5CF6", "#D946EF", "#FF7EC7", "#EC4899"}


def _inventory_names() -> tuple[str, ...]:
    inventory = (ROOT / "assets" / "visuals" / "README.md").read_text(encoding="utf-8")
    names = tuple(ENTRY.findall(inventory))
    assert len(names) == len(set(names))
    return names


def test_readme_visuals_are_diverse_accessible_and_referenced() -> None:
    readmes = [
        (ROOT / "README.md").read_text(encoding="utf-8"),
        (ROOT / "README.zh-CN.md").read_text(encoding="utf-8"),
    ]
    manifest_in = (ROOT / "MANIFEST.in").read_text(encoding="utf-8")
    design_system = (ROOT / "assets" / "visuals" / "DESIGN_SYSTEM.md").read_text(
        encoding="utf-8"
    )
    assert "recursive-include assets *.md *.svg" in manifest_in
    assert "Scientific Swiss Bento V11" in design_system
    assert all(layout.title() in design_system for layout in EXPECTED_LAYOUTS)
    assert all("assets/visuals/DESIGN_SYSTEM.md" in readme for readme in readmes)
    assert all("V11" in readme for readme in readmes)

    names = _inventory_names()
    assert len(names) == 42
    visual_root = ROOT / "assets" / "visuals"
    assert {path.name for path in visual_root.glob("*.svg")} == set(names)

    titles: set[str] = set()
    descriptions: set[str] = set()
    layouts: Counter[str] = Counter()
    namespace = {"svg": "http://www.w3.org/2000/svg"}
    for name in names:
        relative = f"assets/visuals/{name}"
        text = (visual_root / name).read_text(encoding="utf-8")
        lowered = text.lower()
        assert text.startswith('<svg xmlns="http://www.w3.org/2000/svg"')
        assert " viewBox=" in text
        assert f'data-design-system="{DESIGN_SYSTEM}"' in text
        assert " data-family=" in text
        layout_match = LAYOUT.search(text)
        assert layout_match is not None
        layout = layout_match.group(1)
        layouts[layout] += 1

        assert "<script" not in lowered
        assert "<image" not in lowered
        assert "<foreignobject" not in lowered
        assert "onload=" not in lowered
        assert "onclick=" not in lowered
        assert 'href="http' not in lowered
        assert "<lineargradient" not in lowered
        assert "<radialgradient" not in lowered
        assert "<filter" not in lowered
        assert "EVIDENCE-BOUND" in text
        assert "NUMERICAL" in text
        assert "CONVERGENCE" in text
        assert "APPLICABILITY" in text
        assert 3_500 <= len(text.encode("utf-8")) <= 30_000

        if layout == "bento":
            assert "DECISION GATE" in text
        elif layout == "loop":
            assert "FEEDBACK LOOP" in text
        elif layout == "risk":
            assert "BARRIER · LIMIT · ESCALATE" in text

        sizes = [int(value) for value in FONT_SIZE.findall(text)]
        assert sizes and min(sizes) >= 13
        colors = {value.upper() for value in HEX_COLOR.findall(text)}
        assert colors <= ALLOWED_COLORS
        assert not colors & BANNED_DECORATIVE_COLORS

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

    assert dict(layouts) == EXPECTED_LAYOUTS
