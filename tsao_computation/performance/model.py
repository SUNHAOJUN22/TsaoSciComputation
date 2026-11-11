from __future__ import annotations

from dataclasses import asdict, dataclass

from ..hashing import canonical_json_sha256
from ..validation.numerical import _finite_scalar


def canonical_sha256(value: object) -> str:
    """Backward-compatible alias for the shared canonical digest contract."""

    return canonical_json_sha256(value)


def _finite_non_negative(value: float, field_name: str) -> float:
    try:
        parsed = _finite_scalar(value, name=field_name)
    except ValueError as error:
        raise ValueError(f"{field_name} must be a finite non-negative number") from error
    if parsed < 0:
        raise ValueError(f"{field_name} must be a finite non-negative number")
    return parsed


def _integer_count(value: int, field_name: str, *, minimum: int) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        qualifier = "positive" if minimum == 1 else "non-negative"
        raise ValueError(f"{field_name} must be a {qualifier} integer")


@dataclass(frozen=True, slots=True)
class PerformanceEnvironment:
    python_version: str
    python_implementation: str
    operating_system: str
    machine: str
    processor: str
    logical_cpu_count: int

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["environment_sha256"] = canonical_sha256(payload)
        return payload


@dataclass(frozen=True, slots=True)
class WorkloadSample:
    wall_seconds: float
    cpu_seconds: float
    peak_bytes: int
    operations: int

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "wall_seconds",
            _finite_non_negative(self.wall_seconds, "wall_seconds"),
        )
        object.__setattr__(
            self,
            "cpu_seconds",
            _finite_non_negative(self.cpu_seconds, "cpu_seconds"),
        )
        _integer_count(self.peak_bytes, "peak_bytes", minimum=0)
        _integer_count(self.operations, "operations", minimum=1)

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class WorkloadProfile:
    slug: str
    description: str
    tags: tuple[str, ...]
    warmups: int
    repeats: int
    operations_per_sample: int
    samples: tuple[WorkloadSample, ...]
    median_wall_seconds: float
    mad_wall_seconds: float
    p95_wall_seconds: float
    median_cpu_seconds: float
    median_peak_bytes: int
    median_operations_per_second: float
    input_sha256: str
    claim_boundary: str = (
        "Same-process local benchmark evidence only. Results do not establish solver speedup, "
        "cross-host comparability, numerical equivalence, energy improvement, or production fitness."
    )

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["tags"] = list(self.tags)
        payload["samples"] = [item.to_dict() for item in self.samples]
        return payload


@dataclass(frozen=True, slots=True)
class PerformanceProfile:
    environment: PerformanceEnvironment
    workloads: tuple[WorkloadProfile, ...]
    schema_version: str = "1.0"
    claim_boundary: str = (
        "Benchmark measurements are host-, workload-, cache-, and configuration-specific. "
        "They are qualification evidence, not universal performance claims."
    )

    def to_dict(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "schema_version": self.schema_version,
            "environment": self.environment.to_dict(),
            "workloads": [item.to_dict() for item in self.workloads],
            "claim_boundary": self.claim_boundary,
        }
        payload["profile_sha256"] = canonical_sha256(payload)
        return payload
