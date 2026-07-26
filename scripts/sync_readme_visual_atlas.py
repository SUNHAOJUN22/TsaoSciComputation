from __future__ import annotations

import argparse
import re
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class VisualSpec:
    filename: str
    title: str
    description: str
    heading: str
    subtitle: str
    stages: tuple[tuple[str, str], ...]
    footer: str
    accent_start: str
    accent_end: str


NEW_VISUALS = (
    VisualSpec(
        "scale-multifidelity-plan.svg",
        "Scientific scale selection and multi-fidelity planning workflow",
        "Problem decomposition, scale boundaries, method fitness, fidelity ladders, validation budgets and evidence-qualified planning.",
        "Scientific planning: question → scales → fidelity",
        "A calculation plan is accepted only when every scale and approximation has an explicit role.",
        (
            ("Decompose", "claims · observables"),
            ("Bound scales", "electron · process"),
            ("Fit methods", "physics · cost"),
            ("Plan fidelity", "screen · refine"),
            ("Accept", "budget · evidence"),
        ),
        "Method popularity cannot replace fitness, scale coverage or a validation plan.",
        "#38bdf8",
        "#a78bfa",
    ),
    VisualSpec(
        "quantum-chemistry-thermochemistry.svg",
        "Molecular quantum chemistry and thermochemistry workflow",
        "Geometry, conformers, frequencies, electronic energies, solvation, thermochemical corrections and reaction-path acceptance.",
        "Quantum chemistry: structure → energy → thermochemistry",
        "Electronic energies become chemical claims only after structure and thermal corrections agree.",
        (
            ("Structure", "geometry · conformers"),
            ("Curvature", "frequencies · TS"),
            ("Energy", "basis · method"),
            ("Environment", "solvation · standard state"),
            ("Accept", "ΔG · pathway"),
        ),
        "A stationary point without frequency, convergence and state-definition evidence is not accepted.",
        "#8b5cf6",
        "#f472b6",
    ),
    VisualSpec(
        "molecular-dynamics-transport.svg",
        "Molecular dynamics equilibration transport and convergence workflow",
        "System construction, force-field qualification, minimization, ensemble equilibration, production sampling, transport observables and trajectory convergence.",
        "Molecular dynamics: build → equilibrate → observe",
        "A long trajectory is not evidence unless ensembles, sampling and uncertainty are qualified.",
        (
            ("Build", "topology · composition"),
            ("Qualify", "force field · units"),
            ("Equilibrate", "NVT · NPT"),
            ("Sample", "production · replicas"),
            ("Observe", "diffusion · RDF · UQ"),
        ),
        "Transport and structure observables require convergence across time origins, blocks and replicas.",
        "#22d3ee",
        "#34d399",
    ),
    VisualSpec(
        "polymer-composite-topology.svg",
        "Polymer composite interface topology and property workflow",
        "Amorphous and crystalline models, filler localization, adhesion, percolation, rheology, dielectric response and bounded structure-property mapping.",
        "Polymer composites: interface → topology → property",
        "Morphology descriptors remain distinct from causal and transferable property claims.",
        (
            ("Construct", "amorphous · crystal"),
            ("Interface", "adhesion · localization"),
            ("Topology", "dispersion · percolation"),
            ("Response", "rheology · dielectric"),
            ("Map", "property · domain"),
        ),
        "A visually connected network is not automatically electrically or mechanically percolated.",
        "#f97316",
        "#facc15",
    ),
    VisualSpec(
        "flowsheet-convergence-balances.svg",
        "Process flowsheet convergence and balance workflow",
        "Property packages, unit models, recycle convergence, mass and energy closure, optimization, uncertainty and lawful simulator handoff.",
        "Process simulation: property basis → converged flowsheet",
        "A converged recycle is accepted only after physical balances and model domains close.",
        (
            ("Properties", "components · phases"),
            ("Units", "model · parameters"),
            ("Recycle", "tear · converge"),
            ("Balances", "mass · energy"),
            ("Decide", "optimize · UQ"),
        ),
        "Numerical convergence cannot override invalid thermodynamics, balances or operating constraints.",
        "#06b6d4",
        "#3b82f6",
    ),
    VisualSpec(
        "multiscale-handoff-uncertainty.svg",
        "Multiscale handoff and uncertainty governance workflow",
        "DFT, molecular, morphology, population-balance and CFD outputs transferred through explicit contracts with uncertainty and applicability gates.",
        "Multiscale handoff: observable → contract → receiving model",
        "Every transfer preserves definitions, units, uncertainty, provenance and applicability.",
        (
            ("Source", "DFT · MD · PBE"),
            ("Extract", "observable · statistics"),
            ("Contract", "units · semantics"),
            ("Propagate", "UQ · sensitivity"),
            ("Receive", "validate · accept"),
        ),
        "A cross-scale parameter is rejected when its meaning or uncertainty changes silently.",
        "#14b8a6",
        "#a78bfa",
    ),
)

