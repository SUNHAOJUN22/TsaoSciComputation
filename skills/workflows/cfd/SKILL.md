---
name: cfd
description: Computational fluid dynamics workflow with explicit contracts, preflight, convergence, physical validation, uncertainty, provenance, and fail-closed acceptance.
---

# Computational fluid dynamics

## Purpose

Use this workflow for computational fluid dynamics tasks after the root contract establishes the observable, scale, method, evidence, and resource boundary. Routing keywords include `cfd`, `openfoam`, `su2`, `flow`, `turbulence`, `multiphase`.

## Entry questions

- What observable and decision must this workflow produce?
- Which system, scale, conditions, boundary/initial conditions, and reference state apply?
- What method and fidelity are justified, and what alternatives were rejected?
- What evidence, convergence study, validation target, uncertainty, and compute resources are available?

## Core capabilities

- `TSC-099` `flow-domain-definition` — Flow-domain definition
- `TSC-100` `mesh-quality-audit` — CFD mesh-quality audit
- `TSC-101` `laminar-flow-model` — Laminar-flow model
- `TSC-102` `turbulence-model-selection` — Turbulence-model selection
- `TSC-103` `multiphase-model-selection` — Multiphase-model selection
- `TSC-104` `heat-transfer-model` — Conjugate heat-transfer model
- `TSC-105` `species-transport` — Species-transport model
- `TSC-106` `pressure-velocity-coupling` — Pressure-velocity coupling
- `TSC-107` `cfd-convergence` — CFD convergence assessment
- `TSC-108` `mass-balance-validation` — CFD mass-balance validation

## Recommended adapters

`openfoam`, `su2`

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
