"""One-shot tool: add missing cross_model_results.json SHA-256 to manifest.json if present.

Usage:
    .venv/bin/python tools/upgrade_manifests_cross_model_sha.py [--dry-run]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = {".venv", ".git", "node_modules", "__pycache__"}


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def _iter_bundle_dirs(root: Path):
    for manifest_path in sorted(root.rglob("manifest.json")):
        if any(part in SKIP_DIRS for part in manifest_path.parts):
            continue
        yield manifest_path.parent


def upgrade(root: Path, dry_run: bool = False) -> tuple[int, int, int]:
    upgraded = 0
    already = 0
    mismatches = 0
    for bundle_dir in _iter_bundle_dirs(root):
        cm_path = bundle_dir / "cross_model_results.json"
        if not cm_path.exists():
            continue
        manifest_path = bundle_dir / "manifest.json"
        try:
            manifest = json.loads(manifest_path.read_text())
        except json.JSONDecodeError as exc:
            print(f"SKIP (bad json): {manifest_path}: {exc}", file=sys.stderr)
            continue
        actual = _sha256_file(cm_path)
        declared = manifest.get("cross_model_results.json")
        rel = bundle_dir.relative_to(root)
        if declared == actual:
            already += 1
            continue
        if declared is not None and declared != actual:
            print(
                f"MISMATCH: {rel}: declared={declared} actual={actual}",
                file=sys.stderr,
            )
            mismatches += 1
            continue
        # declared is None and file is present -> insert
        manifest["cross_model_results.json"] = actual
        if not dry_run:
            manifest_path.write_text(
                json.dumps(manifest, indent=2, sort_keys=True) + "\n"
            )
        upgraded += 1
        print(f"UPGRADED: {rel}")
    return upgraded, already, mismatches


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    args = parser.parse_args(argv)
    upgraded, already, mismatches = upgrade(args.root, dry_run=args.dry_run)
    print(
        f"\nupgraded={upgraded} already_correct={already} mismatches={mismatches}"
    )
    return 1 if mismatches else 0


if __name__ == "__main__":
    sys.exit(main())
