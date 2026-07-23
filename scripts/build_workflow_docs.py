from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_HEADINGS = (
    "## Purpose",
    "## Entry questions",
    "## Core capabilities",
    "## Recommended adapters",
    "## Preflight",
    "## State and gates",
    "## Failure handling",
    "## Multiscale handoff",
    "## Required outputs",
    "## Human approval",
)


def _load(path: Path) -> list[dict[str, Any]]:
    return list(json.loads(path.read_text(encoding="utf-8")))


def render_workflow(record: dict[str, Any], capability_map: dict[str, dict[str, Any]]) -> str:
    capability_lines = "\n".join(
        f"- `{identifier}` `{capability_map[identifier]['slug']}` — {capability_map[identifier]['name_en']}"
        for identifier in record["capability_ids"]
    )
    adapters = ", ".join(f"`{item}`" for item in record.get("recommended_adapters", [])) or "No adapter is preselected; route by method fitness and lawful availability."
    gates = " → ".join(f"`{item}`" for item in record["required_gates"])
    keywords = ", ".join(f"`{item}`" for item in record.get("keywords", []))
    return f"""---
name: {record['slug']}
description: {record['name_en']} workflow with explicit contracts, preflight, convergence, physical validation, uncertainty, provenance, and fail-closed acceptance.
---

# {record['name_en']}

## Purpose

Use this workflow for {record['name_en'].lower()} tasks after the root contract establishes the observable, scale, method, evidence, and resource boundary. Routing keywords include {keywords}.

## Entry questions

- What observable and decision must this workflow produce?
- Which system, scale, conditions, boundary/initial conditions, and reference state apply?
- What method and fidelity are justified, and what alternatives were rejected?
- What evidence, convergence study, validation target, uncertainty, and compute resources are available?

## Core capabilities

{capability_lines}

## Recommended adapters

{adapters}

Adapters are candidates, not availability claims. Probe before preparing native inputs.

## Preflight

Require a strict calculation contract; validate structures/files, syntax, units, conditions, parameter provenance, lawful software and data access, resources, output locations, convergence plan, validation plan, restart policy, and human gates.

## State and gates

Expected gate order: {gates}. Preserve the distinction `completed ≠ parsed ≠ converged ≠ validated ≠ accepted`.

## Failure handling

Classify environment, file, syntax, structure, unit, numerical, resource, MPI/GPU, queue, license, parser, conservation, and model-applicability failures. Retry only with a bounded, recorded scientific rationale.

## Multiscale handoff

When data enters or leaves this workflow, record source, units, temperature/pressure/composition, reference state, transformation, statistical error, model error, applicability, receiving model, and validation status.

## Required outputs

Calculation contract, environment probe, native inputs/outputs or explicit guidance-only status, method fingerprint, convergence evidence, physical checks, uncertainty/applicability statement, provenance manifest, failure/recovery log, and acceptance decision.

## Human approval

Human review is mandatory for high-risk model selection, unavailable or commercial environments, safety/runaway/control conclusions, extrapolation beyond applicability, repeated recovery, and final scientific acceptance where required by the capability record.
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    workflows = _load(ROOT / "registry" / "workflows.json")
    capabilities = _load(ROOT / "registry" / "capabilities.json")
    capability_map = {str(item["id"]): item for item in capabilities}
    changed: list[str] = []
    for record in workflows:
        path = ROOT / "skills" / "workflows" / str(record["slug"]) / "SKILL.md"
        text = render_workflow(record, capability_map)
        if args.check:
            if not path.is_file() or path.read_text(encoding="utf-8") != text:
                changed.append(path.relative_to(ROOT).as_posix())
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
    if changed:
        print(json.dumps({"out_of_date": changed}, indent=2))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
