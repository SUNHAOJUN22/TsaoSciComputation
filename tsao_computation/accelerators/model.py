from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any

from ..errors import ContractError


class AcceleratorBackend(str, Enum):
    CPU = "cpu"
    OPENMP = "openmp"
    MPI = "mpi"
    TASK_PARALLEL = "task-parallel"
    REMOTE = "remote"
    CUDA = "cuda"
    HIP = "hip"
    SYCL = "sycl"
    OPENCL = "opencl"
    KOKKOS = "kokkos"


class PlacementTarget(str, Enum):
    EDGE = "edge"
    LOCAL = "local"
    WORKSTATION = "workstation"
    HPC = "hpc"
    CLOUD = "cloud"


class AcceleratorPolicy(str, Enum):
    DISABLED = "disabled"
    PREFERRED = "preferred"
    REQUIRED = "required"


class PrecisionPolicy(str, Enum):
    FP64 = "fp64"
    FP32 = "fp32"
    MIXED = "mixed"
    BF16 = "bf16"
    FP16 = "fp16"


@dataclass(frozen=True, slots=True)
class AcceleratorDevice:
    backend: AcceleratorBackend
    index: int
    name: str
    memory_gib: float | None = None
    architecture: str | None = None
    vendor: str | None = None

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["backend"] = self.backend.value
        return payload


@dataclass(frozen=True, slots=True)
class AcceleratorInventory:
    logical_cpu_count: int
    architecture: str
    operating_system: str
    memory_gib: float | None
    backends: tuple[AcceleratorBackend, ...]
    devices: tuple[AcceleratorDevice, ...] = ()
    tools: tuple[str, ...] = ()
    python_modules: tuple[str, ...] = ()
    placements: tuple[PlacementTarget, ...] = (PlacementTarget.LOCAL,)
    claim_boundary: str = (
        "Hardware and library detection is planning evidence only; it does not prove solver "
        "compatibility, numerical speedup, convergence, physical validity, or authorization."
    )

    def has_backend(self, backend: AcceleratorBackend | str) -> bool:
        normalized = (
            backend if isinstance(backend, AcceleratorBackend) else AcceleratorBackend(backend)
        )
        return normalized in self.backends

    def devices_for(self, backend: AcceleratorBackend | str) -> tuple[AcceleratorDevice, ...]:
        normalized = (
            backend if isinstance(backend, AcceleratorBackend) else AcceleratorBackend(backend)
        )
        return tuple(device for device in self.devices if device.backend is normalized)

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["backends"] = [item.value for item in self.backends]
        payload["placements"] = [item.value for item in self.placements]
        payload["devices"] = [item.to_dict() for item in self.devices]
        return payload


def _positive_int(value: object, field_name: str) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ContractError(f"{field_name} must be a positive integer")
    return value


def _positive_float(value: object, field_name: str) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ContractError(f"{field_name} must be a positive finite number")
    parsed = float(value)
    if not math.isfinite(parsed) or parsed <= 0:
        raise ContractError(f"{field_name} must be a positive finite number")
    return parsed


def _enum_value(enum_type: type[Enum], value: object, field_name: str) -> Any:
    if not isinstance(value, str):
        raise ContractError(f"{field_name} must be a string")
    try:
        return enum_type(value)
    except ValueError as error:
        choices = [item.value for item in enum_type]
        raise ContractError(f"{field_name} must be one of {choices}") from error


