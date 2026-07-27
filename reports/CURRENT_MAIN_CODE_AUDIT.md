# Current main code audit

- Validated source SHA: `2e513e55f0d602bbb447bc652326bd277c722eb2`
- Overall status: **FAIL**
- Tests collected: `599`
- Coverage: `96.57444005270092%`
- Runtime dependencies: `0`

## Gate results

| Gate | Status | Return code |
|---|---:|---:|
| `quality` | FAIL | 1 |
| `core` | PASS | 0 |
| `package` | PASS | 0 |
| `benchmark` | PASS | 0 |
| `dependency_audit` | PASS | 0 |
| `collect` | PASS | 0 |
| `manifest` | FAIL | 1 |
| `diff_check` | PASS | 0 |

## Fixed findings

- restored the canonical verification API required by the test suite
- restored deterministic sequential and bounded-parallel timing evidence
- restored Mypy, Bandit, repository security scan and mutation gates
- restored canonical cross-platform CI on main
- removed obsolete V6-V12 audit, performance and visual transport workflows
- removed V9 trigger, status and encoded CI transport files

## Remaining obsolete artifacts

- None.

## Claim boundary

Repository-local verification only; no external solver execution is claimed.
