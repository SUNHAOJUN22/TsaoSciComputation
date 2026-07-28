from __future__ import annotations

import sys
from pathlib import Path

import pytest

from tsao_computation.adapters.base import CommandPlan
from tsao_computation.execution import run_plan_batch


def test_batch_execution_preserves_order_and_failure_indices(tmp_path: Path) -> None:
    plans = [
        CommandPlan((sys.executable, "-c", "print('first')"), tmp_path, {}, "test"),
        CommandPlan((sys.executable, "-c", "raise SystemExit(4)"), tmp_path, {}, "test"),
        CommandPlan((sys.executable, "-c", "print('third')"), tmp_path, {}, "test"),
    ]
    result = run_plan_batch(plans, timeout=10, max_workers=2)
    assert len(result.records) == 3
    assert [record.returncode for record in result.records] == [0, 4, 0]
    assert result.completed is False
    assert result.failed_indices == (1,)


def test_empty_batch_and_worker_validation() -> None:
    result = run_plan_batch([])
    assert result.completed is True
    assert result.records == ()
    with pytest.raises(ValueError, match="positive"):
        run_plan_batch(
            [
                CommandPlan(
                    (sys.executable, "-c", "pass"),
                    Path("."),
                    {},
                    "test",
                )
            ],
            max_workers=0,
        )
