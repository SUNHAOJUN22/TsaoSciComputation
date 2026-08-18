from __future__ import annotations

import json
import re
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
START = "<!-- TSAO_SKILL_NATIVE_V15_START -->"
END = "<!-- TSAO_SKILL_NATIVE_V15_END -->"
OLD = re.compile(r"<!-- TSAO_SKILL_NATIVE_V(?:1[0-4]|[1-9])_START -->.*?<!-- TSAO_SKILL_NATIVE_V(?:1[0-4]|[1-9])_END -->\s*", re.DOTALL)


def clean(value: str) -> str:
    return textwrap.dedent(value).strip() + "\n"


def write(path: str, value: str) -> None:
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(clean(value), encoding="utf-8", newline="\n")


def merge(path: str, block: str, title: str) -> None:
    target = ROOT / path
    current = target.read_text(encoding="utf-8") if target.exists() else f"# {title}\n\n"
    current = OLD.sub("", current).rstrip() + "\n\n"
    target.write_text(current + START + "\n" + clean(block) + END + "\n", encoding="utf-8", newline="\n")


skill = r'''
---
name: tsao-scicomputation
description: Evidence-first scientific-computation execution and acceptance workflow. Use for solver orchestration, strict scientific data, dimensional convergence, bounded subprocess execution, provenance ledgers, and signed acceptance graphs. Do not infer real HPC or solver execution, scientific validation, or acceptance from mock output, ordinary booleans, filenames, or self-reported strings.
---

# TsaoSciComputation Skill

## State progression

Keep these states distinct:

`PLANNED → PREPARED → REPORTED → CONVERGED → NUMERICALLY_CHECKED → PHYSICALLY_VALIDATED → ACCEPTED`.

No state may be skipped merely because a solver returned exit code zero.

## Numeric contract

A convergence decision uses canonical quantities and a scaled norm:

\[
\|r\|_\infty \le a_{tol}+r_{tol}\max(\|y\|_\infty,s_{floor}).
\]

Units and dimensions must match before comparison. Missing, Boolean, NaN, or infinite values are invalid rather than zero.

## Evidence contract

An execution receipt binds exact input/output digests, code and environment revisions, runner identity, timestamps, exit status, nonce, scope, and signature. Scientific acceptance additionally requires independent numerical review, physical validation, and qualified approval.

## Truth boundary

Local contract tests establish software behavior only. Without a real external solver/HPC receipt and independent approval, retain `EXTERNAL_EXECUTION_NOT_VERIFIED` or `HOLD`.
'''

dod = r'''
# Definition of done

- Strict JSON rejects duplicate keys, NaN, infinity, and ambiguous scientific values.
- Quantities carry value, unit, dimension, and canonical conversion.
- Convergence compares compatible dimensions and declared tolerances.
- Exit code, convergence, numerical checking, physical validation, and acceptance are separate fields.
- Subprocess output is bounded and the full process tree is terminated on timeout or overflow.
- Provenance is append-only, transactional, hash-linked, and replay-verifiable.
- Accepted evidence is signed, scoped, unexpired, non-revoked, non-replayed, and independently approved.
- Mock or portable execution never becomes a real solver/HPC claim.
'''

openai_yaml = r'''
interface:
  display_name: "Tsao Scientific Computation"
  short_description: "Dimension-safe execution, provenance, and scientific acceptance"
  default_prompt: "Validate the scientific datum, run the deterministic execution contract, bind evidence to exact artifacts, and keep execution, convergence, validation, and acceptance separate."
policy:
  allow_implicit_invocation: true
  truth_boundary: "No real solver/HPC claim without an external signed execution receipt."
'''

