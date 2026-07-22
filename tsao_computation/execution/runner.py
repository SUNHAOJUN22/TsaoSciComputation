from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime, timezone

from ..security.process import safe_run
from .typing_compat import CommandPlanLike


@dataclass(frozen=True, slots=True)
class ExecutionRecord:
    argv: tuple[str, ...]
    returncode: int
    stdout_sha256: str
    stderr_sha256: str
    started_at: str
    completed_at: str
    completed: bool


def run_plan(plan: CommandPlanLike, *, timeout: float = 300.0) -> ExecutionRecord:
    started = datetime.now(timezone.utc).isoformat()
    result = safe_run(plan.argv, cwd=plan.cwd, timeout=timeout, env=plan.environment)
    completed = datetime.now(timezone.utc).isoformat()
    return ExecutionRecord(
        tuple(plan.argv),
        result.returncode,
        hashlib.sha256(result.stdout.encode()).hexdigest(),
        hashlib.sha256(result.stderr.encode()).hexdigest(),
        started,
        completed,
        result.returncode == 0,
    )
