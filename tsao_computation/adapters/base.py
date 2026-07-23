from __future__ import annotations

import json
import re
import shutil
import subprocess  # nosec B404
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..errors import ContractError

_COMPLETION_SUCCESS = re.compile(
    r"\bnormal\s+termination\b|"
    r"\b(?:run|job|calculation|simulation)\s+(?:finished|completed)(?:\s+successfully)?\b|"
    r"\b(?:finished|completed)\s+successfully\b|"
    r"\b(?:finished|completed)\b|"
    r"\btotal\s+wall\s+time\b",
    re.IGNORECASE,
)
_COMPLETION_FAILURE = re.compile(
    r"\b(?:abnormal|error|fatal)\s+termination\b|"
    r"\b(?:run|job|calculation|simulation)\s+(?:failed|aborted)\b|"
    r"\b(?:not|never)\s+(?:finished|completed)\b|"
    r"\bcompleted\s+with\s+(?:errors?|failures?)\b|"
    r"\bfatal\s+error\b",
    re.IGNORECASE,
)
_CONVERGENCE_SUCCESS = re.compile(
    r"\bconverged\b|\bconvergence\s+(?:achieved|reached)\b",
    re.IGNORECASE,
)
_CONVERGENCE_FAILURE = re.compile(
    r"\bnot(?:\s+fully)?\s+converged\b|"
    r"\bfailed\s+to\s+converge\b|"
    r"\bdid\s+not\s+converge\b|"
    r"\bconvergence\s+(?:not\s+achieved|failed|failure)\b|"
    r"\bnon[-\s]?converged\b|"
    r"\bunconverged\b",
    re.IGNORECASE,
)


@dataclass(frozen=True, slots=True)
class AdapterProbe:
    slug: str
    available: bool
    executable: str | None
    reason: str


@dataclass(frozen=True, slots=True)
class CommandPlan:
    argv: tuple[str, ...]
    cwd: Path
    environment: dict[str, str]
    claim_boundary: str


def _resolve_executable(candidate: str) -> str | None:
    path = Path(candidate).expanduser()
    if path.is_absolute() and path.is_file():
        return str(path)
    if path.parent != Path(".") and path.is_file():
        return str(path.resolve())
    return shutil.which(candidate)


def _module_probe_interpreter(candidate: str, found: str) -> str:
    name = Path(found).name.casefold()
    if name.startswith("python") or name.startswith("pypy"):
        return found
    return sys.executable


def _missing_python_modules(executable: str, modules: tuple[str, ...]) -> tuple[str, ...]:
    if not modules:
        return ()
    script = (
        "import importlib.util,json,sys;"
        "missing=[name for name in sys.argv[1:] if importlib.util.find_spec(name) is None];"
        "print(json.dumps(missing));"
        "raise SystemExit(bool(missing))"
    )
    try:
        result = subprocess.run(  # nosec B603
            [executable, "-c", script, *modules],
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return modules
    if result.returncode == 0:
        return ()
    try:
        payload = json.loads(result.stdout.strip() or "[]")
    except json.JSONDecodeError:
        return modules
    if not isinstance(payload, list):
        return modules
    return tuple(str(item) for item in payload)


@dataclass(frozen=True, slots=True)
class Adapter:
    record: dict[str, Any]

    @property
    def slug(self) -> str:
        return str(self.record["slug"])

    @property
    def python_modules(self) -> tuple[str, ...]:
        raw = self.record.get("python_modules", [])
        if not isinstance(raw, list):
            return ()
        return tuple(str(item) for item in raw)

    def _probe_candidate(self, candidate: str) -> AdapterProbe:
        found = _resolve_executable(candidate)
        if not found:
            return AdapterProbe(self.slug, False, None, f"executable not detected: {candidate}")
        module_interpreter = _module_probe_interpreter(candidate, found)
        missing = _missing_python_modules(module_interpreter, self.python_modules)
        if missing:
            return AdapterProbe(
                self.slug,
                False,
                found,
                "detected "
                f"{candidate}, but required Python modules are missing from "
                f"{module_interpreter}: {', '.join(missing)}",
            )
        reason = f"detected {candidate}"
        if self.python_modules:
            reason += f" with modules in {module_interpreter}: {', '.join(self.python_modules)}"
        return AdapterProbe(self.slug, True, found, reason)

    def probe(self) -> AdapterProbe:
        reasons: list[str] = []
        for executable in self.record.get("executables", []):
            result = self._probe_candidate(str(executable))
            if result.available:
                return result
            reasons.append(result.reason)
        if reasons:
            return AdapterProbe(self.slug, False, None, "; ".join(reasons))
        return AdapterProbe(self.slug, False, None, "no declared executable detected")

    def build_command(self, input_path: Path, *, executable: str | None = None) -> CommandPlan:
        if not input_path.is_file():
            raise ContractError(f"input file does not exist: {input_path}")
        probe = self.probe() if executable is None else self._probe_candidate(executable)
        if not probe.available or not probe.executable:
            raise ContractError(
                f"adapter {self.slug} is not runnable in the current environment: {probe.reason}"
            )
        return CommandPlan(
            (probe.executable, input_path.name),
            input_path.parent.resolve(),
            {},
            "Command prepared only; execution and scientific acceptance require separate evidence.",
        )

    def parse(self, output: str) -> dict[str, Any]:
        completion_failed = _COMPLETION_FAILURE.search(output) is not None
        completed = _COMPLETION_SUCCESS.search(output) is not None and not completion_failed
        convergence_failed = _CONVERGENCE_FAILURE.search(output) is not None
        converged = (
            completed and _CONVERGENCE_SUCCESS.search(output) is not None and not convergence_failed
        )
        return {
            "completed": completed,
            "converged": converged,
            "raw_length": len(output),
            "validated": False,
        }
