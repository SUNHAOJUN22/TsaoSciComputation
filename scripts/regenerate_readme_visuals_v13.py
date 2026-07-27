from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts import regenerate_readme_visuals_v12 as base  # noqa: E402

SYSTEM_ID = "uiux-pro-max-scientific-console-v4"
ICON_SYSTEM = "uiux-pro-max-line-v1"
SYSTEM_MARKER = re.compile(
    r"<!-- V1[0-3]_VISUAL_SYSTEM:START -->.*?<!-- V1[0-3]_VISUAL_SYSTEM:END -->",
    re.DOTALL,
)
ENGLISH_ATLAS = re.compile(r"## Scientific capability atlas\n.*?(?=\n## Quick start)", re.DOTALL)
CHINESE_ATLAS = re.compile(r"## 科研能力图谱\n.*?(?=\n## 快速开始)", re.DOTALL)

COLOR_MAP = {
    "#0B1220": "#07111F",
    "#111827": "#0F1B2D",
    "#172033": "#162338",
    "#334155": "#334865",
    "#CBD5E1": "#D1D9E6",
    "#94A3B8": "#93A4BB",
    "#3B82F6": "#60A5FA",
    "#06B6D4": "#22D3EE",
    "#14B8A6": "#2DD4BF",
    "#22C55E": "#4ADE80",
    "#F59E0B": "#FBBF24",
    "#F97316": "#FB923C",
    "#EF4444": "#F87171",
}

DESIGN_SYSTEM = """# Scientific Research Console V13 visual system

This repository-local system applies the current
[UI/UX Pro Max](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill)
priority model together with the
[Chinese tutorial](https://github.com/bbylw/ui-ux-pro-max-skill-cn)
to TsaoSciComputation README illustrations.

## Product and audience

- Product type: scientific developer tool, workflow orchestrator and evidence-governance platform.
- Audience: researchers, simulation engineers, software reviewers and technical decision makers.
- Context: GitHub README at desktop, tablet and narrow browser widths.
- Primary task: understand scope, sequence, evidence strength and failure boundaries without zooming.

## Design dials

- Variance: 5/10 — five information layouts share one visual grammar.
- Motion: 0/10 — static SVGs make no interaction or live-execution claim.
- Density: 4/10 — generous spacing protects legibility after GitHub scaling.

## Priority decisions

1. Accessibility: high contrast, unique titles/descriptions and no color-only meaning.
2. Progressive disclosure: the README does not expand all 42 diagrams at once.
3. Performance: self-contained SVG, with no network resources, filters, raster images or external fonts.
4. Style: technical editorial + Swiss grid + restrained Bento hierarchy.
5. Responsive layout: hero and detailed diagrams are full width; only two overviews share a row.
6. Typography: minimum 16 px, concise two-line stage copy and system font stacks.
7. Icons: one consistent line-icon family; no emoji or decorative pseudo-data.

## Layout families

| Layout | Purpose |
|---|---|
| Hero | Establish product scope and cross-scale handoffs |
| Bento | Compare architecture, registries and decision responsibilities |
| Workflow | Explain ordered computation and evidence transfer |
| Loop | Show bounded iteration, updating and revalidation |
| Risk | Separate initiating conditions, barriers, consequences and authority |

## Tokens

| Role | Token |
|---|---|
| Canvas | `#07111F` |
| Surface | `#0F1B2D` |
| Raised surface | `#162338` |
| Border | `#334865` |
| Primary text | `#F8FAFC` |
| Secondary text | `#D1D9E6` |
| Muted text | `#93A4BB` |
| Blue | `#60A5FA` |
| Cyan | `#22D3EE` |
| Teal | `#2DD4BF` |
| Green | `#4ADE80` |
| Amber | `#FBBF24` |
| Orange | `#FB923C` |
| Risk red | `#F87171` |

## Accessibility and trust rules

- Meaning is encoded by labels, shapes and position as well as color.
- Every illustration has a unique accessible `<title>` and `<desc>`.
- Every SVG declares its design system, icon system, family and layout.
- SVGs contain no scripts, event handlers, external URLs, raster images, gradients or filters.
- Diagrams explain architecture and scientific boundaries; they are not solver screenshots,
  benchmark plots or evidence of live DFT, MD, CFD or HPC execution.

## Anti-patterns

- Purple/pink AI gradients, neon glow, glass decoration and simulated dashboards.
- Emoji as icons or mixed icon styles.
- Detailed workflows in narrow half-width README cells.
- Dense paragraphs inside diagrams or body labels below 16 px.
- Fabricated curves, numerical values, badges or external-engine screenshots.
"""

