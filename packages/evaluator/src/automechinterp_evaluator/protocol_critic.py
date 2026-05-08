"""Automated ProtocolCritic for red-teaming protocols before execution.

V12: Implements automated checks for common protocol weaknesses:
underpowered grids, ambiguous metrics, insufficient controls,
scope creep potential, missing fields, exception TTL enforcement
(pitfall #53), distributed computation warnings (pitfall #63),
and CI contract validation (pitfall #74).
"""

from __future__ import annotations

from typing import Any

from .constants import (
    ALLOWED_INTERVENTION_LEVELS,
    ALLOWED_PATCH_MODES,
    MODEL_REGISTRY,
    MANDATORY_CONTROL_FAMILIES,
    TASK_REGISTRY,
)


def critique_protocol(protocol: dict[str, Any]) -> dict[str, Any]:
    """Automated protocol critique — returns warnings and blockers.

    Returns a dict with:
        - blockers: list of critical issues that should prevent execution
        - warnings: list of non-critical issues that weaken the study
        - suggestions: list of improvements that would strengthen the study
        - score: overall quality score (0-100)
    """
    blockers: list[str] = []
    warnings: list[str] = []
    suggestions: list[str] = []

    unit = protocol.get("unit_of_work", {})
    grid = protocol.get("execution_grid", {})
    gates = protocol.get("stage_gates", {})
    stat_policy = protocol.get("statistical_policy", {})
    sample_policy = protocol.get("sample_size_policy", {})
    control_policy = protocol.get("control_policy", {})

    # --- Scope checks ---
    task_id = unit.get("task_id", "")
    if task_id and task_id not in TASK_REGISTRY:
        blockers.append(f"Unknown task_id '{task_id}' — not in TASK_REGISTRY")

    model_id = unit.get("model_id", "")
    if model_id and model_id.lower() not in MODEL_REGISTRY:
        warnings.append(f"Model '{model_id}' not in MODEL_REGISTRY — may need model_spec fallback")

    if not protocol.get("frozen", False):
        blockers.append("Protocol is not frozen — set 'frozen: true' before execution")

    # --- Grid adequacy ---
    seeds = grid.get("seeds", [])
    if len(seeds) < 3:
        warnings.append(f"Only {len(seeds)} seeds — recommend ≥3 for robustness")

    prompt_variants = grid.get("prompt_variants", [])
    if len(prompt_variants) < 3:
        warnings.append(f"Only {len(prompt_variants)} prompt variants — recommend ≥3")
    if len(prompt_variants) < 4:
        suggestions.append("Consider using ≥4 prompt variants for stronger robustness")

    methods = grid.get("methods", [])
    if len(methods) < 2:
        blockers.append(f"Only {len(methods)} method(s) — require ≥2 for method sensitivity")

    resamples = grid.get("resample_ids", [])
    if len(resamples) < 2:
        warnings.append(f"Only {len(resamples)} resample(s) — recommend ≥2")

    # --- Power analysis ---
    min_examples = sample_policy.get("min_examples_per_cell", 0)
    if min_examples < 20:
        warnings.append(f"min_examples_per_cell={min_examples} — recommend ≥20 for adequate power")

    power_target = sample_policy.get("power_target", 0)
    if power_target < 0.8:
        warnings.append(f"power_target={power_target} — recommend ≥0.8")

    total_cells = len(seeds) * len(prompt_variants) * len(resamples) * len(methods)
    if total_cells < 8:
        warnings.append(f"Total grid cells = {total_cells} — may be underpowered (recommend ≥8)")

    # --- Control checks ---
    required_controls = control_policy.get("required_families", [])
    missing_controls = set(MANDATORY_CONTROL_FAMILIES) - set(required_controls)
    if missing_controls:
        warnings.append(f"Missing control families: {sorted(missing_controls)}")

    # --- Gate thresholds ---
    min_causal = gates.get("min_causal_effect", 0)
    if min_causal <= 0:
        warnings.append("min_causal_effect ≤ 0 — any positive effect passes (weak)")

    min_spec = gates.get("min_specificity_ratio", 0)
    if min_spec < 5.0:
        suggestions.append(f"min_specificity_ratio={min_spec} — consider ≥5.0 for Stage 2+")

    # --- Bidirectional check ---
    if not gates.get("require_bidirectional", False):
        suggestions.append(
            "Consider setting require_bidirectional: true to enforce both "
            "noising and denoising methods (addresses pitfall #19)"
        )

    # --- Statistical rigor ---
    alpha = stat_policy.get("alpha", 0.05)
    if alpha > 0.05:
        warnings.append(f"alpha={alpha} — recommend ≤0.05")

    multiplicity = stat_policy.get("multiplicity_method", "")
    if "bonferroni" not in multiplicity.lower() and "benjamini" not in multiplicity.lower():
        suggestions.append("Consider using benjamini-hochberg or holm-bonferroni for multiplicity correction")

    # --- Cross-model ---
    if not gates.get("cross_model_rank_stability_tau"):
        suggestions.append(
            "No cross-model rank stability gate configured — consider adding "
            "for stronger generalization claims"
        )

    # --- Exception TTL check (Pitfall #53) ---
    exceptions = protocol.get("exceptions", [])
    for exc in exceptions:
        if isinstance(exc, dict):
            ttl = exc.get("ttl_days")
            if ttl is None:
                warnings.append(
                    f"Exception '{exc.get('description', 'unnamed')}' has no TTL — "
                    f"exceptions must expire (pitfall #53)"
                )
            elif isinstance(ttl, (int, float)) and ttl > 90:
                suggestions.append(
                    f"Exception TTL={ttl} days is >90 — consider shorter TTL"
                )

    # --- Distributed computation warning (Pitfall #63) ---
    intervention_levels = protocol.get("intervention_levels", [])
    if intervention_levels and len(intervention_levels) == 1:
        warnings.append(
            f"Only one intervention level ({intervention_levels[0]}) — "
            f"consider testing at multiple granularities to avoid ignoring "
            f"distributed computation (pitfall #63)"
        )

    # --- CI contract check (Pitfall #74) ---
    if not protocol.get("ci_contract", {}).get("enabled"):
        suggestions.append(
            "No CI contract configured — consider adding ci_contract.enabled: true "
            "to enforce automated scientific contract checks (pitfall #74)"
        )

    # --- Compute score ---
    score = 100
    score -= len(blockers) * 20
    score -= len(warnings) * 5
    score -= len(suggestions) * 1
    score = max(0, min(100, score))

    return {
        "blockers": blockers,
        "warnings": warnings,
        "suggestions": suggestions,
        "score": score,
        "n_blockers": len(blockers),
        "n_warnings": len(warnings),
        "n_suggestions": len(suggestions),
        "verdict": "BLOCK" if blockers else ("WARN" if warnings else "PASS"),
    }


def format_critic_report(critique: dict[str, Any]) -> str:
    """Format critique as a readable markdown report."""
    lines = [
        "# Protocol Critic Report",
        "",
        f"**Verdict**: {critique['verdict']}",
        f"**Score**: {critique['score']}/100",
        "",
    ]

    if critique["blockers"]:
        lines.append("## ❌ Blockers (must fix before execution)")
        lines.append("")
        for b in critique["blockers"]:
            lines.append(f"- {b}")
        lines.append("")

    if critique["warnings"]:
        lines.append("## ⚠️ Warnings")
        lines.append("")
        for w in critique["warnings"]:
            lines.append(f"- {w}")
        lines.append("")

    if critique["suggestions"]:
        lines.append("## 💡 Suggestions")
        lines.append("")
        for s in critique["suggestions"]:
            lines.append(f"- {s}")
        lines.append("")

    return "\n".join(lines)
