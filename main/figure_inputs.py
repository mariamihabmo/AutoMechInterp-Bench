#!/usr/bin/env python3
"""Generate compact figure-input artifacts for the main-track paper."""

from __future__ import annotations

import json
from pathlib import Path

from _bundle_analysis import evaluate_bundle_records, REAL_MULTI_TASK_DIR, REAL_MULTILANE_DIR, write_json, write_text


def main() -> None:
    records = evaluate_bundle_records(REAL_MULTI_TASK_DIR, REAL_MULTILANE_DIR, use_cached_results=True)

    accepted_map: dict[str, dict[str, dict[str, int]]] = {}
    failure_family_counts: dict[str, int] = {}
    for record in records:
        task = record["task"]
        model = record["model"]
        lane = next(iter(record["lane_counts"].keys()))
        accepted = record["result"]["overall"]["accepted_count"]
        accepted_map.setdefault(task, {}).setdefault(model, {})[lane] = accepted
        for claim in record["result"]["claim_reports"]:
            for gate in claim.get("failed_checks", []):
                family = {
                    "causal_effect": "causal",
                    "negative_controls": "controls",
                    "baseline_superiority": "controls",
                    "robustness": "robustness",
                    "method_sensitivity": "robustness",
                    "bidirectional": "robustness",
                    "rank_stability": "robustness",
                    "confirmatory_present": "execution",
                    "confirmatory_firewall": "execution",
                    "confirmatory_ci": "statistics",
                    "multiplicity": "statistics",
                    "power_adequacy": "statistics",
                    "effect_size_practical": "statistics",
                    "cross_model_transfer": "transfer",
                }.get(gate, "other")
                failure_family_counts[family] = failure_family_counts.get(family, 0) + 1

    payload = {
        "accepted_breadth_map": accepted_map,
        "failure_family_counts": failure_family_counts,
    }

    out_dir = Path(__file__).resolve().parents[1] / "main" / "output" / "repro"
    write_json(out_dir / "figure_inputs.json", payload)

    lines = [
        "# Figure Inputs",
        "",
        "## Accepted breadth map",
        "",
    ]
    for task, model_rows in sorted(accepted_map.items()):
        lines.append(f"### {task}")
        lines.append("")
        lines.append("| Model | Lane | Accepted claims |")
        lines.append("|---|---|---|")
        for model, lane_rows in sorted(model_rows.items()):
            for lane, accepted in sorted(lane_rows.items()):
                lines.append(f"| {model} | {lane} | {accepted} |")
        lines.append("")
    lines.extend(
        [
            "## Failure family counts",
            "",
            "| Family | Count |",
            "|---|---|",
        ]
    )
    for family, count in sorted(failure_family_counts.items(), key=lambda kv: (-kv[1], kv[0])):
        lines.append(f"| {family} | {count} |")

    write_text(out_dir / "figure_inputs.md", "\n".join(lines).rstrip() + "\n")
    print(str(out_dir / "figure_inputs.json"))


if __name__ == "__main__":
    main()
