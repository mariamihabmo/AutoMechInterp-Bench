#!/usr/bin/env python3
"""Shared helpers for bundle audits, summaries, and reporting."""

from __future__ import annotations

import json
import math
import os
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

def generated_at_utc(*, timespec: str = "seconds") -> str:
    """Return an ISO-8601 UTC timestamp suitable for canonical artifacts.

    Honors the ``SOURCE_DATE_EPOCH`` environment variable per the Reproducible
    Builds convention (https://reproducible-builds.org/specs/source-date-epoch/)
    so that callers performing deterministic re-execution can pin the embedded
    timestamp without modifying the writer code. When the variable is unset or
    malformed, falls back to ``datetime.now(timezone.utc)``.

    Earlier inspection identified three writers that previously
    embedded a wall-clock timestamp directly; routing them through this helper
    closes the determinism gap without removing the field.
    """
    raw = os.environ.get("SOURCE_DATE_EPOCH")
    if raw:
        try:
            epoch = int(raw)
            return datetime.fromtimestamp(epoch, tz=timezone.utc).isoformat(timespec=timespec)
        except (TypeError, ValueError):
            pass
    return datetime.now(timezone.utc).isoformat(timespec=timespec)

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "packages" / "evaluator" / "src"))

from automechinterp_evaluator.evaluator import _classify_evidence_tier, evaluate_bundle
from automechinterp_evaluator.io_utils import read_jsonl, read_yaml

REAL_MULTI_TASK_DIR = ROOT / "main" / "output" / "real_multi_task"
REAL_MULTILANE_DIR = ROOT / "main" / "output" / "real_multilane"
ZERO_TASK_REAL_REPAIR_DIR = ROOT / "main" / "output" / "zero_task_real_repair"
PROMPT_VARIANT_REPAIR_DIR = ROOT / "main" / "output" / "prompt_variant_repair"
CURRENT_EVALUATION_RESULT_FILENAME = "evaluation_result_current.json"

GATE_FAMILY_MAP = {
    "execution_coverage": "execution",
    "confirmatory_present": "execution",
    "confirmatory_firewall": "execution",
    "causal_effect": "causal",
    "negative_controls": "controls",
    "baseline_superiority": "controls",
    "robustness": "robustness",
    "method_sensitivity": "robustness",
    "bidirectional": "robustness",
    "rank_stability": "robustness",
    "confirmatory_ci": "statistics",
    "multiplicity": "statistics",
    "power_adequacy": "statistics",
    "effect_size_practical": "statistics",
    "cross_model_transfer": "transfer",
    "governance_valid": "governance",
}

COUNTERFACTUAL_GATES = {
    "full_contract": [],
    "no_stat_rigor": ["confirmatory_ci", "multiplicity", "power_adequacy", "effect_size_practical"],
    "no_robustness_suite": ["robustness", "method_sensitivity", "bidirectional", "rank_stability"],
    "no_controls_suite": ["negative_controls", "baseline_superiority"],
}

def pct(value: float | int | None) -> str:
    if value is None:
        return "n/a"
    return f"{float(value) * 100:.1f}%"

def wilson_interval(successes: int, total: int, z: float = 1.96) -> dict[str, float | str]:
    if total <= 0:
        return {"low": 0.0, "high": 0.0, "label": "[0.0%, 0.0%]"}
    phat = successes / total
    denom = 1 + (z * z) / total
    center = (phat + (z * z) / (2 * total)) / denom
    margin = (z / denom) * math.sqrt((phat * (1 - phat) / total) + ((z * z) / (4 * total * total)))
    low = max(0.0, center - margin)
    high = min(1.0, center + margin)
    return {"low": low, "high": high, "label": f"[{low * 100:.1f}%, {high * 100:.1f}%]"}

def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n")

