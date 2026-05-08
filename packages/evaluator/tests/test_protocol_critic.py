"""Tests for the protocol critic red-teaming module."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "packages" / "evaluator" / "src"))

from automechinterp_evaluator.protocol_critic import critique_protocol, format_critic_report


def _good_protocol() -> dict:
    return {
        "protocol_id": "test_good_v1",
        "protocol_version": "2.0",
        "frozen": True,
        "unit_of_work": {
            "task_id": "ioi_v0",
            "model_id": "gpt2-small",
            "metric_id": "logit_diff",
        },
        "execution_grid": {
            "seeds": [101, 202, 303],
            "prompt_variants": ["base", "paraphrase", "synonym"],
            "resample_ids": [0, 1],
            "methods": ["mean_ablation", "zero_ablation"],
        },
        "control_policy": {
            "required_families": [
                "wrong_position", "wrong_layer",
                "random_component", "mismatched_source",
            ],
        },
        "stage_gates": {
            "min_causal_effect": 0.05,
            "min_specificity_ratio": 5.0,
            "min_robustness": {"seed": 0.5, "prompt_variant": 0.5, "resample": 0.5},
            "max_method_sensitivity_std": 0.03,
            "require_bidirectional": True,
        },
        "statistical_policy": {
            "alpha": 0.05,
            "min_effect_floor": 0.04,
            "multiplicity_method": "benjamini-hochberg",
        },
        "sample_size_policy": {
            "min_examples_per_cell": 20,
            "power_target": 0.80,
        },
    }


class TestCritiqueProtocol:
    def test_good_protocol_no_blockers(self):
        result = critique_protocol(_good_protocol())
        assert result["blockers"] == [], f"Unexpected blockers: {result['blockers']}"
        assert result["score"] > 0

    def test_unfrozen_produces_blocker(self):
        p = _good_protocol()
        p["frozen"] = False
        result = critique_protocol(p)
        assert any("frozen" in b.lower() for b in result["blockers"])

    def test_unknown_task_produces_blocker(self):
        p = _good_protocol()
        p["unit_of_work"]["task_id"] = "nonexistent_task"
        result = critique_protocol(p)
        assert any("task_id" in b.lower() or "unknown" in b.lower() for b in result["blockers"])

    def test_single_method_produces_blocker(self):
        p = _good_protocol()
        p["execution_grid"]["methods"] = ["mean_ablation"]
        result = critique_protocol(p)
        assert any("method" in b.lower() for b in result["blockers"])

    def test_weak_settings_produce_warnings(self):
        p = _good_protocol()
        p["execution_grid"]["seeds"] = [1]
        p["execution_grid"]["prompt_variants"] = ["base"]
        p["sample_size_policy"]["min_examples_per_cell"] = 5
        result = critique_protocol(p)
        assert len(result["warnings"]) > 0

    def test_missing_controls_produce_warning(self):
        p = _good_protocol()
        p["control_policy"]["required_families"] = ["wrong_position"]
        result = critique_protocol(p)
        assert any("control" in w.lower() for w in result["warnings"])

    def test_score_is_bounded(self):
        result = critique_protocol(_good_protocol())
        assert 0 <= result["score"] <= 100

    def test_format_report_outputs_markdown(self):
        result = critique_protocol(_good_protocol())
        report = format_critic_report(result)
        assert isinstance(report, str)
        assert "Protocol Critic Report" in report
