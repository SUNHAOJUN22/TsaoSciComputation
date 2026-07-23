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
| Tests | 431 passed, 0 failed |
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

Useful commands:

```bash
python -m tsao_computation list capabilities
python -m tsao_computation list adapters
python -m tsao_computation list workflows
python -m tsao_computation validate-contract examples/organic-dft/contract.json
python -m tsao_computation validate-repository --root .
```

## Full validation

Install both validation and engineering-quality tools, then run the same gates used by CI:

```bash
python -m pip install -e '.[validation,quality]'
python scripts/run_tests.py --coverage
python scripts/quality_check.py
python -m ruff check tsao_computation scripts tests
python -m ruff format --check tsao_computation scripts tests
python -m mypy --python-version 3.13 tsao_computation scripts
python -m bandit -q -r tsao_computation scripts
python scripts/validate_repository.py
python scripts/validate_schemas.py
python scripts/security_scan.py
python scripts/run_mutation_gate.py
python scripts/sync_package_assets.py --check
python scripts/build_capability_index.py --check
python scripts/build_manifest.py --check
SOURCE_DATE_EPOCH=1700000000 python scripts/package_release.py
python scripts/verify_wheel.py
```

CI covers Python 3.10 and 3.13 on Ubuntu, Windows, and macOS, plus quality, security, deterministic packaging, isolated wheel installation, and CodeQL. GitHub Actions are pinned to immutable commits.

## Scientific trust boundary

```text
completed ≠ parsed ≠ converged ≠ validated ≠ accepted
```

Acceptance is fail-closed. Missing convergence, physical checks, uncertainty, applicability limits, provenance, or required human approval prevents promotion to `accepted`. High-risk reactor, control, digital-twin, safety, runaway, and commercial handoff decisions always require expert review.

## Performance

Registries are loaded lazily through bounded caches, probing is concurrent and capped, shell command construction is avoided, and release artifacts are streamed file-by-file. Performance is environment-specific; [`benchmarks/latest.json`](benchmarks/latest.json) is the source of truth and [`docs/performance.md`](docs/performance.md) explains the measurement boundary.

## Repository policy

`main` is the only remote branch and the only authoritative development line. Historical branch heads are preserved by immutable archive tags, not by additional branches. Encoded transfer fragments, recovery controllers, temporary trigger files, and generated build caches are forbidden in the ordinary source tree.
