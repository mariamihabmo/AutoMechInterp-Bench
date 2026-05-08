"""Claim ledger generation for publication.

V7: Produces a machine-readable JSON ledger of all accepted, rejected,
and unstable claims with per-claim breakdowns and summary statistics.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def build_claim_ledger(evaluation_output: dict[str, Any]) -> dict[str, Any]:
    """Build a claim ledger from evaluator output.

    Args:
        evaluation_output: The dict returned by evaluate_bundle().

    Returns:
        Machine-readable claim ledger with summary stats.
    """
    claims: list[dict[str, Any]] = []
    for report in evaluation_output.get("claim_reports", []):
        claims.append({
            "hypothesis_id": report["hypothesis_id"],
            "verdict": "accepted" if report["passed"] else "rejected",
            "evidence_tier": report["evidence_tier"],
            "passed": report["passed"],
            "gate_outcomes": report.get("gate_outcomes", {}),
            "failed_checks": report.get("failed_checks", []),
            "not_evaluated_checks": report.get("not_evaluated_checks", []),
            "key_metrics": {
                "treatment_effect_mean": report["metrics"]["treatment_effect_mean"],
                "cohens_d": report["metrics"].get("cohens_d", None),
                "specificity_ratio": report["metrics"]["specificity_ratio"],
                "p_value_permutation": report["metrics"].get("p_value_permutation", None),
                "q_value": report["metrics"]["q_value"],
                "holm_adjusted_p": report["metrics"].get("holm_adjusted_p", None),
                "n_cells": report["metrics"].get("n_cells", None),
                "seed_consistency": report["metrics"]["seed_consistency"],
                "prompt_variant_consistency": report["metrics"]["prompt_variant_consistency"],
                "resample_consistency": report["metrics"]["resample_consistency"],
                "cross_model_transfer": report.get("checks", {}).get("cross_model_transfer", None),
            },
        })

    overall = evaluation_output.get("overall", {})
    total = overall.get("hypothesis_count", len(claims))
    accepted = overall.get("accepted_count", sum(1 for c in claims if c["passed"]))
    unstable = overall.get("unstable_count", 0)
    rejected = overall.get("rejected_count", total - accepted - unstable)

    return {
        "protocol_id": evaluation_output.get("protocol_id", ""),
        "protocol_hash": evaluation_output.get("protocol_hash", ""),
        "claims": claims,
        "summary": {
            "total": total,
            "accepted": accepted,
            "unstable": unstable,
            "rejected": rejected,
            "acceptance_rate": round(accepted / max(total, 1), 4),
            "instability_rate": round(unstable / max(total, 1), 4),
            "rejection_rate": round(rejected / max(total, 1), 4),
        },
        "tier_breakdown": _tier_breakdown(claims),
    }


def _tier_breakdown(claims: list[dict[str, Any]]) -> dict[str, int]:
    """Count claims per evidence tier."""
    breakdown: dict[str, int] = {}
    for claim in claims:
        tier = claim["evidence_tier"]
        breakdown[tier] = breakdown.get(tier, 0) + 1
    return breakdown


def write_claim_ledger(
    evaluation_output: dict[str, Any],
    output_path: Path,
) -> Path:
    """Generate and write claim ledger to disk."""
    ledger = build_claim_ledger(evaluation_output)
    output_path.write_text(json.dumps(ledger, indent=2, sort_keys=False) + "\n")
    return output_path
