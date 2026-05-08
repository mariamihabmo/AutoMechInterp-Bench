# Discovery Lanes Reference

Auto‑MechInterp separates **hypothesis generation** from **verification**.
Any system that produces mechanistic claims is a *discovery lane* — a
hypothesis provider that emits structured claims into the same deterministic
evaluation pipeline.

## Architecture

```
Provider (lane) → exploration artifact → hypothesis.jsonl
    → Stage-2 runner → evaluation_result.json
    → Stage-1 gates (15 hard gates) → evidence tier + leaderboard
```

Every lane implements the `HypothesisProvider` interface and emits
`hypothesis.jsonl`-compatible dicts. Stage-1 never changes — it is the
single, frozen judge.

---

## Supported Lanes

| Lane | Provider Class | Component Type | Description |
|------|---------------|----------------|-------------|
| **A** | `CircuitSweepProvider` | `head` | Cheap patching sweep: test each head, rank by effect, emit top-k |
| **B1** | `OpenAIAutoInterpProvider` | `mlp_neuron` | Adapter for OpenAI explainer/simulator neuron explanations |
| **B2** | `EfficientNeuronExplanationsProvider` | `mlp_neuron` | Adapter for prompt-tuned neuron explanations (Trustworthy-ML-Lab) |
| **B3** | `SAEAutoInterpProvider` | `sae_feature` | Adapter for SAE feature selection (e.g. bigsnarfdude/autointerp) |
| **C** | `PetriBehavioralProvider` | any | Adapter for Anthropic Petri behavioral auditing transcripts |

---

## Supported Component Types

| Component Type | Required Fields | Control Families |
|---------------|----------------|------------------|
| `head` | `layer`, `head` | wrong_position, wrong_layer, random_component, mismatched_source, shuffled_token, adjacent_head |
| `mlp` | `layer` | wrong_position, wrong_layer, random_component, mismatched_source, shuffled_token |
| `residual_stream` | `layer` | wrong_position, wrong_layer, random_component, mismatched_source |
| `edge` | `source_layer`, `source_head`, `target_layer`, `target_head` | wrong_position, wrong_layer, random_component, mismatched_source, random_edge |
| `mlp_neuron` | `layer`, `neuron` | wrong_position, wrong_layer, random_neuron, mismatched_source, adjacent_neuron |
| `sae_feature` | `sae_id`, `layer`, `feature_id` | wrong_layer_feature, random_feature, mismatched_sae_source, wrong_position |
| `das_subspace` | `layer`, `subspace_dim` | wrong_layer, random_subspace, mismatched_source, wrong_position |

---

## Adding a New Lane

1. Create a new file in `packages/runner/src/automechinterp_runner/providers/`
2. Subclass `HypothesisProvider` and implement `propose(protocol, budget)`
3. Decorate with `@register_provider`
4. Each hypothesis dict must contain all fields from `REQUIRED_HYPOTHESIS_FIELDS`
5. Set `discovery_lane` and `provider_id` in the metadata

```python
from automechinterp_runner.providers import HypothesisProvider, register_provider

@register_provider
class MyCustomProvider(HypothesisProvider):
    name = "my_custom_lane"
    version = "0.1.0"

    def propose(self, protocol, budget):
        # Your discovery logic here
        hypotheses = [...]
        return self.tag_hypotheses(hypotheses)
```

---

## Provider Metadata Fields

Hypotheses can include these optional metadata fields for provenance:

| Field | Type | Description |
|-------|------|-------------|
| `provider_id` | string | Name of the provider that generated this hypothesis |
| `provider_version` | string | Version of the provider |
| `discovery_lane` | string | Which lane produced this hypothesis |
| `explanation_text` | string | NL explanation (for neuron/feature providers) |
| `simulation_score` | float | Simulation quality score (never used for acceptance) |
| `sae_id` | string | Which SAE model was used |
| `sae_site` | string | Hook point for the SAE (resid_post, mlp_post, etc.) |
| `prompt_family` | string | Prompt template family (for B2 prompt-tuning ablations) |

> **Important**: Metadata fields like `explanation_text` and `simulation_score`
> are tracked for analysis but **never** used as acceptance evidence by Stage-1.
> Only causal intervention gates decide.