@dataclass(frozen=True, slots=True)
class ComputeResourceRequest:
    placement: PlacementTarget = PlacementTarget.LOCAL
    accelerator_policy: AcceleratorPolicy = AcceleratorPolicy.PREFERRED
    preferred_backends: tuple[AcceleratorBackend, ...] = (
        AcceleratorBackend.CUDA,
        AcceleratorBackend.HIP,
        AcceleratorBackend.SYCL,
        AcceleratorBackend.OPENMP,
        AcceleratorBackend.MPI,
        AcceleratorBackend.TASK_PARALLEL,
        AcceleratorBackend.REMOTE,
        AcceleratorBackend.CPU,
    )
    cpu_cores: int | None = None
    memory_gib: float | None = None
    mpi_ranks: int | None = None
    threads_per_rank: int | None = None
    accelerator_count: int | None = None
    minimum_vram_gib: float | None = None
    precision: PrecisionPolicy = PrecisionPolicy.FP64
    deterministic: bool = True
    maximum_wall_seconds: float | None = None
    maximum_energy_kwh: float | None = None
    power_limit_watts: float | None = None
    allow_fallback: bool = True

    @classmethod
    def from_mapping(cls, value: Mapping[str, object] | None) -> ComputeResourceRequest:
        if value is None:
            return cls()
        if not isinstance(value, Mapping):
            raise ContractError("compute resources must be an object")
        allowed = {
            "placement",
            "accelerator_policy",
            "preferred_backends",
            "cpu_cores",
            "memory_gib",
            "mpi_ranks",
            "threads_per_rank",
            "accelerator_count",
            "minimum_vram_gib",
            "precision",
            "deterministic",
            "maximum_wall_seconds",
            "maximum_energy_kwh",
            "power_limit_watts",
            "allow_fallback",
        }
        unknown = sorted(set(value) - allowed)
        if unknown:
            raise ContractError(f"unknown compute resource fields: {unknown}")
        raw_backends = value.get(
            "preferred_backends", [item.value for item in cls().preferred_backends]
        )
        if isinstance(raw_backends, str) or not isinstance(raw_backends, (list, tuple)):
            raise ContractError("preferred_backends must be an array")
        backends = tuple(
            _enum_value(AcceleratorBackend, item, "preferred_backends") for item in raw_backends
        )
        if not backends or len(set(backends)) != len(backends):
            raise ContractError("preferred_backends must be non-empty and unique")
        deterministic = value.get("deterministic", True)
        fallback = value.get("allow_fallback", True)
        if not isinstance(deterministic, bool) or not isinstance(fallback, bool):
            raise ContractError("deterministic and allow_fallback must be booleans")
        return cls(
            placement=_enum_value(
                PlacementTarget, value.get("placement", PlacementTarget.LOCAL.value), "placement"
            ),
            accelerator_policy=_enum_value(
                AcceleratorPolicy,
                value.get("accelerator_policy", AcceleratorPolicy.PREFERRED.value),
                "accelerator_policy",
            ),
            preferred_backends=backends,
            cpu_cores=_positive_int(value.get("cpu_cores"), "cpu_cores"),
            memory_gib=_positive_float(value.get("memory_gib"), "memory_gib"),
            mpi_ranks=_positive_int(value.get("mpi_ranks"), "mpi_ranks"),
            threads_per_rank=_positive_int(value.get("threads_per_rank"), "threads_per_rank"),
            accelerator_count=_positive_int(value.get("accelerator_count"), "accelerator_count"),
            minimum_vram_gib=_positive_float(value.get("minimum_vram_gib"), "minimum_vram_gib"),
            precision=_enum_value(
                PrecisionPolicy, value.get("precision", PrecisionPolicy.FP64.value), "precision"
            ),
            deterministic=deterministic,
            maximum_wall_seconds=_positive_float(
                value.get("maximum_wall_seconds"), "maximum_wall_seconds"
            ),
            maximum_energy_kwh=_positive_float(
                value.get("maximum_energy_kwh"), "maximum_energy_kwh"
            ),
            power_limit_watts=_positive_float(value.get("power_limit_watts"), "power_limit_watts"),
            allow_fallback=fallback,
        )

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["placement"] = self.placement.value
        payload["accelerator_policy"] = self.accelerator_policy.value
        payload["preferred_backends"] = [item.value for item in self.preferred_backends]
        payload["precision"] = self.precision.value
        return payload


ResourceRequest = ComputeResourceRequest
HardwareInventory = AcceleratorInventory