evals = {"schema": "tsao-scicomputation.skill-routing.v15", "skill": "tsao-scicomputation", "cases": [
    {"id": "en-execute", "language": "en", "prompt": "Run this solver with bounded logs and produce an exact evidence receipt.", "expected": "TRIGGER"},
    {"id": "zh-execute", "language": "zh", "prompt": "执行这个求解器，限制日志大小并生成精确证据回执。", "expected": "TRIGGER"},
    {"id": "en-convergence", "language": "en", "prompt": "Audit whether these dimensioned residuals actually satisfy convergence.", "expected": "TRIGGER"},
    {"id": "zh-convergence", "language": "zh", "prompt": "核验这些带量纲残差是否真正满足收敛判据。", "expected": "TRIGGER"},
    {"id": "en-negative", "language": "en", "prompt": "What is numerical analysis?", "expected": "NO_TRIGGER"},
    {"id": "zh-negative", "language": "zh", "prompt": "什么是数值分析？", "expected": "NO_TRIGGER"}
]}

validator = r'''
from __future__ import annotations

import argparse
import json
from pathlib import Path

REQUIRED = (
    ".agents/skills/tsao-scicomputation/SKILL.md",
    ".agents/skills/tsao-scicomputation/agents/openai.yaml",
    ".agents/skills/tsao-scicomputation/references/definition-of-done.md",
    ".agents/skills/tsao-scicomputation/evals/evals.json",
    "assets/diagrams/vision-en.svg",
    "assets/diagrams/vision-zh.svg",
)
BAD = ("\x00", "\ufffd", "Ã", "Â", "â€")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--report", default="artifacts/skill-validation-v15.json")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    errors: list[str] = []
    for rel in REQUIRED:
        if not (root / rel).is_file():
            errors.append(f"missing {rel}")
    skill = root / REQUIRED[0]
    if skill.is_file():
        text = skill.read_text(encoding="utf-8")
        if not text.startswith("---\n") or "name: tsao-scicomputation" not in text[:800]:
            errors.append("invalid SKILL.md frontmatter")
        if "Do not infer real HPC" not in text[:1200]:
            errors.append("anti-trigger boundary missing")
    for path in root.rglob("*"):
        if path.is_file() and path.suffix.lower() in {".md", ".py", ".json", ".yaml", ".yml", ".svg"}:
            value = path.read_text(encoding="utf-8")
            if any(marker in value for marker in BAD):
                errors.append(f"Unicode failure in {path.relative_to(root)}")
    eval_path = root / REQUIRED[3]
    if eval_path.is_file():
        cases = json.loads(eval_path.read_text(encoding="utf-8")).get("cases", [])
        if len(cases) < 6 or {c.get("expected") for c in cases} != {"TRIGGER", "NO_TRIGGER"}:
            errors.append("routing evals incomplete")
    report = {"schema": "tsao-scicomputation.skill-validation.v15", "status": "PASS" if not errors else "FAIL", "errors": errors}
    output = root / args.report
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
'''