MARKERS = ("<!-- V6_VISUAL_ATLAS:START -->", "<!-- V6_VISUAL_ATLAS:END -->")

ENGLISH_BLOCK = """<!-- V6_VISUAL_ATLAS:START -->
## Planning, molecular and cross-scale capability atlas

<table>
<tr>
<td width="50%"><img src="assets/visuals/scale-multifidelity-plan.svg" alt="Scientific scale selection and multi fidelity planning" width="100%"></td>
<td width="50%"><img src="assets/visuals/quantum-chemistry-thermochemistry.svg" alt="Molecular quantum chemistry thermochemistry and reaction path" width="100%"></td>
</tr>
<tr>
<td align="center"><b>Scale and multi-fidelity planning</b><br>Claims, scale boundaries, method fitness, fidelity ladders and evidence budgets.</td>
<td align="center"><b>Quantum chemistry and thermochemistry</b><br>Structures, frequencies, energies, solvation, thermal corrections and pathways.</td>
</tr>
<tr>
<td width="50%"><img src="assets/visuals/molecular-dynamics-transport.svg" alt="Molecular dynamics equilibration transport and trajectory convergence" width="100%"></td>
<td width="50%"><img src="assets/visuals/polymer-composite-topology.svg" alt="Polymer composite interface topology percolation and properties" width="100%"></td>
</tr>
<tr>
<td align="center"><b>Molecular dynamics and transport</b><br>System qualification, ensembles, production sampling, observables and convergence.</td>
<td align="center"><b>Polymer composite topology</b><br>Interfaces, localization, dispersion, percolation and bounded property maps.</td>
</tr>
<tr>
<td width="50%"><img src="assets/visuals/flowsheet-convergence-balances.svg" alt="Process flowsheet recycle convergence mass and energy balances" width="100%"></td>
<td width="50%"><img src="assets/visuals/multiscale-handoff-uncertainty.svg" alt="Multiscale handoff contracts uncertainty and applicability" width="100%"></td>
</tr>
<tr>
<td align="center"><b>Flowsheet convergence and balances</b><br>Properties, units, recycle closure, balances, optimization and uncertainty.</td>
<td align="center"><b>Multiscale handoff and uncertainty</b><br>Observable semantics, units, provenance, uncertainty and receiving-model acceptance.</td>
</tr>
</table>

These six views expose implemented capability families that were previously distributed across the registry but lacked dedicated visual explanations. They do not claim bundled solvers or live production execution.
<!-- V6_VISUAL_ATLAS:END -->"""

