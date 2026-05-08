#!/usr/bin/env python3
"""Per-task failed-gate breakdown for the current zero-accepted-claim tasks.

This is the F-019 analogue of ``main/transfer_failure_breakdown.py``: a
**diagnostic artifact only** that tells an operator *which* gate is
killing claims in the 5 released task families that currently have
zero accepted claims, *how many* claims would survive a single-gate
relaxation, and *how close to the gate boundary* each killed claim is
— so that the decision to attempt targeted re-discovery (F-019 fix
path) can be grounded in evidence rather than guesswork.

Scope and zero-task set
-----------------------

This script derives the current zero-task set from the released bundle surface
on every run. That matters because the zero-task real-repair workflow can
legitimately move a task out of this set. The script walks all released bundles
whose ``task_id`` remains zero-accepted, reads per-claim ``failed_checks`` from
``evaluate_bundle_records`` (the same code path that produced the
headline counts in ``field_level_findings.json``), and emits:

- ``per_task.<task>.failed_gate_counts``: how many claims failed each
  gate in that task.
- ``per_task.<task>.single_gate_only_claims``: claims that failed
  **exactly one** gate. A single-gate relaxation argument (if it
  could be defended on the merits, which this script does NOT
  assert) would rescue exactly these claims.
- ``per_task.<task>.multi_gate_claims``: claims that failed two or
  more gates. No single-gate relaxation can rescue these.
- ``per_task.<task>.top_failed_combinations``: the most frequent
  multi-gate failure combinations, so that an operator can see at a
  glance whether the killed claims fail in a coherent pattern
  (e.g., "robustness + confirmatory_ci co-fail") or a diffuse one.
- ``aggregate``: the same roll-up across all 5 zero-tasks.

What this artifact **does not** do
----------------------------------

- It does NOT lower any gate, relax any floor, or re-run evaluation.
- It does NOT assert that any currently-rejected claim should be
  accepted. The "single_gate_only_claims" count is the *upper
  bound* on how many claims a single relaxation could affect — it
  is not a count of claims that would pass under any specific
  relaxation, because the gate itself may be failing for a
  principled reason that the relaxation does not address.
- It does NOT change headline numbers. If the zero-task set changes, that
  happened in the released artifacts before this diagnostic ran.

Usage
-----

    python main/zero_task_gate_breakdown.py

Writes:

    main/output/repro/zero_task_gate_breakdown.json
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "main"))

from _bundle_analysis import (  # noqa: E402  (path adjusted above)
    REAL_MULTI_TASK_DIR,
    REAL_MULTILANE_DIR,
    evaluate_bundle_records,
    iter_claim_rows,
)

OUTPUT_PATH = ROOT / "main" / "output" / "repro" / "zero_task_gate_breakdown.json"


def _effect_stats(values: list[float]) -> dict:
    if not values:
        return {"n": 0, "mean": None, "min": None, "max": None}
    return {
        "n": len(values),
        "mean": mean(values),
        "min": min(values),
        "max": max(values),
    }


def _summarize_rows(rows: list[dict]) -> dict:
    """Build the per-task (or aggregate) summary block from claim rows.

    ``rows`` must be the subset already filtered to a single task id
    (or, for the aggregate block, all zero-task rows). This function
    does not filter.
    """
    n_claims = len(rows)
    n_passed = sum(1 for r in rows if r["passed"])
    n_failed = n_claims - n_passed

    failed_gate_counts: Counter = Counter()
    for r in rows:
        for gate in r["failed_checks"]:
            failed_gate_counts[gate] += 1

    single_gate_only: Counter = Counter()
    multi_gate_combos: Counter = Counter()
    n_single = 0
    n_multi = 0
    n_zero_failed_but_rejected = 0
    for r in rows:
        if r["passed"]:
            continue
        failed = sorted(r["failed_checks"])
        if len(failed) == 0:
            # Rejected without a named failed gate (e.g., not_evaluated
            # path or tier-gating). Surface separately so the counts
            # are auditable.
            n_zero_failed_but_rejected += 1
        elif len(failed) == 1:
            n_single += 1
            single_gate_only[failed[0]] += 1
        else:
            n_multi += 1
            multi_gate_combos[tuple(failed)] += 1

    top_combos = [
        {"failed_checks": list(combo), "count": count}
        for combo, count in multi_gate_combos.most_common(5)
    ]

    return {
        "n_claims": n_claims,
        "n_passed": n_passed,
        "n_failed": n_failed,
        "failed_gate_counts": dict(failed_gate_counts),
        "single_gate_only_count": n_single,
        "single_gate_only_by_gate": dict(single_gate_only),
        "multi_gate_count": n_multi,
        "rejected_with_no_failed_gate": n_zero_failed_but_rejected,
        "top_failed_combinations": top_combos,
    }


def _method_sensitivity_forensics(records: list[dict], zero_tasks: tuple[str, ...]) -> dict:
    """Summarize raw per-method effects for zero-task method-sensitivity failures.

    This is deliberately descriptive. It does not decide that the method
    sensitivity gate is too strict; it shows whether the residual zero-task
    failures are dominated by a sufficiency-only pattern, direction reversal, or
    other cross-method instability.
    """

    by_task: dict[str, list[dict]] = {task: [] for task in zero_tasks}
    aggregate_margins: list[float] = []

    for record in records:
        task = str(record["task"])
        if task not in by_task:
            continue
        eval_path = Path(record["bundle_dir"]) / "evaluation_result.json"
        if not eval_path.exists():
            continue
        try:
            raw = json.loads(eval_path.read_text())
        except Exception:
            continue

        reports = {
            str(row["hypothesis_id"]): row
            for row in record["result"].get("claim_reports", [])
        }
        threshold = float(record["protocol"].get("stage_gates", {}).get("max_method_sensitivity_std", 0.0))
        claims: list[dict] = []
        for hyp_result in raw.get("hypothesis_results", []):
            hypothesis_id = str(hyp_result.get("hypothesis_id"))
            report = reports.get(hypothesis_id, {})
            failed = list(report.get("failed_checks", []))
            if "method_sensitivity" not in failed:
                continue
            by_method: dict[str, list[float]] = {}
            for cell in hyp_result.get("raw_cells", []):
                method = str(cell.get("method", "unknown"))
                try:
                    effect = float(cell.get("treatment_effect"))
                except (TypeError, ValueError):
                    continue
                by_method.setdefault(method, []).append(effect)
            method_effects = {
                method: _effect_stats(values)
                for method, values in sorted(by_method.items())
            }
            method_means = {
                method: float(stats["mean"])
                for method, stats in method_effects.items()
                if stats["mean"] is not None
            }
            if method_means:
                best_method = max(method_means, key=lambda key: method_means[key])
                weakest_method = min(method_means, key=lambda key: method_means[key])
                mean_range = method_means[best_method] - method_means[weakest_method]
                signs = {1 if value > 0 else -1 if value < 0 else 0 for value in method_means.values()}
                if len(signs - {0}) > 1:
                    pattern = "direction_reversal_across_methods"
                elif mean_range > threshold:
                    pattern = "magnitude_gap_across_methods"
                else:
                    pattern = "near_threshold_or_distributional"
            else:
                best_method = None
                weakest_method = None
                mean_range = None
                pattern = "no_numeric_method_effects"

            method_std = float((report.get("metrics") or {}).get("method_sensitivity_std") or 0.0)
            margin = method_std - threshold
            aggregate_margins.append(margin)
            claims.append(
                {
                    "hypothesis_id": hypothesis_id,
                    "model": record["model"],
                    "failed_checks": failed,
                    "method_sensitivity_std": method_std,
                    "threshold": threshold,
                    "margin_over_threshold": margin,
                    "method_mean_range": mean_range,
                    "best_method_by_mean_effect": best_method,
                    "weakest_method_by_mean_effect": weakest_method,
                    "pattern": pattern,
                    "method_effects": method_effects,
                }
            )

        if claims:
            by_task[task].append(
                {
                    "bundle": record["bundle"],
                    "model": record["model"],
                    "claims": claims,
                }
            )

    populated = {task: blocks for task, blocks in by_task.items() if blocks}
    n_claims = sum(len(block["claims"]) for blocks in populated.values() for block in blocks)
    return {
        "description": (
            "Raw per-method treatment-effect forensics for claims in zero-accepted tasks "
            "that fail method_sensitivity. These rows explain residual instability; they "
            "do not relax or reinterpret the gate."
        ),
        "n_method_sensitivity_failed_claims": n_claims,
        "max_margin_over_threshold": max(aggregate_margins) if aggregate_margins else None,
        "per_task": populated,
    }


def main() -> None:
    records = evaluate_bundle_records(REAL_MULTI_TASK_DIR, REAL_MULTILANE_DIR, use_cached_results=True)
    rows = iter_claim_rows(records)
    task_counts: dict[str, dict[str, int]] = {}
    for row in rows:
        block = task_counts.setdefault(str(row["task"]), {"claims": 0, "accepted": 0})
        block["claims"] += 1
        block["accepted"] += int(bool(row["passed"]))
    zero_tasks = tuple(sorted(task for task, block in task_counts.items() if block["accepted"] == 0))

    per_task: dict[str, dict] = {}
    for task in zero_tasks:
        task_rows = [r for r in rows if r["task"] == task]
        per_task[task] = _summarize_rows(task_rows)

    aggregate_rows = [r for r in rows if r["task"] in zero_tasks]
    aggregate = _summarize_rows(aggregate_rows)
    method_forensics = _method_sensitivity_forensics(records, zero_tasks)

    payload = {
        "schema_version": 2,
        "generated_by": "main/zero_task_gate_breakdown.py",
        "source_artifacts": [
            "main/output/real_multi_task/**",
            "main/output/real_multilane/**",
            "main/output/zero_task_real_repair/**",
        ],
        "zero_task_set": list(zero_tasks),
        "task_acceptance_counts": task_counts,
        "per_task": per_task,
        "aggregate": aggregate,
        "method_sensitivity_forensics": method_forensics,
        "interpretation_notes": [
            "single_gate_only_count is the UPPER BOUND on how many "
            "claims a single-gate relaxation could affect: a claim "
            "that failed exactly one gate is the only kind of claim "
            "that a one-gate change can possibly flip. It is NOT a "
            "count of claims that would pass under any specific "
            "relaxation; the killing gate may be failing for a "
            "principled reason that no defensible relaxation "
            "addresses (e.g., causal_effect below a floor that is "
            "itself the contract's minimum viable effect size).",
            "multi_gate_count is a hard lower bound on how many "
            "claims cannot be rescued by any single-gate change. "
            "If this dominates for a given task, the F-019 fix path "
            "of 'targeted re-discovery to find one accepted claim' "
            "is low-yield for that task and an operator should "
            "instead invest in the discovery lane that produced "
            "the claims (e.g., B3 for fact_recall_v0).",
            "top_failed_combinations surfaces whether multi-gate "
            "failures cluster in a coherent pattern (e.g., "
            "'robustness + confirmatory_ci' co-fail, suggesting an "
            "underpowered bundle) or spread across unrelated gates "
            "(suggesting the claim is simply wrong).",
            "rejected_with_no_failed_gate counts claims that were "
            "rejected without a named failed gate (typically via "
            "tier-gating or not-evaluated paths). These are not "
            "rescuable by any gate relaxation.",
            "Diagnostic artifact only. This script does NOT "
            "promote any claim, does NOT lower any gate, and does "
            "NOT change headline numbers; it only reflects the current "
            "released bundle surface.",
            "method_sensitivity_forensics records raw per-method treatment "
            "effects for residual zero-task method-sensitivity failures. "
            "A large activation-patching versus ablation gap is evidence "
            "for method-dependent causal structure, not a reason to delete "
            "the robustness gate post hoc.",
        ],
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(str(OUTPUT_PATH))
    for task in zero_tasks:
        block = per_task[task]
        top_gate = max(block["failed_gate_counts"].items(), key=lambda kv: kv[1], default=(None, 0))
        print(
            f"  {task}: n_claims={block['n_claims']}, "
            f"failed={block['n_failed']}, "
            f"single-gate-only={block['single_gate_only_count']}, "
            f"multi-gate={block['multi_gate_count']}"
            + (f", top_gate={top_gate[0]}({top_gate[1]})" if top_gate[0] else "")
        )
    agg = aggregate
    print(
        f"  AGGREGATE: n_claims={agg['n_claims']}, "
        f"single-gate-only={agg['single_gate_only_count']}, "
        f"multi-gate={agg['multi_gate_count']}"
    )


if __name__ == "__main__":
    main()
