#!/usr/bin/env bash
set -Eeuo pipefail

ISSUE_NUMBER=23
TSAO_COVERAGE_JSON="${TSAO_COVERAGE_JSON:-/tmp/ultimate-v3-coverage.json}"
export TSAO_COVERAGE_JSON

report_failure() {
  local exit_code=$?
  gh issue comment "$ISSUE_NUMBER" --repo "$GITHUB_REPOSITORY" --body \
    "Ultimate main audit V3 coordinator failed. Workflow run: \`$GITHUB_RUN_ID\`; exit code: \`$exit_code\`. No completion is claimed." || true
  exit "$exit_code"
}
trap report_failure ERR

python scripts/ultimate_audit_v3_prepare.py
python -m ruff check --fix tests/test_readme_visuals.py
python -m ruff format tests/test_readme_visuals.py
python scripts/build_manifest.py
python scripts/build_manifest.py --check
python scripts/validate_repository.py
python -m pytest tests/test_readme_visuals.py -q
git diff --check

git config user.name 'github-actions[bot]'
git config user.email '41898282+github-actions[bot]@users.noreply.github.com'
git add README.md README.zh-CN.md CHANGELOG.md \
  assets/visuals/README.md tests/test_readme_visuals.py \
  reports/CURRENT_MAIN_VERIFICATION.json manifest.json
if git diff --cached --quiet; then
  echo 'Expected README and visual-atlas candidate changes.' >&2
  exit 1
fi
git commit -m 'Expand bilingual scientific visual atlas to 18 diagrams'
git push origin HEAD:refs/heads/main
CANDIDATE_SHA="$(git rev-parse HEAD)"

gh issue comment "$ISSUE_NUMBER" --repo "$GITHUB_REPOSITORY" --body \
  "ULTIMATE_V3_CLEANUP_READY candidate=\`$CANDIDATE_SHA\` coordinator_run=\`$GITHUB_RUN_ID\`. Delete both temporary V3 workflows, four .github/audit-v3 fragments, and the two scripts/ultimate_audit_v3_* temporary scripts from main. The running coordinator will verify the cleaned tree."

TEMP_PATHS=(
  '.github/workflows/bootstrap-ultimate-main-audit-v3.yml'
  '.github/workflows/validate-ultimate-v3-coordinator.yml'
  '.github/audit-v3/part00.ymlfrag'
  '.github/audit-v3/part01.ymlfrag'
  '.github/audit-v3/part02.ymlfrag'
  '.github/audit-v3/part03.ymlfrag'
  'scripts/ultimate_audit_v3_prepare.py'
  'scripts/ultimate_audit_v3_coordinator.sh'
)

CLEANED=false
attempt=1
while test "$attempt" -le 360; do
  git fetch origin main --quiet
  PRESENT=()
  for path in "${TEMP_PATHS[@]}"; do
    if git cat-file -e "origin/main:$path" 2>/dev/null; then
      PRESENT+=("$path")
    fi
  done
  if test "${#PRESENT[@]}" -eq 0; then
    CLEANED=true
    break
  fi
  sleep 5
  attempt=$((attempt + 1))
done
test "$CLEANED" = true

git reset --hard origin/main
git clean -fd
EXPECTED_WORKFLOWS="$(printf '%s\n' ci.yml codeql.yml dependency-audit.yml release.yml)"
ACTUAL_WORKFLOWS="$(find .github/workflows -maxdepth 1 -type f -printf '%f\n' | sort)"
test "$ACTUAL_WORKFLOWS" = "$EXPECTED_WORKFLOWS"

python scripts/build_manifest.py
python scripts/build_manifest.py --check
python scripts/validate_repository.py
git diff --check

python scripts/verify_all.py --profile all | tee "$RUNNER_TEMP/ultimate-all-pass1.log"
python scripts/verify_all.py --profile benchmark | tee "$RUNNER_TEMP/ultimate-benchmark.log"
python scripts/run_tests.py --coverage | tee "$RUNNER_TEMP/ultimate-tests.log"

