from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
VERIFIED_DATE = "2026-07-24"


def certification(record: dict[str, Any]) -> dict[str, Any]:
    level = str(record["maturity"])
    evidence_by_level = {
        "A0": ["method-planning-boundary"],
        "A1": ["metadata-schema", "environment-probe-contract"],
        "A2": ["metadata-schema", "environment-probe-contract", "input-contract"],
        "A3": [
            "metadata-schema",
            "environment-probe-contract",
            "input-contract",
            "argv-command-plan",
            "conservative-parser-policy",
        ],
        "A4": [
            "metadata-schema",
            "environment-probe-contract",
            "input-contract",
            "argv-command-plan",
            "conservative-parser-policy",
            "deterministic-success-and-failure-fixtures",
            "numerical-and-physical-validation-gates",
        ],
        "A5": [
            "metadata-schema",
            "environment-probe-contract",
            "input-contract",
            "argv-command-plan",
            "conservative-parser-policy",
            "deterministic-success-and-failure-fixtures",
            "numerical-and-physical-validation-gates",
            "versioned-live-solver-smoke-test",
        ],
    }
    return {
        "level": level,
        "evidence_scope": "repository-fixture-only",
        "evidence": evidence_by_level[level],
        "fixture_hashes": [],
        "last_verified": VERIFIED_DATE,
        "limitations": [
            "No live third-party solver execution is claimed by this certification.",
            "Adapter presence does not establish solver availability or model applicability.",
        ],
        "live_solver_execution": bool(record["live_execution_verified"]),
        "solver_versions": [],
        "verified_platforms": ["repository-ci-contract-fixtures"],
    }


def main() -> int:
    registry = ROOT / "registry" / "adapters.json"
    records = json.loads(registry.read_text(encoding="utf-8"))
    for record in records:
        record["certification"] = certification(record)
        path = ROOT / "adapters" / record["slug"] / "adapter.yaml"
        path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    rendered = json.dumps(records, indent=2, sort_keys=True) + "\n"
    registry.write_text(rendered, encoding="utf-8")
    packaged = ROOT / "tsao_computation" / "data" / "registry" / "adapters.json"
    packaged.write_text(rendered, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
