#!/usr/bin/env python3
"""Cheap policy-counterfactual study on existing evaluated claim reports.

Unlike stress_test_ablation.py, this script does not create synthetic bundles.
It simply asks how acceptance would change if selected gate groups were made
permissive on an already evaluated bundle.
"""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "packages" / "evaluator" / "src"))

from automechinterp_evaluator.evaluator import _classify_evidence_tier, evaluate_bundle


COUNTERFACTUALS = {
    "full_contract": [],
    "no_stat_rigor": ["confirmatory_ci", "multiplicity", "power_adequacy", "effect_size_practical"],
    "no_robustness_suite": ["robustness", "method_sensitivity", "bidirectional", "rank_stability"],
    "no_controls_suite": ["negative_controls", "baseline_superiority"],
}


def run_counterfactuals(bundle_dir: Path) -> dict:
    result = evaluate_bundle(bundle_dir)
    output = {}
    for name, disabled_gates in COUNTERFACTUALS.items():
        modified = []
        for report in copy.deepcopy(result["claim_reports"]):
            checks = dict(report["checks"])
            for gate in disabled_gates:
                checks[gate] = True
            tier, passed, failed_checks, not_evaluated_checks, _demotion = _classify_evidence_tier(
                checks,
                exploratory_present=bool(report["metrics"].get("exploratory_present", False)),
            )
            modified.append(
                {
                    "hypothesis_id": report["hypothesis_id"],
                    "evidence_tier": tier,
                    "passed": passed,
                    "failed_checks": failed_checks,
                    "not_evaluated_checks": not_evaluated_checks,
                }
            )
        output[name] = {
            "disabled_gates": disabled_gates,
            "accepted": sum(1 for row in modified if row["passed"]),
            "total": len(modified),
            "claims": modified,
        }
    return output


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Counterfactual policy study on an evaluated bundle")
    parser.add_argument("--bundle-dir", type=Path, default=ROOT / "main" / "output" / "real_multi_task" / "ioi_v0_gpt2-small")
    args = parser.parse_args()

    results = run_counterfactuals(args.bundle_dir)
    output_path = args.bundle_dir / "gate_ablation_results.json"
    output_path.write_text(json.dumps(results, indent=2) + "\n")
    print(str(output_path))


if __name__ == "__main__":
    main()
