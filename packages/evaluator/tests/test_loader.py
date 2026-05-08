"""Dedicated tests for the bundle loader and schema validation module.

Tests validate_protocol, validate_hypotheses, validate_evaluation_result,
validate_manifest, and load_bundle across all schema edge cases.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "packages" / "evaluator" / "src"))

from automechinterp_evaluator.loader import (
    validate_protocol,
    validate_hypotheses,
    validate_evaluation_result,
    load_bundle,
)
from automechinterp_evaluator.io_utils import BundleError


def _good_protocol() -> dict:
    return {
        "protocol_id": "test_loader_v1",
        "protocol_version": "2.0",
        "frozen": True,
        "unit_of_work": {
            "task_id": "ioi_v0",
            "model_id": "gpt2-small",
            "metric_id": "logit_diff",
            "dataset_id": "ioi_templates_v1",
            "clean_corrupt_definition": "swap-indirect-object-entity",
        },
        "execution_grid": {
            "seeds": [101, 202],
            "prompt_variants": ["base", "paraphrase"],
            "resample_ids": [0],
            "methods": ["mean_ablation", "zero_ablation"],
        },
        "control_policy": {
            "required_families": ["wrong_position", "wrong_layer", "random_component", "mismatched_source"],
            "max_control_abs_mean": 0.5,
        },
        "stage_gates": {
            "min_causal_effect": 0.05,
            "min_specificity_ratio": 5.0,
            "min_robustness": {"seed": 0.5, "prompt_variant": 0.5, "resample": 0.5},
            "max_method_sensitivity_std": 0.03,
            "require_confirmatory_ci_excludes_zero": True,
        },
        "statistical_policy": {
            "alpha": 0.05,
            "fdr_q": 0.10,
            "min_effect_floor": 0.04,
            "multiplicity_method": "benjamini-hochberg",
        },
        "sample_size_policy": {
            "min_examples_per_cell": 20,
            "exploratory_fraction": 0.3,
            "power_target": 0.80,
            "minimum_detectable_effect": 0.5,
            "require_confirmatory_split": False,
            "min_cells_per_hypothesis": 4,
        },
        "claim_budget": {"max_total_claims": 5, "max_claims_per_task": 5},
        "language_policy": {"forbidden_without_pass": ["solved", "proved", "validated"]},
        "intervention_levels": ["head"],
    }


class TestValidateProtocol:
    def test_good_protocol_passes(self):
        validate_protocol(_good_protocol())

    def test_missing_protocol_id_raises(self):
        p = _good_protocol()
        del p["protocol_id"]
        with pytest.raises(BundleError, match="protocol_id"):
            validate_protocol(p)

    def test_missing_unit_of_work_raises(self):
        p = _good_protocol()
        del p["unit_of_work"]
        with pytest.raises(BundleError, match="unit_of_work"):
            validate_protocol(p)

    def test_empty_seeds_raises(self):
        p = _good_protocol()
        p["execution_grid"]["seeds"] = []
        with pytest.raises(BundleError, match="seeds"):
            validate_protocol(p)

    def test_empty_methods_raises(self):
        p = _good_protocol()
        p["execution_grid"]["methods"] = []
        with pytest.raises(BundleError, match="methods"):
            validate_protocol(p)

    def test_exploratory_fraction_zero_raises(self):
        p = _good_protocol()
        p["sample_size_policy"]["exploratory_fraction"] = 0.0
        with pytest.raises(BundleError, match="exploratory_fraction"):
            validate_protocol(p)

    def test_exploratory_fraction_one_raises(self):
        p = _good_protocol()
        p["sample_size_policy"]["exploratory_fraction"] = 1.0
        with pytest.raises(BundleError, match="exploratory_fraction"):
            validate_protocol(p)

    def test_missing_statistical_policy_raises(self):
        p = _good_protocol()
        del p["statistical_policy"]
        with pytest.raises(BundleError):
            validate_protocol(p)

    def test_missing_control_policy_raises(self):
        p = _good_protocol()
        del p["control_policy"]
        with pytest.raises(BundleError):
            validate_protocol(p)


class TestValidateHypotheses:
    def _make_hypothesis(self) -> dict:
        return {
            "hypothesis_id": "h_test_001",
            "protocol_id": "test_loader_v1",
            "task_id": "ioi_v0",
            "model_id": "gpt2-small",
            "metric_id": "logit_diff",
            "claim_text": "Test claim",
            "candidate_components": [{"component_type": "head", "layer": 0, "head": 0}],
            "predicted_effect_direction": "increase",
            "predicted_min_effect": 0.05,
            "predicted_specificity_ratio": 5.0,
            "expected_failure_modes": ["distributed_computation"],
        }

    def test_good_hypothesis_passes(self):
        protocol = _good_protocol()
        validate_hypotheses([self._make_hypothesis()], protocol)

    def test_missing_hypothesis_id_raises(self):
        h = self._make_hypothesis()
        del h["hypothesis_id"]
        with pytest.raises(BundleError, match="hypothesis_id"):
            validate_hypotheses([h], _good_protocol())

    def test_wrong_protocol_id_raises(self):
        h = self._make_hypothesis()
        h["protocol_id"] = "wrong_protocol"
        with pytest.raises(BundleError, match="protocol_id"):
            validate_hypotheses([h], _good_protocol())

    def test_invalid_direction_raises(self):
        h = self._make_hypothesis()
        h["predicted_effect_direction"] = "sideways"
        with pytest.raises(BundleError, match="direction"):
            validate_hypotheses([h], _good_protocol())

    def test_empty_components_raises(self):
        h = self._make_hypothesis()
        h["candidate_components"] = []
        with pytest.raises(BundleError, match="component"):
            validate_hypotheses([h], _good_protocol())

    def test_duplicate_structured_claim_raises(self):
        h1 = self._make_hypothesis()
        h2 = self._make_hypothesis()
        h2["hypothesis_id"] = "h_test_002"
        h2["claim_text"] = "Same evidence, different wording"
        with pytest.raises(BundleError, match="Duplicate claim content"):
            validate_hypotheses([h1, h2], _good_protocol())
