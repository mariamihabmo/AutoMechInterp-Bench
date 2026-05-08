# Reproducible Bundle: IOI × GPT-2 Small

This directory contains all artifacts needed to reproduce the IOI evaluation results from the AutoMechInterp framework.

## Quick Start

```bash
# From repo root:

# 1. Run the full experiment (~4 min on MPS)
python main/run_real_multi_task.py --device mps --tasks ioi_v0 --models gpt2-small --n-examples 15 --top-k 3

# 2. Run gate ablation study (operates on cached results, <1s)
python main/stress_test_ablation.py --bundle-dir main/output/real_multi_task/ioi_v0_gpt2-small

# 3. Independent rerun verification
python -m automechinterp_evaluator.cli submission-review \
  --bundle main/output/real_multi_task/ioi_v0_gpt2-small \
  --reruns 3

# 4. Run all tests
python -m pytest packages/ -q
```

## Bundle Contents

After running, `main/output/real_multi_task/ioi_v0_gpt2-small/` contains:

| File | Contents |
|------|----------|
| `protocol.yaml` | Frozen protocol (SHA-256 hashed) |
| `hypothesis.jsonl` | Generated hypotheses |
| `evaluation_result.json` | Raw cell-level effects (cached) |
| `manifest.json` | Hash integrity verification |
| `stage_gate_report.md` | Per-hypothesis gate verdicts |
| `stress_test_ablation.json` | Evaluator-driven suite-targeted stress |
| `stress_test_agnostic.json` | Evaluator-agnostic latent stress |
| `stress_test_red_team.json` | Adaptive / near-miss / exploit probes |

## Key Results

| Hypothesis | Type | d | Tier |
|-----------|------|---|------|
| L10H7 | Head | −2.224 | `single_model_confirmed` |
| MLP L0 | MLP | −1.136 | `single_model_confirmed` |

Both pass the released core contract. `cross_model_transfer` remains `not_evaluated` in the released bundle, so the strongest released tier here is `single_model_confirmed`.

## Requirements

- Python 3.10+
- transformer_lens
- torch
