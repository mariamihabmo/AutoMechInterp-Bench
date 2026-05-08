# Benchmark Positioning

AutoMechInterp is best positioned as a **reliability benchmark for mechanistic-interpretability evidence**.

It is not primarily a discovery benchmark and not a general model capability benchmark. Its core question is:

> Given a concrete mechanistic claim and its artifact bundle, does the evidence meet a frozen acceptance contract?

## Ecosystem map

The table below organizes adjacent work by evaluation target and objective.

| Category | Representative examples | What is evaluated | Typical output |
|---|---|---|---|
| Claim-verification benchmark | **AutoMechInterp** | quality and robustness of submitted claim evidence | gate outcomes, tier labels, remediation diagnostics |
| Method-performance benchmark (mechanistic interpretability) | [MIB](https://arxiv.org/abs/2504.13151), [InterpBench](https://arxiv.org/abs/2407.14494) | how well interpretability methods recover known/curated structures | task/track scores, benchmark leaderboards |
| Synthetic known-mechanism testbeds | [Tracr](https://arxiv.org/abs/2301.05062) and related synthetic setups | behavior on models with known construction | controlled success/failure analyses |
| General model-eval frameworks | [HELM](https://arxiv.org/abs/2211.09110), [lm-eval-harness](https://github.com/EleutherAI/lm-evaluation-harness), [OpenAI Evals](https://github.com/openai/evals) | model behavior/capability under task suites | aggregate model performance metrics |
| Discovery/intervention toolkits | [TransformerLens](https://transformerlensorg.github.io/TransformerLens/), [nnsight](https://nnsight.net/), [pyvene](https://stanfordnlp.github.io/pyvene/), [SAELens](https://github.com/jbloomAus/SAELens) | exploratory hypothesis generation and intervention workflows | hypotheses, traces, activation analyses |

## Core objective differences

### 1) What is the unit of evaluation?

- AutoMechInterp: a **claim bundle** (claim + protocol + raw cells + manifest).
- Method benchmarks: a **method/task pair**.
- Capability benchmarks: a **model/task pair**.

### 2) What counts as success?

- AutoMechInterp: passing a frozen evidentiary contract with deterministic outputs.
- Method benchmarks: high benchmark score against known/curated criteria.
- Capability benchmarks: high performance on behavior tasks.

### 3) How are failures explained?

- AutoMechInterp: gate-level decomposition (causal, controls, robustness, statistics, integrity).
- Method benchmarks: usually task-level misses or method-level score drop.
- Capability benchmarks: benchmark metric regressions.

## Detailed positioning matrix

| Dimension | AutoMechInterp | MIB / InterpBench-style | HELM / lm-eval / OpenAI Evals |
|---|---|---|---|
| Primary question | Is this claim evidence robust enough to accept? | Which method performs better across benchmark tasks? | How good is model behavior on benchmark tasks? |
| Input artifact | claim bundle with intervention cells | method outputs on benchmark suites | model responses / eval traces |
| Contract stability | explicit and frozen per protocol version | benchmark protocol dependent | benchmark suite dependent |
| Deterministic rerun requirement | first-class requirement | varies | varies |
| Failure granularity | gate-level | task/track-level | metric-level |
| Suitability for publication claim auditing | high | medium | low |
| Suitability for broad capability ranking | low | low/medium | high |

## Where AutoMechInterp is strongest

- Standardizing acceptance criteria across heterogeneous discovery lanes.
- Making evidence failures actionable via structured diagnostics.
- Enabling longitudinal comparability with protocol versioning.
- Supporting external bundle submissions with deterministic rerun checks.

## Where AutoMechInterp is not the best tool

- Discovering mechanisms from scratch.
- Ranking foundation models by capability.
- Replacing controlled synthetic ground-truth method tests.

## Complementarity model

A practical high-rigor stack looks like:

1. discovery tools generate hypotheses and intervention traces
2. method benchmarks evaluate discovery quality trends
3. AutoMechInterp verifies claim evidence readiness for external reporting

This stack separates **exploration speed** from **acceptance rigor**.

## Current field position summary

Today, many mechanistic-interp workflows have strong discovery tooling but weaker standardized acceptance contracts. AutoMechInterp addresses that gap by treating claim verification as a first-class benchmark objective.

That makes it a strong complement to both method benchmarks and discovery toolchains, especially when teams need reproducible acceptance decisions rather than one-off case-study judgments.
