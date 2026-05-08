"""Deterministic stage-gate evaluator for mechanistic claims.

V12: 15 hard gates including bidirectional enforcement, compensatory
mechanism detection, cross-model transfer, edge-level support,
publication-grade statistics (BCa bootstrap CI, permutation p-values,
power analysis, Cohen's d, Holm-Bonferroni, inter-rerun agreement),
tightened evidence tiers, protocol critic, and multi-lane provider
architecture with 7 component types.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import math
from pathlib import Path
from statistics import mean, pstdev, stdev

from .constants import (
    CORE_GATES,
    DEFAULT_BOOTSTRAP_RESAMPLES,
    DEFAULT_PERMUTATION_ITERATIONS,
    EVIDENCE_TIER_ORDER,
    EPSILON,
    GATE_FAIL,
    GATE_NOT_EVALUATED,
    GATE_PASS,
    NOT_EVALUATED_GUIDANCE,
    OPTIONAL_GATES,
)
from .loader import load_bundle
from .io_utils import BundleError, read_json_any

# ---------------------------------------------------------------------------
# Statistical primitives (dependency-free, deterministic via seeded RNG)
# ---------------------------------------------------------------------------

def _seeded_rng_ints(seed_material: str, n: int, modulus: int) -> list[int]:
    """Generate deterministic pseudo-random integers from seed material.

    Uses the first 32 bits of a SHA-256 digest reduced modulo ``modulus``.
    For ``modulus`` values that do not divide ``2**32`` evenly there is a
    small modulo bias (the lowest ``2**32 % modulus`` residues appear with
    probability ``ceil(2**32 / modulus) / 2**32`` instead of
    ``floor(2**32 / modulus) / 2**32``). The bias is on the order of
    ``modulus / 2**32`` per draw, i.e. negligible for the values used in
    this module (``modulus`` is the bundle size for bootstrap resampling
    and ``2`` for permutation sign flips). Replacing this with an
    arithmetically-unbiased rejection-sampling sampler is documented as
    a known pitfall in ``methodology/pitfalls.md`` (see F-008 in the
    audit findings inventory) and is intentionally not changed here in
    order to preserve byte-identical reproducibility of the released
    artifacts.
    """
    results: list[int] = []
    for i in range(n):
        digest = hashlib.sha256(f"{seed_material}|{i}".encode("utf-8")).hexdigest()
        results.append(int(digest[:8], 16) % modulus)
    return results

def _norm_cdf(x: float) -> float:
    """Standard normal CDF via the error function (math.erf)."""
    from math import erf, sqrt
    return 0.5 * (1.0 + erf(x / sqrt(2.0)))

def _norm_ppf(p: float) -> float:
    """Standard normal inverse CDF (quantile function), AS241.

    Implements algorithm AS241 of Wichura (1988), "Algorithm AS241:
    The Percentage Points of the Normal Distribution",
    Applied Statistics 37(3), 477-484. AS241 provides full
    double-precision accuracy (relative error on the order of 1e-15)
    over the entire ``(0, 1)`` open interval, including the deep tails
    where the prior Beasley-Springer-Moro / AS 26.2.23 rational
    approximation degraded to ~1e-3 accuracy. The rest of the BCa
    machinery (jackknife acceleration, bias correction) is sensitive
    to small inaccuracies in z0 and the tail z_alpha quantiles when
    the bootstrap distribution is skewed, so AS241 is preferred.

    The implementation is kept dependency-free; an end-to-end parity
    test against ``scipy.stats.norm.ppf`` is provided in
    ``packages/evaluator/tests/test_norm_ppf_parity.py``, gated on
    ``pytest.importorskip("scipy")`` so that the package retains zero
    runtime dependency on scipy.

    The function is total on ``(0, 1)``; for boundary inputs it
    returns the saturated values ``-inf``/``+inf`` matching
    ``scipy.stats.norm.ppf`` semantics. The previous implementation
    returned ``-6.0``/``6.0`` for ``p<=0``/``p>=1``; that legacy
    saturation was a workaround for the AS 26.2.23 tail blow-up and
    is no longer needed. Existing callers in this module clamp ``p``
    to ``[1e-10, 1 - 1e-10]`` before calling, so the boundary
    behavior change is unobservable in production.
    """
    if p <= 0.0:
        return float("-inf")
    if p >= 1.0:
        return float("inf")

    # AS241 split coefficients.
    # Central region: |q| <= 0.425
    # Intermediate / tail region: |q| in (0.425, ~3.7]
    # Far tail region: |q| > ~3.7
    a = (
        3.3871328727963666080,
        1.3314166789178437745e2,
        1.9715909503065514427e3,
        1.3731693765509461125e4,
        4.5921953931549871457e4,
        6.7265770927008700853e4,
        3.3430575583588128105e4,
        2.5090809287301226727e3,
    )
    b = (
        4.2313330701600911252e1,
        6.8718700749205790830e2,
        5.3941960214247511077e3,
        2.1213794301586595867e4,
        3.9307895800092710610e4,
        2.8729085735721942674e4,
        5.2264952788528545610e3,
    )
    c = (
        1.42343711074968357734,
        4.63033784615654529590,
        5.76949722146069140550,
        3.64784832476320460504,
        1.27045825245236838258,
        2.41780725177450611770e-1,
        2.27238449892691845833e-2,
        7.74545014278341407640e-4,
    )
    d = (
        2.05319162663775882187,
        1.67638483018380384940,
        6.89767334985100004550e-1,
        1.48103976427480074590e-1,
        1.51986665636164571966e-2,
        5.47593808499534494600e-4,
        1.05075007164441684324e-9,
    )
    e = (
        6.65790464350110377720,
        5.46378491116411436990,
        1.78482653991729133580,
        2.96560571828504891230e-1,
        2.65321895265761230930e-2,
        1.24266094738807843860e-3,
        2.71155556874348757815e-5,
        2.01033439929228813265e-7,
    )
    f = (
        5.99832206555887937690e-1,
        1.36929880988191046770e-1,
        1.48753612908506148525e-2,
        7.86869131145613259100e-4,
        1.84631831751005468180e-5,
        1.42151175831644588870e-7,
        2.04426310338993978564e-15,
    )

    q = p - 0.5
    if abs(q) <= 0.425:
        # Central region.
        r = 0.180625 - q * q
        num = ((((((a[7] * r + a[6]) * r + a[5]) * r + a[4]) * r + a[3]) * r + a[2]) * r + a[1]) * r + a[0]
        den = ((((((b[6] * r + b[5]) * r + b[4]) * r + b[3]) * r + b[2]) * r + b[1]) * r + b[0]) * r + 1.0
        return q * num / den

    r = p if q < 0.0 else 1.0 - p
    if r <= 0.0:
        # Defensive: handled above by the boundary returns, but keep this in
        # case future callers omit the clamp.
        return float("-inf") if q < 0.0 else float("inf")
    r = math.sqrt(-math.log(r))

    if r <= 5.0:
        # Intermediate-tail region.
        r -= 1.6
        num = ((((((c[7] * r + c[6]) * r + c[5]) * r + c[4]) * r + c[3]) * r + c[2]) * r + c[1]) * r + c[0]
        den = ((((((d[6] * r + d[5]) * r + d[4]) * r + d[3]) * r + d[2]) * r + d[1]) * r + d[0]) * r + 1.0
        result = num / den
    else:
        # Far-tail region.
        r -= 5.0
        num = ((((((e[7] * r + e[6]) * r + e[5]) * r + e[4]) * r + e[3]) * r + e[2]) * r + e[1]) * r + e[0]
        den = ((((((f[6] * r + f[5]) * r + f[4]) * r + f[3]) * r + f[2]) * r + f[1]) * r + f[0]) * r + 1.0
        result = num / den

    return -result if q < 0.0 else result

def _bootstrap_ci(
    values: list[float],
    confidence: float = 0.95,
    n_resamples: int = DEFAULT_BOOTSTRAP_RESAMPLES,
    seed: str = "bootstrap",
) -> tuple[float, float]:
    """Compute bootstrap confidence interval (BCa method).

    V12: Upgraded from percentile to BCa (bias-corrected and accelerated).
    BCa corrects for bias and skewness in the bootstrap distribution,
    producing more accurate intervals especially for small samples.
    Falls back to percentile if jackknife acceleration fails.

    Uses deterministic seeded resampling for reproducibility.
    Inverse-normal evaluations use the module-level AS241 ``_norm_ppf``
    (Wichura 1988); CDF evaluations use ``_norm_cdf`` via ``math.erf``.
    """
    if not values or len(values) < 2:
        v = values[0] if values else 0.0
        return (v, v)

    n = len(values)
    alpha = 1.0 - confidence
    theta_hat = mean(values)

    # Generate bootstrap resamples
    boot_means: list[float] = []
    for b in range(n_resamples):
        indices = _seeded_rng_ints(f"{seed}|{b}", n, n)
        sample = [values[idx] for idx in indices]
        boot_means.append(mean(sample))

    boot_means.sort()

    # Degenerate-distribution short-circuit. If every bootstrap replicate
    # collapsed to the same value (possible when ``values`` is itself
    # degenerate, e.g. all zeros), the BCa bias-correction term and the
    # jackknife acceleration term are both undefined; return the point
    # estimate as a zero-width interval rather than feeding ``±inf`` through
    # the bias-correction arithmetic. Audit M-2026-05 (BCa redesign).
    if pstdev(boot_means) <= EPSILON:
        return (theta_hat, theta_hat)

    # --- BCa bias correction (z0) ---
    # Efron-DiCiccio define z0 = Phi^{-1}(#{theta* <= theta_hat} / B), i.e.
    # ``<=`` including ties. Strict ``<`` undercounts ties and biases z0
    # toward -inf for discrete or near-degenerate bootstrap distributions.
    count_below = sum(1 for m in boot_means if m <= theta_hat)
    p_below = count_below / len(boot_means)
    z0 = _norm_ppf(p_below)  # may be ±inf if p_below saturates to 0.0/1.0

    # --- BCa acceleration (a_hat) via jackknife ---
    jack_means: list[float] = []
    for i in range(n):
        leave_one = values[:i] + values[i + 1:]
        jack_means.append(mean(leave_one))
    jack_bar = mean(jack_means)
    diffs = [jack_bar - jm for jm in jack_means]
    sum_d2 = sum(d * d for d in diffs)
    sum_d3 = sum(d * d * d for d in diffs)

    if sum_d2 > EPSILON:
        a_hat = sum_d3 / (6.0 * (sum_d2 ** 1.5))
    else:
        a_hat = 0.0  # fallback to percentile

    # --- BCa adjusted quantiles ---
    z_alpha_lo = _norm_ppf(alpha / 2.0)
    z_alpha_hi = _norm_ppf(1.0 - alpha / 2.0)

    denom_lo = 1.0 - a_hat * (z0 + z_alpha_lo)
    denom_hi = 1.0 - a_hat * (z0 + z_alpha_hi)

    # Finiteness guard: if ``z0`` saturated to ±inf (BCa boundary case) or
    # the denominators are non-finite or near zero, fall back to the
    # percentile interval rather than propagate NaN/inf into the index
    # arithmetic, which would otherwise raise ``ValueError: cannot convert
    # float NaN to integer`` at the ``int(math.ceil(...))`` step below.
    bca_finite = (
        math.isfinite(z0)
        and math.isfinite(denom_lo)
        and math.isfinite(denom_hi)
        and abs(denom_lo) > EPSILON
        and abs(denom_hi) > EPSILON
    )
    if bca_finite:
        adj_lo = _norm_cdf(z0 + (z0 + z_alpha_lo) / denom_lo)
        adj_hi = _norm_cdf(z0 + (z0 + z_alpha_hi) / denom_hi)
        if not (math.isfinite(adj_lo) and math.isfinite(adj_hi)):
            adj_lo = alpha / 2.0
            adj_hi = 1.0 - alpha / 2.0
    else:
        adj_lo = alpha / 2.0
        adj_hi = 1.0 - alpha / 2.0

    lo_idx = max(0, int(math.floor(adj_lo * len(boot_means))))
    hi_idx = min(len(boot_means) - 1, int(math.ceil(adj_hi * len(boot_means))) - 1)
    if hi_idx < lo_idx:
        hi_idx = lo_idx
    return (boot_means[lo_idx], boot_means[hi_idx])

def _interrerun_agreement(
    rerun_verdicts: list[list[bool]],
) -> float:
    """Compute inter-rerun agreement (proportion of unanimous decisions).

    V12: Implements a simple agreement metric across multiple reruns.
    Each entry in rerun_verdicts is a list of per-hypothesis pass/fail
    booleans from one rerun. Returns the fraction of hypotheses where
    all reruns agree on the verdict.

    For a single rerun, returns 1.0 (trivially agreed).
    """
    if len(rerun_verdicts) <= 1:
        return 1.0
    n_hypotheses = len(rerun_verdicts[0])
    if n_hypotheses == 0:
        return 1.0
    agreed = 0
    for h_idx in range(n_hypotheses):
        verdicts = [run[h_idx] for run in rerun_verdicts if h_idx < len(run)]
        if len(set(verdicts)) == 1:
            agreed += 1
    return agreed / n_hypotheses

def _permutation_p_value(
    values: list[float],
    n_permutations: int = DEFAULT_PERMUTATION_ITERATIONS,
    seed: str = "permtest",
) -> float:
    """Two-sided permutation test for H0: location is symmetric about zero.

    Builds the null by randomly flipping the sign of each observation, then
    reports the (Monte Carlo) two-sided probability of observing a sample
    mean at least as extreme (in absolute value) as the one actually
    observed.

    **Null hypothesis being tested.** Sign-flip permutation gives an exact
    (or, here, MC-approximate) test under the assumption that the
    observations are exchangeable with respect to a sign flip --- i.e.,
    that the per-observation distribution is **symmetric about zero under
    H0**. This is appropriate for treatment-effect cells where each cell's
    value is a difference (treatment minus control under matched conditions),
    so the sign-flip null is "no treatment effect". It is **not** appropriate
    for raw activations, raw probabilities, or any other quantity whose
    null distribution is not symmetric about zero; for those, a different
    permutation scheme (e.g. label permutation across two groups) would be
    required. The cell ``treatment_effect`` field consumed by the rest of
    this module is constructed to satisfy the symmetric-null assumption.

    **MC correction.** Following Phipson & Smyth, "Permutation P-values
    Should Never Be Zero" (Stat. Appl. Genet. Mol. Biol. 2010), the
    Monte Carlo p-value is computed as ``(count_ge + 1) / (n_permutations + 1)``
    rather than ``count_ge / n_permutations``. The +1 in the numerator
    accounts for the observed sample being one valid (the identity)
    permutation under H0; the +1 in the denominator keeps the estimator
    unbiased and bounds the minimum reportable p-value at
    ``1 / (n_permutations + 1)`` so that an exhaustively-non-rejected
    test can never report a literal p of zero. With the default
    ``n_permutations`` this lower bound is ``1 / 10001 ≈ 9.999e-5``.

    Deterministic via seeded hash-based RNG (see ``_seeded_rng_ints``
    for the modulo-bias caveat; for ``modulus=2`` the bias is
    ``2 / 2**32 ≈ 4.7e-10`` per draw, far below MC noise).
    """
    if not values:
        return 1.0

    observed_stat = abs(mean(values))
    n = len(values)
    count_ge = 0

    for p in range(n_permutations):
        flips = _seeded_rng_ints(f"{seed}|{p}", n, 2)
        perm_values = [v if flips[i] == 0 else -v for i, v in enumerate(values)]
        perm_stat = abs(mean(perm_values))
        if perm_stat >= observed_stat:
            count_ge += 1

    # Phipson-Smyth correction: +1/+1.
    return (count_ge + 1) / (n_permutations + 1)

def _cohens_d(values: list[float]) -> float:
    """Compute Cohen's d for a one-sample test against zero."""
    if not values or len(values) < 2:
        return 0.0
    mu = mean(values)
    sd = stdev(values)
    if sd <= EPSILON:
        return float("inf") if abs(mu) > EPSILON else 0.0
    return mu / sd

