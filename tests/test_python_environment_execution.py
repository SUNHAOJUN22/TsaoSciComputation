from __future__ import annotations

import json
import os
import shutil
import site
import sys
import venv
from pathlib import Path

import pytest

from tsao_computation.adapters.base import Adapter, CommandPlan
from tsao_computation.errors import SecurityError
from tsao_computation.execution import authorize_plan, plan_sha256, run_plan


def test_probed_virtual_environment_is_the_authorized_execution_environment(tmp_path: Path) -> None:
    environment = tmp_path / "venv"
    venv.EnvBuilder(with_pip=False, symlinks=os.name != "nt").create(environment)
    executable = environment / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    installed = Path(site.getsitepackages([str(environment)])[0])
    installed.mkdir(parents=True, exist_ok=True)
    (installed / "venv_only_dependency.py").write_text("VALUE = 34\n", encoding="utf-8")
    output = tmp_path / "interpreter.json"
    driver = tmp_path / "driver.py"
    driver.write_text(
        "import json, sys, venv_only_dependency\n"
        f"with open({str(output)!r}, 'w') as stream:\n"
        "    json.dump({'prefix': sys.prefix, 'value': venv_only_dependency.VALUE}, stream)\n",
        encoding="utf-8",
    )
    adapter = Adapter(
        {
            "slug": "venv-fixture",
            "executables": [str(executable)],
            "python_modules": ["venv_only_dependency"],
        }
    )
    assert adapter.probe().available is True
    plan = adapter.build_command(driver)
    authorization = authorize_plan(
        plan,
        authorized_by="pytest",
        purpose="benign selected-interpreter regression",
        explicit_authorization=True,
    )
    record = run_plan(plan, authorization=authorization, timeout=10)
    assert record.completed is True
    assert record.argv[0] == str(executable)
    observed = json.loads(output.read_text(encoding="utf-8"))
    assert Path(observed["prefix"]) == environment
    assert observed["value"] == 34


@pytest.mark.skipif(os.name == "nt", reason="POSIX executable symlink fixture")
def test_authorization_rejects_same_bytes_at_a_different_symlink_target(tmp_path: Path) -> None:
    first_target = tmp_path / "first-python"
    second_target = tmp_path / "second-python"
    shutil.copy2(sys.executable, first_target)
    shutil.copy2(sys.executable, second_target)
    invoked = tmp_path / "approved-python"
    invoked.symlink_to(first_target)
    plan = CommandPlan((str(invoked), "--version"), tmp_path, {}, "test")
    authorization = authorize_plan(
        plan,
        authorized_by="pytest",
        purpose="symlink target identity regression",
        explicit_authorization=True,
    )
    same_target_other_entry = tmp_path / "other-python"
    same_target_other_entry.symlink_to(first_target)
    other_plan = CommandPlan((str(same_target_other_entry), "--version"), tmp_path, {}, "test")
    assert plan_sha256(other_plan) != authorization.plan_sha256
    invoked.unlink()
    invoked.symlink_to(second_target)
    with pytest.raises(SecurityError, match="immutable command plan"):
        run_plan(plan, authorization=authorization)
