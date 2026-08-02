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
The 42 self-contained SVGs use **Scientific Research Console V13**. The root README keeps only the three overview diagrams; the complete searchable inventory is in [`assets/visuals/README.md`](assets/visuals/README.md), with design rules in [`assets/visuals/DESIGN_SYSTEM.md`](assets/visuals/DESIGN_SYSTEM.md).
<!-- V13_VISUAL_SYSTEM:END -->

## Verification

```bash
python -m pip install -e '.[validation,quality,security]'
python scripts/verify_all.py --profile all
python scripts/verify_all.py --profile benchmark
```

`all` covers quality, security, tests, coverage, scientific benchmarks, schema and registry validation, mutation probes, reproducible source/Wheel builds, isolated installation, SBOMs, checksums and release manifests. `benchmark` is environment-dependent telemetry and is not a release gate.

### Current `main` verification

<!-- CURRENT_MAIN_VERIFICATION:START -->
Validated on `2026-08-02T19:04:13.872746+00:00` by deterministic finalization run `30762511647`.

| Current-main item | Result |
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

The final final-exact-tree-v3 commit is accepted only after canonical Ubuntu/Windows × Python 3.10/3.13 CI is recorded in [Issue #49](../../issues/49). Machine-readable evidence: [`reports/CURRENT_MAIN_VERIFICATION.json`](reports/CURRENT_MAIN_VERIFICATION.json).
<!-- CURRENT_MAIN_VERIFICATION:END -->

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
