from __future__ import annotations

from main.co_failure_matrix import compute_co_failure_matrix


def _toy_summary() -> dict:
    """Construct a small synthetic failure summary with a known answer.

    Two claims fail [a, b]; one claim fails [a, c]; one claim fails [d].
    Marginals: a=3, b=2, c=1, d=1. Total claims=4, failed=4.
    """
    return {
        "n_claims": 4,
        "n_passed": 0,
        "n_failed": 4,
        "failed_gate_counts": {"a": 3, "b": 2, "c": 1, "d": 1},
        "all_failed_combinations": [
            {"failed_checks": ["a", "b"], "count": 2},
            {"failed_checks": ["a", "c"], "count": 1},
            {"failed_checks": ["d"], "count": 1},
        ],
        "top_failed_combinations": [
            {"failed_checks": ["a", "b"], "count": 2},
            {"failed_checks": ["a", "c"], "count": 1},
            {"failed_checks": ["d"], "count": 1},
        ],
    }


def test_co_failure_matrix_diagonals_match_marginals_when_full_combinations_present() -> None:
    payload = compute_co_failure_matrix(_toy_summary())
    assert payload["source"] == "all_failed_combinations"
    assert payload["diagonal_check_complete"] is True
    for gate, marginal in payload["marginal_failed_gate_counts"].items():
        assert payload["diagonal_check"][gate] == marginal


def test_co_failure_matrix_off_diagonals_are_correct() -> None:
    payload = compute_co_failure_matrix(_toy_summary())
    gates = payload["gates"]  # sorted: a, b, c, d
    matrix = payload["matrix"]
    a, b, c, d = gates.index("a"), gates.index("b"), gates.index("c"), gates.index("d")
    # Two claims fail both a and b.
    assert matrix[a][b] == 2
    assert matrix[b][a] == 2
    # One claim fails both a and c.
    assert matrix[a][c] == 1
    assert matrix[c][a] == 1
    # No claim fails both b and c, or anything-and-d.
    assert matrix[b][c] == 0
    assert matrix[a][d] == 0
    assert matrix[d][a] == 0


def test_co_failure_dominant_cluster_is_largest_combination() -> None:
    payload = compute_co_failure_matrix(_toy_summary())
    cluster = payload["dominant_fragility_cluster"]
    assert cluster["claims_with_this_pattern"] == 2
    assert cluster["failed_gates"] == ["a", "b"]
    assert cluster["size"] == 2
    assert cluster["fraction_of_claims_with_failed_gates"] == 0.5
    assert cluster["fraction_of_all_claims"] == 0.5


def test_co_failure_counts_failed_gates_separately_from_rejected_claims() -> None:
    summary = _toy_summary()
    summary["n_failed"] = 1
    payload = compute_co_failure_matrix(summary)

    assert payload["n_failed"] == 1
    assert payload["claims_with_failed_gates"] == 4
    assert payload["dominant_fragility_cluster"]["fraction_of_claims_with_failed_gates"] == 0.5


def test_co_failure_falls_back_to_top_combinations_for_legacy_summaries() -> None:
    summary = _toy_summary()
    summary.pop("all_failed_combinations")
    payload = compute_co_failure_matrix(summary)
    assert payload["source"] == "top_failed_combinations"
    # diagonal_check_complete is conservatively False when we fell back to
    # the truncated top-K list, even if on this toy data top happens to equal
    # all. This is the right behavior: callers should only trust completeness
    # if the source was explicitly the full combination list.
    assert payload["diagonal_check_complete"] is False