def _minimum_sample_size(
    effect_size: float,
    alpha: float = 0.05,
    power: float = 0.80,
) -> int:
    """Approximate minimum n for one-sample t-test (two-sided).

    Uses the formula n >= ((z_alpha/2 + z_beta) / d)^2 where d is Cohen's d.
    """
    if effect_size <= EPSILON:
        return 999999

    # Audit-final §gemini.1: use the high-precision AS241 inverse-normal
    # CDF (``_norm_ppf``) rather than the lower-precision rational
    # ``_inv_erfc`` for power-analysis critical values; the rest of the
    # module uses ``_norm_ppf`` for bootstrap intervals, and consistency
    # avoids two different statistical tail standards living in one file.
    z_alpha = _norm_ppf(1.0 - alpha / 2.0)
    z_beta = _norm_ppf(power)
    n = math.ceil(((z_alpha + z_beta) / effect_size) ** 2)
    return max(n, 4)

def _inv_erfc(p: float) -> float:
    """Approximate inverse complementary error function (rational approx)."""
    if p <= 0.0:
        return float("inf")
    if p >= 2.0:
        return float("-inf")
    if p >= 1.0:
        return -_inv_erfc(2.0 - p)
    t = math.sqrt(-2.0 * math.log(p / 2.0))
    c0, c1, c2 = 2.515517, 0.802853, 0.010328
    d1, d2, d3 = 1.432788, 0.189269, 0.001308
    return t - (c0 + c1 * t + c2 * t * t) / (1.0 + d1 * t + d2 * t * t + d3 * t * t * t)

