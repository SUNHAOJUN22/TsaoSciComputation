---
name: periodic-dft
description: Periodic DFT and materials workflow with explicit contracts, preflight, convergence, physical validation, uncertainty, provenance, and fail-closed acceptance.
---

# Periodic DFT and materials

## Purpose

Use this workflow for periodic dft and materials tasks after the root contract establishes the observable, scale, method, evidence, and resource boundary. Routing keywords include `periodic`, `crystal`, `dft`, `vasp`, `qe`, `cp2k`, `surface`, `defect`.

## Entry questions

- What observable and decision must this workflow produce?
- Which system, scale, conditions, boundary/initial conditions, and reference state apply?
- What method and fidelity are justified, and what alternatives were rejected?
- What evidence, convergence study, validation target, uncertainty, and compute resources are available?

## Core capabilities

- `TSC-017` `crystal-structure-relaxation` — Crystal-structure relaxation
- `TSC-018` `equation-of-state` — Equation-of-state calculation
- `TSC-019` `kpoint-convergence` — K-point convergence study
- `TSC-020` `cutoff-convergence` — Plane-wave cutoff convergence
- `TSC-021` `band-structure` — Electronic band-structure analysis
- `TSC-022` `density-of-states` — Density-of-states analysis
- `TSC-023` `surface-energy` — Surface-energy calculation
- `TSC-024` `adsorption-energy` — Adsorption-energy calculation
- `TSC-025` `point-defect-formation` — Point-defect formation energy
- `TSC-026` `phonon-stability` — Phonon and dynamical-stability analysis
- `TSC-027` `ab-initio-molecular-dynamics` — Ab-initio molecular dynamics planning
- `TSC-028` `periodic-charge-correction` — Periodic charged-system correction

## Recommended adapters

`quantum-espresso`, `cp2k`, `vasp`, `abacus`, `gpaw`, `ase-pymatgen`

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
