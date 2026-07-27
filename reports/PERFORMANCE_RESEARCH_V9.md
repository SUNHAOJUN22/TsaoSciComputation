# Performance research V9

## Scope

This research supports repository-orchestration and verification optimization only. It does not claim faster external DFT, molecular-dynamics, CFD, finite-element, process-simulation or production-HPC solvers.

## Primary sources reviewed

- Python 3.14 `concurrent.futures`: https://docs.python.org/3.14/library/concurrent.futures.html
- Python 3.14 `os.scandir` and `DirEntry`: https://docs.python.org/3.14/library/os.html#os.scandir
- Python `hashlib.file_digest`: https://docs.python.org/3/library/hashlib.html#hashlib.file_digest
- pyperf benchmark execution and warmup model: https://pyperf.readthedocs.io/en/latest/run_benchmark.html
- pyperf system stability guidance: https://pyperf.readthedocs.io/en/latest/system.html
- GitHub Actions dependency caching: https://docs.github.com/en/actions/concepts/workflows-and-actions/dependency-caching
- GitHub Actions artifacts and job handoff: https://docs.github.com/en/actions/tutorials/store-and-share-data

## Decisions adopted

1. Use a bounded `ThreadPoolExecutor` only to supervise independent subprocess gates. The Python work remains in child processes, and no worker waits on another worker future.
2. Capture parallel task output separately and replay it in declared gate order so diagnostics remain deterministic.
3. Keep tests and coverage before dependent coverage checks; keep the final Manifest check after all post-test checks.
4. Run the two reproducibility source builds concurrently only because their output directories are isolated.
5. Retain `os.scandir`-based deterministic traversal and stream SHA-256 for files larger than one MiB to reduce peak allocation.
6. Use warmups, repeated same-host samples, median, p90 and coefficient of variation for V8/V9 comparison.
7. Keep GitHub dependency caches restricted to package-manager data; do not cache acceptance evidence across commit SHAs.

## Decisions rejected

- No persistent executable-probe cache: an executable can appear or disappear without `PATH` changing.
- No mandatory `pyperf`, `orjson`, NumPy or other runtime dependency.
- No parallel test shards that would weaken the canonical full-suite coverage record.
- No reuse of Manifest, security, coverage or scientific-acceptance evidence from a different commit.
- No unordered parallel logging or fail-open completion behavior.
