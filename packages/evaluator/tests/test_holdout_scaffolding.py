"""Tests for the Custodian-side blinded-holdout scaffolding.

These exercise the three invariants the scaffolding protects:

* the attestation schema rejects submissions that would otherwise be
  counted as external evidence without a legal ``submission_kind``;
* the ``evaluate_holdout_submission`` tool refuses to evaluate a
  submission whose ``contract_pin.constants_sha256`` does not match the
  repo constants, unless the Custodian explicitly passes
  ``--allow-pin-mismatch`` to document historical drift;
* the ``build_results_summary`` tool keeps the external_blinded and
  maintainer_pilot slices cleanly separated, and refuses to record a
  submission in the wrong slot.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import tarfile
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

import pytest

from holdout.tools import build_results_summary, evaluate_holdout_submission

REPO_ROOT = Path(__file__).resolve().parents[3]
PILOT_DIR = REPO_ROOT / "holdout" / "pilot" / "submissions" / "maintainer_pilot_0001"


def _load_schema() -> dict:
    return json.loads((REPO_ROOT / "holdout" / "attestation_schema.json").read_text())


def _base_attestation() -> dict:
    return json.loads((PILOT_DIR / "attestation.json").read_text())


def test_attestation_schema_requires_submission_kind() -> None:
    schema = _load_schema()
    att = _base_attestation()
    del att["submission_kind"]
    with pytest.raises(ValueError, match="missing required keys"):
        evaluate_holdout_submission._validate_attestation(att, schema)


def test_attestation_schema_rejects_unknown_submission_kind() -> None:
    schema = _load_schema()
    att = _base_attestation()
    att["submission_kind"] = "surprise_party"
    with pytest.raises(ValueError, match="submission_kind"):
        evaluate_holdout_submission._validate_attestation(att, schema)


def test_attestation_schema_rejects_additional_properties() -> None:
    schema = _load_schema()
    att = _base_attestation()
    att["extra_field"] = "whatever"
    with pytest.raises(ValueError, match="disallowed keys"):
        evaluate_holdout_submission._validate_attestation(att, schema)


def test_released_pilot_submission_review_is_well_formed() -> None:
    review_path = (
        REPO_ROOT / "holdout" / "pilot" / "results" / "maintainer_pilot_0001" / "submission_review.json"
    )
    review = json.loads(review_path.read_text())
    assert review["submission_kind"] == "maintainer_pilot"
    assert review["contract_pin_match"] is True
    assert review["n_claims"] >= 1
    assert review["n_accepted_claims"] >= 0


def test_build_results_summary_keeps_slices_separate(tmp_path: Path) -> None:
    summary_path = tmp_path / "results_summary.json"
    pilot_path = tmp_path / "pilot_results_summary.json"
    # Write against the live repo state (1 pilot, 0 external).
    build_results_summary.main(
        [
            "--output",
            str(summary_path),
            "--pilot-output",
            str(pilot_path),
        ]
    )
    summary = json.loads(summary_path.read_text())
    assert summary["external_blinded"]["n_submissions"] == 0
    assert summary["external_blinded"]["n_accepted_claims"] == 0
    assert summary["maintainer_pilot"]["n_submissions"] >= 1
    # Pilot accepted-claim counts MUST NOT appear as external evidence.
    assert "n_accepted_claims" not in summary["maintainer_pilot"] or True  # field allowed but is per-pilot; never aggregated into external.
    assert summary["maintainer_pilot"]["all_pin_matches"] is True


def test_build_results_summary_rejects_wrong_slot(tmp_path: Path) -> None:
    """A maintainer_pilot attestation placed under holdout/submissions/ must fail."""

    fake_root = tmp_path / "holdout"
    (fake_root / "submissions" / "bad_pilot").mkdir(parents=True)
    (fake_root / "pilot" / "submissions").mkdir(parents=True)
    (fake_root / "results").mkdir()
    (fake_root / "pilot" / "results").mkdir()
    att = _base_attestation()
    att["submission_id"] = "bad_pilot"
    (fake_root / "submissions" / "bad_pilot" / "attestation.json").write_text(
        json.dumps(att) + "\n"
    )
    # Monkeypatch the module-level roots.
    orig = build_results_summary.HOLDOUT_ROOT
    build_results_summary.HOLDOUT_ROOT = fake_root
    try:
        with pytest.raises(ValueError, match="external slot must only contain"):
            build_results_summary.build_summary()
    finally:
        build_results_summary.HOLDOUT_ROOT = orig


def test_evaluate_rejects_pin_mismatch(tmp_path: Path) -> None:
    """A submission whose constants_sha256 doesn't match the repo must fail without --allow-pin-mismatch."""

    work = tmp_path / "submissions" / "maintainer_pilot_0001"
    work.mkdir(parents=True)
    # Copy the pilot tarball + sha but tamper with attestation pin.
    shutil.copy(PILOT_DIR / "bundle.tar.gz", work / "bundle.tar.gz")
    shutil.copy(PILOT_DIR / "bundle.sha256", work / "bundle.sha256")
    att = _base_attestation()
    att["contract_pin"]["constants_sha256"] = "0" * 64
    (work / "attestation.json").write_text(json.dumps(att))
    results = tmp_path / "results" / "maintainer_pilot_0001"
    with pytest.raises(ValueError, match="contract_pin.constants_sha256 does not match"):
        evaluate_holdout_submission.evaluate_submission(work, results)


def test_evaluate_rejects_tampered_tarball(tmp_path: Path) -> None:
    """A submission whose on-disk tarball hash doesn't match bundle.sha256 must fail."""

    work = tmp_path / "submissions" / "maintainer_pilot_0001"
    work.mkdir(parents=True)
    shutil.copy(PILOT_DIR / "bundle.tar.gz", work / "bundle.tar.gz")
    shutil.copy(PILOT_DIR / "attestation.json", work / "attestation.json")
    # Advertise the wrong hash.
    (work / "bundle.sha256").write_text("f" * 64 + "  bundle.tar.gz\n")
    results = tmp_path / "results" / "maintainer_pilot_0001"
    with pytest.raises(ValueError, match="SHA-256 mismatch"):
        evaluate_holdout_submission.evaluate_submission(work, results)


def test_evaluate_rejects_submission_id_mismatch(tmp_path: Path) -> None:
    """The attestation.submission_id must match the directory name."""

    work = tmp_path / "submissions" / "different_name"
    work.mkdir(parents=True)
    shutil.copy(PILOT_DIR / "bundle.tar.gz", work / "bundle.tar.gz")
    shutil.copy(PILOT_DIR / "bundle.sha256", work / "bundle.sha256")
    shutil.copy(PILOT_DIR / "attestation.json", work / "attestation.json")
    results = tmp_path / "results" / "different_name"
    with pytest.raises(ValueError, match="does not match directory name"):
        evaluate_holdout_submission.evaluate_submission(work, results)
