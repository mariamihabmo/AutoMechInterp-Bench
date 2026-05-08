#!/usr/bin/env python3
"""Summarize which suite-targeted synthetic families are diagnostic for which ablations."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize stress calibration from suite-targeted ablation results")
    parser.add_argument("--bundle-dir", type=Path, default=Path("main/output/real_multi_task/ioi_v0_gpt2-small"))
    args = parser.parse_args()

    payload = json.loads((args.bundle_dir / "stress_test_ablation.json").read_text())
    conditions = payload["conditions"]
    calibration = {
        "base_bundle": payload["base_bundle"],
        "families": {
            "plausible_but_wrong": {
                "target_suite": "statistical_rigor",
                "full_far": conditions["full_contract"]["per_family"]["plausible_but_wrong"]["far"],
                "suite_ablated_far": conditions["no_stat_rigor"]["per_family"]["plausible_but_wrong"]["far"],
            },
            "method_sensitive": {
                "target_suite": "robustness",
                "full_far": conditions["full_contract"]["per_family"]["method_sensitive"]["far"],
                "suite_ablated_far": conditions["no_robustness_suite"]["per_family"]["method_sensitive"]["far"],
            },
            "control_leaking": {
                "target_suite": "controls",
                "full_far": conditions["full_contract"]["per_family"]["control_leaking"]["far"],
                "suite_ablated_far": conditions["no_controls_suite"]["per_family"]["control_leaking"]["far"],
            },
        },
    }

    md_lines = [
        "# Stress Calibration",
        "",
        f"- Base bundle: `{payload['base_bundle']}`",
        "",
        "| Family | Intended suite | Full FAR | Ablated FAR | Diagnostic? |",
        "|---|---|---|---|---|",
    ]
    for family, row in calibration["families"].items():
        diagnostic = row["suite_ablated_far"] > row["full_far"]
        md_lines.append(
            f"| {family} | {row['target_suite']} | {row['full_far'] * 100:.1f}% | {row['suite_ablated_far'] * 100:.1f}% | {diagnostic} |"
        )

    out_json = args.bundle_dir / "stress_calibration.json"
    out_md = args.bundle_dir / "stress_calibration.md"
    out_json.write_text(json.dumps(calibration, indent=2) + "\n")
    out_md.write_text("\n".join(md_lines).rstrip() + "\n")
    print(str(out_json))


if __name__ == "__main__":
    main()
