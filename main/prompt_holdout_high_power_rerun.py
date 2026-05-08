#!/usr/bin/env python3
"""High-power diagnostic rerun for prompt-holdout robustness.

This script does not change the released contract. It prospectively reruns the
current canonical bundles that contain accepted claims and multiple prompt
variants, using the existing task-supported prompt grid at a larger
``examples_per_cell``. It then asks whether the originally accepted claims are:

1. still accepted under the higher-power rerun, and
2. stable under a held-out-prompt control computed from the rerun raw cells.

The purpose is to make prompt-holdout weakness measurable without cherry-picking
only the current failures. If claims demote under higher-powered data, that is
evidence against them; it must not be hidden as a robustness gain.
"""

from __future__ import annotations

import argparse
import json
import shutil
import statistics
import sys
import time
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "packages" / "evaluator" / "src"))
sys.path.insert(0, str(ROOT / "packages" / "runner" / "src"))

from automechinterp_evaluator.evaluator import evaluate_bundle  # noqa: E402

# Audit-final §2.D.5: the retention denominator is now floored at
# ``CROSS_MODEL_EFFECT_FLOOR`` rather than ``1e-12``. Using ``1e-12`` made
# claims with near-zero source effects produce nonsense retention ratios
# (e.g. 1e10) that flowed into downstream histograms. Flooring at the same
# epsilon already used as the cross-model gate threshold keeps "retention"
# bounded and consistent with the gate semantics.
try:
    from automechinterp_evaluator.constants import CROSS_MODEL_EFFECT_FLOOR as _RETENTION_EPS
except Exception:  # pragma: no cover - defensive fallback
    _RETENTION_EPS = 1e-3
from automechinterp_evaluator.reporting import build_markdown_report  # noqa: E402
from automechinterp_runner.runner import Stage2Config, run_stage2  # noqa: E402
from main._bundle_analysis import (  # noqa: E402
    REAL_MULTILANE_DIR,
    REAL_MULTI_TASK_DIR,
    _load_cached_or_evaluate_bundle,
    find_bundle_dirs,
    read_jsonl,
    read_yaml,
    write_json,
    write_text,
)

REPRO = ROOT / "main" / "output" / "repro"
OUT_DIR = ROOT / "main" / "output" / "prompt_holdout_high_power_n100"
OUT_JSON = REPRO / "prompt_holdout_high_power_n100_rerun.json"
OUT_MD = REPRO / "prompt_holdout_high_power_n100_rerun.md"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def _accepted_ids(result: dict[str, Any]) -> set[str]:
    return {str(row["hypothesis_id"]) for row in result.get("claim_reports", []) if row.get("passed")}


def _mean(values: list[float]) -> float:
    return statistics.mean(values) if values else 0.0


def _sign(value: float) -> int:
    if value > 0:
        return 1
    if value < 0:
        return -1
    return 0


def _candidate_bundles() -> list[Path]:
    bundles: list[Path] = []
    for bundle_dir in find_bundle_dirs(REAL_MULTI_TASK_DIR, REAL_MULTILANE_DIR):
        protocol = read_yaml(bundle_dir / "protocol.yaml")
        prompt_variants = list(protocol.get("execution_grid", {}).get("prompt_variants", []) or [])
        if len(prompt_variants) < 2:
            continue
        current = _load_cached_or_evaluate_bundle(bundle_dir)
        if _accepted_ids(current):
            bundles.append(bundle_dir)
    return sorted(bundles, key=lambda path: path.name)


def _copy_bundle_inputs(source: Path, target: Path, *, examples_per_cell: int) -> dict[str, Any]:
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True, exist_ok=True)
    protocol = yaml.safe_load((source / "protocol.yaml").read_text())
    protocol = json.loads(json.dumps(protocol))
    protocol["protocol_id"] = f"{protocol['protocol_id']}_prompt_holdout_high_power_n{examples_per_cell}"
    protocol["protocol_version"] = (
        f"{protocol.get('protocol_version', '1.0')}-prompt_holdout_high_power_n{examples_per_cell}"
    )
    (target / "protocol.yaml").write_text(yaml.safe_dump(protocol, sort_keys=False))

    lines: list[str] = []
    for row in read_jsonl(source / "hypothesis.jsonl"):
        row = dict(row)
        row["protocol_id"] = protocol["protocol_id"]
        lines.append(json.dumps(row, sort_keys=False))
    (target / "hypothesis.jsonl").write_text("\n".join(lines) + ("\n" if lines else ""))
    return protocol


