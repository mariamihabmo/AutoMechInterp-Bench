"""Lane B3: SAE-based autointerp adapter (bigsnarfdude/autointerp style).

Converts selected SAE features (chosen via natural-language descriptions
for detecting alignment faking or other phenomena) into structured
hypotheses with ``component_type: "sae_feature"``.

Stage-2 then runs **causal** SAE feature interventions (ablation, clamp,
replacement) and Stage-1 tells you which description-selected features
are causally diagnostic vs merely correlated.
"""

from __future__ import annotations

from typing import Any

from . import HypothesisProvider, register_provider


@register_provider
class SAEAutoInterpProvider(HypothesisProvider):
    """Adapter for SAE feature-selection discovery lanes.

    Input: a list of selected SAE features, each containing at minimum
    an ``sae_id``, ``layer``, ``feature_id``, and optionally a
    natural-language ``description`` and ``detection_score``.

    Output: hypothesis dicts targeting ``sae_feature`` components,
    claiming that each feature causally affects the specified metric
    under the specified task.
    """

    name = "sae_autointerp"
    version = "0.1.0"

    def __init__(
        self,
        *,
        features: list[dict[str, Any]] | None = None,
    ) -> None:
        self.features = features or []

    def propose(
        self,
        protocol: dict[str, Any],
        budget: int,
    ) -> list[dict[str, Any]]:
        uow = protocol["unit_of_work"]
        model_id = uow["model_id"]

        hypotheses: list[dict[str, Any]] = []
        for i, feat in enumerate(self.features[:budget]):
            sae_id = feat.get("sae_id", "default_sae")
            layer = feat.get("layer", 0)
            feature_id = feat.get("feature_id", 0)
            description = feat.get("description", "")
            sae_site = feat.get("site", "resid_post")

            hyp: dict[str, Any] = {
                "hypothesis_id": f"sae_{sae_id}_L{layer}F{feature_id}_{i}",
                "protocol_id": protocol["protocol_id"],
                "task_id": uow["task_id"],
                "model_id": model_id,
                "metric_id": uow["metric_id"],
                "claim_text": (
                    f"SAE feature {sae_id}:L{layer}:F{feature_id} causally "
                    f"affects {uow['task_id']} — {description[:100]}"
                ),
                "candidate_components": [
                    {
                        "component_type": "sae_feature",
                        "sae_id": sae_id,
                        "layer": layer,
                        "feature_id": feature_id,
                        "site": sae_site,
                    }
                ],
                "predicted_effect_direction": "increase",
                "predicted_min_effect": 0.02,
                "predicted_specificity_ratio": 2.0,
                "expected_failure_modes": [
                    "feature may detect surface correlate, not causal mechanism",
                    "SAE reconstruction error may confound ablation",
                    "feature may be polysemantic across unrelated tasks",
                ],
                "intervention_level": "sae_feature",
                "sae_id": sae_id,
                "sae_site": sae_site,
                "explanation_text": description,
                "discovery_lane": self.name,
            }
            hypotheses.append(hyp)

        return self.tag_hypotheses(hypotheses)
