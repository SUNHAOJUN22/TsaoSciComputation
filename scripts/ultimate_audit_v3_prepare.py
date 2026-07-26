from __future__ import annotations

import json
import textwrap
from pathlib import Path

VISUAL_NAMES = (
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
    "hpc-execution-provenance.svg",
    "engine-ecosystem.svg",
    "evidence-loop.svg",
    "confidence-ladder.svg",
    "digital-thread.svg",
)

ENGLISH_ATLAS = """
## Specialized simulation and AI capability atlas

<table>
<tr>
<td width="50%"><img src="assets/visuals/free-energy-sampling.svg" alt="Enhanced sampling and free-energy reconstruction workflow" width="100%"></td>
<td width="50%"><img src="assets/visuals/reaction-kinetics-network.svg" alt="Reaction pathways kinetic networks and reactor evidence" width="100%"></td>
</tr>
<tr>
<td align="center"><b>Enhanced sampling &amp; free energy</b><br>Collective variables, biased ensembles, overlap, reconstruction and uncertainty.</td>
<td align="center"><b>Reaction pathways &amp; kinetics</b><br>Stationary points, transition states, rates, networks and reactor-balance handoff.</td>
</tr>
<tr>
<td width="50%"><img src="assets/visuals/ml-potential-active-learning.svg" alt="Machine learned potential and active learning loop" width="100%"></td>
<td width="50%"><img src="assets/visuals/mesoscale-phase-field.svg" alt="Mesoscale phase field and morphology workflow" width="100%"></td>
</tr>
<tr>
<td align="center"><b>ML potentials &amp; active learning</b><br>Reference labels, model committees, uncertainty alarms and validated dynamics.</td>
<td align="center"><b>Mesoscale morphology</b><br>Coarse-graining, phase evolution, topology metrics and continuum transfer.</td>
</tr>
<tr>
<td width="50%"><img src="assets/visuals/hpc-execution-provenance.svg" alt="Bounded HPC execution and provenance workflow" width="100%"></td>
<td width="50%"><img src="assets/visuals/uncertainty-sensitivity.svg" alt="Uncertainty quantification sensitivity and decision boundary" width="100%"></td>
</tr>
<tr>
<td align="center"><b>HPC execution provenance</b><br>Preflight, scheduler boundaries, isolated execution, hashes and reviewed evidence.</td>
<td align="center"><b>UQ &amp; sensitivity</b><br>Input distributions, propagation, global ranking, prediction intervals and robust decisions.</td>
</tr>
</table>

These views make six high-impact capability families explicit without claiming bundled solvers or live production execution. Each diagram separates numerical output from convergence, physical validity, uncertainty, applicability and human authorization.
"""

CHINESE_ATLAS = """
## 专项模拟与 AI 能力图谱

<table>
<tr>
<td width="50%"><img src="assets/visuals/free-energy-sampling.svg" alt="增强采样与自由能重构工作流" width="100%"></td>
<td width="50%"><img src="assets/visuals/reaction-kinetics-network.svg" alt="反应路径 动力学网络与反应器证据" width="100%"></td>
</tr>
<tr>
<td align="center"><b>增强采样与自由能</b><br>集体变量、偏置系综、重叠检查、自由能重构与不确定度。</td>
<td align="center"><b>反应路径与动力学</b><br>驻点、过渡态、速率、反应网络及反应器衡算交接。</td>
</tr>
<tr>
<td width="50%"><img src="assets/visuals/ml-potential-active-learning.svg" alt="机器学习势与主动学习闭环" width="100%"></td>
<td width="50%"><img src="assets/visuals/mesoscale-phase-field.svg" alt="介观相场与形貌演化工作流" width="100%"></td>
</tr>
<tr>
<td align="center"><b>机器学习势与主动学习</b><br>参考标注、模型委员会、不确定度报警与受验证动力学。</td>
<td align="center"><b>介观形貌模拟</b><br>粗粒化、相演化、拓扑指标与连续介质参数交接。</td>
</tr>
<tr>
<td width="50%"><img src="assets/visuals/hpc-execution-provenance.svg" alt="有界 HPC 执行与溯源工作流" width="100%"></td>
<td width="50%"><img src="assets/visuals/uncertainty-sensitivity.svg" alt="不确定度量化 敏感性与决策边界" width="100%"></td>
</tr>
<tr>
<td align="center"><b>HPC 执行溯源</b><br>环境前检、调度边界、隔离执行、哈希与人工证据审核。</td>
<td align="center"><b>不确定度与敏感性</b><br>输入分布、传播、全局排序、预测区间与稳健决策。</td>
</tr>
</table>

这六类高价值能力由专属图示明确呈现，但不宣称仓库打包了外部求解器或已经完成生产级真实运行。每幅图均将数值输出与收敛性、物理有效性、不确定度、适用域和人工授权分开。
"""

VISUAL_TEST = '''from __future__ import annotations

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
    inventory = (ROOT / "assets" / "visuals" / "README.md").read_text(
        encoding="utf-8"
    )
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
'''


def insert_atlas(path: Path, heading: str, marker: str, atlas: str) -> None:
    text = path.read_text(encoding="utf-8")
    if heading not in text:
        if marker not in text:
            raise RuntimeError(f"README insertion marker missing: {path}")
        text = text.replace(marker, textwrap.dedent(atlas).strip() + "\n\n" + marker, 1)
    path.write_text(text, encoding="utf-8", newline="\n")


