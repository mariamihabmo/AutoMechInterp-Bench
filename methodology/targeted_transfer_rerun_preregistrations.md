# Targeted Transfer Rerun Preregistrations

This file records targeted transfer reruns before execution so follow-up runs
cannot quietly become threshold shopping. A targeted rerun may update released
artifacts only if the command, candidate, decision rule, and claim-language
constraints are written here first.

## 2026-05-04 - Sentiment top near-miss n=200 variance check

**Candidate:** `sentiment_v0_gpt2-small_lane_c / h_dla_sentiment_v0_001`

**Why this candidate:** It is the top remaining row in
`main/output/repro/transfer_breadth_candidate_table.json`: non-country-capital
task, passes all prompt-holdout checks, already has a same-family GPT-2 Small
-> GPT-2 Medium transfer row, and sits closest to the frozen transfer floor
among remaining accepted near-misses (`floor_fraction=0.706` at n=100).

**Command:**

```bash
python main/run_transfer_release.py \
  --bundle-dir main/output/prompt_variant_repair/sentiment_v0_gpt2-small_lane_c \
  --transfer-model gpt2-medium \
  --device mps \
  --n-examples 200 \
  --local-only \
  --local-model-dir model_cache/gpt2-medium
```

**Frozen decision rule:** Use the existing released transfer rule only:
same-direction transfer effect and `cross_model_effect_floor = 0.02`. No floor,
mapping, task, or accepted-claim rule may be changed because of this run.

**Allowed claim update if pass:** transfer-confirmed accepted claims increase
from `12/25` to `13/25`, with an additional sentiment positive. The paper must
still say transfer is narrow and country-capital-heavy.

**Required claim update if fail:** keep the `12/25` headline and report that
the top remaining sentiment near-miss stayed below floor after an n=200
variance-check rerun.

**Not allowed:** claiming broad cross-model generalization, claiming Goodhart
robustness improved, or treating a targeted rerun as independent evidence.

**Result recorded 2026-05-04:** The rerun completed and did not clear the
floor. `h_dla_sentiment_v0_001` remains same-direction but below floor:
`transfer_effect = 0.013992223739624023`, `n_examples = 200`,
`transfer_contract_pass = false`. The allowed update is therefore the negative
one: keep the `12/25` transfer-confirmed headline and report that the top
remaining sentiment near-miss stayed below floor after a preregistered n=200
variance-check rerun.

## 2026-05-04 - Fact-recall GPT-2 Small new accepted claim transfer test

**Candidate:** `fact_recall_v0_gpt2-small / h_fact_recall_v0_003`

**Why this candidate:** The preregistered n=48 zero-cell repair for
`fact_recall_v0 x gpt2-small` produced a new accepted claim. Regenerated
`transfer_breadth_candidate_table.json` marks it as locally runnable with
missing same-family transfer rows and all available prompt-holdout checks
passing. Running the transfer test prevents the new accepted claim from
inflating breadth while remaining an avoidably untested transfer case.

**Command:**

```bash
python main/run_transfer_release.py \
  --bundle-dir main/output/zero_task_real_repair/fact_recall_v0_gpt2-small \
  --transfer-model gpt2-medium \
  --device mps \
  --n-examples 100 \
  --local-only \
  --local-model-dir model_cache/gpt2-medium
```

**Frozen decision rule:** Use the existing released transfer rule only:
same-direction transfer effect and `cross_model_effect_floor = 0.02`. No floor,
component mapping, task, accepted-claim, or evidence-tier rule may be changed
because of this run.

**Allowed claim update if pass:** transfer-confirmed accepted claims increase
from `12/26` transfer-tested accepted claims to `13/26`, with one additional
fact-recall same-family GPT-2 Small -> GPT-2 Medium positive. The paper must
still say transfer is narrow and maintainer-authored.

**Required claim update if fail:** keep the `12/26` transfer-confirmed headline
after this row is added to the transfer-tested set, and report the new
fact-recall GPT-2 Small accepted claim as single-model-only under the current
transfer rule.

**Not allowed:** treating this as external evidence, changing the transfer
threshold after seeing the result, or using a pass to claim broad cross-model
generalization.

**Result recorded 2026-05-04:** The transfer test completed and did not clear
the optional gate. `h_fact_recall_v0_003` remains accepted as
`single_model_confirmed`, but its GPT-2 Small -> GPT-2 Medium transfer effect
is opposite-direction and below floor: `transfer_effect =
-0.0015985202789306641`, `n_examples = 100`,
`transfer_contract_pass = false`. The allowed update is therefore the negative
one: after regenerated summaries, the transfer-tested accepted-claim headline
should become `12/26`, with the new fact-recall GPT-2 Small claim explicitly
described as single-model-only under the current transfer rule.
