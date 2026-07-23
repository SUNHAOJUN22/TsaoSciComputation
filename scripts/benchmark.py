from __future__ import annotations

import json
import statistics
import subprocess  # nosec B404
import sys
import time
from collections.abc import Callable
from pathlib import Path
from typing import TypeVar

import _bootstrap  # noqa: F401
from tsao_computation.adapters import get_adapter
from tsao_computation.registries import adapters, capabilities, clear_registry_caches, workflows
from tsao_computation.routing import route_question

T = TypeVar("T")


def median_seconds(operation: Callable[[], T], repeats: int = 11) -> float:
    samples: list[float] = []
    for _ in range(repeats):
        started = time.perf_counter()
        operation()
        samples.append(time.perf_counter() - started)
    return statistics.median(samples)


def cold_registry_seconds(loader: Callable[[], T], repeats: int = 9) -> float:
    def operation() -> T:
        clear_registry_caches()
        return loader()

    return median_seconds(operation, repeats)


def import_seconds() -> float:
    code = (
        "import time; started=time.perf_counter(); "
        "import tsao_computation.cli; print(time.perf_counter()-started)"
    )
    values = [
        float(subprocess.check_output([sys.executable, "-c", code], text=True).strip())  # nosec B603
        for _ in range(9)
    ]
    return statistics.median(values)


def parser_throughput_mib_s() -> float:
    payload = ("iteration converged completed\n" * 180_000)[: 5 * 1024 * 1024]
    adapter = get_adapter("orca")
    seconds = median_seconds(lambda: adapter.parse(payload), repeats=7)
    return len(payload.encode("utf-8")) / (1024 * 1024) / seconds


def main() -> int:
    clear_registry_caches()
    capabilities()
    adapters()
    workflows()
    result = {
        "schema_version": "1.0",
        "python": sys.version,
        "cli_import_median_ms": round(import_seconds() * 1000, 3),
        "capability_registry_cold_median_ms": round(cold_registry_seconds(capabilities) * 1000, 3),
        "capability_registry_cached_median_ms": round(median_seconds(capabilities) * 1000, 4),
        "adapter_registry_cold_median_ms": round(cold_registry_seconds(adapters) * 1000, 3),
        "workflow_registry_cold_median_ms": round(cold_registry_seconds(workflows) * 1000, 3),
        "route_decision_median_ms": round(
            median_seconds(lambda: route_question("OpenFOAM non-Newtonian polymer extrusion"))
            * 1000,
            4,
        ),
        "parser_5mib_throughput_mib_s": round(parser_throughput_mib_s(), 2),
        "claim_boundary": "Local orchestration microbenchmarks; no solver execution measured.",
    }
    output = Path("benchmarks/latest.json")
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
