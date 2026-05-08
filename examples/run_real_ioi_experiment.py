#!/usr/bin/env python3
"""Real end-to-end experiment: IOI on GPT-2-small with TransformerLens.

Runs on M4 Pro MacBook (CPU/MPS). Generates real evaluation_result.json
with actual causal intervention data, then evaluates through 15 gates.

Usage:
    python run_real_ioi_experiment.py
    python run_real_ioi_experiment.py --device mps --examples-per-cell 10
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "packages" / "evaluator" / "src"))
sys.path.insert(0, str(ROOT / "packages" / "runner" / "src"))

from automechinterp_evaluator.agent_output_generation import generate_agent_output
from automechinterp_evaluator.hypothesis_generation import generate_hypotheses_from_agent_output
from automechinterp_evaluator.evaluator import evaluate_bundle
from automechinterp_evaluator.reporting import build_markdown_report
from automechinterp_runner.runner import run_stage2, Stage2Config


def _make_real_protocol(task_id: str, model_id: str) -> dict:
    """Lean protocol optimized for real GPU/CPU execution."""
    return {
        "protocol_id": f"{task_id}_{model_id}_real_v1",
        "protocol_version": "2.0",
        "frozen": True,
        "unit_of_work": {
            "task_id": task_id,
            "model_id": model_id,
            "model_spec": {"n_layers": 12, "n_heads": 12},
            "dataset_id": f"{task_id}_templates_v1",
            "metric_id": "logit_diff_io_minus_s",
            "clean_corrupt_definition": "swap-indirect-object-entity",
        },
        "execution_grid": {
            "seeds": [101, 202],
            "prompt_variants": ["base", "paraphrase"],
            "resample_ids": [0],
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
            "min_specificity_ratio": 3.0,
            "min_robustness": {"seed": 0.3, "prompt_variant": 0.3, "resample": 0.0},
            "max_method_sensitivity_std": 0.10,
            "require_confirmatory_ci_excludes_zero": True,
            "min_practical_cohens_d": 0.5,
            "baseline_superiority_ratio": 1.5,
        },
        "statistical_policy": {
            "alpha": 0.05,
            "fdr_q": 0.10,
            "min_effect_floor": 0.04,
            "multiplicity_method": "benjamini-hochberg",
        },
        "claim_budget": {"max_total_claims": 5, "max_claims_per_task": 5},
        "language_policy": {"forbidden_without_pass": ["solved", "proved", "validated", "confirmed"]},
        "sample_size_policy": {
            "min_examples_per_cell": 5,
            "exploratory_fraction": 0.3,
            "power_target": 0.70,
            "minimum_detectable_effect": 0.5,
            "require_confirmatory_split": False,
            "min_cells_per_hypothesis": 4,
        },
        "intervention_levels": ["head"],
    }


def main():
    parser = argparse.ArgumentParser(description="Real IOI experiment")
    parser.add_argument("--task", default="ioi_v0")
    parser.add_argument("--model", default="gpt2-small")
    parser.add_argument("--device", default="cpu", help="cpu or mps")
    parser.add_argument("--examples-per-cell", type=int, default=5)
    parser.add_argument("--hypothesis-count", type=int, default=2)
    args = parser.parse_args()

    output_dir = ROOT / "examples" / "output" / f"real_{args.task}_{args.model}"
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"  AutoMechInterp REAL Experiment")
    print(f"  Task: {args.task}  |  Model: {args.model}  |  Device: {args.device}")
    print(f"{'='*60}\n")

    t0 = time.time()

    # Step 1: Write protocol
    print("[1/5] Writing protocol.yaml...")
    protocol = _make_real_protocol(args.task, args.model)
    (output_dir / "protocol.yaml").write_text(yaml.safe_dump(protocol, sort_keys=False))

    # Step 2: Generate agent output
    print("[2/5] Generating agent output (known IOI heads: 9.9, 9.6, 10.7)...")
    # Use the standard pipeline to generate hypotheses
    generate_agent_output(
        bundle_dir=output_dir,
        hypothesis_count=args.hypothesis_count,
        overwrite=True,
    )

    # Step 3: Convert to hypothesis.jsonl
    print("[3/5] Converting to hypothesis.jsonl...")
    generate_hypotheses_from_agent_output(
        bundle_dir=output_dir,
        input_path=output_dir / "agent_output.json",
        overwrite=True,
    )

    # Step 4: Run real Stage-2
    print(f"[4/5] Running Stage-2 REAL mode (device={args.device}, examples_per_cell={args.examples_per_cell})...")
    print("      This will download GPT-2-small (~500MB) on first run...")
    config = Stage2Config(
        bundle_dir=output_dir,
        mode="real",
        device=args.device,
        examples_per_cell=args.examples_per_cell,
    )
    run_stage2(config)
    elapsed = time.time() - t0
    print(f"  → evaluation_result.json written ({elapsed:.1f}s)")

    # Step 5: Run Stage-1 evaluator
    print("[5/5] Running Stage-1 evaluator (15 hard gates)...")
    result = evaluate_bundle(output_dir)

    # Generate report
    report = build_markdown_report(result)
    report_path = output_dir / "stage_gate_report.md"
    report_path.write_text(report)

    # Print summary
    overall = result["overall"]
    total_elapsed = time.time() - t0
    print(f"\n{'='*60}")
    print(f"  REAL EXPERIMENT RESULTS ({total_elapsed:.1f}s total)")
    print(f"{'='*60}")
    print(f"  Hypotheses tested:  {overall['hypothesis_count']}")
    print(f"  Accepted:           {overall['accepted_count']}")
    print(f"  Unstable:           {overall['unstable_count']}")
    print(f"  Rejected:           {overall['rejected_count']}")
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
