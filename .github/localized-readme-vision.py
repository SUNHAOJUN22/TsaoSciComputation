from __future__ import annotations

from html import escape
from pathlib import Path
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
CONFIG = {'repo': 'TsaoSciComputation', 'readmes': {'zh': 'README.zh-CN.md', 'en': 'README.md'}, 'paths': {'zh': 'docs/localized-vision/scicomputation-vision-zh.svg', 'en': 'docs/localized-vision/scicomputation-vision-en.svg'}, 'anchors': {'zh': '</div>', 'en': '</div>'}, 'zh': {'eyebrow': 'TSAO SCI COMPUTATION · 跨尺度科学计算控制平面', 'title': '从基本方程到可复现科学计算', 'subtitle': '计算合同 · 方法路由 · 资源准入 · 授权执行 · 数值/物理验收', 'vision_label': '项目愿景', 'vision': '连接 DFT、MD、CFD、FEM 与流程模拟，同时保持证据和尺度边界', 'vision_note': '专业求解器提供数值内核；本仓库治理身份、执行、验证与交付。', 'formula_label': '核心计算不变量', 'formula_rows': ['Hbundle = SHA256(solver∥inputs∥environment∥contract∥reference)', '||xₖ₊₁−xₖ|| ≤ εabs + εrel||xₖ||   ·   Σy ≈ JΣθJᵀ + Σnum + Σmodel + Σtransfer'], 'cards': [{'title': '计算合同', 'subtitle': 'Question → Contract', 'formula': 'C=(Q,M,D,R,E,V,U,A)', 'formula_note': '明确目标与权限', 'lines': ['观测量与单位', '输入和假设', '验收容差']}, {'title': '方法与尺度路由', 'subtitle': 'Method · Scale · Adapter', 'formula': 'admit(C)=∏1ᵢ', 'formula_note': '强制谓词合取', 'lines': ['最低充分模型', '适配器能力', '尺度桥变量']}, {'title': '资源准入', 'subtitle': 'CPU · GPU · License', 'formula': 'Σ rₚ ⪯ c', 'formula_note': '容量向量约束', 'lines': ['线程与内存', '设备独占', '许可证 token']}, {'title': '授权执行', 'subtitle': 'Immutable Command Plan', 'formula': 'Hplan = SHA256(argv∥cwd∥env)', 'formula_note': '启动前重新绑定', 'lines': ['可执行体哈希', '输入文件哈希', '受控 PATH']}, {'title': '验证与交付', 'subtitle': 'Numerics · Physics · Evidence', 'formula': 'A=Cfinite∧Cconv∧Cphysics', 'formula_note': '外部结果仍需资格', 'lines': ['收敛与守恒', '不确定度/适用域', '可复现证据包']}], 'disclaimer': 'AI辅助概念设计 · 非科学数据 · 公式对应软件合同而非运行结果', 'footer': 'TsaoSciComputation · 中文跨尺度计算愿景', 'accessible_title': 'TsaoSciComputation 中文跨尺度科学计算愿景图', 'accessible_desc': '连接计算合同、方法尺度路由、资源准入、授权执行和数值物理验证的中文概念设计图。', 'readme_heading': '中文项目愿景图：从基本方程到可复现科学计算', 'readme_alt': 'TsaoSciComputation 中文跨尺度科学计算愿景与数理架构', 'readme_note': '图中方程对应合同、执行身份、收敛、不确定度和验收模块；图不代表 VASP、Gaussian、GROMACS、OpenFOAM 或 Aspen 已经运行。'}, 'en': {'eyebrow': 'TSAO SCI COMPUTATION · MULTISCALE COMPUTATION CONTROL PLANE', 'title': 'From Governing Equations to Reproducible Computation', 'subtitle': 'Calculation contract · method routing · resource admission · authorized execution · numerical/physical acceptance', 'vision_label': 'VISION', 'vision': 'Connect DFT, MD, CFD, FEM and process simulation without losing evidence or scale boundaries', 'vision_note': 'Professional solvers provide kernels; this repository governs identity, execution, validation and delivery.', 'formula_label': 'CORE COMPUTATION INVARIANTS', 'formula_rows': ['Hbundle = SHA256(solver∥inputs∥environment∥contract∥reference)', '||xₖ₊₁−xₖ|| ≤ εabs + εrel||xₖ||   ·   Σy ≈ JΣθJᵀ + Σnum + Σmodel + Σtransfer'], 'cards': [{'title': 'Calculation contract', 'subtitle': 'Question → Contract', 'formula': 'C=(Q,M,D,R,E,V,U,A)', 'formula_note': 'objective and authority', 'lines': ['observables & units', 'inputs & assumptions', 'acceptance tolerances']}, {'title': 'Method routing', 'subtitle': 'Method · Scale · Adapter', 'formula': 'admit(C)=∏1ᵢ', 'formula_note': 'conjunctive gates', 'lines': ['minimum model', 'adapter capability', 'scale-bridge variables']}, {'title': 'Resource admission', 'subtitle': 'CPU · GPU · License', 'formula': 'Σ rₚ ⪯ c', 'formula_note': 'capacity vector', 'lines': ['threads & memory', 'exclusive devices', 'license tokens']}, {'title': 'Authorized execution', 'subtitle': 'Immutable Command Plan', 'formula': 'Hplan = SHA256(argv∥cwd∥env)', 'formula_note': 'rebound before launch', 'lines': ['executable hash', 'input-file hash', 'sanitized PATH']}, {'title': 'Validation delivery', 'subtitle': 'Numerics · Physics · Evidence', 'formula': 'A=Cfinite∧Cconv∧Cphysics', 'formula_note': 'external qualification remains', 'lines': ['convergence & balance', 'UQ & applicability', 'reproducible bundle']}], 'disclaimer': 'AI-ASSISTED CONCEPTUAL DESIGN · NOT SCIENTIFIC DATA', 'footer': 'TsaoSciComputation · English multiscale vision', 'accessible_title': 'TsaoSciComputation English multiscale scientific computation vision', 'accessible_desc': 'English conceptual design connecting calculation contracts, method and scale routing, resource admission, authorized execution and numerical/physical validation.', 'readme_heading': 'Project vision: from governing equations to reproducible computation', 'readme_alt': 'TsaoSciComputation English multiscale computation vision and mathematical architecture', 'readme_note': 'The equations map to contract, execution-identity, convergence, uncertainty and acceptance modules. The figure does not claim that VASP, Gaussian, GROMACS, OpenFOAM or Aspen has run.'}}

