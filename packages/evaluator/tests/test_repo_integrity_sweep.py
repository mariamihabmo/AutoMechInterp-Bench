"""Regression tests for current-facing integrity-sweep drift detection."""

from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
SWEEP_PATH = REPO_ROOT / "main" / "repo_integrity_sweep.py"


def _load_sweep():
    spec = importlib.util.spec_from_file_location("repo_integrity_sweep", SWEEP_PATH)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_sweep_flags_stale_current_transfer_fraction() -> None:
    sweep = _load_sweep()

    hits = sweep._stale_transfer_fraction_hits(
        "Current evidence: 9/23 accepted claims reach cross_model_confirmed.",
        current_fraction="9/26",
    )

    assert hits == ["stale current transfer fraction 9/23"]


def test_sweep_flags_stale_current_transfer_fraction_with_spaces() -> None:
    sweep = _load_sweep()

    hits = sweep._stale_transfer_fraction_hits(
        "Current evidence: 9 / 23 accepted claims reach cross_model_confirmed.",
        current_fraction="9/26",
    )

    assert hits == ["stale current transfer fraction 9/23"]


def test_sweep_does_not_match_stale_fraction_inside_larger_prompt_fraction() -> None:
    sweep = _load_sweep()

    hits = sweep._stale_transfer_fraction_hits(
        "A high-power prompt diagnostic retained 23/26 accepted claims, "
        "but only 19/23 retained claims pass all held-out prompts.",
        current_fraction="12/26",
    )

    assert hits == []


def test_sweep_allows_historical_transfer_fraction() -> None:
    sweep = _load_sweep()

    hits = sweep._stale_transfer_fraction_hits(
        "The historical 8/12 and 9/23 states were superseded by 9/26.",
        current_fraction="9/26",
    )

    assert hits == []


def test_sweep_flags_stale_current_audit_count() -> None:
    sweep = _load_sweep()

    hits = sweep._stale_audit_count_hits(
        "Current reproducibility audit: 31/31 commands pass.",
        current_count=37,
    )

    assert hits == ["stale current audit command count 31; expected 37"]


def test_sweep_allows_historical_audit_count() -> None:
    sweep = _load_sweep()

    hits = sweep._stale_audit_count_hits(
        "Historical checkpoint: 31/31 commands pass; this is superseded.",
        current_count=37,
    )

    assert hits == []


def test_sweep_audit_count_respects_live_audit_override(monkeypatch) -> None:
    sweep = _load_sweep()
    monkeypatch.setenv("AUTOMECHINTERP_EXPECTED_AUDIT_COMMANDS", "38")

    assert sweep._audit_command_count({"commands": [{}, {}]}) == 38
