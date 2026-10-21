from __future__ import annotations

import json
import sys
from copy import deepcopy
from dataclasses import FrozenInstanceError, replace
from decimal import Decimal
from hashlib import sha256
from pathlib import Path

import pytest
from approval_fixtures import TEST_KEYS, verified_record

from tsao_computation.adapters.base import Adapter, AdapterProbe
from tsao_computation.contracts import HandoffRecord
from tsao_computation.errors import ContractError, StateTransitionError
from tsao_computation.scientific_quantity import ScientificQuantity
from tsao_computation.state.machine import ScientificStateMachine
from tsao_computation.validation.confidence import assess_confidence

PRESSURE = (-1, 1, -2, 0, 0, 0, 0)
TEMPERATURE = (0, 0, 0, 1, 0, 0, 0)


def handoff(**changes: object) -> HandoffRecord:
    payload = dict(
        source_model="MD",
        target_model="CFD",
        quantity="viscosity",
        value=1250.0,
        unit="Pa*s",
        conditions={"temperature_K": 453.15, "composition": {"fractions": [0.2, 0.8]}},
        reference_state="453.15 K",
        statistical_uncertainty={"value": 75.0, "unit": "Pa*s", "method": "block means"},
        model_uncertainty=150.0,
        applicability="synthetic range",
        transformation="identity",
        validation_status="checked",
    )
    payload.update(changes)
    return HandoffRecord(**payload)


def test_public_confidence_rejects_caller_strings_and_embedded_keys() -> None:
    record = verified_record(governance=True)
    record["approvals"] = ["Dr. Reviewer approved"]
    record["trusted_approval_keys"] = TEST_KEYS
    result = assess_confidence(record)
    assert result.level == "C3" and not result.engineering_decision_ready
    assert assess_confidence(verified_record(governance=True)).level == "C3"


def test_c5_has_distinct_scope_signatures_and_cannot_relabel_a_decision() -> None:
    good = verified_record(governance=True)
    assert assess_confidence(good, trusted_approval_keys=TEST_KEYS).level == "C5"
    for mutation in ("decision_scope", "signature", "artifact", "duplicate_nonce"):
        bad = deepcopy(good)
        if mutation == "decision_scope":
            bad["decision_scope"] = "unreviewed decision"
        elif mutation == "signature":
            bad["approvals"][2]["signature"] = "0" * 64
        elif mutation == "artifact":
            bad["artifact_sha256"] = "b" * 64
        else:
            bad["approvals"][2]["nonce"] = bad["approvals"][1]["nonce"]
        result = assess_confidence(bad, trusted_approval_keys=TEST_KEYS)
        assert result.level in {"C3", "C4"} and not result.engineering_decision_ready


@pytest.mark.parametrize("initial", ["scientifically-accepted", "accepted"])
def test_initial_state_cannot_fabricate_acceptance(initial: str) -> None:
    with pytest.raises(StateTransitionError, match="verified transition"):
        ScientificStateMachine(initial)


def test_state_acceptance_binds_actual_transition_and_does_not_mutate_on_failure() -> None:
    machine = ScientificStateMachine("physically-validated")
    for kwargs in (
        {},
        {"acceptance_record": verified_record()},
        {
            "acceptance_record": verified_record(),
            "trusted_approval_keys": {"synthetic-local-review": b"wrong"},
        },
    ):
        with pytest.raises(StateTransitionError):
            machine.transition("accepted", evidence="a" * 64, **kwargs)
        assert machine.state == "physically-validated" and machine.events == ()
    with pytest.raises(StateTransitionError, match="match"):
        machine.transition(
            "accepted",
            evidence="different artifact",
            acceptance_record=verified_record(),
            trusted_approval_keys=TEST_KEYS,
        )
    event = machine.transition(
        "accepted",
        evidence="a" * 64,
        acceptance_record=verified_record(),
        trusted_approval_keys=TEST_KEYS,
    )
    assert event["acceptance"]["accepted"] and machine.state == "scientifically-accepted"
    with pytest.raises(TypeError):
        event["acceptance"]["accepted"] = False
    with pytest.raises(FrozenInstanceError):
        machine.state = "proposed"


