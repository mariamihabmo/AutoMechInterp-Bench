# Zero-Task Real Confirmatory Repair

Real Stage-2 repair reruns. In canonical aggregate reporting, same-named legacy zero-task bundles from main/output/real_multi_task are superseded by these reruns, so headline bundle and claim counts remain stable while repaired evidence is counted.

- Bundles run: **10**
- Accepted before: **0**
- Accepted after real repair: **7**
- Tasks with any real accepted claim after repair: **arithmetic_v0, fact_recall_v0, gendered_pronoun_v0, greater_than_v0**
- Runtime: **15.4 min**

| Bundle | Task | Model | Accepted before | Accepted after real | Accepted hypotheses | Candidate bundle |
|---|---|---|---:|---:|---|---|
| `arithmetic_v0_gpt2-small` | `arithmetic_v0` | `gpt2-small` | 0 | 3 | `h_arithmetic_v0_001`, `h_arithmetic_v0_002`, `h_arithmetic_v0_003` | `main/output/zero_task_real_repair/arithmetic_v0_gpt2-small` |
| `arithmetic_v0_pythia-70m` | `arithmetic_v0` | `pythia-70m` | 0 | 0 | none | `main/output/zero_task_real_repair/arithmetic_v0_pythia-70m` |
| `docstring_v0_gpt2-small` | `docstring_v0` | `gpt2-small` | 0 | 0 | none | `main/output/zero_task_real_repair/docstring_v0_gpt2-small` |
| `docstring_v0_pythia-70m` | `docstring_v0` | `pythia-70m` | 0 | 0 | none | `main/output/zero_task_real_repair/docstring_v0_pythia-70m` |
| `fact_recall_v0_gpt2-small` | `fact_recall_v0` | `gpt2-small` | 0 | 1 | `h_fact_recall_v0_003` | `main/output/zero_task_real_repair/fact_recall_v0_gpt2-small` |
| `fact_recall_v0_pythia-70m` | `fact_recall_v0` | `pythia-70m` | 0 | 1 | `h_fact_recall_v0_001` | `main/output/zero_task_real_repair/fact_recall_v0_pythia-70m` |
| `gendered_pronoun_v0_gpt2-small` | `gendered_pronoun_v0` | `gpt2-small` | 0 | 1 | `h_gendered_pronoun_v0_002` | `main/output/zero_task_real_repair/gendered_pronoun_v0_gpt2-small` |
| `gendered_pronoun_v0_pythia-70m` | `gendered_pronoun_v0` | `pythia-70m` | 0 | 0 | none | `main/output/zero_task_real_repair/gendered_pronoun_v0_pythia-70m` |
| `greater_than_v0_gpt2-small` | `greater_than_v0` | `gpt2-small` | 0 | 1 | `h_greater_than_v0_003` | `main/output/zero_task_real_repair/greater_than_v0_gpt2-small` |
| `greater_than_v0_pythia-70m` | `greater_than_v0` | `pythia-70m` | 0 | 0 | none | `main/output/zero_task_real_repair/greater_than_v0_pythia-70m` |
