#!/usr/bin/env python3
"""Evaluator-agnostic latent-factor stress testing.

Default CLI behavior preserves the historical artifact written by the repo:
no seed namespace and the legacy generator regime reproduce the previous
results. Newer callers can request a rotated seed namespace and a fresh
regime with additional prompt-instability structure for larger-budget refresh
runs that do not silently retune the contract to the known legacy leak set.

This script also supports a temporary reduced statistical budget for local
rehearsal runs. When enabled, the output records the reduced budget
explicitly; it is diagnostic infrastructure, not release-grade evidence.
"""

from __future__ import annotations

import argparse
import json
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Any

try:
    from _bundle_analysis import wilson_interval
    from _stress_utils import apply_gate_ablation, build_synthetic_bundle, clone_hypothesis, stable_rng
except ModuleNotFoundError:
    from main._bundle_analysis import wilson_interval
    from main._stress_utils import apply_gate_ablation, build_synthetic_bundle, clone_hypothesis, stable_rng

import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "packages" / "evaluator" / "src"))

import automechinterp_evaluator.evaluator as evaluator_mod
from automechinterp_evaluator.evaluator import evaluate_bundle
from automechinterp_evaluator.io_utils import read_jsonl, read_yaml

CONDITIONS = {
    "full_contract": [],
    "no_controls_suite": ["negative_controls", "baseline_superiority"],
    "no_robustness_suite": ["robustness", "method_sensitivity", "bidirectional", "rank_stability"],
}

@contextmanager
def _temporary_stat_budget(
    *,
    bootstrap_resamples: int | None = None,
    permutation_iterations: int | None = None,
):
    if bootstrap_resamples is None and permutation_iterations is None:
        yield
        return

    original_bootstrap = evaluator_mod._bootstrap_ci
    original_permutation = evaluator_mod._permutation_p_value

    def patched_bootstrap_ci(
        values: list[float],
        confidence: float = 0.95,
        n_resamples: int = evaluator_mod.DEFAULT_BOOTSTRAP_RESAMPLES,
        seed: str = "bootstrap",
    ) -> tuple[float, float]:
        target = int(bootstrap_resamples) if bootstrap_resamples is not None else int(n_resamples)
        return original_bootstrap(values, confidence=confidence, n_resamples=target, seed=seed)

    def patched_permutation_p_value(
        values: list[float],
        n_permutations: int = evaluator_mod.DEFAULT_PERMUTATION_ITERATIONS,
        seed: str = "permtest",
    ) -> float:
        target = int(permutation_iterations) if permutation_iterations is not None else int(n_permutations)
        return original_permutation(values, n_permutations=target, seed=seed)

    evaluator_mod._bootstrap_ci = patched_bootstrap_ci
    evaluator_mod._permutation_p_value = patched_permutation_p_value
    try:
        yield
    finally:
        evaluator_mod._bootstrap_ci = original_bootstrap
        evaluator_mod._permutation_p_value = original_permutation

def _bucket(value: float, scale: int = 10) -> int:
    clamped = max(0.0, min(0.999999, float(value)))
    return int(clamped * scale)

def _rng(parts: list[str | int], seed_namespace: str = "") -> float:
    namespaced = [seed_namespace, *parts] if seed_namespace else parts
    return stable_rng(namespaced)

