from __future__ import annotations

import importlib.util
import os
import platform
import re
import shutil
from collections.abc import Callable
from pathlib import Path

from ..security.process import safe_run
from .model import (
    AcceleratorBackend,
    AcceleratorDevice,
    AcceleratorInventory,
    PlacementTarget,
)

_TOOL_CANDIDATES = (
    "nvidia-smi",
    "nvcc",
    "rocminfo",
    "hipcc",
    "sycl-ls",
    "dpcpp",
    "icpx",
    "clinfo",
    "mpirun",
    "mpiexec",
    "srun",
    "sbatch",
    "qsub",
)
_MODULE_CANDIDATES = (
    "cupy",
    "torch",
    "jax",
    "nvmath",
    "cuequivariance",
    "cuequivariance_torch",
    "cuequivariance_jax",
    "mpi4py",
    "dask",
)


def _memory_gib() -> float | None:
    if os.name != "posix":
        return None
    try:
        pages = os.sysconf("SC_PHYS_PAGES")
        page_size = os.sysconf("SC_PAGE_SIZE")
    except (OSError, ValueError):
        return None
    if not isinstance(pages, int) or not isinstance(page_size, int) or pages <= 0 or page_size <= 0:
        return None
    return round(pages * page_size / (1024**3), 3)


def _command_output(executable: str, arguments: tuple[str, ...]) -> str:
    result = safe_run((executable, *arguments), cwd=Path.cwd(), timeout=8)
    return result.stdout if result.returncode == 0 else ""


def _nvidia_devices(executable: str, runner: Callable[[str, tuple[str, ...]], str]) -> tuple[AcceleratorDevice, ...]:
    output = runner(
        executable,
        (
            "--query-gpu=index,name,memory.total,compute_cap",
            "--format=csv,noheader,nounits",
        ),
    )
    devices: list[AcceleratorDevice] = []
    for line in output.splitlines():
        parts = [part.strip() for part in line.split(",")]
        if len(parts) < 3:
            continue
        try:
            index = int(parts[0])
            memory_gib = round(float(parts[2]) / 1024, 3)
        except ValueError:
            continue
        architecture = parts[3] if len(parts) > 3 and parts[3] else None
        devices.append(
            AcceleratorDevice(
                backend=AcceleratorBackend.CUDA,
                index=index,
                name=parts[1] or f"NVIDIA GPU {index}",
                memory_gib=memory_gib,
                architecture=architecture,
                vendor="NVIDIA",
            )
        )
    return tuple(devices)


def _jetson_detected() -> bool:
    model = Path("/proc/device-tree/model")
    try:
        return "jetson" in model.read_text(encoding="utf-8", errors="ignore").casefold()
    except OSError:
        return False


def probe_accelerators(
    *,
    which: Callable[[str], str | None] = shutil.which,
    runner: Callable[[str, tuple[str, ...]], str] = _command_output,
    module_finder: Callable[[str], object | None] = importlib.util.find_spec,
) -> AcceleratorInventory:
    found = {name: path for name in _TOOL_CANDIDATES if (path := which(name))}
    modules = tuple(sorted(name for name in _MODULE_CANDIDATES if module_finder(name) is not None))
    backends: set[AcceleratorBackend] = {AcceleratorBackend.CPU}
    logical_cpus = max(1, os.cpu_count() or 1)
    if logical_cpus > 1:
        backends.update({AcceleratorBackend.OPENMP, AcceleratorBackend.TASK_PARALLEL})
    if {"mpirun", "mpiexec", "srun"} & found.keys():
        backends.add(AcceleratorBackend.MPI)
    if {"nvidia-smi", "nvcc"} & found.keys():
        backends.add(AcceleratorBackend.CUDA)
    if {"rocminfo", "hipcc"} & found.keys():
        backends.add(AcceleratorBackend.HIP)
    if {"sycl-ls", "dpcpp", "icpx"} & found.keys():
        backends.add(AcceleratorBackend.SYCL)
    if "clinfo" in found:
        backends.add(AcceleratorBackend.OPENCL)

    devices: tuple[AcceleratorDevice, ...] = ()
    if "nvidia-smi" in found:
        devices = _nvidia_devices(found["nvidia-smi"], runner)

    placements = {PlacementTarget.LOCAL}
    if logical_cpus >= 8 or devices:
        placements.add(PlacementTarget.WORKSTATION)
    if {"srun", "sbatch", "qsub"} & found.keys():
        placements.add(PlacementTarget.HPC)
    architecture = platform.machine() or "unknown"
    if _jetson_detected() or re.search(r"(?:aarch64|arm64)", architecture, re.I):
        placements.add(PlacementTarget.EDGE)

    return AcceleratorInventory(
        logical_cpu_count=logical_cpus,
        architecture=architecture,
        operating_system=platform.system() or os.name,
        memory_gib=_memory_gib(),
        backends=tuple(sorted(backends, key=lambda item: item.value)),
        devices=devices,
        tools=tuple(sorted(found)),
        python_modules=modules,
        placements=tuple(sorted(placements, key=lambda item: item.value)),
    )


probe_hardware = probe_accelerators
