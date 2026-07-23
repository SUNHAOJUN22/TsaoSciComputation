from __future__ import annotations

import hashlib
from collections.abc import Sequence
from pathlib import Path

from scripts import verify_all


def test_all_profile_contains_only_deterministic_release_gates() -> None:
    assert verify_all.RELEASE_PROFILE_NAMES == ("quality", "core", "package")
    assert [step.__name__ for step in verify_all.selected_verifications("all")] == [
        "verify_quality",
        "verify_core",
        "verify_package",
    ]
    assert [step.__name__ for step in verify_all.selected_verifications("benchmark")] == [
        "verify_benchmark"
    ]


def test_run_commands_stops_after_first_failure(monkeypatch) -> None:
    labels: list[str] = []

    def fake_run(
        label: str,
        command: Sequence[str],
        *,
        env: dict[str, str] | None = None,
    ) -> int:
        del command, env
        labels.append(label)
        return 7 if label == "second" else 0

    monkeypatch.setattr(verify_all, "run", fake_run)

    result = verify_all.run_commands(
        (
            ("first", ("one",)),
            ("second", ("two",)),
            ("third", ("three",)),
        )
    )

    assert result == 7
    assert labels == ["first", "second"]


def test_sha256_reads_complete_file(tmp_path: Path) -> None:
    payload = (b"TsaoSciComputation\n" * 100_000) + b"final"
    path = tmp_path / "artifact.bin"
    path.write_bytes(payload)

    assert verify_all.sha256(path) == hashlib.sha256(payload).hexdigest()