contracts = r'''
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Sequence


@dataclass(frozen=True)
class ScientificQuantity:
    value: float
    unit: str
    dimension: str
    scale_to_si: float

    def canonical(self) -> float:
        if isinstance(self.value, bool) or isinstance(self.scale_to_si, bool):
            raise TypeError("quantity values must not be booleans")
        if not isfinite(float(self.value)) or not isfinite(float(self.scale_to_si)):
            raise ValueError("quantity values must be finite")
        if self.scale_to_si <= 0.0 or not self.unit or not self.dimension:
            raise ValueError("positive scale, unit, and dimension are required")
        return float(self.value) * float(self.scale_to_si)


@dataclass(frozen=True)
class ExecutionReceipt:
    input_digest: str
    output_digest: str
    code_revision: str
    environment_digest: str
    runner_id: str
    exit_code: int
    external_solver: bool
    signature_valid: bool
    scope_valid: bool
    nonce_fresh: bool

    def valid_external_execution(self) -> bool:
        digests = (self.input_digest, self.output_digest, self.code_revision, self.environment_digest)
        return (
            all(len(value) >= 16 for value in digests)
            and bool(self.runner_id)
            and self.exit_code == 0
            and self.external_solver
            and self.signature_valid
            and self.scope_valid
            and self.nonce_fresh
        )


@dataclass(frozen=True)
class ConvergenceDecision:
    status: str
    residual_norm_si: float
    threshold_si: float


def convergence_gate(
    residuals: Sequence[ScientificQuantity],
    references: Sequence[ScientificQuantity],
    *,
    abs_tolerance_si: float,
    rel_tolerance: float,
    scale_floor_si: float,
) -> ConvergenceDecision:
    if not residuals or len(residuals) != len(references):
        raise ValueError("residual and reference vectors must be non-empty and aligned")
    dimensions = {item.dimension for item in [*residuals, *references]}
    if len(dimensions) != 1:
        raise ValueError("convergence operands must share one dimension")
    for value in (abs_tolerance_si, rel_tolerance, scale_floor_si):
        if isinstance(value, bool) or not isfinite(float(value)) or value < 0.0:
            raise ValueError("tolerances must be finite non-negative reals")
    residual_norm = max(abs(item.canonical()) for item in residuals)
    reference_norm = max(abs(item.canonical()) for item in references)
    threshold = float(abs_tolerance_si) + float(rel_tolerance) * max(reference_norm, float(scale_floor_si))
    return ConvergenceDecision("CONVERGED" if residual_norm <= threshold else "NOT_CONVERGED", residual_norm, threshold)


def acceptance_state(
    *, execution: ExecutionReceipt | None, converged: bool, numerically_checked: bool,
    physically_validated: bool, independent_approval: bool
) -> str:
    if execution is None or not execution.valid_external_execution():
        return "EXTERNAL_EXECUTION_NOT_VERIFIED"
    if not converged:
        return "REPORTED_NOT_CONVERGED"
    if not numerically_checked:
        return "CONVERGED_NUMERICAL_REVIEW_PENDING"
    if not physically_validated:
        return "NUMERICALLY_CHECKED_PHYSICAL_VALIDATION_PENDING"
    if not independent_approval:
        return "PHYSICALLY_VALIDATED_ACCEPTANCE_PENDING"
    return "ACCEPTED"
'''

tests = r'''
from __future__ import annotations

import unittest

from tsao_computation.scientific_contracts_v15 import (
    ExecutionReceipt,
    ScientificQuantity,
    acceptance_state,
    convergence_gate,
)


class ScientificContractTests(unittest.TestCase):
    def quantity(self, value: float, unit: str = "Pa", scale: float = 1.0) -> ScientificQuantity:
        return ScientificQuantity(value, unit, "pressure", scale)

    def test_unit_invariant_convergence(self) -> None:
        decision = convergence_gate(
            [self.quantity(0.001, "kPa", 1000.0)],
            [self.quantity(1000.0, "Pa", 1.0)],
            abs_tolerance_si=2.0,
            rel_tolerance=0.0,
            scale_floor_si=1.0,
        )
        self.assertEqual(decision.status, "CONVERGED")

    def test_dimension_mismatch_is_rejected(self) -> None:
        residual = ScientificQuantity(1.0, "Pa", "pressure", 1.0)
        reference = ScientificQuantity(1.0, "K", "temperature", 1.0)
        with self.assertRaises(ValueError):
            convergence_gate([residual], [reference], abs_tolerance_si=1.0, rel_tolerance=0.0, scale_floor_si=1.0)

    def test_software_only_receipt_cannot_be_accepted(self) -> None:
        receipt = ExecutionReceipt("a" * 64, "b" * 64, "c" * 40, "d" * 64, "local", 0, False, True, True, True)
        self.assertEqual(
            acceptance_state(execution=receipt, converged=True, numerically_checked=True, physically_validated=True, independent_approval=True),
            "EXTERNAL_EXECUTION_NOT_VERIFIED",
        )

    def test_state_progression_is_monotone(self) -> None:
        receipt = ExecutionReceipt("a" * 64, "b" * 64, "c" * 40, "d" * 64, "hpc-runner", 0, True, True, True, True)
        self.assertEqual(
            acceptance_state(execution=receipt, converged=True, numerically_checked=True, physically_validated=False, independent_approval=False),
            "NUMERICALLY_CHECKED_PHYSICAL_VALIDATION_PENDING",
        )

    def test_boolean_quantity_is_invalid(self) -> None:
        with self.assertRaises(TypeError):
            ScientificQuantity(True, "Pa", "pressure", 1.0).canonical()


if __name__ == "__main__":
    unittest.main()
'''

