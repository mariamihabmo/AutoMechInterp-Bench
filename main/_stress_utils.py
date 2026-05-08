#!/usr/bin/env python3
"""Helpers for evaluator-driven synthetic stress tests."""

from __future__ import annotations

import copy
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "packages" / "evaluator" / "src"))

from automechinterp_evaluator.io_utils import sha256_file


def stable_rng(parts: list[str | int]) -> float:
    digest = hashlib.sha256("|".join(str(p) for p in parts).encode("utf-8")).hexdigest()
    return int(digest[:8], 16) / 0xFFFFFFFF


def iter_grid(protocol: dict[str, Any]) -> list[tuple[int, str, int, str]]:
    grid = protocol["execution_grid"]
    return [
        (int(seed), str(prompt_variant), int(resample_id), str(method))
        for seed in grid["seeds"]
        for prompt_variant in grid["prompt_variants"]
        for resample_id in grid["resample_ids"]
        for method in grid["methods"]
    ]


def exploratory_seed_set(protocol: dict[str, Any]) -> set[int]:
    seeds = [int(seed) for seed in protocol["execution_grid"]["seeds"]]
    exploratory_fraction = float(protocol.get("sample_size_policy", {}).get("exploratory_fraction", 0.3))
    n_exploratory = max(1, int(round(len(seeds) * exploratory_fraction)))
    n_exploratory = min(max(1, n_exploratory), max(1, len(seeds) - 1))
    return set(seeds[:n_exploratory])


def default_direction(method: str) -> str:
    if "activation" in method or "patch" in method or "clean" in method:
        return "sufficiency_patch"
    return "necessity_ablate"


def clone_hypothesis(template: dict[str, Any], hypothesis_id: str, claim_text: str) -> dict[str, Any]:
    row = copy.deepcopy(template)
    row["hypothesis_id"] = hypothesis_id
    row["claim_text"] = claim_text
    return row


def build_synthetic_bundle(
    bundle_dir: Path,
    protocol: dict[str, Any],
    hypotheses: list[dict[str, Any]],
    row_builder: Callable[[int, dict[str, Any], int, str, int, str], dict[str, Any]],
) -> Path:
    """Write a fully evaluable synthetic bundle to disk."""
    bundle_dir.mkdir(parents=True, exist_ok=True)
    protocol_path = bundle_dir / "protocol.yaml"
    hypothesis_path = bundle_dir / "hypothesis.jsonl"
    evaluation_path = bundle_dir / "evaluation_result.json"
    manifest_path = bundle_dir / "manifest.json"

    import yaml

    protocol_path.write_text(yaml.safe_dump(protocol, sort_keys=False))
    hypothesis_path.write_text("\n".join(json.dumps(row) for row in hypotheses) + ("\n" if hypotheses else ""))

    hypothesis_results = []
    for hyp_idx, hypothesis in enumerate(hypotheses):
        raw_cells = []
        for seed, prompt_variant, resample_id, method in iter_grid(protocol):
            cell_payload = row_builder(hyp_idx, hypothesis, seed, prompt_variant, resample_id, method)
            slice_name = cell_payload.get(
                "slice",
                "exploratory" if seed in exploratory_seed_set(protocol) else "confirmatory",
            )
            raw_cells.append(
                {
                    "seed": seed,
                    "prompt_variant": prompt_variant,
                    "resample_id": resample_id,
                    "method": method,
                    "direction": cell_payload.get("direction", default_direction(method)),
                    "slice": slice_name,
                    "treatment_effect": float(cell_payload["treatment_effect"]),
                    "control_effects": {
                        key: float(value) for key, value in cell_payload["control_effects"].items()
                    },
                    "runner_id": cell_payload.get("runner_id", "synthetic_stress_runner"),
                    "runner_version": cell_payload.get("runner_version", "1.0"),
                    "pipeline_sha": cell_payload.get("pipeline_sha", "synthetic"),
                    "model_ref": cell_payload.get("model_ref", protocol["unit_of_work"]["model_id"]),
                    "dataset_seed": int(cell_payload.get("dataset_seed", seed)),
                    "prompt_template_id": cell_payload.get("prompt_template_id", prompt_variant),
                }
            )
        hypothesis_results.append({"hypothesis_id": hypothesis["hypothesis_id"], "raw_cells": raw_cells})

    evaluation_result = {
        "protocol_id": protocol["protocol_id"],
        "protocol_sha256": sha256_file(protocol_path),
        "hypothesis_results": hypothesis_results,
    }
    evaluation_path.write_text(json.dumps(evaluation_result, indent=2) + "\n")
    manifest = {
        "protocol.yaml": sha256_file(protocol_path),
        "hypothesis.jsonl": sha256_file(hypothesis_path),
        "evaluation_result.json": sha256_file(evaluation_path),
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    return bundle_dir


def apply_gate_ablation(protocol: dict[str, Any], disabled_gates: list[str]) -> dict[str, Any]:
    """Create a protocol variant with selected gates made permissive."""
    variant = copy.deepcopy(protocol)
    stage = variant.setdefault("stage_gates", {})
    stat = variant.setdefault("statistical_policy", {})
    sample = variant.setdefault("sample_size_policy", {})
    control = variant.setdefault("control_policy", {})
    governance = variant.setdefault("governance", {})

    for gate in disabled_gates:
        if gate == "confirmatory_ci":
            stage["require_confirmatory_ci_excludes_zero"] = False
        elif gate == "multiplicity":
            stat["fdr_q"] = 1.0
        elif gate == "power_adequacy":
            stage["min_effect_size_d"] = 0.0
            sample["min_cells_per_hypothesis"] = 1
            sample["power_target"] = 0.50
        elif gate == "effect_size_practical":
            stage["min_practical_cohens_d"] = 0.0
        elif gate == "robustness":
            stage["min_robustness"] = {"seed": 0.0, "prompt_variant": 0.0, "resample": 0.0}
        elif gate == "method_sensitivity":
            stage["max_method_sensitivity_std"] = 1e9
        elif gate == "rank_stability":
            stage["min_rank_stability_tau"] = 0.0
        elif gate == "bidirectional":
            stage["require_bidirectional"] = False
        elif gate == "negative_controls":
            control["max_control_abs_mean"] = 1e9
            stage["min_specificity_ratio"] = 0.0
        elif gate == "baseline_superiority":
            stage["baseline_superiority_ratio"] = 0.0
        elif gate == "cross_model_transfer":
            stage["cross_model_rank_stability_tau"] = 0.0
        elif gate == "governance_valid":
            governance["red_team_required"] = False

    variant["protocol_version"] = f"{protocol.get('protocol_version', '1.0')}-ablated"
    return variant
