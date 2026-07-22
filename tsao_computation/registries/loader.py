from __future__ import annotations

import json
from functools import lru_cache
from typing import Any, cast

from ..paths import REGISTRY_ROOT


@lru_cache(maxsize=8)
def _load(name: str) -> tuple[Any, ...] | dict[str, Any]:
    path = (REGISTRY_ROOT / name).resolve()
    if path.parent != REGISTRY_ROOT.resolve():
        raise ValueError("registry path escaped root")
    data = json.loads(path.read_text(encoding="utf-8"))
    return tuple(data) if isinstance(data, list) else data


def capabilities() -> tuple[dict[str, Any], ...]:
    return cast(tuple[dict[str, Any], ...], _load("capabilities.json"))


def adapters() -> tuple[dict[str, Any], ...]:
    return cast(tuple[dict[str, Any], ...], _load("adapters.json"))


def workflows() -> tuple[dict[str, Any], ...]:
    return cast(tuple[dict[str, Any], ...], _load("workflows.json"))


def units() -> dict[str, Any]:
    return cast(dict[str, Any], _load("units.json"))


def clear_registry_caches() -> None:
    _load.cache_clear()
