# Submission Review

- Generated: 2026-04-29T22:41:56.044797+00:00
- Bundle: `main/output/real_multilane/docstring_v0_gpt2-small_lane_b`
- Protocol: `multilane_B_docstring_v0_gpt2-small`
- Protocol hash: `394fd339aa513c2b5e86343506faa7263b550828c41e0432b7816260ebcfdc51`
- Reruns: 3 / 3
- Deterministic: True
- Exact JSON matches: 3
- Exact Markdown matches: 3

## Overall

- Hypotheses: 3
- Accepted: 0
- Unstable: 0
- Rejected: 3

## Workflow Actions

### h_neuron_docstring_v0_001
- Tier: `rejected`
- Passed: False
- Action: Do not present as validated; use failed gates to redesign the hypothesis or protocol.
- Failed checks: causal_effect, negative_controls, robustness, confirmatory_ci, multiplicity, power_adequacy, effect_size_practical, baseline_superiority
- Not evaluated: cross_model_transfer

### h_neuron_docstring_v0_002
- Tier: `rejected`
- Passed: False
- Action: Do not present as validated; use failed gates to redesign the hypothesis or protocol.
- Failed checks: causal_effect, robustness, power_adequacy
- Not evaluated: cross_model_transfer

### h_neuron_docstring_v0_003
- Tier: `rejected`
- Passed: False
- Action: Do not present as validated; use failed gates to redesign the hypothesis or protocol.
- Failed checks: causal_effect, negative_controls, robustness, confirmatory_ci, multiplicity, power_adequacy, effect_size_practical
- Not evaluated: cross_model_transfer

## Protocol Critic

- Verdict: WARN
- Score: 82/100
- Blockers: 0
- Warnings: 3
- Suggestions: 3

## Recommendation

Resolve determinism or evidentiary weaknesses before external submission.
