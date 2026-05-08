"""Bundle loading and schema validation for stage-1 harness.

V7: Extended with sample_size_policy validation, intervention_levels,
optional stage-gate fields, and backwards-compatible schema expansion.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from .constants import (
    ALLOWED_COMPONENT_TYPES,
    ALLOWED_EFFECT_DIRECTIONS,
    ALLOWED_INTERVENTION_LEVELS,
    ALLOWED_PATCH_MODES,
    ALLOWED_SLICES,
    COMPONENT_REQUIRED_FIELDS,
    DEFAULT_FORBIDDEN_TERMS,
    DIRECTION_VALUES,
    MANDATORY_CONTROL_FAMILIES,
    OPTIONAL_PROTOCOL_TOP_LEVEL,
    OPTIONAL_SAMPLE_SIZE_POLICY_KEYS,
    OPTIONAL_UNIT_OF_WORK_MODEL_SPEC,
    REQUIRED_CLAIM_BUDGET,
    REQUIRED_CONTROL_POLICY,
    REQUIRED_EVAL_TOP_LEVEL,
    REQUIRED_EXECUTION_GRID,
    REQUIRED_HYPOTHESIS_FIELDS,
    REQUIRED_HYPOTHESIS_RESULT_FIELDS,
    REQUIRED_LANGUAGE_POLICY,
    REQUIRED_MIN_ROBUSTNESS_AXES,
    REQUIRED_PROTOCOL_TOP_LEVEL,
    REQUIRED_RAW_CELL_FIELDS,
    REQUIRED_STAGE_GATES,
    REQUIRED_STATISTICAL_POLICY,
    REQUIRED_UNIT_OF_WORK,
)
from .io_utils import BundleError, read_json, read_jsonl, read_yaml, sha256_file


def _require_keys(obj: dict, keys: Iterable[str], label: str) -> None:
    missing = [k for k in keys if k not in obj]
    if missing:
        raise BundleError(f"{label} missing keys: {missing}")


def _ensure_list(value: object, label: str) -> list:
    if not isinstance(value, list) or not value:
        raise BundleError(f"{label} must be a non-empty list")
    return value


def _ensure_numeric(value: object, label: str) -> float:
    # Booleans are a subclass of ``int`` in Python; reject them here so that
    # ``True`` / ``False`` cannot masquerade as 1 / 0 in numeric fields.
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise BundleError(f"{label} must be numeric")
    f = float(value)
    # Audit-final §gpt2.B1: reject NaN/Inf at load time. Json serialisers
    # (including stdlib ``json``) round-trip these as ``NaN`` / ``Infinity``
    # tokens which are not valid JSON; allowing them downstream silently
    # poisons every statistic (mean, FDR, bootstrap CI) computed against
    # that field.
    import math
    if not math.isfinite(f):
        raise BundleError(f"{label} must be a finite number, got {value!r}")
    return f


def _hypothesis_fingerprint(hypothesis: dict) -> str:
    """Stable fingerprint for duplicate semantic-content detection."""
    payload = {
        "task_id": hypothesis.get("task_id"),
        "model_id": hypothesis.get("model_id"),
        "metric_id": hypothesis.get("metric_id"),
        "claim_text": str(hypothesis.get("claim_text", "")).strip(),
        "candidate_components": hypothesis.get("candidate_components", []),
        "predicted_effect_direction": hypothesis.get("predicted_effect_direction"),
        "predicted_min_effect": hypothesis.get("predicted_min_effect"),
        "predicted_specificity_ratio": hypothesis.get("predicted_specificity_ratio"),
        "expected_failure_modes": hypothesis.get("expected_failure_modes", []),
    }
    return json.dumps(payload, sort_keys=True)


def _canonical_claim_signature(hypothesis: dict) -> str:
    """Stable signature for duplicate-claim detection within a bundle."""
    payload = {
        "protocol_id": hypothesis.get("protocol_id"),
        "task_id": hypothesis.get("task_id"),
        "model_id": hypothesis.get("model_id"),
        "metric_id": hypothesis.get("metric_id"),
        "candidate_components": hypothesis.get("candidate_components"),
        "predicted_effect_direction": hypothesis.get("predicted_effect_direction"),
        "predicted_min_effect": hypothesis.get("predicted_min_effect"),
        "predicted_specificity_ratio": hypothesis.get("predicted_specificity_ratio"),
        "expected_failure_modes": hypothesis.get("expected_failure_modes"),
    }
    return json.dumps(payload, sort_keys=True)


def validate_protocol(protocol: dict) -> None:
    _require_keys(protocol, REQUIRED_PROTOCOL_TOP_LEVEL, "protocol")
    if not isinstance(protocol.get("frozen"), bool) or not protocol["frozen"]:
        raise BundleError("protocol.frozen must be true")

    # reject unknown top-level
    # protocol keys. Without this, a typo (``stage_gate`` vs ``stage_gates``)
    # silently disables the misnamed section while the validator still passes
    # because the *required* key is also present somewhere downstream — and
    # an attacker (or a hurried author) could smuggle non-frozen state into
    # the bundle.
    _allowed_top = set(REQUIRED_PROTOCOL_TOP_LEVEL) | set(OPTIONAL_PROTOCOL_TOP_LEVEL)
    extra_top = sorted(k for k in protocol.keys() if k not in _allowed_top)
    if extra_top:
        raise BundleError(
            f"protocol contains unknown top-level keys: {extra_top}. "
            "Allowed keys: required="
            f"{sorted(REQUIRED_PROTOCOL_TOP_LEVEL)}, optional="
            f"{sorted(OPTIONAL_PROTOCOL_TOP_LEVEL)}."
        )

    # ---- unit_of_work ----
    unit = protocol["unit_of_work"]
    if not isinstance(unit, dict):
        raise BundleError("protocol.unit_of_work must be a mapping")
    _require_keys(unit, REQUIRED_UNIT_OF_WORK, "protocol.unit_of_work")
    if "model_spec" in unit:
        model_spec = unit["model_spec"]
        if not isinstance(model_spec, dict):
            raise BundleError("protocol.unit_of_work.model_spec must be a mapping")
        _require_keys(model_spec, OPTIONAL_UNIT_OF_WORK_MODEL_SPEC, "protocol.unit_of_work.model_spec")
        for key in OPTIONAL_UNIT_OF_WORK_MODEL_SPEC:
            if not isinstance(model_spec[key], int) or model_spec[key] <= 0:
                raise BundleError(f"protocol.unit_of_work.model_spec.{key} must be positive int")

    # ---- execution_grid ----
    grid = protocol["execution_grid"]
    if not isinstance(grid, dict):
        raise BundleError("protocol.execution_grid must be a mapping")
    _require_keys(grid, REQUIRED_EXECUTION_GRID, "protocol.execution_grid")

    for key in REQUIRED_EXECUTION_GRID:
        values = _ensure_list(grid[key], f"protocol.execution_grid.{key}")
        if key in ("seeds", "resample_ids") and not all(isinstance(v, int) for v in values):
            raise BundleError(f"protocol.execution_grid.{key} must be integers")
        if key in ("prompt_variants", "methods") and not all(isinstance(v, str) for v in values):
            raise BundleError(f"protocol.execution_grid.{key} must be strings")
        # reject duplicate
        # axis values. With duplicates the per-axis consistency means and
        # method-sensitivity standard deviation can be trivially satisfied
        # (e.g. ``methods: [m, m]`` collapses pstdev to 0), which silently
        # weakens the corresponding gates.
        if len(set(values)) != len(values):
            raise BundleError(
                f"protocol.execution_grid.{key} must not contain duplicate values; "
                f"got {values}"
            )
        # cap per-axis size. A
        # ``seeds: [0..9999]`` row would balloon the cell grid by 10000x and
        # exhaust evaluator memory before any gate runs. The cap is set far
        # above any legitimate protocol (the largest released axis has 8
        # entries) so it only catches accidents and DoS attempts.
        if len(values) > 1024:
            raise BundleError(
                f"protocol.execution_grid.{key} has {len(values)} entries; "
                "the per-axis cap is 1024 to bound the cell grid."
            )

    if len(grid["methods"]) < 2:
        raise BundleError("execution_grid.methods must include >=2 methods for sensitivity checks")

    # ---- control_policy ----
    control = protocol["control_policy"]
    if not isinstance(control, dict):
        raise BundleError("protocol.control_policy must be a mapping")
    _require_keys(control, REQUIRED_CONTROL_POLICY, "protocol.control_policy")
    families = _ensure_list(control["required_families"], "protocol.control_policy.required_families")
    missing_families = [f for f in MANDATORY_CONTROL_FAMILIES if f not in families]
    if missing_families:
        raise BundleError(f"control_policy.required_families missing mandatory controls: {missing_families}")
    _ensure_numeric(control["max_control_abs_mean"], "protocol.control_policy.max_control_abs_mean")

    # ---- stage_gates ----
    gates = protocol["stage_gates"]
    if not isinstance(gates, dict):
        raise BundleError("protocol.stage_gates must be a mapping")
    _require_keys(gates, REQUIRED_STAGE_GATES, "protocol.stage_gates")
    _ensure_numeric(gates["min_causal_effect"], "protocol.stage_gates.min_causal_effect")
    _ensure_numeric(gates["min_specificity_ratio"], "protocol.stage_gates.min_specificity_ratio")
    _ensure_numeric(gates["max_method_sensitivity_std"], "protocol.stage_gates.max_method_sensitivity_std")
    if not isinstance(gates["require_confirmatory_ci_excludes_zero"], bool):
        raise BundleError("protocol.stage_gates.require_confirmatory_ci_excludes_zero must be bool")

    # V7 optional stage-gate numerics
    for opt_key in ("min_effect_size_d", "min_practical_cohens_d", "min_rank_stability_tau", "baseline_superiority_ratio"):
        if opt_key in gates:
            _ensure_numeric(gates[opt_key], f"protocol.stage_gates.{opt_key}")
    # power-adequacy gate degenerates to always-pass
    # when ``min_effect_size_d == 0`` because the n_required threshold collapses.
    # If the gate is declared at all it must be strictly positive; protocols
    # that intend to disable it should omit the key entirely.
    if "min_effect_size_d" in gates and gates["min_effect_size_d"] <= 0:
        raise BundleError(
            "protocol.stage_gates.min_effect_size_d must be > 0 when present "
            "(omit the key to disable the gate); got "
            f"{gates['min_effect_size_d']}"
        )

    min_rob = gates["min_robustness"]
    if not isinstance(min_rob, dict):
        raise BundleError("protocol.stage_gates.min_robustness must be a mapping")
    _require_keys(min_rob, REQUIRED_MIN_ROBUSTNESS_AXES, "protocol.stage_gates.min_robustness")
    for axis in REQUIRED_MIN_ROBUSTNESS_AXES:
        _ensure_numeric(min_rob[axis], f"protocol.stage_gates.min_robustness.{axis}")

    # ---- statistical_policy ----
    stat = protocol["statistical_policy"]
    if not isinstance(stat, dict):
        raise BundleError("protocol.statistical_policy must be a mapping")
    _require_keys(stat, REQUIRED_STATISTICAL_POLICY, "protocol.statistical_policy")
    alpha_v = _ensure_numeric(stat["alpha"], "protocol.statistical_policy.alpha")
    fdr_v = _ensure_numeric(stat["fdr_q"], "protocol.statistical_policy.fdr_q")
    floor_v = _ensure_numeric(stat["min_effect_floor"], "protocol.statistical_policy.min_effect_floor")
    # Audit-final §gpt2.B3: range-check stats fields. ``alpha`` and ``fdr_q``
    # must lie strictly in (0, 1) — values outside that interval either
    # disable significance gating entirely or invert it. ``min_effect_floor``
    # must be non-negative.
    if not (0.0 < alpha_v < 1.0):
        raise BundleError(
            f"protocol.statistical_policy.alpha must lie in (0, 1); got {alpha_v}"
        )
    if not (0.0 < fdr_v < 1.0):
        raise BundleError(
            f"protocol.statistical_policy.fdr_q must lie in (0, 1); got {fdr_v}"
        )
    if floor_v < 0.0:
        raise BundleError(
            f"protocol.statistical_policy.min_effect_floor must be non-negative; got {floor_v}"
        )
    if not isinstance(stat["multiplicity_method"], str):
        raise BundleError("protocol.statistical_policy.multiplicity_method must be string")

    # ---- claim_budget ----
    budget = protocol["claim_budget"]
    if not isinstance(budget, dict):
        raise BundleError("protocol.claim_budget must be a mapping")
    _require_keys(budget, REQUIRED_CLAIM_BUDGET, "protocol.claim_budget")
    if not isinstance(budget["max_total_claims"], int) or budget["max_total_claims"] <= 0:
        raise BundleError("claim_budget.max_total_claims must be positive int")
    if not isinstance(budget["max_claims_per_task"], int) or budget["max_claims_per_task"] <= 0:
        raise BundleError("claim_budget.max_claims_per_task must be positive int")

    # ---- language_policy ----
    language = protocol["language_policy"]
    if not isinstance(language, dict):
        raise BundleError("protocol.language_policy must be a mapping")
    _require_keys(language, REQUIRED_LANGUAGE_POLICY, "protocol.language_policy")
    for term in _ensure_list(language["forbidden_without_pass"], "language_policy.forbidden_without_pass"):
        if not isinstance(term, str) or not term.strip():
            raise BundleError("language_policy.forbidden_without_pass entries must be non-empty strings")

    # ---- sample_size_policy (V7 optional) ----
    if "sample_size_policy" in protocol:
        ssp = protocol["sample_size_policy"]
        if not isinstance(ssp, dict):
            raise BundleError("protocol.sample_size_policy must be a mapping")
        for key in ssp:
            if key not in OPTIONAL_SAMPLE_SIZE_POLICY_KEYS:
                raise BundleError(f"protocol.sample_size_policy contains unknown key: {key}")
        if "exploratory_fraction" in ssp:
            frac = _ensure_numeric(ssp["exploratory_fraction"], "sample_size_policy.exploratory_fraction")
            if not (0.0 < frac < 1.0):
                raise BundleError("sample_size_policy.exploratory_fraction must be between 0 and 1 exclusive")
        if "min_examples_per_cell" in ssp:
            val = ssp["min_examples_per_cell"]
            if not isinstance(val, int) or val <= 0:
                raise BundleError("sample_size_policy.min_examples_per_cell must be positive int")
        if "power_target" in ssp:
            pt = _ensure_numeric(ssp["power_target"], "sample_size_policy.power_target")
            if not (0.0 < pt < 1.0):
                raise BundleError("sample_size_policy.power_target must be between 0 and 1 exclusive")
        if "minimum_detectable_effect" in ssp:
            _ensure_numeric(ssp["minimum_detectable_effect"], "sample_size_policy.minimum_detectable_effect")
        if "require_confirmatory_split" in ssp:
            if not isinstance(ssp["require_confirmatory_split"], bool):
                raise BundleError("sample_size_policy.require_confirmatory_split must be bool")
        if "min_cells_per_hypothesis" in ssp:
            val = ssp["min_cells_per_hypothesis"]
            if not isinstance(val, int) or val <= 0:
                raise BundleError("sample_size_policy.min_cells_per_hypothesis must be positive int")

    # ---- intervention_levels (V7 optional) ----
    if "intervention_levels" in protocol:
        levels = protocol["intervention_levels"]
        if not isinstance(levels, list) or not levels:
            raise BundleError("protocol.intervention_levels must be a non-empty list")
        for lvl in levels:
            if lvl not in ALLOWED_INTERVENTION_LEVELS:
                raise BundleError(f"protocol.intervention_levels contains unknown level: {lvl}")


def validate_hypotheses(hypotheses: list[dict], protocol: dict) -> None:
    if not hypotheses:
        raise BundleError("hypothesis.jsonl must contain at least one hypothesis")

    seen_ids: set[str] = set()
    seen_fingerprints: dict[str, str] = {}
    seen_signatures: dict[str, str] = {}
    by_task: dict[str, int] = {}
    required_forbidden = {
        t.lower() for t in protocol["language_policy"]["forbidden_without_pass"]
    } | {t.lower() for t in DEFAULT_FORBIDDEN_TERMS}

    for idx, hyp in enumerate(hypotheses, start=1):
        if not isinstance(hyp, dict):
            raise BundleError(f"hypothesis row {idx} must be mapping")
        _require_keys(hyp, REQUIRED_HYPOTHESIS_FIELDS, f"hypothesis[{idx}]")

        hyp_id = hyp["hypothesis_id"]
        if not isinstance(hyp_id, str) or not hyp_id.strip():
            raise BundleError(f"hypothesis[{idx}].hypothesis_id must be non-empty string")
        if hyp_id in seen_ids:
            raise BundleError(f"Duplicate hypothesis_id: {hyp_id}")
        seen_ids.add(hyp_id)
        fingerprint = _hypothesis_fingerprint(hyp)
        if fingerprint in seen_fingerprints:
            raise BundleError(
                f"Hypothesis {hyp_id} duplicates the semantic content of {seen_fingerprints[fingerprint]}"
            )
        seen_fingerprints[fingerprint] = hyp_id

        if hyp["protocol_id"] != protocol["protocol_id"]:
            raise BundleError(f"Hypothesis {hyp_id} protocol_id mismatch")

        unit = protocol["unit_of_work"]
        if hyp["task_id"] != unit["task_id"]:
            raise BundleError(f"Hypothesis {hyp_id} task_id mismatch with protocol")
        if hyp["model_id"] != unit["model_id"]:
            raise BundleError(f"Hypothesis {hyp_id} model_id mismatch with protocol")
        if hyp["metric_id"] != unit["metric_id"]:
            raise BundleError(f"Hypothesis {hyp_id} metric_id mismatch with protocol")

        direction = hyp["predicted_effect_direction"]
        if direction not in ALLOWED_EFFECT_DIRECTIONS:
            raise BundleError(f"Hypothesis {hyp_id} has invalid direction: {direction}")

        _ensure_numeric(hyp["predicted_min_effect"], f"hypothesis[{idx}].predicted_min_effect")
        _ensure_numeric(
            hyp["predicted_specificity_ratio"],
            f"hypothesis[{idx}].predicted_specificity_ratio",
        )

        components = _ensure_list(hyp["candidate_components"], f"hypothesis[{idx}].candidate_components")
        if not all(isinstance(c, dict) for c in components):
            raise BundleError(f"Hypothesis {hyp_id} candidate_components must be list[dict]")

        # Audit-final §gpt2.A4: enforce component-type schema. Each
        # ``candidate_components`` entry must declare an ``ALLOWED`` type
        # and supply the required fields for that type
        # (``COMPONENT_REQUIRED_FIELDS``). Previously the schema lived in
        # ``constants.py`` but was never checked; bundles with missing
        # fields silently propagated to the runner where the consequences
        # ranged from KeyError to wrong-component patching.
        for c_idx, comp in enumerate(components):
            ctype = comp.get("component_type")
            if ctype is None:
                raise BundleError(
                    f"Hypothesis {hyp_id} candidate_components[{c_idx}] missing component_type"
                )
            if ctype not in ALLOWED_COMPONENT_TYPES:
                raise BundleError(
                    f"Hypothesis {hyp_id} candidate_components[{c_idx}].component_type "
                    f"{ctype!r} is not in ALLOWED_COMPONENT_TYPES "
                    f"{sorted(ALLOWED_COMPONENT_TYPES)}"
                )
            required = COMPONENT_REQUIRED_FIELDS.get(ctype, ())
            missing = [f for f in required if f not in comp]
            if missing:
                raise BundleError(
                    f"Hypothesis {hyp_id} candidate_components[{c_idx}] (type={ctype}) "
                    f"missing required fields: {missing}"
                )

        failure_modes = _ensure_list(hyp["expected_failure_modes"], f"hypothesis[{idx}].expected_failure_modes")
        if not all(isinstance(m, str) and m.strip() for m in failure_modes):
            raise BundleError(f"Hypothesis {hyp_id} expected_failure_modes must be non-empty strings")

        claim_text = hyp["claim_text"]
        if not isinstance(claim_text, str) or not claim_text.strip():
            raise BundleError(f"Hypothesis {hyp_id} claim_text must be non-empty string")
        lowered = claim_text.lower()
        for token in required_forbidden:
            if token in lowered:
                raise BundleError(
                    f"Hypothesis {hyp_id} uses forbidden verdict language before verification: '{token}'"
                )

        for forbidden_key in ("accepted", "passed", "verdict"):
            if forbidden_key in hyp:
                raise BundleError(f"Hypothesis {hyp_id} contains forbidden field: {forbidden_key}")

        signature = _canonical_claim_signature(hyp)
        prior_hypothesis = seen_signatures.get(signature)
        if prior_hypothesis is not None:
            raise BundleError(
                f"Duplicate claim content detected: {hyp_id} duplicates structured claim of {prior_hypothesis}"
            )
        seen_signatures[signature] = hyp_id

        # V7 optional fields
        if "intervention_level" in hyp:
            if hyp["intervention_level"] not in ALLOWED_INTERVENTION_LEVELS:
                raise BundleError(f"Hypothesis {hyp_id} has invalid intervention_level: {hyp['intervention_level']}")

        if "alternative_hypotheses" in hyp:
            alt = hyp["alternative_hypotheses"]
            if not isinstance(alt, list) or not all(isinstance(a, str) and a.strip() for a in alt):
                raise BundleError(f"Hypothesis {hyp_id} alternative_hypotheses must be list of non-empty strings")

        by_task[hyp["task_id"]] = by_task.get(hyp["task_id"], 0) + 1

    if len(hypotheses) > protocol["claim_budget"]["max_total_claims"]:
        raise BundleError("Claim budget exceeded: max_total_claims")

    for task_id, count in by_task.items():
        if count > protocol["claim_budget"]["max_claims_per_task"]:
            raise BundleError(
                f"Claim budget exceeded for task {task_id}: {count} > {protocol['claim_budget']['max_claims_per_task']}"
            )


def validate_evaluation_result(
    evaluation_result: dict,
    protocol: dict,
    protocol_sha256: str,
    hypothesis_ids: set[str],
) -> None:
    _require_keys(evaluation_result, REQUIRED_EVAL_TOP_LEVEL, "evaluation_result")
    if evaluation_result["protocol_id"] != protocol["protocol_id"]:
        raise BundleError("evaluation_result.protocol_id mismatch")
    if evaluation_result["protocol_sha256"] != protocol_sha256:
        raise BundleError("evaluation_result.protocol_sha256 mismatch")

    rows = evaluation_result["hypothesis_results"]
    if not isinstance(rows, list) or not rows:
        raise BundleError("evaluation_result.hypothesis_results must be non-empty list")

    seen_results: set[str] = set()
    for idx, row in enumerate(rows, start=1):
        if not isinstance(row, dict):
            raise BundleError(f"hypothesis_results[{idx}] must be mapping")
        _require_keys(row, REQUIRED_HYPOTHESIS_RESULT_FIELDS, f"hypothesis_results[{idx}]")

        hyp_id = row["hypothesis_id"]
        if hyp_id not in hypothesis_ids:
            raise BundleError(f"evaluation_result references unknown hypothesis_id: {hyp_id}")
        if hyp_id in seen_results:
            raise BundleError(f"Duplicate hypothesis result for hypothesis_id: {hyp_id}")
        seen_results.add(hyp_id)

        raw_cells = row["raw_cells"]
        if not isinstance(raw_cells, list) or not raw_cells:
            raise BundleError(f"hypothesis_results[{idx}].raw_cells must be non-empty list")
        # Audit-final §gpt2.B2: detect duplicate raw cells. The cell key
        # ``(slice, seed, prompt_variant, resample_id, method)`` uniquely
        # identifies one Monte-Carlo evaluation point; submitting the same
        # tuple twice silently inflates effective sample size in any
        # downstream aggregation that does not deduplicate.
        seen_cell_keys: set[tuple] = set()
        for cidx, cell in enumerate(raw_cells, start=1):
            if not isinstance(cell, dict):
                raise BundleError(f"raw_cells[{cidx}] for {hyp_id} must be mapping")
            _require_keys(cell, REQUIRED_RAW_CELL_FIELDS, f"raw_cell[{cidx}] for {hyp_id}")
            if cell["slice"] not in ALLOWED_SLICES:
                raise BundleError(f"raw_cell[{cidx}] for {hyp_id} has invalid slice")
            if not isinstance(cell["seed"], int):
                raise BundleError(f"raw_cell[{cidx}] for {hyp_id} seed must be int")
            if not isinstance(cell["prompt_variant"], str):
                raise BundleError(f"raw_cell[{cidx}] for {hyp_id} prompt_variant must be str")
            if not isinstance(cell["resample_id"], int):
                raise BundleError(f"raw_cell[{cidx}] for {hyp_id} resample_id must be int")
            if not isinstance(cell["method"], str):
                raise BundleError(f"raw_cell[{cidx}] for {hyp_id} method must be str")
            if not isinstance(cell["runner_id"], str) or not cell["runner_id"].strip():
                raise BundleError(f"raw_cell[{cidx}] for {hyp_id} runner_id must be non-empty str")
            if not isinstance(cell["runner_version"], str) or not cell["runner_version"].strip():
                raise BundleError(f"raw_cell[{cidx}] for {hyp_id} runner_version must be non-empty str")
            if not isinstance(cell["pipeline_sha"], str) or not cell["pipeline_sha"].strip():
                raise BundleError(f"raw_cell[{cidx}] for {hyp_id} pipeline_sha must be non-empty str")
            if not isinstance(cell["model_ref"], str) or not cell["model_ref"].strip():
                raise BundleError(f"raw_cell[{cidx}] for {hyp_id} model_ref must be non-empty str")
            if not isinstance(cell["prompt_template_id"], str) or not cell["prompt_template_id"].strip():
                raise BundleError(f"raw_cell[{cidx}] for {hyp_id} prompt_template_id must be non-empty str")
            if not isinstance(cell["dataset_seed"], int):
                raise BundleError(f"raw_cell[{cidx}] for {hyp_id} dataset_seed must be int")
            if "direction" in cell and cell["direction"] not in DIRECTION_VALUES and cell["direction"] not in {"denoise", "noise"}:
                raise BundleError(f"raw_cell[{cidx}] for {hyp_id} has invalid direction: {cell['direction']}")
            _ensure_numeric(cell["treatment_effect"], f"raw_cell[{cidx}] for {hyp_id}.treatment_effect")
            if not isinstance(cell["control_effects"], dict):
                raise BundleError(f"raw_cell[{cidx}] for {hyp_id}.control_effects must be mapping")

            families = protocol["control_policy"]["required_families"]
            missing = [f for f in families if f not in cell["control_effects"]]
            if missing:
                raise BundleError(f"raw_cell[{cidx}] for {hyp_id} missing control families: {missing}")
            for fam, value in cell["control_effects"].items():
                _ensure_numeric(value, f"raw_cell[{cidx}] for {hyp_id}.control_effects[{fam}]")

            cell_key = (
                cell["slice"],
                cell["seed"],
                cell["prompt_variant"],
                cell["resample_id"],
                cell["method"],
            )
            if cell_key in seen_cell_keys:
                raise BundleError(
                    f"raw_cell[{cidx}] for {hyp_id} duplicates an earlier "
                    f"cell with key (slice, seed, prompt_variant, "
                    f"resample_id, method)={cell_key}"
                )
            seen_cell_keys.add(cell_key)

    if seen_results != hypothesis_ids:
        missing = sorted(hypothesis_ids - seen_results)
        raise BundleError(f"evaluation_result missing hypothesis results: {missing}")


def validate_manifest(
    bundle_dir: Path,
    protocol_sha: str,
    hyp_sha: str,
    eval_sha: str,
    cross_model_sha: str | None = None,
) -> None:
    manifest_path = bundle_dir / "manifest.json"
    if not manifest_path.exists():
        raise BundleError("manifest.json is required")
    manifest = read_json(manifest_path)
    required = {
        "protocol.yaml": protocol_sha,
        "hypothesis.jsonl": hyp_sha,
        "evaluation_result.json": eval_sha,
    }
    for key, expected in required.items():
        actual = manifest.get(key)
        if actual != expected:
            raise BundleError(f"manifest mismatch for {key}")
    # enforce cross_model_results.json hash. The
    # surrounding load_bundle() previously computed the SHA and threaded it
    # into the returned ``hashes`` dict but the manifest never enforced it,
    # leaving transfer evidence outside the integrity hash chain. We now
    # require: (a) if the file exists on disk, the manifest must declare a
    # matching SHA; (b) if the file is absent, the manifest must NOT declare
    # the key (claiming evidence that does not exist is also a tamper signal).
    declared = manifest.get("cross_model_results.json")
    if cross_model_sha is not None:
        if declared is None:
            raise BundleError(
                "manifest.json is missing cross_model_results.json hash but "
                "the file is present on disk; transfer evidence must be "
                "included in the integrity hash chain."
            )
        if declared != cross_model_sha:
            raise BundleError("manifest mismatch for cross_model_results.json")
    elif declared is not None:
        raise BundleError(
            "manifest.json declares a cross_model_results.json hash but no "
            "such file exists on disk; refusing to validate against a "
            "phantom transfer-evidence file."
        )


def load_bundle(bundle_dir: Path) -> dict:
    protocol_path = bundle_dir / "protocol.yaml"
    hypotheses_path = bundle_dir / "hypothesis.jsonl"
    evaluation_path = bundle_dir / "evaluation_result.json"

    if not protocol_path.exists() or not hypotheses_path.exists() or not evaluation_path.exists():
        raise BundleError("Bundle must contain protocol.yaml, hypothesis.jsonl, evaluation_result.json")

    protocol = read_yaml(protocol_path)
    hypotheses = read_jsonl(hypotheses_path)
    evaluation_result = read_json(evaluation_path)

    validate_protocol(protocol)
    validate_hypotheses(hypotheses, protocol)

    protocol_sha = sha256_file(protocol_path)
    hypotheses_sha = sha256_file(hypotheses_path)
    evaluation_sha = sha256_file(evaluation_path)

    # include
    # cross_model_results.json in the integrity manifest when present so that
    # post-evaluation tampering with transfer evidence is caught by the same
    # hash-chain that protects protocol/hypothesis/evaluation_result.
    cross_model_path = bundle_dir / "cross_model_results.json"
    cross_model_sha = sha256_file(cross_model_path) if cross_model_path.exists() else None

    validate_evaluation_result(
        evaluation_result=evaluation_result,
        protocol=protocol,
        protocol_sha256=protocol_sha,
        hypothesis_ids={h["hypothesis_id"] for h in hypotheses},
    )

    validate_manifest(
        bundle_dir=bundle_dir,
        protocol_sha=protocol_sha,
        hyp_sha=hypotheses_sha,
        eval_sha=evaluation_sha,
        cross_model_sha=cross_model_sha,
    )

    hashes = {
        "protocol.yaml": protocol_sha,
        "hypothesis.jsonl": hypotheses_sha,
        "evaluation_result.json": evaluation_sha,
    }
    if cross_model_sha is not None:
        hashes["cross_model_results.json"] = cross_model_sha

    return {
        "protocol": protocol,
        "hypotheses": hypotheses,
        "evaluation_result": evaluation_result,
        "hashes": hashes,
    }
