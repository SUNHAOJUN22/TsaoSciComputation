from __future__ import annotations

import json
import multiprocessing
from pathlib import Path

import pytest

from tsao_computation.provenance import append_event, read_events


def _write_events(path: str, worker: int) -> None:
    for index in range(12):
        append_event(Path(path), {"worker": worker, "index": index})


@pytest.mark.parametrize("text", ['{"x":1,"x":2}', '{"x":NaN}', '{"x":Infinity}', '{"x":1e400}', 'null', '[]', '3'])
def test_ambiguous_or_nonobject_records_fail_closed(tmp_path: Path, text: str) -> None:
    path = tmp_path / "events.jsonl"
    path.write_text(text + "\n", encoding="utf-8")
    original = path.read_bytes()
    with pytest.raises(ValueError):
        read_events(path)
    with pytest.raises(ValueError):
        append_event(path, {"kind": "new"})
    assert path.read_bytes() == original


@pytest.mark.parametrize("value", [float("nan"), float("inf"), -float("inf")])
def test_invalid_new_record_does_not_corrupt_prior_evidence(tmp_path: Path, value: float) -> None:
    path = tmp_path / "events.jsonl"
    append_event(path, {"kind": "existing", "title": "中文证据"})
    original = path.read_bytes()
    with pytest.raises(ValueError):
        append_event(path, {"nested": [{"value": value}]})
    assert path.read_bytes() == original
    assert not path.with_name(path.name + ".lock").exists()


def test_multiprocess_append_preserves_all_events(tmp_path: Path) -> None:
    path = tmp_path / "events.jsonl"
    context = multiprocessing.get_context("spawn")
    workers = [context.Process(target=_write_events, args=(str(path), index)) for index in range(4)]
    for worker in workers:
        worker.start()
    try:
        for worker in workers:
            worker.join(timeout=30)
            assert worker.exitcode == 0
    finally:
        for worker in workers:
            if worker.is_alive():
                worker.terminate()
                worker.join(timeout=5)
    events = read_events(path)
    assert len(events) == 48
    assert {(row["worker"], row["index"]) for row in events} == {
        (worker, index) for worker in range(4) for index in range(12)
    }
    assert all(isinstance(row["timestamp"], str) for row in events)
    assert not path.with_name(path.name + ".lock").exists()
    assert all(isinstance(json.loads(line), dict) for line in path.read_text().splitlines())


def test_empty_lines_and_valid_finite_fraction_are_preserved(tmp_path: Path) -> None:
    path = tmp_path / "events.jsonl"
    path.write_text('\n{"nested":{"value":1.25}}\n\n', encoding="utf-8")
    assert read_events(path) == [{"nested": {"value": 1.25}}]


def test_directory_and_symlink_inputs_are_rejected(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    with pytest.raises(ValueError, match="regular file"):
        read_events(tmp_path)
    path = tmp_path / "events.jsonl"
    original = Path.is_symlink
    monkeypatch.setattr(Path, "is_symlink", lambda value: value == path or original(value))
    with pytest.raises(ValueError, match="symbolic link"):
        read_events(path)


def test_size_bounds_apply_to_existing_and_new_records(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from tsao_computation.provenance import ledger

    path = tmp_path / "events.jsonl"
    path.write_text('{"event":"original"}\n', encoding="utf-8")
    original = path.read_bytes()
    monkeypatch.setattr(ledger, "MAX_LEDGER_BYTES", 1)
    with pytest.raises(ValueError, match="bounded regular"):
        read_events(path)
    monkeypatch.setattr(ledger, "MAX_LEDGER_BYTES", len(original) + 1)
    with pytest.raises(ValueError, match="bounded file size"):
        append_event(path, {"event": "new"})
    assert path.read_bytes() == original
    assert not path.with_name(path.name + ".lock").exists()


def test_existing_lock_times_out_without_stealing_it(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from tsao_computation.provenance import ledger

    path = tmp_path / "events.jsonl"
    lock = path.with_name(path.name + ".lock")
    lock.write_text("another writer")
    monkeypatch.setattr(ledger, "LOCK_TIMEOUT_SECONDS", 0.0)
    with pytest.raises(TimeoutError, match="locked"):
        append_event(path, {"event": "new"})
    assert lock.read_text() == "another writer"
    assert not path.exists()


def test_write_failure_releases_lock_and_nonobject_input_is_rejected(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from tsao_computation.provenance import ledger

    path = tmp_path / "events.jsonl"
    with pytest.raises(ValueError, match="JSON object"):
        append_event(path, [])  # type: ignore[arg-type]

    def fail_write(_path: Path, _text: str) -> None:
        raise OSError("simulated disk error")

    monkeypatch.setattr(ledger, "atomic_write_text", fail_write)
    with pytest.raises(OSError, match="disk error"):
        append_event(path, {"event": "new"})
    assert not path.with_name(path.name + ".lock").exists()
    assert not path.exists()
