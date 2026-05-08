"""Report generation utilities.

V9: Extended with compensation warnings, bidirectional gate status,
15-gate summary, and enhanced per-hypothesis details.
"""

from __future__ import annotations

from pathlib import Path

from .constants import EVIDENCE_TIER_ORDER
from .evaluator import evaluate_bundle
from .io_utils import write_text


def build_markdown_report(result: dict) -> str:
    overall = result["overall"]
    lines = [
        "# Stage-Gate Report",
        "",
        f"- Protocol: `{result['protocol_id']}`",
        f"- Protocol hash: `{result['protocol_hash']}`",
        f"- Hypotheses: {overall['hypothesis_count']}",
        f"- Accepted: {overall['accepted_count']}",
        f"- Unstable: {overall['unstable_count']}",
        f"- Rejected: {overall['rejected_count']}",
        f"- All pass: {overall['all_pass']}",
    ]

    # Cross-method rank stability (V7)
    if "cross_method_rank_tau" in overall:
        lines.append(f"- Cross-method rank τ: {overall['cross_method_rank_tau']:.4f}")

    # Cross-model rank stability (V8)
    if "cross_model_rank_tau" in overall:
        lines.append(f"- Cross-model rank τ: {overall['cross_model_rank_tau']:.4f}")

    lines.extend(["", "## Summary Table", ""])
    lines.append("| Hypothesis | Verdict | Tier | Cohen's d | Spec. Ratio | q-value |")
    lines.append("|---|---|---|---|---|---|")
    for report in result["claim_reports"]:
        m = report["metrics"]
        verdict = "✅ PASS" if report["passed"] else "❌ FAIL"
        d_val = m.get("cohens_d", 0.0)
        lines.append(
            f"| {report['hypothesis_id']} "
            f"| {verdict} "
            f"| `{report['evidence_tier']}` "
            f"| {d_val:.3f} "
            f"| {m['specificity_ratio']:.3f} "
            f"| {m['q_value']:.4f} |"
        )

    # Failure rate table (V7)
    # separate optional transfer diagnostics from core
    # gate failures so reviewers don't read "100% cross_model_transfer
    # failure" alongside "Accepted: 2" as a contradiction. Cross-model
    # transfer is optional unless a claim explicitly requests
    # ``cross_model_confirmed``.
    lines.extend(["", "## Failure Analysis", ""])
    OPTIONAL_DIAGNOSTIC_CHECKS = {"cross_model_transfer"}
    core_fail_counts: dict[str, int] = {}
    optional_fail_counts: dict[str, int] = {}
    for report in result["claim_reports"]:
        for check in report.get("failed_checks", []):
            target = optional_fail_counts if check in OPTIONAL_DIAGNOSTIC_CHECKS else core_fail_counts
            target[check] = target.get(check, 0) + 1

    if core_fail_counts:
        lines.append("### Core gate failures")
        lines.append("")
        lines.append("| Check | Failure Count | Failure Rate |")
        lines.append("|---|---|---|")
        total = overall["hypothesis_count"]
        for check, count in sorted(core_fail_counts.items(), key=lambda x: -x[1]):
            rate = count / max(total, 1)
            lines.append(f"| {check} | {count} | {rate:.1%} |")
    else:
        lines.append("No core gate failures detected.")

    if optional_fail_counts:
        lines.extend([
            "",
            "### Optional transfer diagnostics (tier demotions, not core failures)",
            "",
            "| Check | Demotion Count | Demotion Rate |",
            "|---|---|---|",
        ])
        total = overall["hypothesis_count"]
        for check, count in sorted(optional_fail_counts.items(), key=lambda x: -x[1]):
            rate = count / max(total, 1)
            lines.append(f"| {check} | {count} | {rate:.1%} |")

    # Evidence tier breakdown (V7)
    lines.extend(["", "## Evidence Tier Breakdown", ""])
    tier_counts: dict[str, int] = {}
    for report in result["claim_reports"]:
        tier = report["evidence_tier"]
        tier_counts[tier] = tier_counts.get(tier, 0) + 1

    lines.append("| Tier | Count |")
    lines.append("|---|---|")
    for tier in EVIDENCE_TIER_ORDER:
        if tier in tier_counts:
            lines.append(f"| `{tier}` | {tier_counts[tier]} |")

    lines.extend(["", "## Per-Hypothesis Details", ""])

    for report in result["claim_reports"]:
        metrics = report["metrics"]
        lines.extend(
            [
                f"### {report['hypothesis_id']}",
                f"- Passed: {report['passed']}",
                f"- Evidence tier: `{report['evidence_tier']}`",
                (
                    "- Gate outcomes: "
                    + ", ".join(
                        f"{gate}={status}"
                        for gate, status in sorted(report.get("gate_outcomes", {}).items())
                    )
                    if report.get("gate_outcomes")
                    else "- Gate outcomes: unavailable"
                ),
                f"- Failed checks: {', '.join(report['failed_checks']) if report['failed_checks'] else 'none'}",
                f"- Treatment mean: {metrics['treatment_effect_mean']:.6f}",
                f"- Cohen's d: {metrics.get('cohens_d', 0.0):.4f}",
                (
                    "- Confirmatory CI (bootstrap): "
                    f"[{metrics['confirmatory_ci_low']:.6f}, {metrics['confirmatory_ci_high']:.6f}]"
                ),
                f"- Specificity ratio: {metrics['specificity_ratio']:.6f}",
                f"- Control abs mean: {metrics['control_abs_mean']:.6f}",
                f"- Robustness (seed/prompt/resample): "
                f"{metrics['seed_consistency']:.3f} / "
                f"{metrics['prompt_variant_consistency']:.3f} / "
                f"{metrics['resample_consistency']:.3f}",
                f"- Method sensitivity std: {metrics['method_sensitivity_std']:.6f}",
                f"- Permutation p-value: {metrics.get('p_value_permutation', 'N/A')}",
                f"- BH q-value: {metrics['q_value']:.6f}",
                f"- Holm-adjusted p: {metrics.get('holm_adjusted_p', 'N/A')}",
                f"- Cells: {metrics.get('n_cells', 'N/A')}",
            ]
        )
        # Compensation warning (V9, Pitfall #62)
        if metrics.get("compensation_warning", False):
            lines.append(
                "- ⚠️ **Compensation warning**: Treatment effect reverses direction "
                "across methods — possible compensatory circuit detected"
            )
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def write_markdown_report(bundle_dir: Path, output_path: Path | None = None) -> Path:
    result = evaluate_bundle(bundle_dir)
    report = build_markdown_report(result)
    if output_path is None:
        output_path = bundle_dir / "stage_gate_report.md"
    write_text(output_path, report)
    return output_path
