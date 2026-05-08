from pathlib import Path

import pytest

from automechinterp_evaluator.evaluator import evaluate_bundle
from automechinterp_evaluator.io_utils import BundleError

from .conftest import read_json, write_json


def test_protocol_hash_mismatch_fails(bundle_dir: Path) -> None:
    payload = read_json(bundle_dir / "evaluation_result.json")
    payload["protocol_sha256"] = "deadbeef"
    write_json(bundle_dir / "evaluation_result.json", payload)

    with pytest.raises(BundleError, match="protocol_sha256 mismatch"):
        evaluate_bundle(bundle_dir)


def test_manifest_mismatch_fails(bundle_dir: Path) -> None:
    manifest = read_json(bundle_dir / "manifest.json")
    manifest["protocol.yaml"] = "deadbeef"
    write_json(bundle_dir / "manifest.json", manifest)

    with pytest.raises(BundleError, match="manifest mismatch"):
        evaluate_bundle(bundle_dir)
