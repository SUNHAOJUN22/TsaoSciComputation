from __future__ import annotations

import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def write(relative: str, content: str) -> None:
    path = ROOT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(content).lstrip(), encoding="utf-8", newline="\n")


write(
    "tsao_computation/accelerators/model.py",
    r'''
    from __future__ import annotations

    import math
    from collections.abc import Iterable, Mapping
    from dataclasses import asdict, dataclass
    from enum import Enum
    from typing import Any, TypeVar

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


    E = TypeVar("E", bound=Enum)


    def _required_string(value: object, field_name: str) -> str:
        if not isinstance(value, str) or not value.strip():
            raise ContractError(f"{field_name} must be a non-empty string")
        return value.strip()


    def _optional_string(value: object, field_name: str) -> str | None:
        return None if value is None else _required_string(value, field_name)


    def _positive_int(value: object, field_name: str) -> int | None:
        if value is None:
            return None
        if isinstance(value, bool) or not isinstance(value, int) or value < 1:
            raise ContractError(f"{field_name} must be a positive integer")
        return value


    def _non_negative_int(value: object, field_name: str) -> int:
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ContractError(f"{field_name} must be a non-negative integer")
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


    def _enum_value(enum_type: type[E], value: object, field_name: str) -> E:
        if isinstance(value, enum_type):
            return value
        if not isinstance(value, str):
            raise ContractError(f"{field_name} must be a string")
        try:
            return enum_type(value)
        except ValueError as error:
            choices = [item.value for item in enum_type]
            raise ContractError(f"{field_name} must be one of {choices}") from error


    def _enum_tuple(
        enum_type: type[E], value: object, field_name: str, *, non_empty: bool = True
    ) -> tuple[E, ...]:
        if isinstance(value, str) or not isinstance(value, Iterable):
            raise ContractError(f"{field_name} must be an array")
        parsed = tuple(_enum_value(enum_type, item, field_name) for item in value)
        if non_empty and not parsed:
            raise ContractError(f"{field_name} must be non-empty")
        if len(set(parsed)) != len(parsed):
            raise ContractError(f"{field_name} must be unique")
        return parsed


    def _string_tuple(value: object, field_name: str) -> tuple[str, ...]:
        if isinstance(value, str) or not isinstance(value, Iterable):
            raise ContractError(f"{field_name} must be an array")
        parsed = tuple(_required_string(item, field_name) for item in value)
        if len(set(parsed)) != len(parsed):
            raise ContractError(f"{field_name} must be unique")
        return parsed


    @dataclass(frozen=True, slots=True)
    class AcceleratorDevice:
        backend: AcceleratorBackend
        index: int
        name: str
        memory_gib: float | None = None
        architecture: str | None = None
        vendor: str | None = None

        def __post_init__(self) -> None:
            object.__setattr__(
                self, "backend", _enum_value(AcceleratorBackend, self.backend, "backend")
            )
            object.__setattr__(self, "index", _non_negative_int(self.index, "index"))
            object.__setattr__(self, "name", _required_string(self.name, "name"))
            object.__setattr__(
                self, "memory_gib", _positive_float(self.memory_gib, "memory_gib")
            )
            object.__setattr__(
                self, "architecture", _optional_string(self.architecture, "architecture")
            )
            object.__setattr__(self, "vendor", _optional_string(self.vendor, "vendor"))

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

        def __post_init__(self) -> None:
            cpu_count = _positive_int(self.logical_cpu_count, "logical_cpu_count")
            assert cpu_count is not None
            object.__setattr__(self, "logical_cpu_count", cpu_count)
            object.__setattr__(
                self, "architecture", _required_string(self.architecture, "architecture")
            )
            object.__setattr__(
                self,
                "operating_system",
                _required_string(self.operating_system, "operating_system"),
            )
            object.__setattr__(
                self, "memory_gib", _positive_float(self.memory_gib, "memory_gib")
            )
            backends = _enum_tuple(AcceleratorBackend, self.backends, "backends")
            object.__setattr__(self, "backends", backends)
            if isinstance(self.devices, (str, bytes)) or not isinstance(self.devices, Iterable):
                raise ContractError("devices must be an array")
            devices = tuple(self.devices)
            if any(not isinstance(item, AcceleratorDevice) for item in devices):
                raise ContractError("devices must contain AcceleratorDevice records")
            if any(item.backend not in backends for item in devices):
                raise ContractError("device backends must be declared in inventory backends")
            keys = tuple((item.backend, item.index) for item in devices)
            if len(set(keys)) != len(keys):
                raise ContractError("device backend/index pairs must be unique")
            object.__setattr__(self, "devices", devices)
            object.__setattr__(self, "tools", _string_tuple(self.tools, "tools"))
            object.__setattr__(
                self, "python_modules", _string_tuple(self.python_modules, "python_modules")
            )
            object.__setattr__(
                self,
                "placements",
                _enum_tuple(PlacementTarget, self.placements, "placements"),
            )
            object.__setattr__(
                self,
                "claim_boundary",
                _required_string(self.claim_boundary, "claim_boundary"),
            )

        def has_backend(self, backend: AcceleratorBackend | str) -> bool:
            normalized = _enum_value(AcceleratorBackend, backend, "backend")
            return normalized in self.backends

        def devices_for(self, backend: AcceleratorBackend | str) -> tuple[AcceleratorDevice, ...]:
            normalized = _enum_value(AcceleratorBackend, backend, "backend")
            return tuple(device for device in self.devices if device.backend == normalized)

        def to_dict(self) -> dict[str, object]:
            payload = asdict(self)
            payload["backends"] = [item.value for item in self.backends]
            payload["placements"] = [item.value for item in self.placements]
            payload["devices"] = [item.to_dict() for item in self.devices]
            return payload


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

        def __post_init__(self) -> None:
            object.__setattr__(
                self, "placement", _enum_value(PlacementTarget, self.placement, "placement")
            )
            object.__setattr__(
                self,
                "accelerator_policy",
                _enum_value(AcceleratorPolicy, self.accelerator_policy, "accelerator_policy"),
            )
            object.__setattr__(
                self,
                "preferred_backends",
                _enum_tuple(
                    AcceleratorBackend, self.preferred_backends, "preferred_backends"
                ),
            )
            for field_name in (
                "cpu_cores",
                "mpi_ranks",
                "threads_per_rank",
                "accelerator_count",
            ):
                object.__setattr__(
                    self, field_name, _positive_int(getattr(self, field_name), field_name)
                )
            for field_name in (
                "memory_gib",
                "minimum_vram_gib",
                "maximum_wall_seconds",
                "maximum_energy_kwh",
                "power_limit_watts",
            ):
                object.__setattr__(
                    self, field_name, _positive_float(getattr(self, field_name), field_name)
                )
            object.__setattr__(
                self, "precision", _enum_value(PrecisionPolicy, self.precision, "precision")
            )
            if not isinstance(self.deterministic, bool) or not isinstance(
                self.allow_fallback, bool
            ):
                raise ContractError("deterministic and allow_fallback must be booleans")

        @classmethod
        def from_mapping(cls, value: Mapping[str, object] | None) -> ComputeResourceRequest:
            if value is None:
                return cls()
            if not isinstance(value, Mapping):
                raise ContractError("compute resources must be an object")
            allowed = {
                "placement", "accelerator_policy", "preferred_backends", "cpu_cores",
                "memory_gib", "mpi_ranks", "threads_per_rank", "accelerator_count",
                "minimum_vram_gib", "precision", "deterministic", "maximum_wall_seconds",
                "maximum_energy_kwh", "power_limit_watts", "allow_fallback",
            }
            unknown = sorted(set(value) - allowed)
            if unknown:
                raise ContractError(f"unknown compute resource fields: {unknown}")
            raw_backends = value.get(
                "preferred_backends", [item.value for item in cls().preferred_backends]
            )
            if isinstance(raw_backends, str) or not isinstance(raw_backends, (list, tuple)):
                raise ContractError("preferred_backends must be an array")
            return cls(
                placement=_enum_value(
                    PlacementTarget,
                    value.get("placement", PlacementTarget.LOCAL.value),
                    "placement",
                ),
                accelerator_policy=_enum_value(
                    AcceleratorPolicy,
                    value.get("accelerator_policy", AcceleratorPolicy.PREFERRED.value),
                    "accelerator_policy",
                ),
                preferred_backends=tuple(
                    _enum_value(AcceleratorBackend, item, "preferred_backends")
                    for item in raw_backends
                ),
                cpu_cores=_positive_int(value.get("cpu_cores"), "cpu_cores"),
                memory_gib=_positive_float(value.get("memory_gib"), "memory_gib"),
                mpi_ranks=_positive_int(value.get("mpi_ranks"), "mpi_ranks"),
                threads_per_rank=_positive_int(
                    value.get("threads_per_rank"), "threads_per_rank"
                ),
                accelerator_count=_positive_int(
                    value.get("accelerator_count"), "accelerator_count"
                ),
                minimum_vram_gib=_positive_float(
                    value.get("minimum_vram_gib"), "minimum_vram_gib"
                ),
                precision=_enum_value(
                    PrecisionPolicy,
                    value.get("precision", PrecisionPolicy.FP64.value),
                    "precision",
                ),
                deterministic=value.get("deterministic", True),  # type: ignore[arg-type]
                maximum_wall_seconds=_positive_float(
                    value.get("maximum_wall_seconds"), "maximum_wall_seconds"
                ),
                maximum_energy_kwh=_positive_float(
                    value.get("maximum_energy_kwh"), "maximum_energy_kwh"
                ),
                power_limit_watts=_positive_float(
                    value.get("power_limit_watts"), "power_limit_watts"
                ),
                allow_fallback=value.get("allow_fallback", True),  # type: ignore[arg-type]
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
    ''',
)

