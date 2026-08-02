<div align="center">

<img src="assets/visuals/hero-multiscale.svg" alt="TsaoSciComputation electron-to-process architecture" width="100%">

# TsaoSciComputation

**Evidence-bound scientific-computation orchestration from electrons to industrial processes.**

![version](https://img.shields.io/badge/version-3.0.3-2563eb) ![capabilities](https://img.shields.io/badge/capabilities-164-7c3aed) ![adapters](https://img.shields.io/badge/adapters-27-ea580c) ![workflows](https://img.shields.io/badge/workflows-20-0891b2)

[中文说明](README.zh-CN.md) · [Root Skill](SKILL.md) · [Capabilities](capability-index/README.md) · [Coverage](docs/coverage-matrix.md) · [Scientific validation](docs/scientific-validation.md) · [Confidence](docs/scientific-confidence.md) · [Architecture](docs/architecture.md) · [Releases](docs/release.md) · [Security](SECURITY.md)

</div>

<!-- V13_VISUAL_SYSTEM:START -->
## Visual design system

The 42 repository-local SVGs now use **Scientific Research Console V13**, generated from the
UI/UX Pro Max upstream priority model and its Chinese tutorial adaptation.

- accessibility and GitHub-scale readability come before decoration;
- all diagrams use one restrained technical-editorial palette and one line-icon grammar;
- meaning is reinforced by labels, shapes and position rather than color alone;
- detailed workflows remain full width inside semantic `<details>` groups;
- diagram text is at least 16 px, with no external fonts, scripts, raster images, gradients or filters.

See [`assets/visuals/DESIGN_SYSTEM.md`](assets/visuals/DESIGN_SYSTEM.md).
<!-- V13_VISUAL_SYSTEM:END -->

## What it is

TsaoSciComputation converts a scientific question into a traceable calculation program with explicit contracts, method and scale routing, environment preflight, bounded execution, conservative parsing, numerical and physical validation, uncertainty, applicability, provenance, and acceptance gates.

```text
question → contract → route → preflight → execute → parse
         → converge → validate → quantify uncertainty → accept or reject
```

It is an **orchestration and governance layer**. It does not bundle, redistribute, unlock, or impersonate external solvers, licenses, databases, basis sets, pseudopotentials, private data, or production HPC infrastructure.

<!-- SUPER_SKILL_ORCHESTRATION:START -->
## Scientific computation super-skill

TsaoSciComputation acts as both a scientific Skill and a fail-closed intermediary platform. It exposes **23 computation methods**, **9 invocation types**, **7 trusted local scientific functions**, **27 external adapters**, **20 governed workflows**, **13 acceleration strategies**, and a **9-stage orchestration plan**.

| Invocation mode | Default behavior |
|---|---|
| Registered trusted Python callable | May execute locally with validated payloads, duration and request/result hashes |
| External adapter or commercial solver | Probe and command-plan only; execution remains separately authorized |
| Python module, CLI, API, container, scheduler or other Skill | Declarative plan/handoff only until a runtime, identity, authorization and evidence policy are supplied |

```bash
python -m tsao_computation list methods
python -m tsao_computation list invocations
python -m tsao_computation plan templates/calculation-contract.json --strict
python -m tsao_computation recommend-acceleration --method finite-element
python -m tsao_computation invoke balance-check --payload balance.json --execute
```

Acceleration guidance covers algorithm, memory, backend, execution and model-reduction choices. A recommendation is not presented as measured speedup unless isolated machine evidence says so. See [`docs/orchestration.md`](docs/orchestration.md) and [`reports/ULTIMATE_COMPUTATION_SUPER_SKILL_AUDIT.json`](reports/ULTIMATE_COMPUTATION_SUPER_SKILL_AUDIT.json).
<!-- SUPER_SKILL_ORCHESTRATION:END -->

## Scientific capability atlas

Only two compact architecture overviews remain inline. Detailed workflows, loops and risk maps are full width and grouped by domain to reduce scrolling while keeping all 42 assets discoverable.

<table>
<tr>
<td width="50%"><img src="assets/visuals/agent-orchestration.svg" alt="Governed scientific agent orchestration" width="100%"></td>
<td width="50%"><img src="assets/visuals/capability-landscape.svg" alt="Scientific capability landscape" width="100%"></td>
</tr>
<tr>
<td align="center"><strong>Governed scientific agent</strong></td>
<td align="center"><strong>Contract-based capability system</strong></td>
</tr>
</table>

The core design is fail-closed: declared capability is not environment availability; process completion is not convergence; numerical convergence is not physical validity; validation is not high-risk authority.


<details open>
<summary><strong>Electronic structure, molecular simulation and reactions</strong> — quantum, sampling, kinetics, spectroscopy and cross-scale parameterization</summary>

<img src="assets/visuals/quantum-to-md.svg" alt="Electronic structure to molecular dynamics handoff" width="100%">

<img src="assets/visuals/electronic-structure-landscape.svg" alt="Electronic structure evidence landscape" width="100%">

<img src="assets/visuals/free-energy-sampling.svg" alt="Enhanced sampling and free energy workflow" width="100%">

<img src="assets/visuals/reaction-kinetics-network.svg" alt="Reaction pathway and kinetic network" width="100%">

<img src="assets/visuals/ml-potential-active-learning.svg" alt="Machine learned potential active learning" width="100%">

<img src="assets/visuals/periodic-materials-stability.svg" alt="Periodic materials stability workflow" width="100%">

<img src="assets/visuals/catalysis-microkinetics.svg" alt="Catalysis microkinetic evidence workflow" width="100%">

<img src="assets/visuals/quantum-chemistry-thermochemistry.svg" alt="Quantum chemistry thermochemistry workflow" width="100%">

<img src="assets/visuals/molecular-dynamics-transport.svg" alt="Molecular dynamics transport workflow" width="100%">

<img src="assets/visuals/conformer-solvation-excited-state.svg" alt="Conformer solvation and excited state workflow" width="100%">

<img src="assets/visuals/surface-adsorption-migration.svg" alt="Surface adsorption defect and migration workflow" width="100%">

<img src="assets/visuals/spectroscopy-observables.svg" alt="Spectroscopy observable assignment workflow" width="100%">

</details>

<details>
<summary><strong>Materials, interfaces and manufacturing</strong> — morphology, transport, polymerization, composites and processing windows</summary>

<img src="assets/visuals/polymer-process.svg" alt="Polymer structure to process workflow" width="100%">

<img src="assets/visuals/mesoscale-phase-field.svg" alt="Mesoscale phase field evidence workflow" width="100%">

<img src="assets/visuals/electrochemical-interface.svg" alt="Electrochemical interface evidence workflow" width="100%">

<img src="assets/visuals/transport-degradation.svg" alt="Coupled transport and degradation workflow" width="100%">

<img src="assets/visuals/polymerization-population-balance.svg" alt="Polymerization population balance workflow" width="100%">

<img src="assets/visuals/extrusion-rheology-window.svg" alt="Extrusion rheology processing window" width="100%">

<img src="assets/visuals/polymer-composite-topology.svg" alt="Polymer composite topology workflow" width="100%">

<img src="assets/visuals/multiscale-handoff-uncertainty.svg" alt="Multiscale handoff and uncertainty workflow" width="100%">

</details>

<details>
<summary><strong>Continuum, process and operations</strong> — CFD, FEM, flowsheets, reactors, control and digital twins</summary>

<img src="assets/visuals/continuum-multiphysics.svg" alt="Continuum multiphysics verification" width="100%">

<img src="assets/visuals/process-optimization-uq.svg" alt="Process optimization and uncertainty workflow" width="100%">

<img src="assets/visuals/reactor-safety-control.svg" alt="Reactor safety control workflow" width="100%">

<img src="assets/visuals/fem-verification-convergence.svg" alt="Finite element verification and convergence" width="100%">

<img src="assets/visuals/flowsheet-convergence-balances.svg" alt="Flowsheet convergence and balance workflow" width="100%">

<img src="assets/visuals/cfd-turbulence-multiphase.svg" alt="CFD turbulence multiphase transport workflow" width="100%">

<img src="assets/visuals/reactor-scaleup-thermal-risk.svg" alt="Reactor scale up and thermal risk workflow" width="100%">

<img src="assets/visuals/dynamic-control-estimation.svg" alt="Dynamic control and state estimation workflow" width="100%">

<img src="assets/visuals/digital-twin-drift.svg" alt="Digital twin drift aware lifecycle" width="100%">

</details>

<details>
<summary><strong>Evidence, governance and computing infrastructure</strong> — uncertainty, adapters, HPC, confidence and reproducibility</summary>

<img src="assets/visuals/uncertainty-sensitivity.svg" alt="Uncertainty and sensitivity decision workflow" width="100%">

<img src="assets/visuals/inverse-design-loop.svg" alt="Inverse design evidence loop" width="100%">

<img src="assets/visuals/data-model-governance.svg" alt="Scientific data and model governance" width="100%">

<img src="assets/visuals/hpc-execution-provenance.svg" alt="Bounded HPC execution provenance" width="100%">

<img src="assets/visuals/engine-ecosystem.svg" alt="Scientific solver adapter ecosystem" width="100%">

<img src="assets/visuals/evidence-loop.svg" alt="Fail-closed scientific evidence loop" width="100%">

<img src="assets/visuals/confidence-ladder.svg" alt="Scientific confidence ladder C0 to C5" width="100%">

<img src="assets/visuals/digital-thread.svg" alt="Reproducible scientific digital thread" width="100%">

<img src="assets/visuals/scale-multifidelity-plan.svg" alt="Scientific scale and multi fidelity plan" width="100%">

<img src="assets/visuals/hpc-failure-recovery.svg" alt="HPC failure classification and recovery workflow" width="100%">

</details>

The repository contains 27 conservative adapter definitions; external solvers remain separately installed, licensed and validated. Governed handoffs can retain units, versions, seeds, tolerances, raw artifacts, parsed results, hashes and release evidence.
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

<!-- PERFORMANCE_V9:START -->
## Performance engineering

V9 measures the accepted V8 baseline and the candidate on the same runner before accepting any efficiency claim. Deterministic audit run `30235135456` recorded:

| Measured path | V8 baseline | V9 candidate | Result |
|---|---:|---:|---:|
| `verify_all --profile all` median wall time | 12.270 s | 8.129 s | 1.51× |
| `verify_all` wall p90 | 12.286 s | 8.135 s | telemetry |
| Workflow routing | baseline | candidate | 260.23× |
| 5 MiB solver-output parsing | baseline | candidate | 0.98× |
| Peak RSS ratio | 1.00× | 0.77× | limit 1.10× |

The optimized verifier runs only independent subprocess gates concurrently, captures their output separately, and emits logs in the original declared order. Source reproducibility builds run concurrently only because their output directories are isolated. Zero mandatory runtime dependencies, fail-closed parsing, cache invalidation, deterministic Manifests and scientific acceptance boundaries remain unchanged. Evidence: [`reports/PERFORMANCE_COMPARISON_V9.json`](reports/PERFORMANCE_COMPARISON_V9.json), [`reports/PERFORMANCE_PROFILE_V9.json`](reports/PERFORMANCE_PROFILE_V9.json), and [Issue #29](../../issues/29).
<!-- PERFORMANCE_V9:END -->

## Verification

```bash
python -m pip install -e '.[validation,quality]'
python scripts/verify_all.py --profile all
python scripts/verify_all.py --profile benchmark
```

`all` runs the deterministic release gates: quality and security checks, tests and branch coverage, scientific reference benchmarks, critical coverage policy, version and registry synchronization, repository and Schema validation, adapter and documentation validation, controlled mutation probes, reproducible source and Wheel builds, isolated installation, SPDX and CycloneDX SBOM generation, checksums and release manifests. `benchmark` is environment-dependent telemetry and remains separate from release acceptance.

### Current `main` verification

<!-- CURRENT_MAIN_VERIFICATION:START -->
Validated on `2026-08-02T16:37:12.500249+00:00` by deterministic finalization run `30756995636`.

| Current-main item | Result |
|---|---:|
| Version | 3.0.3 |
| Capabilities / adapters / workflows | 164 / 27 / 20 |
| Tests | 747 passed, 0 failed |
| Statement / branch coverage | 96.85% / 91.27% |
| Windows core | Python 3.10 and 3.13; final result recorded in Issue #61 |
| Linux compatibility | Ubuntu validation; final result recorded in Issue #61 |
| Controlled mutation probes | 64/64 killed |
| Scientific reference benchmarks | 8/8 passed |
| Repository / dependency findings | 0 / 0 |
| Source archives / Wheel | reproducible / reproducible + isolated install |
| Generated text / Manifest | canonical LF / cross-platform stable |
| Scientific visual assets | 42 self-contained SVGs |
| Remote branches | `main` only |

The final adversarial-computation-super-skill commit is accepted only after canonical Ubuntu/Windows × Python 3.10/3.13 CI is recorded in [Issue #61](../../issues/61). Machine-readable evidence: [`reports/CURRENT_MAIN_VERIFICATION.json`](reports/CURRENT_MAIN_VERIFICATION.json).
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

CI runs the core matrix on Python 3.10 and 3.13 across Ubuntu and Windows. A read-only weekly dependency audit records vulnerability evidence without creating an upstream branch. Third-party Actions are pinned to immutable commits.

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

The 42 illustrations in `assets/visuals/` are original explanatory diagrams generated for this repository. They are not screenshots, benchmark plots, or evidence of live external-engine execution. Their integrity, accessibility, source-distribution inclusion and bilingual README references are automatically tested.

## Repository policy

`main` is the sole authoritative upstream branch. External contributions use fork branches; the canonical repository does not retain feature branches. Historical releases are immutable tags. Generated environments and caches are excluded, while source, configuration, tests, evidence and release metadata remain auditable.

<!-- MATH_PERFORMANCE_V10:START -->
### Mathematical correctness and performance V10

The current main line uses stable uncertainty propagation, O(1)-memory convergence checks, compensated conservation residuals, finite benchmark-error arithmetic and cached acceleration-library recommendations. A proposed compiled-regex parser prefilter was rejected and reverted after measuring a `0.30×` parser ratio.

Isolated same-host results versus the previously certified main: repeated acceleration planning **1.06×**, convergence evaluation **1.24×**, uncertainty propagation **1.57×**, and convergence peak traced memory **0.006%** of baseline. All eight scientific reference benchmarks and the complete deterministic gate passed. These figures cover repository-local Python kernels and orchestration only; they do not claim external-solver, GPU-kernel or production-HPC speedup.

Machine evidence: [`reports/MATH_PERFORMANCE_AUDIT_V10.json`](reports/MATH_PERFORMANCE_AUDIT_V10.json).
<!-- MATH_PERFORMANCE_V10:END -->

<!-- MATH_PERFORMANCE_V11:START -->
### Mathematical correctness and performance V11

A second-pass audit cached static acceleration-profile parsing, normalized semantically equivalent routing cache keys, and hoisted invariant arithmetic from the deterministic Poiseuille, RK4 and velocity-Verlet benchmark loops. Numerical methods, tolerances and scientific acceptance remain unchanged.

Isolated same-host results versus V10: pre-parsed acceleration planning **1.09×**, semantic route variants **184.03×**, and the eight-benchmark suite **1.37×**. Equivalent route inputs use **1** cached decision instead of **256** entries. Mapping planning, parser, convergence and uncertainty kernels remained within no-material-regression limits. These figures cover repository-local Python kernels only.

Machine evidence: [`reports/MATH_PERFORMANCE_AUDIT_V11.json`](reports/MATH_PERFORMANCE_AUDIT_V11.json).
<!-- MATH_PERFORMANCE_V11:END -->
