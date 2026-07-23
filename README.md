<div align="center">

# TsaoSciComputation

**Evidence-bound scientific-computation orchestration from electrons to processes.**

![version](https://img.shields.io/badge/version-3.0.0-2563eb) ![capabilities](https://img.shields.io/badge/capabilities-164-7c3aed) ![adapters](https://img.shields.io/badge/adapters-27-ea580c) ![workflows](https://img.shields.io/badge/workflows-20-0891b2)

[中文说明](README.zh-CN.md) · [Root Skill](SKILL.md) · [Capabilities](capability-index/README.md) · [Coverage](docs/coverage-matrix.md) · [Architecture](docs/architecture.md) · [Security](SECURITY.md)

</div>

## What it is

TsaoSciComputation turns a scientific question into a traceable program:

```text
question → strict calculation contract → scale/method routing → environment preflight
         → bounded execution → conservative parsing → numerical/physical validation
         → uncertainty/applicability → evidence-bound acceptance → multiscale handoff
```

It does not bundle or impersonate external solvers, licenses, databases, pseudopotentials, basis sets, private data, or production HPC infrastructure.

## Verified baseline

| Item | Verified result |
|---|---:|
| Version | 3.0.0 |
| Capabilities / adapters / workflows | 164 / 27 / 20 |
| Runtime dependencies | 0 mandatory third-party packages |
| Tests | 455 passed, 0 failed |
| Statement / branch coverage | 97.52% / 93.33% |
| Controlled mutation probes | 64/64 killed |
| Repository security scan | 0 findings |
| Source archives | byte-identical ZIP and tar.gz rebuilds |
| Wheel | byte-identical rebuild and isolated install |
| Remote branches | `main` only |

Machine-readable evidence is stored in `evidence/quality-baseline.json`, `reports/REMOTE_FINALIZATION.json`, and `benchmarks/latest.json`.

## Coverage boundary

The uploaded catalog contains 322 skills, including a 164-item computational subset and a 32-engine shortlist. This repository also has 164 capabilities, but reorganizes them into 20 validation-aware workflows rather than copying catalog slugs one-for-one. It has 27 core adapters; 21 of the 32 engine rows are represented directly or through combined adapters, while 11 remain explicit non-standalone limits. See [`docs/coverage-matrix.md`](docs/coverage-matrix.md).

## Quick start

```bash
git clone https://github.com/SUNHAOJUN22/TsaoSciComputation.git
cd TsaoSciComputation
python -m pip install -e .

python -m tsao_computation --version
python -m tsao_computation route "Use DFT and MD to study a polymer interface"
python scripts/init_project.py --root demo --name demo \
  --question "How does morphology affect conductivity?"
```

Start from [`templates/calculation-contract.json`](templates/calculation-contract.json), then require the complete preflight contract:

```bash
python -m tsao_computation validate-contract contract.json --strict
python -m tsao_computation probe
```

## Install as an Agent Skill

```bash
python scripts/install_skill.py --agent codex --scope user --dry-run
python scripts/install_skill.py --agent codex --scope user
python scripts/install_skill.py --agent claude --scope project
python scripts/install_skill.py --agent open-agent-skills --target /custom/skills
python scripts/install_skill.py --agent codex --scope user --validate
python scripts/install_skill.py --agent codex --scope user --uninstall
```

Use `--force` only for an intentional replacement or verified uninstall override. The installer supports Windows, Linux, macOS, offline copies, and explicit custom targets.

## Verification

The minimum supported interpreter is Python 3.10; release gates are validated on Python 3.10 and 3.13.

```bash
python -m pip install -e '.[validation,quality]'
python scripts/verify_all.py --profile all
python scripts/verify_all.py --profile benchmark  # environment-specific; separate from release gates
```

`all` runs quality, tests and coverage, repository/schema/asset/manifest validation, security and mutation checks, reproducible source packaging, reproducible wheel building, and isolated wheel installation. CI also covers Python 3.10/3.13 on Ubuntu, Windows, and macOS. GitHub Actions are pinned to immutable commits.

## Scientific trust boundary

```text
completed ≠ parsed ≠ converged ≠ validated ≠ accepted
```

Acceptance is fail-closed. Missing convergence, physical checks, uncertainty, applicability, provenance, or required human approval prevents promotion to `scientifically-accepted`. High-risk reactor, control, digital-twin, safety, runaway, and commercial handoff decisions require expert review.

## Repository policy

`main` is the only remote branch and authoritative development line. Historical branch heads are preserved by immutable archive tags, not additional branches. Generated environments and caches are consistently pruned, while real source and configuration files remain in scope.
