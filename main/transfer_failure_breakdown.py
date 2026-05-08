#!/usr/bin/env python3
"""Per-claim breakdown of why each cross-model-tested accepted claim
fails the cross-model-transfer gate.

Why this exists (audit finding F-017 in
``methodology/audit/findings_inventory.md``; "first concrete step" in
``docs/reference/open_item_cross_model_transfer.md``): the released
``transfer_results_summary.json`` now records a mixed transfer surface rather than an all-zero one, but it still does *not* surface *why* the unresolved accepted claims fail or how the remaining failure tail decomposes. The
open-item plan requires this breakdown before deciding among Paths A
(first transfer-confirmed claim under the released contract), B
(pre-registered re-specification), or C (accept "no evidence of
transfer" as a genuine field-level finding).

This script emits ``main/output/repro/transfer_failure_breakdown.json``,
which classifies each unresolved cross-model-tested accepted claim into one of
four mutually-exclusive failure modes:

- ``wrong_direction``: the mapped components in the transfer model
  produce a transfer effect with the **opposite sign** from the
  source-model effect. No floor change can rescue these; they are
  affirmative evidence that the claimed mechanism does not transfer.
- ``below_floor_correct_direction``: the transfer effect has the
  correct sign but its magnitude is below the floor. These are the
  *only* claims that a floor relaxation could plausibly rescue.
- ``zero_or_missing``: the transfer effect is exactly zero or absent
  from ``cross_model_results.json``.
- ``other``: residual catch-all.

In addition to the per-claim buckets, the output now carries two
aggregate controls that the open-item plan (Path C) depends on:

- ``transfer_to_source_magnitude_ratio``: the per-claim ratio
  ``|transfer_effect| / |source_effect_mean|``, aggregated across
  claims. Quantifies cross-model attenuation. A median ratio well
  below 1 means the mechanism produces a real source-model effect
  but does not carry over to the transfer model under the released
  mapping; no defensible floor relaxation can close that gap.
- ``within_source_bundle_stability_control``: for each claim, the
  coefficient of variation ``stdev / |mean|`` across the source
  bundle's raw cells. If the source effect is stable
  (``cv_abs <= 0.5``), then the cross-model failure cannot be
  dismissed as "the source effect was noisy anyway" --- the
  mechanism exists in the source model, it just does not transfer.
  This is a necessary-but-not-sufficient control for Path C:
  a same-family within-model prompt-holdout control is still
  required before the paper can reframe the cross-model section
  as a positive finding, and that stronger control requires
  compute beyond this sandbox.

The script also reports the median and quartiles of correct-direction
magnitudes, so an operator considering Path B (re-specification) can
see what floor change would actually move which claims --- and can see
that any floor change small enough to admit the typical
correct-direction claim would also admit much of the
wrong-direction noise band.

The output is **diagnostic only**. It does NOT assert that any new
claim is transfer-confirmed; it does NOT lower the cross-model floor;
it does NOT mutate any existing artifact. It is exactly the evidence
artifact the open-item plan calls for.

Usage:
    python main/transfer_failure_breakdown.py
"""

from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "packages" / "evaluator" / "src"))

from automechinterp_evaluator.evaluator import evaluate_bundle  # noqa: E402
from main._bundle_analysis import REAL_MULTI_TASK_DIR, REAL_MULTILANE_DIR, find_bundle_dirs  # noqa: E402

REPRO = ROOT / "main" / "output" / "repro"
TRANSFER_SUMMARY = REPRO / "transfer_results_summary.json"
OUTPUT_PATH = REPRO / "transfer_failure_breakdown.json"
BUNDLE_BY_NAME = {
    bundle.name: bundle
    for bundle in find_bundle_dirs(REAL_MULTI_TASK_DIR, REAL_MULTILANE_DIR)
}