def _quantile(values: list[float], q: float) -> float:
    """Linear interpolation quantile (retained for backwards compat)."""
    if not values:
        return 0.0
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    pos = (len(ordered) - 1) * q
    lower = int(math.floor(pos))
    upper = int(math.ceil(pos))
    if lower == upper:
        return ordered[lower]
    weight = pos - lower
    return ordered[lower] * (1.0 - weight) + ordered[upper] * weight

# ---------------------------------------------------------------------------
# Multiplicity correction
# ---------------------------------------------------------------------------

def _bh_q_values(items: list[tuple[str, float]]) -> dict[str, float]:
    """Benjamini-Hochberg FDR correction."""
    if not items:
        return {}
    ordered = sorted(items, key=lambda x: x[1])
    n = len(ordered)
    qvals: dict[str, float] = {}
    prev = 1.0
    for rank, (hid, pval) in enumerate(reversed(ordered), start=1):
        i = n - rank + 1
        candidate = min(prev, (pval * n) / max(i, 1))
        qvals[hid] = candidate
        prev = candidate
    return qvals

def _holm_bonferroni(items: list[tuple[str, float]]) -> dict[str, float]:
    """Holm-Bonferroni step-down correction. Returns adjusted p-values."""
    if not items:
        return {}
    ordered = sorted(items, key=lambda x: x[1])
    n = len(ordered)
    adjusted: dict[str, float] = {}
    prev = 0.0
    for rank, (hid, pval) in enumerate(ordered):
        k = n - rank
        adj = min(1.0, max(prev, pval * k))
        adjusted[hid] = adj
        prev = adj
    return adjusted

# ---------------------------------------------------------------------------
# Grid / direction helpers
# ---------------------------------------------------------------------------

def _expected_grid(protocol: dict) -> set[tuple[int, str, int, str]]:
    grid = protocol["execution_grid"]
    return {
        (seed, prompt, resample_id, method)
        for seed, prompt, resample_id, method in itertools.product(
            grid["seeds"],
            grid["prompt_variants"],
            grid["resample_ids"],
            grid["methods"],
        )
    }

def _direction_pass(value: float, direction: str, floor: float) -> bool:
    if direction == "increase":
        return value >= floor
    return value <= -floor

def _axis_consistency(
    cells: list[dict],
    axis: str,
    direction: str,
    floor: float,
) -> float:
    grouped: dict[object, list[float]] = {}
    for cell in cells:
        grouped.setdefault(cell[axis], []).append(float(cell["treatment_effect"]))
    if not grouped:
        return 0.0
    passes = 0
    for _, vals in grouped.items():
        axis_mean = mean(vals)
        if _direction_pass(axis_mean, direction, floor):
            passes += 1
    return passes / len(grouped)

def _contains_confirmatory(cells: list[dict]) -> bool:
    return any(cell["slice"] == "confirmatory" for cell in cells)

def _contains_exploratory(cells: list[dict]) -> bool:
    return any(cell["slice"] == "exploratory" for cell in cells)

def _kendall_tau(rankings_a: list[float], rankings_b: list[float]) -> float:
    """Rank-correlation between two rankings using the Goodman--Kruskal
    gamma form ``(C - D) / (C + D)``, where ``C`` and ``D`` count
    concordant and discordant pairs.

    This is *not* tau-b: tied pairs are dropped from the denominator
    rather than corrected for, so on tie-free inputs it reduces to
    tau-a, and on inputs with ties it agrees with Goodman--Kruskal
    gamma. The benchmark uses this primitive only on continuous-valued
    rankings where ties are vanishingly rare; the rank-stability gate
    therefore treats the function as ``tau-a-equivalent``.

    Edge cases:
      * ``n < 2``: returns ``1.0`` (a single-element ranking is
        trivially monotone with itself).
      * ``concordant + discordant == 0`` (all observed pairs tied):
        returns ``1.0`` for byte-stable backward compatibility with
        released artifacts. Callers that need to distinguish "no
        information" from "perfect agreement" should inspect the
        underlying ranking lengths and tie counts directly.
    """
    # Audit-final §gpt2.B4: silently truncating mismatched-length input
    # via ``zip`` masks alignment bugs upstream and produces a tau on a
    # truncated prefix.
    if len(rankings_a) != len(rankings_b):
        raise ValueError(
            f"_kendall_tau: rankings_a (len={len(rankings_a)}) and rankings_b "
            f"(len={len(rankings_b)}) must be equal length"
        )
    n = len(rankings_a)
    if n < 2:
        return 1.0
    concordant = 0
    discordant = 0
    for i in range(n):
        for j in range(i + 1, n):
            sign_a = (rankings_a[j] - rankings_a[i])
            sign_b = (rankings_b[j] - rankings_b[i])
            product = sign_a * sign_b
            if product > 0:
                concordant += 1
            elif product < 0:
                discordant += 1
    denom = concordant + discordant
    if denom == 0:
        return 1.0
    return (concordant - discordant) / denom

def _normalize_gate_outcomes(checks: dict[str, bool | str]) -> dict[str, str]:
    """Convert legacy bool/mixed checks into canonical gate outcomes."""
    gate_outcomes: dict[str, str] = {}
    for gate, value in checks.items():
        if value == "not_evaluated":
            gate_outcomes[gate] = GATE_NOT_EVALUATED
        elif value is True:
            gate_outcomes[gate] = GATE_PASS
        else:
            gate_outcomes[gate] = GATE_FAIL
    return gate_outcomes

