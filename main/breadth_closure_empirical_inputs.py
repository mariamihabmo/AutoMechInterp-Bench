#!/usr/bin/env python3
"""Build the exact empirical queue for closing the breadth blocker.

This script does not fabricate new accepted claims. Instead it turns the current
zero-task / low-breadth situation into a concrete rerun queue by combining:
- released zero-acceptance-cell forensics,
- mock-mode confirmatory repair results, and
- current per-claim statistical metrics.

The goal is to tell the next real rerun exactly which bundle/hypothesis to run,
why it is the best breadth candidate, and whether the bottleneck is more
confirmatory evidence, method harmonization, or controls.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "packages" / "evaluator" / "src"))

from automechinterp_evaluator.evaluator import _minimum_sample_size  # noqa: E402

REPRO = ROOT / "main" / "output" / "repro"
REAL_MULTI = ROOT / "main" / "output" / "real_multi_task"
REAL_MULTILANE = ROOT / "main" / "output" / "real_multilane"
OUT_JSON = REPRO / "breadth_closure_empirical_inputs.json"
OUT_MD = REPRO / "breadth_closure_empirical_inputs.md"


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def _closest_claim_payload(bundle: str, hypothesis_id: str) -> tuple[dict[str, Any], dict[str, Any]]:
    candidates = [REAL_MULTI / bundle, REAL_MULTILANE / bundle]
    bundle_dir = next((path for path in candidates if path.exists()), None)
    if bundle_dir is None:
        raise FileNotFoundError(f"could not locate bundle={bundle} in real_multi_task or real_multilane")
    current = json.loads((bundle_dir / "evaluation_result_current.json").read_text())
    protocol = yaml.safe_load((bundle_dir / "protocol.yaml").read_text())
    for row in current.get("claim_reports", []):
        if str(row.get("hypothesis_id")) == str(hypothesis_id):
            return row, protocol
    raise KeyError(f"missing hypothesis_id={hypothesis_id} in {bundle}")


def _repair_lookup() -> dict[tuple[str, str], dict[str, Any]]:
    payload = _load(REPRO / "zero_task_confirmatory_repair.json")
    rows = payload.get("bundles") or payload.get("rows") or []
    out: dict[tuple[str, str], dict[str, Any]] = {}
    for row in rows:
        out[(str(row.get("task")), str(row.get("model")))] = row
    return out


def _task_bucket(priority_row: dict[str, Any], repair: dict[str, Any] | None) -> str:
    failed = set((priority_row.get("closest_to_pass") or {}).get("failed_gates") or [])
    if failed == {"multiplicity"}:
        return "more_confirmatory_signal"
    if failed <= {"method_sensitivity", "multiplicity"}:
        return "method_harmonization_then_confirmatory_rerun"
    if repair and int(repair.get("confirmatory_present_failures_after_mock", 0)) == 0:
        return "real_rerun_on_repaired_protocol"
    if "negative_controls" in failed or "baseline_superiority" in failed:
        return "controls_problem_not_just_sample_size"
    return "mixed_blockers"


def main() -> None:
    REPRO.mkdir(parents=True, exist_ok=True)

    breadth = _load(REPRO / "breadth_gap_analysis.json")
    repairs = _repair_lookup()
    queue: list[dict[str, Any]] = []

    for rank, row in enumerate(breadth.get("priority_targets") or [], start=1):
        ctp = row.get("closest_to_pass") or {}
        bundle = str(ctp.get("bundle"))
        hypothesis_id = str(ctp.get("hypothesis_id"))
        claim, protocol = _closest_claim_payload(bundle, hypothesis_id)
        metrics = claim.get("metrics") or {}
        repair = repairs.get((str(row.get("task")), str(row.get("model"))))
        sample_policy = protocol.get("sample_size_policy") or {}
        stage_gates = protocol.get("stage_gates") or {}
        observed_n = int(metrics.get("n_cells") or 0)
        effect_size = float(abs(metrics.get("cohens_d") or 0.0))
        min_d = float(stage_gates.get("min_effect_size_d") or 0.0)
        power_target = float(sample_policy.get("power_target") or 0.80)
        required_n = _minimum_sample_size(max(effect_size, min_d), alpha=0.05, power=power_target)
        additional_n = max(0, required_n - observed_n) if required_n < 999999 else None

        queue.append({
            "priority_rank": rank,
            "task": row.get("task"),
            "model": row.get("model"),
            "bundle": bundle,
            "hypothesis_id": hypothesis_id,
            "evidence_tier": claim.get("evidence_tier"),
            "failed_gates": list(claim.get("failed_checks") or []),
            "not_evaluated_gates": list(claim.get("not_evaluated_checks") or []),
            "treatment_effect_mean": metrics.get("treatment_effect_mean"),
            "cohens_d_abs": effect_size,
            "p_value_permutation": metrics.get("p_value_permutation"),
            "q_value": metrics.get("q_value"),
            "holm_adjusted_p": metrics.get("holm_adjusted_p"),
            "method_sensitivity_std": metrics.get("method_sensitivity_std"),
            "observed_confirmatory_cells": observed_n,
            "required_cells_for_power_target_estimate": required_n,
            "additional_cells_estimate": additional_n,
            "repair_available": repair is not None,
            "repair_bundle": (repair or {}).get("repaired_bundle"),
            "accepted_after_mock": (repair or {}).get("accepted_after_mock"),
            "confirmatory_present_failures_before": (repair or {}).get("confirmatory_present_failures_before"),
            "confirmatory_present_failures_after_mock": (repair or {}).get("confirmatory_present_failures_after_mock"),
            "confirmatory_ci_failures_before": (repair or {}).get("confirmatory_ci_failures_before"),
            "confirmatory_ci_failures_after_mock": (repair or {}).get("confirmatory_ci_failures_after_mock"),
            "recommended_experiment_type": _task_bucket(row, repair),
            "next_real_command": f"python main/run_real_multi_task.py --device cpu --tasks {row.get('task')} --models {row.get('model')}",
        })

    payload = {
        "generated_by": "main/breadth_closure_empirical_inputs.py",
        "tasks_with_accepted_current": 3,
        "tasks_needed_for_5_of_8": 2,
        "priority_queue": queue,
        "interpretation": [
            "These are not new accepted claims. They are the exact rerun targets with the cleanest evidence-based path to closing the breadth blocker.",
            "Multiplicity-only candidates suggest more confirmatory signal may be sufficient; method-sensitivity candidates need method-harmonized reruns, not just more cells.",
            "Mock-mode repair artifacts only remove plumbing uncertainty; they do not count as scientific evidence.",
        ],
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")

    lines = [
        "# Breadth Closure Empirical Inputs",
        "",
        "This report converts the remaining breadth blocker into an exact rerun queue.",
        "",
        f"- Current accepted-task breadth: **{payload['tasks_with_accepted_current']} / 8**",
        f"- Additional accepted tasks needed for the repo's 5-of-8 criterion: **{payload['tasks_needed_for_5_of_8']}**",
        "",
        "## Priority queue",
        "",
        "| Rank | Task | Model | Bundle | Hypothesis | Failed gates | Est. extra cells | Rerun type |",
        "|---|---|---|---|---|---|---:|---|",
    ]
    for row in queue:
        failed = ", ".join(f"`{g}`" for g in row["failed_gates"]) or "none"
        extra = row["additional_cells_estimate"]
        extra_text = str(extra) if extra is not None else "n/a"
        lines.append(
            f"| {row['priority_rank']} | `{row['task']}` | `{row['model']}` | `{row['bundle']}` | `{row['hypothesis_id']}` | {failed} | {extra_text} | {row['recommended_experiment_type']} |"
        )
    lines.extend(["", "## Notes", ""])
    for note in payload["interpretation"]:
        lines.append(f"- {note}")
    OUT_MD.write_text("\n".join(lines).rstrip() + "\n")
    print(str(OUT_JSON))


if __name__ == "__main__":
    main()
