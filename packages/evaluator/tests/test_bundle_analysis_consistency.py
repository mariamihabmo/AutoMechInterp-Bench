from __future__ import annotations

from main._bundle_analysis import REAL_MULTILANE_DIR, REAL_MULTI_TASK_DIR, evaluate_bundle_records, summarize_coverage


def test_coverage_summary_is_self_consistent() -> None:
    records = evaluate_bundle_records(REAL_MULTI_TASK_DIR, REAL_MULTILANE_DIR, use_cached_results=True)
    coverage = summarize_coverage(records)

    assert coverage["n_bundles"] == len(coverage["bundles"])
    assert coverage["totals"]["claims"] == sum(row["n_claims"] for row in coverage["bundles"])
    assert coverage["totals"]["accepted"] == sum(row["accepted"] for row in coverage["bundles"])
    assert coverage["totals"]["rejected"] == sum(row["rejected"] for row in coverage["bundles"])