@pytest.mark.parametrize(
    "changes",
    [
        {"value": float("nan")},
        {"value": float("inf")},
        {"value": True},
        {"value": "1250"},
        {"value": {"mean": 2}},
        {"value": []},
        {"value": [[1], [2, 3]]},
        {"value": 10**400},
        {"unit": "banana"},
        {"conditions": {"x": float("nan")}},
        {"conditions": {1: 3}},
        {"conditions": {"x": object()}},
        {"statistical_uncertainty": -1},
        {"model_uncertainty": float("inf")},
        {"model_uncertainty": {"value": 1}},
        {"model_uncertainty": {"value": 1, "unit": "K"}},
        {"model_uncertainty": {"value": -1, "unit": "Pa*s"}},
        {"model_uncertainty": [1, 2]},
        {"validation_status": "validated"},
        {"validation_status": []},
        {"validation_evidence": ["approved"]},
        {"source_model": None},
    ],
)
def test_handoff_public_constructor_fails_closed(changes: dict[str, object]) -> None:
    with pytest.raises(ContractError):
        handoff(**changes)


def test_handoff_freezes_aliases_roundtrips_and_binds_signed_payload() -> None:
    conditions = {"x": {"y": [1, 2]}}
    original = handoff(conditions=conditions)
    digest = original.digest
    conditions["x"]["y"][0] = 999
    assert original.conditions["x"]["y"] == [1, 2]
    assert original.digest == digest
    with pytest.raises(TypeError):
        original.conditions["x"]["y"].append(3)
    assert HandoffRecord.from_mapping(json.loads(json.dumps(original.to_dict()))).digest == digest
    verified = replace(
        original,
        validation_status="validated",
        validation_evidence=verified_record(digest),
        trusted_approval_keys=TEST_KEYS,
    )
    assert verified.validation_status == "validated"
    assert (
        HandoffRecord.from_mapping(verified.to_dict(), trusted_approval_keys=TEST_KEYS).digest
        == digest
    )
    with pytest.raises(ContractError):
        HandoffRecord.from_mapping(
            {**verified.to_dict(), "value": 9}, trusted_approval_keys=TEST_KEYS
        )
    with pytest.raises(ContractError):
        HandoffRecord.from_mapping(verified.to_dict())
    with pytest.raises(ContractError):
        HandoffRecord.from_mapping({"value": 1})
    with pytest.raises(ContractError):
        HandoffRecord.from_mapping({**original.to_dict(), "trusted_approval_keys": {}})


def test_handoff_tensor_shapes_and_unitful_uncertainty() -> None:
    record = handoff(
        value=[[1, 2], [3, 4]],
        statistical_uncertainty={"value": [[0.1, 0.2], [0.2, 0.1]], "unit": "mPa*s"},
    )
    assert record.value[1][1] == 4
    with pytest.raises(TypeError):
        record.value[1][1] = 99


@pytest.mark.parametrize(
    "changes",
    [
        {"unit": "K"},
        {"unit": "bogus"},
        {"unit": None},
        {"source_id": None},
        {"dimension": [True, 1, -2, 0, 0, 0, 0]},
        {"basis": None},
        {"value": float("nan")},
        {"value": "1e999"},
        {"uncertainty": -1},
        {"source_quantity_digest": "fake"},
    ],
)
def test_quantity_mapping_binds_units_dimensions_and_finite_metadata(
    changes: dict[str, object],
) -> None:
    payload = {"value": "1.25", "unit": "MPa", "dimension": PRESSURE, "source_id": "measured:1"}
    payload.update(changes)
    with pytest.raises((ValueError, TypeError)):
        ScientificQuantity.from_mapping(payload)


def test_quantity_registry_drives_conversion_and_keeps_parent_digest() -> None:
    original = ScientificQuantity(
        Decimal("1.25"), "MPa", PRESSURE, "measured:1", uncertainty=Decimal("0.05")
    )
    result = original.convert(unit="Pa", dimension=PRESSURE)
    assert result.value == Decimal("1250000") and result.uncertainty == 50000
    assert result.source_quantity_digest == original.digest
    assert ScientificQuantity.from_mapping(result.canonical_payload()).digest == result.digest
    for options in ({"unit": "K", "factor": 1}, {"unit": "Pa", "factor": 7}):
        with pytest.raises(ValueError):
            original.convert(dimension=PRESSURE, **options)


def test_quantity_affine_temperature_and_interval_are_distinct() -> None:
    original = ScientificQuantity(
        Decimal("32"), "degF", TEMPERATURE, "thermometer", uncertainty=Decimal("1.8")
    )
    result = original.convert(unit="K", dimension=TEMPERATURE)
    assert result.value == Decimal("273.15") and result.uncertainty == Decimal("1")
    assert result.convert(unit="degC", dimension=TEMPERATURE).value == Decimal("0")
    with pytest.raises(ValueError, match="temperature kinds"):
        original.convert(unit="delta_K", dimension=TEMPERATURE)
    with pytest.raises(ValueError, match="zero kelvin"):
        ScientificQuantity(Decimal("-273.15"), "degC", TEMPERATURE, "impossible")
    assert (
        ScientificQuantity(Decimal("-5"), "delta_K", TEMPERATURE, "temperature change").value == -5
    )


