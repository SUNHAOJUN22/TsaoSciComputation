from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VISUALS = (
    "hero-multiscale.svg",
    "agent-orchestration.svg",
    "capability-landscape.svg",
    "quantum-to-md.svg",
    "electronic-structure-landscape.svg",
    "free-energy-sampling.svg",
    "reaction-kinetics-network.svg",
    "ml-potential-active-learning.svg",
    "polymer-process.svg",
    "mesoscale-phase-field.svg",
    "continuum-multiphysics.svg",
    "process-optimization-uq.svg",
    "uncertainty-sensitivity.svg",
    "electrochemical-interface.svg",
    "spectroscopy-observables.svg",
    "transport-degradation.svg",
    "inverse-design-loop.svg",
    "data-model-governance.svg",
    "reactor-safety-control.svg",
    "hpc-execution-provenance.svg",
    "engine-ecosystem.svg",
    "evidence-loop.svg",
    "confidence-ladder.svg",
    "digital-thread.svg",
)


def test_readme_visuals_are_self_contained_accessible_and_referenced() -> None:
    readmes = [
        (ROOT / "README.md").read_text(encoding="utf-8"),
        (ROOT / "README.zh-CN.md").read_text(encoding="utf-8"),
    ]
    manifest_in = (ROOT / "MANIFEST.in").read_text(encoding="utf-8")
    inventory = (ROOT / "assets" / "visuals" / "README.md").read_text(encoding="utf-8")
    assert "recursive-include assets *.md *.svg" in manifest_in

    visual_root = ROOT / "assets" / "visuals"
    assert {path.name for path in visual_root.glob("*.svg")} == set(VISUALS)

    titles: set[str] = set()
    descriptions: set[str] = set()
    namespace = {"svg": "http://www.w3.org/2000/svg"}
    for name in VISUALS:
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

        assert name in inventory
        assert all(relative in readme for readme in readmes)
