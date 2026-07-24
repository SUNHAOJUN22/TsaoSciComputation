<div align="center">

# TsaoSciComputation

**Evidence-bound scientific-computation orchestration from electrons to processes.**

![version](https://img.shields.io/badge/version-3.0.1-2563eb) ![capabilities](https://img.shields.io/badge/capabilities-164-7c3aed) ![adapters](https://img.shields.io/badge/adapters-27-ea580c) ![workflows](https://img.shields.io/badge/workflows-20-0891b2)

[中文说明](README.zh-CN.md) · [Root Skill](SKILL.md) · [Capabilities](capability-index/README.md) · [Coverage](docs/coverage-matrix.md) · [Architecture](docs/architecture.md) · [Releases](docs/release.md) · [Security](SECURITY.md)

</div>

## Purpose

TsaoSciComputation converts a scientific question into a traceable calculation program:

```text
question → strict contract → method/scale route → environment preflight
         → bounded execution → conservative parsing → validation
         → uncertainty/applicability → acceptance → multiscale handoff
```

It orchestrates scientific work; it does **not** bundle or impersonate external solvers, licenses, databases, basis sets, pseudopotentials, private data, or production HPC infrastructure.

## Verified baseline

| Item | Verified result |
|---|---:|
| Version | 3.0.1 |
| Capabilities / adapters / workflows | 164 / 27 / 20 |
| Runtime dependencies | 0 mandatory third-party packages |
| Tests | 514 passed, 0 failed |
| Statement / branch coverage | 97.02% / 93.06% |
| Controlled mutation probes | 64/64 killed |
| Repository security scan | 0 findings |
| Source archives | byte-identical ZIP and tar.gz rebuilds |
| Wheel | byte-identical rebuild and isolated install |
| Supply-chain evidence | SPDX + CycloneDX SBOMs, SHA-256 Manifest, Sigstore attestations |
| Remote branches | `main` only |

The authoritative machine-readable evidence is in `reports/FINAL_VERIFICATION.json`, `evidence/quality-baseline.json`, `reports/REMOTE_FINALIZATION.json`, and `benchmarks/latest.json`.

## Start

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

The strict contract is the control point: malformed fields, missing preflight information, unavailable executables or Python modules, unsafe paths, invalid state transitions, and incomplete acceptance evidence fail closed.

## Scope

The repository contains 164 differentiated capabilities organized into 20 validation-aware workflows and 27 core adapters. Of the 32 engines in the source shortlist, 21 are represented directly or through combined adapters; 11 remain explicit non-standalone limits. See [`docs/coverage-matrix.md`](docs/coverage-matrix.md).

## Verify

```bash
python -m pip install -e '.[validation,quality]'
python scripts/verify_all.py --profile all
python scripts/verify_all.py --profile benchmark
```

`all` is the deterministic release gate: version consistency, quality, tests and coverage, repository/Schema/asset/Manifest checks, security, controlled mutation probes, reproducible source and Wheel builds, isolated installation, SBOM generation, and release checksums. `benchmark` is environment-dependent telemetry and is deliberately separate from release acceptance. CI validates the core matrix on Python 3.10 and 3.13 across Ubuntu, Windows, and macOS; Actions are pinned to immutable commits.

## Releases

Formal releases are created only by the governed Release workflow after every deterministic gate passes. Each immutable `vX.Y.Z` release contains reproducible archives and Wheel, SPDX and CycloneDX SBOMs, `SHA256SUMS`, a release Manifest, final verification evidence, and GitHub/Sigstore provenance bundles.

```bash
sha256sum -c SHA256SUMS
gh attestation verify TsaoSciComputation-X.Y.Z.zip \
  --repo SUNHAOJUN22/TsaoSciComputation
```

See [`docs/release.md`](docs/release.md) for the complete publication and consumer-verification process.

## Install as an Agent Skill

```bash
python scripts/install_skill.py --agent codex --scope user --dry-run
python scripts/install_skill.py --agent codex --scope user
python scripts/install_skill.py --agent codex --scope user --validate
```

Use `--force` only for an intentional, reviewed replacement or uninstall override.

## Scientific trust boundary

Adapter discovery requires every declared executable and Python module; normal exit is not convergence. Installed copies are checked against the full SHA-256 Manifest, and all 12 scenario contracts pass strict preflight validation.

```text
completed ≠ parsed ≠ converged ≠ validated ≠ accepted
```

Acceptance remains fail-closed. Missing convergence, physical checks, uncertainty, applicability, provenance, evidence, or required human approval prevents scientific acceptance. Reactor, control, digital-twin, safety, runaway, and commercial handoff decisions require domain-expert review.

## Repository policy

`main` is the only upstream remote branch and the authoritative line. External contributions use fork branches; the canonical repository does not retain feature branches. Historical releases are immutable tags. Generated environments and caches are excluded; real source, configuration, tests, evidence, and release metadata remain auditable.
