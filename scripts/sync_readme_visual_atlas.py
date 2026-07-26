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
        "periodic-materials-stability.svg",
        "Periodic materials stability and defect workflow",
        "Crystal relaxation, reciprocal-space convergence, defect energetics, phonon stability and observable acceptance.",
        "Periodic materials: structure → stability → defects",
        "Cells, reciprocal space and lattice dynamics remain separate evidence gates.",
        (
            ("Relax", "forces · stress · EOS"),
            ("Converge", "k-points · cutoff"),
            ("Defects", "formation · charge"),
            ("Phonons", "modes · stability"),
            ("Accept", "bands · DOS · domain"),
        ),
        "No stable-material claim without numerical convergence and dynamical stability.",
        "#8b5cf6",
        "#22d3ee",
    ),
    VisualSpec(
        "catalysis-microkinetics.svg",
        "Catalysis and microkinetic evidence workflow",
        "Active-site fidelity, elementary-step thermodynamics, coverage-aware microkinetics, rate control and bounded catalyst ranking.",
        "Catalysis: active site → elementary steps → microkinetics",
        "Energetics become turnover predictions only after closure and coverage checks.",
        (
            ("Site", "structure · charge"),
            ("Steps", "barriers · reverse"),
            ("Coverage", "sites · interactions"),
            ("Rates", "TOF · DRC"),
            ("Rank", "sensitivity · domain"),
        ),
        "Catalyst ranking is rejected when site, thermodynamic or coverage evidence is incomplete.",
        "#f97316",
        "#facc15",
    ),
    VisualSpec(
        "polymerization-population-balance.svg",
        "Polymerization population-balance workflow",
        "Elementary chain events, moments, population-balance equations, molecular-weight distributions and reactor-scale handoff.",
        "Polymerization kinetics: chain events → distributions",
        "Moments and PBEs retain chain-level meaning and identifiability.",
        (
            ("Network", "initiate · propagate"),
            ("Moments", "number · mass"),
            ("PBE", "birth · death"),
            ("Distributions", "MWD · composition"),
            ("Handoff", "calibrate · flowsheet"),
        ),
        "Conversion alone cannot validate molecular-weight or composition distributions.",
        "#ec4899",
        "#8b5cf6",
    ),
    VisualSpec(
        "extrusion-rheology-window.svg",
        "Extrusion rheology and processing-window workflow",
        "Non-Newtonian fitting, screw and die flow, residence-time and thermal history, product quality and reviewed operating windows.",
        "Extrusion rheology: constitutive law → product window",
        "Material functions, flow history and shape evidence are qualified separately.",
        (
            ("Fit law", "η(γ̇,T) · elasticity"),
            ("Flow", "screw · die · pressure"),
            ("History", "RTD · temperature"),
            ("Product", "swell · eccentricity"),
            ("Window", "robust · reviewed"),
        ),
        "A converged flow field is not automatically an acceptable processing window.",
        "#06b6d4",
        "#34d399",
    ),
    VisualSpec(
        "digital-twin-drift.svg",
        "Digital twin state estimation and drift workflow",
        "Scope contracts, soft sensing, online parameter updates, drift detection, applicability control and authorized decisions.",
        "Digital twin: scope → estimation → drift-aware decisions",
        "Online updates never outrun applicability, uncertainty or operating authority.",
        (
            ("Scope", "states · sensors"),
            ("Estimate", "soft sensor · UQ"),
            ("Update", "parameters · lineage"),
            ("Detect drift", "residual · shift"),
            ("Decide", "bounded · authorized"),
        ),
        "Out-of-domain or drifting twins fall back to review instead of silent automation.",
        "#3b82f6",
        "#a78bfa",
    ),
    VisualSpec(
        "fem-verification-convergence.svg",
        "Finite-element verification and convergence workflow",
        "Governing equations, weak forms, mesh and time-step studies, solver tolerances, conservation and qualified field acceptance.",
        "FEM verification: equations → discretization → fields",
        "A solved system is not accepted until formulation and convergence agree.",
        (
            ("Contract", "equations · units"),
            ("Weak form", "BCs · domains"),
            ("Discretize", "mesh · Δt"),
            ("Verify", "residual · balance"),
            ("Accept", "benchmark · domain"),
        ),
        "Field plots without mesh, time-step and balance evidence remain unqualified.",
        "#14b8a6",
        "#60a5fa",
    ),
)

ENGLISH_MARKERS = ("<!-- V5_VISUAL_ATLAS:START -->", "<!-- V5_VISUAL_ATLAS:END -->")
CHINESE_MARKERS = ENGLISH_MARKERS

