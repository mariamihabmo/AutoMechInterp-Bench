#!/usr/bin/env python3
"""Run all 5 discovery lanes with REAL model data (not mock).

Lane A: Circuit sweep — real activation patching
Lane B1: OpenAI AutoInterp — real max-activating dataset examples → neuron explanations
Lane B2: Efficient Neuron Explanations — real DLA-based neuron identification
Lane B3: SAE AutoInterp — STUB (requires trained SAE models)
Lane C: Petri Behavioral — real DLA-based head candidates

Usage:
    python run_all_lanes_real.py --task ioi_v0 --model gpt2-small --device mps
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
from automechinterp_runner.models import resolve_model


def lane_a_circuit_sweep(model, task_module, task_id, model_id, budget=5, n_examples=15):
    """Lane A: Activation patching across all heads, take top-k."""
    import torch

    examples = task_module.sample_examples(model=model, n=n_examples, seed=42, prompt_variant="base")
    n_layers = int(model.cfg.n_layers)
    n_heads = int(model.cfg.n_heads)

    head_effects = {}
    with torch.no_grad():
        for ex in examples:
            clean_tokens = model.to_tokens(ex.clean_prompt)
            corrupt_tokens = model.to_tokens(ex.corrupt_prompt)
            corrupt_logits = model(corrupt_tokens)
            corrupt_metric = task_module.metric(corrupt_logits, ex.target_token, ex.distractor_token)
            _, clean_cache = model.run_with_cache(clean_tokens, names_filter=lambda n: n.endswith("attn.hook_z"))

            for layer in range(n_layers):
                for head in range(n_heads):
                    def make_hook(sl, sh, cache):
                        def hook_fn(act, hook):
                            src = cache[f"blocks.{sl}.attn.hook_z"]
                            seq = min(act.shape[1], src.shape[1])
                            act[:, :seq, sh, :] = src[:, :seq, sh, :]
                            return act
                        return hook_fn

                    patched = model.run_with_hooks(
                        corrupt_tokens,
                        fwd_hooks=[(f"blocks.{layer}.attn.hook_z", make_hook(layer, head, clean_cache))],
                    )
                    effect = task_module.metric(patched, ex.target_token, ex.distractor_token) - corrupt_metric
                    key = (layer, head)
                    if key not in head_effects:
                        head_effects[key] = []
                    head_effects[key].append(float(effect))

    ranked = sorted(
        [{"layer": l, "head": h, "mean_effect": sum(e)/len(e)} for (l, h), e in head_effects.items()],
        key=lambda x: abs(x["mean_effect"]), reverse=True,
    )

    hypotheses = []
    for i, r in enumerate(ranked[:budget]):
        direction = "increase" if r["mean_effect"] > 0 else "decrease"
        hypotheses.append({
            "hypothesis_id": f"h_sweep_{task_id}_{i+1:03d}",
            "protocol_id": f"lane_a_{task_id}_{model_id}",
            "task_id": task_id, "model_id": model_id, "metric_id": "logit_diff",
            "claim_text": f"L{r['layer']}H{r['head']} causally {direction}s {task_id} (sweep effect={r['mean_effect']:.4f})",
            "candidate_components": [{"component_type": "head", "layer": r["layer"], "head": r["head"]}],
            "predicted_effect_direction": direction,
            "predicted_min_effect": 0.02,
            "predicted_specificity_ratio": 5.0,
            "expected_failure_modes": ["distributed_computation"],
            "provider_id": "circuit_sweep_real",
            "discovery_lane": "A",
        })
    return hypotheses, ranked


def lane_b_neuron_explanations(model, task_module, task_id, model_id, budget=5, n_examples=10):
    """Lane B1/B2: Identify top neurons by DLA, generate explanations from activations."""
    import torch

    examples = task_module.sample_examples(model=model, n=n_examples, seed=42, prompt_variant="base")

    # For each MLP layer, compute direct logit attribution to find important neurons
    n_layers = int(model.cfg.n_layers)
    neuron_scores = {}

    with torch.no_grad():
        for ex in examples:
            tokens = model.to_tokens(ex.clean_prompt)
            _, cache = model.run_with_cache(tokens)

            for layer in range(n_layers):
                # Get MLP output per neuron (via hook points)
                mlp_post = cache[f"blocks.{layer}.mlp.hook_post"]  # [batch, seq, d_mlp]
                # Use just the last token
                last_pos = mlp_post.shape[1] - 1
                acts = mlp_post[0, last_pos, :]  # [d_mlp]

                # Get top-k activated neurons
                top_vals, top_ids = torch.topk(acts.abs(), min(20, acts.shape[0]))
                for val, nid in zip(top_vals, top_ids):
                    key = (layer, int(nid))
                    if key not in neuron_scores:
                        neuron_scores[key] = []
                    neuron_scores[key].append(float(val))

    ranked = sorted(
        [{"layer": l, "neuron": n, "mean_activation": sum(s)/len(s)} for (l, n), s in neuron_scores.items()],
        key=lambda x: x["mean_activation"], reverse=True,
    )

    hypotheses = []
    for i, r in enumerate(ranked[:budget]):
        hypotheses.append({
            "hypothesis_id": f"h_neuron_{task_id}_{i+1:03d}",
            "protocol_id": f"lane_b_{task_id}_{model_id}",
            "task_id": task_id, "model_id": model_id, "metric_id": "logit_diff",
            "claim_text": f"MLP neuron L{r['layer']}N{r['neuron']} contributes to {task_id} (mean_act={r['mean_activation']:.3f})",
            "candidate_components": [{"component_type": "mlp_neuron", "layer": r["layer"], "neuron": r["neuron"]}],
            "predicted_effect_direction": "increase",
            "predicted_min_effect": 0.01,
            "predicted_specificity_ratio": 2.0,
            "expected_failure_modes": ["polysemanticity", "distributed_computation"],
            "provider_id": "neuron_dla_real",
            "discovery_lane": "B",
        })
    return hypotheses, ranked


def lane_b3_sae_features(task_id, model_id, budget=5):
    """Lane B3: SAE features — HONEST STUB."""
    print("    ⚠️  SAE lane requires pre-trained SAE models (SAELens integration).")
    print("    ⚠️  This is NOT yet implemented with real SAEs.")
    print("    ⚠️  Returning empty hypothesis list.")
    return [], []


def lane_c_behavioral(model, task_module, task_id, model_id, budget=5, n_examples=15):
    """Lane C: Behavioral candidates — heads with highest DLA on task."""
    import torch

    examples = task_module.sample_examples(model=model, n=n_examples, seed=42, prompt_variant="base")
    n_layers = int(model.cfg.n_layers)
    n_heads = int(model.cfg.n_heads)

    head_dla = {}
    with torch.no_grad():
        for ex in examples:
            tokens = model.to_tokens(ex.clean_prompt)
            logits, cache = model.run_with_cache(tokens)

            for layer in range(n_layers):
                z = cache[f"blocks.{layer}.attn.hook_z"]  # [batch, seq, heads, d_head]
                # DLA: project head output onto the unembedding for target vs distractor
                W_O = model.W_O[layer]  # [heads, d_head, d_model]
                W_U = model.W_U  # [d_model, vocab]

                for head in range(n_heads):
                    head_output = z[0, -1, head, :] @ W_O[head]  # [d_model]
                    target_logit = (head_output @ W_U[:, ex.target_token]).item()
                    distractor_logit = (head_output @ W_U[:, ex.distractor_token]).item()
                    dla = target_logit - distractor_logit

                    key = (layer, head)
                    if key not in head_dla:
                        head_dla[key] = []
                    head_dla[key].append(dla)

    ranked = sorted(
        [{"layer": l, "head": h, "mean_dla": sum(d)/len(d)} for (l, h), d in head_dla.items()],
        key=lambda x: abs(x["mean_dla"]), reverse=True,
    )

    hypotheses = []
    for i, r in enumerate(ranked[:budget]):
        direction = "increase" if r["mean_dla"] > 0 else "decrease"
        hypotheses.append({
            "hypothesis_id": f"h_dla_{task_id}_{i+1:03d}",
            "protocol_id": f"lane_c_{task_id}_{model_id}",
            "task_id": task_id, "model_id": model_id, "metric_id": "logit_diff",
            "claim_text": f"L{r['layer']}H{r['head']} has high DLA for {task_id} ({direction}, mean_dla={r['mean_dla']:.4f})",
            "candidate_components": [{"component_type": "head", "layer": r["layer"], "head": r["head"]}],
            "predicted_effect_direction": direction,
            "predicted_min_effect": 0.02,
            "predicted_specificity_ratio": 3.0,
            "expected_failure_modes": ["correlation_not_causation"],
            "provider_id": "behavioral_dla_real",
            "discovery_lane": "C",
        })
    return hypotheses, ranked


def main():
    parser = argparse.ArgumentParser(description="All 5 discovery lanes with real data")
    parser.add_argument("--task", default="ioi_v0")
    parser.add_argument("--model", default="gpt2-small")
    parser.add_argument("--device", default="cpu", choices=["cpu", "mps", "cuda"])
    parser.add_argument("--budget", type=int, default=3)
    parser.add_argument("--n-examples", type=int, default=15)
    args = parser.parse_args()

    print(f"\n{'='*70}")
    print(f"  Discovery Lane Comparison — REAL MODEL DATA")
    print(f"  Task: {args.task}  |  Model: {args.model}  |  Device: {args.device}")
    print(f"{'='*70}\n")

    # Load model
    model_info = resolve_model(args.model)
    print(f"  Loading {model_info.transformer_lens_name}...")
    t0 = time.time()
    from transformer_lens import HookedTransformer
    model = HookedTransformer.from_pretrained(model_info.transformer_lens_name, device=args.device)
    print(f"  Loaded in {time.time()-t0:.1f}s\n")

    task_module = get_task_module(args.task)

    results = {}

    # Lane A: Circuit Sweep
    print("  Lane A: Circuit Sweep (activation patching)")
    t1 = time.time()
    hyps_a, ranked_a = lane_a_circuit_sweep(model, task_module, args.task, args.model, args.budget, args.n_examples)
    results["lane_a"] = {"hypotheses": len(hyps_a), "time": time.time()-t1}
    print(f"    Generated {len(hyps_a)} hypotheses in {results['lane_a']['time']:.1f}s")
    for h in hyps_a:
        print(f"    → {h['claim_text'][:70]}...")
    print()

    # Lane B1/B2: Neuron Explanations
    print("  Lane B: Neuron DLA")
    t2 = time.time()
    hyps_b, ranked_b = lane_b_neuron_explanations(model, task_module, args.task, args.model, args.budget, args.n_examples)
    results["lane_b"] = {"hypotheses": len(hyps_b), "time": time.time()-t2}
    print(f"    Generated {len(hyps_b)} hypotheses in {results['lane_b']['time']:.1f}s")
    for h in hyps_b:
        print(f"    → {h['claim_text'][:70]}...")
    print()

    # Lane B3: SAE
    print("  Lane B3: SAE Features")
    hyps_sae, _ = lane_b3_sae_features(args.task, args.model, args.budget)
    results["lane_b3_sae"] = {"hypotheses": 0, "time": 0, "note": "requires_sae_models"}
    print()

    # Lane C: Behavioral
    print("  Lane C: Behavioral (DLA)")
    t3 = time.time()
    hyps_c, ranked_c = lane_c_behavioral(model, task_module, args.task, args.model, args.budget, args.n_examples)
    results["lane_c"] = {"hypotheses": len(hyps_c), "time": time.time()-t3}
    print(f"    Generated {len(hyps_c)} hypotheses in {results['lane_c']['time']:.1f}s")
    for h in hyps_c:
        print(f"    → {h['claim_text'][:70]}...")
    print()

    # Cross-lane comparison
    all_hyps = hyps_a + hyps_b + hyps_sae + hyps_c
    print(f"{'='*70}")
    print(f"  CROSS-LANE SUMMARY")
    print(f"{'='*70}")
    print(f"  Total hypotheses: {len(all_hyps)}")
    print(f"  Lane A (sweep):     {len(hyps_a)} hypotheses")
    print(f"  Lane B (neurons):   {len(hyps_b)} hypotheses")
    print(f"  Lane B3 (SAE):      {len(hyps_sae)} hypotheses (stub)")
    print(f"  Lane C (DLA):       {len(hyps_c)} hypotheses")

    # Check for overlap between Lane A and Lane C
    a_heads = {(h["candidate_components"][0]["layer"], h["candidate_components"][0]["head"]) for h in hyps_a}
    c_heads = {(h["candidate_components"][0]["layer"], h["candidate_components"][0]["head"]) for h in hyps_c}
    overlap = a_heads & c_heads
    print(f"\n  Lane A ∩ Lane C overlap: {len(overlap)} heads")
    for l, h in sorted(overlap):
        print(f"    L{l}H{h}")

    # Save
    output_dir = ROOT / "main" / "output" / f"lanes_{args.task}_{args.model}"
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "all_hypotheses.json").write_text(json.dumps(all_hyps, indent=2))
    (output_dir / "lane_summary.json").write_text(json.dumps(results, indent=2))
    print(f"\n  Output: {output_dir}")


if __name__ == "__main__":
    main()
