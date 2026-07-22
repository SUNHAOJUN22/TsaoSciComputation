from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..errors import ContractError


@dataclass(frozen=True, slots=True)
class HandoffRecord:
    source_model: str
    target_model: str
    quantity: str
    value: Any
    unit: str
    conditions: dict[str, Any]
    reference_state: str
    statistical_uncertainty: Any
    model_uncertainty: Any
    applicability: str
    transformation: str
    validation_status: str

    def __post_init__(self) -> None:
        required = (
            self.source_model,
            self.target_model,
            self.quantity,
            self.unit,
            self.reference_state,
            self.applicability,
            self.transformation,
        )
        if any(not str(x).strip() for x in required):
            raise ContractError("handoff metadata must be complete")
        if self.validation_status not in {"unvalidated", "checked", "validated", "rejected"}:
            raise ContractError("invalid handoff validation status")
