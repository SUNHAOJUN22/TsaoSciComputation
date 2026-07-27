from __future__ import annotations

import argparse
import html
import re
import sys
from collections.abc import Iterable
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.regenerate_readme_visuals_v10 import (  # noqa: E402
    ROOT,
    TOKENS,
    VISUAL_ROOT,
    VisualSpec,
    parse_specs,
    stage_glyph,
    wrap_words,
)
from scripts.regenerate_readme_visuals_v11 import (  # noqa: E402
    BENTO_FILES,
    LOOP_FILES,
    RISK_FILES,
    layout_for,
)

SYSTEM_ID = "uiux-pro-max-scientific-swiss-v3"
SYSTEM_MARKER = re.compile(
    r"<!-- V1[012]_VISUAL_SYSTEM:START -->.*?<!-- V1[012]_VISUAL_SYSTEM:END -->",
    re.DOTALL,
)
ENGLISH_ATLAS = re.compile(r"## Architecture at a glance\n.*?(?=\n## Quick start)", re.DOTALL)
CHINESE_ATLAS = re.compile(r"## 架构总览\n.*?(?=\n## 快速开始)", re.DOTALL)

GROUPS = (
    (
        "electronic",
        (
            "quantum-to-md.svg",
            "electronic-structure-landscape.svg",
            "free-energy-sampling.svg",
            "reaction-kinetics-network.svg",
            "ml-potential-active-learning.svg",
            "periodic-materials-stability.svg",
            "catalysis-microkinetics.svg",
            "quantum-chemistry-thermochemistry.svg",
            "molecular-dynamics-transport.svg",
            "conformer-solvation-excited-state.svg",
            "surface-adsorption-migration.svg",
            "spectroscopy-observables.svg",
        ),
    ),
    (
        "materials",
        (
            "polymer-process.svg",
            "mesoscale-phase-field.svg",
            "electrochemical-interface.svg",
            "transport-degradation.svg",
            "polymerization-population-balance.svg",
            "extrusion-rheology-window.svg",
            "polymer-composite-topology.svg",
            "multiscale-handoff-uncertainty.svg",
        ),
    ),
    (
        "process",
        (
            "continuum-multiphysics.svg",
            "process-optimization-uq.svg",
            "reactor-safety-control.svg",
            "fem-verification-convergence.svg",
            "flowsheet-convergence-balances.svg",
            "cfd-turbulence-multiphase.svg",
            "reactor-scaleup-thermal-risk.svg",
            "dynamic-control-estimation.svg",
            "digital-twin-drift.svg",
        ),
    ),
    (
        "governance",
        (
            "uncertainty-sensitivity.svg",
            "inverse-design-loop.svg",
            "data-model-governance.svg",
            "hpc-execution-provenance.svg",
            "engine-ecosystem.svg",
            "evidence-loop.svg",
            "confidence-ladder.svg",
            "digital-thread.svg",
            "scale-multifidelity-plan.svg",
            "hpc-failure-recovery.svg",
        ),
    ),
)

