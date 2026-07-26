# Performance engineering V8

- Baseline commit: `f3f533160cc64766fec862b96822db89b468e53c`
- Audit run: `30212227899`
- Status: `PASS`
- Parser throughput: `19.54 MiB/s` (`1.33x` baseline)
- Route decision: `0.03383 ms` (`3.75x` baseline)
- Cached adapter lookup: `0.1077 us`
- Repository walk: `8.607 ms`
- Mandatory runtime dependencies added: `0`

Timings are same-host orchestration telemetry, not solver-performance or production-HPC claims. Correctness, fail-closed semantics, deterministic ordering, cache invalidation, packaging reproducibility and cross-platform CI remain mandatory.
