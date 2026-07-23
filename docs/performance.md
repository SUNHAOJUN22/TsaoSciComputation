# Performance engineering

Performance changes are evidence-led and may not remove scientific, security, provenance, or acceptance gates.

The 3.0.0 architecture keeps the CLI import surface small, loads immutable JSON registries lazily through bounded caches, caps concurrent solver probes, avoids shell command construction, and streams manifests and release archives file-by-file.

## Recorded local baseline

`benchmarks/latest.json` is the machine-readable source of truth. The current snapshot was produced with Python 3.13.14 and measures orchestration overhead only—no scientific solver execution:

| Operation | Median result |
|---|---:|
| CLI module import | 15.841 ms |
| 164-capability registry cold load | 3.177 ms |
| Capability registry cached access | 0.0006 ms |
| 27-adapter registry cold load | 0.168 ms |
| 20-workflow registry cold load | 0.229 ms |
| Route decision | 0.1302 ms |
| Conservative parser over 5 MiB fixture | 643.32 MiB/s |

These values are environment-specific. Regression decisions must compare like-for-like hardware, interpreter, filesystem, and input size. A faster number on different hardware is not evidence of a code improvement, and no result in this file is a solver benchmark.
