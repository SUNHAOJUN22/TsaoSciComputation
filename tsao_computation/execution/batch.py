from __future__ import annotations

import os
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

from .runner import ExecutionRecord, run_plan
from .typing_compat import CommandPlanLike


@dataclass(frozen=True, slots=True)
class BatchExecutionResult:
    records: tuple[ExecutionRecord, ...]
    completed: bool
    failed_indices: tuple[int, ...]


def run_plan_batch(
    plans: tuple[CommandPlanLike, ...] | list[CommandPlanLike],
    *,
    timeout: float = 300.0,
    max_workers: int | None = None,
) -> BatchExecutionResult:
    items = tuple(plans)
    if not items:
        return BatchExecutionResult((), True, ())
    workers = min(len(items), max(1, os.cpu_count() or 1)) if max_workers is None else max_workers
    if workers < 1:
        raise ValueError("max_workers must be positive")
    workers = min(workers, len(items))
    with ThreadPoolExecutor(max_workers=workers, thread_name_prefix="tsao-external-plan") as pool:
        futures = [pool.submit(run_plan, plan, timeout=timeout) for plan in items]
        records = tuple(future.result() for future in futures)
    failed = tuple(index for index, record in enumerate(records) if not record.completed)
    return BatchExecutionResult(records, not failed, failed)


run_plans = run_plan_batch
