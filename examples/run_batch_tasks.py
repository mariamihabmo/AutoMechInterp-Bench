#!/usr/bin/env python3
"""Batch-run mock pipelines across multiple tasks and models.

Usage:
    python run_batch_tasks.py
    python run_batch_tasks.py --models gpt2-small,pythia-70m --tasks ioi_v0,sentiment_v0

No GPU required.
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
from automechinterp_runner.runner import run_stage2, Stage2Config

ALL_TASKS = [
    "ioi_v0", "greater_than_v0", "gendered_pronoun_v0",
    "country_capital_v0", "sentiment_v0", "docstring_v0",
    "fact_recall_v0", "arithmetic_v0",
]


def _make_protocol(task_id: str, model_id: str) -> dict:
    model_info = MODEL_REGISTRY.get(model_id.lower(), {})
    n_layers = model_info.get("n_layers", 12)
    n_heads = model_info.get("n_heads", 12)
    return {
        "protocol_id": f"{task_id}_{model_id}_batch",
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
            "required_families": ["wrong_position", "wrong_layer", "random_component", "mismatched_source"],
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
            "alpha": 0.05, "fdr_q": 0.10, "min_effect_floor": 0.04,
            "multiplicity_method": "benjamini-hochberg",
        },
        "claim_budget": {"max_total_claims": 5, "max_claims_per_task": 5},
        "language_policy": {"forbidden_without_pass": ["solved", "proved", "validated", "confirmed"]},
        "sample_size_policy": {
            "min_examples_per_cell": 20, "exploratory_fraction": 0.3,
            "power_target": 0.80, "minimum_detectable_effect": 0.5,
            "require_confirmatory_split": False, "min_cells_per_hypothesis": 8,
        },
        "intervention_levels": ["head"],
    }


def run_single(task: str, model: str, base_dir: Path) -> dict:
    bundle_dir = base_dir / f"{task}_{model}"
    bundle_dir.mkdir(parents=True, exist_ok=True)

    # Write protocol
    protocol = _make_protocol(task, model)
    (bundle_dir / "protocol.yaml").write_text(yaml.safe_dump(protocol, sort_keys=False))

    # Generate agent output
    generate_agent_output(bundle_dir=bundle_dir, hypothesis_count=3, overwrite=True)

    # Convert to hypothesis.jsonl
    generate_hypotheses_from_agent_output(
        bundle_dir=bundle_dir,
        input_path=bundle_dir / "agent_output.json",
        overwrite=True,
    )

    # Run Stage-2
    config = Stage2Config(bundle_dir=bundle_dir, mode="mock")
    run_stage2(config)

    # Evaluate
    return evaluate_bundle(bundle_dir)


def main():
    parser = argparse.ArgumentParser(description="Batch mock pipeline")
    parser.add_argument("--tasks", default=",".join(ALL_TASKS[:4]), help="Comma-separated task IDs")
    parser.add_argument("--models", default="gpt2-small,pythia-70m", help="Comma-separated model IDs")
    args = parser.parse_args()

    tasks = args.tasks.split(",")
    models = args.models.split(",")
    base_dir = ROOT / "examples" / "output" / "batch"
    base_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*70}")
    print(f"  AutoMechInterp Batch Pipeline")
    print(f"  Tasks: {len(tasks)}  |  Models: {len(models)}  |  Total: {len(tasks)*len(models)}")
    print(f"{'='*70}\n")

    results_table = []
    errors = []

    for task in tasks:
        for model in models:
            try:
                result = run_single(task, model, base_dir)
                overall = result["overall"]
                results_table.append({
                    "task": task, "model": model,
                    "hypotheses": overall["hypothesis_count"],
                    "accepted": overall["accepted_count"],
                    "rejected": overall["rejected_count"],
                    "all_pass": overall["all_pass"],
                    "status": "✅",
                })
                status = "✅ ALL PASS" if overall["all_pass"] else f"❌ {overall['rejected_count']} rejected"
                print(f"  {task:25s} × {model:15s} → {status}")
            except Exception as e:
                errors.append({"task": task, "model": model, "error": str(e)})
                results_table.append({"task": task, "model": model, "status": "💥 ERROR"})
                print(f"  {task:25s} × {model:15s} → 💥 {e}")

    # Summary
    print(f"\n{'='*70}")
    total = len(results_table)
    passed = sum(1 for r in results_table if r.get("all_pass"))
    errored = len(errors)
    print(f"  Total: {total}  |  All-pass: {passed}  |  Errors: {errored}")

    summary_path = base_dir / "batch_summary.json"
    summary_path.write_text(json.dumps(results_table, indent=2))
    print(f"  Summary: {summary_path}")


if __name__ == "__main__":
    main()
