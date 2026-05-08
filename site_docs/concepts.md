# Concepts

## Core objects

| Term | Definition | Where it appears |
|---|---|---|
| Claim | Mechanistic hypothesis to verify | `hypothesis.jsonl` |
| Bundle | Full artifact package for evaluation | bundle directory |
| Protocol | Frozen acceptance policy and thresholds | `protocol.yaml` |
| Raw cell | Intervention/measurement record | `evaluation_result.json` |
| Gate | Deterministic evidence check | evaluator outputs |
| Gate outcome | `pass`, `fail`, `not_evaluated` | `claim_reports[*].gate_outcomes` |
| Evidence tier | Final claim classification | `claim_reports[*].evidence_tier` |
| Lane | Discovery source/workflow | claim metadata |

## Supported discovery lanes

| Lane | Source style | Typical output |
|---|---|---|
| A | Circuit sweep workflows | ranked component hypotheses |
| B1 | OpenAI-style neuron explanation | neuron claims |
| B2 | Efficient prompt-tuned autointerp | neuron/feature claims |
| B3 | SAE feature pipelines | `sae_feature` claims |
| C | Behavioral/Petri-style workflows | behavior-linked claims |

## Supported component types

| Type | Granularity |
|---|---|
| `head` | attention head role |
| `mlp` | MLP block role |
| `residual_stream` | residual stream contribution |
| `edge` | source-target component interaction |
| `mlp_neuron` | single neuron function |
| `sae_feature` | sparse latent feature function |
| `das_subspace` | causal subspace effect |

## Required files

- `protocol.yaml`
- `hypothesis.jsonl`
- `evaluation_result.json`
- `manifest.json`

## Why tri-state outcomes matter

`not_evaluated` distinguishes missing evidence from contradictory evidence, which prevents misleading boolean-only summaries and improves remediation planning.
