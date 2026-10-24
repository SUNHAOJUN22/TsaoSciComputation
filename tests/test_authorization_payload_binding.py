from __future__ import annotations

import copy
import sys
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

import pytest

from tsao_computation.adapters.base import CommandPlan
from tsao_computation.errors import SecurityError
from tsao_computation.execution import authorize_plan, plan_sha256, run_plan


def _grant(tmp_path: Path):
    plan = CommandPlan((sys.executable, "-c", "print('approved')"), tmp_path, {}, "approved")
    return plan, authorize_plan(
        plan,
        authorized_by="pytest",
        purpose="reviewed fixture only",
        explicit_authorization=True,
    )


def test_copied_seal_cannot_authorize_a_substituted_command(tmp_path: Path) -> None:
    _, authorization = _grant(tmp_path)
    marker = tmp_path / "unreviewed.txt"
    plan = CommandPlan(
        (
            sys.executable,
            "-c",
            f"from pathlib import Path; Path({str(marker)!r}).write_text('bad')",
        ),
        tmp_path,
        {},
        "not approved",
    )
    with pytest.raises(SecurityError, match="seal does not match"):
        forged = replace(authorization, plan_sha256=plan_sha256(plan))
        run_plan(plan, authorization=forged)
    assert not marker.exists()


def test_duck_typed_authorization_never_reaches_execution(tmp_path: Path) -> None:
    plan, authorization = _grant(tmp_path)
    forged = SimpleNamespace(
        plan_sha256=authorization.plan_sha256,
        executable_sha256=authorization.executable_sha256,
        input_sha256=authorization.input_sha256,
        explicit_authorization=True,
        authorization_sha256=authorization.authorization_sha256,
        authorized_by=authorization.authorized_by,
    )
    with pytest.raises(SecurityError, match="created by authorize_plan"):
        run_plan(plan, authorization=forged)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "changed",
    [
        {"authorized_by": "another identity"},
        {"purpose": "another use"},
        {"explicit_authorization": False},
        {"input_sha256": "a" * 64},
        {"_seal": b"unissued"},
    ],
)
def test_grant_identity_purpose_and_inputs_remain_bound(tmp_path: Path, changed: dict) -> None:
    _, authorization = _grant(tmp_path)
    with pytest.raises(SecurityError, match="seal does not match"):
        replace(authorization, **changed)


def test_execution_rechecks_binding_even_after_frozen_object_bypass(tmp_path: Path) -> None:
    plan, authorization = _grant(tmp_path)
    object.__setattr__(authorization, "purpose", "altered after construction")
    with pytest.raises(SecurityError, match="seal does not match"):
        run_plan(plan, authorization=authorization)


def test_unchanged_grant_copies_preserve_reusable_local_semantics(tmp_path: Path) -> None:
    plan, authorization = _grant(tmp_path)
    for duplicate in (copy.copy(authorization), replace(authorization)):
        record = run_plan(plan, authorization=duplicate, timeout=5)
        assert record.completed is True
        assert record.authorization_sha256 == authorization.authorization_sha256
