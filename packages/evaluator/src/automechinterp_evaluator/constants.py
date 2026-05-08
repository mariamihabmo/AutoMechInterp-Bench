"""Constants used across schema validation and stage-gate evaluation.

V10: Multi-lane architecture — 7 component types (head, mlp, residual_stream,
edge, mlp_neuron, sae_feature, das_subspace), per-component control families,
provider metadata, and expanded intervention levels.
"""

from __future__ import annotations

EPSILON = 1e-12
# rationale for the constants in this file is now
# documented inline so reviewers do not need to chase commit archaeology.
# ``EPSILON``: float64 has ~15-17 significant decimal digits; 1e-12 is the
# smallest divisor we use as a "tiny but safely above subnormal" guard against
# division-by-zero in ratio computations (specificity ratios, baseline
# superiority ratios). Larger values would mask legitimately small effects;
# smaller values would touch float64's rounding floor.

GATE_PASS = "pass"
GATE_FAIL = "fail"
GATE_NOT_EVALUATED = "not_evaluated"

# ---------------------------------------------------------------------------
# Bootstrap / permutation defaults
# ---------------------------------------------------------------------------

DEFAULT_BOOTSTRAP_RESAMPLES = 10_000
DEFAULT_PERMUTATION_ITERATIONS = 10_000

# ---------------------------------------------------------------------------
# Gate classification (V20: core vs optional, defined in code)
# ---------------------------------------------------------------------------
# Core gates: MUST be PASS for any accepted tier. These cannot be NOT_EVALUATED.
# Optional gates: Can be NOT_EVALUATED without blocking acceptance.
# The distinction drives the tier system:
#   single_model_confirmed: all core PASS, optional may be NOT_EVALUATED
#   cross_model_confirmed: all core + optional PASS

CORE_GATES = frozenset({
    "execution_coverage",
    "confirmatory_present",
    "confirmatory_firewall",
    "causal_effect",
    "negative_controls",
    "robustness",
    "method_sensitivity",
    "confirmatory_ci",
    "multiplicity",
    "power_adequacy",
    "effect_size_practical",
    "rank_stability",
    "baseline_superiority",
    "bidirectional",
    "governance_valid",
})

OPTIONAL_GATES = frozenset({
    "cross_model_transfer",
})

NOT_EVALUATED_GUIDANCE = {
    "cross_model_transfer": {
        "why_missing": "No cross-model transfer data in bundle",
        "how_to_run": "Run run_cross_model_transfer() with a second model family",
        "impact": "Prevents cross_model_confirmed tier; single_model_confirmed still achievable",
    },
}

EVIDENCE_TIER_ORDER = (
    "cross_model_confirmed",
    "single_model_confirmed",
    "causal_plus_robustness",
    "causal_tested_unstable",
    "suggestive",
    "rejected",
)

# ---------------------------------------------------------------------------
# Direction values (V21: sufficiency/necessity, not denoise/noise)
# ---------------------------------------------------------------------------
# sufficiency_patch: patch clean → corrupt (restores behavior → sufficiency test)
# necessity_ablate: ablate on clean (disrupts behavior → necessity test)
# Conceptual mapping: sufficiency_patch ≈ denoising, necessity_ablate ≈ noising
# But they are not identical: noising in the literature is corrupt→clean patching,
# while necessity_ablate is ablation on clean. We use unambiguous MI-specific terms.
DIRECTION_VALUES = frozenset({"sufficiency_patch", "necessity_ablate"})

# ---------------------------------------------------------------------------
# Cross-model transfer gate definition (V21: single crisp definition)
# ---------------------------------------------------------------------------
# The cross-model gate checks: for each hypothesis, the mapped component on
# the transfer model has (a) the same effect direction as on the source model,
# AND (b) the effect magnitude exceeds a minimum floor.
# This prevents accepting "transfers" of near-zero noise. The floor is set
# relative to logit-diff units (the standard task metric).
# This is "direction + floor replication," NOT rank stability (Kendall τ).
# Kendall τ is retained as a secondary diagnostic but not the gate condition.
CROSS_MODEL_EFFECT_FLOOR = 0.02  # Minimum abs(effect) on transfer model in logit-diff units


