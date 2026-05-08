# Transfer Breadth Candidate Table

diagnostic_queue_only_not_transfer_evidence

- Candidate claims needing new transfer evidence: **14**
- Non-country-capital candidate claims: **11**
- Already transfer-confirmed claims: **12**
- Candidates blocked by missing local target-model snapshot: **13**
- Missing eligible same-family rows among candidates: **0**

## Top candidates

| Rank | Bundle | Hypothesis | Task | Source | Same-family target | Status | Score | Why |
|---:|---|---|---|---|---|---|---:|---|
| 1 | `sentiment_v0_gpt2-small_lane_c` | `h_dla_sentiment_v0_001` | `sentiment_v0` | `gpt2-small` | `gpt2-medium` | `blocked_missing_local_model_snapshot` | 213 | non-country-capital task; passes all prompt-holdout checks; existing cross-model near miss; floor_fraction=0.700 |
| 2 | `docstring_v0_gpt2-small_lane_a` | `h_sweep_docstring_v0_002` | `docstring_v0` | `gpt2-small` | `gpt2-medium` | `blocked_missing_local_model_snapshot` | 207 | non-country-capital task; passes all prompt-holdout checks; existing cross-model near miss; floor_fraction=0.356 |
| 3 | `fact_recall_v0_pythia-70m` | `h_fact_recall_v0_001` | `fact_recall_v0` | `pythia-70m` | `pythia-160m` | `already_scored` | 196 | non-country-capital task; passes all prompt-holdout checks; existing cross-model near miss; floor_fraction=0.324 |
| 4 | `arithmetic_v0_gpt2-small` | `h_arithmetic_v0_003` | `arithmetic_v0` | `gpt2-small` | `gpt2-medium` | `blocked_missing_local_model_snapshot` | 160 | non-country-capital task; existing cross-model near miss; floor_fraction=0.001; scientifically queued; blocked only by local target-model snapshot |
| 5 | `arithmetic_v0_gpt2-small` | `h_arithmetic_v0_001` | `arithmetic_v0` | `gpt2-small` | `gpt2-medium` | `blocked_missing_local_model_snapshot` | 160 | non-country-capital task; existing cross-model near miss; floor_fraction=0.003; scientifically queued; blocked only by local target-model snapshot |
| 6 | `greater_than_v0_gpt2-small` | `h_greater_than_v0_003` | `greater_than_v0` | `gpt2-small` | `gpt2-medium` | `blocked_missing_local_model_snapshot` | 113 | non-country-capital task; passes all prompt-holdout checks; existing transfer direction problem; floor_fraction=0.184 |
| 7 | `fact_recall_v0_gpt2-small` | `h_fact_recall_v0_003` | `fact_recall_v0` | `gpt2-small` | `gpt2-medium` | `blocked_missing_local_model_snapshot` | 111 | non-country-capital task; passes all prompt-holdout checks; existing transfer direction problem; floor_fraction=0.080 |
| 8 | `gendered_pronoun_v0_gpt2-small` | `h_gendered_pronoun_v0_002` | `gendered_pronoun_v0` | `gpt2-small` | `gpt2-medium` | `blocked_missing_local_model_snapshot` | 110 | non-country-capital task; passes all prompt-holdout checks; existing transfer direction problem; floor_fraction=0.035 |
| 9 | `ioi_v0_gpt2-small_lane_c` | `h_dla_ioi_v0_002` | `ioi_v0` | `gpt2-small` | `gpt2-medium` | `blocked_missing_local_model_snapshot` | 110 | non-country-capital task; existing transfer direction problem; floor_fraction=6.882; scientifically queued; blocked only by local target-model snapshot |
| 10 | `ioi_v0_gpt2-small_lane_a` | `h_sweep_ioi_v0_001` | `ioi_v0` | `gpt2-small` | `gpt2-medium` | `blocked_missing_local_model_snapshot` | 110 | non-country-capital task; existing transfer direction problem; floor_fraction=6.882; scientifically queued; blocked only by local target-model snapshot |
| 11 | `ioi_v0_gpt2-small` | `h_ioi_v0_001` | `ioi_v0` | `gpt2-small` | `gpt2-medium` | `blocked_missing_local_model_snapshot` | 110 | non-country-capital task; existing transfer direction problem; floor_fraction=6.882; scientifically queued; blocked only by local target-model snapshot |
| 12 | `country_capital_v0_gpt2-small_lane_c` | `h_dla_country_capital_v0_003` | `country_capital_v0` | `gpt2-small` | `gpt2-medium` | `blocked_missing_local_model_snapshot` | 85 | country-capital already dominates current transfer positives; passes all prompt-holdout checks; existing cross-model near miss; floor_fraction=0.507 |

