# Performance engineering V9

- Baseline commit: `c2c0eca0fd6bf81cc3cbb1ff29489eefbcba58fd`
- Candidate commit: `65101d3989b7890a5dd884e01b383c229e88d749`
- Audit run: `30232461778`
- Status: `PASS`
- `verify_all --profile all`: `12.065 s` to `11.109 s` (`1.09x`)
- Workflow routing: `258.77x`
- 5 MiB parser throughput: `1.02x`
- Peak RSS ratio: `1.00x`
- Mandatory runtime dependencies added: `0`

The measurements are same-host repository orchestration telemetry. They do not claim faster external scientific solvers or production HPC execution.
