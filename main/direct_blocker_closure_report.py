#!/usr/bin/env python3
"""Summarize which late-stage blockers are now closed and which remain open."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REPRO = ROOT / 'main' / 'output' / 'repro'
HOLDOUT = ROOT / 'holdout' / 'results_summary.json'
OUT_JSON = REPRO / 'direct_blocker_closure_report.json'
OUT_MD = REPRO / 'direct_blocker_closure_report.md'

def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}

def main() -> None:
    transfer = _load(REPRO / 'transfer_results_summary.json')
    spot = _load(REPRO / 'release_readiness_report.json')
    hard = _load(REPRO / 'contract_hardening_v1_summary.json')
    fresh = _load(REPRO / 'stress_test_agnostic_fresh_release_grade.json')
    docstring_repair = _load(REPRO / 'docstring_distributed_repair.json')
    docstring_explorer = _load(REPRO / 'docstring_method_sensitivity_explorer.json')
    transfer_queue = _load(REPRO / 'transfer_breadth_candidate_table.json')
    migration = _load(REPRO / 'contract_hardening_v1_migration_decision.json')
    runtime = _load(REPRO / 'runtime_cost_report.json')
    prompt_variant_audit = _load(REPRO / 'prompt_variant_validity_audit.json')
    prompt_variant_repair = _load(REPRO / 'prompt_variant_repair_rerun.json')
    high_power_prompt_holdout = _load(REPRO / 'prompt_holdout_high_power_n40_rerun.json')
    holdout = _load(HOLDOUT)
    field = _load(REPRO / 'field_level_findings.json')
    breadth = _load(REPRO / 'benchmark_breadth_summary.json')
    zero_real = _load(REPRO / 'zero_task_real_repair.json')
    zero_task = _load(REPRO / 'zero_task_gate_breakdown.json')
    breadth_gap = _load(REPRO / 'breadth_gap_analysis.json')

    released_criteria = (spot.get('release_quality_criteria') or {}) if isinstance(spot, dict) else {}
    hard_criteria = hard.get('criteria_closed_under_v1') or {}
    hard_replicates = hard.get('fresh_agnostic_hardened_v1_replicates') or {}
    accepted_by_task = field.get('acceptance_by_task') or {}
    tasks_total = len(accepted_by_task)
    tasks_with_accepted = sum(1 for row in accepted_by_task.values() if int(row.get('accepted', 0)) > 0)
    zero_real_agg = zero_real.get('aggregate') or {}
    remaining_zero_tasks = list(zero_task.get('zero_task_set') or [])
    method_forensics = zero_task.get('method_sensitivity_forensics') or {}
    fresh_full = (fresh.get('conditions') or {}).get('full_contract') or {}
    docstring_agg = docstring_repair.get('aggregate') or {}
    docstring_explorer_summary = docstring_explorer.get('summary') or {}
    transfer_queue_summary = transfer_queue.get('summary') or {}
    top_transfer_candidate = (
        transfer_queue_summary.get('top_priority')
        or ((transfer_queue.get('top_candidates') or [{}])[0] if transfer_queue.get('top_candidates') else {})
        or {}
    )
    same_family_preflight = _load(REPRO / 'same_family_transfer_preflight.json')
    migration_criteria = migration.get('criteria') or {}
    runtime_sources = runtime.get('measurement_sources') or {}
    prompt_variant_affected_accepts = int(prompt_variant_audit.get('affected_accepted_claims_in_existing_artifacts') or 0)
    prompt_variant_canonical_affected_accepts = int(prompt_variant_audit.get('canonical_affected_accepted_claims') or 0)
    prompt_variant_canonical_unsupported_files = int(prompt_variant_audit.get('canonical_files_with_unsupported_prompt_variants') or 0)
    prompt_variant_planned = int(
        prompt_variant_repair.get('planned_unsupported_prompt_bundles')
        or prompt_variant_repair.get('planned_affected_bundles_with_accepts')
        or 0
    )
    prompt_variant_rerun = int(prompt_variant_repair.get('bundles_rerun') or 0)
    prompt_variant_demoted = int(prompt_variant_repair.get('previously_accepted_demoted') or 0)
    prompt_variant_retained = int(prompt_variant_repair.get('previously_accepted_retained') or 0)
    prompt_variant_covered = int(prompt_variant_repair.get('accepted_before_in_rerun_bundles') or 0)
    prompt_variant_repair_incomplete = (
        (prompt_variant_affected_accepts > 0 or prompt_variant_canonical_affected_accepts > 0)
        and (
            prompt_variant_rerun < prompt_variant_planned
            or prompt_variant_covered < prompt_variant_affected_accepts
            or prompt_variant_canonical_affected_accepts > 0
        )
    )
    high_power_examples = int(high_power_prompt_holdout.get('examples_per_cell') or 0)
    high_power_planned = int(high_power_prompt_holdout.get('planned_bundles') or 0)
    high_power_rerun = int(high_power_prompt_holdout.get('bundles_rerun') or 0)
    high_power_covered = int(high_power_prompt_holdout.get('original_accepted_claims_covered') or 0)
    high_power_retained = int(high_power_prompt_holdout.get('original_accepted_claims_retained') or 0)
    high_power_demoted = int(high_power_prompt_holdout.get('original_accepted_claims_demoted') or 0)
    high_power_holdout_pass = int(
        high_power_prompt_holdout.get('retained_original_accepted_claims_passing_all_holdouts') or 0
    )
    high_power_holdout_fail = int(
        high_power_prompt_holdout.get('retained_original_accepted_claims_failing_any_holdout') or 0
    )
    high_power_prompt_holdout_incomplete = bool(
        high_power_planned
        and high_power_rerun >= high_power_planned
        and (high_power_demoted > 0 or high_power_holdout_fail > 0)
    )

    task_model_zero_cells = int(breadth_gap.get('n_zero_acceptance_cells') or 0)
    task_model_total_cells = int(breadth_gap.get('n_cells') or 0)
    bundle_count = int(breadth.get('bundle_count') or 0)
    external_blinded_missing = int(((holdout.get('external_blinded') or {}).get('n_submissions') or 0)) == 0
    operational_holdout_missing = int(((holdout.get('external_blinded') or {}).get('n_evaluated') or 0)) == 0
    independent_agnostic_missing = not bool(migration_criteria.get('independent_evidence'))

    payload = {
        'schema_version': 2,
        'released_contract': {
            'cross_model_confirmed_claims': transfer.get('transfer_confirmed_claims', 0),
            'second_cross_model_confirmed_claim': bool(released_criteria.get('second_cross_model_confirmed_claim')),
            'tasks_with_accepted': tasks_with_accepted,
            'tasks_total': tasks_total,
            'accepted_claims_in_at_least_5_of_8_tasks': bool(released_criteria.get('accepted_claims_in_at_least_5_of_8_tasks')),
            'zero_task_real_repair_accepted_claims': int(zero_real_agg.get('accepted_after_real_total') or 0),
            'zero_task_real_repair_tasks_with_accepts': list(zero_real_agg.get('tasks_with_any_real_accept_after') or []),
            'remaining_zero_tasks': remaining_zero_tasks,
            'agnostic_far_upper_below_5pct': bool(released_criteria.get('agnostic_far_upper_bound_below_5pct')),
            'fresh_agnostic_release_grade_far': fresh_full.get('false_accept_rate'),
            'fresh_agnostic_release_grade_ci95': fresh_full.get('false_accept_rate_ci95'),
        },
        'contract_hardening_v1': {
            'accepted_claims_before_total': hard.get('accepted_claims_before_total', 0),
            'accepted_claims_after_total': hard.get('accepted_claims_after_total', 0),
            'accepted_claim_retention_rate': hard.get('accepted_claim_retention_rate', 0.0),
            'tasks_with_accepted_after_count': hard.get('tasks_with_accepted_after_count', 0),
            'tasks_with_accepted_after': hard.get('tasks_with_accepted_after', []),
            'cross_model_confirmed_after_total': hard.get('cross_model_confirmed_after_total', 0),
            'agnostic_far': ((hard.get('fresh_agnostic_hardened_v1') or {}).get('false_accept_rate')),
            'agnostic_far_ci95': ((hard.get('fresh_agnostic_hardened_v1') or {}).get('false_accept_rate_ci95')),
            'agnostic_replicate_namespace_count': hard_replicates.get('namespace_count', 0),
            'agnostic_worst_ci95_high': hard_replicates.get('worst_ci95_high'),
            'second_cross_model_confirmed_claim': bool(hard_criteria.get('second_cross_model_confirmed_claim')),
            'agnostic_far_upper_bound_below_5pct': bool(hard_criteria.get('agnostic_far_upper_bound_below_5pct')),
        },
        'still_open': {
            'docstring_task_still_zero_accepted': 'docstring_v0' in remaining_zero_tasks,
            'docstring_method_sensitivity_failed_claims': method_forensics.get('n_method_sensitivity_failed_claims'),
            'docstring_method_sensitivity_max_margin': method_forensics.get('max_margin_over_threshold'),
            'docstring_distributed_repair_accepted_claims': int(docstring_agg.get('accepted_after_real_total') or 0),
            'docstring_distributed_repair_gate_failures': docstring_agg.get('gate_failures_after_real') or {},
            'docstring_method_sensitivity_diagnosis_counts': docstring_explorer_summary.get('diagnosis_counts') or {},
            'transfer_non_country_candidate_claims': int(transfer_queue_summary.get('non_country_candidate_claims') or 0),
            'transfer_candidates_blocked_missing_local_snapshot': int(transfer_queue_summary.get('blocked_missing_local_model_snapshot') or 0),
            'transfer_top_candidate': top_transfer_candidate,
            'same_family_ready_to_run': int(same_family_preflight.get('ready_to_run_count') or 0),
            'same_family_missing_eligible_rows': int(same_family_preflight.get('missing_eligible_same_family_rows_count') or 0),
            'same_family_already_scored': int(same_family_preflight.get('already_scored_count') or 0),
            'same_family_blocked': int(same_family_preflight.get('blocked_count') or 0),
            'independent_agnostic_validation_missing': independent_agnostic_missing,
            'v1_migration_decision_status': migration.get('decision_status'),
            'runtime_measured_bundles': int(runtime.get('bundles_measured') or 0),
            'runtime_measurement_coverage': float(runtime.get('measurement_coverage') or 0.0),
            'runtime_measurement_sources': runtime_sources,
            'task_model_grid_uniformity_gap': task_model_zero_cells > 0,
            'task_model_zero_acceptance_cells': task_model_zero_cells,
            'task_model_total_cells': task_model_total_cells,
            'external_blinded_submission_missing': external_blinded_missing,
            'operational_holdout_execution_missing': operational_holdout_missing,
            'same_family_live_transfer_weights_missing': int(same_family_preflight.get('blocked_count') or 0) > 0,
            'prompt_variant_aliasing_affected_accepted_claims': prompt_variant_affected_accepts,
            'prompt_variant_canonical_affected_accepted_claims': prompt_variant_canonical_affected_accepts,
            'prompt_variant_canonical_unsupported_files': prompt_variant_canonical_unsupported_files,
            'prompt_variant_repair_bundles_rerun': prompt_variant_rerun,
            'prompt_variant_repair_planned_bundles': prompt_variant_planned,
            'prompt_variant_repair_accepted_claims_covered': prompt_variant_covered,
            'prompt_variant_repair_retained_claims': prompt_variant_retained,
            'prompt_variant_repair_demoted_claims': prompt_variant_demoted,
            'prompt_variant_repair_incomplete': prompt_variant_repair_incomplete,
            'high_power_prompt_holdout_examples_per_cell': high_power_examples,
            'high_power_prompt_holdout_bundles_rerun': high_power_rerun,
            'high_power_prompt_holdout_planned_bundles': high_power_planned,
            'high_power_prompt_holdout_original_claims_covered': high_power_covered,
            'high_power_prompt_holdout_original_claims_retained': high_power_retained,
            'high_power_prompt_holdout_original_claims_demoted': high_power_demoted,
            'high_power_prompt_holdout_retained_claims_passing_all': high_power_holdout_pass,
            'high_power_prompt_holdout_retained_claims_failing_any': high_power_holdout_fail,
            'high_power_prompt_holdout_incomplete': high_power_prompt_holdout_incomplete,
        },
        'open_blocker_names': [
            name
            for name, is_open in {
                'docstring_task_still_zero_accepted': 'docstring_v0' in remaining_zero_tasks,
                'released_contract_agnostic_far_upper_not_below_5pct': not bool(released_criteria.get('agnostic_far_upper_bound_below_5pct')),
                'independent_agnostic_validation_missing': independent_agnostic_missing,
                'task_model_grid_uniformity_gap': task_model_zero_cells > 0,
                'external_blinded_submission_missing': external_blinded_missing,
                'operational_holdout_execution_missing': operational_holdout_missing,
                'broader_transfer_breadth_missing': int(transfer_queue_summary.get('non_country_candidate_claims') or 0) > 0,
                'runtime_measurement_coverage_incomplete': float(runtime.get('measurement_coverage') or 0.0) < 1.0,
                'prompt_variant_aliasing_repair_incomplete': prompt_variant_repair_incomplete,
                'high_power_prompt_holdout_frontier_incomplete': high_power_prompt_holdout_incomplete,
            }.items()
            if is_open
        ],
        'honest_bottom_line': 'Task-level breadth, docstring acceptance, and the basic cross-model count blocker are materially closed on current released artifacts, and same-family transfer is now operationally unblocked locally. A targeted n=100 docstring transfer rerun moves one accepted docstring claim over the frozen transfer floor, but the second accepted docstring claim remains below floor and the positive transfer set is still concentrated. The next top sentiment near-miss was preregistered and rerun at n=200; it stayed same-direction but below the frozen floor, so the current transfer tail is observed negative evidence rather than a missing local queue. Release-grade fresh agnostic stress is now at the floor under the released contract (0/200 false accepts, Wilson 95% CI [0.0%, 1.9%]) under the full statistical budget on the release_grade_2026q2 namespace; under a reduced rehearsal budget (128/128) on the rotated_2026q2 namespace the same generator family leaks 49/200 (24.5%, [19.1%, 30.9%]). The two cells differ on both budget AND seed namespace, so the spread is not a clean budget-only ablation; we publish both. The 0/200 is therefore a within-generator floor signal, not an external Goodhart-resistance proof. Contract-hardening V1 sharply reduces agnostic false accepts in two release-grade rotated diagnostics, but it is a migration tradeoff that demotes accepted claims (1/26 retained, 1/8 tasks with accepted) and reduces accepted-task breadth; the migration decision defers adoption because independent evidence is absent. Prompt-variant repair is closed for canonical unsupported-prompt aliasing, but the n=40 high-power prompt-holdout diagnostic shows remaining arithmetic, IOI, and sentiment fragility. External blinded evidence, operational holdout execution, independent Goodhart validation, broader transfer breadth, additional docstring transfer robustness, and task-model uniformity still require empirical inputs.',
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + '\n')

    ci = (payload['contract_hardening_v1'].get('agnostic_far_ci95') or {}).get('label', '[n/a]')
    retention = float(payload['contract_hardening_v1'].get('accepted_claim_retention_rate') or 0.0)
    worst = payload['contract_hardening_v1'].get('agnostic_worst_ci95_high')
    worst_label = f"{float(worst) * 100:.1f}%" if worst is not None else 'n/a'
    fresh_far = payload['released_contract'].get('fresh_agnostic_release_grade_far')
    fresh_ci = payload['released_contract'].get('fresh_agnostic_release_grade_ci95') or {}
    fresh_label = fresh_ci.get('label', '[n/a]') if isinstance(fresh_ci, dict) else '[n/a]'
    lines = [
        '# Direct Blocker Closure Report',
        '',
        '## Closed or materially closed',
        '',
        f"- Released-contract cross-model criterion: **{'closed' if payload['released_contract']['second_cross_model_confirmed_claim'] else 'open'}** ({payload['released_contract']['cross_model_confirmed_claims']} cross-model-confirmed claims now recorded).",
        f"- Task-level breadth criterion: **{'closed' if payload['released_contract']['accepted_claims_in_at_least_5_of_8_tasks'] else 'open'}** ({tasks_with_accepted}/{tasks_total} tasks with accepted claims; real zero-task repair contributes {payload['released_contract']['zero_task_real_repair_accepted_claims']} accepted claims).",
        f"- Contract-hardening-V1 agnostic criterion: **{'closed as a migration candidate' if payload['contract_hardening_v1']['agnostic_far_upper_bound_below_5pct'] else 'open'}** (primary FAR {(payload['contract_hardening_v1']['agnostic_far'] or 0)*100:.1f}%, 95% CI {ci}; {payload['contract_hardening_v1']['agnostic_replicate_namespace_count']} rotated namespaces; worst upper bound {worst_label}).",
        '',
        '## Important tradeoff',
        '',
        f"- V1 is **not** the released contract. On the current repaired release it keeps **{payload['contract_hardening_v1']['accepted_claims_after_total']}/{payload['contract_hardening_v1']['accepted_claims_before_total']}** accepted claims ({retention * 100:.1f}% retention) and accepted claims in **{payload['contract_hardening_v1']['tasks_with_accepted_after_count']}/{tasks_total}** tasks.",
        '- That tradeoff is scientifically useful because it quantifies the Goodhart-resistance versus breadth frontier, but it should not be presented as a free robustness fix.',
        '',
        '## Still genuinely open',
        '',
        f"- Residual breadth: remaining zero-accepted tasks are **{', '.join(remaining_zero_tasks) or 'none'}**, and task-model coverage is still uneven.",
        f"- Docstring forensics: **{payload['still_open']['docstring_method_sensitivity_failed_claims'] or 0}** residual zero-task claims fail `method_sensitivity`; maximum margin over threshold is **{(float(payload['still_open']['docstring_method_sensitivity_max_margin']) if payload['still_open']['docstring_method_sensitivity_max_margin'] is not None else 0.0):.3f}**. The old zero-task docstring blocker is closed; one accepted docstring claim now clears GPT-2 Medium transfer after the targeted n=100 rerun, while the other accepted docstring claim remains below the frozen transfer floor.",
        f"- Docstring method-sensitivity explorer: diagnosis counts are **{payload['still_open']['docstring_method_sensitivity_diagnosis_counts']}**. This remains useful for the zero-acceptance task-model cells, but no longer describes the whole docstring task as zero-accepted.",
        f"- Released-contract agnostic stress: still open; the release-grade fresh rotated stress has FAR **{(float(fresh_far) * 100 if fresh_far is not None else 0.0):.1f}%** with 95% CI **{fresh_label}**. V1 is a candidate migration, not the current released contract.",
        f"- V1 migration decision: **{payload['still_open']['v1_migration_decision_status'] or 'missing'}**; independent evidence criterion satisfied: **{not payload['still_open']['independent_agnostic_validation_missing']}**.",
        f"- Transfer breadth queue: **{payload['still_open']['transfer_non_country_candidate_claims']}** non-country candidates need new transfer evidence, with **{payload['still_open']['transfer_candidates_blocked_missing_local_snapshot']}** candidates blocked by missing local target-model snapshots.",
        f"- Top transfer tail case: `{(top_transfer_candidate or {}).get('bundle', 'missing')} / {(top_transfer_candidate or {}).get('hypothesis_id', 'missing')}` is **{(top_transfer_candidate or {}).get('current_transfer_status', 'missing')}** at **{float((top_transfer_candidate or {}).get('floor_fraction') or 0.0) * 100:.1f}%** of the floor after the latest scored row. This is the preregistered sentiment n=200 row, so it should be treated as persistent below-floor evidence, not a queued rerun.",
        f"- Docstring distributed-head repair: **{payload['still_open']['docstring_distributed_repair_accepted_claims']}** accepted claims; gate failures after real repair are **{payload['still_open']['docstring_distributed_repair_gate_failures']}**. This suggests docstring needs better necessity-aligned discovery, not threshold loosening.",
        f"- Task-model uniformity: **{payload['still_open']['task_model_zero_acceptance_cells']}/{payload['still_open']['task_model_total_cells']}** task-model cells still have zero accepted claims.",
        f"- Runtime coverage: **{payload['still_open']['runtime_measured_bundles']}/{bundle_count}** measured bundles ({payload['still_open']['runtime_measurement_coverage'] * 100:.1f}%); sources are **{payload['still_open']['runtime_measurement_sources']}**.",
        f"- Prompt-variant repair: legacy unsupported-prompt artifacts covered **{payload['still_open']['prompt_variant_repair_accepted_claims_covered']}** affected accepted claims, retaining **{payload['still_open']['prompt_variant_repair_retained_claims']}** and demoting **{payload['still_open']['prompt_variant_repair_demoted_claims']}**. Canonical unsupported-prompt accepted claims now affected: **{payload['still_open']['prompt_variant_canonical_affected_accepted_claims']}** across **{payload['still_open']['prompt_variant_canonical_unsupported_files']}** files.",
        f"- High-power prompt-holdout diagnostic: n=**{payload['still_open']['high_power_prompt_holdout_examples_per_cell']}** covers **{payload['still_open']['high_power_prompt_holdout_original_claims_covered']}** original accepted claims across **{payload['still_open']['high_power_prompt_holdout_bundles_rerun']}/{payload['still_open']['high_power_prompt_holdout_planned_bundles']}** accepted bundles; **{payload['still_open']['high_power_prompt_holdout_original_claims_retained']}** are retained, **{payload['still_open']['high_power_prompt_holdout_original_claims_demoted']}** demote, and **{payload['still_open']['high_power_prompt_holdout_retained_claims_passing_all']}/{payload['still_open']['high_power_prompt_holdout_original_claims_retained']}** retained claims pass all holdouts.",
        '- External blinded evidence: still zero genuine external submissions evaluated.',
        '- Operational holdout: still no real private-suite evaluation under an external custodian.',
        f"- Same-family live transfer: runtime and local target-model snapshots are ready for **{payload['still_open']['same_family_ready_to_run']}** queued bundle runs with **{payload['still_open']['same_family_missing_eligible_rows']}** missing prompt-holdout-passing rows, **{payload['still_open']['same_family_already_scored']}** candidate bundles already scored, and **{payload['still_open']['same_family_blocked']}** blocked. Remaining transfer breadth risk is now mostly scientific/evidentiary rather than weight-availability.",
        '',
        payload['honest_bottom_line'],
    ]
    OUT_MD.write_text('\n'.join(lines).rstrip() + '\n')
    print(str(OUT_JSON))

if __name__ == '__main__':
    main()
