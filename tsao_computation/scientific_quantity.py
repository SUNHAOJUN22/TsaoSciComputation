"""Dimensioned scientific quantities and fail-closed human acceptance."""

from __future__ import annotations

import json
import re
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation, localcontext
from hashlib import sha256
from typing import Literal, TypeAlias

from .quantity_units import DIMENSION_ORDER, REGISTRY_VERSION, unit_definition

QuantityBasis: TypeAlias = Literal["MEASURED", "CALCULATED", "SIMULATED", "REFERENCE", "DERIVED"]
AcceptanceVerifier: TypeAlias = Callable[[bytes, str, str], bool]
_DIGEST = re.compile(r"[0-9a-f]{64}")


def _decimal(value: object, *, field: str) -> Decimal:
    if isinstance(value, bool):
        raise TypeError(f"{field} must be numeric, not boolean")
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise ValueError(f"{field} is not a valid decimal quantity") from exc
    if not result.is_finite():
        raise ValueError(f"{field} must be finite")
    if result and not -308 <= result.adjusted() <= 308:
        raise ValueError(f"{field} exceeds the supported decimal exponent range [-308, 308]")
    return result


@dataclass(frozen=True, slots=True)
class ScientificQuantity:
    value: Decimal
    unit: str
    dimension: tuple[int, ...]
    source_id: str
    basis: QuantityBasis = "MEASURED"
    uncertainty: Decimal | None = None
    source_quantity_digest: str | None = None

    def __post_init__(self) -> None:
        value = _decimal(self.value, field="value")
        if not isinstance(self.unit, str):
            raise ValueError("unit must be a non-empty string")
        if not isinstance(self.source_id, str):
            raise ValueError("source_id must be a non-empty string")
        unit = self.unit.strip()
        source_id = self.source_id.strip()
        if not unit:
            raise ValueError("unit must not be blank")
        if not source_id:
            raise ValueError("source_id must not be blank")
        if (
            not isinstance(self.dimension, (list, tuple))
            or len(self.dimension) != 7
            or any(
                isinstance(power, bool) or not isinstance(power, int) for power in self.dimension
            )
        ):
            raise ValueError("dimension must be a seven-integer exponent vector")
        definition = unit_definition(unit)
        if tuple(self.dimension) != definition.dimension:
            raise ValueError("unit and dimension are incompatible")
        if definition.kind == "absolute-temperature" and value <= -definition.offset:
            raise ValueError("absolute temperature must be above zero kelvin")
        if self.source_quantity_digest is not None and (
            not isinstance(self.source_quantity_digest, str)
            or _DIGEST.fullmatch(self.source_quantity_digest) is None
        ):
            raise ValueError("source_quantity_digest must be a SHA-256 digest")
        if not isinstance(self.basis, str) or self.basis not in {
            "MEASURED",
            "CALCULATED",
            "SIMULATED",
            "REFERENCE",
            "DERIVED",
        }:
            raise ValueError(f"unsupported quantity basis: {self.basis}")
        uncertainty = None
        if self.uncertainty is not None:
            uncertainty = _decimal(self.uncertainty, field="uncertainty")
            if uncertainty < 0:
                raise ValueError("uncertainty must be non-negative")
        object.__setattr__(self, "dimension", tuple(self.dimension))
        object.__setattr__(self, "value", value)
        object.__setattr__(self, "unit", unit)
        object.__setattr__(self, "source_id", source_id)
        object.__setattr__(self, "uncertainty", uncertainty)

    @classmethod
    def from_mapping(cls, payload: Mapping[str, object]) -> ScientificQuantity:
        required = {"value", "unit", "dimension", "source_id"}
        missing = sorted(required - payload.keys())
        if missing:
            raise ValueError(f"scientific quantity missing fields: {missing}")
        if (
            "unit_registry_version" in payload
            and payload["unit_registry_version"] != REGISTRY_VERSION
        ):
            raise ValueError("unsupported unit registry version")
        if "dimension_order" in payload and payload["dimension_order"] != list(DIMENSION_ORDER):
            raise ValueError("unsupported dimension order")
        raw_dimension = payload["dimension"]
        if isinstance(raw_dimension, (str, bytes)) or not isinstance(raw_dimension, Sequence):
            raise TypeError("dimension must be an integer sequence")
        return cls(
            value=_decimal(payload["value"], field="value"),
            unit=payload["unit"],  # type: ignore[arg-type]
            dimension=tuple(raw_dimension),
            source_id=payload["source_id"],  # type: ignore[arg-type]
            basis=payload.get("basis", "MEASURED"),  # type: ignore[arg-type]
            source_quantity_digest=payload.get("source_quantity_digest"),  # type: ignore[arg-type]
            uncertainty=(
                None
                if payload.get("uncertainty") is None
                else _decimal(payload["uncertainty"], field="uncertainty")
            ),
        )

    def convert(
        self,
        *,
        factor: Decimal | int | float | str | None = None,
        unit: str,
        dimension: Sequence[int],
        source_id: str | None = None,
    ) -> ScientificQuantity:
        target_dimension = tuple(dimension)
        if target_dimension != self.dimension:
            raise ValueError("cannot convert between incompatible dimensions")
        source = unit_definition(self.unit)
        target = unit_definition(unit)
        if target.dimension != self.dimension or source.kind != target.kind:
            raise ValueError("cannot convert between incompatible units or temperature kinds")
        with localcontext() as context:
            context.prec = 50
            scale = (source.scale * target.divisor) / (source.divisor * target.scale)
            if factor is not None:
                requested_scale = _decimal(factor, field="factor")
                if requested_scale <= 0:
                    raise ValueError("conversion factor must be positive")
                if requested_scale != scale:
                    raise ValueError("conversion factor contradicts the controlled unit registry")
            canonical_value = (self.value + source.offset) * source.scale / source.divisor
            converted_value = canonical_value * target.divisor / target.scale - target.offset
            converted_uncertainty = None if self.uncertainty is None else self.uncertainty * scale
        return ScientificQuantity(
            value=converted_value,
            unit=unit,
            dimension=target_dimension,
            source_id=self.source_id if source_id is None else source_id,
            basis="DERIVED",
            uncertainty=converted_uncertainty,
            source_quantity_digest=self.digest,
        )

    def canonical_payload(self) -> dict[str, object]:
        return {
            "value": str(self.value),
            "unit": self.unit,
            "dimension": list(self.dimension),
            "dimension_order": list(DIMENSION_ORDER),
            "unit_registry_version": REGISTRY_VERSION,
            "source_quantity_digest": self.source_quantity_digest,
            "source_id": self.source_id,
            "basis": self.basis,
            "uncertainty": (None if self.uncertainty is None else str(self.uncertainty)),
        }

    @property
    def digest(self) -> str:
        encoded = json.dumps(
            self.canonical_payload(),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
        return sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class AcceptanceEnvelope:
    decision: Literal["ACCEPTED", "REJECTED"]
    reviewer_id: str
    reviewed_at: datetime
    evidence_digest: str
    signature: str
    signature_scheme: str

    @classmethod
    def from_mapping(cls, payload: Mapping[str, object]) -> AcceptanceEnvelope:
        if payload.get("accepted") is True and not payload.get("signature"):
            raise ValueError("accepted boolean is not acceptance evidence")
        reviewed_at = datetime.fromisoformat(str(payload["reviewed_at"]))
        if reviewed_at.tzinfo is None or reviewed_at.utcoffset() is None:
            raise ValueError("reviewed_at must be timezone-aware")
        envelope = cls(
            decision=str(payload["decision"]),  # type: ignore[arg-type]
            reviewer_id=str(payload["reviewer_id"]).strip(),
            reviewed_at=reviewed_at.astimezone(timezone.utc),
            evidence_digest=str(payload["evidence_digest"]).casefold(),
            signature=str(payload["signature"]).strip(),
            signature_scheme=str(payload["signature_scheme"]).strip(),
        )
        if envelope.decision not in {"ACCEPTED", "REJECTED"}:
            raise ValueError("decision must be ACCEPTED or REJECTED")
        if not envelope.reviewer_id:
            raise ValueError("reviewer_id must not be blank")
        if _DIGEST.fullmatch(envelope.evidence_digest) is None:
            raise ValueError("evidence_digest must be a SHA-256 hex digest")
        if not envelope.signature or not envelope.signature_scheme:
            raise ValueError("signature and signature_scheme are required")
        return envelope

    def canonical_bytes(self) -> bytes:
        payload = {
            "decision": self.decision,
            "reviewer_id": self.reviewer_id,
            "reviewed_at": self.reviewed_at.isoformat(),
            "evidence_digest": self.evidence_digest,
            "signature_scheme": self.signature_scheme,
        }
        return json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")


def acceptance_is_verified(
    payload: Mapping[str, object],
    *,
    verifier: AcceptanceVerifier | None = None,
) -> bool:
    if verifier is None:
        return False
    try:
        envelope = AcceptanceEnvelope.from_mapping(payload)
    except (KeyError, TypeError, ValueError):
        return False
    if envelope.decision != "ACCEPTED":
        return False
    try:
        # A verifier's result is a strict decision, not a truthiness protocol.
        # In particular, "false", status objects and numeric codes cannot approve.
        return (
            verifier(
                envelope.canonical_bytes(),
                envelope.signature,
                envelope.reviewer_id,
            )
            is True
        )
    except Exception:
        return False


def require_verified_acceptance(
    payload: Mapping[str, object],
    *,
    verifier: AcceptanceVerifier | None = None,
) -> AcceptanceEnvelope:
    if not acceptance_is_verified(payload, verifier=verifier):
        raise PermissionError("cryptographically verified human acceptance is required")
    return AcceptanceEnvelope.from_mapping(payload)
