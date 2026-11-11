from __future__ import annotations

import math
import sys
from decimal import Decimal
from enum import IntEnum
from fractions import Fraction

import pytest

from tsao_computation.performance import WorkloadSample, WorkloadSpec
from tsao_computation.performance import runner as performance_runner


@pytest.mark.parametrize("field", ["wall_seconds", "cpu_seconds"])
@pytest.mark.parametrize(
    "value",
    [
        pytest.param(True, id="boolean-true"),
        pytest.param(False, id="boolean-false"),
        pytest.param("1e-10000", id="text-underflow"),
        pytest.param(b"1e-10000", id="bytes-underflow"),
        pytest.param(Decimal("1e-10000"), id="decimal-underflow"),
        pytest.param(Fraction(1, 10**400), id="fraction-underflow"),
        pytest.param(float("nan"), id="nan"),
        pytest.param(float("inf"), id="infinity"),
        pytest.param(-1.0, id="negative"),
        pytest.param(10**400, id="integer-overflow"),
        pytest.param(None, id="none"),
    ],
)
def test_sample_rejects_invalid_time_evidence(field: str, value: object) -> None:
    sample = {"wall_seconds": 0.25, "cpu_seconds": 0.125, "peak_bytes": 0, "operations": 1}
    sample[field] = value
    with pytest.raises(ValueError, match=field):
        WorkloadSample(**sample)  # type: ignore[arg-type]


@pytest.mark.parametrize("field", ["wall_seconds", "cpu_seconds"])
@pytest.mark.parametrize(
    "value",
    [
        pytest.param(0.0, id="zero"),
        pytest.param(-0.0, id="signed-zero"),
        pytest.param(float.fromhex("0x0.0000000000001p-1022"), id="smallest-subnormal"),
        pytest.param(sys.float_info.max, id="largest-finite"),
        pytest.param("1.25", id="numeric-text"),
        pytest.param(b"0.125", id="numeric-bytes"),
        pytest.param(Decimal("0.125"), id="decimal"),
        pytest.param(Fraction(1, 8), id="fraction"),
    ],
)
def test_sample_preserves_representable_time_inputs(field: str, value: object) -> None:
    sample = {"wall_seconds": 0.25, "cpu_seconds": 0.125, "peak_bytes": 0, "operations": 1}
    sample[field] = value
    record = WorkloadSample(**sample)  # type: ignore[arg-type]
    measured = getattr(record, field)
    assert measured == float(value)  # type: ignore[arg-type]
    assert math.isfinite(measured)
    if measured == 0:
        assert math.copysign(1, measured) == math.copysign(1, float(value))  # type: ignore[arg-type]


@pytest.mark.parametrize("field", ["peak_bytes", "operations"])
@pytest.mark.parametrize(
    "value",
    [
        pytest.param(True, id="boolean"),
        pytest.param(1.5, id="fractional"),
        pytest.param(float("nan"), id="nan"),
        pytest.param(float("inf"), id="infinity"),
        pytest.param("1", id="text"),
        pytest.param(Decimal(1), id="decimal"),
        pytest.param(Fraction(1, 1), id="fraction"),
    ],
)
def test_sample_rejects_noninteger_counts(field: str, value: object) -> None:
    sample = {"wall_seconds": 0.25, "cpu_seconds": 0.125, "peak_bytes": 0, "operations": 1}
    sample[field] = value
    with pytest.raises(ValueError, match=field):
        WorkloadSample(**sample)  # type: ignore[arg-type]


@pytest.mark.parametrize("field", ["repeats", "warmups", "operations_per_sample"])
@pytest.mark.parametrize(
    "value",
    [
        pytest.param(True, id="boolean"),
        pytest.param(1.5, id="fractional"),
        pytest.param(float("nan"), id="nan"),
        pytest.param(float("inf"), id="infinity"),
        pytest.param("1", id="text"),
    ],
)
def test_single_profile_rejects_invalid_counts_before_effects(field: str, value: object) -> None:
    effects: list[str] = []
    controls = {"repeats": 1, "warmups": 1}
    operations: object = 1
    if field == "operations_per_sample":
        operations = value
    else:
        controls[field] = value  # type: ignore[assignment]
    spec = WorkloadSpec(
        "admission",
        "invalid counts must not execute",
        lambda: effects.append("operation"),
        operations_per_sample=operations,  # type: ignore[arg-type]
        setup=lambda: effects.append("setup"),
    )
    with pytest.raises(ValueError, match=field):
        performance_runner.profile_workload(spec, **controls)
    assert effects == []


