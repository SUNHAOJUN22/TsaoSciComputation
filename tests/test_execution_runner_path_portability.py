from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from tsao_computation.errors import SecurityError
from tsao_computation.execution import authorize_plan, runner


def _literal_executable(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"portable executable fixture\n")
    path.chmod(path.stat().st_mode | 0o111)
    return path.resolve()


def test_explicit_relative_prefix_is_separator_independent() -> None:
    assert runner._has_explicit_relative_prefix("./solver") is True
    assert runner._has_explicit_relative_prefix(".\\solver") is True
    assert runner._has_explicit_relative_prefix("../solver") is True
    assert runner._has_explicit_relative_prefix("..\\solver") is True
    assert runner._has_explicit_relative_prefix("solver") is False
    assert runner._has_explicit_relative_prefix("nested/solver") is False


def test_adapter_plan_relative_executable_binds_cwd_before_path(tmp_path: Path) -> None:
    work = tmp_path / "work"
    executable = _literal_executable(work / "solver")
    shadow = _literal_executable(tmp_path / "path-bin" / "solver")
    shadow.write_bytes(b"different PATH executable\n")
    # Third-party CommandPlanLike adapters need not use CommandPlan's eager
    # normalization. Validate their raw relative paths through the public API.
    plan = SimpleNamespace(
        argv=(f".{os.sep}solver",),
        cwd=work,
        environment={"PATH": str(shadow.parent)},
    )

    authorization = authorize_plan(
        plan,
        authorized_by="pytest",
        purpose="bind an adapter's explicit relative executable",
        explicit_authorization=True,
    )

    assert authorization.executable_sha256 == hashlib.sha256(executable.read_bytes()).hexdigest()
    assert authorization.executable_sha256 != hashlib.sha256(shadow.read_bytes()).hexdigest()


def test_adapter_plan_rejects_file_as_working_directory(tmp_path: Path) -> None:
    cwd = tmp_path / "not-a-directory"
    cwd.write_bytes(b"preserved input")
    plan = SimpleNamespace(argv=(sys.executable, "--version"), cwd=cwd, environment={})

    with pytest.raises(SecurityError, match="working directory is unavailable"):
        authorize_plan(
            plan,
            authorized_by="pytest",
            purpose="reject an unusable adapter working directory",
            explicit_authorization=True,
        )
    assert cwd.read_bytes() == b"preserved input"


@pytest.mark.parametrize(
    ("kind", "message"),
    (("missing", "executable is unavailable"), ("directory", "executable is not runnable")),
)
def test_adapter_plan_rejects_unusable_executable_targets(
    tmp_path: Path, kind: str, message: str
) -> None:
    target = tmp_path / "solver"
    if kind == "directory":
        target.mkdir()
    plan = SimpleNamespace(argv=(str(target),), cwd=tmp_path, environment={})

    with pytest.raises(SecurityError, match=message):
        authorize_plan(
            plan,
            authorized_by="pytest",
            purpose="reject an unavailable adapter executable before granting execution",
            explicit_authorization=True,
        )


def test_exact_path_entry_search_is_bounded_to_declared_path(tmp_path: Path) -> None:
    left = tmp_path / "left"
    right = tmp_path / "right"
    executable = _literal_executable(right / "solver")

    assert runner._search_exact_path_entry("solver", "") is None
    assert runner._search_exact_path_entry("missing", str(right)) is None
    assert runner._search_exact_path_entry(
        "solver",
        os.pathsep.join((str(left), f'"{right}"')),
    ) == str(executable)


def test_exact_path_search_skips_blank_declared_entries(tmp_path: Path) -> None:
    path_bin = tmp_path / "path-bin"
    executable = _literal_executable(path_bin / "solver")
    search_path = os.pathsep.join(("", "   ", '""', str(path_bin)))

    assert runner._search_exact_path_entry("solver", search_path) == str(executable)


def test_resolver_uses_literal_immutable_path_fallback(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    path_bin = tmp_path / "path-bin"
    executable = _literal_executable(path_bin / "solver")
    work = tmp_path / "work"
    work.mkdir()
    monkeypatch.setattr(runner.shutil, "which", lambda *_args, **_kwargs: None)

    resolved = runner._resolve_executable("solver", work, search_path=str(path_bin))

    assert resolved == executable


def test_literal_path_fallback_tolerates_unreadable_entries(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    path_bin = tmp_path / "path-bin"
    executable = _literal_executable(path_bin / "solver")
    original_is_file = Path.is_file

    def guarded_is_file(path: Path) -> bool:
        if path.parent.name == "broken":
            raise OSError("fixture path failure")
        return original_is_file(path)

    monkeypatch.setattr(Path, "is_file", guarded_is_file)
    search_path = os.pathsep.join((str(tmp_path / "broken"), str(path_bin)))

    assert runner._search_exact_path_entry("solver", search_path) == str(executable)
