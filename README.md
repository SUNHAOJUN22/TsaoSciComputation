<div align="center">

<img src="assets/visuals/hero-multiscale.svg" alt="TsaoSciComputation electron-to-process architecture" width="100%">

# TsaoSciComputation

**Evidence-bound scientific-computation orchestration from electrons to industrial processes.**

![version](https://img.shields.io/badge/version-3.0.2-2563eb) ![capabilities](https://img.shields.io/badge/capabilities-164-7c3aed) ![adapters](https://img.shields.io/badge/adapters-27-ea580c) ![workflows](https://img.shields.io/badge/workflows-20-0891b2)

[中文说明](README.zh-CN.md) · [Root Skill](SKILL.md) · [Capabilities](capability-index/README.md) · [Coverage](docs/coverage-matrix.md) · [Scientific validation](docs/scientific-validation.md) · [Confidence](docs/scientific-confidence.md) · [Architecture](docs/architecture.md) · [Releases](docs/release.md) · [Security](SECURITY.md)

</div>

## What it is

TsaoSciComputation converts a scientific question into a traceable calculation program with explicit contracts, method and scale routing, environment preflight, bounded execution, conservative parsing, numerical and physical validation, uncertainty, applicability, provenance, and acceptance gates.

```text
question → contract → route → preflight → execute → parse
         → converge → validate → quantify uncertainty → accept or reject
```

It is an **orchestration and governance layer**. It does not bundle, redistribute, unlock, or impersonate external solvers, licenses, databases, basis sets, pseudopotentials, private data, or production HPC infrastructure.

## Architecture at a glance

<table>
<tr>
<td width="50%"><img src="assets/visuals/agent-orchestration.svg" alt="Governed AI scientific agent orchestration" width="100%"></td>
<td width="50%"><img src="assets/visuals/capability-landscape.svg" alt="Scientific capability and workflow landscape" width="100%"></td>
</tr>
<tr>
<td align="center"><b>Governed scientific agent</b><br>Planning, routing, execution, evidence and review remain separate.</td>
<td align="center"><b>Contract-based capability system</b><br>164 differentiated capabilities are organized through 20 workflows.</td>
</tr>
</table>

The core design is fail-closed:

- a declared adapter is not automatically available;
- a normal process exit is not automatically parsed or converged;
- a converged result is not automatically physically valid;
- a validated observable is not automatically applicable outside its domain;
- a high-risk engineering conclusion is not automatically authorized.

## Multiscale scientific workflows

<table>
<tr>
<td width="50%"><img src="assets/visuals/quantum-to-md.svg" alt="Quantum chemistry to molecular dynamics workflow" width="100%"></td>
<td width="50%"><img src="assets/visuals/polymer-process.svg" alt="Polymer structure to process simulation workflow" width="100%"></td>
</tr>
<tr>
<td align="center"><b>Quantum → molecular</b><br>Electronic structure, parameterization, ensembles and validated observables.</td>
<td align="center"><b>Polymer → process</b><br>Sequence, morphology, continuum fields and process-system handoffs.</td>
</tr>
</table>

Representative scope includes electronic structure, quantum chemistry, atomistic and enhanced-sampling workflows, machine-learned potentials, mesoscale and continuum models, reaction engineering, CFD, multiphysics, process simulation, optimization, uncertainty, reproducibility and multiscale handoff.

## Domain capability views

<table>
<tr>
<td width="50%"><img src="assets/visuals/electronic-structure-landscape.svg" alt="DFT electronic structure and energy landscape" width="100%"></td>
<td width="50%"><img src="assets/visuals/continuum-multiphysics.svg" alt="CFD FEM and continuum multiphysics workflow" width="100%"></td>
</tr>
<tr>
<td align="center"><b>Electronic structure &amp; DFT</b><br>Geometry, density, self-consistency, energy, forces and observable-level acceptance.</td>
<td align="center"><b>CFD, FEM &amp; multiphysics</b><br>Mesh quality, conservation, coupled fields, stability and discretization evidence.</td>
</tr>
</table>

<img src="assets/visuals/process-optimization-uq.svg" alt="Process optimization uncertainty quantification and reviewed decision workflow" width="100%">

The process layer separates flowsheet construction, model calibration, uncertainty propagation, sensitivity, constrained search and human authorization. A numerical optimum is rejected when feasibility, uncertainty, safety, applicability or review evidence is incomplete.

## Solver-aware ecosystem

<img src="assets/visuals/engine-ecosystem.svg" alt="Scientific solver and adapter ecosystem" width="100%">

The repository contains 27 conservative adapter definitions. Of 32 engines in the source shortlist, 21 are represented directly or through combined adapters; 11 remain explicit non-standalone limits. Adapter discovery requires every declared executable and Python module. `live_execution_verified` remains false unless independent live-solver evidence exists.

See the [coverage matrix](docs/coverage-matrix.md), [adapter certification](docs/adapter-certification.md), and individual `adapters/*/ADAPTER.md` records for exact boundaries.

## Evidence, confidence and reproducibility

<table>
<tr>
<td width="50%"><img src="assets/visuals/evidence-loop.svg" alt="Evidence-bound scientific validation loop" width="100%"></td>
<td width="50%"><img src="assets/visuals/confidence-ladder.svg" alt="C0 to C5 scientific confidence ladder" width="100%"></td>
</tr>
<tr>
<td align="center"><b>Acceptance loop</b><br>Contract, execution, convergence, physics, uncertainty and domain checks.</td>
<td align="center"><b>C0–C5 confidence</b><br>Stronger claims require stronger evidence; C5 is explicit-only.</td>
</tr>
</table>

<img src="assets/visuals/digital-thread.svg" alt="Reproducible scientific digital thread" width="100%">

Every governed handoff can retain inputs, units, methods, versions, paths, seeds, tolerances, raw and parsed artifacts, validation results, hashes and release evidence. Reproducibility is tested through independent source-archive and Wheel rebuilds rather than inferred from documentation.

## Quick start

```bash
git clone https://github.com/SUNHAOJUN22/TsaoSciComputation.git
cd TsaoSciComputation
python -m pip install -e .

python -m tsao_computation route "Use DFT and MD to study a polymer interface"
python scripts/init_project.py --root demo --name demo \
  --question "How does morphology affect conductivity?"
python -m tsao_computation validate-contract \
  templates/calculation-contract.json --strict
python -m tsao_computation probe
```

External solvers are optional and must be installed, licensed and validated separately. Missing executables, malformed contracts, unsafe paths, illegal state transitions or incomplete evidence are rejected rather than silently accepted.

## Verification

```bash
python -m pip install -e '.[validation,quality]'
python scripts/verify_all.py --profile all
python scripts/verify_all.py --profile benchmark
```

`all` runs the deterministic release gates: quality and security checks, tests and branch coverage, scientific reference benchmarks, critical coverage policy, version and registry synchronization, repository and Schema validation, adapter and documentation validation, controlled mutation probes, reproducible source and Wheel builds, isolated installation, SPDX and CycloneDX SBOM generation, checksums and release manifests. `benchmark` is environment-dependent telemetry and remains separate from release acceptance.

### Current `main` verification

<!-- CURRENT_MAIN_VERIFICATION:START -->
Validated on `2026-07-25T19:56:18.624713+00:00` by deterministic finalization run `30172561968`.

| Current-main item | Result |
|---|---:|
| Version | 3.0.2 |
| Capabilities / adapters / workflows | 164 / 27 / 20 |
| Tests | 559 passed, 0 failed |
| Statement / branch coverage | 97.32% / 93.67% |
| Windows core | Python 3.10 and 3.13 passed |
| Controlled mutation probes | 64/64 killed |
| Scientific reference benchmarks | 8/8 passed |
| Repository / dependency findings | 0 / 0 |
| Source archives / Wheel | reproducible / reproducible + isolated install |
| Generated text / Manifest | canonical LF / cross-platform stable |
| Scientific visual assets | 12 self-contained SVGs |
| Remote branches | `main` only |

The final commit is accepted only after the canonical Ubuntu/Windows/macOS × Python 3.10/3.13 CI result is recorded in [Issue #22](../../issues/22). Machine-readable evidence: [`reports/CURRENT_MAIN_VERIFICATION.json`](reports/CURRENT_MAIN_VERIFICATION.json).
<!-- CURRENT_MAIN_VERIFICATION:END -->

### v3.0.2 verified release baseline

| Item | Machine-recorded result |
|---|---:|
| Version | 3.0.2 |
| Capabilities / adapters / workflows | 164 / 27 / 20 |
| Mandatory runtime dependencies | 0 |
| Tests | 553 passed, 0 failed |
| Statement / branch coverage | 97.27% / 93.48% |
| Controlled mutation probes | 64/64 killed |
| Scientific reference benchmarks | 8/8 passed |
| Repository / dependency findings | 0 / 0 |
| Source archives | byte-identical ZIP and tar.gz rebuilds |
| Wheel | byte-identical rebuild and isolated install |
| Supply-chain evidence | SPDX + CycloneDX SBOMs, SHA-256 Manifest, Sigstore attestations |
| Remote branches | `main` only |

This table reports the immutable v3.0.2 verification evidence dated 2026-07-24. Current-head evidence is kept separately so later documentation and test changes do not rewrite a historical release record. Authoritative release records are stored in `reports/FINAL_VERIFICATION.json`, `evidence/quality-baseline.json`, `reports/REMOTE_FINALIZATION.json`, and `benchmarks/latest.json`.

## CI, release and installation

CI runs the core matrix on Python 3.10 and 3.13 across Ubuntu, Windows and macOS. A read-only weekly dependency audit records vulnerability evidence without creating an upstream branch. Third-party Actions are pinned to immutable commits.

Formal releases are produced only by the governed Release workflow after all deterministic gates pass. Each immutable `vX.Y.Z` release contains reproducible source archives and Wheel, SPDX and CycloneDX SBOMs, `SHA256SUMS`, a release Manifest, final verification evidence and GitHub/Sigstore provenance bundles.

```bash
python scripts/install_skill.py --agent codex --scope user --dry-run
python scripts/install_skill.py --agent codex --scope user
python scripts/install_skill.py --agent codex --scope user --validate
```

Use `--force` only for an intentional, reviewed replacement or uninstall override.

## Trust boundaries

```text
completed ≠ parsed ≠ converged ≠ validated ≠ accepted
```

Benchmark success does not prove live third-party solver execution. Missing convergence, physical checks, uncertainty, applicability, provenance, evidence or required human approval prevents scientific acceptance. Reactor, control, digital-twin, safety, runaway and commercial decisions require qualified domain review.

The 12 illustrations in `assets/visuals/` are original explanatory diagrams generated for this repository. They are not screenshots, benchmark plots, or evidence of live external-engine execution. Their integrity, accessibility, source-distribution inclusion and bilingual README references are automatically tested.

## Repository policy

`main` is the sole authoritative upstream branch. External contributions use fork branches; the canonical repository does not retain feature branches. Historical releases are immutable tags. Generated environments and caches are excluded, while source, configuration, tests, evidence and release metadata remain auditable.
