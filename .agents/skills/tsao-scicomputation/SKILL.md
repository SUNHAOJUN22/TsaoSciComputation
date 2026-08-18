---
name: tsao-scicomputation
description: Use for TsaoSciComputation contracts, solver handoffs, convergence and balance checks, execution capabilities, process isolation, provenance ledgers, or scientific acceptance gates. Activate on requests to mark an unverified external run as accepted so the request is held. Do not use for generic mathematics, unrelated coding, or prose-only scientific explanation.
license: Apache-2.0
compatibility: Windows and Linux scientific-computation runtime. External solver or HPC execution requires exact-bound, independently verifiable evidence.
metadata:
  author: "SUNHAOJUN22"
  version: "16.0.0"
  repository: "TsaoSciComputation"
---
# TsaoSciComputation

## Workflow

1. Parse all numerical data as finite, dimensioned quantities; reject Boolean values and non-standard JSON numbers.
2. Canonicalize units before convergence or balance arithmetic.
3. Require a scoped, short-lived, signed, one-time capability before external process start.
4. Keep `executed`, `converged`, `numerically_checked`, `physically_validated`, and `accepted` as separate monotone states.
5. Preserve bounded output, full process-tree cleanup, and hash-chained provenance.
6. Run the smallest counterexample first, then the repository-native frozen gates.

## Truth boundary

Software tests do not prove an external solver/HPC run or scientific acceptance. Without exact external evidence retain `EXTERNAL_EXECUTION_NOT_VERIFIED`.

## Mathematics

For canonical quantities, convergence is accepted only when

\[
|x_{n+1}-x_n|\le a_{tol}+r_{tol}\max(|x_n|,|x_{n+1}|).
\]

The absolute tolerance has the same dimension as the state; the relative tolerance is dimensionless.