DESIGN_SYSTEM = """# Scientific Swiss Bento V12 visual system

This design system applies the current UI/UX Pro Max priority model to GitHub README illustrations for TsaoSciComputation.

## Product and audience

- Product type: scientific developer tool and evidence-bound orchestration platform.
- Audience: researchers, simulation engineers, software reviewers and technical decision makers.
- Primary context: GitHub README at desktop, tablet and narrow browser widths.
- Primary task: understand scope, execution order, evidence strength and failure boundaries without zooming the page.

## Design dials

- Variance: 6/10 — five governed information layouts remain visually related.
- Motion: 0/10 — static repository SVGs make no interaction claim.
- Density: 5/10 — reduced from V11 so diagrams remain legible after GitHub scaling.

## Responsive presentation tiers

| Tier | README treatment | Visual purpose |
|---|---|---|
| Hero | Full width above the project title | Product scope and primary evidence narrative |
| Overview | At most two compact Bento diagrams in one row | Architecture and capability orientation |
| Detail | Full-width diagrams inside semantic `<details>` groups | Workflows, loops, risk and scientific evidence |

Detailed Workflow, Loop and Risk diagrams must never be placed in a 50% README column. Progressive disclosure keeps the first screen concise without removing any capability documentation.

## Layout families

| Layout | Purpose |
|---|---|
| Hero | Establish product scope and the principal evidence narrative |
| Bento | Compare architecture, registries and governance responsibilities |
| Workflow | Explain ordered computation and cross-scale handoffs |
| Loop | Show iterative learning, updating and evidence feedback |
| Risk | Separate initiating conditions, barriers, consequences and authority |

## Typography and spacing

- Minimum SVG text size: 16 px.
- Stage labels: 20–22 px; headings: 34–46 px.
- Detail copy is limited to two concise lines per stage.
- Structural spacing follows an 8 px rhythm.
- Full-width diagrams use a wide, shallow canvas to preserve readable type at GitHub scale.

## Tokens

| Role | Token |
|---|---|
| Canvas | `#0B1220` |
| Surface | `#111827` |
| Raised surface | `#172033` |
| Border | `#334155` |
| Primary text | `#F8FAFC` |
| Secondary text | `#CBD5E1` |
| Muted text | `#94A3B8` |
| Blue | `#3B82F6` |
| Cyan | `#06B6D4` |
| Teal | `#14B8A6` |
| Green | `#22C55E` |
| Amber | `#F59E0B` |
| Orange | `#F97316` |
| Risk red | `#EF4444` |

## Accessibility and trust rules

- Information is never encoded by color alone.
- Every illustration has a unique accessible `<title>` and `<desc>`.
- Every SVG declares its design system, scientific family and information layout.
- No external fonts, scripts, raster images, network resources, event handlers or tracking.
- Diagrams explain architecture and scientific boundaries; they are not solver screenshots, benchmark plots or live-execution evidence.

## Anti-patterns

- Detailed diagrams placed in narrow two-column README cells.
- Body labels below 16 px or more than two dense detail lines per stage.
- Forty-two illustrations expanded at once with no progressive disclosure.
- Purple/pink AI gradients, neon glow, glass decoration or simulated dashboards.
- Fabricated curves, numerical values or external-engine screenshots.
"""

README_EN_SYSTEM = """<!-- V12_VISUAL_SYSTEM:START -->
## Visual design system

The 42 repository-local SVGs use **Scientific Swiss Bento V12**, derived from the UI/UX Pro Max priority model. V12 optimizes for actual GitHub rendering rather than source-canvas appearance alone:

- the hero and detailed scientific workflows are full width;
- only two compact architecture overviews share a row;
- the full atlas is organized through semantic, accessible `<details>` groups;
- diagram body text is at least 16 px and stage copy is limited to two concise lines.

See [`assets/visuals/DESIGN_SYSTEM.md`](assets/visuals/DESIGN_SYSTEM.md).
<!-- V12_VISUAL_SYSTEM:END -->"""

README_ZH_SYSTEM = """<!-- V12_VISUAL_SYSTEM:START -->
## 配图设计系统

仓库内 42 幅 SVG 已采用源自 UI/UX Pro Max 优先级模型的 **Scientific Swiss Bento V12**。V12 不只关注源画布效果，而是针对 GitHub 实际缩放后的阅读体验进行优化：

- Hero 与详细科研工作流全部采用全宽展示；
- 只有两幅紧凑架构总览图共享一行；
- 完整图谱按语义明确、可访问的 `<details>` 分组渐进展开；
- 图内正文字号不低于 16 px，每个阶段说明最多两行。

详见 [`assets/visuals/DESIGN_SYSTEM.md`](assets/visuals/DESIGN_SYSTEM.md)。
<!-- V12_VISUAL_SYSTEM:END -->"""

INVENTORY_POLICY = """## UI/UX Pro Max design system

All 42 assets use **Scientific Swiss Bento V12** and declare `data-design-system="uiux-pro-max-scientific-swiss-v3"`.

- Five information layouts remain: Hero, Bento, Workflow, Loop and Risk.
- SVG body text is at least 16 px and stage details are capped at two concise lines.
- The bilingual README presents detailed diagrams full width under progressive-disclosure groups.
- Only two compact Bento overview diagrams share a row.
- No external fonts, scripts, raster images, gradients, filters, network resources, event handlers or tracking.
- Diagrams are explanatory evidence maps, not solver screenshots or live-execution claims.

See [`DESIGN_SYSTEM.md`](DESIGN_SYSTEM.md) for the complete V12 specification.

"""


def text_lines(
    x: float,
    y: float,
    value: str,
    css_class: str,
    limit: int,
    *,
    step: int = 22,
    anchor: str = "start",
    maximum: int = 2,
) -> str:
    wrapped = wrap_words(value, limit)[:maximum]
    tspans = "".join(
        f'<tspan x="{x:.1f}" dy="{0 if index == 0 else step}">{html.escape(line)}</tspan>'
        for index, line in enumerate(wrapped)
    )
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" '
        f'class="{css_class}">{tspans}</text>'
    )


