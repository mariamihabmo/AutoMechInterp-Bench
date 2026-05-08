# Evaluator-Agnostic Stress Leak Forensics

- Source: `main/output/real_multi_task/ioi_v0_gpt2-small/stress_test_agnostic.json`
- Total negatives per condition: **40**

## Per-condition leak summary

| condition | leaked | FAR | leaks with per-leak data |
|---|---|---|---|
| `full_contract` | 4/40 | 10.0% | 4 |
| `no_controls_suite` | 5/40 | 12.5% | 5 |
| `no_robustness_suite` | 4/40 | 10.0% | 4 |

_If `leaks with per-leak data` < `leaked`, regenerate `stress_test_agnostic.json` after the per-leak enrichment in `main/stress_test_agnostic.py` to populate the diagnostic._

## Full-contract leak detail

| hypothesis | tier | signal | control | dispersion | decay | flip |
|---|---|---|---|---|---|---|
| `latent_018` | `single_model_confirmed` | 0.0529 | 0.0266 | 0.1527 | 0.5848 | False |
| `latent_028` | `single_model_confirmed` | 0.0125 | 0.0111 | 0.1034 | 0.5708 | False |
| `latent_031` | `single_model_confirmed` | 0.0643 | 0.0251 | 0.2179 | 1.1118 | False |
| `latent_032` | `single_model_confirmed` | 0.0687 | 0.0519 | 0.2863 | 0.5918 | False |

## Structural observations (DESIGN DISCUSSION ONLY)

- **Observation:** Full-contract leaks have latent_signal in [0.0125, 0.0687] (median 0.0586). The latent generator's signal range is [0.01, 0.08].
  - **Candidate addendum:** Tighten the practical-effect-size floor or require confirmatory evidence at >= max(signal) latent magnitude before granting single_model_confirmed. NOT APPLIED -- applying this against the leak set would risk overfitting the contract to the agnostic generator's known sample.
- **Observation:** Full-contract leaks have latent_control in [0.0111, 0.0519] (median 0.0258).
  - **Candidate addendum:** Add a control-leakage floor that disqualifies any claim whose control effect exceeds a tighter fraction of its treatment effect. NOT APPLIED for the same Goodhart reason.
- **Observation:** All full-contract leaks have latent_direction_flip = False, i.e. the direction was stable relative to the source.
  - **Candidate addendum:** This is informative for diagnosis but does NOT motivate a contract addendum: the stable-direction subset is precisely what a true positive should look like. Tightening here would weaken the benchmark, not strengthen it.

## Why no contract changes are applied here

Suggestions in 'suggested_addenda_for_design_discussion_only' are structural observations from the released leak set. Applying them as actual gate changes would tune the contract to the agnostic generator's known leaks, which is the exact Goodhart trap the agnostic regime exists to detect. Any future contract change motivated by these observations should be designed against a *new* generator that did not produce the leaks, with the original generator preserved as a regression check.
