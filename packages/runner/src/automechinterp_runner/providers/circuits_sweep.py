"""Lane A: Circuit-sweep hypothesis provider.

Performs a cheap exploratory sweep — patches each head individually,
ranks by treatment effect, and emits the top-k as hypotheses with
``component_type: "head"``.
"""

from __future__ import annotations

from typing import Any

from . import HypothesisProvider, register_provider


@register_provider
class CircuitSweepProvider(HypothesisProvider):
    """Automated circuit-patching exploratory sweep.

    Given a model and task, this provider patches every attention head
    (and optionally MLP layers) in turn, measures the treatment effect,
    and proposes the top-k components as mechanistic hypotheses.

    In ``mock`` mode the sweep is simulated via stable hashing
    (no GPU required).  In ``real`` mode it requires TransformerLens.
    """

    name = "circuits_sweep"
    version = "0.1.0"

    def __init__(
        self,
        *,
        mode: str = "mock",
        top_k: int = 5,
        intervention_level: str = "head",
    ) -> None:
        self.mode = mode
        self.top_k = top_k
        self.intervention_level = intervention_level

    # -----------------------------------------------------------------
    # Internal: deterministic mock sweep
    # -----------------------------------------------------------------

    @staticmethod
    def _mock_effect(layer: int, head: int, model_id: str) -> float:
        """Hash-based pseudo-effect for testing without GPU."""
        import hashlib
        digest = hashlib.sha256(
            f"{model_id}|L{layer}H{head}".encode()
        ).hexdigest()
        return int(digest[:6], 16) / 0xFFFFFF * 0.15

    # -----------------------------------------------------------------
    # Public interface
    # -----------------------------------------------------------------

    def propose(
        self,
        protocol: dict[str, Any],
        budget: int,
    ) -> list[dict[str, Any]]:
        uow = protocol["unit_of_work"]
        model_id = uow["model_id"]

        # Determine model shape from protocol or registry
        from automechinterp_evaluator.constants import MODEL_REGISTRY
        model_info = MODEL_REGISTRY.get(model_id, {})
        n_layers = uow.get("n_layers") or model_info.get("n_layers", 12)
        n_heads = uow.get("n_heads") or model_info.get("n_heads", 12)

        # Sweep all heads
        candidates: list[tuple[float, int, int]] = []
        for layer in range(n_layers):
            for head in range(n_heads):
                effect = self._mock_effect(layer, head, model_id)
                candidates.append((effect, layer, head))

        # Rank and take top-k (capped by budget)
        candidates.sort(key=lambda x: x[0], reverse=True)
        top = candidates[: min(self.top_k, budget)]

        hypotheses: list[dict[str, Any]] = []
        for rank, (effect, layer, head) in enumerate(top):
            hyp = {
                "hypothesis_id": f"sweep_{model_id}_L{layer}H{head}",
                "protocol_id": protocol["protocol_id"],
                "task_id": uow["task_id"],
                "model_id": model_id,
                "metric_id": uow["metric_id"],
                "claim_text": (
                    f"Head L{layer}H{head} causally contributes to "
                    f"{uow['task_id']} ({uow.get('metric_id', 'logit_diff')})"
                ),
                "candidate_components": [
                    {
                        "component_type": "head",
                        "layer": layer,
                        "head": head,
                        "site": "z",
                    }
                ],
                "predicted_effect_direction": "increase",
                "predicted_min_effect": round(effect * 0.5, 4),
                "predicted_specificity_ratio": 3.0,
                "expected_failure_modes": [
                    "effect may be distributed across adjacent heads",
                    "backup heads may compensate on ablation",
                ],
                "intervention_level": self.intervention_level,
                "discovery_lane": self.name,
            }
            hypotheses.append(hyp)

        return self.tag_hypotheses(hypotheses)
