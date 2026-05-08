"""Dedicated tests for the reporting module.

Tests build_markdown_report output structure, content, and edge cases.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "packages" / "evaluator" / "src"))

from automechinterp_evaluator.reporting import build_markdown_report


def _mock_result() -> dict:
    return {
        "protocol_id": "test_report_v1",
        "protocol_hash": "abc123def456",
        "overall": {
            "hypothesis_count": 3,
            "accepted_count": 2,
            "unstable_count": 0,
            "rejected_count": 1,
            "all_pass": False,
            "cross_method_rank_tau": 0.8,
            "cross_model_rank_tau": 0.6,
        },
        "claim_reports": [
            {
                "hypothesis_id": "h_001",
                "passed": True,
                "evidence_tier": "single_model_confirmed",
                "failed_checks": [],
                "gate_outcomes": {
                    "causal_effect": "pass",
                    "negative_controls": "pass",
                    "cross_model_transfer": "not_evaluated",
                },
                "metrics": {
                    "cohens_d": 2.5,
                    "specificity_ratio": 10.0,
                    "q_value": 0.01,
                    "treatment_effect_mean": 0.15,
                    "confirmatory_ci_low": 0.05,
                    "confirmatory_ci_high": 0.25,
                    "control_abs_mean": 0.01,
                    "seed_consistency": 0.9,
                    "prompt_variant_consistency": 0.85,
                    "resample_consistency": 0.8,
                    "method_sensitivity_std": 0.02,
                    "p_value_permutation": 0.001,
                    "holm_adjusted_p": 0.003,
                    "n_cells": 24,
                    "compensation_warning": False,
                },
            },
            {
                "hypothesis_id": "h_002",
                "passed": True,
                "evidence_tier": "cross_model_confirmed",
                "failed_checks": [],
                "gate_outcomes": {
                    "causal_effect": "pass",
                    "negative_controls": "pass",
                    "cross_model_transfer": "pass",
                },
                "metrics": {
                    "cohens_d": 3.0,
                    "specificity_ratio": 15.0,
                    "q_value": 0.005,
                    "treatment_effect_mean": 0.20,
                    "confirmatory_ci_low": 0.10,
                    "confirmatory_ci_high": 0.30,
                    "control_abs_mean": 0.005,
                    "seed_consistency": 0.95,
                    "prompt_variant_consistency": 0.90,
                    "resample_consistency": 0.88,
                    "method_sensitivity_std": 0.01,
                    "p_value_permutation": 0.0005,
                    "holm_adjusted_p": 0.001,
                    "n_cells": 24,
                    "compensation_warning": False,
                },
            },
            {
                "hypothesis_id": "h_003",
                "passed": False,
                "evidence_tier": "rejected",
                "failed_checks": ["causal_effect", "negative_controls"],
                "gate_outcomes": {
                    "causal_effect": "fail",
                    "negative_controls": "fail",
                    "cross_model_transfer": "not_evaluated",
                },
                "metrics": {
                    "cohens_d": 0.1,
                    "specificity_ratio": 1.0,
                    "q_value": 0.50,
                    "treatment_effect_mean": 0.005,
                    "confirmatory_ci_low": -0.01,
                    "confirmatory_ci_high": 0.02,
                    "control_abs_mean": 0.005,
                    "seed_consistency": 0.3,
                    "prompt_variant_consistency": 0.2,
                    "resample_consistency": 0.1,
                    "method_sensitivity_std": 0.05,
                    "p_value_permutation": 0.45,
                    "holm_adjusted_p": 0.80,
                    "n_cells": 24,
                    "compensation_warning": True,
                },
            },
        ],
    }


class TestBuildMarkdownReport:
    def test_report_is_string(self):
        report = build_markdown_report(_mock_result())
        assert isinstance(report, str)

    def test_has_header(self):
        report = build_markdown_report(_mock_result())
        assert "Stage-Gate Report" in report

    def test_has_protocol_info(self):
        report = build_markdown_report(_mock_result())
        assert "test_report_v1" in report
        assert "abc123def456" in report

    def test_has_summary_stats(self):
        report = build_markdown_report(_mock_result())
        assert "Hypotheses: 3" in report
        assert "Accepted: 2" in report
        assert "Rejected: 1" in report

    def test_has_summary_table(self):
        report = build_markdown_report(_mock_result())
        assert "Summary Table" in report
        assert "h_001" in report
        assert "h_002" in report
        assert "h_003" in report
        assert "✅ PASS" in report
        assert "❌ FAIL" in report

    def test_has_failure_analysis(self):
        report = build_markdown_report(_mock_result())
        assert "Failure Analysis" in report
        assert "causal_effect" in report

    def test_has_evidence_tiers(self):
        report = build_markdown_report(_mock_result())
        assert "Evidence Tier Breakdown" in report
        assert "single_model_confirmed" in report
        assert "cross_model_confirmed" in report
        assert "rejected" in report

    def test_has_per_hypothesis_details(self):
        report = build_markdown_report(_mock_result())
        assert "Per-Hypothesis Details" in report
        assert "Treatment mean:" in report
        assert "Cohen's d:" in report
        assert "Confirmatory CI" in report

    def test_has_compensation_warning(self):
        report = build_markdown_report(_mock_result())
        assert "Compensation warning" in report

    def test_has_gate_outcomes(self):
        report = build_markdown_report(_mock_result())
        assert "Gate outcomes:" in report
        assert "cross_model_transfer=not_evaluated" in report

    def test_has_cross_method_tau(self):
        report = build_markdown_report(_mock_result())
        assert "Cross-method rank τ" in report

    def test_has_cross_model_tau(self):
        report = build_markdown_report(_mock_result())
        assert "Cross-model rank τ" in report
