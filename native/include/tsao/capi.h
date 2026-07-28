#pragma once

#include <stdint.h>

#if defined(_WIN32)
  #if defined(TSAO_NATIVE_BUILD)
    #define TSAO_NATIVE_API __declspec(dllexport)
  #else
    #define TSAO_NATIVE_API __declspec(dllimport)
  #endif
#else
  #define TSAO_NATIVE_API __attribute__((visibility("default")))
#endif

#ifdef __cplusplus
extern "C" {
#endif

#define TSAO_NATIVE_ABI_VERSION 1u

enum TsaoNativeBackendMask {
    TSAO_NATIVE_BACKEND_CPU = 1u << 0,
    TSAO_NATIVE_BACKEND_OPENMP = 1u << 1,
    TSAO_NATIVE_BACKEND_CUDA = 1u << 2,
    TSAO_NATIVE_BACKEND_HIP = 1u << 3,
    TSAO_NATIVE_BACKEND_SYCL = 1u << 4
};

typedef struct TsaoNativeHardwareSummary {
    uint32_t abi_version;
    uint32_t logical_cpu_count;
    uint32_t backend_mask;
    uint32_t accelerator_count;
} TsaoNativeHardwareSummary;

TSAO_NATIVE_API uint32_t tsao_native_abi_version(void);
TSAO_NATIVE_API int32_t tsao_native_probe(TsaoNativeHardwareSummary* output);

#ifdef __cplusplus
}
#endif
