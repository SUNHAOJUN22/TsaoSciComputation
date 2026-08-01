from __future__ import annotations

from tsao_computation.routing import route_question
from tsao_computation.routing.router import (
    _route_alias_cached,
    _route_cached,
    clear_routing_caches,
)


def test_case_and_whitespace_variants_share_canonical_scoring_cache() -> None:
    clear_routing_caches()

    first = route_question("OpenFOAM   Non-Newtonian Polymer Extrusion")
    first_cache = _route_cached.cache_info()
    second = route_question("  openfoam non-newtonian   polymer extrusion  ")
    second_cache = _route_cached.cache_info()

    assert second == first
    assert first_cache.misses == 1
    assert second_cache.misses == first_cache.misses
    assert second_cache.hits == first_cache.hits + 1


def test_routing_cache_clear_removes_alias_and_canonical_entries() -> None:
    clear_routing_caches()
    route_question("OpenFOAM polymer extrusion")
    assert _route_alias_cached.cache_info().currsize == 1
    assert _route_cached.cache_info().currsize == 1

    clear_routing_caches()
    assert _route_alias_cached.cache_info().currsize == 0
    assert _route_cached.cache_info().currsize == 0