@pytest.mark.parametrize(
    "invalid_operations",
    [
        pytest.param(True, id="boolean"),
        pytest.param(1.5, id="fractional"),
        pytest.param(float("nan"), id="nan"),
        pytest.param(float("inf"), id="infinity"),
        pytest.param("1e-10000", id="text-underflow"),
        pytest.param(10**400, id="integer-overflow"),
    ],
)
def test_batch_preflights_later_workload_counts(invalid_operations: object) -> None:
    effects: list[str] = []
    first = WorkloadSpec(
        "first",
        "valid first workload",
        lambda: effects.append("first-operation"),
        setup=lambda: effects.append("first-setup"),
    )
    later = WorkloadSpec(
        "later",
        "invalid later workload",
        lambda: effects.append("later-operation"),
        operations_per_sample=invalid_operations,  # type: ignore[arg-type]
        setup=lambda: effects.append("later-setup"),
    )
    with pytest.raises(ValueError, match="operations_per_sample"):
        performance_runner.profile_workloads((first, later), repeats=1, warmups=0)
    assert effects == []


def test_single_profile_rejects_unrepresentable_integer_before_effects() -> None:
    effects: list[str] = []
    spec = WorkloadSpec(
        "too-large",
        "integer outside floating point throughput range",
        lambda: effects.append("operation"),
        operations_per_sample=10**400,
        setup=lambda: effects.append("setup"),
    )
    with pytest.raises(ValueError, match="operations_per_sample"):
        performance_runner.profile_workload(spec, repeats=1, warmups=0)
    assert effects == []


@pytest.mark.parametrize("batch", [False, True])
@pytest.mark.parametrize("count", [2**53 + 1, 10**100, int(sys.float_info.max)])
def test_large_representable_integer_counts_keep_their_identity(
    monkeypatch: pytest.MonkeyPatch,
    batch: bool,
    count: int,
) -> None:
    sample = WorkloadSample(1.0, 1.0, 0, count)
    monkeypatch.setattr(performance_runner, "_run_sample", lambda spec: sample)
    spec = WorkloadSpec(
        "large-valid", "do not round count metadata", lambda: None, operations_per_sample=count
    )
    if batch:
        profile = performance_runner.profile_workloads((spec,), repeats=1, warmups=0).workloads[0]
    else:
        profile = performance_runner.profile_workload(spec, repeats=1, warmups=0)
    assert profile.operations_per_sample == count
    assert profile.samples[0].operations == count
    assert isinstance(profile.operations_per_sample, int)
    assert profile.median_operations_per_second == count / 1.0


def test_integer_subclasses_and_valid_call_order_are_preserved() -> None:
    class Count(IntEnum):
        TWO = 2

    effects: list[str] = []
    spec = WorkloadSpec(
        "valid-order",
        "legal integer subclass counts",
        lambda: effects.append("operation"),
        operations_per_sample=Count.TWO,
        setup=lambda: effects.append("setup"),
    )
    profile = performance_runner.profile_workload(spec, repeats=Count.TWO, warmups=1)
    assert effects == ["setup", "operation"] * 3
    assert len(profile.samples) == 2
    assert profile.operations_per_sample == 2


@pytest.mark.parametrize("batch", [False, True])
def test_dynamic_throughput_overflow_never_returns_a_profile(
    monkeypatch: pytest.MonkeyPatch,
    batch: bool,
) -> None:
    effects: list[str] = []
    count = int(sys.float_info.max)
    spec = WorkloadSpec(
        "dynamic-overflow",
        "duration-dependent throughput",
        lambda: effects.append("operation"),
        operations_per_sample=count,
    )

    def fixed_sample(workload: WorkloadSpec) -> WorkloadSample:
        workload.operation()
        return WorkloadSample(0.5, 0.25, 0, workload.operations_per_sample)

    monkeypatch.setattr(performance_runner, "_run_sample", fixed_sample)
    with pytest.raises(ValueError, match="median_operations_per_second"):
        if batch:
            performance_runner.profile_workloads((spec,), repeats=1, warmups=0)
        else:
            performance_runner.profile_workload(spec, repeats=1, warmups=0)
    # The duration is only known after execution; this is a post-measurement guard.
    assert effects == ["operation"]


def test_zero_resolution_duration_preserves_existing_fallback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(performance_runner, "_run_sample", lambda spec: WorkloadSample(0, 0, 0, 1))
    spec = WorkloadSpec("zero-clock", "zero is admitted for clock resolution", lambda: None)
    profile = performance_runner.profile_workload(spec, repeats=1, warmups=0)
    assert profile.median_wall_seconds == 0
    assert profile.median_operations_per_second == float(sys.maxsize)
