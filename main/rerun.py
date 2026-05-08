#!/usr/bin/env python3
"""Honest Stage-1 rerun and submission-review utility for archived bundles."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "packages" / "evaluator" / "src"))

from automechinterp_evaluator.evaluator import evaluate_bundle
from automechinterp_evaluator.reporting import build_markdown_report
from automechinterp_evaluator.submission_review import write_submission_review


def main() -> None:
    parser = argparse.ArgumentParser(description="Rerun Stage-1 evaluation on an existing archived bundle")
    parser.add_argument(
        "--bundle-dir",
        default="main/output/real_multi_task/ioi_v0_gpt2-small",
        help="Bundle directory to rerun",
    )
    parser.add_argument("--reruns", type=int, default=3, help="How many deterministic reruns to compare")
    args = parser.parse_args()

    bundle_dir = (ROOT / args.bundle_dir).resolve() if not Path(args.bundle_dir).is_absolute() else Path(args.bundle_dir).resolve()
    if not bundle_dir.exists():
        raise SystemExit(f"Bundle not found: {bundle_dir}")

    result = evaluate_bundle(bundle_dir)
    report_path = bundle_dir / "rerun_report.md"
    report_path.write_text(build_markdown_report(result))

    _, review_json, review_md = write_submission_review(
        bundle_dir,
        reruns=max(1, args.reruns),
        output_json=bundle_dir / "rerun_submission_review.json",
        output_md=bundle_dir / "rerun_submission_review.md",
    )

    summary = {
        "bundle": str(bundle_dir),
        "protocol_id": result["protocol_id"],
        "accepted": result["overall"]["accepted_count"],
        "rejected": result["overall"]["rejected_count"],
        "report": str(report_path),
        "submission_review_json": str(review_json),
        "submission_review_md": str(review_md),
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
