# Independent Agnostic Negative Spec

This document defines a neutral interchange format for independently authored
negative claims. It is intentionally simpler than a full claim bundle so that a
negative author can produce test cases without learning the evaluator's gate
taxonomy.

## JSONL Format

Each line is one negative claim object:

```json
{
  "negative_id": "neg_000001",
  "task_id": "ioi_v0",
  "model_id": "gpt2-small",
  "claim_text": "A plausible but intentionally unsupported mechanistic claim.",
  "candidate_components": [
    {"component_type": "head", "layer": 10, "head": 7}
  ],
  "predicted_effect_direction": "increase",
  "predicted_min_effect": 0.02,
  "predicted_specificity_ratio": 2.0,
  "author_slice": "near_miss",
  "generation_notes": "Short private-to-public-safe description.",
  "visibility": {
    "saw_public_bundles": true,
    "saw_gate_taxonomy": false,
    "saw_v1_thresholds": false,
    "received_scoring_feedback": false
  },
  "evidence_cells": [
    {
      "seed": 42,
      "prompt_variant": "base",
      "resample_id": 0,
      "method": "activation_patching",
      "direction": "sufficiency_patch",
      "slice": "exploratory",
      "treatment_effect": 0.01,
      "control_effects": {
        "wrong_position": 0.0,
        "wrong_layer": 0.0,
        "random_component": 0.0,
        "mismatched_source": 0.0
      },
      "runner_id": "external_runner",
      "runner_version": "0.1.0",
      "pipeline_sha": "sha256-or-version-pin",
      "model_ref": "gpt2-small",
      "dataset_seed": 42,
      "prompt_template_id": "base"
    }
  ]
}
```

## Required Fields

| Field | Meaning |
|---|---|
| `negative_id` | Stable unique ID within the negative set |
| `task_id` | Released task family |
| `model_id` | Released model or approved target model |
| `claim_text` | Natural language claim, safe to publish after review |
| `candidate_components` | Candidate mechanism components |
| `predicted_effect_direction` | `increase` or `decrease` |
| `author_slice` | Author-defined slice such as `near_miss`, `adaptive`, `plausible_wrong` |
| `visibility` | What the author saw while generating the negative |

## Optional Fields

| Field | Meaning |
|---|---|
| `predicted_min_effect` | Claimed practical effect floor |
| `predicted_specificity_ratio` | Claimed specificity ratio |
| `generation_notes` | Public-safe notes about generation |
| `private_metadata_sha256` | Hash of private generation metadata |
| `evidence_cells` | Optional raw evidence cells. If present on every row, `main/run_independent_agnostic_stress.py` can score the set under the current or V1 contract. |

## Scorable Evidence Cells

Validation-only negative sets are useful for rehearsal, but they do not produce
a false-accept rate. To score a negative set, every row must include
`evidence_cells`, where each cell has:

| Field | Meaning |
|---|---|
| `seed`, `prompt_variant`, `resample_id`, `method`, `slice` | The execution-grid coordinates. `slice` must be `exploratory` or `confirmatory`. |
| `direction` | Optional intervention direction such as `sufficiency_patch` or `necessity_ablate`. |
| `treatment_effect` | Numeric measured treatment effect for this cell. |
| `control_effects` | Numeric control effects for all control families required by the matched released protocol. |
| `runner_id`, `runner_version`, `pipeline_sha`, `model_ref`, `dataset_seed`, `prompt_template_id` | Provenance fields required by the evaluator loader. |

The scorer groups rows by `(task_id, model_id)`, uses the matching released
protocol as the base contract, and writes only aggregate false-accept results.
It does not by itself establish independence; independence still depends on
provenance, attestation, and freeze-before-scoring discipline.

## Evidence-Bearing Requirements

For an evidence-bearing independent stress run:

1. `visibility.saw_v1_thresholds` must be false.
2. `visibility.received_scoring_feedback` must be false.
3. The negative set must be frozen before scoring.
4. The author must provide a provenance statement or attestation.
5. If `evidence_cells` are supplied, they must be generated before any scoring
   feedback under either the current contract or contract-hardening V1.

If these requirements are not met, the run may still be useful, but it should
be labeled evaluator-aware or rehearsal rather than evaluator-agnostic.
