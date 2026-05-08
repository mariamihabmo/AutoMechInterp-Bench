"""Regression test: ``evaluate_bundle_records()`` must refuse to return a
partial summary when any bundle in the input roots fails to evaluate.

History (F-020 in ``methodology/audit/findings_inventory.md``): the
function in ``main/_bundle_analysis.py`` accumulates per-bundle errors
into a list and raises ``RuntimeError`` at the end of the loop with a
message naming each broken bundle. The failure path was unexercised by
any test, so a future refactor (for example, "let me just log and skip
the broken bundle so my new pipeline keeps moving") could silently
regress to producing a partial summary --- which would silently move
the released headline numbers without any other signal.

This test pins the contract by constructing a tiny temporary root with
two sub-directories: one that looks like a bundle (has the three
required files) but whose ``protocol.yaml`` is invalid YAML, and one
that contains the trio but with a non-conforming evaluation result.
The test asserts that ``evaluate_bundle_records()`` raises
``RuntimeError`` mentioning the broken bundle path. It does NOT assert
on the exact error message text, so future improvements to the message
remain free.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from main._bundle_analysis import evaluate_bundle_records


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def test_evaluate_bundle_records_raises_on_broken_bundle(tmp_path: Path) -> None:
    """A bundle whose ``protocol.yaml`` cannot be parsed must cause
    ``evaluate_bundle_records()`` to raise ``RuntimeError`` rather than
    silently returning a partial summary."""
    bundle_root = tmp_path / "broken_root"
    broken = bundle_root / "deliberately_invalid_v0_test-model"
    # All three sentinel files must exist for ``find_bundle_dirs`` to
    # consider the directory a bundle (otherwise it would simply be
    # skipped, which is a different code path and not what F-020 is
    # locking down).
    _write(broken / "protocol.yaml", "this: is: not: valid yaml: [unterminated")
    _write(broken / "hypothesis.jsonl", "{}\n")
    _write(broken / "evaluation_result.json", "{}\n")

    with pytest.raises(RuntimeError) as excinfo:
        evaluate_bundle_records(bundle_root)

    # The error message should name the broken bundle so an operator can
    # find it without grepping. We check substring containment, not
    # exact text, so that the message can be improved without breaking
    # this test.
    msg = str(excinfo.value)
    assert "deliberately_invalid_v0_test-model" in msg, (
        f"Expected broken bundle name in error message, got: {msg!r}"
    )


def test_evaluate_bundle_records_raises_on_missing_required_artifact(tmp_path: Path) -> None:
    """Complement to the test above: a bundle whose ``evaluation_result.json``
    exists but is malformed JSON should also raise. (Bundles that are
    missing a required artifact are silently skipped by
    ``find_bundle_dirs`` --- that is the intended behaviour for
    "directory exists but is not a bundle" --- so this test exercises a
    third broken-state distinct from invalid-YAML.)"""
    bundle_root = tmp_path / "broken_root_2"
    broken = bundle_root / "malformed_eval_v0_test-model"
    _write(broken / "protocol.yaml", "unit_of_work:\n  task_id: t\n  model_id: m\n")
    _write(broken / "hypothesis.jsonl", "{}\n")
    _write(broken / "evaluation_result.json", "this is not json")

    with pytest.raises(RuntimeError) as excinfo:
        evaluate_bundle_records(bundle_root)
    assert "malformed_eval_v0_test-model" in str(excinfo.value)


def test_evaluate_bundle_records_returns_empty_for_empty_root(tmp_path: Path) -> None:
    """Sanity check: a root with no bundle-shaped sub-directories must
    return an empty list (not raise). This pins the boundary so that
    "no bundles at all" is distinguishable from "some bundles broken"."""
    empty_root = tmp_path / "empty_root"
    empty_root.mkdir()
    (empty_root / "not_a_bundle").mkdir()
    (empty_root / "not_a_bundle" / "README.md").write_text("not a bundle\n")

    records = evaluate_bundle_records(empty_root)
    assert records == []
