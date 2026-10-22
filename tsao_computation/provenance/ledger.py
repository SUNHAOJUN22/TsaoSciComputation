from __future__ import annotations

import errno
import json
import math
import os
import time
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, NoReturn

from ..security.paths import atomic_write_text

MAX_LEDGER_BYTES = 64 * 1024 * 1024
LOCK_TIMEOUT_SECONDS = 10.0


def _reject_constant(value: str) -> NoReturn:
    raise ValueError(f"non-finite event number is forbidden: {value}")


def _finite_float(value: str) -> float:
    number = float(value)
    if not math.isfinite(number):
        raise ValueError("event number exceeds the finite floating-point range")
    return number


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate event key is forbidden: {key!r}")
        result[key] = value
    return result


def read_events(path: Path) -> list[dict[str, Any]]:
    if path.is_symlink():
        raise ValueError("event ledger must not be a symbolic link")
    if not path.exists():
        return []
    if not path.is_file() or path.stat().st_size > MAX_LEDGER_BYTES:
        raise ValueError("event ledger must be a bounded regular file")
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8", errors="strict") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                value = json.loads(
                    line,
                    parse_constant=_reject_constant,
                    parse_float=_finite_float,
                    object_pairs_hook=_unique_object,
                )
                if not isinstance(value, dict):
                    raise ValueError("event must be a JSON object")
            except ValueError as error:
                raise ValueError(f"{path.name}:{line_number}: {error}") from error
            records.append(value)
    return records


@contextmanager
def _writer_lock(path: Path) -> Iterator[None]:
    """Serialize cooperating writers; never steal an abandoned lock silently."""
    path.parent.mkdir(parents=True, exist_ok=True)
    lock = path.with_name(path.name + ".lock")
    deadline = time.monotonic() + LOCK_TIMEOUT_SECONDS
    while True:
        try:
            descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            break
        except FileExistsError:
            if time.monotonic() >= deadline:
                raise TimeoutError(f"event ledger is locked: {path.name}") from None
            time.sleep(0.01)
        except PermissionError as error:
            # Windows CRT maps sharing/delete-pending conflicts to EACCES too.
            # Retry only acquisition, within the same deadline; persistent access
            # denial remains PermissionError and never authorizes or removes a lock.
            if os.name != "nt" or error.errno != errno.EACCES or time.monotonic() >= deadline:
                raise
            time.sleep(0.01)
    try:
        yield
    finally:
        os.close(descriptor)
        lock.unlink()


def append_event(path: Path, event: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(event, dict):
        raise ValueError("event must be a JSON object")
    record = dict(event)
    record.setdefault("timestamp", datetime.now(timezone.utc).isoformat())
    # Reject an invalid new record before acquiring the lock or changing the file.
    json.dumps(record, ensure_ascii=False, sort_keys=True, allow_nan=False)
    with _writer_lock(path):
        records = read_events(path)
        records.append(record)
        text = "".join(
            json.dumps(item, ensure_ascii=False, sort_keys=True, allow_nan=False) + "\n"
            for item in records
        )
        if len(text.encode("utf-8")) > MAX_LEDGER_BYTES:
            raise ValueError("event ledger exceeds the bounded file size")
        atomic_write_text(path, text)
    return record
