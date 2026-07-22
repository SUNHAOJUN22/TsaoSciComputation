import json
from pathlib import Path

import _bootstrap  # noqa: F401

from tsao_computation.repository_audit import audit_repository

r = audit_repository(Path("."))
print(json.dumps(r, indent=2, sort_keys=True))
raise SystemExit(0 if r["passed"] else 1)
