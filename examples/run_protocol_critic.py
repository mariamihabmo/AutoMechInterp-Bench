#!/usr/bin/env python3
"""Test the protocol critic on various protocol configurations.

Demonstrates how the automated red-teaming catches common protocol weaknesses.

Usage:
    python run_protocol_critic.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "packages" / "evaluator" / "src"))

from automechinterp_evaluator.protocol_critic import critique_protocol, format_critic_report


def main():
    print(f"\n{'='*70}")
    print(f"  Protocol Critic Demonstration")
    print(f"{'='*70}\n")

    # Protocol 1: Well-designed (should score high)
    good_protocol = {
        "protocol_id": "good_001",
        "frozen": True,
        "unit_of_work": {
            "task_id": "ioi_v0",
            "model_id": "gpt2-small",
            "metric_id": "logit_diff",
        },
        "execution_grid": {
            "seeds": [42, 43, 44],
            "prompt_variants": ["standard", "reversed", "distractor", "formal"],
            "resample_ids": [0, 1],
            "methods": ["activation_patching_clean", "zero_ablation"],
        },
        "stage_gates": {
            "min_causal_effect": 0.01,
            "min_specificity_ratio": 5.0,
            "require_bidirectional": True,
            "min_robustness": {"seed": 0.8, "prompt_variant": 0.8, "resample": 0.8},
            "max_method_sensitivity_std": 0.05,
            "require_confirmatory_ci_excludes_zero": True,
            "min_effect_size_d": 0.5,
            "min_practical_cohens_d": 0.3,
            "cross_model_rank_stability_tau": 0.6,
        },
        "statistical_policy": {
            "alpha": 0.05,
            "fdr_q": 0.10,
            "min_effect_floor": 0.005,
            "multiplicity_method": "benjamini-hochberg",
        },
        "sample_size_policy": {
            "min_examples_per_cell": 20,
            "power_target": 0.80,
            "require_confirmatory_split": True,
        },
        "control_policy": {
            "required_families": [
                "wrong_position", "wrong_layer", "random_component",
                "mismatched_source", "shuffled_token", "adjacent_head",
            ],
            "max_control_abs_mean": 0.02,
        },
    }

    # Protocol 2: Underpowered (should warn)
    weak_protocol = {
        "protocol_id": "weak_001",
        "frozen": True,
        "unit_of_work": {
            "task_id": "ioi_v0",
            "model_id": "gpt2-small",
            "metric_id": "logit_diff",
        },
        "execution_grid": {
            "seeds": [42],
            "prompt_variants": ["standard"],
            "resample_ids": [0],
            "methods": ["activation_patching_clean"],
        },
        "stage_gates": {
            "min_causal_effect": 0.0,
            "min_specificity_ratio": 1.0,
            "min_robustness": {"seed": 0.5, "prompt_variant": 0.5, "resample": 0.5},
            "max_method_sensitivity_std": 0.1,
            "require_confirmatory_ci_excludes_zero": False,
        },
        "statistical_policy": {
            "alpha": 0.10,
            "fdr_q": 0.20,
            "min_effect_floor": 0.001,
            "multiplicity_method": "none",
        },
        "sample_size_policy": {
            "min_examples_per_cell": 5,
            "power_target": 0.50,
        },
        "control_policy": {
            "required_families": ["wrong_position", "random_component"],
            "max_control_abs_mean": 0.05,
        },
    }

    # Protocol 3: Not frozen (should block)
    unfrozen_protocol = {
        "protocol_id": "unfrozen_001",
        "frozen": False,
        "unit_of_work": {
            "task_id": "unknown_task",
            "model_id": "gpt2-small",
        },
        "execution_grid": {
            "seeds": [42],
            "prompt_variants": ["standard"],
            "resample_ids": [0],
            "methods": ["patching"],
        },
        "stage_gates": {
            "min_causal_effect": 0.01,
            "min_specificity_ratio": 3.0,
            "min_robustness": {"seed": 0.8, "prompt_variant": 0.8, "resample": 0.8},
            "max_method_sensitivity_std": 0.05,
            "require_confirmatory_ci_excludes_zero": True,
        },
        "statistical_policy": {
            "alpha": 0.05,
            "fdr_q": 0.10,
            "min_effect_floor": 0.005,
        },
        "sample_size_policy": {},
        "control_policy": {
            "required_families": [],
            "max_control_abs_mean": 0.02,
        },
    }

    protocols = [
        ("Well-Designed Protocol", good_protocol),
        ("Underpowered Protocol", weak_protocol),
        ("Unfrozen + Unknown Task", unfrozen_protocol),
    ]

    for name, proto in protocols:
        print(f"\n--- {name} ---\n")
        critique = critique_protocol(proto)
        print(format_critic_report(critique))


if __name__ == "__main__":
    main()
