"""Strict numerical, execution-capability, and acceptance contracts."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from math import isfinite
import hashlib
import hmac
import json
from typing import MutableSet


class ContractError(ValueError):
    """Raised when a scientific-computation contract is invalid."""


def _real(value: object, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be a non-Boolean real")
    number = float(value)
    if not isfinite(number):
        raise ContractError(f"{name} must be finite")
    return number


@dataclass(frozen=True, slots=True)
class ScientificDatum:
    value: float
    unit: str
    dimension: str
    scale_to_si: float
    uncertainty: float = 0.0

    def canonical(self) -> tuple[float, float]:
        value = _real(self.value, "value")
        scale = _real(self.scale_to_si, "scale_to_si")
        uncertainty = _real(self.uncertainty, "uncertainty")
        if scale <= 0.0 or uncertainty < 0.0 or not self.unit or not self.dimension:
            raise ContractError("invalid datum metadata")
        return value * scale, uncertainty * scale


def convergence(
    previous: ScientificDatum,
    current: ScientificDatum,
    *,
    atol: ScientificDatum,
    rtol: float,
) -> bool:
    if len({previous.dimension, current.dimension, atol.dimension}) != 1:
        raise ContractError("dimension mismatch")
    previous_value, _ = previous.canonical()
    current_value, _ = current.canonical()
    absolute_tolerance, _ = atol.canonical()
    relative_tolerance = _real(rtol, "rtol")
    if absolute_tolerance < 0.0 or relative_tolerance < 0.0:
        raise ContractError("negative tolerance")
    scale = max(abs(previous_value), abs(current_value))
    return abs(current_value - previous_value) <= absolute_tolerance + relative_tolerance * scale


@dataclass(frozen=True, slots=True)
class ExecutionCapability:
    plan_sha256: str
    executable_sha256: str
    input_sha256: str
    subject: str
    scope: str
    audience: str
    issued_at: int
    expires_at: int
    nonce: str
    key_id: str
    signature: str = ""


def _payload(capability: ExecutionCapability) -> bytes:
    payload = asdict(capability)
    payload.pop("signature")
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def issue_capability(capability: ExecutionCapability, key: bytes) -> ExecutionCapability:
    if capability.signature or not isinstance(key, bytes) or len(key) < 32:
        raise ContractError("invalid signing request")
    signature = hmac.new(key, _payload(capability), hashlib.sha256).hexdigest()
    return ExecutionCapability(**{**asdict(capability), "signature": signature})


def verify_capability(
    capability: ExecutionCapability,
    *,
    key: bytes,
    expected_subject: str,
    expected_scope: str,
    now: int,
    used_nonces: MutableSet[str],
) -> None:
    if capability.nonce in used_nonces:
        raise ContractError("capability replay")
    if (
        capability.subject != expected_subject
        or capability.scope != expected_scope
        or capability.audience != "tsao-scicomputation"
    ):
        raise ContractError("capability binding mismatch")
    if (
        now < capability.issued_at
        or now >= capability.expires_at
        or capability.expires_at - capability.issued_at > 900
    ):
        raise ContractError("capability is expired or overlong")
    expected_signature = hmac.new(key, _payload(capability), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(capability.signature, expected_signature):
        raise ContractError("capability signature mismatch")
    for digest in (
        capability.plan_sha256,
        capability.executable_sha256,
        capability.input_sha256,
    ):
        if len(digest) != 64 or any(character not in "0123456789abcdef" for character in digest):
            raise ContractError("invalid SHA-256 binding")
    used_nonces.add(capability.nonce)


def acceptance_status(
    *,
    executed: bool,
    converged: bool,
    numerically_checked: bool,
    physically_validated: bool,
    independent_approval: bool,
) -> str:
    if not executed:
        return "PLANNED"
    if not converged:
        return "EXECUTED_NOT_CONVERGED"
    if not numerically_checked:
        return "CONVERGED_NOT_CHECKED"
    if not physically_validated:
        return "NUMERICALLY_CHECKED_NOT_PHYSICALLY_VALIDATED"
    if not independent_approval:
        return "PHYSICALLY_VALIDATED_ACCEPTANCE_HOLD"
    return "ACCEPTED"
