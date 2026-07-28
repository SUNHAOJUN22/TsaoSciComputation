# Tsao Native Core

`native/` is an optional C++20 compatibility and acceleration boundary for
TsaoSciComputation. The Python control plane remains the authoritative layer for
Skill instructions, contracts, routing, validation, uncertainty, provenance, and
scientific acceptance.

The initial native core deliberately exposes a narrow versioned C ABI:

- `tsao_native_abi_version`
- `tsao_native_probe`

The library always reports the CPU backend and reports OpenMP only when the
compiler enabled it. CUDA, HIP, and SYCL bits are reserved for separately built
and validated backends. This repository does not bundle CUDA, ROCm, oneAPI,
Kokkos, professional solvers, licenses, or live accelerator evidence.

Build and test:

```bash
cmake -S native -B build/native -DCMAKE_BUILD_TYPE=Release
cmake --build build/native --config Release
ctest --test-dir build/native -C Release --output-on-failure
```

Future native kernels must preserve the C ABI, provide CPU reference behavior,
and pass numerical-equivalence, convergence, physical-validation, memory,
performance, energy, and fallback gates before they can support an acceleration
claim.
