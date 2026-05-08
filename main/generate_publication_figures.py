#!/usr/bin/env python3
"""Generate publication figures and release-takeaway artifacts from canonical outputs."""

from __future__ import annotations

import json
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
REPRO_DIR = ROOT / "main" / "output" / "repro"
FIG_DIR = ROOT / "papers" / "submissions" / "shared" / "figures"
SITE_FIG_DIR = ROOT / "site_docs" / "assets" / "generated"
BASE_STRESS_DIR = ROOT / "main" / "output" / "real_multi_task" / "ioi_v0_gpt2-small"

def _load_json(path: Path) -> dict:
    return json.loads(path.read_text())

def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")

def _pretty_condition(name: str) -> str:
    return {
        "full_contract": "Full contract",
        "no_stat_rigor": "No stat rigour",
        "no_robustness_suite": "No robustness",
        "no_controls_suite": "No controls",
        "minimal_gates": "Minimal gates",
    }.get(name, name.replace("_", " "))

def _save_figure(fig: plt.Figure, stem: str) -> list[str]:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    SITE_FIG_DIR.mkdir(parents=True, exist_ok=True)
    saved = []
    for out_dir in (FIG_DIR, SITE_FIG_DIR):
        pdf_path = out_dir / f"{stem}.pdf"
        png_path = out_dir / f"{stem}.png"
        fig.savefig(pdf_path, bbox_inches="tight")
        fig.savefig(png_path, dpi=220, bbox_inches="tight")
        saved.extend([str(pdf_path.relative_to(ROOT)), str(png_path.relative_to(ROOT))])
    plt.close(fig)
    return saved

