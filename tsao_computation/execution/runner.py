from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone

from ..errors import SecurityError
from ..security.process import safe_run
from .typing_compat import CommandPlanLike


def plan_sha256(plan: CommandPlanLike) -> str:
    payload = {
        "argv": list(plan.argv),
        "cwd": str(plan.cwd.expanduser().resolve(strict=False)),
        "environment": dict(sorted(plan.environment.items())),
        "adapter_slug": getattr(plan, "adapter_slug", None),
        "input_sha256": getattr(plan, "input_sha256", None),
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class ExecutionAuthorization:
    plan_sha256: str
    authorized_by: str
    purpose: str
    explicit_authorization: bool

    @property
    def authorization_sha256(self) -> str:
        encoded = json.dumps(
            {
                "plan_sha256": self.plan_sha256,
                "authorized_by": self.authorized_by,
                "purpose": self.purpose,
                "explicit_authorization": self.explicit_authorization,
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def authorize_plan(
    plan: CommandPlanLike,
    *,
    authorized_by: str,
    purpose: str,
    explicit_authorization: bool,
) -> ExecutionAuthorization:
    if explicit_authorization is not True:
        raise SecurityError("explicit process execution authorization must be boolean true")
    if not isinstance(authorized_by, str) or not authorized_by.strip():
        raise SecurityError("authorized_by must be a non-empty identity")
    if not isinstance(purpose, str) or not purpose.strip():
        raise SecurityError("authorization purpose must be a non-empty string")
    return ExecutionAuthorization(plan_sha256(plan), authorized_by.strip(), purpose.strip(), True)


@dataclass(frozen=True, slots=True)
class ExecutionRecord:
    argv: tuple[str, ...]
    returncode: int
    stdout_sha256: str
    stderr_sha256: str
    started_at: str
    completed_at: str
    completed: bool
    plan_sha256: str
    authorization_sha256: str
    authorized_by: str


def run_plan(
    plan: CommandPlanLike,
    *,
    authorization: ExecutionAuthorization | None = None,
    timeout: float = 300.0,
) -> ExecutionRecord:
    if authorization is None:
        raise SecurityError("external process execution is plan-only until explicitly authorized")
    digest = plan_sha256(plan)
    if authorization.explicit_authorization is not True or authorization.plan_sha256 != digest:
        raise SecurityError("execution authorization does not match the immutable command plan")
    started = datetime.now(timezone.utc).isoformat()
    result = safe_run(
        plan.argv,
        cwd=plan.cwd,
        timeout=timeout,
        env=plan.environment,
        allow_process_execution=True,
    )
    completed_at = datetime.now(timezone.utc).isoformat()
    return ExecutionRecord(
        tuple(plan.argv),
        result.returncode,
        hashlib.sha256(result.stdout.encode()).hexdigest(),
        hashlib.sha256(result.stderr.encode()).hexdigest(),
        started,
        completed_at,
        result.returncode == 0,
        digest,
        authorization.authorization_sha256,
        authorization.authorized_by,
    )
