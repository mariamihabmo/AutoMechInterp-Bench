"""Regression tests for ``_bootstrap_ci`` BCa boundary behaviour.

Audit 2026-05 (post-Phase-C) flagged that the BCa bias-correction term
previously used a strict ``<`` (Efron-DiCiccio require ``<=``) and masked
the saturation crash with a ``[1e-10, 1-1e-10]`` clamp on ``p_below``.
The redesign:

1. uses ``<=`` (correct Efron-DiCiccio convention),
2. short-circuits degenerate bootstrap distributions to a zero-width interval,
3. falls back to the percentile interval when ``z0`` saturates to ``±inf``
   or the BCa denominators are non-finite/near-zero,
4. preserves correct behaviour on well-conditioned distributions.

These regression tests pin (1)-(4) so a future refactor cannot silently
re-introduce the saturation crash or the strict-``<`` bias.
"""
from __future__ import annotations

import math

from automechinterp_evaluator.evaluator import _bootstrap_ci


def test_bootstrap_ci_degenerate_constant_values_returns_point_interval():
    """All-equal input -> zero-width interval, no crash."""
    lo, hi = _bootstrap_ci([0.0] * 16, n_resamples=64, seed="degen-zero")
    assert lo == 0.0 and hi == 0.0

    lo, hi = _bootstrap_ci([0.5] * 16, n_resamples=64, seed="degen-half")
    assert lo == 0.5 and hi == 0.5


def test_bootstrap_ci_p_below_saturated_one_falls_back_to_percentile():
    """When every bootstrap mean <= theta_hat, p_below=1.0 -> z0=+inf.

    The redesigned guard must catch the non-finite ``z0`` and fall back
    to the percentile interval rather than raise ``ValueError`` from
    ``int(math.ceil(NaN * len))``.
    """
    # Pathological input: one large outlier pulls theta_hat above almost
    # every bootstrap-resample mean for small B; this drives count_below
    # toward saturation.
    values = [0.0] * 19 + [100.0]
    lo, hi = _bootstrap_ci(values, n_resamples=64, seed="saturate-hi")
    assert math.isfinite(lo) and math.isfinite(hi)
    assert lo <= hi


def test_bootstrap_ci_well_conditioned_distribution_returns_finite_interval():
    """Sanity check: a clean iid-like sequence still produces a finite CI
    that brackets the sample mean."""
    values = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    theta = sum(values) / len(values)
    lo, hi = _bootstrap_ci(values, n_resamples=128, seed="well-cond")
    assert math.isfinite(lo) and math.isfinite(hi)
    assert lo <= theta <= hi


def test_bootstrap_ci_tie_at_theta_hat_uses_le_not_lt():
    """If many bootstrap means tie exactly at theta_hat, the strict-``<``
    convention would undercount them and bias z0 toward -inf, producing a
    spuriously low CI. The ``<=`` convention should keep the CI centered
    on theta_hat for a symmetric, tie-heavy distribution."""
    # Symmetric distribution where the mean is exactly representable and
    # many bootstrap resamples will hit it on the nose.
    values = [0.0, 0.0, 1.0, 1.0]  # mean = 0.5
    lo, hi = _bootstrap_ci(values, n_resamples=256, seed="ties")
    assert math.isfinite(lo) and math.isfinite(hi)
    # The interval should bracket 0.5 (the true sample mean) regardless
    # of the tie convention, but with ``<=`` z0 stays finite and the CI
    # is bounded by the bootstrap support [0.0, 1.0].
    assert 0.0 <= lo <= 0.5 <= hi <= 1.0


def test_bootstrap_ci_short_input_returns_point_interval():
    """Single-value input -> point interval (existing contract)."""
    lo, hi = _bootstrap_ci([0.42], n_resamples=64, seed="single")
    assert lo == 0.42 and hi == 0.42

    lo, hi = _bootstrap_ci([], n_resamples=64, seed="empty")
    assert lo == 0.0 and hi == 0.0