def short_detail(value: str) -> str:
    terms = [part.strip() for part in value.split("·") if part.strip()]
    return " · ".join(terms[:3])


def evidence_strip(accent: str, y: float, width: float = 1104.0) -> str:
    labels = ("NUMERICAL", "CONVERGENCE", "PHYSICAL", "UNCERTAINTY", "APPLICABILITY", "REVIEW")
    segment = width / len(labels)
    items: list[str] = []
    for index, label in enumerate(labels):
        x = 48.0 + index * segment
        items.append(
            f'<circle cx="{x + 12:.1f}" cy="{y:.1f}" r="9" fill="none" '
            f'stroke="{accent}" stroke-width="2"/>'
            f'<text x="{x + 30:.1f}" y="{y + 6:.1f}" class="gate">{label}</text>'
        )
    return "".join(items)


def frame(spec: VisualSpec, layout: str, body: str, *, height: int = 600) -> str:
    accent = TOKENS[spec.accent]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 {height}" role="img" aria-labelledby="title desc" data-design-system="{SYSTEM_ID}" data-layout="{layout}" data-family="{html.escape(spec.family)}">
  <title id="title">{html.escape(spec.title)}</title>
  <desc id="desc">{html.escape(spec.description)}</desc>
  <style>
    .eyebrow {{ fill: {accent}; font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, sans-serif; font-size: 16px; font-weight: 700; letter-spacing: 1.4px; }}
    .heading {{ fill: {TOKENS['text']}; font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, sans-serif; font-size: 38px; font-weight: 700; }}
    .subtitle {{ fill: {TOKENS['secondary']}; font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, sans-serif; font-size: 18px; font-weight: 400; }}
    .card {{ fill: {TOKENS['surface']}; stroke: {TOKENS['border']}; stroke-width: 2; }}
    .raised {{ fill: {TOKENS['raised']}; stroke: {TOKENS['border']}; stroke-width: 2; }}
    .index {{ fill: {TOKENS['text']}; font-family: ui-monospace, SFMono-Regular, Consolas, monospace; font-size: 16px; font-weight: 700; }}
    .stage {{ fill: {TOKENS['text']}; font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, sans-serif; font-size: 21px; font-weight: 650; }}
    .detail {{ fill: {TOKENS['secondary']}; font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, sans-serif; font-size: 16px; font-weight: 400; }}
    .mono {{ fill: {TOKENS['secondary']}; font-family: ui-monospace, SFMono-Regular, Consolas, monospace; font-size: 16px; font-weight: 650; }}
    .gate {{ fill: {TOKENS['secondary']}; font-family: ui-monospace, SFMono-Regular, Consolas, monospace; font-size: 16px; font-weight: 650; }}
    .footer {{ fill: {TOKENS['muted']}; font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, sans-serif; font-size: 16px; font-weight: 400; }}
    .line {{ fill: none; stroke: {TOKENS['muted']}; stroke-width: 2.5; stroke-linecap: round; stroke-linejoin: round; }}
  </style>
  <rect width="1200" height="{height}" rx="24" fill="{TOKENS['canvas']}"/>
  <rect x="24" y="24" width="1152" height="{height - 48}" rx="20" fill="none" stroke="{TOKENS['border']}" stroke-width="2"/>
  <text x="56" y="58" class="eyebrow">{html.escape(spec.family.upper())} · {layout.upper()}</text>
  <text x="56" y="108" class="heading">{html.escape(spec.heading)}</text>
  {text_lines(56, 142, spec.subtitle, 'subtitle', 88, maximum=1)}
  <rect x="970" y="42" width="174" height="34" rx="17" fill="{TOKENS['raised']}" stroke="{TOKENS['border']}"/>
  <text x="1057" y="65" text-anchor="middle" class="mono">EVIDENCE-BOUND</text>
  {body}
  {evidence_strip(accent, height - 78)}
  {text_lines(56, height - 30, spec.footer, 'footer', 120, maximum=1)}