workflow = r'''
name: Skill-native portability
on:
  push:
    branches: [main]
  pull_request:
  workflow_dispatch:
permissions:
  contents: read
jobs:
  validate:
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-24.04, windows-2025]
    runs-on: ${{ matrix.os }}
    timeout-minutes: 12
    steps:
      - uses: actions/checkout@11d5960a326750d5838078e36cf38b85af677262
        with:
          persist-credentials: false
      - run: python scripts/validate_skill.py --root . --report artifacts/skill-validation-v15.json
      - run: python -m unittest tests.test_scientific_contracts_v15 -v
'''

svg_en = r'''
<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="900" viewBox="0 0 1600 900"><defs><linearGradient id="g" x2="1" y2="1"><stop stop-color="#08142c"/><stop offset=".55" stop-color="#173557"/><stop offset="1" stop-color="#080f20"/></linearGradient><linearGradient id="c" x2="1" y2="1"><stop stop-color="#1d4568"/><stop offset="1" stop-color="#10263f"/></linearGradient></defs><rect width="1600" height="900" fill="url(#g)"/><g opacity=".16" stroke="#76e2ff"><path d="M0 180H1600M0 360H1600M0 540H1600M0 720H1600"/><path d="M200 0V900M500 0V900M800 0V900M1100 0V900M1400 0V900"/></g><text x="80" y="100" fill="#fff" font-family="Arial" font-size="50" font-weight="700">TsaoSciComputation · Evidence-Bound Scientific Execution</text><text x="85" y="148" fill="#afe9ff" font-family="Arial" font-size="24">Strict datum → bounded process tree → convergence → validation → independent acceptance</text><g transform="translate(80 225)"><rect width="440" height="400" rx="28" fill="url(#c)" stroke="#56d9ff" stroke-width="2"/><text x="35" y="65" fill="#fff" font-family="Arial" font-size="29" font-weight="700">Scientific datum</text><text x="35" y="125" fill="#c8efff" font-family="Arial" font-size="22">value · unit · dimension</text><text x="35" y="165" fill="#c8efff" font-family="Arial" font-size="22">method · conditions · provenance</text><text x="35" y="235" fill="#75f0bd" font-family="Arial" font-size="21">Boolean / NaN / Infinity</text><text x="35" y="272" fill="#75f0bd" font-family="Arial" font-size="21">are invalid, never zero.</text><text x="35" y="335" fill="#fff" font-family="Arial" font-size="24">Strict JSON · exact hashes</text></g><g transform="translate(580 225)"><rect width="440" height="400" rx="28" fill="url(#c)" stroke="#b89fff" stroke-width="2"/><text x="35" y="65" fill="#fff" font-family="Arial" font-size="29" font-weight="700">Convergence gate</text><text x="35" y="135" fill="#e4dcff" font-family="Arial" font-size="23">||r||∞ ≤ atol + rtol max(||y||∞, sfloor)</text><text x="35" y="205" fill="#d9f2ff" font-family="Arial" font-size="21">Canonical units before norms</text><text x="35" y="245" fill="#d9f2ff" font-family="Arial" font-size="21">Bounded logs and process tree</text><text x="35" y="320" fill="#75f0bd" font-family="Arial" font-size="21">Exit 0 ≠ convergence</text><text x="35" y="355" fill="#75f0bd" font-family="Arial" font-size="21">Convergence ≠ acceptance</text></g><g transform="translate(1080 225)"><rect width="440" height="400" rx="28" fill="url(#c)" stroke="#ffbd66" stroke-width="2"/><text x="35" y="65" fill="#fff" font-family="Arial" font-size="29" font-weight="700">Acceptance graph</text><text x="35" y="125" fill="#ffe0ad" font-family="Arial" font-size="20">reported → converged</text><text x="35" y="165" fill="#ffe0ad" font-family="Arial" font-size="20">→ numerically checked</text><text x="35" y="205" fill="#ffe0ad" font-family="Arial" font-size="20">→ physically validated</text><text x="35" y="245" fill="#ffe0ad" font-family="Arial" font-size="20">→ independently accepted</text><text x="35" y="320" fill="#75f0bd" font-family="Arial" font-size="20">scope · nonce · expiry</text><text x="35" y="355" fill="#75f0bd" font-family="Arial" font-size="20">signature · revocation</text></g><rect x="80" y="690" width="1440" height="118" rx="24" fill="#071b34" stroke="#4dcdf2"/><text x="120" y="742" fill="#fff" font-family="Arial" font-size="26" font-weight="700">Truth boundary</text><text x="120" y="785" fill="#c7edff" font-family="Arial" font-size="22">Software contracts are verified; real external solver/HPC execution remains NOT VERIFIED until an exact signed receipt exists.</text></svg>
'''

