# Submission Review

- Generated: 2026-04-08T21:39:38.594881+00:00
- Bundle: `main/output/real_multi_task/ioi_v0_gpt2-small`
- Protocol: `real_ioi_v0_gpt2-small`
- Protocol hash: `2cf9391768fcc170931f8224eb50009edde4e328ae068c6389e398b9f8a15fba`
- Reruns: 2 / 2
- Deterministic: True
- Exact JSON matches: 2
- Exact Markdown matches: 2

## Overall

- Hypotheses: 4
- Accepted: 2
- Unstable: 0
- Rejected: 2

## Workflow Actions

### h_ioi_v0_001
- Tier: `single_model_confirmed`
- Passed: True
- Action: Ready to share as a single-model claim; collect cross-model evidence before making transfer claims.
- Failed checks: none
- Not evaluated: cross_model_transfer

### h_ioi_v0_002
- Tier: `rejected`
- Passed: False
- Action: Do not present as validated; use failed gates to redesign the hypothesis or protocol.
- Failed checks: causal_effect, negative_controls, robustness, method_sensitivity
- Not evaluated: cross_model_transfer

### h_ioi_v0_003
- Tier: `rejected`
- Passed: False
- Action: Do not present as validated; use failed gates to redesign the hypothesis or protocol.
- Failed checks: causal_effect, robustness, method_sensitivity
- Not evaluated: cross_model_transfer

### h_ioi_v0_mlp_001
- Tier: `single_model_confirmed`
- Passed: True
- Action: Ready to share as a single-model claim; collect cross-model evidence before making transfer claims.
- Failed checks: none
- Not evaluated: cross_model_transfer

## Protocol Critic

- Verdict: WARN
- Score: 87/100
- Blockers: 0
- Warnings: 2
- Suggestions: 3

## Recommendation

Bundle is deterministic and contains accepted claims.
