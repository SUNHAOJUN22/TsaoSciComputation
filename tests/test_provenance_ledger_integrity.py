from __future__ import annotations

import errno
import json
import multiprocessing
import os
from collections.abc import Callable
from pathlib import Path
from types import SimpleNamespace

import pytest

from tsao_computation.provenance import append_event, ledger, read_events


def _write_events(path: str, worker: int) -> None:
    for index in range(12):
        append_event(Path(path), {"worker": worker, "index": index})


@pytest.mark.parametrize(
    "text",
    [
        '{"x":1,"x":2}',
        '{"x":NaN}',
        '{"x":Infinity}',
        '{"x":1e400}',
        '{"x":1e-400}',
        "null",
        "[]",
        "3",
    ],
)
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


def test_directory_and_symlink_inputs_are_rejected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    with pytest.raises(ValueError, match="regular file"):
        read_events(tmp_path)
    path = tmp_path / "events.jsonl"
    original = Path.is_symlink
    monkeypatch.setattr(Path, "is_symlink", lambda value: value == path or original(value))
    with pytest.raises(ValueError, match="symbolic link"):
        read_events(path)


def test_size_bounds_apply_to_existing_and_new_records(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
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


def test_existing_lock_times_out_without_stealing_it(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from tsao_computation.provenance import ledger

    path = tmp_path / "events.jsonl"
    lock = path.with_name(path.name + ".lock")
    lock.write_text("another writer")
    monkeypatch.setattr(ledger, "LOCK_TIMEOUT_SECONDS", 0.0)
    with pytest.raises(TimeoutError, match="locked"):
        append_event(path, {"event": "new"})
    assert lock.read_text() == "another writer"
    assert not path.exists()


def test_write_failure_releases_lock_and_nonobject_input_is_rejected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
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


def _install_lock_open(
    monkeypatch: pytest.MonkeyPatch, platform: str, opener: Callable[..., int]
) -> None:
    # Replace only the ledger's OS boundary; pathlib and atomic replacement remain real.
    monkeypatch.setattr(
        ledger,
        "os",
        SimpleNamespace(
            name=platform,
            open=opener,
            close=os.close,
            O_CREAT=os.O_CREAT,
            O_EXCL=os.O_EXCL,
            O_WRONLY=os.O_WRONLY,
        ),
    )


def test_windows_access_conflict_waits_for_real_exclusive_lock(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "events.jsonl"
    append_event(path, {"event": "prior"})
    original = path.read_bytes()
    lock = path.with_name(path.name + ".lock")
    lock.write_text("another writer", encoding="utf-8")
    attempts: list[tuple[Path, int, int]] = []
    clock = [0.0]
    waits: list[float] = []

    def lock_open(candidate: Path, flags: int, mode: int) -> int:
        attempts.append((candidate, flags, mode))
        if len(attempts) == 1:
            # The CRT error in the Windows CI trace has errno, but no winerror.
            raise PermissionError(errno.EACCES, "delete-pending sharing conflict", str(lock))
        return os.open(candidate, flags, mode)

    def wait(delay: float) -> None:
        waits.append(delay)
        clock[0] += delay
        assert path.read_bytes() == original
        assert lock.read_text(encoding="utf-8") == "another writer"
        if len(waits) == 2:
            # Simulate the other owner releasing its lock, not the contender stealing it.
            lock.unlink()

    _install_lock_open(monkeypatch, "nt", lock_open)
    monkeypatch.setattr(ledger, "time", SimpleNamespace(monotonic=lambda: clock[0], sleep=wait))
    append_event(path, {"event": "new"})
    assert attempts == [(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)] * 3
    assert waits == [0.01, 0.01]
    assert [record["event"] for record in read_events(path)] == ["prior", "new"]
    assert not lock.exists()


def test_windows_persistent_access_denial_keeps_original_error_and_lock(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "events.jsonl"
    append_event(path, {"event": "prior"})
    original = path.read_bytes()
    lock = path.with_name(path.name + ".lock")
    lock.write_text("another writer", encoding="utf-8")
    denied = PermissionError(errno.EACCES, "permission remains denied", str(lock))
    clock = [0.0]
    attempts = [0]
    waits: list[float] = []

    def lock_open(_candidate: Path, _flags: int, _mode: int) -> int:
        attempts[0] += 1
        raise denied

    def wait(delay: float) -> None:
        waits.append(delay)
        clock[0] += delay

    _install_lock_open(monkeypatch, "nt", lock_open)
    monkeypatch.setattr(ledger, "time", SimpleNamespace(monotonic=lambda: clock[0], sleep=wait))
    monkeypatch.setattr(ledger, "LOCK_TIMEOUT_SECONDS", 0.02)
    with pytest.raises(PermissionError) as captured:
        append_event(path, {"event": "new"})
    assert captured.value is denied
    assert attempts == [3] and waits == [0.01, 0.01]
    assert path.read_bytes() == original
    assert lock.read_text(encoding="utf-8") == "another writer"


def test_windows_access_retry_shares_existing_lock_deadline(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "events.jsonl"
    lock = path.with_name(path.name + ".lock")
    lock.write_text("another writer", encoding="utf-8")
    denied = PermissionError(errno.EACCES, "still denied at deadline", str(lock))
    clock = [0.0]
    attempts = [0]
    waits: list[float] = []

    def lock_open(candidate: Path, flags: int, mode: int) -> int:
        attempts[0] += 1
        if attempts[0] == 1:
            return os.open(candidate, flags, mode)
        raise denied

    def wait(delay: float) -> None:
        waits.append(delay)
        clock[0] += delay

    _install_lock_open(monkeypatch, "nt", lock_open)
    monkeypatch.setattr(ledger, "time", SimpleNamespace(monotonic=lambda: clock[0], sleep=wait))
    monkeypatch.setattr(ledger, "LOCK_TIMEOUT_SECONDS", 0.01)
    with pytest.raises(PermissionError) as captured:
        append_event(path, {"event": "new"})
    assert captured.value is denied
    assert attempts == [2] and waits == [0.01]
    assert not path.exists()
    assert lock.read_text(encoding="utf-8") == "another writer"


@pytest.mark.parametrize("platform,error_number", [("posix", errno.EACCES), ("nt", errno.EPERM)])
def test_unrelated_permission_errors_are_not_retried(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, platform: str, error_number: int
) -> None:
    path = tmp_path / "events.jsonl"
    lock = path.with_name(path.name + ".lock")
    lock.write_text("another writer", encoding="utf-8")
    denied = PermissionError(error_number, "genuine permission error", str(lock))
    attempts = [0]

    def lock_open(_candidate: Path, _flags: int, _mode: int) -> int:
        attempts[0] += 1
        raise denied

    def unexpected_wait(_delay: float) -> None:
        raise AssertionError("unrelated permission errors must propagate immediately")

    _install_lock_open(monkeypatch, platform, lock_open)
    monkeypatch.setattr(
        ledger, "time", SimpleNamespace(monotonic=lambda: 0.0, sleep=unexpected_wait)
    )
    with pytest.raises(PermissionError) as captured:
        append_event(path, {"event": "new"})
    assert captured.value is denied and attempts == [1]
    assert not path.exists()
    assert lock.read_text(encoding="utf-8") == "another writer"