def _classify_evidence_tier(
    checks: dict[str, bool | str],
    *,
    exploratory_present: bool | None = None,
) -> tuple[str, bool, list[str], list[str], list[str]]:
    """Classify a claim using the canonical evidence-tier contract.

    ``exploratory_present`` is the **observed** presence of an exploratory
    slice in the bundle, NOT a derived gate outcome. Callers in this module
    pass it explicitly from ``bool(exploratory)`` (see ``_summarize_hypothesis``
    line near 687) or from the persisted metric (see the report-replay path
    near line 893). When ``exploratory_present`` is ``None`` we default to
    ``False`` — the conservative reading — so that an external caller who
    forgets the keyword argument cannot accidentally promote a claim to
    ``single_model_confirmed``/``cross_model_confirmed`` on the basis of a
    trivially-passed ``confirmatory_firewall`` gate.

    Specifically: ``confirmatory_firewall_pass`` is set to ``True`` whenever
    the protocol does NOT declare ``sample_size_policy.require_confirmatory_split``
    (see ``_summarize_hypothesis`` lines 466-472). Reading that gate value to
    infer "the bundle has an exploratory slice" is therefore unsound. The
    explicit ``exploratory_present`` argument carries the truthful signal.
    """
    core_failed = [k for k in checks if k in CORE_GATES and checks[k] is False]
    core_not_eval = [k for k in checks if k in CORE_GATES and checks[k] == "not_evaluated"]
    optional_failed = [k for k in checks if k in OPTIONAL_GATES and checks[k] is False]
    optional_not_eval = [k for k in checks if k in OPTIONAL_GATES and checks[k] == "not_evaluated"]
    failed_gates = core_failed + optional_failed
    not_evaluated_gates = core_not_eval + optional_not_eval

    all_core_pass = len(core_failed) == 0 and len(core_not_eval) == 0
    all_optional_pass = len(optional_failed) == 0 and len(optional_not_eval) == 0
    confirmatory_present = checks.get("confirmatory_present") is True
    if exploratory_present is None:
        # Conservative default: assume no exploratory slice unless the caller
        # affirmatively supplies one. See docstring above for why we do NOT
        # fall back to ``checks.get("confirmatory_firewall")``.
        exploratory_present = False

    if all_core_pass and all_optional_pass and confirmatory_present and exploratory_present:
        evidence_tier = "cross_model_confirmed"
        demotion_reason: list[str] = []
    elif all_core_pass and confirmatory_present and exploratory_present:
        evidence_tier = "single_model_confirmed"
        demotion_reason = ["optional_gate_failed:" + g for g in optional_failed] + [
            "optional_gate_not_evaluated:" + g for g in optional_not_eval
        ]
    elif all_core_pass:
        evidence_tier = "causal_plus_robustness"
        demotion_reason = []
        if not confirmatory_present:
            demotion_reason.append("missing_confirmatory_slice")
        if not exploratory_present:
            demotion_reason.append("missing_exploratory_slice")
        demotion_reason += ["optional_gate_failed:" + g for g in optional_failed]
        demotion_reason += ["optional_gate_not_evaluated:" + g for g in optional_not_eval]
    elif (
        checks.get("causal_effect") is True
        and checks.get("negative_controls") is True
        and checks.get("robustness") is True
        and checks.get("bidirectional") is True
        and checks.get("method_sensitivity") is True
    ):
        evidence_tier = "causal_tested_unstable"
        demotion_reason = ["core_gate_failed:" + g for g in core_failed] + [
            "core_gate_not_evaluated:" + g for g in core_not_eval
        ]
    elif checks.get("causal_effect") is True and checks.get("negative_controls") is True:
        evidence_tier = "suggestive"
        demotion_reason = ["core_gate_failed:" + g for g in core_failed] + [
            "core_gate_not_evaluated:" + g for g in core_not_eval
        ]
    else:
        evidence_tier = "rejected"
        demotion_reason = ["core_gate_failed:" + g for g in core_failed] + [
            "core_gate_not_evaluated:" + g for g in core_not_eval
        ]

    passed = evidence_tier in ("single_model_confirmed", "cross_model_confirmed")
    # surface a structured demotion reason so the
    # gate-failure analyses can attribute tier-classification outcomes to
    # specific gate failures rather than re-deriving them downstream.
    return evidence_tier, passed, failed_gates, not_evaluated_gates, demotion_reason

# ---------------------------------------------------------------------------
# Per-hypothesis evaluation
# ---------------------------------------------------------------------------