# ---------------------------------------------------------------------------
# Protocol schema
# ---------------------------------------------------------------------------

REQUIRED_PROTOCOL_TOP_LEVEL = (
    "protocol_id",
    "protocol_version",
    "frozen",
    "unit_of_work",
    "execution_grid",
    "control_policy",
    "stage_gates",
    "statistical_policy",
    "claim_budget",
    "language_policy",
)

# Optional top-level sections (validated if present)
OPTIONAL_PROTOCOL_TOP_LEVEL = (
    "sample_size_policy",
    "intervention_levels",
    # ``governance`` is metadata-only (provenance, custodian, etc.); accepted
    # by released bundles but not interpreted by the evaluator.
    "governance",
)

REQUIRED_UNIT_OF_WORK = (
    "task_id",
    "model_id",
    "dataset_id",
    "metric_id",
    "clean_corrupt_definition",
)

OPTIONAL_UNIT_OF_WORK_MODEL_SPEC = (
    "n_layers",
    "n_heads",
)

REQUIRED_EXECUTION_GRID = (
    "seeds",
    "prompt_variants",
    "resample_ids",
    "methods",
)

REQUIRED_CONTROL_POLICY = (
    "required_families",
    "max_control_abs_mean",
)

REQUIRED_STAGE_GATES = (
    "min_causal_effect",
    "min_specificity_ratio",
    "min_robustness",
    "max_method_sensitivity_std",
    "require_confirmatory_ci_excludes_zero",
)

# Optional stage-gate keys (V7/V8/V9 extensions)
OPTIONAL_STAGE_GATES = (
    "min_effect_size_d",
    "min_practical_cohens_d",
    "min_rank_stability_tau",
    "baseline_superiority_ratio",
    "cross_model_rank_stability_tau",
    "require_bidirectional",
)

REQUIRED_MIN_ROBUSTNESS_AXES = (
    "seed",
    "prompt_variant",
    "resample",
)

REQUIRED_STATISTICAL_POLICY = (
    "alpha",
    "fdr_q",
    "min_effect_floor",
    "multiplicity_method",
)

REQUIRED_CLAIM_BUDGET = (
    "max_total_claims",
    "max_claims_per_task",
)

REQUIRED_LANGUAGE_POLICY = (
    "forbidden_without_pass",
)

# Optional sample-size policy (V7 extension)
OPTIONAL_SAMPLE_SIZE_POLICY_KEYS = (
    "min_examples_per_cell",
    "exploratory_fraction",
    "power_target",
    "minimum_detectable_effect",
    "require_confirmatory_split",
    "min_cells_per_hypothesis",
)

# ---------------------------------------------------------------------------
# Control families
# ---------------------------------------------------------------------------

MANDATORY_CONTROL_FAMILIES = (
    "wrong_position",
    "wrong_layer",
    "random_component",
    "mismatched_source",
)

EXTENDED_CONTROL_FAMILIES = (
    "shuffled_token",
    "adjacent_head",
)

# ---------------------------------------------------------------------------
# Language policy
# ---------------------------------------------------------------------------

DEFAULT_FORBIDDEN_TERMS = (
    "solved",
    "proved",
    "proven",
    "validated",
    "confirmed",
    "mechanism discovered",
)

# Canonical evidence-tier language constraints
EVIDENCE_TIER_ALLOWED_LANGUAGE = {
    "cross_model_confirmed": [
        "causally contributes across model families",
        "transfers across architectures",
        "replicates across model families",
    ],
    "single_model_confirmed": [
        "causally contributes",
        "is necessary for",
        "is causally relevant",
    ],
    "causal_plus_robustness": [
        "causally contributes",
        "is necessary for",
    ],
    "causal_tested_unstable": [
        "preliminary causal evidence",
        "unstable across",
    ],
    "suggestive": [
        "correlates with",
        "is associated with",
    ],
    "rejected": [],
}

