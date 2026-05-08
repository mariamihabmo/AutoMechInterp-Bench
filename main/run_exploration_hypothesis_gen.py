#!/usr/bin/env python3
"""Hypothesis generation from exploration: real activation patching.

Loads a real transformer_lens model, runs activation patching across all
heads for a given task, identifies top-k heads by intervention effect,
and generates hypotheses with proper schema.

Usage:
    python run_exploration_hypothesis_gen.py --task ioi_v0 --model gpt2-small --device mps
    python run_exploration_hypothesis_gen.py --task greater_than_v0 --model pythia-70m --device cpu
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "packages" / "evaluator" / "src"))
sys.path.insert(0, str(ROOT / "packages" / "runner" / "src"))

from automechinterp_runner.tasks import get_task_module


def explore_heads(
    model,
    task_module,
    n_examples: int = 30,
    seed: int = 42,
    prompt_variant: str = "base",
    device: str = "cpu",
):
    """Run activation patching across all heads to find important ones.

    For each head (L, H), patches clean activations into corrupt run
    and measures recovery (denoising patching). Returns sorted list
    of (layer, head, mean_effect) tuples.
    """
    import torch

    examples = task_module.sample_examples(
        model=model, n=n_examples, seed=seed, prompt_variant=prompt_variant,
    )

    n_layers = int(model.cfg.n_layers)
    n_heads = int(model.cfg.n_heads)

    print(f"  Exploring {n_layers} layers × {n_heads} heads = {n_layers * n_heads} components")
    print(f"  Using {len(examples)} examples, prompt_variant='{prompt_variant}'")

    head_effects: dict[tuple[int, int], list[float]] = {}
    for layer in range(n_layers):
        for head in range(n_heads):
            head_effects[(layer, head)] = []

    t0 = time.time()
    with torch.no_grad():
        for i, ex in enumerate(examples):
            clean_tokens = model.to_tokens(ex.clean_prompt)
            corrupt_tokens = model.to_tokens(ex.corrupt_prompt)

            # Baseline: corrupt logits
            corrupt_logits = model(corrupt_tokens)
            corrupt_metric = task_module.metric(
                corrupt_logits, ex.target_token, ex.distractor_token,
            )

            # Get clean cache
            _, clean_cache = model.run_with_cache(
                clean_tokens,
                names_filter=lambda n: n.endswith("attn.hook_z"),
            )

            # Patch each head individually (denoising: clean → corrupt)
            for layer in range(n_layers):
                for head in range(n_heads):
                    hook_name = f"blocks.{layer}.attn.hook_z"

                    def make_hook(src_layer, src_head, cache):
                        def hook_fn(act, hook):
                            src = cache[f"blocks.{src_layer}.attn.hook_z"]
                            seq = min(act.shape[1], src.shape[1])
                            act[:, :seq, src_head, :] = src[:, :seq, src_head, :]
                            return act
                        return hook_fn

                    patched_logits = model.run_with_hooks(
                        corrupt_tokens,
                        fwd_hooks=[(hook_name, make_hook(layer, head, clean_cache))],
                    )
                    patched_metric = task_module.metric(
                        patched_logits, ex.target_token, ex.distractor_token,
                    )
                    effect = patched_metric - corrupt_metric
                    head_effects[(layer, head)].append(effect)

            if (i + 1) % 5 == 0:
                elapsed = time.time() - t0
                print(f"    Example {i+1}/{len(examples)} ({elapsed:.1f}s)")

    elapsed = time.time() - t0
    print(f"  Exploration complete in {elapsed:.1f}s")

    # Compute mean effects and sort
    results = []
    for (layer, head), effects in head_effects.items():
        mean_effect = sum(effects) / len(effects) if effects else 0.0
        results.append({
            "layer": layer,
            "head": head,
            "mean_effect": mean_effect,
            "n_examples": len(effects),
        })

    results.sort(key=lambda x: abs(x["mean_effect"]), reverse=True)
    return results


def generate_hypotheses_from_exploration(
    ranked_heads: list[dict],
    protocol_id: str,
    task_id: str,
    model_id: str,
    metric_id: str = "logit_diff",
    top_k: int = 5,
    min_effect: float = 0.02,
) -> list[dict]:
    """Convert top-k explored heads into formal hypotheses."""
    hypotheses = []
    for i, head_info in enumerate(ranked_heads[:top_k]):
        if abs(head_info["mean_effect"]) < min_effect:
            continue

        direction = "increase" if head_info["mean_effect"] > 0 else "decrease"
        h_id = f"h_explore_{task_id}_{i+1:03d}"

        hypotheses.append({
            "hypothesis_id": h_id,
            "protocol_id": protocol_id,
            "task_id": task_id,
            "model_id": model_id,
            "metric_id": metric_id,
            "claim_text": (
                f"Head L{head_info['layer']}H{head_info['head']} causally contributes "
                f"to {task_id} via {direction} in {metric_id} "
                f"(exploration mean effect: {head_info['mean_effect']:.4f})"
            ),
            "candidate_components": [{
                "component_type": "head",
                "layer": head_info["layer"],
                "head": head_info["head"],
            }],
            "predicted_effect_direction": direction,
            "predicted_min_effect": min_effect,
            "predicted_specificity_ratio": 5.0,
            "expected_failure_modes": ["distributed_computation", "task_specificity"],
            "provider_id": "exploration_activation_patching",
            "discovery_lane": "A",
            "exploration_evidence": {
                "mean_effect": head_info["mean_effect"],
                "n_examples": head_info["n_examples"],
                "method": "denoising_activation_patching",
            },
        })

    return hypotheses


def main():
    parser = argparse.ArgumentParser(description="Exploration-based hypothesis generation")
    parser.add_argument("--task", default="ioi_v0", help="Task ID")
    parser.add_argument("--model", default="gpt2-small", help="Model ID")
    parser.add_argument("--device", default="cpu", choices=["cpu", "mps", "cuda"])
    parser.add_argument("--n-examples", type=int, default=20, help="Examples for exploration")
    parser.add_argument("--top-k", type=int, default=5, help="Top-k heads to generate hypotheses for")
    parser.add_argument("--output-dir", default=None, help="Output directory")
    args = parser.parse_args()

    from automechinterp_runner.models import resolve_model

    print(f"\n{'='*70}")
    print(f"  Exploration-Based Hypothesis Generation")
    print(f"  Task: {args.task}  |  Model: {args.model}  |  Device: {args.device}")
    print(f"{'='*70}\n")

    # Resolve model info
    model_info = resolve_model(args.model)
    print(f"  Model: {model_info.transformer_lens_name} ({model_info.n_layers}L, {model_info.n_heads}H)")

    # Load real model
    print(f"  Loading model...")
    t0 = time.time()
    from transformer_lens import HookedTransformer
    model = HookedTransformer.from_pretrained(
        model_info.transformer_lens_name,
        device=args.device,
    )
    print(f"  Model loaded in {time.time() - t0:.1f}s\n")

    # Load task
    task_module = get_task_module(args.task)
    print(f"  Task: {args.task}")
    print(f"  Prompt variants: {task_module.PROMPT_VARIANTS}\n")

    # Phase 1: Explore
    print("  Phase 1: Exploration (activation patching all heads)")
    print("  " + "-" * 50)
    ranked_heads = explore_heads(
        model=model,
        task_module=task_module,
        n_examples=args.n_examples,
        device=args.device,
    )

    # Show top heads
    print(f"\n  Top 10 heads by |effect|:")
    for i, h in enumerate(ranked_heads[:10]):
        bar = "█" * int(min(40, abs(h["mean_effect"]) * 20))
        print(f"    {i+1:2d}. L{h['layer']:2d}H{h['head']:2d}  effect={h['mean_effect']:+.4f}  {bar}")

    # Phase 2: Generate hypotheses
    print(f"\n  Phase 2: Generating hypotheses from top-{args.top_k}")
    print("  " + "-" * 50)
    protocol_id = f"explore_{args.task}_{args.model}"
    hypotheses = generate_hypotheses_from_exploration(
        ranked_heads=ranked_heads,
        protocol_id=protocol_id,
        task_id=args.task,
        model_id=args.model,
        top_k=args.top_k,
    )

    for h in hypotheses:
        print(f"    → {h['hypothesis_id']}: {h['claim_text'][:80]}...")

    # Save
    output_dir = Path(args.output_dir) if args.output_dir else ROOT / "main" / "output" / f"explore_{args.task}_{args.model}"
    output_dir.mkdir(parents=True, exist_ok=True)

    (output_dir / "exploration_ranked_heads.json").write_text(
        json.dumps(ranked_heads, indent=2)
    )
    (output_dir / "generated_hypotheses.json").write_text(
        json.dumps(hypotheses, indent=2)
    )

    print(f"\n  Output saved to: {output_dir}")
    print(f"  Ranked heads: {len(ranked_heads)}")
    print(f"  Hypotheses generated: {len(hypotheses)}")

    # Summary
    print(f"\n{'='*70}")
    print(f"  EXPLORATION SUMMARY")
    print(f"{'='*70}")
    print(f"  Task: {args.task}")
    print(f"  Model: {args.model} ({model_info.n_layers}L × {model_info.n_heads}H = {model_info.n_layers * model_info.n_heads} heads)")
    print(f"  Examples used: {args.n_examples}")
    print(f"  Top head: L{ranked_heads[0]['layer']}H{ranked_heads[0]['head']} (effect={ranked_heads[0]['mean_effect']:+.4f})")
    print(f"  Hypotheses generated: {len(hypotheses)}")
    print(f"  Output: {output_dir}")


if __name__ == "__main__":
    main()