## Concrete next commands

### `sentiment_v0_gpt2-small_lane_c` / `h_dla_sentiment_v0_001`

- Current blocker: no_loadable_local_snapshot_for_gpt2-medium; huggingface_dns_resolves=True
- Command after blocker is resolved: `python main/run_transfer_release.py --bundle-dir main/output/prompt_variant_repair/sentiment_v0_gpt2-small_lane_c --transfer-model gpt2-medium --device cpu --local-only --local-model-dir <path-to-local-model-snapshot>`

### `docstring_v0_gpt2-small_lane_a` / `h_sweep_docstring_v0_002`

- Current blocker: no_loadable_local_snapshot_for_gpt2-medium; huggingface_dns_resolves=True
- Command after blocker is resolved: `python main/run_transfer_release.py --bundle-dir main/output/real_multilane/docstring_v0_gpt2-small_lane_a --transfer-model gpt2-medium --device cpu --local-only --local-model-dir <path-to-local-model-snapshot>`

### `fact_recall_v0_pythia-70m` / `h_fact_recall_v0_001`

- Current status: already_scored
- Optional variance-check rerun command: `python main/run_transfer_release.py --bundle-dir main/output/zero_task_real_repair/fact_recall_v0_pythia-70m --transfer-model pythia-160m --device cpu --local-only --local-model-dir ~/.cache/huggingface/hub/models--EleutherAI--pythia-160m/snapshots/50f5173d932e8e61f858120bcb800b97af589f46`

### `arithmetic_v0_gpt2-small` / `h_arithmetic_v0_003`

- Current blocker: no_loadable_local_snapshot_for_gpt2-medium; huggingface_dns_resolves=True
- Command after blocker is resolved: `python main/run_transfer_release.py --bundle-dir main/output/prompt_variant_repair/arithmetic_v0_gpt2-small --transfer-model gpt2-medium --device cpu --local-only --local-model-dir <path-to-local-model-snapshot>`

### `arithmetic_v0_gpt2-small` / `h_arithmetic_v0_001`

- Current blocker: no_loadable_local_snapshot_for_gpt2-medium; huggingface_dns_resolves=True
- Command after blocker is resolved: `python main/run_transfer_release.py --bundle-dir main/output/prompt_variant_repair/arithmetic_v0_gpt2-small --transfer-model gpt2-medium --device cpu --local-only --local-model-dir <path-to-local-model-snapshot>`

### `greater_than_v0_gpt2-small` / `h_greater_than_v0_003`

- Current blocker: no_loadable_local_snapshot_for_gpt2-medium; huggingface_dns_resolves=True
- Command after blocker is resolved: `python main/run_transfer_release.py --bundle-dir main/output/zero_task_real_repair/greater_than_v0_gpt2-small --transfer-model gpt2-medium --device cpu --local-only --local-model-dir <path-to-local-model-snapshot>`

## Interpretation

- This artifact ranks next experiments; it is not new transfer evidence.
- Non-country-capital claims are prioritized because current confirmed transfer is country-capital-heavy.
- A ready_to_run_missing_rows status means the target snapshot and command are available locally and at least one prompt-holdout-passing accepted claim lacks a same-family row.
- An already_scored status means the relevant same-family row exists; the remaining blocker is the observed transfer failure/near-miss, not missing execution.
- A blocked_missing_local_model_snapshot status means the next action is to supply the target-model snapshot and run the proposed command, not to update paper claims.
- Existing near misses are useful but should not be rescued by lowering the transfer floor without a versioned protocol migration.
