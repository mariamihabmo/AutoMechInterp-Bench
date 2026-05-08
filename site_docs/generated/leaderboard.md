# Leaderboard

Bundle-level verification outcomes from the released evaluated bundle set.

- Bundles: **36**
- Claims: **109**
- Accepted: **26**
- Rejected: **83**
- Acceptance rate: **23.85%**

## Bundle results

| Bundle | Task | Model | Claims | Accepted | Acceptance | Determinism |
|---|---|---|---|---|---|---|
| arithmetic_v0_gpt2-small | arithmetic_v0 | gpt2-small | 3 | 3 | 100.00% | match |
| country_capital_v0_gpt2-small_lane_a | country_capital_v0 | gpt2-small | 3 | 3 | 100.00% | match |
| country_capital_v0_gpt2-small_lane_c | country_capital_v0 | gpt2-small | 3 | 3 | 100.00% | match |
| country_capital_v0_pythia-70m_lane_a | country_capital_v0 | pythia-70m | 3 | 2 | 66.67% | match |
| country_capital_v0_pythia-70m_lane_c | country_capital_v0 | pythia-70m | 3 | 2 | 66.67% | match |
| sentiment_v0_gpt2-small_lane_c | sentiment_v0 | gpt2-small | 3 | 2 | 66.67% | match |
| arithmetic_v0_pythia-70m | arithmetic_v0 | pythia-70m | 3 | 1 | 33.33% | match |
| country_capital_v0_gpt2-small_lane_b | country_capital_v0 | gpt2-small | 3 | 1 | 33.33% | match |
| docstring_v0_gpt2-small_lane_a | docstring_v0 | gpt2-small | 3 | 1 | 33.33% | match |
| docstring_v0_gpt2-small_lane_c | docstring_v0 | gpt2-small | 3 | 1 | 33.33% | match |
| fact_recall_v0_gpt2-small | fact_recall_v0 | gpt2-small | 3 | 1 | 33.33% | match |
| fact_recall_v0_pythia-70m | fact_recall_v0 | pythia-70m | 3 | 1 | 33.33% | match |
| gendered_pronoun_v0_gpt2-small | gendered_pronoun_v0 | gpt2-small | 3 | 1 | 33.33% | match |
| greater_than_v0_gpt2-small | greater_than_v0 | gpt2-small | 3 | 1 | 33.33% | match |
| ioi_v0_gpt2-small_lane_a | ioi_v0 | gpt2-small | 3 | 1 | 33.33% | match |
| ioi_v0_gpt2-small_lane_c | ioi_v0 | gpt2-small | 3 | 1 | 33.33% | match |
| ioi_v0_gpt2-small | ioi_v0 | gpt2-small | 4 | 1 | 25.00% | match |
| country_capital_v0_gpt2-small | country_capital_v0 | gpt2-small | 3 | 0 | 0.00% | match |
| country_capital_v0_pythia-70m | country_capital_v0 | pythia-70m | 3 | 0 | 0.00% | match |
| country_capital_v0_pythia-70m_lane_b | country_capital_v0 | pythia-70m | 3 | 0 | 0.00% | match |
| docstring_v0_gpt2-small | docstring_v0 | gpt2-small | 3 | 0 | 0.00% | match |
| docstring_v0_gpt2-small_lane_b | docstring_v0 | gpt2-small | 3 | 0 | 0.00% | match |
| docstring_v0_pythia-70m | docstring_v0 | pythia-70m | 3 | 0 | 0.00% | match |
| fact_recall_v0_gpt2-small_lane_b3 | fact_recall_v0 | gpt2-small | 3 | 0 | 0.00% | match |
| gendered_pronoun_v0_pythia-70m | gendered_pronoun_v0 | pythia-70m | 3 | 0 | 0.00% | match |
| greater_than_v0_pythia-70m | greater_than_v0 | pythia-70m | 3 | 0 | 0.00% | match |
| ioi_v0_gpt2-small_lane_b | ioi_v0 | gpt2-small | 3 | 0 | 0.00% | match |
| ioi_v0_gpt2-small_lane_b3 | ioi_v0 | gpt2-small | 3 | 0 | 0.00% | match |
| ioi_v0_pythia-70m | ioi_v0 | pythia-70m | 3 | 0 | 0.00% | match |
| sentiment_v0_gpt2-small | sentiment_v0 | gpt2-small | 3 | 0 | 0.00% | match |
| sentiment_v0_gpt2-small_lane_a | sentiment_v0 | gpt2-small | 3 | 0 | 0.00% | match |
| sentiment_v0_gpt2-small_lane_b | sentiment_v0 | gpt2-small | 3 | 0 | 0.00% | match |
| sentiment_v0_pythia-70m | sentiment_v0 | pythia-70m | 3 | 0 | 0.00% | match |
| sentiment_v0_pythia-70m_lane_a | sentiment_v0 | pythia-70m | 3 | 0 | 0.00% | match |
| sentiment_v0_pythia-70m_lane_b | sentiment_v0 | pythia-70m | 3 | 0 | 0.00% | match |
| sentiment_v0_pythia-70m_lane_c | sentiment_v0 | pythia-70m | 3 | 0 | 0.00% | match |

## Tier counts

| Tier | Count |
|---|---|
| rejected | 67 |
| single_model_confirmed | 14 |
| suggestive | 13 |
| cross_model_confirmed | 12 |
| causal_tested_unstable | 3 |

## Regenerate

```bash
python main/reproducibility_audit.py
```