svg_zh = r'''
<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="900" viewBox="0 0 1600 900"><defs><linearGradient id="g" x2="1" y2="1"><stop stop-color="#08142c"/><stop offset=".55" stop-color="#173557"/><stop offset="1" stop-color="#080f20"/></linearGradient><linearGradient id="c" x2="1" y2="1"><stop stop-color="#1d4568"/><stop offset="1" stop-color="#10263f"/></linearGradient></defs><rect width="1600" height="900" fill="url(#g)"/><g opacity=".16" stroke="#76e2ff"><path d="M0 180H1600M0 360H1600M0 540H1600M0 720H1600"/><path d="M200 0V900M500 0V900M800 0V900M1100 0V900M1400 0V900"/></g><text x="80" y="100" fill="#fff" font-family="Microsoft YaHei,Arial" font-size="50" font-weight="700">TsaoSciComputation · 证据绑定科学计算</text><text x="85" y="148" fill="#afe9ff" font-family="Microsoft YaHei,Arial" font-size="24">严格科学数据 → 受控进程树 → 收敛 → 物理验证 → 独立接受</text><g transform="translate(80 225)"><rect width="440" height="400" rx="28" fill="url(#c)" stroke="#56d9ff" stroke-width="2"/><text x="35" y="65" fill="#fff" font-family="Microsoft YaHei,Arial" font-size="29" font-weight="700">科学数据封装</text><text x="35" y="125" fill="#c8efff" font-family="Microsoft YaHei,Arial" font-size="22">数值 · 单位 · 量纲</text><text x="35" y="165" fill="#c8efff" font-family="Microsoft YaHei,Arial" font-size="22">方法 · 条件 · 来源谱系</text><text x="35" y="235" fill="#75f0bd" font-family="Microsoft YaHei,Arial" font-size="21">布尔值 / NaN / Infinity</text><text x="35" y="272" fill="#75f0bd" font-family="Microsoft YaHei,Arial" font-size="21">属于无效值，绝不默认为零</text><text x="35" y="335" fill="#fff" font-family="Microsoft YaHei,Arial" font-size="24">严格JSON · 精确哈希</text></g><g transform="translate(580 225)"><rect width="440" height="400" rx="28" fill="url(#c)" stroke="#b89fff" stroke-width="2"/><text x="35" y="65" fill="#fff" font-family="Microsoft YaHei,Arial" font-size="29" font-weight="700">收敛判据</text><text x="35" y="135" fill="#e4dcff" font-family="Arial" font-size="23">||r||∞ ≤ atol + rtol max(||y||∞, sfloor)</text><text x="35" y="205" fill="#d9f2ff" font-family="Microsoft YaHei,Arial" font-size="21">求范数前统一规范单位</text><text x="35" y="245" fill="#d9f2ff" font-family="Microsoft YaHei,Arial" font-size="21">限制日志并管理完整进程树</text><text x="35" y="320" fill="#75f0bd" font-family="Microsoft YaHei,Arial" font-size="21">退出码0 ≠ 收敛</text><text x="35" y="355" fill="#75f0bd" font-family="Microsoft YaHei,Arial" font-size="21">收敛 ≠ 科学接受</text></g><g transform="translate(1080 225)"><rect width="440" height="400" rx="28" fill="url(#c)" stroke="#ffbd66" stroke-width="2"/><text x="35" y="65" fill="#fff" font-family="Microsoft YaHei,Arial" font-size="29" font-weight="700">接受状态图</text><text x="35" y="125" fill="#ffe0ad" font-family="Microsoft YaHei,Arial" font-size="20">已报告 → 已收敛</text><text x="35" y="165" fill="#ffe0ad" font-family="Microsoft YaHei,Arial" font-size="20">→ 数值复核</text><text x="35" y="205" fill="#ffe0ad" font-family="Microsoft YaHei,Arial" font-size="20">→ 物理验证</text><text x="35" y="245" fill="#ffe0ad" font-family="Microsoft YaHei,Arial" font-size="20">→ 独立批准</text><text x="35" y="320" fill="#75f0bd" font-family="Microsoft YaHei,Arial" font-size="20">范围 · 随机数 · 有效期</text><text x="35" y="355" fill="#75f0bd" font-family="Microsoft YaHei,Arial" font-size="20">签名 · 撤销状态</text></g><rect x="80" y="690" width="1440" height="118" rx="24" fill="#071b34" stroke="#4dcdf2"/><text x="120" y="742" fill="#fff" font-family="Microsoft YaHei,Arial" font-size="26" font-weight="700">真实性边界</text><text x="120" y="785" fill="#c7edff" font-family="Microsoft YaHei,Arial" font-size="22">软件合同已经验证；在取得精确签名回执前，真实外部求解器/HPC执行仍为“未验证”。</text></svg>
'''

