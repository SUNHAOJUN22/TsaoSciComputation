from __future__ import annotations

import json
import re
import shutil
import subprocess  # nosec B404
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..errors import ContractError


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
    if path.parent != Path(".") and path.is_file():
        return str(path.resolve())
    return shutil.which(candidate)


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
        missing = _missing_python_modules(found, self.python_modules)
        if missing:
            return AdapterProbe(
                self.slug,
                False,
                found,
                "detected "
                f"{candidate}, but required Python modules are missing: {', '.join(missing)}",
            )
        reason = f"detected {candidate}"
        if self.python_modules:
            reason += f" with modules: {', '.join(self.python_modules)}"
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
        lowered = output.casefold()
        completed = any(
            marker in lowered
            for marker in ("normal termination", "finished", "completed", "total wall time")
        )
        negative_convergence = any(
            marker in lowered
            for marker in (
                "not converged",
                "not fully converged",
                "failed to converge",
                "did not converge",
                "convergence not achieved",
                "non-converged",
                "nonconverged",
            )
        )
        positive_convergence = bool(
            re.search(r"\bconverged\b|\bconvergence (?:achieved|reached)\b", lowered)
        )
        return {
            "completed": completed,
            "converged": positive_convergence and not negative_convergence,
            "raw_length": len(output),
            "validated": False,
        }
