# Accelerated native backend architecture

TsaoSciComputation is a scientific-computation **control plane**, not a replacement for
GROMACS, LAMMPS, OpenMM, PySCF, DOLFINx, OpenFOAM, Aspen or other domain solvers. The
performance architecture therefore keeps orchestration, contracts, routing, validation,
uncertainty and provenance in Python while moving only measured numerical or data-path
hotspots behind stable native interfaces.

## Repository-wide audit conclusion

The current `main` baseline contains 570 source and project files before this change:

- 152 Python files with about 17,900 lines;
- one C++ implementation, one C++ smoke test and one public C header;
- no repository-owned CUDA kernel;
- substantial JSON, YAML and Markdown registries, adapter metadata and evidence assets.

Static analysis of every Python module found that repository-local work is dominated by file
walking, JSON/YAML parsing, hashing, validation, subprocess planning and bounded workflow
orchestration. Those operations are generally latency- and I/O-bound. Rewriting them in CUDA
would add transfer, deployment and maintenance costs without a defensible speedup. The correct
optimization targets are caching, streaming, bounded task parallelism, fewer filesystem passes
and native interoperability.

The expensive scientific numerics remain in external solvers. Their supported GPU, MPI,
OpenMP, Kokkos or vendor-library paths should be preferred before creating a new kernel here.

## Implemented native boundary

The source-only `native/` library now provides a versioned C ABI that:

1. reports compiled CPU, OpenMP and optional CUDA Runtime support;
2. discovers CUDA devices through the CUDA Runtime when the toolkit was available at build
   time;
3. exposes device name, memory and compute capability without executing a scientific solver;
4. remains buildable and testable without CUDA;
5. is consumed from Python through an optional `ctypes` bridge;
6. merges native discovery with CLI-based NVIDIA, AMD, SYCL and OpenCL probing without
   double-counting devices.

The C ABI is the compatibility foundation because it can be called from Python (`ctypes` or
`cffi`), Fortran (`ISO_C_BINDING`), Julia (`ccall`), Rust FFI, C# P/Invoke and C++. A pybind11
module may later provide a more ergonomic Python API, but it should remain an adapter over the
stable C ABI rather than the only integration surface.

Build and verify:

```bash
cmake -S native -B build/native -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON
cmake --build build/native --config Release --parallel
ctest --test-dir build/native -C Release --output-on-failure

# The repository verifier also exercises the Python/native bridge.
python scripts/verify_native_core.py
```

CUDA Runtime discovery is optional and auto-detected. Disable it explicitly for a portable
CPU-only build:

```bash
cmake -S native -B build/native-cpu \
  -DTSAO_NATIVE_ENABLE_CUDA_RUNTIME=OFF \
  -DTSAO_NATIVE_ENABLE_OPENMP=ON
```

## Acceleration decision matrix

| Workload evidence | First implementation path | Native/accelerated candidate | Required gate |
|---|---|---|---|
| Python control-plane latency | cache, stream, reduce filesystem passes | C++ only after profiling | same-tree benchmark and behavior equivalence |
| Dense BLAS/eigensolver hotspot | nvmath-python or solver-native GPU build | cuBLAS/cuBLASLt, cuSOLVER | CPU reference, precision and condition-number evidence |
| Sparse FEM/CFD linear solve | solver-native GPU backend | cuSPARSE, cuDSS, AmgX, Kokkos | matrix class, convergence and preconditioner evidence |
| FFT/particle-mesh/spectral step | solver-native GPU backend | cuFFT or nvmath-python FFT | normalization and numerical-equivalence evidence |
| High-order tensor contraction | framework-native implementation | cuTENSOR | layout, contraction plan and memory evidence |
| MACE/NequIP/Allegro-style equivariant ML | supported framework integration | cuEquivariance | model/version compatibility and end-to-end validation |
| Monte Carlo or stochastic ensemble | vectorized CPU baseline first | cuRAND plus CUDA kernel or task/MPI parallelism | reproducibility and statistical-equivalence evidence |
| Multi-GPU domain decomposition | solver-supported MPI/GPU route | NCCL or NVSHMEM only when supported | topology, communication and scaling evidence |
| Large trajectory/checkpoint path | chunking and asynchronous I/O first | nvCOMP, GPUDirect Storage | storage topology and end-to-end throughput evidence |
| Validated edge surrogate | export a fixed model and calibration envelope | TensorRT; Holoscan for streaming graphs | accuracy, drift, latency, power and fallback evidence |
| Cross-language tensor/data exchange | stable schemas and file formats | DLPack and Arrow C Data Interface | ownership, lifetime and zero-copy correctness |

## C++ and CUDA migration rules

Do not translate Python by file count. Migrate a function only when profiling shows that it is
both material and suitable for native execution.

A native numerical kernel must have:

- a CPU or analytical reference implementation;
- explicit shape, stride, ownership and alignment contracts;
- bounds, empty-input, NaN/Inf and overflow behavior;
- FP64/FP32/mixed-precision policy and deterministic-mode behavior;
- numerical-equivalence tolerances tied to the scientific method;
- memory-leak, race, sanitizer and device-error tests;
- CPU fallback and unsupported-hardware behavior;
- same-host performance, energy and thermal measurements;
- unchanged convergence, physical-validation and acceptance gates.

Use C++20 plus OpenMP for portable CPU kernels. Use Kokkos when one repository-owned kernel
must span CUDA, HIP and SYCL. Use direct CUDA C++ only when NVIDIA-specific performance is a
measured requirement and the maintenance tradeoff is accepted.

## Phased implementation plan

### Phase 1 — completed foundation

- Stable C ABI and CMake build.
- Optional OpenMP and CUDA Runtime detection.
- Runtime device inventory through the C ABI.
- Python `ctypes` bridge and merged accelerator inventory.
- CTest and pytest coverage with CPU-only fallback.

### Phase 2 — packaging and interoperability

- Package platform-specific native wheels with an isolated build backend such as
  scikit-build-core while retaining the pure-Python wheel.
- Add install-time selection for CPU-only and CUDA-enabled native artifacts; never make CUDA a
  core dependency.
- Add DLPack/Arrow ownership contracts for future array and table exchange.
- Add a thin optional pybind11 facade only where typed NumPy-buffer ergonomics materially help.

### Phase 3 — measured native kernels

- Profile real user workflows and select at most one high-impact repository-owned numerical
  kernel.
- Implement CPU reference and C++20/OpenMP version first.
- Add CUDA/Kokkos implementation only after reference correctness and performance thresholds
  are fixed.
- Add benchmark evidence by problem size; never publish a single unqualified speedup number.

### Phase 4 — solver and edge deployment

- Bind exact external-solver versions and build features to acceleration plans.
- Record driver, runtime, GPU architecture, device binding, precision and environment hashes.
- For edge targets, validate TensorRT/Holoscan pipelines on the actual Jetson or IGX class,
  including power mode, thermal throttling and CPU fallback.

## Claim boundary

A detected CUDA runtime, GPU, Python module or candidate library does not establish that an
external solver supports it or that a calculation is faster, converged, physically valid or
scientifically accepted. Those claims require bound execution and validation evidence.