def _prompt_holdout_for_claim(
    *,
    bundle_dir: Path,
    protocol: dict[str, Any],
    hypothesis_id: str,
) -> dict[str, Any]:
    prompt_variants = [str(v) for v in protocol.get("execution_grid", {}).get("prompt_variants", [])]
    raw_eval = _load_json(bundle_dir / "evaluation_result.json")
    raw_rows = {
        row["hypothesis_id"]: row.get("raw_cells", [])
        for row in raw_eval.get("hypothesis_results", [])
    }
    cells = [
        cell
        for cell in raw_rows.get(hypothesis_id, [])
        if str(cell.get("slice", "confirmatory")) == "confirmatory"
    ]
    by_prompt = {
        variant: [
            float(cell["treatment_effect"])
            for cell in cells
            if str(cell.get("prompt_variant")) == variant
        ]
        for variant in prompt_variants
    }
    floor = float(protocol.get("stage_gates", {}).get("min_causal_effect", 0.02))
    holdouts: list[dict[str, Any]] = []
    all_pass = bool(prompt_variants) and all(by_prompt.values())
    for holdout_variant in prompt_variants:
        source_values = [
            value
            for variant, values in by_prompt.items()
            if variant != holdout_variant
            for value in values
        ]
        holdout_values = by_prompt.get(holdout_variant, [])
        source_mean = _mean(source_values)
        holdout_mean = _mean(holdout_values)
        same_direction = _sign(source_mean) != 0 and _sign(source_mean) == _sign(holdout_mean)
        above_floor = abs(holdout_mean) >= floor
        passes = bool(source_values and holdout_values and same_direction and above_floor)
        all_pass = all_pass and passes
        holdouts.append(
            {
                "holdout_prompt_variant": holdout_variant,
                "source_mean": source_mean,
                "holdout_mean": holdout_mean,
                "same_direction": same_direction,
                "above_floor": above_floor,
                "passes": passes,
                "n_source_cells": len(source_values),
                "n_holdout_cells": len(holdout_values),
                "retention_ratio": abs(holdout_mean) / max(abs(source_mean), _RETENTION_EPS),
            }
        )
    return {"all_holdouts_pass": all_pass, "holdouts": holdouts}


