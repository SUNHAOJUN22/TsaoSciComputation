from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VISUALS = (
    "hero-multiscale.svg",
    "agent-orchestration.svg",
    "quantum-to-md.svg",
    "polymer-process.svg",
    "evidence-loop.svg",
    "confidence-ladder.svg",
    "engine-ecosystem.svg",
    "digital-thread.svg",
    "capability-landscape.svg",
)


def test_readme_visuals_are_self_contained_accessible_and_referenced() -> None:
    readmes = [
        (ROOT / "README.md").read_text(encoding="utf-8"),
        (ROOT / "README.zh-CN.md").read_text(encoding="utf-8"),
    ]
    manifest_in = (ROOT / "MANIFEST.in").read_text(encoding="utf-8")
    assert "recursive-include assets *.md *.svg" in manifest_in

    visual_root = ROOT / "assets" / "visuals"
    assert {path.name for path in visual_root.glob("*.svg")} == set(VISUALS)

    for name in VISUALS:
        relative = f"assets/visuals/{name}"
        text = (visual_root / name).read_text(encoding="utf-8")
        assert text.startswith('<svg xmlns="http://www.w3.org/2000/svg"')
        assert " viewBox=" in text
        assert "<title" in text and "</title>" in text
        assert "<desc" in text and "</desc>" in text
        assert "<script" not in text.lower()
        assert "<image" not in text.lower()
        assert 'href="http' not in text.lower()
        assert 1_000 <= len(text.encode("utf-8")) <= 30_000
        assert all(relative in readme for readme in readmes)