python -m pip_audit --local --skip-editable --progress-spinner=off \
  --format=json --output "$RUNNER_TEMP/ultimate-dependency-audit.json"
python scripts/security_scan.py > "$RUNNER_TEMP/ultimate-security.json"
git ls-remote --heads origin | tee "$RUNNER_TEMP/ultimate-remote-heads.txt"

python - <<'PY'
from __future__ import annotations

import json
import os
import re
import subprocess
import textwrap
from datetime import datetime, timezone
from pathlib import Path

runner_temp = Path(os.environ["RUNNER_TEMP"])
test_log = (runner_temp / "ultimate-tests.log").read_text(encoding="utf-8")
matches = [int(value) for value in re.findall(r"(\d+) passed", test_log)]
if not matches:
    raise SystemExit("unable to determine passing test count")
passed = max(matches)

coverage = json.loads(Path(os.environ["TSAO_COVERAGE_JSON"]).read_text(encoding="utf-8"))
totals = coverage["totals"]
statement = float(totals["percent_statements_covered"])
branch = float(totals["percent_branches_covered"])

dependency_payload = json.loads(
    (runner_temp / "ultimate-dependency-audit.json").read_text(encoding="utf-8")
)
if isinstance(dependency_payload, list):
    vulnerability_count = len(dependency_payload)
else:
    vulnerability_count = sum(
        len(item.get("vulns", []))
        for item in dependency_payload.get("dependencies", [])
    )
if vulnerability_count:
    raise SystemExit(f"dependency vulnerabilities found: {vulnerability_count}")

security = json.loads(
    (runner_temp / "ultimate-security.json").read_text(encoding="utf-8")
)
findings = security.get("findings", [])
if findings:
    raise SystemExit(f"repository security findings: {findings}")

remote_branches = [
    line.split()[1].removeprefix("refs/heads/")
    for line in (runner_temp / "ultimate-remote-heads.txt")
    .read_text(encoding="utf-8")
    .splitlines()
    if line.strip()
]
if remote_branches != ["main"]:
    raise SystemExit(f"unexpected remote branches: {remote_branches}")

now = datetime.now(timezone.utc).isoformat()
parent_commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
run_id = int(os.environ["GITHUB_RUN_ID"])

