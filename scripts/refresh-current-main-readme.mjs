#!/usr/bin/env node
/** Deterministic bilingual documentation; figures describe contracts, not runs. */
import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
const ROOT = resolve(fileURLToPath(new URL('..', import.meta.url)));
const PROFILE = {
 "slug":"tsao-scicomputation","title":"TsaoSciComputation",
 "code":["tsao_computation/adapters/base.py","tsao_computation/execution/runner.py","tsao_computation/validation/numerical.py"],
 "readmes":[{"path":"README.md","lang":"en"},{"path":"README.zh-CN.md","lang":"zh"}],
 "zh":{"tagline":"从计算合同、执行身份与收敛门到可重复多尺度交付","stages":[["问题与合同","目标、方法、数据与容差"],["执行身份","求解器、输入与环境哈希"],["资源准入","CPU/GPU/许可证与工作目录"],["数值验收","解析、收敛、守恒与等价"],["证据交付","UQ、适用域与责任主体"]],"boundary":"仓库是计算控制面与资格框架；第三方 DFT、MD、CFD、FEM 和流程求解器保持 EXTERNAL_HOLD。","strategy":["先核对安装环境、输入结构、单位、有效范围与执行权限。","按上面的源码锚点区分原生实现、解释性合同和外部执行要求。","先运行快速回归和完整质量门，再用固定提交执行长期回归。","逐项保存原始日志、机器报告和限制；任何缺失证据不得写成 PASS。"]},
 "en":{"tagline":"From calculation contracts, execution identity and convergence gates to reproducible multiscale delivery","stages":[["Question and contract","Objective, method, data, tolerances"],["Execution identity","Solver, input and environment hashes"],["Resource admission","CPU/GPU/licence and working directory"],["Numerical acceptance","Parsing, convergence, conservation, parity"],["Evidence delivery","UQ, applicability and authority"]],"boundary":"The repository is a computation control plane and qualification framework; third-party DFT, MD, CFD, FEM and process solvers remain EXTERNAL_HOLD.","strategy":["Check the installation environment, input structure, units, applicability and execution permissions.","Use the source mappings above to distinguish native implementation, explanatory contracts and external execution requirements.","Run focused regression and full quality gates before long-duration testing of pinned commits.","Preserve original logs, machine-readable reports and limitations; missing evidence must never be reported as PASS."]},
 "math":[
  {"latex":"u_c=\\sqrt{u_{\\mathrm{stat}}^2+u_{\\mathrm{model}}^2+u_{\\mathrm{num}}^2}","plain":["u_c² = u_stat² + u_model² + u_num²"],"zh":{"name":"独立标准不确定度","note":"各分量必须有限、非负，并使用同一输出单位；平方和要求分量互不相关。实现使用 `math.hypot` 避免直接平方造成的中间溢出，并拒绝不可表示的最终结果。相关项必须另行采用协方差传播，不能套用该接口。"},"en":{"name":"Independent uncertainty","note":"Components must be finite, nonnegative and expressed in the same output units. Quadrature assumes uncorrelated contributions. The implementation uses math.hypot to avoid intermediate squaring overflow and rejects unrepresentable totals. Correlated contributions require covariance propagation, not this interface."},"code":["tsao_computation/uncertainty/model.py"]},
  {"latex":"\\Delta=|x_n-x_{n-1}|,\\qquad \\tau=\\max\\!\\left(a,r\\max(|x_n|,|x_{n-1}|,1)\\right),\\qquad\\Delta\\le\\tau","plain":["Δ = |x_n − x_(n−1)|","τ = max(a, r · max(|x_n|,|x_(n−1)|,1))"],"zh":{"name":"末两点收敛检查","note":"该门比较末两个有限数值，绝对容差为 a、相对容差为 r；阈值使用 `max`，不是两项相加。数值尺度的下限 1 按输入单位解释，因此应先规范单位或无量纲化。通过末两点检查不证明轨迹整体收敛或统计采样充分。"},"en":{"name":"Last-pair convergence","note":"This gate compares the final two finite values using absolute tolerance a and relative tolerance r. Its threshold uses max, not an additive tolerance. The scale floor of one is expressed in the chosen input units, so normalize units or nondimensionalize first. Passing the last pair does not prove global trajectory convergence or adequate sampling."},"code":["tsao_computation/validation/numerical.py"]},
  {"latex":"C_{\\mathrm{accept}}=C_{\\mathrm{identity}}\\land C_{\\mathrm{input}}\\land C_{\\mathrm{finite}}\\land C_{\\mathrm{policy}}","plain":["accept = identity ∧ inputs","∧ finite outputs ∧ declared policy"],"zh":{"name":"控制面验收合同","note":"这是执行层和适配器约束的解释性组合，不是一个拟合分数或所有引擎共享的单一函数。必须分别保存引擎版本、输入校验和、解析证据和适用的验收规则；仅发现软件、生成输入文件或解析示例不等于完成外部科学计算。"},"en":{"name":"Control-plane contract","note":"This is an explanatory composition of runner and adapter requirements, not a fitted score or a single function shared by every engine. Preserve engine versions, input hashes, parser evidence and applicable acceptance policies separately. Software discovery, generated inputs and parsed examples are not external scientific execution."},"code":["tsao_computation/adapters/base.py","tsao_computation/execution/runner.py"]}
 ],
 "commands":["python scripts/verify_all.py --profile core","python scripts/verify_all.py --profile quality","python scripts/verify_native_core.py"],"accent":"#67e8f9"
};
PROFILE.math.push({
  "latex": "E_{n+1}=E_n\\mathbin{\\Vert}[e_{n+1}],\\quad \\lvert\\operatorname{UTF8}(E_{n+1})\\rvert\\le64\\times2^{20}\\;\\mathrm{bytes}",
  "plain": [
    "lock → validate → append",
    "→ atomic replace → unlock"
  ],
  "zh": {
    "name": "可追溯事件的串行追加",
    "note": "事件必须是 JSON 对象；嵌套重复键、NaN、Infinity、浮点溢出和非 UTF-8 输入拒绝进入账本。协作写入者通过排他侧车锁串行执行读—追加—原子替换，避免多个进程覆盖彼此的事件。此为本地文件协议，不是分布式数据库事务；64 MiB 上界到达时需要显式归档。等待锁最多 10 秒，崩溃遗留锁不会被自动抢占；维护者应确认写入者已退出并备份账本后再恢复。"
  },
  "en": {
    "name": "Serialized provenance append",
    "note": "Events must be JSON objects; nested duplicate keys, NaN, Infinity, overflowing floating-point numbers and non-UTF-8 input are rejected. Cooperating writers serialize read–append–atomic-replace operations through an exclusive sidecar lock, preventing lost updates. This is a local-file protocol, not a distributed database transaction; explicit archival is required at the 64 MiB bound. Lock acquisition times out after 10 seconds. An abandoned lock is not stolen automatically; confirm the writer has exited and back up the ledger before recovery."
  },
  "code": [
    "tsao_computation/provenance/ledger.py",
    "tests/test_provenance_ledger_integrity.py"
  ]
});
const START = '<!-- CURRENT_MAIN_ACCEPTANCE_V2:START -->';
const END = '<!-- CURRENT_MAIN_ACCEPTANCE_V2:END -->';
const esc = (value) => String(value).replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;').replaceAll("'", '&apos;');
const normalized = (value) => value.normalize('NFC').replaceAll('\r\n', '\n');

