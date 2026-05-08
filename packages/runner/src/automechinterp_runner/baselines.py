"""Baseline generators for comparison.

V7: Implements random-circuit baseline and attribution-only baseline
for use in baseline superiority gate.
"""

from __future__ import annotations

import random
from statistics import mean
from typing import Any


def random_circuit_baseline(
    *,
    model: Any,
    task_module: Any,
    n_components: int,
    n_examples: int,
    seed: int,
    prompt_variant: str,
    patch_mode: str = "clean",
) -> dict[str, float]:
    """Run a random-circuit baseline: patch random components and measure effect.

    Returns dict with mean_effect and individual effects.
    """
    from .interventions.node_patching import (
        head_intervention_logits,
        random_head_components,
    )

    rng = random.Random(seed)
    n_layers = int(model.cfg.n_layers)
    n_heads = int(model.cfg.n_heads)

    examples = task_module.sample_examples(
        model=model, n=n_examples, seed=seed, prompt_variant=prompt_variant,
    )

    n_trials = 10
    trial_effects: list[float] = []

    import torch

    for trial in range(n_trials):
        components = random_head_components(
            n_layers=n_layers,
            n_heads=n_heads,
            count=n_components,
            seed=seed + trial * 1000,
        )

        effects: list[float] = []
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

                patched_logits = head_intervention_logits(
                    model=model,
                    target_tokens=corrupt_tokens,
                    source_cache=clean_cache,
                    components=components,
                    patch_mode=patch_mode,
                    target_position=-1,
                )
                effect = task_module.metric(
                    patched_logits, ex.target_token, ex.distractor_token,
                ) - corrupt_metric
                effects.append(effect)

        trial_effects.append(mean(effects))

    return {
        "mean_effect": mean(trial_effects),
        "trial_effects": trial_effects,
        "n_trials": n_trials,
        "n_components": n_components,
    }


def attribution_baseline(
    *,
    model: Any,
    task_module: Any,
    n_examples: int,
    seed: int,
    prompt_variant: str,
    top_k: int = 5,
) -> dict[str, Any]:
    """Run attribution-only baseline: rank heads by attention weight magnitude.

    Selects top-k heads by attention at the final position and reports
    the mean treatment effect when patching those heads.
    NOTE: This is intentionally a WEAK baseline — attributions are not causal.
    """
    from .interventions.node_patching import head_intervention_logits

    examples = task_module.sample_examples(
        model=model, n=min(n_examples, 5), seed=seed, prompt_variant=prompt_variant,
    )

    import torch

    n_layers = int(model.cfg.n_layers)
    n_heads = int(model.cfg.n_heads)

    # Accumulate attention magnitudes
    head_scores: dict[tuple[int, int], float] = {}
    for layer in range(n_layers):
        for head in range(n_heads):
            head_scores[(layer, head)] = 0.0

    with torch.no_grad():
        for ex in examples:
            clean_tokens = model.to_tokens(ex.clean_prompt)
            _, cache = model.run_with_cache(
                clean_tokens,
                names_filter=lambda n: n.endswith("attn.hook_pattern"),
            )
            for layer in range(n_layers):
                pattern = cache[f"blocks.{layer}.attn.hook_pattern"]
                for head in range(n_heads):
                    attn_weight = float(pattern[0, head, -1, :].abs().mean())
                    head_scores[(layer, head)] += attn_weight

    # Select top-k heads
    ranked = sorted(head_scores.items(), key=lambda x: x[1], reverse=True)
    top_components = [
        {"component_type": "head", "layer": layer, "head": head, "selection_source": "attribution"}
        for (layer, head), _ in ranked[:top_k]
    ]

    # Measure their actual causal effect
    effects: list[float] = []
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
            patched_logits = head_intervention_logits(
                model=model,
                target_tokens=corrupt_tokens,
                source_cache=clean_cache,
                components=top_components,
                patch_mode="clean",
                target_position=-1,
            )
            effect = task_module.metric(
                patched_logits, ex.target_token, ex.distractor_token,
            ) - corrupt_metric
            effects.append(effect)

    return {
        "mean_effect": mean(effects) if effects else 0.0,
        "top_components": top_components,
        "n_examples": len(examples),
        "top_k": top_k,
    }
