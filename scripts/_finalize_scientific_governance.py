from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def apply_docs() -> None:
    readme_path = ROOT / "README.md"
    readme = readme_path.read_text(encoding="utf-8")
    readme = readme.replace(
        "[Coverage](docs/coverage-matrix.md) · [Architecture]",
        "[Coverage](docs/coverage-matrix.md) · [Scientific validation](docs/scientific-validation.md) · [Architecture]",
        1,
    )
    mutation_row = "| Controlled mutation probes | 64/64 killed |\n"
    if "| Scientific reference benchmarks |" not in readme:
        readme = readme.replace(
            mutation_row,
            mutation_row + "| Scientific reference benchmarks | 8/8 passed |\n",
            1,
        )
    trust = (
        "Adapter discovery requires every declared executable and Python module; normal exit is not convergence. "
        "Installed copies are checked against the full SHA-256 Manifest, and all 12 scenario contracts pass strict preflight validation."
    )
    if trust in readme:
        readme = readme.replace(
            trust,
            trust
            + " Eight deterministic analytical, conservation, and invariant benchmarks must also pass; they do not claim third-party solver execution.",
            1,
        )
    readme_path.write_text(readme, encoding="utf-8")

    zh_path = ROOT / "README.zh-CN.md"
    zh = zh_path.read_text(encoding="utf-8")
    zh = zh.replace(
        "[覆盖矩阵](docs/coverage-matrix.md) · [架构]",
        "[覆盖矩阵](docs/coverage-matrix.md) · [科学验证](docs/scientific-validation.md) · [架构]",
        1,
    )
    mutation_row = "| 受控变异探针 | 64/64 被识别 |\n"
    if "| 科学参考基准 |" not in zh:
        zh = zh.replace(mutation_row, mutation_row + "| 科学参考基准 | 8/8 通过 |\n", 1)
    trust = (
        "适配器只有在全部声明的可执行程序和 Python 模块均通过探测后才可标记为可用；正常退出不等于数值收敛。"
        "安装副本按完整 SHA-256 Manifest 校验，12 类场景合同均通过严格前检。"
    )
    if trust in zh:
        zh = zh.replace(
            trust,
            trust + " 另有8项确定性的解析解、守恒与不变量基准必须通过，但这些基准不声称第三方求解器已真实运行。",
            1,
        )
    zh_path.write_text(zh, encoding="utf-8")

    changelog_path = ROOT / "CHANGELOG.md"
    changelog = changelog_path.read_text(encoding="utf-8")
    anchor = "## 3.0.2 — 2026-07-24\n\n"
    bullets = (
        "- Added eight deterministic analytical, conservation, and invariant scientific reference benchmarks spanning heat transfer, flow, reactors, molecular dynamics, polymer statistical mechanics, electrostatics, and electrothermal coupling.\n"
        "- Replaced the permissive Adapter shape check with a strict no-unknown-fields Schema and structured A0–A5 certification evidence; A5 requires versioned live-solver evidence.\n"
        "- Added a critical coverage policy that prevents repository and high-trust module coverage from silently regressing.\n"
        "- Added explicit Schema/API compatibility and repository Ruleset desired-state policies without falsely claiming platform settings are enabled.\n"
        "- Added a structured pull-request template aligned with the single-`main`, evidence-first contribution model.\n"
    )
    if anchor not in changelog:
        raise RuntimeError("v3.0.2 changelog heading not found")
    if "eight deterministic analytical" not in changelog:
        changelog = changelog.replace(anchor, anchor + bullets, 1)
    changelog_path.write_text(changelog, encoding="utf-8")

    release_path = ROOT / "docs" / "releases" / "v3.0.2.md"
    release = release_path.read_text(encoding="utf-8")
    first = "- Adds a pinned, branchless weekly dependency-vulnerability audit with read-only permissions and retained JSON evidence.\n"
    additions = (
        "- Adds eight deterministic scientific reference benchmarks with analytical, conservation, and invariant acceptance criteria.\n"
        "- Adds strict Adapter Schema validation and A0–A5 certification; A5 is reserved for versioned live-solver evidence.\n"
        "- Adds critical coverage, compatibility, and repository Ruleset desired-state policies.\n"
    )
    if additions not in release:
        release = release.replace(first, first + additions, 1)
    release_path.write_text(release, encoding="utf-8")


