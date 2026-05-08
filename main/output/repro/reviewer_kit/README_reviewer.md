# Reviewer Audit Kit

## What this is

This kit packages the core bundle artifacts, claim ledger, stage-gate report,
and protocol critic output for a single evaluated bundle.

It is **portable but not fully standalone**. To rerun the evaluator you need
either:

1. an installed `automechinterp_evaluator` package, or
2. a checkout of this repository exposed via `AUTOMECHINTERP_REPO_ROOT`.

## Quick Start
```bash
bash reproduce.sh
```

## Bundle source
- Source bundle: `main/output/real_multi_task/ioi_v0_gpt2-small`

## Contents
- `protocol.yaml` — frozen protocol defining all execution parameters
- `hypothesis.jsonl` — pre-registered hypotheses with predicted effects
- `evaluation_result.json` — raw intervention results with provenance
- `manifest.json` — SHA-256 hashes of core artifacts
- `cross_model_results.json` — released transfer diagnostics when present
- `claim_ledger.json` — machine-readable verdict for every claim
- `stage_gate_report.md` — human-readable stage-gate report
- `protocol_critic_report.md` — protocol-level readiness critique when available
- `kit_manifest.json` — reviewer-kit inventory and reproduction requirements
- `reproduce.sh` — one-command reproduction helper

## Summary
- **Protocol**: `real_ioi_v0_gpt2-small`
- **Protocol Hash**: `2cf9391768fcc170931f8224eb50009edde4e328ae068c6389e398b9f8a15fba`
- **Total Hypotheses**: 4
- **Accepted**: 2
- **Unstable**: 0
- **Rejected**: 2
- **All Pass**: False

## Verification Steps
1. Run `bash reproduce.sh` to re-evaluate from the copied artifacts.
2. Check that `manifest.json` hashes match file contents.
3. Review `claim_ledger.json` for per-claim verdicts.
4. Compare `stage_gate_report.md` with the reproduced output.
5. Inspect `protocol_critic_report.md` for missing controls or reporting gaps.

## Important caveats
- This kit does **not** prove mechanistic truth. It packages evidence for
  deterministic evaluation under the current contract.
- If `cross_model_results.json` is absent, the bundle should not be described as
  cross-model confirmed.
- The environment lockfile is a provenance artifact, not a guarantee that every
  dependency line is directly re-installable on every machine.
