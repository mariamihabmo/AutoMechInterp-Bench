# Wide Test Sweep

- Sweep style: grouped per-file clusters plus a separate `test_stress_agnostic.py` run.
- Why grouped: a monolithic `pytest packages/evaluator` invocation intermittently hung near suite shutdown in this container even after the underlying test regression was fixed; grouped runs gave stable pass/fail evidence.
- All grouped commands passed: **True**

| Sweep command | Return code | Notes |
|---|---:|---|
| `python -m pytest -q packages/evaluator/tests/test_bundle_analysis_cached_results.py packages/evaluator/tests/test_bundle_analysis_consistency.py packages/evaluator/tests/test_bundle_analysis_failure_mode.py packages/evaluator/tests/test_causal_and_robustness_gates.py packages/evaluator/tests/test_cli_report_generation.py packages/evaluator/tests/test_co_failure_matrix.py packages/evaluator/tests/test_diagnostic_scripts.py` | 0 | Grouped evaluator sweep, file cluster 1/4. |
| `python -m pytest -q packages/evaluator/tests/test_duplicate_claim_protection.py packages/evaluator/tests/test_duplicate_claims_rejected.py packages/evaluator/tests/test_evidence_tier_classifier.py packages/evaluator/tests/test_execution_grid_and_controls.py packages/evaluator/tests/test_forensic_analyzers.py packages/evaluator/tests/test_full_valid_bundle_passes.py packages/evaluator/tests/test_generate_agent_output.py` | 0 | Grouped evaluator sweep, file cluster 2/4. |
| `python -m pytest -q packages/evaluator/tests/test_generate_hypotheses.py packages/evaluator/tests/test_holdout_author_tools.py packages/evaluator/tests/test_holdout_scaffolding.py packages/evaluator/tests/test_loader.py packages/evaluator/tests/test_norm_ppf_parity.py packages/evaluator/tests/test_protocol_and_hypothesis_constraints.py packages/evaluator/tests/test_protocol_critic.py` | 0 | Grouped evaluator sweep, file cluster 3/4. |
| `python -m pytest -q packages/evaluator/tests/test_protocol_hash_and_manifest.py packages/evaluator/tests/test_reporting.py packages/evaluator/tests/test_reproducibility_audit_helpers.py packages/evaluator/tests/test_sensitivity_ci_and_multiplicity.py packages/evaluator/tests/test_submission_review_and_vectors.py packages/evaluator/tests/test_zero_task_repair_schema.py` | 0 | Grouped evaluator sweep, file cluster 4/4 excluding the slower stress file. |
| `python -m pytest -q packages/evaluator/tests/test_stress_agnostic.py` | 0 | Run separately because the full-suite invocation in this environment occasionally hangs after this file despite per-file success. |
| `pytest packages/runner -q` | 0 | Broad runner-package sweep. |
