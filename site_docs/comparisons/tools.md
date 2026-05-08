# Compared To Discovery Tools

AutoMechInterp is not a replacement for discovery or intervention frameworks. It is a verifier layer that sits downstream of them.

## Tool landscape

| Tool / framework | Primary purpose | Typical role in pipeline |
|---|---|---|
| [TransformerLens](https://transformerlensorg.github.io/TransformerLens/) | activation inspection, patching, circuit analysis | generate candidate mechanistic hypotheses |
| [nnsight](https://nnsight.net/) | model internals inspection/intervention at scale | collect intervention traces and candidate explanations |
| [pyvene](https://stanfordnlp.github.io/pyvene/) | declarative intervention experiments | run causal tests and produce structured intervention outputs |
| [SAELens](https://github.com/jbloomAus/SAELens) | sparse autoencoder training/analysis | derive feature-centric hypotheses |
| [Captum](https://captum.ai/) | attribution/explainability toolkit | produce attribution evidence for hypothesis generation |

## Layer boundaries

### Discovery layer (tools above)

- prioritize hypothesis generation speed and exploratory coverage
- allow diverse intervention and analysis methods
- optimize for finding potentially interesting mechanisms

### Verification layer (AutoMechInterp)

- enforce fixed acceptance policy
- evaluate claim evidence under controls/robustness/statistics/integrity
- optimize for reliability and comparability

## Why strict separation helps

If discovery and acceptance are merged, standards often drift with method changes.

A separate verifier layer avoids this by keeping acceptance criteria stable while discovery methods continue to evolve.

## Integration pattern

1. Run your preferred discovery/intervention tool.
2. Convert outputs into claim bundle artifacts.
3. Evaluate with AutoMechInterp.
4. Use gate diagnostics to design the next discovery experiments.

## Mapping tool outputs to bundle artifacts

| Bundle artifact | Upstream source examples |
|---|---|
| `hypothesis.jsonl` | ranked components, neuron explanations, feature candidates |
| `evaluation_result.json` | intervention cells, patching traces, causal test outputs |
| `protocol.yaml` | frozen evaluation policy chosen for this run |
| `manifest.json` | hash binding over finalized artifacts |

## Typical failure loop

- Discovery proposes promising claim.
- Verifier rejects due to method sensitivity or controls.
- Discovery reruns with targeted interventions and stronger controls.
- Bundle resubmitted and reevaluated.

This loop is exactly where verification benchmarks add value: they convert “interesting idea” into “evidence that survives scrutiny.”

## Practical takeaway

Discovery tools answer “what might be happening?”

AutoMechInterp answers “is the current evidence strong enough under a fixed contract?”

Both are necessary for robust mechanistic-interpretability science.