def make_acceptance_heatmap(accepted_breadth_map: dict, breadth_summary: dict) -> dict:
    total_by_task_model: dict[tuple[str, str], int] = {}
    for row in breadth_summary.get("bundles", []):
        key = (row["task"], row["model"])
        total_by_task_model[key] = total_by_task_model.get(key, 0) + int(row["claims"])

    task_totals = {}
    for task, model_rows in accepted_breadth_map.items():
        claims = sum(total_by_task_model.get((task, model), 0) for model in model_rows)
        accepted = sum(sum(lane_rows.values()) for lane_rows in model_rows.values())
        task_totals[task] = {"claims": claims, "accepted": accepted}

    tasks = sorted(task_totals, key=lambda t: (-task_totals[t]["accepted"], -task_totals[t]["claims"], t))
    models = sorted({model for model_rows in accepted_breadth_map.values() for model in model_rows})

    matrix = np.zeros((len(tasks), len(models)))
    annotations: list[list[str]] = []
    for i, task in enumerate(tasks):
        row_annotations = []
        for j, model in enumerate(models):
            accepted = sum(accepted_breadth_map.get(task, {}).get(model, {}).values())
            claims = total_by_task_model.get((task, model), 0)
            matrix[i, j] = (accepted / claims) if claims else 0.0
            row_annotations.append(f"{accepted}/{claims}" if claims else "0/0")
        annotations.append(row_annotations)

    fig, ax = plt.subplots(figsize=(7.4, 4.9))
    image = ax.imshow(matrix, aspect="auto")
    ax.set_xticks(np.arange(len(models)))
    ax.set_yticks(np.arange(len(tasks)))
    ax.set_xticklabels(models)
    ax.set_yticklabels([task.replace("_v0", "").replace("_", " ") for task in tasks])
    ax.set_xlabel("Model family")
    ax.set_ylabel("Task")
    ax.set_title("Accepted claims cluster in a narrow task-model slice")
    cbar = fig.colorbar(image, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label("Acceptance rate")

    max_value = float(matrix.max()) if matrix.size else 0.0
    threshold = max_value / 2.0 if max_value else 0.0
    for i in range(len(tasks)):
        for j in range(len(models)):
            text_color = "white" if matrix[i, j] > threshold else "black"
            ax.text(j, i, annotations[i][j], ha="center", va="center", color=text_color, fontsize=9)

    fig.tight_layout()
    saved = _save_figure(fig, "accepted_breadth_heatmap")
    return {
        "tasks": tasks,
        "models": models,
        "matrix": matrix.tolist(),
        "annotations": annotations,
        "saved_files": saved,
    }

def make_contract_vs_stress_figure(policy: dict, suite_targeted: dict, agnostic: dict) -> dict:
    ordered_conditions = [
        "full_contract",
        "no_stat_rigor",
        "no_robustness_suite",
        "no_controls_suite",
    ]
    released = [policy["conditions"][name]["acceptance_rate"] for name in ordered_conditions]
    suite = [suite_targeted["conditions"][name]["false_accept_rate"] for name in ordered_conditions]
    agnostic_series = [
        agnostic["conditions"].get(name, {}).get("false_accept_rate", float("nan"))
        for name in ordered_conditions
    ]

    x = np.arange(len(ordered_conditions))
    width = 0.24

    fig, ax = plt.subplots(figsize=(7.8, 4.9))
    bars1 = ax.bar(x - width, released, width, label="Released acceptance")
    bars2 = ax.bar(x, suite, width, label="Suite-targeted FAR")
    bars3 = ax.bar(x + width, agnostic_series, width, label="Evaluator-agnostic FAR")

    ax.set_xticks(x)
    ax.set_xticklabels([_pretty_condition(name) for name in ordered_conditions])
    ax.set_ylabel("Rate")
    ax.set_ylim(0.0, 0.45)
    ax.set_title("Released-claim sensitivity differs from synthetic false-accept sensitivity")
    ax.legend()

    for bars in (bars1, bars2, bars3):
        for bar in bars:
            height = bar.get_height()
            if math.isnan(height):
                continue
            ax.annotate(
                f"{height * 100:.0f}%",
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=8,
            )

    fig.tight_layout()
    saved = _save_figure(fig, "contract_vs_stress_rates")
    return {
        "conditions": ordered_conditions,
        "released_acceptance": released,
        "suite_targeted_far": suite,
        "agnostic_far": agnostic_series,
        "saved_files": saved,
    }

def make_failure_family_figure(failure_family_counts: dict[str, int]) -> dict:
    ordered = sorted(failure_family_counts.items(), key=lambda kv: (-kv[1], kv[0]))
    families = [name for name, _ in ordered]
    counts = [count for _, count in ordered]

    fig, ax = plt.subplots(figsize=(7.0, 4.6))
    bars = ax.bar(families, counts)
    ax.set_ylabel("Failed-gate count")
    ax.set_xlabel("Gate family")
    ax.set_title("Statistics and robustness dominate released-claim failures")
    ax.tick_params(axis="x", rotation=25)

    for bar, count in zip(bars, counts):
        ax.annotate(
            str(count),
            xy=(bar.get_x() + bar.get_width() / 2, count),
            xytext=(0, 3),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=8,
        )

    fig.tight_layout()
    saved = _save_figure(fig, "failure_family_counts")
    return {
        "families": families,
        "counts": counts,
        "saved_files": saved,
    }

def make_co_failure_heatmap(co_failure: dict) -> dict:
    """Render the gate-by-gate co-failure heatmap.

    The diagonal reports the marginal count of claims failing each gate;
    off-diagonal entries report the count of claims failing both gates.
    The dominant fragility cluster is annotated in the figure title so the
    headline takeaway is legible without reading the JSON. The
    denominator is claims with at least one failed gate because accepted
    single-model claims can still fail optional transfer confirmation.
    """
    gates = co_failure["gates"]
    matrix = np.array(co_failure["matrix"], dtype=float)
    n = len(gates)

    fig, ax = plt.subplots(figsize=(8.4, 6.4))
    image = ax.imshow(matrix, aspect="auto", cmap="viridis")
    ax.set_xticks(np.arange(n))
    ax.set_yticks(np.arange(n))
    short_labels = [g.replace("_", "\n") for g in gates]
    ax.set_xticklabels(short_labels, rotation=35, ha="right", fontsize=8)
    ax.set_yticklabels(short_labels, fontsize=8)
    cbar = fig.colorbar(image, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label("Claims failing both gates")

    cluster = co_failure.get("dominant_fragility_cluster")
    if cluster:
        gate_count = int(cluster.get("size", len(cluster.get("failed_gates", []))))
        denominator = int(co_failure.get("claims_with_failed_gates") or co_failure.get("n_failed") or 0)
        fraction = float(
            cluster.get(
                "fraction_of_claims_with_failed_gates",
                cluster.get("fraction_of_failed_claims", 0.0),
            )
        )
        title = (
            f"Gate co-failures: a single {gate_count}-gate pattern accounts for "
            f"{cluster['claims_with_this_pattern']}/{denominator} "
            f"({fraction * 100:.0f}%) claims with failed gates"
        )
    else:
        title = "Gate co-failures across released claims"
    ax.set_title(title, fontsize=10)

    max_value = float(matrix.max()) if matrix.size else 0.0
    threshold = max_value / 2.0 if max_value else 0.0
    for i in range(n):
        for j in range(n):
            value = int(matrix[i, j])
            if value == 0:
                continue
            color = "white" if matrix[i, j] < threshold else "black"
            ax.text(j, i, str(value), ha="center", va="center", color=color, fontsize=7)

    fig.tight_layout()
    saved = _save_figure(fig, "gate_cofailure_heatmap")
    return {
        "gates": gates,
        "matrix": matrix.tolist(),
        "dominant_fragility_cluster": cluster,
        "saved_files": saved,
    }

def main() -> None:
    breadth = _load_json(REPRO_DIR / "benchmark_breadth_summary.json")
    field = _load_json(REPRO_DIR / "field_level_findings.json")
    figure_inputs = _load_json(REPRO_DIR / "figure_inputs.json")
    transfer = _load_json(REPRO_DIR / "transfer_results_summary.json")
    community = _load_json(ROOT / "main" / "output" / "community_submissions" / "community_value_summary.json")
    stress_targeted = _load_json(BASE_STRESS_DIR / "stress_test_ablation.json")
    stress_agnostic = _load_json(BASE_STRESS_DIR / "stress_test_agnostic.json")
    stress_red = _load_json(BASE_STRESS_DIR / "stress_test_red_team.json")
    co_failure_path = REPRO_DIR / "co_failure_matrix.json"
    co_failure = _load_json(co_failure_path) if co_failure_path.exists() else None
    prompt_audit_path = REPRO_DIR / "prompt_variant_validity_audit.json"
    prompt_repair_path = REPRO_DIR / "prompt_variant_repair_rerun.json"
    zero_task_real_repair_path = REPRO_DIR / "zero_task_real_repair.json"
    prompt_audit = _load_json(prompt_audit_path) if prompt_audit_path.exists() else {}
    prompt_repair = _load_json(prompt_repair_path) if prompt_repair_path.exists() else {}

    heatmap = make_acceptance_heatmap(figure_inputs["accepted_breadth_map"], breadth)
    contrast = make_contract_vs_stress_figure(field["policy_sensitivity"], stress_targeted, stress_agnostic)
    failure_plot = make_failure_family_figure(figure_inputs["failure_family_counts"])
    cofailure_plot = make_co_failure_heatmap(co_failure) if co_failure else None

    family_total = sum(field["gate_family_failure_counts"].values())
    stats_plus_robustness = (
        field["gate_family_failure_counts"].get("statistics", 0)
        + field["gate_family_failure_counts"].get("robustness", 0)
    )
    accepted_in_multilane = (
        field["acceptance_by_lane"].get("A", {}).get("accepted", 0)
        + field["acceptance_by_lane"].get("B", {}).get("accepted", 0)
        + field["acceptance_by_lane"].get("C", {}).get("accepted", 0)
    )
    accepted_in_real_repair = field["acceptance_by_lane"].get("canonical_real_repair_v1", {}).get("accepted", 0)
    # the previous publication field
    # ``accepted_in_zero_task_real_repair`` was sourced from the
    # ``canonical_real_repair_v1`` lane (the contract-hardening rerun, accepts
    # = 8) but its name pointed at the artefact named
    # ``zero_task_real_repair.json`` (the zero-task real repair rerun,
    # accepts = 7). Two different questions answered by one field is
    # a dangerous overload, so we now emit BOTH numbers under unambiguous
    # keys and keep the legacy key for one release as a backwards-compatible
    # alias to whichever value matches the legacy semantics (the lane number).
    zero_task_real_repair_doc = (
        _load_json(zero_task_real_repair_path) if zero_task_real_repair_path.exists() else {}
    )
    accepted_in_zero_task_real_repair_artifact = int(
        (zero_task_real_repair_doc.get("aggregate") or {}).get("accepted_after_real_total") or 0
    )
    accepted_total = field["totals"]["accepted"]
    prompt_affected = int(prompt_audit.get("affected_accepted_claims_in_existing_artifacts") or 0)
    prompt_covered = int(prompt_repair.get("accepted_before_in_rerun_bundles") or 0)
    prompt_retained = int(prompt_repair.get("previously_accepted_retained") or 0)
    prompt_demoted = int(prompt_repair.get("previously_accepted_demoted") or 0)

    takeaways = {
        "headline_numbers": {
            "claims": field["totals"]["claims"],
            "accepted": accepted_total,
            "acceptance_rate": field["totals"]["acceptance_rate"],
            "acceptance_rate_ci95": field["totals"]["acceptance_rate_ci95"],
            "accepted_tasks": [
                task for task, row in sorted(field["acceptance_by_task"].items()) if row["accepted"] > 0
            ],
            "accepted_models": {
                model: row["accepted"] for model, row in sorted(field["acceptance_by_model"].items())
            },
        },
        "concentration": {
            "accepted_in_regenerated_multilane": accepted_in_multilane,
            # New, unambiguous keys:
            "accepted_in_canonical_real_repair_v1_lane": accepted_in_real_repair,
            "accepted_in_zero_task_real_repair_artifact": accepted_in_zero_task_real_repair_artifact,
            # Legacy alias (deprecated, removed after one release). Kept
            # equal to its historical value (the lane number) so external
            # consumers do not silently flip semantics.
            "accepted_in_zero_task_real_repair": accepted_in_real_repair,
            "accepted_in_canonical_real": field["acceptance_by_lane"].get("canonical_real", {}).get("accepted", 0),
            "accepted_tasks_count": sum(1 for row in field["acceptance_by_task"].values() if row["accepted"] > 0),
            "evaluated_tasks_count": len(field["acceptance_by_task"]),
        },
        "failure_structure": {
            "family_total_failures": family_total,
            "statistics_plus_robustness_failures": stats_plus_robustness,
            "statistics_plus_robustness_fraction": stats_plus_robustness / family_total if family_total else 0.0,
            "failed_gate_counts": field["failed_gate_counts"],
        },
        "policy_vs_stress": {
            "released_policy_sensitivity": field["policy_sensitivity"],
            "suite_targeted_stress": stress_targeted["conditions"],
            "agnostic_stress": stress_agnostic["conditions"],
            "adaptive_red_team": stress_red["adaptive"],
            "near_miss": stress_red["near_miss"],
        },
        "transfer_and_determinism": {
            "transfer_summary": transfer,
            "submission_review_stable_bundles": community["stable_bundles"],
            "submission_review_bundles_reviewed": community["bundles_reviewed"],
        },
        "figures": {
            "acceptance_heatmap": heatmap,
            "contract_vs_stress": contrast,
            "failure_families": failure_plot,
            "gate_cofailure_heatmap": cofailure_plot,
        },
        "fragility_cluster": (co_failure or {}).get("dominant_fragility_cluster"),
        "prompt_variant_repair_frontier": {
            "affected_accepted_claims": prompt_affected,
            "covered_accepted_claims": prompt_covered,
            "previously_accepted_retained": prompt_retained,
            "previously_accepted_demoted": prompt_demoted,
        },
    }

    # Format Wilson CI at 2-decimal precision to match the published paper
    # The cached label uses 1-decimal for
    # historical reasons; format directly from the float low/high so the
    # repo-level publication surface matches papers/submissions/*/paper_body.tex.
    _ci = field["totals"]["acceptance_rate_ci95"]
    _ci_label2 = (
        f"[{_ci['low'] * 100:.2f}%, {_ci['high'] * 100:.2f}%]"
        if isinstance(_ci, dict) and _ci.get("low") is not None and _ci.get("high") is not None
        else _ci.get("label", "n/a")
    )

    lines = [
        "# Release Takeaways",
        "",
        f"- **Acceptance is broader but still selective:** {accepted_total}/{field['totals']['claims']} claims are accepted "
        f"({_ci_label2}), and accepted claims appear in "
        f"{takeaways['concentration']['accepted_tasks_count']}/{takeaways['concentration']['evaluated_tasks_count']} released tasks.",
        f"- **Most accepted evidence comes from regenerated evidence paths:** "
        f"{accepted_in_multilane}/{accepted_total} accepted claims appear in lanes A/B/C, "
        f"{accepted_in_real_repair}/{accepted_total} appear in the canonical_real_repair_v1 lane, and "
        f"{takeaways['concentration']['accepted_in_canonical_real']}/{accepted_total} appear in the canonical historical slice "
        "(lane attribution is per-lane, not a partition: a claim accepted in multiple lanes is counted in each). "
        "",
        f"- **Statistics and robustness dominate failures:** {stats_plus_robustness}/{family_total} family-level failures "
        f"({(stats_plus_robustness / family_total) * 100:.1f}%) come from those two suites.",
        f"- **Released-claim sensitivity differs from synthetic false-accept sensitivity:** controls ablation raises released acceptance "
        f"{field['policy_sensitivity']['conditions']['full_contract']['accepted']} → {field['policy_sensitivity']['conditions']['no_controls_suite']['accepted']}, "
        f"while suite-targeted synthetic false accepts jump 0/30 → 10/30 under each of statistical-rigor, robustness, and controls ablations.",
        f"- **The benchmark is useful but not solved:** on the current released artifact surface, evaluator-agnostic latent stress leaks "
        f"{stress_agnostic['conditions']['full_contract']['leaked']}/{stress_agnostic['conditions']['full_contract']['total']} under the full contract, "
        f"adaptive search succeeds {stress_red['adaptive']['successes']}/{stress_red['adaptive']['attempts']}, "
        f"and transfer-confirmed accepted claims remain {transfer['transfer_confirmed_claims']}/{transfer['accepted_claims_tested']}. "
        "See `main/output/repro/release_readiness_report.md` and "
        "`main/output/repro/direct_blocker_closure_report.md` for fresh rotated agnostic diagnostics and hardened-contract follow-up.",
        f"- **Prompt robustness is a repair frontier, not a settled result:** unsupported nominal variants affect "
        f"{prompt_affected} accepted claims; task-supported reruns retain {prompt_retained}/{prompt_covered} "
        f"and demote {prompt_demoted}/{prompt_covered}.",
        f"- **Deterministic review is a scientific enabler here:** submission review is stable on "
        f"{community['stable_bundles']}/{community['bundles_reviewed']} released bundles.",
    ]
    if co_failure and co_failure.get("dominant_fragility_cluster"):
        cluster = co_failure["dominant_fragility_cluster"]
        gates = [str(gate).replace("_", " ") for gate in cluster.get("failed_gates", [])]
        gate_phrase = " + ".join(gates) if gates else "multiple gates"
        denominator = int(co_failure.get("claims_with_failed_gates") or co_failure.get("n_failed") or 0)
        fraction = float(
            cluster.get(
                "fraction_of_claims_with_failed_gates",
                cluster.get("fraction_of_failed_claims", 0.0),
            )
        )
        lines.append(
            f"- **A single fragility pattern dominates claims with failed gates:** "
            f"{cluster['claims_with_this_pattern']}/{denominator} "
            f"({fraction * 100:.0f}%) fail the same "
            f"{cluster['size']}-gate pattern ({gate_phrase}), suggesting that fragility is structured, "
            "not idiosyncratic."
        )
    lines.extend(
        [
            "",
            "## Figure files",
            "",
            "- `papers/submissions/shared/figures/accepted_breadth_heatmap.pdf`",
            "- `papers/submissions/shared/figures/contract_vs_stress_rates.pdf`",
            "- `papers/submissions/shared/figures/failure_family_counts.pdf`",
        ]
    )
    if cofailure_plot:
        lines.append("- `papers/submissions/shared/figures/gate_cofailure_heatmap.pdf`")
    lines.extend(
        [
            "",
            "## Data sources",
            "",
            "- `main/output/repro/benchmark_breadth_summary.json`",
            "- `main/output/repro/field_level_findings.json`",
            "- `main/output/repro/figure_inputs.json`",
            "- `main/output/repro/transfer_results_summary.json`",
            "- `main/output/community_submissions/community_value_summary.json`",
            "- `main/output/real_multi_task/ioi_v0_gpt2-small/stress_test_ablation.json`",
            "- `main/output/real_multi_task/ioi_v0_gpt2-small/stress_test_agnostic.json`",
            "- `main/output/real_multi_task/ioi_v0_gpt2-small/stress_test_red_team.json`",
            "- `main/output/repro/prompt_variant_validity_audit.json`",
            "- `main/output/repro/prompt_variant_repair_rerun.json`",
        ]
    )
    if co_failure:
        lines.append("- `main/output/repro/co_failure_matrix.json`")

    _write_json(REPRO_DIR / "release_takeaways.json", takeaways)
    _write_text(REPRO_DIR / "release_takeaways.md", "\n".join(lines).rstrip() + "\n")
    print(str(REPRO_DIR / "release_takeaways.json"))

if __name__ == "__main__":
    main()
