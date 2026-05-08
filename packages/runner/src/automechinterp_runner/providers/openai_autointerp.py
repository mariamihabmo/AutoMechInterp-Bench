"""Lane B1: OpenAI automated-interpretability adapter.

Converts neuron/feature explanation artifacts produced by OpenAI's
explainer/simulator pipeline into structured hypotheses with
``component_type: "mlp_neuron"``.

The provider does NOT accept or reject claims — it simply translates
discovery outputs into the common schema so that Stage-2 can run
causal interventions and Stage-1 can judge whether a "well-explained"
neuron is also causally important.
"""

from __future__ import annotations

from typing import Any

from . import HypothesisProvider, register_provider


@register_provider
class OpenAIAutoInterpProvider(HypothesisProvider):
    """Adapter for OpenAI-style automated neuron explanations.

    Input: a list of neuron explanation artifacts, each containing at
    minimum a layer, neuron index, natural-language explanation, and
    an optional simulation score.

    Output: hypothesis dicts targeting ``mlp_neuron`` components, with
    the explanation text and simulation score stored as metadata (never
    as acceptance evidence — only causal gates decide).
    """

    name = "openai_autointerp"
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

            hyp: dict[str, Any] = {
                "hypothesis_id": f"oai_neuron_L{layer}N{neuron}_{i}",
                "protocol_id": protocol["protocol_id"],
                "task_id": uow["task_id"],
                "model_id": model_id,
                "metric_id": uow["metric_id"],
                "claim_text": (
                    f"MLP neuron L{layer}N{neuron} causally contributes to "
                    f"{uow['task_id']} — explanation: {explanation[:120]}"
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
                    "neuron may be polysemantic — explanation covers only one sense",
                    "simulation score may not correlate with causal importance",
                ],
                "intervention_level": "mlp_neuron",
                "explanation_text": explanation,
                "discovery_lane": self.name,
            }
            if sim_score is not None:
                hyp["simulation_score"] = float(sim_score)

            hypotheses.append(hyp)

        return self.tag_hypotheses(hypotheses)
