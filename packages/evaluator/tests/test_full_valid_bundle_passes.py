from pathlib import Path

from automechinterp_evaluator.evaluator import evaluate_bundle


def test_full_valid_bundle_passes(bundle_dir: Path) -> None:
    result = evaluate_bundle(bundle_dir)
    # Without released transfer evidence, the best non-transfer tiers are
    # causal_plus_robustness or single_model_confirmed depending on slice coverage.
    claim = result["claim_reports"][0]
    assert claim["evidence_tier"] in ("causal_plus_robustness", "single_model_confirmed")
    assert claim["failed_checks"] == []
    # With no cross-model data, cross_model_transfer should be not_evaluated unless
    # the template is upgraded to include transfer artifacts in the future.
    assert "cross_model_transfer" in claim.get("not_evaluated_checks", []) or claim["evidence_tier"] == "cross_model_confirmed"
