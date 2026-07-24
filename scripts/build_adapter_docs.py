from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_HEADINGS = (
    "## Description",
    "## Certification",
    "## Capabilities",
    "## Prerequisites",
    "## Environment probe",
    "## Input contract",
    "## Output contract",
    "## Preflight",
    "## Run guidance",
    "## Validation",
    "## Convergence",
    "## Common errors",
    "## Recovery",
    "## Provenance",
    "## Examples",
    "## Scripts",
)


def _load(path: Path) -> list[dict[str, Any]]:
    return list(json.loads(path.read_text(encoding="utf-8")))


def render_adapter(record: dict[str, Any], capabilities: list[dict[str, Any]]) -> str:
    slug = str(record["slug"])
    related = [item for item in capabilities if slug in item.get("recommended_adapters", [])]
    executables = (
        ", ".join(f"`{item}`" for item in record.get("executables", []))
        or "No executable is declared; this adapter is guidance-only until a lawful integration is configured."
    )
    python_modules = (
        ", ".join(f"`{item}`" for item in record.get("python_modules", [])) or "None declared."
    )
    capability_lines = (
        "\n".join(f"- `{item['id']}` `{item['slug']}` — {item['name_en']}" for item in related)
        or "- No capability is hard-wired to this adapter. Select it only after method and environment qualification."
    )
    certification = dict(record["certification"])
    certification_evidence = ", ".join(f"`{item}`" for item in certification["evidence"])
    certification_limitations = "\n".join(f"- {item}" for item in certification["limitations"])
    return f"""# {record["name"]} adapter

## Description

- Slug: `{slug}`
- Workflow: `{record["workflow"]}`
- Maturity: `{record["maturity"]}`
- License posture: `{record["license_kind"]}`
- Live execution verified in this repository: **{"yes" if record["live_execution_verified"] else "no"}**

This adapter provides discovery, input/output contracts, conservative parsing, and bounded recovery guidance. It never bundles executables, licenses, keys, pseudopotentials, basis databases, private data, or copyrighted manuals.

## Certification

- Certification level: `{certification["level"]}`
- Evidence scope: `{certification["evidence_scope"]}`
- Last repository verification: `{certification["last_verified"]}`
- Live solver execution verified: **{"yes" if certification["live_solver_execution"] else "no"}**
- Versioned solver evidence: {", ".join(certification["solver_versions"]) or "None recorded."}
- Repository evidence: {certification_evidence}

{certification_limitations}

`A5` is reserved for a versioned live-solver smoke test with fixture hashes and platform evidence. Levels `A0`–`A4` do not establish installed solver availability.

## Capabilities

{capability_lines}

## Prerequisites

- Candidate executable(s): {executables}
- Required Python module(s): {python_modules}
- The user must provide a lawful installation, license where required, version information, and required scientific data files.
- The calculation contract must identify the observable, method, units, reference state, convergence plan, validation plan, and resource envelope.

## Environment probe

Run `python -m tsao_computation probe` and retain the executable path, required-module outcome, version, environment, license outcome, and probe timestamp. Python-library adapters are unavailable unless every declared module is import-discoverable through the selected interpreter. A detected executable is not proof that a scientifically valid run is possible.

## Input contract

Inputs must include the native model/input deck, method fingerprint, units, conditions, boundary or initial conditions where applicable, parameter provenance, expected outputs, and restart policy. Reject ambiguous defaults and undeclared reference states.

## Output contract

Preserve native stdout/stderr and output files, return code, hashes, parser version, parsed values with units, convergence evidence, warnings, and provenance. Unknown or incomplete output remains unvalidated.

## Preflight

1. Strictly validate the calculation contract.
2. Probe the executable, required modules, and lawful environment.
3. Validate files, syntax, units, model consistency, resources, and output paths.
4. Confirm the convergence and scientific-validation plans before submission.

## Run guidance

Build an argv list without shell construction, use an explicit working directory and bounded timeout, record the environment, and never claim execution when only guidance or input generation occurred.

## Validation

Validate file completeness, exit status, units, conservation or invariants, method-specific physical checks, benchmark/literature/experiment comparison, uncertainty, applicability, and whether the result answers the research question.

## Convergence

Require method-appropriate SCF, geometry, force, residual, mesh, time-step, sampling, queue, or process convergence evidence. Normal exit alone is not convergence, and a single successful run is not a convergence study.

## Common errors

Environment, module, or license missing; malformed input; unavailable data file; invalid structure or units; numerical nonconvergence; insufficient memory; MPI/GPU/queue failure; parser mismatch; or model inapplicability.

## Recovery

Recovery is bounded and auditable. Record the original setting, replacement, reason, attempt count, and possible scientific impact. Escalate repeated, unknown, safety, licensing, or model-validity failures.

## Provenance

Record adapter slug, solver/version, executable path, required-module probe, platform, input/output hashes, method fingerprint, parameters and sources, timestamps, resource use, parser version, validation results, and human approvals.

## Examples

Use the closest workflow example under `examples/`, then replace every system-specific value with contract-backed data. Examples are templates, not evidence that {record["name"]} is installed.

## Scripts

- `python -m tsao_computation probe`
- `python -m tsao_computation validate-contract <contract.json> --strict`
- `python scripts/validate_adapter_metadata.py`
- `python scripts/verify_all.py --profile core`
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    adapters = _load(ROOT / "registry" / "adapters.json")
    capabilities = _load(ROOT / "registry" / "capabilities.json")
    changed: list[str] = []
    for record in adapters:
        path = ROOT / "adapters" / str(record["slug"]) / "ADAPTER.md"
        text = render_adapter(record, capabilities)
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
