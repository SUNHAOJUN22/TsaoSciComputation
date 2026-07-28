#include "tsao/capi.h"

#include <cstdlib>
#include <cstring>

int main() {
    if (tsao_native_abi_version() != TSAO_NATIVE_ABI_VERSION) {
        return EXIT_FAILURE;
    }
    if (std::strcmp(tsao_native_api_version(), TSAO_NATIVE_API_VERSION) != 0) {
        return EXIT_FAILURE;
    }
    const char* capabilities = tsao_native_capabilities_json();
    if (capabilities == nullptr || std::strstr(capabilities, "\"cpu\"") == nullptr) {
        return EXIT_FAILURE;
    }
    TsaoNativeHardwareSummary summary{};
    if (tsao_native_probe(&summary) != 0) {
        return EXIT_FAILURE;
    }
    if (summary.abi_version != TSAO_NATIVE_ABI_VERSION || summary.logical_cpu_count < 1u) {
        return EXIT_FAILURE;
    }
    if ((summary.backend_mask & TSAO_NATIVE_BACKEND_CPU) == 0u) {
        return EXIT_FAILURE;
    }
    if (tsao_native_probe(nullptr) == 0) {
        return EXIT_FAILURE;
    }
    return EXIT_SUCCESS;
}
