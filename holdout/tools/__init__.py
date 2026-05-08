"""Tooling for the AutoMechInterp blinded-holdout slice.

This package now contains both:

- author-side helpers that package and preflight sealed submissions without
  evaluating them; and
- custodian-side helpers that re-run the pinned evaluator and aggregate results.

The author-side helpers reduce operational friction while preserving the blind:
they validate packaging, hashes, and contract pins but never call the evaluator.
"""
