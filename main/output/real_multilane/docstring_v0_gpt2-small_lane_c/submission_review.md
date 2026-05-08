# Submission Review

- Generated: 2026-04-29T22:41:56.029913+00:00
- Bundle: `main/output/real_multilane/docstring_v0_gpt2-small_lane_c`
- Protocol: `multilane_C_docstring_v0_gpt2-small`
- Protocol hash: `204a1246e4bf07f8a31701e864cf70c26b0a74eb0fb85ee861d21d7cc08a9090`
- Reruns: 3 / 3
- Deterministic: True
- Exact JSON matches: 3
- Exact Markdown matches: 3

## Overall

- Hypotheses: 3
- Accepted: 1
- Unstable: 0
- Rejected: 2

## Workflow Actions

### h_dla_docstring_v0_001
- Tier: `rejected`
- Passed: False
- Action: Do not present as validated; use failed gates to redesign the hypothesis or protocol.
- Failed checks: negative_controls, baseline_superiority, cross_model_transfer
- Not evaluated: none

### h_dla_docstring_v0_002
- Tier: `rejected`
- Passed: False
- Action: Do not present as validated; use failed gates to redesign the hypothesis or protocol.
- Failed checks: negative_controls
- Not evaluated: none

### h_dla_docstring_v0_003
- Tier: `single_model_confirmed`
- Passed: True
- Action: Ready to share as a single-model claim; collect cross-model evidence before making transfer claims.
- Failed checks: cross_model_transfer
- Not evaluated: none

## Protocol Critic

- Verdict: WARN
- Score: 82/100
- Blockers: 0
- Warnings: 3
- Suggestions: 3

## Recommendation

Bundle is deterministic and contains accepted claims.
