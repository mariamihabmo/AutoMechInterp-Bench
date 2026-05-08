# Suite-Targeted Stress Test

- Base bundle: `main/output/real_multi_task/ioi_v0_gpt2-small`
- Synthetic negatives: **30**

| Condition | Leaked | FAR | 95% CI |
|---|---|---|---|
| full_contract | 0/30 | 0.0% | [0.0%, 11.4%] |
| no_stat_rigor | 10/30 | 33.3% | [19.2%, 51.2%] |
| no_robustness_suite | 10/30 | 33.3% | [19.2%, 51.2%] |
| no_controls_suite | 10/30 | 33.3% | [19.2%, 51.2%] |
| minimal_gates | 30/30 | 100.0% | [88.6%, 100.0%] |

## Calibration Notes

- `plausible_but_wrong` is intended to be most diagnostic for the statistical-rigor suite.
- `method_sensitive` is intended to be most diagnostic for the robustness / sensitivity suite.
- `control_leaking` is intended to be most diagnostic for the controls suite.

## Per-family leakage

### full_contract

| Family | Leaked | FAR |
|---|---|---|
| plausible_but_wrong | 0/10 | 0.0% |
| method_sensitive | 0/10 | 0.0% |
| control_leaking | 0/10 | 0.0% |

### no_stat_rigor

| Family | Leaked | FAR |
|---|---|---|
| plausible_but_wrong | 10/10 | 100.0% |
| method_sensitive | 0/10 | 0.0% |
| control_leaking | 0/10 | 0.0% |

### no_robustness_suite

| Family | Leaked | FAR |
|---|---|---|
| plausible_but_wrong | 0/10 | 0.0% |
| method_sensitive | 10/10 | 100.0% |
| control_leaking | 0/10 | 0.0% |

### no_controls_suite

| Family | Leaked | FAR |
|---|---|---|
| plausible_but_wrong | 0/10 | 0.0% |
| method_sensitive | 0/10 | 0.0% |
| control_leaking | 10/10 | 100.0% |

### minimal_gates

| Family | Leaked | FAR |
|---|---|---|
| plausible_but_wrong | 10/10 | 100.0% |
| method_sensitive | 10/10 | 100.0% |
| control_leaking | 10/10 | 100.0% |