write(
    "tsao_computation/accelerators/planner.py",
    r'''
    from __future__ import annotations

    import hashlib
    import json
    from collections.abc import Mapping
    from dataclasses import asdict, dataclass
    from functools import cache
    from typing import Any

    from ..errors import ContractError
    from ..immutable import freeze_json, thaw_json
    from ..registries import accelerators as accelerator_records
    from .catalog import recommend_acceleration_libraries
    from .model import (
        AcceleratorBackend,
        AcceleratorInventory,
        AcceleratorPolicy,
        ComputeResourceRequest,
        PlacementTarget,
        PrecisionPolicy,
    )
    from .probe import probe_accelerators

    _PHYSICAL_ACCELERATOR_BACKENDS = {
        AcceleratorBackend.CUDA,
        AcceleratorBackend.HIP,
        AcceleratorBackend.SYCL,
        AcceleratorBackend.OPENCL,
    }
    _LOCAL_PLACEMENTS = {
        PlacementTarget.EDGE,
        PlacementTarget.LOCAL,
        PlacementTarget.WORKSTATION,
    }


    def _request_sha256(request: ComputeResourceRequest) -> str:
        encoded = json.dumps(
            request.to_dict(), sort_keys=True, separators=(",", ":"), allow_nan=False
        )
        return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


    @dataclass(frozen=True, slots=True)
    class AccelerationPlan:
        adapter_slug: str
        workflow: str
        backend: AcceleratorBackend
        placement: PlacementTarget
        execution_mode: str
        cpu_cores: int
        mpi_ranks: int
        threads_per_rank: int
        device_indices: tuple[int, ...]
        library_candidates: tuple[str, ...]
        environment: dict[str, str]
        precision: PrecisionPolicy
        deterministic: bool
        allow_fallback: bool
        resource_request: dict[str, object]
        resource_request_sha256: str
        fallback_used: bool
        reason: str
        claim_boundary: str

        def __post_init__(self) -> None:
            object.__setattr__(self, "environment", freeze_json(dict(self.environment)))
            object.__setattr__(
                self, "resource_request", freeze_json(dict(self.resource_request))
            )

        def to_dict(self) -> dict[str, object]:
            payload = asdict(self)
            payload["backend"] = self.backend.value
            payload["placement"] = self.placement.value
            payload["precision"] = self.precision.value
            payload["device_indices"] = list(self.device_indices)
            payload["library_candidates"] = list(self.library_candidates)
            payload["environment"] = thaw_json(self.environment)
            payload["resource_request"] = thaw_json(self.resource_request)
            return payload


    @cache
    def _profile(slug: str) -> dict[str, Any]:
        for record in accelerator_records():
            if str(record.get("slug")) == slug:
                return dict(record)
        raise KeyError(f"unknown accelerator profile: {slug}")


    def _record_backends(
        record: Mapping[str, object], key: str
    ) -> tuple[AcceleratorBackend, ...]:
        raw = record.get(key, [])
        if not isinstance(raw, list):
            return ()
        result: list[AcceleratorBackend] = []
        for item in raw:
            try:
                result.append(AcceleratorBackend(str(item)))
            except ValueError:
                continue
        return tuple(result)


    def _cpu_fallback(
        *, supported: set[AcceleratorBackend], adapter_slug: str
    ) -> AcceleratorBackend:
        if AcceleratorBackend.CPU not in supported:
            raise ContractError(f"adapter {adapter_slug} does not declare a CPU fallback")
        return AcceleratorBackend.CPU


    def plan_acceleration(
        adapter_slug: str,
        resources: ComputeResourceRequest | Mapping[str, object] | None = None,
        *,
        inventory: AcceleratorInventory | None = None,
    ) -> AccelerationPlan:
        request = (
            resources
            if isinstance(resources, ComputeResourceRequest)
            else ComputeResourceRequest.from_mapping(resources)
        )
        detected = inventory or probe_accelerators()
        record = _profile(adapter_slug)
        supported = set(_record_backends(record, "candidate_backends"))
        preferred = _record_backends(record, "preferred_backends")
        order = tuple(item for item in request.preferred_backends if item in supported)
        if not order:
            if not request.allow_fallback and request.accelerator_policy is not AcceleratorPolicy.DISABLED:
                raise ContractError(
                    f"none of the requested backends are supported by adapter {adapter_slug}"
                )
            order = tuple(item for item in preferred if item in supported)
        if (
            request.allow_fallback or request.accelerator_policy is AcceleratorPolicy.DISABLED
        ) and AcceleratorBackend.CPU in supported and AcceleratorBackend.CPU not in order:
            order += (AcceleratorBackend.CPU,)
        if not order:
            raise ContractError(f"adapter {adapter_slug} has no usable backend candidates")

        fallback = False
        if request.placement not in detected.placements:
            if (
                request.allow_fallback
                and request.placement is not PlacementTarget.EDGE
                and PlacementTarget.LOCAL in detected.placements
            ):
                placement = PlacementTarget.LOCAL
                fallback = True
            else:
                raise ContractError(
                    f"requested placement {request.placement.value} is unavailable in the detected environment"
                )
        else:
            placement = request.placement

        edge_suitability = str(record.get("edge_suitability", "unsuitable"))
        if placement is PlacementTarget.EDGE and edge_suitability == "unsuitable":
            raise ContractError(f"adapter {adapter_slug} is not suitable for edge placement")

        selected: AcceleratorBackend | None = None
        for candidate in order:
            if candidate in detected.backends:
                selected = candidate
                break

        first_requested = order[0]
        if request.accelerator_policy is AcceleratorPolicy.DISABLED:
            selected = _cpu_fallback(supported=supported, adapter_slug=adapter_slug)
        elif selected is None:
            if request.accelerator_policy is AcceleratorPolicy.REQUIRED or not request.allow_fallback:
                raise ContractError(
                    f"no requested backend is both supported by {adapter_slug} and detected locally"
                )
            selected = _cpu_fallback(supported=supported, adapter_slug=adapter_slug)
            fallback = True
        elif selected is not first_requested:
            if not request.allow_fallback:
                raise ContractError(
                    f"preferred backend {first_requested.value} is unavailable and fallback is disabled"
                )
            fallback = True

        if (
            request.accelerator_policy is AcceleratorPolicy.REQUIRED
            and selected not in _PHYSICAL_ACCELERATOR_BACKENDS
        ):
            raise ContractError(
                "an accelerator was required, but only CPU/MPI/task/remote/framework backends are available"
            )

        devices = detected.devices_for(selected)
        if selected in _PHYSICAL_ACCELERATOR_BACKENDS:
            count = request.accelerator_count or 1
            eligible = tuple(
                device
                for device in devices
                if request.minimum_vram_gib is None
                or (
                    device.memory_gib is not None
                    and device.memory_gib >= request.minimum_vram_gib
                )
            )
            if len(eligible) < count:
                if (
                    request.accelerator_policy is AcceleratorPolicy.REQUIRED
                    or not request.allow_fallback
                ):
                    raise ContractError(
                        "detected accelerator devices do not satisfy count or VRAM requirements"
                    )
                selected = _cpu_fallback(supported=supported, adapter_slug=adapter_slug)
                devices = ()
                fallback = True
            else:
                devices = eligible[:count]

        if placement in _LOCAL_PLACEMENTS and request.memory_gib is not None:
            if detected.memory_gib is None:
                raise ContractError(
                    "detected local memory is unknown; requested memory cannot be verified"
                )
            if request.memory_gib > detected.memory_gib:
                raise ContractError(
                    "requested memory exceeds the detected local resource envelope"
                )

        cpu_cores = request.cpu_cores or detected.logical_cpu_count
        if placement in _LOCAL_PLACEMENTS and cpu_cores > detected.logical_cpu_count:
            if not request.allow_fallback:
                raise ContractError(
                    "requested CPU cores exceed the detected local resource envelope"
                )
            cpu_cores = detected.logical_cpu_count
            fallback = True

        mpi_ranks = request.mpi_ranks or (
            1 if selected is not AcceleratorBackend.MPI else min(4, cpu_cores)
        )
        if placement in _LOCAL_PLACEMENTS and mpi_ranks > cpu_cores:
            if not request.allow_fallback:
                raise ContractError("MPI ranks exceed the detected local CPU resource envelope")
            mpi_ranks = cpu_cores
            fallback = True

        threads = request.threads_per_rank or max(1, cpu_cores // max(1, mpi_ranks))
        if placement in _LOCAL_PLACEMENTS and mpi_ranks * threads > cpu_cores:
            if not request.allow_fallback:
                raise ContractError(
                    "MPI ranks multiplied by threads per rank oversubscribe local CPUs"
                )
            threads = max(1, cpu_cores // max(1, mpi_ranks))
            fallback = True

        environment: dict[str, str] = {}
        if selected is AcceleratorBackend.CUDA and devices:
            environment["CUDA_VISIBLE_DEVICES"] = ",".join(
                str(item.index) for item in devices
            )
        if selected is AcceleratorBackend.HIP and devices:
            visible = ",".join(str(item.index) for item in devices)
            environment["HIP_VISIBLE_DEVICES"] = visible
            environment["ROCR_VISIBLE_DEVICES"] = visible
        if selected in {AcceleratorBackend.OPENMP, AcceleratorBackend.MPI}:
            environment["OMP_NUM_THREADS"] = str(threads)

        profile_libraries = tuple(
            str(item) for item in record.get("library_candidates", [])
        )
        compatible = {
            item.slug for item in recommend_acceleration_libraries(backend=selected)
        }
        libraries = tuple(item for item in profile_libraries if item in compatible)
        request_payload = request.to_dict()
        request_digest = _request_sha256(request)
        reason = (
            f"selected {selected.value} for {adapter_slug}; "
            f"supported={sorted(item.value for item in supported)}; "
            f"detected={sorted(item.value for item in detected.backends)}; "
            f"cpu_cores={cpu_cores}; mpi_ranks={mpi_ranks}; threads_per_rank={threads}; "
            f"precision={request.precision.value}; deterministic={request.deterministic}; "
            f"request_sha256={request_digest}"
        )
        return AccelerationPlan(
            adapter_slug=adapter_slug,
            workflow=str(record.get("workflow", "")),
            backend=selected,
            placement=placement,
            execution_mode=str(record.get("execution_mode", "solver-native")),
            cpu_cores=cpu_cores,
            mpi_ranks=mpi_ranks,
            threads_per_rank=threads,
            device_indices=tuple(item.index for item in devices),
            library_candidates=libraries,
            environment=environment,
            precision=request.precision,
            deterministic=request.deterministic,
            allow_fallback=request.allow_fallback,
            resource_request=request_payload,
            resource_request_sha256=request_digest,
            fallback_used=fallback,
            reason=reason,
            claim_boundary=str(
                record.get(
                    "claim_boundary",
                    "Planning metadata only; live execution and scientific validity are unverified.",
                )
            ),
        )


    def clear_acceleration_caches() -> None:
        _profile.cache_clear()


    acceleration_plan = plan_acceleration
    ''',
)