FONT = "Inter,'Noto Sans SC','Noto Sans CJK SC','Microsoft YaHei','PingFang SC','WenQuanYi Micro Hei','Segoe UI',Arial,sans-serif"
MATH_FONT = "'STIX Two Math','Cambria Math','Noto Sans Math','Noto Sans SC',serif"


def text(value: object) -> str:
    return escape(str(value), quote=True)


def render_svg(spec: dict[str, object]) -> str:
    cards = list(spec['cards'])
    colors = ['#22d3ee', '#818cf8', '#c084fc', '#34d399', '#fbbf24']
    x_positions = [78, 370, 662, 954, 1246]
    card_markup: list[str] = []
    for index, card in enumerate(cards):
        x = x_positions[index]
        color = colors[index]
        lines = list(card['lines'])
        formula = card['formula']
        card_markup.append(f'''<g transform="translate({x} 250)" filter="url(#shadow)">
  <rect width="250" height="390" rx="26" fill="#0d2034" stroke="{color}" stroke-width="2"/>
  <circle cx="42" cy="42" r="23" fill="{color}"/><text x="42" y="48" text-anchor="middle" class="step">{index + 1}</text>
  <text x="24" y="93" class="card-title">{text(card['title'])}</text>
  <text x="24" y="124" class="card-sub">{text(card['subtitle'])}</text>
  <rect x="20" y="151" width="210" height="76" rx="15" fill="#081522" stroke="#334155"/>
  <text x="125" y="184" text-anchor="middle" class="formula-small">{text(formula)}</text>
  <text x="125" y="207" text-anchor="middle" class="micro">{text(card['formula_note'])}</text>
  <circle cx="34" cy="274" r="6" fill="{color}"/><text x="51" y="280" class="body">{text(lines[0])}</text>
  <circle cx="34" cy="316" r="6" fill="{color}"/><text x="51" y="322" class="body">{text(lines[1])}</text>
  <circle cx="34" cy="358" r="6" fill="{color}"/><text x="51" y="364" class="body">{text(lines[2])}</text>
</g>''')
    arrows = []
    for x in [330, 622, 914, 1206]:
        arrows.append(f'<path d="M{x} 445h28" stroke="#94a3b8" stroke-width="4"/><path d="M{x+28} 445l-12-8v16z" fill="#94a3b8"/>')

    formula_rows = list(spec['formula_rows'])
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 900" role="img" aria-labelledby="title desc">
<title id="title">{text(spec['accessible_title'])}</title>
<desc id="desc">{text(spec['accessible_desc'])}</desc>
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#06121f"/><stop offset="0.55" stop-color="#10233f"/><stop offset="1" stop-color="#1f2554"/></linearGradient>
  <radialGradient id="halo" cx="50%" cy="50%" r="60%"><stop offset="0" stop-color="#22d3ee" stop-opacity=".30"/><stop offset="1" stop-color="#22d3ee" stop-opacity="0"/></radialGradient>
  <filter id="shadow" x="-30%" y="-30%" width="160%" height="160%"><feDropShadow dx="0" dy="14" stdDeviation="18" flood-color="#020617" flood-opacity=".42"/></filter>
  <pattern id="grid" width="38" height="38" patternUnits="userSpaceOnUse"><path d="M38 0H0V38" fill="none" stroke="#dbeafe" stroke-opacity=".055"/></pattern>
  <style>
    text{{font-family:{FONT}}}
    .eyebrow{{font-size:17px;letter-spacing:3.5px;font-weight:800;fill:#67e8f9}}
    .title{{font-size:50px;font-weight:850;fill:#f8fafc}}
    .subtitle{{font-size:21px;fill:#cbd5e1}}
    .vision{{font-size:18px;font-weight:700;fill:#dbeafe}}
    .card-title{{font-size:23px;font-weight:800;fill:#f8fafc}}
    .card-sub{{font-size:15px;fill:#9fb1c8}}
    .body{{font-size:15px;fill:#d5deea}}
    .micro{{font-size:12px;fill:#8ea2ba}}
    .step{{font-size:15px;font-weight:900;fill:#07111f}}
    .formula{{font-family:{MATH_FONT};font-size:22px;fill:#e0f2fe}}
    .formula-small{{font-family:{MATH_FONT};font-size:17px;fill:#f0f9ff}}
    .disclaimer{{font-size:12px;font-weight:850;letter-spacing:1.1px;fill:#111827}}
  </style>
</defs>
<rect width="1600" height="900" fill="url(#bg)"/>
<rect width="1600" height="900" fill="url(#grid)"/>
<ellipse cx="800" cy="188" rx="610" ry="190" fill="url(#halo)"/>
<g transform="translate(78 54)">
  <text class="eyebrow">{text(spec['eyebrow'])}</text>
  <text class="title" y="63">{text(spec['title'])}</text>
  <text class="subtitle" y="105">{text(spec['subtitle'])}</text>
</g>
<g transform="translate(1030 68)" filter="url(#shadow)">
  <rect width="490" height="104" rx="24" fill="#0a1829" stroke="#334155"/>
  <text x="24" y="36" class="vision">{text(spec['vision_label'])}</text>
  <text x="24" y="70" class="formula-small">{text(spec['vision'])}</text>
  <text x="24" y="92" class="micro">{text(spec['vision_note'])}</text>
</g>
{''.join(card_markup)}
{''.join(arrows)}
<g transform="translate(78 686)" filter="url(#shadow)">
  <rect width="1444" height="128" rx="25" fill="#091827" stroke="#334155"/>
  <text x="24" y="34" class="vision">{text(spec['formula_label'])}</text>
  <text x="24" y="68" class="formula">{text(formula_rows[0])}</text>
  <text x="24" y="100" class="formula">{text(formula_rows[1])}</text>
</g>
<g transform="translate(78 842)">
  <rect width="640" height="28" rx="14" fill="#f8fafc" opacity=".95"/>
  <text x="320" y="19" text-anchor="middle" class="disclaimer">{text(spec['disclaimer'])}</text>
  <text x="1440" y="20" text-anchor="end" class="micro">{text(spec['footer'])}</text>
</g>
</svg>'''


def localized_block(language: str, image_path: str, spec: dict[str, object]) -> str:
    marker = f'LOCALIZED_VISION_{language.upper()}'
    return f'''<!-- {marker}:START -->
## {spec['readme_heading']}

<p align="center">
  <img src="{image_path}" width="100%" alt="{spec['readme_alt']}">
</p>

> {spec['readme_note']}

<!-- {marker}:END -->'''


def replace_or_insert(path: Path, language: str, image_path: str, spec: dict[str, object], anchor: str) -> None:
    content = path.read_text(encoding='utf-8')
    marker = f'LOCALIZED_VISION_{language.upper()}'
    pattern = re.compile(rf'<!-- {re.escape(marker)}:START -->.*?<!-- {re.escape(marker)}:END -->', flags=re.DOTALL)
    block = localized_block(language, image_path, spec)
    if pattern.search(content):
        content = pattern.sub(block, content, count=1)
    elif anchor and anchor in content:
        content = content.replace(anchor, anchor + '\n\n' + block, 1)
    elif '</div>' in content[:5000]:
        content = content.replace('</div>', '</div>\n\n' + block, 1)
    else:
        first_break = content.find('\n\n')
        if first_break < 0:
            raise RuntimeError(f'{path}: no safe insertion point')
        content = content[:first_break] + '\n\n' + block + content[first_break:]
    path.write_text(content, encoding='utf-8', newline='\n')


def main() -> None:
    for language in ('zh', 'en'):
        svg_path = ROOT / CONFIG['paths'][language]
        svg_path.parent.mkdir(parents=True, exist_ok=True)
        svg_path.write_text(render_svg(CONFIG[language]), encoding='utf-8', newline='\n')
        parsed = ET.parse(svg_path).getroot()
        if not parsed.tag.endswith('svg') or not parsed.attrib.get('viewBox'):
            raise RuntimeError(f'{svg_path}: invalid SVG root/viewBox')
        raw = svg_path.read_text(encoding='utf-8')
        if '\ufffd' in raw or '<script' in raw.lower() or 'javascript:' in raw.lower():
            raise RuntimeError(f'{svg_path}: unsafe or corrupted content')

    replace_or_insert(ROOT / CONFIG['readmes']['zh'], 'zh', CONFIG['paths']['zh'], CONFIG['zh'], CONFIG['anchors']['zh'])
    replace_or_insert(ROOT / CONFIG['readmes']['en'], 'en', CONFIG['paths']['en'], CONFIG['en'], CONFIG['anchors']['en'])

    for language in ('zh', 'en'):
        target = ROOT / CONFIG['readmes'][language]
        if CONFIG['paths'][language] not in target.read_text(encoding='utf-8'):
            raise RuntimeError(f'{target}: localized image reference missing')
    print(f"localized README vision generated for {CONFIG['repo']}")


if __name__ == '__main__':
    main()
