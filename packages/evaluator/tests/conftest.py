from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest
import yaml


@pytest.fixture
def bundle_dir(tmp_path: Path) -> Path:
    src = Path(__file__).resolve().parents[1] / "templates" / "example_bundle"
    dst = tmp_path / "bundle"
    shutil.copytree(src, dst)
    return dst


def read_json(path: Path) -> dict:
    return json.loads(path.read_text())


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def read_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text())


def write_yaml(path: Path, payload: dict) -> None:
    path.write_text(yaml.safe_dump(payload, sort_keys=False))


def sync_hashes(bundle_dir: Path, *, refresh_eval_protocol_hash: bool = True) -> None:
    protocol_path = bundle_dir / "protocol.yaml"
    hypothesis_path = bundle_dir / "hypothesis.jsonl"
    evaluation_path = bundle_dir / "evaluation_result.json"
    manifest_path = bundle_dir / "manifest.json"
    cross_model_path = bundle_dir / "cross_model_results.json"

    import hashlib

    def file_sha(path: Path) -> str:
        h = hashlib.sha256()
        h.update(path.read_bytes())
        return h.hexdigest()

    protocol_sha = file_sha(protocol_path)
    if refresh_eval_protocol_hash:
        payload = read_json(evaluation_path)
        payload["protocol_sha256"] = protocol_sha
        write_json(evaluation_path, payload)

    manifest = {
        "protocol.yaml": file_sha(protocol_path),
        "hypothesis.jsonl": file_sha(hypothesis_path),
        "evaluation_result.json": file_sha(evaluation_path),
    }
    # include cross_model_results.json in the
    # integrity hash chain when present.
    if cross_model_path.exists():
        manifest["cross_model_results.json"] = file_sha(cross_model_path)
    write_json(manifest_path, manifest)