# ---------------------------------------------------------------------------
# Intervention levels (V7)
# ---------------------------------------------------------------------------

ALLOWED_INTERVENTION_LEVELS = (
    "head",
    "mlp",
    "residual_stream",
    "edge",
    "mlp_neuron",
    "sae_feature",
    "das_subspace",
    "transcoder_feature",
)

ALLOWED_COMPONENT_TYPES = (
    "head",
    "mlp",
    "residual_stream",
    "edge",
    "mlp_neuron",
    "sae_feature",
    "das_subspace",
    "transcoder_feature",
)

# Component-type-specific required fields (beyond component_type itself)
COMPONENT_REQUIRED_FIELDS = {
    "head": ("layer", "head"),
    "mlp": ("layer",),
    "residual_stream": ("layer",),
    "edge": ("source_layer", "source_head", "target_layer", "target_head"),
    "mlp_neuron": ("layer", "neuron"),
    "sae_feature": ("sae_id", "layer", "feature_id"),
    "das_subspace": ("layer", "subspace_dim"),
    "transcoder_feature": ("layer", "feature_id"),
}

# Control families required per component type
CONTROL_FAMILIES_BY_COMPONENT = {
    "head": (
        "wrong_position", "wrong_layer", "random_component",
        "mismatched_source", "shuffled_token", "adjacent_head",
    ),
    "mlp": (
        "wrong_position", "wrong_layer", "random_component",
        "mismatched_source", "shuffled_token",
    ),
    "residual_stream": (
        "wrong_position", "wrong_layer",
        "random_component", "mismatched_source",
    ),
    "edge": (
        "wrong_position", "wrong_layer", "random_component",
        "mismatched_source", "random_edge",
    ),
    "mlp_neuron": (
        "wrong_position", "wrong_layer", "random_neuron",
        "mismatched_source", "adjacent_neuron",
    ),
    "sae_feature": (
        "wrong_layer_feature", "random_feature",
        "mismatched_sae_source", "wrong_position",
    ),
    "das_subspace": (
        "wrong_layer", "random_subspace",
        "mismatched_source", "wrong_position",
    ),
    "transcoder_feature": (
        "wrong_layer_feature", "random_feature",
        "mismatched_source", "wrong_position",
    ),
}

ALLOWED_PATCH_MODES = (
    "clean",
    "zero",
    "mean",
    "resample",
    "clamp",
)

# ---------------------------------------------------------------------------
# Hypothesis schema
# ---------------------------------------------------------------------------

REQUIRED_HYPOTHESIS_FIELDS = (
    "hypothesis_id",
    "protocol_id",
    "task_id",
    "model_id",
    "metric_id",
    "claim_text",
    "candidate_components",
    "predicted_effect_direction",
    "predicted_min_effect",
    "predicted_specificity_ratio",
    "expected_failure_modes",
)

# Optional hypothesis fields (V10: provider provenance + SAE metadata)
OPTIONAL_HYPOTHESIS_FIELDS = (
    "intervention_level",
    "alternative_hypotheses",
    "provider_id",
    "provider_version",
    "explanation_text",
    "simulation_score",
    "sae_id",
    "sae_site",
    "prompt_family",
    "discovery_lane",
)

ALLOWED_EFFECT_DIRECTIONS = ("increase", "decrease")

# ---------------------------------------------------------------------------
# Evaluation result schema
# ---------------------------------------------------------------------------

REQUIRED_EVAL_TOP_LEVEL = (
    "protocol_id",
    "protocol_sha256",
    "hypothesis_results",
)

REQUIRED_HYPOTHESIS_RESULT_FIELDS = (
    "hypothesis_id",
    "raw_cells",
)

REQUIRED_RAW_CELL_FIELDS = (
    "seed",
    "prompt_variant",
    "resample_id",
    "method",
    "slice",
    "treatment_effect",
    "control_effects",
    "runner_id",
    "runner_version",
    "pipeline_sha",
    "model_ref",
    "dataset_seed",
    "prompt_template_id",
)

