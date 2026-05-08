from __future__ import annotations

import json
from pathlib import Path

import pytest

from automechinterp_evaluator.evaluator import evaluate_bundle
from automechinterp_evaluator.io_utils import BundleError

from .conftest import read_json, sync_hashes, write_json


def test_duplicate_semantic_claims_are_rejected(bundle_dir: Path) -> None:
    hypothesis_path = bundle_dir / "hypothesis.jsonl"
    lines = hypothesis_path.read_text().strip().splitlines()
    original = json.loads(lines[0])
    duplicate = dict(original)
    duplicate["hypothesis_id"] = "duplicate_semantic_claim"
    with hypothesis_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(duplicate) + "\n")

    eval_payload = read_json(bundle_dir / "evaluation_result.json")
    first_row = dict(eval_payload["hypothesis_results"][0])
    first_row["hypothesis_id"] = duplicate["hypothesis_id"]
    eval_payload["hypothesis_results"].append(first_row)
    write_json(bundle_dir / "evaluation_result.json", eval_payload)
    sync_hashes(bundle_dir)

    with pytest.raises(BundleError, match="duplicates the semantic content"):
        evaluate_bundle(bundle_dir)
