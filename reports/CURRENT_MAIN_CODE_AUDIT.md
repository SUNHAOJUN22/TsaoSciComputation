# Current main code audit

- Audited SHA: `04e6aa5cf8a6b07bc598b60cc44fbc7c8a1fcf2f`
- Overall status: **FAIL**
- Tests collected: `591`

## Gate results

| Gate | Status | Return code |
|---|---:|---:|
| `quality` | FAIL | 1 |
| `core` | FAIL | 2 |
| `package` | FAIL | 1 |
| `benchmark` | PASS | 0 |
| `dependency_audit` | PASS | 0 |
| `collect` | FAIL | 2 |
| `git_diff` | PASS | 0 |

## Static issues

- ci.yml is a temporary V9 same-host A/B workflow rather than canonical CI
- sequential timing record is unreachable after return
- 13 obsolete or one-shot workflow/status artifacts remain tracked

## Obsolete or one-shot artifacts

- `.github/workflows/main-audit-v7.yml`
- `.github/workflows/main-audit.yml`
- `.github/workflows/performance-audit-v8.yml`
- `.github/workflows/performance-audit-v9.yml`
- `.github/workflows/performance-refresh-v9.yml`
- `.github/workflows/readme-visual-redesign-v10.yml`
- `.github/workflows/readme-visual-redesign-v11.yml`
- `.github/workflows/readme-visual-redesign-v12.yml`
- `.v9-ci-status.json`
- `.v9-ci-trigger`
- `.v9-performance-status.json`
- `.v9-performance-trigger`
- `.v9-production-ci.b64`

## Claim boundary

This audit validates repository-local code, tests, packaging, metadata and known dependency advisories. It does not claim external solver execution.
