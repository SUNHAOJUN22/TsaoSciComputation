from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..contracts import CalculationContract
from ..registries import workflows
from ..routing import route_question


@dataclass(frozen=True, slots=True)
class GateResult:
    gate: str
    passed: bool
    evidence: str


class WorkflowEngine:
    def select(self, contract: CalculationContract) -> dict[str, Any]:
        slug = contract.workflow or route_question(contract.question).workflow
        for record in workflows():
            if record["slug"] == slug:
                return record
        raise KeyError(f"unknown workflow: {slug}")

    def initial_gates(self, contract: CalculationContract) -> tuple[GateResult, ...]:
        selected = self.select(contract)
        return (
            GateResult(
                "contract",
                bool(contract.question and contract.system and contract.target_observables),
                "contract fields present",
            ),
            GateResult("method", bool(selected), f"workflow={selected['slug']}"),
            GateResult("environment", False, "environment has not been probed"),
            GateResult("execution", False, "no execution record"),
            GateResult("acceptance", False, "completed != converged != validated != accepted"),
        )
