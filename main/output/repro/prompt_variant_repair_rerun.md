# Prompt Variant Repair Reruns

These reruns test whether affected accepted claims survive real task-supported prompt variants. They repair the canonical release only after the canonical bundle-discovery layer promotes the candidate bundles; legacy unsupported-prompt artifacts remain historical evidence of the repaired failure mode.

- Planned unsupported-prompt bundles: **21**
- Planned affected bundles with accepted claims: **11**
- Bundles rerun: **21**
- Accepted claims covered before rerun: **25**
- Accepted claims after rerun: **20**
- Previously accepted retained: **19**
- Previously accepted demoted: **6**
- Newly promoted claims: **1**
- Retention rate in rerun bundles: **76.0%**

| Bundle | Task | Model | Variants old -> new | Accepted before | Retained | Demoted | Candidate bundle |
|---|---|---|---|---:|---:|---:|---|
| `arithmetic_v0_gpt2-small` | `arithmetic_v0` | `gpt2-small` | `base, paraphrase` -> `base, worded` | 3 | 3 | 0 | `main/output/prompt_variant_repair/arithmetic_v0_gpt2-small` |
| `arithmetic_v0_pythia-70m` | `arithmetic_v0` | `pythia-70m` | `base, paraphrase` -> `base, worded` | 0 | 0 | 0 | `main/output/prompt_variant_repair/arithmetic_v0_pythia-70m` |
| `country_capital_v0_gpt2-small_lane_a` | `country_capital_v0` | `gpt2-small` | `base, varied, paraphrase` -> `base, paraphrase, fill_blank` | 3 | 3 | 0 | `main/output/prompt_variant_repair/country_capital_v0_gpt2-small_lane_a` |
| `country_capital_v0_gpt2-small_lane_b` | `country_capital_v0` | `gpt2-small` | `base, varied, paraphrase` -> `base, paraphrase, fill_blank` | 2 | 1 | 1 | `main/output/prompt_variant_repair/country_capital_v0_gpt2-small_lane_b` |
| `country_capital_v0_gpt2-small_lane_c` | `country_capital_v0` | `gpt2-small` | `base, varied, paraphrase` -> `base, paraphrase, fill_blank` | 3 | 3 | 0 | `main/output/prompt_variant_repair/country_capital_v0_gpt2-small_lane_c` |
| `country_capital_v0_pythia-70m_lane_a` | `country_capital_v0` | `pythia-70m` | `base, varied, paraphrase` -> `base, paraphrase, fill_blank` | 2 | 2 | 0 | `main/output/prompt_variant_repair/country_capital_v0_pythia-70m_lane_a` |
| `country_capital_v0_pythia-70m_lane_b` | `country_capital_v0` | `pythia-70m` | `base, varied, paraphrase` -> `base, paraphrase, fill_blank` | 0 | 0 | 0 | `main/output/prompt_variant_repair/country_capital_v0_pythia-70m_lane_b` |
| `country_capital_v0_pythia-70m_lane_c` | `country_capital_v0` | `pythia-70m` | `base, varied, paraphrase` -> `base, paraphrase, fill_blank` | 2 | 2 | 0 | `main/output/prompt_variant_repair/country_capital_v0_pythia-70m_lane_c` |
| `docstring_v0_gpt2-small` | `docstring_v0` | `gpt2-small` | `base, paraphrase` -> `base, detailed` | 0 | 0 | 0 | `main/output/prompt_variant_repair/docstring_v0_gpt2-small` |
| `fact_recall_v0_gpt2-small_lane_b3` | `fact_recall_v0` | `gpt2-small` | `base, varied, paraphrase` -> `base, paraphrase, contextual` | 0 | 0 | 0 | `main/output/prompt_variant_repair/fact_recall_v0_gpt2-small_lane_b3` |
| `ioi_v0_gpt2-small` | `ioi_v0` | `gpt2-small` | `base, varied, paraphrase` -> `base, paraphrase, structural` | 2 | 1 | 1 | `main/output/prompt_variant_repair/ioi_v0_gpt2-small` |
| `ioi_v0_gpt2-small_lane_a` | `ioi_v0` | `gpt2-small` | `base, varied, paraphrase` -> `base, paraphrase, structural` | 2 | 1 | 1 | `main/output/prompt_variant_repair/ioi_v0_gpt2-small_lane_a` |
| `ioi_v0_gpt2-small_lane_b` | `ioi_v0` | `gpt2-small` | `base, varied, paraphrase` -> `base, paraphrase, structural` | 1 | 0 | 1 | `main/output/prompt_variant_repair/ioi_v0_gpt2-small_lane_b` |
| `ioi_v0_gpt2-small_lane_b3` | `ioi_v0` | `gpt2-small` | `base, varied, paraphrase` -> `base, paraphrase, structural` | 0 | 0 | 0 | `main/output/prompt_variant_repair/ioi_v0_gpt2-small_lane_b3` |
| `ioi_v0_gpt2-small_lane_c` | `ioi_v0` | `gpt2-small` | `base, varied, paraphrase` -> `base, paraphrase, structural` | 2 | 1 | 1 | `main/output/prompt_variant_repair/ioi_v0_gpt2-small_lane_c` |
| `sentiment_v0_gpt2-small_lane_a` | `sentiment_v0` | `gpt2-small` | `base, varied, paraphrase` -> `base, review, statement` | 0 | 0 | 0 | `main/output/prompt_variant_repair/sentiment_v0_gpt2-small_lane_a` |
| `sentiment_v0_gpt2-small_lane_b` | `sentiment_v0` | `gpt2-small` | `base, varied, paraphrase` -> `base, review, statement` | 0 | 0 | 0 | `main/output/prompt_variant_repair/sentiment_v0_gpt2-small_lane_b` |
| `sentiment_v0_gpt2-small_lane_c` | `sentiment_v0` | `gpt2-small` | `base, varied, paraphrase` -> `base, review, statement` | 3 | 2 | 1 | `main/output/prompt_variant_repair/sentiment_v0_gpt2-small_lane_c` |
| `sentiment_v0_pythia-70m_lane_a` | `sentiment_v0` | `pythia-70m` | `base, varied, paraphrase` -> `base, review, statement` | 0 | 0 | 0 | `main/output/prompt_variant_repair/sentiment_v0_pythia-70m_lane_a` |
| `sentiment_v0_pythia-70m_lane_b` | `sentiment_v0` | `pythia-70m` | `base, varied, paraphrase` -> `base, review, statement` | 0 | 0 | 0 | `main/output/prompt_variant_repair/sentiment_v0_pythia-70m_lane_b` |
| `sentiment_v0_pythia-70m_lane_c` | `sentiment_v0` | `pythia-70m` | `base, varied, paraphrase` -> `base, review, statement` | 0 | 0 | 0 | `main/output/prompt_variant_repair/sentiment_v0_pythia-70m_lane_c` |
