"""Submission-review workflow for publication-facing claim bundles."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .evaluator import evaluate_bundle
from .io_utils import read_yaml, write_json, write_text
from .protocol_critic import critique_protocol
from .reporting import build_markdown_report


TIER_WORKFLOW_ACTIONS = {
    "cross_model_confirmed": "Ready to share as a cross-model claim; include transfer evidence and full reviewer kit.",
    "single_model_confirmed": "Ready to share as a single-model claim; collect cross-model evidence before making transfer claims.",
    "causal_plus_robustness": "Keep as a strong internal result, but do not present as accepted; add missing confirmatory or transfer evidence.",
    "causal_tested_unstable": "Revise the claim and run targeted follow-up on the failed core gates before reuse.",
    "suggestive": "Treat as exploratory only; strengthen causal, robustness, and statistical evidence.",
    "rejected": "Do not present as validated; use failed gates to redesign the hypothesis or protocol.",
}


def _repo_relative(path: Path) -> str:
    for parent in path.resolve().parents:
        if (parent / "packages").exists() and (parent / "main").exists():
            try:
                return str(path.resolve().relative_to(parent))
            except Exception:
                break
    return str(path.resolve())


def run_submission_review(bundle_dir: Path, reruns: int = 3) -> dict[str, Any]:
    """Run repeated deterministic evaluations and summarize publication readiness."""
    bundle_dir = bundle_dir.resolve()
    reruns = max(1, int(reruns))

    evaluation_payloads: list[dict[str, Any]] = []
    evaluation_rendered: list[str] = []
    report_rendered: list[str] = []

    for _ in range(reruns):
        payload = evaluate_bundle(bundle_dir)
        rendered = json.dumps(payload, sort_keys=True, indent=2)
        evaluation_payloads.append(payload)
        evaluation_rendered.append(rendered)
        report_rendered.append(build_markdown_report(payload))

    baseline_payload = evaluation_payloads[0]
    baseline_report = report_rendered[0]
    exact_json_matches = sum(1 for item in evaluation_rendered if item == evaluation_rendered[0])
    exact_report_matches = sum(1 for item in report_rendered if item == report_rendered[0])
    deterministic = exact_json_matches == reruns and exact_report_matches == reruns

    protocol = read_yaml(bundle_dir / "protocol.yaml")
    critique = critique_protocol(protocol)

    claim_actions = []
    for report in baseline_payload["claim_reports"]:
        claim_actions.append(
            {
                "hypothesis_id": report["hypothesis_id"],
                "evidence_tier": report["evidence_tier"],
                "passed": report["passed"],
                "workflow_action": TIER_WORKFLOW_ACTIONS[report["evidence_tier"]],
                "failed_checks": report.get("failed_checks", []),
                "not_evaluated_checks": report.get("not_evaluated_checks", []),
            }
        )

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "bundle_dir": _repo_relative(bundle_dir),
        "protocol_id": baseline_payload["protocol_id"],
        "protocol_hash": baseline_payload["protocol_hash"],
        "reruns_requested": reruns,
        "reruns_completed": reruns,
        "deterministic": deterministic,
        "exact_json_matches": exact_json_matches,
        "exact_report_matches": exact_report_matches,
        "overall": baseline_payload["overall"],
        "claim_actions": claim_actions,
        "protocol_critic": critique,
        "recommended_next_step": (
            "Bundle is deterministic and contains accepted claims."
            if deterministic and baseline_payload["overall"]["accepted_count"] > 0
            else "Resolve determinism or evidentiary weaknesses before external submission."
        ),
        "result": baseline_payload,
        "report_markdown": baseline_report,
    }


def format_submission_review(review: dict[str, Any]) -> str:
    """Render a concise Markdown summary for external review."""
    lines = [
        "# Submission Review",
        "",
        f"- Generated: {review['generated_at']}",
        f"- Bundle: `{review['bundle_dir']}`",
        f"- Protocol: `{review['protocol_id']}`",
        f"- Protocol hash: `{review['protocol_hash']}`",
        f"- Reruns: {review['reruns_completed']} / {review['reruns_requested']}",
        f"- Deterministic: {review['deterministic']}",
        f"- Exact JSON matches: {review['exact_json_matches']}",
        f"- Exact Markdown matches: {review['exact_report_matches']}",
        "",
        "## Overall",
        "",
        f"- Hypotheses: {review['overall']['hypothesis_count']}",
        f"- Accepted: {review['overall']['accepted_count']}",
        f"- Unstable: {review['overall']['unstable_count']}",
        f"- Rejected: {review['overall']['rejected_count']}",
        "",
        "## Workflow Actions",
        "",
    ]

    for claim in review["claim_actions"]:
        lines.extend(
            [
                f"### {claim['hypothesis_id']}",
                f"- Tier: `{claim['evidence_tier']}`",
                f"- Passed: {claim['passed']}",
                f"- Action: {claim['workflow_action']}",
                f"- Failed checks: {', '.join(claim['failed_checks']) if claim['failed_checks'] else 'none'}",
                (
                    f"- Not evaluated: {', '.join(claim['not_evaluated_checks'])}"
                    if claim["not_evaluated_checks"]
                    else "- Not evaluated: none"
                ),
                "",
            ]
        )

    critique = review["protocol_critic"]
    lines.extend(
        [
            "## Protocol Critic",
            "",
            f"- Verdict: {critique['verdict']}",
            f"- Score: {critique['score']}/100",
            f"- Blockers: {critique['n_blockers']}",
            f"- Warnings: {critique['n_warnings']}",
            f"- Suggestions: {critique['n_suggestions']}",
            "",
            "## Recommendation",
            "",
            review["recommended_next_step"],
            "",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def write_submission_review(
    bundle_dir: Path,
    *,
    reruns: int = 3,
    output_json: Path | None = None,
    output_md: Path | None = None,
) -> tuple[dict[str, Any], Path, Path]:
    """Run the workflow and write both JSON and Markdown artifacts."""
    review = run_submission_review(bundle_dir, reruns=reruns)
    if output_json is None:
        output_json = bundle_dir / "submission_review.json"
    if output_md is None:
        output_md = bundle_dir / "submission_review.md"

    serializable = dict(review)
    serializable.pop("report_markdown", None)
    write_json(output_json, serializable)
    write_text(output_md, format_submission_review(review))
    return review, output_json, output_md