write(
    "tests/test_adversarial_acceleration_contract.py",
    r'''
    from __future__ import annotations

    import json

    import pytest

    from tsao_computation.accelerators import (
        AcceleratorBackend,
        AcceleratorDevice,
        AcceleratorInventory,
        AcceleratorPolicy,
        ComputeResourceRequest,
        PlacementTarget,
        PrecisionPolicy,
        plan_acceleration,
    )
    from tsao_computation.errors import ContractError


    def inventory(
        *,
        memory_gib: float | None = 64.0,
        backends: tuple[AcceleratorBackend, ...] = (
            AcceleratorBackend.CPU,
            AcceleratorBackend.OPENMP,
        ),
        devices: tuple[AcceleratorDevice, ...] = (),
    ) -> AcceleratorInventory:
        return AcceleratorInventory(
            logical_cpu_count=16,
            architecture="x86_64",
            operating_system="Linux",
            memory_gib=memory_gib,
            backends=backends,
            devices=devices,
        )


    @pytest.mark.parametrize(
        "kwargs",
        (
            {"cpu_cores": 0},
            {"memory_gib": float("nan")},
            {"preferred_backends": ()},
            {"deterministic": "yes"},
            {"allow_fallback": 1},
            {"precision": "invalid"},
        ),
    )
    def test_direct_resource_constructor_is_fail_closed(kwargs: dict[str, object]) -> None:
        with pytest.raises(ContractError):
            ComputeResourceRequest(**kwargs)  # type: ignore[arg-type]


    def test_device_and_inventory_direct_constructors_are_validated() -> None:
        with pytest.raises(ContractError, match="non-negative"):
            AcceleratorDevice(AcceleratorBackend.CUDA, -1, "GPU")
        with pytest.raises(ContractError, match="positive finite"):
            AcceleratorDevice(AcceleratorBackend.CUDA, 0, "GPU", 0.0)
        device = AcceleratorDevice("cuda", 0, "GPU", 24.0)  # type: ignore[arg-type]
        assert device.backend is AcceleratorBackend.CUDA
        with pytest.raises(ContractError, match="declared"):
            AcceleratorInventory(
                logical_cpu_count=8,
                architecture="x86_64",
                operating_system="Linux",
                memory_gib=32.0,
                backends=(AcceleratorBackend.CPU,),
                devices=(device,),
            )
        with pytest.raises(ContractError, match="unique"):
            AcceleratorInventory(
                logical_cpu_count=8,
                architecture="x86_64",
                operating_system="Linux",
                memory_gib=32.0,
                backends=(AcceleratorBackend.CPU, AcceleratorBackend.CPU),
            )


    def test_plan_preserves_complete_resource_contract_and_hash() -> None:
        request = ComputeResourceRequest(
            placement=PlacementTarget.LOCAL,
            accelerator_policy=AcceleratorPolicy.DISABLED,
            preferred_backends=(AcceleratorBackend.CPU,),
            cpu_cores=4,
            memory_gib=12.0,
            mpi_ranks=2,
            threads_per_rank=2,
            precision=PrecisionPolicy.MIXED,
            deterministic=False,
            maximum_wall_seconds=120.0,
            maximum_energy_kwh=0.5,
            power_limit_watts=150.0,
            allow_fallback=False,
        )
        plan = plan_acceleration("orca", request, inventory=inventory())
        payload = plan.to_dict()
        assert plan.cpu_cores == 4
        assert plan.precision is PrecisionPolicy.MIXED
        assert not plan.deterministic
        assert not plan.allow_fallback
        assert payload["resource_request"] == request.to_dict()
        assert len(plan.resource_request_sha256) == 64
        assert json.dumps(payload, sort_keys=True)
        with pytest.raises(TypeError, match="immutable"):
            plan.resource_request["cpu_cores"] = 9


    def test_local_memory_requirements_are_never_silently_weakened() -> None:
        with pytest.raises(ContractError, match="unknown"):
            plan_acceleration(
                "orca", {"memory_gib": 8.0}, inventory=inventory(memory_gib=None)
            )
        with pytest.raises(ContractError, match="exceeds"):
            plan_acceleration(
                "orca", {"memory_gib": 128.0}, inventory=inventory(memory_gib=64.0)
            )


    def test_disabled_fallback_rejects_secondary_backend_selection() -> None:
        detected = inventory(backends=(AcceleratorBackend.CPU,))
        with pytest.raises(ContractError, match="fallback is disabled"):
            plan_acceleration(
                "gromacs",
                {
                    "preferred_backends": ["cuda", "cpu"],
                    "accelerator_policy": "preferred",
                    "allow_fallback": False,
                },
                inventory=detected,
            )


    def test_accelerator_count_and_vram_are_bound_to_selected_devices() -> None:
        devices = (
            AcceleratorDevice(AcceleratorBackend.CUDA, 0, "GPU0", 24.0),
            AcceleratorDevice(AcceleratorBackend.CUDA, 1, "GPU1", 8.0),
        )
        detected = inventory(
            backends=(AcceleratorBackend.CPU, AcceleratorBackend.CUDA),
            devices=devices,
        )
        with pytest.raises(ContractError, match="count or VRAM"):
            plan_acceleration(
                "mace",
                {
                    "preferred_backends": ["cuda", "cpu"],
                    "accelerator_policy": "required",
                    "accelerator_count": 2,
                    "minimum_vram_gib": 16.0,
                    "allow_fallback": False,
                },
                inventory=detected,
            )
    ''',
)

print("adversarial acceleration contract candidate applied")
