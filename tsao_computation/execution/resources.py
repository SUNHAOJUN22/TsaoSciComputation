from __future__ import annotations

import hashlib
import json
import threading
from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from dataclasses import asdict, dataclass

from ..errors import SecurityError


def _positive_int(value: int, field_name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError(f"{field_name} must be a positive integer")
    return value


def _gpu_devices(value: tuple[int, ...], field_name: str) -> tuple[int, ...]:
    if any(isinstance(item, bool) or not isinstance(item, int) or item < 0 for item in value):
        raise ValueError(f"{field_name} must contain non-negative integers")
    if len(set(value)) != len(value):
        raise ValueError(f"{field_name} must be unique")
    return tuple(value)


def _license_tokens(
    value: tuple[tuple[str, int], ...],
    field_name: str,
) -> tuple[tuple[str, int], ...]:
    normalized: list[tuple[str, int]] = []
    for name, count in value:
        if not isinstance(name, str) or not name.strip():
            raise ValueError(f"{field_name} names must be non-empty strings")
        normalized.append((name.strip(), _positive_int(count, field_name)))
    if len({name for name, _ in normalized}) != len(normalized):
        raise ValueError(f"{field_name} names must be unique")
    return tuple(sorted(normalized))


def _sha256(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class ExecutionResourceClaim:
    cpu_cores: int = 1
    gpu_devices: tuple[int, ...] = ()
    license_tokens: tuple[tuple[str, int], ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "cpu_cores", _positive_int(self.cpu_cores, "cpu_cores"))
        object.__setattr__(
            self,
            "gpu_devices",
            _gpu_devices(self.gpu_devices, "gpu_devices"),
        )
        object.__setattr__(
            self,
            "license_tokens",
            _license_tokens(self.license_tokens, "license_tokens"),
        )

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["gpu_devices"] = list(self.gpu_devices)
        payload["license_tokens"] = dict(self.license_tokens)
        return payload

    @property
    def sha256(self) -> str:
        return _sha256(self.to_dict())


@dataclass(frozen=True, slots=True)
class ExecutionResourceCapacity:
    cpu_cores: int
    gpu_devices: tuple[int, ...] = ()
    license_tokens: tuple[tuple[str, int], ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "cpu_cores", _positive_int(self.cpu_cores, "cpu_cores"))
        object.__setattr__(
            self,
            "gpu_devices",
            _gpu_devices(self.gpu_devices, "gpu_devices"),
        )
        object.__setattr__(
            self,
            "license_tokens",
            _license_tokens(self.license_tokens, "license_tokens"),
        )

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["gpu_devices"] = list(self.gpu_devices)
        payload["license_tokens"] = dict(self.license_tokens)
        return payload

    @property
    def sha256(self) -> str:
        return _sha256(self.to_dict())


class ExecutionResourceBroker:
    def __init__(self, capacity: ExecutionResourceCapacity) -> None:
        self.capacity = capacity
        self._available_cpu = capacity.cpu_cores
        self._available_gpus = set(capacity.gpu_devices)
        self._available_licenses = dict(capacity.license_tokens)
        self._condition = threading.Condition()

    def _assert_fits(self, claim: ExecutionResourceClaim) -> None:
        if claim.cpu_cores > self.capacity.cpu_cores:
            raise SecurityError("resource claim exceeds CPU capacity")
        if not set(claim.gpu_devices) <= set(self.capacity.gpu_devices):
            raise SecurityError("resource claim requests unavailable GPU devices")
        capacity_licenses = dict(self.capacity.license_tokens)
        for name, count in claim.license_tokens:
            if count > capacity_licenses.get(name, 0):
                raise SecurityError(f"resource claim exceeds license capacity: {name}")

    def _available(self, claim: ExecutionResourceClaim) -> bool:
        if claim.cpu_cores > self._available_cpu:
            return False
        if not set(claim.gpu_devices) <= self._available_gpus:
            return False
        return all(
            count <= self._available_licenses.get(name, 0) for name, count in claim.license_tokens
        )

    @contextmanager
    def lease(self, claim: ExecutionResourceClaim) -> Iterator[None]:
        self._assert_fits(claim)
        with self._condition:
            self._condition.wait_for(lambda: self._available(claim))
            self._available_cpu -= claim.cpu_cores
            self._available_gpus.difference_update(claim.gpu_devices)
            for name, count in claim.license_tokens:
                self._available_licenses[name] -= count
        try:
            yield
        finally:
            with self._condition:
                self._available_cpu += claim.cpu_cores
                self._available_gpus.update(claim.gpu_devices)
                for name, count in claim.license_tokens:
                    self._available_licenses[name] = self._available_licenses.get(name, 0) + count
                self._condition.notify_all()


def validate_resource_binding(
    environment: Mapping[str, str],
    claim: ExecutionResourceClaim,
) -> None:
    if not claim.gpu_devices:
        return
    raw = (
        environment.get("CUDA_VISIBLE_DEVICES")
        or environment.get("HIP_VISIBLE_DEVICES")
        or environment.get("ROCR_VISIBLE_DEVICES")
    )
    if raw is None:
        raise SecurityError("GPU resource claim requires a bound visible-device environment")
    try:
        bound = tuple(int(item.strip()) for item in raw.split(",") if item.strip())
    except ValueError as error:
        raise SecurityError(
            "visible-device environment is not a comma-separated integer list"
        ) from error
    if tuple(claim.gpu_devices) != bound:
        raise SecurityError("GPU resource claim does not match the immutable command environment")
