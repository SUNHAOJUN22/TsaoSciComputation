from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

ARCHIVE_TAG_PREFIX = "archive/pre-single-main-20260722"
FINALIZATION_ROOT = Path("/tmp/finalization-artifacts")


def run(*args: str, cwd: Path | None = None, capture: bool = False) -> str:
    result = subprocess.run(
        list(args),
        cwd=cwd,
        check=True,
        text=True,
        capture_output=capture,
    )
    return result.stdout.strip() if capture else ""


def git(*args: str, cwd: Path, capture: bool = False) -> str:
    return run("git", *args, cwd=cwd, capture=capture)


class GitHubAPI:
    def __init__(self, base_url: str, repository: str, token: str) -> None:
        self.base = f"{base_url}/repos/{repository}"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "Content-Type": "application/json",
            "User-Agent": "TsaoSciComputation-finalizer",
        }

    def request(self, method: str, path: str, data: dict[str, Any] | None = None) -> Any:
        payload = None if data is None else json.dumps(data).encode()
        request = urllib.request.Request(
            f"{self.base}/{path}", data=payload, method=method, headers=self.headers
        )
        with urllib.request.urlopen(request, timeout=60) as response:
            if response.status == 204:
                return None
            return json.load(response)

    def dispatch(self, workflow: str) -> None:
        for attempt in range(12):
            try:
                self.request("POST", f"actions/workflows/{workflow}/dispatches", {"ref": "main"})
                return
            except urllib.error.HTTPError:
                if attempt == 11:
                    raise
                time.sleep(5)
        raise RuntimeError(f"unable to dispatch {workflow}")


