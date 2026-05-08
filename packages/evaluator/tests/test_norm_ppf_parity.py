"""Parity tests for the dependency-free statistical primitives.

These tests provide an independent oracle for two pieces of statistics
machinery that the evaluator implements without relying on scipy:

- ``_norm_ppf``: AS241 (Wichura 1988) inverse standard-normal quantile.
  Compared element-wise against ``scipy.stats.norm.ppf`` over a deep grid
  of probabilities including the tails. The test is gated on
  ``pytest.importorskip("scipy")`` so the package retains zero runtime
  dependency on scipy.
- ``_permutation_p_value``: the Phipson & Smyth (2010) MC correction
  ``(count_ge + 1) / (n_permutations + 1)``. The test verifies the
  documented lower bound (an exhaustively-non-rejected test cannot
  return a literal zero) and an algebraic identity that pins the
  correction down independently of the RNG.

History: both were tightened in the Option C audit pass (see
``methodology/audit/v2_audit_report.md`` findings F-005 and F-006). The
tests exist so a future rewrite cannot silently regress to the prior
AS 26.2.23 / uncorrected-MC-p formulations.
"""

from __future__ import annotations

import math

import pytest

from automechinterp_evaluator.evaluator import (
    _norm_cdf,
    _norm_ppf,
    _permutation_p_value,
)


# ----------------------------------------------------------------------------
# F-005: AS241 parity vs scipy.stats.norm.ppf
# ----------------------------------------------------------------------------


@pytest.fixture(scope="module")
def scipy_norm():
    """Skip the parity test if scipy is not available."""
    scipy_stats = pytest.importorskip("scipy.stats")
    return scipy_stats.norm


# Probabilities chosen to span the AS241 region splits (|q| <= 0.425,
# intermediate tail with r <= 5, and far tail with r > 5). The far-tail
# split is reached at probabilities below ~exp(-25) ~ 1e-11.
_GRID = [
    1e-15,
    1e-12,
    1e-10,
    1e-8,
    1e-6,
    1e-4,
    1e-3,
    1e-2,
    0.05,
    0.1,
    0.2,
    0.25,
    0.3,
    0.4,
    0.425,  # central/intermediate boundary
    0.4999,
    0.5,
    0.5001,
    0.575,  # central/intermediate boundary on the right
    0.6,
    0.7,
    0.75,
    0.8,
    0.9,
    0.95,
    0.99,
    0.999,
    1.0 - 1e-4,
    1.0 - 1e-6,
    1.0 - 1e-8,
    1.0 - 1e-10,
    1.0 - 1e-12,
    1.0 - 1e-15,
]


@pytest.mark.parametrize("p", _GRID)
def test_norm_ppf_matches_scipy(p: float, scipy_norm) -> None:
    """AS241 must agree with scipy.stats.norm.ppf to 1e-9 absolute and
    1e-10 relative across the full evaluation grid, including the deep
    tails where the prior AS 26.2.23 approximation degraded to ~1e-3."""
    expected = float(scipy_norm.ppf(p))
    actual = _norm_ppf(p)
    if math.isinf(expected):
        # scipy returns +/-inf at the boundary; AS241 should match.
        assert math.isinf(actual), f"AS241 returned finite {actual} for p={p}"
        assert (actual > 0) == (expected > 0)
        return
    abs_err = abs(actual - expected)
    rel_err = abs_err / max(1.0, abs(expected))
    assert abs_err < 1e-9, (
        f"AS241 vs scipy abs error too large at p={p}: |{actual} - {expected}| = {abs_err}"
    )
    assert rel_err < 1e-10, (
        f"AS241 vs scipy rel error too large at p={p}: {rel_err}"
    )


