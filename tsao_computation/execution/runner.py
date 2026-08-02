from __future__ import annotations

import hashlib
import json
import os
import shutil
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from ..errors import SecurityError
from ..security.process import (
    _authorized_run,
    _issue_process_execution_permit,
    _subprocess_environment,
)
from .typing_compat import CommandPlanLike

_AUTHORIZATION_SEAL = object()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _resolve_executable(argv0: str) -> Path:
    if not isinstance(argv0, str) or not argv0 or "\x00" in argv0:
        raise SecurityError("command plan executable must be a non-empty string")
    candidate = Path(argv0).expanduser()
    if candidate.is_absolute() or candidate.parent != Path("."):
        found = str(candidate)
    else:
        found = shutil.which(argv0)
    if not found:
        raise SecurityError(f"command plan executable is unavailable: {argv0}")
    try:
        resolved = Path(found).resolve(strict=True)
    except OSError as error:
        raise SecurityError(f"command plan executable is unavailable: {argv0}") from error
    if not resolved.is_file() or (os.name != "nt" and not os.access(resolved, os.X_OK)):
        raise SecurityError(f"command plan executable is not runnable: {argv0}")
    return resolved


def _input_binding(plan: CommandPlanLike) -> tuple[str | None, str | None]:
    raw_path = getattr(plan, "input_path", None)
    declared_sha256 = getattr(plan, "input_sha256", None)
    if raw_path is None:
        if declared_sha256 is not None:
            raise SecurityError("command plan declares an input hash without an input path")
        return None, None
    try:
        resolved = Path(raw_path).expanduser().resolve(strict=True)
    except OSError as error:
        raise SecurityError(f"command plan input file is unavailable: {raw_path}") from error
    if not resolved.is_file():
        raise SecurityError(f"command plan input file is unavailable: {raw_path}")
    actual_sha256 = _sha256_file(resolved)
    if declared_sha256 is not None and declared_sha256 != actual_sha256:
        raise SecurityError("command plan input file does not match its declared SHA-256")
    return str(resolved), actual_sha256


def _bound_plan(
    plan: CommandPlanLike,
) -> tuple[str, str, str, str | None, Mapping[str, str]]:
    if not plan.argv or any(
        not isinstance(item, str) or not item or "\x00" in item for item in plan.argv
    ):
        raise SecurityError("command plan argv must contain non-empty strings")
    try:
        cwd = plan.cwd.expanduser().resolve(strict=True)
    except OSError as error:
        raise SecurityError(f"command plan working directory is unavailable: {plan.cwd}") from error
    if not cwd.is_dir():
        raise SecurityError(f"command plan working directory is unavailable: {plan.cwd}")
    executable = _resolve_executable(plan.argv[0])
    executable_sha256 = _sha256_file(executable)
    input_path, input_sha256 = _input_binding(plan)
    normalized_environment = _subprocess_environment(plan.environment)
    normalized_argv = [str(executable), *plan.argv[1:]]
    payload = {
        "argv": normalized_argv,
        "cwd": str(cwd),
        "environment": dict(sorted(normalized_environment.items())),
        "adapter_slug": getattr(plan, "adapter_slug", None),
        "executable_sha256": executable_sha256,
        "input_path": input_path,
        "input_sha256": input_sha256,
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    digest = hashlib.sha256(encoded.encode("utf-8")).hexdigest()
    return digest, str(executable), executable_sha256, input_sha256, normalized_environment


def plan_sha256(plan: CommandPlanLike) -> str:
    return _bound_plan(plan)[0]


@dataclass(frozen=True, slots=True)
class ExecutionAuthorization:
    plan_sha256: str
    executable_sha256: str
    input_sha256: str | None
    authorized_by: str
    purpose: str
    explicit_authorization: bool
    _seal: object = field(repr=False, compare=False)

    def __post_init__(self) -> None:
        if self._seal is not _AUTHORIZATION_SEAL:
            raise SecurityError("execution authorizations must be created by authorize_plan")

    @property
    def authorization_sha256(self) -> str:
        encoded = json.dumps(
            {
                "plan_sha256": self.plan_sha256,
                "executable_sha256": self.executable_sha256,
                "input_sha256": self.input_sha256,
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
    digest, _, executable_sha256, input_sha256, _ = _bound_plan(plan)
    return ExecutionAuthorization(
        digest,
        executable_sha256,
        input_sha256,
        authorized_by.strip(),
        purpose.strip(),
        True,
        _AUTHORIZATION_SEAL,
    )


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
    executable_sha256: str
    input_sha256: str | None


def run_plan(
    plan: CommandPlanLike,
    *,
    authorization: ExecutionAuthorization | None = None,
    timeout: float = 300.0,
) -> ExecutionRecord:
    if authorization is None:
        raise SecurityError("external process execution is plan-only until explicitly authorized")
    digest, executable, executable_sha256, input_sha256, environment = _bound_plan(plan)
    if authorization.explicit_authorization is not True or authorization.plan_sha256 != digest:
        raise SecurityError("execution authorization does not match the immutable command plan")
    if authorization.executable_sha256 != executable_sha256:
        raise SecurityError("authorized executable content changed before execution")
    if authorization.input_sha256 != input_sha256:
        raise SecurityError("authorized input content changed before execution")
    started = datetime.now(timezone.utc).isoformat()
    argv = (executable, *plan.argv[1:])
    result = _authorized_run(
        argv,
        cwd=plan.cwd,
        timeout=timeout,
        environment=environment,
        permit=_issue_process_execution_permit(),
    )
    completed_at = datetime.now(timezone.utc).isoformat()
    return ExecutionRecord(
        tuple(argv),
        result.returncode,
        hashlib.sha256(result.stdout.encode()).hexdigest(),
        hashlib.sha256(result.stderr.encode()).hexdigest(),
        started,
        completed_at,
        result.returncode == 0,
        digest,
        authorization.authorization_sha256,
        authorization.authorized_by,
        executable_sha256,
        input_sha256,
    )
