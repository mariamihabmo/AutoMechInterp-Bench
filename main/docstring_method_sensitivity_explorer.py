#!/usr/bin/env python3
"""Diagnose docstring_v0 method-sensitivity failures and rank repair paths.

This is a lightweight, cached-artifact explorer for WP5 in
REMAINING_BLOCKERS_RELEASE_EXECUTION_PLAN.md. It does not run new model
interventions. It re-projects existing raw per-method effects plus the
distributed-head repair attempt into a necessity-alignment queue.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

try:
    from _bundle_analysis import write_json, write_text
except ModuleNotFoundError:
    from main._bundle_analysis import write_json, write_text

ROOT = Path(__file__).resolve().parents[1]
REPRO = ROOT / "main" / "output" / "repro"
OUT_JSON = REPRO / "docstring_method_sensitivity_explorer.json"
OUT_MD = REPRO / "docstring_method_sensitivity_explorer.md"


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def _method_mean(claim: dict[str, Any], method: str) -> float | None:
    block = (claim.get("method_effects") or {}).get(method) or {}
    value = block.get("mean")
    return float(value) if value is not None else None


def _sign(value: float | None) -> int:
    if value is None:
        return 0
    if value > 0:
        return 1
    if value < 0:
        return -1
    return 0


def _summarize_claim(bundle: str, model: str, claim: dict[str, Any]) -> dict[str, Any]:
    activation = _method_mean(claim, "activation_patching")
    zero = _method_mean(claim, "zero_ablation")
    mean_ablation = _method_mean(claim, "mean_ablation")
    signs = {_sign(v) for v in (activation, zero, mean_ablation) if v is not None}
    nonzero_signs = signs - {0}
    abs_activation = abs(activation) if activation is not None else None
    abs_zero = abs(zero) if zero is not None else None
    necessity_ratio = (
        abs_zero / abs_activation
        if abs_activation not in (None, 0) and abs_zero is not None
        else None
    )
    if len(nonzero_signs) > 1:
        diagnosis = "direction_reversal"
        priority = 20
    elif necessity_ratio is not None and necessity_ratio < 0.25:
        diagnosis = "sufficiency_dominant_low_necessity"
        priority = 70
    elif necessity_ratio is not None and necessity_ratio < 0.60:
        diagnosis = "partial_necessity_gap"
        priority = 85
    else:
        diagnosis = "magnitude_dispersion_or_underpowered"
        priority = 55

    single_gate_only = list(claim.get("failed_checks", [])) == ["method_sensitivity"]
    if single_gate_only:
        priority += 20
    priority -= min(30, int(max(0.0, float(claim.get("margin_over_threshold") or 0.0)) * 30))

    return {
        "bundle": bundle,
        "model": model,
        "hypothesis_id": claim.get("hypothesis_id"),
        "failed_checks": claim.get("failed_checks", []),
        "single_gate_only_method_sensitivity": single_gate_only,
        "method_sensitivity_std": claim.get("method_sensitivity_std"),
        "threshold": claim.get("threshold"),
        "margin_over_threshold": claim.get("margin_over_threshold"),
        "activation_patching_mean": activation,
        "zero_ablation_mean": zero,
        "mean_ablation_mean": mean_ablation,
        "necessity_to_sufficiency_abs_ratio": necessity_ratio,
        "method_mean_range": claim.get("method_mean_range"),
        "diagnosis": diagnosis,
        "repair_priority_score": priority,
        "recommended_next_experiment": _recommend(diagnosis, single_gate_only),
    }


def _recommend(diagnosis: str, single_gate_only: bool) -> str:
    if diagnosis == "partial_necessity_gap" and single_gate_only:
        return (
            "rerun with finer position/component localization and same claim text; "
            "this is the closest class to necessity alignment"
        )
    if diagnosis == "sufficiency_dominant_low_necessity":
        return (
            "search for redundant partner components whose ablation closes the gap; "
            "single-component patching is likely insufficient"
        )
    if diagnosis == "direction_reversal":
        return (
            "do not rescue by threshold changes; inspect task metric, source token, "
            "and intervention direction before generating new claims"
        )
    return "increase confirmatory cells only after verifying same-sign necessity and sufficiency on pilot cells"


def build_analysis(source_dir: Path | None = None) -> dict[str, Any]:
    zero = _load(REPRO / "zero_task_gate_breakdown.json")
    distributed = _load(REPRO / "docstring_distributed_repair.json")
    breadth = _load(REPRO / "breadth_gap_analysis.json")

    rows: list[dict[str, Any]] = []
    for block in ((zero.get("method_sensitivity_forensics") or {}).get("per_task") or {}).get("docstring_v0", []):
        bundle = str(block.get("bundle"))
        model = str(block.get("model"))
        for claim in block.get("claims", []):
            rows.append(_summarize_claim(bundle, model, claim))
    rows.sort(key=lambda row: (row["repair_priority_score"], row["single_gate_only_method_sensitivity"]), reverse=True)

    diagnoses: dict[str, int] = {}
    for row in rows:
        diagnoses[row["diagnosis"]] = diagnoses.get(row["diagnosis"], 0) + 1

    zero_cells = [
        row
        for row in breadth.get("zero_acceptance_cells", [])
        if row.get("task") == "docstring_v0"
    ]
    distributed_agg = distributed.get("aggregate") or {}
    payload = {
        "generated_by": "main/docstring_method_sensitivity_explorer.py",
        "status": "diagnostic_queue_only_not_new_model_evidence",
        "source_artifacts": [
            "main/output/repro/zero_task_gate_breakdown.json",
            "main/output/repro/docstring_distributed_repair.json",
            "main/output/repro/breadth_gap_analysis.json",
        ],
        "requested_source_dir": str(source_dir) if source_dir is not None else "main/output/real_multi_task",
        "summary": {
            "docstring_method_sensitivity_failed_claims": len(rows),
            "single_gate_only_method_sensitivity": sum(1 for row in rows if row["single_gate_only_method_sensitivity"]),
            "diagnosis_counts": diagnoses,
            "distributed_repair_accepted_claims": int(distributed_agg.get("accepted_after_real_total") or 0),
            "distributed_repair_gate_failures": distributed_agg.get("gate_failures_after_real") or {},
            "docstring_zero_acceptance_cells": len(zero_cells),
            "top_repair_candidate": rows[0] if rows else None,
        },
        "ranked_claims": rows,
        "docstring_zero_cells": zero_cells,
        "recommended_program": [
            "Do not relax method_sensitivity for docstring_v0 post hoc.",
            "Start with single-gate-only method_sensitivity failures whose zero-ablation effect has the same sign as activation patching.",
            "Use pilot cells to search for components or positions that increase the zero-ablation/activation-patching absolute ratio before running full Stage-2.",
            "Treat direction-reversal cases as metric/intervention-mapping failures until proven otherwise.",
            "If no necessity-aligned pilot exists, propose a versioned sufficiency-only docstring claim type rather than accepting current claims under the existing tier.",
        ],
    }
    return payload


def format_md(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Docstring Method-Sensitivity Explorer",
        "",
        payload["status"],
        "",
        f"- Method-sensitivity failed docstring claims: **{summary['docstring_method_sensitivity_failed_claims']}**",
        f"- Single-gate-only method-sensitivity failures: **{summary['single_gate_only_method_sensitivity']}**",
        f"- Distributed-head repair accepted claims: **{summary['distributed_repair_accepted_claims']}**",
        f"- Distributed-head residual gates: **{summary['distributed_repair_gate_failures']}**",
        f"- Diagnosis counts: **{summary['diagnosis_counts']}**",
        "",
        "## Ranked repair candidates",
        "",
        "| Rank | Bundle | Hypothesis | Model | Diagnosis | Ratio | Margin | Single gate | Next experiment |",
        "|---:|---|---|---|---|---:|---:|---|---|",
    ]
    for idx, row in enumerate(payload["ranked_claims"], start=1):
        ratio = row.get("necessity_to_sufficiency_abs_ratio")
        ratio_label = f"{ratio:.3f}" if isinstance(ratio, (int, float)) else "n/a"
        margin = row.get("margin_over_threshold")
        margin_label = f"{float(margin):.3f}" if margin is not None else "n/a"
        lines.append(
            f"| {idx} | `{row['bundle']}` | `{row['hypothesis_id']}` | `{row['model']}` | "
            f"`{row['diagnosis']}` | {ratio_label} | {margin_label} | "
            f"{'yes' if row['single_gate_only_method_sensitivity'] else 'no'} | "
            f"{row['recommended_next_experiment']} |"
        )
    lines.extend(["", "## Recommended program", ""])
    lines.extend(f"- {item}" for item in payload["recommended_program"])
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Diagnose docstring_v0 method-sensitivity failures")
    parser.add_argument(
        "--source-dir",
        type=Path,
        default=None,
        help="Optional source bundle directory recorded for provenance; cached repro artifacts drive the analysis.",
    )
    parser.add_argument("--out-json", type=Path, default=OUT_JSON, help="Output JSON path")
    parser.add_argument("--out-md", type=Path, default=OUT_MD, help="Output Markdown path")
    args = parser.parse_args()

    payload = build_analysis(source_dir=args.source_dir)
    write_json(args.out_json, payload)
    write_text(args.out_md, format_md(payload))
    print(str(args.out_json))


if __name__ == "__main__":
    main()
