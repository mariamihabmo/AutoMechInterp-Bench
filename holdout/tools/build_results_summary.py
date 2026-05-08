"""Custodian: aggregate holdout submission results into ``results_summary.json``.

Walks ``holdout/submissions/`` (external_blinded slot) and
``holdout/pilot/submissions/`` (maintainer_pilot slot), pairs each
submission with its corresponding entry under ``holdout/results/`` or
``holdout/pilot/results/``, and writes a top-level summary that keeps
the two slices cleanly separated.

The summary is designed so a reviewer can tell at a glance:

* how many external_blinded submissions have been received (always a
  strict count, never conflated with pilots);
* how many maintainer_pilot submissions exist (scaffolding-only, never
  evidence);
* whether every evaluated submission matched the pinned contract hash.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


REPO_ROOT = Path(__file__).resolve().parents[2]
HOLDOUT_ROOT = REPO_ROOT / "holdout"


def _generated_at_utc() -> str:
    """ISO-8601 UTC timestamp honoring ``SOURCE_DATE_EPOCH`` for reproducible builds.

    Custodians who re-run ``build_results_summary`` for an integrity audit can
    pin the embedded timestamp via the ``SOURCE_DATE_EPOCH`` environment
    variable; the resulting ``results_summary.json`` is then byte-identical to
    the canonical artifact as long as the underlying submission/result tree is
    unchanged. See 
    """
    raw = os.environ.get("SOURCE_DATE_EPOCH")
    if raw:
        try:
            return datetime.fromtimestamp(int(raw), tz=timezone.utc).isoformat(timespec="seconds")
        except (TypeError, ValueError):
            pass
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _relpath(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def _collect_slice(submissions_dir: Path, results_dir: Path) -> List[Dict[str, Any]]:
    """Collect per-submission records for a single slice (external or pilot)."""

    records: List[Dict[str, Any]] = []
    if not submissions_dir.exists():
        return records
    for sub in sorted(submissions_dir.iterdir()):
        if not sub.is_dir():
            continue
        record: Dict[str, Any] = {
            "submission_id": sub.name,
            "submission_dir": _relpath(sub),
            "status": "unevaluated",
        }
        attestation = sub / "attestation.json"
        if attestation.exists():
            try:
                att = json.loads(attestation.read_text())
                record["submission_kind"] = att.get("submission_kind")
                record["author_institution"] = att.get("author_institution")
                record["submitted_at_utc"] = att.get("submitted_at_utc")
            except json.JSONDecodeError:
                record["attestation_parse_error"] = True

        review_path = results_dir / sub.name / "submission_review.json"
        if review_path.exists():
            review = json.loads(review_path.read_text())
            record.update(
                {
                    "status": "evaluated",
                    "contract_pin_match": review.get("contract_pin_match"),
                    "evaluator_version": review.get("evaluator_version"),
                    "evaluated_at_utc": review.get("evaluated_at_utc"),
                    "n_claims": review.get("n_claims"),
                    "n_accepted_claims": review.get("n_accepted_claims"),
                    "bundle_tarball_sha256": review.get("bundle_tarball_sha256"),
                    # propagate signature
                    # verification status so external-evidence aggregation can
                    # exclude unverified or skipped-signature submissions.
                    "signature_verified": review.get("signature_verified"),
                    "signature_status": review.get("signature_status"),
                }
            )
        records.append(record)
    return records


def build_summary() -> Dict[str, Any]:
    external = _collect_slice(HOLDOUT_ROOT / "submissions", HOLDOUT_ROOT / "results")
    pilot = _collect_slice(
        HOLDOUT_ROOT / "pilot" / "submissions", HOLDOUT_ROOT / "pilot" / "results"
    )

    # Invariants the audit relies on.
    for rec in external:
        kind = rec.get("submission_kind")
        if kind is not None and kind != "external_blinded":
            raise ValueError(
                f"submission {rec['submission_id']!r} is under holdout/submissions/ "
                f"but attests submission_kind={kind!r}; external slot must only contain "
                "external_blinded submissions."
            )
    for rec in pilot:
        kind = rec.get("submission_kind")
        if kind is not None and kind != "maintainer_pilot":
            raise ValueError(
                f"submission {rec['submission_id']!r} is under holdout/pilot/submissions/ "
                f"but attests submission_kind={kind!r}; pilot slot must only contain "
                "maintainer_pilot submissions."
            )

    evaluated_external = [r for r in external if r["status"] == "evaluated"]
    evaluated_pilot = [r for r in pilot if r["status"] == "evaluated"]
    # a submission whose signature is not
    # cryptographically verified (skipped via --skip-signature, missing, or
    # rejected) MUST NOT contribute to the public ``n_accepted_claims`` count
    # for external evidence. We expose both the verified-only count and the
    # full evaluated set so reviewers can see exactly which submissions were
    # held back.
    verified_external = [
        r for r in evaluated_external if bool(r.get("signature_verified"))
    ]
    unverified_external = [
        r for r in evaluated_external if not bool(r.get("signature_verified"))
    ]

    summary: Dict[str, Any] = {
        "generated_at_utc": _generated_at_utc(),
        "policy_note": (
            "external_blinded submissions are the only slice that counts as external "
            "evidence per methodology/blinded_holdout_protocol.md. maintainer_pilot "
            "submissions exist solely to exercise the Custodian pipeline and are NEVER "
            "included in external-evidence counts."
        ),
        "external_blinded": {
            "n_submissions": len(external),
            "n_evaluated": len(evaluated_external),
            "n_signature_verified": len(verified_external),
            "n_signature_unverified": len(unverified_external),
            "unverified_submission_ids": [r["submission_id"] for r in unverified_external],
            "n_accepted_claims": sum(
                int(r.get("n_accepted_claims") or 0) for r in verified_external
            ),
            "n_accepted_claims_includes_unverified": False,
            "all_pin_matches": all(
                bool(r.get("contract_pin_match")) for r in evaluated_external
            )
            if evaluated_external
            else None,
            "submissions": external,
        },
        "maintainer_pilot": {
            "n_submissions": len(pilot),
            "n_evaluated": len(evaluated_pilot),
            "all_pin_matches": all(bool(r.get("contract_pin_match")) for r in evaluated_pilot)
            if evaluated_pilot
            else None,
            "submissions": pilot,
        },
    }
    return summary


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument(
        "--output",
        type=Path,
        default=HOLDOUT_ROOT / "results_summary.json",
        help="Path to write the top-level summary JSON.",
    )
    p.add_argument(
        "--pilot-output",
        type=Path,
        default=HOLDOUT_ROOT / "pilot" / "results_summary.json",
        help="Path to write the pilot-only summary JSON (same shape, pilot slice only).",
    )
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    summary = build_summary()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    pilot_only = {
        "generated_at_utc": summary["generated_at_utc"],
        "policy_note": summary["policy_note"],
        "maintainer_pilot": summary["maintainer_pilot"],
    }
    args.pilot_output.parent.mkdir(parents=True, exist_ok=True)
    args.pilot_output.write_text(json.dumps(pilot_only, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "external_blinded": {
                    "n_submissions": summary["external_blinded"]["n_submissions"],
                    "n_evaluated": summary["external_blinded"]["n_evaluated"],
                    "n_accepted_claims": summary["external_blinded"]["n_accepted_claims"],
                },
                "maintainer_pilot": {
                    "n_submissions": summary["maintainer_pilot"]["n_submissions"],
                    "n_evaluated": summary["maintainer_pilot"]["n_evaluated"],
                },
                "summary_json": _relpath(args.output),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
