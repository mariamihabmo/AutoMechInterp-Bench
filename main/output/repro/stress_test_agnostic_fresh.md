# Evaluator-Agnostic Latent Stress

- Base bundle: `main/output/real_multi_task/ioi_v0_gpt2-small`
- Negatives: **200**
- Generator regime: **fresh_v2**
- Seed namespace: **rotated_2026q2**
- Bootstrap resamples override: **128**
- Permutation iterations override: **128**

| Condition | Leaked | FAR | 95% CI |
|---|---|---|---|
| full_contract | 49/200 | 24.5% | [19.1%, 30.9%] |