@pytest.mark.parametrize(
    "output,completed,converged",
    [
        ("Normal termination; SCF not yet converged", True, False),
        ("not normal termination; converged", False, False),
        ("Normal termination; converged=false", True, False),
        ("Normal termination; never converged", True, False),
        ("Normal termination; not necessarily converged", True, False),
        ("Normal termination; convergence has not been achieved", True, False),
        ("completed=false; converged", False, False),
        ("completed; converged=no", True, False),
        ("completed; converged=0", True, False),
        ("SCF CONVERGED AFTER 12 CYCLES\nORCA TERMINATED NORMALLY", True, True),
        (
            "Program PWSCF v.7.4\nconvergence has been achieved in 6 iterations\nJOB DONE.",
            True,
            True,
        ),
        ("JOB START\nnormal termination; converged\nJOB START\nSCF iteration 1", False, False),
        ("finished mdrun", True, False),
        ("the previous calculation converged yesterday", False, False),
    ],
)
def test_public_parser_handles_negation_and_run_boundaries(
    output: str, completed: bool, converged: bool
) -> None:
    result = Adapter({"slug": "orca"}).parse(output)
    assert result["completed"] is completed and result["converged"] is converged
    assert result["source_sha256"] == sha256(output.encode()).hexdigest()
    assert result["parser_version"] == "tsao-conservative-status/2" and not result["validated"]


@pytest.mark.parametrize(
    "slug,filename,tail",
    [
        ("gromacs", "system.tpr", ("mdrun", "-s", "system.tpr")),
        ("quantum-espresso", "scf.in", ("-i", "scf.in")),
        ("orca", "water.inp", ("water.inp",)),
    ],
)
def test_real_command_plan_engine_protocol(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, slug: str, filename: str, tail: tuple[str, ...]
) -> None:
    source = tmp_path / filename
    source.write_text("synthetic input", encoding="utf-8")
    monkeypatch.setattr(
        Adapter,
        "probe",
        lambda self: AdapterProbe(self.slug, True, f"/mock/{self.slug}", "synthetic probe"),
    )
    plan = Adapter({"slug": slug}).build_command(source)
    assert plan.argv[1:] == tail and not plan.execute_allowed
    assert plan.input_sha256 == sha256(source.read_bytes()).hexdigest()
    assert plan.cwd == tmp_path.resolve()


def test_unsupported_command_protocol_and_wrong_input_are_not_runnable(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = tmp_path / "system.in"
    source.write_text("fixture", encoding="utf-8")
    monkeypatch.setattr(
        Adapter,
        "probe",
        lambda self: AdapterProbe(self.slug, True, sys.executable, "synthetic probe"),
    )
    for record in (
        {"slug": "gromacs"},
        {"slug": "vasp"},
        {"slug": "openmm", "python_modules": ["openmm"]},
    ):
        with pytest.raises(ContractError):
            Adapter(record).build_command(source)
    with pytest.raises(TypeError):
        Adapter({"slug": "generic"}).parse(None)


@pytest.mark.parametrize("unit,zero", [("K", 0), ("degC", -273.15), ("degF", -459.67)])
def test_handoff_absolute_zero_rejected_without_binary_float_roundoff(
    unit: str, zero: float
) -> None:
    with pytest.raises(ContractError, match="zero kelvin"):
        handoff(value=zero, unit=unit, statistical_uncertainty=0, model_uncertainty=0)
    assert (
        handoff(value=[zero + 1], unit=unit, statistical_uncertainty=0, model_uncertainty=0).value[
            0
        ]
        > zero
    )


def test_parser_source_offset_is_not_changed_by_unicode_casefold_expansion() -> None:
    output = "ß old output\nProgram PWSCF v.7.4\nconvergence has been achieved in 6 iterations\nJOB DONE."
    result = Adapter({"slug": "quantum-espresso"}).parse(output)
    assert result["active_run_offset"] == len("ß old output")
    assert result["engine_version"] == "7.4" and result["converged"]


@pytest.mark.parametrize(
    "changes", [{"unit_registry_version": "unknown-v99"}, {"dimension_order": ["wrong"]}]
)
def test_quantity_deserialization_rejects_conflicting_registry_metadata(
    changes: dict[str, object],
) -> None:
    record = ScientificQuantity(Decimal("1"), "MPa", PRESSURE, "instrument:1").canonical_payload()
    record.update(changes)
    with pytest.raises(ValueError, match="unsupported"):
        ScientificQuantity.from_mapping(record)