// Conservative em-width estimates determine wrapping; browser QA checks glyph bounds.
function widthEm(text) {
  return [...text].reduce((sum, char) => sum + (/\p{Script=Han}/u.test(char) ? 1 : /[MW@%]/u.test(char) ? 0.95 : /[il.,:;!| ]/u.test(char) ? 0.34 : 0.65), 0);
}
function lines(text, width, size) {
  const output = []; let line = '';
  for (const word of String(text).match(/\p{Script=Han}|[^\p{Script=Han}\s]+|\s+/gu) ?? []) {
    if (line && widthEm(line + word) * size > width) { output.push(line.trim()); line = ''; }
    if (widthEm(word) * size > width) {
      for (const char of word) {
        if (line && widthEm(line + char) * size > width) { output.push(line.trim()); line = ''; }
        line += char;
      }
    } else line += word;
  }
  if (line.trim()) output.push(line.trim());
  return output;
}
function textBlock(value, x, baseline, width, size, leading, maxLines, color = '#dbeafe', weight = 400) {
  const wrapped = lines(value, width, size);
  if (wrapped.length > maxLines) throw Error(`Text exceeds its layout box: ${value}`);
  return `<text x="${x}" y="${baseline}" font-size="${size}" font-weight="${weight}" fill="${color}" data-box="${x},${baseline - size * 1.3},${width},${leading * maxLines + size * 0.5}">${wrapped.map((line, index) => `<tspan x="${x}" dy="${index ? leading : 0}">${esc(line)}</tspan>`).join('')}</text>`;
}
function visual(lang) {
  const t = PROFILE[lang], zh = lang === 'zh', accent = PROFILE.accent;
  const stages = t.stages.map(([heading, detail], index) => {
    const x = 46 + 307 * index;
    return `<g><rect x="${x}" y="246" width="278" height="220" rx="20" fill="#0f2038" stroke="${accent}" stroke-opacity=".5"/><circle cx="${x + 31}" cy="279" r="15" fill="${accent}" fill-opacity=".16"/><text x="${x + 31}" y="284" text-anchor="middle" font-size="13" fill="${accent}">0${index + 1}</text>${textBlock(heading, x + 20, 326, 237, 23, 28, 2, '#f8fafc', 700)}${textBlock(detail, x + 20, 399, 237, 17, 25, 2)}</g>`;
  }).join('');
  const arrows = [0, 1, 2, 3].map((index) => `<path d="M${327 + 307 * index} 357h21" fill="none" stroke="${accent}" stroke-width="2" marker-end="url(#arrow)"/>`).join('');
  const equations = PROFILE.math.slice(0, 3).map((formula, index) => {
    const x = 46 + 506 * index;
    return `<g><rect x="${x}" y="510" width="476" height="161" rx="20" fill="#101827" stroke="#64748b" stroke-opacity=".65"/>${textBlock(`${String(index + 1).padStart(2, '0')}  ${formula[lang].name}`, x + 22, 544, 432, 17, 22, 1, accent, 650)}${formula.plain.map((line, row) => textBlock(line, x + 22, 588 + row * 29, 432, 19, 26, 1, '#f8fafc')).join('')}</g>`;
  }).join('');
  const boundary = textBlock(t.boundary, 73, 767, 1440, 18, 27, 2);
  return normalized(`<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 900" role="img" aria-labelledby="title desc" lang="${zh ? 'zh-CN' : 'en'}">
<title id="title">${esc(PROFILE.title)} — ${zh ? '代码与数学合同' : 'Code and mathematical contracts'}</title>
<desc id="desc">${esc(t.tagline)} ${esc(t.boundary)}</desc>
<defs><linearGradient id="background" x2="1" y2="1"><stop stop-color="#070e1d"/><stop offset="1" stop-color="#172338"/></linearGradient><pattern id="grid" width="44" height="44" patternUnits="userSpaceOnUse"><path d="M44 0H0V44" fill="none" stroke="#cbd5e1" stroke-opacity=".055"/></pattern><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0 1L9 5L0 9" fill="none" stroke="${accent}" stroke-width="1.4"/></marker><style>text{font-family:"Noto Sans CJK SC","Microsoft YaHei","PingFang SC","Noto Sans",Arial,sans-serif}</style></defs>
<rect width="1600" height="900" fill="url(#background)"/><rect width="1600" height="900" fill="url(#grid)"/><circle cx="1444" cy="70" r="178" fill="${accent}" opacity=".07"/>
<path d="M1350 26L1480 75L1410 162L1539 203M1480 75L1570 20M1410 162L1310 175" fill="none" stroke="${accent}" stroke-opacity=".22" stroke-width="2"/>
${textBlock(PROFILE.title, 48, 82, 1400, 49, 54, 1, '#f8fafc', 750)}
${textBlock(t.tagline, 49, 130, 1465, 22, 30, 2, accent)}
${textBlock(zh ? '概念架构图 · 非测量数据 · 不代表外部求解已经执行' : 'CONCEPTUAL ARCHITECTURE · NOT MEASURED DATA · NOT PROOF OF EXTERNAL EXECUTION', 49, 214, 1470, 15, 23, 1, '#94a3b8')}
${arrows}${stages}${equations}
<rect x="46" y="712" width="1488" height="111" rx="18" fill="#080f1b" stroke="#334155"/>
${textBlock(zh ? '资格与解释边界' : 'QUALIFICATION AND INTERPRETATION', 73, 741, 1440, 13, 20, 1, accent, 650)}${boundary}
${textBlock(zh ? '固定源码 · 有限数值 · 可复现证据 · 人工审阅' : 'PINNED SOURCE · FINITE NUMERICS · REPRODUCIBLE EVIDENCE · HUMAN REVIEW', 49, 871, 1470, 14, 20, 1, '#94a3b8')}
</svg>
`);
}
function mathSection(lang) {
  return PROFILE.math.map((formula) => {
    const t = formula[lang];
    return `#### ${t.name}\n\n$$\n${formula.latex}\n$$\n\n${t.note}\n\n${lang === 'zh' ? '源码对应' : 'Source mapping'}: ${formula.code.map((path) => `[\`${path}\`](${path})`).join(' · ')}`;
  }).join('\n\n');
}
function section(lang, markers = true) {
  const zh = lang === 'zh', t = PROFILE[lang];
  return [markers ? START : '', `## ${zh ? '当前实现：代码、数学与使用策略' : 'Current implementation: code, mathematics and usage'}`, '',
    `![${zh ? '中文代码与数学合同概念图' : 'English code and mathematical-contract concept'}](docs/current-main/${PROFILE.slug}-current-main-${lang}.svg)`, '',
    `> ${t.boundary}`, '', mathSection(lang), '', `### ${zh ? '使用与验收顺序' : 'Usage and acceptance sequence'}`, '',
    ...t.strategy.map((item, index) => `${index + 1}. ${item}`), '', '```bash', ...PROFILE.commands, '```', '',
    zh ? '每次修复均须绑定新提交重新测试。基线回归、两段各三小时的重复回归、浏览器图形检查和外部工程认证是不同证据，不可互相替代。没有原始回执时，不宣称已完成六小时验收。' : 'Retest every changed commit. Baseline regression, two three-hour regression segments, browser visual checks and external engineering qualification are distinct evidence classes. Without original receipts, no six-hour completion is claimed.', '',
    `${zh ? '源码锚点' : 'Implementation anchors'}: ${PROFILE.code.map((path) => `[\`${path}\`](${path})`).join(' · ')}`, '', markers ? END : '',
  ].join('\n').trim();
}
function inject(original, generated) {
  const start = original.indexOf(START), end = original.indexOf(END);
  if ((start === -1) !== (end === -1) || end < start) throw Error('Unbalanced generated-section markers');
  const text = start === -1 ? `${original.trimEnd()}\n\n${generated}\n` : original.slice(0, start) + generated + original.slice(end + END.length);
  return normalized(text.trimEnd() + '\n');
}
const output = new Map(['zh', 'en'].map((lang) => [`docs/current-main/${PROFILE.slug}-current-main-${lang}.svg`, visual(lang)]));
for (const spec of PROFILE.readmes) {
  const content = spec.lang === 'bi' ? `${START}\n${section('zh', false)}\n\n${section('en', false)}\n${END}` : section(spec.lang);
  output.set(spec.path, inject(readFileSync(join(ROOT, spec.path), 'utf8'), content));
}
output.set('docs/CURRENT_MAIN_ACCEPTANCE.md', `# ${PROFILE.title} — code-backed documentation\n\n${PROFILE.code.map((path) => `- [\`${path}\`](../${path})`).join('\n')}\n\n${PROFILE.zh.boundary}\n\n${PROFILE.en.boundary}\n\nThe equations and diagrams document the declared implementation and its interpretation limits. They are not an execution attestation.\n`);
for (const path of new Set([...PROFILE.code, ...PROFILE.math.flatMap((formula) => formula.code)])) if (!existsSync(join(ROOT, path))) throw Error(`Missing source mapping: ${path}`);
const bad = [String.fromCodePoint(0xfffd), String.fromCodePoint(0x951f, 0x65a4, 0x62f7)];
for (const [path, content] of output) {
  if (bad.some((token) => content.includes(token))) throw Error(`Invalid text: ${path}`);
  if (path.endsWith('.svg') && /<script\b|<foreignObject\b|\son[a-z]+\s*=|javascript:|(?:href|xlink:href)\s*=\s*["'](?:https?:|\/\/|data:)/iu.test(content)) throw Error(`Active or external SVG content: ${path}`);
}
if (process.argv.includes('--write')) for (const [path, content] of output) { mkdirSync(dirname(join(ROOT, path)), { recursive: true }); writeFileSync(join(ROOT, path), content, 'utf8'); }
const stale = [...output].filter(([path, content]) => !existsSync(join(ROOT, path)) || readFileSync(join(ROOT, path), 'utf8') !== content).map(([path]) => path);
if (stale.length) throw Error(`Stale documentation: ${stale.join(', ')}`);
console.log(JSON.stringify({ schemaVersion: 'readme-mathematics-v6', project: PROFILE.title, files: [...output.keys()], status: 'PASS', scope: 'source mapping, deterministic generation and text integrity; not external scientific acceptance' }, null, 2));
