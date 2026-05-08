#!/usr/bin/env python3
"""Forensic analysis of evaluator-agnostic stress leaks.

The headline 4/40 evaluator-agnostic latent leakage figure under the full
contract is correct but uninformative on its own: it does not identify
*which structural patterns* in the latent generator slipped
through. This analyzer projects the per-leak detail (now persisted by
``main/stress_test_agnostic.py``) into a more compact summary form.

For each condition (``full_contract``, ``no_controls_suite``,
``no_robustness_suite``), it summarizes the latent factors of each
leaked negative across five axes:

* ``latent_signal``  -- effective treatment magnitude
* ``latent_control`` -- amount of control-prompt leakage
* ``latent_method_dispersion`` -- across-method variance
* ``latent_confirmatory_decay`` -- decay of confirmatory evidence
* ``latent_direction_flip`` -- whether the prediction-effect direction
  was flipped relative to the source

The script then identifies whether the leaks share a common structural
profile (for example, "all leaks have low control leakage and stable
direction") and *suggests* (does NOT apply) a contract addendum that
would close the observed leaks. Suggestions are explicitly framed as
hypotheses for future contract-design discussion, not as edits to the
released constants, because tightening thresholds against a known leak
set is exactly the Goodhart trap the agnostic stress regime exists to
detect.

Inputs:

* ``main/output/real_multi_task/ioi_v0_gpt2-small/stress_test_agnostic.json``
  (the only released agnostic-stress bundle today)

Outputs:

* ``main/output/repro/agnostic_leak_forensics.json``
* ``main/output/repro/agnostic_leak_forensics.md``
"""

from __future__ import annotations

import json
import statistics
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
AGNOSTIC_PATH = (
    ROOT / "main" / "output" / "real_multi_task" / "ioi_v0_gpt2-small" / "stress_test_agnostic.json"
)
REPRO_DIR = ROOT / "main" / "output" / "repro"


def _summarize_floats(values: list[float | None]) -> dict[str, float | None]:
    real = [v for v in values if v is not None]
    if not real:
        return {"n": 0, "min": None, "max": None, "mean": None, "median": None}
    return {
        "n": len(real),
        "min": min(real),
        "max": max(real),
        "mean": statistics.fmean(real),
        "median": statistics.median(real),
    }


def _summarize_bool(values: list[bool | None]) -> dict[str, int]:
    real = [v for v in values if v is not None]
    return {
        "n": len(real),
        "n_true": sum(1 for v in real if v),
        "n_false": sum(1 for v in real if not v),
    }


def analyze() -> dict[str, Any]:
    payload = json.loads(AGNOSTIC_PATH.read_text())
    conditions = payload["conditions"]
    total_negatives = payload.get("negatives", 0)

    per_condition = {}
    for cond_name, cond in conditions.items():
        leaked_negs = cond.get("leaked_negatives", [])
        per_condition[cond_name] = {
            "leaked": cond["leaked"],
            "total": cond["total"],
            "false_accept_rate": cond["false_accept_rate"],
            "false_accept_rate_ci95": cond["false_accept_rate_ci95"],
            "leaked_count_with_per_leak_data": len(leaked_negs),
            "latent_signal": _summarize_floats([n.get("latent_signal") for n in leaked_negs]),
            "latent_control": _summarize_floats([n.get("latent_control") for n in leaked_negs]),
            "latent_method_dispersion": _summarize_floats(
                [n.get("latent_method_dispersion") for n in leaked_negs]
            ),
            "latent_confirmatory_decay": _summarize_floats(
                [n.get("latent_confirmatory_decay") for n in leaked_negs]
            ),
            "latent_direction_flip": _summarize_bool(
                [n.get("latent_direction_flip") for n in leaked_negs]
            ),
            "leaked_negatives": leaked_negs,
        }

    full = per_condition.get("full_contract", {})
    leaks = full.get("leaked_negatives", [])

    # Structural pattern hypotheses, expressed only as observations -- no
    # contract changes are made or recommended here.
    suggested_addenda: list[dict[str, str]] = []
    if leaks:
        signal = full["latent_signal"]
        control = full["latent_control"]
        flip = full["latent_direction_flip"]
        if signal.get("n") and signal.get("min") is not None:
            suggested_addenda.append(
                {
                    "observation": (
                        f"Full-contract leaks have latent_signal in "
                        f"[{signal['min']:.4f}, {signal['max']:.4f}] (median "
                        f"{signal['median']:.4f}). The latent generator's "
                        f"signal range is [0.01, 0.08]."
                    ),
                    "candidate_addendum": (
                        "Tighten the practical-effect-size floor or require "
                        "confirmatory evidence at >= max(signal) latent magnitude "
                        "before granting single_model_confirmed. NOT APPLIED -- "
                        "applying this against the leak set would risk overfitting "
                        "the contract to the agnostic generator's known sample."
                    ),
                }
            )
        if control.get("n") and control.get("max") is not None:
            suggested_addenda.append(
                {
                    "observation": (
                        f"Full-contract leaks have latent_control in "
                        f"[{control['min']:.4f}, {control['max']:.4f}] (median "
                        f"{control['median']:.4f})."
                    ),
                    "candidate_addendum": (
                        "Add a control-leakage floor that disqualifies any claim "
                        "whose control effect exceeds a tighter fraction of its "
                        "treatment effect. NOT APPLIED for the same Goodhart reason."
                    ),
                }
            )
        if flip.get("n") and flip.get("n_true", 0) == 0:
            suggested_addenda.append(
                {
                    "observation": (
                        "All full-contract leaks have latent_direction_flip = False, "
                        "i.e. the direction was stable relative to the source."
                    ),
                    "candidate_addendum": (
                        "This is informative for diagnosis but does NOT motivate a "
                        "contract addendum: the stable-direction subset is precisely "
                        "what a true positive should look like. Tightening here would "
                        "weaken the benchmark, not strengthen it."
                    ),
                }
            )

    return {
        "source_artifact": str(AGNOSTIC_PATH.relative_to(ROOT)),
        "total_negatives": total_negatives,
        "per_condition": per_condition,
        "suggested_addenda_for_design_discussion_only": suggested_addenda,
        "applied_contract_changes": [],
        "warning": (
            "Suggestions in 'suggested_addenda_for_design_discussion_only' are "
            "structural observations from the released leak set. Applying them as "
            "actual gate changes would tune the contract to the agnostic generator's "
            "known leaks, which is the exact Goodhart trap the agnostic regime "
            "exists to detect. Any future contract change motivated by these "
            "observations should be designed against a *new* generator that did "
            "not produce the leaks, with the original generator preserved as a "
            "regression check."
        ),
    }


