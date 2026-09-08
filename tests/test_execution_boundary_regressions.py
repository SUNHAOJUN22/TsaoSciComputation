from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from tsao_computation.execution_boundary import (
    ConcurrentProvenanceLedger,
    ExternalExecutionCapability,
    ProvenanceIntegrityError,
    _canonical,
)


@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf")])
def test_nonfinite_payload_never_reaches_ledger(tmp_path: Path, value: float) -> None:
    ledger = ConcurrentProvenanceLedger(tmp_path / "events.jsonl")
    with pytest.raises(ValueError):
        ledger.append("result", {"energy": value})
    assert ledger.read() == ()
    assert not ledger.lock_path.exists()


@pytest.mark.parametrize(
    "body",
    [
        '{"sequence":0,"sequence":1}',
        '{"sequence":0,"payload":{"energy":NaN}}',
        '{"sequence":0,"payload":{"energy":1e999}}',
    ],
)
def test_invalid_json_is_an_integrity_failure(tmp_path: Path, body: str) -> None:
    path = tmp_path / "events.jsonl"
    path.write_text(body + "\n", encoding="utf-8")
    with pytest.raises(ProvenanceIntegrityError):
        ConcurrentProvenanceLedger(path).read()


def test_finite_unicode_hash_encoding_remains_compatible() -> None:
    value = {"name": "材料", "value": 1.25}
    expected = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    assert _canonical(value) == expected.encode()


def test_append_detaches_nested_caller_payload(tmp_path: Path) -> None:
    ledger = ConcurrentProvenanceLedger(tmp_path / "events.jsonl")
    values = [1.0]
    event = ledger.append("result", {"values": values})
    values.append(2.0)
    assert event.payload["values"] == [1.0]
    ledger.verify(ledger.read())


def test_capability_is_expired_at_exact_deadline() -> None:
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    end = start + timedelta(seconds=1)
    capability = ExternalExecutionCapability("id", "executor", "a" * 64, start, end, "test", "test")
    assert not capability.is_verified(verifier=lambda *args: True, command_digest="a" * 64, now=end)
