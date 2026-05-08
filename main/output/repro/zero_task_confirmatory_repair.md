# Zero-Task Confirmatory Repair (Mock Rehearsal)

Engineering rehearsal only. Mock-mode accepted counts do NOT change released headline numbers and must not be cited as scientific evidence.

- Bundles rebuilt in mock mode: **10**
- confirmatory_present failures before: **0**
- confirmatory_present failures after mock repair: **0**
- confirmatory_ci failures before: **23**
- confirmatory_ci failures after mock repair: **0**
- Tasks with any mock accepted claims after repair: **arithmetic_v0, docstring_v0, fact_recall_v0, gendered_pronoun_v0, greater_than_v0**

## Per-bundle summary

| Bundle | Task | Model | Accepted before | Accepted after (mock) | confirmatory_present before | confirmatory_present after (mock) |
|---|---|---|---:|---:|---:|---:|
| `arithmetic_v0_gpt2-small` | `arithmetic_v0` | `gpt2-small` | 0 | 3 | 0 | 0 |
| `arithmetic_v0_pythia-70m` | `arithmetic_v0` | `pythia-70m` | 0 | 3 | 0 | 0 |
| `docstring_v0_gpt2-small` | `docstring_v0` | `gpt2-small` | 0 | 3 | 0 | 0 |
| `docstring_v0_pythia-70m` | `docstring_v0` | `pythia-70m` | 0 | 3 | 0 | 0 |
| `fact_recall_v0_gpt2-small` | `fact_recall_v0` | `gpt2-small` | 0 | 3 | 0 | 0 |
| `fact_recall_v0_pythia-70m` | `fact_recall_v0` | `pythia-70m` | 0 | 3 | 0 | 0 |
| `gendered_pronoun_v0_gpt2-small` | `gendered_pronoun_v0` | `gpt2-small` | 0 | 3 | 0 | 0 |
| `gendered_pronoun_v0_pythia-70m` | `gendered_pronoun_v0` | `pythia-70m` | 0 | 2 | 0 | 0 |
| `greater_than_v0_gpt2-small` | `greater_than_v0` | `gpt2-small` | 0 | 2 | 0 | 0 |
| `greater_than_v0_pythia-70m` | `greater_than_v0` | `pythia-70m` | 0 | 2 | 0 | 0 |

## Interpretation

If confirmatory-stage failures disappear in these repaired mock bundles, the remaining breadth problem is no longer a pure plumbing issue. That means the next honest step is real-model discovery / Stage-2 execution, not more evaluator surgery.
