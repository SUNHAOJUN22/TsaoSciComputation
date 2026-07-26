from __future__ import annotations

import argparse
import html
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
        "conformer-solvation-excited-state.svg",
        "Conformer solvation and excited-state evidence workflow",
        "Conformer coverage, solvent and standard-state choices, excited-state screening, thermal corrections and observable acceptance.",
        "Molecular states: conformers → environment → observables",
        "State populations and environments remain explicit parts of the scientific claim.",
        (
            ("Conformers", "search · rank · deduplicate"),
            ("Environment", "solvent · standard state"),
            ("Excited states", "method · roots · character"),
            ("Thermal terms", "ZPE · entropy · free energy"),
            ("Accept", "population · spectrum · domain"),
        ),
        "A single optimized structure cannot support ensemble, solution or excited-state claims.",
        "#8b5cf6",
        "#38bdf8",
    ),
    VisualSpec(
        "surface-adsorption-migration.svg",
        "Surface adsorption defect and migration workflow",
        "Surface models, adsorption states, charged defects, migration pathways, finite-size corrections and bounded kinetic interpretation.",
        "Surfaces and defects: site → state → migration",
        "Energetics become mechanistic evidence only after model and correction checks.",
        (
            ("Surface", "termination · slab · vacuum"),
            ("Adsorption", "sites · coverage · reference"),
            ("Defects", "charge · chemical potentials"),
            ("Migration", "NEB · images · barrier"),
            ("Accept", "corrections · rates · domain"),
        ),
        "Barrier or adsorption rankings are rejected when reference states or finite-size effects are unresolved.",
        "#f97316",
        "#facc15",
    ),
    VisualSpec(
        "cfd-turbulence-multiphase.svg",
        "CFD turbulence multiphase and transport workflow",
        "Flow-domain qualification, turbulence and multiphase model selection, conjugate heat transfer, species transport and conservation evidence.",
        "CFD: model selection → coupled transport → conservation",
        "Mesh, closure laws and conservation remain separate acceptance gates.",
        (
            ("Domain", "geometry · BCs · mesh"),
            ("Closures", "laminar · turbulence"),
            ("Phases", "interface · slip · regime"),
            ("Transport", "heat · species · reaction"),
            ("Accept", "mass · energy · sensitivity"),
        ),
        "A converged residual history does not replace mesh, regime and balance validation.",
        "#06b6d4",
        "#34d399",
    ),
    VisualSpec(
        "reactor-scaleup-thermal-risk.svg",
        "Reactor scale-up and thermal-risk evidence workflow",
        "Ideal-reactor baselines, residence-time behavior, heat removal, runaway screening, parameter fitting and scale-up applicability.",
        "Reactor engineering: balances → heat removal → scale-up",
        "Kinetics, transport and protection assumptions are qualified independently.",
        (
            ("Baselines", "batch · CSTR · PFR"),
            ("Residence time", "RTD · mixing · bypass"),
            ("Thermal risk", "heat release · removal"),
            ("Scale-up", "transport · geometry · fit"),
            ("Accept", "scenario · margin · review"),
        ),
        "A fitted conversion curve cannot authorize scale-up or dismiss runaway risk.",
        "#ef4444",
        "#fb923c",
    ),
    VisualSpec(
        "dynamic-control-estimation.svg",
        "Dynamic control state-estimation and safety workflow",
        "Dynamic inventories, startup and shutdown logic, control structures, disturbance scenarios, state estimation and safety boundaries.",
        "Dynamic control: states → disturbances → bounded authority",
        "Control performance and independent safety protection remain distinct claims.",
        (
            ("States", "inventories · sensors · units"),
            ("Sequences", "startup · shutdown · modes"),
            ("Control", "PID · structure · constraints"),
            ("Estimate", "soft sensor · residual · UQ"),
            ("Boundary", "disturbance · safety · authority"),
        ),
        "A stable controller is not an independent protection layer and cannot authorize unsafe operation.",
        "#3b82f6",
        "#a78bfa",
    ),
    VisualSpec(
        "hpc-failure-recovery.svg",
        "HPC failure classification and bounded recovery workflow",
        "Environment probing, resource estimation, scheduler evidence, checkpoint integrity, failure classification and bounded recovery.",
        "HPC execution: preflight → failure evidence → recovery",
        "Automation is bounded by reproducibility, retry limits and preserved artifacts.",
        (
            ("Preflight", "software · license · resources"),
            ("Submit", "scheduler · limits · provenance"),
            ("Checkpoint", "state · hash · restart"),
            ("Classify", "input · solver · system"),
            ("Recover", "bounded retry · package · review"),
        ),
        "Unknown failures, corrupted checkpoints or repeated divergence stop automation and require review.",
        "#14b8a6",
        "#60a5fa",
    ),
)

MARKERS = ("<!-- V7_VISUAL_ATLAS:START -->", "<!-- V7_VISUAL_ATLAS:END -->")

