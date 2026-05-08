#!/usr/bin/env python3
"""Score the public AutoMechInterp contract against a privately-held bundle suite.

This is the operational-plumbing closure of the F-018 sub-item (the
"rehearsal" path described in
``docs/reference/open_item_blinded_holdout.md``). It is **not** the full
close of F-018: the full close requires (a) a real privately-held bundle
suite from an external collaborator, and (b) a versioning + rotation
policy demonstrated end-to-end. This script makes those follow-on steps
mechanical instead of conceptual.

The key contract enforced by this script is **aggregate-only output**.
The output JSON contains *only* counts and rates --- never per-claim
identifiers, per-bundle paths within the private suite, or anything else
that could leak the holdout's contents. This is the mechanism described
in the holdout governance plan
(``docs/reference/holdout_stress_governance_plan.md``) for the same
reason that other benchmarks use blinded leaderboards: per-item leakage
turns the holdout into just another public test set on the next release.

Usage:
    python main/run_holdout.py \
        --private-suite /path/to/private/bundles \
        --release-version v1.0 \
        --output main/output/repro/holdout_v1.0.json

Or with the rehearsal flag (when no real private suite exists yet):
    python main/run_holdout.py --rehearsal --release-version v0-rehearsal

The rehearsal mode treats the released ``main/output/real_multi_task/``
bundles as if they were a private suite. It is **not** scientifically
informative (the contract has already seen these bundles), but it does
exercise the entire plumbing end-to-end so that when a real private
suite arrives the only remaining question is "where is it on disk?".
The output JSON is clearly marked ``mode: rehearsal`` so that no
downstream consumer can mistake it for a real holdout score.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "packages" / "evaluator" / "src"))

from automechinterp_evaluator.evaluator import evaluate_bundle  # noqa: E402

try:
    from _bundle_analysis import _load_cached_or_evaluate_bundle, generated_at_utc
except ModuleNotFoundError:
    from main._bundle_analysis import _load_cached_or_evaluate_bundle, generated_at_utc

# Released-bundle directory used as the rehearsal placeholder.
REHEARSAL_SUITE = ROOT / "main" / "output" / "real_multi_task"


def _aggregate(suite_root: Path, *, use_cached_results: bool = False) -> dict[str, object]:
    """Score every bundle directory under ``suite_root`` against the
    released contract and return aggregate-only counts.

    A bundle directory is any sub-directory of ``suite_root`` containing
    the four required artifacts (``protocol.yaml``, ``hypothesis.jsonl``,
    ``evaluation_result.json``, ``manifest.json``). This matches the
    ``find_bundle_dirs`` discipline in ``_bundle_analysis.py``.

    When ``use_cached_results`` is true, prefer the bundle's current cached
    evaluator summary (or the released summary if it already has claim
    reports). This is appropriate for aggregate-only rehearsal plumbing
    where the goal is to exercise the reporting path without paying the full
    cost of re-scoring every visible bundle again.
    """
    n_bundles_seen = 0
    n_bundles_scored = 0
    n_bundles_failed = 0
    n_claims = 0
    n_accepted = 0
    tier_counts: dict[str, int] = {}
    if not suite_root.exists():
        raise FileNotFoundError(f"private suite root does not exist: {suite_root}")
    for sub in sorted(suite_root.iterdir()):
        if not sub.is_dir():
            continue
        if not (sub / "protocol.yaml").exists():
            continue
        if not (sub / "hypothesis.jsonl").exists():
            continue
        if not (sub / "evaluation_result.json").exists():
            continue
        n_bundles_seen += 1
        try:
            if use_cached_results:
                result = _load_cached_or_evaluate_bundle(sub)
            else:
                result = evaluate_bundle(sub)
        except Exception:
            # Aggregate-only: do NOT echo the exception text or the path.
            # An operator running this locally can re-invoke the
            # evaluator on the same private bundle directly to debug.
            n_bundles_failed += 1
            continue
        n_bundles_scored += 1
        for claim in result.get("claim_reports", []):
            n_claims += 1
            tier = claim.get("evidence_tier", "unknown")
            tier_counts[tier] = tier_counts.get(tier, 0) + 1
            if claim.get("passed"):
                n_accepted += 1

    return {
        "n_bundles_seen": n_bundles_seen,
        "n_bundles_scored": n_bundles_scored,
        "n_bundles_failed_to_evaluate": n_bundles_failed,
        "n_claims": n_claims,
        "n_accepted": n_accepted,
        "acceptance_rate": (n_accepted / n_claims) if n_claims > 0 else 0.0,
        "tier_counts": tier_counts,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n", 1)[0])
    parser.add_argument(
        "--private-suite",
        type=Path,
        help="Path to the privately-held bundle suite. Mutually exclusive with --rehearsal.",
    )
    parser.add_argument(
        "--rehearsal",
        action="store_true",
        help=(
            "Run against the released bundles under main/output/real_multi_task/ "
            "as a rehearsal of the plumbing. Output will be clearly marked "
            "mode=rehearsal and is NOT scientifically informative."
        ),
    )
    parser.add_argument(
        "--release-version",
        type=str,
        required=True,
        help="The released contract version that this scoring run is against (e.g. v1.0).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Path to write the aggregate-only JSON. Defaults to main/output/repro/holdout_<release_version>.json.",
    )
    parser.add_argument(
        "--use-cached-results",
        action="store_true",
        help=(
            "Prefer evaluation_result_current.json (or released summaries with claim_reports) when available. "
            "Useful for fast aggregate-only rehearsal runs; not a replacement for a real private-suite scoring pass."
        ),
    )
    args = parser.parse_args()

    if args.rehearsal == bool(args.private_suite):
        parser.error("Exactly one of --private-suite or --rehearsal must be supplied.")

    if args.rehearsal:
        suite_root = REHEARSAL_SUITE
        mode = "rehearsal"
    else:
        suite_root = args.private_suite.resolve()
        mode = "real"

    aggregate = _aggregate(suite_root, use_cached_results=args.use_cached_results)
    payload: dict[str, object] = {
        "schema_version": 1,
        "mode": mode,
        "release_version": args.release_version,
        "generated_at": generated_at_utc(timespec="microseconds"),
        "aggregate": aggregate,
        "policy": {
            "aggregate_only": True,
            "per_item_information_emitted": False,
            "private_suite_path_emitted": False,
            "see": "docs/reference/holdout_stress_governance_plan.md",
        },
        "scoring_mode": "cached_or_released_summary" if args.use_cached_results else "fresh_current_evaluator",
    }
    if mode == "rehearsal":
        payload["rehearsal_warning"] = (
            "This output is from rehearsal mode. The contract has already seen "
            "these bundles, so the score is NOT a measure of holdout-hardening. "
            "Do not cite this score in any paper as a holdout result."
        )
    if args.use_cached_results:
        payload["cached_results_warning"] = (
            "This run aggregated current/released summary artifacts when available. "
            "That is appropriate for fast plumbing rehearsal, but it is not a substitute for a fresh private-suite scoring pass."
        )

    output_path = args.output
    if output_path is None:
        output_path = ROOT / "main" / "output" / "repro" / f"holdout_{args.release_version}.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(str(output_path))


if __name__ == "__main__":
    main()
