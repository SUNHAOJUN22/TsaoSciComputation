---
name: extrusion
description: Polymer processing and extrusion workflow with explicit contracts, preflight, convergence, physical validation, uncertainty, provenance, and fail-closed acceptance.
---

# Polymer processing and extrusion

## Purpose

Use this workflow for polymer processing and extrusion tasks after the root contract establishes the observable, scale, method, evidence, and resource boundary. Routing keywords include `extrusion`, `non-newtonian`, `melt`, `die`, `screw`.

## Entry questions

- What observable and decision must this workflow produce?
- Which system, scale, conditions, boundary/initial conditions, and reference state apply?
- What method and fidelity are justified, and what alternatives were rejected?
- What evidence, convergence study, validation target, uncertainty, and compute resources are available?

## Core capabilities

- `TSC-109` `nonnewtonian-rheology` — Non-Newtonian rheology model
- `TSC-110` `viscosity-parameter-fit` — Viscosity-parameter fitting
- `TSC-111` `die-flow-model` — Extrusion-die flow model
- `TSC-112` `screw-channel-model` — Screw-channel flow model
- `TSC-113` `residence-time-distribution` — Processing residence-time distribution
- `TSC-114` `extrudate-quality-map` — Extrudate quality and eccentricity map

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
