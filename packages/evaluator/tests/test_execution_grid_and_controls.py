from pathlib import Path

import pytest

from automechinterp_evaluator.evaluator import evaluate_bundle
from automechinterp_evaluator.io_utils import BundleError

from .conftest import read_json, read_yaml, sync_hashes, write_json, write_yaml


def _single_claim(bundle_dir: Path) -> dict:
    payload = read_json(bundle_dir / "evaluation_result.json")
    return payload["hypothesis_results"][0]


def test_execution_grid_missing_cell_fails_gate(bundle_dir: Path) -> None:
    payload = read_json(bundle_dir / "evaluation_result.json")
    payload["hypothesis_results"][0]["raw_cells"] = payload["hypothesis_results"][0]["raw_cells"][:-1]
    write_json(bundle_dir / "evaluation_result.json", payload)
    sync_hashes(bundle_dir, refresh_eval_protocol_hash=False)

    result = evaluate_bundle(bundle_dir)
    claim = result["claim_reports"][0]
    assert claim["checks"]["execution_coverage"] is False
    assert claim["passed"] is False


def test_missing_control_family_fails_schema(bundle_dir: Path) -> None:
    payload = read_json(bundle_dir / "evaluation_result.json")
    cell = payload["hypothesis_results"][0]["raw_cells"][0]
    cell["control_effects"].pop("wrong_layer")
    write_json(bundle_dir / "evaluation_result.json", payload)
    sync_hashes(bundle_dir, refresh_eval_protocol_hash=False)

    with pytest.raises(BundleError, match="missing control families"):
        evaluate_bundle(bundle_dir)


def test_specificity_gate_fails_on_large_controls(bundle_dir: Path) -> None:
    payload = read_json(bundle_dir / "evaluation_result.json")
    for cell in payload["hypothesis_results"][0]["raw_cells"]:
        for key in cell["control_effects"]:
            cell["control_effects"][key] = 0.05
    write_json(bundle_dir / "evaluation_result.json", payload)
    sync_hashes(bundle_dir, refresh_eval_protocol_hash=False)

    result = evaluate_bundle(bundle_dir)
    claim = result["claim_reports"][0]
    assert claim["checks"]["negative_controls"] is False


def test_missing_provenance_field_fails_schema(bundle_dir: Path) -> None:
    payload = read_json(bundle_dir / "evaluation_result.json")
    cell = payload["hypothesis_results"][0]["raw_cells"][0]
    cell.pop("runner_id")
    write_json(bundle_dir / "evaluation_result.json", payload)
    sync_hashes(bundle_dir, refresh_eval_protocol_hash=False)

    with pytest.raises(BundleError, match="runner_id"):
        evaluate_bundle(bundle_dir)
