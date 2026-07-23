---
name: finite-element
description: Finite-element analysis workflow with explicit contracts, preflight, convergence, physical validation, uncertainty, provenance, and fail-closed acceptance.
---

# Finite-element analysis

## Purpose

Use this workflow for finite-element analysis tasks after the root contract establishes the observable, scale, method, evidence, and resource boundary. Routing keywords include `fem`, `finite element`, `solid`, `thermal`, `diffusion`.

## Entry questions

- What observable and decision must this workflow produce?
- Which system, scale, conditions, boundary/initial conditions, and reference state apply?
- What method and fidelity are justified, and what alternatives were rejected?
- What evidence, convergence study, validation target, uncertainty, and compute resources are available?

## Core capabilities

- `TSC-083` `governing-equation-contract` — Governing-equation contract
- `TSC-084` `weak-form-verification` — Weak-form verification
- `TSC-085` `mesh-convergence` — Mesh-convergence study
- `TSC-086` `time-step-convergence` — Time-step convergence study
- `TSC-087` `constitutive-model` — Constitutive-model qualification
- `TSC-088` `boundary-condition-audit` — Boundary-condition audit
- `TSC-089` `solver-tolerance-study` — Solver-tolerance study
- `TSC-090` `verification-benchmark` — FEM verification benchmark

## Recommended adapters

`dolfinx`, `elmer`

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
