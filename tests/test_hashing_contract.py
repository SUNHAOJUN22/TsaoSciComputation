from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from tsao_computation.hashing import (
    canonical_json_bytes,
    canonical_json_sha256,
    file_sha256,
    strict_json_loads,
    text_sha256,
)


def test_canonical_json_digest_is_order_invariant_and_compact() -> None:
    left = {"b": [2, 1], "a": {"x": "μ"}}
    right = {"a": {"x": "μ"}, "b": [2, 1]}
    assert canonical_json_bytes(left) == b'{"a":{"x":"\\u03bc"},"b":[2,1]}'
    assert canonical_json_sha256(left) == canonical_json_sha256(right)


def test_canonical_json_digest_rejects_nonfinite_values() -> None:
    with pytest.raises(ValueError):
        canonical_json_sha256({"value": float("nan")})
    with pytest.raises(ValueError):
        canonical_json_sha256({"value": float("inf")})


@pytest.mark.parametrize("token", ["1e-400", "-1e-400"])
def test_strict_json_loader_rejects_nonzero_underflow(token: str) -> None:
    with pytest.raises(ValueError, match="underflows"):
        strict_json_loads('{"value":' + token + "}")


@pytest.mark.parametrize("token", ["0e-400", "-0e-400", "5e-324", "-5e-324"])
def test_strict_json_loader_preserves_zero_and_representable_subnormal(token: str) -> None:
    value = strict_json_loads('{"value":' + token + "}")
    assert isinstance(value, dict)
    assert value["value"] == float(token)


def test_file_digest_streams_exact_bytes_and_validates_buffer(tmp_path: Path) -> None:
    payload = (b"0123456789abcdef" * 100_000) + b"tail"
    path = tmp_path / "payload.bin"
    path.write_bytes(payload)
    assert file_sha256(path, chunk_size=17) == hashlib.sha256(payload).hexdigest()
    with pytest.raises(ValueError, match="chunk_size"):
        file_sha256(path, chunk_size=0)
    with pytest.raises(ValueError, match="chunk_size"):
        file_sha256(path, chunk_size=True)


def test_text_digest_does_not_apply_json_quoting() -> None:
    assert text_sha256("a\n") == hashlib.sha256(b"a\n").hexdigest()
    with pytest.raises(TypeError):
        text_sha256(1)  # type: ignore[arg-type]
