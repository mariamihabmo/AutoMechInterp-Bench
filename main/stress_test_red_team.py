#!/usr/bin/env python3
"""Adaptive, near-miss, and bundle-hacking stress probes."""

from __future__ import annotations

import argparse
import copy
import json
import tempfile
from pathlib import Path

from _bundle_analysis import wilson_interval
from _stress_utils import build_synthetic_bundle, clone_hypothesis, stable_rng

import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "packages" / "evaluator" / "src"))

from automechinterp_evaluator.evaluator import evaluate_bundle
from automechinterp_evaluator.io_utils import read_jsonl, read_yaml, sha256_file


def _accepted_baseline_row(hyp_idx: int, hypothesis: dict, seed: int, prompt_variant: str, resample_id: int, method: str) -> dict:
    noise = (stable_rng(["baseline", hyp_idx, seed, prompt_variant, resample_id, method]) - 0.5) * 0.01
    return {
        "slice": "exploratory" if seed in (42, 123) else "confirmatory",
        "direction": "sufficiency_patch" if method == "activation_patching" else "necessity_ablate",
        "treatment_effect": 0.14 + noise,
        "control_effects": {
            "wrong_position": 0.003,
            "wrong_layer": 0.003,
            "random_component": 0.004,
            "mismatched_source": 0.003,
        },
    }


def _evaluate_temp_bundle(protocol: dict, hypotheses: list[dict], row_builder, mutate_bundle=None) -> tuple[dict | None, str | None]:
    with tempfile.TemporaryDirectory(prefix="redteam_") as tmpdir:
        tmp_bundle = Path(tmpdir)
        build_synthetic_bundle(tmp_bundle, protocol, hypotheses, row_builder)
        if mutate_bundle is not None:
            mutate_bundle(tmp_bundle)
        try:
            return evaluate_bundle(tmp_bundle), None
        except Exception as exc:
            return None, str(exc)


