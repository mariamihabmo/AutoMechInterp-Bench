"""Deterministic generator for discovery-agent output artifacts.

V8: Extended with systematic_search discovery mode that grids over all
component pairs, ranks by deterministic heuristic, and generates
structured hypotheses for exploratory-split evaluation.
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any

from .io_utils import BundleError, read_json_any, read_yaml, write_json
from .loader import validate_protocol

DEFAULT_FAILURE_MODES = [
    "prompt_template_overfitting",
    "distributed_backup_components",
    "method_sensitivity_instability",
]

DEFAULT_MODEL_SHAPES = {
    "gpt2-small": {"n_layers": 12, "n_heads": 12},
    "gpt2": {"n_layers": 12, "n_heads": 12},
}

EXPLORATION_CLAIM_KEYS = (
    "claim_text",
    "mechanistic_claim",
    "summary",
    "hypothesis",
    "description",
)

EXPLORATION_COMPONENT_KEYS = (
    "components",
    "candidate_components",
    "top_components",
)

EXPLORATION_EFFECT_KEYS = (
    "predicted_effect_size",
    "effect_size",
    "metric_delta",
    "treatment_effect_mean",
)

EXPLORATION_SPECIFICITY_KEYS = (
    "specificity_ratio",
    "control_ratio",
)

EXPLORATION_FAILURE_KEYS = (
    "failure_modes",
    "expected_failure_modes",
)

def _stable_int(seed: str, modulus: int) -> int:
    if modulus <= 0:
        raise ValueError("modulus must be positive")
    digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()
    return int(digest[:8], 16) % modulus

def _slug(value: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "_", value.strip()).strip("_").lower()
    return s or "task"

def _load_component_catalog(path: Path | None) -> list[dict[str, Any]]:
    if path is None:
        return []
    payload = read_json_any(path)
    if isinstance(payload, list):
        rows = payload
    elif isinstance(payload, dict):
        rows = payload.get("components")
        if not isinstance(rows, list):
            raise BundleError("component catalog JSON object must contain list field 'components'")
    else:
        raise BundleError("component catalog must be JSON object or JSON list")

    if not rows:
        return []
    if not all(isinstance(row, dict) for row in rows):
        raise BundleError("component catalog entries must be JSON objects")
    return [dict(row) for row in rows]

def _load_exploration_findings(path: Path | None) -> list[dict[str, Any]]:
    if path is None:
        return []
    payload = read_json_any(path)
    if isinstance(payload, list):
        findings = payload
    elif isinstance(payload, dict):
        for key in ("findings", "hypotheses", "results", "items"):
            value = payload.get(key)
            if isinstance(value, list):
                findings = value
                break
        else:
            findings = [payload]
    else:
        raise BundleError("exploration input must be JSON object or list")

    if not all(isinstance(item, dict) for item in findings):
        raise BundleError("exploration findings must contain JSON objects only")
    return [dict(item) for item in findings]

def _first_present(record: dict[str, Any], keys: tuple[str, ...]) -> Any:
    for key in keys:
        if key in record:
            return record[key]
    return None

def _normalize_direction(value: Any, default: str) -> str:
    if isinstance(value, str):
        mapped = {
            "increase": "increase",
            "up": "increase",
            "positive": "increase",
            "inc": "increase",
            "decrease": "decrease",
            "down": "decrease",
            "negative": "decrease",
            "dec": "decrease",
        }.get(value.strip().lower())
        if mapped:
            return mapped
    if isinstance(value, (int, float)):
        return "increase" if float(value) >= 0.0 else "decrease"
    return default

def _normalize_components(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    rows = [row for row in value if isinstance(row, dict)]
    return [dict(row) for row in rows]

def _normalize_failure_modes(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    rows = [str(v).strip() for v in value if isinstance(v, str) and v.strip()]
    return rows

def _resolve_model_shape(protocol: dict[str, Any]) -> tuple[int, int]:
    unit = protocol["unit_of_work"]
    model_spec = unit.get("model_spec")
    if isinstance(model_spec, dict):
        n_layers = model_spec.get("n_layers")
        n_heads = model_spec.get("n_heads")
        if isinstance(n_layers, int) and n_layers > 0 and isinstance(n_heads, int) and n_heads > 0:
            return n_layers, n_heads

    model_id = str(unit.get("model_id", "")).strip().lower()
    fallback = DEFAULT_MODEL_SHAPES.get(model_id)
    if fallback:
        return int(fallback["n_layers"]), int(fallback["n_heads"])

    raise BundleError(
        "Unable to infer model shape for fallback components. Add "
        "unit_of_work.model_spec.{n_layers,n_heads} to protocol.yaml."
    )

def _fallback_components(
    task_id: str,
    model_id: str,
    n_layers: int,
    n_heads: int,
    hypothesis_index: int,
    count: int,
) -> list[dict[str, Any]]:
    task_seed = f"{task_id}|{model_id}|{hypothesis_index}"
    components = []
    for i in range(max(1, count)):
        layer = _stable_int(f"{task_seed}|layer|{i}", n_layers)
        head = _stable_int(f"{task_seed}|head|{i}", n_heads)
        components.append(
            {
                "component_type": "head",
                "layer": layer,
                "head": head,
                "selection_source": "deterministic_fallback",
            }
        )
    return components

def _catalog_components(
    catalog: list[dict[str, Any]],
    hypothesis_index: int,
    per_hypothesis: int,
) -> list[dict[str, Any]]:
    if not catalog:
        return []
    k = max(1, per_hypothesis)
    start = (hypothesis_index * k) % len(catalog)
    return [dict(catalog[(start + j) % len(catalog)]) for j in range(k)]

def generate_systematic_search_hypotheses(
    *,
    protocol: dict[str, Any],
    n_layers: int,
    n_heads: int,
    hypothesis_count: int,
    components_per_hypothesis: int,
    effect_floor: float,
    specificity_floor: float,
) -> list[dict[str, Any]]:
    """Generate hypotheses by systematically searching over all components.

    V8 §2.2: Ranks all (layer, head) pairs by a deterministic
    hash-based heuristic and selects the top-k as candidate components.
    These hypotheses are marked for exploratory-split-only evaluation.
    """
    unit = protocol["unit_of_work"]
    task_id = unit["task_id"]
    model_id = unit["model_id"]
    metric_id = unit["metric_id"]
    prefix = _slug(task_id)

    # Grid over all (layer, head) pairs and rank by deterministic score
    all_components: list[tuple[float, int, int]] = []
    for layer in range(n_layers):
        for head in range(n_heads):
            # Deterministic "importance" score based on hash
            score_seed = f"{task_id}|{model_id}|systematic|{layer}|{head}"
            score = _stable_int(score_seed, 10000) / 10000.0
            all_components.append((score, layer, head))

    # Sort by score descending (highest "importance" first)
    all_components.sort(key=lambda x: -x[0])

    hypotheses: list[dict[str, Any]] = []
    k = max(1, components_per_hypothesis)

    for h_idx in range(min(hypothesis_count, len(all_components) // k)):
        components = []
        for c_idx in range(k):
            flat_idx = h_idx * k + c_idx
            if flat_idx >= len(all_components):
                break
            _, layer, head = all_components[flat_idx]
            components.append({
                "component_type": "head",
                "layer": layer,
                "head": head,
                "selection_source": "systematic_search",
            })

        claim_text = (
            f"Systematic search identifies components predicted to affect {metric_id} "
            f"for task {task_id} on model {model_id}."
        )
        hypotheses.append({
            "hypothesis_id": f"h_{prefix}_sys_{h_idx + 1:03d}",
            "mechanistic_claim": claim_text,
            "components": components,
            "predicted_effect_direction": "increase",
            "predicted_effect_size": effect_floor,
            "specificity_ratio": specificity_floor,
            "failure_modes": list(DEFAULT_FAILURE_MODES),
            "discovery_mode": "systematic_search",
            "evaluation_slice": "exploratory",  # V8: systematic search = exploratory only
        })

    return hypotheses

def generate_agent_output(
    *,
    bundle_dir: Path,
    output_path: Path | None = None,
    hypothesis_count: int = 3,
    predicted_direction: str = "increase",
    component_catalog_path: Path | None = None,
    exploration_input_path: Path | None = None,
    components_per_hypothesis: int = 2,
    overwrite: bool = False,
    discovery_mode: str | None = None,
) -> dict[str, Any]:
    protocol_path = bundle_dir / "protocol.yaml"
    if not protocol_path.exists():
        raise BundleError("Bundle must contain protocol.yaml before generating agent output")

    protocol = read_yaml(protocol_path)
    validate_protocol(protocol)

    direction = predicted_direction.strip().lower()
    if direction not in {"increase", "decrease"}:
        raise BundleError("predicted_direction must be 'increase' or 'decrease'")

    max_claims = int(protocol["claim_budget"]["max_claims_per_task"])
    if hypothesis_count <= 0:
        raise BundleError("hypothesis_count must be positive")
    if hypothesis_count > max_claims:
        raise BundleError(
            f"hypothesis_count exceeds protocol claim budget: {hypothesis_count} > {max_claims}"
        )

    unit = protocol["unit_of_work"]
    task_id = unit["task_id"]
    model_id = unit["model_id"]
    metric_id = unit["metric_id"]
    n_layers, n_heads = _resolve_model_shape(protocol)

    catalog = _load_component_catalog(component_catalog_path)
    exploration_findings = _load_exploration_findings(exploration_input_path)

    effect_floor = float(
        max(
            protocol["stage_gates"]["min_causal_effect"],
            protocol["statistical_policy"]["min_effect_floor"],
        )
    )
    specificity_floor = float(protocol["stage_gates"]["min_specificity_ratio"])

    # V8: Support systematic_search discovery mode
    if discovery_mode == "systematic_search":
        hypotheses = generate_systematic_search_hypotheses(
            protocol=protocol,
            n_layers=n_layers,
            n_heads=n_heads,
            hypothesis_count=hypothesis_count,
            components_per_hypothesis=components_per_hypothesis,
            effect_floor=effect_floor,
            specificity_floor=specificity_floor,
        )
        source_mode = "systematic_search"
    else:
        source_mode = "template"  # default, may be overridden below
        hypotheses = []
        prefix = _slug(task_id)

        if exploration_findings:
            source_mode = "exploration"
            usable = 0
            for idx, finding in enumerate(exploration_findings, start=1):
                if usable >= hypothesis_count:
                    break

                components = _normalize_components(_first_present(finding, EXPLORATION_COMPONENT_KEYS))
                if not components:
                    continue

                claim_text = _first_present(finding, EXPLORATION_CLAIM_KEYS)
                if not isinstance(claim_text, str) or not claim_text.strip():
                    claim_text = (
                        f"Exploration-derived candidate components are predicted to affect {metric_id} "
                        f"for task {task_id} on model {model_id}."
                    )

                effect_guess = _first_present(finding, EXPLORATION_EFFECT_KEYS)
                if isinstance(effect_guess, (int, float)):
                    effect_size = max(abs(float(effect_guess)), effect_floor)
                else:
                    effect_size = effect_floor

                specificity_guess = _first_present(finding, EXPLORATION_SPECIFICITY_KEYS)
                specificity = float(specificity_guess) if isinstance(specificity_guess, (int, float)) else specificity_floor
                specificity = max(specificity, specificity_floor)

                direction_guess = finding.get("predicted_effect_direction", finding.get("direction", effect_guess))
                direction_final = _normalize_direction(direction_guess, default=direction)

                failure_modes = _normalize_failure_modes(_first_present(finding, EXPLORATION_FAILURE_KEYS))
                if not failure_modes:
                    failure_modes = list(DEFAULT_FAILURE_MODES)

                usable += 1
                hypotheses.append(
                    {
                        "hypothesis_id": f"h_{prefix}_{usable:03d}",
                        "mechanistic_claim": claim_text.strip(),
                        "components": components[: max(1, components_per_hypothesis)],
                        "predicted_effect_direction": direction_final,
                        "predicted_effect_size": effect_size,
                        "specificity_ratio": specificity,
                        "failure_modes": failure_modes,
                    }
                )

            if not hypotheses:
                raise BundleError("No usable exploration findings with component lists were found")

        for idx in range(len(hypotheses) + 1, hypothesis_count + 1):
            components = _catalog_components(
                catalog=catalog,
                hypothesis_index=idx - 1 - len(hypotheses),
                per_hypothesis=components_per_hypothesis,
            )
            if not components:
                components = _fallback_components(
                    task_id=task_id,
                    model_id=model_id,
                    n_layers=n_layers,
                    n_heads=n_heads,
                    hypothesis_index=idx,
                    count=components_per_hypothesis,
                )

            claim_text = (
                f"Candidate components are predicted to {direction} {metric_id} "
                f"for task {task_id} on model {model_id}."
            )
            hypotheses.append(
                {
                    "hypothesis_id": f"h_{prefix}_{idx:03d}",
                    "mechanistic_claim": claim_text,
                    "components": components,
                    "predicted_effect_direction": direction,
                    "predicted_effect_size": effect_floor,
                    "specificity_ratio": specificity_floor,
                    "failure_modes": list(DEFAULT_FAILURE_MODES),
                }
            )

    payload: dict[str, Any] = {
        "agent_metadata": {
            "generator": "automechinterp_evaluator.generate_agent_output",
            "protocol_id": protocol["protocol_id"],
            "task_id": task_id,
            "model_id": model_id,
            "model_shape": {"n_layers": n_layers, "n_heads": n_heads},
            "metric_id": metric_id,
            "hypothesis_count": len(hypotheses),
            "source_mode": source_mode,
            "component_catalog_used": bool(catalog),
            "exploration_input_used": bool(exploration_findings),
            "exploration_records": len(exploration_findings),
            "components_per_hypothesis": int(max(1, components_per_hypothesis)),
        },
        "hypotheses": hypotheses,
    }

    target = output_path or (bundle_dir / "agent_output.json")
    if target.exists() and not overwrite:
        raise BundleError(f"Refusing to overwrite existing file without --overwrite: {target}")

    write_json(target, payload)

    return {
        "bundle": str(bundle_dir),
        "protocol_id": protocol["protocol_id"],
        "output": str(target),
        "hypothesis_count": len(hypotheses),
        "component_catalog_used": bool(catalog),
        "exploration_input_used": bool(exploration_findings),
        "source_mode": source_mode,
    }
