from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import asdict, dataclass, field
from typing import Any, ClassVar

from ..errors import ContractError


def _required_string(value: object, *, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ContractError(f"{field_name} must be a non-empty string")
    return value


def _optional_string(value: object, *, field_name: str) -> str | None:
    if value is None:
        return None
    return _required_string(value, field_name=field_name)


def _mapping(value: object, *, field_name: str) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise ContractError(f"{field_name} must be an object")
    return {str(key): item for key, item in value.items()}


def _string_tuple(value: object, *, field_name: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        return (_required_string(value, field_name=field_name),)
    if isinstance(value, Mapping) or not isinstance(value, Iterable):
        raise ContractError(f"{field_name} must be a string or an array of strings")
    result: list[str] = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise ContractError(f"{field_name} must contain only non-empty strings")
        result.append(item)
    return tuple(result)


def _mapping_tuple(value: object, *, field_name: str) -> tuple[dict[str, Any], ...]:
    if value is None:
        return ()
    if isinstance(value, (str, bytes, Mapping)) or not isinstance(value, Iterable):
        raise ContractError(f"{field_name} must be an array of objects")
    result: list[dict[str, Any]] = []
    for item in value:
        if not isinstance(item, Mapping):
            raise ContractError(f"{field_name} must contain only objects")
        normalized = {str(key): item_value for key, item_value in item.items()}
        if not normalized:
            raise ContractError(f"{field_name} must not contain empty objects")
        result.append(normalized)
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
        _required_string(self.question, field_name="question")
        system = _mapping(self.system, field_name="system")
        if not system:
            raise ContractError("system definition must be non-empty")
        _mapping(self.conditions, field_name="conditions")
        observables = _string_tuple(self.target_observables, field_name="target_observables")
        if not observables:
            raise ContractError("at least one target observable is required")
        _optional_string(self.workflow, field_name="workflow")
        _string_tuple(self.assumptions, field_name="assumptions")
        _mapping(self.acceptance_criteria, field_name="acceptance_criteria")
        _mapping(self.model_object, field_name="model_object")
        _string_tuple(self.scales, field_name="scales")
        _string_tuple(self.methods, field_name="methods")
        _mapping(self.boundary_conditions, field_name="boundary_conditions")
        _mapping(self.initial_conditions, field_name="initial_conditions")
        _mapping_tuple(self.parameter_sources, field_name="parameter_sources")
        _mapping(self.convergence_plan, field_name="convergence_plan")
        _mapping(self.validation_plan, field_name="validation_plan")
        _string_tuple(self.uncertainty_sources, field_name="uncertainty_sources")
        _mapping(self.compute_resources, field_name="compute_resources")
        _string_tuple(self.expected_artifacts, field_name="expected_artifacts")
        _string_tuple(self.human_approval_nodes, field_name="human_approval_nodes")
        _required_string(self.schema_version, field_name="schema_version")

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> CalculationContract:
        if not isinstance(data, Mapping):
            raise ContractError("calculation contract must be an object")
        required = {"question", "system", "conditions", "target_observables"}
        missing = sorted(required - data.keys())
        if missing:
            raise ContractError(f"missing contract fields: {missing}")
        scale_value = data.get("scales", data.get("scale"))
        method_value = data.get("methods", data.get("method"))
        return cls(
            question=_required_string(data["question"], field_name="question"),
            system=_mapping(data["system"], field_name="system"),
            conditions=_mapping(data["conditions"], field_name="conditions"),
            target_observables=_string_tuple(
                data["target_observables"], field_name="target_observables"
            ),
            workflow=_optional_string(data.get("workflow"), field_name="workflow"),
            assumptions=_string_tuple(data.get("assumptions"), field_name="assumptions"),
            acceptance_criteria=_mapping(
                data.get("acceptance_criteria"), field_name="acceptance_criteria"
            ),
            model_object=_mapping(data.get("model_object"), field_name="model_object"),
            scales=_string_tuple(scale_value, field_name="scales"),
            methods=_string_tuple(method_value, field_name="methods"),
            boundary_conditions=_mapping(
                data.get("boundary_conditions"), field_name="boundary_conditions"
            ),
            initial_conditions=_mapping(
                data.get("initial_conditions"), field_name="initial_conditions"
            ),
            parameter_sources=_mapping_tuple(
                data.get("parameter_sources"), field_name="parameter_sources"
            ),
            convergence_plan=_mapping(
                data.get("convergence_plan"), field_name="convergence_plan"
            ),
            validation_plan=_mapping(
                data.get("validation_plan"), field_name="validation_plan"
            ),
            uncertainty_sources=_string_tuple(
                data.get("uncertainty_sources"), field_name="uncertainty_sources"
            ),
            compute_resources=_mapping(
                data.get("compute_resources"), field_name="compute_resources"
            ),
            expected_artifacts=_string_tuple(
                data.get("expected_artifacts"), field_name="expected_artifacts"
            ),
            human_approval_nodes=_string_tuple(
                data.get("human_approval_nodes"), field_name="human_approval_nodes"
            ),
            schema_version=_required_string(
                data.get("schema_version", "1.0"), field_name="schema_version"
            ),
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
            raise ContractError(
                f"contract is not ready for preflight; missing fields: {list(gaps)}"
            )

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