def test_norm_ppf_boundary_behavior() -> None:
    """The contract: at the open-interval boundaries return saturated +/-inf.
    Earlier callers in the module clamp to ``[1e-10, 1 - 1e-10]`` so the
    boundary saturation is unobservable in production, but the test pins
    it down so a future rewrite cannot silently flip back to the legacy
    +/-6.0 saturation."""
    assert _norm_ppf(0.0) == float("-inf")
    assert _norm_ppf(-0.5) == float("-inf")
    assert _norm_ppf(1.0) == float("inf")
    assert _norm_ppf(1.5) == float("inf")
    # Symmetric around 0.5 to within machine epsilon.
    for p in (0.001, 0.01, 0.1, 0.25, 0.4, 0.45):
        assert math.isclose(_norm_ppf(p), -_norm_ppf(1.0 - p), abs_tol=1e-12)


def test_norm_cdf_inverts_norm_ppf() -> None:
    """End-to-end identity: ``_norm_cdf(_norm_ppf(p)) ≈ p``."""
    for p in (0.001, 0.01, 0.1, 0.25, 0.5, 0.75, 0.9, 0.99, 0.999):
        round_trip = _norm_cdf(_norm_ppf(p))
        assert math.isclose(round_trip, p, abs_tol=1e-9), (
            f"norm_cdf(norm_ppf({p})) = {round_trip}"
        )


# ----------------------------------------------------------------------------
# F-006: Phipson-Smyth +1/+1 correction
# ----------------------------------------------------------------------------


def test_permutation_p_value_never_returns_zero() -> None:
    """Per Phipson & Smyth (2010): an MC permutation test must not be able
    to report a literal zero p-value. With ``n_permutations=N`` the
    minimum reportable p is ``1 / (N + 1)``."""
    # All values identical and very large -> observed_stat dominates every
    # permutation's stat (max bound). Without the +1 correction this
    # would have returned exactly 0.0.
    values = [1000.0] * 12
    p = _permutation_p_value(values, n_permutations=99, seed="t1")
    assert p > 0.0
    assert p == pytest.approx(1.0 / (99 + 1), abs=1e-12)


def test_permutation_p_value_bounded_above_by_one() -> None:
    """With every permutation matching, p must be exactly 1.0 (the prior
    formulation gave (N+1)/(N+1) = 1.0; the corrected formulation must
    preserve this upper bound)."""
    # Symmetric values around zero -> observed_stat = 0 -> every
    # permutation's |mean| >= 0 -> count_ge = N. The corrected p is
    # (N + 1) / (N + 1) = 1.0.
    values = [1.0, -1.0, 1.0, -1.0]
    p = _permutation_p_value(values, n_permutations=50, seed="t2")
    assert p == pytest.approx(1.0, abs=1e-12)


def test_permutation_p_value_consistent_with_count_under_correction() -> None:
    """Algebraic check: for any observed sample, the returned p is exactly
    ``(count_ge + 1) / (n_permutations + 1)`` where ``count_ge`` is the
    number of permutations with ``|perm_mean| >= |obs_mean|``. Re-runs
    the permutations to derive the count independently."""
    from automechinterp_evaluator.evaluator import _seeded_rng_ints
    from statistics import mean

    values = [0.4, -0.1, 0.3, 0.2, -0.05, 0.15, 0.25, -0.2, 0.3, 0.1]
    n_perm = 200
    seed = "consistency"
    p_reported = _permutation_p_value(values, n_permutations=n_perm, seed=seed)
    obs = abs(mean(values))
    count = 0
    n = len(values)
    for k in range(n_perm):
        flips = _seeded_rng_ints(f"{seed}|{k}", n, 2)
        perm = [v if flips[i] == 0 else -v for i, v in enumerate(values)]
        if abs(mean(perm)) >= obs:
            count += 1
    expected = (count + 1) / (n_perm + 1)
    assert p_reported == pytest.approx(expected, abs=1e-15)


def test_permutation_p_value_empty_input_returns_one() -> None:
    """Defensive boundary: empty input keeps the documented sentinel of 1.0."""
    assert _permutation_p_value([], n_permutations=100) == 1.0
