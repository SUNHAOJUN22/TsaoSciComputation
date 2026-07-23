---
name: process-simulation
description: Process simulation and flowsheets workflow with explicit contracts, preflight, convergence, physical validation, uncertainty, provenance, and fail-closed acceptance.
---

# Process simulation and flowsheets

## Purpose

Use this workflow for process simulation and flowsheets tasks after the root contract establishes the observable, scale, method, evidence, and resource boundary. Routing keywords include `process`, `flowsheet`, `aspen`, `dwsim`, `idaes`.

## Entry questions

- What observable and decision must this workflow produce?
- Which system, scale, conditions, boundary/initial conditions, and reference state apply?
- What method and fidelity are justified, and what alternatives were rejected?
- What evidence, convergence study, validation target, uncertainty, and compute resources are available?

## Core capabilities

- `TSC-115` `component-property-package` — Component and property-package selection
- `TSC-116` `flowsheet-topology` — Flowsheet topology construction
- `TSC-117` `unit-operation-model` — Unit-operation model qualification
- `TSC-118` `recycle-convergence` — Recycle convergence strategy
- `TSC-119` `process-energy-balance` — Process energy-balance validation
- `TSC-120` `process-mass-balance` — Process mass-balance validation
- `TSC-121` `process-optimization` — Process optimization formulation
- `TSC-122` `process-sensitivity` — Process sensitivity analysis
- `TSC-123` `commercial-simulator-handoff` — Commercial-simulator lawful handoff
- `TSC-124` `flowsheet-uncertainty` — Flowsheet uncertainty analysis

## Recommended adapters

`dwsim`, `idaes-pyomo`, `aspen`

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
