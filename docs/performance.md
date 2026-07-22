# Performance engineering

Performance changes are evidence-led and may not remove scientific, security, provenance, or acceptance gates.

The 3.0.0 architecture keeps the CLI import surface small, loads immutable JSON registries lazily through bounded caches, caps concurrent solver probes, avoids shell command construction, and streams manifests and release archives file-by-file.

## Local baseline

The current `benchmarks/latest.json` was produced on Python 3.13.5 in the build environment. It records orchestration overhead only—no scientific solver execution:

| Operation | Median result |
|---|---:|
| CLI module import | 1.951 ms |
| 164-capability registry cold load | 1.333 ms |
| Capability registry cached access | 0.0001 ms |
| 27-adapter registry cold load | 0.067 ms |
| 20-workflow registry cold load | 0.099 ms |
| Route decision | 0.0689 ms |
| Conservative parser over 5 MiB fixture | 731.24 MiB/s |

These values are environment-specific. Regression decisions must compare like-for-like hardware, interpreter, filesystem, and input size.