def _variant_components(template: dict[str, Any], idx: int, protocol: dict[str, Any]) -> list[dict[str, Any]]:
    model_spec = protocol.get("unit_of_work", {}).get("model_spec", {})
    n_layers = max(1, int(model_spec.get("n_layers", 1)))
    n_heads = max(1, int(model_spec.get("n_heads", 1)))
    d_model = max(1, int(model_spec.get("d_model", 1024)))
    variants: list[dict[str, Any]] = []

    for offset, component in enumerate(template.get("candidate_components", [])):
        variant = dict(component)
        component_type = str(variant.get("component_type", "head"))
        if "layer" in variant:
            variant["layer"] = (int(variant["layer"]) + idx + offset) % n_layers
        if component_type == "head" and "head" in variant:
            variant["head"] = (int(variant["head"]) + (idx * 3) + offset + 1) % n_heads
        if component_type == "mlp_neuron":
            variant["neuron"] = int(variant.get("neuron", 0)) + idx + offset + 1
        if component_type in {"sae_feature", "transcoder_feature"}:
            feature_key = "feature_id" if "feature_id" in variant else "feature_index"
            variant[feature_key] = (int(variant.get(feature_key, 0)) + idx + offset + 1) % d_model
        variant["selection_source"] = f"latent_synthetic_{idx:03d}"
        variant["synthetic_variant_id"] = idx
        variants.append(variant)

    return variants or [
        {
            "component_type": "head",
            "layer": idx % n_layers,
            "head": (idx * 3 + 1) % n_heads,
            "selection_source": f"latent_synthetic_{idx:03d}",
            "synthetic_variant_id": idx,
        }
    ]

def _legacy_latent_fields(idx: int, seed_namespace: str) -> dict[str, Any]:
    latent_signal = 0.01 + 0.07 * _rng(["signal", idx], seed_namespace)
    latent_control = 0.01 + 0.07 * _rng(["control", idx], seed_namespace)
    latent_method_dispersion = 0.05 + 0.25 * _rng(["method", idx], seed_namespace)
    latent_confirmatory_decay = 0.40 + 1.00 * _rng(["decay", idx], seed_namespace)
    latent_direction_flip = _rng(["flip", idx], seed_namespace) < 0.30
    latent_prompt_instability = 0.0
    return {
        "latent_signal": latent_signal,
        "latent_control": latent_control,
        "latent_method_dispersion": latent_method_dispersion,
        "latent_confirmatory_decay": latent_confirmatory_decay,
        "latent_direction_flip": latent_direction_flip,
        "latent_prompt_instability": latent_prompt_instability,
    }

def _fresh_v2_latent_fields(idx: int, seed_namespace: str) -> dict[str, Any]:
    latent_signal = 0.008 + 0.075 * _rng(["signal_v2", idx], seed_namespace)
    latent_control = 0.008 + 0.055 * _rng(["control_v2", idx], seed_namespace)
    latent_method_dispersion = 0.03 + 0.28 * _rng(["method_v2", idx], seed_namespace)
    latent_confirmatory_decay = 0.25 + 1.15 * _rng(["decay_v2", idx], seed_namespace)
    latent_direction_flip = _rng(["flip_v2", idx], seed_namespace) < 0.22
    latent_prompt_instability = 0.01 + 0.08 * _rng(["prompt_instability_v2", idx], seed_namespace)
    return {
        "latent_signal": latent_signal,
        "latent_control": latent_control,
        "latent_method_dispersion": latent_method_dispersion,
        "latent_confirmatory_decay": latent_confirmatory_decay,
        "latent_direction_flip": latent_direction_flip,
        "latent_prompt_instability": latent_prompt_instability,
    }

def _latent_fields(idx: int, seed_namespace: str, generator_regime: str) -> dict[str, Any]:
    if generator_regime == "legacy":
        return _legacy_latent_fields(idx, seed_namespace)
    if generator_regime == "fresh_v2":
        return _fresh_v2_latent_fields(idx, seed_namespace)
    raise ValueError(f"Unknown generator_regime={generator_regime!r}")

