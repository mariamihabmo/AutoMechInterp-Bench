#!/usr/bin/env python3
"""Generate field-level findings and real-bundle summary artifacts."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from _bundle_analysis import (
    REAL_MULTILANE_DIR,
    REAL_MULTI_TASK_DIR,
    compute_counterfactual_sensitivity,
    evaluate_bundle_records,
    iter_claim_rows,
    pct,
    summarize_coverage,
    summarize_failure_modes,
    write_json,
    write_text,
)

def _direction_fragility(records: list[dict]) -> dict:
    missing_sufficiency = 0
    missing_necessity = 0
    bidirectional_failed = 0
    for record in records:
        payload = json.loads((record["bundle_dir"] / "evaluation_result.json").read_text())
        by_id = {row["hypothesis_id"]: row for row in payload["hypothesis_results"]}
        for claim in record["result"]["claim_reports"]:
            directions = {cell.get("direction") for cell in by_id[claim["hypothesis_id"]]["raw_cells"]}
            has_sufficiency = "sufficiency_patch" in directions
            has_necessity = "necessity_ablate" in directions
            missing_sufficiency += int(not has_sufficiency)
            missing_necessity += int(not has_necessity)
            bidirectional_failed += int("bidirectional" in claim.get("failed_checks", []))
    return {
        "missing_sufficiency_claims": missing_sufficiency,
        "missing_necessity_claims": missing_necessity,
        "bidirectional_failed_claims": bidirectional_failed,
    }

def _stratified_rates(claim_rows: list[dict], key: str) -> dict:
    grouped: dict[str, list[dict]] = {}
    for row in claim_rows:
        grouped.setdefault(str(row[key]), []).append(row)
    summary = {}
    for value, rows in grouped.items():
        accepted = sum(1 for row in rows if row["passed"])
        summary[value] = {
            "claims": len(rows),
            "accepted": accepted,
            "acceptance_rate": accepted / len(rows) if rows else 0.0,
        }
    return summary

def _fmt_rate2(value: float | None) -> str:
    """Two-decimal percentage to match the published paper"""
    if value is None:
        return "n/a"
    return f"{float(value) * 100:.2f}%"

def _fmt_ci2(ci95: dict | None) -> str:
    if not ci95:
        return "n/a"
    lo = ci95.get("low")
    hi = ci95.get("high")
    if lo is None or hi is None:
        return ci95.get("label", "n/a")
    return f"[{lo * 100:.2f}%, {hi * 100:.2f}%]"

def format_field_findings(payload: dict) -> str:
    lines = [
        "# Field-Level Findings",
        "",
        f"- Claims analyzed: **{payload['totals']['claims']}**",
        f"- Accepted: **{payload['totals']['accepted']}**",
        f"- Rejected: **{payload['totals']['rejected']}**",
        f"- Acceptance rate: **{_fmt_rate2(payload['totals']['acceptance_rate'])}** (95% CI: {_fmt_ci2(payload['totals']['acceptance_rate_ci95'])})",
        "",
        "## Gate-family failure counts",
        "",
        "| Gate family | Count |",
        "|---|---|",
    ]
    for family, count in sorted(payload["gate_family_failure_counts"].items()):
        lines.append(f"| {family} | {count} |")

    lines.extend(["", "## Failed gates", "", "| Gate | Count |", "|---|---|"])
    for gate, count in sorted(payload["failed_gate_counts"].items(), key=lambda kv: (-kv[1], kv[0])):
        lines.append(f"| {gate} | {count} |")

    lines.extend(["", "## Acceptance by task", "", "| Task | Claims | Accepted | Acceptance |", "|---|---|---|---|"])
    for task, row in sorted(payload["acceptance_by_task"].items()):
        lines.append(f"| {task} | {row['claims']} | {row['accepted']} | {_fmt_rate2(row['acceptance_rate'])} |")

    lines.extend(["", "## Acceptance by model", "", "| Model | Claims | Accepted | Acceptance |", "|---|---|---|---|"])
    for model, row in sorted(payload["acceptance_by_model"].items()):
        lines.append(f"| {model} | {row['claims']} | {row['accepted']} | {_fmt_rate2(row['acceptance_rate'])} |")

    lines.extend(["", "## Acceptance by component type", "", "| Component | Claims | Accepted | Acceptance |", "|---|---|---|---|"])
    for component, row in sorted(payload["acceptance_by_component_type"].items()):
        lines.append(f"| {component} | {row['claims']} | {row['accepted']} | {_fmt_rate2(row['acceptance_rate'])} |")

    lines.extend(
        [
            "",
            "## Directional fragility",
            "",
            f"- Missing sufficiency claims: {payload['direction_fragility']['missing_sufficiency_claims']}",
            f"- Missing necessity claims: {payload['direction_fragility']['missing_necessity_claims']}",
            f"- Claims failing bidirectional gate: {payload['direction_fragility']['bidirectional_failed_claims']}",
            "",
            "## Policy sensitivity",
            "",
            f"- Full-contract acceptance rate: {_fmt_rate2(payload['policy_sensitivity']['full_acceptance_rate'])}",
            f"- Most sensitive counterfactual: {payload['policy_sensitivity']['most_sensitive_counterfactual']['name']}",
            f"- Acceptance under that counterfactual: {_fmt_rate2(payload['policy_sensitivity']['most_sensitive_counterfactual']['acceptance_rate'])}",
            "",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"

def format_coverage_md(payload: dict) -> str:
    lines = [
        "# Coverage Summary",
        "",
        f"- Bundles: **{payload['n_bundles']}**",
        f"- Claims: **{payload['totals']['claims']}**",
        f"- Accepted: **{payload['totals']['accepted']}**",
        f"- Acceptance rate: **{_fmt_rate2(payload['totals']['acceptance_rate'])}** (95% CI: {_fmt_ci2(payload['totals']['acceptance_rate_ci95'])})",
        "",
        "| Bundle | Task | Model | Claims | Accepted | Acceptance | Cross-model file |",
        "|---|---|---|---|---|---|---|",
    ]
    for row in payload["bundles"]:
        lines.append(
            f"| {row['bundle']} | {row['task']} | {row['model']} | {row['n_claims']} | {row['accepted']} | {row['acceptance_rate_pct']} | {row['has_cross_model_results']} |"
        )
    return "\n".join(lines).rstrip() + "\n"

def format_failure_md(payload: dict) -> str:
    lines = [
        "# Failure Mode Summary",
        "",
        f"- Claims analyzed: **{payload['n_claims']}**",
        f"- Passed: **{payload['n_passed']}**",
        f"- Failed: **{payload['n_failed']}**",
        "",
        "## Failed gates",
        "",
        "| Gate | Count |",
        "|---|---|",
    ]
    for gate, count in sorted(payload["failed_gate_counts"].items(), key=lambda kv: (-kv[1], kv[0])):
        lines.append(f"| {gate} | {count} |")
    lines.extend(["", "## Top failed-check combinations", "", "| Count | Failed checks |", "|---|---|"])
    for row in payload["top_failed_combinations"]:
        lines.append(f"| {row['count']} | {', '.join(row['failed_checks'])} |")
    return "\n".join(lines).rstrip() + "\n"

def main() -> None:
    records = evaluate_bundle_records(REAL_MULTI_TASK_DIR, REAL_MULTILANE_DIR, use_cached_results=True)
    claim_rows = iter_claim_rows(records)
    coverage = summarize_coverage(records)
    failures = summarize_failure_modes(records)
    policy = compute_counterfactual_sensitivity(records)
    direction_fragility = _direction_fragility(records)

    totals = {
        **coverage["totals"],
        "claims": coverage["totals"]["claims"],
        "accepted": coverage["totals"]["accepted"],
        "rejected": coverage["totals"]["rejected"],
    }
    payload = {
        "totals": totals,
        "tier_counts": coverage["tier_counts"],
        "failed_gate_counts": failures["failed_gate_counts"],
        "gate_family_failure_counts": failures["failed_gate_family_counts"],
        "policy_sensitivity": policy,
        "direction_fragility": direction_fragility,
        "acceptance_by_task": _stratified_rates(claim_rows, "task"),
        "acceptance_by_model": _stratified_rates(claim_rows, "model"),
        "acceptance_by_component_type": _stratified_rates(claim_rows, "component_type"),
        "acceptance_by_lane": _stratified_rates(claim_rows, "discovery_lane"),
    }

    repro_dir = Path(__file__).resolve().parents[1] / "main" / "output" / "repro"
    real_dir = Path(__file__).resolve().parents[1] / "main" / "output" / "real_multi_task"

    write_json(repro_dir / "field_level_findings.json", payload)
    write_text(repro_dir / "field_level_findings.md", format_field_findings(payload))
    write_json(real_dir / "coverage_summary.json", coverage)
    write_text(real_dir / "coverage_summary.md", format_coverage_md(coverage))
    failure_payload = {**failures, "policy_sensitivity": policy}
    write_json(real_dir / "failure_mode_summary.json", failure_payload)
    write_text(real_dir / "failure_mode_summary.md", format_failure_md(failure_payload))
    print(str(repro_dir / "field_level_findings.json"))

if __name__ == "__main__":
    main()
