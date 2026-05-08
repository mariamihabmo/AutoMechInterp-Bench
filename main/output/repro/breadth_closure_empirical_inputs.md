# Breadth Closure Empirical Inputs

This report converts the remaining breadth blocker into an exact rerun queue.

- Current accepted-task breadth: **3 / 8**
- Additional accepted tasks needed for the repo's 5-of-8 criterion: **2**

## Priority queue

| Rank | Task | Model | Bundle | Hypothesis | Failed gates | Est. extra cells | Rerun type |
|---|---|---|---|---|---|---:|---|
| 1 | `arithmetic_v0` | `pythia-70m` | `arithmetic_v0_pythia-70m` | `h_arithmetic_v0_001` | `causal_effect`, `robustness`, `method_sensitivity`, `confirmatory_ci`, `multiplicity` | 80 | real_rerun_on_repaired_protocol |
| 2 | `docstring_v0` | `gpt2-small` | `docstring_v0_gpt2-small` | `h_docstring_v0_001` | `confirmatory_present`, `causal_effect`, `negative_controls`, `robustness`, `method_sensitivity`, `confirmatory_ci`, `multiplicity` | 38 | method_harmonization_then_confirmatory_rerun |
| 3 | `fact_recall_v0` | `gpt2-small` | `fact_recall_v0_gpt2-small` | `h_fact_recall_v0_001` | `causal_effect`, `robustness`, `method_sensitivity`, `confirmatory_ci`, `multiplicity` | 33 | method_harmonization_then_confirmatory_rerun |
| 4 | `fact_recall_v0` | `pythia-70m` | `fact_recall_v0_pythia-70m` | `h_fact_recall_v0_001` | `confirmatory_present`, `causal_effect`, `negative_controls`, `robustness`, `method_sensitivity`, `confirmatory_ci`, `multiplicity` | 428630 | method_harmonization_then_confirmatory_rerun |
| 5 | `gendered_pronoun_v0` | `gpt2-small` | `gendered_pronoun_v0_gpt2-small` | `h_gendered_pronoun_v0_002` | `causal_effect`, `robustness`, `method_sensitivity`, `confirmatory_ci`, `multiplicity` | 87 | method_harmonization_then_confirmatory_rerun |

## Notes

- These are not new accepted claims. They are the exact rerun targets with the cleanest evidence-based path to closing the breadth blocker.
- Multiplicity-only candidates suggest more confirmatory signal may be sufficient; method-sensitivity candidates need method-harmonized reruns, not just more cells.
- Mock-mode repair artifacts only remove plumbing uncertainty; they do not count as scientific evidence.
