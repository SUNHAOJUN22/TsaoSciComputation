from __future__ import annotations

import argparse
import html
import re
import sys
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

SYSTEM_ID = "uiux-pro-max-scientific-swiss-v2"
LAYOUTS = ("hero", "bento", "workflow", "loop", "risk")
VISUAL_MARKER = re.compile(
    r"<!-- V1[01]_VISUAL_SYSTEM:START -->.*?<!-- V1[01]_VISUAL_SYSTEM:END -->",
    re.DOTALL,
)

LOOP_FILES = {
    "ml-potential-active-learning.svg",
    "inverse-design-loop.svg",
    "evidence-loop.svg",
    "digital-twin-drift.svg",
    "dynamic-control-estimation.svg",
}
RISK_FILES = {
    "transport-degradation.svg",
    "reactor-safety-control.svg",
    "hpc-execution-provenance.svg",
    "reactor-scaleup-thermal-risk.svg",
    "hpc-failure-recovery.svg",
    "cfd-turbulence-multiphase.svg",
}
BENTO_FILES = {
    "agent-orchestration.svg",
    "capability-landscape.svg",
    "engine-ecosystem.svg",
    "confidence-ladder.svg",
    "digital-thread.svg",
    "data-model-governance.svg",
    "scale-multifidelity-plan.svg",
}

README_EN_BLOCK = """<!-- V11_VISUAL_SYSTEM:START -->
## Visual design system

The 42 repository-local SVGs use **Scientific Swiss Bento V11**, derived from the UI/UX Pro Max priority model. The atlas now uses five information-specific layouts instead of repeating one card template:

| Layout | Communicates |
|---|---|
| Hero | Product scope and the primary evidence narrative |
| Bento | Architecture, registries and governance responsibilities |
| Workflow | Ordered calculations and cross-scale handoffs |
| Loop | Iterative learning, updating and evidence feedback |
| Risk | Initiating conditions, barriers, consequences and review authority |

All layouts retain high contrast, system fonts, semantic colors, explicit labels and a shared evidence vocabulary. See [`assets/visuals/DESIGN_SYSTEM.md`](assets/visuals/DESIGN_SYSTEM.md).
<!-- V11_VISUAL_SYSTEM:END -->"""

README_ZH_BLOCK = """<!-- V11_VISUAL_SYSTEM:START -->
## 配图设计系统

仓库内 42 幅 SVG 已采用源自 UI/UX Pro Max 优先级规则的 **Scientific Swiss Bento V11**。图谱不再重复同一种卡片模板，而是按信息模型使用五类版式：

| 版式 | 表达内容 |
|---|---|
| Hero | 产品范围与核心证据主线 |
| Bento | 架构、注册表及治理责任 |
| Workflow | 有序计算与跨尺度交接 |
| Loop | 迭代学习、在线更新及证据反馈 |
| Risk | 起始条件、防护屏障、后果及复核权限 |

所有版式继续采用高对比、系统字体、语义色、明确文字标签和统一证据词汇。详见 [`assets/visuals/DESIGN_SYSTEM.md`](assets/visuals/DESIGN_SYSTEM.md)。
<!-- V11_VISUAL_SYSTEM:END -->"""

INVENTORY_BLOCK = """## UI/UX Pro Max design system

All assets follow [`DESIGN_SYSTEM.md`](DESIGN_SYSTEM.md), the **Scientific Swiss Bento V11** system derived from UI/UX Pro Max.

- The atlas uses five governed layouts: Hero, Bento, Workflow, Loop and Risk.
- Layout selection follows the information model rather than decoration.
- Shared tokens, typography, evidence labels and scientific trust boundaries remain consistent.
- Every SVG is self-contained and includes unique accessible title and description metadata.
- Purple/pink AI gradients, glow filters, raster screenshots, external fonts and fabricated plots are prohibited.

"""


def layout_for(spec: VisualSpec) -> str:
    if spec.filename == "hero-multiscale.svg":
        return "hero"
    if spec.filename in LOOP_FILES:
        return "loop"
    if spec.filename in RISK_FILES or spec.family == "operations":
        return "risk"
    if spec.filename in BENTO_FILES or spec.family in {"architecture", "governance"}:
        return "bento"
    return "workflow"


def lines(
    x: float,
    y: float,
    value: str,
    css_class: str,
    limit: int,
    *,
    anchor: str = "start",
    step: int = 21,
    maximum: int = 3,
) -> str:
    wrapped = wrap_words(value.replace(" · ", " "), limit)[:maximum]
    tspans = "".join(
        f'<tspan x="{x:.1f}" dy="{0 if index == 0 else step}">{html.escape(line)}</tspan>'
        for index, line in enumerate(wrapped)
    )
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" class="{css_class}">{tspans}</text>'
    )


