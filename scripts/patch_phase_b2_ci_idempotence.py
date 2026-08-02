from __future__ import annotations

from pathlib import Path

PATH = Path("scripts/apply_adversarial_super_skill_phase_b2.py")
START = 'if text.count("os: [ubuntu-latest, windows-latest, macos-latest]") != 2:'
END = '\n\npyproject = ROOT / "pyproject.toml"'
REPLACEMENT = "\n".join(
    [
        'legacy = "os: [ubuntu-latest, windows-latest, macos-latest]"',
        'current = "os: [ubuntu-latest, windows-latest]"',
        "legacy_count = text.count(legacy)",
        "if legacy_count not in (0, 2):",
        '    raise ValueError(f"unexpected CI platform matrix count: {legacy_count}")',
        "updated = text.replace(legacy, current)",
        "if updated.count(current) != 2:",
        '    raise ValueError("expected two Windows/Linux CI platform matrices")',
        'ci.write_text(updated, encoding="utf-8", newline="\\n")',
        "",
    ]
)


def main() -> int:
    text = PATH.read_text(encoding="utf-8")
    start = text.find(START)
    if start < 0:
        raise ValueError("Phase B2 CI governance start marker not found")
    end = text.find(END, start)
    if end < 0:
        raise ValueError("Phase B2 CI governance end marker not found")
    PATH.write_text(text[:start] + REPLACEMENT + text[end:], encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