def _summarize_hypothesis(
    protocol: dict,
    hypothesis: dict,
    hypothesis_result: dict,
    q_value: float,
    holm_adjusted_p: float,
) -> dict:
    stage = protocol["stage_gates"]
    stat = protocol["statistical_policy"]
    control_policy = protocol["control_policy"]

    # ---- Execution coverage gate ----
    expected = _expected_grid(protocol)
    observed = {
        (
            int(cell["seed"]),
            str(cell["prompt_variant"]),
            int(cell["resample_id"]),
            str(cell["method"]),
        )
        for cell in hypothesis_result["raw_cells"]
    }
    missing = sorted(expected - observed)
    undeclared = sorted(observed - expected)
    coverage_pass = (not missing) and (not undeclared)

    # ---- Slice separation ----
    cells = hypothesis_result["raw_cells"]
    confirmatory = [c for c in cells if c["slice"] == "confirmatory"]
    exploratory = [c for c in cells if c["slice"] == "exploratory"]
    confirmatory_present = bool(confirmatory)
    exploratory_present = bool(exploratory)
    scope_cells = confirmatory if confirmatory_present else cells

    # ---- Confirmatory firewall gate (NEW) ----
    sample_size_policy = protocol.get("sample_size_policy", {})
    # default to **fail-closed** (require=True). The
    # previous default (``False``) silently treated bundles without a
    # confirmatory/exploratory split as if they passed the firewall, which
    # is exactly the leak the gate is meant to detect. A protocol can still
    # opt out by setting ``require_confirmatory_split: false``.
    confirmatory_firewall_required = sample_size_policy.get("require_confirmatory_split", True)
    if confirmatory_firewall_required:
        confirmatory_firewall_pass = confirmatory_present and exploratory_present
    else:
        # surface the effective
        # opt-out so downstream aggregators can refuse to count vacuous
        # gate-passes as gate evidence. The gate stays True (a protocol that
        # explicitly declines a confirmatory/exploratory split is still
        # honoured), but the per-claim summary records that the pass is
        # vacuous rather than satisfied.
        # C1 : we considered
        # tightening this to ``confirmatory_present and exploratory_present``
        # so opt-out cannot vacuously pass the firewall, but verified the
        # protection is already enforced one layer up: the tier classifier
        # only awards ``single_model_confirmed`` / ``cross_model_confirmed``
        # when the *observed* ``exploratory_present`` flag (passed
        # explicitly from ``bool(exploratory)`` -- see line ~1048) is true.
        # Therefore an opt-out single-slice bundle can vacuously pass the
        # firewall gate but cannot reach a confirmed tier. We keep the
        # vacuous pass (legitimate ``causal_plus_robustness`` path is
        # preserved) and the ``confirmatory_firewall_vacuous`` flag below
        # signals the situation to downstream aggregators.
        confirmatory_firewall_pass = True
    confirmatory_firewall_vacuous = not confirmatory_firewall_required

    # ---- Treatment effect statistics ----
    treatment_values = [float(c["treatment_effect"]) for c in scope_cells]
    treatment_mean = mean(treatment_values) if treatment_values else 0.0

    # Bootstrap CI (replaces empirical quantile)
    hyp_id = hypothesis["hypothesis_id"]
    ci_low, ci_high = _bootstrap_ci(
        treatment_values,
        confidence=1.0 - float(stat["alpha"]),
        seed=f"ci|{hyp_id}",
    )

    # Cohen's d (NEW)
    effect_size_d = _cohens_d(treatment_values)

    # Permutation p-value (replaces normal approx)
    perm_p_value = _permutation_p_value(
        treatment_values,
        seed=f"perm|{hyp_id}",
    )

    # ---- Control statistics ----
    control_abs_values: list[float] = []
    for cell in scope_cells:
        for fam in control_policy["required_families"]:
            control_abs_values.append(abs(float(cell["control_effects"][fam])))
    control_abs_mean = mean(control_abs_values) if control_abs_values else float("inf")

    specificity_ratio = abs(treatment_mean) / (control_abs_mean + EPSILON)

    # ---- Causal effect gate ----
    min_floor = max(
        float(stage["min_causal_effect"]),
        float(stat["min_effect_floor"]),
        float(hypothesis["predicted_min_effect"]),
    )
    direction = hypothesis["predicted_effect_direction"]
    causal_pass = _direction_pass(treatment_mean, direction, min_floor)

    # ---- Negative controls gate ----
    control_pass = (
        control_abs_mean <= float(control_policy["max_control_abs_mean"])
        and specificity_ratio >= max(
            float(stage["min_specificity_ratio"]),
            float(hypothesis["predicted_specificity_ratio"]),
        )
    )

    # ---- Robustness gate ----
    # use max(min_effect_floor, predicted_min_effect) so a hypothesis declaring
    # `predicted_min_effect = 0.3` is judged robust only when per-axis means clear
    # the author's own pre-registered effect size, not just the (often lower)
    # protocol floor. This matches the causal-effect gate above and prevents
    # silent weakening of author-declared effect sizes during robustness checking.
    robustness_floor = max(
        float(stat["min_effect_floor"]),
        float(hypothesis["predicted_min_effect"]),
    )
    seed_consistency = _axis_consistency(scope_cells, "seed", direction, robustness_floor)
    prompt_consistency = _axis_consistency(
        scope_cells, "prompt_variant", direction, robustness_floor,
    )
    resample_consistency = _axis_consistency(
        scope_cells, "resample_id", direction, robustness_floor,
    )

    robust_cfg = stage["min_robustness"]
    robustness_pass = (
        seed_consistency >= float(robust_cfg["seed"])
        and prompt_consistency >= float(robust_cfg["prompt_variant"])
        and resample_consistency >= float(robust_cfg["resample"])
    )

    # ---- Method sensitivity gate ----
    method_groups: dict[str, list[float]] = {}
    for cell in scope_cells:
        method_groups.setdefault(str(cell["method"]), []).append(float(cell["treatment_effect"]))
    method_means = {m: mean(vals) for m, vals in sorted(method_groups.items())}
    method_std = pstdev(list(method_means.values())) if len(method_means) > 1 else 0.0
    sensitivity_pass = method_std <= float(stage["max_method_sensitivity_std"])

    # ---- Confirmatory CI gate (now with bootstrap CI) ----
    ci_excludes_zero = (ci_low > 0.0 and ci_high > 0.0) or (ci_low < 0.0 and ci_high < 0.0)
    ci_pass = (
        (not bool(stage["require_confirmatory_ci_excludes_zero"]))
        or (confirmatory_present and ci_excludes_zero)
    )

    # ---- Multiplicity gate ----
    multiplicity_pass = q_value <= float(stat["fdr_q"])

    # ---- Power adequacy gate ----
    min_d = float(stage.get("min_effect_size_d", 0.0))
    power_target = float(sample_size_policy.get("power_target", 0.80))
    # if a protocol omits
    # ``min_cells_per_hypothesis`` entirely, the power-adequacy gate used to
    # silently default to 0, disabling the cells-floor. Fall back to the
    # product of the declared axes (seeds × prompts × resamples × methods)
    # capped at the number of expected cells for this hypothesis, so that
    # silence is not a free pass. ``loader.validate_protocol`` already
    # rejects an explicit non-positive value.
    if "min_cells_per_hypothesis" in sample_size_policy:
        min_cells = int(sample_size_policy["min_cells_per_hypothesis"])
    else:
        min_cells = max(1, len(expected))
    if min_d > 0:
        # prior versions used ``max(observed_d, min_d)``
        # as the effect size in the power calculation, which is post-hoc
        # power inflation: a bundle that happened to observe a large effect
        # would need fewer cells to be deemed "adequately powered" than the
        # protocol pre-registered minimum required. The corrected behaviour
        # is to size the test against the **protocol's pre-registered
        # minimum effect** (``min_d``); observed effect is irrelevant to
        # the sample-size requirement.
        required_n = _minimum_sample_size(
            effect_size=min_d,
            alpha=float(stat["alpha"]),
            power=power_target,
        )
        power_pass = len(treatment_values) >= max(required_n, min_cells)
    else:
        power_pass = len(treatment_values) >= min_cells if min_cells > 0 else True

    # ---- Effect size practicality gate (NEW) ----
    min_practical_d = float(stage.get("min_practical_cohens_d", 0.0))
    if min_practical_d > 0:
        effect_size_pass = abs(effect_size_d) >= min_practical_d
    else:
        effect_size_pass = True

    # ---- Cross-method rank stability gate (NEW) ----
    min_rank_tau = float(stage.get("min_rank_stability_tau", 0.0))
    if min_rank_tau > 0 and len(method_means) >= 2:
        # Compute rank correlation between each pair of methods across cells
        method_keys = sorted(method_groups.keys())
        tau_pairs: list[float] = []
        for i in range(len(method_keys)):
            for j in range(i + 1, len(method_keys)):
                tau_pairs.append(
                    _kendall_tau(method_groups[method_keys[i]], method_groups[method_keys[j]])
                )
        avg_hyp_tau = mean(tau_pairs) if tau_pairs else 1.0
        rank_stability_pass = avg_hyp_tau >= min_rank_tau
    else:
        rank_stability_pass = True

    # ---- Baseline superiority gate (NEW) ----
    baseline_min_ratio = float(stage.get("baseline_superiority_ratio", 0.0))
    if baseline_min_ratio > 0:
        baseline_control_mean = mean([
            abs(float(c["control_effects"].get("random_component", 0.0)))
            for c in scope_cells
        ]) if scope_cells else 0.0
        baseline_pass = (
            abs(treatment_mean) >= baseline_min_ratio * (baseline_control_mean + EPSILON)
        )
    else:
        baseline_pass = True

    # ---- Cross-model transfer gate (V19: tri-state) ----
    # not_evaluated when no transfer data exists. Evaluated at bundle level.
    # V19: honest — "not_evaluated" instead of silently passing.
    cross_model_pass = "not_evaluated"

    # ---- Bidirectional enforcement gate (V21: sufficiency+necessity) ----
    # Requires BOTH intervention directions to be **present** AND to yield
    # **non-degenerate, magnitude-balanced** effects:
    #   - sufficiency_patch: patch clean → corrupt (restores behavior → sufficiency test)
    #   - necessity_ablate: ablate on clean (disrupts behavior → necessity test)
    # V21: checks explicit "direction" field; falls back to method-name inference.
    # V22 (, ): also require both directions to have
    # |mean effect| >= min_effect_floor and balance ratio
    # min(|suff|, |nec|)/max(|suff|, |nec|) >= bidirectional_balance_ratio
    # so that a bundle where both labels run identical code (or where one
    # direction has trivial magnitude) cannot trivially clear the gate.
    require_bidir = bool(stage.get("require_bidirectional", False))
    # Audit-final §gpt.P2: surface whether bidirectionality was determined
    # from explicit ``direction`` labels on raw cells (the contract path)
    # or inferred from method-name substrings (the backward-compat path).
    # Reviewers reading the report should be able to tell which without
    # re-deriving it from raw_cells.
    bidirectional_source = "not_required"
    if require_bidir:
        observed_directions = set(c.get("direction", "") for c in scope_cells)
        if observed_directions - {""}:
            bidirectional_source = "explicit_direction_field"
            has_sufficiency = "sufficiency_patch" in observed_directions
            has_necessity = "necessity_ablate" in observed_directions
            # V20 backward compat
            if not has_sufficiency:
                has_sufficiency = "denoise" in observed_directions
            if not has_necessity:
                has_necessity = "noise" in observed_directions

            def _direction_mean(*labels: str) -> float | None:
                vals = [
                    float(c["treatment_effect"])
                    for c in scope_cells
                    if c.get("direction", "") in labels
                ]
                return mean(vals) if vals else None

            suff_mean = _direction_mean("sufficiency_patch", "denoise")
            nec_mean = _direction_mean("necessity_ablate", "noise")
        else:
            # Fallback: infer from method names (backward compat)
            bidirectional_source = "method_name_inference"
            observed_methods = set(c.get("method", "") for c in scope_cells)
            has_sufficiency = any(
                "clean" in m or "denois" in m or "patch" in m for m in observed_methods
            )
            has_necessity = any(
                "zero" in m or "mean" in m or "nois" in m or "ablat" in m
                for m in observed_methods
            )

            def _method_mean(predicate) -> float | None:
                vals = [
                    float(c["treatment_effect"])
                    for c in scope_cells
                    if predicate(c.get("method", ""))
                ]
                return mean(vals) if vals else None

            suff_mean = _method_mean(
                lambda m: ("clean" in m) or ("denois" in m) or ("patch" in m)
            )
            nec_mean = _method_mean(
                lambda m: ("zero" in m) or ("mean" in m) or ("nois" in m) or ("ablat" in m)
            )

        floor = float(stat["min_effect_floor"])
        balance_threshold = float(stage.get("bidirectional_balance_ratio", 0.5))
        labels_present = has_sufficiency and has_necessity
        magnitudes_ok = (
            suff_mean is not None
            and nec_mean is not None
            and abs(suff_mean) >= floor
            and abs(nec_mean) >= floor
        )
        balance_ok = False
        if magnitudes_ok:
            lo = min(abs(suff_mean), abs(nec_mean))  # type: ignore[arg-type]
            hi = max(abs(suff_mean), abs(nec_mean))  # type: ignore[arg-type]
            balance_ok = (hi <= EPSILON) or (lo / hi >= balance_threshold)
        bidirectional_pass = bool(labels_present and magnitudes_ok and balance_ok)
    else:
        bidirectional_pass = True

    # ---- Compensatory mechanism detection (V9 NEW, Pitfall #62) ----
    # Flag when treatment effects reverse sign across methods — suggests
    # compensatory circuits where patching one path shifts load to another.
    compensation_warning = False
    method_sensitivity_type = "consistent"  # V16: classify sensitivity type
    if len(method_means) >= 2:
        signs = [1 if v > 0 else -1 for v in method_means.values() if v != 0]
        if signs and not all(s == signs[0] for s in signs):
            compensation_warning = True
            method_sensitivity_type = "direction_reversal"
        elif method_std > 0.5:
            method_sensitivity_type = "magnitude_variation"

    # ---- Governance gate (V16 NEW, Pitfalls #52, #53) ----
    governance = protocol.get("governance", {})
    governance_valid = True
    governance_issues: list[str] = []
    if governance.get("red_team_required", False):
        # Check that protocol has a creation timestamp (frozen before execution)
        if not governance.get("protocol_creation_timestamp"):
            governance_valid = False
            governance_issues.append("missing protocol_creation_timestamp")
    # Exception expiry: check that exceptions haven't expired
    expiry_hours = governance.get("exception_expiry_hours", 0)
    if expiry_hours > 0 and governance.get("protocol_creation_timestamp"):
        governance_issues.append(f"exception_expiry_hours={expiry_hours}")

    # ---- Assemble checks (V19: tri-state: True / False / "not_evaluated") ----
    checks = {
        "execution_coverage": coverage_pass,
        "confirmatory_present": confirmatory_present,
        "confirmatory_firewall": confirmatory_firewall_pass,
        "causal_effect": causal_pass,
        "negative_controls": control_pass,
        "robustness": robustness_pass,
        "method_sensitivity": sensitivity_pass,
        "confirmatory_ci": ci_pass,
        "multiplicity": multiplicity_pass,
        "power_adequacy": power_pass,
        "effect_size_practical": effect_size_pass,
        "rank_stability": rank_stability_pass,
        "baseline_superiority": baseline_pass,
        "cross_model_transfer": cross_model_pass,  # V19: may be "not_evaluated"
        "bidirectional": bidirectional_pass,
        "governance_valid": governance_valid,
    }

    evidence_tier, passed, failed_gates, not_evaluated_gates, demotion_reason = _classify_evidence_tier(
        checks,
        exploratory_present=exploratory_present,
    )
    gate_outcomes = _normalize_gate_outcomes(checks)

    # V20: NOT_EVALUATED guidance for reports
    ne_guidance = {
        g: NOT_EVALUATED_GUIDANCE.get(g, {"why_missing": "Unknown", "how_to_run": "N/A"})
        for g in not_evaluated_gates
    }

    metrics: dict[str, Any] = {
        "treatment_effect_mean": treatment_mean,
        "confirmatory_ci_low": ci_low,
        "confirmatory_ci_high": ci_high,
        "control_abs_mean": control_abs_mean,
        "specificity_ratio": specificity_ratio,
        "seed_consistency": seed_consistency,
        "prompt_variant_consistency": prompt_consistency,
        "resample_consistency": resample_consistency,
        "method_sensitivity_std": method_std,
        "q_value": q_value,
        "holm_adjusted_p": holm_adjusted_p,
        "p_value_permutation": perm_p_value,
        "cohens_d": effect_size_d,
        "compensation_warning": compensation_warning,
        "method_sensitivity_type": method_sensitivity_type,
        "governance_issues": governance_issues,
        "bidirectional_source": bidirectional_source,
        "n_cells": len(treatment_values),
        "exploratory_present": exploratory_present,
        "expected_cells": len(expected),
        "observed_cells": len(observed),
        "missing_cells": [
            {
                "seed": seed,
                "prompt_variant": prompt_variant,
                "resample_id": resample_id,
                "method": method,
            }
            for (seed, prompt_variant, resample_id, method) in missing
        ],
        "undeclared_cells": [
            {
                "seed": seed,
                "prompt_variant": prompt_variant,
                "resample_id": resample_id,
                "method": method,
            }
            for (seed, prompt_variant, resample_id, method) in undeclared
        ],
    }
    # only emit the
    # ``confirmatory_firewall_vacuous`` flag when the protocol actually opted
    # out (``require_confirmatory_split: false``). All currently-released
    # bundles require the split, so this avoids touching their evaluation_result
    # bytes while still flagging any future opt-out for downstream aggregators.
    if confirmatory_firewall_vacuous:
        metrics["confirmatory_firewall_vacuous"] = True

    return {
        "hypothesis_id": hypothesis["hypothesis_id"],
        "passed": passed,
        "evidence_tier": evidence_tier,
        "tier_demotion_reason": demotion_reason,
        "gate_outcomes": gate_outcomes,
        "failed_checks": failed_gates,
        "not_evaluated_checks": not_evaluated_gates,
        "not_evaluated_guidance": ne_guidance,
        "checks": checks,
        "metrics": metrics,
    }

