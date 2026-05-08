#!/usr/bin/env python3
"""Assemble a contract-hardening V1 migration decision record.

The script does not automatically adopt or reject V1. It collects the current
and candidate stress artifacts, retention tradeoffs, and pre-registered
criteria into a decision document with an explicit human decision field. This
prevents a paper from silently treating a promising post-hoc hardening result
as the released contract.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

try:
    from _bundle_analysis import write_json, write_text
except ModuleNotFoundError:
    from main._bundle_analysis import write_json, write_text


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def _stress_summary(payload: dict[str, Any]) -> dict[str, Any]:
    row = payload.get("stress_result") or payload
    return {
        "status": payload.get("status"),
        "negatives": int(row.get("negatives") or row.get("total") or 0),
        "false_accepts": row.get("false_accepts", row.get("leaked")),
        "false_accept_rate": row.get("false_accept_rate"),
        "false_accept_rate_ci95": row.get("false_accept_rate_ci95") or {},
        "source_artifact": row.get("source_artifact"),
    }


def build_decision(
    current: dict[str, Any],
    candidate: dict[str, Any],
    retention: dict[str, Any],
    *,
    decision: str,
    rationale: str,
) -> dict[str, Any]:
    current_s = _stress_summary(current)
    candidate_s = _stress_summary(candidate)
    current_ci = current_s["false_accept_rate_ci95"] or {}
    candidate_ci = candidate_s["false_accept_rate_ci95"] or {}
    current_far = float(current_s["false_accept_rate"] or 0.0)
    candidate_far = float(candidate_s["false_accept_rate"] or 0.0)
    retention_rate = float(retention.get("accepted_claim_retention_rate") or 0.0)
    accepted_before = int(retention.get("accepted_claims_before_total") or 0)
    accepted_after = int(retention.get("accepted_claims_after_total") or 0)
    tasks_after = retention.get("tasks_with_accepted_after") or []
    independent_statuses = [str(current_s.get("status")), str(candidate_s.get("status"))]
    independent_evidence = all("rehearsal" not in status for status in independent_statuses)

    criteria = {
        "independent_evidence": independent_evidence,
        "candidate_ci_upper_below_5pct": float(candidate_ci.get("high") or 1.0) < 0.05,
        "current_ci_lower_above_candidate_point": float(current_ci.get("low") or 0.0) > candidate_far,
        "accepted_claim_retention_at_least_60pct": retention_rate >= 0.60,
        "accepted_task_retention_documented": bool(tasks_after),
    }
    adoptable = all(criteria.values())
    if decision == "adopt_next_major" and not adoptable:
        decision_status = "invalid_adoption_decision_criteria_not_met"
    elif decision == "adopt_next_major":
        decision_status = "adopt_next_major_version_candidate"
    elif decision == "reject":
        decision_status = "rejected_by_human_decision"
    else:
        decision_status = "deferred_pending_external_validation"

    return {
        "generated_by": "main/contract_migration_decision.py",
        "decision": decision,
        "decision_status": decision_status,
        "human_rationale": rationale,
        "criteria": criteria,
        "adoptable_under_preregistered_criteria": adoptable,
        "current_contract_stress": current_s,
        "candidate_contract_stress": candidate_s,
        "retention_tradeoff": {
            "accepted_claims_before": accepted_before,
            "accepted_claims_after": accepted_after,
            "accepted_claim_retention_rate": retention_rate,
            "tasks_with_accepted_after": tasks_after,
            "tasks_with_accepted_after_count": int(retention.get("tasks_with_accepted_after_count") or 0),
            "bundles_changed_count": len(retention.get("bundles_changed") or []),
        },
        "claim_boundary": (
            "V1 is not adopted by this artifact unless decision=adopt_next_major and all pre-registered criteria are met. "
            "Rehearsal or benchmark-authored stress is not independent validation."
        ),
    }


def format_md(payload: dict[str, Any]) -> str:
    current = payload["current_contract_stress"]
    candidate = payload["candidate_contract_stress"]
    retention = payload["retention_tradeoff"]
    lines = [
        "# Contract Hardening V1 Migration Decision",
        "",
        f"- Decision: **{payload['decision']}**",
        f"- Decision status: **{payload['decision_status']}**",
        f"- Adoptable under pre-registered criteria: **{payload['adoptable_under_preregistered_criteria']}**",
        "",
        "## Stress Tradeoff",
        "",
        "| Contract | Status | False accepts | FAR | 95% CI |",
        "|---|---|---:|---:|---|",
        (
            f"| Current | `{current.get('status')}` | {current.get('false_accepts')}/{current.get('negatives')} | "
            f"{float(current.get('false_accept_rate') or 0.0) * 100:.1f}% | "
            f"{(current.get('false_accept_rate_ci95') or {}).get('label', 'n/a')} |"
        ),
        (
            f"| V1 candidate | `{candidate.get('status')}` | {candidate.get('false_accepts')}/{candidate.get('negatives')} | "
            f"{float(candidate.get('false_accept_rate') or 0.0) * 100:.1f}% | "
            f"{(candidate.get('false_accept_rate_ci95') or {}).get('label', 'n/a')} |"
        ),
        "",
        "## Retention Tradeoff",
        "",
        f"- Accepted claims before: **{retention['accepted_claims_before']}**",
        f"- Accepted claims after: **{retention['accepted_claims_after']}**",
        f"- Accepted-claim retention: **{retention['accepted_claim_retention_rate'] * 100:.1f}%**",
        f"- Tasks with accepted claims after: **{retention['tasks_with_accepted_after_count']}** ({', '.join(retention['tasks_with_accepted_after'])})",
        f"- Bundles changed: **{retention['bundles_changed_count']}**",
        "",
        "## Criteria",
        "",
    ]
    lines.extend(f"- `{key}`: **{value}**" for key, value in payload["criteria"].items())
    lines.extend(
        [
            "",
            "## Human Rationale",
            "",
            payload["human_rationale"],
            "",
            "## Claim Boundary",
            "",
            payload["claim_boundary"],
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Assemble contract-hardening V1 migration decision")
    parser.add_argument("--current", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--retention", type=Path, required=True)
    parser.add_argument("--out-md", type=Path, required=True)
    parser.add_argument("--out-json", type=Path, required=True)
    parser.add_argument(
        "--decision",
        choices=["defer", "reject", "adopt_next_major"],
        default="defer",
    )
    parser.add_argument(
        "--rationale",
        default=(
            "Defer adoption until an externally authored negative set or external custodian run validates the "
            "stress reduction under the pre-registered protocol."
        ),
    )
    args = parser.parse_args()

    payload = build_decision(
        _load(args.current),
        _load(args.candidate),
        _load(args.retention),
        decision=args.decision,
        rationale=args.rationale,
    )
    write_json(args.out_json, payload)
    write_text(args.out_md, format_md(payload))
    print(str(args.out_json))


if __name__ == "__main__":
    main()