ENGLISH_BLOCK = """<!-- V7_VISUAL_ATLAS:START -->
## Molecular states, transport and operational-resilience atlas

<table>
<tr>
<td width="50%"><img src="assets/visuals/conformer-solvation-excited-state.svg" alt="Conformer solvation excited state and thermochemistry workflow" width="100%"></td>
<td width="50%"><img src="assets/visuals/surface-adsorption-migration.svg" alt="Surface adsorption defect and migration evidence workflow" width="100%"></td>
</tr>
<tr>
<td align="center"><b>Molecular states and environments</b><br>Conformers, solvation, excited states, thermal corrections and population-aware observables.</td>
<td align="center"><b>Surfaces, defects and migration</b><br>Surface models, adsorption references, charged defects, pathways and correction evidence.</td>
</tr>
<tr>
<td width="50%"><img src="assets/visuals/cfd-turbulence-multiphase.svg" alt="CFD turbulence multiphase heat and species transport" width="100%"></td>
<td width="50%"><img src="assets/visuals/reactor-scaleup-thermal-risk.svg" alt="Reactor residence time scale up and thermal risk workflow" width="100%"></td>
</tr>
<tr>
<td align="center"><b>CFD closures and transport</b><br>Turbulence, multiphase regimes, heat/species coupling, mesh evidence and conservation.</td>
<td align="center"><b>Reactor scale-up and thermal risk</b><br>Ideal baselines, RTD, heat removal, runaway scenarios and qualified scale transfer.</td>
</tr>
<tr>
<td width="50%"><img src="assets/visuals/dynamic-control-estimation.svg" alt="Dynamic control disturbance state estimation and safety boundaries" width="100%"></td>
<td width="50%"><img src="assets/visuals/hpc-failure-recovery.svg" alt="HPC checkpoint failure classification and bounded recovery" width="100%"></td>
</tr>
<tr>
<td align="center"><b>Dynamic control and estimation</b><br>Inventories, operating sequences, control structures, disturbances and safety authority.</td>
<td align="center"><b>HPC failure and recovery</b><br>Preflight, scheduler evidence, checkpoints, failure classes and bounded retries.</td>
</tr>
</table>

These six views make additional implemented capability families explicit while retaining strict boundaries between numerical completion, scientific validity, operational safety and human authorization.
<!-- V7_VISUAL_ATLAS:END -->"""

CHINESE_BLOCK = """<!-- V7_VISUAL_ATLAS:START -->
## 分子状态、耦合输运与运行韧性图谱

<table>
<tr>
<td width="50%"><img src="assets/visuals/conformer-solvation-excited-state.svg" alt="构象 溶剂化 激发态与热化学工作流" width="100%"></td>
<td width="50%"><img src="assets/visuals/surface-adsorption-migration.svg" alt="表面 吸附 缺陷与迁移证据工作流" width="100%"></td>
</tr>
<tr>
<td align="center"><b>分子状态与环境</b><br>构象、溶剂化、激发态、热校正及考虑布居的观测量。</td>
<td align="center"><b>表面、缺陷与迁移</b><br>表面模型、吸附参照、带电缺陷、迁移路径和修正证据。</td>
</tr>
<tr>
<td width="50%"><img src="assets/visuals/cfd-turbulence-multiphase.svg" alt="CFD 湍流 多相流 传热与组分输运" width="100%"></td>
<td width="50%"><img src="assets/visuals/reactor-scaleup-thermal-risk.svg" alt="反应器停留时间 放大与热风险工作流" width="100%"></td>
</tr>
<tr>
<td align="center"><b>CFD 闭合模型与输运</b><br>湍流、多相流型、热/组分耦合、网格证据和守恒。</td>
<td align="center"><b>反应器放大与热风险</b><br>理想模型、RTD、移热、失控场景和合格的尺度迁移。</td>
</tr>
<tr>
<td width="50%"><img src="assets/visuals/dynamic-control-estimation.svg" alt="动态控制 扰动 状态估计与安全边界" width="100%"></td>
<td width="50%"><img src="assets/visuals/hpc-failure-recovery.svg" alt="HPC 检查点 失败分类与有界恢复" width="100%"></td>
</tr>
<tr>
<td align="center"><b>动态控制与状态估计</b><br>库存、开停车序列、控制结构、扰动和安全权限。</td>
<td align="center"><b>HPC 失败与恢复</b><br>环境前检、调度证据、检查点、失败分类和有界重试。</td>
</tr>
</table>

这六幅图进一步显式呈现已有能力，并继续严格区分数值完成、科学有效性、运行安全与人工授权。
<!-- V7_VISUAL_ATLAS:END -->"""

INVENTORY_LINES = (
    (
        "conformer-solvation-excited-state.svg",
        "conformers, solvation, excited states and thermal populations",
    ),
    (
        "surface-adsorption-migration.svg",
        "surfaces, adsorption, charged defects and migration pathways",
    ),
    (
        "cfd-turbulence-multiphase.svg",
        "turbulence, multiphase regimes and coupled transport evidence",
    ),
    (
        "reactor-scaleup-thermal-risk.svg",
        "reactor residence time, heat removal, runaway and scale-up",
    ),
    (
        "dynamic-control-estimation.svg",
        "dynamic control, disturbances, state estimation and safety boundaries",
    ),
    ("hpc-failure-recovery.svg", "checkpoints, failure classification and bounded recovery"),
)


