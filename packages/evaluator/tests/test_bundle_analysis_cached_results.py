from __future__ import annotations

import json
from pathlib import Path

from main._bundle_analysis import evaluate_bundle_records


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def _sync_hashes(bundle_dir: Path, *, refresh_eval_protocol_hash: bool = True) -> None:
    import hashlib

    protocol_path = bundle_dir / "protocol.yaml"
    hypothesis_path = bundle_dir / "hypothesis.jsonl"
    evaluation_path = bundle_dir / "evaluation_result.json"
    manifest_path = bundle_dir / "manifest.json"

    def file_sha(path: Path) -> str:
        h = hashlib.sha256()
        h.update(path.read_bytes())
        return h.hexdigest()

    protocol_sha = file_sha(protocol_path)
    if refresh_eval_protocol_hash:
        payload = json.loads(evaluation_path.read_text())
        payload["protocol_sha256"] = protocol_sha
        evaluation_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")

    manifest = {
        "protocol.yaml": file_sha(protocol_path),
        "hypothesis.jsonl": file_sha(hypothesis_path),
        "evaluation_result.json": file_sha(evaluation_path),
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")


def test_evaluate_bundle_records_cached_mode_uses_evaluation_result_json(tmp_path: Path) -> None:
    bundle_root = tmp_path / "cached_root"
    bundle = bundle_root / "toy_task_v0_test-model"
    _write(
        bundle / "protocol.yaml",
        "unit_of_work:\n"
        "  task_id: toy_task_v0\n"
        "  model_id: test-model\n",
    )
    _write(
        bundle / "hypothesis.jsonl",
        json.dumps(
            {
                "hypothesis_id": "h1",
                "candidate_components": [{"component_type": "head"}],
            }
        )
        + "\n",
    )
    eval_payload = {
        "overall": {"hypothesis_count": 1, "accepted_count": 1},
        "claim_reports": [
            {
                "hypothesis_id": "h1",
                "evidence_tier": "single_model_confirmed",
                "passed": True,
                "failed_checks": [],
                "not_evaluated_checks": [],
                "gate_outcomes": {},
                "metrics": {},
            }
        ],
        "hypothesis_results": [{"hypothesis_id": "h1", "raw_cells": []}],
    }
    _write(bundle / "evaluation_result.json", json.dumps(eval_payload) + "\n")

    records = evaluate_bundle_records(bundle_root, use_cached_results=True)
    assert len(records) == 1
    assert records[0]["bundle"] == "toy_task_v0_test-model"
    assert records[0]["result"]["overall"]["accepted_count"] == 1


def test_evaluate_bundle_records_cached_mode_upgrades_legacy_cache(bundle_dir: Path) -> None:
    original = json.loads((bundle_dir / "evaluation_result.json").read_text())
    legacy_payload = {
        "protocol_id": original["protocol_id"],
        "protocol_sha256": original["protocol_sha256"],
        "hypothesis_results": original["hypothesis_results"],
    }
    _write(bundle_dir / "evaluation_result.json", json.dumps(legacy_payload) + "\n")
    current_cache = bundle_dir / "evaluation_result_current.json"
    if current_cache.exists():
        current_cache.unlink()
    _sync_hashes(bundle_dir, refresh_eval_protocol_hash=False)

    records = evaluate_bundle_records(bundle_dir.parent, use_cached_results=True)
    assert len(records) == 1
    assert records[0]["bundle"] == bundle_dir.name
    assert records[0]["result"]["overall"]["accepted_count"] >= 0
    assert current_cache.exists()
    upgraded = json.loads(current_cache.read_text())
    assert "overall" in upgraded
    assert "claim_reports" in upgraded
