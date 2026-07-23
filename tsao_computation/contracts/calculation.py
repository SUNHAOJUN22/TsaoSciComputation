from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import asdict, dataclass, field
from typing import Any, ClassVar

from ..errors import ContractError


def _string_tuple(value: object, *, field_name: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        return (value,)
    if isinstance(value, Mapping) or not isinstance(value, Iterable):
        raise ContractError(f"{field_name} must be a string or an array of strings")
    return tuple(str(item) for item in value)


def _mapping_tuple(value: object, *, field_name: str) -> tuple[dict[str, Any], ...]:
    if value is None:
        return ()
    if isinstance(value, (str, bytes, Mapping)) or not isinstance(value, Iterable):
        raise ContractError(f"{field_name} must be an array of objects")
    result: list[dict[str, Any]] = []
    for item in value:
        if not isinstance(item, Mapping):
            raise ContractError(f"{field_name} must contain only objects")
        result.append({str(key): item_value for key, item_value in item.items()})
    return tuple(result)


@dataclass(frozen=True, slots=True)
class CalculationContract:
    question: str
    system: dict[str, Any]
    conditions: dict[str, Any]
    target_observables: tuple[str, ...]
    workflow: str | None = None
    assumptions: tuple[str, ...] = ()
    acceptance_criteria: dict[str, Any] = field(default_factory=dict)
    model_object: dict[str, Any] = field(default_factory=dict)
    scales: tuple[str, ...] = ()
    methods: tuple[str, ...] = ()
    boundary_conditions: dict[str, Any] = field(default_factory=dict)
    initial_conditions: dict[str, Any] = field(default_factory=dict)
    parameter_sources: tuple[dict[str, Any], ...] = ()
    convergence_plan: dict[str, Any] = field(default_factory=dict)
    validation_plan: dict[str, Any] = field(default_factory=dict)
    uncertainty_sources: tuple[str, ...] = ()
    compute_resources: dict[str, Any] = field(default_factory=dict)
    expected_artifacts: tuple[str, ...] = ()
    human_approval_nodes: tuple[str, ...] = ()
    schema_version: str = "1.0"

    PREFLIGHT_FIELDS: ClassVar[tuple[str, ...]] = (
        "assumptions",
        "model_object",
        "scales",
        "methods",
        "boundary_conditions",
        "initial_conditions",
        "parameter_sources",
        "convergence_plan",
        "validation_plan",
        "uncertainty_sources",
        "compute_resources",
        "expected_artifacts",
        "human_approval_nodes",
        "acceptance_criteria",
    )

    def __post_init__(self) -> None:
        if not self.question.strip():
            raise ContractError("question must be non-empty")
        if not self.system:
            raise ContractError("system definition must be non-empty")
        if not self.target_observables:
            raise ContractError("at least one target observable is required")
        if any(not item.strip() for item in self.target_observables):
            raise ContractError("target observables must be non-empty strings")
        if any(not item.strip() for item in self.scales + self.methods):
            raise ContractError("scales and methods must be non-empty strings")
        if any(not item.strip() for item in self.uncertainty_sources + self.expected_artifacts):
            raise ContractError("uncertainty sources and expected artifacts must be non-empty strings")
        if any(not item.strip() for item in self.human_approval_nodes):
            raise ContractError("human approval nodes must be non-empty strings")

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CalculationContract:
        required = {"question", "system", "conditions", "target_observables"}
        missing = sorted(required - data.keys())
        if missing:
            raise ContractError(f"missing contract fields: {missing}")
        scale_value = data.get("scales", data.get("scale"))
        method_value = data.get("methods", data.get("method"))
        return cls(
            question=str(data["question"]),
            system=dict(data["system"]),
            conditions=dict(data["conditions"]),
            target_observables=_string_tuple(
                data["target_observables"], field_name="target_observables"
            ),
            workflow=data.get("workflow"),
            assumptions=_string_tuple(data.get("assumptions"), field_name="assumptions"),
            acceptance_criteria=dict(data.get("acceptance_criteria", {})),
            model_object=dict(data.get("model_object", {})),
            scales=_string_tuple(scale_value, field_name="scales"),
            methods=_string_tuple(method_value, field_name="methods"),
            boundary_conditions=dict(data.get("boundary_conditions", {})),
            initial_conditions=dict(data.get("initial_conditions", {})),
            parameter_sources=_mapping_tuple(
                data.get("parameter_sources"), field_name="parameter_sources"
            ),
            convergence_plan=dict(data.get("convergence_plan", {})),
            validation_plan=dict(data.get("validation_plan", {})),
            uncertainty_sources=_string_tuple(
                data.get("uncertainty_sources"), field_name="uncertainty_sources"
            ),
            compute_resources=dict(data.get("compute_resources", {})),
            expected_artifacts=_string_tuple(
                data.get("expected_artifacts"), field_name="expected_artifacts"
            ),
            human_approval_nodes=_string_tuple(
                data.get("human_approval_nodes"), field_name="human_approval_nodes"
            ),
            schema_version=str(data.get("schema_version", "1.0")),
        )

    def specification_gaps(self) -> tuple[str, ...]:
        gaps: list[str] = []
        for field_name in self.PREFLIGHT_FIELDS:
            if not getattr(self, field_name):
                gaps.append(field_name)
        return tuple(gaps)

    def assert_ready_for_preflight(self) -> None:
        gaps = self.specification_gaps()
        if gaps:
            raise ContractError(f"contract is not ready for preflight; missing fields: {list(gaps)}")

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        for name in (
            "target_observables",
            "assumptions",
            "scales",
            "methods",
            "uncertainty_sources",
            "expected_artifacts",
            "human_approval_nodes",
        ):
            result[name] = list(getattr(self, name))
        result["parameter_sources"] = [dict(item) for item in self.parameter_sources]
        return result
