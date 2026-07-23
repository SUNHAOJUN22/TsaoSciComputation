---
name: polymer-composite
description: Polymers, fillers, and composites workflow with explicit contracts, preflight, convergence, physical validation, uncertainty, provenance, and fail-closed acceptance.
---

# Polymers, fillers, and composites

## Purpose

Use this workflow for polymers, fillers, and composites tasks after the root contract establishes the observable, scale, method, evidence, and resource boundary. Routing keywords include `polymer`, `composite`, `carbon black`, `percolation`, `morphology`.

## Entry questions

- What observable and decision must this workflow produce?
- Which system, scale, conditions, boundary/initial conditions, and reference state apply?
- What method and fidelity are justified, and what alternatives were rejected?
- What evidence, convergence study, validation target, uncertainty, and compute resources are available?

## Core capabilities

- `TSC-073` `polymer-amorphous-cell` — Polymer amorphous-cell construction
- `TSC-074` `polymer-crystal-interface` — Polymer crystal-interface model
- `TSC-075` `filler-dispersion` — Filler-dispersion analysis
- `TSC-076` `selective-localization` — Filler selective-localization analysis
- `TSC-077` `interfacial-adhesion` — Interfacial adhesion estimation
- `TSC-078` `percolation-network` — Conductive-percolation network model
- `TSC-079` `rheology-structure-link` — Rheology-structure relationship
- `TSC-080` `thermal-aging-model` — Thermo-oxidative aging model
- `TSC-081` `dielectric-property-model` — Dielectric-property model
- `TSC-082` `structure-property-map` — Polymer structure-property map

## Recommended adapters

No adapter is preselected; route by method fitness and lawful availability.

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
