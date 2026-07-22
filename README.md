<div align="center">

# TsaoSciComputation

**Evidence-bound, solver-aware scientific-computation orchestration from electrons to processes.**

![version](https://img.shields.io/badge/version-3.0.0-2563eb) ![capabilities](https://img.shields.io/badge/capabilities-164-7c3aed) ![adapters](https://img.shields.io/badge/adapters-27-ea580c) ![workflows](https://img.shields.io/badge/workflows-20-0891b2)

[中文说明](README.zh-CN.md) · [Skill](SKILL.md) · [Capabilities](capability-index/README.md) · [Architecture](docs/architecture.md) · [Security](SECURITY.md)

</div>

## Purpose

TsaoSciComputation converts a research question into a reproducible computation program across molecular quantum chemistry, periodic DFT, reaction paths, molecular dynamics, enhanced sampling, machine-learning potentials, catalysis, polymerization, polymer/composite modeling, FEM, multiphysics, CFD, extrusion, flowsheets, reactors, dynamics/control, digital twins, multiscale handoffs, and HPC execution.

It provides orchestration, contracts, validators, secure execution primitives, conservative parsers, registries, examples, tests, and release tooling. It never pretends that an external solver, license, pseudopotential, basis database, or production cluster is available.

## Trust model

```text
proposed → planned → prepared → submitted → running → completed
         → parsed → converged → validated → accepted
```

A successful process exit proves only completion. Acceptance is fail-closed and requires numerical convergence, physical validation, uncertainty, applicability, evidence lineage, and required expert approvals.

## Architecture

```text
question → calculation contract → workflow router → adapter discovery
         → preflight → bounded execution → conservative parsing
         → convergence → physical validation → UQ/applicability
         → evidence-bound acceptance → multiscale handoff/report
```

The ordinary source tree separates contracts/state, lazy registries/routing, workflows, adapters, execution/security, validation/UQ, provenance, schemas, examples, tests, and deterministic release tooling. Runtime has no mandatory third-party dependency. Package registry assets are mirrored and verified so editable and isolated wheel installations behave identically.

## Current verified baseline

| Gate | Result |
|---|---:|
| Tests | 431 passed, 0 failed |
| Statement coverage | 98.80% |
| Branch coverage | 96.81% |
| Controlled mutation probes | 64/64 killed |
| Repository security scan | 0 findings |
| Capability / adapter / workflow records | 164 / 27 / 20 |
| Runtime dependencies | 0 |
| Source ZIP and tar.gz | byte-identical rebuilds |
| Wheel | byte-identical rebuild and isolated install |

The detailed machine-readable baseline is in `evidence/quality-baseline.json`. No live scientific-solver execution is included in these claims.

## Quick start

```bash
python -m tsao_computation --version
python -m tsao_computation route "Use DFT and MD to study a polymer interface"
python -m tsao_computation probe
python scripts/init_project.py --name demo --question "How does morphology affect conductivity?"
```

## CLI

```bash
python -m tsao_computation route "OpenFOAM non-Newtonian extrusion"
python -m tsao_computation list capabilities
python -m tsao_computation list adapters
python -m tsao_computation list workflows
python -m tsao_computation probe --workers 8
python -m tsao_computation validate-contract examples/organic-dft/contract.json
python -m tsao_computation validate-repository --root .
```

## Solver adapters

Gaussian, ORCA, Psi4, PySCF, Quantum ESPRESSO, CP2K, VASP, ABACUS, GPAW, ASE/pymatgen, GROMACS, OpenMM, LAMMPS, PLUMED, DeePMD-kit, MACE, DOLFINx, MOOSE, Elmer, Kratos, OpenFOAM, SU2, DWSIM, IDAES/Pyomo, OpenModelica, Cantera/RMG, and Aspen.

Adapters discover executables, prepare argv-only command plans, and parse conservatively. `live_execution_verified` remains false until a specific environment/input/output evidence chain is attached. Commercial adapters are lawful local integration guides only.

## Validation and release

```bash
python -m pip install -e '.[validation]'
python scripts/run_tests.py --coverage
python scripts/quality_check.py
python scripts/validate_repository.py
python scripts/validate_schemas.py
python scripts/security_scan.py
python scripts/run_mutation_gate.py
python scripts/sync_package_assets.py --check
python scripts/build_capability_index.py --check
python scripts/build_manifest.py --check
python scripts/benchmark.py
SOURCE_DATE_EPOCH=1700000000 python scripts/package_release.py
python scripts/verify_wheel.py
```

CI runs a Python 3.10/3.13 matrix on Ubuntu, Windows, and macOS, plus deterministic packaging and CodeQL. Third-party GitHub Actions are pinned to verified release commits.

## Performance

The CLI imports only lightweight modules; registries load lazily with bounded caches; environment probing is concurrent and capped. The current local baseline records a 1.951 ms CLI import, 1.333 ms cold load for all 164 capabilities, a 0.0689 ms route decision, and 731.24 MiB/s over a 5 MiB conservative parser fixture. These are orchestration microbenchmarks, not solver benchmarks; see `benchmarks/latest.json` and `docs/performance.md`.

## Known limits

- Repository validation does not substitute for domain-expert review or experimental validation.
- Scientific thresholds and applicability limits remain project-specific and belong in the calculation contract.
- No production third-party solver, commercial license, or real HPC scheduler execution is claimed.
- High-risk reactor, control, digital-twin, safety, runaway, and commercial handoff decisions require human approval.

## Branch policy

`main` is the only long-lived authoritative branch. Short-lived branches must be audited and deleted after validated integration. Historical Base64/Zstandard transfer directories are forbidden in the ordinary source tree. See `docs/branch-policy.md` and `docs/branch-consolidation-audit.md`.