def write_inventory(root: Path) -> None:
    descriptions = {
        "hero-multiscale.svg": "electron-to-process architecture",
        "agent-orchestration.svg": "governed AI scientific agent",
        "capability-landscape.svg": "capability, workflow, validation and governance layers",
        "quantum-to-md.svg": "electronic-structure to molecular-dynamics handoff",
        "electronic-structure-landscape.svg": "DFT density, self-consistency, energy and observable gates",
        "free-energy-sampling.svg": "enhanced sampling, overlap, reconstruction and uncertainty",
        "reaction-kinetics-network.svg": "reaction pathways, rate evidence and reactor handoff",
        "ml-potential-active-learning.svg": "reference data, uncertainty and active learning",
        "polymer-process.svg": "polymer-to-process multiscale transfer",
        "mesoscale-phase-field.svg": "coarse-graining, phase evolution and morphology evidence",
        "continuum-multiphysics.svg": "CFD, FEM, heat, mechanics and field coupling",
        "process-optimization-uq.svg": "flowsheet optimization, sensitivity, UQ and reviewed decisions",
        "uncertainty-sensitivity.svg": "uncertainty propagation, sensitivity ranking and decision limits",
        "hpc-execution-provenance.svg": "bounded execution, scheduler boundaries and provenance",
        "engine-ecosystem.svg": "external solver adapter ecosystem",
        "evidence-loop.svg": "fail-closed scientific acceptance loop",
        "confidence-ladder.svg": "C0–C5 confidence model",
        "digital-thread.svg": "reproducibility and supply-chain evidence",
    }
    lines = [
        "# README visual assets",
        "",
        "This directory contains original, repository-local SVG illustrations created for the TsaoSciComputation documentation.",
        "",
        "## Design and trust policy",
        "",
        "- Every asset is self-contained SVG with an accessible `<title>` and `<desc>`.",
        "- Assets use no external fonts, scripts, raster images, network resources, event handlers, or tracking elements.",
        "- Diagrams explain architecture and scientific boundaries; they are not solver screenshots or claims of live third-party execution.",
        "- Text labels are intentionally concise and must remain consistent with registries, workflows, and machine-readable evidence.",
        "- README references use relative paths so visuals remain available in repository clones and source archives.",
        "",
        "## Asset set",
        "",
    ]
    lines.extend(f"- `{name}` — {descriptions[name]}" for name in VISUAL_NAMES)
    lines.extend(
        [
            "",
            "Run `python -m pytest tests/test_readme_visuals.py -q` to validate the asset inventory and bilingual README references.",
            "",
        ]
    )
    (root / "README.md").write_text(
        "\n".join(lines), encoding="utf-8", newline="\n"
    )


def update_changelog() -> None:
    path = Path("CHANGELOG.md")
    text = path.read_text(encoding="utf-8")
    old = "- Expanded the bilingual project homepage to twelve repository-local scientific SVG diagrams covering multiscale architecture, AI orchestration, DFT, molecular dynamics, polymers, continuum multiphysics, process optimization, evidence, confidence and reproducibility."
    new = "- Expanded the bilingual project homepage to eighteen repository-local scientific SVG diagrams, adding dedicated enhanced-sampling, reaction-kinetics, ML-potential, mesoscale-morphology, HPC-provenance and UQ/sensitivity views to the existing multiscale atlas."
    if old in text:
        text = text.replace(old, new, 1)
    elif new not in text:
        raise RuntimeError("Changelog visual-atlas entry missing")
    path.write_text(text, encoding="utf-8", newline="\n")


def main() -> None:
    visual_root = Path("assets/visuals")
    missing = [name for name in VISUAL_NAMES if not (visual_root / name).is_file()]
    if missing:
        raise RuntimeError(f"missing visual assets: {missing}")

    insert_atlas(
        Path("README.md"),
        "## Specialized simulation and AI capability atlas",
        "## Solver-aware ecosystem",
        ENGLISH_ATLAS,
    )
    insert_atlas(
        Path("README.zh-CN.md"),
        "## 专项模拟与 AI 能力图谱",
        "## 求解器感知型生态",
        CHINESE_ATLAS,
    )

    english = Path("README.md").read_text(encoding="utf-8").replace(
        "The 12 illustrations in `assets/visuals/`",
        "The 18 illustrations in `assets/visuals/`",
    )
    Path("README.md").write_text(english, encoding="utf-8", newline="\n")
    chinese = Path("README.zh-CN.md").read_text(encoding="utf-8").replace(
        "`assets/visuals/` 中的 12 幅图片",
        "`assets/visuals/` 中的 18 幅图片",
    )
    Path("README.zh-CN.md").write_text(chinese, encoding="utf-8", newline="\n")

    write_inventory(visual_root)
    Path("tests/test_readme_visuals.py").write_text(
        textwrap.dedent(VISUAL_TEST), encoding="utf-8", newline="\n"
    )
    update_changelog()

    evidence_path = Path("reports/CURRENT_MAIN_VERIFICATION.json")
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    evidence["counts"]["visual_assets"] = len(VISUAL_NAMES)
    evidence["visual_atlas_version"] = 3
    evidence_path.write_text(
        json.dumps(evidence, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


if __name__ == "__main__":
    main()
