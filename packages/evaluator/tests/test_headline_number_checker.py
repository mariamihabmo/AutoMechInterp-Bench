"""Regression tests for the cross-document headline drift checker.

The checker is intentionally a narrow paper/README canary, but it now
guards several externally visible contradictions that previously survived
because the script only checked abstracts. These tests exercise the
paper-body checks directly with synthetic text so future edits cannot
silently reintroduce stale transfer, failure-total, or audit-count
claims.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
CHECKER_PATH = REPO_ROOT / "tools" / "check_headline_numbers.py"


def _load_checker():
    spec = importlib.util.spec_from_file_location("check_headline_numbers", CHECKER_PATH)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _headlines() -> dict:
    return {
        "bundles": 33,
        "claims": 100,
        "accepted": 23,
        "tasks_with_accepted": 7,
        "tasks_total": 8,
        "transfer_confirmed": 11,
        "transfer_tested": 23,
        "transfer_bundles_tested": 16,
        "accepted_in_transfer_tested_bundles": 23,
        "accepted_with_transfer_effect": 23,
        "accepted_transfer_failures": 12,
        "statistics_plus_robustness_failures": 204,
        "family_total_failures": 319,
        "gate_counts": {
            "causal_effect": 43,
            "robustness": 44,
            "multiplicity": 46,
            "confirmatory_ci": 39,
            "confirmatory_present": 3,
            "method_sensitivity": 29,
            "negative_controls": 34,
            "cross_model_transfer": 21,
        },
        "gate_family_counts": {
            "statistics": 131,
            "robustness": 73,
            "causal": 43,
            "controls": 51,
            "transfer": 21,
        },
        "audit_command_count": 43,
        "prompt_variant_affected_accepted": 25,
        "prompt_variant_repair_covered": 25,
        "prompt_variant_repair_retained": 19,
        "prompt_variant_repair_demoted": 6,
        "maintainer_pilot_submissions": 2,
        "v1_accepted_before": 23,
        "v1_accepted_after": 14,
        "v1_tasks_after": 3,
        "high_power_prompt_examples": 40,
        "high_power_prompt_covered": 23,
        "high_power_prompt_retained": 20,
        "high_power_prompt_demoted": 3,
        "high_power_prompt_holdout_pass": 16,
        "high_power_prompt_checks_pass": 51,
        "high_power_prompt_checks_total": 55,
    }


def _paper_text(
    *,
    transfer_sentence: str = "The accepted transfer set reaches `cross_model_confirmed` (11/23).",
    failure_sentence: str = "Statistics and robustness account for 204/319 family-level failures.",
    family_sentence: str = (
        "Gate family counts are statistics 131, robustness 73, causal 43, "
        "controls 51 and transfer 21."
    ),
    gate_sentence: str = (
        "Top failed gates include causal_effect (43), robustness (44), "
        "multiplicity (46), confirmatory_ci (39), method_sensitivity (29), "
        "negative_controls (34), and cross_model_transfer (21)."
    ),
    audit_sentence: str = "The current audit contract contains 43 commands.",
    prompt_sentence: str = (
        "Unsupported nominal variants appeared in artifacts containing 25 accepted claims; "
        "task-supported repair reruns retain 19/25 and demote 6/25."
    ),
    v1_sentence: str = (
        "The hardened candidate retains only 14/23 current accepted claims and accepted claims in 3/8 tasks."
    ),
    high_power_prompt_sentence: str = (
        "A higher-power n=40 prompt-holdout diagnostic retains 20/23 original accepted claims; "
        "only 16/20 retained claims pass all held-out prompts (51/55 retained-claim holdout checks)."
    ),
) -> str:
    return "\n".join(
        [
            "This paper evaluates 33 bundles and 100 claims.",
            "The verifier accepts 23 accepted claims.",
            "Acceptance remains uneven: accepted claims appear in 7/8 tasks.",
            transfer_sentence,
            (
                "Released transfer diagnostics now cover 23 accepted claims inside "
                "16 transfer-tested bundles; 23 accepted claims have transfer-effect rows."
            ),
            "The remaining transfer-effect rows are mostly negative: 12 accepted claims fail direction or floor.",
            failure_sentence,
            family_sentence,
            gate_sentence,
            audit_sentence,
            prompt_sentence,
            v1_sentence,
            high_power_prompt_sentence,
        ]
    )


def _check_text(tmp_path: Path, text: str) -> list[str]:
    paper = tmp_path / "paper_body.tex"
    paper.write_text(text)
    return _load_checker().check_paper(paper, _headlines())


def test_checker_accepts_current_canonical_paper_stub(tmp_path: Path) -> None:
    assert _check_text(tmp_path, _paper_text()) == []


def test_checker_rejects_stale_readme_headlines(tmp_path: Path, monkeypatch) -> None:
    checker = _load_checker()
    readme = tmp_path / "README.md"
    readme.write_text(
        "\n".join(
            [
                "- `33` evaluated bundles",
                "- `100` evaluated claims",
                "- `28` accepted claims",
                "- **9 / 26** accepted claims with transfer-effect rows currently reach `cross_model_confirmed`",
            ]
        )
    )
    monkeypatch.setattr(checker, "ROOT", tmp_path)

    failures = checker.check_readme(_headlines())

    assert any("`23` accepted claims" in failure for failure in failures)
    assert any("stale pre-prompt-promotion accepted count" in failure for failure in failures)
    assert any("stale pre-prompt-promotion transfer fraction" in failure for failure in failures)


def test_checker_accepts_current_transfer_prose_style(tmp_path: Path) -> None:
    failures = _check_text(
        tmp_path,
        _paper_text(
            transfer_sentence=(
                "Under the current release, 11/23 accepted claims with transfer "
                "effects reach `cross_model_confirmed`."
            )
        ),
    )

    assert failures == []


def test_checker_rejects_stale_zero_transfer_language(tmp_path: Path) -> None:
    failures = _check_text(
        tmp_path,
        _paper_text(
            transfer_sentence="No accepted claim currently clears `cross_model_confirmed`."
        ),
    )

    assert any("stale transfer phrase" in failure for failure in failures)


def test_checker_rejects_stale_failure_totals(tmp_path: Path) -> None:
    failures = _check_text(
        tmp_path,
        _paper_text(
            failure_sentence="Statistics and robustness account for 234/389 family-level failures."
        ),
    )

    assert any("statistics+robustness failures=234" in failure for failure in failures)
    assert any("family-level failures=389" in failure for failure in failures)


def test_checker_rejects_stale_gate_family_counts(tmp_path: Path) -> None:
    failures = _check_text(
        tmp_path,
        _paper_text(
            family_sentence=(
                "Gate family counts are statistics 132, robustness 74, causal 43, "
                "controls 46, and transfer 6."
            )
        ),
    )

    assert any("statistics family count 132" in failure for failure in failures)


def test_checker_rejects_stale_audit_command_count(tmp_path: Path) -> None:
    failures = _check_text(
        tmp_path,
        _paper_text(audit_sentence="All 19 audit commands passed."),
    )

    assert any("cites 19 audit commands" in failure for failure in failures)


def test_checker_rejects_stale_high_power_prompt_counts(tmp_path: Path) -> None:
    failures = _check_text(
        tmp_path,
        _paper_text(
            high_power_prompt_sentence=(
                "A higher-power n=40 prompt-holdout diagnostic retains 22/23 original accepted claims; "
                "only 18/22 retained claims pass all held-out prompts (55/61 retained-claim holdout checks)."
            ),
        ),
    )

    assert any("high-power prompt retention 22/23" in failure for failure in failures)
    assert any("high-power prompt holdout 18/22" in failure for failure in failures)
    assert any("high-power prompt checks 55/61" in failure for failure in failures)


def test_checker_does_not_confuse_unrelated_n48_with_high_power_prompt_n40(tmp_path: Path) -> None:
    failures = _check_text(
        tmp_path,
        _paper_text(
            high_power_prompt_sentence=(
                "A preregistered n=48 fact-recall repair appears earlier in the same abstract. "
                "A prospective higher-power prompt-holdout diagnostic at 40 examples per cell "
                "retains 20/23 original accepted claims; only 16/20 retained claims pass all "
                "held-out prompts (51/55 retained-claim holdout checks)."
            ),
        ),
    )

    assert failures == []


def test_checker_rejects_stale_maintainer_pilot_count(tmp_path: Path) -> None:
    failures = _check_text(
        tmp_path,
        _paper_text()
        + "\nCurrent state: 1 `maintainer_pilot` submission is present.",
    )

    assert any("maintainer_pilot submissions" in failure for failure in failures)


def test_checker_rejects_stale_transfer_diagnostics_counts(tmp_path: Path) -> None:
    failures = _check_text(
        tmp_path,
        _paper_text().replace(
            "Released transfer diagnostics now cover 23 accepted claims inside "
            "16 transfer-tested bundles; 23 accepted claims have transfer-effect rows.",
            "Released transfer diagnostics now cover 25 accepted claims inside "
            "14 transfer-tested bundles; 22 accepted claims have transfer-effect rows.",
        ),
    )

    assert any("25 accepted claims inside transfer-tested" in failure for failure in failures)
    assert any("14 transfer-tested bundles" in failure for failure in failures)
    assert any("22 accepted claims with transfer-effect" in failure for failure in failures)


def test_checker_rejects_stale_transfer_failure_tail_count(tmp_path: Path) -> None:
    failures = _check_text(
        tmp_path,
        _paper_text().replace(
            "12 accepted claims fail direction or floor",
            "14 accepted claims fail direction or floor",
        ),
    )

    assert any("14 accepted transfer direction/floor failures" in failure for failure in failures)
