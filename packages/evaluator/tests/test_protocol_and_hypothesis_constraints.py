from pathlib import Path

import pytest

from automechinterp_evaluator.evaluator import evaluate_bundle
from automechinterp_evaluator.io_utils import BundleError

from .conftest import read_yaml, sync_hashes, write_yaml


def test_methods_min_count_enforced(bundle_dir: Path) -> None:
    protocol = read_yaml(bundle_dir / "protocol.yaml")
    protocol["execution_grid"]["methods"] = ["mean_ablation"]
    write_yaml(bundle_dir / "protocol.yaml", protocol)
    sync_hashes(bundle_dir)

    with pytest.raises(BundleError, match=">=2 methods"):
        evaluate_bundle(bundle_dir)


def test_claim_budget_enforced(bundle_dir: Path) -> None:
    protocol = read_yaml(bundle_dir / "protocol.yaml")
    protocol["claim_budget"]["max_total_claims"] = 0
    write_yaml(bundle_dir / "protocol.yaml", protocol)
    sync_hashes(bundle_dir)

    with pytest.raises(BundleError, match="max_total_claims"):
        evaluate_bundle(bundle_dir)


def test_discovery_cannot_self_certify(bundle_dir: Path) -> None:
    lines = (bundle_dir / "hypothesis.jsonl").read_text().splitlines()
    # Parse and rewrite first row with forbidden language.
    import json

    obj = json.loads(lines[0])
    obj["claim_text"] = "This hypothesis is solved and confirmed."
    (bundle_dir / "hypothesis.jsonl").write_text(json.dumps(obj) + "\n")
    sync_hashes(bundle_dir, refresh_eval_protocol_hash=False)

    with pytest.raises(BundleError, match="forbidden verdict language"):
        evaluate_bundle(bundle_dir)
