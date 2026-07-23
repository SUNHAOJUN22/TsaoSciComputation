# Final verification diagnosis

- Python 3.10: `PASS`
- Python 3.13: `quality`

## Python 3.10 log

```text
STAGE=PASS

```

## Python 3.13 log

```text
STAGE=quality
EXIT_CODE=1
--- LOG TAIL ---

==> repository quality rules
    /opt/hostedtoolcache/Python/3.13.14/x64/bin/python scripts/quality_check.py
{"passed": true, "problems": [], "python_files": 82, "schema_version": "1.0"}

==> Ruff lint
    /opt/hostedtoolcache/Python/3.13.14/x64/bin/python -m ruff check tsao_computation scripts tests
All checks passed!

==> Ruff formatting
    /opt/hostedtoolcache/Python/3.13.14/x64/bin/python -m ruff format --check tsao_computation scripts tests
82 files already formatted

==> Mypy
    /opt/hostedtoolcache/Python/3.13.14/x64/bin/python -m mypy --python-version 3.13 tsao_computation scripts
scripts/security_scan.py:7: error: Cannot find implementation or library stub for module named "_bootstrap"  [import-not-found]
scripts/package_release.py:13: error: Cannot find implementation or library stub for module named "_bootstrap"  [import-not-found]
scripts/build_manifest.py:7: error: Cannot find implementation or library stub for module named "_bootstrap"  [import-not-found]
scripts/run_mutation_gate.py:14: error: Cannot find implementation or library stub for module named "_bootstrap"  [import-not-found]
scripts/run_mutation_gate.py:14: error: Name "_bootstrap" already defined (by an import)  [no-redef]
scripts/select_solver.py:5: error: Cannot find implementation or library stub for module named "_bootstrap"  [import-not-found]
scripts/build_capability_index.py:6: error: Cannot find implementation or library stub for module named "_bootstrap"  [import-not-found]
scripts/init_project.py:4: error: Cannot find implementation or library stub for module named "_bootstrap"  [import-not-found]
scripts/verify_wheel.py:13: error: Cannot find implementation or library stub for module named "_bootstrap"  [import-not-found]
scripts/validate_repository.py:8: error: Cannot find implementation or library stub for module named "_bootstrap"  [import-not-found]
scripts/select_scale.py:4: error: Cannot find implementation or library stub for module named "_bootstrap"  [import-not-found]
scripts/validate_schemas.py:7: error: Cannot find implementation or library stub for module named "_bootstrap"  [import-not-found]
scripts/probe_environment.py:7: error: Cannot find implementation or library stub for module named "_bootstrap"  [import-not-found]
scripts/benchmark.py:12: error: Cannot find implementation or library stub for module named "_bootstrap"  [import-not-found]
scripts/benchmark.py:12: note: See https://mypy.readthedocs.io/en/stable/running_mypy.html#missing-imports
Found 14 errors in 13 files (checked 63 source files)

FAILED: Mypy (exit 1)

```
