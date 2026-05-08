# Protocol Critic Report

**Verdict**: WARN
**Score**: 87/100

## ⚠️ Warnings

- Only 1 resample(s) — recommend ≥2
- min_examples_per_cell=10 — recommend ≥20 for adequate power

## 💡 Suggestions

- Consider using ≥4 prompt variants for stronger robustness
- min_specificity_ratio=2.0 — consider ≥5.0 for Stage 2+
- No CI contract configured — consider adding ci_contract.enabled: true to enforce automated scientific contract checks (pitfall #74)
