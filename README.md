<div align="center">

<img src="assets/visuals/hero-multiscale.svg" alt="TsaoSciComputation electron-to-process architecture" width="100%">

# TsaoSciComputation

**Evidence-bound scientific-computation orchestration from electrons to industrial processes.**

![version](https://img.shields.io/badge/version-3.0.4-2563eb) ![capabilities](https://img.shields.io/badge/capabilities-164-7c3aed) ![adapters](https://img.shields.io/badge/adapters-27-ea580c) ![workflows](https://img.shields.io/badge/workflows-20-0891b2)

[中文说明](README.zh-CN.md) · [Skill](SKILL.md) · [Capabilities](capability-index/README.md) · [Visual atlas](assets/visuals/README.md) · [Validation](docs/scientific-validation.md) · [Architecture](docs/architecture.md) · [Security](SECURITY.md)

</div>

## What it does

TsaoSciComputation turns a scientific question into a traceable calculation program:

```text
question → contract → route → preflight → execute → parse
         → converge → validate → quantify uncertainty → accept or reject
```

It provides contracts, method and scale routing, environment checks, bounded execution, conservative parsing, validation, uncertainty, provenance and acceptance gates. It is an orchestration and governance layer—not a bundled solver, license, database, private dataset or production-HPC environment.

## Quick start

```bash
git clone https://github.com/SUNHAOJUN22/TsaoSciComputation.git
cd TsaoSciComputation
python -m pip install -e .

python -m tsao_computation route "Use DFT and MD to study a polymer interface"
python -m tsao_computation validate-contract templates/calculation-contract.json --strict
python -m tsao_computation probe
```

External tools are optional and remain separately installed, licensed, authorized and validated.

<!-- SUPER_SKILL_ORCHESTRATION:START -->
## Capability and execution model

The repository exposes **164 capabilities**, **23 computation methods**, **9 invocation types**, **7 trusted local functions**, **27 external adapters**, **20 workflows**, **13 acceleration strategies** and a **9-stage orchestration plan**.

| Invocation mode | Default behavior |
|---|---|
| Registered trusted local function | May execute after payload validation and request/result hashing |
| External solver or adapter | Probe and command-plan only until separately authorized |
| Python module, CLI, API, container, scheduler or Skill | Declarative handoff until runtime, identity, authorization and evidence requirements are satisfied |

Execution is fail-closed: the legacy low-level process API cannot execute; hardware probes use fixed read-only commands; external authorization is rebound to the executable, declared inputs and normalized environment immediately before launch.
<!-- SUPER_SKILL_ORCHESTRATION:END -->

## Architecture at a glance

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

<!-- V13_VISUAL_SYSTEM:START -->
The 43 self-contained SVGs use **Scientific Research Console V13**. The root README showcases 12 representative diagrams; the complete searchable inventory is in [`assets/visuals/README.md`](assets/visuals/README.md), with design rules in [`assets/visuals/DESIGN_SYSTEM.md`](assets/visuals/DESIGN_SYSTEM.md).
<!-- V13_VISUAL_SYSTEM:END -->

## Multiscale scientific visual map

These AI-assisted information designs are deterministic, repository-owned SVG sources with no external scripts, fonts, raster images or fabricated solver output.

<img src="assets/visuals/quantum-to-md.svg" alt="Electronic-structure to molecular-dynamics handoff" width="100%">
<img src="assets/visuals/reaction-kinetics-network.svg" alt="Reaction pathways, kinetic evidence and reactor handoff" width="100%">
<img src="assets/visuals/polymer-process.svg" alt="Polymer multiscale transfer from molecular architecture to processing" width="100%">
<img src="assets/visuals/continuum-multiphysics.svg" alt="Continuum multiphysics coupling" width="100%">
<img src="assets/visuals/process-optimization-uq.svg" alt="Process optimization and uncertainty quantification" width="100%">
<img src="assets/visuals/uncertainty-sensitivity.svg" alt="Uncertainty propagation and sensitivity ranking" width="100%">

## Acceleration and native interoperability

Python remains the control plane for contracts, routing, provenance and acceptance. Measured hotspots may cross the versioned C ABI into C++20/OpenMP or optional CUDA-enabled backends; CPU-only builds remain supported. Prefer solver-native GPU paths and CUDA-X libraries only after profiling and numerical-equivalence gates.

<img src="assets/visuals/hpc-execution-provenance.svg" alt="Bounded HPC execution and provenance" width="100%">
<img src="assets/visuals/hpc-failure-recovery.svg" alt="HPC checkpointing and bounded recovery" width="100%">
<img src="assets/visuals/acceleration-opportunity-pipeline.svg" alt="Evidence-bound repository acceleration opportunity audit" width="100%">

### Executable repository source audit

```bash
python scripts/build_acceleration_audits.py
python -m tsao_computation audit-acceleration \
  --root . --scope production --limit 50 --min-score 40 \
  --output reports/ACCELERATION_OPPORTUNITIES_PRODUCTION_V4.json
python -m tsao_computation profile-performance \
  --workload routing-hot --workload acceleration-plan \
  --repeats 7 --warmups 1 --output .tsao-computation/performance-profile.json
python -m tsao_computation probe-solver gromacs \
  --output .tsao-computation/gromacs-capability-evidence.json
```

The production audit excludes tests, repository tooling and benchmark fixtures from migration decisions; the full-tree audit remains available for diagnostics. Every candidate is bound to a source hash and stable candidate ID and remains `unprofiled` until runtime evidence exists. Acceleration plans now separate candidate, detected and qualified libraries and bind request, inventory, adapter-profile and plan hashes.

<!-- ACCELERATION_AUDIT_SUMMARY:START -->
V5 reports inventory **169 source files** and **3 native-language files**. The production scope analyzes **59 Python files** and finds **3 unprofiled candidates**; the diagnostic full tree analyzes **166 Python files** and finds **35 candidates**. Neither report claims measured speedup.
<!-- ACCELERATION_AUDIT_SUMMARY:END -->

The batch execution layer now accepts immutable per-plan CPU, GPU and license-token claims plus a host capacity envelope. A condition-based resource broker prevents CPU oversubscription, exclusive-GPU collisions and license over-allocation, while binding the allocation hashes into the batch result.

V5 adds registry-bounded solver capability evidence. `probe-solver` fingerprints the exact resolved executable, records its byte size and SHA-256, checks declared Python modules, and may run only a fixed bounded shell-free version/help argument set. Version output is bounded and hash-bound. The strongest automatic status is `version-probed-unqualified`; numerical equivalence, backend support, speedup, convergence and licensing remain separate qualification gates.

Architecture, CUDA-X selection rules and C++ migration gates: [`docs/accelerated-native-backend.md`](docs/accelerated-native-backend.md). Native verification: `python scripts/verify_native_core.py`.

## Verification

```bash
python -m pip install -e '.[validation,quality,security]'
python scripts/verify_all.py --profile all
python scripts/verify_all.py --profile benchmark
```

`all` covers quality, security, tests, coverage, scientific benchmarks, schema and registry validation, mutation probes, reproducible source/Wheel builds, isolated installation, SBOMs, checksums and release manifests. `benchmark` is environment-dependent telemetry and is not a release gate.

### Canonical cross-platform qualification

<!-- CURRENT_MAIN_VERIFICATION:START -->
The immutable Ubuntu/Windows × Python 3.10/3.13 qualification baseline was validated on `2026-08-02T19:04:13.872746+00:00` by deterministic finalization run `30762511647`.

| Canonical qualification item | Result |
|---|---:|
| Version | 3.0.4 |
| Capabilities / adapters / workflows | 164 / 27 / 20 |
| Tests | 774 passed, 0 failed |
| Statement / branch coverage | 96.63% / 90.99% |
| Windows core | Python 3.10 and 3.13; final result recorded in Issue #49 |
| Linux compatibility | Ubuntu validation; final result recorded in Issue #49 |
| Controlled mutation probes | 64/64 killed |
| Scientific reference benchmarks | 8/8 passed |
| Repository / dependency findings | 0 / 0 |
| Source archives / Wheel | reproducible / reproducible + isolated install |
| Generated text / Manifest | canonical LF / cross-platform stable |
| Scientific visual assets | 42 self-contained SVGs |
| Remote branches | `main` only |

This baseline remains the canonical cross-platform evidence recorded in [Issue #49](../../issues/49). Machine-readable evidence: [`reports/CURRENT_MAIN_VERIFICATION.json`](reports/CURRENT_MAIN_VERIFICATION.json).
<!-- CURRENT_MAIN_VERIFICATION:END -->

### Latest main-only README and native verification

The current main tree, source audit and native-interoperability layer were revalidated on `2026-08-05` by GitHub Actions run `30981066673` before direct publication to `main`.

| Latest gate | Result |
|---|---:|
| Tests | 785 passed, 0 failed |
| Total coverage | 95.26% (required: 95.00%) |
| Ruff / Mypy / Bandit / repository security scan | PASS |
| Controlled mutation probes / scientific benchmarks | 64/64 killed / 8/8 passed |
| Reproducible source archives / Wheel isolated install | PASS / PASS |
| C++20 C ABI build / CTest / Python bridge | PASS / 1 of 1 / PASS |
| Scientific visual assets | 43 self-contained SVGs / 12 featured |
| Remote branches | `main` only |

## Performance evidence

<!-- PERFORMANCE_V9:START -->
**V9:** same-runner acceptance measured `verify_all --profile all` at 12.270 s → 8.129 s (1.51×), bounded deterministic parallel verification and lower peak RSS. Evidence: [`reports/PERFORMANCE_COMPARISON_V9.json`](reports/PERFORMANCE_COMPARISON_V9.json).
<!-- PERFORMANCE_V9:END -->

<!-- MATH_PERFORMANCE_V10:START -->
**V10:** improved repository-local uncertainty, convergence and acceleration-planning kernels; a slower parser candidate was rejected. Evidence: [`reports/MATH_PERFORMANCE_AUDIT_V10.json`](reports/MATH_PERFORMANCE_AUDIT_V10.json).
<!-- MATH_PERFORMANCE_V10:END -->

<!-- MATH_PERFORMANCE_V11:START -->
**V11:** cached static acceleration profiles, canonicalized semantic routing keys and hoisted invariant benchmark arithmetic without changing scientific equations or tolerances. Evidence: [`reports/MATH_PERFORMANCE_AUDIT_V11.json`](reports/MATH_PERFORMANCE_AUDIT_V11.json).
<!-- MATH_PERFORMANCE_V11:END -->

All performance claims cover repository-local orchestration or deterministic kernels only; they do not claim external-solver, GPU-kernel or production-HPC speedup.

## Trust boundaries

```text
completed ≠ parsed ≠ converged ≠ validated ≠ accepted
```

A successful command or benchmark does not prove live third-party solver validity. Missing convergence, physical checks, uncertainty, applicability, provenance, evidence or required expert approval blocks scientific acceptance.

## Platform, release and repository policy

- **Windows:** core supported workflow.
- **Linux:** compatible and CI-validated.
- **Repository:** `main` is the sole authoritative upstream branch; no retained feature branches.
- **Release:** governed tags include reproducible artifacts, SPDX/CycloneDX SBOMs, SHA-256 checksums and provenance evidence.

```bash
python scripts/install_skill.py --agent codex --scope user --dry-run
python scripts/install_skill.py --agent codex --scope user
python scripts/install_skill.py --agent codex --scope user --validate
```

Use `--force` only for an intentional reviewed replacement.

## License and citation

MIT licensed. Citation metadata is in [`CITATION.cff`](CITATION.cff); third-party boundaries are documented in [`THIRD_PARTY.md`](THIRD_PARTY.md).
