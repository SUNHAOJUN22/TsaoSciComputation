from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
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


@pytest.mark.parametrize("ending", [b"", b" ", b"\r", b"\r\n", b"\n"])
def test_append_preserves_valid_chain_without_a_final_newline(
    tmp_path: Path, ending: bytes
) -> None:
    ledger = ConcurrentProvenanceLedger(tmp_path / "events.jsonl")
    first = ledger.append("first", {"name": "材料", "value": 1})
    original = ledger.path.read_bytes().rstrip(b"\n") + ending
    ledger.path.write_bytes(original)
    ledger.verify(ledger.read())
    second = ledger.append("second", {"value": 2})
    assert ledger.path.read_bytes().startswith(original)
    assert ledger.read() == (first, second)
    ledger.verify(ledger.read())
    assert second.previous_hash == first.event_hash
    assert not ledger.lock_path.exists()


def test_concurrent_append_repairs_only_record_separator_and_keeps_every_event(
    tmp_path: Path,
) -> None:
    path = tmp_path / "events.jsonl"
    initial = ConcurrentProvenanceLedger(path)
    first = initial.append("first", {"value": -1})
    original = path.read_bytes().rstrip(b"\n")
    path.write_bytes(original)

    def append(index: int) -> None:
        ConcurrentProvenanceLedger(path).append("next", {"value": index})

    with ThreadPoolExecutor(max_workers=4) as pool:
        tuple(pool.map(append, range(8)))
    events = initial.read()
    initial.verify(events)
    assert path.read_bytes().startswith(original)
    assert events[0] == first
    assert len(events) == 9
    assert {event.payload["value"] for event in events[1:]} == set(range(8))


def test_incomplete_record_is_not_repaired_or_overwritten(tmp_path: Path) -> None:
    ledger = ConcurrentProvenanceLedger(tmp_path / "events.jsonl")
    ledger.append("first", {"value": 1})
    original = ledger.path.read_bytes() + b'{"sequence":1'
    ledger.path.write_bytes(original)
    with pytest.raises(ProvenanceIntegrityError):
        ledger.append("second", {"value": 2})
    assert ledger.path.read_bytes() == original
    assert not ledger.lock_path.exists()