evidence_path = Path("reports/CURRENT_MAIN_VERIFICATION.json")
evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
evidence.update(
    {
        "audit_generation": "ultimate-main-audit-v3",
        "canonical_ci_evidence": (
            "The accepted final-commit CI run is recorded in the closing "
            "comment of GitHub Issue #23."
        ),
        "canonical_text_parent_commit": parent_commit,
        "dependency_vulnerabilities": vulnerability_count,
        "deterministic_finalization_run_id": run_id,
        "remote_branches": remote_branches,
        "repository_security_findings": len(findings),
        "schema_version": "1.3",
        "status": "VALIDATED",
        "tests": {"failed": 0, "passed": passed},
        "ultimate_audit_issue": 23,
        "verified_at_utc": now,
        "visual_atlas_version": 3,
    }
)
evidence["counts"]["visual_assets"] = 18
evidence["coverage"] = {
    "branch_percent": branch,
    "statement_percent": statement,
}
evidence_path.write_text(
    json.dumps(evidence, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
    newline="\n",
)

english = f'''<!-- CURRENT_MAIN_VERIFICATION:START -->
Validated on `{now}` by deterministic finalization run `{run_id}`.

| Current-main item | Result |
|---|---:|
| Version | {evidence["version"]} |
| Capabilities / adapters / workflows | 164 / 27 / 20 |
| Tests | {passed} passed, 0 failed |
| Statement / branch coverage | {statement:.2f}% / {branch:.2f}% |
| Windows core | Python 3.10 and 3.13; final result recorded in Issue #23 |
| Controlled mutation probes | 64/64 killed |
| Scientific reference benchmarks | 8/8 passed |
| Repository / dependency findings | 0 / 0 |
| Source archives / Wheel | reproducible / reproducible + isolated install |
| Generated text / Manifest | canonical LF / cross-platform stable |
| Scientific visual assets | 18 self-contained SVGs |
| Remote branches | `main` only |

The final commit is accepted only after canonical Ubuntu/Windows/macOS × Python 3.10/3.13 CI is recorded in [Issue #23](../../issues/23). Machine-readable evidence: [`reports/CURRENT_MAIN_VERIFICATION.json`](reports/CURRENT_MAIN_VERIFICATION.json).
<!-- CURRENT_MAIN_VERIFICATION:END -->'''

chinese = f'''<!-- CURRENT_MAIN_VERIFICATION:START -->
已于 `{now}` 由确定性终验运行 `{run_id}` 完成验证。

| 当前主线项目 | 结果 |
|---|---:|
| 版本 | {evidence["version"]} |
| 能力 / 适配器 / 工作流 | 164 / 27 / 20 |
| 自动测试 | {passed} 通过，0 失败 |
| 语句 / 分支覆盖率 | {statement:.2f}% / {branch:.2f}% |
| Windows core | Python 3.10 与 3.13；最终结果记录于 Issue #23 |
| 受控变异探针 | 64/64 被识别 |
| 科学参考基准 | 8/8 通过 |
| 仓库 / 依赖安全发现 | 0 / 0 |
| 源码包 / Wheel | 可重复 / 可重复并通过隔离安装 |
| 生成文本 / Manifest | 统一 LF / 跨平台稳定 |
| 科研视觉资产 | 18 幅自包含 SVG |
| 远程分支 | 仅 `main` |

最终提交只有在 [Issue #23](../../issues/23) 记录 Ubuntu/Windows/macOS × Python 3.10/3.13 正式 CI 成功后才被接受。机器可读证据：[`reports/CURRENT_MAIN_VERIFICATION.json`](reports/CURRENT_MAIN_VERIFICATION.json)。
<!-- CURRENT_MAIN_VERIFICATION:END -->'''


def replace(path: Path, block: str) -> None:
    text = path.read_text(encoding="utf-8")
    updated, count = re.subn(
        r"<!-- CURRENT_MAIN_VERIFICATION:START -->.*?<!-- CURRENT_MAIN_VERIFICATION:END -->",
        textwrap.dedent(block).strip(),
        text,
        count=1,
        flags=re.DOTALL,
    )
    if count != 1:
        raise SystemExit(f"verification block not found: {path}")
    path.write_text(updated, encoding="utf-8", newline="\n")


replace(Path("README.md"), english)
replace(Path("README.zh-CN.md"), chinese)

report = f'''# Ultimate main audit V3

- Repository: `SUNHAOJUN22/TsaoSciComputation`
- Issue: `#23`
- Branch policy: `main` only; no branch or pull request created
- Version: `{evidence["version"]}`
- Deterministic finalization run: `{run_id}`
- Tests: `{passed} passed, 0 failed`
- Coverage: `{statement:.2f}%` statement / `{branch:.2f}%` branch
- Scientific benchmarks: `8/8`
- Controlled mutation probes: `64/64`
- Capabilities / adapters / workflows: `164 / 27 / 20`
- Scientific visuals: `18` self-contained SVGs
- Dependency vulnerabilities: `0`
- Repository security findings: `0`
- Source archives and Wheel: reproducible; isolated install passed
- Temporary automation in accepted tree: `0`
- Final canonical CI: recorded in the closing comment of Issue `#23`

## Added visual families

Enhanced sampling; reaction kinetics; ML potentials; mesoscale morphology;
HPC execution provenance; uncertainty and sensitivity.

## Scientific boundary

The repository validates orchestration, contracts, deterministic fixtures,
packaging, documentation and evidence. It does not claim live execution of
external solvers, licensed databases, production HPC infrastructure or
automatic authorization of high-risk engineering decisions.
'''
Path("reports/ULTIMATE_MAIN_AUDIT_V3.md").write_text(
    textwrap.dedent(report), encoding="utf-8", newline="\n"
)
PY

python scripts/build_manifest.py
python scripts/build_manifest.py --check
python scripts/validate_repository.py
git diff --check

python scripts/verify_all.py --profile all | tee "$RUNNER_TEMP/ultimate-all-pass2.log"
python -m pytest -q | tee "$RUNNER_TEMP/ultimate-pytest-pass2.log"
python scripts/build_manifest.py
python scripts/build_manifest.py --check
python scripts/validate_repository.py
python -m pytest tests/test_readme_visuals.py -q
ACTUAL_WORKFLOWS="$(find .github/workflows -maxdepth 1 -type f -printf '%f\n' | sort)"
test "$ACTUAL_WORKFLOWS" = "$EXPECTED_WORKFLOWS"
git diff --check

git add -A
if git diff --cached --quiet; then
  echo 'Expected final Manifest and evidence changes.' >&2
  exit 1
fi
git commit -m 'Complete ultimate main audit V3 and 18-visual README atlas'
git push origin HEAD:refs/heads/main
FINAL_SHA="$(git rev-parse HEAD)"

gh workflow run ci.yml --ref main
CI_RUN_ID=''
attempt=1
while test "$attempt" -le 30; do
  sleep 4
  RUNS="$(gh run list --workflow ci.yml --event workflow_dispatch --branch main \
    --limit 30 --json databaseId,headSha,status,conclusion,createdAt,url)"
  CI_RUN_ID="$(RUNS_JSON="$RUNS" FINAL_SHA="$FINAL_SHA" python - <<'PY'
import json
import os

for run in json.loads(os.environ["RUNS_JSON"]):
    if run.get("headSha") == os.environ["FINAL_SHA"]:
        print(run["databaseId"])
        break
PY
  )"
  if test -n "$CI_RUN_ID"; then
    break
  fi
  attempt=$((attempt + 1))