README_EN_SYSTEM = """<!-- V13_VISUAL_SYSTEM:START -->
## Visual design system

The 42 repository-local SVGs now use **Scientific Research Console V13**, generated from the
UI/UX Pro Max upstream priority model and its Chinese tutorial adaptation.

- accessibility and GitHub-scale readability come before decoration;
- all diagrams use one restrained technical-editorial palette and one line-icon grammar;
- meaning is reinforced by labels, shapes and position rather than color alone;
- detailed workflows remain full width inside semantic `<details>` groups;
- diagram text is at least 16 px, with no external fonts, scripts, raster images, gradients or filters.

See [`assets/visuals/DESIGN_SYSTEM.md`](assets/visuals/DESIGN_SYSTEM.md).
<!-- V13_VISUAL_SYSTEM:END -->"""

README_ZH_SYSTEM = """<!-- V13_VISUAL_SYSTEM:START -->
## 配图设计系统

仓库内 42 幅 SVG 已升级为 **Scientific Research Console V13**，设计依据同时来自
UI/UX Pro Max 上游优先级模型及其中文教程适配。

- 无障碍与 GitHub 缩放后的可读性优先于装饰效果；
- 全部图采用统一、克制的技术编辑色板和线性图标语法；
- 信息同时通过文字、形状和位置表达，不依赖颜色单独传意；
- 详细工作流继续在语义化 `<details>` 分组中全宽展示；
- 图内文字不低于 16 px，且不使用外部字体、脚本、位图、渐变或滤镜。

详见 [`assets/visuals/DESIGN_SYSTEM.md`](assets/visuals/DESIGN_SYSTEM.md)。
<!-- V13_VISUAL_SYSTEM:END -->"""

INVENTORY_POLICY = """## UI/UX Pro Max design system

All 42 assets use **Scientific Research Console V13** and declare
`data-design-system="uiux-pro-max-scientific-console-v4"`.

- The design follows the upstream UI/UX Pro Max priority model and its Chinese tutorial adaptation.
- Five information layouts remain: Hero, Bento, Workflow, Loop and Risk.
- One line-icon system and explicit labels reinforce meaning beyond color.
- SVG body text is at least 16 px and stage details are capped at two concise lines.
- The bilingual README keeps detailed diagrams full width under progressive-disclosure groups.
- No external fonts, scripts, raster images, gradients, filters, event handlers or tracking.
- Diagrams are explanatory evidence maps, not solver screenshots or live-execution claims.

See [`DESIGN_SYSTEM.md`](DESIGN_SYSTEM.md) for the complete V13 specification.

"""


def line_icon(kind: str, color: str) -> str:
    shapes = {
        "orbit": '<circle r="4"/><ellipse rx="18" ry="7"/><ellipse rx="7" ry="18" transform="rotate(35)"/>',
        "network": '<circle cx="-14" cy="8" r="4"/><circle cy="-12" r="4"/><circle cx="14" cy="8" r="4"/><path d="M-10 4L-3-8M3-8L10 4M-9 8H9"/>',
        "layers": '<path d="M-18-8L0-17L18-8L0 1Z"/><path d="M-18 1L0 10L18 1"/><path d="M-18 9L0 18L18 9"/>',
        "molecule": '<circle cx="-14" cy="8" r="5"/><circle cy="-11" r="5"/><circle cx="15" cy="8" r="5"/><path d="M-10 3L-4-7M4-7L11 3"/>',
        "chart": '<path d="M-18 16V-16M-18 16H20"/><path d="M-13 7L-5-2L3 4L16-11"/>',
        "flow": '<path d="M-20-9H8M2-15L8-9L2-3"/><path d="M20 9H-8M-2 3L-8 9L-2 15"/>',
        "spectrum": '<path d="M-20 16H20"/><path d="M-14 16V4M-7 16V-7M0 16V7M7 16V-14M14 16V0"/>',
        "shield": '<path d="M0-19L16-13V-1C16 10 9 16 0 20C-9 16-16 10-16-1V-13Z"/><path d="M-7 0L-2 6L9-6"/>',
        "hpc": '<rect x="-17" y="-14" width="34" height="28" rx="4"/><path d="M-9-7H9M-9 0H9M-9 7H3"/><path d="M-22-7H-17M17-7H22M-22 7H-17M17 7H22"/>',
        "lattice": '<path d="M0-19L17-10V10L0 19L-17 10V-10Z"/><path d="M0-19V19M-17-10L17 10M17-10L-17 10"/>',
        "process": '<rect x="-18" y="-15" width="13" height="30" rx="4"/><rect x="5" y="-15" width="13" height="30" rx="4"/><path d="M-5 0H5M-12-20V-15M12 15V20"/>',
        "control": '<path d="M-18-11H18M-18 0H18M-18 11H18"/><circle cx="-6" cy="-11" r="3"/><circle cx="8" cy="0" r="3"/><circle cx="-2" cy="11" r="3"/>',
    }
    shape = shapes.get(kind, shapes["network"])
    return (
        f'<g transform="translate(920 104)" fill="none" stroke="{color}" stroke-width="2.3" '
        'stroke-linecap="round" stroke-linejoin="round" vector-effect="non-scaling-stroke">'
        f"{shape}</g>"
    )


