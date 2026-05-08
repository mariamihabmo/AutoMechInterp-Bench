"""Lane C: Petri / autoaudit behavioral adapter.

Integrates Anthropic's Petri framework for scalable model auditing.
In v1, Petri is treated as a **dataset generator**: it produces
behaviorally-scored transcripts (e.g. alignment faking), and this
provider emits mechanistic hypotheses about which components causally
affect the behavioral detection metric.

v2 (future): unified mechanistic + behavioral evaluation stage where
Petri transcripts are re-scored after mechanistic interventions.
"""

from __future__ import annotations

from typing import Any

from . import HypothesisProvider, register_provider


@register_provider
class PetriBehavioralProvider(HypothesisProvider):
    """Adapter for Anthropic Petri / autoaudit behavioral auditing.

    Input: a list of candidate components (heads, neurons, or features)
    that are hypothesized to affect a behavioral metric (e.g. alignment
    faking detection AUROC), along with dataset metadata from a Petri
    audit run.

    Output: hypothesis dicts where the ``metric_id`` is a behavioral
    detection metric, and ``candidate_components`` are mechanistic
    units to be causally tested.
    """

    name = "petri_behavioral"
    version = "0.1.0"

    def __init__(
        self,
        *,
        candidates: list[dict[str, Any]] | None = None,
        behavioral_metric: str = "alignment_faking_auroc",
        dataset_source: str = "petri_generated",
    ) -> None:
        self.candidates = candidates or []
        self.behavioral_metric = behavioral_metric
        self.dataset_source = dataset_source

    def propose(
        self,
        protocol: dict[str, Any],
        budget: int,
    ) -> list[dict[str, Any]]:
        uow = protocol["unit_of_work"]
        model_id = uow["model_id"]

        hypotheses: list[dict[str, Any]] = []
        for i, cand in enumerate(self.candidates[:budget]):
            comp_type = cand.get("component_type", "head")
            component = dict(cand)

            hyp: dict[str, Any] = {
                "hypothesis_id": f"petri_{comp_type}_{i}",
                "protocol_id": protocol["protocol_id"],
                "task_id": uow["task_id"],
                "model_id": model_id,
                "metric_id": self.behavioral_metric,
                "claim_text": (
                    f"{comp_type} component {cand} causally affects "
                    f"{self.behavioral_metric} on {self.dataset_source} transcripts"
                ),
                "candidate_components": [component],
                "predicted_effect_direction": cand.get(
                    "predicted_direction", "increase"
                ),
                "predicted_min_effect": cand.get("min_effect", 0.02),
                "predicted_specificity_ratio": cand.get(
                    "specificity_ratio", 2.0
                ),
                "expected_failure_modes": [
                    "behavioral metric may not isolate the targeted behavior",
                    "transcript distribution may not be representative",
                    "multiple components may jointly cause the effect",
                ],
                "intervention_level": comp_type,
                "discovery_lane": self.name,
            }
            hypotheses.append(hyp)

        return self.tag_hypotheses(hypotheses)
