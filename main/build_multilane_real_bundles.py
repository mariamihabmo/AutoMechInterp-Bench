#!/usr/bin/env python3
"""Build evaluated bundles from locally available multi-lane artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "packages" / "evaluator" / "src"))
sys.path.insert(0, str(ROOT / "packages" / "runner" / "src"))

from automechinterp_evaluator.evaluator import evaluate_bundle
from automechinterp_evaluator.reporting import build_markdown_report
from automechinterp_runner.runner import Stage2Config, run_stage2
from run_real_multi_task import make_protocol

LANE_OUTPUT_DIR = ROOT / "main" / "output"
REAL_MULTILANE_DIR = ROOT / "main" / "output" / "real_multilane"

def _write_bundle(bundle_dir: Path, protocol: dict[str, Any], hypotheses: list[dict[str, Any]]) -> None:
    bundle_dir.mkdir(parents=True, exist_ok=True)
    for name in (
        "evaluation_result.json",
        "manifest.json",
        "stage_gate_report.md",
        "environment_lockfile.txt",
        "environment_info.json",
        "cross_model_results.json",
    ):
        path = bundle_dir / name
        if path.exists():
            path.unlink()
    (bundle_dir / "protocol.yaml").write_text(yaml.safe_dump(protocol, sort_keys=False))
    (bundle_dir / "hypothesis.jsonl").write_text("\n".join(json.dumps(row) for row in hypotheses) + ("\n" if hypotheses else ""))

def _load_lane_hypothesis_groups() -> list[tuple[str, str, str, list[dict[str, Any]]]]:
    groups: list[tuple[str, str, str, list[dict[str, Any]]]] = []

    for lane_dir in sorted(LANE_OUTPUT_DIR.glob("lanes_*")):
        hypotheses_path = lane_dir / "all_hypotheses.json"
        if not hypotheses_path.exists():
            continue
        hypotheses = json.loads(hypotheses_path.read_text())
        grouped: dict[str, list[dict[str, Any]]] = {}
        for row in hypotheses:
            grouped.setdefault(row.get("discovery_lane", "unknown"), []).append(row)
        for lane, rows in grouped.items():
            task = rows[0]["task_id"]
            model = rows[0]["model_id"]
            groups.append((task, model, lane, rows))

    for sae_dir in sorted(LANE_OUTPUT_DIR.glob("sae_lane_*")):
        hypotheses_path = sae_dir / "hypotheses.json"
        if not hypotheses_path.exists():
            continue
        source_rows = json.loads(hypotheses_path.read_text())
        parts = sae_dir.name.split("_")
        model = parts[-1]
        task = "_".join(parts[2:-1])
        rows = []
        for row in source_rows:
            direction = "increase" if float(row.get("mean_diff", 0.0)) >= 0 else "decrease"
            rows.append(
                {
                    "hypothesis_id": row["hypothesis_id"],
                    "protocol_id": f"lane_b3_{task}_{model}",
                    "task_id": task,
                    "model_id": model,
                    "metric_id": "logit_diff",
                    "claim_text": row["claim_text"],
                    "candidate_components": [
                        {
                            "component_type": "sae_feature",
                            "sae_id": "local_sae",
                            "layer": int(str(row["hook_point"]).split(".")[1]),
                            "feature_id": int(row["feature_id"]),
                        }
                    ],
                    "predicted_effect_direction": direction,
                    "predicted_min_effect": 0.01,
                    "predicted_specificity_ratio": 2.0,
                    "expected_failure_modes": ["feature_polysemy", "distributed_computation"],
                    "provider_id": "sae_autointerp_local",
                    "discovery_lane": "B3",
                }
            )
        groups.append((task, model, "B3", rows))

    return groups

def main() -> None:
    parser = argparse.ArgumentParser(description="Build evaluated multi-lane bundles from local artifacts")
    parser.add_argument("--mode", default="real", choices=["real", "mock"], help="Runner mode")
    parser.add_argument(
        "--device",
        default="cpu",
        help=(
            "Runner device for real mode. Defaults to ``cpu`` for cross-platform reproducibility "
            "; pass ``mps`` on Apple Silicon or ``cuda`` on "
            "NVIDIA hardware to use accelerated kernels. This script is a development helper, "
            "not part of the canonical reproducibility-audit chain."
        ),
    )
    parser.add_argument("--examples-per-cell", type=int, default=8, help="Examples per cell for Stage-2")
    parser.add_argument("--limit", type=int, default=0, help="Optional limit on number of bundles to build")
    parser.add_argument("--task", default=None, help="Optional task filter, e.g. ioi_v0")
    parser.add_argument("--lane", default=None, help="Optional lane filter, e.g. A or B3")
    args = parser.parse_args()

    groups = _load_lane_hypothesis_groups()
    if args.task:
        groups = [row for row in groups if row[0] == args.task]
    if args.lane:
        groups = [row for row in groups if row[2] == args.lane]
    if args.limit > 0:
        groups = groups[: args.limit]

    summary = {"bundles": [], "mode": args.mode, "device": args.device}
    for task, model, lane, hypotheses in groups:
        protocol = make_protocol(task, model)
        protocol["protocol_id"] = f"multilane_{lane}_{task}_{model}"
        protocol["claim_budget"]["max_total_claims"] = max(len(hypotheses), protocol["claim_budget"]["max_total_claims"])
        protocol["claim_budget"]["max_claims_per_task"] = max(len(hypotheses), protocol["claim_budget"]["max_claims_per_task"])
        protocol["intervention_levels"] = sorted({row["candidate_components"][0]["component_type"] for row in hypotheses})

        for row in hypotheses:
            row["protocol_id"] = protocol["protocol_id"]

        bundle_name = f"{task}_{model}_lane_{lane.lower()}"
        bundle_dir = REAL_MULTILANE_DIR / bundle_name
        _write_bundle(bundle_dir, protocol, hypotheses)
        try:
            run_stage2(
                Stage2Config(
                    bundle_dir=bundle_dir,
                    mode=args.mode,
                    device=args.device,
                    examples_per_cell=args.examples_per_cell,
                )
            )
            result = evaluate_bundle(bundle_dir)
            (bundle_dir / "stage_gate_report.md").write_text(build_markdown_report(result))
            summary["bundles"].append(
                {
                    "bundle": bundle_name,
                    "task": task,
                    "model": model,
                    "lane": lane,
                    "claims": result["overall"]["hypothesis_count"],
                    "accepted": result["overall"]["accepted_count"],
                    "tiers": {row["hypothesis_id"]: row["evidence_tier"] for row in result["claim_reports"]},
                }
            )
        except Exception as exc:
            summary["bundles"].append(
                {
                    "bundle": bundle_name,
                    "task": task,
                    "model": model,
                    "lane": lane,
                    "error": str(exc),
                }
            )

    REAL_MULTILANE_DIR.mkdir(parents=True, exist_ok=True)
    (REAL_MULTILANE_DIR / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(str(REAL_MULTILANE_DIR / "summary.json"))

if __name__ == "__main__":
    main()
