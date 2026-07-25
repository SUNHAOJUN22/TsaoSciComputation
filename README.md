<div align="center">

# TsaoSciComputation

**Evidence-bound scientific-computation orchestration from electrons to processes.**

![version](https://img.shields.io/badge/version-3.0.2-2563eb) ![capabilities](https://img.shields.io/badge/capabilities-164-7c3aed) ![adapters](https://img.shields.io/badge/adapters-27-ea580c) ![workflows](https://img.shields.io/badge/workflows-20-0891b2)

[中文说明](README.zh-CN.md) · [Root Skill](SKILL.md) · [Capabilities](capability-index/README.md) · [Coverage](docs/coverage-matrix.md) · [Scientific validation](docs/scientific-validation.md) · [Confidence](docs/scientific-confidence.md) · [Architecture](docs/architecture.md) · [Releases](docs/release.md) · [Maintenance](docs/dependency-maintenance.md) · [Security](SECURITY.md)

</div>

## Overview

TsaoSciComputation turns a scientific question into a traceable, fail-closed calculation program:

```text
question → contract → method/scale route → environment preflight
         → bounded execution → conservative parsing → validation
         → uncertainty/applicability → acceptance → multiscale handoff
```

It orchestrates scientific work. It does **not** bundle or impersonate external solvers, licenses, databases, basis sets, pseudopotentials, private data, or production HPC infrastructure.

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

External solvers remain optional and must be installed, licensed, and validated separately. Missing executables, malformed contracts, unsafe paths, illegal state transitions, or incomplete evidence are rejected rather than silently accepted.

## Verified baseline

| Item | Verified result |
|---|---:|
| Version | 3.0.2 |
| Capabilities / adapters / workflows | 164 / 27 / 20 |
| Mandatory runtime dependencies | 0 |
| Tests | 553 passed, 0 failed |
| Statement / branch coverage | 97.27% / 93.48% |
| Controlled mutation probes | 64/64 killed |
| Scientific reference benchmarks | 8/8 passed |
| Scientific confidence model | C0–C5 fail-closed |
| Repository and dependency findings | 0 / 0 |
| Source archives | byte-identical ZIP and tar.gz rebuilds |
| Wheel | byte-identical rebuild and isolated install |
| Supply-chain evidence | SPDX + CycloneDX SBOMs, SHA-256 Manifest, Sigstore attestations |
| Remote branches | `main` only |

Authoritative machine-readable evidence is stored in `reports/FINAL_VERIFICATION.json`, `evidence/quality-baseline.json`, `reports/REMOTE_FINALIZATION.json`, and `benchmarks/latest.json`.

## Verification

```bash
python -m pip install -e '.[validation,quality]'
python scripts/verify_all.py --profile all
python scripts/verify_all.py --profile benchmark
```

`all` runs the deterministic release gates: version consistency, quality checks, tests and coverage, repository/Schema/asset/Manifest validation, security scanning, controlled mutation probes, reproducible source and Wheel builds, isolated installation, SBOM generation, and release checksums. `benchmark` is environment-dependent telemetry and remains separate from release acceptance.

CI runs the core matrix on Python 3.10 and 3.13 across Ubuntu, Windows, and macOS. A read-only weekly dependency audit records known-vulnerability evidence without creating an upstream branch. All third-party Actions are pinned to immutable commits.

## Scientific scope and boundaries

The repository contains 164 differentiated capabilities, 20 validation-aware workflows, and 27 core adapters. Of 32 engines in the source shortlist, 21 are represented directly or through combined adapters; 11 remain explicit non-standalone limits. See [`docs/coverage-matrix.md`](docs/coverage-matrix.md).

```text
completed ≠ parsed ≠ converged ≠ validated ≠ accepted
```

Adapter discovery requires every declared executable and Python module. Normal exit does not prove convergence, benchmark success does not prove live third-party solver execution, and missing convergence, physical checks, uncertainty, applicability, provenance, evidence, or required human approval prevents scientific acceptance. High-risk reactor, control, digital-twin, safety, runaway, and commercial decisions require qualified domain review.

## Release and Skill installation

Formal releases are produced only by the governed Release workflow after every deterministic gate passes. Each immutable `vX.Y.Z` release includes reproducible archives and Wheel, SPDX and CycloneDX SBOMs, `SHA256SUMS`, a release Manifest, final verification evidence, and GitHub/Sigstore provenance bundles.

```bash
python scripts/install_skill.py --agent codex --scope user --dry-run
python scripts/install_skill.py --agent codex --scope user
python scripts/install_skill.py --agent codex --scope user --validate
```

Use `--force` only for an intentional, reviewed replacement or uninstall override. See [`docs/release.md`](docs/release.md) for release and consumer-verification details.

## Repository policy

`main` is the only upstream remote branch and the authoritative line. External contributions use fork branches; the canonical repository does not retain feature branches. Historical releases are immutable tags. Generated environments and caches are excluded, while source, configuration, tests, evidence, and release metadata remain auditable.