readme_en = r'''
## Skill-native scientific execution

![TsaoSciComputation evidence-bound architecture](assets/diagrams/vision-en.svg)

The canonical Skill is `.agents/skills/tsao-scicomputation/SKILL.md`. It complements the runtime with strict route, evidence, and acceptance boundaries.

The convergence contract is

\[
\|r\|_\infty \le a_{tol}+r_{tol}\max(\|y\|_\infty,s_{floor}),
\]

with dimension-compatible canonical quantities. Exit code, convergence, numerical review, physical validation, and independent acceptance are separate states.

```bash
python scripts/validate_skill.py --root . --report artifacts/skill-validation-v15.json
python -m unittest tests.test_scientific_contracts_v15 -v
```
'''

readme_zh = r'''
## Skill 原生科学计算执行层

![TsaoSciComputation 证据绑定架构](assets/diagrams/vision-zh.svg)

规范 Skill 位于 `.agents/skills/tsao-scicomputation/SKILL.md`，用于为现有运行时补充严格路由、证据与接受边界。

收敛合同为

\[
\|r\|_\infty \le a_{tol}+r_{tol}\max(\|y\|_\infty,s_{floor}),
\]

其中参与比较的量必须先转换为量纲一致的规范单位。退出码、收敛、数值复核、物理验证与独立接受是不同状态。

```bash
python scripts/validate_skill.py --root . --report artifacts/skill-validation-v15.json
python -m unittest tests.test_scientific_contracts_v15 -v
```
'''

write(".agents/skills/tsao-scicomputation/SKILL.md", skill)
write(".agents/skills/tsao-scicomputation/references/definition-of-done.md", dod)
write(".agents/skills/tsao-scicomputation/agents/openai.yaml", openai_yaml)
write(".agents/skills/tsao-scicomputation/evals/evals.json", json.dumps(evals, ensure_ascii=False, indent=2))
write("scripts/validate_skill.py", validator)
write("tsao_computation/scientific_contracts_v15.py", contracts)
write("tests/test_scientific_contracts_v15.py", tests)
write(".github/workflows/skill-native-ci.yml", workflow)
write("assets/diagrams/vision-en.svg", svg_en)
write("assets/diagrams/vision-zh.svg", svg_zh)
merge("README.md", readme_en, "TsaoSciComputation")
zh = "README.zh-CN.md" if (ROOT / "README.zh-CN.md").exists() else "README_CN.md"
merge(zh, readme_zh, "TsaoSciComputation 中文说明")
print(json.dumps({"status": "APPLIED", "version": "15.0.0"}, ensure_ascii=False))
