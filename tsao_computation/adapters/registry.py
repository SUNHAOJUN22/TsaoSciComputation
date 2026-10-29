from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from functools import cache

from ..errors import SecurityError
from ..registries import adapters as adapter_records
from ..security.process import _verified_python_modules
from . import base
from .base import Adapter, AdapterProbe

_MAX_GROUP_REQUEST_CHARS = 16_384


@dataclass(frozen=True, slots=True)
class _ModuleCandidate:
    adapter: Adapter
    declared: str
    found: str


@dataclass(frozen=True, slots=True)
class _ModuleGroup:
    interpreter: str
    candidates: tuple[_ModuleCandidate, ...]
    modules: tuple[str, ...]


def _probe_group_or_adapter(task: _ModuleGroup | Adapter) -> tuple[AdapterProbe, ...] | None:
    if isinstance(task, Adapter):
        return (task.probe(),)
    try:
        observed_missing = _verified_python_modules(task.interpreter, task.modules)
    except SecurityError:
        return None
    if observed_missing is None:
        return None
    missing = frozenset(observed_missing)
    results = []
    for candidate in task.candidates:
        adapter = candidate.adapter
        own_missing = tuple(name for name in adapter.python_modules if name in missing)
        observed = adapter._resolved_probe_result(candidate.declared, candidate.found, own_missing)
        # A group contains only single-candidate adapters. Preserve probe()'s
        # exhausted-candidate shape, including executable=None on failure.
        results.append(
            observed
            if observed.available
            else AdapterProbe(adapter.slug, False, None, observed.reason)
        )
    return tuple(results)


def _probe_tasks(items: tuple[Adapter, ...]) -> tuple[_ModuleGroup | Adapter, ...]:
    """Combine metadata requests only within this call and exact invoked Python path.

    Never resolve a Python symlink for grouping: two virtual environments can
    share the same executable inode but have different installed packages. Keep
    multi-candidate adapters on their original ordered, short-circuit path.
    """

    tasks: list[_ModuleGroup | Adapter] = []
    candidates_by_interpreter: dict[str, list[_ModuleCandidate]] = {}
    for adapter in items:
        declared = adapter.record.get("executables", [])
        modules = adapter.python_modules
        canonical_names = all(
            name.isascii() and all(part.isidentifier() for part in name.split("."))
            for name in modules
        )
        if len(declared) != 1 or not modules or not canonical_names:
            tasks.append(adapter)
            continue
        candidate = str(declared[0])
        found = base._resolve_executable(candidate)
        if not found:
            tasks.append(adapter)
            continue
        interpreter = base._module_probe_interpreter(candidate, found)
        candidates_by_interpreter.setdefault(interpreter, []).append(
            _ModuleCandidate(adapter, candidate, found)
        )
    for interpreter, candidates in candidates_by_interpreter.items():
        modules = tuple(
            dict.fromkeys(name for item in candidates for name in item.adapter.python_modules)
        )
        # Retain the existing bounded response protocol. An unusually large
        # union must not make independently verifiable adapters fail together.
        if len(json.dumps(modules)) > _MAX_GROUP_REQUEST_CHARS:
            tasks.extend(item.adapter for item in candidates)
        else:
            tasks.append(_ModuleGroup(interpreter, tuple(candidates), modules))
    return tuple(tasks)


@cache
def list_adapters() -> tuple[Adapter, ...]:
    return tuple(Adapter(record) for record in adapter_records())


@cache
def _adapter_index() -> dict[str, Adapter]:
    return {adapter.slug: adapter for adapter in list_adapters()}


def get_adapter(slug: str) -> Adapter:
    try:
        return _adapter_index()[slug]
    except KeyError as error:
        raise KeyError(f"unknown adapter: {slug}") from error


def probe_all(max_workers: int = 8) -> tuple[AdapterProbe, ...]:
    items = list_adapters()
    workers = max(1, min(max_workers, len(items)))
    tasks = _probe_tasks(items)
    results: list[AdapterProbe] = []
    fallback: list[Adapter] = []
    with ThreadPoolExecutor(max_workers=workers) as pool:
        for task, observed in zip(tasks, pool.map(_probe_group_or_adapter, tasks), strict=True):
            if observed is None and isinstance(task, _ModuleGroup):
                # Retry through the original per-adapter path after an invalid
                # group observation. One bad request must not disqualify its
                # healthy peers, and retries share the same bounded executor.
                fallback.extend(candidate.adapter for candidate in task.candidates)
            elif observed is not None:
                results.extend(observed)
        results.extend(pool.map(Adapter.probe, fallback))
    return tuple(sorted(results, key=lambda result: result.slug))


def clear_adapter_caches() -> None:
    _adapter_index.cache_clear()
    list_adapters.cache_clear()
