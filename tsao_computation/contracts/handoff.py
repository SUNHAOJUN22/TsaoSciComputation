from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import InitVar, dataclass
from decimal import Decimal
from hashlib import sha256
from typing import Any

from ..errors import ContractError
from ..hashing import canonical_json_bytes
from ..immutable import freeze_json, thaw_json
from ..quantity_units import unit_definition
from ..validation.acceptance import acceptance_gate

_MAX_CELLS = 100_000


def _numeric_shape(value: object, *, name: str, nonnegative: bool = False) -> tuple[int, ...]:
    """Accept only bounded, rectangular, finite numeric scalar/array payloads."""
    cells = 0

    def visit(item: object, depth: int) -> tuple[int, ...]:
        nonlocal cells
        if depth > 6:
            raise ContractError(f"{name} exceeds the supported array depth")
        if isinstance(item, (list, tuple)):
            if not item or len(item) > _MAX_CELLS:
                raise ContractError(f"{name} must have a non-empty bounded shape")
            child_shapes = [visit(child, depth + 1) for child in item]
            if any(shape != child_shapes[0] for shape in child_shapes):
                raise ContractError(f"{name} must be a rectangular numeric array")
            return (len(item), *child_shapes[0])
        cells += 1
        if cells > _MAX_CELLS:
            raise ContractError(f"{name} exceeds the {_MAX_CELLS}-cell budget")
        try:
            finite = (
                not isinstance(item, bool)
                and isinstance(item, (int, float))
                and math.isfinite(item)
            )
        except OverflowError:
            finite = False
        if not finite:
            raise ContractError(f"{name} must contain finite real numbers")
        if nonnegative and item < 0:  # type: ignore[operator]
            raise ContractError(f"{name} must be non-negative")
        return ()

    return visit(value, 0)


def _json_metadata(value: object, *, name: str, depth: int = 0) -> None:
    if depth > 16:
        raise ContractError(f"{name} exceeds the metadata depth budget")
    if isinstance(value, Mapping):
        if len(value) > 10_000:
            raise ContractError(f"{name} exceeds the metadata size budget")
        for key, item in value.items():
            if not isinstance(key, str) or not key.strip():
                raise ContractError(f"{name} requires non-empty string keys")
            _json_metadata(item, name=name, depth=depth + 1)
    elif isinstance(value, (list, tuple)):
        if len(value) > _MAX_CELLS:
            raise ContractError(f"{name} exceeds the metadata size budget")
        for item in value:
            _json_metadata(item, name=name, depth=depth + 1)
    elif isinstance(value, (int, float)) and not isinstance(value, bool):
        _numeric_shape(value, name=name)
    elif value is not None and not isinstance(value, (str, bool)):
        raise ContractError(f"{name} must be finite JSON-compatible metadata")


