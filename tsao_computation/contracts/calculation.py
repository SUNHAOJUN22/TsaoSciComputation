from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from ..errors import ContractError


@dataclass(frozen=True, slots=True)
class CalculationContract:
    question: str
    system: dict[str, Any]
    conditions: dict[str, Any]
    target_observables: tuple[str, ...]
    workflow: str | None = None
    assumptions: tuple[str, ...] = ()
    acceptance_criteria: dict[str, Any] = field(default_factory=dict)
    schema_version: str = "1.0"

    def __post_init__(self) -> None:
        if not self.question.strip():
            raise ContractError("question must be non-empty")
        if not self.system:
            raise ContractError("system definition must be non-empty")
        if not self.target_observables:
            raise ContractError("at least one target observable is required")
        if any(not str(x).strip() for x in self.target_observables):
            raise ContractError("target observables must be non-empty strings")

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CalculationContract:
        required = {"question", "system", "conditions", "target_observables"}
        missing = sorted(required - data.keys())
        if missing:
            raise ContractError(f"missing contract fields: {missing}")
        return cls(
            question=str(data["question"]),
            system=dict(data["system"]),
            conditions=dict(data["conditions"]),
            target_observables=tuple(map(str, data["target_observables"])),
            workflow=data.get("workflow"),
            assumptions=tuple(map(str, data.get("assumptions", ()))),
            acceptance_criteria=dict(data.get("acceptance_criteria", {})),
            schema_version=str(data.get("schema_version", "1.0")),
        )

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["target_observables"] = list(self.target_observables)
        result["assumptions"] = list(self.assumptions)
        return result