def format_md(payload: dict[str, Any]) -> str:
    lines = [
        "# Evaluator-Agnostic Stress Leak Forensics",
        "",
        f"- Source: `{payload['source_artifact']}`",
        f"- Total negatives per condition: **{payload['total_negatives']}**",
        "",
        "## Per-condition leak summary",
        "",
        "| condition | leaked | FAR | leaks with per-leak data |",
        "|---|---|---|---|",
    ]
    for cond_name, cond in payload["per_condition"].items():
        lines.append(
            f"| `{cond_name}` | {cond['leaked']}/{cond['total']} | "
            f"{cond['false_accept_rate'] * 100:.1f}% | "
            f"{cond['leaked_count_with_per_leak_data']} |"
        )
    lines.extend(
        [
            "",
            "_If `leaks with per-leak data` < `leaked`, regenerate "
            "`stress_test_agnostic.json` after the per-leak enrichment "
            "in `main/stress_test_agnostic.py` to populate the diagnostic._",
            "",
        ]
    )

    full = payload["per_condition"].get("full_contract", {})
    leaks = full.get("leaked_negatives", [])
    if leaks:
        lines.extend(
            [
                "## Full-contract leak detail",
                "",
                "| hypothesis | tier | signal | control | dispersion | decay | flip |",
                "|---|---|---|---|---|---|---|",
            ]
        )
        for n in leaks:
            lines.append(
                f"| `{n['hypothesis_id']}` | `{n.get('evidence_tier', '')}` | "
                f"{n.get('latent_signal', float('nan')):.4f} | "
                f"{n.get('latent_control', float('nan')):.4f} | "
                f"{n.get('latent_method_dispersion', float('nan')):.4f} | "
                f"{n.get('latent_confirmatory_decay', float('nan')):.4f} | "
                f"{n.get('latent_direction_flip', False)} |"
            )
        lines.append("")

    lines.extend(["## Structural observations (DESIGN DISCUSSION ONLY)", ""])
    if payload["suggested_addenda_for_design_discussion_only"]:
        for s in payload["suggested_addenda_for_design_discussion_only"]:
            lines.append(f"- **Observation:** {s['observation']}")
            lines.append(f"  - **Candidate addendum:** {s['candidate_addendum']}")
        lines.append("")
    else:
        lines.append("_No structural observations: regenerate the agnostic stress artifact first._")
        lines.append("")

    lines.extend(
        [
            "## Why no contract changes are applied here",
            "",
            payload["warning"],
            "",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    REPRO_DIR.mkdir(parents=True, exist_ok=True)
    payload = analyze()
    out_json = REPRO_DIR / "agnostic_leak_forensics.json"
    out_md = REPRO_DIR / "agnostic_leak_forensics.md"
    out_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    out_md.write_text(format_md(payload))
    print(str(out_json))


if __name__ == "__main__":
    main()
