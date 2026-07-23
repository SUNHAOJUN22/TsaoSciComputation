<div align="center">

# TsaoSciComputation

**Evidence-bound scientific-computation orchestration from electrons to processes.**

![version](https://img.shields.io/badge/version-3.0.0-2563eb) ![capabilities](https://img.shields.io/badge/capabilities-164-7c3aed) ![adapters](https://img.shields.io/badge/adapters-27-ea580c) ![workflows](https://img.shields.io/badge/workflows-20-0891b2)

[中文说明](README.zh-CN.md) · [Skill](SKILL.md) · [Capabilities](capability-index/README.md) · [Architecture](docs/architecture.md) · [Security](SECURITY.md)

</div>

## What it is

TsaoSciComputation turns a research question into a reproducible computation plan:

```text
question → calculation contract → workflow routing → environment preflight
         → bounded execution → conservative parsing → convergence/physics checks
         → uncertainty/applicability → evidence-bound acceptance → report/handoff
```

It supplies contracts, registries, validators, secure execution primitives, conservative parsers, examples, tests, and deterministic packaging. It does **not** bundle or impersonate external scientific solvers, licenses, databases, or production HPC infrastructure.

## Verified baseline

| Item | Verified result |
|---|---:|
| Version | 3.0.0 |
| Capabilities / adapters / workflows | 164 / 27 / 20 |
| Runtime dependencies | 0 mandatory third-party packages |
| Tests | 432 passed, 0 failed |
| Statement / branch coverage | 98.80% / 96.81% |
| Controlled mutation probes | 64/64 killed |
| Repository security scan | 0 findings |
| Source archives | byte-identical ZIP and tar.gz rebuilds |
| Wheel | byte-identical rebuild and isolated install |
| Remote branches | `main` only |

Machine-readable evidence is stored in [`evidence/quality-baseline.json`](evidence/quality-baseline.json), [`reports/REMOTE_FINALIZATION.json`](reports/REMOTE_FINALIZATION.json), and [`benchmarks/latest.json`](benchmarks/latest.json). These results validate the orchestration repository; they do not claim live third-party solver or production-cluster execution.

## Quick start

```bash
git clone https://github.com/SUNHAOJUN22/TsaoSciComputation.git
cd TsaoSciComputation
python -m pip install -e .

python -m tsao_computation --version
python -m tsao_computation route "Use DFT and MD to study a polymer interface"
python -m tsao_computation probe
python scripts/init_project.py --root demo --name demo \
  --question "How does morphology affect conductivity?"
```

## Verify everything

The README, CI, and release workflow use the same cross-platform verification entrypoint:

```bash
python -m pip install -e '.[validation,quality]'
python scripts/verify_all.py --profile all
```

`all` runs quality, tests and coverage, repository/schema/asset/manifest validation, security and mutation gates, reproducible source packaging, reproducible wheel building, and isolated wheel installation. For focused diagnosis, use `core`, `quality`, `package`, or `benchmark` instead.

CI runs `core` on Python 3.10 and 3.13 across Ubuntu, Windows, and macOS; it also runs the quality, benchmark, packaging, and CodeQL gates. Release candidates must pass `--profile all`. GitHub Actions are pinned to immutable commits.

## Scientific trust boundary

```text
completed ≠ parsed ≠ converged ≠ validated ≠ accepted
```

Acceptance is fail-closed. Missing convergence, physical checks, uncertainty, applicability limits, provenance, or required human approval prevents promotion to `accepted`. High-risk reactor, control, digital-twin, safety, runaway, and commercial handoff decisions always require expert review.

Performance is environment-specific. [`benchmarks/latest.json`](benchmarks/latest.json) is the source of truth, and [`docs/performance.md`](docs/performance.md) defines the measurement boundary.

## Repository policy

`main` is the only remote branch and the only authoritative development line. Historical branch heads are preserved by immutable archive tags, not by additional branches. Encoded transfer fragments, recovery controllers, temporary trigger files, and generated build caches are forbidden in the ordinary source tree.
