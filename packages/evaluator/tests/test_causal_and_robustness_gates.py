from pathlib import Path

from automechinterp_evaluator.evaluator import evaluate_bundle

from .conftest import read_json, sync_hashes, write_json


def test_causal_effect_gate_fails_when_too_small(bundle_dir: Path) -> None:
    payload = read_json(bundle_dir / "evaluation_result.json")
    for cell in payload["hypothesis_results"][0]["raw_cells"]:
        cell["treatment_effect"] = 0.01
    write_json(bundle_dir / "evaluation_result.json", payload)
    sync_hashes(bundle_dir, refresh_eval_protocol_hash=False)

    result = evaluate_bundle(bundle_dir)
    claim = result["claim_reports"][0]
    assert claim["checks"]["causal_effect"] is False


def test_seed_robustness_gate_fails(bundle_dir: Path) -> None:
    payload = read_json(bundle_dir / "evaluation_result.json")
    for cell in payload["hypothesis_results"][0]["raw_cells"]:
        if cell["seed"] == 202:
            cell["treatment_effect"] = -0.08
    write_json(bundle_dir / "evaluation_result.json", payload)
    sync_hashes(bundle_dir, refresh_eval_protocol_hash=False)

    result = evaluate_bundle(bundle_dir)
    claim = result["claim_reports"][0]
    assert claim["checks"]["robustness"] is False


def test_prompt_robustness_gate_fails(bundle_dir: Path) -> None:
    payload = read_json(bundle_dir / "evaluation_result.json")
    for cell in payload["hypothesis_results"][0]["raw_cells"]:
        if cell["prompt_variant"] == "paraphrase":
            cell["treatment_effect"] = -0.09
    write_json(bundle_dir / "evaluation_result.json", payload)
    sync_hashes(bundle_dir, refresh_eval_protocol_hash=False)

    result = evaluate_bundle(bundle_dir)
    claim = result["claim_reports"][0]
    assert claim["checks"]["robustness"] is False


def test_resample_robustness_gate_fails(bundle_dir: Path) -> None:
    payload = read_json(bundle_dir / "evaluation_result.json")
    for cell in payload["hypothesis_results"][0]["raw_cells"]:
        if cell["resample_id"] == 1:
            cell["treatment_effect"] = -0.09
    write_json(bundle_dir / "evaluation_result.json", payload)
    sync_hashes(bundle_dir, refresh_eval_protocol_hash=False)

    result = evaluate_bundle(bundle_dir)
    claim = result["claim_reports"][0]
    assert claim["checks"]["robustness"] is False