def _svg(spec: VisualSpec) -> str:
    left = 68.0
    gap = 20.0
    width = (1064.0 - gap * (len(spec.stages) - 1)) / len(spec.stages)
    boxes: list[str] = []
    arrows: list[str] = []
    for index, (label, detail) in enumerate(spec.stages):
        x = left + index * (width + gap)
        boxes.extend(
            [
                f'<rect x="{x:.1f}" y="215" width="{width:.1f}" height="180" rx="18" class="box"/>',
                f'<text x="{x + 18:.1f}" y="258" class="label">{html.escape(label)}</text>',
                f'<text x="{x + 18:.1f}" y="292" class="small">{html.escape(detail)}</text>',
                f'<circle cx="{x + width / 2:.1f}" cy="342" r="{23 + index * 2}" fill="none" stroke="url(#accent)" stroke-width="4" opacity="{0.96 - index * 0.08:.2f}"/>',
            ]
        )
        if index < len(spec.stages) - 1:
            arrows.append(f'<path d="M{x + width:.1f} 305H{x + width + gap:.1f}" class="line"/>')
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 680" role="img" aria-labelledby="title desc">
<title id="title">{html.escape(spec.title)}</title>
<desc id="desc">{html.escape(spec.description)}</desc>
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
    .small{{font:500 13px ui-sans-serif,system-ui;fill:#cbd5e1}}
    .box{{fill:#0f2745;stroke:#3b82f6;stroke-width:1.5}}
    .line{{fill:none;stroke:url(#accent);stroke-width:4;stroke-linecap:round}}
  </style>
</defs>
<rect width="1200" height="680" rx="28" fill="url(#bg)"/>
<rect x="28" y="28" width="1144" height="624" rx="24" fill="none" stroke="#1e3a5f"/>
<text x="68" y="92" class="title">{html.escape(spec.heading)}</text>
<text x="68" y="126" class="sub">{html.escape(spec.subtitle)}</text>
{"".join(boxes)}
{"".join(arrows)}
<rect x="68" y="455" width="1064" height="125" rx="18" fill="#0b1d34" stroke="#334155"/>
<text x="96" y="505" class="label">Evidence boundary</text>
<text x="96" y="542" class="sub">{html.escape(spec.footer)}</text>
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
        english_path.read_text(encoding="utf-8"),
        ENGLISH_BLOCK,
        "## Solver-aware ecosystem",
    )
    english = re.sub(
        r"The \d+ illustrations in `assets/visuals/`",
        "The 42 illustrations in `assets/visuals/`",
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
        "`assets/visuals/` 中的 42 幅图片",
        chinese,
        count=1,
    )

    inventory = inventory_path.read_text(encoding="utf-8")
    insert_at = inventory.find("\nRun `python")
    if insert_at < 0:
        raise ValueError("visual inventory insertion point missing")
    before = inventory[:insert_at].rstrip() + "\n"
    after = inventory[insert_at:]
    for name, _ in INVENTORY_LINES:
        before = re.sub(rf"(?m)^- `{re.escape(name)}` — .*\n?", "", before)
    additions = "".join(f"- `{name}` — {description}\n" for name, description in INVENTORY_LINES)
    inventory = before.rstrip() + "\n" + additions + after

    changelog = changelog_path.read_text(encoding="utf-8")
    bullet = (
        "- Expanded the bilingual scientific atlas from thirty-six to forty-two "
        "repository-local SVG diagrams, adding molecular-state/environment, "
        "surface/defect migration, CFD closure, reactor scale-up, dynamic-control "
        "and HPC-recovery views."
    )
    if bullet not in changelog:
        changelog = changelog.replace("## Unreleased\n", f"## Unreleased\n\n{bullet}\n", 1)

    return {
        english_path: english.rstrip() + "\n",
        chinese_path: chinese.rstrip() + "\n",
        inventory_path: inventory.rstrip() + "\n",
        changelog_path: changelog.rstrip() + "\n",
    }


def synchronize(root: Path, *, check: bool = False) -> list[Path]:
    root = root.resolve()
    desired: dict[Path, str] = _desired_documents(root)
    for spec in NEW_VISUALS:
        desired[root / "assets" / "visuals" / spec.filename] = _svg(spec)

    changed = [
        path
        for path, content in desired.items()
        if not path.exists() or path.read_text(encoding="utf-8") != content
    ]
    if check and changed:
        relative = ", ".join(str(path.relative_to(root)) for path in changed)
        raise ValueError(f"V7 visual atlas is not synchronized: {relative}")
    if not check:
        for path, content in desired.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8", newline="\n")
    return changed


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Synchronize the V7 README visual atlas.")
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--check", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    synchronize(args.root, check=args.check)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
