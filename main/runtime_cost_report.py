#!/usr/bin/env python3
"""Summarize runtime and cost envelopes for evaluated bundles.

This script intentionally distinguishes:

* **Measured** bundles --- those with a recorded wall-clock time in
  ``main/output/real_multi_task/experiment_summary.json`` or a positive
  real-repair runtime in ``main/output/repro/zero_task_real_repair.json``.
* **Estimated** bundles --- those without a recorded wall-clock time, for
  which we extrapolate from the per-cell rate observed across measured
  bundles only.

Earlier versions of this script keyed the observed-time lookup by
``(task, model)`` alone, which meant that when several distinct bundles
shared the same ``(task, model)`` (for example, IOI/GPT-2 Small canonical
plus the multi-lane regenerations), they each inherited the *same*
observed wall-clock measurement. That over-attributed the observed time,
inflated the ``observed_runtime_seconds`` total, and biased the per-cell
baseline used to estimate the remaining bundles. The current
implementation deduplicates measurements at ``(task, model)`` granularity,
counts each measurement once, applies it to a single representative bundle
in that group (preferring the canonical ``real_multi_task`` bundle), and
estimates all other bundles from the per-cell rate derived strictly from
those deduplicated measurements and positive repair runtimes. Zero-valued
repair runtimes are treated as absent measurements, not free evaluations.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from _bundle_analysis import REAL_MULTILANE_DIR, REAL_MULTI_TASK_DIR, evaluate_bundle_records, pct, write_json, write_text


def _is_canonical_bundle(bundle_name: str, task: str, model: str) -> bool:
    """Return True if this bundle is the canonical ``task_model`` (no lane suffix)."""
    return bundle_name == f"{task}_{model}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Runtime and cost envelope for evaluated bundles")
    parser.add_argument("--reruns", type=int, default=3, help="Planned reruns for reproducibility budgeting")
    args = parser.parse_args()

    records = evaluate_bundle_records(REAL_MULTI_TASK_DIR, REAL_MULTILANE_DIR, use_cached_results=True)
    experiment_summary_path = REAL_MULTI_TASK_DIR / "experiment_summary.json"
    experiment_summary = (
        json.loads(experiment_summary_path.read_text())
        if experiment_summary_path.exists()
        else {"results": []}
    )
    # Deduplicate at (task, model) granularity. If multiple measurements exist
    # for the same key (rare), we use the most recent (last in list).
    measured_runtime: dict[tuple[str, str], float] = {}
    for row in experiment_summary.get("results", []):
        key = (row["task"], row["model"])
        if "time_seconds" in row:
            measured_runtime[key] = float(row["time_seconds"])

    # Collect each bundle's cell count up front (needed for per-cell baseline).
    bundle_meta: list[dict] = []
    for record in records:
        evaluation = json.loads((record["bundle_dir"] / "evaluation_result.json").read_text())
        cell_count = sum(len(row["raw_cells"]) for row in evaluation["hypothesis_results"])
        bundle_meta.append(
            {
                "bundle": record["bundle"],
                "task": record["task"],
                "model": record["model"],
                "claims": record["result"]["overall"]["hypothesis_count"],
                "raw_cells": cell_count,
            }
        )

    # For each (task, model) group with a measurement, pick exactly one bundle
    # to mark as "measured" --- preferring the canonical bundle when present
    # so that the canonical baseline numbers stay attached to the canonical
    # bundle row in the report.
    measured_bundle_names: dict[tuple[str, str], str] = {}
    for key in measured_runtime:
        candidates = [b for b in bundle_meta if (b["task"], b["model"]) == key]
        if not candidates:
            continue
        canonical = next(
            (b for b in candidates if _is_canonical_bundle(b["bundle"], b["task"], b["model"])),
            candidates[0],
        )
        measured_bundle_names[key] = canonical["bundle"]

    measured_by_bundle: dict[str, tuple[float, str]] = {}
    for key, bundle_name in measured_bundle_names.items():
        measured_by_bundle[bundle_name] = (measured_runtime[key], "measured_experiment_summary")

    zero_repair_path = Path(__file__).resolve().parents[1] / "main" / "output" / "repro" / "zero_task_real_repair.json"
    if zero_repair_path.exists():
        zero_repair = json.loads(zero_repair_path.read_text())
        for row in zero_repair.get("rows", []):
            runtime = float(row.get("runtime_seconds") or 0.0)
            bundle_name = str(row.get("bundle"))
            if runtime > 0:
                measured_by_bundle[bundle_name] = (runtime, "measured_zero_task_real_repair")

    meta_by_bundle = {row["bundle"]: row for row in bundle_meta}

    # Per-cell baseline derived ONLY from deduplicated measured bundles,
    # including measured real-repair replacement bundles when available.
    total_measured_seconds = sum(seconds for seconds, _ in measured_by_bundle.values())
    total_measured_cells = sum(
        int(meta_by_bundle[name]["raw_cells"])
        for name in measured_by_bundle
        if name in meta_by_bundle
    )
    baseline_seconds_per_cell = (
        total_measured_seconds / total_measured_cells
        if total_measured_cells > 0
        else 1.0
    )

    # Build the per-bundle rows, marking each as measured or estimated.
    normalized_bundle_rows: list[dict] = []
    by_model: dict[str, dict[str, float | int]] = {}
    estimated_runtime_seconds = 0.0
    measured_runtime_seconds_attributed = 0.0

    for meta in bundle_meta:
        is_measured = meta["bundle"] in measured_by_bundle
        if is_measured:
            runtime_seconds, source = measured_by_bundle[meta["bundle"]]
            measured_runtime_seconds_attributed += runtime_seconds
        else:
            runtime_seconds = meta["raw_cells"] * baseline_seconds_per_cell
            source = "estimated"
            estimated_runtime_seconds += runtime_seconds

        seconds_per_claim = runtime_seconds / max(meta["claims"], 1)
        normalized_bundle_rows.append(
            {
                "bundle": meta["bundle"],
                "task": meta["task"],
                "model": meta["model"],
                "claims": meta["claims"],
                "raw_cells": meta["raw_cells"],
                "runtime_seconds_mean": runtime_seconds,
                "seconds_per_claim": seconds_per_claim,
                "source": source,
            }
        )
        model_stats = by_model.setdefault(
            meta["model"],
            {
                "bundles": 0,
                "claims": 0,
                "raw_cells": 0,
                "runtime_seconds_total": 0.0,
                "measured_bundles": 0,
            },
        )
        model_stats["bundles"] += 1
        model_stats["claims"] += meta["claims"]
        model_stats["raw_cells"] += meta["raw_cells"]
        model_stats["runtime_seconds_total"] += runtime_seconds
        if is_measured:
            model_stats["measured_bundles"] += 1

    by_model_summary = {}
    for model, stats in by_model.items():
        by_model_summary[model] = {
            "bundles": stats["bundles"],
            "measured_bundles": stats["measured_bundles"],
            "claims": stats["claims"],
            "runtime_seconds_mean_per_bundle": stats["runtime_seconds_total"] / max(stats["bundles"], 1),
            "seconds_per_claim": stats["runtime_seconds_total"] / max(stats["claims"], 1),
            "seconds_per_1000_cells": (stats["runtime_seconds_total"] / max(stats["raw_cells"], 1)) * 1000.0,
        }

    total_estimate_seconds = measured_runtime_seconds_attributed + estimated_runtime_seconds
    total_claims = sum(b["claims"] for b in bundle_meta)
    total_cells = sum(b["raw_cells"] for b in bundle_meta)
    source_counts = Counter(str(row["source"]) for row in normalized_bundle_rows)
    n_measured = sum(count for source, count in source_counts.items() if source.startswith("measured_"))

    payload = {
        "reruns": args.reruns,
        "bundles_profiled": len(bundle_meta),
        "bundles_measured": n_measured,
        "bundles_estimated": len(bundle_meta) - n_measured,
        "measurement_coverage": n_measured / max(len(bundle_meta), 1),
        "measurement_sources": dict(source_counts),
        "totals": {
            "bundles": len(bundle_meta),
            "claims": total_claims,
            "cells": total_cells,
            "raw_cells": total_cells,
            "observed_runtime_seconds": measured_runtime_seconds_attributed,
            "observed_runtime_seconds_distinct_measurements": sum(measured_runtime.values()),
            "observed_runtime_seconds_all_sources": total_measured_seconds,
            "estimated_runtime_seconds_for_unmeasured_bundles": estimated_runtime_seconds,
            "estimated_runtime_seconds": total_estimate_seconds,
            "estimated_runtime_minutes": total_estimate_seconds / 60.0,
            "estimated_runtime_with_reruns_seconds": total_estimate_seconds * max(1, args.reruns),
            "estimated_runtime_with_reruns_minutes": (total_estimate_seconds * max(1, args.reruns)) / 60.0,
            "observed_seconds_per_cell": baseline_seconds_per_cell,
            "runtime_seconds_mean_sum": total_estimate_seconds,
            "seconds_per_claim": total_estimate_seconds / max(total_claims, 1),
            "seconds_per_1000_cells": (total_estimate_seconds / max(total_cells, 1)) * 1000.0,
        },
        "by_model": by_model_summary,
        "bundles": normalized_bundle_rows,
        "notes": [
            "Observed runtime comes from main/output/real_multi_task/experiment_summary.json when available.",
            "Measured real zero-task repair replacement bundle runtimes are included when runtime_seconds is positive in main/output/repro/zero_task_real_repair.json.",
            "Zero-valued repair runtimes are treated as missing measurements, not as zero-cost evaluations.",
            "Each (task, model) measurement is counted exactly once (attributed to the canonical bundle when present).",
            "Bundles without a recorded wall-clock time are extrapolated from the per-cell rate of the measured bundles only.",
            "This is a runtime envelope, not a cloud-price quotation. Coverage is reported via 'bundles_measured' and 'measurement_coverage'.",
        ],
    }

    lines = [
        "# Runtime and Cost Report",
        "",
        f"- Bundles profiled: **{payload['totals']['bundles']}** ({n_measured} measured, {len(bundle_meta) - n_measured} estimated)",
        f"- Measurement coverage: **{payload['measurement_coverage'] * 100:.1f}%**",
        f"- Claims: **{payload['totals']['claims']}**",
        f"- Cells: **{payload['totals']['cells']}**",
        f"- Sum of distinct measured wall-clock times: **{payload['totals']['observed_runtime_seconds_distinct_measurements']:.1f}s**",
        f"- Sum of all attributed measured wall-clock times: **{payload['totals']['observed_runtime_seconds_all_sources']:.1f}s**",
        f"- Measurement sources: **{dict(source_counts)}**",
        f"- Estimated runtime envelope: **{payload['totals']['estimated_runtime_minutes']:.1f} minutes** "
        f"(measured + extrapolated)",
        f"- Estimated runtime envelope with {args.reruns} reruns: "
        f"**{payload['totals']['estimated_runtime_with_reruns_minutes']:.1f} minutes**",
        f"- Per-cell baseline (from measured bundles only): "
        f"**{payload['totals']['observed_seconds_per_cell']:.3f}s/cell**",
        "",
        "| Bundle | Task | Model | Claims | Cells | Runtime (s) | Source |",
        "|---|---|---|---|---|---|---|",
    ]
    for row in normalized_bundle_rows:
        lines.append(
            f"| {row['bundle']} | {row['task']} | {row['model']} | {row['claims']} | "
            f"{row['raw_cells']} | {row['runtime_seconds_mean']:.1f} | {row['source']} |"
        )

    out_dir = Path(__file__).resolve().parents[1] / "main" / "output" / "repro"
    write_json(out_dir / "runtime_cost_report.json", payload)
    write_text(out_dir / "runtime_cost_report.md", "\n".join(lines).rstrip() + "\n")
    print(str(out_dir / "runtime_cost_report.json"))


if __name__ == "__main__":
    main()
