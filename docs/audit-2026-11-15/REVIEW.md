# Code review and automated validation — 2026-11-15

## Scope and baseline

Reviewed baseline: `6fc37a93f840376998406cbe2539d96d8b2a15f2`.
The remote repository had one branch, `main`, and no open pull requests at the start
of this review. The review covered repository and registry validation, provenance
manifests, generated audit outputs, CI and packaging, and the existing execution,
numerical, and evidence contract tests.

Validation used Linux and CPython 3.12.14. The unchanged `requirements-ci.txt` was
installed with hash verification into an isolated environment, and the editable
package was bound to this checkout. CMake 4.4.5 and GNU C++ 14.2.0 were used for the
native CPU/C-ABI checks.

## Confirmed defects and corrections

| Area | Observed defect | Correction |
| --- | --- | --- |
| Registry validation | Malformed nested fields could raise `TypeError`, or malformed values could pass preliminary checks through implicit string conversion. | Validate the consumed array and text fields before iteration, membership tests, and registry comparison; return a failed audit with field-specific diagnostics. |
| Metadata and JSON path boundary | `VERSION` and `pyproject.toml` could be read through symlinks; invalid UTF-8 in `VERSION` escaped the structured report. Symlink cycles in registry/schema paths could terminate validation with `RuntimeError`. | Check every path component before resolving or reading metadata; report confinement and decoding failures without reading the external target. |
| Tracked provenance manifest | An indexed `directory/file` could be hashed through a directory replaced by a symlink, even though the final file itself was not a symlink. | Reject symlinked ancestors before hashing the file. |
| Audit output destination | `build_acceleration_audits.py --root OTHER_ROOT` inspected the selected tree but wrote or checked reports relative to the caller's current directory. A missing report in check mode raised an exception. | Resolve output paths beneath the requested root and return a failed check when an expected report is absent. |

The first regression run reproduced 20 failures against the baseline. Further
adversarial review reproduced four additional failures for symlink cycles, including
a symlinked registry directory. After the corrections, all 34 targeted tests pass;
24 of these are newly added cases and 10 were existing regression cases.

Generated acceleration reports, quality/security scan counts, and the tracked
manifest were regenerated from the corrected source. The README and scientific
support-level declarations were left intact.

## Executed validation

| Gate | Observed result |
| --- | --- |
| `verify_all.py --profile core` | Passed: **1,406 tests**, **95.57% combined coverage**; statement coverage 96.76%, branch coverage 91.83%; critical-file coverage policy passed |
| Scientific analytical/conservation references | **8/8 passed** |
| Registry, repository, schema, adapter, capability, workflow, scenario and generated-evidence checks | Passed |
| `verify_all.py --profile quality` | Passed: Ruff, formatting, mypy, Bandit, repository security scan, and controlled mutation checks |
| Mypy | No issues in **114 source files** |
| Controlled mutation gate | **64/64 killed**, zero survived |
| `verify_all.py --profile package` | Passed: two identical source archive builds, two identical wheel builds, isolated wheel install, SPDX/CycloneDX SBOM generation and release checksums |
| `verify_native_core.py` | Passed: native C++ library build, **1/1 CTest**, and Python/C-ABI discovery smoke check |
| `verify_all.py --profile benchmark` | Passed: scientific references and local orchestration microbenchmark |
| `run_large_parser_regression.py` | Passed for a **50 MiB synthetic input**; completion did not imply convergence |
| `git diff --check` | Passed |

The principal commands were:

```bash
python scripts/verify_all.py --profile core
python scripts/verify_all.py --profile quality
python scripts/verify_all.py --profile package
python scripts/verify_native_core.py
python scripts/verify_all.py --profile benchmark
python scripts/run_large_parser_regression.py
```

CMake and CTest were initially absent from the environment. After installing the
external build tooling, the native gate passed without source or dependency-lock
changes. The native check validates CPU discovery and the C ABI, not numerical
acceleration. Local tests do not establish Windows qualification, third-party solver
execution, GPU performance, physical validity, or acceptance of scientific results.
