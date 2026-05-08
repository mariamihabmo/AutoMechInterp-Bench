# Reproducibility Runbook

## Primary path

```bash
python main/reproducibility_audit.py
```

## Current audit contract

The current audit is a 43-command materialized audit of the released artifact
surface. It intentionally avoids live model intervention reruns. It is designed
to answer: "Can a reviewer regenerate the cached summaries, diagnostics,
prompt-repair transfer summaries, contract-hardening tradeoff outputs, blocker-execution queues,
independent-stress rehearsal and migration-decision artifacts, figures, docs,
holdout rehearsal outputs, repo-integrity sweep outputs, paper/README number
checks, and release-overclaim checks that the submission cites?"

The audit fails if any sub-command exits non-zero, if an expected output is
missing, or if an expected output is stale relative to the audit start time.
`main/repo_integrity_sweep.py` is part of the audit before the overclaim and
headline-number checks. `tools/check_headline_numbers.py` is the final command, and
`main/reproducibility_audit.py` sets `AUTOMECHINTERP_EXPECTED_AUDIT_COMMANDS`
so paper claims about the command count are checked against the live command
list during the same run. The preceding `tools/check_release_overclaims.py`
command fails if current-facing prose claims release readiness while
`release_readiness_report.json` still lists genuine blockers.

## What this regenerates

1. environment manifest
2. benchmark breadth summary
3. real zero-task repair summary
4. field-level findings and failure-family summaries
5. breadth-gap, zero-task, and legacy-split diagnostic reports
6. transfer summary, transfer near-miss analysis, and transfer failure breakdown
7. runtime/cost summary
8. community summary, figure inputs, and co-failure matrix
9. release-grade fresh evaluator-agnostic stress diagnostic over cached/released artifacts
10. prompt-variant validity/repair, prompt-holdout, same-family-transfer, and external-evidence preflights
11. holdout aggregate summary and rehearsal-mode holdout report
12. publication figures plus release takeaways under `papers/submissions/shared/figures/` and `main/output/repro/release_takeaways.json`
13. docstring distributed-repair diagnostic summary
14. transfer-breadth candidate queue and docstring method-sensitivity explorer
15. independent-stress rehearsal artifacts plus contract-hardening V1 migration-decision record
16. release readiness and direct blocker reports
17. generated docs under `site_docs/generated/` and `site_docs/assets/generated/`
18. release-overclaim check over current-facing prose
19. headline-number drift check over README and both NeurIPS paper sources

## Manual verification path

```bash
python -m pytest packages/evaluator/tests -q
python -m pytest packages/runner/tests -q
python main/zero_task_real_repair.py --summarize-existing
python main/summarize_benchmark_breadth.py
python main/field_level_findings.py
python main/breadth_gap_analysis.py
python main/transfer_results_summary.py
python main/transfer_near_miss_analysis.py
python main/runtime_cost_report.py --reruns 3
python main/community_value_summary.py
python main/figure_inputs.py
python main/co_failure_matrix.py
python main/generate_publication_figures.py
python main/prompt_holdout_transfer_control.py
python main/prompt_variant_validity_audit.py
python main/prompt_variant_repair_rerun.py --summarize-existing
python main/same_family_transfer_preflight.py
python main/transfer_breadth_candidate_table.py
python main/stress_test_agnostic.py --bundle-dir main/output/real_multi_task/ioi_v0_gpt2-small --count 200 --generator-regime fresh_v2 --seed-namespace release_grade_2026q2 --condition full_contract --json-out main/output/repro/stress_test_agnostic_fresh_release_grade.json --md-out main/output/repro/stress_test_agnostic_fresh_release_grade.md
python main/transfer_failure_breakdown.py
python main/zero_task_gate_breakdown.py
python main/docstring_method_sensitivity_explorer.py --source-dir main/output/real_multi_task
python main/docstring_distributed_repair.py --summarize-existing
python main/repair_legacy_no_split_bundles.py
python main/zero_task_confirmatory_repair.py
python main/external_evidence_preflight.py
python -m holdout.tools.build_results_summary
python main/run_holdout.py --rehearsal --release-version v0-rehearsal --use-cached-results
python main/contract_hardening_v1.py
python main/run_independent_agnostic_stress.py --rehearsal-from-cached --contract current --json-out main/output/repro/independent_agnostic_stress_current_rehearsal.json --md-out main/output/repro/independent_agnostic_stress_current_rehearsal.md
python main/run_independent_agnostic_stress.py --rehearsal-from-cached --contract contract_hardening_v1 --json-out main/output/repro/independent_agnostic_stress_hardened_v1_rehearsal.json --md-out main/output/repro/independent_agnostic_stress_hardened_v1_rehearsal.md
python main/contract_migration_decision.py --current main/output/repro/independent_agnostic_stress_current_rehearsal.json --candidate main/output/repro/independent_agnostic_stress_hardened_v1_rehearsal.json --retention main/output/repro/contract_hardening_v1_summary.json --out-md methodology/contract_hardening_v1_migration_decision.md --out-json main/output/repro/contract_hardening_v1_migration_decision.json --decision defer
python main/release_readiness_report.py
python main/direct_blocker_closure_report.py
python scripts/generate_docs_from_json.py
python tools/check_release_overclaims.py
python tools/check_headline_numbers.py
```

Submission-review and reviewer-kit commands remain important for community
workflow testing, but they are not part of the current materialized
reproducibility audit contract. Run them separately when evaluating a specific
submitted bundle.

## Caveats

1. Real reruns require local model access and appropriate hardware.
2. Public-facing artifacts should use repo-relative or redacted paths rather than leaking local machine paths.
3. Reviewer-kit reruns require either the installed package or a repo checkout available via `AUTOMECHINTERP_REPO_ROOT`.
4. Publication-figure regeneration requires `matplotlib` in the active environment.
5. PDF compilation is not guaranteed unless a LaTeX toolchain is installed.
6. Determinism is operational within fixed code, artifacts, and environment versions.
7. The fresh evaluator-agnostic stress diagnostic is release-grade for the benchmark-authored generator, but it is not independent adaptive-red-team evidence.