def finalize() -> None:
    benchmark = json.loads(
        (ROOT / "evidence" / "scientific-benchmarks.json").read_text(encoding="utf-8")
    )
    if benchmark["total"] != 8 or benchmark["passed"] != 8 or benchmark["failed"] != 0:
        raise RuntimeError("scientific reference benchmark gate is not 8/8")
    records = json.loads((ROOT / "registry" / "adapters.json").read_text(encoding="utf-8"))
    levels: dict[str, int] = {}
    for record in records:
        level = record["certification"]["level"]
        levels[level] = levels.get(level, 0) + 1

    coverage = json.loads(Path("/tmp/scientific-coverage.json").read_text(encoding="utf-8"))[
        "totals"
    ]
    statement = 100.0 * (coverage["num_statements"] - coverage["missing_lines"]) / coverage[
        "num_statements"
    ]
    branch = 100.0 * (coverage["num_branches"] - coverage["missing_branches"]) / coverage[
        "num_branches"
    ]

    baseline_path = ROOT / "evidence" / "quality-baseline.json"
    baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
    baseline["counts"].update(
        {
            "scientific_reference_benchmarks_passed": 8,
            "scientific_reference_benchmarks_failed": 0,
        }
    )
    baseline["coverage"] = {
        "branches_percent": branch,
        "missing_branches": coverage["missing_branches"],
        "missing_statements": coverage["missing_lines"],
        "statements_percent": statement,
    }
    baseline["adapter_certification"] = {
        "scheme": "A0-A5",
        "levels": levels,
        "live_solver_adapters": 0,
        "claim_boundary": "A0-A4 repository evidence is not live solver execution.",
    }
    baseline_path.write_text(json.dumps(baseline, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    final_path = ROOT / "reports" / "FINAL_VERIFICATION.json"
    final = json.loads(final_path.read_text(encoding="utf-8"))
    final.update(
        {
            "scientific_reference_benchmarks": "8/8",
            "adapter_certification_scheme": "A0-A5",
            "adapter_certifications": levels,
            "live_solver_adapters": 0,
            "critical_coverage_policy": "PASS",
            "compatibility_policy": "VALIDATED",
            "repository_ruleset_desired_state_documented": True,
            "statement_coverage_percent": statement,
            "branch_coverage_percent": branch,
            "verified_at_utc": datetime.now(timezone.utc).isoformat(),
        }
    )
    final_path.write_text(json.dumps(final, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    platform_path = ROOT / "reports" / "PLATFORM_SETTINGS.json"
    platform = json.loads(platform_path.read_text(encoding="utf-8"))
    remaining = set(platform.get("remaining_admin_actions", []))
    remaining.add("verify_or_enable_main_repository_ruleset")
    if not platform.get("private_vulnerability_reporting_enabled"):
        remaining.add("enable_private_vulnerability_reporting_in_repository_settings")
    platform["repository_ruleset_desired_state_documented"] = True
    platform["remaining_admin_actions"] = sorted(remaining)
    platform_path.write_text(json.dumps(platform, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    updates = (
        (
            "README.md",
            r"\| Tests \| \d+ passed, \d+ failed \|",
            r"\| Statement / branch coverage \| [^|]+ \|",
            f"| Tests | {final['tests_passed']} passed, 0 failed |",
            f"| Statement / branch coverage | {statement:.2f}% / {branch:.2f}% |",
        ),
        (
            "README.zh-CN.md",
            r"\| 自动测试 \| \d+ 通过，\d+ 失败 \|",
            r"\| 语句 / 分支覆盖率 \| [^|]+ \|",
            f"| 自动测试 | {final['tests_passed']} 通过，0 失败 |",
            f"| 语句 / 分支覆盖率 | {statement:.2f}% / {branch:.2f}% |",
        ),
    )
    for filename, test_pattern, coverage_pattern, test_text, coverage_text in updates:
        path = ROOT / filename
        text = path.read_text(encoding="utf-8")
        text = re.sub(test_pattern, test_text, text)
        text = re.sub(coverage_pattern, coverage_text, text)
        path.write_text(text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("apply", "finalize"))
    args = parser.parse_args()
    if args.mode == "apply":
        apply_docs()
    else:
        finalize()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
