#!/usr/bin/env python3
"""Evaluator-driven suite-targeted stress testing.

This script generates synthetic raw-cell bundles that target specific
failure suites, then re-evaluates those bundles under ablated protocol
variants. No post-hoc mutation of evaluator outputs is used.

Per-family budget (audit finding F-014). The script's CLI default is
``--per-family 20``. The released stress JSON
(``main/output/real_multi_task/ioi_v0_gpt2-small/stress_test_ablation.json``)
was generated with ``--per-family 10`` --- the value that
``Makefile`` and ``main/reproducibility_audit.py`` invoke --- so any
re-run with the script default will produce 30 negatives instead of
the 30 documented in the paper. Both the script default and the audit
invocation are intentionally kept at the **historical** values to
preserve byte-stable reproduction of the released numbers
(``10/30 leaks under controls/statistical/robustness ablations``,
cited in ``papers/submissions/neurips2026_maintrack/paper_body.tex``).

Recommended next-release budget: ``--per-family 100`` (i.e. 300
negatives, sized so that the per-family Wilson 95% CI half-width is
below ~0.06 even when the per-family leak rate is near 0.5). When the
next release rotates the public stress suite (which it must, to limit
evaluator-aware overfitting --- see
``docs/reference/holdout_stress_governance_plan.md``), bump the
``--per-family`` flag in both ``Makefile`` and
``main/reproducibility_audit.py`` simultaneously, regenerate the
stress JSONs, and update the paper numbers in the same commit. Do not
bump the script default in isolation: the byte-identical
reproducibility check in CI will then start failing on a
non-deliberate change.
"""

from __future__ import annotations

import argparse
import copy
import json
import tempfile
from pathlib import Path

from _bundle_analysis import wilson_interval
from _stress_utils import apply_gate_ablation, build_synthetic_bundle, clone_hypothesis, stable_rng

import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "packages" / "evaluator" / "src"))

from automechinterp_evaluator.evaluator import evaluate_bundle
from automechinterp_evaluator.io_utils import read_jsonl, read_yaml


CONDITIONS = {
    "full_contract": [],
    "no_stat_rigor": ["confirmatory_ci", "multiplicity", "power_adequacy", "effect_size_practical"],
    "no_robustness_suite": ["robustness", "method_sensitivity", "bidirectional", "rank_stability"],
    "no_controls_suite": ["negative_controls", "baseline_superiority"],
    "minimal_gates": [
        "confirmatory_ci",
        "multiplicity",
        "power_adequacy",
        "effect_size_practical",
        "robustness",
        "method_sensitivity",
        "bidirectional",
        "rank_stability",
        "negative_controls",
        "baseline_superiority",
        "governance_valid",
    ],
}


def _family_row_builder(family_name: str):
    def builder(hyp_idx: int, hypothesis: dict, seed: int, prompt_variant: str, resample_id: int, method: str) -> dict:
        noise = (stable_rng([family_name, hyp_idx, seed, prompt_variant, resample_id, method]) - 0.5) * 0.02
        prompt_noise = (stable_rng(["prompt", family_name, prompt_variant]) - 0.5) * 0.01
        slice_name = "exploratory" if seed in (42, 123) else "confirmatory"

        if family_name == "plausible_but_wrong":
            methods = ["activation_patching", "zero_ablation", "mean_ablation"]
            rotate_idx = (seed + resample_id + len(prompt_variant)) % len(methods)
            high_method = methods[rotate_idx]
            if method == high_method:
                treatment = 0.22 + noise + prompt_noise
            else:
                treatment = -0.07 + noise + prompt_noise
            controls = {
                "wrong_position": 0.004,
                "wrong_layer": 0.004,
                "random_component": 0.005,
                "mismatched_source": 0.004,
            }
        elif family_name == "method_sensitive":
            method_bias = {
                "activation_patching": 7.0,
                "zero_ablation": 0.15,
                "mean_ablation": 0.15,
            }.get(method, 0.10)
            treatment = method_bias + noise + prompt_noise
            controls = {
                "wrong_position": 0.003,
                "wrong_layer": 0.003,
                "random_component": 0.004,
                "mismatched_source": 0.003,
            }
        elif family_name == "control_leaking":
            treatment = 0.12 + noise
            controls = {
                "wrong_position": 0.055,
                "wrong_layer": 0.060,
                "random_component": 0.070,
                "mismatched_source": 0.050,
            }
        else:
            raise ValueError(f"Unknown family: {family_name}")

        return {
            "slice": slice_name,
            "direction": "sufficiency_patch" if method == "activation_patching" else "necessity_ablate",
            "treatment_effect": treatment,
            "control_effects": controls,
        }

    return builder


def _make_synthetic_hypotheses(template: dict, per_family: int) -> list[dict]:
    hypotheses = []
    for family_name in ("plausible_but_wrong", "method_sensitive", "control_leaking"):
        for idx in range(per_family):
            hyp = clone_hypothesis(
                template,
                hypothesis_id=f"stress_{family_name}_{idx:03d}",
                claim_text=f"Synthetic {family_name} negative #{idx}",
            )
            components = []
            for comp in hyp.get("candidate_components", []):
                new_comp = dict(comp)
                if "layer" in new_comp:
                    new_comp["layer"] = (int(new_comp["layer"]) + idx) % 12
                if "head" in new_comp:
                    new_comp["head"] = (int(new_comp["head"]) + idx) % 12
                if "neuron" in new_comp:
                    new_comp["neuron"] = int(new_comp["neuron"]) + idx
                new_comp["synthetic_variant"] = idx
                components.append(new_comp)
            if components:
                hyp["candidate_components"] = components
            hyp["predicted_effect_direction"] = "increase"
            hyp["predicted_min_effect"] = 0.005
            hyp["predicted_specificity_ratio"] = 2.0
            hyp["expected_failure_modes"] = [family_name, f"variant_{idx}"]
            hyp["synthetic_family"] = family_name
            hypotheses.append(hyp)
    return hypotheses