def run_red_team(bundle_dir: Path, adaptive_attempts: int = 40, near_miss_count: int = 20) -> dict:
    protocol = read_yaml(bundle_dir / "protocol.yaml")
    template = read_jsonl(bundle_dir / "hypothesis.jsonl")[0]

    # Adaptive black-box search
    adaptive_successes = 0
    for attempt in range(adaptive_attempts):
        hypothesis = clone_hypothesis(template, f"adaptive_{attempt:03d}", f"Adaptive latent probe #{attempt}")
        hypothesis["predicted_effect_direction"] = "increase"
        hypothesis["predicted_min_effect"] = 0.005
        hypothesis["protocol_id"] = protocol["protocol_id"]
        signal = 0.01 + 0.08 * stable_rng(["adaptive_signal", attempt])
        control_scale = 0.01 + 0.06 * stable_rng(["adaptive_control", attempt])
        dispersion = 0.25 * stable_rng(["adaptive_dispersion", attempt])

        def adaptive_row_builder(hyp_idx: int, hypothesis: dict, seed: int, prompt_variant: str, resample_id: int, method: str) -> dict:
            method_bias = {"activation_patching": 0.0, "zero_ablation": dispersion, "mean_ablation": -dispersion / 2.0}.get(method, 0.0)
            treatment = signal + method_bias + (stable_rng([attempt, seed, prompt_variant, method]) - 0.5) * 0.04
            return {
                "slice": "exploratory" if seed in (42, 123) else "confirmatory",
                "direction": "sufficiency_patch" if method == "activation_patching" else "necessity_ablate",
                "treatment_effect": treatment,
                "control_effects": {
                    "wrong_position": control_scale * 0.8,
                    "wrong_layer": control_scale * 0.9,
                    "random_component": control_scale * 1.1,
                    "mismatched_source": control_scale * 0.7,
                },
            }

        evaluation, error = _evaluate_temp_bundle(protocol, [hypothesis], adaptive_row_builder)
        if evaluation and evaluation["claim_reports"][0]["passed"]:
            adaptive_successes += 1

    # Near-miss probes
    near_miss_hypotheses = []
    for idx in range(near_miss_count):
        hypothesis = clone_hypothesis(template, f"near_miss_{idx:03d}", f"Near-miss probe #{idx}")
        hypothesis["predicted_effect_direction"] = "increase"
        hypothesis["predicted_min_effect"] = 0.005
        hypothesis["protocol_id"] = protocol["protocol_id"]
        near_miss_hypotheses.append(hypothesis)

    def near_miss_row_builder(hyp_idx: int, hypothesis: dict, seed: int, prompt_variant: str, resample_id: int, method: str) -> dict:
        threshold_noise = (stable_rng(["near", hyp_idx, seed, prompt_variant, method]) - 0.5) * 0.01
        treatment = 0.022 + threshold_noise
        controls = {
            "wrong_position": 0.009,
            "wrong_layer": 0.010,
            "random_component": 0.011,
            "mismatched_source": 0.009,
        }
        return {
            "slice": "exploratory" if seed in (42, 123) else "confirmatory",
            "direction": "sufficiency_patch" if method == "activation_patching" else "necessity_ablate",
            "treatment_effect": treatment,
            "control_effects": controls,
        }

    near_eval, _ = _evaluate_temp_bundle(protocol, near_miss_hypotheses, near_miss_row_builder)
    near_leaked = sum(1 for row in near_eval["claim_reports"] if row["passed"]) if near_eval else 0

    # Bundle-hacking probes
    baseline_hypothesis = clone_hypothesis(template, "hack_baseline", "Strong synthetic baseline")
    baseline_hypothesis["predicted_effect_direction"] = "increase"
    baseline_hypothesis["predicted_min_effect"] = 0.005
    baseline_hypothesis["protocol_id"] = protocol["protocol_id"]
    bundle_hacks = {}

    def missing_slice_attack(bundle_path: Path) -> None:
        payload = json.loads((bundle_path / "evaluation_result.json").read_text())
        for row in payload["hypothesis_results"]:
            for cell in row["raw_cells"]:
                cell["slice"] = "confirmatory"
        (bundle_path / "evaluation_result.json").write_text(json.dumps(payload, indent=2) + "\n")
        manifest = {
            "protocol.yaml": sha256_file(bundle_path / "protocol.yaml"),
            "hypothesis.jsonl": sha256_file(bundle_path / "hypothesis.jsonl"),
            "evaluation_result.json": sha256_file(bundle_path / "evaluation_result.json"),
        }
        (bundle_path / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")

    def single_direction_attack(bundle_path: Path) -> None:
        payload = json.loads((bundle_path / "evaluation_result.json").read_text())
        for row in payload["hypothesis_results"]:
            for cell in row["raw_cells"]:
                cell["direction"] = "sufficiency_patch"
        (bundle_path / "evaluation_result.json").write_text(json.dumps(payload, indent=2) + "\n")
        manifest = {
            "protocol.yaml": sha256_file(bundle_path / "protocol.yaml"),
            "hypothesis.jsonl": sha256_file(bundle_path / "hypothesis.jsonl"),
            "evaluation_result.json": sha256_file(bundle_path / "evaluation_result.json"),
        }
        (bundle_path / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")

    def coverage_hole_attack(bundle_path: Path) -> None:
        payload = json.loads((bundle_path / "evaluation_result.json").read_text())
        payload["hypothesis_results"][0]["raw_cells"] = payload["hypothesis_results"][0]["raw_cells"][:-1]
        (bundle_path / "evaluation_result.json").write_text(json.dumps(payload, indent=2) + "\n")
        manifest = {
            "protocol.yaml": sha256_file(bundle_path / "protocol.yaml"),
            "hypothesis.jsonl": sha256_file(bundle_path / "hypothesis.jsonl"),
            "evaluation_result.json": sha256_file(bundle_path / "evaluation_result.json"),
        }
        (bundle_path / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")

    def protocol_hash_attack(bundle_path: Path) -> None:
        payload = json.loads((bundle_path / "evaluation_result.json").read_text())
        payload["protocol_sha256"] = "tampered"
        (bundle_path / "evaluation_result.json").write_text(json.dumps(payload, indent=2) + "\n")
        manifest = {
            "protocol.yaml": sha256_file(bundle_path / "protocol.yaml"),
            "hypothesis.jsonl": sha256_file(bundle_path / "hypothesis.jsonl"),
            "evaluation_result.json": sha256_file(bundle_path / "evaluation_result.json"),
        }
        (bundle_path / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")

    attack_map = {
        "missing_slice": missing_slice_attack,
        "single_direction": single_direction_attack,
        "coverage_hole": coverage_hole_attack,
        "protocol_hash_mismatch": protocol_hash_attack,
    }
    for attack_name, mutator in attack_map.items():
        evaluation, error = _evaluate_temp_bundle(protocol, [baseline_hypothesis], _accepted_baseline_row, mutate_bundle=mutator)
        bundle_hacks[attack_name] = {
            "blocked": error is not None or (evaluation is not None and not evaluation["claim_reports"][0]["passed"]),
            "error": error,
            "accepted": bool(evaluation and evaluation["claim_reports"][0]["passed"]),
        }

    return {
        "base_bundle": str(bundle_dir),
        "adaptive": {
            "attempts": adaptive_attempts,
            "successes": adaptive_successes,
            "success_rate": adaptive_successes / adaptive_attempts if adaptive_attempts else 0.0,
            "success_rate_ci95": wilson_interval(adaptive_successes, adaptive_attempts),
        },
        "near_miss": {
            "count": near_miss_count,
            "accepted": near_leaked,
            "acceptance_rate": near_leaked / near_miss_count if near_miss_count else 0.0,
            "acceptance_rate_ci95": wilson_interval(near_leaked, near_miss_count),
        },
        "bundle_hacking": bundle_hacks,
        "notes": [
            "Adaptive search is a black-box random search over latent factors, not a direct gate-targeted optimizer.",
            "Bundle-hacking probes modify serialized artifacts before evaluation and are counted as blocked if they error or fail acceptance.",
        ],
    }


def format_markdown(payload: dict) -> str:
    lines = [
        "# Red-Team Stress Probes",
        "",
        f"- Base bundle: `{payload['base_bundle']}`",
        "",
        "## Adaptive search",
        "",
        f"- Attempts: {payload['adaptive']['attempts']}",
        f"- Successes: {payload['adaptive']['successes']}",
        f"- Success rate: {payload['adaptive']['success_rate'] * 100:.1f}% (95% CI: {payload['adaptive']['success_rate_ci95']['label']})",
        "",
        "## Near-miss negatives",
        "",
        f"- Accepted: {payload['near_miss']['accepted']}/{payload['near_miss']['count']}",
        f"- Acceptance rate: {payload['near_miss']['acceptance_rate'] * 100:.1f}% (95% CI: {payload['near_miss']['acceptance_rate_ci95']['label']})",
        "",
        "## Bundle-hacking probes",
        "",
        "| Attack | Blocked | Accepted | Error |",
        "|---|---|---|---|",
    ]
    for attack_name, row in payload["bundle_hacking"].items():
        lines.append(f"| {attack_name} | {row['blocked']} | {row['accepted']} | {row['error'] or ''} |")
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Adaptive / near-miss / bundle-hacking stress probes")
    parser.add_argument("--bundle-dir", type=Path, default=ROOT / "main" / "output" / "real_multi_task" / "ioi_v0_gpt2-small")
    parser.add_argument("--adaptive-attempts", type=int, default=40)
    parser.add_argument("--near-miss-count", type=int, default=20)
    args = parser.parse_args()

    payload = run_red_team(args.bundle_dir, adaptive_attempts=args.adaptive_attempts, near_miss_count=args.near_miss_count)
    json_path = args.bundle_dir / "stress_test_red_team.json"
    md_path = args.bundle_dir / "stress_test_red_team.md"
    json_path.write_text(json.dumps(payload, indent=2) + "\n")
    md_path.write_text(format_markdown(payload))
    print(str(json_path))


if __name__ == "__main__":
    main()
