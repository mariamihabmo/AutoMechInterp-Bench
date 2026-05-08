from __future__ import annotations

import json
from pathlib import Path

import pytest

from holdout.tools import preflight_submission
from holdout.tools.package_holdout_submission import package_submission

REPO_ROOT = Path(__file__).resolve().parents[3]
EXAMPLE_BUNDLE = REPO_ROOT / 'packages' / 'evaluator' / 'templates' / 'example_bundle'


def test_package_and_preflight_maintainer_pilot(tmp_path: Path) -> None:
    submission_dir = tmp_path / 'pilot' / 'submissions' / 'maintainer_pilot_test'
    result = package_submission(
        bundle_dir=EXAMPLE_BUNDLE,
        submission_dir=submission_dir,
        submission_id='maintainer_pilot_test',
        submission_kind='maintainer_pilot',
        author_institution='AutoMechInterp maintainers (test pilot)',
    )
    assert result['submission_kind'] == 'maintainer_pilot'
    payload = preflight_submission.preflight_submission(submission_dir)
    assert payload['bundle_sha256_matches'] is True
    assert payload['contract_pin_match'] is True
    assert payload['ready_for_custodian_evaluation'] is True


def test_external_blinded_requires_signature(tmp_path: Path) -> None:
    submission_dir = tmp_path / 'submissions' / 'external_001'
    with pytest.raises(ValueError, match='attestation_signature'):
        package_submission(
            bundle_dir=EXAMPLE_BUNDLE,
            submission_dir=submission_dir,
            submission_id='external_001',
            submission_kind='external_blinded',
            author_institution='Independent Lab',
        )
