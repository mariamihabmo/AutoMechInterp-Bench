#!/usr/bin/env python3
"""Real experiment with known IOI circuit heads.

Uses the known name mover heads (9.9, 9.6) and negative name mover (10.7)
from Wang et al. 2022 to demonstrate the pipeline correctly accepts
genuine circuits and rejects random ones.

Usage:
    python run_real_known_circuit.py
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "packages" / "evaluator" / "src"))
sys.path.insert(0, str(ROOT / "packages" / "runner" / "src"))

from automechinterp_evaluator.hypothesis_generation import generate_hypotheses_from_agent_output
from automechinterp_evaluator.evaluator import evaluate_bundle
from automechinterp_evaluator.reporting import build_markdown_report
from automechinterp_runner.runner import run_stage2, Stage2Config


def _make_protocol() -> dict:
    return {
        "protocol_id": "ioi_known_circuit_real_v1",
        "protocol_version": "2.0",
        "frozen": True,
        "unit_of_work": {
            "task_id": "ioi_v0",
            "model_id": "gpt2-small",
            "model_spec": {"n_layers": 12, "n_heads": 12},
            "dataset_id": "ioi_templates_v1",
            "metric_id": "logit_diff_io_minus_s",
            "clean_corrupt_definition": "swap-indirect-object-entity",
        },
        "execution_grid": {
            "seeds": [101, 202],
            "prompt_variants": ["base", "paraphrase"],
            "resample_ids": [0],
            "methods": ["activation_patching", "zero_ablation"],
        },
        "control_policy": {
            "required_families": [
                "wrong_position", "wrong_layer",
                "random_component", "mismatched_source",
            ],
            "max_control_abs_mean": 0.5,
        },
        "stage_gates": {
            "min_causal_effect": 0.02,
            "min_specificity_ratio": 1.5,
            "min_robustness": {"seed": 0.3, "prompt_variant": 0.3, "resample": 0.0},
            "max_method_sensitivity_std": 0.5,
            "require_confirmatory_ci_excludes_zero": True,
            "min_practical_cohens_d": 0.3,
            "baseline_superiority_ratio": 1.0,
        },
        "statistical_policy": {
            "alpha": 0.05,
            "fdr_q": 0.10,
            "min_effect_floor": 0.02,
            "multiplicity_method": "benjamini-hochberg",
        },
        "claim_budget": {"max_total_claims": 5, "max_claims_per_task": 5},
        "language_policy": {"forbidden_without_pass": ["solved", "proved"]},
        "sample_size_policy": {
            "min_examples_per_cell": 5,
            "exploratory_fraction": 0.3,
            "power_target": 0.60,
            "minimum_detectable_effect": 0.3,
            "require_confirmatory_split": False,
            "min_cells_per_hypothesis": 4,
        },
        "intervention_levels": ["head"],
    }


def _make_hypotheses() -> list[dict]:
    """Create hypotheses for known IOI circuit components."""
    return [
        {
            "hypothesis_id": "h_ioi_name_movers",
            "protocol_id": "ioi_known_circuit_real_v1",
            "task_id": "ioi_v0",
            "model_id": "gpt2-small",
            "metric_id": "logit_diff_io_minus_s",
            "claim_text": "Name mover heads (L9H9, L9H6) causally contribute to IOI logit difference",
            "candidate_components": [
                {"component_type": "head", "layer": 9, "head": 9, "site": "z", "patch_mode": "clean"},
                {"component_type": "head", "layer": 9, "head": 6, "site": "z", "patch_mode": "clean"},
            ],
            "predicted_effect_direction": "increase",
            "predicted_min_effect": 0.05,
            "predicted_specificity_ratio": 2.0,
            "expected_failure_modes": ["distributed_computation", "compensatory_mechanism"],
        },
        {
            "hypothesis_id": "h_ioi_random_baseline",
            "protocol_id": "ioi_known_circuit_real_v1",
            "task_id": "ioi_v0",
            "model_id": "gpt2-small",
            "metric_id": "logit_diff_io_minus_s",
            "claim_text": "Random heads (L2H3, L4H1) do NOT causally contribute to IOI",
            "candidate_components": [
                {"component_type": "head", "layer": 2, "head": 3, "site": "z", "patch_mode": "clean"},
                {"component_type": "head", "layer": 4, "head": 1, "site": "z", "patch_mode": "clean"},
            ],
            "predicted_effect_direction": "increase",
            "predicted_min_effect": 0.05,
            "predicted_specificity_ratio": 2.0,
            "expected_failure_modes": ["false_positive"],
        },
    ]


def main():
    output_dir = ROOT / "examples" / "output" / "real_known_circuit"
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"  AutoMechInterp REAL Known Circuit Experiment")
    print(f"  Task: IOI  |  Model: GPT-2-small  |  Device: cpu")
    print(f"  H1: Name movers (L9H9, L9H6) — expected PASS")
    print(f"  H2: Random heads (L2H3, L4H1) — expected FAIL")
    print(f"{'='*60}\n")

    t0 = time.time()

    # Write protocol
    print("[1/4] Writing protocol.yaml...")
    protocol = _make_protocol()
    (output_dir / "protocol.yaml").write_text(yaml.safe_dump(protocol, sort_keys=False))

    # Write hand-crafted hypotheses directly as agent output
    print("[2/4] Writing known-circuit hypotheses...")
    hypotheses = _make_hypotheses()
    agent_output = {"hypotheses": hypotheses}
    (output_dir / "agent_output.json").write_text(json.dumps(agent_output, indent=2))

    generate_hypotheses_from_agent_output(
        bundle_dir=output_dir,
        input_path=output_dir / "agent_output.json",
        overwrite=True,
    )

    # Real Stage-2
    print("[3/4] Running Stage-2 REAL mode...")
    config = Stage2Config(bundle_dir=output_dir, mode="real", device="cpu", examples_per_cell=5)
    run_stage2(config)
    elapsed = time.time() - t0
    print(f"  → evaluation_result.json written ({elapsed:.1f}s)")

    # Stage-1 evaluation
    print("[4/4] Running Stage-1 evaluator (15 hard gates)...")
    result = evaluate_bundle(output_dir)

    report = build_markdown_report(result)
    report_path = output_dir / "stage_gate_report.md"
    report_path.write_text(report)

    # Print results
    overall = result["overall"]
    total_elapsed = time.time() - t0
    print(f"\n{'='*60}")
    print(f"  RESULTS ({total_elapsed:.1f}s)")
    print(f"{'='*60}")

    for claim in result["claim_reports"]:
        status = "✅ PASS" if claim["passed"] else "❌ FAIL"
        tier = claim["evidence_tier"]
        hid = claim["hypothesis_id"]
        d = claim["metrics"].get("cohens_d", 0)
        effect = claim["metrics"].get("mean_treatment_effect", 0)
        print(f"  {status}  {hid}")
        print(f"         tier={tier}  d={d:.3f}  effect={effect:.4f}")
        if claim["failed_checks"]:
            print(f"         failed: {', '.join(claim['failed_checks'])}")
        print()

    print(f"Report: {report_path}")


if __name__ == "__main__":
    main()