CHINESE_BLOCK = """<!-- V6_VISUAL_ATLAS:START -->
## 科学规划、分子模拟与跨尺度能力图谱

<table>
<tr>
<td width="50%"><img src="assets/visuals/scale-multifidelity-plan.svg" alt="科学尺度选择与多保真计算规划" width="100%"></td>
<td width="50%"><img src="assets/visuals/quantum-chemistry-thermochemistry.svg" alt="分子量子化学 热化学与反应路径" width="100%"></td>
</tr>
<tr>
<td align="center"><b>尺度选择与多保真规划</b><br>结论、尺度边界、方法适配、保真度阶梯和证据预算。</td>
<td align="center"><b>量子化学与热化学</b><br>结构、频率、能量、溶剂化、热修正和反应路径。</td>
</tr>
<tr>
<td width="50%"><img src="assets/visuals/molecular-dynamics-transport.svg" alt="分子动力学平衡 输运与轨迹收敛" width="100%"></td>
<td width="50%"><img src="assets/visuals/polymer-composite-topology.svg" alt="聚合物复合材料界面 拓扑 渗流与性能" width="100%"></td>
</tr>
<tr>
<td align="center"><b>分子动力学与输运</b><br>体系资格、统计系综、生产采样、观测量和收敛性。</td>
<td align="center"><b>聚合物复合材料拓扑</b><br>界面、选择性定位、分散、渗流和有边界的性能映射。</td>
</tr>
<tr>
<td width="50%"><img src="assets/visuals/flowsheet-convergence-balances.svg" alt="流程模拟回路收敛 物料与能量衡算" width="100%"></td>
<td width="50%"><img src="assets/visuals/multiscale-handoff-uncertainty.svg" alt="跨尺度交接合同 不确定度与适用域" width="100%"></td>
</tr>
<tr>
<td align="center"><b>流程收敛与衡算</b><br>物性、单元、循环回路、物料/能量闭合、优化和不确定度。</td>
<td align="center"><b>跨尺度交接与不确定度</b><br>观测量语义、单位、溯源、不确定度和接收模型验收。</td>
</tr>
</table>

这六类能力均已存在于能力注册表中，但此前缺少独立视觉说明。图示不代表仓库打包了外部求解器，也不构成生产环境真实执行证据。
<!-- V6_VISUAL_ATLAS:END -->"""

INVENTORY_LINES = (
    ("scale-multifidelity-plan.svg", "problem decomposition, scale selection and multi-fidelity planning"),
    ("quantum-chemistry-thermochemistry.svg", "molecular structures, frequencies, energies and thermochemical acceptance"),
    ("molecular-dynamics-transport.svg", "equilibration, production sampling, transport and trajectory convergence"),
    ("polymer-composite-topology.svg", "interfaces, localization, percolation and structure-property evidence"),
    ("flowsheet-convergence-balances.svg", "property packages, recycle convergence and balance closure"),
    ("multiscale-handoff-uncertainty.svg", "cross-scale contracts, uncertainty propagation and applicability"),
)


