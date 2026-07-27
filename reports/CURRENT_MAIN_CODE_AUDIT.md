# Current main code audit

- Validated source SHA: `3ac026cfeeaf038e5183fd7493a4a17790ee7eb4`
- Overall status: **PASS**
- Tests collected: `599`
- Coverage: `96.57444005270092%`
- Runtime dependencies: `0`

## Gate results

| Gate | Status | Return code |
|---|---:|---:|
| `quality` | PASS | 0 |
| `core` | PASS | 0 |
| `package` | PASS | 0 |
| `benchmark` | PASS | 0 |
| `dependency_audit` | PASS | 0 |
| `collect` | PASS | 0 |
| `manifest` | PASS | 0 |
| `diff_check` | PASS | 0 |

## Fixed findings

- restored the canonical verification API required by the test suite
- restored complete Ruff, Mypy, Bandit, repository security and mutation gates
- repaired strict type handling in timing and performance evidence generation
- made benchmark verification side-effect-free
- restored canonical Ubuntu, Windows and macOS CI on Python 3.10 and 3.13
- removed obsolete audit, performance, visual transport, trigger and status files

## Remaining obsolete artifacts

- None.

## Claim boundary

Repository-local verification only; no external scientific solver or production HPC execution is claimed.
