---
name: TsaoSciComputation
description: Route full-scale scientific-computation requests through explicit contracts, solver-aware preparation, convergence, physical validation, uncertainty, provenance, and fail-closed scientific acceptance.
---

# TsaoSciComputation

Use this root skill as the single entrypoint for scientific-computation work spanning electronic, atomistic, mesoscale, continuum, reactor, process, control, and digital-twin scales. Load only the workflow and adapter documents needed for the current task.

## Intake questions

Before selecting software or writing an input file, answer and record:

1. Is the user asking to predict, explain, compare, calibrate, or optimize?
2. What observable or decision quantity must be produced?
3. What spatial and temporal scales control that quantity?
4. Is electronic structure required?
5. Is atomic motion, conformational sampling, or free-energy sampling required?
6. Is chemical or polymerization kinetics required?
7. Is a continuum field model required?
8. Is equipment, reactor, flowsheet, control, or digital-twin scale required?
9. Is an explicit multiscale handoff required?
10. What experimental, literature, or upstream-model evidence already exists?
11. How will numerical, physical, and scientific validity be demonstrated?
12. What compute resources, licensed environments, cost, and time limits are available?

If any answer needed for method selection is unknown, stop at `proposed` and request or derive a bounded calculation contract. Do not fabricate solver inputs from a vague prompt.

## Calculation contract

Before `prepared`, the contract must explicitly contain or justify as not applicable:

- scientific question and intended operation;
- target observables;
- model object and system definition;
- scales and methods;
- assumptions;
- thermodynamic/composition conditions;
- boundary and initial conditions;
- parameter sources and reference states;
- convergence plan;
- validation plan and acceptance criteria;
- uncertainty sources and applicability domain;
- compute resources and lawful software/license constraints;
- expected artifacts;
- human-approval nodes.

Use `python -m tsao_computation validate-contract <file> --strict` before preflight. The non-strict mode exists only for reading legacy contracts.

## Routing and progressive loading

1. Route by observable, scale, method fitness, fidelity, evidence, and lawful environment.
2. Load one or more files under `skills/workflows/` only after the contract identifies the needed domain.
3. Probe adapters before use. An adapter record never proves that a solver, database, license, pseudopotential, basis set, container, queue, GPU, or cloud account is available.
4. Generate argv and input guidance only after preflight passes.
5. Use structured handoffs for every scale transition, including units, conditions, reference states, transformations, statistical error, model error, applicability, receiver, and validation status.

## State and acceptance policy

The scientific state chain is:

`proposed → specified → prepared → preflight-passed → submitted → running → completed → parsed → numerically-converged → physically-validated → scientifically-accepted`

Failure terminals include `failed`, `rejected`, and `superseded`.

Never equate input generation with execution, normal program exit with convergence, one run with a convergence study, model output with experimental fact, or an unavailable solver with completed work. `completed ≠ parsed ≠ converged ≠ validated ≠ accepted`.

## Required gates

Every accepted result must pass the applicable gates for file integrity, exit status, numerical convergence, discretization/sampling convergence, units, conservation, boundary/initial conditions, physical plausibility, benchmark/literature/experiment comparison, uncertainty, applicability, provenance, and the original research question.

Automatic recovery is bounded. Record the original parameter, new parameter, reason, attempt count, and possible scientific effect. Escalate unknown, licensing, safety, runaway, control, commercial-handoff, or repeated failures to a human gate.