</svg>
'''


def render_hero(spec: VisualSpec) -> str:
    accent = TOKENS[spec.accent]
    cards: list[str] = []
    for index, (label, detail) in enumerate(spec.stages):
        x = 48 + index * 224
        cards.append(
            f'<rect x="{x}" y="190" width="208" height="240" rx="18" class="card"/>'
            f'<rect x="{x}" y="190" width="208" height="5" rx="2" fill="{accent}"/>'
            f'<text x="{x + 20}" y="232" class="index">{index + 1:02d}</text>'
            + text_lines(x + 20, 278, label, "stage", 16)
            + text_lines(x + 20, 326, short_detail(detail), "detail", 22)
            + stage_glyph(index, x + 104, 390, accent)
        )
    return frame(spec, "hero", "".join(cards), height=620)


def render_bento(spec: VisualSpec) -> str:
    accent = TOKENS[spec.accent]
    positions = ((48, 178, 426, 132), (490, 178, 662, 132), (48, 326, 340, 126), (404, 326, 340, 126), (760, 326, 392, 126))
    cards: list[str] = []
    for index, ((label, detail), (x, y, width, height)) in enumerate(zip(spec.stages, positions, strict=True)):
        cards.append(
            f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="18" class="card"/>'
            f'<rect x="{x}" y="{y}" width="5" height="{height}" rx="2" fill="{accent}"/>'
            f'<text x="{x + 22}" y="{y + 38}" class="index">{index + 1:02d}</text>'
            + text_lines(x + 72, y + 38, label, "stage", 28, maximum=1)
            + text_lines(x + 22, y + 82, short_detail(detail), "detail", 44, maximum=1)
        )
    cards.append(
        f'<rect x="48" y="470" width="1104" height="42" rx="14" fill="{TOKENS["raised"]}" stroke="{TOKENS["border"]}"/>'
        '<text x="72" y="497" class="mono">DECISION GATE · declare → verify → review</text>'
    )
    return frame(spec, "bento", "".join(cards), height=620)


def render_workflow(spec: VisualSpec) -> str:
    accent = TOKENS[spec.accent]
    cards: list[str] = []
    for index, (label, detail) in enumerate(spec.stages):
        x = 48 + index * 224
        cards.append(
            f'<rect x="{x}" y="190" width="208" height="228" rx="18" class="card"/>'
            f'<circle cx="{x + 28}" cy="222" r="17" fill="{TOKENS["raised"]}" stroke="{accent}" stroke-width="2"/>'
            f'<text x="{x + 28}" y="228" text-anchor="middle" class="index">{index + 1}</text>'
            + text_lines(x + 20, 274, label, "stage", 17)
            + text_lines(x + 20, 322, short_detail(detail), "detail", 22)
            + stage_glyph(index, x + 104, 386, accent)
        )
        if index < 4:
            cards.append(
                f'<path d="M{x + 208} 304H{x + 220}" class="line"/>'
                f'<path d="M{x + 214} 296L{x + 222} 304L{x + 214} 312" class="line"/>'
            )
    return frame(spec, "workflow", "".join(cards), height=600)


def render_loop(spec: VisualSpec) -> str:
    accent = TOKENS[spec.accent]
    positions = ((600, 196), (850, 290), (760, 444), (440, 444), (350, 290))
    nodes: list[str] = [
        f'<circle cx="600" cy="332" r="126" fill="none" stroke="{TOKENS["border"]}" stroke-width="2"/>'
    ]
    for index, ((label, detail), (x, y)) in enumerate(zip(spec.stages, positions, strict=True)):
        nodes.append(
            f'<rect x="{x - 112}" y="{y - 48}" width="224" height="96" rx="18" class="card"/>'
            f'<circle cx="{x - 84}" cy="{y - 18}" r="15" fill="{TOKENS["raised"]}" stroke="{accent}" stroke-width="2"/>'
            f'<text x="{x - 84}" y="{y - 12}" text-anchor="middle" class="index">{index + 1}</text>'
            + text_lines(x - 58, y - 14, label, "stage", 18, maximum=1)
            + text_lines(x, y + 22, short_detail(detail), "detail", 26, anchor="middle", maximum=1)
        )
    nodes.append(
        f'<circle cx="600" cy="332" r="68" fill="{TOKENS["raised"]}" stroke="{accent}" stroke-width="3"/>'
        '<text x="600" y="326" text-anchor="middle" class="mono">FEEDBACK LOOP</text>'
        '<text x="600" y="350" text-anchor="middle" class="detail">measure · update · revalidate</text>'
    )
    return frame(spec, "loop", "".join(nodes), height=650)


def render_risk(spec: VisualSpec) -> str:
    accent = TOKENS[spec.accent]
    top = spec.stages[:3]
    bottom = spec.stages[3:]
    body: list[str] = []
    for index, (label, detail) in enumerate(top):
        x = 48 + index * 368
        body.append(
            f'<rect x="{x}" y="190" width="344" height="156" rx="18" class="card"/>'
            f'<rect x="{x}" y="190" width="344" height="5" rx="2" fill="{accent}"/>'
            f'<text x="{x + 22}" y="230" class="index">0{index + 1}</text>'
            + text_lines(x + 22, 270, label, "stage", 26, maximum=1)
            + text_lines(x + 22, 310, short_detail(detail), "detail", 38, maximum=1)
        )
    for index, (label, detail) in enumerate(bottom):
        x = 48 + index * 552
        body.append(
            f'<rect x="{x}" y="366" width="528" height="86" rx="18" class="raised"/>'
            f'<text x="{x + 22}" y="402" class="index">0{index + 4}</text>'
            + text_lines(x + 76, 402, label, "stage", 24, maximum=1)
            + text_lines(x + 22, 434, short_detail(detail), "detail", 58, maximum=1)
        )
    body.append(
        f'<rect x="278" y="474" width="644" height="42" rx="14" fill="{TOKENS["raised"]}" stroke="{accent}" stroke-width="2"/>'
        '<text x="600" y="501" text-anchor="middle" class="mono">BARRIER · LIMIT · ESCALATE</text>'
    )
    return frame(spec, "risk", "".join(body), height=620)


def render_svg(spec: VisualSpec) -> str:
    layout = layout_for(spec)
    renderers = {
        "hero": render_hero,
        "bento": render_bento,
        "workflow": render_workflow,
        "loop": render_loop,
        "risk": render_risk,
    }
    return renderers[layout](spec)


def image(spec: VisualSpec) -> str:
    return (
        f'<img src="assets/visuals/{spec.filename}" alt="{html.escape(spec.title)}" '
        'width="100%">'
    )


def detail_group(
    title: str,
    description: str,
    filenames: Iterable[str],
    specs: dict[str, VisualSpec],
    *,
    opened: bool = False,
) -> str:
    open_attr = " open" if opened else ""
    images = "\n\n".join(image(specs[name]) for name in filenames)
    return (
        f'<details{open_attr}>\n<summary><strong>{title}</strong> — {description}</summary>\n\n'
        f'{images}\n\n</details>'
    )


def build_atlas(specs: tuple[VisualSpec, ...], *, chinese: bool) -> str:
    by_name = {spec.filename: spec for spec in specs}
    agent = by_name["agent-orchestration.svg"]
    capability = by_name["capability-landscape.svg"]
    if chinese:
        heading = "## 科研能力图谱"
        intro = (
            "首屏只展示两幅紧凑架构总览图；详细工作流、闭环和风险图采用全宽显示，"
            "并按领域折叠，减少滚动负担，同时保留全部 42 幅图的可发现性。"
        )
        labels = {
            "agent": "受治理科研智能体",
            "capability": "合同化能力体系",
            "electronic": ("电子结构、分子模拟与反应", "量子、采样、动力学、光谱及跨尺度参数化"),
            "materials": ("材料、界面与制造", "形貌、输运、聚合、复合材料及加工窗口"),
            "process": ("连续介质、流程与运行", "CFD、FEM、流程、反应器、控制与数字孪生"),
            "governance": ("证据、治理与计算基础设施", "不确定度、适配器、HPC、可信等级与可重复性"),
        }
        fail_closed = (
            "核心设计采用缺项拒绝推进：声明能力不等于环境可用，进程完成不等于收敛，"
            "数值收敛不等于物理有效，验证通过也不等于获得高风险工程授权。"
        )
        final_note = (
            "仓库包含 27 个保守适配器定义；外部求解器仍须独立安装、授权和验证。"
            "每次受治理交接均可保留单位、版本、种子、容差、原始产物、解析结果、哈希和发布证据。"
        )
    else:
        heading = "## Scientific capability atlas"
        intro = (
            "Only two compact architecture overviews remain inline. Detailed workflows, loops and risk maps "
            "are full width and grouped by domain to reduce scrolling while keeping all 42 assets discoverable."
        )
        labels = {
            "agent": "Governed scientific agent",
            "capability": "Contract-based capability system",
            "electronic": ("Electronic structure, molecular simulation and reactions", "quantum, sampling, kinetics, spectroscopy and cross-scale parameterization"),
            "materials": ("Materials, interfaces and manufacturing", "morphology, transport, polymerization, composites and processing windows"),
            "process": ("Continuum, process and operations", "CFD, FEM, flowsheets, reactors, control and digital twins"),
            "governance": ("Evidence, governance and computing infrastructure", "uncertainty, adapters, HPC, confidence and reproducibility"),
        }
        fail_closed = (
            "The core design is fail-closed: declared capability is not environment availability; process completion "
            "is not convergence; numerical convergence is not physical validity; validation is not high-risk authority."
        )
        final_note = (
            "The repository contains 27 conservative adapter definitions; external solvers remain separately installed, "
            "licensed and validated. Governed handoffs can retain units, versions, seeds, tolerances, raw artifacts, "
            "parsed results, hashes and release evidence."
        )

    overview = f'''{heading}

