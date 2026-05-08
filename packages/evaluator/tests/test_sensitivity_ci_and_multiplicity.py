from pathlib import Path

from automechinterp_evaluator.evaluator import evaluate_bundle

from .conftest import read_json, read_yaml, sync_hashes, write_json, write_yaml


def test_method_sensitivity_gate_fails(bundle_dir: Path) -> None:
    payload = read_json(bundle_dir / "evaluation_result.json")
    for cell in payload["hypothesis_results"][0]["raw_cells"]:
        if cell["method"] == "zero_ablation":
            cell["treatment_effect"] = -0.12
    write_json(bundle_dir / "evaluation_result.json", payload)
    sync_hashes(bundle_dir, refresh_eval_protocol_hash=False)

    result = evaluate_bundle(bundle_dir)
    claim = result["claim_reports"][0]
    assert claim["checks"]["method_sensitivity"] is False


def test_confirmatory_ci_gate_requires_confirmatory_slice(bundle_dir: Path) -> None:
    payload = read_json(bundle_dir / "evaluation_result.json")
    for cell in payload["hypothesis_results"][0]["raw_cells"]:
        cell["slice"] = "exploratory"
    write_json(bundle_dir / "evaluation_result.json", payload)
    sync_hashes(bundle_dir, refresh_eval_protocol_hash=False)

    result = evaluate_bundle(bundle_dir)
    claim = result["claim_reports"][0]
    assert claim["checks"]["confirmatory_ci"] is False


def test_multiplicity_gate_can_fail(bundle_dir: Path) -> None:
    payload = read_json(bundle_dir / "evaluation_result.json")
    # Keep means above floor but inflate variance to increase p-value.
    values = [0.0, 0.12] * 8
    for cell, value in zip(payload["hypothesis_results"][0]["raw_cells"], values):
        cell["treatment_effect"] = value
    write_json(bundle_dir / "evaluation_result.json", payload)

    protocol = read_yaml(bundle_dir / "protocol.yaml")
    protocol["statistical_policy"]["fdr_q"] = 1e-6
    write_yaml(bundle_dir / "protocol.yaml", protocol)
    sync_hashes(bundle_dir)

    result = evaluate_bundle(bundle_dir)
    claim = result["claim_reports"][0]
    assert claim["checks"]["multiplicity"] is False
