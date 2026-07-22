from __future__ import annotations

import shutil
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


@dataclass(frozen=True, slots=True)
class Adapter:
    record: dict[str, Any]

    @property
    def slug(self) -> str:
        return str(self.record["slug"])

    def probe(self) -> AdapterProbe:
        for executable in self.record.get("executables", []):
            found = shutil.which(executable)
            if found:
                return AdapterProbe(self.slug, True, found, f"detected {executable}")
        return AdapterProbe(self.slug, False, None, "no declared executable detected")

    def build_command(self, input_path: Path, *, executable: str | None = None) -> CommandPlan:
        if not input_path.is_file():
            raise ContractError(f"input file does not exist: {input_path}")
        selected = executable or self.probe().executable
        if not selected:
            raise ContractError(f"adapter {self.slug} is not runnable in the current environment")
        return CommandPlan(
            (selected, input_path.name),
            input_path.parent.resolve(),
            {},
            "Command prepared only; execution and scientific acceptance require separate evidence.",
        )

    def parse(self, output: str) -> dict[str, Any]:
        lowered = output.casefold()
        completed = any(
            x in lowered for x in ("normal termination", "finished", "completed", "total wall time")
        )
        converged = any(
            x in lowered for x in ("converged", "convergence achieved", "normal termination")
        )
        return {
            "completed": completed,
            "converged": converged,
            "raw_length": len(output),
            "validated": False,
        }
