---
name: quantum-chemistry
description: Molecular quantum chemistry workflow with explicit contracts, preflight, convergence, physical validation, uncertainty, provenance, and fail-closed acceptance.
---

# Molecular quantum chemistry

## Purpose

Use this workflow for molecular quantum chemistry tasks after the root contract establishes the observable, scale, method, evidence, and resource boundary. Routing keywords include `molecule`, `orca`, `gaussian`, `psi4`, `pyscf`, `frequency`, `orbital`.

## Entry questions

- What observable and decision must this workflow produce?
- Which system, scale, conditions, boundary/initial conditions, and reference state apply?
- What method and fidelity are justified, and what alternatives were rejected?
- What evidence, convergence study, validation target, uncertainty, and compute resources are available?

## Core capabilities

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

## Recommended adapters

`gaussian`, `orca`, `psi4`, `pyscf`

Adapters are candidates, not availability claims. Probe before preparing native inputs.

## Preflight

Require a strict calculation contract; validate structures/files, syntax, units, conditions, parameter provenance, lawful software and data access, resources, output locations, convergence plan, validation plan, restart policy, and human gates.

## State and gates

Expected gate order: `contract` → `preflight` → `completion` → `convergence` → `physical_validation` → `uncertainty` → `acceptance`. Preserve the distinction `completed ≠ parsed ≠ converged ≠ validated ≠ accepted`.

## Failure handling

Classify environment, file, syntax, structure, unit, numerical, resource, MPI/GPU, queue, license, parser, conservation, and model-applicability failures. Retry only with a bounded, recorded scientific rationale.

## Multiscale handoff

When data enters or leaves this workflow, record source, units, temperature/pressure/composition, reference state, transformation, statistical error, model error, applicability, receiving model, and validation status.

## Required outputs

Calculation contract, environment probe, native inputs/outputs or explicit guidance-only status, method fingerprint, convergence evidence, physical checks, uncertainty/applicability statement, provenance manifest, failure/recovery log, and acceptance decision.

## Human approval

Human review is mandatory for high-risk model selection, unavailable or commercial environments, safety/runaway/control conclusions, extrapolation beyond applicability, repeated recovery, and final scientific acceptance where required by the capability record.
