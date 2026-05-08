#!/usr/bin/env python3
"""Forensic near-miss analysis of cross-model transfer evidence.

The historical transfer headline was 0/12 before paired-bundle replication
artifacts were added; the later country-capital-only 8/12 and
pre-prompt-promotion 9/26 states are now superseded by the current 12/26 mixed
transfer surface. This analyzer remains
useful because the unresolved tail is still informative rather than solved: it
projects the same
underlying data into a more compact form: for each tested accepted
claim, it reports the transfer effect's distance from the cross-model floor,
whether the direction matched the source model, and where the strongest
near-misses cluster.

Key derived quantities:

* ``floor_fraction`` -- ``|transfer_effect| / CROSS_MODEL_EFFECT_FLOOR``.
  A value of 1.0 means the claim sits exactly at the floor; 0.9 means 90% of
  the floor (one of the strongest near-misses); values << 1 mean the effect
  is far below the floor.
* ``transfer_status`` -- one of:
    - ``"confirmed"``: same direction and above floor (would be cross_model_confirmed).
    - ``"near_miss_below_floor"``: same direction, below floor (closest to confirmation).
    - ``"opposite_direction_subthreshold"``: opposite direction, magnitude below floor.
    - ``"opposite_direction_above_floor"``: opposite direction, magnitude above floor
      (a stronger negative result -- the claim transfers but in the *opposite* direction).
* ``transfer_asymmetry`` -- per (source_model, transfer_model) ordered pair, the
  fraction of accepted claims that share the source direction and the median
  ``floor_fraction``. This surfaces directional asymmetries (e.g., pythia→gpt2
  may be much more consistent than gpt2→pythia).

The analyzer reads only ``main/output/repro/transfer_results_summary.json``
(which is itself derived from the ``cross_model_results.json`` and
``evaluation_result.json`` produced by the evaluator) plus the per-claim
``cross_model_same_direction`` and ``cross_model_above_floor`` metrics
recovered via :mod:`main._bundle_analysis`. It does not change any underlying
ground truth; it re-projects the same raw transfer information.

Outputs:

* ``main/output/repro/transfer_near_miss_analysis.json``
* ``main/output/repro/transfer_near_miss_analysis.md``
"""

from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from main._bundle_analysis import (  # noqa: E402
    REAL_MULTILANE_DIR,
    REAL_MULTI_TASK_DIR,
    evaluate_bundle_records,
    find_bundle_dirs,
    iter_claim_rows,
)

# Source of truth: the evaluator constant. Imported here so the analyzer
# automatically tracks any future floor change.
from automechinterp_evaluator.constants import CROSS_MODEL_EFFECT_FLOOR  # noqa: E402

REPRO_DIR = ROOT / "main" / "output" / "repro"


def _classify(effect: float, same_dir: bool, above_floor: bool) -> str:
    if same_dir and above_floor:
        return "confirmed"
    if same_dir and not above_floor:
        return "near_miss_below_floor"
    if not same_dir and above_floor:
        return "opposite_direction_above_floor"
    return "opposite_direction_subthreshold"


def collect_transfer_records() -> list[dict[str, Any]]:
    """Return one record per accepted claim that has a cross-model effect.

    The record is restricted to *accepted* claims because the cross-model
    transfer gate is only meaningful for those. Rejected claims that
    happen to have a cross-model effect are useful for context but are
    not the subject of the released accepted-claim transfer headline.
    """
    records = evaluate_bundle_records(REAL_MULTI_TASK_DIR, REAL_MULTILANE_DIR, use_cached_results=True)
    bundle_by_name = {
        bundle.name: bundle
        for bundle in find_bundle_dirs(REAL_MULTI_TASK_DIR, REAL_MULTILANE_DIR)
    }
    rows = iter_claim_rows(records)
    transfer_records: list[dict[str, Any]] = []
    for row in rows:
        metrics = row.get("metrics", {})
        if "cross_model_transfer_effect" not in metrics:
            continue
        transfer_model = None
        transfer_n_examples = None
        transfer_mapping_version = None
        transfer_artifact = bundle_by_name.get(row["bundle"], Path()) / "cross_model_results.json"
        if transfer_artifact.exists():
            for transfer_row in json.loads(transfer_artifact.read_text()):
                if transfer_row.get("hypothesis_id") == row["hypothesis_id"]:
                    transfer_model = transfer_row.get("transfer_model")
                    transfer_n_examples = transfer_row.get("n_examples")
                    transfer_mapping_version = transfer_row.get("transfer_mapping_version")
                    break
        if not row["passed"]:
            # Keep the data on the side for context but tag it.
            included = False
        else:
            included = True
        effect = float(metrics["cross_model_transfer_effect"])
        same_dir = bool(metrics.get("cross_model_same_direction", False))
        above_floor = bool(metrics.get("cross_model_above_floor", False))
        transfer_records.append(
            {
                "task": row["task"],
                "source_model": row["model"],
                "transfer_model": transfer_model,
                "transfer_n_examples": transfer_n_examples,
                "transfer_mapping_version": transfer_mapping_version,
                "bundle": row["bundle"],
                "hypothesis_id": row["hypothesis_id"],
                "transfer_effect": effect,
                "same_direction_as_source": same_dir,
                "above_floor": above_floor,
                "floor_fraction": abs(effect) / CROSS_MODEL_EFFECT_FLOOR,
                "transfer_status": _classify(effect, same_dir, above_floor),
                "evidence_tier": row["evidence_tier"],
                "discovery_lane": row["discovery_lane"],
                "is_accepted_claim": included,
            }
        )
    return transfer_records