# Optional raw-cell fields (V7 provenance extensions)
OPTIONAL_RAW_CELL_FIELDS = (
    "direction",
    "intervention_level",
    "standardized_effect",
    "raw_logit_diff",
    "accuracy_delta",
    "hardware_info",
)

# Optional cross-model results section (V8)
OPTIONAL_CROSS_MODEL_KEYS = (
    "model_id",
    "family",
    "hypothesis_effects",
)

ALLOWED_SLICES = ("exploratory", "confirmatory")

# ---------------------------------------------------------------------------
# Model registry (V7)
# ---------------------------------------------------------------------------

MODEL_REGISTRY = {
    "gpt2-small": {
        "family": "gpt2",
        "n_layers": 12,
        "n_heads": 12,
        "d_model": 768,
        "transformer_lens_name": "gpt2-small",
    },
    # Audit-final §2.D.1: the bare ``gpt2`` alias was removed because it
    # silently mapped to ``gpt2-small`` and let bundles claim "gpt2"
    # provenance without committing to a specific size variant. Submitters
    # must now explicitly use ``gpt2-small`` / ``gpt2-medium`` / ``gpt2-large``.
    "gpt2-medium": {
        "family": "gpt2",
        "n_layers": 24,
        "n_heads": 16,
        "d_model": 1024,
        "transformer_lens_name": "gpt2-medium",
    },
    "gpt2-large": {
        "family": "gpt2",
        "n_layers": 36,
        "n_heads": 20,
        "d_model": 1280,
        "transformer_lens_name": "gpt2-large",
    },
    "pythia-70m": {
        "family": "pythia",
        "n_layers": 6,
        "n_heads": 8,
        "d_model": 512,
        "transformer_lens_name": "EleutherAI/pythia-70m",
    },
    "pythia-160m": {
        "family": "pythia",
        "n_layers": 12,
        "n_heads": 12,
        "d_model": 768,
        "transformer_lens_name": "EleutherAI/pythia-160m",
    },
    "pythia-410m": {
        "family": "pythia",
        "n_layers": 24,
        "n_heads": 16,
        "d_model": 1024,
        "transformer_lens_name": "EleutherAI/pythia-410m",
    },
    "pythia-1b": {
        "family": "pythia",
        "n_layers": 16,
        "n_heads": 8,
        "d_model": 2048,
        "transformer_lens_name": "EleutherAI/pythia-1b",
    },
}

# ---------------------------------------------------------------------------
# Task registry (V7)
# ---------------------------------------------------------------------------

TASK_REGISTRY = {
    "ioi_v0": {
        "name": "Indirect Object Identification",
        "domain": "syntax",
        "complexity": "medium",
        "module": "automechinterp_runner.tasks.ioi",
    },
    "greater_than_v0": {
        "name": "Greater-Than Comparison",
        "domain": "arithmetic",
        "complexity": "low",
        "module": "automechinterp_runner.tasks.greater_than",
    },
    "gendered_pronoun_v0": {
        "name": "Gendered Pronoun Resolution",
        "domain": "syntax",
        "complexity": "low",
        "module": "automechinterp_runner.tasks.gendered_pronoun",
    },
    "docstring_v0": {
        "name": "Docstring Completion",
        "domain": "code",
        "complexity": "medium",
        "module": "automechinterp_runner.tasks.docstring",
    },
    "country_capital_v0": {
        "name": "Country-Capital Recall",
        "domain": "factual",
        "complexity": "medium",
        "module": "automechinterp_runner.tasks.country_capital",
    },
    "sentiment_v0": {
        "name": "Sentiment Direction",
        "domain": "sentiment",
        "complexity": "medium",
        "module": "automechinterp_runner.tasks.sentiment",
    },
    "fact_recall_v0": {
        "name": "Single-Fact Recall",
        "domain": "factual",
        "complexity": "high",
        "module": "automechinterp_runner.tasks.fact_recall",
    },
    "arithmetic_v0": {
        "name": "Simple Arithmetic",
        "domain": "arithmetic",
        "complexity": "high",
        "module": "automechinterp_runner.tasks.arithmetic",
    },
}
