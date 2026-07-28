from __future__ import annotations

import json
from functools import cache
from typing import Any, cast

from ..paths import REGISTRY_ROOT

_RESOLVED_REGISTRY_ROOT = REGISTRY_ROOT.resolve()


@cache
def _load(name: str) -> tuple[Any, ...] | dict[str, Any]:
    path = (_RESOLVED_REGISTRY_ROOT / name).resolve()
    if path.parent != _RESOLVED_REGISTRY_ROOT:
        raise ValueError("registry path escaped root")
    data = json.loads(path.read_bytes())
    return tuple(data) if isinstance(data, list) else data


def capabilities() -> tuple[dict[str, Any], ...]:
    return cast(tuple[dict[str, Any], ...], _load("capabilities.json"))


def adapters() -> tuple[dict[str, Any], ...]:
    return cast(tuple[dict[str, Any], ...], _load("adapters.json"))


def accelerators() -> tuple[dict[str, Any], ...]:
    return cast(tuple[dict[str, Any], ...], _load("accelerators.json"))


def workflows() -> tuple[dict[str, Any], ...]:
    return cast(tuple[dict[str, Any], ...], _load("workflows.json"))


def units() -> dict[str, Any]:
    return cast(dict[str, Any], _load("units.json"))


def clear_registry_caches() -> None:
    from ..adapters.registry import clear_adapter_caches
    from ..routing.router import clear_routing_caches

    clear_adapter_caches()
    clear_routing_caches()
    _load.cache_clear()