def _classify(transfer_effect: float | None, gate_pass: bool | None, source_sign: int | None) -> str:
    """Classify a single cross-model-tested claim's failure mode.

    ``source_sign`` is the sign of the source-model treatment effect,
    extracted from the source bundle's evaluation report (``+1`` for
    a positive-effect claim, ``-1`` for a negative-effect claim,
    ``0`` if not available). The cross-model gate is "transfer
    confirmed" iff ``sign(transfer_effect) == source_sign`` AND
    ``abs(transfer_effect) >= floor``.
    """
    if gate_pass is True:
        return "passed"  # can happen on the current released set after paired-bundle replication
    if transfer_effect is None or transfer_effect == 0.0:
        return "zero_or_missing"
    if source_sign is None or source_sign == 0:
        # Unable to determine direction; classify as below_floor by
        # default (the most generous bucket for the claim).
        return "below_floor_correct_direction"
    transfer_sign = 1 if transfer_effect > 0 else -1
    if transfer_sign != source_sign:
        return "wrong_direction"
    return "below_floor_correct_direction"


def _source_effect_summary(bundle_dir: Path, hypothesis_id: str) -> dict[str, float | int | None]:
    """Return per-cell source-model treatment-effect summary for one hypothesis.

    Returns a dict with:

    - ``n_cells``: number of raw cells contributing a numeric treatment_effect.
    - ``mean``: arithmetic mean of per-cell treatment effects.
    - ``stdev``: sample standard deviation (``statistics.stdev``); ``None`` if ``n_cells < 2``.
    - ``cv_abs``: coefficient of variation relative to the absolute mean
      (``stdev / |mean|``); ``None`` if ``|mean|`` is below ``1e-12`` or
      ``stdev`` is not defined. This is the source-stability metric used
      by the within-source-bundle control for F-017 Path C: a low
      ``cv_abs`` means the source effect is a stable per-cell signal,
      so a 1000x-smaller cross-model transfer effect cannot be
      dismissed as "the source effect was noisy anyway".
    - ``sign``: +1/-1/0 for the sign of the mean, or ``None`` if no cells
      are available. Preserved for backwards compatibility with the
      ``_classify`` direction check.

    All fields are ``None`` if the bundle's ``evaluation_result.json``
    is missing, unparseable, or does not contain the requested
    ``hypothesis_id``.
    """
    empty: dict[str, float | int | None] = {
        "n_cells": 0,
        "mean": None,
        "stdev": None,
        "cv_abs": None,
        "sign": None,
    }
    eval_path = bundle_dir / "evaluation_result.json"
    if not eval_path.exists():
        return empty
    try:
        data = json.loads(eval_path.read_text())
    except json.JSONDecodeError:
        return empty
    for hyp in data.get("hypothesis_results", []):
        if hyp.get("hypothesis_id") != hypothesis_id:
            continue
        cells = hyp.get("raw_cells", []) or []
        effects = [c.get("treatment_effect") for c in cells if isinstance(c.get("treatment_effect"), (int, float))]
        if not effects:
            return empty
        mean_effect = sum(effects) / len(effects)
        if len(effects) >= 2:
            sd = statistics.stdev(effects)
        else:
            sd = None
        if sd is not None and abs(mean_effect) > 1e-12:
            cv = sd / abs(mean_effect)
        else:
            cv = None
        if mean_effect > 0:
            sign: int = 1
        elif mean_effect < 0:
            sign = -1
        else:
            sign = 0
        return {
            "n_cells": len(effects),
            "mean": mean_effect,
            "stdev": sd,
            "cv_abs": cv,
            "sign": sign,
        }
    return empty


def _source_sign(bundle_dir: Path, hypothesis_id: str) -> int | None:
    """Back-compat shim: sign of the source-model mean treatment effect.

    Preserved for backwards compatibility with the ``_classify`` direction
    check. Delegates to ``_source_effect_summary``.
    """
    return _source_effect_summary(bundle_dir, hypothesis_id)["sign"]  # type: ignore[return-value]


