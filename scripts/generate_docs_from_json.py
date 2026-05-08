#!/usr/bin/env python3
"""Generate MkDocs pages from benchmark JSON outputs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, Mapping

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "site_docs" / "generated"

SOURCES = {
    "breadth": ROOT / "main" / "output" / "repro" / "benchmark_breadth_summary.json",
    "coverage": ROOT / "main" / "output" / "real_multi_task" / "coverage_summary.json",
    "failure_modes": ROOT / "main" / "output" / "real_multi_task" / "failure_mode_summary.json",
    "runtime": ROOT / "main" / "output" / "repro" / "runtime_cost_report.json",
    "community": ROOT
    / "main"
    / "output"
    / "community_submissions"
    / "community_value_summary.json",
    "field_findings": ROOT / "main" / "output" / "repro" / "field_level_findings.json",
    "release_takeaways": ROOT / "main" / "output" / "repro" / "release_takeaways.json",
    "fresh_agnostic_release_grade": ROOT
    / "main"
    / "output"
    / "repro"
    / "stress_test_agnostic_fresh_release_grade.json",
    "fresh_agnostic": ROOT
    / "main"
    / "output"
    / "repro"
    / "stress_test_agnostic_fresh.json",
    "docstring_repair": ROOT / "main" / "output" / "repro" / "docstring_distributed_repair.json",
    "hardening": ROOT / "main" / "output" / "repro" / "contract_hardening_v1_summary.json",
    "prompt_variant_audit": ROOT / "main" / "output" / "repro" / "prompt_variant_validity_audit.json",
    "prompt_variant_repair": ROOT / "main" / "output" / "repro" / "prompt_variant_repair_rerun.json",
}

def load_json(path: Path):
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def pct(value: float | int | None) -> str:
    if value is None:
        return "n/a"
    return f"{float(value) * 100:.2f}%"

def ci_label(ci95: dict | None) -> str:
    """Return Wilson 95% CI label at 2-decimal precision (matches the paper).

    The legacy ``label`` field embedded in ``field_level_findings.json`` is
    rendered at 1-decimal precision for historical reasons; format directly
    from the ``low``/``high`` floats so the website matches
    ``papers/submissions/neurips2026_maintrack/paper_body.tex``.
    """
    if not ci95:
        return "n/a"
    lo = ci95.get("low")
    hi = ci95.get("high")
    if lo is None or hi is None:
        return ci95.get("label", "n/a")
    return f"[{lo * 100:.2f}%, {hi * 100:.2f}%]"

def md_table(headers: list[str], rows: Iterable[Iterable[object]]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
    for row in rows:
        lines.append("| " + " | ".join(str(x) for x in row) + " |")
    return "\n".join(lines)

def sort_count_map(mapping: Mapping[str, int] | None) -> list[tuple[str, int]]:
    if not mapping:
        return []
    return sorted(mapping.items(), key=lambda kv: (-kv[1], kv[0]))

def generate_snapshot() -> str:
    breadth = load_json(SOURCES["breadth"]) or {}
    findings = load_json(SOURCES["field_findings"]) or {}

    bundle_count = breadth.get("bundle_count", 0)
    claim_count = breadth.get("claim_count", 0)
    task_count = breadth.get("task_count", 0)
    model_count = breadth.get("model_count", 0)
    lane_count = breadth.get("discovery_lane_count", 0)
    provider_count = breadth.get("provider_count", 0)

    totals = findings.get("totals", {})
    acceptance_rate = totals.get("acceptance_rate")
    acceptance_ci = ci_label(totals.get("acceptance_rate_ci95"))

    task_rows = sort_count_map(breadth.get("claims_by_task"))[:12]
    model_rows = sort_count_map(breadth.get("claims_by_model"))[:12]
    lane_rows = sort_count_map(breadth.get("claims_by_lane"))[:12]

    bundle_rows = []
    for b in breadth.get("bundles", [])[:25]:
        lane_counts = b.get("lane_counts") or {}
        lane_summary = ", ".join(f"{k}:{v}" for k, v in sorted(lane_counts.items())) or "n/a"
        bundle_rows.append(
            [
                b.get("bundle", "n/a"),
                b.get("task", "n/a"),
                b.get("model", "n/a"),
                b.get("claims", "n/a"),
                lane_summary,
            ]
        )

    sections = [
        "# Benchmark Snapshot",
        "",
        "Latest auto-generated summary from benchmark artifacts.",
        "",
        f"- Bundles: **{bundle_count}**",
        f"- Claims evaluated: **{claim_count}**",
        f"- Tasks covered: **{task_count}**",
        f"- Models covered: **{model_count}**",
        f"- Discovery lanes represented: **{lane_count}**",
        f"- Providers represented: **{provider_count}**",
        f"- Acceptance rate: **{pct(acceptance_rate)}** (95% CI: {acceptance_ci})",
        "",
        "## Claims by task",
        "",
        md_table(["Task", "Claims"], [[k, v] for k, v in task_rows]) if task_rows else "No data.",
        "",
        "## Claims by model",
        "",
        md_table(["Model", "Claims"], [[k, v] for k, v in model_rows]) if model_rows else "No data.",
        "",
        "## Claims by discovery lane",
        "",
        md_table(["Lane", "Claims"], [[k, v] for k, v in lane_rows]) if lane_rows else "No data.",
        "",
        "## Bundle inventory",
        "",
        md_table(["Bundle", "Task", "Model", "Claims", "Lane counts"], bundle_rows)
        if bundle_rows
        else "No data.",
        "",
        "## Data sources",
        "",
        "- `main/output/repro/benchmark_breadth_summary.json`",
        "- `main/output/repro/field_level_findings.json`",
    ]
    return "\n".join(sections) + "\n"

def generate_leaderboard() -> str:
    coverage = load_json(SOURCES["coverage"]) or {}
    totals = coverage.get("totals", {})
    rows = []
    bundles = list(coverage.get("bundles", []))
    bundles.sort(key=lambda b: (-b.get("accepted", 0), -b.get("acceptance_rate", 0.0), b.get("bundle", "")))

    for b in bundles:
        rows.append(
            [
                b.get("bundle", "n/a"),
                b.get("task", "n/a"),
                b.get("model", "n/a"),
                b.get("n_claims", 0),
                b.get("accepted", 0),
                pct(b.get("acceptance_rate")),
                "match" if b.get("determinism_match") else "mismatch",
            ]
        )

    tier_counts = sort_count_map(coverage.get("tier_counts"))

    sections = [
        "# Leaderboard",
        "",
        "Bundle-level verification outcomes from the released evaluated bundle set.",
        "",
        f"- Bundles: **{coverage.get('n_bundles', 0)}**",
        f"- Claims: **{totals.get('claims', 0)}**",
        f"- Accepted: **{totals.get('accepted', 0)}**",
        f"- Rejected: **{totals.get('rejected', 0)}**",
        f"- Acceptance rate: **{pct(totals.get('acceptance_rate'))}**",
        "",
        "## Bundle results",
        "",
        md_table(
            ["Bundle", "Task", "Model", "Claims", "Accepted", "Acceptance", "Determinism"],
            rows,
        )
        if rows
        else "No data.",
        "",
        "## Tier counts",
        "",
        md_table(["Tier", "Count"], [[k, v] for k, v in tier_counts]) if tier_counts else "No data.",
        "",
        "## Regenerate",
        "",
        "```bash",
        "python main/reproducibility_audit.py",
        "```",
    ]
    return "\n".join(sections) + "\n"

def generate_failure_modes() -> str:
    failure = load_json(SOURCES["failure_modes"]) or {}
    findings = load_json(SOURCES["field_findings"]) or {}

    failed_counts = sort_count_map(failure.get("failed_gate_counts"))
    not_eval_counts = sort_count_map(failure.get("not_evaluated_gate_counts"))
    tier_counts = sort_count_map(failure.get("tier_counts"))

    combos = failure.get("top_failed_combinations", [])[:10]
    combo_rows = []
    for combo in combos:
        combo_rows.append([combo.get("count", 0), ", ".join(combo.get("failed_checks", []))])

    policy = findings.get("policy_sensitivity", {})
    most_sensitive = policy.get("most_sensitive_counterfactual", {})

    sections = [
        "# Failure Modes",
        "",
        "Auto-generated failure decomposition from the released evaluated bundle set.",
        "",
        f"- Claims analyzed: **{failure.get('n_claims', 0)}**",
        f"- Passed: **{failure.get('n_passed', 0)}**",
        f"- Failed: **{failure.get('n_failed', 0)}**",
        "",
        "## Failed gate counts",
        "",
        md_table(["Gate", "Count"], [[k, v] for k, v in failed_counts]) if failed_counts else "No data.",
        "",
        "## Not-evaluated gate counts",
        "",
        md_table(["Gate", "Count"], [[k, v] for k, v in not_eval_counts])
        if not_eval_counts
        else "No data.",
        "",
        "## Tier counts",
        "",
        md_table(["Tier", "Count"], [[k, v] for k, v in tier_counts]) if tier_counts else "No data.",
        "",
        "## Top failed-check combinations",
        "",
        md_table(["Claims", "Failed checks"], combo_rows) if combo_rows else "No data.",
        "",
        "## Contract sensitivity snapshot",
        "",
        f"- Full-contract acceptance rate: **{pct(policy.get('full_acceptance_rate'))}**",
        f"- Most sensitive suite removal: **{most_sensitive.get('name', 'n/a')}**",
        f"- Acceptance under that counterfactual: **{pct(most_sensitive.get('acceptance_rate'))}**",
        f"- Tier changes under that counterfactual: **{most_sensitive.get('tier_changes', 'n/a')}**",
        "",
        "## Data sources",
        "",
        "- `main/output/real_multi_task/failure_mode_summary.json`",
        "- `main/output/repro/field_level_findings.json`",
    ]
    return "\n".join(sections) + "\n"

def generate_runtime_cost() -> str:
    runtime = load_json(SOURCES["runtime"]) or {}
    totals = runtime.get("totals", {})

    by_model_rows = []
    for model, stats in sorted((runtime.get("by_model") or {}).items()):
        by_model_rows.append(
            [
                model,
                stats.get("bundles", 0),
                stats.get("claims", 0),
                f"{stats.get('runtime_seconds_mean_per_bundle', 0.0):.3f}",
                f"{stats.get('seconds_per_claim', 0.0):.3f}",
                f"{stats.get('seconds_per_1000_cells', 0.0):.3f}",
            ]
        )

    bundle_rows = []
    for b in sorted(runtime.get("bundles", []), key=lambda x: x.get("runtime_seconds_mean", 0.0), reverse=True):
        bundle_rows.append(
            [
                b.get("bundle", "n/a"),
                b.get("task", "n/a"),
                b.get("model", "n/a"),
                b.get("claims", 0),
                b.get("raw_cells", 0),
                f"{b.get('runtime_seconds_mean', 0.0):.3f}",
                f"{b.get('seconds_per_claim', 0.0):.3f}",
            ]
        )

    sections = [
        "# Runtime And Cost",
        "",
        "Evaluator runtime profile generated from reproducibility runs.",
        "",
        f"- Bundles covered by runtime envelope: **{runtime.get('bundles_profiled', 0)}** "
        f"(measured: **{runtime.get('bundles_measured', 0)} / {runtime.get('bundles_profiled', 0)}**, "
        f"estimated: **{runtime.get('bundles_estimated', 0)} / {runtime.get('bundles_profiled', 0)}**, "
        f"measurement coverage: **{(runtime.get('measurement_coverage') or 0.0) * 100:.1f}%**)",
        f"- Claims: **{totals.get('claims', 0)}**",
        f"- Raw cells: **{totals.get('raw_cells', 0)}**",
        f"- Total mean runtime (s): **{totals.get('runtime_seconds_mean_sum', 0.0):.3f}**",
        f"- Seconds per claim: **{totals.get('seconds_per_claim', 0.0):.3f}**",
        f"- Seconds per 1000 cells: **{totals.get('seconds_per_1000_cells', 0.0):.3f}**",
        "",
        "## Runtime by model",
        "",
        md_table(
            [
                "Model",
                "Bundles",
                "Claims",
                "Mean sec/bundle",
                "Sec/claim",
                "Sec/1000 cells",
            ],
            by_model_rows,
        )
        if by_model_rows
        else "No data.",
        "",
        "## Runtime by bundle",
        "",
        md_table(
            ["Bundle", "Task", "Model", "Claims", "Raw cells", "Mean runtime (s)", "Sec/claim"],
            bundle_rows,
        )
        if bundle_rows
        else "No data.",
        "",
        "## Data source",
        "",
        "- `main/output/repro/runtime_cost_report.json`",
    ]
    return "\n".join(sections) + "\n"

def generate_release_findings() -> str:
    release_takeaways = load_json(SOURCES["release_takeaways"]) or {}
    headline = release_takeaways.get("headline_numbers", {})
    concentration = release_takeaways.get("concentration", {})
    failure = release_takeaways.get("failure_structure", {})
    policy_vs_stress = release_takeaways.get("policy_vs_stress", {})
    transfer_and_determinism = release_takeaways.get("transfer_and_determinism", {})

    release_policy = (policy_vs_stress.get("released_policy_sensitivity") or {}).get("conditions", {})
    suite_stress = policy_vs_stress.get("suite_targeted_stress", {})
    agnostic_stress = policy_vs_stress.get("agnostic_stress", {})
    adaptive = policy_vs_stress.get("adaptive_red_team", {})
    transfer_summary = transfer_and_determinism.get("transfer_summary", {})
    hardening = load_json(SOURCES["hardening"]) or {}
    hardening_replicates = hardening.get("fresh_agnostic_hardened_v1_replicates") or {}
    hardening_before = int(hardening.get("accepted_claims_before_total") or 0)
    hardening_after = int(hardening.get("accepted_claims_after_total") or 0)
    hardening_retention = float(hardening.get("accepted_claim_retention_rate") or 0.0)
    hardening_tasks_after = int(hardening.get("tasks_with_accepted_after_count") or 0)
    hardening_worst_ci_high = hardening_replicates.get("worst_ci95_high")
    fresh_release = load_json(SOURCES["fresh_agnostic_release_grade"]) or {}
    fresh_full = (fresh_release.get("conditions") or {}).get("full_contract") or {}
    fresh_leaked = int(fresh_full.get("leaked") or 0)
    fresh_total = int(fresh_full.get("total") or fresh_release.get("negatives") or 0)
    fresh_ci = fresh_full.get("false_accept_rate_ci95") or {}
    # every quote of the
    # release-grade 0/200 stress result must be paired with the reduced-rehearsal
    # 49/200 cell from ``stress_test_agnostic_fresh.json``; the two cells differ
    # on namespace and statistical budget and only mean what they mean together.
    fresh_paired = load_json(SOURCES["fresh_agnostic"]) or {}
    paired_full = (fresh_paired.get("conditions") or {}).get("full_contract") or {}
    paired_leaked = int(paired_full.get("leaked") or 0)
    paired_total = int(paired_full.get("total") or fresh_paired.get("negatives") or 0)
    docstring_repair = load_json(SOURCES["docstring_repair"]) or {}
    docstring_agg = docstring_repair.get("aggregate") or {}
    prompt_audit = load_json(SOURCES["prompt_variant_audit"]) or {}
    prompt_repair = load_json(SOURCES["prompt_variant_repair"]) or {}
    prompt_affected = int(prompt_audit.get("affected_accepted_claims_in_existing_artifacts") or 0)
    prompt_repair_covered = int(prompt_repair.get("accepted_before_in_rerun_bundles") or 0)
    prompt_retained = int(prompt_repair.get("previously_accepted_retained") or 0)
    prompt_demoted = int(prompt_repair.get("previously_accepted_demoted") or 0)

    figure_lines = []
    for rel in [
        "../assets/generated/accepted_breadth_heatmap.png",
        "../assets/generated/contract_vs_stress_rates.png",
        "../assets/generated/failure_family_counts.png",
    ]:
        path = (OUT_DIR / rel).resolve()
        if path.exists():
            figure_lines.append(f"![]({rel})")
            figure_lines.append("")

    sections = [
        "# Release Findings",
        "",
        "Auto-generated page for the headline empirical takeaways from the released benchmark artifacts.",
        "",
        f"- Accepted claims: **{headline.get('accepted', 0)} / {headline.get('claims', 0)}** "
        f"({ci_label(headline.get('acceptance_rate_ci95'))})",
        f"- Accepted tasks: **{concentration.get('accepted_tasks_count', 0)} / {concentration.get('evaluated_tasks_count', 0)}**",
        f"- Accepted claims from regenerated multi-lane bundles: **{concentration.get('accepted_in_regenerated_multilane', 0)}**",
        f"- Accepted claims retained in `canonical_real_repair_v1` lane (contract-hardening rerun): **{concentration.get('accepted_in_canonical_real_repair_v1_lane', concentration.get('accepted_in_zero_task_real_repair', 0))}**",
        f"- Accepted claims after zero-task real repair (`zero_task_real_repair.json` aggregate): **{concentration.get('accepted_in_zero_task_real_repair_artifact', 0)}**",
        f"- Accepted claims from canonical historical bundles: **{concentration.get('accepted_in_canonical_real', 0)}**",
        f"- Statistics + robustness failure share: **{pct(failure.get('statistics_plus_robustness_fraction'))}**",
        f"- Contract-hardening V1 candidate: **{hardening_after} / {hardening_before}** accepted claims retained "
        f"({pct(hardening_retention)}), **{hardening_tasks_after} / {concentration.get('evaluated_tasks_count', 0)}** accepted tasks retained, "
        f"worst hardened-stress CI upper bound **{pct(hardening_worst_ci_high)}** across **{hardening_replicates.get('namespace_count', 0)}** rotated namespaces",
        f"- Release-grade fresh agnostic current-contract stress: **{fresh_leaked} / {fresh_total}** false accepts "
        f"({(fresh_ci.get('label') if isinstance(fresh_ci, dict) else 'n/a')}); paired reduced-rehearsal cell (different namespace and statistical budget): **{paired_leaked} / {paired_total}** false accepts. Quote both cells together; neither is a stand-alone Goodhart-resistance number.",
        f"- Docstring distributed-head repair: **{docstring_agg.get('accepted_after_real_total', 0)}** accepted claims; "
        f"top residual gates **{docstring_agg.get('gate_failures_after_real', {})}**",
        f"- Prompt-variant repair frontier: unsupported nominal variants affect **{prompt_affected}** accepted claims; "
        f"task-supported reruns retain **{prompt_retained} / {prompt_repair_covered}** and demote **{prompt_demoted} / {prompt_repair_covered}**",
        f"- Stable submission reviews: **{transfer_and_determinism.get('submission_review_stable_bundles', 0)} / "
        f"{transfer_and_determinism.get('submission_review_bundles_reviewed', 0)}**",
        "",
        "## Core takeaways",
        "",
        f"1. The visible release accepts only **{headline.get('accepted', 0)} / {headline.get('claims', 0)}** claims, "
        f"and those accepted claims occupy **{concentration.get('accepted_tasks_count', 0)} / {concentration.get('evaluated_tasks_count', 0)}** released tasks but remain uneven across the task-model grid.",
        f"2. Controls are the most acceptance-sensitive suite on released claims: **"
        f"{release_policy.get('full_contract', {}).get('accepted', 0)} → "
        f"{release_policy.get('no_controls_suite', {}).get('accepted', 0)}** accepted claims under the counterfactual.",
        f"3. Synthetic false-accept stress behaves differently: suite-targeted FAR changes from **"
        f"{suite_stress.get('full_contract', {}).get('leaked', 0)} / "
        f"{suite_stress.get('full_contract', {}).get('total', 0)}** under the full contract to **"
        f"{suite_stress.get('no_controls_suite', {}).get('leaked', 0)} / "
        f"{suite_stress.get('no_controls_suite', {}).get('total', 0)}** under controls ablation, with analogous jumps under statistical-rigor and robustness ablations.",
        f"4. The benchmark is useful but not solved: on the legacy released artifact surface, evaluator-agnostic latent stress leaks **"
        f"{agnostic_stress.get('full_contract', {}).get('leaked', 0)} / "
        f"{agnostic_stress.get('full_contract', {}).get('total', 0)}**; a release-grade fresh agnostic refresh leaks **"
        f"{fresh_leaked} / {fresh_total}**, with a paired reduced-rehearsal cell at **{paired_leaked} / {paired_total}** (different namespace and statistical budget; quote both together). Adaptive search succeeds **"
        f"{adaptive.get('successes', 0)} / {adaptive.get('attempts', 0)}**, and transfer-confirmed accepted claims remain **"
        f"{transfer_summary.get('transfer_confirmed_claims', 0)} / {transfer_summary.get('accepted_claims_tested', 0)}**. "
        f"V1 hardening reduces agnostic leakage in two rotated diagnostics but keeps only **{hardening_after} / {hardening_before}** accepted claims, so it is a migration tradeoff rather than a free fix. "
        "See `main/output/repro/release_readiness_report.md` and "
        "`main/output/repro/direct_blocker_closure_report.md` for fresh rotated agnostic diagnostics and hardened-contract follow-up.",
        f"5. Prompt robustness is a measured governance issue rather than a settled claim: task-supported prompt repair retains **{prompt_retained} / {prompt_repair_covered}** affected accepted claims and demotes **{prompt_demoted} / {prompt_repair_covered}**. "
        "The old prompt-holdout count should be read with the repair caveat until repaired bundles are promoted and dependent diagnostics are rerun.",
        "",
        "## Figures",
        "",
    ] + figure_lines + [
        "## Data sources",
        "",
        "- `main/output/repro/release_takeaways.json`",
        "- `main/output/repro/field_level_findings.json`",
        "- `main/output/repro/transfer_results_summary.json`",
        "- `main/output/repro/stress_test_agnostic_fresh_release_grade.json`",
        "- `main/output/repro/docstring_distributed_repair.json`",
        "- `main/output/repro/contract_hardening_v1_summary.json`",
        "- `main/output/repro/prompt_variant_validity_audit.json`",
        "- `main/output/repro/prompt_variant_repair_rerun.json`",
        "- `main/output/community_submissions/community_value_summary.json`",
    ]
    return "\n".join(sections) + "\n"

def generate_community_impact() -> str:
    community = load_json(SOURCES["community"]) or {}

    decisions = sort_count_map(community.get("workflow_decision_counts"))
    failed = community.get("top_failed_gates", [])
    failed_rows = [[gate, count] for gate, count in failed]
    bundles = community.get("bundle_summaries", [])

    bundle_rows = []
    for b in bundles:
        bundle_rows.append(
            [
                b.get("bundle", "n/a"),
                b.get("discovery_candidates", 0),
                b.get("accepted_for_claims", 0),
                b.get("blocked_from_claims", 0),
                "yes" if b.get("stable") else "no",
            ]
        )

    sections = [
        "# Community Impact",
        "",
        "Submission-review outcomes across the canonical released bundle set used for workflow guidance.",
        "",
        f"- Bundles reviewed: **{community.get('bundles_reviewed', 0)}**",
        f"- Stable across reruns: **{community.get('stable_bundles', 0)} / {community.get('bundles_reviewed', 0)}**",
        f"- Discovery candidates: **{community.get('workflow_totals', {}).get('discovery_candidates', 0)}**",
        f"- Accepted claims: **{community.get('workflow_totals', {}).get('accepted_for_claims', 0)}**",
        f"- Blocked or downgraded claims: **{community.get('workflow_totals', {}).get('blocked_from_claims', 0)}**",
        f"- Decision change rate: **{pct(community.get('workflow_totals', {}).get('decision_change_rate'))}**",
        "",
        "## Workflow decisions",
        "",
        md_table(["Decision", "Count"], [[k, v] for k, v in decisions]) if decisions else "No data.",
        "",
        "## Top failed gates",
        "",
        md_table(["Gate", "Count"], failed_rows) if failed_rows else "No data.",
        "",
        "## Bundle outcomes",
        "",
        md_table(["Bundle", "Candidates", "Accepted", "Blocked", "Stable"], bundle_rows)
        if bundle_rows
        else "No data.",
        "",
        "## Data source",
        "",
        "- `main/output/community_submissions/community_value_summary.json`",
    ]
    return "\n".join(sections) + "\n"

def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    outputs = {
        "benchmark-snapshot.md": generate_snapshot(),
        "leaderboard.md": generate_leaderboard(),
        "failure-modes.md": generate_failure_modes(),
        "runtime-cost.md": generate_runtime_cost(),
        "community-impact.md": generate_community_impact(),
        "release-findings.md": generate_release_findings(),
    }

    for name, content in outputs.items():
        path = OUT_DIR / name
        path.write_text(content, encoding="utf-8")
        print(f"wrote {path.relative_to(ROOT)}")

if __name__ == "__main__":
    main()
