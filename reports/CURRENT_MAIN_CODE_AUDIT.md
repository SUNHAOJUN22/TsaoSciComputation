# Current main code audit

- Validated source SHA: `f4c8c2714901e2bf9b72e170c201489000390797`
- Overall status: **FAIL**
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
| `manifest` | FAIL | 1 |
| `diff_check` | PASS | 0 |

## Fixed findings

- restored the canonical verification API required by all verification tests
- restored complete quality, security and mutation gates
- repaired strict type handling in timing and performance evidence generation
- restored canonical cross-platform CI on main
- removed obsolete audit, performance, visual transport, trigger and status files

## Remaining obsolete artifacts

- None.

## Claim boundary

Repository-local verification only; no external solver execution is claimed.