def _svg(spec: VisualSpec) -> str:
    count = len(spec.stages)
    left = 68
    gap = 20
    width = (1064 - gap * (count - 1)) / count
    boxes: list[str] = []
    arrows: list[str] = []
    for index, (label, detail) in enumerate(spec.stages):
        x = left + index * (width + gap)
        boxes.append(
            f'<rect x="{x:.1f}" y="215" width="{width:.1f}" height="180" rx="18" class="box"/>'
        )
        boxes.append(f'<text x="{x + 20:.1f}" y="258" class="label">{label}</text>')
        boxes.append(f'<text x="{x + 20:.1f}" y="291" class="small">{detail}</text>')
        boxes.append(
            f'<circle cx="{x + width / 2:.1f}" cy="342" r="{24 + index * 2}" '
            f'fill="none" stroke="url(#accent)" stroke-width="4" '
            f'opacity="{0.95 - index * 0.08:.2f}"/>'
        )
        if index < count - 1:
            start = x + width
            end = start + gap
            arrows.append(f'<path d="M{start:.1f} 305H{end:.1f}" class="line"/>')
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 680" role="img" aria-labelledby="title desc">
<title id="title">{spec.title}</title>
<desc id="desc">{spec.description}</desc>
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#071426"/>
    <stop offset="0.55" stop-color="#10233f"/>
    <stop offset="1" stop-color="#071426"/>
  </linearGradient>
  <linearGradient id="accent" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="{spec.accent_start}"/>
    <stop offset="1" stop-color="{spec.accent_end}"/>
  </linearGradient>
  <style>
    .title{{font:700 34px ui-sans-serif,system-ui;fill:#f8fafc}}
    .sub{{font:500 17px ui-sans-serif,system-ui;fill:#cbd5e1}}
    .label{{font:700 17px ui-sans-serif,system-ui;fill:#f8fafc}}
    .small{{font:500 14px ui-sans-serif,system-ui;fill:#cbd5e1}}
    .box{{fill:#0f2745;stroke:#3b82f6;stroke-width:1.5}}
    .line{{fill:none;stroke:url(#accent);stroke-width:4;stroke-linecap:round}}
  </style>
</defs>
<rect width="1200" height="680" rx="28" fill="url(#bg)"/>
<rect x="28" y="28" width="1144" height="624" rx="24" fill="none" stroke="#1e3a5f"/>
<text x="68" y="92" class="title">{spec.heading}</text>
<text x="68" y="126" class="sub">{spec.subtitle}</text>
{"".join(boxes)}
{"".join(arrows)}
<rect x="68" y="455" width="1064" height="125" rx="18" fill="#0b1d34" stroke="#334155"/>
<text x="96" y="505" class="label">Evidence boundary</text>
<text x="96" y="542" class="sub">{spec.footer}</text>
<path d="M96 565H1100" stroke="url(#accent)" stroke-width="3" stroke-linecap="round"/>
</svg>
"""


def _replace_or_insert(text: str, block: str, heading: str) -> str:
    start, end = MARKERS
    pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.DOTALL)
    if pattern.search(text):
        return pattern.sub(block, text, count=1)
    if heading not in text:
        raise ValueError(f"README insertion heading missing: {heading}")
    return text.replace(heading, block + "\n\n" + heading, 1)


def _desired_documents(root: Path) -> dict[Path, str]:
    english_path = root / "README.md"
    chinese_path = root / "README.zh-CN.md"
    inventory_path = root / "assets" / "visuals" / "README.md"
    changelog_path = root / "CHANGELOG.md"

    english = _replace_or_insert(
        english_path.read_text(encoding="utf-8"), ENGLISH_BLOCK, "## Solver-aware ecosystem"
    )
    english = re.sub(
        r"The \d+ illustrations in `assets/visuals/`",
        "The 36 illustrations in `assets/visuals/`",
        english,
        count=1,
    )
    chinese = _replace_or_insert(
        chinese_path.read_text(encoding="utf-8"), CHINESE_BLOCK, "## 求解器感知型生态"
    )
    chinese = re.sub(
        r"`assets/visuals/` 中的 \d+ 幅图片",
        "`assets/visuals/` 中的 36 幅图片",
        chinese,
        count=1,
    )

    inventory = inventory_path.read_text(encoding="utf-8")
    insert_at = inventory.find("\nRun `python")
    if insert_at < 0:
        raise ValueError("visual inventory insertion point missing")
    additions = "".join(f"- `{name}` — {description}\n" for name, description in INVENTORY_LINES)
    before = inventory[:insert_at].rstrip() + "\n"
    after = inventory[insert_at:]
    for name, _ in INVENTORY_LINES:
        before = re.sub(rf"(?m)^- `{re.escape(name)}` — .*\n?", "", before)
    inventory = before.rstrip() + "\n" + additions + after

    changelog = changelog_path.read_text(encoding="utf-8")
    bullet = (
        "- Expanded the bilingual scientific atlas from thirty to thirty-six "
        "repository-local SVG diagrams, adding scale/multi-fidelity planning, "
        "quantum-chemistry thermochemistry, MD transport/convergence, polymer-composite "
        "topology, flowsheet convergence and multiscale handoff/UQ views."
    )
    changelog, count = re.subn(
        r"(?m)^- Expanded the bilingual (?:project homepage|scientific atlas).*$",
        bullet,
        changelog,
        count=1,
    )
    if count == 0 and bullet not in changelog:
        changelog = changelog.replace("## Unreleased\n", f"## Unreleased\n\n{bullet}\n", 1)

    return {
        english_path: english.rstrip() + "\n",
        chinese_path: chinese.rstrip() + "\n",
        inventory_path: inventory.rstrip() + "\n",
        changelog_path: changelog.rstrip() + "\n",
    }


def synchronize(root: Path, *, check: bool = False) -> list[Path]:
    root = root.resolve()
    desired: dict[Path, str] = {
        root / "assets" / "visuals" / spec.filename: _svg(spec) for spec in NEW_VISUALS
    }
    desired.update(_desired_documents(root))
    changed = [
        path
        for path, content in desired.items()
        if not path.exists() or path.read_text(encoding="utf-8") != content
    ]
    if check and changed:
        names = ", ".join(str(path.relative_to(root)) for path in changed)
        raise ValueError(f"visual atlas is not synchronized: {names}")
    if not check:
        for path in changed:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(desired[path], encoding="utf-8", newline="\n")
    return changed


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Synchronize the bilingual scientific atlas.")
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--check", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    synchronize(args.root, check=args.check)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
