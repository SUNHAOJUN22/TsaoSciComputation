from __future__ import annotations

from collections.abc import Mapping
from dataclasses import asdict, dataclass
from functools import cache
from typing import Any

from ..errors import ContractError
from ..registries import accelerators as accelerator_records
from .catalog import recommend_acceleration_libraries
from .model import (
    AcceleratorBackend,
    AcceleratorInventory,
    AcceleratorPolicy,
    ComputeResourceRequest,
    PlacementTarget,
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


@dataclass(frozen=True, slots=True)
class AccelerationPlan:
    adapter_slug: str
    workflow: str
    backend: AcceleratorBackend
    placement: PlacementTarget
    execution_mode: str
    mpi_ranks: int
    threads_per_rank: int
    device_indices: tuple[int, ...]
    library_candidates: tuple[str, ...]
    environment: dict[str, str]
    fallback_used: bool
    reason: str
    claim_boundary: str

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["backend"] = self.backend.value
        payload["placement"] = self.placement.value
        payload["device_indices"] = list(self.device_indices)
        payload["library_candidates"] = list(self.library_candidates)
        return payload


@cache
def _profile(slug: str) -> dict[str, Any]:
    for record in accelerator_records():
        if str(record.get("slug")) == slug:
            return dict(record)
    raise KeyError(f"unknown accelerator profile: {slug}")


def _record_backends(record: Mapping[str, object], key: str) -> tuple[AcceleratorBackend, ...]:
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
    *,
    supported: set[AcceleratorBackend],
    adapter_slug: str,
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
        order = tuple(item for item in preferred if item in supported)
    if AcceleratorBackend.CPU in supported and AcceleratorBackend.CPU not in order:
        order += (AcceleratorBackend.CPU,)

    fallback = False
    if request.placement not in detected.placements:
        if request.allow_fallback and request.placement is not PlacementTarget.EDGE:
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

    first_requested = order[0] if order else AcceleratorBackend.CPU
    if request.accelerator_policy is AcceleratorPolicy.DISABLED:
        selected = _cpu_fallback(supported=supported, adapter_slug=adapter_slug)
        fallback = fallback or first_requested is not AcceleratorBackend.CPU
    elif selected is None:
        if request.accelerator_policy is AcceleratorPolicy.REQUIRED or not request.allow_fallback:
            raise ContractError(
                f"no requested backend is both supported by {adapter_slug} and detected locally"
            )
        selected = _cpu_fallback(supported=supported, adapter_slug=adapter_slug)
        fallback = True
    elif selected is not first_requested:
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
            or (device.memory_gib is not None and device.memory_gib >= request.minimum_vram_gib)
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

    cpu_cores = request.cpu_cores or detected.logical_cpu_count
    if placement in _LOCAL_PLACEMENTS and cpu_cores > detected.logical_cpu_count:
        if not request.allow_fallback:
            raise ContractError("requested CPU cores exceed the detected local resource envelope")
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
            raise ContractError("MPI ranks multiplied by threads per rank oversubscribe local CPUs")
        threads = max(1, cpu_cores // max(1, mpi_ranks))
        fallback = True

    environment: dict[str, str] = {}
    if selected is AcceleratorBackend.CUDA and devices:
        environment["CUDA_VISIBLE_DEVICES"] = ",".join(str(item.index) for item in devices)
    if selected is AcceleratorBackend.HIP and devices:
        visible = ",".join(str(item.index) for item in devices)
        environment["HIP_VISIBLE_DEVICES"] = visible
        environment["ROCR_VISIBLE_DEVICES"] = visible
    if selected in {AcceleratorBackend.OPENMP, AcceleratorBackend.MPI}:
        environment["OMP_NUM_THREADS"] = str(threads)

    profile_libraries = tuple(str(item) for item in record.get("library_candidates", []))
    compatible = {item.slug for item in recommend_acceleration_libraries(backend=selected)}
    libraries = tuple(item for item in profile_libraries if item in compatible)
    reason = (
        f"selected {selected.value} for {adapter_slug}; "
        f"supported={sorted(item.value for item in supported)}; "
        f"detected={sorted(item.value for item in detected.backends)}; "
        f"cpu_cores={cpu_cores}; mpi_ranks={mpi_ranks}; threads_per_rank={threads}"
    )
    return AccelerationPlan(
        adapter_slug=adapter_slug,
        workflow=str(record.get("workflow", "")),
        backend=selected,
        placement=placement,
        execution_mode=str(record.get("execution_mode", "solver-native")),
        mpi_ranks=mpi_ranks,
        threads_per_rank=threads,
        device_indices=tuple(item.index for item in devices),
        library_candidates=libraries,
        environment=environment,
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
