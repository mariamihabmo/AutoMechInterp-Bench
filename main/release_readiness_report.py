#!/usr/bin/env python3
"""Summarize current artifact-backed release readiness from cached artifacts.

Separates released artifact-backed headline numbers, local diagnostic outputs,
and items that still require external inputs or real-model reruns.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

try:
    from _bundle_analysis import write_json, write_text
except ModuleNotFoundError:
    from main._bundle_analysis import write_json, write_text

ROOT = Path(__file__).resolve().parents[1]
REPRO = ROOT / "main" / "output" / "repro"
HOLDOUT = ROOT / "holdout" / "results_summary.json"
OUT_JSON = REPRO / "release_readiness_report.json"
OUT_MD = REPRO / "release_readiness_report.md"


def _load(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text())


def _parse_ci95(raw: Any) -> list[float]:
    if isinstance(raw, dict):
        return [float(raw.get("low", 0.0)), float(raw.get("high", 0.0))]
    if isinstance(raw, (list, tuple)) and len(raw) >= 2:
        return [float(raw[0]), float(raw[1])]
    return [0.0, 0.0]


def main() -> None:
    REPRO.mkdir(parents=True, exist_ok=True)

    breadth = _load(REPRO / "benchmark_breadth_summary.json") or {}
    field = _load(REPRO / "field_level_findings.json") or {}
    transfer = _load(REPRO / "transfer_results_summary.json") or {}
    transfer_breakdown = _load(REPRO / "transfer_failure_breakdown.json") or {}
    zero_task = _load(REPRO / "zero_task_gate_breakdown.json") or {}
    zero_task_repair = _load(REPRO / "zero_task_confirmatory_repair.json") or {}
    zero_task_real_repair = _load(REPRO / "zero_task_real_repair.json") or {}
    breadth_gap = _load(REPRO / "breadth_gap_analysis.json") or {}
    prompt_holdout = _load(REPRO / "prompt_holdout_transfer_control.json") or {}
    high_power_prompt_holdout = _load(REPRO / "prompt_holdout_high_power_n40_rerun.json") or {}
    same_family = _load(REPRO / "same_family_transfer_preflight.json") or {}
    external_preflight = _load(REPRO / "external_evidence_preflight.json") or {}
    fresh_agnostic_path = REPRO / "stress_test_agnostic_fresh_release_grade.json"
    fresh_agnostic = _load(fresh_agnostic_path)
    fresh_agnostic_source = "release_grade"
    if fresh_agnostic is None:
        fresh_agnostic = _load(REPRO / "stress_test_agnostic_fresh.json") or {}
        fresh_agnostic_source = "reduced_diagnostic"
    hardening = _load(REPRO / "contract_hardening_v1_summary.json") or {}
    migration = _load(REPRO / "contract_hardening_v1_migration_decision.json") or {}
    runtime = _load(REPRO / "runtime_cost_report.json") or {}
    transfer_queue = _load(REPRO / "transfer_breadth_candidate_table.json") or {}
    docstring_explorer = _load(REPRO / "docstring_method_sensitivity_explorer.json") or {}
    prompt_variant_audit = _load(REPRO / "prompt_variant_validity_audit.json") or {}
    prompt_variant_repair = _load(REPRO / "prompt_variant_repair_rerun.json") or {}
    holdout = _load(HOLDOUT) or {}

    tasks_total = len((field.get("acceptance_by_task") or {}))
    tasks_with_accepted = sum(
        1
        for row in (field.get("acceptance_by_task") or {}).values()
        if int(row.get("accepted", 0)) > 0
    )

    # Legacy released stress (from current public artifact surface).
    legacy_full_contract = ((
        ((_load(REPRO / "agnostic_leak_forensics.json") or {}).get("per_condition") or {})
    ).get("full_contract") or {})
    legacy_far = float(legacy_full_contract.get("false_accept_rate", 0.0))
    legacy_ci95 = _parse_ci95(legacy_full_contract.get("false_accept_rate_ci95"))

    # Fresh refresh run.
    fresh_full_contract = ((fresh_agnostic.get("conditions") or {}).get("full_contract") or {})
    fresh_far = float(fresh_full_contract.get("false_accept_rate", 0.0))
    fresh_ci95 = _parse_ci95(fresh_full_contract.get("false_accept_rate_ci95"))
    fresh_negatives = int(fresh_agnostic.get("negatives") or 0)

    hardening_replicates = hardening.get("fresh_agnostic_hardened_v1_replicates") or {}
    hardening_primary = hardening.get("fresh_agnostic_hardened_v1") or {}
    hardening_retention = float(hardening.get("accepted_claim_retention_rate") or 0.0)
    hardening_after = int(hardening.get("accepted_claims_after_total") or 0)
    hardening_before = int(hardening.get("accepted_claims_before_total") or 0)
    hardening_tasks_after = int(hardening.get("tasks_with_accepted_after_count") or 0)
    hardening_worst_ci_high = hardening_replicates.get("worst_ci95_high")

    external_blinded = int(((holdout.get("external_blinded") or {}).get("n_submissions") or 0))
    external_evaluated = int(((holdout.get("external_blinded") or {}).get("n_evaluated") or 0))
    holdout_rehearsal_exists = bool((REPRO / "holdout_v0-rehearsal.json").exists())

    prompt_holdout_claims = int(prompt_holdout.get("accepted_claims_with_multi_prompt") or 0)
    prompt_holdout_all = int(prompt_holdout.get("claims_passing_all_holdouts") or 0)
    prompt_holdout_checks = int(prompt_holdout.get("passing_holdout_checks") or 0)
    prompt_holdout_total_checks = int(prompt_holdout.get("total_holdout_checks") or 0)
    high_power_examples = int(high_power_prompt_holdout.get("examples_per_cell") or 0)
    high_power_planned_bundles = int(high_power_prompt_holdout.get("planned_bundles") or 0)
    high_power_rerun_bundles = int(high_power_prompt_holdout.get("bundles_rerun") or 0)
    high_power_covered_claims = int(high_power_prompt_holdout.get("original_accepted_claims_covered") or 0)
    high_power_retained_claims = int(high_power_prompt_holdout.get("original_accepted_claims_retained") or 0)
    high_power_demoted_claims = int(high_power_prompt_holdout.get("original_accepted_claims_demoted") or 0)
    high_power_retained_holdout_pass = int(
        high_power_prompt_holdout.get("retained_original_accepted_claims_passing_all_holdouts") or 0
    )
    high_power_retained_holdout_fail = int(
        high_power_prompt_holdout.get("retained_original_accepted_claims_failing_any_holdout") or 0
    )
    high_power_checks_pass = int(high_power_prompt_holdout.get("passing_holdout_checks_on_retained_claims") or 0)
    high_power_checks_total = int(high_power_prompt_holdout.get("total_holdout_checks_on_retained_claims") or 0)
    high_power_complete = bool(high_power_planned_bundles and high_power_rerun_bundles >= high_power_planned_bundles)

    same_family_ready = int(same_family.get("ready_to_run_count") or 0)
    same_family_missing_eligible_rows = int(same_family.get("missing_eligible_same_family_rows_count") or 0)
    same_family_already_scored = int(same_family.get("already_scored_count") or 0)
    same_family_blocked = int(same_family.get("blocked_count") or 0)

    zero_repair_agg = zero_task_repair.get("aggregate") or {}
    zero_real_agg = zero_task_real_repair.get("aggregate") or {}
    zero_confirmatory_present_before = int(
        zero_real_agg.get("confirmatory_present_failures_before")
        or zero_repair_agg.get("confirmatory_present_failures_before")
        or 0
    )
    zero_confirmatory_present_after = int(
        zero_real_agg.get("confirmatory_present_failures_after_real")
        or zero_repair_agg.get("confirmatory_present_failures_after_mock")
        or 0
    )
    zero_confirmatory_ci_before = int(
        zero_real_agg.get("confirmatory_ci_failures_before")
        or zero_repair_agg.get("confirmatory_ci_failures_before")
        or 0
    )
    zero_confirmatory_ci_after = int(
        zero_real_agg.get("confirmatory_ci_failures_after_real")
        or zero_repair_agg.get("confirmatory_ci_failures_after_mock")
        or 0
    )
    zero_tasks_with_real_accepts = list(zero_real_agg.get("tasks_with_any_real_accept_after") or [])
    zero_real_accepted = int(zero_real_agg.get("accepted_after_real_total") or 0)
    remaining_zero_tasks = list(zero_task.get("zero_task_set") or [])
    task_model_zero_cells = int(breadth_gap.get("n_zero_acceptance_cells") or 0)
    task_model_total_cells = int(breadth_gap.get("n_cells") or 0)
    prompt_variant_affected_accepts = int(prompt_variant_audit.get("affected_accepted_claims_in_existing_artifacts") or 0)
    prompt_variant_canonical_affected_accepts = int(prompt_variant_audit.get("canonical_affected_accepted_claims") or 0)
    prompt_variant_canonical_unsupported_files = int(prompt_variant_audit.get("canonical_files_with_unsupported_prompt_variants") or 0)
    prompt_variant_planned_bundles = int(
        prompt_variant_repair.get("planned_unsupported_prompt_bundles")
        or prompt_variant_repair.get("planned_affected_bundles_with_accepts")
        or 0
    )
    prompt_variant_rerun_bundles = int(prompt_variant_repair.get("bundles_rerun") or 0)
    prompt_variant_covered_accepts = int(prompt_variant_repair.get("accepted_before_in_rerun_bundles") or 0)
    prompt_variant_retained_accepts = int(prompt_variant_repair.get("previously_accepted_retained") or 0)
    prompt_variant_demoted_accepts = int(prompt_variant_repair.get("previously_accepted_demoted") or 0)
    prompt_variant_repair_incomplete = (
        (prompt_variant_affected_accepts > 0 or prompt_variant_canonical_affected_accepts > 0)
        and (
            prompt_variant_rerun_bundles < prompt_variant_planned_bundles
            or prompt_variant_covered_accepts < prompt_variant_affected_accepts
            or prompt_variant_canonical_affected_accepts > 0
        )
    )
    transfer_queue_summary = transfer_queue.get("summary") or {}
    top_transfer_candidate = (
        transfer_queue_summary.get("top_priority")
        or ((transfer_queue.get("top_candidates") or [{}])[0] if transfer_queue.get("top_candidates") else {})
        or {}
    )

    release_quality_criteria = {
        "operational_holdout_execution": bool(holdout_rehearsal_exists and external_evaluated > 0),
        "second_cross_model_confirmed_claim": int(transfer.get("transfer_confirmed_claims", 0)) >= 2,
        "accepted_claims_in_at_least_5_of_8_tasks": tasks_with_accepted >= 5,
        "second_external_third_party_bundle_accepted": external_blinded >= 2,
        "agnostic_far_upper_bound_below_5pct": float(fresh_ci95[1] if fresh_negatives else legacy_ci95[1]) < 0.05,
    }
    satisfied = sum(1 for value in release_quality_criteria.values() if value)
    release_quality_blockers = []
    if external_evaluated <= 0:
        release_quality_blockers.append("no_external_blinded_or_independent_bundle_evaluated")
    if not release_quality_criteria["operational_holdout_execution"]:
        release_quality_blockers.append("no_operational_external_custodian_holdout")
    if not release_quality_criteria["agnostic_far_upper_bound_below_5pct"]:
        release_quality_blockers.append("current_contract_agnostic_far_upper_bound_not_below_5pct")
    if tasks_with_accepted < tasks_total or remaining_zero_tasks or task_model_zero_cells:
        release_quality_blockers.append("residual_task_model_breadth_gap")
    if prompt_variant_repair_incomplete:
        release_quality_blockers.append("prompt_variant_aliasing_repair_incomplete")
    if high_power_complete and (
        high_power_demoted_claims > 0 or high_power_retained_holdout_fail > 0
    ):
        release_quality_blockers.append("high_power_prompt_holdout_frontier_incomplete")

    prioritized_actions = []
    if prompt_variant_repair_incomplete:
        prioritized_actions.append(
            {
                "priority": 1,
                "gap": "prompt-variant aliasing repair",
                "why_open": (
                    f"{prompt_variant_affected_accepts} accepted claims sit in existing artifacts with unsupported nominal prompt variants. "
                    f"Repair reruns currently cover {prompt_variant_covered_accepts} accepted claims across "
                    f"{prompt_variant_rerun_bundles}/{prompt_variant_planned_bundles} affected accepted bundles, retaining "
                    f"{prompt_variant_retained_accepts} and demoting {prompt_variant_demoted_accepts}. "
                    f"The canonical surface still has {prompt_variant_canonical_unsupported_files} unsupported-prompt files "
                    f"covering {prompt_variant_canonical_affected_accepts} accepted claims."
                ),
                "next_action": "Finish task-supported prompt-variant reruns and decide explicitly whether to promote repaired bundles into the canonical surface.",
                "expected_payoff": "Closes a prompt-robustness objection that survived earlier checks.",
            }
        )

    if high_power_complete and (
        high_power_demoted_claims > 0 or high_power_retained_holdout_fail > 0
    ):
        prioritized_actions.append(
            {
                "priority": 1,
                "gap": "prompt-holdout robustness",
                "why_open": (
                    f"The prospective n={high_power_examples} rerun covered all "
                    f"{high_power_covered_claims} originally accepted claims across "
                    f"{high_power_rerun_bundles}/{high_power_planned_bundles} accepted bundles. "
                    f"It retained {high_power_retained_claims}/{high_power_covered_claims}, demoted "
                    f"{high_power_demoted_claims}, and only {high_power_retained_holdout_pass}/"
                    f"{high_power_retained_claims} retained claims passed all held-out prompts "
                    f"({high_power_checks_pass}/{high_power_checks_total} held-out checks)."
                ),
                "next_action": (
                    "Treat arithmetic, IOI structural prompts, and one sentiment claim as targeted "
                    "prompt-robustness weaknesses; do not promote a stronger prompt-robustness claim "
                    "unless a pre-registered repair rerun improves the full accepted surface."
                ),
                "expected_payoff": "Turns a vague prompt-generalization concern into an artifact-backed field-level fragility finding.",
            }
        )

    if not release_quality_criteria["second_cross_model_confirmed_claim"]:
        candidates = [
            {
                "bundle": row.get("bundle"),
                "source_model": row.get("source_model"),
                "target_model": row.get("target_model"),
                "task": row.get("task"),
                "claims_passing_all_holdouts": row.get("claims_passing_all_holdouts"),
                "accepted_claims_with_multi_prompt": row.get("accepted_claims_with_multi_prompt"),
            }
            for row in (same_family.get("blocked") or [])[:3]
        ]
        prioritized_actions.append(
            {
                "priority": 1,
                "gap": "cross-model transfer",
                "why_open": (
                    f"transfer_confirmed_claims={transfer.get('transfer_confirmed_claims', 0)} of accepted_claims_tested="
                    f"{transfer.get('accepted_claims_tested', 0)}; prompt_holdout={prompt_holdout_all}/{prompt_holdout_claims} claims and "
                    f"{prompt_holdout_checks}/{prompt_holdout_total_checks} checks pass. Same-family transfer is no longer a pure "
                    f"weight-availability issue: ready_to_run_missing_rows={same_family_ready}, "
                    f"missing_eligible_rows={same_family_missing_eligible_rows}, already_scored={same_family_already_scored}, "
                    f"blocked={same_family_blocked}."
                ),
                "next_action": "Cache the target-model weights locally and run the top same-family transfer candidates immediately.",
                "concrete_candidates": candidates,
                "expected_payoff": "Most direct path to turning the transfer weakness into a concrete scientific result.",
            }
        )

    if not release_quality_criteria["accepted_claims_in_at_least_5_of_8_tasks"]:
        prioritized_actions.append(
            {
                "priority": 2,
                "gap": "breadth",
                "why_open": (
                    f"tasks_with_accepted={tasks_with_accepted}/{tasks_total}; zero-task real repair removed confirmatory_present "
                    f"failures {zero_confirmatory_present_before}->{zero_confirmatory_present_after} and confirmatory_ci failures "
                    f"{zero_confirmatory_ci_before}->{zero_confirmatory_ci_after}, with real accepts now appearing in {zero_tasks_with_real_accepts}."
                ),
                "next_action": "Run real-model discovery / Stage-2 on the upgraded zero-task protocols, starting with the closest-to-pass remaining cells.",
                "expected_payoff": "Most direct path to closing task-level breadth without changing the contract.",
            }
        )
    elif tasks_with_accepted < tasks_total or remaining_zero_tasks or task_model_zero_cells:
        prioritized_actions.append(
            {
                "priority": 2,
                "gap": "residual breadth",
                "why_open": (
                    f"task-level breadth criterion is now satisfied at {tasks_with_accepted}/{tasks_total}, "
                    f"but remaining_zero_tasks={remaining_zero_tasks}, zero_acceptance_task_model_cells={task_model_zero_cells}/{task_model_total_cells}, "
                    f"and accepted evidence is still uneven across the task-model grid. "
                    f"Real zero-task repair contributes {zero_real_accepted} accepted claims in {zero_tasks_with_real_accepts}."
                ),
                "next_action": "Target zero-accepted task-model cells without changing the contract; prioritize closest-to-pass cells in breadth_gap_analysis.json.",
                "expected_payoff": "Turns task-level breadth from criterion-satisfying into concrete external-validity evidence.",
            }
        )

    if not release_quality_criteria["second_external_third_party_bundle_accepted"]:
        prioritized_actions.append(
            {
                "priority": 3,
                "gap": "external ecosystem / blinded authorship",
                "why_open": (
                    f"external_blinded_submissions={external_blinded}, external_evaluated={external_evaluated}; maintainer_pilot="
                    f"{((external_preflight.get('maintainer_pilot') or {}).get('n_submissions') or 0)} and holdout_rehearsal_exists={holdout_rehearsal_exists}."
                ),
                "next_action": "Ingest one real external_blinded bundle and run one real private-suite holdout scoring pass with an external custodian.",
                "expected_payoff": "Largest governance credibility gain; scaffolding is already in place, but evidence is still absent.",
            }
        )

    if not release_quality_criteria["agnostic_far_upper_bound_below_5pct"]:
        hardening_note = ""
        if hardening:
            if hardening_worst_ci_high is not None:
                hardening_note = (
                    f" Contract-hardening V1 is a candidate migration, not the released contract: it keeps "
                    f"{hardening_after}/{hardening_before} accepted claims ({hardening_retention * 100:.1f}% retention), "
                    f"accepted claims in {hardening_tasks_after}/{tasks_total} tasks, and its worst rotated hardened-stress "
                    f"CI upper bound is {float(hardening_worst_ci_high) * 100:.1f}%."
                )
            else:
                hardening_note = (
                    f" Contract-hardening V1 is a candidate migration, not the released contract: it keeps "
                    f"{hardening_after}/{hardening_before} accepted claims ({hardening_retention * 100:.1f}% retention)."
                )
        prioritized_actions.append(
            {
                "priority": 4,
                "gap": "agnostic leak confidence",
                "why_open": (
                    f"legacy released stress was FAR={legacy_far:.3f} with ci95={legacy_ci95}; fresh rotated stress refresh over "
                    f"{fresh_negatives} negatives is FAR={fresh_far:.3f} with ci95={fresh_ci95} from source={fresh_agnostic_source}."
                    f"{hardening_note}"
                ),
                "next_action": "Treat V1 as a versioned migration candidate, then validate it with a genuinely independent generator/custodian before adopting it.",
                "expected_payoff": "Turns Goodhart resistance into an explicit precision-recall frontier instead of an unvalidated threshold tweak.",
            }
        )

    if not release_quality_criteria["operational_holdout_execution"]:
        prioritized_actions.append(
            {
                "priority": 5,
                "gap": "operational holdout",
                "why_open": (
                    f"holdout_rehearsal_exists={holdout_rehearsal_exists}, external_evaluated={external_evaluated}."
                ),
                "next_action": "Run the aggregate-only helper on a real private suite with an external custodian and keep it separated from pilot/rehearsal counts.",
                "expected_payoff": "Closes a named verdict criterion and demonstrates governance, not just tooling.",
            }
        )

    payload = {
        "schema_version": 2,
        "generated_by": "main/release_readiness_report.py",
        "headline": {
            "bundle_count": int(breadth.get("bundle_count", 0)),
            "claim_count": int(breadth.get("claim_count", 0)),
            "accepted_claims": int((field.get("totals") or {}).get("accepted", 0)),
            "tasks_with_accepted": tasks_with_accepted,
            "tasks_total": tasks_total,
            "transfer_confirmed_claims": int(transfer.get("transfer_confirmed_claims", 0)),
            "transfer_tested_claims": int(transfer.get("accepted_claims_tested", 0)),
            "prompt_holdout_claims_passing_all": prompt_holdout_all,
            "prompt_holdout_claims_tested": prompt_holdout_claims,
            "prompt_holdout_checks_passing": prompt_holdout_checks,
            "prompt_holdout_checks_total": prompt_holdout_total_checks,
            "high_power_prompt_holdout_examples_per_cell": high_power_examples,
            "high_power_prompt_holdout_bundles_rerun": high_power_rerun_bundles,
            "high_power_prompt_holdout_planned_bundles": high_power_planned_bundles,
            "high_power_prompt_holdout_original_claims_covered": high_power_covered_claims,
            "high_power_prompt_holdout_original_claims_retained": high_power_retained_claims,
            "high_power_prompt_holdout_original_claims_demoted": high_power_demoted_claims,
            "high_power_prompt_holdout_retained_claims_passing_all": high_power_retained_holdout_pass,
            "high_power_prompt_holdout_retained_claims_failing_any": high_power_retained_holdout_fail,
            "high_power_prompt_holdout_checks_passing": high_power_checks_pass,
            "high_power_prompt_holdout_checks_total": high_power_checks_total,
            "same_family_ready_to_run": same_family_ready,
            "same_family_missing_eligible_rows": same_family_missing_eligible_rows,
            "same_family_already_scored": same_family_already_scored,
            "same_family_blocked": same_family_blocked,
            "legacy_agnostic_full_contract_far": legacy_far,
            "legacy_agnostic_full_contract_far_ci95": legacy_ci95,
            "fresh_agnostic_full_contract_far": fresh_far,
            "fresh_agnostic_full_contract_far_ci95": fresh_ci95,
            "fresh_agnostic_negatives": fresh_negatives,
            "fresh_agnostic_source": fresh_agnostic_source,
            "contract_hardening_v1_accepted_before": hardening_before,
            "contract_hardening_v1_accepted_after": hardening_after,
            "contract_hardening_v1_retention": hardening_retention,
            "contract_hardening_v1_tasks_with_accepted_after": hardening_tasks_after,
            "contract_hardening_v1_primary_far": hardening_primary.get("false_accept_rate"),
            "contract_hardening_v1_worst_ci95_high": hardening_worst_ci_high,
            "contract_hardening_v1_namespace_count": hardening_replicates.get("namespace_count", 0),
            "contract_hardening_v1_migration_decision_status": migration.get("decision_status"),
            "contract_hardening_v1_independent_evidence": ((migration.get("criteria") or {}).get("independent_evidence")),
            "runtime_bundles_measured": int(runtime.get("bundles_measured") or 0),
            "runtime_measurement_coverage": float(runtime.get("measurement_coverage") or 0.0),
            "runtime_estimated_minutes": float(((runtime.get("totals") or {}).get("estimated_runtime_minutes")) or 0.0),
            "runtime_estimated_rerun_minutes": float(((runtime.get("totals") or {}).get("estimated_runtime_with_reruns_minutes")) or 0.0),
            "transfer_non_country_candidate_claims": int(transfer_queue_summary.get("non_country_candidate_claims") or 0),
            "top_transfer_candidate": top_transfer_candidate,
            "docstring_explorer_diagnosis_counts": ((docstring_explorer.get("summary") or {}).get("diagnosis_counts") or {}),
            "external_blinded_submissions": external_blinded,
            "external_blinded_evaluated": external_evaluated,
            "holdout_rehearsal_exists": holdout_rehearsal_exists,
            "zero_task_confirmatory_present_failures_before": zero_confirmatory_present_before,
            "zero_task_confirmatory_present_failures_after_real": zero_confirmatory_present_after,
            "zero_task_confirmatory_ci_failures_before": zero_confirmatory_ci_before,
            "zero_task_confirmatory_ci_failures_after_real": zero_confirmatory_ci_after,
            "zero_task_real_repair_accepted_claims": zero_real_accepted,
            "zero_task_real_repair_tasks_with_accepts": zero_tasks_with_real_accepts,
            "remaining_zero_tasks": remaining_zero_tasks,
            "task_model_zero_acceptance_cells": task_model_zero_cells,
            "task_model_total_cells": task_model_total_cells,
            "prompt_variant_affected_accepted_claims": prompt_variant_affected_accepts,
            "prompt_variant_canonical_affected_accepted_claims": prompt_variant_canonical_affected_accepts,
            "prompt_variant_canonical_unsupported_files": prompt_variant_canonical_unsupported_files,
            "prompt_variant_planned_bundles": prompt_variant_planned_bundles,
            "prompt_variant_rerun_bundles": prompt_variant_rerun_bundles,
            "prompt_variant_covered_accepted_claims": prompt_variant_covered_accepts,
            "prompt_variant_retained_accepted_claims": prompt_variant_retained_accepts,
            "prompt_variant_demoted_accepted_claims": prompt_variant_demoted_accepts,
        },
        "release_quality_criteria": release_quality_criteria,
        "n_release_quality_criteria_satisfied": satisfied,
        "n_additional_count_criteria_needed_for_old_plausible_threshold": max(0, 2 - satisfied),
        "release_quality_blockers": release_quality_blockers,
        "prioritized_actions": prioritized_actions,
        "verdict": (
            "not_yet_maintrack_plausible" if satisfied < 2
            else "plausible_but_not_high_confidence_release_quality" if release_quality_blockers
            else "release_quality_candidate_pending_external_review"
        ),
        "warning": (
            "This report operationalizes late-stage release criteria but does not certify release readiness by count alone. "
            "The fresh agnostic refresh and hardening-candidate stress replicates use benchmark-authored generators, so treat them as release-grade stress/tradeoff evidence, not as independent Goodhart validation."
        ),
    }
    write_json(OUT_JSON, payload)

    lines = [
        "# Release Readiness Report",
        "",
        "> **Filename note.** This report does NOT certify release-quality. The verdict is",
        "> `plausible_but_not_high_confidence_release_quality`. The legacy filename is retained to",
        "> preserve cross-references and committed SHAs; treat it as a release-readiness report",
        "> with a hard cap at the contract-relative tier.",
        "",
        f"- Bundles: **{payload['headline']['bundle_count']}**",
        f"- Claims: **{payload['headline']['claim_count']}**",
        f"- Accepted claims: **{payload['headline']['accepted_claims']}**",
        f"- Tasks with accepted claims: **{tasks_with_accepted}/{tasks_total}**",
        f"- Cross-model-confirmed claims: **{payload['headline']['transfer_confirmed_claims']}/{payload['headline']['transfer_tested_claims']}**",
        f"- Prompt-holdout control: **{prompt_holdout_all}/{prompt_holdout_claims}** claims and **{prompt_holdout_checks}/{prompt_holdout_total_checks}** checks pass",
        f"- High-power prompt-holdout diagnostic (n={high_power_examples}): **{high_power_retained_claims}/{high_power_covered_claims}** original accepted claims retained, **{high_power_retained_holdout_pass}/{high_power_retained_claims}** retained claims pass all holdouts, **{high_power_checks_pass}/{high_power_checks_total}** retained-claim holdout checks pass",
        f"- Same-family transfer locally ready to run: **{same_family_ready}**, blocked: **{same_family_blocked}**",
        f"- Legacy agnostic FAR (released artifact): **{legacy_far * 100:.1f}%** with 95% CI [{legacy_ci95[0] * 100:.1f}%, {legacy_ci95[1] * 100:.1f}%]",
        f"- Fresh agnostic FAR ({fresh_agnostic_source.replace('_', ' ')}, rotated refresh, {fresh_negatives} negatives): **{fresh_far * 100:.1f}%** with 95% CI [{fresh_ci95[0] * 100:.1f}%, {fresh_ci95[1] * 100:.1f}%]",
        f"- Contract-hardening V1 candidate: **{hardening_after}/{hardening_before}** accepted claims retained ({hardening_retention * 100:.1f}%), **{hardening_tasks_after}/{tasks_total}** accepted tasks retained, worst hardened-stress CI upper bound **{(float(hardening_worst_ci_high) * 100 if hardening_worst_ci_high is not None else 0.0):.1f}%** across **{hardening_replicates.get('namespace_count', 0)}** rotated namespaces",
        f"- V1 migration decision: **{payload['headline']['contract_hardening_v1_migration_decision_status'] or 'missing'}**; independent evidence: **{payload['headline']['contract_hardening_v1_independent_evidence']}**",
        f"- Runtime envelope: **{payload['headline']['runtime_estimated_minutes']:.1f}** minutes one sweep, **{payload['headline']['runtime_estimated_rerun_minutes']:.1f}** minutes with reruns; measured coverage **{payload['headline']['runtime_bundles_measured']}/{payload['headline']['bundle_count']}** ({payload['headline']['runtime_measurement_coverage'] * 100:.1f}%)",
        f"- Transfer breadth queue: **{payload['headline']['transfer_non_country_candidate_claims']}** non-country candidate claims need new transfer evidence",
        f"- Top transfer tail case: `{top_transfer_candidate.get('bundle', 'missing')} / {top_transfer_candidate.get('hypothesis_id', 'missing')}` is **{top_transfer_candidate.get('current_transfer_status', 'missing')}** at **{float(top_transfer_candidate.get('floor_fraction') or 0.0) * 100:.1f}%** of the floor after the preregistered n=200 scored row",
        f"- Docstring explorer diagnosis counts: **{payload['headline']['docstring_explorer_diagnosis_counts']}**",
        f"- External blinded submissions evaluated: **{external_evaluated}**",
        f"- Holdout rehearsal artifact present: **{holdout_rehearsal_exists}**",
        f"- Zero-task real repair accepted claims: **{zero_real_accepted}** across **{len(zero_tasks_with_real_accepts)}** formerly zero-accepted tasks",
        f"- Remaining zero-accepted tasks: **{', '.join(remaining_zero_tasks) or 'none'}**",
        f"- Zero-accepted task-model cells: **{task_model_zero_cells}/{task_model_total_cells}**",
        f"- Prompt-variant repair: **{prompt_variant_covered_accepts}/{prompt_variant_affected_accepts}** affected accepted claims covered; retained **{prompt_variant_retained_accepts}**, demoted **{prompt_variant_demoted_accepts}**",
        f"- Zero-task confirmatory-present failures (real repair): **{zero_confirmatory_present_before} -> {zero_confirmatory_present_after}**",
        f"- Zero-task confirmatory-CI failures (real repair): **{zero_confirmatory_ci_before} -> {zero_confirmatory_ci_after}**",
        f"- Bottom-line verdict: **{payload['verdict']}**",
        "",
        "## Binding release-quality criteria status",
        "",
        "| criterion | satisfied |",
        "|---|---|",
    ]
    for name, value in release_quality_criteria.items():
        lines.append(f"| `{name}` | {'yes' if value else 'no'} |")
    lines.extend([
        "",
        f"- Criteria currently satisfied: **{satisfied}**",
        f"- Additional count criteria needed for the old `plausible` threshold: **{max(0, 2 - satisfied)}**",
        f"- Genuine release-quality blockers still open: **{', '.join(release_quality_blockers) or 'none'}**",
        "",
        "Meeting two count criteria is not enough to claim high-confidence release quality. External blinded evidence, operational holdout execution, and independent/current-contract Goodhart validation remain decisive.",
        "",
        "## Priority order",
        "",
    ])
    for row in prioritized_actions:
        lines.extend([
            f"### Priority {row['priority']} - {row['gap']}",
            "",
            f"- Why still open: {row['why_open']}",
            f"- Next action: {row['next_action']}",
            f"- Expected payoff: {row['expected_payoff']}",
        ])
        candidates = row.get("concrete_candidates") or []
        if candidates:
            lines.append("- Top concrete candidates:")
            for cand in candidates:
                lines.append(
                    f"  - `{cand['bundle']}`: {cand['source_model']} -> {cand['target_model']} on `{cand['task']}` "
                    f"with prompt-holdout {cand['claims_passing_all_holdouts']}/{cand['accepted_claims_with_multi_prompt']}"
                )
        lines.append("")
    lines.append(payload["warning"])
    write_text(OUT_MD, "\n".join(lines).rstrip() + "\n")
    print(str(OUT_JSON))


if __name__ == "__main__":
    main()