def _latent_hypotheses(
    template: dict[str, Any],
    protocol: dict[str, Any],
    count: int,
    *,
    seed_namespace: str = "",
    generator_regime: str = "legacy",
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for idx in range(count):
        latent = _latent_fields(idx, seed_namespace, generator_regime)
        latent_signal = float(latent["latent_signal"])
        latent_control = float(latent["latent_control"])
        latent_method_dispersion = float(latent["latent_method_dispersion"])
        latent_confirmatory_decay = float(latent["latent_confirmatory_decay"])
        latent_direction_flip = bool(latent["latent_direction_flip"])
        latent_prompt_instability = float(latent["latent_prompt_instability"])
        profile = (
            f"s{_bucket(latent_signal)}_c{_bucket(latent_control)}_"
            f"m{_bucket(latent_method_dispersion / 0.30)}_"
            f"d{_bucket(latent_confirmatory_decay / 1.40)}_"
            f"p{_bucket(min(0.999999, latent_prompt_instability / 0.10))}_"
            f"{'flip' if latent_direction_flip else 'stable'}"
        )
        row = clone_hypothesis(
            template,
            f"latent_{idx:03d}",
            f"Latent synthetic negative #{idx}: profile {profile}",
        )
        row["candidate_components"] = _variant_components(template, idx, protocol)
        row["predicted_effect_direction"] = "increase"
        row["predicted_min_effect"] = 0.005 + 0.001 * (idx % 3)
        row["predicted_specificity_ratio"] = 2.0 + 0.1 * (idx % 4)
        row["expected_failure_modes"] = list(
            dict.fromkeys(
                [
                    *(mode for mode in row.get("expected_failure_modes", []) if isinstance(mode, str)),
                    "latent_synthetic_negative",
                    f"generator_{generator_regime}",
                    f"profile_{profile}",
                ]
            )
        )
        row.update(latent)
        rows.append(row)
    return rows

def _slice_name_for_seed(seed: int) -> str:
    return "exploratory" if int(seed) in (42, 123) else "confirmatory"

def _row_builder_factory(seed_namespace: str, generator_regime: str):
    def row_builder(
        hyp_idx: int,
        hypothesis: dict[str, Any],
        seed: int,
        prompt_variant: str,
        resample_id: int,
        method: str,
    ) -> dict[str, Any]:
        base_signal = float(hypothesis["latent_signal"])
        control_scale = float(hypothesis["latent_control"])
        method_dispersion = float(hypothesis["latent_method_dispersion"])
        decay = float(hypothesis["latent_confirmatory_decay"])
        direction_flip = bool(hypothesis["latent_direction_flip"])
        prompt_instability = float(hypothesis.get("latent_prompt_instability", 0.0))

        slice_name = _slice_name_for_seed(int(seed))
        noise = (_rng([hyp_idx, seed, prompt_variant, resample_id, method], seed_namespace) - 0.5) * 0.06
        prompt_noise = (_rng(["prompt", hyp_idx, prompt_variant], seed_namespace) - 0.5) * 0.03
        method_bias = {
            "activation_patching": 0.0,
            "zero_ablation": method_dispersion,
            "mean_ablation": -method_dispersion if direction_flip else method_dispersion / 2.0,
        }.get(method, 0.0)

        if generator_regime == "fresh_v2":
            prompt_profile = (_rng(["prompt_profile", hyp_idx, prompt_variant], seed_namespace) - 0.5) * 2.0
            confirmatory_profile = (_rng(["confirmatory_profile", hyp_idx, seed], seed_namespace) - 0.5) * 2.0
            prompt_noise += prompt_instability * prompt_profile
            noise += 0.5 * prompt_instability * confirmatory_profile

        treatment = base_signal + prompt_noise + noise + method_bias
        if slice_name == "confirmatory":
            treatment = treatment * (1.0 - 0.6 * decay)

        controls = {
            "wrong_position": control_scale * 0.8,
            "wrong_layer": control_scale * 0.9,
            "random_component": control_scale * 1.1,
            "mismatched_source": control_scale * 0.7,
        }
        if generator_regime == "fresh_v2":
            controls["wrong_layer"] += 0.25 * prompt_instability
            controls["random_component"] += 0.15 * prompt_instability

        return {
            "slice": slice_name,
            "direction": "sufficiency_patch" if method == "activation_patching" else "necessity_ablate",
            "treatment_effect": treatment,
            "control_effects": controls,
        }

    return row_builder

def run_stress_test(
    bundle_dir: Path,
    count: int = 80,
    *,
    seed_namespace: str = "",
    generator_regime: str = "legacy",
    conditions: dict[str, list[str]] | None = None,
    bootstrap_resamples: int | None = None,
    permutation_iterations: int | None = None,
) -> dict[str, Any]:
    protocol = read_yaml(bundle_dir / "protocol.yaml")
    template = read_jsonl(bundle_dir / "hypothesis.jsonl")[0]
    hypotheses = _latent_hypotheses(
        template,
        protocol,
        count,
        seed_namespace=seed_namespace,
        generator_regime=generator_regime,
    )
    selected_conditions = conditions or CONDITIONS
    condition_results: dict[str, Any] = {}
    row_builder = _row_builder_factory(seed_namespace, generator_regime)

    for condition_name, disabled_gates in selected_conditions.items():
        protocol_variant = apply_gate_ablation(protocol, disabled_gates)
        protocol_variant["protocol_id"] = f"latent_{condition_name}_{protocol['protocol_id']}"
        protocol_variant["claim_budget"]["max_total_claims"] = len(hypotheses)
        protocol_variant["claim_budget"]["max_claims_per_task"] = len(hypotheses)
        variant_hypotheses = []
        for row in hypotheses:
            hyp = dict(row)
            hyp["protocol_id"] = protocol_variant["protocol_id"]
            variant_hypotheses.append(hyp)

        with tempfile.TemporaryDirectory(prefix=f"latent_{condition_name}_") as tmpdir:
            tmp_bundle = Path(tmpdir)
            build_synthetic_bundle(tmp_bundle, protocol_variant, variant_hypotheses, row_builder)
            with _temporary_stat_budget(
                bootstrap_resamples=bootstrap_resamples,
                permutation_iterations=permutation_iterations,
            ):
                evaluation = evaluate_bundle(tmp_bundle)

        leaked = sum(1 for row in evaluation["claim_reports"] if row["passed"])
        latent_lookup = {row["hypothesis_id"]: row for row in hypotheses}
        leaked_negatives = []
        for report in evaluation["claim_reports"]:
            if not report["passed"]:
                continue
            hyp = latent_lookup.get(report["hypothesis_id"], {})
            leaked_negatives.append(
                {
                    "hypothesis_id": report["hypothesis_id"],
                    "evidence_tier": report.get("evidence_tier"),
                    "latent_signal": hyp.get("latent_signal"),
                    "latent_control": hyp.get("latent_control"),
                    "latent_method_dispersion": hyp.get("latent_method_dispersion"),
                    "latent_confirmatory_decay": hyp.get("latent_confirmatory_decay"),
                    "latent_direction_flip": hyp.get("latent_direction_flip"),
                    "latent_prompt_instability": hyp.get("latent_prompt_instability"),
                    "expected_failure_modes": hyp.get("expected_failure_modes", []),
                }
            )
        condition_results[condition_name] = {
            "leaked": leaked,
            "total": len(hypotheses),
            "false_accept_rate": leaked / len(hypotheses) if hypotheses else 0.0,
            "false_accept_rate_ci95": wilson_interval(leaked, len(hypotheses)),
            "leaked_negatives": leaked_negatives,
        }

    notes = [
        "Latent factors control signal strength, control leakage, confirmatory decay, and method dispersion.",
        "This generator is less suite-labeled than the targeted stress regime, but it is still benchmark-authored synthetic data.",
    ]
    if generator_regime == "fresh_v2":
        notes.append("fresh_v2 adds prompt-instability structure and rotated RNG namespaces for a less overfit latent stress refresh.")
    if bootstrap_resamples is not None or permutation_iterations is not None:
        notes.append("Statistical budget was temporarily reduced for this local rehearsal run. Treat the artifact as refresh-direction evidence, not as a release-grade final number.")

    return {
        "base_bundle": str(bundle_dir),
        "negatives": len(hypotheses),
        "seed_namespace": seed_namespace,
        "generator_regime": generator_regime,
        # explicitly
        # label the generator as benchmark-authored rather than externally
        # constructed. ``stress_source`` is the machine-readable form of the
        # naming caveat the papers now footnote: ``agnostic`` here means
        # evaluator-internals-blind, NOT author-independent. An external
        # generator would set ``stress_source: "external_author"`` and live in
        # ``methodology/independent_agnostic_stress_protocol.md`` slot.
        "stress_source": "internal_maintainer",
        "stress_source_note": (
            "'agnostic' = evaluator-internals-blind (no suite labels / no "
            "threshold lookups), NOT author-independent. The generator is "
            "maintainer-authored; see "
            "methodology/independent_agnostic_stress_protocol.md for the "
            "future external-author protocol."
        ),
        "statistical_budget": {
            "bootstrap_resamples": bootstrap_resamples,
            "permutation_iterations": permutation_iterations,
        },
        # stress JSONs must self-document the
        # namespace+budget confound. The 0/200 release-grade and 49/200
        # reduced-rehearsal numbers are not directly comparable: they are
        # paired evidence that must be quoted together. ``namespace_budget_confound_pair``
        # names the sibling artifact so any downstream tool reading only one
        # cell still sees the pairing requirement.
        "namespace_budget_confound_pair": (
            "stress_test_agnostic_fresh_release_grade.json"
            if (bootstrap_resamples is not None or permutation_iterations is not None)
            else "stress_test_agnostic_fresh.json"
        ),
        "namespace_budget_confound_warning": (
            "Quote alongside the paired artifact named in "
            "namespace_budget_confound_pair: this file's leak rate reflects a "
            "specific (seed_namespace, statistical_budget) cell and is not a "
            "stand-alone Goodhart-resistance number."
        ),
        "conditions": condition_results,
        "notes": notes,
    }

def format_markdown(payload: dict[str, Any]) -> str:
    stat_budget = payload.get("statistical_budget", {}) or {}
    lines = [
        "# Evaluator-Agnostic Latent Stress",
        "",
        f"- Base bundle: `{payload['base_bundle']}`",
        f"- Negatives: **{payload['negatives']}**",
        f"- Generator regime: **{payload.get('generator_regime', 'legacy')}**",
        f"- Seed namespace: **{payload.get('seed_namespace') or 'default'}**",
        f"- Bootstrap resamples override: **{stat_budget.get('bootstrap_resamples') if stat_budget.get('bootstrap_resamples') is not None else 'default'}**",
        f"- Permutation iterations override: **{stat_budget.get('permutation_iterations') if stat_budget.get('permutation_iterations') is not None else 'default'}**",
        "",
        "| Condition | Leaked | FAR | 95% CI |",
        "|---|---|---|---|",
    ]
    for condition, row in payload["conditions"].items():
        lines.append(
            f"| {condition} | {row['leaked']}/{row['total']} | {row['false_accept_rate'] * 100:.1f}% | {row['false_accept_rate_ci95']['label']} |"
        )
    return "\n".join(lines).rstrip() + "\n"

def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluator-agnostic latent stress")
    parser.add_argument("--bundle-dir", type=Path, default=ROOT / "main" / "output" / "real_multi_task" / "ioi_v0_gpt2-small")
    parser.add_argument("--count", type=int, default=80)
    parser.add_argument("--seed-namespace", default="")
    parser.add_argument("--generator-regime", choices=["legacy", "fresh_v2"], default="legacy")
    parser.add_argument("--condition", choices=sorted(CONDITIONS.keys()), action="append", default=None)
    parser.add_argument("--bootstrap-resamples", type=int, default=None)
    parser.add_argument("--permutation-iterations", type=int, default=None)
    parser.add_argument("--json-out", type=Path, default=None)
    parser.add_argument("--md-out", type=Path, default=None)
    args = parser.parse_args()

    chosen_conditions = {name: CONDITIONS[name] for name in args.condition} if args.condition else None
    payload = run_stress_test(
        args.bundle_dir,
        count=args.count,
        seed_namespace=args.seed_namespace,
        generator_regime=args.generator_regime,
        conditions=chosen_conditions,
        bootstrap_resamples=args.bootstrap_resamples,
        permutation_iterations=args.permutation_iterations,
    )
    json_path = args.json_out or (args.bundle_dir / "stress_test_agnostic.json")
    md_path = args.md_out or (args.bundle_dir / "stress_test_agnostic.md")
    json_path.write_text(json.dumps(payload, indent=2) + "\n")
    md_path.write_text(format_markdown(payload))
    print(str(json_path))

if __name__ == "__main__":
    main()
