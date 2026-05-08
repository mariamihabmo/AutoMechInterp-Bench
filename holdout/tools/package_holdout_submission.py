"""Author-side helper: package a bundle into a sealed holdout submission.

This tool does *not* evaluate the bundle. It only packages the canonical bundle
files into ``bundle.tar.gz``, writes ``bundle.sha256``, and emits a schema-
conforming ``attestation.json`` so an external author can hand a sealed payload
to the Custodian without manually assembling files.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tarfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable

REPO_ROOT = Path(__file__).resolve().parents[2]
CONSTANTS_PATH = REPO_ROOT / 'packages' / 'evaluator' / 'src' / 'automechinterp_evaluator' / 'constants.py'
EVALUATOR_PYPROJECT = REPO_ROOT / 'packages' / 'evaluator' / 'pyproject.toml'
ALLOWED_MEMBERS = (
    'protocol.yaml',
    'hypothesis.jsonl',
    'evaluation_result.json',
    'manifest.json',
    'cross_model_results.json',
)

def _generated_at_utc() -> str:
    """ISO-8601 UTC timestamp honoring ``SOURCE_DATE_EPOCH`` for byte-reproducible attestations.

    the external author packaging flow
    must be byte-reproducible — two authors who package the same bundle
    contents with the same ``SOURCE_DATE_EPOCH`` (and identical attestation
    inputs) should produce byte-identical ``attestation.json``. Mirrors
    ``holdout/tools/build_results_summary.py:_generated_at_utc``.
    """
    raw = os.environ.get("SOURCE_DATE_EPOCH")
    if raw:
        try:
            return datetime.fromtimestamp(int(raw), tz=timezone.utc).isoformat(timespec="seconds")
        except (TypeError, ValueError):
            pass
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()

def _evaluator_version() -> str:
    """Return the pinned evaluator version string.

    use ``tomllib`` (or the
    ``tomli`` fallback for Python <3.11) instead of string-splitting
    ``pyproject.toml``. The previous implementation broke on quoting
    variations, comments, or dynamic-version metadata.
    """
    try:
        import tomllib  # type: ignore[import-not-found]
    except ModuleNotFoundError:  # Python < 3.11
        try:
            import tomli as tomllib  # type: ignore[import-not-found,no-redef]
        except ModuleNotFoundError:
            tomllib = None  # type: ignore[assignment]
    if tomllib is not None:
        try:
            with EVALUATOR_PYPROJECT.open('rb') as fh:
                data = tomllib.load(fh)
            version = data.get('project', {}).get('version')
            if isinstance(version, str) and version.strip():
                return f'automechinterp-evaluator=={version}'
        except Exception:
            pass
    # Fallback: legacy string-split (kept only as a last resort).
    text = EVALUATOR_PYPROJECT.read_text()
    marker = 'version = "'
    if marker not in text:
        return 'automechinterp-evaluator==unknown'
    version = text.split(marker, 1)[1].split('"', 1)[0]
    return f'automechinterp-evaluator=={version}'

def current_contract_pin() -> Dict[str, str]:
    return {
        'evaluator_version': _evaluator_version(),
        'constants_sha256': _sha256_file(CONSTANTS_PATH),
    }

def canonical_bundle_members(bundle_dir: Path) -> list[Path]:
    members: list[Path] = []
    for name in ALLOWED_MEMBERS:
        path = bundle_dir / name
        if path.exists():
            members.append(path)
    required = {'protocol.yaml', 'hypothesis.jsonl', 'evaluation_result.json', 'manifest.json'}
    missing = [name for name in required if not (bundle_dir / name).exists()]
    if missing:
        raise FileNotFoundError(f'Bundle is missing required files: {missing}')
    return members

def default_attestation_text(submission_kind: str, bundle_dir: Path) -> str:
    bundle_hint = bundle_dir.name
    if submission_kind == 'maintainer_pilot':
        return (
            'PILOT, NOT BLINDED. This submission is authored by the AutoMechInterp maintainers '
            'for the sole purpose of exercising the Custodian evaluation pipeline end-to-end '
            '(schema validation, tarball SHA-256, contract-pin audit, evaluator re-run, and '
            'results aggregation). It does NOT satisfy the independence requirements of '
            'methodology/blinded_holdout_protocol.md and MUST NOT be counted as external evidence. '
            f'The payload is a maintainer-authored bundle re-sealed from `{bundle_hint}`.'
        )
    return (
        'BLINDED EXTERNAL AUTHORING. This bundle was authored against the public AutoMechInterp '
        'contract specification without consulting any AutoMechInterp maintainer about acceptance '
        'heuristics, accepted-claim examples, or unpublished thresholds during authoring, and it '
        'was not pre-evaluated against the pinned evaluator before sealed submission to the Custodian.'
    )

def build_attestation(
    *,
    submission_id: str,
    submission_kind: str,
    author_institution: str,
    attestation_text: str,
    attestation_signature: str,
    submitted_at_utc: str | None = None,
) -> Dict[str, Any]:
    submitted_at_utc = submitted_at_utc or _generated_at_utc()
    return {
        'submission_id': submission_id,
        'submission_kind': submission_kind,
        'submitted_at_utc': submitted_at_utc,
        'author_institution': author_institution,
        'contract_pin': current_contract_pin(),
        'attestation_text': attestation_text,
        'attestation_signature': attestation_signature,
    }

def package_submission(
    *,
    bundle_dir: Path,
    submission_dir: Path,
    submission_id: str,
    submission_kind: str,
    author_institution: str,
    attestation_text: str | None = None,
    attestation_signature: str | None = None,
    submitted_at_utc: str | None = None,
) -> Dict[str, Any]:
    bundle_dir = bundle_dir.resolve()
    submission_dir = submission_dir.resolve()
    submission_dir.mkdir(parents=True, exist_ok=True)

    if submission_kind not in {'external_blinded', 'maintainer_pilot'}:
        raise ValueError(f'Unsupported submission_kind: {submission_kind}')

    if not attestation_signature:
        if submission_kind == 'maintainer_pilot':
            attestation_signature = (
                'PILOT-NO-SIGNATURE: maintainer pilots use a literal sentinel in place '
                'of a Custodian-scheme signature because they are never counted as external evidence.'
            )
        else:
            raise ValueError('external_blinded submissions require a non-empty attestation_signature')

    attestation_text = attestation_text or default_attestation_text(submission_kind, bundle_dir)
    attestation = build_attestation(
        submission_id=submission_id,
        submission_kind=submission_kind,
        author_institution=author_institution,
        attestation_text=attestation_text,
        attestation_signature=attestation_signature,
        submitted_at_utc=submitted_at_utc,
    )

    tarball_path = submission_dir / 'bundle.tar.gz'
    with tarfile.open(tarball_path, 'w:gz') as tar:
        for member in canonical_bundle_members(bundle_dir):
            tar.add(member, arcname=member.name)

    sha = _sha256_file(tarball_path)
    (submission_dir / 'bundle.sha256').write_text(f'{sha}  bundle.tar.gz\n')
    (submission_dir / 'attestation.json').write_text(json.dumps(attestation, indent=2, sort_keys=True) + '\n')
    return {
        'submission_dir': str(submission_dir),
        'submission_id': submission_id,
        'submission_kind': submission_kind,
        'bundle_tarball_sha256': sha,
        'contract_pin': attestation['contract_pin'],
        'members': [p.name for p in canonical_bundle_members(bundle_dir)],
    }

def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument('--bundle-dir', required=True, type=Path)
    p.add_argument('--submission-dir', required=True, type=Path)
    p.add_argument('--submission-id', required=True)
    p.add_argument('--submission-kind', required=True, choices=['external_blinded', 'maintainer_pilot'])
    p.add_argument('--author-institution', required=True)
    p.add_argument('--attestation-text-file', type=Path, default=None)
    p.add_argument('--attestation-signature', default=None)
    p.add_argument('--submitted-at-utc', default=None)
    return p.parse_args(argv)

def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    attestation_text = args.attestation_text_file.read_text().strip() if args.attestation_text_file else None
    result = package_submission(
        bundle_dir=args.bundle_dir,
        submission_dir=args.submission_dir,
        submission_id=args.submission_id,
        submission_kind=args.submission_kind,
        author_institution=args.author_institution,
        attestation_text=attestation_text,
        attestation_signature=args.attestation_signature,
        submitted_at_utc=args.submitted_at_utc,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0

if __name__ == '__main__':  # pragma: no cover
    raise SystemExit(main())
