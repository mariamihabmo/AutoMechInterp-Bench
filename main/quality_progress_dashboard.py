#!/usr/bin/env python3
"""Generate a quality progress dashboard from canonical artifacts.

Records a baseline snapshot of the canonical metrics and compares each later
snapshot against it, surfacing both improvements and regressions explicitly so
that negative movements are not washed out by prose.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from _bundle_analysis import generated_at_utc, write_json, write_text
except ModuleNotFoundError:
    from main._bundle_analysis import generated_at_utc, write_json, write_text

ROOT = Path(__file__).resolve().parents[1]
REPRO = ROOT / "main" / "output" / "repro"
BASELINE = REPRO / "quality_dashboard_baseline_2026-05-04_pre_final_pass.json"
OUT_JSON = REPRO / "quality_progress_dashboard.json"
OUT_MD = REPRO / "quality_progress_dashboard.md"

METRIC_POLICY: dict[str, dict[str, str]] = {
    "headline_check": {"label": "Headline/prose drift check", "direction": "higher"},
    "overclaim_check": {"label": "Release overclaim guard", "direction": "higher"},
    "compile_check": {"label": "Python compile check", "direction": "higher"},
    "pytest_check": {"label": "Evaluator+runner tests", "direction": "higher"},
    "bundles": {"label": "Evaluated bundles", "direction": "neutral"},
    "claims": {"label": "Evaluated claims", "direction": "neutral"},
    "accepted_claims": {"label": "Accepted claims", "direction": "neutral"},
    "tasks_with_accepted": {"label": "Tasks with accepted claims", "direction": "higher"},
    "zero_task_model_cells": {"label": "Zero-accepted task-model cells", "direction": "lower"},
    "transfer_confirmed": {"label": "Transfer-confirmed accepted claims", "direction": "higher"},
    "prompt_release_claims_pass": {"label": "Released prompt-holdout claims passing", "direction": "higher"},
    "prompt_high_power_covered": {"label": "High-power prompt claims covered", "direction": "higher"},
    "prompt_high_power_retained": {"label": "High-power prompt retained claims", "direction": "higher"},
    "prompt_high_power_demoted": {"label": "High-power prompt demoted claims", "direction": "lower"},
    "prompt_high_power_all_holdouts": {"label": "High-power retained claims passing all holdouts", "direction": "higher"},
    "prompt_high_power_checks_pass": {"label": "High-power held-out checks passing", "direction": "higher"},
    "prompt_n100_completion": {"label": "n=100 prompt-holdout completion", "direction": "higher"},
    "fresh_agnostic_far": {"label": "Release-grade fresh agnostic FAR (full budget, release_grade_2026q2)", "direction": "lower"},
    "fresh_agnostic_far_reduced_rehearsal": {"label": "Reduced-rehearsal fresh agnostic FAR (128/128, rotated_2026q2)", "direction": "lower"},
    "v1_retained_claims": {"label": "V1 retained accepted claims", "direction": "higher"},
    "v1_tasks_retained": {"label": "V1 retained task breadth", "direction": "higher"},
    "runtime_coverage": {"label": "Measured runtime coverage", "direction": "higher"},
    "external_blinded_evaluated": {"label": "External blinded submissions evaluated", "direction": "higher"},
    "external_holdout_executions": {"label": "External-custodian holdout executions", "direction": "higher"},
    "independent_goodhart_validations": {"label": "Independent Goodhart validations", "direction": "higher"},
}

def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}

def _ratio(num: int | float, den: int | float | None = None) -> dict[str, Any]:
    value = float(num) / float(den) if den else float(num)
    return {"num": num, "den": den, "value": value}

def _status_ratio(status: str) -> dict[str, Any]:
    return {"status": status, "value": 1.0 if status == "pass" else 0.0}

def _run_command(name: str, cmd: list[str], *, timeout: int) -> dict[str, Any]:
    started = datetime.now(timezone.utc)
    try:
        result = subprocess.run(
            cmd,
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout,
            check=False,
        )
        status = "pass" if result.returncode == 0 else "fail"
        return {
            "name": name,
            "cmd": cmd,
            "status": status,
            "returncode": result.returncode,
            "started_at_utc": started.isoformat(timespec="seconds"),
            "duration_seconds": (datetime.now(timezone.utc) - started).total_seconds(),
            "stdout_tail": result.stdout[-2000:],
            "stderr_tail": result.stderr[-2000:],
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "name": name,
            "cmd": cmd,
            "status": "timeout",
            "returncode": None,
            "started_at_utc": started.isoformat(timespec="seconds"),
            "duration_seconds": timeout,
            "stdout_tail": (exc.stdout or "")[-2000:] if isinstance(exc.stdout, str) else "",
            "stderr_tail": (exc.stderr or "")[-2000:] if isinstance(exc.stderr, str) else "",
        }

def run_health_checks(*, include_tests: bool) -> dict[str, Any]:
    commands = [
        ("headline_check", [sys.executable, "tools/check_headline_numbers.py"], 120),
        ("overclaim_check", [sys.executable, "tools/check_release_overclaims.py"], 120),
        (
            "compile_check",
            [
                sys.executable,
                "-m",
                "compileall",
                "-q",
                "main",
                "packages/evaluator/src",
                "packages/runner/src",
            ],
            180,
        ),
    ]
    if include_tests:
        commands.append(
            (
                "pytest_check",
                [
                    sys.executable,
                    "-m",
                    "pytest",
                    "packages/evaluator/tests",
                    "packages/runner/tests",
                    "-q",
                ],
                600,
            )
        )
    return {name: _run_command(name, cmd, timeout=timeout) for name, cmd, timeout in commands}

def collect_metrics(health: dict[str, Any] | None = None) -> dict[str, Any]:
    breadth = _load(REPRO / "benchmark_breadth_summary.json")
    field = _load(REPRO / "field_level_findings.json")
    transfer = _load(REPRO / "transfer_results_summary.json")
    breadth_gap = _load(REPRO / "breadth_gap_analysis.json")
    prompt_holdout = _load(REPRO / "prompt_holdout_transfer_control.json")
    high_power = _load(REPRO / "prompt_holdout_high_power_n40_rerun.json")
    high_power_100 = _load(REPRO / "prompt_holdout_high_power_n100_rerun.json")
    fresh_agnostic = _load(REPRO / "stress_test_agnostic_fresh_release_grade.json")
    # Reduced-rehearsal fresh cell (rotated namespace, 128/128 budget). Audit
    # 2026-05 made the dual-budget cells visible in the dashboard so that the
    # release-grade 0/200 vs reduced-rehearsal 49/200 spread is not silently
    # collapsed onto a single "fresh" row.
    fresh_agnostic_reduced = _load(REPRO / "stress_test_agnostic_fresh.json")
    hardening = _load(REPRO / "contract_hardening_v1_summary.json")
    runtime = _load(REPRO / "runtime_cost_report.json")
    holdout = _load(ROOT / "holdout" / "results_summary.json")
    migration = _load(REPRO / "contract_hardening_v1_migration_decision.json")

    acceptance_by_task = field.get("acceptance_by_task") or {}
    tasks_with_accepted = sum(1 for row in acceptance_by_task.values() if int(row.get("accepted", 0)) > 0)
    tasks_total = len(acceptance_by_task)
    fresh_full = (fresh_agnostic.get("conditions") or {}).get("full_contract") or {}
    external = holdout.get("external_blinded") or {}
    runtime_measured = float(
        runtime.get("measured_bundle_count")
        or runtime.get("measured_bundles")
        or runtime.get("bundles_measured")
        or 0
    )
    runtime_total = float(
        runtime.get("bundle_count")
        or runtime.get("total_bundles")
        or runtime.get("bundles_profiled")
        or (runtime.get("totals") or {}).get("bundles")
        or breadth.get("bundle_count")
        or 0
    )

    metrics: dict[str, Any] = {
        "bundles": _ratio(int(breadth.get("bundle_count") or 0)),
        "claims": _ratio(int(breadth.get("claim_count") or 0)),
        "accepted_claims": _ratio(int((field.get("totals") or {}).get("accepted") or 0), int((field.get("totals") or {}).get("claims") or 0)),
        "tasks_with_accepted": _ratio(tasks_with_accepted, tasks_total),
        "zero_task_model_cells": _ratio(int(breadth_gap.get("n_zero_acceptance_cells") or 0), int(breadth_gap.get("n_cells") or 0)),
        "transfer_confirmed": _ratio(int(transfer.get("transfer_confirmed_claims") or 0), int(transfer.get("accepted_claims_tested") or 0)),
        "prompt_release_claims_pass": _ratio(int(prompt_holdout.get("claims_passing_all_holdouts") or 0), int(prompt_holdout.get("accepted_claims_with_multi_prompt") or 0)),
        "prompt_high_power_covered": _ratio(int(high_power.get("original_accepted_claims_covered") or 0)),
        "prompt_high_power_retained": _ratio(int(high_power.get("original_accepted_claims_retained") or 0), int(high_power.get("original_accepted_claims_covered") or 0)),
        "prompt_high_power_demoted": _ratio(int(high_power.get("original_accepted_claims_demoted") or 0), int(high_power.get("original_accepted_claims_covered") or 0)),
        "prompt_high_power_all_holdouts": _ratio(int(high_power.get("retained_original_accepted_claims_passing_all_holdouts") or 0), int(high_power.get("original_accepted_claims_retained") or 0)),
        "prompt_high_power_checks_pass": _ratio(int(high_power.get("passing_holdout_checks_on_retained_claims") or 0), int(high_power.get("total_holdout_checks_on_retained_claims") or 0)),
        "prompt_n100_completion": _ratio(int(high_power_100.get("bundles_rerun") or 0), int(high_power_100.get("planned_bundles") or 0)),
        "fresh_agnostic_far": _ratio(int(fresh_full.get("leaked") or 0), int(fresh_full.get("total") or fresh_agnostic.get("negatives") or 0)),
        "fresh_agnostic_far_reduced_rehearsal": _ratio(
            int(((fresh_agnostic_reduced.get("conditions") or {}).get("full_contract") or {}).get("leaked") or 0),
            int(((fresh_agnostic_reduced.get("conditions") or {}).get("full_contract") or {}).get("total") or fresh_agnostic_reduced.get("negatives") or 0),
        ),
        "v1_retained_claims": _ratio(int(hardening.get("accepted_claims_after_total") or 0), int(hardening.get("accepted_claims_before_total") or 0)),
        "v1_tasks_retained": _ratio(
            int(hardening.get("tasks_with_accepted_after_count") or 0),
            int(hardening.get("tasks_with_accepted_before_count") or tasks_total or 0),
        ),
        "runtime_coverage": _ratio(runtime_measured, runtime_total),
        "external_blinded_evaluated": _ratio(int(external.get("n_evaluated") or 0)),
        "external_holdout_executions": _ratio(1 if int(external.get("n_evaluated") or 0) > 0 else 0),
        "independent_goodhart_validations": _ratio(1 if bool(migration.get("independent_evidence_criterion_satisfied")) else 0),
    }
    health = health or {}
    for key in ("headline_check", "overclaim_check", "compile_check", "pytest_check"):
        metrics[key] = _status_ratio((health.get(key) or {}).get("status", "not_run"))
    return metrics

def _value(metric: dict[str, Any]) -> float:
    return float(metric.get("value") or 0.0)

def _format_metric(metric: dict[str, Any]) -> str:
    if "status" in metric:
        return str(metric["status"])
    num = metric.get("num")
    den = metric.get("den")
    if den is None:
        if isinstance(num, float) and not num.is_integer():
            return f"{num:.3f}"
        return str(int(num) if isinstance(num, float) and num.is_integer() else num)
    if float(den) == 0:
        return f"{num}/0"
    return f"{num}/{den} ({_value(metric) * 100:.2f}%)"

def _movement(name: str, baseline: dict[str, Any], current: dict[str, Any]) -> dict[str, str]:
    direction = METRIC_POLICY[name]["direction"]
    old = _value(baseline)
    new = _value(current)
    if abs(new - old) < 1e-12:
        return {"movement": "unchanged", "quality_effect": "unchanged"}
    raw = "up" if new > old else "down"
    if direction == "neutral":
        effect = "changed"
    elif (direction == "higher" and new > old) or (direction == "lower" and new < old):
        effect = "improved"
    else:
        effect = "worsened"
    return {"movement": raw, "quality_effect": effect}

def build_payload(*, baseline_path: Path, health: dict[str, Any] | None = None) -> dict[str, Any]:
    current_metrics = collect_metrics(health)
    baseline_payload = _load(baseline_path)
    baseline_metrics = baseline_payload.get("metrics") or current_metrics
    comparisons = {}
    for name in METRIC_POLICY:
        comparisons[name] = {
            "label": METRIC_POLICY[name]["label"],
            "direction": METRIC_POLICY[name]["direction"],
            "baseline": baseline_metrics.get(name, _ratio(0)),
            "current": current_metrics.get(name, _ratio(0)),
            **_movement(name, baseline_metrics.get(name, _ratio(0)), current_metrics.get(name, _ratio(0))),
        }
    blockers = [
        name
        for name in (
            "external_blinded_evaluated",
            "external_holdout_executions",
            "independent_goodhart_validations",
        )
        if _value(current_metrics[name]) <= 0
    ]
    return {
        "generated_by": "main/quality_progress_dashboard.py",
        "generated_at_utc": generated_at_utc(),
        "baseline_path": str(baseline_path.relative_to(ROOT)) if baseline_path.exists() else str(baseline_path),
        "baseline_generated_at_utc": baseline_payload.get("generated_at_utc"),
        "metrics": current_metrics,
        "comparisons": comparisons,
        "health_checks": health or {},
        "no_human_provenance_blockers": blockers,
        "claim_boundary": (
            "This dashboard tracks local artifact quality progress. "
            "It does not convert maintainer-authored runs into external blinded submissions, "
            "external-custodian holdout executions, or independent Goodhart validation."
        ),
    }

def format_md(payload: dict[str, Any]) -> str:
    lines = [
        "# Quality Progress Dashboard",
        "",
        payload["claim_boundary"],
        "",
        f"- Generated: **{payload['generated_at_utc']}**",
        f"- Baseline: `{payload['baseline_path']}`",
        f"- Open no-human provenance blockers: **{', '.join(payload['no_human_provenance_blockers']) or 'none'}**",
        "",
        "| Metric | Direction | Baseline | Current | Movement | Quality effect |",
        "|---|---|---:|---:|---|---|",
    ]
    for name, row in payload["comparisons"].items():
        lines.append(
            f"| {row['label']} | {row['direction']} | {_format_metric(row['baseline'])} | "
            f"{_format_metric(row['current'])} | {row['movement']} | {row['quality_effect']} |"
        )
    lines.extend(
        [
            "",
            "## Stress-row source caveat (2026-05 audit)",
            "",
            "The `Release-grade fresh agnostic FAR` row's *baseline* number"
            " (42/200, 21.0%) was sourced from `stress_test_agnostic_fresh.json`"
            " under a 128/128 reduced statistical budget on the `rotated_2026q2`"
            " seed namespace; the *current* number (0/200, 0.0%) is sourced from"
            " `stress_test_agnostic_fresh_release_grade.json` under the full"
            " default statistical budget on the `release_grade_2026q2` seed"
            " namespace. The baseline-to-current movement therefore reflects"
            " both an artifact change AND a (budget, namespace) change; the"
            " new `Reduced-rehearsal fresh agnostic FAR` row makes the"
            " reduced-budget cell visible separately so the dual-budget spread"
            " is not silently collapsed onto a single \"fresh\" row.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"

def main() -> None:
    parser = argparse.ArgumentParser(description="Generate quality progress dashboard")
    parser.add_argument("--baseline", type=Path, default=BASELINE)
    parser.add_argument("--write-baseline", action="store_true")
    parser.add_argument("--run-health-checks", action="store_true")
    parser.add_argument("--include-tests", action="store_true")
    parser.add_argument("--json-out", type=Path, default=OUT_JSON)
    parser.add_argument("--md-out", type=Path, default=OUT_MD)
    args = parser.parse_args()

    health = run_health_checks(include_tests=args.include_tests) if args.run_health_checks else None
    payload = build_payload(baseline_path=args.baseline, health=health)

    if args.write_baseline:
        baseline_payload = {
            "generated_by": "main/quality_progress_dashboard.py --write-baseline",
            "generated_at_utc": payload["generated_at_utc"],
            "metrics": payload["metrics"],
            "claim_boundary": payload["claim_boundary"],
        }
        write_json(args.baseline, baseline_payload)
        # Rebuild comparisons against the just-written baseline.
        payload = build_payload(baseline_path=args.baseline, health=health)

    write_json(args.json_out, payload)
    write_text(args.md_out, format_md(payload))
    print(str(args.json_out))

if __name__ == "__main__":
    main()
