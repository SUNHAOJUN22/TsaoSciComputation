#include "tsao/capi.h"

#include <thread>

namespace {

constexpr const char* kCapabilities =
    "{\"abi_version\":1,\"api_version\":\"1.0.0\","
    "\"control_plane\":\"python\",\"native_language\":\"c++20\","
    "\"candidate_backends\":[\"cpu\",\"openmp\",\"cuda\",\"hip\",\"sycl\"],"
    "\"claim_boundary\":\"Build-time capability metadata only; no GPU device, solver support, "
    "speedup, convergence, physical validity, applicability, or authorization is claimed.\"}";

}  // namespace

uint32_t tsao_native_abi_version(void) {
    return TSAO_NATIVE_ABI_VERSION;
}

const char* tsao_native_api_version(void) {
    return TSAO_NATIVE_API_VERSION;
}

const char* tsao_native_capabilities_json(void) {
    return kCapabilities;
}

int32_t tsao_native_probe(TsaoNativeHardwareSummary* output) {
    if (output == nullptr) {
        return 1;
    }
    output->abi_version = TSAO_NATIVE_ABI_VERSION;
    const auto detected = std::thread::hardware_concurrency();
    output->logical_cpu_count = detected == 0u ? 1u : detected;
    output->backend_mask = TSAO_NATIVE_BACKEND_CPU;
#if defined(_OPENMP)
    output->backend_mask |= TSAO_NATIVE_BACKEND_OPENMP;
#endif
#if defined(TSAO_NATIVE_HAS_CUDA)
    output->backend_mask |= TSAO_NATIVE_BACKEND_CUDA;
#endif
#if defined(TSAO_NATIVE_HAS_HIP)
    output->backend_mask |= TSAO_NATIVE_BACKEND_HIP;
#endif
#if defined(TSAO_NATIVE_HAS_SYCL)
    output->backend_mask |= TSAO_NATIVE_BACKEND_SYCL;
#endif
    output->accelerator_count = 0u;
    return 0;
}
