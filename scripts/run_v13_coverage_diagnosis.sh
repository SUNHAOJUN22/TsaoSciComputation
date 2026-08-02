#!/usr/bin/env bash
set -Eeuo pipefail

ORIGINAL_SHA="$(git rev-parse HEAD)"
git read-tree --reset -u 27af704e6f6c28dae400cdd28d943936312fd802
git checkout "$ORIGINAL_SHA" -- scripts/prepare_execution_integrity_v13e.py
git clean -fd
python scripts/prepare_execution_integrity_v13e.py
python -m pip install -e '.[validation,quality,security]'
python -m coverage erase
python -m coverage run --branch -m pytest -q
python -m coverage json -o /tmp/v13-coverage-diagnosis.json
python - <<'PY' > /tmp/v13-coverage-summary.txt
import json
from pathlib import Path

data = json.loads(Path('/tmp/v13-coverage-diagnosis.json').read_text())
print(f"TOTAL {data['totals']['percent_covered']:.4f}%")
rows = []
for name, info in data['files'].items():
    if not name.startswith('tsao_computation/'):
        continue
    summary = info['summary']
    rows.append((summary['percent_covered'], name, info.get('missing_lines', []), summary))
for percent, name, missing, summary in sorted(rows)[:35]:
    print(
        f"{percent:.2f}% {name} statements={summary['num_statements']} "
        f"branches={summary.get('num_branches', 0)} missing={missing}"
    )
PY
cat /tmp/v13-coverage-summary.txt
gh issue comment 85 --repo "$GITHUB_REPOSITORY" --body-file /tmp/v13-coverage-summary.txt