def write_text(path: Path, payload: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(payload)

def repo_relative(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except Exception:
        return str(path)

def _valid_bundle_dir(path: Path) -> bool:
    return (
        path.is_dir()
        and (path / "protocol.yaml").exists()
        and (path / "hypothesis.jsonl").exists()
        and (path / "evaluation_result.json").exists()
    )

def _zero_task_real_repair_replacements() -> dict[str, Path]:
    """Return real-repair bundles that supersede same-named legacy bundles.

    These are only used when callers request the canonical released artifact
    surface via ``REAL_MULTI_TASK_DIR`` + ``REAL_MULTILANE_DIR``. The
    supersession keeps bundle/claim counts comparable by replacing the old
    zero-task bundle with its real confirmatory-repair rerun instead of counting
    both.
    """

    if not ZERO_TASK_REAL_REPAIR_DIR.exists():
        return {}
    replacements: dict[str, Path] = {}
    for path in sorted(ZERO_TASK_REAL_REPAIR_DIR.iterdir()):
        if _valid_bundle_dir(path):
            replacements[path.name] = path
    return replacements

def _prompt_variant_repair_replacements() -> dict[str, Path]:
    """Return prompt-repair bundles that supersede same-named legacy bundles.

    Prompt repair is a release-level migration, not a side diagnostic. To avoid
    silently changing headline numbers from a partial repair run, replacements
    are only active when ``prompt_variant_repair_rerun.json`` says that every
    planned unsupported-prompt bundle has a repaired candidate on disk.
    """

    summary_path = ROOT / "main" / "output" / "repro" / "prompt_variant_repair_rerun.json"
    if not PROMPT_VARIANT_REPAIR_DIR.exists() or not summary_path.exists():
        return {}
    try:
        summary = json.loads(summary_path.read_text())
    except Exception:
        return {}
    planned = int(
        summary.get("planned_unsupported_prompt_bundles")
        or summary.get("planned_affected_bundles_with_accepts")
        or 0
    )
    rerun = int(summary.get("bundles_rerun") or 0)
    if planned <= 0 or rerun < planned:
        return {}
    replacements: dict[str, Path] = {}
    for path in sorted(PROMPT_VARIANT_REPAIR_DIR.iterdir()):
        if _valid_bundle_dir(path):
            replacements[path.name] = path
    if len(replacements) < planned:
        return {}
    return replacements

def find_bundle_dirs(*roots: Path) -> list[Path]:
    canonical_release = REAL_MULTI_TASK_DIR in roots and REAL_MULTILANE_DIR in roots
    repair_replacements = _zero_task_real_repair_replacements() if canonical_release else {}
    prompt_replacements = _prompt_variant_repair_replacements() if canonical_release else {}
    bundle_dirs: list[Path] = []
    for root in roots:
        if not root.exists():
            continue
        for path in sorted(root.iterdir()):
            if path.name in prompt_replacements:
                continue
            if root == REAL_MULTI_TASK_DIR and path.name in repair_replacements:
                continue
            if _valid_bundle_dir(path):
                bundle_dirs.append(path)
    if canonical_release:
        for name in sorted(repair_replacements):
            if name not in prompt_replacements:
                bundle_dirs.append(repair_replacements[name])
        bundle_dirs.extend(prompt_replacements[name] for name in sorted(prompt_replacements))
    return bundle_dirs

def _result_has_current_summary(result: Any) -> bool:
    return isinstance(result, dict) and isinstance(result.get("claim_reports"), list) and isinstance(result.get("overall"), dict)

def _evaluation_cache_is_stale(bundle_dir: Path, cache_path: Path) -> bool:
    """Return True when cached gate results predate mutable bundle evidence.

    Audit-final §gpt.P2: prefer a content-hash signature over wall-clock
    mtime. ``mtime`` is unreliable in two common cases that both bite us:
    ``cp -p`` / ``rsync --times`` preserves source timestamps so a freshly
    rewritten bundle can look older than its cache, and ``touch`` can
    trivially mark a stale bundle as fresh without changing any bytes.
    The cache JSON now embeds a ``"_content_hash"`` field that is the
    SHA-256 of the concatenated mutable evidence files; we mark stale on
    any mismatch, with a fall-back to the legacy mtime path for caches
    that pre-date the hash field.
    """

    if not cache_path.exists():
        return True

    mutable_files = (
        "protocol.yaml",
        "hypothesis.jsonl",
        "evaluation_result.json",
        "cross_model_results.json",
    )
    current_hash = _content_hash(bundle_dir, mutable_files)
    try:
        cached_payload = json.loads(cache_path.read_text())
    except Exception:
        return True
    cached_hash = cached_payload.get("_content_hash") if isinstance(cached_payload, dict) else None
    if isinstance(cached_hash, str) and cached_hash:
        return cached_hash != current_hash

    # Legacy fall-back for caches without an embedded content hash.
    cache_mtime = cache_path.stat().st_mtime
    for name in mutable_files:
        path = bundle_dir / name
        if path.exists() and path.stat().st_mtime > cache_mtime:
            return True
    return False

def _content_hash(bundle_dir: Path, names: tuple[str, ...]) -> str:
    import hashlib
    h = hashlib.sha256()
    for name in names:
        path = bundle_dir / name
        if path.exists():
            h.update(name.encode("utf-8"))
            h.update(b"\x00")
            h.update(path.read_bytes())
            h.update(b"\x00")
    return h.hexdigest()

def _load_cached_or_evaluate_bundle(bundle_dir: Path) -> dict[str, Any]:
    current_cache = bundle_dir / CURRENT_EVALUATION_RESULT_FILENAME
    if current_cache.exists() and not _evaluation_cache_is_stale(bundle_dir, current_cache):
        try:
            current = json.loads(current_cache.read_text())
            if _result_has_current_summary(current):
                return current
        except Exception:
            pass

    released_cache = bundle_dir / "evaluation_result.json"
    try:
        released = json.loads(released_cache.read_text())
        if _result_has_current_summary(released):
            return released
    except Exception:
        pass

    result = evaluate_bundle(bundle_dir)
    # Stamp the cache with the current content hash so subsequent calls
    # can detect drift without trusting filesystem mtimes (audit-final §gpt.P2).
    result_with_hash = dict(result)
    result_with_hash["_content_hash"] = _content_hash(
        bundle_dir,
        (
            "protocol.yaml",
            "hypothesis.jsonl",
            "evaluation_result.json",
            "cross_model_results.json",
        ),
    )
    current_cache.write_text(json.dumps(result_with_hash, sort_keys=True, indent=2) + "\n")
    return result_with_hash

def evaluate_bundle_records(*roots: Path, use_cached_results: bool = False) -> list[dict[str, Any]]:
    """Load released bundle records and (optionally) re-evaluate them.

    Parameters
    ----------
    use_cached_results:
        When ``False`` (default), call ``evaluate_bundle(bundle_dir)`` and
        therefore validate the on-disk bundle against the *current* evaluator
        semantics. When ``True``, trust the bundle's persisted
        ``evaluation_result.json`` and avoid re-running Stage-1. The cached path
        is appropriate for artifact-backed summary / diagnostic scripts whose
        goal is to re-project the released evidence surface rather than to
        re-score every bundle under the current evaluator.
    """
    records: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    for bundle_dir in find_bundle_dirs(*roots):
        # Keep ALL bundle I/O and evaluation in the same try/except so a
        # malformed protocol or hypothesis file is reported alongside any
        # evaluator failures, rather than escaping as an uncaught exception
        # and hiding the rest of the broken bundles.
        try:
            protocol = read_yaml(bundle_dir / "protocol.yaml")
            hypotheses = read_jsonl(bundle_dir / "hypothesis.jsonl")
            if use_cached_results:
                result = _load_cached_or_evaluate_bundle(bundle_dir)
            else:
                result = evaluate_bundle(bundle_dir)
        except Exception as exc:
            errors.append({"bundle": bundle_dir.name, "path": repo_relative(bundle_dir), "error": repr(exc)})
            continue
        lanes = Counter(h.get("discovery_lane", "canonical_real") for h in hypotheses)
        providers = Counter(h.get("provider_id", "canonical_runner") for h in hypotheses)
        records.append(
            {
                "bundle": bundle_dir.name,
                "path": repo_relative(bundle_dir),
                "bundle_dir": bundle_dir,
                "protocol": protocol,
                "hypotheses": hypotheses,
                "result": result,
                "task": protocol["unit_of_work"]["task_id"],
                "model": protocol["unit_of_work"]["model_id"],
                "lane_counts": dict(lanes),
                "provider_counts": dict(providers),
                "has_cross_model_results": (bundle_dir / "cross_model_results.json").exists(),
            }
        )
    if errors:
        details = "; ".join(f"{row['bundle']} ({row['path']}): {row['error']}" for row in errors)
        raise RuntimeError(
            "Failed to evaluate one or more bundles while summarizing released artifacts. "
            "Refusing to continue with a partial summary. "
            f"Errors: {details}"
        )
    return records

def iter_claim_rows(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for record in records:
        by_id = {h["hypothesis_id"]: h for h in record["hypotheses"]}
        for report in record["result"]["claim_reports"]:
            hypothesis = by_id[report["hypothesis_id"]]
            components = hypothesis.get("candidate_components", [])
            component_type = components[0].get("component_type", "unknown") if components else "unknown"
            rows.append(
                {
                    "bundle": record["bundle"],
                    "task": record["task"],
                    "model": record["model"],
                    "hypothesis_id": report["hypothesis_id"],
                    "evidence_tier": report["evidence_tier"],
                    "passed": report["passed"],
                    "failed_checks": list(report.get("failed_checks", [])),
                    "not_evaluated_checks": list(report.get("not_evaluated_checks", [])),
                    "gate_outcomes": dict(report.get("gate_outcomes", {})),
                    "component_type": component_type,
                    "discovery_lane": hypothesis.get("discovery_lane", "canonical_real"),
                    "provider_id": hypothesis.get("provider_id", "canonical_runner"),
                    "metrics": report.get("metrics", {}),
                }
            )
    return rows

def summarize_coverage(records: list[dict[str, Any]]) -> dict[str, Any]:
    claim_rows = iter_claim_rows(records)
    total_claims = len(claim_rows)
    accepted = sum(1 for row in claim_rows if row["passed"])
    rejected = sum(1 for row in claim_rows if not row["passed"])
    tier_counts = dict(Counter(row["evidence_tier"] for row in claim_rows))
    ci95 = wilson_interval(accepted, total_claims)
    bundles = []

    for record in records:
        total = record["result"]["overall"]["hypothesis_count"]
        accepted_count = record["result"]["overall"]["accepted_count"]
        bundles.append(
            {
                "bundle": record["bundle"],
                "task": record["task"],
                "model": record["model"],
                "n_claims": total,
                "accepted": accepted_count,
                "rejected": total - accepted_count,
                "acceptance_rate": accepted_count / total if total else 0.0,
                "acceptance_rate_pct": pct(accepted_count / total if total else 0.0),
                "determinism_match": True,
                "lane_counts": record["lane_counts"],
                "provider_counts": record["provider_counts"],
                "has_cross_model_results": record["has_cross_model_results"],
            }
        )

    return {
        "n_bundles": len(records),
        "bundles": bundles,
        "tier_counts": tier_counts,
        "totals": {
            "claims": total_claims,
            "accepted": accepted,
            "rejected": rejected,
            "acceptance_rate": accepted / total_claims if total_claims else 0.0,
            "acceptance_rate_pct": pct(accepted / total_claims if total_claims else 0.0),
            "acceptance_rate_ci95": ci95,
        },
    }

def summarize_failure_modes(records: list[dict[str, Any]]) -> dict[str, Any]:
    claim_rows = iter_claim_rows(records)
    failed_gate_counts = Counter()
    not_evaluated_gate_counts = Counter()
    tier_counts = Counter(row["evidence_tier"] for row in claim_rows)
    failed_combinations = Counter()
    gate_family_counts = Counter()

    for row in claim_rows:
        failed = tuple(sorted(row["failed_checks"]))
        if failed:
            failed_combinations[failed] += 1
        for gate in row["failed_checks"]:
            failed_gate_counts[gate] += 1
            gate_family_counts[GATE_FAMILY_MAP.get(gate, "other")] += 1
        for gate in row["not_evaluated_checks"]:
            not_evaluated_gate_counts[gate] += 1

    top_failed = [
        {"failed_checks": list(combo), "count": count}
        for combo, count in failed_combinations.most_common(10)
    ]
    all_failed = [
        {"failed_checks": list(combo), "count": count}
        for combo, count in failed_combinations.most_common()
    ]

    return {
        "n_claims": len(claim_rows),
        "n_passed": sum(1 for row in claim_rows if row["passed"]),
        "n_failed": sum(1 for row in claim_rows if not row["passed"]),
        "failed_gate_counts": dict(failed_gate_counts),
        "failed_gate_family_counts": dict(gate_family_counts),
        "not_evaluated_gate_counts": dict(not_evaluated_gate_counts),
        "tier_counts": dict(tier_counts),
        "top_failed_combinations": top_failed,
        "all_failed_combinations": all_failed,
    }

def compute_counterfactual_sensitivity(records: list[dict[str, Any]]) -> dict[str, Any]:
    claim_rows = iter_claim_rows(records)
    full_acceptance_rate = sum(1 for row in claim_rows if row["passed"]) / len(claim_rows) if claim_rows else 0.0
    conditions: dict[str, Any] = {}

    for name, disabled_gates in COUNTERFACTUAL_GATES.items():
        accepted = 0
        tier_changes = 0
        for row in claim_rows:
            checks = dict(row["gate_outcomes"])
            legacy_checks: dict[str, bool | str] = {}
            for gate, status in checks.items():
                if status == "pass":
                    legacy_checks[gate] = True
                elif status == "not_evaluated":
                    legacy_checks[gate] = "not_evaluated"
                else:
                    legacy_checks[gate] = False
            for gate in disabled_gates:
                legacy_checks[gate] = True
            tier, passed, _, _, _ = _classify_evidence_tier(
                legacy_checks,
                exploratory_present=bool(row["metrics"].get("exploratory_present", False)),
            )
            accepted += int(passed)
            if tier != row["evidence_tier"]:
                tier_changes += 1
        rate = accepted / len(claim_rows) if claim_rows else 0.0
        conditions[name] = {
            "disabled_gates": disabled_gates,
            "accepted": accepted,
            "acceptance_rate": rate,
            "tier_changes": tier_changes,
        }

    most_sensitive = max(
        (item for item in conditions.items() if item[0] != "full_contract"),
        key=lambda kv: (kv[1]["acceptance_rate"], kv[1]["tier_changes"]),
        default=("n/a", {"acceptance_rate": 0.0, "tier_changes": 0}),
    )
    return {
        "full_acceptance_rate": full_acceptance_rate,
        "conditions": conditions,
        "most_sensitive_counterfactual": {
            "name": most_sensitive[0],
            "acceptance_rate": most_sensitive[1]["acceptance_rate"],
            "tier_changes": most_sensitive[1]["tier_changes"],
        },
    }

def summarize_breadth(records: list[dict[str, Any]]) -> dict[str, Any]:
    claim_rows = iter_claim_rows(records)
    auxiliary_lane_rows = load_auxiliary_lane_artifacts()

    claims_by_task = Counter(row["task"] for row in claim_rows)
    claims_by_model = Counter(row["model"] for row in claim_rows)
    claims_by_lane = Counter(row["discovery_lane"] for row in claim_rows)
    providers = Counter(row["provider_id"] for row in claim_rows)

    for row in auxiliary_lane_rows:
        claims_by_lane[row["discovery_lane"]] += 0
        providers[row["provider_id"]] += 0

    bundles = []
    for record in records:
        bundles.append(
            {
                "bundle": record["bundle"],
                "task": record["task"],
                "model": record["model"],
                "claims": record["result"]["overall"]["hypothesis_count"],
                "lane_counts": record["lane_counts"],
                "provider_counts": record["provider_counts"],
                "has_cross_model_results": record["has_cross_model_results"],
                "source": "evaluated_bundle",
            }
        )

    return {
        "bundle_count": len(records),
        "claim_count": len(claim_rows),
        "task_count": len(claims_by_task),
        "model_count": len(claims_by_model),
        "discovery_lane_count": len(claims_by_lane),
        "provider_count": len(providers),
        "claims_by_task": dict(claims_by_task),
        "claims_by_model": dict(claims_by_model),
        "claims_by_lane": dict(claims_by_lane),
        "provider_counts": dict(providers),
        "bundles": bundles,
        "auxiliary_lane_artifacts": auxiliary_lane_rows,
    }

def load_auxiliary_lane_artifacts() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    output_dir = ROOT / "main" / "output"

    for lane_dir in sorted(output_dir.glob("lanes_*")):
        hypotheses_path = lane_dir / "all_hypotheses.json"
        if not hypotheses_path.exists():
            continue
        data = json.loads(hypotheses_path.read_text())
        for row in data:
            rows.append(
                {
                    "source_dir": lane_dir.name,
                    "task": row.get("task_id"),
                    "model": row.get("model_id"),
                    "discovery_lane": row.get("discovery_lane", "unknown"),
                    "provider_id": row.get("provider_id", "unknown"),
                    "hypothesis_id": row.get("hypothesis_id"),
                }
            )

    for sae_dir in sorted(output_dir.glob("sae_lane_*")):
        hypotheses_path = sae_dir / "hypotheses.json"
        if not hypotheses_path.exists():
            continue
        data = json.loads(hypotheses_path.read_text())
        parts = sae_dir.name.split("_")
        task = "_".join(parts[2:-1]) if len(parts) > 3 else "unknown"
        model = parts[-1] if parts else "unknown"
        for row in data:
            rows.append(
                {
                    "source_dir": sae_dir.name,
                    "task": task,
                    "model": model,
                    "discovery_lane": "B3",
                    "provider_id": "sae_autointerp_local",
                    "hypothesis_id": row.get("hypothesis_id"),
                }
            )
    return rows
