"""Regression tests for fixes documented in ````.

§1.1 — manifest must include cross_model_results.json hash when the file
       exists; manifest must NOT declare the key when the file is absent.
§1.2 — duplicate (transfer_model_id, hyp_key) rows in cross_model_results.json
       must raise BundleError instead of silent last-write-wins.
§1.4 — ``min_effect_size_d`` must be > 0 when the gate is declared
       (omit the key to disable; 0 silently makes the gate always-pass).
"""
from __future__ import annotations

import importlib.util as _ilu
import json
from pathlib import Path

import pytest
import yaml

from automechinterp_evaluator.evaluator import evaluate_bundle
from automechinterp_evaluator.io_utils import BundleError
from automechinterp_evaluator.loader import load_bundle

# Local conftest helper (path-tolerant import; see test_submission_review).
_spec = _ilu.spec_from_file_location(
    "_evaluator_tests_conftest_audit", Path(__file__).resolve().parent / "conftest.py"
)
_mod = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(_mod)  # type: ignore[union-attr]
sync_hashes = _mod.sync_hashes

def test_manifest_must_declare_cross_model_sha_when_file_present(bundle_dir: Path) -> None:
    """§1.1: phantom evidence detection — file present but hash missing."""
    (bundle_dir / "cross_model_results.json").write_text("[]\n")
    # Do NOT call sync_hashes — manifest is now stale on purpose.
    with pytest.raises(BundleError, match="missing cross_model_results.json hash"):
        load_bundle(bundle_dir)

def test_manifest_must_not_declare_cross_model_sha_when_file_absent(bundle_dir: Path) -> None:
    """§1.1: phantom evidence detection — declaration without file."""
    manifest_path = bundle_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["cross_model_results.json"] = "0" * 64
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    with pytest.raises(BundleError, match="declares a cross_model_results.json hash"):
        load_bundle(bundle_dir)

def test_manifest_with_synced_cross_model_sha_loads(bundle_dir: Path) -> None:
    """§1.1: positive case — declared hash matching file content loads cleanly."""
    (bundle_dir / "cross_model_results.json").write_text("[]\n")
    sync_hashes(bundle_dir)
    load_bundle(bundle_dir)  # must not raise

def test_cross_model_duplicate_rows_raise(bundle_dir: Path) -> None:
    """§1.2: duplicate (transfer_model, hypothesis_id) rows must error."""
    (bundle_dir / "cross_model_results.json").write_text(
        json.dumps(
            [
                {
                    "hypothesis_id": "h_ioi_name_movers",
                    "transfer_model": "target-a",
                    "transfer_effect": 0.10,
                },
                {
                    "hypothesis_id": "h_ioi_name_movers",
                    "transfer_model": "target-a",
                    "transfer_effect": 0.20,
                },
            ],
            indent=2,
        )
        + "\n"
    )
    sync_hashes(bundle_dir)
    with pytest.raises(BundleError, match="duplicate"):
        evaluate_bundle(bundle_dir)

def test_min_effect_size_d_zero_rejected(bundle_dir: Path) -> None:
    """§1.4: power-adequacy gate degenerates if min_effect_size_d <= 0."""
    proto_path = bundle_dir / "protocol.yaml"
    protocol = yaml.safe_load(proto_path.read_text())
    protocol["stage_gates"]["min_effect_size_d"] = 0.0
    proto_path.write_text(yaml.safe_dump(protocol, sort_keys=False))
    sync_hashes(bundle_dir)
    with pytest.raises(BundleError, match="min_effect_size_d must be > 0"):
        load_bundle(bundle_dir)

def test_min_effect_size_d_positive_loads(bundle_dir: Path) -> None:
    """§1.4: positive value loads cleanly."""
    proto_path = bundle_dir / "protocol.yaml"
    protocol = yaml.safe_load(proto_path.read_text())
    protocol["stage_gates"]["min_effect_size_d"] = 0.5
    proto_path.write_text(yaml.safe_dump(protocol, sort_keys=False))
    sync_hashes(bundle_dir)
    load_bundle(bundle_dir)  # must not raise

def test_min_effect_size_d_absent_loads(bundle_dir: Path) -> None:
    """§1.4: omitting the key disables the gate without rejection."""
    # Default template already omits the key; just confirm load() works.
    load_bundle(bundle_dir)
