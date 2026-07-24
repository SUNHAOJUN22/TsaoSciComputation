# Gaussian adapter

## Description

- Slug: `gaussian`
- Workflow: `quantum-chemistry`
- Maturity: `A3`
- License posture: `commercial`
- Live execution verified in this repository: **no**

This adapter provides discovery, input/output contracts, conservative parsing, and bounded recovery guidance. It never bundles executables, licenses, keys, pseudopotentials, basis databases, private data, or copyrighted manuals.

## Certification

- Certification level: `A3`
- Evidence scope: `repository-fixture-only`
- Last repository verification: `2026-07-24`
- Live solver execution verified: **no**
- Versioned solver evidence: None recorded.
- Repository evidence: `metadata-schema`, `environment-probe-contract`, `input-contract`, `argv-command-plan`, `conservative-parser-policy`

- No live third-party solver execution is claimed by this certification.
- Adapter presence does not establish solver availability or model applicability.

`A5` is reserved for a versioned live-solver smoke test with fixture hashes and platform evidence. Levels `A0`–`A4` do not establish installed solver availability.

## Capabilities

- `TSC-005` `molecular-geometry-optimization` — Molecular geometry optimization
- `TSC-006` `harmonic-frequency-analysis` — Harmonic frequency analysis
- `TSC-007` `single-point-energy` — Single-point electronic energy
- `TSC-008` `conformer-search-plan` — Conformer-search planning
- `TSC-009` `transition-state-search` — Transition-state search
- `TSC-010` `intrinsic-reaction-coordinate` — Intrinsic reaction-coordinate analysis
- `TSC-011` `solvation-model-selection` — Implicit-solvation model selection
- `TSC-012` `charge-population-analysis` — Atomic-charge and population analysis
- `TSC-013` `frontier-orbital-analysis` — Frontier-orbital analysis
- `TSC-014` `excited-state-screening` — Excited-state method screening
- `TSC-015` `thermochemistry-correction` — Thermochemistry correction
- `TSC-016` `basis-method-convergence` — Basis and method convergence study

## Prerequisites

- Candidate executable(s): `g16`, `g09`
- Required Python module(s): None declared.
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

Use the closest workflow example under `examples/`, then replace every system-specific value with contract-backed data. Examples are templates, not evidence that Gaussian is installed.

## Scripts

- `python -m tsao_computation probe`
- `python -m tsao_computation validate-contract <contract.json> --strict`
- `python scripts/validate_adapter_metadata.py`
- `python scripts/verify_all.py --profile core`
