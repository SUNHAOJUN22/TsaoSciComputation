from __future__ import annotations

import os
import subprocess  # nosec B404 - used only to classify the runner's timeout exception
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

from ..errors import SecurityError
from .resources import (
    ExecutionResourceBroker,
    ExecutionResourceCapacity,
    ExecutionResourceClaim,
    validate_resource_binding,
)
from .runner import ExecutionAuthorization, ExecutionRecord, run_plan
from .typing_compat import CommandPlanLike

_DEFAULT_MAX_EXTERNAL_PLANS = 4


@dataclass(frozen=True, slots=True)
class BatchExecutionFailure:
    """A process-level batch failure without copying possibly sensitive argv text."""

    index: int
    reason: str
    error_type: str


@dataclass(frozen=True, slots=True)
class BatchExecutionResult:
    records: tuple[ExecutionRecord, ...]
    completed: bool
    failed_indices: tuple[int, ...]
    resource_capacity_sha256: str | None = None
    resource_claim_sha256s: tuple[str, ...] = ()
    record_indices: tuple[int, ...] = ()
    failures: tuple[BatchExecutionFailure, ...] = ()


def _default_workers(plan_count: int) -> int:
    return min(plan_count, max(1, min(_DEFAULT_MAX_EXTERNAL_PLANS, os.cpu_count() or 1)))


def run_plan_batch(
    plans: tuple[CommandPlanLike, ...] | list[CommandPlanLike],
    *,
    authorizations: tuple[ExecutionAuthorization, ...] | list[ExecutionAuthorization] | None = None,
    timeout: float = 300.0,
    max_workers: int | None = None,
    resource_claims: tuple[ExecutionResourceClaim, ...]
    | list[ExecutionResourceClaim]
    | None = None,
    resource_capacity: ExecutionResourceCapacity | None = None,
) -> BatchExecutionResult:
    """Execute authorized plans and retain completed siblings when a process fails.

    ``records`` contains processes that returned normally, in input order;
    ``record_indices`` maps each record back to its plan. Timeouts and OS-level
    launch failures are represented in ``failures`` and ``failed_indices``.
    Security/contract violations still raise and are never converted to success.
    """
    items = tuple(plans)
    if not items:
        return BatchExecutionResult((), True, ())
    if authorizations is None or len(authorizations) != len(items):
        raise SecurityError("each external command plan requires one matching authorization")
    auth_items = tuple(authorizations)
    workers = _default_workers(len(items)) if max_workers is None else max_workers
    if workers < 1:
        raise ValueError("max_workers must be positive")
    workers = min(workers, len(items))

    broker: ExecutionResourceBroker | None = None
    claim_items: tuple[ExecutionResourceClaim, ...] = ()
    if resource_claims is not None or resource_capacity is not None:
        if resource_claims is None or resource_capacity is None:
            raise SecurityError("resource claims and capacity must be provided together")
        if len(resource_claims) != len(items):
            raise SecurityError("each command plan requires one matching resource claim")
        claim_items = tuple(resource_claims)
        broker = ExecutionResourceBroker(resource_capacity)
        for plan, claim in zip(items, claim_items, strict=True):
            validate_resource_binding(plan.environment, claim)
            broker._assert_fits(claim)

    def execute(index: int) -> ExecutionRecord:
        plan = items[index]
        authorization = auth_items[index]
        if broker is None:
            return run_plan(plan, authorization=authorization, timeout=timeout)
        claim = claim_items[index]
        with broker.lease(claim):
            return run_plan(plan, authorization=authorization, timeout=timeout)

    outcomes: list[ExecutionRecord | BatchExecutionFailure | None] = [None] * len(items)
    with ThreadPoolExecutor(max_workers=workers, thread_name_prefix="tsao-external-plan") as pool:
        futures = [pool.submit(execute, index) for index in range(len(items))]
        for index, future in enumerate(futures):
            try:
                outcomes[index] = future.result()
            except subprocess.TimeoutExpired as error:
                outcomes[index] = BatchExecutionFailure(
                    index=index,
                    reason="timeout",
                    error_type=type(error).__name__,
                )
            except OSError as error:
                outcomes[index] = BatchExecutionFailure(
                    index=index,
                    reason="process_start_failed",
                    error_type=type(error).__name__,
                )
    records = tuple(outcome for outcome in outcomes if isinstance(outcome, ExecutionRecord))
    record_indices = tuple(
        index for index, outcome in enumerate(outcomes) if isinstance(outcome, ExecutionRecord)
    )
    failures = tuple(outcome for outcome in outcomes if isinstance(outcome, BatchExecutionFailure))
    failed = tuple(
        sorted(
            {failure.index for failure in failures}
            | {
                index
                for index, record in zip(record_indices, records, strict=True)
                if not record.completed
            }
        )
    )
    return BatchExecutionResult(
        records,
        not failed,
        failed,
        None if resource_capacity is None else resource_capacity.sha256,
        tuple(claim.sha256 for claim in claim_items),
        record_indices,
        failures,
    )


run_plans = run_plan_batch
