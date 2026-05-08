"""Repo-level pytest path configuration for fresh-checkout test runs."""

from __future__ import annotations

import os
import sys
import warnings
from pathlib import Path

# PYTHONHASHSEED must be set BEFORE the Python interpreter starts to affect
# hashing; we cannot enforce it from inside the process. We can, however, warn
# loudly when contributors invoke `pytest` directly without the Makefile/
# Dockerfile wrapper, so that any test relying on dict/set ordering does not
# silently behave non-deterministically.
_hashseed = os.environ.get("PYTHONHASHSEED")
if _hashseed not in ("0", "random"):  # "random" is the default if unset
    pass  # neither pinned to 0 nor explicitly random; let the warning below fire
if _hashseed != "0":
    warnings.warn(
        "PYTHONHASHSEED is not pinned to 0 for this pytest invocation; "
        "deterministic-ordering tests may be flaky. Run via `make test` or "
        "set `PYTHONHASHSEED=0 pytest ...` to match the release-grade audit.",
        RuntimeWarning,
        stacklevel=1,
    )

ROOT = Path(__file__).resolve().parent
for rel in (".", "packages/evaluator/src", "packages/runner/src"):
    path = str((ROOT / rel).resolve())
    if path not in sys.path:
        sys.path.insert(0, path)
