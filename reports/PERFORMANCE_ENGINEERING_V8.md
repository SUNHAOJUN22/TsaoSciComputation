# Performance engineering V8

- Baseline commit: `f3f533160cc64766fec862b96822db89b468e53c`
- Audit run: `30212422333`
- Status: `PASS`
- Parser throughput: `18.85 MiB/s` (`1.24x` baseline)
- Route decision: `0.03347 ms` (`3.86x` baseline)
- Cached adapter lookup: `0.1082 us`
- Repository walk: `8.286 ms`
- Mandatory runtime dependencies added: `0`

Timings are same-host orchestration telemetry, not solver-performance or production-HPC claims. Correctness, fail-closed semantics, deterministic ordering, cache invalidation, packaging reproducibility and cross-platform CI remain mandatory.
