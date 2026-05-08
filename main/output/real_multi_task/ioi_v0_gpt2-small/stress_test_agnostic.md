# Evaluator-Agnostic Latent Stress

- Base bundle: `main/output/real_multi_task/ioi_v0_gpt2-small`
- Negatives: **40**

| Condition | Leaked | FAR | 95% CI |
|---|---|---|---|
| full_contract | 4/40 | 10.0% | [4.0%, 23.1%] |
| no_controls_suite | 5/40 | 12.5% | [5.5%, 26.1%] |
| no_robustness_suite | 4/40 | 10.0% | [4.0%, 23.1%] |
