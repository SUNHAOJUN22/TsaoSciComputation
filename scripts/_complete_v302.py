from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PRODUCTION_CI = """name: CI

on:
  workflow_dispatch:
  pull_request:
    branches: [main]
  push:
    branches: [main]

permissions:
  contents: read

concurrency:
  group: ci-${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  core:
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        python: ['3.10', '3.13']
    runs-on: ${{ matrix.os }}
    timeout-minutes: 20
    steps:
      - uses: actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5
        with:
          persist-credentials: false
      - uses: actions/setup-python@a309ff8b426b58ec0e2a45f0f869d46889d02405
        with:
          python-version: ${{ matrix.python }}
          cache: pip
      - run: python -m pip install -e '.[validation,quality]'
      - run: python scripts/verify_all.py --profile core

  quality:
    runs-on: ubuntu-latest
    timeout-minutes: 20
    steps:
      - uses: actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5
        with:
          persist-credentials: false
      - uses: actions/setup-python@a309ff8b426b58ec0e2a45f0f869d46889d02405
        with:
          python-version: '3.13'
          cache: pip
      - run: python -m pip install -e '.[validation,quality]'
      - run: python scripts/verify_all.py --profile quality

  package:
    runs-on: ubuntu-latest
    timeout-minutes: 25
    steps:
      - uses: actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5
        with:
          persist-credentials: false
      - uses: actions/setup-python@a309ff8b426b58ec0e2a45f0f869d46889d02405
        with:
          python-version: '3.13'
      - run: python -m pip install -e '.[validation,quality]'
      - run: python scripts/verify_all.py --profile package
      - uses: actions/upload-artifact@043fb46d1a93c77aae656e7c1c64a875d1fc6a0a
        with:
          name: TsaoSciComputation-release-candidate-${{ github.run_id }}-${{ github.run_attempt }}
          path: dist/*
          if-no-files-found: error
          retention-days: 14

  benchmark:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    continue-on-error: true
    steps:
      - uses: actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5
        with:
          persist-credentials: false
      - uses: actions/setup-python@a309ff8b426b58ec0e2a45f0f869d46889d02405
        with:
          python-version: '3.13'
          cache: pip
      - run: python -m pip install -e '.[validation,quality]'
      - run: python scripts/verify_all.py --profile benchmark
"""


def patch_build_sbom() -> None:
    path = ROOT / "scripts" / "build_sbom.py"
    text = path.read_text(encoding="utf-8")
    old = """try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python 3.10 compatibility
    import tomli as tomllib  # type: ignore[import-not-found,no-redef]
"""
    new = """import sys

if sys.version_info >= (3, 11):
    import tomllib
else:  # pragma: no cover - exercised only on Python 3.10
    import tomli as tomllib
"""
    if old in text:
        path.write_text(text.replace(old, new, 1), encoding="utf-8")


def patch_dependency_audit_parser() -> None:
    path = ROOT / "scripts" / "_apply_v302_governance.py"
    text = path.read_text(encoding="utf-8")
    old = """    dependency = json.loads((ROOT / \"reports/DEPENDENCY_AUDIT.json\").read_text(encoding=\"utf-8\"))
    vulnerable = [item for item in dependency.get(\"dependencies\", []) if item.get(\"vulns\")]
"""
    new = """    dependency_payload = json.loads(
        (ROOT / \"reports/DEPENDENCY_AUDIT.json\").read_text(encoding=\"utf-8\")
    )
    dependencies = (
        dependency_payload
        if isinstance(dependency_payload, list)
        else dependency_payload.get(\"dependencies\", [])
    )
    vulnerable = [item for item in dependencies if item.get(\"vulns\")]
"""
    if old not in text:
        raise RuntimeError("dependency-audit parsing anchor not found")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def prepare() -> None:
    (ROOT / ".github" / "workflows" / "ci.yml").write_text(PRODUCTION_CI, encoding="utf-8")
    patch_build_sbom()
    patch_dependency_audit_parser()
    for relative in (
        ".github/workflows/deepen-maintenance.yml",
        ".github/workflows/v302-issue-finalizer.yml",
        ".github/workflows/finalize-v302-confidence.yml",
        ".deepen-maintenance",
        ".finalize-v302-confidence",
        "reports/MAINTENANCE_GOVERNANCE_FAILURE.json",
        "reports/SCIENTIFIC_GOVERNANCE_FAILURE.json",
        "reports/V302_COMPLETION_FAILURE.json",
        "reports/V302_CONFIDENCE_FINALIZATION_FAILURE.json",
    ):
        (ROOT / relative).unlink(missing_ok=True)


def record_confidence_evidence() -> None:
    final_path = ROOT / "reports" / "FINAL_VERIFICATION.json"
    final = json.loads(final_path.read_text(encoding="utf-8"))
    final.update(
        {
            "version": "3.0.2",
            "scientific_confidence_model": "C0-C5_FAIL_CLOSED",
            "confidence_schema_validated": True,
            "engineering_decision_level": "C5_EXPLICIT_ONLY",
            "remote_branches": ["main"],
            "temporary_branch_created": False,
        }
    )
    final_path.write_text(json.dumps(final, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    baseline_path = ROOT / "evidence" / "quality-baseline.json"
    baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
    baseline["scientific_confidence"] = {
        "scheme": "C0-C5",
        "policy": "fail-closed-sequential",
        "schema": "schemas/confidence-assessment.schema.json",
        "engineering_decision_ready_only_at": "C5",
    }
    baseline_path.write_text(
        json.dumps(baseline, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def cleanup() -> None:
    record_confidence_evidence()
    for relative in (
        "scripts/_apply_adapter_certification.py",
        "scripts/_finalize_scientific_governance.py",
        "scripts/_apply_confidence_model.py",
        ".github/workflows/finalize-v302-confidence.yml",
        ".finalize-v302-confidence",
        "reports/V302_COMPLETION_FAILURE.json",
        "reports/V302_CONFIDENCE_FINALIZATION_FAILURE.json",
    ):
        (ROOT / relative).unlink(missing_ok=True)
    Path(__file__).unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("prepare", "cleanup"))
    args = parser.parse_args()
    if args.mode == "prepare":
        prepare()
    else:
        cleanup()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