done
test -n "$CI_RUN_ID"

gh issue comment "$ISSUE_NUMBER" --repo "$GITHUB_REPOSITORY" --body \
  "Canonical CI dispatched for final commit \`$FINAL_SHA\`. Run ID: \`$CI_RUN_ID\`."
gh run watch "$CI_RUN_ID" --repo "$GITHUB_REPOSITORY" --exit-status
gh api "repos/$GITHUB_REPOSITORY/actions/runs/$CI_RUN_ID/jobs?per_page=100" \
  > "$RUNNER_TEMP/ultimate-ci-jobs.json"

python - <<'PY'
import json
import os
from pathlib import Path

jobs = json.loads(
    (Path(os.environ["RUNNER_TEMP"]) / "ultimate-ci-jobs.json").read_text(
        encoding="utf-8"
    )
)["jobs"]
failures = [
    (job["name"], job["status"], job["conclusion"])
    for job in jobs
    if job["status"] != "completed" or job["conclusion"] != "success"
]
if failures:
    raise SystemExit(f"canonical CI jobs not successful: {failures}")
names = {job["name"] for job in jobs}
if not {"quality", "package", "benchmark"}.issubset(names):
    raise SystemExit(f"canonical CI job inventory incomplete: {sorted(names)}")
core = [name for name in names if name.startswith("core (")]
if len(core) != 6:
    raise SystemExit(f"expected 6 core matrix jobs, found: {sorted(core)}")
PY

test "$(git ls-remote origin refs/heads/main | awk '{print $1}')" = "$FINAL_SHA"

gh issue comment "$ISSUE_NUMBER" --repo "$GITHUB_REPOSITORY" --body \
  "Ultimate main audit V3 passed. Final commit: \`$FINAL_SHA\`. Canonical CI Run ID: \`$CI_RUN_ID\`. All six Ubuntu/Windows/macOS × Python 3.10/3.13 core jobs plus quality, package and benchmark succeeded. The final tree has 18 self-contained scientific SVGs, zero temporary workflows, no new branch or PR, and only remote branch \`main\`."
gh issue close "$ISSUE_NUMBER" --repo "$GITHUB_REPOSITORY" --reason completed
trap - ERR