def frame(spec: VisualSpec, layout: str, body: str, footer_y: int = 620) -> str:
    accent = TOKENS[spec.accent]
    title = html.escape(spec.title)
    description = html.escape(spec.description)
    family = html.escape(spec.family)
    footer = lines(56, footer_y, spec.footer, "footer", 130, maximum=2)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 680" role="img" aria-labelledby="title desc" data-design-system="{SYSTEM_ID}" data-family="{family}" data-layout="{layout}">
  <title id="title">{title}</title>
  <desc id="desc">{description}</desc>
  <defs><pattern id="grid" width="32" height="32" patternUnits="userSpaceOnUse"><path d="M32 0H0V32" fill="none" stroke="#334155" stroke-width="1" opacity="0.18"/></pattern></defs>
  <style>
    .eyebrow {{ fill: {accent}; font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, sans-serif; font-size: 13px; font-weight: 700; letter-spacing: 1.6px; }}
    .heading {{ fill: #F8FAFC; font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, sans-serif; font-size: 32px; font-weight: 700; }}
    .subtitle {{ fill: #CBD5E1; font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, sans-serif; font-size: 15px; font-weight: 400; }}
    .stage {{ fill: #F8FAFC; font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, sans-serif; font-size: 18px; font-weight: 650; }}
    .detail {{ fill: #CBD5E1; font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, sans-serif; font-size: 13px; font-weight: 400; }}
    .mono {{ fill: #F8FAFC; font-family: ui-monospace, SFMono-Regular, Consolas, monospace; font-size: 13px; font-weight: 700; }}
    .gate {{ fill: #CBD5E1; font-family: ui-monospace, SFMono-Regular, Consolas, monospace; font-size: 13px; font-weight: 650; letter-spacing: 0.5px; }}
    .footer {{ fill: #94A3B8; font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, sans-serif; font-size: 14px; font-weight: 400; }}
    .card {{ fill: #111827; stroke: #334155; stroke-width: 2; }}
    .raised {{ fill: #172033; stroke: #334155; stroke-width: 2; }}
    .link {{ fill: none; stroke: #94A3B8; stroke-width: 2; stroke-linecap: round; stroke-linejoin: round; }}
  </style>
  <rect width="1200" height="680" rx="24" fill="#0B1220"/>
  <rect width="1200" height="680" rx="24" fill="url(#grid)"/>
  <rect x="32" y="28" width="1136" height="624" rx="20" fill="none" stroke="#334155" stroke-width="2"/>
  <text x="56" y="62" class="eyebrow">{family.upper()} · {layout.upper()}</text>
  <text x="56" y="108" class="heading">{html.escape(spec.heading)}</text>
  {lines(56, 140, spec.subtitle, "subtitle", 88, maximum=2)}
  <rect x="950" y="48" width="194" height="32" rx="16" fill="#172033" stroke="#334155"/>
  <text x="1047" y="69" text-anchor="middle" class="mono">EVIDENCE-BOUND</text>
  {body}
  {evidence_strip(accent)}
  {footer}
</svg>
'''


def evidence_strip(accent: str) -> str:
    labels = ("NUMERICAL", "CONVERGENCE", "PHYSICAL", "UNCERTAINTY", "APPLICABILITY", "REVIEW")
    items: list[str] = []
    for index, label in enumerate(labels):
        x = 58 + index * 174
        items.append(
            f'<circle cx="{x}" cy="552" r="9" fill="#0B1220" stroke="{accent}" stroke-width="2"/>'
            f'<text x="{x + 16}" y="557" class="gate">{label}</text>'
        )
    return '<rect x="48" y="516" width="1104" height="72" rx="16" class="raised"/>' + "".join(items)


def render_hero(spec: VisualSpec) -> str:
    accent = TOKENS[spec.accent]
    cards: list[str] = []
    for index, (label, detail) in enumerate(spec.stages):
        x = 48 + index * 225
        cards.append(
            f'<rect x="{x}" y="192" width="204" height="282" rx="18" class="card"/>'
            f'<rect x="{x}" y="192" width="204" height="5" rx="2" fill="{accent}"/>'
            f'<text x="{x + 18}" y="232" class="mono">0{index + 1}</text>'
            + lines(x + 18, 274, label, "stage", 18)
            + lines(x + 18, 322, detail, "detail", 23, maximum=3)
            + stage_glyph(index, x + 102, 430, accent)
        )
        if index < 4:
            cards.append(f'<path d="M{x + 206} 335H{x + 221}" class="link"/>')
    return frame(spec, "hero", "".join(cards))


def render_workflow(spec: VisualSpec) -> str:
    accent = TOKENS[spec.accent]
    path = '<path d="M90 350H1110" class="link"/>'
    nodes: list[str] = [path]
    for index, (label, detail) in enumerate(spec.stages):
        x = 112 + index * 218
        upper = index % 2 == 0
        y = 190 if upper else 354
        connector_y = y + (142 if upper else 0)
        nodes.append(
            f'<path d="M{x} 350V{connector_y}" class="link"/>'
            f'<circle cx="{x}" cy="350" r="11" fill="#0B1220" stroke="{accent}" stroke-width="3"/>'
            f'<rect x="{x - 92}" y="{y}" width="184" height="142" rx="16" class="card"/>'
            f'<rect x="{x - 92}" y="{y}" width="6" height="142" rx="3" fill="{accent}"/>'
            f'<text x="{x - 72}" y="{y + 30}" class="mono">0{index + 1}</text>'
            + lines(x - 72, y + 62, label, "stage", 17, maximum=2)
            + lines(x - 72, y + 98, detail, "detail", 20, maximum=2)
        )
    return frame(spec, "workflow", "".join(nodes))


def render_bento(spec: VisualSpec) -> str:
    accent = TOKENS[spec.accent]
    positions = ((48, 190), (382, 190), (48, 340), (382, 340))
    cards: list[str] = []
    for index, ((label, detail), (x, y)) in enumerate(zip(spec.stages[:4], positions, strict=True)):
        cards.append(
            f'<rect x="{x}" y="{y}" width="310" height="126" rx="16" class="card"/>'
            f'<rect x="{x}" y="{y}" width="6" height="126" rx="3" fill="{accent}"/>'
            f'<text x="{x + 22}" y="{y + 31}" class="mono">0{index + 1}</text>'
            + lines(x + 70, y + 32, label, "stage", 24, maximum=1)
            + lines(x + 22, y + 76, detail, "detail", 34, maximum=2)
        )
    label, detail = spec.stages[4]
    cards.append(
        '<rect x="716" y="190" width="436" height="276" rx="18" class="raised"/>'
        f'<rect x="716" y="190" width="436" height="6" rx="3" fill="{accent}"/>'
        '<text x="746" y="232" class="mono">05 · DECISION GATE</text>'
        + lines(746, 278, label, "stage", 32, maximum=2)
        + lines(746, 326, detail, "detail", 42, maximum=3)
        + f'<circle cx="1032" cy="366" r="54" fill="#0B1220" stroke="{accent}" stroke-width="3"/>'
        + f'<path d="M1008 366L1024 382L1057 345" fill="none" stroke="{accent}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>'
        + '<text x="934" y="442" text-anchor="middle" class="mono">TRACE · VERIFY · AUTHORIZE</text>'
    )
    return frame(spec, "bento", "".join(cards))


def render_loop(spec: VisualSpec) -> str:
    accent = TOKENS[spec.accent]
    positions = ((600, 202), (870, 310), (766, 454), (434, 454), (330, 310))
    nodes: list[str] = [
        '<circle cx="600" cy="344" r="92" class="raised"/>',
        f'<circle cx="600" cy="344" r="72" fill="#0B1220" stroke="{accent}" stroke-width="3"/>',
        '<text x="600" y="338" text-anchor="middle" class="mono">EVIDENCE</text>',
        '<text x="600" y="362" text-anchor="middle" class="mono">FEEDBACK LOOP</text>',
    ]
    path_points = " ".join(f"{x},{y}" for x, y in positions)
    nodes.append(
        f'<polygon points="{path_points}" fill="none" stroke="#94A3B8" stroke-width="2" stroke-linejoin="round"/>'
    )
    for index, ((label, detail), (x, y)) in enumerate(zip(spec.stages, positions, strict=True)):
        nodes.append(
            f'<circle cx="{x}" cy="{y}" r="76" class="card"/>'
            f'<circle cx="{x}" cy="{y - 38}" r="15" fill="#0B1220" stroke="{accent}" stroke-width="2"/>'
            f'<text x="{x}" y="{y - 33}" text-anchor="middle" class="mono">0{index + 1}</text>'
            + lines(x, y + 2, label, "stage", 16, anchor="middle", maximum=2)
            + lines(x, y + 38, detail, "detail", 18, anchor="middle", maximum=2)
        )
    return frame(spec, "loop", "".join(nodes), footer_y=624)


def render_risk(spec: VisualSpec) -> str:
    accent = TOKENS[spec.accent]
    left = spec.stages[:2]
    right = spec.stages[2:4]
    authority = spec.stages[4]
    body: list[str] = [
        '<path d="M80 330H1120" class="link"/>',
        '<path d="M510 250L600 330L510 410" fill="#172033" stroke="#334155" stroke-width="2"/>',
        '<path d="M690 250L600 330L690 410" fill="#172033" stroke="#334155" stroke-width="2"/>',
        f'<circle cx="600" cy="330" r="58" fill="#0B1220" stroke="{accent}" stroke-width="3"/>',
        f'<path d="M600 288L632 302V329C632 352 618 369 600 379C582 369 568 352 568 329V302Z" fill="none" stroke="{accent}" stroke-width="3"/>',
        '<text x="600" y="438" text-anchor="middle" class="mono">BARRIER · LIMIT · ESCALATE</text>',
    ]
    for index, (label, detail) in enumerate(left):
        x = 48 + index * 222
        body.append(
            f'<rect x="{x}" y="224" width="190" height="164" rx="16" class="card"/>'
            f'<rect x="{x}" y="224" width="6" height="164" rx="3" fill="{accent}"/>'
            f'<text x="{x + 22}" y="254" class="mono">INIT 0{index + 1}</text>'
            + lines(x + 22, 290, label, "stage", 18, maximum=2)
            + lines(x + 22, 334, detail, "detail", 21, maximum=2)
        )
    for index, (label, detail) in enumerate(right):
        x = 770 + index * 222
        body.append(
            f'<rect x="{x}" y="224" width="190" height="164" rx="16" class="card"/>'
            f'<rect x="{x + 184}" y="224" width="6" height="164" rx="3" fill="{accent}"/>'
            f'<text x="{x + 22}" y="254" class="mono">OUTCOME 0{index + 3}</text>'
            + lines(x + 22, 290, label, "stage", 18, maximum=2)
            + lines(x + 22, 334, detail, "detail", 21, maximum=2)
        )
    label, detail = authority
    body.append(
        '<rect x="358" y="458" width="484" height="48" rx="14" class="raised"/>'
        f'<text x="382" y="488" class="mono">05 · {html.escape(label.upper())}</text>'
        + lines(818, 487, detail, "detail", 45, anchor="end", maximum=1)
    )
    return frame(spec, "risk", "".join(body), footer_y=624)


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


def update_marker(text: str, block: str) -> str:
    if VISUAL_MARKER.search(text):
        return VISUAL_MARKER.sub(block, text, count=1)
    anchor = "</div>\n"
    if anchor not in text:
        raise ValueError("README center block closing tag not found")
    return text.replace(anchor, anchor + "\n" + block + "\n", 1)


def update_inventory(text: str) -> str:
    pattern = re.compile(r"## UI/UX Pro Max design system\n.*?(?=\n## Asset set)", re.DOTALL)
    if not pattern.search(text):
        return text.replace("## Asset set", INVENTORY_BLOCK + "## Asset set", 1)
    return pattern.sub(INVENTORY_BLOCK.rstrip() + "\n", text, count=1)


def update_changelog(text: str) -> str:
    bullet = (
        "- Diversified all 42 UI/UX Pro Max README illustrations into Hero, Bento, "
        "Workflow, Loop and Risk layouts while preserving filenames, accessibility and "
        "scientific evidence boundaries."
    )
    if bullet in text:
        return text
    return text.replace("## Unreleased\n", f"## Unreleased\n\n{bullet}\n", 1)


def write(path: Path, content: str, *, check: bool) -> None:
    normalized = content.rstrip() + "\n"
    current = path.read_text(encoding="utf-8") if path.exists() else ""
    if check:
        if current != normalized:
            raise SystemExit(f"generated V11 visual artifact is stale: {path.relative_to(ROOT)}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(normalized, encoding="utf-8", newline="\n")


def synchronize(*, check: bool) -> None:
    specs = parse_specs()
    for spec in specs:
        write(VISUAL_ROOT / spec.filename, render_svg(spec), check=check)

    readme = ROOT / "README.md"
    readme_zh = ROOT / "README.zh-CN.md"
    inventory = VISUAL_ROOT / "README.md"
    changelog = ROOT / "CHANGELOG.md"
    write(
        readme,
        update_marker(readme.read_text(encoding="utf-8"), README_EN_BLOCK),
        check=check,
    )
    write(
        readme_zh,
        update_marker(readme_zh.read_text(encoding="utf-8"), README_ZH_BLOCK),
        check=check,
    )
    write(
        inventory,
        update_inventory(inventory.read_text(encoding="utf-8")),
        check=check,
    )
    write(
        changelog,
        update_changelog(changelog.read_text(encoding="utf-8")),
        check=check,
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Regenerate the complete README atlas with five UI/UX Pro Max V11 layouts."
    )
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    synchronize(check=args.check)
    print("PASS: 42 diversified UI/UX Pro Max V11 README visuals are synchronized.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