def upgrade_svg(spec: base.VisualSpec) -> str:
    text = base.render_svg(spec)
    for old, new in COLOR_MAP.items():
        text = text.replace(old, new)
    color = COLOR_MAP.get(base.TOKENS[spec.accent], "#22D3EE")
    text = text.replace(
        'data-design-system="uiux-pro-max-scientific-swiss-v3"',
        f'data-design-system="{SYSTEM_ID}" data-icon-system="{ICON_SYSTEM}" '
        'data-density="balanced"',
        1,
    )
    text = text.replace(
        'role="img" aria-labelledby="title desc"',
        'role="img" aria-labelledby="title desc" shape-rendering="geometricPrecision" '
        'text-rendering="optimizeLegibility"',
        1,
    )
    text = text.replace("EVIDENCE-BOUND", "EVIDENCE BOUND")
    text = text.replace("font-size: 38px", "font-size: 40px")
    text = text.replace("font-size: 21px", "font-size: 22px")
    anchor = '<rect x="970" y="42" width="174" height="34"'
    if anchor not in text:
        raise ValueError(f"V12 header anchor missing: {spec.filename}")
    text = text.replace(anchor, line_icon(spec.icon, color) + "\n  " + anchor, 1)
    return text


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
        "- Regenerated all 42 README illustrations as Scientific Research Console V13 using "
        "the UI/UX Pro Max upstream and Chinese tutorial rules: accessible contrast, one line-icon "
        "grammar and GitHub-scale progressive disclosure."
    )
    if bullet in text:
        return text
    return text.replace("## Unreleased\n", f"## Unreleased\n\n{bullet}\n", 1)


def write(path: Path, content: str, *, check: bool) -> None:
    normalized = content.rstrip() + "\n"
    current = path.read_text(encoding="utf-8") if path.exists() else ""
    if check:
        if current != normalized:
            raise SystemExit(f"generated V13 visual artifact is stale: {path.relative_to(base.ROOT)}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(normalized, encoding="utf-8", newline="\n")


def synchronize(*, check: bool) -> None:
    specs = base.parse_specs()
    if len(specs) != 42:
        raise ValueError(f"expected 42 visual specifications, found {len(specs)}")
    for spec in specs:
        write(base.VISUAL_ROOT / spec.filename, upgrade_svg(spec), check=check)

    readme_path = base.ROOT / "README.md"
    readme_zh_path = base.ROOT / "README.zh-CN.md"
    readme = update_system(readme_path.read_text(encoding="utf-8"), README_EN_SYSTEM)
    readme = ENGLISH_ATLAS.sub(base.build_atlas(specs, chinese=False), readme, count=1)
    readme_zh = update_system(readme_zh_path.read_text(encoding="utf-8"), README_ZH_SYSTEM)
    readme_zh = CHINESE_ATLAS.sub(base.build_atlas(specs, chinese=True), readme_zh, count=1)

    write(readme_path, readme, check=check)
    write(readme_zh_path, readme_zh, check=check)
    write(base.VISUAL_ROOT / "DESIGN_SYSTEM.md", DESIGN_SYSTEM, check=check)
    inventory_path = base.VISUAL_ROOT / "README.md"
    write(inventory_path, update_inventory(inventory_path.read_text(encoding="utf-8")), check=check)
    changelog_path = base.ROOT / "CHANGELOG.md"
    write(changelog_path, update_changelog(changelog_path.read_text(encoding="utf-8")), check=check)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Regenerate the UI/UX Pro Max V13 scientific README illustration atlas."
    )
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    synchronize(check=args.check)
    print("PASS: 42 UI/UX Pro Max V13 README visuals are accessible and synchronized.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
