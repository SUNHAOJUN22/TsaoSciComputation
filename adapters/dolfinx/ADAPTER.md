# DOLFINx adapter

## Description

- Slug: `dolfinx`
- Workflow: `finite-element`
- Maturity: `A4`
- License posture: `open-source`
- Live execution verified in this repository: **no**

This adapter provides discovery, input/output contracts, conservative parsing, and bounded recovery guidance. It never bundles executables, licenses, keys, pseudopotentials, basis databases, private data, or copyrighted manuals.

## Capabilities

- `TSC-083` `governing-equation-contract` — Governing-equation contract
- `TSC-084` `weak-form-verification` — Weak-form verification
- `TSC-085` `mesh-convergence` — Mesh-convergence study
- `TSC-086` `time-step-convergence` — Time-step convergence study
- `TSC-087` `constitutive-model` — Constitutive-model qualification
- `TSC-088` `boundary-condition-audit` — Boundary-condition audit
- `TSC-089` `solver-tolerance-study` — Solver-tolerance study
- `TSC-090` `verification-benchmark` — FEM verification benchmark

## Prerequisites

- Candidate executable(s): `python`
- Required Python module(s): `dolfinx`
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

Use the closest workflow example under `examples/`, then replace every system-specific value with contract-backed data. Examples are templates, not evidence that DOLFINx is installed.

## Scripts

- `python -m tsao_computation probe`
- `python -m tsao_computation validate-contract <contract.json> --strict`
- `python scripts/validate_adapter_metadata.py`
- `python scripts/verify_all.py --profile core`