def _uncertainty(value: object, *, name: str, unit: str, shape: tuple[int, ...]) -> None:
    if value is None:
        raise ContractError(f"{name} must be explicit")
    if isinstance(value, Mapping):
        if "value" not in value or "unit" not in value:
            raise ContractError(f"{name} object requires value and unit")
        try:
            if unit_definition(value["unit"]).dimension != unit_definition(unit).dimension:
                raise ValueError("incompatible uncertainty unit")
        except ValueError as exc:
            raise ContractError(f"{name} unit is incompatible with the quantity") from exc
        _json_metadata(value, name=name)
        magnitude = value["value"]
    else:
        magnitude = value
    uncertainty_shape = _numeric_shape(magnitude, name=name, nonnegative=True)
    if uncertainty_shape and uncertainty_shape != shape:
        raise ContractError(f"{name} shape must match the quantity (or be a scalar bound)")


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
    validation_evidence: Mapping[str, Any] | None = None
    trusted_approval_keys: InitVar[Mapping[str, bytes] | None] = None

    def __post_init__(self, trusted_approval_keys: Mapping[str, bytes] | None) -> None:
        required = (
            self.source_model,
            self.target_model,
            self.quantity,
            self.unit,
            self.reference_state,
            self.applicability,
            self.transformation,
        )
        if any(not isinstance(item, str) or not item.strip() for item in required):
            raise ContractError("handoff metadata must contain non-empty strings")
        try:
            definition = unit_definition(self.unit)
        except ValueError as exc:
            raise ContractError(str(exc)) from exc
        shape = _numeric_shape(self.value, name="handoff value")
        if definition.kind == "absolute-temperature":

            def check_temperature(item: Any) -> None:
                if isinstance(item, (list, tuple)):
                    for child in item:
                        check_temperature(child)
                elif Decimal(str(item)) <= -definition.offset:
                    raise ContractError("absolute handoff temperature must be above zero kelvin")

            check_temperature(self.value)
        if not isinstance(self.conditions, Mapping) or not self.conditions:
            raise ContractError("handoff conditions must be a non-empty object")
        _json_metadata(self.conditions, name="conditions")
        _uncertainty(
            self.statistical_uncertainty,
            name="statistical uncertainty",
            unit=self.unit,
            shape=shape,
        )
        _uncertainty(self.model_uncertainty, name="model uncertainty", unit=self.unit, shape=shape)
        if not isinstance(self.validation_status, str) or self.validation_status not in {
            "unvalidated",
            "checked",
            "validated",
            "rejected",
        }:
            raise ContractError("invalid handoff validation status")
        if self.validation_evidence is not None:
            if not isinstance(self.validation_evidence, Mapping):
                raise ContractError("validation evidence must be an object")
            _json_metadata(self.validation_evidence, name="validation evidence")
        for name in (
            "value",
            "conditions",
            "statistical_uncertainty",
            "model_uncertainty",
            "validation_evidence",
        ):
            # Copy first, including previously frozen containers, to detach caller aliases.
            object.__setattr__(self, name, freeze_json(thaw_json(getattr(self, name))))
        if self.validation_status == "validated":
            evidence = dict(self.validation_evidence or {})
            if (
                evidence.get("artifact_sha256") != self.digest
                or not acceptance_gate(
                    evidence,
                    trusted_approval_keys=trusted_approval_keys,
                )["accepted"]
            ):
                raise ContractError(
                    "validated handoff requires artifact-bound verified acceptance evidence"
                )

    def canonical_payload(self) -> dict[str, Any]:
        """The scientific payload excludes the review decision to avoid circular signing."""
        names = (
            "source_model",
            "target_model",
            "quantity",
            "value",
            "unit",
            "conditions",
            "reference_state",
            "statistical_uncertainty",
            "model_uncertainty",
            "applicability",
            "transformation",
        )
        return {name: thaw_json(getattr(self, name)) for name in names}

    @property
    def digest(self) -> str:
        return sha256(canonical_json_bytes(self.canonical_payload())).hexdigest()

    def to_dict(self) -> dict[str, Any]:
        return {
            **self.canonical_payload(),
            "validation_status": self.validation_status,
            "validation_evidence": thaw_json(self.validation_evidence),
        }

    @classmethod
    def from_mapping(
        cls, payload: Mapping[str, Any], *, trusted_approval_keys: Mapping[str, bytes] | None = None
    ) -> HandoffRecord:
        allowed = {
            "source_model",
            "target_model",
            "quantity",
            "value",
            "unit",
            "conditions",
            "reference_state",
            "statistical_uncertainty",
            "model_uncertainty",
            "applicability",
            "transformation",
            "validation_status",
            "validation_evidence",
        }
        if payload.keys() - allowed:
            raise ContractError(
                "unknown handoff fields; trust keys must be supplied outside the record"
            )
        try:
            return cls(**dict(payload), trusted_approval_keys=trusted_approval_keys)
        except TypeError as exc:
            raise ContractError("handoff record is incomplete") from exc
