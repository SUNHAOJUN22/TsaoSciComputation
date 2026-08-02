from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if text.count(old) != 1:
        raise ValueError(f"expected one {label}, found {text.count(old)}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8", newline="\n")


(ROOT / "tsao_computation/security/__init__.py").write_text(
    '''from .paths import atomic_write_text, confined_path
from .process import safe_run

__all__ = ["confined_path", "atomic_write_text", "safe_run"]
''',
    encoding="utf-8",
    newline="\n",
)

process = ROOT / "tsao_computation/security/process.py"
text = process.read_text(encoding="utf-8")
start = text.index("def _subprocess_environment(")
end = text.index("\n\ndef safe_run(", start)
replacement = '''def _override_allowed(key: str) -> bool:
    normalized = key.upper()
    return (
        normalized in _SAFE_OVERRIDE_KEYS
        or normalized in _PORTABLE_ENVIRONMENT_KEYS
        or normalized in _WINDOWS_ENVIRONMENT_KEYS
        or normalized.startswith("TSAO_")
    )


def _subprocess_environment(
    overrides: Mapping[str, str] | None = None, *, parent: Mapping[str, str] | None = None,
    platform_name: str | None = None,
) -> dict[str, str]:
    source = os.environ if parent is None else parent
    platform = os.name if platform_name is None else platform_name
    allowed = _PORTABLE_ENVIRONMENT_KEYS + (_WINDOWS_ENVIRONMENT_KEYS if platform == "nt" else ())
    if platform == "nt":
        source_by_name = {str(key).casefold(): str(value) for key, value in source.items()}
        merged = {name: source_by_name[name.casefold()] for name in allowed if name.casefold() in source_by_name}
    else:
        merged = {name: str(source[name]) for name in allowed if name in source}
    merged.setdefault("PATH", "")
    merged["LANG"] = "C.UTF-8"
    if overrides:
        unsafe = sorted(str(key) for key in overrides if not _override_allowed(str(key)))
        if unsafe:
            raise SecurityError(f"unsafe subprocess environment overrides: {unsafe}")
        for raw_key, raw_value in overrides.items():
            key = str(raw_key)
            value = str(raw_value)
            if not value or "\\x00" in value:
                raise SecurityError(f"invalid subprocess environment value: {key}")
            if platform == "nt":
                for existing in tuple(merged):
                    if existing.casefold() == key.casefold():
                        del merged[existing]
            merged[key] = value
    return merged
'''
process.write_text(text[:start] + replacement + text[end:], encoding="utf-8", newline="\n")

core = ROOT / "tests/test_core.py"
replace_once(
    core,
    '    r = safe_run([sys.executable, "-c", "print(7)"], cwd=tmp_path, timeout=5)\n',
    '    r = safe_run(\n        [sys.executable, "-c", "print(7)"],\n        cwd=tmp_path,\n        timeout=5,\n        allow_process_execution=True,\n    )\n',
    "core safe_run authorization",
)

extended = ROOT / "tests/test_extended.py"
text = extended.read_text(encoding="utf-8")
text = text.replace(
    "from tsao_computation.execution import run_plan\n",
    "from tsao_computation.execution import authorize_plan, run_plan\n",
    1,
)
text = text.replace(
    '    adapter = get_adapter("orca")\n    plan = adapter.build_command(source, executable=sys.executable)\n',
    '    adapter = Adapter({"slug": "test-python", "executables": [sys.executable]})\n    plan = adapter.build_command(source, executable=sys.executable)\n',
    1,
)
old_execution = '''    ok = CommandPlan((sys.executable, "-c", "print('ok')"), tmp_path, {}, "test")
    record = run_plan(ok, timeout=5)
    assert record.completed is True
    assert record.returncode == 0
    assert len(record.stdout_sha256) == 64
    failed = CommandPlan((sys.executable, "-c", "raise SystemExit(3)"), tmp_path, {}, "test")
    failed_record = run_plan(failed, timeout=5)
'''
new_execution = '''    ok = CommandPlan((sys.executable, "-c", "print('ok')"), tmp_path, {}, "test")
    ok_authorization = authorize_plan(
        ok, authorized_by="pytest", purpose="execution success test", explicit_authorization=True
    )
    record = run_plan(ok, authorization=ok_authorization, timeout=5)
    assert record.completed is True
    assert record.returncode == 0
    assert len(record.stdout_sha256) == 64
    failed = CommandPlan((sys.executable, "-c", "raise SystemExit(3)"), tmp_path, {}, "test")
    failed_authorization = authorize_plan(
        failed, authorized_by="pytest", purpose="execution failure test", explicit_authorization=True
    )
    failed_record = run_plan(failed, authorization=failed_authorization, timeout=5)
'''
if text.count(old_execution) != 1:
    raise ValueError("execution test block not found exactly once")
text = text.replace(old_execution, new_execution, 1)
text = text.replace(
    "        safe_run(argv, cwd=tmp_path)\n",
    "        safe_run(argv, cwd=tmp_path, allow_process_execution=True)\n",
    1,
)
text = text.replace(
    "        safe_run([sys.executable], cwd=tmp_path, timeout=0)\n",
    "        safe_run([sys.executable], cwd=tmp_path, timeout=0, allow_process_execution=True)\n",
    1,
)
text = text.replace(
    '        safe_run([sys.executable], cwd=tmp_path / "missing")\n',
    '        safe_run([sys.executable], cwd=tmp_path / "missing", allow_process_execution=True)\n',
    1,
)
text = text.replace(
    '        env={"TSAO_TEST": "yes"},\n    )\n',
    '        env={"TSAO_TEST": "yes"},\n        allow_process_execution=True,\n    )\n',
    1,
)
extended.write_text(text, encoding="utf-8", newline="\n")

print("phase A public API compatibility migration applied")
