from __future__ import annotations

import math

from tsao_computation.accelerators import planner
from tsao_computation.registries import clear_registry_caches
from tsao_computation.routing import router
from tsao_computation.routing.router import route_question
from tsao_computation.validation.scientific_benchmarks import (
    harmonic_oscillator,
    pfr_first_order,
    poiseuille_flow,
)


def test_acceleration_profile_lookup_is_cached_and_clearable() -> None:
    planner.clear_acceleration_caches()
    first = planner._profile("gromacs")
    second = planner._profile("gromacs")
    assert first is second
    assert planner._profile.cache_info().hits == 1

    clear_registry_caches()
    assert planner._profile.cache_info().currsize == 0


def test_semantically_equivalent_route_questions_share_one_cache_key() -> None:
    router.clear_routing_caches()
    first = route_question("molecular dynamics simulation")
    second = route_question("  MOLECULAR DYNAMICS SIMULATION\t")
    third = route_question("molecular dynamics simulation   ")

    assert first is second is third
    assert router._route_cached.cache_info().currsize == 1


def test_optimized_scientific_kernels_preserve_equations_and_acceptance() -> None:
    flow = poiseuille_flow()
    reactor = pfr_first_order()
    oscillator = harmonic_oscillator()

    assert flow.passed
    assert reactor.passed
    assert oscillator.passed
    assert math.isclose(reactor.expected, math.exp(-1.4), rel_tol=0.0, abs_tol=0.0)
    assert flow.relative_error <= flow.tolerance
    assert oscillator.relative_error <= oscillator.tolerance
