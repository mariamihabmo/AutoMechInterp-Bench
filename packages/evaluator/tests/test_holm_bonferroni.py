"""Regression tests for ``_holm_bonferroni``.

The implementation is correct today, but a future refactor (e.g.
swapping ``min(prev, ...)`` for plain assignment, or inverting the
sort) would silently produce unsound corrected p-values. These tests
pin the three semantic properties the procedure must always have:
outputs are at least as large as inputs, outputs are monotone
non-decreasing in original p-value rank, and outputs are bounded by 1.
"""

from __future__ import annotations

import random

from automechinterp_evaluator.evaluator import _holm_bonferroni

def test_holm_bonferroni_empty() -> None:
    assert _holm_bonferroni([]) == {}

def test_holm_bonferroni_outputs_geq_inputs() -> None:
    items = [("a", 0.001), ("b", 0.01), ("c", 0.04), ("d", 0.2)]
    adj = _holm_bonferroni(items)
    for hid, p in items:
        assert adj[hid] >= p, f"{hid}: adjusted {adj[hid]} < raw {p}"

def test_holm_bonferroni_outputs_bounded_by_one() -> None:
    items = [("a", 0.4), ("b", 0.5), ("c", 0.9)]
    adj = _holm_bonferroni(items)
    for hid in adj:
        assert adj[hid] <= 1.0

def test_holm_bonferroni_monotone_in_rank() -> None:
    items = [("a", 0.001), ("b", 0.01), ("c", 0.04), ("d", 0.2)]
    adj = _holm_bonferroni(items)
    ordered = sorted(items, key=lambda x: x[1])
    prev = 0.0
    for hid, _ in ordered:
        assert adj[hid] >= prev
        prev = adj[hid]

def test_holm_bonferroni_smallest_uses_full_n() -> None:
    items = [("a", 0.01), ("b", 0.02), ("c", 0.03)]
    adj = _holm_bonferroni(items)
    # Smallest p gets multiplied by n=3
    assert abs(adj["a"] - 0.03) < 1e-12

def test_holm_bonferroni_random_inputs_satisfy_invariants() -> None:
    rng = random.Random(20260506)
    for _ in range(50):
        n = rng.randint(1, 25)
        items = [(f"h{i}", rng.random()) for i in range(n)]
        adj = _holm_bonferroni(items)
        # Geq inputs.
        for hid, p in items:
            assert adj[hid] >= p - 1e-12
        # Bounded by 1.
        for hid in adj:
            assert 0.0 <= adj[hid] <= 1.0 + 1e-12
        # Monotone in rank.
        ordered = sorted(items, key=lambda x: x[1])
        prev = -1.0
        for hid, _ in ordered:
            assert adj[hid] >= prev - 1e-12
            prev = adj[hid]
