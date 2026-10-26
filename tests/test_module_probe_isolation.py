from __future__ import annotations

import json
import os
import site
import subprocess
import sys
import venv
from pathlib import Path
from types import SimpleNamespace

import pytest

from tsao_computation.accelerators import probe_solver_capability
from tsao_computation.adapters import registry as adapter_registry
from tsao_computation.adapters.base import Adapter
from tsao_computation.cli import main
from tsao_computation.errors import ContractError, SecurityError
from tsao_computation.security import process as process_security
from tsao_computation.security import python_module_probe as metadata_probe


def _marker_source(marker: Path) -> str:
    return (
        f"with open({str(marker)!r}, 'w') as stream:\n    stream.write('unexpected import')\n"
        "raise RuntimeError('metadata discovery must not import this fixture')\n"
    )


def test_probe_ignores_current_directory_and_python_startup_overrides(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    marker = tmp_path / "executed.txt"
    for name in ("json.py", "sitecustomize.py", "local_only_dependency.py"):
        (tmp_path / name).write_text(_marker_source(marker), encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("PYTHONPATH", str(tmp_path))
    monkeypatch.setenv("PYTHONSTARTUP", str(tmp_path / "sitecustomize.py"))
    monkeypatch.setenv("PYTHONHOME", str(tmp_path))

    assert process_security.probe_python_modules(
        sys.executable, ("json.decoder", "local_only_dependency", "absent_parent.child")
    ) == ("local_only_dependency", "absent_parent.child")
    assert not marker.exists()


@pytest.fixture
def isolated_installation(tmp_path: Path) -> tuple[Path, Path, Path]:
    environment = tmp_path / "venv"
    venv.EnvBuilder(with_pip=False, symlinks=os.name != "nt").create(environment)
    executable = environment / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    installed = Path(site.getsitepackages([str(environment)])[0])
    installed.mkdir(parents=True, exist_ok=True)
    marker = tmp_path / "package-imported.txt"
    source = _marker_source(marker)
    (installed / "metadata_parent").mkdir()
    (installed / "metadata_parent" / "__init__.py").write_text(source, encoding="utf-8")
    (installed / "metadata_parent" / "child.py").write_text(source, encoding="utf-8")
    (installed / "metadata_namespace" / "inner").mkdir(parents=True)
    (installed / "metadata_namespace" / "inner" / "leaf.py").write_text(source, encoding="utf-8")
    (installed / "metadata_top.py").write_text(source, encoding="utf-8")
    (installed / "sitecustomize.py").write_text(source, encoding="utf-8")
    (installed / "audit-hook.pth").write_text(
        f"import pathlib; pathlib.Path({str(marker)!r}).write_text('unexpected startup hook')\n",
        encoding="utf-8",
    )
    return executable, installed, marker


def test_selected_venv_packages_namespace_and_builtins_are_found_without_imports(
    isolated_installation: tuple[Path, Path, Path],
) -> None:
    executable, _, marker = isolated_installation
    requested = (
        "sys",
        "math",
        "json.decoder",
        "metadata_top",
        "metadata_parent.child",
        "metadata_namespace.inner.leaf",
        "metadata_parent.missing",
        "metadata_top.child",
    )
    assert process_security.probe_python_modules(str(executable), requested) == requested[-2:]
    assert not marker.exists()


def test_metadata_lookup_supports_nested_namespaces_without_importing_parent(
    isolated_installation: tuple[Path, Path, Path],
) -> None:
    _, installed, marker = isolated_installation
    paths = (str(installed),)
    assert metadata_probe._module_available("metadata_parent.child", paths)
    assert metadata_probe._module_available("metadata_namespace.inner.leaf", paths)
    assert metadata_probe._module_available("sys", paths)
    assert not metadata_probe._module_available("metadata_parent.missing", paths)
    assert not metadata_probe._module_available("metadata_top.child", paths)
    assert not marker.exists()


def test_adapter_cli_and_command_preparation_share_real_isolated_probe(
    isolated_installation: tuple[Path, Path, Path],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    executable, _, marker = isolated_installation
    adapter = Adapter(
        {
            "slug": "metadata-fixture",
            "executables": [str(executable)],
            "python_modules": ["metadata_parent.child", "metadata_namespace.inner.leaf"],
        }
    )
    monkeypatch.setattr(adapter_registry, "list_adapters", lambda: (adapter,))
    assert main(["probe", "--workers", "1"]) == 0
    report = json.loads(capsys.readouterr().out)
    assert report[0]["available"] is True
    assert report[0]["executable"] == str(executable)
    driver = tmp_path / "driver.py"
    driver.write_text("raise RuntimeError('planning must not run a driver')\n", encoding="utf-8")
    plan = adapter.build_command(driver, executable=str(executable))
    assert plan.argv == (str(executable), driver.name)
    assert plan.execute_allowed is False
    assert not marker.exists()

    missing_adapter = Adapter(
        {
            **dict(adapter.record),
            "python_modules": ["absent_parent.child"],
        }
    )
    monkeypatch.setattr(adapter_registry, "list_adapters", lambda: (missing_adapter,))
    assert main(["probe", "--workers", "1"]) == 0
    report = json.loads(capsys.readouterr().out)
    assert report[0]["available"] is False
    assert "absent_parent.child" in report[0]["reason"]
    with pytest.raises(ContractError, match="required Python modules are missing"):
        missing_adapter.build_command(driver)


def test_solver_capability_binds_the_selected_python_environment(
    isolated_installation: tuple[Path, Path, Path],
) -> None:
    executable, _, marker = isolated_installation
    adapter = {
        "slug": "metadata-fixture",
        "executables": [str(executable)],
        "python_modules": ["metadata_parent.child"],
    }
    evidence = probe_solver_capability(
        "metadata-fixture",
        adapters_loader=lambda: (adapter,),
        accelerators_loader=lambda: ({"slug": "metadata-fixture", "probe_hints": []},),
    )
    assert evidence.executable_path == str(executable)
    assert evidence.missing_python_modules == ()
    assert evidence.qualification_status == "fingerprinted-unqualified"
    assert not marker.exists()


@pytest.mark.parametrize(
    ("returncode", "stdout"),
    [
        (1, ""),
        (1, "[]"),
        (1, '{"schema_version":1,"requested":["json","absent"],"missing":[]}'),
        (0, ""),
        (0, " "),
        (0, "[]"),
        (0, "{}"),
        (0, "null"),
        (0, "not-json"),
        (0, "[" * 2000 + "]" * 2000),
        (0, '{"schema_version":true,"requested":["json","absent"],"missing":[]}'),
        (0, '{"schema_version":2,"requested":["json","absent"],"missing":[]}'),
        (0, '{"schema_version":1,"requested":["absent"],"missing":[]}'),
        (0, '{"schema_version":1,"requested":["json","absent"],"missing":["other"]}'),
        (0, '{"schema_version":1,"requested":["json","absent"],"missing":[false]}'),
        (0, '{"schema_version":1,"requested":["json","absent"],"missing":{}}'),
        (0, '{"schema_version":1,"requested":["json","absent"],"missing":["absent","absent"]}'),
        (0, '{"schema_version":1,"requested":["json","absent"],"missing":["absent","json"]}'),
        (0, '{"schema_version":1,"requested":["json","absent"],"missing":[],"missing":["absent"]}'),
        (0, " " * 65537),
    ],
)
def test_probe_failures_and_unbound_responses_cannot_report_availability(
    returncode: int, stdout: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    requested = ("json", "absent")

    def response(argv, **kwargs):
        assert argv[1:3] == ("-I", "-S")
        return subprocess.CompletedProcess(argv, returncode, stdout, "fixture failure")

    monkeypatch.setattr(process_security, "_run_sanitized", response)
    assert process_security.probe_python_modules(sys.executable, requested) == requested


@pytest.mark.parametrize("missing", [[], ["absent"]])
def test_complete_protocol_response_preserves_missing_module_tuple(
    missing: list[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    requested = ("json", "absent")
    payload = json.dumps({"schema_version": 1, "requested": list(requested), "missing": missing})
    monkeypatch.setattr(
        process_security,
        "_run_sanitized",
        lambda *args, **kwargs: subprocess.CompletedProcess([], 0, payload, ""),
    )
    assert process_security.probe_python_modules(sys.executable, requested) == tuple(missing)


def test_undecodable_probe_output_cannot_report_availability(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def invalid_output(*args, **kwargs):
        raise UnicodeDecodeError("utf-8", b"\xff", 0, 1, "invalid fixture output")

    monkeypatch.setattr(process_security, "_run_sanitized", invalid_output)
    assert process_security.probe_python_modules(sys.executable, ("json",)) == ("json",)


@pytest.mark.parametrize("name", ["pkg..child", ".pkg", "pkg.", "pkg.1child"])
def test_empty_or_invalid_name_components_are_rejected_before_probe(name: str) -> None:
    with pytest.raises(SecurityError, match="dotted identifiers"):
        process_security.probe_python_modules(sys.executable, (name,))


def test_venv_search_paths_respect_system_site_policy_without_running_hooks(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    prefix = tmp_path / "venv"
    (prefix / "bin").mkdir(parents=True)
    config = prefix / "pyvenv.cfg"
    config.write_text("include-system-site-packages = false\n", encoding="utf-8")
    monkeypatch.setattr(metadata_probe.sys, "executable", str(prefix / "bin" / "python"))
    monkeypatch.setattr(metadata_probe.sys, "path", ["", "/trusted/stdlib"])
    paths = metadata_probe._installed_search_paths()
    assert paths == tuple(dict.fromkeys(["/trusted/stdlib", *site.getsitepackages([str(prefix)])]))
    config.write_text("include-system-site-packages = true\n", encoding="utf-8")
    paths = metadata_probe._installed_search_paths()
    assert set(site.getsitepackages([sys.base_prefix, sys.base_exec_prefix])) <= set(paths)
    config.unlink()
    paths = metadata_probe._installed_search_paths()
    assert set(site.getsitepackages([sys.prefix, sys.exec_prefix])) <= set(paths)


def test_private_probe_requires_isolation_and_emits_request_bound_metadata(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    assert metadata_probe.main() == 2
    monkeypatch.setattr(
        metadata_probe,
        "sys",
        SimpleNamespace(
            flags=SimpleNamespace(isolated=1, no_site=1),
            argv=["probe.py", "sys", "not_installed"],
        ),
    )
    monkeypatch.setattr(metadata_probe, "_installed_search_paths", lambda: (str(tmp_path),))
    assert metadata_probe.main() == 0
    assert json.loads(capsys.readouterr().out) == {
        "schema_version": 1,
        "requested": ["sys", "not_installed"],
        "missing": ["not_installed"],
    }