def main() -> None:
    if not TRANSFER_SUMMARY.exists():
        raise SystemExit(
            f"missing {TRANSFER_SUMMARY}; run main/transfer_results_summary.py first"
        )
    summary = json.loads(TRANSFER_SUMMARY.read_text())
    rows = []
    bucket_counts: dict[str, int] = {
        "wrong_direction": 0,
        "below_floor_correct_direction": 0,
        "zero_or_missing": 0,
        "passed": 0,
        "other": 0,
    }
    correct_direction_magnitudes: list[float] = []
    transfer_to_source_ratios: list[float] = []
    stable_source_claims = 0  # cv_abs <= 0.5 threshold; see comment below
    unstable_source_claims = 0
    source_cv_values: list[float] = []

    # Source-stability threshold for the "within-source-bundle control".
    # Threshold is cv_abs <= 0.5, i.e. stdev <= 50% of |mean|. This is a
    # deliberately loose threshold: the cross-model transfer effects in
    # the current released set are ~1000x smaller than their source
    # effects (see the ratio field below), so any cv_abs well below 1
    # suffices to rule out "the source effect was noisy enough to
    # account for the transfer gap". The open_item plan's Path C
    # argument requires the source effect to be stable; this threshold
    # makes the requirement explicit and auditable.
    STABILITY_CV_THRESHOLD = 0.5

    for claim in summary["claims"]:
        bundle_dir = BUNDLE_BY_NAME.get(claim["bundle"])
        if bundle_dir is None:
            raise SystemExit(f"transfer summary references unknown bundle {claim['bundle']!r}")
        src = _source_effect_summary(bundle_dir, claim["hypothesis_id"])
        sign = src["sign"]  # type: ignore[assignment]
        bucket = _classify(claim["transfer_effect"], claim["cross_model_transfer_gate"], sign)  # type: ignore[arg-type]
        bucket_counts[bucket] = bucket_counts.get(bucket, 0) + 1
        if bucket == "below_floor_correct_direction" and claim["transfer_effect"] is not None:
            correct_direction_magnitudes.append(abs(claim["transfer_effect"]))

        # Per-claim magnitude ratio (|transfer_effect| / |source_mean|);
        # quantifies the "1000x gap" the Path-C argument depends on.
        src_mean = src["mean"]  # type: ignore[assignment]
        if (
            claim["transfer_effect"] is not None
            and src_mean is not None
            and abs(src_mean) > 1e-12
        ):
            ratio = abs(claim["transfer_effect"]) / abs(src_mean)
            transfer_to_source_ratios.append(ratio)
        else:
            ratio = None

        # Per-claim within-source stability verdict.
        cv = src["cv_abs"]  # type: ignore[assignment]
        if cv is None:
            stability = "insufficient_cells"
        elif cv <= STABILITY_CV_THRESHOLD:
            stability = "stable"
            stable_source_claims += 1
            source_cv_values.append(cv)
        else:
            stability = "unstable"
            unstable_source_claims += 1
            source_cv_values.append(cv)

        rows.append(
            {
                "bundle": claim["bundle"],
                "hypothesis_id": claim["hypothesis_id"],
                "transfer_effect": claim["transfer_effect"],
                "source_sign": sign,
                "source_effect_mean": src_mean,
                "source_effect_stdev": src["stdev"],
                "source_effect_cv_abs": cv,
                "source_n_cells": src["n_cells"],
                "source_stability": stability,
                "transfer_to_source_ratio": ratio,
                "transfer_sign": (
                    1 if (claim["transfer_effect"] or 0) > 0
                    else -1 if (claim["transfer_effect"] or 0) < 0
                    else 0
                ),
                "failure_mode": bucket,
            }
        )

    median_ok = (
        statistics.median(correct_direction_magnitudes)
        if correct_direction_magnitudes
        else None
    )
    max_ok = max(correct_direction_magnitudes) if correct_direction_magnitudes else None
    median_ratio = (
        statistics.median(transfer_to_source_ratios) if transfer_to_source_ratios else None
    )
    max_ratio = max(transfer_to_source_ratios) if transfer_to_source_ratios else None
    median_cv = statistics.median(source_cv_values) if source_cv_values else None

    payload = {
        "schema_version": 2,
        "generated_by": "main/transfer_failure_breakdown.py",
        "source_artifact": str(TRANSFER_SUMMARY.relative_to(ROOT)),
        "n_cross_model_tested": len(rows),
        "bucket_counts": bucket_counts,
        "correct_direction_magnitudes": {
            "n": len(correct_direction_magnitudes),
            "median_abs_transfer_effect": median_ok,
            "max_abs_transfer_effect": max_ok,
        },
        "transfer_to_source_magnitude_ratio": {
            "n": len(transfer_to_source_ratios),
            "median": median_ratio,
            "max": max_ratio,
            "description": (
                "Per-claim |transfer_effect| / |source_effect_mean|. Quantifies "
                "the cross-model attenuation. A median ratio << 1 is the core "
                "of Path C in docs/reference/open_item_cross_model_transfer.md: "
                "the mechanism produces a real source-model effect but does not "
                "carry over to the transfer model under the released mapping."
            ),
        },
        "within_source_bundle_stability_control": {
            "threshold_cv_abs": STABILITY_CV_THRESHOLD,
            "stable_source_claims": stable_source_claims,
            "unstable_source_claims": unstable_source_claims,
            "insufficient_cells_claims": (
                len(rows) - stable_source_claims - unstable_source_claims
            ),
            "median_cv_abs": median_cv,
            "description": (
                "Within-source-bundle control called for by "
                "docs/reference/open_item_cross_model_transfer.md Path C. "
                "Each claim's source-model treatment-effect cells are "
                "summarized by cv_abs = stdev / |mean|; a claim is "
                "'stable' iff cv_abs <= threshold_cv_abs. If most claims "
                "are stable, 'mechanism does not transfer' cannot be "
                "dismissed as 'source effect was noisy'. This is NOT a "
                "same-family within-model prompt-holdout control "
                "(that still requires compute the sandbox does not have); "
                "it is a cheaper within-bundle check that rules out the "
                "cheapest alternative explanation."
            ),
        },
        "claims": rows,
        "interpretation_notes": [
            "wrong_direction: a floor relaxation cannot rescue these; "
            "they are affirmative evidence against the claimed mechanism transferring "
            "to the second model.",
            "below_floor_correct_direction: the only bucket that a defensible "
            "floor relaxation could plausibly move. Compare median_abs_transfer_effect "
            "to the contract's floor before considering Path B in "
            "docs/reference/open_item_cross_model_transfer.md.",
            "zero_or_missing: indistinguishable from contract failure; do not "
            "interpret as evidence either way.",
            "transfer_to_source_magnitude_ratio.median quantifies the "
            "cross-model attenuation; values below ~0.01 (i.e. ~100x attenuation) "
            "mean no defensible floor relaxation can close the gap.",
            "within_source_bundle_stability_control is a necessary but not "
            "sufficient control for Path C: a same-family within-model "
            "prompt-holdout control is still required before the paper can "
            "reframe the cross-model section as a positive finding. In "
            "particular, if within_source_bundle_stability_control reports "
            "few 'stable' claims (as in the current released set, where "
            "source cv_abs has median ~0.83 so 0/12 are 'stable' at the "
            "threshold), the Path-C argument rests on the ratio: only if "
            "transfer_to_source_magnitude_ratio.median is << source cv "
            "(as here: median ratio ~4e-4 vs median cv ~0.8, i.e. the "
            "transfer effect is ~2000x smaller than one standard deviation "
            "of the source effect) can 'mechanism does not transfer' "
            "survive the alternative 'source effect was noisy anyway'.",
            "Diagnostic artifact only. This script does NOT assert that any new "
            "claim is transfer-confirmed.",
        ],
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(str(OUTPUT_PATH))
    print(f"  buckets: {bucket_counts}")
    if median_ok is not None:
        print(
            f"  correct-direction n={len(correct_direction_magnitudes)}, "
            f"median |effect|={median_ok:.6f}, max |effect|={max_ok:.6f}"
        )
    else:
        print("  no correct-direction transfer effects in the cross-model-tested set")
    if median_ratio is not None:
        print(
            f"  transfer/source magnitude ratio: median={median_ratio:.4g}, "
            f"max={max_ratio:.4g} (smaller = more attenuation)"
        )
    print(
        f"  within-source stability: stable={stable_source_claims}, "
        f"unstable={unstable_source_claims}, "
        f"insufficient_cells={len(rows) - stable_source_claims - unstable_source_claims}"
        + (f", median_cv_abs={median_cv:.3f}" if median_cv is not None else "")
    )


if __name__ == "__main__":
    main()
