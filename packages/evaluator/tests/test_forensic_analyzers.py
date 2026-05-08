"""Tests for the post-release forensic analyzers.

These analyzers re-project existing released data into more
compact summary form. The tests focus on the pure helper functions so
they remain fast and do not require evaluating real bundles end-to-end.
"""

from __future__ import annotations

import json
from pathlib import Path

from main.agnostic_leak_forensics import _summarize_bool, _summarize_floats
from main.breadth_gap_analysis import _closest_to_pass_score
from main.transfer_near_miss_analysis import _classify


def test_transfer_classification_handles_all_four_cases() -> None:
    assert _classify(0.05, same_dir=True, above_floor=True) == "confirmed"
    assert _classify(0.018, same_dir=True, above_floor=False) == "near_miss_below_floor"
    assert _classify(-1.5, same_dir=False, above_floor=True) == "opposite_direction_above_floor"
    assert _classify(-1e-5, same_dir=False, above_floor=False) == "opposite_direction_subthreshold"


def test_breadth_closest_to_pass_score_orders_correctly() -> None:
    a = {"failed_checks": ["x"], "not_evaluated_checks": ["y"], "gate_outcomes": {"x": 0, "y": 0, "z": 1}}
    b = {"failed_checks": ["x", "y"], "not_evaluated_checks": [], "gate_outcomes": {"x": 0, "y": 0, "z": 1}}
    c = {"failed_checks": ["x"], "not_evaluated_checks": [], "gate_outcomes": {"x": 0, "z": 1}}
    assert _closest_to_pass_score(a) < _closest_to_pass_score(b)
    assert _closest_to_pass_score(a) < _closest_to_pass_score(c)


def test_agnostic_summarize_floats_handles_empty_and_partial() -> None:
    assert _summarize_floats([]) == {"n": 0, "min": None, "max": None, "mean": None, "median": None}
    out = _summarize_floats([0.1, 0.3, None, 0.2])
    assert out["n"] == 3
    assert out["min"] == 0.1
    assert out["max"] == 0.3
    assert out["median"] == 0.2


def test_agnostic_summarize_bool_counts_true_false_ignoring_none() -> None:
    assert _summarize_bool([True, False, None, True]) == {"n": 3, "n_true": 2, "n_false": 1}


def test_released_forensic_artifacts_exist_and_parse() -> None:
    repro = Path(__file__).resolve().parents[3] / "main" / "output" / "repro"
    transfer = json.loads((repro / "transfer_near_miss_analysis.json").read_text())
    assert "n_accepted_claims_with_transfer" in transfer
    assert "transfer_asymmetry" in transfer
    breadth = json.loads((repro / "breadth_gap_analysis.json").read_text())
    assert "n_zero_acceptance_cells" in breadth
    assert "priority_targets" in breadth
    agnostic = json.loads((repro / "agnostic_leak_forensics.json").read_text())
    assert "per_condition" in agnostic
    assert "Goodhart" in agnostic["warning"]
