# Final verification diagnosis

- Python 3.10: `core`
- Python 3.13: `quality`

## Python 3.10 log

```text
STAGE=core
EXIT_CODE=2
--- LOG TAIL ---

==> tests and coverage
    /opt/hostedtoolcache/Python/3.10.20/x64/bin/python scripts/run_tests.py --coverage

==================================== ERRORS ====================================
____________ ERROR collecting tests/test_validation_fail_closed.py _____________
ImportError while importing test module '/home/runner/work/TsaoSciComputation/TsaoSciComputation/tests/test_validation_fail_closed.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/importlib/__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
tests/test_validation_fail_closed.py:7: in <module>
    from scripts.run_mutation_gate import state_mutants
scripts/run_mutation_gate.py:11: in <module>
    import _bootstrap  # noqa: F401
E   ModuleNotFoundError: No module named '_bootstrap'
=========================== short test summary info ============================
ERROR tests/test_validation_fail_closed.py
!!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
1 error in 0.64s

FAILED: tests and coverage (exit 2)

```

## Python 3.13 log

```text
STAGE=quality
EXIT_CODE=1
--- LOG TAIL ---

==> repository quality rules
    /opt/hostedtoolcache/Python/3.13.14/x64/bin/python scripts/quality_check.py
{"passed": true, "problems": [], "python_files": 81, "schema_version": "1.0"}

==> Ruff lint
    /opt/hostedtoolcache/Python/3.13.14/x64/bin/python -m ruff check tsao_computation scripts tests
I001 [*] Import block is un-sorted or un-formatted
  --> scripts/run_mutation_gate.py:2:1
   |
 1 |   # mypy: disable-error-code=misc
 2 | / from __future__ import annotations
 3 | |
 4 | | import json
 5 | | import math
 6 | | import tempfile
 7 | | from collections.abc import Callable
 8 | | from pathlib import Path
 9 | | from typing import Any
10 | |
11 | | import _bootstrap  # noqa: F401
12 | |
13 | | from tsao_computation.errors import StateTransitionError
14 | | from tsao_computation.security.paths import confined_path
15 | | from tsao_computation.state.machine import ScientificStateMachine, TRANSITIONS
16 | | from tsao_computation.validation.acceptance import REQUIRED
   | |___________________________________________________________^
17 |
18 |   Probe = tuple[str, Callable[[], bool]]
   |
help: Organize imports

Found 1 error.
[*] 1 fixable with the `--fix` option.

FAILED: Ruff lint (exit 1)

```
