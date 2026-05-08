#!/usr/bin/env python3
"""Map problem catalog entries to runnable AutoMechInterp experiments.

This script connects the 375-problem catalog (problems-to-projects/problems.md)
to our verification pipeline, running real experiments on tractable problems.

Mapping from catalog problems to our 8 task modules:
  - P0033 (gendered pronouns) → gendered_pronoun_v0
  - P0028 (factual recall)    → fact_recall_v0 / country_capital_v0
  - P0039-P0048 (IOI)         → ioi_v0
  - P0024/P0025 (greater-than) → greater_than_v0
  - P0057 (addition)          → arithmetic_v0
  - P0034 (sentiment)         → sentiment_v0

Usage:
    python run_problem_pipeline.py --device mps
    python run_problem_pipeline.py --device cpu --problems P0033,P0028
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


# Mapping: problem_id → (task_id, known_components, description)
PROBLEM_TASK_MAP = {
    "P0033": {
        "task_id": "gendered_pronoun_v0",
        "title": "Choosing the right pronouns (he vs she vs it vs they)",
        "source_id": "AF-2.11",
        "known_components": [
            {"component_type": "head", "layer": 9, "head": 9, "note": "Often involved in name/gender tracking"},
            {"component_type": "head", "layer": 10, "head": 7, "note": "Name mover analogue for pronouns"},
        ],
        "models": ["gpt2-small"],
    },
    "P0028": {
        "task_id": "fact_recall_v0",
        "title": "Interpret factual recall (ROME-style causal tracing)",
        "source_id": "AF-2.6",
        "known_components": [
            {"component_type": "head", "layer": 11, "head": 10, "note": "Late attention heads for entity extraction"},
        ],
        "models": ["gpt2-small"],
    },
    "P0039": {
        "task_id": "ioi_v0",
        "title": "IOI in Stanford Mistral models — does the same circuit arise?",
        "source_id": "AF-2.17",
        "known_components": [
            {"component_type": "head", "layer": 9, "head": 9, "note": "Name mover"},
            {"component_type": "head", "layer": 9, "head": 6, "note": "Name mover"},
            {"component_type": "head", "layer": 10, "head": 0, "note": "Name mover"},
        ],
        "models": ["gpt2-small"],
    },
    "P0025": {
        "task_id": "greater_than_v0",
        "title": "Number comparison (continuing common sequences)",
        "source_id": "AF-2.3",
        "known_components": [],
        "models": ["gpt2-small"],
    },
    "P0057": {
        "task_id": "arithmetic_v0",
        "title": "How does addition work?",
        "source_id": "AF-2.35",
        "known_components": [],
        "models": ["gpt2-small"],
    },
    "P0050": {
        "task_id": "ioi_v0",
        "title": "GPT-2 Small's performance is ruined if you ablate MLP0. Why?",
        "source_id": "AF-2.28",
        "known_components": [
            {"component_type": "mlp", "layer": 0, "note": "MLP0 is critical for GPT-2 Small"},
        ],
        "models": ["gpt2-small"],
    },
}


def run_problem(
    problem_id: str,
    model,
    device: str,
    base_dir: Path,
    n_examples: int = 15,
):
    """Run an experiment for a specific problem from the catalog."""
    from automechinterp_runner.tasks import get_task_module
    import torch

    if problem_id not in PROBLEM_TASK_MAP:
        print(f"  ⚠️  Problem {problem_id} has no task mapping. Skipping.")
        return None

    info = PROBLEM_TASK_MAP[problem_id]
    task_id = info["task_id"]
    print(f"\n  {'─'*60}")
    print(f"  Problem {problem_id}: {info['title'][:60]}")
    print(f"  Source: {info['source_id']}  |  Task: {task_id}")
    print(f"  {'─'*60}")

    task_module = get_task_module(task_id)

    # Exploration: find top heads for this task
    print("  [1/3] Exploring heads...")
    t0 = time.time()

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
                    head_effects.setdefault(key, []).append(float(effect))

    ranked = sorted(
        [{"layer": l, "head": h, "mean_effect": sum(e)/len(e)} for (l, h), e in head_effects.items()],
        key=lambda x: abs(x["mean_effect"]), reverse=True,
    )
    print(f"    Exploration complete in {time.time()-t0:.1f}s")
    top5_str = ", ".join(
        f"L{r['layer']}H{r['head']}({r['mean_effect']:+.3f})" for r in ranked[:5]
    )
    print(f"    Top 5: {top5_str}")

    # Check known components
    print("  [2/3] Checking known components...")
    if info["known_components"]:
        for kc in info["known_components"]:
            if kc["component_type"] == "head":
                key = (kc["layer"], kc["head"])
                rank = next((i for i, r in enumerate(ranked) if (r["layer"], r["head"]) == key), -1)
                effect = head_effects.get(key, [0])
                mean_eff = sum(effect) / len(effect) if effect else 0
                if rank >= 0:
                    print(f"    Known L{kc['layer']}H{kc['head']}: rank={rank+1}/{len(ranked)}, effect={mean_eff:+.4f}")
                    if rank < 10:
                        print(f"      ✅ Found in top-10 by exploration")
                    else:
                        print(f"      ⚠️  Ranked {rank+1} — may not be dominant for this task/prompt variant")
                else:
                    print(f"    Known L{kc['layer']}H{kc['head']}: NOT FOUND (may need different prompt variant)")
    else:
        print("    No known components specified — using exploration results only")

    # Save results
    print("  [3/3] Saving results...")
    output_dir = base_dir / f"{problem_id}_{task_id}"
    output_dir.mkdir(parents=True, exist_ok=True)

    result = {
        "problem_id": problem_id,
        "source_id": info["source_id"],
        "title": info["title"],
        "task_id": task_id,
        "model_id": "gpt2-small",
        "n_examples": n_examples,
        "top_10_heads": ranked[:10],
        "known_component_check": [],
    }

    for kc in info.get("known_components", []):
        if kc.get("component_type") == "head":
            key = (kc["layer"], kc["head"])
            rank = next((i for i, r in enumerate(ranked) if (r["layer"], r["head"]) == key), -1)
            result["known_component_check"].append({
                **kc,
                "exploration_rank": rank + 1 if rank >= 0 else None,
                "in_top_10": rank < 10 if rank >= 0 else False,
            })

    (output_dir / "problem_result.json").write_text(json.dumps(result, indent=2))
    (output_dir / "full_ranking.json").write_text(json.dumps(ranked, indent=2))

    return result


def main():
    parser = argparse.ArgumentParser(description="Problem catalog pipeline")
    parser.add_argument("--device", default="cpu", choices=["cpu", "mps", "cuda"])
    parser.add_argument("--problems", default=",".join(PROBLEM_TASK_MAP.keys()),
                        help="Comma-separated problem IDs")
    parser.add_argument("--n-examples", type=int, default=10)
    args = parser.parse_args()

    problems = args.problems.split(",")

    print(f"\n{'='*70}")
    print(f"  Problem Catalog Pipeline")
    print(f"  Problems: {problems}")
    print(f"  Device: {args.device}")
    print(f"{'='*70}")

    # Load model
    from transformer_lens import HookedTransformer
    from automechinterp_runner.models import resolve_model

    model_info = resolve_model("gpt2-small")
    print(f"\n  Loading {model_info.transformer_lens_name}...")
    t0 = time.time()
    model = HookedTransformer.from_pretrained(model_info.transformer_lens_name, device=args.device)
    print(f"  Loaded in {time.time()-t0:.1f}s")

    base_dir = ROOT / "main" / "output" / "problem_pipeline"
    base_dir.mkdir(parents=True, exist_ok=True)

    all_results = []
    for pid in problems:
        try:
            result = run_problem(pid, model, args.device, base_dir, args.n_examples)
            if result:
                all_results.append(result)
        except Exception as e:
            print(f"  💥 ERROR on {pid}: {e}")
            import traceback; traceback.print_exc()

    # Summary
    print(f"\n{'='*70}")
    print(f"  PROBLEM PIPELINE SUMMARY")
    print(f"{'='*70}")
    print(f"  Problems attempted: {len(problems)}")
    print(f"  Problems completed: {len(all_results)}")

    for r in all_results:
        top = r["top_10_heads"][0]
        print(f"  {r['problem_id']}: {r['task_id']:25s} top=L{top['layer']}H{top['head']}({top['mean_effect']:+.3f})")
        for kc in r.get("known_component_check", []):
            status = "✅" if kc.get("in_top_10") else "❌"
            rank = kc.get("exploration_rank", "N/A")
            print(f"    {status} Known L{kc['layer']}H{kc['head']} rank={rank}")

    summary_path = base_dir / "pipeline_summary.json"
    summary_path.write_text(json.dumps(all_results, indent=2))
    print(f"\n  Summary: {summary_path}")
    print(f"  Output: {base_dir}")


if __name__ == "__main__":
    main()