# ---------------------------------------------------------------------------
# Bundle-level evaluation
# ---------------------------------------------------------------------------

def evaluate_bundle(bundle_dir: Path) -> dict:
    loaded = load_bundle(bundle_dir)
    protocol = loaded["protocol"]
    hypotheses = loaded["hypotheses"]
    evaluation_result = loaded["evaluation_result"]

    by_id = {h["hypothesis_id"]: h for h in hypotheses}

    # Compute p-values with permutation test
    pvals: list[tuple[str, float]] = []
    treatments_by_hid: dict[str, list[float]] = {}
    for row in evaluation_result["hypothesis_results"]:
        hid = row["hypothesis_id"]
        vals = [
            float(cell["treatment_effect"])
            for cell in row["raw_cells"]
            if cell["slice"] == "confirmatory"
        ]
        if not vals:
            vals = [float(cell["treatment_effect"]) for cell in row["raw_cells"]]
        treatments_by_hid[hid] = vals
        pvals.append((hid, _permutation_p_value(vals, seed=f"bundle_perm|{hid}")))

    # Multiplicity correction: BH (primary) + Holm-Bonferroni (secondary)
    q_values = _bh_q_values(pvals)
    holm_values = _holm_bonferroni(pvals)

    # Cross-method rank stability (computed across all hypotheses)
    method_list = list(protocol["execution_grid"]["methods"])
    if len(method_list) >= 2 and len(hypotheses) >= 2:
        rankings_per_method: dict[str, list[float]] = {m: [] for m in method_list}
        for hid in sorted(treatments_by_hid.keys()):
            row = next(r for r in evaluation_result["hypothesis_results"] if r["hypothesis_id"] == hid)
            for meth in method_list:
                method_vals = [
                    float(c["treatment_effect"]) for c in row["raw_cells"]
                    if str(c["method"]) == meth
                ]
                rankings_per_method[meth].append(mean(method_vals) if method_vals else 0.0)

        tau_pairs: list[float] = []
        # sort to keep iteration
        # order deterministic regardless of Python dict insertion order; the
        # downstream ``mean(cross_taus)`` is order-invariant today, but a
        # future change that emits the per-pair list would otherwise drift.
        method_keys = sorted(rankings_per_method.keys())
        for i in range(len(method_keys)):
            for j in range(i + 1, len(method_keys)):
                tau = _kendall_tau(rankings_per_method[method_keys[i]], rankings_per_method[method_keys[j]])
                tau_pairs.append(tau)
        avg_tau = mean(tau_pairs) if tau_pairs else 1.0
    else:
        avg_tau = 1.0

    claim_reports = []
    for row in sorted(evaluation_result["hypothesis_results"], key=lambda r: r["hypothesis_id"]):
        hid = row["hypothesis_id"]
        claim_reports.append(
            _summarize_hypothesis(
                protocol=protocol,
                hypothesis=by_id[hid],
                hypothesis_result=row,
                q_value=float(q_values.get(hid, 1.0)),
                holm_adjusted_p=float(holm_values.get(hid, 1.0)),
            )
        )

    # Cross-model transfer analysis (V8/V17: load from file if present)
    cross_model_results = evaluation_result.get("cross_model_results", [])

    # the inline ``cross_model_results``
    # structure historically bypassed the strict normalization applied to the
    # separate ``cross_model_results.json`` file. An adversarial bundle could
    # therefore inject string literals like ``"Infinity"`` (a valid JSON
    # string), per-hypothesis duplicates, or unexpected shapes that would
    # quietly survive ``float()`` conversion further down. Validate the inline
    # path with the same closed-shape rules: must be a list of grouped entries
    # ``{"model_id": str, "family": str, "hypothesis_effects": {hid: float}}``,
    # every effect must be finite, and ``(model_id, hid)`` pairs must be unique.
    if cross_model_results:
        if not isinstance(cross_model_results, list):
            raise BundleError(
                "evaluation_result.cross_model_results must be a list; "
                f"got {type(cross_model_results).__name__}"
            )
        seen_pairs: set[tuple[str, str]] = set()
        for entry in cross_model_results:
            if not isinstance(entry, dict):
                raise BundleError(
                    "evaluation_result.cross_model_results entries must be "
                    f"objects; got {type(entry).__name__}"
                )
            entry_model_id = str(entry.get("model_id", "unknown"))
            hyp_effects = entry.get("hypothesis_effects", {})
            if not isinstance(hyp_effects, dict):
                raise BundleError(
                    "evaluation_result.cross_model_results entry for "
                    f"model_id={entry_model_id!r} has non-dict "
                    f"hypothesis_effects (type={type(hyp_effects).__name__})."
                )
            for hyp_key, effect_raw in hyp_effects.items():
                pair = (entry_model_id, str(hyp_key))
                if pair in seen_pairs:
                    raise BundleError(
                        "evaluation_result.cross_model_results contains "
                        f"duplicate (model_id={entry_model_id!r}, "
                        f"hypothesis_id={hyp_key!r}); refusing to silently "
                        "last-write-win on inline transfer evidence."
                    )
                seen_pairs.add(pair)
                try:
                    effect_val = float(effect_raw)
                except (TypeError, ValueError) as exc:
                    raise BundleError(
                        f"evaluation_result.cross_model_results entry for "
                        f"(model_id={entry_model_id!r}, "
                        f"hypothesis_id={hyp_key!r}) has non-numeric "
                        f"hypothesis_effects value={effect_raw!r}"
                    ) from exc
                if not math.isfinite(effect_val):
                    raise BundleError(
                        f"evaluation_result.cross_model_results entry for "
                        f"(model_id={entry_model_id!r}, "
                        f"hypothesis_id={hyp_key!r}) has non-finite "
                        f"hypothesis_effects value={effect_val!r}"
                    )
                hyp_effects[hyp_key] = effect_val

    # V17: Also check for separate cross_model_results.json file
    cross_model_file = bundle_dir / "cross_model_results.json"
    if not cross_model_results and cross_model_file.exists():
        # route through the strict JSON helper so transfer
        # evidence is parsed with the same BOM-tolerant, non-finite-rejecting
        # contract as every other bundle JSON file.
        raw_transfers = read_json_any(cross_model_file)
        if not isinstance(raw_transfers, list):
            raise BundleError(
                "cross_model_results.json must be a list of transfer rows; "
                f"got {type(raw_transfers).__name__}"
            )
        # Convert per-hypothesis transfer results to evaluator format. A bundle
        # may contain more than one transfer target for the same hypothesis
        # (for example paired-bundle replication plus same-family transfer).
        # Preserve target-model grouping instead of collapsing by hypothesis ID,
        # because row-order overwrites can otherwise change the tier.
        if raw_transfers:
            grouped_transfers: dict[str, dict[str, float]] = {}
            # detect duplicate
            # ``(transfer_model, hypothesis_id)`` rows and refuse to silently
            # last-write-win. Adversarial submissions could otherwise hide a
            # sub-floor effect under a passing one for the same target/hyp.
            for row in raw_transfers:
                transfer_model_id = str(row.get("transfer_model", "unknown"))
                hyp_key = str(row["hypothesis_id"])
                bucket = grouped_transfers.setdefault(transfer_model_id, {})
                if hyp_key in bucket:
                    raise BundleError(
                        "cross_model_results.json contains duplicate "
                        f"(transfer_model={transfer_model_id!r}, "
                        f"hypothesis_id={hyp_key!r}) rows; refusing to "
                        "silently last-write-win on transfer evidence."
                    )
                # explicitly validate finiteness even though
                # ``read_json_any`` rejects NaN/Infinity literals; a numeric
                # field could still arrive as ``None`` or a non-numeric type.
                effect_raw = row.get("transfer_effect")
                try:
                    effect_val = float(effect_raw)
                except (TypeError, ValueError) as exc:
                    raise BundleError(
                        f"cross_model_results.json row for "
                        f"(transfer_model={transfer_model_id!r}, "
                        f"hypothesis_id={hyp_key!r}) has non-numeric "
                        f"transfer_effect={effect_raw!r}"
                    ) from exc
                if not math.isfinite(effect_val):
                    raise BundleError(
                        f"cross_model_results.json row for "
                        f"(transfer_model={transfer_model_id!r}, "
                        f"hypothesis_id={hyp_key!r}) has non-finite "
                        f"transfer_effect={effect_val!r}"
                    )
                bucket[hyp_key] = effect_val
            cross_model_results = [
                {
                    "model_id": transfer_model_id,
                    "family": "transfer",
                    "hypothesis_effects": hyp_effects,
                }
                for transfer_model_id, hyp_effects in sorted(grouped_transfers.items())
            ]

    cross_model_tau = None
    min_cross_model_tau = float(protocol.get("stage_gates", {}).get("cross_model_rank_stability_tau", 0.0))

    if cross_model_results:
        # V21: Per-hypothesis direction + floor replication gate
        # For each hypothesis, check: transfer effect has same direction AND abs >= floor
        from .constants import CROSS_MODEL_EFFECT_FLOOR

        for report in claim_reports:
            hid = report["hypothesis_id"]
            source_effect = treatments_by_hid.get(hid, [0.0])
            source_mean = mean(source_effect) if source_effect else 0.0
            # an exact zero source mean has no signed direction. The previous
            # ``-1 if source_mean <= 0`` collapsed zero into "negative", which
            # would silently accept a negative-going transfer effect as
            # "same direction" against a flat source. Treat zero as a distinct
            # ``0`` sign and require same_direction to mean both effects are
            # nonzero AND share the same strict sign.
            if source_mean > 0:
                source_sign = 1
            elif source_mean < 0:
                source_sign = -1
            else:
                source_sign = 0

            # Find transfer effects for this hypothesis. Passing any frozen
            # target-model replication is enough for the cross-model tier; a
            # failing additional target should be reported as a robustness
            # weakness, not silently overwrite an existing positive target.
            transfer_evaluations: list[dict[str, object]] = []
            for cm_entry in cross_model_results:
                cm_effects = cm_entry.get("hypothesis_effects", {})
                if hid in cm_effects:
                    transfer_effect = float(cm_effects[hid])
                    if transfer_effect > 0:
                        transfer_sign = 1
                    elif transfer_effect < 0:
                        transfer_sign = -1
                    else:
                        transfer_sign = 0
                    same_direction = (
                        source_sign != 0
                        and transfer_sign != 0
                        and source_sign == transfer_sign
                    )
                    above_floor = abs(transfer_effect) >= CROSS_MODEL_EFFECT_FLOOR
                    transfer_evaluations.append(
                        {
                            "model_id": cm_entry.get("model_id", "unknown"),
                            "effect": transfer_effect,
                            "same_direction": same_direction,
                            "above_floor": above_floor,
                            "passes": same_direction and above_floor,
                        }
                    )

            if transfer_evaluations:
                passing = [row for row in transfer_evaluations if row["passes"]]
                # cross-model aggregation strategy is now
                # protocol-configurable. Default ``"any"`` matches the
                # historical behaviour (passing one frozen target promotes the
                # claim); ``"all"`` requires every evaluated target to pass;
                # ``"majority"`` requires > 50% of targets to pass.
                #
                # unknown values are now rejected loud
                # rather than silently downgrading to permissive ``"any"``.
                # An acceptance contract must fail closed; otherwise a
                # protocol typo (``"majorirty"``, ``"all_targets"``) makes
                # the evaluator more, not less, permissive.
                aggregation_requested = str(
                    protocol.get("stage_gates", {})
                    .get("cross_model_aggregation", "any")
                ).lower()
                _ALLOWED_AGGREGATION = {"any", "all", "majority"}
                if aggregation_requested not in _ALLOWED_AGGREGATION:
                    raise BundleError(
                        f"protocol.stage_gates.cross_model_aggregation="
                        f"{aggregation_requested!r} is not one of "
                        f"{sorted(_ALLOWED_AGGREGATION)}; refusing to fall "
                        "back to permissive 'any' on a typo."
                    )
                aggregation = aggregation_requested
                n_targets = len(transfer_evaluations)
                n_pass = len(passing)
                if aggregation == "all":
                    cm_pass = n_pass == n_targets
                elif aggregation == "majority":
                    cm_pass = n_pass * 2 > n_targets
                else:
                    cm_pass = n_pass > 0
                selected = passing[0] if passing else max(
                    transfer_evaluations,
                    key=lambda row: abs(float(row["effect"])),
                )
                report["checks"]["cross_model_transfer"] = bool(cm_pass)
                report["metrics"]["cross_model_transfer_effect"] = selected["effect"]
                report["metrics"]["cross_model_same_direction"] = selected["same_direction"]
                report["metrics"]["cross_model_above_floor"] = selected["above_floor"]
                report["metrics"]["cross_model_transfer_model"] = selected["model_id"]
                report["metrics"]["cross_model_transfer_evaluated_models"] = [
                    row["model_id"] for row in transfer_evaluations
                ]
                report["metrics"]["cross_model_transfer_passed_models"] = [
                    row["model_id"] for row in transfer_evaluations if row["passes"]
                ]
                report["metrics"]["cross_model_aggregation_used"] = aggregation
            # If no transfer data for this hypothesis, remains "not_evaluated"

        # Secondary diagnostic: Kendall τ (not the gate condition)
        if len(cross_model_results) >= 1 and len(hypotheses) >= 2:
            model_rankings: dict[str, list[float]] = {}
            sorted_hids = sorted(treatments_by_hid.keys())
            for cm_entry in cross_model_results:
                cm_model_id = cm_entry.get("model_id", "")
                cm_effects = cm_entry.get("hypothesis_effects", {})
                rankings = [float(cm_effects.get(hid, 0.0)) for hid in sorted_hids]
                model_rankings[cm_model_id] = rankings
            primary_rankings = [mean(treatments_by_hid[hid]) for hid in sorted_hids]
            model_rankings["__primary__"] = primary_rankings
            # see above.
            model_keys = sorted(model_rankings.keys())
            cross_taus: list[float] = []
            for i in range(len(model_keys)):
                for j in range(i + 1, len(model_keys)):
                    tau = _kendall_tau(model_rankings[model_keys[i]], model_rankings[model_keys[j]])
                    cross_taus.append(tau)
            cross_model_tau = mean(cross_taus) if cross_taus else 1.0

        # V20: Recompute tiers after cross-model gate update
        for report in claim_reports:
            c = report["checks"]
            tier, passed, failed_checks, not_evaluated_checks, demotion = _classify_evidence_tier(
                c,
                exploratory_present=bool(report.get("metrics", {}).get("exploratory_present", False)),
            )
            report["evidence_tier"] = tier
            report["tier_demotion_reason"] = demotion
            report["passed"] = passed
            report["failed_checks"] = failed_checks
            report["not_evaluated_checks"] = not_evaluated_checks
            report["gate_outcomes"] = _normalize_gate_outcomes(c)
            report["not_evaluated_guidance"] = {
                gate: NOT_EVALUATED_GUIDANCE.get(
                    gate,
                    {"why_missing": "Unknown", "how_to_run": "N/A", "impact": "Unknown"},
                )
                for gate in not_evaluated_checks
            }

    accepted = [r for r in claim_reports if r["passed"]]
    unstable = [
        r for r in claim_reports
        if (not r["passed"]) and r["evidence_tier"] in ("causal_tested_unstable", "suggestive")
    ]

    overall = {
        "hypothesis_count": len(claim_reports),
        "accepted_count": len(accepted),
        "unstable_count": len(unstable),
        "rejected_count": len(claim_reports) - len(accepted) - len(unstable),
        "all_pass": len(accepted) == len(claim_reports),
        "cross_method_rank_tau": avg_tau,
        "tier_order": list(EVIDENCE_TIER_ORDER),
    }
    if cross_model_tau is not None:
        overall["cross_model_rank_tau"] = cross_model_tau

    return {
        "protocol_id": protocol["protocol_id"],
        "protocol_hash": loaded["hashes"]["protocol.yaml"],
        "bundle_hashes": loaded["hashes"],
        "overall": overall,
        "claim_reports": claim_reports,
    }