def summarize_pairs(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Group accepted-claim transfer evidence by (source, target) pair."""
    accepted = [r for r in records if r["is_accepted_claim"]]
    pair_buckets: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for r in accepted:
        target = r.get("transfer_model") or "unknown"
        pair_buckets.setdefault((r["source_model"], target), []).append(r)

    pair_summary = []
    for (src, tgt), bucket in sorted(pair_buckets.items()):
        directions_correct = sum(1 for r in bucket if r["same_direction_as_source"])
        floor_fractions = [r["floor_fraction"] for r in bucket]
        pair_summary.append(
            {
                "source_model": src,
                "transfer_model": tgt,
                "n_claims": len(bucket),
                "n_correct_direction": directions_correct,
                "fraction_correct_direction": directions_correct / len(bucket),
                "median_floor_fraction": statistics.median(floor_fractions),
                "max_floor_fraction": max(floor_fractions),
                "min_floor_fraction": min(floor_fractions),
                "n_confirmed": sum(1 for r in bucket if r["transfer_status"] == "confirmed"),
                "n_near_miss_below_floor": sum(
                    1 for r in bucket if r["transfer_status"] == "near_miss_below_floor"
                ),
            }
        )
    return {"pairs": pair_summary}


def build_analysis() -> dict[str, Any]:
    records = collect_transfer_records()
    accepted = [r for r in records if r["is_accepted_claim"]]
    accepted_sorted = sorted(
        accepted,
        key=lambda r: (
            -int(r["same_direction_as_source"]),
            -r["floor_fraction"],
        ),
    )
    near_misses = [r for r in accepted_sorted if r["transfer_status"] == "near_miss_below_floor"]

    pair_summary = summarize_pairs(records)

    # Headline asymmetry: which (source, target) pair has the strongest
    # consistent-direction near-miss median? This is the pair where another
    # discovery iteration would have the highest a-priori chance of crossing
    # the cross-model floor.
    best_pair = None
    if pair_summary["pairs"]:
        best_pair = max(
            pair_summary["pairs"],
            key=lambda p: (p["fraction_correct_direction"], p["median_floor_fraction"]),
        )

    payload = {
        "cross_model_floor": CROSS_MODEL_EFFECT_FLOOR,
        "n_accepted_claims_with_transfer": len(accepted),
        "n_confirmed": sum(1 for r in accepted if r["transfer_status"] == "confirmed"),
        "n_near_miss_below_floor": sum(
            1 for r in accepted if r["transfer_status"] == "near_miss_below_floor"
        ),
        "n_opposite_direction_subthreshold": sum(
            1 for r in accepted if r["transfer_status"] == "opposite_direction_subthreshold"
        ),
        "n_opposite_direction_above_floor": sum(
            1 for r in accepted if r["transfer_status"] == "opposite_direction_above_floor"
        ),
        "closest_near_miss": near_misses[0] if near_misses else None,
        "top_5_near_misses": near_misses[:5],
        "transfer_asymmetry": pair_summary,
        "highest_consistency_pair": best_pair,
        "all_accepted_claim_transfers": accepted_sorted,
    }
    return payload


def format_md(payload: dict[str, Any]) -> str:
    lines = [
        "# Cross-Model Transfer Near-Miss Forensics",
        "",
        f"- Cross-model floor (`CROSS_MODEL_EFFECT_FLOOR`): **{payload['cross_model_floor']}**",
        f"- Accepted claims with transfer evidence: **{payload['n_accepted_claims_with_transfer']}**",
        f"- Cross-model confirmed: **{payload['n_confirmed']}**",
        f"- Same-direction near-misses (below floor): **{payload['n_near_miss_below_floor']}**",
        f"- Opposite-direction subthreshold: **{payload['n_opposite_direction_subthreshold']}**",
        f"- Opposite-direction above floor: **{payload['n_opposite_direction_above_floor']}**",
        "",
        "## Closest near-miss",
        "",
    ]
    cnm = payload.get("closest_near_miss")
    if cnm:
        lines.extend(
            [
                f"- Bundle: `{cnm['bundle']}`",
                f"- Hypothesis: `{cnm['hypothesis_id']}`",
                f"- Source → transfer effect: **{cnm['transfer_effect']:+.6f}**",
                f"- Transfer examples: **{cnm.get('transfer_n_examples') or 'unknown'}**",
                f"- Floor fraction: **{cnm['floor_fraction'] * 100:.1f}%** of the {payload['cross_model_floor']} floor",
                f"- Same direction as source: **{cnm['same_direction_as_source']}**",
                "",
                "This is the unresolved accepted released claim that is closest to satisfying"
                " the cross-model transfer gate. It has already been preregistered and"
                " rerun at n=200, where it stayed same-direction but below the frozen"
                " floor. The current interpretation is therefore not \"missing run\" or"
                " obvious sampling noise; it is a persistent below-floor tail case under"
                " the released mapping and threshold. Further reruns should require a"
                " new preregistered rationale rather than being repeated until lucky.",
                "",
            ]
        )
    else:
        lines.extend(["- No same-direction near-misses below the floor.", ""])

    lines.extend(["## Top 5 same-direction near-misses", "",
                  "| bundle | hypothesis | effect | floor fraction |",
                  "|---|---|---|---|"])
    for r in payload["top_5_near_misses"]:
        lines.append(
            f"| `{r['bundle']}` | `{r['hypothesis_id']}` | "
            f"{r['transfer_effect']:+.6f} | {r['floor_fraction'] * 100:.1f}% |"
        )
    lines.append("")

    lines.extend(["## Direction-and-magnitude asymmetry by (source, target)", "",
                  "| source | target | n | correct dir | median floor frac | max floor frac |",
                  "|---|---|---|---|---|---|"])
    for p in payload["transfer_asymmetry"]["pairs"]:
        lines.append(
            f"| {p['source_model']} | {p['transfer_model']} | {p['n_claims']} | "
            f"{p['n_correct_direction']}/{p['n_claims']} | "
            f"{p['median_floor_fraction'] * 100:.1f}% | {p['max_floor_fraction'] * 100:.1f}% |"
        )
    lines.append("")

    if payload.get("highest_consistency_pair"):
        bp = payload["highest_consistency_pair"]
        lines.extend(
            [
                "## Most consistent transfer direction",
                "",
                f"- {bp['source_model']} → {bp['transfer_model']}: "
                f"{bp['n_correct_direction']}/{bp['n_claims']} accepted claims share the "
                f"source direction; median floor fraction {bp['median_floor_fraction'] * 100:.1f}% "
                f"(max {bp['max_floor_fraction'] * 100:.1f}%).",
                "",
                "This pair is where the unresolved data most plausibly extrapolates to an"
                " additional cross-model-confirmed result. This should not be generalized"
                " beyond the paired-bundle country-capital-heavy evidence currently in the"
                " release; it means future discovery-side work targeted at this pair has"
                " the highest a-priori chance of crossing the floor without changing the"
                " contract.",
                "",
            ]
        )

    lines.extend(["## All accepted-claim transfer evidence", "",
                  "| bundle | hypothesis | effect | same dir | above floor | status |",
                  "|---|---|---|---|---|---|"])
    for r in payload["all_accepted_claim_transfers"]:
        lines.append(
            f"| `{r['bundle']}` | `{r['hypothesis_id']}` | "
            f"{r['transfer_effect']:+.6f} | {r['same_direction_as_source']} | "
            f"{r['above_floor']} | `{r['transfer_status']}` |"
        )

    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    REPRO_DIR.mkdir(parents=True, exist_ok=True)
    payload = build_analysis()
    out_json = REPRO_DIR / "transfer_near_miss_analysis.json"
    out_md = REPRO_DIR / "transfer_near_miss_analysis.md"
    out_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    out_md.write_text(format_md(payload))
    print(str(out_json))


if __name__ == "__main__":
    main()
