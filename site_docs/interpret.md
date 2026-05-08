# Interpret Results

## Recommended reading order

1. `failed_checks`
2. `not_evaluated_checks`
3. `gate_outcomes`
4. `evidence_tier`

This avoids over-indexing on the final label before understanding the causal reason for it.

## Evidence tiers in practice

- `cross_model_confirmed`: strongest cross-model evidence pathway
- `single_model_confirmed`: accepted within one model context
- `causal_plus_robustness`: meaningful signal, but incomplete acceptance evidence
- `causal_tested_unstable`: causal evidence exists but instability remains
- `suggestive`: weak/incomplete support
- `rejected`: evidence did not satisfy the contract

## Failure decomposition workflow

For a bundle set:

1. Count failed gates across all claims.
2. Group failures by task/model/lane/provider.
3. Separate missing-evidence failures from contradiction failures.
4. Prioritize experiments that target the highest-concentration failure modes.

## Interpreting `not_evaluated`

`not_evaluated` often indicates missing slice or unavailable transfer evidence, not necessarily negative evidence.

Treat it as a data-completeness signal.

## Resubmission strategy

- Fix structural incompleteness first (slices, schema, manifest integrity).
- Then target robustness/method sensitivity failure clusters.
- Re-run deterministic review before resubmitting.
