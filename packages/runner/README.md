# AutoMechInterp Stage-2 Runner

The Stage-2 runner generates `evaluation_result.json` artifacts from structured hypothesis bundles.

## Responsibilities

1. load the frozen protocol and hypotheses
2. run real or mock interventions
3. emit provenance-rich raw cells
4. preserve split semantics, direction semantics, and manifest integrity

## Current scope

The packaged runner supports the benchmark task registry and component types implemented in `automechinterp_runner`.
Real breadth is still narrower than theoretical support, so users should distinguish:

1. what the package can execute,
2. what the release has actually evaluated, and
3. what the papers use as headline evidence.

## Command

```bash
automechinterp-runner run --bundle ./my_bundle --device cpu --mode mock
```

Useful flags:

1. `--mode real|mock`
2. `--examples-per-cell N`
3. `--device cpu|mps|cuda`

## Output

The runner writes:

1. `evaluation_result.json`
2. updated `manifest.json`
3. environment/provenance fields required by the evaluator

## Semantics

The current runner is intended to preserve:

1. explicit sufficiency vs necessity direction fields,
2. a real exploratory/confirmatory partition in real mode,
3. type-matched random controls where implemented,
4. deterministic shuffled-token controls,
5. non-silent mean-ablation behavior.

## Typical pipeline

```bash
python -m automechinterp_evaluator.cli generate-agent-output \
  --bundle ./my_bundle \
  --count 3 \
  --overwrite

python -m automechinterp_evaluator.cli generate-hypotheses \
  --bundle ./my_bundle \
  --agent-output ./my_bundle/agent_output.json \
  --overwrite

automechinterp-runner run --bundle ./my_bundle --device cpu --mode mock
python -m automechinterp_evaluator.cli evaluate --bundle ./my_bundle
```

## Caveat

Passing through the runner does not make a claim accepted. Acceptance is always decided downstream by the evaluator contract.
