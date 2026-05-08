# Submission Review

- Generated: 2026-04-29T22:41:55.405635+00:00
- Bundle: `main/output/real_multilane/docstring_v0_gpt2-small_lane_a`
- Protocol: `multilane_A_docstring_v0_gpt2-small`
- Protocol hash: `55f778d423942a6e290ec364c305843dbce8d1bb0198144c4f0640fef3f9d545`
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

### h_sweep_docstring_v0_001
- Tier: `rejected`
- Passed: False
- Action: Do not present as validated; use failed gates to redesign the hypothesis or protocol.
- Failed checks: negative_controls, cross_model_transfer
- Not evaluated: none

### h_sweep_docstring_v0_002
- Tier: `single_model_confirmed`
- Passed: True
- Action: Ready to share as a single-model claim; collect cross-model evidence before making transfer claims.
- Failed checks: cross_model_transfer
- Not evaluated: none

### h_sweep_docstring_v0_003
- Tier: `rejected`
- Passed: False
- Action: Do not present as validated; use failed gates to redesign the hypothesis or protocol.
- Failed checks: negative_controls
- Not evaluated: none

## Protocol Critic

- Verdict: WARN
- Score: 82/100
- Blockers: 0
- Warnings: 3
- Suggestions: 3

## Recommendation

Bundle is deterministic and contains accepted claims.