{intro}

<table>
<tr>
<td width="50%">{image(agent)}</td>
<td width="50%">{image(capability)}</td>
</tr>
<tr>
<td align="center"><strong>{labels['agent']}</strong></td>
<td align="center"><strong>{labels['capability']}</strong></td>
</tr>
</table>

{fail_closed}
'''
    groups = []
    for index, (key, filenames) in enumerate(GROUPS):
        title, description = labels[key]
        groups.append(
            detail_group(title, description, filenames, by_name, opened=index == 0)
        )
    return overview + "\n\n" + "\n\n".join(groups) + "\n\n" + final_note


def update_system(text: str, block: str) -> str:
    if not SYSTEM_MARKER.search(text):
        raise ValueError("README visual-system marker not found")
    return SYSTEM_MARKER.sub(block, text, count=1)


def update_inventory(text: str) -> str:
    pattern = re.compile(r"## UI/UX Pro Max design system\n.*?(?=\n## Asset set)", re.DOTALL)
    if not pattern.search(text):
        raise ValueError("visual inventory policy block not found")
    return pattern.sub(INVENTORY_POLICY.rstrip() + "\n", text, count=1)


def update_changelog(text: str) -> str:
    bullet = (
        "- Regenerated all 42 README visuals for GitHub-scale readability with 16 px minimum "
        "diagram text, full-width detailed workflows and progressive-disclosure domain groups."
    )
    if bullet in text:
        return text
    return text.replace("## Unreleased\n", f"## Unreleased\n\n{bullet}\n", 1)


def write(path: Path, content: str, *, check: bool) -> None:
    normalized = content.rstrip() + "\n"
    current = path.read_text(encoding="utf-8") if path.exists() else ""
    if check:
        if current != normalized:
            raise SystemExit(f"generated V12 visual artifact is stale: {path.relative_to(ROOT)}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(normalized, encoding="utf-8", newline="\n")


def synchronize(*, check: bool) -> None:
    specs = parse_specs()
    if len(specs) != 42:
        raise ValueError(f"expected 42 visual specifications, found {len(specs)}")
    for spec in specs:
        write(VISUAL_ROOT / spec.filename, render_svg(spec), check=check)

    readme_path = ROOT / "README.md"
    readme_zh_path = ROOT / "README.zh-CN.md"
    readme = update_system(readme_path.read_text(encoding="utf-8"), README_EN_SYSTEM)
    readme = ENGLISH_ATLAS.sub(build_atlas(specs, chinese=False), readme, count=1)
    readme_zh = update_system(readme_zh_path.read_text(encoding="utf-8"), README_ZH_SYSTEM)
    readme_zh = CHINESE_ATLAS.sub(build_atlas(specs, chinese=True), readme_zh, count=1)

    write(readme_path, readme, check=check)
    write(readme_zh_path, readme_zh, check=check)
    write(VISUAL_ROOT / "DESIGN_SYSTEM.md", DESIGN_SYSTEM, check=check)
    inventory_path = VISUAL_ROOT / "README.md"
    write(
        inventory_path,
        update_inventory(inventory_path.read_text(encoding="utf-8")),
        check=check,
    )
    changelog_path = ROOT / "CHANGELOG.md"
    write(
        changelog_path,
        update_changelog(changelog_path.read_text(encoding="utf-8")),
        check=check,
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Regenerate the README atlas for GitHub-scale readability and progressive disclosure."
    )
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    synchronize(check=args.check)
    print("PASS: 42 UI/UX Pro Max V12 README visuals are readable and synchronized.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
