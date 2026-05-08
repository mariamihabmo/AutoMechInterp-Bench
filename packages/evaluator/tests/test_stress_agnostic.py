from __future__ import annotations

import json

from automechinterp_evaluator.loader import _canonical_claim_signature
from automechinterp_evaluator.io_utils import read_yaml
from main.stress_test_agnostic import _latent_hypotheses, run_stress_test


def test_latent_hypotheses_have_unique_structured_signatures(bundle_dir) -> None:
    protocol = read_yaml(bundle_dir / "protocol.yaml")
    template = json.loads((bundle_dir / "hypothesis.jsonl").read_text().splitlines()[0])

    hypotheses = _latent_hypotheses(template, protocol, count=8)
    signatures = [_canonical_claim_signature(row) for row in hypotheses]

    assert len(signatures) == len(set(signatures))


def test_run_stress_test_succeeds_on_example_bundle(bundle_dir) -> None:
    payload = run_stress_test(bundle_dir, count=6)

    assert payload["negatives"] == 6
    assert set(payload["conditions"]) == {"full_contract", "no_controls_suite", "no_robustness_suite"}
    for row in payload["conditions"].values():
        assert row["total"] == 6
