#!/usr/bin/env python3
"""Generate community-style submission workflow summary artifacts.

This summary is intended to be cheap to regenerate from released artifacts. It
therefore uses the current evaluator-side caches produced by
``main._bundle_analysis`` rather than re-running submission review across every
bundle. When an earlier full submission-review summary is already present, we
carry forward its determinism counts as metadata instead of recomputing them
expensively here.
"""

from __future__ import annotations

import json
from pathlib import Path

from _bundle_analysis import _load_cached_or_evaluate_bundle, find_bundle_dirs, write_json

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    bundle_summaries = []
    workflow_decisions: dict[str, int] = {}
    top_failed_gates: dict[str, int] = {}

    out_dir = ROOT / "main" / "output" / "community_submissions"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "community_value_summary.json"

    previous = None
    if out_path.exists():
        try:
            previous = json.loads(out_path.read_text())
        except Exception:
            previous = None

    previous_by_bundle = {}
    if isinstance(previous, dict):
        previous_by_bundle = {
            row.get("bundle"): row
            for row in previous.get("bundle_summaries", [])
            if isinstance(row, dict) and row.get("bundle")
        }

    def stable_from_bundle_review(bundle_dir: Path) -> bool | None:
        review_path = bundle_dir / "submission_review.json"
        if not review_path.exists():
            return None
        try:
            review = json.loads(review_path.read_text())
        except Exception:
            return None
        if not isinstance(review, dict):
            return None
        if "deterministic" not in review:
            return None
        return bool(review["deterministic"])

    for bundle in find_bundle_dirs(
        ROOT / "main" / "output" / "real_multi_task",
        ROOT / "main" / "output" / "real_multilane",
    ):
        result = _load_cached_or_evaluate_bundle(bundle)
        accepted_for_claims = 0
        blocked_from_claims = 0
        for claim in result["claim_reports"]:
            workflow_decisions[claim["evidence_tier"]] = workflow_decisions.get(claim["evidence_tier"], 0) + 1
            accepted_for_claims += int(claim["passed"])
            blocked_from_claims += int(not claim["passed"])
            for gate in claim.get("failed_checks", []):
                top_failed_gates[gate] = top_failed_gates.get(gate, 0) + 1
        prior_row = previous_by_bundle.get(bundle.name, {})
        measured_stable = stable_from_bundle_review(bundle)
        bundle_summaries.append(
            {
                "bundle": bundle.name,
                "discovery_candidates": result["overall"]["hypothesis_count"],
                "accepted_for_claims": accepted_for_claims,
                "blocked_from_claims": blocked_from_claims,
                "stable": measured_stable if measured_stable is not None else prior_row.get("stable"),
            }
        )

    total_candidates = sum(row["discovery_candidates"] for row in bundle_summaries)
    total_accepted = sum(row["accepted_for_claims"] for row in bundle_summaries)
    total_blocked = sum(row["blocked_from_claims"] for row in bundle_summaries)

    current_stable_values_complete = all(row["stable"] is not None for row in bundle_summaries)
    if current_stable_values_complete:
        stable_bundles = sum(1 for row in bundle_summaries if row["stable"] is True)
        determinism_source = "bundle_submission_review_artifacts"
    elif isinstance(previous, dict) and previous.get("bundles_reviewed") == len(bundle_summaries):
        stable_bundles = int(previous.get("stable_bundles", 0))
        determinism_source = "inherited_from_existing_submission_review_summary"
    else:
        stable_bundles = sum(1 for row in bundle_summaries if row["stable"] is True)
        determinism_source = "current_summary_rows_only"

    payload = {
        "bundles_reviewed": len(bundle_summaries),
        "stable_bundles": stable_bundles,
        "determinism_source": determinism_source,
        "workflow_totals": {
            "discovery_candidates": total_candidates,
            "accepted_for_claims": total_accepted,
            "blocked_from_claims": total_blocked,
            "decision_change_rate": total_blocked / total_candidates if total_candidates else 0.0,
        },
        "workflow_decision_counts": workflow_decisions,
        "top_failed_gates": sorted(top_failed_gates.items(), key=lambda kv: (-kv[1], kv[0]))[:10],
        "bundle_summaries": bundle_summaries,
    }

    write_json(out_path, payload)
    print(str(out_path))


if __name__ == "__main__":
    main()
