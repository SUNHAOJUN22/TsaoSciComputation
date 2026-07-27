# Performance engineering V9

- Baseline commit: `c2c0eca0fd6bf81cc3cbb1ff29489eefbcba58fd`
- Candidate commit: `852ffa461aa50d7e021623f8ff0692468b71e4cb`
- Audit run: `30231886878`
- Status: `PASS`
- `verify_all --profile all`: `9.508 s` to `8.796 s` (`1.08x`)
- Workflow routing: `247.70x`
- 5 MiB parser throughput: `0.97x`
- Peak RSS ratio: `1.00x`
- Mandatory runtime dependencies added: `0`

The measurements are same-host repository orchestration telemetry. They do not claim faster external scientific solvers or production HPC execution.
