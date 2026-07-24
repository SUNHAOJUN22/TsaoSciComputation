# Changelog

## Unreleased

No unreleased changes.

## 3.0.2 — 2026-07-24

- Added a machine-readable, fail-closed C0–C5 scientific-confidence assessment with sequential evidence requirements, JSON Schema validation, and explicit engineering-decision boundaries.
- Added eight deterministic analytical, conservation, and invariant scientific reference benchmarks spanning heat transfer, flow, reactors, molecular dynamics, polymer statistical mechanics, electrostatics, and electrothermal coupling.
- Replaced the permissive Adapter shape check with a strict no-unknown-fields Schema and structured A0–A5 certification evidence; A5 requires versioned live-solver evidence.
- Added a critical coverage policy that prevents repository and high-trust module coverage from silently regressing.
- Added explicit Schema/API compatibility and repository Ruleset desired-state policies without falsely claiming platform settings are enabled.
- Added a structured pull-request template aligned with the single-`main`, evidence-first contribution model.
- Added a branchless weekly dependency-vulnerability audit using a pinned `pip-audit` toolchain and read-only GitHub permissions.
- Added CODEOWNERS for security-sensitive, release, workflow, contract, adapter, and validation paths.
- Added structured software-defect, scientific-validity, and capability-request issue forms with explicit security and data-handling boundaries.
- Added support, conduct, and dependency-maintenance policies aligned with the canonical single-`main` upstream model.
- Added regression tests that prevent branch-creating dependency automation, unpinned maintenance Actions, blank public issues, and unsafe security-report routing.

## 3.0.1 — 2026-07-24

- Hardened adapter parsing so abnormal, failed, incomplete, or negatively converged output cannot be promoted through positive substrings; explicit convergence now requires a completed run.
- Rejected unknown calculation-contract fields, non-object mappings, non-string mapping keys, malformed approval evidence, non-finite values, and invalid validation tolerances instead of coercing them.
- Corrected canonical-state mutation probes to exercise actual illegal transitions and retained the 64/64 controlled mutation gate.
- Separated environment-dependent benchmarks from deterministic release acceptance and made uploaded artifact names collision-safe.
- Made `VERSION` the single authoritative version source for package metadata and runtime `__version__`, with automatic README, CITATION, and Changelog consistency checks.
- Added deterministic SPDX 2.3 and CycloneDX 1.6 SBOMs, complete release Manifests, SHA-256 checksum sets, and isolated Wheel verification.
- Added GitHub/Sigstore provenance and SBOM attestations plus formal GitHub Release publication for immutable tags.
- Expanded private vulnerability reporting, supported-version guidance, coordinated disclosure, and scientific safety boundaries.
- Aligned contribution guidance with the canonical single-`main` policy: upstream retains no feature branches; external contributions use forks.
- Simplified and synchronized the English and Chinese README files around purpose, use, verification, releases, scope, and scientific trust boundaries.

## 3.0.0 — 2026-07-22

- Replaced damaged encoded source-transfer machinery with an ordinary, browsable source tree.
- Consolidated 164 differentiated capabilities, 27 solver adapters, and 20 scientific workflows.
- Added explicit calculation/result/handoff contracts and guarded scientific state transitions.
- Added secure argv-only execution, path confinement, atomic writes, provenance ledgers, and fail-closed acceptance.
- Added package-internal registry assets with synchronization checks for reliable isolated Wheel installation.
- Expanded validation to hundreds of passing tests, high statement and branch coverage, 64 controlled mutation probes, Schema checks, repository audit, and security scan.
- Added deterministic source ZIP/tar.gz builds and byte-identical Wheel rebuild verification.
- Rewrote English/Chinese README files, architecture, trust, performance, security, branch, and release documentation.
- Reduced CI to production workflows with minimal permissions, concurrency cancellation, multi-OS/Python matrices, and pinned Action commits.
