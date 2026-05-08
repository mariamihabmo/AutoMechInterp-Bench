"""Author-side preflight for a sealed holdout submission.

Unlike ``evaluate_holdout_submission.py``, this tool does not run the evaluator.
It only checks that the submission package is internally well-formed and pinned
against the current contract hash so authors can catch packaging mistakes without
piercing the holdout blind.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from . import evaluate_holdout_submission


def preflight_submission(submission_dir: Path) -> Dict[str, Any]:
    submission_dir = submission_dir.resolve()
    attestation_path = submission_dir / 'attestation.json'
    tarball_path = submission_dir / 'bundle.tar.gz'
    sha_path = submission_dir / 'bundle.sha256'

    for required in (attestation_path, tarball_path, sha_path):
        if not required.exists():
            raise FileNotFoundError(f'submission is missing: {required.name}')

    schema = json.loads(evaluate_holdout_submission.SCHEMA_PATH.read_text())
    attestation = json.loads(attestation_path.read_text())
    evaluate_holdout_submission._validate_attestation(attestation, schema)

    actual_sha = evaluate_holdout_submission._sha256_file(tarball_path)
    expected_sha = sha_path.read_text().split()[0].strip()
    repo_constants_sha = evaluate_holdout_submission._sha256_file(
        evaluate_holdout_submission.CONSTANTS_PATH
    )
    pin_constants_sha = attestation['contract_pin']['constants_sha256']

    payload = {
        'submission_id': attestation['submission_id'],
        'submission_kind': attestation['submission_kind'],
        'submission_dir': str(submission_dir),
        'bundle_sha256_matches': actual_sha == expected_sha,
        'contract_pin_match': repo_constants_sha == pin_constants_sha,
        'actual_bundle_sha256': actual_sha,
        'expected_bundle_sha256': expected_sha,
        'repo_constants_sha256': repo_constants_sha,
        'attested_constants_sha256': pin_constants_sha,
        'ready_for_custodian_evaluation': actual_sha == expected_sha and repo_constants_sha == pin_constants_sha,
    }
    return payload


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument('--submission-dir', required=True, type=Path)
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    payload = preflight_submission(args.submission_dir)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == '__main__':  # pragma: no cover
    raise SystemExit(main())
