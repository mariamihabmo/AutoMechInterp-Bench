"""Lane B2: Efficient-LLM automated interpretability adapter.

Adapter for the Trustworthy-ML-Lab prompt-tuned neuron explanation
pipeline.  Same contract as the OpenAI provider, but additionally
tracks ``prompt_id`` and ``prompt_family`` so you can answer the
question: *does prompt tuning improve explanation quality AND causal
validity under hard gates?*
"""

from __future__ import annotations

from typing import Any

from . import HypothesisProvider, register_provider


@register_provider
class EfficientNeuronExplanationsProvider(HypothesisProvider):
    """Adapter for Trustworthy-ML-Lab prompt-tuned neuron explanations.

    Wraps the same neuron-explanation schema as Lane B1 but adds
    prompt-engineering metadata for ablation studies on explanation
    quality vs causal validity.
    """

    name = "efficient_neuron_explanations"
    version = "0.1.0"

    def __init__(
        self,
        *,
        explanations: list[dict[str, Any]] | None = None,
    ) -> None:
        self.explanations = explanations or []

    def propose(
        self,
        protocol: dict[str, Any],
        budget: int,
    ) -> list[dict[str, Any]]:
        uow = protocol["unit_of_work"]
        model_id = uow["model_id"]

        hypotheses: list[dict[str, Any]] = []
        for i, expl in enumerate(self.explanations[:budget]):
            layer = expl.get("layer", 0)
            neuron = expl.get("neuron", 0)
            explanation = expl.get("explanation_text", "")
            sim_score = expl.get("simulation_score", None)
            prompt_id = expl.get("prompt_id", "default")
            prompt_family = expl.get("prompt_family", "baseline")

            hyp: dict[str, Any] = {
                "hypothesis_id": f"eff_neuron_L{layer}N{neuron}_{prompt_id}_{i}",
                "protocol_id": protocol["protocol_id"],
                "task_id": uow["task_id"],
                "model_id": model_id,
                "metric_id": uow["metric_id"],
                "claim_text": (
                    f"MLP neuron L{layer}N{neuron} causally contributes to "
                    f"{uow['task_id']} (prompt_family={prompt_family})"
                ),
                "candidate_components": [
                    {
                        "component_type": "mlp_neuron",
                        "layer": layer,
                        "neuron": neuron,
                        "site": "mlp_post",
                    }
                ],
                "predicted_effect_direction": "increase",
                "predicted_min_effect": 0.02,
                "predicted_specificity_ratio": 2.0,
                "expected_failure_modes": [
                    "prompt-tuned explanation may overfit surface pattern",
                    "causal importance may not track explanation quality",
                ],
                "intervention_level": "mlp_neuron",
                "explanation_text": explanation,
                "prompt_family": prompt_family,
                "discovery_lane": self.name,
            }
            if sim_score is not None:
                hyp["simulation_score"] = float(sim_score)

            hypotheses.append(hyp)

        return self.tag_hypotheses(hypotheses)
