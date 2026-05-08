#!/usr/bin/env python3
"""Full mock pipeline: write protocol → generate hypotheses → mock runner → 15 gates.

Usage:
    python run_full_mock_pipeline.py
    python run_full_mock_pipeline.py --task ioi_v0 --model gpt2-small

No GPU required — all intervention effects are deterministically simulated.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "packages" / "evaluator" / "src"))
sys.path.insert(0, str(ROOT / "packages" / "runner" / "src"))

from automechinterp_evaluator.constants import MODEL_REGISTRY
from automechinterp_evaluator.agent_output_generation import generate_agent_output
from automechinterp_evaluator.hypothesis_generation import generate_hypotheses_from_agent_output
from automechinterp_evaluator.evaluator import evaluate_bundle
from automechinterp_evaluator.reporting import build_markdown_report
from automechinterp_runner.runner import run_stage2, Stage2Config


def _make_protocol(task_id: str, model_id: str) -> dict:
    """Build a minimal valid protocol for the given task/model."""
    model_info = MODEL_REGISTRY.get(model_id.lower(), {})
    n_layers = model_info.get("n_layers", 12)
    n_heads = model_info.get("n_heads", 12)

    return {
        "protocol_id": f"{task_id}_{model_id}_mock_v1",
        "protocol_version": "2.0",
        "frozen": True,
        "unit_of_work": {
            "task_id": task_id,
            "model_id": model_id,
            "model_spec": {"n_layers": n_layers, "n_heads": n_heads},
            "dataset_id": f"{task_id}_templates_v1",
            "metric_id": "logit_diff_io_minus_s",
            "clean_corrupt_definition": "swap-target-entity",
        },
        "execution_grid": {
            "seeds": [101, 202],
            "prompt_variants": ["base", "paraphrase"],
            "resample_ids": [0, 1],
            "methods": ["mean_ablation", "zero_ablation"],
        },
        "control_policy": {
            "required_families": [
                "wrong_position", "wrong_layer",
                "random_component", "mismatched_source",
            ],
            "max_control_abs_mean": 0.03,
        },
        "stage_gates": {
            "min_causal_effect": 0.05,
            "min_specificity_ratio": 5.0,
            "min_robustness": {"seed": 0.5, "prompt_variant": 0.5, "resample": 0.5},
            "max_method_sensitivity_std": 0.03,
            "require_confirmatory_ci_excludes_zero": True,
            "min_practical_cohens_d": 0.5,
            "baseline_superiority_ratio": 2.0,
        },
        "statistical_policy": {
            "alpha": 0.05,
            "fdr_q": 0.10,
            "min_effect_floor": 0.04,
            "multiplicity_method": "benjamini-hochberg",
        },
        "claim_budget": {
            "max_total_claims": 5,
            "max_claims_per_task": 5,
        },
        "language_policy": {
            "forbidden_without_pass": ["solved", "proved", "validated", "confirmed"],
        },
        "sample_size_policy": {
            "min_examples_per_cell": 20,
            "exploratory_fraction": 0.3,
            "power_target": 0.80,
            "minimum_detectable_effect": 0.5,
            "require_confirmatory_split": False,
            "min_cells_per_hypothesis": 8,
        },
        "intervention_levels": ["head"],
    }


def main():
    parser = argparse.ArgumentParser(description="Run full mock pipeline")
    parser.add_argument("--task", default="ioi_v0", help="Task ID")
    parser.add_argument("--model", default="gpt2-small", help="Model ID")
    parser.add_argument("--output-dir", default=None, help="Output directory")
    args = parser.parse_args()

    output_dir = Path(args.output_dir) if args.output_dir else ROOT / "examples" / "output" / f"{args.task}_{args.model}"
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"  AutoMechInterp Full Mock Pipeline")
    print(f"  Task: {args.task}  |  Model: {args.model}")
    print(f"{'='*60}\n")

    # Step 1: Write protocol
    print("[1/4] Writing protocol.yaml...")
    protocol = _make_protocol(args.task, args.model)
    (output_dir / "protocol.yaml").write_text(yaml.safe_dump(protocol, sort_keys=False))

    # Step 2: Generate agent output (exploration)
    print("[2/5] Generating agent output...")
    generate_agent_output(
        bundle_dir=output_dir,
        hypothesis_count=3,
        overwrite=True,
    )
    agent_output_path = output_dir / "agent_output.json"
    print(f"  → agent_output.json written")

    # Step 3: Convert to hypothesis.jsonl
    print("[3/5] Generating hypothesis.jsonl...")
    generate_hypotheses_from_agent_output(
        bundle_dir=output_dir,
        input_path=agent_output_path,
        overwrite=True,
    )
    print(f"  → hypothesis.jsonl written")

    # Step 4: Run Stage-2 mock runner
    print("[4/5] Running Stage-2 mock runner (simulated interventions)...")
    config = Stage2Config(bundle_dir=output_dir, mode="mock")
    run_stage2(config)
    print(f"  → evaluation_result.json written")

    # Step 5: Run Stage-1 evaluator (15 gates)
    print("[5/5] Running Stage-1 evaluator (15 hard gates)...")
    result = evaluate_bundle(output_dir)

    # Generate report
    report = build_markdown_report(result)
    report_path = output_dir / "stage_gate_report.md"
    report_path.write_text(report)

    # Print summary
    overall = result["overall"]
    print(f"\n{'='*60}")
    print(f"  RESULTS")
    print(f"{'='*60}")
    print(f"  Hypotheses tested:  {overall['hypothesis_count']}")
    print(f"  Accepted:           {overall['accepted_count']}")
    print(f"  Unstable:           {overall['unstable_count']}")
    print(f"  Rejected:           {overall['rejected_count']}")
    print(f"  Cross-method τ:     {overall.get('cross_method_rank_tau', 'N/A'):.4f}")
    print()

    for claim in result["claim_reports"]:
        status = "✅ PASS" if claim["passed"] else "❌ FAIL"
        tier = claim["evidence_tier"]
        hid = claim["hypothesis_id"]
        d = claim["metrics"].get("cohens_d", 0)
        print(f"  {status}  {hid}")
        print(f"         tier={tier}  d={d:.3f}")
        if claim["failed_checks"]:
            print(f"         failed: {', '.join(claim['failed_checks'])}")
        print()

    print(f"Report saved to: {report_path}")
    return 0 if overall["all_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