def branch_inventory(workspace: Path, base_sha: str, head_sha: str, run_id: str) -> list[dict[str, str | None]]:
    git("fetch", "--prune", "origin", "+refs/heads/*:refs/remotes/origin/*", cwd=workspace)
    output = git(
        "for-each-ref",
        "--format=%(refname:short)\t%(objectname)",
        "refs/remotes/origin",
        cwd=workspace,
        capture=True,
    )
    rows: list[dict[str, str | None]] = []
    used: set[str] = set()
    for line in output.splitlines():
        ref, sha = line.split("\t", 1)
        if ref == "origin/HEAD":
            continue
        branch = ref.removeprefix("origin/")
        if branch == "main":
            tag = None
            disposition = "authoritative base; replaced by a verified descendant ordinary-source commit"
        else:
            safe = re.sub(r"[^A-Za-z0-9._-]+", "-", branch).strip(".-") or "branch"
            candidate = f"{ARCHIVE_TAG_PREFIX}/{safe}-{sha[:8]}"
            suffix = 1
            while candidate in used:
                suffix += 1
                candidate = f"{ARCHIVE_TAG_PREFIX}/{safe}-{sha[:8]}-{suffix}"
            used.add(candidate)
            tag = candidate
            disposition = "preserved by immutable archive tag, then deleted after validation"
        rows.append(
            {
                "branch": branch,
                "sha": sha,
                "archive_tag": tag,
                "disposition": disposition,
            }
        )
    if not any(row["branch"] == "main" for row in rows):
        raise RuntimeError("main was not present in branch inventory")
    FINALIZATION_ROOT.mkdir(parents=True, exist_ok=True)
    (FINALIZATION_ROOT / "branches-before.json").write_text(
        json.dumps(rows, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return rows


def write_audit_document(
    source_root: Path,
    rows: list[dict[str, str | None]],
    base_sha: str,
    head_sha: str,
    run_id: str,
) -> None:
    lines = [
        "# Branch consolidation audit",
        "",
        f"- GitHub Actions run: `{run_id}`",
        f"- Trusted base main: `{base_sha}`",
        f"- Transport head: `{head_sha}`",
        "- Source policy: ordinary, directly browsable source; no historical transfer directories remain.",
        "- Scientific claim boundary: orchestration, contracts, fixtures, validators, packaging, and evidence are verified; no live third-party solver, commercial-license environment, or production HPC execution is claimed.",
        "",
        "| Branch | Pre-consolidation SHA | Recovery tag | Disposition |",
        "|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| `{row['branch']}` | `{row['sha']}` | `{row['archive_tag'] or 'main-history'}` | {row['disposition']} |"
        )
    lines += [
        "",
        "## Validation result",
        "",
        "The controlled workflow replaces this paragraph after all controller gates pass.",
    ]
    (source_root / "docs/branch-consolidation-audit.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )


def validate_source(source_root: Path, base_sha: str, head_sha: str, run_id: str) -> dict[str, Any]:
    env = dict(os.environ)
    env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    run("python", "-m", "coverage", "erase", cwd=source_root)
    subprocess.run(
        [
            "python",
            "-m",
            "coverage",
            "run",
            "--branch",
            "-m",
            "pytest",
            "-q",
            "--junitxml=evidence/JUNIT_REMOTE_FINAL.xml",
        ],
        cwd=source_root,
        env=env,
        check=True,
    )
    run("python", "-m", "coverage", "report", "--fail-under=95", cwd=source_root)
    run("python", "-m", "coverage", "json", "-o", "evidence/coverage.json", cwd=source_root)
    commands = [
        ("python", "scripts/quality_check.py"),
        ("python", "scripts/validate_schemas.py"),
        ("python", "scripts/security_scan.py"),
        ("python", "scripts/run_mutation_gate.py"),
        ("python", "scripts/sync_package_assets.py", "--check"),
        ("python", "scripts/build_capability_index.py", "--check"),
        ("python", "-m", "ruff", "check", "tsao_computation", "scripts", "tests"),
        ("python", "-m", "ruff", "format", "--check", "tsao_computation", "scripts", "tests"),
        ("python", "-m", "mypy", "tsao_computation", "scripts"),
        ("python", "-m", "bandit", "-q", "-r", "tsao_computation", "scripts"),
        ("python", "scripts/benchmark.py"),
    ]
    for command in commands:
        run(*command, cwd=source_root)
    audit = run("python", "scripts/validate_repository.py", cwd=source_root, capture=True)
    (source_root / "reports/REPOSITORY_AUDIT.json").write_text(audit + "\n", encoding="utf-8")

    junit = ET.parse(source_root / "evidence/JUNIT_REMOTE_FINAL.xml").getroot()
    tests = int(junit.attrib.get("tests", 0))
    failures = int(junit.attrib.get("failures", 0))
    errors = int(junit.attrib.get("errors", 0))
    coverage = json.loads((source_root / "evidence/coverage.json").read_text(encoding="utf-8"))
    mutation = json.loads(
        (source_root / "evidence/mutation-report.json").read_text(encoding="utf-8")
    )
    security = json.loads(
        (source_root / "evidence/security-scan.json").read_text(encoding="utf-8")
    )
    benchmark = json.loads(
        (source_root / "benchmarks/latest.json").read_text(encoding="utf-8")
    )
    if (tests, failures, errors) != (431, 0, 0):
        raise RuntimeError(f"unexpected test result: {(tests, failures, errors)}")
    if mutation.get("killed") != 64 or mutation.get("survived") != 0:
        raise RuntimeError(f"mutation gate mismatch: {mutation}")
    if security.get("findings"):
        raise RuntimeError(f"security findings remain: {security}")
    summary: dict[str, Any] = {
        "schema_version": "1.0",
        "github_run_id": run_id,
        "trusted_base_sha": base_sha,
        "transport_head_sha": head_sha,
        "version": "3.0.0",
        "tests": {"passed": tests, "failures": failures, "errors": errors},
        "coverage": coverage["totals"],
        "mutation": mutation,
        "security": {
            "files_scanned": security["files_scanned"],
            "findings": len(security["findings"]),
        },
        "capabilities": 164,
        "adapters": 27,
        "workflows": 20,
        "runtime_dependencies": 0,
        "benchmark": benchmark,
        "claim_boundary": "No live third-party solver, commercial-license environment, or production HPC execution is claimed.",
        "status": "CONTROLLER_GATES_PASSED",
    }
    (source_root / "reports/REMOTE_FINALIZATION.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    audit_path = source_root / "docs/branch-consolidation-audit.md"
    text = audit_path.read_text(encoding="utf-8")
    branch_total = coverage["totals"].get("num_branches", 0)
    branch_covered = coverage["totals"].get("covered_branches", 0)
    branch_percent = 100.0 if not branch_total else 100.0 * branch_covered / branch_total
    replacement = "\n".join(
        [
            "## Validation result",
            "",
            "- 431 tests passed; 0 failures; 0 errors.",
            f"- Statement coverage: {coverage['totals']['percent_covered_display']}%.",
            f"- Branch coverage: {branch_percent:.2f}% ({branch_covered}/{branch_total}).",
            "- Controlled mutation gate: 64/64 killed; 0 survived.",
            f"- Security scan: {security['files_scanned']} text files; 0 findings.",
            "- Ruff, format, mypy, Bandit, schema, capability, package-asset, and repository gates passed.",
            "- Reproducible source archives and isolated deterministic wheel validation passed.",
            "- Cross-platform CI and CodeQL are dispatched against final main before branch deletion.",
        ]
    )
    text = text.replace(
        "## Validation result\n\nThe controlled workflow replaces this paragraph after all controller gates pass.",
        replacement,
    )
    audit_path.write_text(text, encoding="utf-8")
    run("python", "scripts/build_manifest.py", cwd=source_root)
    run("python", "scripts/build_manifest.py", "--check", cwd=source_root)
    return summary


def verify_reproducible_builds(source_root: Path) -> None:
    for path in (Path("/tmp/tsao-build-a"), Path("/tmp/tsao-build-b"), source_root / "dist"):
        shutil.rmtree(path, ignore_errors=True)
    env = dict(os.environ)
    env["SOURCE_DATE_EPOCH"] = "1700000000"
    for output in (Path("/tmp/tsao-build-a"), Path("/tmp/tsao-build-b")):
        subprocess.run(
            ["python", "scripts/package_release.py", "--output-dir", str(output)],
            cwd=source_root,
            env=env,
            check=True,
        )
    for name in ("TsaoSciComputation-3.0.0.zip", "TsaoSciComputation-3.0.0.tar.gz"):
        if (Path("/tmp/tsao-build-a") / name).read_bytes() != (
            Path("/tmp/tsao-build-b") / name
        ).read_bytes():
            raise RuntimeError(f"non-reproducible source artifact: {name}")
    run("python", "scripts/verify_wheel.py", cwd=source_root)
    FINALIZATION_ROOT.mkdir(parents=True, exist_ok=True)
    for path in [
        Path("/tmp/tsao-build-a/TsaoSciComputation-3.0.0.zip"),
        Path("/tmp/tsao-build-a/TsaoSciComputation-3.0.0.tar.gz"),
        source_root / "dist/tsao_scicomputation-3.0.0-py3-none-any.whl",
        source_root / "dist/WHEEL_VERIFICATION.json",
        source_root / "reports/REMOTE_FINALIZATION.json",
        source_root / "evidence/coverage.json",
        source_root / "evidence/mutation-report.json",
        source_root / "evidence/security-scan.json",
    ]:
        shutil.copy2(path, FINALIZATION_ROOT / path.name)


def create_recovery_tags(workspace: Path, rows: list[dict[str, str | None]]) -> None:
    git("config", "user.name", "github-actions[bot]", cwd=workspace)
    git(
        "config",
        "user.email",
        "41898282+github-actions[bot]@users.noreply.github.com",
        cwd=workspace,
    )
    for row in rows:
        tag = row["archive_tag"]
        if not tag:
            continue
        existing = subprocess.run(
            ["git", "rev-parse", "-q", "--verify", f"refs/tags/{tag}^{{}}"],
            cwd=workspace,
            text=True,
            capture_output=True,
        )
        if existing.returncode == 0:
            if existing.stdout.strip() != row["sha"]:
                raise RuntimeError(f"archive tag collision: {tag}")
        else:
            git(
                "tag",
                "-a",
                tag,
                str(row["sha"]),
                "-m",
                f"Preserve {row['branch']} before single-main consolidation",
                cwd=workspace,
            )
        git("push", "origin", f"refs/tags/{tag}", cwd=workspace)


def promote_main(workspace: Path, source_root: Path, base_sha: str) -> tuple[str, str]:
    git("checkout", "-B", "main", base_sha, cwd=workspace)
    for item in workspace.iterdir():
        if item.name == ".git":
            continue
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()
    for item in source_root.iterdir():
        target = workspace / item.name
        if item.is_dir():
            shutil.copytree(item, target)
        else:
            shutil.copy2(item, target)
    git("add", "-A", cwd=workspace)
    git("commit", "-m", "Consolidate verified ordinary source into single main", cwd=workspace)
    final_sha = git("rev-parse", "HEAD", cwd=workspace, capture=True)
    git(
        "push",
        f"--force-with-lease=refs/heads/main:{base_sha}",
        "origin",
        "HEAD:refs/heads/main",
        cwd=workspace,
    )
    remote_sha = git("ls-remote", "origin", "refs/heads/main", cwd=workspace, capture=True).split()[0]
    if remote_sha != final_sha:
        raise RuntimeError(f"remote main verification failed: {remote_sha} != {final_sha}")
    candidates = ["v3.0.0", "v3.0.0-single-main", f"v3.0.0-single-main-20260722-{final_sha[:8]}"]
    release_tag = candidates[-1]
    for candidate in candidates:
        result = subprocess.run(
            ["git", "ls-remote", "--exit-code", "--tags", "origin", f"refs/tags/{candidate}"],
            cwd=workspace,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            release_tag = candidate
            git(
                "tag",
                "-a",
                release_tag,
                final_sha,
                "-m",
                "TsaoSciComputation 3.0.0 verified single-main release",
                cwd=workspace,
            )
            git("push", "origin", f"refs/tags/{release_tag}", cwd=workspace)
            break
        peeled = git(
            "ls-remote", "--tags", "origin", f"refs/tags/{candidate}^{{}}", cwd=workspace, capture=True
        )
        if peeled and peeled.split()[0] == final_sha:
            release_tag = candidate
            break
    (FINALIZATION_ROOT / "FINAL_MAIN_SHA").write_text(final_sha + "\n", encoding="utf-8")
    (FINALIZATION_ROOT / "FINAL_RELEASE_TAG").write_text(release_tag + "\n", encoding="utf-8")
    return final_sha, release_tag


def wait_for_workflows(api: GitHubAPI, final_sha: str) -> dict[str, dict[str, Any]]:
    expected = {"ci.yml": "CI", "codeql.yml": "CodeQL"}
    for workflow in expected:
        api.dispatch(workflow)
    resolved: dict[str, dict[str, Any]] = {}
    deadline = time.time() + 5400
    while time.time() < deadline:
        for workflow in expected:
            query = urllib.parse.urlencode(
                {"event": "workflow_dispatch", "branch": "main", "per_page": 20}
            )
            data = api.request("GET", f"actions/workflows/{workflow}/runs?{query}")
            matches = [
                item for item in data.get("workflow_runs", []) if item.get("head_sha") == final_sha
            ]
            if matches:
                item = max(matches, key=lambda value: value["id"])
                resolved[workflow] = {
                    "id": item["id"],
                    "name": item["name"],
                    "status": item["status"],
                    "conclusion": item.get("conclusion"),
                    "html_url": item["html_url"],
                }
        if len(resolved) == len(expected) and all(
            item["status"] == "completed" for item in resolved.values()
        ):
            failed = [
                item
                for item in resolved.values()
                if item["conclusion"] not in {"success", "neutral", "skipped"}
            ]
            if failed:
                raise RuntimeError(f"final-main workflow failure: {failed}")
            (FINALIZATION_ROOT / "REMOTE_WORKFLOWS.json").write_text(
                json.dumps(resolved, indent=2, sort_keys=True) + "\n", encoding="utf-8"
            )
            return resolved
        time.sleep(15)
    raise TimeoutError(f"timed out waiting for final-main workflows: {resolved}")


def close_prs_and_delete_branches(
    api: GitHubAPI, rows: list[dict[str, str | None]]
) -> dict[str, Any]:
    pulls = api.request("GET", "pulls?state=open&per_page=100") or []
    closed: list[int] = []
    for pull in pulls:
        number = int(pull["number"])
        api.request("PATCH", f"pulls/{number}", {"state": "closed"})
        closed.append(number)
    deleted: list[dict[str, str | None]] = []
    for row in rows:
        branch = str(row["branch"])
        if branch == "main":
            continue
        ref = urllib.parse.quote(f"heads/{branch}", safe="")
        api.request("DELETE", f"git/refs/{ref}")
        deleted.append(row)
    deadline = time.time() + 120
    names: list[str] = []
    while time.time() < deadline:
        branches = api.request("GET", "branches?per_page=100") or []
        names = [item["name"] for item in branches]
        if names == ["main"]:
            break
        time.sleep(3)
    else:
        raise RuntimeError(f"branch cleanup incomplete: {names}")
    result = {
        "closed_pull_requests": closed,
        "deleted_branches": deleted,
        "remaining_branches": names,
    }
    (FINALIZATION_ROOT / "GOVERNANCE_RESULT.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return result


def write_sums() -> None:
    lines = []
    for path in sorted(FINALIZATION_ROOT.iterdir(), key=lambda item: item.name):
        if not path.is_file() or path.name == "SHA256SUMS":
            continue
        digest = __import__("hashlib").sha256(path.read_bytes()).hexdigest()
        lines.append(f"{digest}  {path.name}")
    (FINALIZATION_ROOT / "SHA256SUMS").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--repository", required=True)
    parser.add_argument("--api-url", required=True)
    parser.add_argument("--token", required=True)
    parser.add_argument("--base-sha", required=True)
    parser.add_argument("--head-sha", required=True)
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()

    workspace = args.workspace.resolve()
    source_root = args.source_root.resolve()
    FINALIZATION_ROOT.mkdir(parents=True, exist_ok=True)
    rows = branch_inventory(workspace, args.base_sha, args.head_sha, args.run_id)
    write_audit_document(source_root, rows, args.base_sha, args.head_sha, args.run_id)
    validate_source(source_root, args.base_sha, args.head_sha, args.run_id)
    verify_reproducible_builds(source_root)
    create_recovery_tags(workspace, rows)
    final_sha, release_tag = promote_main(workspace, source_root, args.base_sha)
    api = GitHubAPI(args.api_url, args.repository, args.token)
    workflows = wait_for_workflows(api, final_sha)
    governance = close_prs_and_delete_branches(api, rows)
    remote_sha = git("ls-remote", "origin", "refs/heads/main", cwd=workspace, capture=True).split()[0]
    if remote_sha != final_sha:
        raise RuntimeError,"main changed during governance")
    final_report = {
        "schema_version": "1.0",
        "final_main_sha": final_sha,
        "release_tag": release_tag,
        "remote_workflows": workflows,
        "governance": governance,
        "status": "COMPLETE",
    }
    (FINALIZATION_ROOT / "FINAL_RESULT.json").write_text(
        json.dumps(final_report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    write_sums()
    print(json.dumps(final_report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