ENGLISH_BLOCK = """<!-- V5_VISUAL_ATLAS:START -->
## Materials, manufacturing and model-lifecycle atlas

<table>
<tr>
<td width="50%"><img src="assets/visuals/periodic-materials-stability.svg" alt="Periodic materials stability defects and phonons" width="100%"></td>
<td width="50%"><img src="assets/visuals/catalysis-microkinetics.svg" alt="Catalysis active sites and microkinetic evidence" width="100%"></td>
</tr>
<tr>
<td align="center"><b>Periodic materials</b><br>Relaxation, convergence, defects, phonons and observable-level acceptance.</td>
<td align="center"><b>Catalysis &amp; microkinetics</b><br>Sites, elementary steps, coverage, rates and bounded catalyst ranking.</td>
</tr>
<tr>
<td width="50%"><img src="assets/visuals/polymerization-population-balance.svg" alt="Polymerization moments and population balance workflow" width="100%"></td>
<td width="50%"><img src="assets/visuals/extrusion-rheology-window.svg" alt="Extrusion rheology flow history and processing window" width="100%"></td>
</tr>
<tr>
<td align="center"><b>Polymerization &amp; PBE</b><br>Elementary events, moments, molecular distributions, identifiability and scale handoff.</td>
<td align="center"><b>Extrusion rheology</b><br>Constitutive laws, screw/die flow, RTD, thermal history and product quality.</td>
</tr>
<tr>
<td width="50%"><img src="assets/visuals/digital-twin-drift.svg" alt="Digital twin state estimation and drift control" width="100%"></td>
<td width="50%"><img src="assets/visuals/fem-verification-convergence.svg" alt="Finite element formulation and convergence verification" width="100%"></td>
</tr>
<tr>
<td align="center"><b>Digital twin lifecycle</b><br>Scope, estimation, online updates, drift, applicability and human authority.</td>
<td align="center"><b>FEM verification</b><br>Governing equations, weak forms, mesh/time-step convergence and balance evidence.</td>
</tr>
</table>

These views expose six implemented capability families that were previously present in the registry but not independently visualized. Each keeps numerical completion separate from scientific acceptance.
<!-- V5_VISUAL_ATLAS:END -->"""

CHINESE_BLOCK = """<!-- V5_VISUAL_ATLAS:START -->
## 材料、制造与模型生命周期图谱

<table>
<tr>
<td width="50%"><img src="assets/visuals/periodic-materials-stability.svg" alt="周期材料稳定性 缺陷与声子工作流" width="100%"></td>
<td width="50%"><img src="assets/visuals/catalysis-microkinetics.svg" alt="催化活性位与微观动力学证据工作流" width="100%"></td>
</tr>
<tr>
<td align="center"><b>周期材料</b><br>结构弛豫、数值收敛、缺陷、声子与观测量级验收。</td>
<td align="center"><b>催化与微观动力学</b><br>活性位、基元步骤、覆盖度、速率和有边界的催化剂排序。</td>
</tr>
<tr>
<td width="50%"><img src="assets/visuals/polymerization-population-balance.svg" alt="聚合动力学矩模型与群体平衡工作流" width="100%"></td>
<td width="50%"><img src="assets/visuals/extrusion-rheology-window.svg" alt="挤出流变 流动历史与加工窗口" width="100%"></td>
</tr>
<tr>
<td align="center"><b>聚合动力学与 PBE</b><br>基元事件、矩模型、分子分布、可辨识性和跨尺度交接。</td>
<td align="center"><b>挤出流变</b><br>本构关系、螺杆/口模流动、停留时间、热历史和制品质量。</td>
</tr>
<tr>
<td width="50%"><img src="assets/visuals/digital-twin-drift.svg" alt="数字孪生状态估计与漂移控制" width="100%"></td>
<td width="50%"><img src="assets/visuals/fem-verification-convergence.svg" alt="有限元方程与收敛验证工作流" width="100%"></td>
</tr>
<tr>
<td align="center"><b>数字孪生生命周期</b><br>范围合同、状态估计、在线更新、漂移、适用域和人工授权。</td>
<td align="center"><b>FEM 验证</b><br>控制方程、弱形式、网格/时间步收敛和守恒证据。</td>
</tr>
</table>

这六类能力在注册表中均已实现，但此前缺少独立图示。所有图均将数值计算完成与科学验收明确分离。
<!-- V5_VISUAL_ATLAS:END -->"""

INVENTORY_LINES = tuple(
    {
        "periodic-materials-stability.svg": "periodic relaxation, defects, phonons and stability",
        "catalysis-microkinetics.svg": "active sites, elementary steps and microkinetic evidence",
        "polymerization-population-balance.svg": "chain events, moments, PBEs and molecular distributions",
        "extrusion-rheology-window.svg": "constitutive rheology, flow history and processing windows",
        "digital-twin-drift.svg": "state estimation, online updates and drift-aware decisions",
        "fem-verification-convergence.svg": "weak forms, discretization convergence and balance checks",
    }.items()
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
    start, end = ENGLISH_MARKERS
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
        english_path.read_text(encoding="utf-8"),
        ENGLISH_BLOCK,
        "## Solver-aware ecosystem",
    )
    english = re.sub(
        r"The \d+ illustrations in `assets/visuals/`",
        "The 30 illustrations in `assets/visuals/`",
        english,
        count=1,
    )
    chinese = _replace_or_insert(
        chinese_path.read_text(encoding="utf-8"),
        CHINESE_BLOCK,
        "## 求解器感知型生态",
    )
    chinese = re.sub(
        r"`assets/visuals/` 中的 \d+ 幅图片",
        "`assets/visuals/` 中的 30 幅图片",
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
        "- Expanded the bilingual scientific atlas from twenty-four to thirty "
        "repository-local SVG diagrams, adding periodic-material stability, "
        "catalysis/microkinetics, polymerization/PBE, extrusion rheology, "
        "digital-twin drift and FEM-verification views."
    )
    changelog, count = re.subn(
        r"(?m)^- Expanded the bilingual project homepage to .*$",
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
    desired = _desired_documents(root)
    for spec in NEW_VISUALS:
        desired[root / "assets" / "visuals" / spec.filename] = _svg(spec)

    changed = [
        path
        for path, content in desired.items()
        if not path.exists() or path.read_text(encoding="utf-8") != content
    ]
    if check and changed:
        raise ValueError(
            "visual atlas is not synchronized: "
            + ", ".join(path.relative_to(root).as_posix() for path in changed)
        )
    if not check:
        for path, content in desired.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8", newline="\n")
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
