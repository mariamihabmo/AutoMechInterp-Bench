# Stage-Gate Checks and Formulas

This document defines the objective checks used by `evaluator.py`.

## 1) Execution coverage
- Build expected execution grid from protocol:
  `seeds x prompt_variants x resample_ids x methods`
- Build observed grid from raw cells.
- Pass condition: no missing cells and no undeclared cells.

## 2) Causal effect gate
- Compute confirmatory treatment mean (fallback to all cells if confirmatory absent).
- Required floor:
  `max(stage.min_causal_effect, statistical.min_effect_floor, hypothesis.predicted_min_effect)`
- Pass if effect direction matches hypothesis and exceeds floor.

## 3) Negative-control gate
- Compute pooled mean absolute control effect.
- Compute specificity ratio:
  `abs(treatment_mean) / (control_abs_mean + epsilon)`
- Pass if:
  - `control_abs_mean <= control_policy.max_control_abs_mean`
  - `specificity_ratio >= max(stage.min_specificity_ratio, hypothesis.predicted_specificity_ratio)`

## 4) Robustness gate
Compute consistency by axis (`seed`, `prompt_variant`, `resample_id`):
- For each axis value, average treatment effect over remaining dimensions.
- Score = fraction of axis values passing direction + effect floor.
- Pass if each axis score >= configured minimum.

## 5) Method-sensitivity gate
- Group treatment effects by method.
- Compute method-level mean effect.
- Compute population std of method means.
- Pass if std <= `stage.max_method_sensitivity_std`.

## 6) Confirmatory CI gate
- Compute bootstrap confidence intervals on confirmatory treatment effects.
- Pass if CI excludes zero when `require_confirmatory_ci_excludes_zero=true`.
- Also requires confirmatory slice presence in that case.

## 7) Multiplicity gate
- Estimate per-claim p-value with a deterministic sign-flip permutation test.
- Apply Benjamini-Hochberg correction over claims.
- Pass if q-value <= `statistical_policy.fdr_q`.

## 8) Integrity gates
- `evaluation_result.protocol_sha256` must match SHA256 of `protocol.yaml`.
- `manifest.json` hashes must match all tracked files.

## 9) Provenance gates
- Every raw cell must include runner and provenance fields:
  - `runner_id`, `runner_version`, `pipeline_sha`
  - `model_ref`, `dataset_seed`, `prompt_template_id`
- Missing provenance fields are hard failures during schema loading.

## Final verdict
Claim passes only if all hard checks pass.
Evidence tiers:
- `cross_model_confirmed`: all core gates pass and cross-model transfer passes.
- `single_model_confirmed`: all core gates pass; transfer may remain not evaluated.
- `causal_plus_robustness`: all core gates pass but accepted-tier slice requirements are incomplete.
- `causal_tested_unstable`: causal/control/robustness signal exists but at least one core requirement still fails.
- `rejected`: otherwise.
