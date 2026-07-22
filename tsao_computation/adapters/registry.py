from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

from ..registries import adapters as adapter_records
from .base import Adapter, AdapterProbe


def list_adapters() -> tuple[Adapter, ...]:
    return tuple(Adapter(r) for r in adapter_records())


def get_adapter(slug: str) -> Adapter:
    for adapter in list_adapters():
        if adapter.slug == slug:
            return adapter
    raise KeyError(f"unknown adapter: {slug}")


def probe_all(max_workers: int = 8) -> tuple[AdapterProbe, ...]:
    items = list_adapters()
    workers = max(1, min(max_workers, len(items)))
    with ThreadPoolExecutor(max_workers=workers) as pool:
        results = tuple(pool.map(lambda a: a.probe(), items))
    return tuple(sorted(results, key=lambda x: x.slug))