def run_stress_test(bundle_dir: Path, per_family: int = 20) -> dict:
    protocol = read_yaml(bundle_dir / "protocol.yaml")
    template = read_jsonl(bundle_dir / "hypothesis.jsonl")[0]
    hypotheses = _make_synthetic_hypotheses(template, per_family)
    family_lookup = {row["hypothesis_id"]: row["synthetic_family"] for row in hypotheses}
    results = {}

    for condition_name, disabled_gates in CONDITIONS.items():
        protocol_variant = apply_gate_ablation(protocol, disabled_gates)
        protocol_variant["protocol_id"] = f"stress_{condition_name}_{protocol['protocol_id']}"
        protocol_variant["claim_budget"]["max_total_claims"] = len(hypotheses)
        protocol_variant["claim_budget"]["max_claims_per_task"] = len(hypotheses)
        variant_hypotheses = []
        for row in hypotheses:
            hyp = copy.deepcopy(row)
            hyp["protocol_id"] = protocol_variant["protocol_id"]
            variant_hypotheses.append(hyp)

        with tempfile.TemporaryDirectory(prefix=f"stress_{condition_name}_") as tmpdir:
            tmp_bundle = Path(tmpdir)

            def row_builder(hyp_idx: int, hypothesis: dict, seed: int, prompt_variant: str, resample_id: int, method: str) -> dict:
                return _family_row_builder(hypothesis["synthetic_family"])(hyp_idx, hypothesis, seed, prompt_variant, resample_id, method)

            build_synthetic_bundle(tmp_bundle, protocol_variant, variant_hypotheses, row_builder)
            evaluation = evaluate_bundle(tmp_bundle)

        leaked = sum(1 for row in evaluation["claim_reports"] if row["passed"])
        per_family_leaked = {}
        for family_name in ("plausible_but_wrong", "method_sensitive", "control_leaking"):
            family_reports = [
                row for row in evaluation["claim_reports"] if family_lookup[row["hypothesis_id"]] == family_name
            ]
            family_leaked = sum(1 for row in family_reports if row["passed"])
            per_family_leaked[family_name] = {
                "leaked": family_leaked,
                "total": len(family_reports),
                "far": family_leaked / len(family_reports) if family_reports else 0.0,
            }

        ci95 = wilson_interval(leaked, len(hypotheses))
        results[condition_name] = {
            "disabled_gates": disabled_gates,
            "leaked": leaked,
            "total": len(hypotheses),
            "false_accept_rate": leaked / len(hypotheses) if hypotheses else 0.0,
            "false_accept_rate_ci95": ci95,
            "per_family": per_family_leaked,
        }

    return {
        "base_bundle": str(bundle_dir),
        "per_family": per_family,
        "total_negatives": len(hypotheses),
        "conditions": results,
        "notes": [
            "All FAR values are computed from evaluator outputs on synthetic raw-cell bundles.",
            "Ablated conditions modify protocol thresholds rather than mutating evaluated checks post hoc.",
        ],
    }


def format_markdown(payload: dict) -> str:
    lines = [
        "# Suite-Targeted Stress Test",
        "",
        f"- Base bundle: `{payload['base_bundle']}`",
        f"- Synthetic negatives: **{payload['total_negatives']}**",
        "",
        "| Condition | Leaked | FAR | 95% CI |",
        "|---|---|---|---|",
    ]
    for condition, row in payload["conditions"].items():
        lines.append(
            f"| {condition} | {row['leaked']}/{row['total']} | {row['false_accept_rate'] * 100:.1f}% | {row['false_accept_rate_ci95']['label']} |"
        )
    lines.extend(
        [
            "",
            "## Calibration Notes",
            "",
            "- `plausible_but_wrong` is intended to be most diagnostic for the statistical-rigor suite.",
            "- `method_sensitive` is intended to be most diagnostic for the robustness / sensitivity suite.",
            "- `control_leaking` is intended to be most diagnostic for the controls suite.",
        ]
    )
    lines.extend(["", "## Per-family leakage", ""])
    for condition, row in payload["conditions"].items():
        lines.append(f"### {condition}")
        lines.append("")
        lines.append("| Family | Leaked | FAR |")
        lines.append("|---|---|---|")
        for family, fam_row in row["per_family"].items():
            lines.append(f"| {family} | {fam_row['leaked']}/{fam_row['total']} | {fam_row['far'] * 100:.1f}% |")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluator-driven suite-targeted stress test")
    parser.add_argument("--bundle-dir", type=Path, default=ROOT / "main" / "output" / "real_multi_task" / "ioi_v0_gpt2-small")
    parser.add_argument("--per-family", type=int, default=20)
    args = parser.parse_args()

    payload = run_stress_test(args.bundle_dir, per_family=args.per_family)
    json_path = args.bundle_dir / "stress_test_ablation.json"
    md_path = args.bundle_dir / "stress_test_ablation.md"
    json_path.write_text(json.dumps(payload, indent=2) + "\n")
    md_path.write_text(format_markdown(payload))
    print(str(json_path))


if __name__ == "__main__":
    main()
