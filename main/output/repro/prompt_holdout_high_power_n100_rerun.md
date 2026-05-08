# High-Power Prompt-Holdout Rerun

This prospective diagnostic covers every current canonical bundle with accepted claims and multiple prompt variants. It must be reported as a high-power robustness frontier, not as external validation or a silent contract migration.

- Completion status: **partial**
- Examples per cell: **100**
- Planned bundles: **17**
- Bundles rerun: **5**
- Original accepted claims covered: **7**
- Original accepted claims retained: **5**
- Original accepted claims demoted: **2**
- Retained original accepted claims passing all held-out prompts: **4/5**
- Passing held-out prompt checks on retained claims: **9/10**

## Bundle Summary

| Bundle | Task | Model | Accepted before | Retained | Demoted | Retained + all holdouts pass |
|---|---|---|---:|---:|---:|---:|
| `arithmetic_v0_gpt2-small` | `arithmetic_v0` | `gpt2-small` | 3 | 1 | 2 | 1 |
| `arithmetic_v0_pythia-70m` | `arithmetic_v0` | `pythia-70m` | 1 | 1 | 0 | 0 |
| `fact_recall_v0_gpt2-small` | `fact_recall_v0` | `gpt2-small` | 1 | 1 | 0 | 1 |
| `gendered_pronoun_v0_gpt2-small` | `gendered_pronoun_v0` | `gpt2-small` | 1 | 1 | 0 | 1 |
| `greater_than_v0_gpt2-small` | `greater_than_v0` | `gpt2-small` | 1 | 1 | 0 | 1 |

## Failing Or Demoted Original Claims

- `arithmetic_v0_gpt2-small` / `h_arithmetic_v0_001`: demoted under the high-power rerun
- `arithmetic_v0_gpt2-small` / `h_arithmetic_v0_003`: demoted under the high-power rerun
- `arithmetic_v0_pythia-70m` / `h_arithmetic_v0_002`: retained but failed holdouts ['base']
