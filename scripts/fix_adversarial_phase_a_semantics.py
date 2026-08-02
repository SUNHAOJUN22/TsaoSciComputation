from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise ValueError(f"expected one {label}, found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8", newline="\n")


contract = ROOT / "tsao_computation/contracts/calculation.py"
replace_once(
    contract,
    '''    for item in values:
        parsed = _slug(item, field_name=field_name) if slugs else _required_string(item, field_name=field_name)
        if parsed not in normalized:
            normalized.append(parsed)
''',
    '''    for item in values:
        if not isinstance(item, str) or not item.strip():
            raise ContractError(f"{field_name} must contain non-empty strings")
        parsed = _slug(item, field_name=field_name) if slugs else item.strip()
        if parsed not in normalized:
            normalized.append(parsed)
''',
    "contract collection item validation",
)

adapter = ROOT / "tsao_computation/adapters/base.py"
text = adapter.read_text(encoding="utf-8")
start = text.index("_COMPLETION_SUCCESS = re.compile(")
end = text.index("\n_COMPLETION_FAILURE_PATTERN", start)
completion = '''_COMPLETION_SUCCESS = re.compile(
    r"\\bnormal\\s+termination\\b|"
    r"(?:^|[;\\r\\n])\\s*(?:(?:run|job|calculation|simulation)\\s+)?"
    r"(?:finished|completed)(?:\\s+successfully)?\\s*(?=$|[;\\r\\n])|"
    r"\\btotal\\s+wall\\s+time\\b"
)
'''
adapter.write_text(text[:start] + completion + text[end:], encoding="utf-8", newline="\n")

test = ROOT / "tests/test_fail_closed_coverage_regressions.py"
text = test.read_text(encoding="utf-8")
text = text.replace("import importlib.metadata\n", "import importlib.metadata\nimport os\nimport stat\n", 1)
old = '''    executable.parent.mkdir()
    executable.write_text("fixture", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
'''
new = '''    executable.parent.mkdir()
    executable.write_text("fixture", encoding="utf-8")
    if os.name != "nt":
        executable.chmod(executable.stat().st_mode | stat.S_IXUSR)
    monkeypatch.chdir(tmp_path)
'''
if text.count(old) != 1:
    raise ValueError("relative executable fixture not found exactly once")
test.write_text(text.replace(old, new, 1), encoding="utf-8", newline="\n")

print("phase A state semantics corrections applied")
