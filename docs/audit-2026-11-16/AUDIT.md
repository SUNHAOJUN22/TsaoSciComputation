# Scientific logic review and automated validation — 2026-11-16

## Scope and baseline

Baseline: `7ddba2ab86c373bcc2fea9664579492b00406003`, on `main`.
The coordinator verified that the remote repository had only `main` and no open
pull requests. This review used a different reviewer from the preceding registry
and filesystem audit and concentrated on the meaning of scientific decisions.

| Assessed code paths | Reasoning and outcome |
| --- | --- |
| `validation/numerical.py`, `validation/physical.py` | Checked tolerance units, scale invariance, sign conventions, zero/trace values and finite arithmetic. Confirmed and corrected the defects below. |
| `scientific_quantity.py`, `uncertainty/model.py` | Inspected explicit unit conversion and independent-component uncertainty assumptions; retained existing guards and validated their regressions. |
| `validation/scientific_benchmarks.py` | Reviewed the fixed conduction, flow, reaction, oscillator, chain, electrostatic and electrothermal references; all eight fixtures pass. These remain local reference calculations. |
| `execution/runner.py`, `execution/batch.py` | Inspected authorization binding, executable/input identity, process failures and retained sibling records. Batch execution has per-plan authorization and permits partial execution; it is not a transactional external-solver rollback facility. |
| `state/machine.py`, `validation/acceptance.py`, `workflows/engine.py` | Checked that planning/completion do not imply convergence or scientific acceptance, and that accepted state still needs bound evidence and independent approval. |
| Verification, native C ABI, packaging and generated evidence | Executed the canonical quality, core, package, native, benchmark, performance and large-parser gates. |

## Confirmed defects and corrections

### Hidden absolute floors changed relative decisions when units changed

The convergence gate used `max(abs(current), abs(previous), 1.0)` even when
`absolute_tolerance=0`. For `[1e-12, 2e-12]` with relative tolerance `0.01`, it
accepted a 50% relative change. Expressing the same values in a basis multiplied
by `1e12` produced `[1, 2]` and a rejection. The documented one-unit floor
therefore made the dimensionless relative tolerance behave as an undeclared
absolute tolerance.

The balance gate had the same floor. An input of `1e-12` with zero output and
zero accumulation passed a 1% relative tolerance, despite losing the entire
flow. The corrected normalization reports a relative residual of one at every
common unit scale.

Both gates now use the magnitude of the supplied quantities, without an implicit
one-unit floor. Convergence retains its explicit absolute tolerance. An all-zero
balance has normalized residual zero and an all-zero observation pair converges.
Positive accumulation remains the storage term in `input - output - accumulation`.
This intentionally makes small-magnitude checks stricter; callers that need an
absolute convergence tolerance must specify its value in the observation unit.

### Subnormal multiplication could round the relative threshold upward

For the smallest positive float `q`, the pair `[q, 2*q]` has relative change
exactly one half. Multiplying `2*q` by `0.49` rounds to `q`, which would wrongly
admit that pair if the rounded product alone decided the result. The decision
now compares the dimensionless change directly. Tolerance `0.49` rejects the
pair and `0.5` accepts it. The returned threshold remains a rounded diagnostic.
Existing invalid-input, overflow and nonzero-to-zero admission guards remain in
place, including the original public `ValueError` behavior for invalid balance
arithmetic. Balanced representable trace flows still pass.

The English/Chinese implementation contracts, both READMEs and the acceptance
notes now describe the same equations and zero-scale behavior.

## Before/after evidence

The new regression file adds **29 cases**. Against the unchanged baseline it
reported **14 failed, 15 passed**, covering ordinary unit scaling and the boundary
controls. The corrected focused numerical/scientific suite reported **92 passed**.
Fraction arithmetic supplies an independent exact relative-change reference for
the half-scale counterexamples; the positive controls include well-converged
values, explicit absolute tolerances, accumulation, zero and balanced subnormals.

## Executed validation

Validation used Linux, CPython **3.12.14**, the unchanged hash-pinned
`requirements-ci.txt`, and an editable installation bound to this checkout.
The exact command records and source hashes are in [validation.json](validation.json).

| Gate | Observed result |
| --- | --- |
| Hash-locked dependency installation and editable install | Passed; no dependency constraints changed |
| `python scripts/verify_all.py --profile core` | **1,435 passed**, **95.57% combined coverage**; critical-file coverage policy passed |
| Analytical/conservation reference fixtures | **8/8 passed** |
| Repository, schema, registry, adapter, workflow and generated-evidence checks | Passed |
| `python scripts/verify_all.py --profile quality` | Ruff, formatting, mypy, Bandit, security scan and quality rules passed |
| Controlled mutation probes | **64/64 killed**, zero survived |
| `python scripts/verify_all.py --profile package` | Reproducible source archives and wheels, isolated wheel installation, SPDX/CycloneDX SBOMs and release checksums passed |
| `python scripts/verify_native_core.py` | Native build, **1/1 CTest** and Python/C-ABI discovery passed |
| `python scripts/verify_all.py --profile benchmark` | Scientific fixtures and local orchestration microbenchmark passed |
| `python -m pytest -q tests/test_performance_v9.py tests/test_performance_optimizations.py` | **33 passed** |
| `python scripts/run_large_parser_regression.py` | **50 MiB** synthetic input passed; completion remained distinct from convergence |

CMake/CTest were initially absent from `PATH`; the native gate initially returned
that explicit environment error. Reusing the existing CMake **4.4.5** tooling with
GNU C++ **14.2.0** made the unchanged native gate pass. No native source or lock
file was changed to accommodate the local environment.

Generated acceleration reports, quality/security counts and the tracked manifest
were refreshed after staging the new test and audit files. Raw logs and runtime
outputs are retained outside the repository, not in the distributable source.

## Limits

These results validate local scientific arithmetic, orchestration contracts and
packaging. They do not establish third-party solver execution, physical model
validity, correlated uncertainty propagation, GPU acceleration or production HPC
performance. Windows and the other supported Python versions require the remote
CI matrix. Whole-trajectory convergence and experimental acceptance remain
separate evidence requirements.
