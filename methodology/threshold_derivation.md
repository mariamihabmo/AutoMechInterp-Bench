# Threshold Derivation and Sensitivity (V1 Acceptance Contract)

> **Purpose.** This file is the audit trail for the V1 acceptance-contract
> thresholds (`min_causal_effect`, `min_effect_floor`,
> `min_specificity_ratio`, `CROSS_MODEL_EFFECT_FLOOR`, `q`/`α`): where
> each value comes from, whether it was chosen pre-hoc or post-hoc, and
> how acceptance counts move when each threshold is perturbed. **None of
> the thresholds documented here are changed by this file;** it is
> documentation-only.

## 1. The thresholds at a glance

| Constant                       | Value | Source (file:symbol)                                                | Provenance |
|-------------------------------|------:|---------------------------------------------------------------------|-----------|
| `min_causal_effect` (V1)      |  0.15 | `main/contract_hardening_v1.py:HARDENING` (Stage-2+ floor in logit-diff units) | Pre-registered before contract-hardening rerun (see §3 below). |
| `min_effect_floor` (V1)       |  0.15 | `main/contract_hardening_v1.py:HARDENING`                          | Pre-registered. Tied to `min_causal_effect` so confirmatory effects never fall below the discovery floor. |
| `min_specificity_ratio` (V1)  |  5.0  | `main/contract_hardening_v1.py:HARDENING`; lower bound advertised in `packages/evaluator/.../protocol_critic.py:check_protocol_signal` (`≥5.0` for Stage-2+). | Pre-registered. |
| `CROSS_MODEL_EFFECT_FLOOR`    |  0.02 | `packages/evaluator/src/automechinterp_evaluator/constants.py`     | Post-hoc, fixed once before the cross-model transfer sweep started. Documented in `main/transfer_near_miss_analysis.py` and `papers/.../paper_body.tex`. |
| `α` / `q` (FDR)               |  0.05 | `packages/evaluator/.../constants.py:FDR_Q`; default in `evaluate_bundle` Benjamini–Hochberg step. | Pre-registered (standard). |
| `min_cells_per_hypothesis`    |  8    | `evaluation_protocol.yaml` for every released bundle. | Pre-registered. Power analysis target. |

The four thresholds discussed in detail below are the V1 stage-gate
overrides (`min_causal_effect`, `min_effect_floor`,
`min_specificity_ratio`) and the cross-model floor
(`CROSS_MODEL_EFFECT_FLOOR`).

## 2. Provenance: pre-hoc vs. post-hoc

We classify a threshold as **pre-hoc** if it was fixed before the relevant
acceptance counts were observed, and **post-hoc** if it was chosen after
inspecting any version of the acceptance histogram.

| Threshold                    | Provenance | Evidence                                                                                                |
|------------------------------|------------|---------------------------------------------------------------------------------------------------------|
| `min_causal_effect` ≥ 0.15   | pre-hoc    | First committed in `methodology/contract_hardening_v1_migration_decision.md` before the V1 rerun. The contract-hardening rerun was the first run that used these floors. |
| `min_effect_floor` ≥ 0.15    | pre-hoc    | Same commit as above; chosen equal to `min_causal_effect` so effect-on-confirmatory cannot dip below the discovery floor. |
| `min_specificity_ratio` ≥ 5.0| pre-hoc    | Same commit. Selected to enforce ≥5× separation between targeted and control conditions. |
| `CROSS_MODEL_EFFECT_FLOOR` = 0.02 | post-hoc | Chosen once after observing the absolute-effect distribution of the cross-model transfer sweep. The value was fixed before any transfer claim was published in the paper. **No iterative tuning** — selected at 2× the median noise floor and frozen. Documented in `methodology/targeted_transfer_rerun_preregistrations.md`. |
| `α` / `q` = 0.05             | pre-hoc    | Standard. |
| `min_cells_per_hypothesis` 8 | pre-hoc    | Power-analysis target written into the very first protocol template. |

## 3. Sensitivity (±10 / ±20 / ±50%)

> **Status (2026-05-06).** This section currently documents the
> sensitivity *protocol* but does not yet ship the per-perturbation
> acceptance counts. We deliberately do not fabricate numbers here:
> publishing illustrative tables that look empirical would be worse than
> a frank gap. The sweep is a deferred camera-ready item, listed in
> `methodology/blinded_holdout_protocol.md` and tracked in
> `EXECUTED_REMAINING_GAPS.md`.

### 3.1 What the sweep will measure

For each of the four thresholds in §1 we will hold the others fixed at
the V1 values, replay the released stage gates over the same 109-claim
universe, and emit the accepted-count (and, for
`CROSS_MODEL_EFFECT_FLOOR`, the transfer-confirmed count) at
perturbations `−50%`, `−20%`, `−10%`, V1, `+10%`, `+20%`, `+50%`.

This is a *gate-reanalysis* sensitivity, not a re-run sensitivity: we do
not regenerate cells (no new compute), we only re-evaluate the cached
cell tables under perturbed gates. The output is one machine-readable
JSON file per threshold under
`main/output/repro/threshold_sensitivity/` plus a single Markdown
roll-up.

### 3.2 What we already know (qualitatively)

* Acceptance under `min_causal_effect`, `min_effect_floor`, and
  `min_specificity_ratio` is **monotone non-increasing** in the
  threshold by construction (tightening a gate cannot accept more
  claims).
* `CROSS_MODEL_EFFECT_FLOOR` gates the *transfer* qualifier, not
  acceptance; perturbing it reshapes the transfer count, not the
  acceptance count.
* The currently-accepted set has been spot-checked against ±10%
  perturbations during contract-hardening development (see
  `methodology/contract_hardening_v1_migration_decision.md`); none of
  the ±10% perturbations of any single threshold flipped the headline
  by more than a small handful of claims.

### 3.3 What this section will become

Once the sweep ships, this section will be replaced with the
machine-generated tables (one row per perturbation, columns
`accepted`, `Δ`, plus 95% bootstrap CI) and a one-paragraph reading.
Until then, readers should treat the V1 thresholds as deliberately
chosen point estimates whose neighborhood has not been formally
characterized in the released artifact.

## 4. What this analysis does not establish

* **No real power analysis.** The cell counts (`min_cells_per_hypothesis
  = 8`) were chosen to give nominal 80% power against an effect of
  0.15 in logit-diff units under a two-sample permutation test, but we
  have not yet shipped the simulation backing that claim. Adding a real
  power analysis is a deferred camera-ready item (see
  `methodology/blinded_holdout_protocol.md`).
* **Pre-registration timestamps.** This file records that the V1
  thresholds were committed before the rerun that uses them, but the
  audit trail is **internal** — it is not a third-party-witnessed
  pre-registration. A public registry (e.g. OSF) is also a deferred
  camera-ready item.
* **Sensitivity is gate-reanalysis only.** We do not re-run cell
  collection at perturbed thresholds. A change to
  `min_cells_per_hypothesis` would require new compute and is not
  covered.

## 5. References

* `main/contract_hardening_v1.py` (V1 stage-gate overrides)
* `methodology/contract_hardening_v1_migration_decision.md` (the
  decision log).
* `packages/evaluator/src/automechinterp_evaluator/constants.py`
  (`CROSS_MODEL_EFFECT_FLOOR`, `FDR_Q`).
* `main/transfer_near_miss_analysis.py` (cross-model floor in action).
* `papers/submissions/neurips2026_dnb/paper_body.tex` §Methods (V1
  thresholds quoted).
