from __future__ import annotations

import hashlib
import io
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

from tsao_computation.execution_boundary import ConcurrentProvenanceLedger
from tsao_computation.hashing import file_sha256


@pytest.mark.parametrize("requested", [2 * 1024 * 1024, 10**100])
def test_hash_read_buffer_is_bounded(requested: int) -> None:
    data = b"artifact" * 200_000

    class ReadSpy(io.BytesIO):
        def read(self, size: int = -1) -> bytes:
            assert 0 < size <= 1024 * 1024
            return super().read(size)

    stream = ReadSpy(data)
    with patch.object(Path, "open", return_value=stream):
        assert file_sha256("artifact.out", chunk_size=requested) == hashlib.sha256(data).hexdigest()
    assert stream.closed


@pytest.mark.parametrize("chunk_size", [1, 17, 1024 * 1024, 10**100])
def test_hash_digest_does_not_depend_on_requested_buffer(tmp_path: Path, chunk_size: int) -> None:
    path = tmp_path / "artifact.out"
    path.write_bytes(b"abc")
    assert file_sha256(path, chunk_size=chunk_size) == hashlib.sha256(b"abc").hexdigest()


@pytest.mark.parametrize(
    "timeout",
    [-1.0, float("nan"), float("inf"), float("-inf"), True, "1", None, 10**1000],
)
def test_invalid_lock_timeout_rejected_before_filesystem_change(
    tmp_path: Path, timeout: Any
) -> None:
    path = tmp_path / "not-created" / "ledger.jsonl"
    with pytest.raises(ValueError, match="lock_timeout"):
        ConcurrentProvenanceLedger(path, lock_timeout=timeout)
    assert not path.parent.exists()


@pytest.mark.parametrize("timeout", [0.0, 0.01, 1, 10.0])
def test_valid_lock_timeout_preserves_append_and_verification(
    tmp_path: Path, timeout: float
) -> None:
    ledger = ConcurrentProvenanceLedger(tmp_path / "ledger.jsonl", lock_timeout=timeout)
    ledger.append("result", {"value": 1.0})
    events = ledger.read()
    ledger.verify(events)
    assert len(events) == 1
    assert not ledger.lock_path.exists()
