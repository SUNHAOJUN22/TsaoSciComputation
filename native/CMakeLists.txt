cmake_minimum_required(VERSION 3.20)

project(TsaoNativeCore VERSION 1.0.0 LANGUAGES CXX)

option(TSAO_NATIVE_ENABLE_OPENMP "Enable the portable OpenMP CPU backend when available" ON)

add_library(tsao_native SHARED src/capi.cpp)
target_compile_features(tsao_native PUBLIC cxx_std_20)
target_compile_definitions(tsao_native PRIVATE TSAO_NATIVE_BUILD=1)
target_include_directories(
  tsao_native
  PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:include>
)
set_target_properties(
  tsao_native
  PROPERTIES
    CXX_VISIBILITY_PRESET hidden
    VISIBILITY_INLINES_HIDDEN YES
    POSITION_INDEPENDENT_CODE YES
)

if(TSAO_NATIVE_ENABLE_OPENMP)
  find_package(OpenMP QUIET)
  if(OpenMP_CXX_FOUND)
    target_link_libraries(tsao_native PRIVATE OpenMP::OpenMP_CXX)
  endif()
endif()

include(CTest)
if(BUILD_TESTING)
  add_executable(tsao_native_smoke tests/native_smoke.cpp)
  target_compile_features(tsao_native_smoke PRIVATE cxx_std_20)
  target_link_libraries(tsao_native_smoke PRIVATE tsao_native)
  add_test(NAME tsao_native_smoke COMMAND tsao_native_smoke)
endif()

include(GNUInstallDirs)
install(
  TARGETS tsao_native
  RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
  LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
  ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
)
install(FILES include/tsao/capi.h DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/tsao)
