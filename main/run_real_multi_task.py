#!/usr/bin/env python3
"""Run real end-to-end experiments on multiple tasks × models.

This is the core V19 experiment script. For each (task, model) pair:
1. Load the real transformer_lens model
2. Run exploration (activation patching all heads)
3. Generate hypotheses from top-k explored heads
4. Build protocol + bundle
5. Run Stage-2 verification (real interventions)
6. Evaluate with Stage-1 evaluator
7. Generate report

Usage:
    python run_real_multi_task.py --device mps
    python run_real_multi_task.py --device cpu --tasks ioi_v0,greater_than_v0 --models gpt2-small
    python run_real_multi_task.py --device mps --n-examples 30 --top-k 3
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import traceback
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "packages" / "evaluator" / "src"))
sys.path.insert(0, str(ROOT / "packages" / "runner" / "src"))

from automechinterp_evaluator.evaluator import evaluate_bundle
from automechinterp_evaluator.reporting import build_markdown_report
from automechinterp_runner.runner import Stage2Config, run_stage2
from automechinterp_runner.tasks import get_task_module
from automechinterp_runner.models import resolve_model

# Tasks that we can actually run on real models
REAL_TASKS = [
    "ioi_v0",
    "greater_than_v0",
    "gendered_pronoun_v0",
    "country_capital_v0",
    "fact_recall_v0",
    "sentiment_v0",
    "docstring_v0",
    "arithmetic_v0",
]

REAL_MODELS = ["gpt2-small", "pythia-70m"]


def prompt_variants_for_task(task_id: str, count: int = 3) -> list[str]:
    """Return real task-supported prompt variants, keeping base first when present."""
    variants = list(getattr(get_task_module(task_id), "PROMPT_VARIANTS", []) or ["base"])
    ordered = (["base"] if "base" in variants else []) + [v for v in variants if v != "base"]
    return ordered[: max(1, min(count, len(ordered)))]


def make_protocol(task_id: str, model_id: str) -> dict:
    """Build a proper protocol for real experiments."""
    model_info = resolve_model(model_id)
    protocol_timestamp = os.environ.get(
        "AUTOMECHINTERP_PROTOCOL_TIMESTAMP",
        "2026-01-01T00:00:00Z",
    )
    return {
        "protocol_id": f"real_{task_id}_{model_id}",
        "protocol_version": "3.0",
        "frozen": True,
        "unit_of_work": {
            "task_id": task_id,
            "model_id": model_id,
            "model_spec": {
                "n_layers": model_info.n_layers,
                "n_heads": model_info.n_heads,
                "d_model": model_info.d_model,
            },
            "dataset_id": f"{task_id}_templates_v1",
            "metric_id": "logit_diff",
            "clean_corrupt_definition": "swap-target-entity",
        },
        "execution_grid": {
            "seeds": [42, 123, 77, 999, 314, 2025],
            "prompt_variants": prompt_variants_for_task(task_id, count=3),
            "resample_ids": [0],
            "methods": ["activation_patching", "zero_ablation", "mean_ablation"],
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
            "min_specificity_ratio": 2.0,
            "min_robustness": {"seed": 0.5, "prompt_variant": 0.5, "resample": 0.5},
            "max_method_sensitivity_std": 3.0,
            "require_confirmatory_ci_excludes_zero": True,
            "require_bidirectional": True,
            "min_effect_size_d": 0.3,
            "min_practical_cohens_d": 0.2,
            "baseline_superiority_ratio": 2.0,
            "cross_model_rank_stability_tau": 0.3,
        },
        "statistical_policy": {
            "alpha": 0.05,
            "fdr_q": 0.10,
            "min_effect_floor": 0.02,
            "multiplicity_method": "benjamini-hochberg",
        },
        "claim_budget": {"max_total_claims": 5, "max_claims_per_task": 5},
        "language_policy": {
            "forbidden_without_pass": ["solved", "proved", "validated"],
        },
        "sample_size_policy": {
            "min_examples_per_cell": 10,
            "exploratory_fraction": 0.3,
            "power_target": 0.80,
            "minimum_detectable_effect": 0.3,
            "require_confirmatory_split": True,
            "min_cells_per_hypothesis": 24,
        },
        "intervention_levels": ["head", "mlp"],
        "governance": {
            "protocol_creation_timestamp": protocol_timestamp,
            "exception_expiry_hours": 168,
            "red_team_required": True,
        },
    }


def run_exploration_for_task(model, task_module, n_examples: int = 20):
    """Quick exploration: patch each head, measure denoising effect."""
    import torch

    examples = task_module.sample_examples(
        model=model, n=min(n_examples, 20), seed=42, prompt_variant="base",
    )
    n_layers = int(model.cfg.n_layers)
    n_heads = int(model.cfg.n_heads)

    head_effects = {}
    with torch.no_grad():
        for ex in examples:
            clean_tokens = model.to_tokens(ex.clean_prompt)
            corrupt_tokens = model.to_tokens(ex.corrupt_prompt)
            corrupt_logits = model(corrupt_tokens)
            corrupt_metric = task_module.metric(
                corrupt_logits, ex.target_token, ex.distractor_token,
            )
            _, clean_cache = model.run_with_cache(
                clean_tokens,
                names_filter=lambda n: n.endswith("attn.hook_z"),
            )

            for layer in range(n_layers):
                for head in range(n_heads):
                    hook_name = f"blocks.{layer}.attn.hook_z"

                    def make_hook(sl, sh, cache):
                        def hook_fn(act, hook):
                            src = cache[f"blocks.{sl}.attn.hook_z"]
                            seq = min(act.shape[1], src.shape[1])
                            act[:, :seq, sh, :] = src[:, :seq, sh, :]
                            return act
                        return hook_fn

                    patched_logits = model.run_with_hooks(
                        corrupt_tokens,
                        fwd_hooks=[(hook_name, make_hook(layer, head, clean_cache))],
                    )
                    effect = task_module.metric(
                        patched_logits, ex.target_token, ex.distractor_token,
                    ) - corrupt_metric

                    key = (layer, head)
                    if key not in head_effects:
                        head_effects[key] = []
                    head_effects[key].append(effect)

    ranked = []
    for (layer, head), effects in head_effects.items():
        ranked.append({
            "layer": layer, "head": head,
            "mean_effect": sum(effects) / len(effects),
        })
    ranked.sort(key=lambda x: abs(x["mean_effect"]), reverse=True)
    return ranked


def run_mlp_exploration(model, task_module, n_examples=10):
    """Explore MLP layers by zero-ablating each MLP output."""
    import torch

    examples = task_module.sample_examples(
        model=model, n=min(n_examples, 10), seed=42, prompt_variant="base",
    )
    n_layers = int(model.cfg.n_layers)

    mlp_effects = {}
    with torch.no_grad():
        for ex in examples:
            clean_tokens = model.to_tokens(ex.clean_prompt)
            clean_logits = model(clean_tokens)
            clean_metric = task_module.metric(
                clean_logits, ex.target_token, ex.distractor_token,
            )

            for layer in range(n_layers):
                hook_name = f"blocks.{layer}.hook_mlp_out"

                def make_hook(sl):
                    def hook_fn(act, hook):
                        act[:, -1, :] = 0.0  # Zero-ablate at final position
                        return act
                    return hook_fn

                ablated_logits = model.run_with_hooks(
                    clean_tokens,
                    fwd_hooks=[(hook_name, make_hook(layer))],
                )
                ablated_metric = task_module.metric(
                    ablated_logits, ex.target_token, ex.distractor_token,
                )
                effect = float(clean_metric - ablated_metric)  # Positive = important

                if layer not in mlp_effects:
                    mlp_effects[layer] = []
                mlp_effects[layer].append(effect)

    ranked = []
    for layer, effects in mlp_effects.items():
        ranked.append({
            "layer": layer,
            "mean_effect": sum(effects) / len(effects),
        })
    ranked.sort(key=lambda x: abs(x["mean_effect"]), reverse=True)
    return ranked


def build_real_bundle(
    model, task_module, task_id, model_id, ranked_heads,
    bundle_dir: Path, n_examples: int = 20, top_k: int = 3,
    ranked_mlps=None,
):
    """Write a bundle skeleton and let the packaged Stage-2 runner fill it."""

    protocol = make_protocol(task_id, model_id)
    bundle_dir.mkdir(parents=True, exist_ok=True)
    (bundle_dir / "protocol.yaml").write_text(yaml.safe_dump(protocol, sort_keys=False))

    # Build hypotheses from top explored heads
    hypotheses = []
    for i, h in enumerate(ranked_heads[:top_k]):
        if abs(h["mean_effect"]) < 0.01:
            continue
        direction = "increase" if h["mean_effect"] > 0 else "decrease"
        hypotheses.append({
            "hypothesis_id": f"h_{task_id}_{i+1:03d}",
            "protocol_id": protocol["protocol_id"],
            "task_id": task_id,
            "model_id": model_id,
            "metric_id": "logit_diff",
            "claim_text": f"L{h['layer']}H{h['head']} is causal for {task_id} ({direction})",
            "candidate_components": [{"component_type": "head", "layer": h["layer"], "head": h["head"]}],
            "predicted_effect_direction": direction,
            "predicted_min_effect": 0.02,
            "predicted_specificity_ratio": 2.0,
            "expected_failure_modes": ["distributed_computation"],
        })

    # V18: Also generate MLP hypotheses from top explored MLPs
    if ranked_mlps:
        for j, m in enumerate(ranked_mlps[:1]):  # Top-1 MLP
            if abs(m["mean_effect"]) < 0.01:
                continue
            direction = "decrease"  # MLP ablation typically decreases metric
            idx = len(hypotheses) + 1
            hypotheses.append({
                "hypothesis_id": f"h_{task_id}_mlp_{j+1:03d}",
                "protocol_id": protocol["protocol_id"],
                "task_id": task_id,
                "model_id": model_id,
                "metric_id": "logit_diff",
                "claim_text": f"MLP layer {m['layer']} is causal for {task_id}",
                "candidate_components": [{"component_type": "mlp", "layer": m["layer"]}],
                "predicted_effect_direction": direction,
                "predicted_min_effect": 0.02,
                "predicted_specificity_ratio": 1.5,
                "expected_failure_modes": ["distributed_computation"],
            })

    # Write hypotheses (atomic: write to a sibling .tmp then rename so a
    # crash mid-write never leaves a half-written hypothesis.jsonl that
    # downstream readers would silently truncate; audit-final §2.D.6).
    hyp_path = bundle_dir / "hypothesis.jsonl"
    tmp_path = hyp_path.with_suffix(".jsonl.tmp")
    with open(tmp_path, "w", encoding="utf-8") as f:
        for h in hypotheses:
            f.write(json.dumps(h, sort_keys=True) + "\n")
    tmp_path.replace(hyp_path)

    return bundle_dir


def map_transfer_component(
    comp: dict,
    *,
    source_n_layers: int,
    transfer_n_layers: int,
    transfer_n_heads: int,
    transfer_d_mlp: int | None = None,
) -> dict:
    """Map a source-model component to the proportional transfer-model coordinate."""
    mapped = dict(comp)
    if "layer" in mapped:
        mapped["layer"] = int(comp["layer"]) * transfer_n_layers // source_n_layers
    if mapped.get("component_type") == "head":
        mapped["head"] = min(int(comp["head"]), transfer_n_heads - 1)
    if mapped.get("component_type") == "mlp_neuron" and transfer_d_mlp is not None:
        mapped["neuron"] = min(int(comp["neuron"]), max(0, transfer_d_mlp - 1))
    return mapped


def transfer_intervention_kind(components: list[dict]) -> str:
    """Return the hook family required for a transfer intervention."""
    component_types = {str(comp.get("component_type")) for comp in components}
    if component_types == {"head"}:
        return "head"
    if component_types == {"mlp"}:
        return "mlp"
    if component_types == {"mlp_neuron"}:
        return "mlp_neuron"
    if component_types == {"residual_stream"}:
        return "residual_stream"
    raise ValueError(
        "Unsupported or mixed component types for transfer run: "
        f"{sorted(component_types)}. Add a type-aware transfer implementation "
        "before generating cross_model_results for this bundle."
    )


def transfer_cache_names_filter(components: list[dict]):
    """Build a TransformerLens cache filter matching the component hook family."""
    intervention_kind = transfer_intervention_kind(components)

    def names_filter(name: str) -> bool:
        if intervention_kind == "head":
            return name.endswith("attn.hook_z")
        if intervention_kind in {"mlp", "mlp_neuron"}:
            return name.endswith("mlp.hook_post")
        if intervention_kind == "residual_stream":
            return name.endswith("hook_resid_post")
        return False

    return names_filter


def transfer_contract_metadata(transfer_effect: float, source_effect_mean: float | None) -> dict:
    """Return contract-facing transfer metadata for a per-hypothesis effect."""
    from automechinterp_evaluator.constants import CROSS_MODEL_EFFECT_FLOOR

    transfer_sign = 1 if transfer_effect > 0 else -1
    above_floor = abs(transfer_effect) >= CROSS_MODEL_EFFECT_FLOOR
    same_direction = None
    contract_pass = None
    if source_effect_mean is not None:
        source_sign = 1 if source_effect_mean > 0 else -1
        same_direction = source_sign == transfer_sign
        contract_pass = bool(same_direction and above_floor)
    return {
        "source_effect_mean": source_effect_mean,
        "cross_model_effect_floor": CROSS_MODEL_EFFECT_FLOOR,
        "transfer_above_floor": above_floor,
        "transfer_same_direction": same_direction,
        "transfer_contract_pass": contract_pass,
        # Backward-compatible magnitude flag. The evaluator's gate also requires
        # same-direction evidence, recorded separately above.
        "transfer_positive": above_floor,
    }


def source_effect_means_by_hypothesis(source_bundle_dir: Path) -> dict[str, float]:
    """Read source-model treatment-effect means from the latest evaluation file."""
    for name in ("evaluation_result_current.json", "evaluation_result.json"):
        path = source_bundle_dir / name
        if not path.exists():
            continue
        try:
            payload = json.loads(path.read_text())
        except json.JSONDecodeError:
            continue
        means: dict[str, float] = {}
        for row in payload.get("claim_reports", []):
            metrics = row.get("metrics") or {}
            if "treatment_effect_mean" in metrics:
                means[str(row["hypothesis_id"])] = float(metrics["treatment_effect_mean"])
        if means:
            return means
    return {}


def run_cross_model_transfer(
    source_bundle_dir: Path,
    transfer_model,
    transfer_model_id: str,
    source_model_id: str,
    task_id: str,
    n_examples: int = 10,
):
    """Test hypotheses from source model on a different transfer model.

    Maps head positions via proportional layer mapping:
      transfer_layer = source_layer * transfer_n_layers // source_n_layers

    Returns transfer results dict and writes to cross_model_results.json.
    """
    import torch
    from automechinterp_runner.interventions.node_patching import (
        head_intervention_logits,
        mlp_intervention_logits,
        neuron_intervention_logits,
        residual_stream_intervention_logits,
    )

    task_module = get_task_module(task_id)
    source_info = resolve_model(source_model_id)
    transfer_info = resolve_model(transfer_model_id)

    # Read hypotheses from bundle
    hyp_lines = (source_bundle_dir / "hypothesis.jsonl").read_text().strip().split("\n")
    hypotheses = [json.loads(line) for line in hyp_lines]
    source_effect_means = source_effect_means_by_hypothesis(source_bundle_dir)

    intervention_by_kind = {
        "head": head_intervention_logits,
        "mlp": mlp_intervention_logits,
        "mlp_neuron": neuron_intervention_logits,
        "residual_stream": residual_stream_intervention_logits,
    }

    transfer_results = []
    for hyp in hypotheses:
        # Map components from source to transfer model
        mapped_components = [
            map_transfer_component(
                comp,
                source_n_layers=source_info.n_layers,
                transfer_n_layers=transfer_info.n_layers,
                transfer_n_heads=transfer_info.n_heads,
                transfer_d_mlp=int(getattr(transfer_model.cfg, "d_mlp", 0)) or None,
            )
            for comp in hyp["candidate_components"]
        ]
        intervention_logits = intervention_by_kind[transfer_intervention_kind(mapped_components)]
        names_filter = transfer_cache_names_filter(mapped_components)

        # Run patching on transfer model with mapped components
        examples = task_module.sample_examples(
            model=transfer_model, n=n_examples, seed=42, prompt_variant="base",
        )

        effects = []
        with torch.no_grad():
            for ex in examples:
                clean_tokens = transfer_model.to_tokens(ex.clean_prompt)
                corrupt_tokens = transfer_model.to_tokens(ex.corrupt_prompt)
                corrupt_logits = transfer_model(corrupt_tokens)
                corrupt_metric = task_module.metric(
                    corrupt_logits, ex.target_token, ex.distractor_token,
                )
                _, clean_cache = transfer_model.run_with_cache(
                    clean_tokens,
                    names_filter=names_filter,
                )
                patched_logits = intervention_logits(
                    model=transfer_model,
                    target_tokens=corrupt_tokens,
                    source_cache=clean_cache,
                    components=mapped_components,
                    patch_mode="clean",
                    target_position=-1,
                )
                patched_metric = task_module.metric(
                    patched_logits, ex.target_token, ex.distractor_token,
                )
                effects.append(float(patched_metric - corrupt_metric))

        mean_effect = sum(effects) / len(effects) if effects else 0.0
        source_effect_mean = source_effect_means.get(str(hyp["hypothesis_id"]))
        transfer_results.append({
            "hypothesis_id": hyp["hypothesis_id"],
            "source_model": source_model_id,
            "transfer_model": transfer_model_id,
            "source_components": hyp["candidate_components"],
            "mapped_components": mapped_components,
            "transfer_mapping_version": "type_aware_v1",
            "transfer_intervention_kind": transfer_intervention_kind(mapped_components),
            "transfer_effect": mean_effect,
            "n_examples": len(effects),
            **transfer_contract_metadata(mean_effect, source_effect_mean),
        })

    # Write cross-model results
    cross_path = source_bundle_dir / "cross_model_results.json"
    cross_path.write_text(json.dumps(transfer_results, indent=2))

    return transfer_results


def run_single_experiment(model, task_id, model_id, base_dir, n_examples=20, top_k=3):
    """Run a complete experiment for one (task, model) pair."""
    task_module = get_task_module(task_id)
    bundle_dir = base_dir / f"{task_id}_{model_id}"

    print(f"\n  {'─'*60}")
    print(f"  Task: {task_id}  |  Model: {model_id}")
    print(f"  {'─'*60}")

    # Phase 1: Explore
    t0 = time.time()
    print(f"  [1/5] Exploring heads...")
    ranked = run_exploration_for_task(model, task_module, n_examples=min(n_examples, 10))
    top3_str = ", ".join(
        f"L{h['layer']}H{h['head']}({h['mean_effect']:+.3f})" for h in ranked[:3]
    )
    print(f"    Top 3: {top3_str}")
    print(f"    Time: {time.time()-t0:.1f}s")

    # Phase 1b: Explore MLPs (V18)
    t0b = time.time()
    print(f"  [1b/5] Exploring MLPs...")
    ranked_mlps = run_mlp_exploration(model, task_module, n_examples=min(n_examples, 10))
    top_mlp = ranked_mlps[0] if ranked_mlps else None
    if top_mlp:
        print(f"    Top MLP: L{top_mlp['layer']}({top_mlp['mean_effect']:+.3f})")
    print(f"    Time: {time.time()-t0b:.1f}s")

    # Phase 2: Build bundle with real interventions
    t1 = time.time()
    print(f"  [2/5] Writing bundle + running packaged Stage-2...")
    build_real_bundle(
        model=model, task_module=task_module,
        task_id=task_id, model_id=model_id,
        ranked_heads=ranked, bundle_dir=bundle_dir,
        n_examples=n_examples, top_k=top_k,
        ranked_mlps=ranked_mlps,
    )
    run_stage2(
        Stage2Config(
            bundle_dir=bundle_dir,
            mode="real",
            device=str(getattr(model.cfg, "device", "cpu")),
            examples_per_cell=n_examples,
        )
    )
    print(f"    Time: {time.time()-t1:.1f}s")

    # Phase 3: Evaluate
    t2 = time.time()
    print(f"  [3/5] Evaluating...")
    result = evaluate_bundle(bundle_dir)
    print(f"    Time: {time.time()-t2:.1f}s")

    # Phase 4: Report
    report = build_markdown_report(result)
    report_path = bundle_dir / "stage_gate_report.md"
    report_path.write_text(report)

    # Phase 5: Report results
    overall = result["overall"]
    print(f"  [5/5] Results:")
    print(f"    Hypotheses: {overall['hypothesis_count']}")
    print(f"    Accepted: {overall['accepted_count']}")
    print(f"    Rejected: {overall['rejected_count']}")

    for cr in result["claim_reports"]:
        status = "✅" if cr["passed"] else "❌"
        d = cr["metrics"].get("cohens_d", 0)
        print(f"    {status} {cr['hypothesis_id']}  tier={cr['evidence_tier']}  d={d:.3f}")

    total_time = time.time() - t0
    print(f"  Total time: {total_time:.1f}s")

    return {
        "task": task_id,
        "model": model_id,
        "hypotheses": overall["hypothesis_count"],
        "accepted": overall["accepted_count"],
        "rejected": overall["rejected_count"],
        "tiers": {cr["hypothesis_id"]: cr["evidence_tier"] for cr in result["claim_reports"]},
        "time_seconds": total_time,
    }


def main():
    parser = argparse.ArgumentParser(description="Real multi-task experiment")
    parser.add_argument("--device", default="cpu", choices=["cpu", "mps", "cuda"])
    parser.add_argument("--tasks", default=",".join(REAL_TASKS[:3]),
                        help="Comma-separated task IDs")
    parser.add_argument("--models", default="gpt2-small",
                        help="Comma-separated model IDs")
    parser.add_argument("--n-examples", type=int, default=20)
    parser.add_argument("--top-k", type=int, default=3)
    args = parser.parse_args()

    tasks = args.tasks.split(",")
    models = args.models.split(",")
    base_dir = ROOT / "main" / "output" / "real_multi_task"
    base_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*70}")
    print(f"  AutoMechInterp V19: Real Multi-Task Experiment")
    print(f"  Tasks: {tasks}")
    print(f"  Models: {models}")
    print(f"  Device: {args.device}")
    print(f"  Examples/cell: {args.n_examples}  |  Top-k: {args.top_k}")
    print(f"{'='*70}")

    # Load models once, reuse across tasks
    from transformer_lens import HookedTransformer

    all_results = []
    errors = []

    for model_id in models:
        print(f"\n  Loading {model_id}...")
        t0 = time.time()
        model_info = resolve_model(model_id)
        model = HookedTransformer.from_pretrained(
            model_info.transformer_lens_name, device=args.device,
        )
        print(f"  Loaded in {time.time()-t0:.1f}s")

        for task_id in tasks:
            try:
                result = run_single_experiment(
                    model=model,
                    task_id=task_id,
                    model_id=model_id,
                    base_dir=base_dir,
                    n_examples=args.n_examples,
                    top_k=args.top_k,
                )
                all_results.append(result)
            except Exception as e:
                print(f"  💥 ERROR on {task_id} × {model_id}: {e}")
                traceback.print_exc()
                errors.append({"task": task_id, "model": model_id, "error": str(e)})

        # Free model memory
        del model
        import gc; gc.collect()

    # Summary
    print(f"\n{'='*70}")
    print(f"  EXPERIMENT SUMMARY")
    print(f"{'='*70}")
    print(f"  {'Task':25s} {'Model':15s} {'Hyp':>4s} {'Acc':>4s} {'Rej':>4s} {'Time':>6s}")
    print(f"  {'─'*60}")
    for r in all_results:
        print(f"  {r['task']:25s} {r['model']:15s} {r['hypotheses']:4d} {r['accepted']:4d} {r['rejected']:4d} {r['time_seconds']:5.0f}s")
    if errors:
        print(f"\n  ERRORS: {len(errors)}")
        for e in errors:
            print(f"    {e['task']} × {e['model']}: {e['error'][:60]}")

    # Save summary
    summary_path = base_dir / "experiment_summary.json"
    summary_path.write_text(json.dumps({
        "results": all_results,
        "errors": errors,
        "config": {"tasks": tasks, "models": models, "n_examples": args.n_examples, "top_k": args.top_k},
    }, indent=2))
    print(f"\n  Summary: {summary_path}")
    print(f"  Bundles: {base_dir}")


if __name__ == "__main__":
    main()
