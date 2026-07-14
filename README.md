<div align="center">

# TsaoSciComputation

**A full-scale scientific-computation Agent Skill with explicit state, deterministic validation, multiscale handoffs, and solver-aware execution.**

[![Version](https://img.shields.io/badge/version-0.1.0-2563eb?style=for-the-badge)](VERSION)
[![License](https://img.shields.io/badge/license-MIT-16a34a?style=for-the-badge)](LICENSE)
[![Capabilities](https://img.shields.io/badge/capabilities-164-7c3aed?style=for-the-badge)](capability-index/README.md)
[![Adapters](https://img.shields.io/badge/adapters-27-ea580c?style=for-the-badge)](#solver-adapters)
[![Workflows](https://img.shields.io/badge/workflows-20-0891b2?style=for-the-badge)](#workflow-map)
[![Scientific state](https://img.shields.io/badge/completed_%E2%89%A0_converged_%E2%89%A0_validated-b91c1c?style=for-the-badge)](#trust-model)

[中文说明](README.zh-CN.md) · [Root skill](SKILL.md) · [Capability index](capability-index/README.md) · [Third-party posture](THIRD_PARTY.md)

</div>

---

## What it is

TsaoSciComputation turns a research question into a traceable computation program across electronic, atomistic, mesoscale, continuum, device, reactor, and process scales. It is not a collection of copied command snippets and it does not pretend that software is installed. It provides a single routing skill, scale-specific workflows, solver adapters, deterministic preflight/validation tools, explicit project state, multiscale data contracts, and reproducible packaging.

The 164-item capability index is grounded in the seven computation/simulation categories of the user-provided 322-item AI-for-Science catalog. The architecture is independently implemented and informed by public computational-agent projects; no third-party code is vendored.

## Trust model

```text
question
  → calculation contract
  → scale / method / solver decision
  → prepared inputs
  → preflight-passed
  → submitted / running / completed
  → parsed
  → numerically-converged
  → physically-validated
  → scientifically-accepted
```

A program that exits successfully has only **completed**. Acceptance requires convergence, physical validation, uncertainty, applicability, evidence, and approvals.

## Architecture

```mermaid
flowchart LR
  Q[Scientific question] --> C[Calculation contract]
  C --> R[Scale & method router]
  R --> W[Scale workflow]
  W --> A[Solver adapter]
  A --> P[Environment + preflight]
  P --> X[Execution / HPC]
  X --> F[Failure classification]
  X --> O[Output collection]
  O --> N[Numerical convergence]
  N --> V[Physical validation]
  V --> U[Uncertainty + applicability]
  U --> S[Scientific acceptance]
  S --> H[Multiscale handoff / report]
  F -->|bounded, logged recovery| A
  F -->|model/license/unknown| G[Human gate]
```

The repository separates:

- **workflows** — scientific lifecycle and gates;
- **adapters** — solver-specific operation;
- **references** — tool-independent scientific guidance;
- **scripts** — deterministic checks with non-zero failure exits;
- **schemas/templates** — machine-readable contracts;
- **capability index** — routing graph;
- **examples/tests** — executable smoke fixtures.

## Workflow map

| Scale / domain | Workflow |
|---|---|
| Problem definition | scale selection |
| Molecular electronic structure | quantum chemistry |
| Crystals, surfaces, defects | periodic DFT |
| TS, IRC, NEB | reaction path |
| Classical/reactive/coarse-grained trajectories | molecular dynamics |
| Free-energy landscapes | enhanced sampling |
| Learned interatomic models | machine-learning potential |
| Catalytic cycles | catalysis |
| Chain growth and distributions | polymerization |
| Polymer/filler/composite morphology | polymer and composite |
| PDE/solid/thermal/diffusion | finite element |
| Coupled fields | multiphysics |
| Flow, heat/mass transfer, multiphase | CFD |
| Non-Newtonian melt processing | extrusion |
| Flowsheets | process simulation |
| CSTR/PFR/batch/RTD | reactor engineering |
| Transients and control | dynamic simulation |
| Estimation and operational decision support | digital twin |
| Parameter transfer | multiscale coupling |
| Slurm/PBS/cloud/local execution | HPC execution |

## Solver adapters

27 adapters are included:

`gaussian, orca, psi4, pyscf, quantum-espresso, cp2k, vasp, abacus, gpaw, ase-pymatgen, gromacs, openmm, lammps, plumed, deepmd, mace, dolfinx, moose, elmer, kratos, openfoam, su2, dwsim, idaes-pyomo, openmodelica, cantera-rmg, aspen`

Availability is always discovered. Commercial adapters are lawful-environment integration guides only; no executable, key, license bypass, pseudopotential, basis database, or copyrighted manual is bundled.

## Quick start

### Validate the repository

```bash
python scripts/run_tests.py --verbose
python scripts/build_capability_index.py --check
python scripts/build_manifest.py --check
```

### Initialize a research project

```bash
python scripts/init_project.py \
  --name pp-shield-multiscale \
  --question "How do carbon-black localization and melt rheology control shielding resistivity and extrusion eccentricity?"
```

### Route scale and inspect the environment

```bash
python scripts/select_scale.py "Use DFT, MD and non-Newtonian CFD for PP/carbon-black extrusion"
python scripts/probe_environment.py --output environment.json
python scripts/select_solver.py --workflow extrusion --environment environment.json
```

No solver is selected as runnable unless the probe detects it.

## Installation

```bash
# Open Agent Skills convention, user scope
python scripts/install.py --agent open-agent-skills --scope user

# Codex project scope
python scripts/install.py --agent codex --scope project

# Claude Code user scope
python scripts/install.py --agent claude --scope user

# Inspect without changing files
python scripts/install.py --agent codex --scope user --dry-run

# Custom target
python scripts/install.py --target /path/to/skills/TsaoSciComputation

# Validate or uninstall
python scripts/install.py --agent codex --scope user --validate
python scripts/install.py --agent codex --scope user --uninstall
```

Supported flags: `--agent`, `--scope`, `--target`, `--force`, `--dry-run`, `--uninstall`, `--validate`.

## Project state

A live project uses:

```text
.tsao-computation/
├── project.yaml
├── tasks/             # DAG nodes
├── methods/           # method fingerprints
├── environments/      # solver and site probes
├── inputs/            # immutable prepared inputs
├── outputs/           # native outputs or links
├── checks/            # convergence/validation records
├── reports/
├── artifacts.jsonl
├── decisions.jsonl
├── events.jsonl
├── failures.jsonl
└── approvals.jsonl
```

## Multiscale handoff contract

Every transfer records source, unit, thermodynamic/compositional conditions, reference state, statistical uncertainty, model uncertainty, applicability, transformation, target model, and validation status. Supported patterns include DFT→rates, DFT→force fields, DFT→ML potentials, MD→diffusion/viscosity/interfaces, coarse-graining→continuum, population balance→flowsheet, CFD→equipment performance, flowsheet→digital twin, and experiments→calibration.

## PP semiconductive cable shielding focus

A dedicated validation map connects PP/elastomer morphology, conductive-carbon-black aggregation and selective localization, interfacial compatibility, electrical percolation, resistivity-temperature stability, rheology, extrusion eccentricity, surface quality, and Cu-contact thermo-oxidative aging across DFT, MD, mesoscale/percolation, CFD, FEM, and process models.

## Examples

Twelve preparation/preflight scenarios are included, matching the acceptance prompt: organic DFT opt/freq; surface adsorption/NEB; protein–nucleic-acid GROMACS 100 ns; polymer–carbon-black LAMMPS; polymerization PBE; PP shielding percolation; OpenFOAM extrusion eccentricity; cable thermo-electro-mechanical FEM; DWSIM/IDAES polymer process; Aspen dynamic twin; DFT→MD→CFD handoff; and failure classification/human approval.

Examples never claim execution unless an explicit execution record exists.

## TsaoSciResearcher handoff

TsaoSciResearcher can create an evidence-backed calculation request containing the question, literature method fingerprint, experimental conditions, target observables, candidate benchmarks, and unresolved assumptions. TsaoSciComputation returns artifact manifests, accepted/rejected claims, convergence and validation reports, uncertainty, and structured multiscale handoffs. A researcher-facing report should cite only accepted claims by default and surface contradictory or unresolved results.

## Known limitations

- This release provides orchestration, contracts, validators, adapters, and preparation fixtures; it does not install or run third-party solvers automatically.
- Solver-specific parsers are intentionally conservative and will expand in later releases.
- Handwritten full YAML requires PyYAML; generated state uses JSON-compatible YAML for standard-library portability.
- Scientific thresholds remain project-specific; templates do not substitute for literature, benchmarks, or expert judgment.
- Commercial API automation depends on a user's lawful local installation, version, COM/API availability, and institutional policy.

## License and provenance

Core code and documentation: MIT. Third-party projects are referenced, not vendored; see [THIRD_PARTY.md](THIRD_PARTY.md). SHA-256 integrity is recorded in `SHA256SUMS`.