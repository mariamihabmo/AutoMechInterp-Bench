"""Regression tests for the evidence-tier classifier safe defaults.

These tests lock down the contract documented in
``_classify_evidence_tier``'s docstring: when the ``exploratory_present``
keyword is omitted, the classifier must NOT fall back to inspecting the
``confirmatory_firewall`` gate (which can be trivially True when the
protocol does not require a confirmatory split). The conservative default
is ``False``, so a forgetful caller cannot accidentally promote a claim
to ``single_model_confirmed`` or ``cross_model_confirmed``.

History: this defensive default was introduced after the v2 audit
(``methodology/audit/v2_audit_report.md`` finding F-007) traced the
prior default (``checks.get("confirmatory_firewall") is True``) and
showed it was unsound for protocols where the firewall gate passes
trivially.
"""

from __future__ import annotations

from automechinterp_evaluator.evaluator import _classify_evidence_tier


def _all_pass_checks() -> dict[str, object]:
    """Return a checks dict where every gate (core + optional) passes.

    Uses the canonical gate names from
    ``automechinterp_evaluator.constants.{CORE_GATES, OPTIONAL_GATES}``.
    """
    from automechinterp_evaluator.constants import CORE_GATES, OPTIONAL_GATES
    checks: dict[str, object] = {gate: True for gate in CORE_GATES}
    for gate in OPTIONAL_GATES:
        checks[gate] = True
    return checks


def test_default_exploratory_present_is_conservative_false() -> None:
    """Without an explicit ``exploratory_present`` argument, the classifier
    must not promote a claim above ``causal_plus_robustness`` even when every
    gate (including ``confirmatory_firewall``) passes."""
    checks = _all_pass_checks()
    tier, passed, failed, not_evaluated, _demotion = _classify_evidence_tier(checks)
    # All gates pass, but the classifier was not told an exploratory slice
    # exists, so the highest reachable tier is ``causal_plus_robustness``.
    assert tier == "causal_plus_robustness", (
        f"Expected conservative tier without exploratory_present, got {tier}"
    )
    assert passed is False
    assert failed == []


def test_explicit_exploratory_present_true_enables_single_model_confirmed() -> None:
    """When the caller affirmatively passes ``exploratory_present=True``,
    the classifier may promote to ``single_model_confirmed`` (or higher
    if the cross-model gate is also pass)."""
    checks = _all_pass_checks()
    # Drop the optional cross-model gate to land on single-model tier.
    checks["cross_model_transfer"] = "not_evaluated"
    tier, passed, _, _, _ = _classify_evidence_tier(checks, exploratory_present=True)
    assert tier == "single_model_confirmed"
    assert passed is True


def test_explicit_exploratory_present_true_with_cross_model_reaches_top_tier() -> None:
    checks = _all_pass_checks()
    tier, passed, _, _, _ = _classify_evidence_tier(checks, exploratory_present=True)
    assert tier == "cross_model_confirmed"
    assert passed is True


def test_explicit_exploratory_present_false_caps_at_causal_plus_robustness() -> None:
    checks = _all_pass_checks()
    tier, passed, _, _, _ = _classify_evidence_tier(checks, exploratory_present=False)
    assert tier == "causal_plus_robustness"
    assert passed is False


def test_default_does_not_inspect_confirmatory_firewall_gate() -> None:
    """Direct regression for the F-007 trap: even if ``confirmatory_firewall``
    is explicitly set in ``checks``, omitting ``exploratory_present`` must
    still default to the conservative ``False`` (which caps the tier below
    ``single_model_confirmed``)."""
    checks = _all_pass_checks()
    # Both pass and not_evaluated forms should produce the same conservative tier.
    for firewall_value in (True, False, "not_evaluated"):
        c = dict(checks)
        c["confirmatory_firewall"] = firewall_value
        tier, _, _, _, _ = _classify_evidence_tier(c)  # no exploratory_present
        if firewall_value is False or firewall_value == "not_evaluated":
            # A failed/missing core gate already prevents ``all_core_pass``,
            # so the tier drops further. We only assert the absence of
            # promotion to single/cross-model confirmed.
            assert tier not in ("single_model_confirmed", "cross_model_confirmed")
        else:
            # Firewall pass + omitted ``exploratory_present`` must still
            # cap at ``causal_plus_robustness``.
            assert tier == "causal_plus_robustness", (
                f"With firewall={firewall_value!r}, expected conservative "
                f"tier, got {tier}"
            )
