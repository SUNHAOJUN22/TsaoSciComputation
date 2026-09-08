"""Canonical SHA-256 helpers shared by evidence, execution, and performance code.

All structured payloads use one JSON canonicalization rule so digests cannot drift
between subsystems. File hashing is streamed to avoid loading large solver outputs
into memory.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

_DEFAULT_CHUNK_SIZE = 1024 * 1024


def canonical_json_bytes(value: object, *, ensure_ascii: bool = True) -> bytes:
    """Return deterministic UTF-8 JSON bytes and reject non-finite numbers."""

    encoded = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=ensure_ascii,
        allow_nan=False,
    )
    return encoded.encode("utf-8")


def canonical_json_sha256(value: object, *, ensure_ascii: bool = True) -> str:
    """Hash a structured value using the repository-wide canonical JSON contract."""

    return hashlib.sha256(canonical_json_bytes(value, ensure_ascii=ensure_ascii)).hexdigest()


def file_sha256(path: str | Path, *, chunk_size: int = _DEFAULT_CHUNK_SIZE) -> str:
    """Stream a file into SHA-256 with a bounded, validated read buffer."""

    if isinstance(chunk_size, bool) or not isinstance(chunk_size, int) or chunk_size < 1:
        raise ValueError("chunk_size must be a positive integer")
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def text_sha256(value: str) -> str:
    """Hash UTF-8 text without applying JSON quoting or normalization."""

    if not isinstance(value, str):
        raise TypeError("value must be a string")
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def strict_json_loads(value: str | bytes) -> object:
    """Read exchange JSON without duplicate keys or non-finite numeric values."""

    def reject_constant(token: str) -> object:
        raise ValueError(f"non-finite JSON constant: {token}")

    def finite_float(token: str) -> float:
        number = float(token)
        if not math.isfinite(number):
            raise ValueError("JSON number exceeds the finite float range")
        return number

    def unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, item in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON key: {key}")
            result[key] = item
        return result

    return json.loads(
        value,
        parse_constant=reject_constant,
        parse_float=finite_float,
        object_pairs_hook=unique_object,
    )
