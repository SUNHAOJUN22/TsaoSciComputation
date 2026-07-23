from __future__ import annotations

import ast
from pathlib import Path

import pytest

from tsao_computation.repository_audit import _parse_project_version


def test_project_version_parser_uses_project_table() -> None:
    text = """[tool.example]
version = "99.0"

[project]
name = "demo"
version = "3.0.0" # release
"""
    assert _parse_project_version(text) == "3.0.0"


def test_project_version_parser_accepts_single_quotes_and_table_comment() -> None:
    text = "[project] # package metadata\nversion = '3.0.0'\n"
    assert _parse_project_version(text) == "3.0.0"


@pytest.mark.parametrize(
    "text",
    (
        "",
        "[project]\nname = 'demo'\n",
        "[project]\nversion = 3\n",
    ),
)
def test_project_version_parser_rejects_invalid_values(text: str) -> None:
    with pytest.raises(ValueError, match="project.*version"):
        _parse_project_version(text)


def test_repository_audit_source_is_python310_compatible() -> None:
    source = Path("tsao_computation/repository_audit.py").read_text(encoding="utf-8")
    ast.parse(source, filename="repository_audit.py", feature_version=(3, 10))
    assert "tomllib" not in source
