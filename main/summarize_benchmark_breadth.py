#!/usr/bin/env python3
"""Summarize benchmark breadth from evaluated bundles and local lane artifacts."""

from __future__ import annotations

from pathlib import Path

from _bundle_analysis import (
    REAL_MULTILANE_DIR,
    REAL_MULTI_TASK_DIR,
    evaluate_bundle_records,
    summarize_breadth,
    write_json,
    write_text,
)


def format_markdown(payload: dict) -> str:
    lines = [
        "# Benchmark Breadth Summary",
        "",
        f"- Evaluated bundles: **{payload['bundle_count']}**",
        f"- Evaluated claims: **{payload['claim_count']}**",
        f"- Tasks covered: **{payload['task_count']}**",
        f"- Models covered: **{payload['model_count']}**",
        f"- Discovery lanes represented: **{payload['discovery_lane_count']}**",
        f"- Providers represented: **{payload['provider_count']}**",
        "",
        "## Claims by task",
        "",
        "| Task | Claims |",
        "|---|---|",
    ]
    for task, count in sorted(payload["claims_by_task"].items()):
        lines.append(f"| {task} | {count} |")

    lines.extend(["", "## Claims by model", "", "| Model | Claims |", "|---|---|"])
    for model, count in sorted(payload["claims_by_model"].items()):
        lines.append(f"| {model} | {count} |")

    lines.extend(["", "## Claims by discovery lane", "", "| Lane | Claims |", "|---|---|"])
    for lane, count in sorted(payload["claims_by_lane"].items()):
        lines.append(f"| {lane} | {count} |")

    lines.extend(["", "## Evaluated bundles", "", "| Bundle | Task | Model | Claims | Lane counts |", "|---|---|---|---|---|"])
    for row in payload["bundles"]:
        lane_counts = ", ".join(f"{k}:{v}" for k, v in sorted(row["lane_counts"].items())) or "n/a"
        lines.append(f"| {row['bundle']} | {row['task']} | {row['model']} | {row['claims']} | {lane_counts} |")

    if payload["auxiliary_lane_artifacts"]:
        lines.extend(
            [
                "",
                "## Auxiliary lane artifacts",
                "",
                "These artifacts exist locally but are not counted as evaluated bundles unless Stage-2 and Stage-1 were run on them.",
                "",
                "| Source dir | Task | Model | Lane | Provider | Hypothesis |",
                "|---|---|---|---|---|---|",
            ]
        )
        for row in payload["auxiliary_lane_artifacts"][:50]:
            lines.append(
                f"| {row['source_dir']} | {row['task']} | {row['model']} | {row['discovery_lane']} | {row['provider_id']} | {row['hypothesis_id']} |"
            )

    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    records = evaluate_bundle_records(REAL_MULTI_TASK_DIR, REAL_MULTILANE_DIR, use_cached_results=True)
    payload = summarize_breadth(records)
    out_dir = Path(__file__).resolve().parents[1] / "main" / "output" / "repro"
    write_json(out_dir / "benchmark_breadth_summary.json", payload)
    write_text(out_dir / "benchmark_breadth_summary.md", format_markdown(payload))
    print(str(out_dir / "benchmark_breadth_summary.json"))


if __name__ == "__main__":
    main()
