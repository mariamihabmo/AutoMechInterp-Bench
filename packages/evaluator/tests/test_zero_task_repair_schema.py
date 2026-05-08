from __future__ import annotations

import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
OUT = REPO_ROOT / "main" / "output" / "repro" / "zero_task_confirmatory_repair.json"


def test_zero_task_repair_output_exposes_backward_compatible_rows_alias() -> None:
    if not OUT.exists():
        pytest.skip("zero_task_confirmatory_repair.json not present")
    payload = json.loads(OUT.read_text())
    rows = payload.get("rows")
    bundles = payload.get("bundles")
    assert isinstance(rows, list)
    assert isinstance(bundles, list)
    assert rows == bundles
    agg = payload.get("aggregate") or {}
    assert int(agg.get("bundles_repaired") or 0) == len(rows)
