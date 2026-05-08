# Auto-MechInterp Stage-1 (Rebuild)

Stage-1 is a deterministic gatekeeper for mechanistic-interpretability claims.

## Purpose
- Allow agents to propose hypotheses.
- Prevent agents from self-certifying claims.
- Accept claims only when precommitted, objective checks pass.

## Bundle contract
A valid bundle directory must contain:
- `protocol.yaml`
- `hypothesis.jsonl`
- `evaluation_result.json`
- `manifest.json`

`evaluation_result.json` raw cells must include provenance metadata (`runner_id`, `runner_version`, `pipeline_sha`, `model_ref`, `dataset_seed`, `prompt_template_id`) so results are traceable to a concrete execution pipeline.

## Hard-gate pillars
1. Causal effect passes effect floor and direction.
2. Negative controls are complete and small enough.
3. Robustness passes seed/prompt/resample thresholds.
4. Method sensitivity stays below max dispersion.
5. Confirmatory CI exclusion (if required).
6. Multiplicity threshold pass.
7. Protocol hash and manifest integrity.
8. Execution grid completeness.

## Commands
```bash
# Evaluate bundle and print JSON summary
automechinterp-evaluator evaluate --bundle path/to/bundle

# Write markdown report
automechinterp-evaluator report --bundle path/to/bundle --output stage_gate_report.md

# Copy example bundle template
automechinterp-evaluator init-template --output-dir ./my_bundle

# Run publication-facing rerun + workflow review
automechinterp-evaluator submission-review --bundle ./my_bundle --reruns 3

# Emit compatibility vectors for third-party implementations
automechinterp-evaluator reference-vectors --output-dir ./reference_vectors

# Assemble a reviewer audit kit (portable, but still requiring either the installed package or a repo checkout for reruns)
automechinterp-evaluator reviewer-kit --bundle ./my_bundle --output-dir .

# Generate deterministic discovery-agent output from protocol
automechinterp-evaluator generate-agent-output \
  --bundle ./my_bundle \
  --count 3 \
  --exploration-input ./autonomous_exploration.json \
  --overwrite

# Generate validated hypothesis.jsonl from agent output
automechinterp-evaluator generate-hypotheses \
  --bundle ./my_bundle \
  --agent-output ./agent_hypotheses.json \
  --overwrite
```

## Determinism model
- Protocol defines execution grid exactly.
- Stage-gate computes verdict from artifacts only.
- Any protocol or manifest mismatch is a hard failure.

## Test coverage
The test suite checks schema integrity and every gate failure path.

Run from the repository root:
```bash
python -m pytest packages/evaluator/tests -q
```
