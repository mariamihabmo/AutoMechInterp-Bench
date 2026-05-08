"""Model registry for cross-model support.

V7: Provides model shape inference, family grouping, and TransformerLens
name resolution for all supported models.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from automechinterp_evaluator.constants import MODEL_REGISTRY


@dataclass(frozen=True)
class ModelInfo:
    """Model metadata resolved from the registry."""
    model_id: str
    family: str
    n_layers: int
    n_heads: int
    d_model: int
    transformer_lens_name: str


def resolve_model(model_id: str, protocol: dict[str, Any] | None = None) -> ModelInfo:
    """Look up model info from registry, with protocol fallback."""
    normalized = model_id.strip().lower()

    # Check registry first
    if normalized in MODEL_REGISTRY:
        entry = MODEL_REGISTRY[normalized]
        return ModelInfo(
            model_id=model_id,
            family=entry["family"],
            n_layers=entry["n_layers"],
            n_heads=entry["n_heads"],
            d_model=entry["d_model"],
            transformer_lens_name=entry["transformer_lens_name"],
        )

    # Fallback to protocol model_spec
    if protocol is not None:
        unit = protocol.get("unit_of_work", {})
        model_spec = unit.get("model_spec", {})
        if isinstance(model_spec, dict):
            n_layers = model_spec.get("n_layers")
            n_heads = model_spec.get("n_heads")
            d_model = model_spec.get("d_model", n_heads * 64 if n_heads else 768)
            if isinstance(n_layers, int) and isinstance(n_heads, int):
                return ModelInfo(
                    model_id=model_id,
                    family="unknown",
                    n_layers=n_layers,
                    n_heads=n_heads,
                    d_model=d_model,
                    transformer_lens_name=model_id,
                )

    raise ValueError(
        f"Unknown model_id '{model_id}' and no model_spec in protocol. "
        f"Available models: {list(MODEL_REGISTRY.keys())}"
    )


def list_models() -> list[str]:
    return sorted(MODEL_REGISTRY.keys())


def list_families() -> list[str]:
    return sorted(set(v["family"] for v in MODEL_REGISTRY.values()))


def models_in_family(family: str) -> list[str]:
    return sorted(k for k, v in MODEL_REGISTRY.items() if v["family"] == family)
