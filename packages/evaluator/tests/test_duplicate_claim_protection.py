from __future__ import annotations

import json
import hashlib
from pathlib import Path

import pytest

from automechinterp_evaluator.evaluator import evaluate_bundle
from automechinterp_evaluator.io_utils import BundleError


def _file_sha(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def _sync_hashes(bundle_dir: Path) -> None:
    protocol_path = bundle_dir / "protocol.yaml"
    hypothesis_path = bundle_dir / "hypothesis.jsonl"
    evaluation_path = bundle_dir / "evaluation_result.json"
    payload = json.loads(evaluation_path.read_text())
    payload["protocol_sha256"] = _file_sha(protocol_path)
    evaluation_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    manifest = {
        "protocol.yaml": _file_sha(protocol_path),
        "hypothesis.jsonl": _file_sha(hypothesis_path),
        "evaluation_result.json": _file_sha(evaluation_path),
    }
    (bundle_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")


def test_duplicate_claim_content_is_rejected(bundle_dir: Path) -> None:
    hypothesis_path = bundle_dir / "hypothesis.jsonl"
    rows = [json.loads(line) for line in hypothesis_path.read_text().splitlines() if line.strip()]
    duplicate = dict(rows[0])
    duplicate["hypothesis_id"] = "h_duplicate_claim"
    rows.append(duplicate)
    hypothesis_path.write_text("\n".join(json.dumps(row) for row in rows) + "\n")
    _sync_hashes(bundle_dir)

    with pytest.raises(BundleError, match="duplicates the semantic content"):
        evaluate_bundle(bundle_dir)
