# AutoMechInterp

<div class="hero">
  <p><strong>AutoMechInterp is an open-source benchmark for mechanistic-interpretability claim verification.</strong></p>
  <p>It gives teams a deterministic acceptance contract: the same bundle, protocol, and environment should produce the same gate outcomes and evidence tier every time.</p>
  <div class="cta-row">
    <a href="quickstart/">Run the 10-minute quickstart</a>
    <a href="contract/">Read the benchmark contract</a>
    <a href="submit/">Submit a claim bundle</a>
    <a href="comparisons/positioning/">See field positioning</a>
  </div>
</div>

<div class="snapshot-strip">
  <strong>Why this benchmark matters:</strong> mechanistic claims can look convincing under one intervention setup and fail under controls, robustness tests, or stricter statistical policy. AutoMechInterp standardizes those checks so evidence quality is comparable across tasks, models, and discovery pipelines.
</div>

## What AutoMechInterp is and is not

AutoMechInterp is a verifier contract, not a mechanism-discovery algorithm.

- It accepts or rejects claim evidence under a frozen policy.
- It emits gate-level diagnostics so failures are actionable.
- It can evaluate bundles from many upstream discovery methods.

It does **not** claim to prove universal circuit ground truth by itself.

## What you get

<div class="grid cards" markdown>

- :material-shield-check: **Deterministic verification contract**

  A fixed gate policy with explicit outcomes (`pass`, `fail`, `not_evaluated`) and stable tier mapping.

- :material-file-document-outline: **Portable bundle standard**

  Common artifacts (`protocol.yaml`, `hypothesis.jsonl`, `evaluation_result.json`, `manifest.json`) that any lab can produce.

- :material-chart-box-outline: **Actionable failure reports**

  Claim-level failure decomposition and remediation guidance, not just a single summary label.

- :material-lan-connect: **Lane-agnostic acceptance logic**

  Discovery methods can vary widely while acceptance standards stay fixed and comparable.

</div>

## Who this is for

- Researchers publishing mechanistic claims.
- Labs validating claims from multiple discovery lanes.
- Tool builders implementing compatible evaluators.
- External collaborators who need reproducible acceptance criteria.

## Stage-gate flow

1. A discovery lane proposes candidate mechanistic hypotheses.
2. Hypotheses and intervention outputs are serialized into a bundle.
3. The evaluator applies causal, controls, robustness, and statistical gates.
4. Evidence tiers and diagnostics drive publication decisions and next experiments.

## Documentation map

### Start quickly

- [Quickstart (10 min)](quickstart.md)
- [Setup](setup.md)
- [Demo (2-5 min)](demo.md)

### Understand the contract

- [Benchmark contract](contract.md)
- [Evidence tiers](tiers.md)
- [Gates and suites](gates.md)
- [Determinism and integrity](determinism.md)

### Build and submit bundles

- [Submitting a claim bundle](submit.md)
- [Bundle checklist](bundle-checklist.md)
- [Artifact spec overview](spec.md)
- [Bundle page template](results/bundle-template.md)

### Compare with adjacent work

- [Benchmark positioning](comparisons/positioning.md)
- [Compared to MIB](comparisons/mib.md)
- [Compared to discovery tools](comparisons/tools.md)

## Legacy website access

The previous static site is preserved and still accessible:

- `https://anonymous.example.org/automechinterp/legacy/index.html`
