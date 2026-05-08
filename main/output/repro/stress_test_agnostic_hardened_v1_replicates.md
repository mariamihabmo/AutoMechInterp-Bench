# Evaluator-Agnostic Stress Replicates Under Contract Hardening V1

- Overrides: **min_causal_effect=0.15, min_effect_floor=0.15, min_specificity_ratio=5.0**
- Generator regime: **fresh_v2**
- Statistical budget: **default release-grade**
- Namespaces: **2**
- Worst 95% upper bound: **1.9%**
- All upper bounds below 5%: **yes**

| Seed namespace | Leaked | FAR | 95% CI |
|---|---:|---:|---|
| `rotated_2026q2` | 0/200 | 0.0% | [0.0%, 1.9%] |
| `rotated_2026q3` | 0/200 | 0.0% | [0.0%, 1.9%] |

These are diagnostic stress replicates for a versioned contract-migration candidate. They do not change the released contract unless adopted through protocol governance.
