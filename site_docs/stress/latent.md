# Evaluator-Agnostic Latent Stress

## Goal

Test verifier robustness using perturbations that are not directly defined by named gate templates.

## Command

```bash
python main/stress_test_agnostic.py \
  --bundle-dir main/output/real_multi_task/ioi_v0_gpt2-small
```

## Why this regime exists

If stress generation is fully evaluator-aware, measured robustness can be inflated by construction.

Latent stress reduces that coupling by perturbing underlying factors instead of directly targeting declared gate families.

## Output artifact

- `stress_test_agnostic.json`

## What to inspect

- false-accept behavior under latent perturbation families
- whether failures cluster differently than suite-targeted ablations
- whether observed weaknesses generalize across bundles