def _summarize_existing(candidates: list[Path], *, examples_per_cell: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for source in candidates:
        target = OUT_DIR / source.name
        if not (target / "evaluation_result_current.json").exists():
            continue
        source_result = _load_cached_or_evaluate_bundle(source)
        target_result = _load_json(target / "evaluation_result_current.json")
        source_accepted = _accepted_ids(source_result)
        target_accepted = _accepted_ids(target_result)
        protocol = read_yaml(target / "protocol.yaml")
        originally_accepted_rows: list[dict[str, Any]] = []
        for hid in sorted(source_accepted):
            holdout = _prompt_holdout_for_claim(
                bundle_dir=target,
                protocol=protocol,
                hypothesis_id=hid,
            )
            retained = hid in target_accepted
            originally_accepted_rows.append(
                {
                    "hypothesis_id": hid,
                    "retained": retained,
                    "all_holdouts_pass": bool(retained and holdout["all_holdouts_pass"]),
                    "holdouts": holdout["holdouts"],
                }
            )
        rows.append(
            {
                "bundle": source.name,
                "source_bundle": str(source.relative_to(ROOT)),
                "rerun_bundle": str(target.relative_to(ROOT)),
                "task": protocol["unit_of_work"]["task_id"],
                "model": protocol["unit_of_work"]["model_id"],
                "examples_per_cell": examples_per_cell,
                "prompt_variants": list(protocol.get("execution_grid", {}).get("prompt_variants", [])),
                "accepted_before": len(source_accepted),
                "accepted_after": len(target_accepted),
                "retained_originally_accepted": sum(1 for row in originally_accepted_rows if row["retained"]),
                "demoted_originally_accepted": sum(1 for row in originally_accepted_rows if not row["retained"]),
                "retained_and_prompt_holdout_pass": sum(
                    1 for row in originally_accepted_rows if row["retained"] and row["all_holdouts_pass"]
                ),
                "originally_accepted_claims": originally_accepted_rows,
            }
        )
    return rows


def _write_summary(
    rows: list[dict[str, Any]],
    *,
    planned_bundles: int,
    examples_per_cell: int,
) -> None:
    original_claims = sum(row["accepted_before"] for row in rows)
    retained = sum(row["retained_originally_accepted"] for row in rows)
    demoted = sum(row["demoted_originally_accepted"] for row in rows)
    retained_holdout = sum(row["retained_and_prompt_holdout_pass"] for row in rows)
    total_holdout_checks = sum(
        len(claim["holdouts"])
        for row in rows
        for claim in row["originally_accepted_claims"]
        if claim["retained"]
    )
    passing_holdout_checks = sum(
        int(holdout["passes"])
        for row in rows
        for claim in row["originally_accepted_claims"]
        if claim["retained"]
        for holdout in claim["holdouts"]
    )
    failing_claims = [
        {
            "bundle": row["bundle"],
            "hypothesis_id": claim["hypothesis_id"],
            "retained": claim["retained"],
            "all_holdouts_pass": claim["all_holdouts_pass"],
            "failed_holdouts": [
                holdout["holdout_prompt_variant"]
                for holdout in claim["holdouts"]
                if not holdout["passes"]
            ],
        }
        for row in rows
        for claim in row["originally_accepted_claims"]
        if (not claim["retained"]) or (not claim["all_holdouts_pass"])
    ]
    completion_status = "complete" if len(rows) == planned_bundles else "partial"
    payload = {
        "schema_version": 1,
        "generated_by": "main/prompt_holdout_high_power_rerun.py",
        "status": (
            "diagnostic high-power prompt-holdout rerun; "
            f"{completion_status}; not a released-contract change"
        ),
        "completion_status": completion_status,
        "examples_per_cell": examples_per_cell,
        "planned_bundles": planned_bundles,
        "bundles_rerun": len(rows),
        "original_accepted_claims_covered": original_claims,
        "original_accepted_claims_retained": retained,
        "original_accepted_claims_demoted": demoted,
        "retained_original_accepted_claims_passing_all_holdouts": retained_holdout,
        "retained_original_accepted_claims_failing_any_holdout": retained - retained_holdout,
        "passing_holdout_checks_on_retained_claims": passing_holdout_checks,
        "total_holdout_checks_on_retained_claims": total_holdout_checks,
        "failing_or_demoted_original_claims": failing_claims,
        "rows": rows,
        "claim_boundary": (
            "This prospective diagnostic covers every current canonical bundle with accepted claims and multiple prompt variants. "
            "It must be reported as a high-power robustness frontier, not as external validation or a silent contract migration."
        ),
    }
    write_json(OUT_JSON, payload)

    lines = [
        "# High-Power Prompt-Holdout Rerun",
        "",
        payload["claim_boundary"],
        "",
        f"- Completion status: **{completion_status}**",
        f"- Examples per cell: **{examples_per_cell}**",
        f"- Planned bundles: **{planned_bundles}**",
        f"- Bundles rerun: **{len(rows)}**",
        f"- Original accepted claims covered: **{original_claims}**",
        f"- Original accepted claims retained: **{retained}**",
        f"- Original accepted claims demoted: **{demoted}**",
        f"- Retained original accepted claims passing all held-out prompts: **{retained_holdout}/{retained}**",
        f"- Passing held-out prompt checks on retained claims: **{passing_holdout_checks}/{total_holdout_checks}**",
        "",
        "## Bundle Summary",
        "",
        "| Bundle | Task | Model | Accepted before | Retained | Demoted | Retained + all holdouts pass |",
        "|---|---|---|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| `{row['bundle']}` | `{row['task']}` | `{row['model']}` | "
            f"{row['accepted_before']} | {row['retained_originally_accepted']} | "
            f"{row['demoted_originally_accepted']} | {row['retained_and_prompt_holdout_pass']} |"
        )
    lines.extend(["", "## Failing Or Demoted Original Claims", ""])
    if not failing_claims:
        lines.append("- None.")
    else:
        for row in failing_claims:
            if row["retained"]:
                lines.append(
                    f"- `{row['bundle']}` / `{row['hypothesis_id']}`: retained but failed holdouts {row['failed_holdouts']}"
                )
            else:
                lines.append(
                    f"- `{row['bundle']}` / `{row['hypothesis_id']}`: demoted under the high-power rerun"
                )
    write_text(OUT_MD, "\n".join(lines).rstrip() + "\n")


def _run_one(source: Path, *, device: str, examples_per_cell: int) -> None:
    target = OUT_DIR / source.name
    protocol = _copy_bundle_inputs(source, target, examples_per_cell=examples_per_cell)
    started = time.time()
    run_stage2(
        Stage2Config(
            bundle_dir=target,
            mode="real",
            device=device,
            examples_per_cell=examples_per_cell,
            exploratory_fraction=float(protocol.get("sample_size_policy", {}).get("exploratory_fraction", 0.3)),
        )
    )
    result = evaluate_bundle(target)
    (target / "evaluation_result_current.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    (target / "stage_gate_report.md").write_text(build_markdown_report(result))
    (target / "runtime_prompt_holdout_high_power.json").write_text(
        json.dumps(
            {
                "generated_by": "main/prompt_holdout_high_power_rerun.py",
                "runtime_seconds": time.time() - started,
                "examples_per_cell": examples_per_cell,
                "device": device,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )


def main() -> None:
    global OUT_DIR, OUT_JSON, OUT_MD
    parser = argparse.ArgumentParser(description="Run high-power prompt-holdout diagnostics")
    parser.add_argument("--device", default="cpu", choices=["cpu", "mps", "cuda"],
                        help="Inference device. Defaults to 'cpu' for cross-platform reproducibility; pass --device mps on Apple silicon or --device cuda on Linux GPUs to enable hardware acceleration.")
    parser.add_argument("--examples-per-cell", type=int, default=100)
    parser.add_argument(
        "--out-dir",
        default="",
        help="Optional output directory. Defaults to main/output/prompt_holdout_high_power_n<examples>.",
    )
    parser.add_argument(
        "--out-json",
        default="",
        help="Optional summary JSON path. Defaults to main/output/repro/prompt_holdout_high_power_n<examples>_rerun.json.",
    )
    parser.add_argument(
        "--out-md",
        default="",
        help="Optional summary Markdown path. Defaults to main/output/repro/prompt_holdout_high_power_n<examples>_rerun.md.",
    )
    parser.add_argument("--bundle", action="append", default=[], help="Optional exact bundle name; repeatable")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--summarize-existing", action="store_true")
    args = parser.parse_args()

    OUT_DIR = (
        Path(args.out_dir).resolve()
        if args.out_dir
        else ROOT / "main" / "output" / f"prompt_holdout_high_power_n{args.examples_per_cell}"
    )
    OUT_JSON = (
        Path(args.out_json).resolve()
        if args.out_json
        else REPRO / f"prompt_holdout_high_power_n{args.examples_per_cell}_rerun.json"
    )
    OUT_MD = (
        Path(args.out_md).resolve()
        if args.out_md
        else REPRO / f"prompt_holdout_high_power_n{args.examples_per_cell}_rerun.md"
    )

    candidates = _candidate_bundles()
    if args.bundle:
        wanted = set(args.bundle)
        candidates = [path for path in candidates if path.name in wanted]
    planned_bundles = len(candidates)

    rows_by_bundle = {row["bundle"]: row for row in _summarize_existing(candidates, examples_per_cell=args.examples_per_cell)}
    if args.summarize_existing:
        _write_summary(
            [rows_by_bundle[name] for name in sorted(rows_by_bundle)],
            planned_bundles=planned_bundles,
            examples_per_cell=args.examples_per_cell,
        )
        print(str(OUT_JSON))
        return

    todo = [path for path in candidates if path.name not in rows_by_bundle]
    if args.limit > 0:
        todo = todo[: args.limit]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for idx, source in enumerate(todo, start=1):
        print(f"[{idx}/{len(todo)}] high-power prompt-holdout rerun {source.name}", flush=True)
        _run_one(source, device=args.device, examples_per_cell=args.examples_per_cell)
        rows_by_bundle = {
            row["bundle"]: row
            for row in _summarize_existing(candidates, examples_per_cell=args.examples_per_cell)
        }
        _write_summary(
            [rows_by_bundle[name] for name in sorted(rows_by_bundle)],
            planned_bundles=planned_bundles,
            examples_per_cell=args.examples_per_cell,
        )

    _write_summary(
        [rows_by_bundle[name] for name in sorted(rows_by_bundle)],
        planned_bundles=planned_bundles,
        examples_per_cell=args.examples_per_cell,
    )
    print(str(OUT_JSON))


if __name__ == "__main__":
    main()
