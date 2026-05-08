"""Stage-2 intervention runner package."""

# single source of truth for runner_version. The
# Stage2Config default reads from this constant so artifact provenance and
# package metadata cannot drift apart.
__version__ = "0.2.0"

from .runner import run_stage2

__all__ = ["run_stage2", "__version__"]
