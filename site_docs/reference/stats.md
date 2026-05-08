# Metrics And Statistics

This page describes the role of statistical checks in the contract.

## Why a statistics suite exists

Mechanistic claims can appear convincing from effect means alone. Statistical gates protect against chance-driven acceptance and unstable conclusions.

## Statistical checks in scope

- confirmatory interval adequacy
- multiplicity correction policy
- power adequacy checks
- thresholded effect requirements

## Interaction with other suites

Statistics is not a replacement for causal/controls/robustness evidence.

A claim can pass statistical checks and still fail causal or control gates.

## Practical interpretation

- `confirmatory_ci` failure often indicates uncertain confirmatory signal.
- `multiplicity` failure indicates insufficient correction under family-level testing.
- `power_adequacy` failure indicates underpowered evidence.

## Reporting recommendation

Always report:

- accepted and rejected counts
- failed statistics gates by frequency
- confidence intervals for acceptance-rate summaries
- protocol version/hash and rerun status
