#!/usr/bin/env python3
"""Compute a per-claim gate co-failure matrix and the dominant fragility cluster.

The co-failure matrix is a derived projection of the existing
``top_failed_combinations`` data emitted by ``main/field_level_findings.py``
into ``main/output/real_multi_task/failure_mode_summary.json``. It does not
introduce any new ground truth; it re-projects the same raw failure
information into a more compact summary form.

For each ordered pair of gates ``(g1, g2)`` the matrix entry is the number
of claims that failed both ``g1`` and ``g2``. Diagonal entries are the
total number of claims failing the gate. The "dominant fragility cluster"
is the single largest entry of ``top_failed_combinations`` and is reported
separately because it is unusually informative on the current release: a
    the dominant exact pattern can include optional-gate failures on accepted
    single-model claims, so it is reported over claims with at least one failed
    gate rather than only over rejected claims.

Outputs:

* ``main/output/repro/co_failure_matrix.json`` -- machine-readable matrix
  plus the dominant fragility cluster summary.
* ``main/output/repro/co_failure_matrix.md`` -- human-readable matrix,
  per-gate marginal totals, and a one-paragraph narrative summary.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FAILURE_SUMMARY_PATH = ROOT / "main" / "output" / "real_multi_task" / "failure_mode_summary.json"
REPRO_DIR = ROOT / "main" / "output" / "repro"


def compute_co_failure_matrix(failure_summary: dict) -> dict:
    """Build the co-failure matrix from ``all_failed_combinations``.

    The ``all_failed_combinations`` field collapses identical failed-gate
    sets across claims with their occurrence counts (and, unlike
    ``top_failed_combinations``, includes the full long tail), so the matrix
    can be reconstructed exactly without re-evaluating any bundle. We fall
    back to ``top_failed_combinations`` for backwards compatibility with
    older summaries; in that fallback path the matrix may understate
    co-failures from the long tail and we surface that fact in
    ``diagonal_check_complete``.
    """
    combos_full = failure_summary.get("all_failed_combinations")
    using_full = combos_full is not None
    combos = combos_full if using_full else failure_summary["top_failed_combinations"]
    failed_gate_counts: dict[str, int] = dict(failure_summary["failed_gate_counts"])

    gates = sorted(failed_gate_counts.keys())
    gate_to_idx = {g: i for i, g in enumerate(gates)}
    n = len(gates)

    matrix = [[0 for _ in range(n)] for _ in range(n)]
    for entry in combos:
        count = entry["count"]
        for g1 in entry["failed_checks"]:
            i = gate_to_idx[g1]
            for g2 in entry["failed_checks"]:
                j = gate_to_idx[g2]
                matrix[i][j] += count

    # Diagonal-vs-marginal check: if we used the full combination list,
    # diagonals must equal the marginal failed_gate_counts (this is a hard
    # invariant). If we fell back to top-10 only, the diagonal will
    # under-count and we record that.
    diagonal_check = {gates[i]: matrix[i][i] for i in range(n)}
    diagonal_check_complete = using_full and all(
        diagonal_check[g] == failed_gate_counts[g] for g in gates
    )

    # Dominant cluster = largest single co-failure combo.
    dominant = max(combos, key=lambda r: r["count"]) if combos else None

    n_failed = failure_summary.get("n_failed", 0)
    n_claims = failure_summary.get("n_claims", 0)
    claims_with_failed_gates = sum(int(entry["count"]) for entry in combos)

    payload = {
        "gates": gates,
        "matrix": matrix,
        "diagonal_check": diagonal_check,
        "diagonal_check_complete": diagonal_check_complete,
        "source": "all_failed_combinations" if using_full else "top_failed_combinations",
        "marginal_failed_gate_counts": failed_gate_counts,
        "n_claims": n_claims,
        "n_failed": n_failed,
        "claims_with_failed_gates": claims_with_failed_gates,
        "dominant_fragility_cluster": (
            {
                "failed_gates": dominant["failed_checks"],
                "claims_with_this_pattern": dominant["count"],
                "fraction_of_claims_with_failed_gates": (
                    dominant["count"] / claims_with_failed_gates
                    if claims_with_failed_gates
                    else 0.0
                ),
                "fraction_of_all_claims": (
                    dominant["count"] / n_claims if n_claims else 0.0
                ),
                "size": len(dominant["failed_checks"]),
            }
            if dominant
            else None
        ),
        "top_failed_combinations": failure_summary["top_failed_combinations"],
    }
    return payload


def format_co_failure_md(payload: dict) -> str:
    gates = payload["gates"]
    matrix = payload["matrix"]
    n_claims = payload["n_claims"]
    n_failed = payload["n_failed"]
    claims_with_failed_gates = payload["claims_with_failed_gates"]
    cluster = payload["dominant_fragility_cluster"]

    lines = [
        "# Gate Co-Failure Matrix",
        "",
        f"- Claims analyzed: **{n_claims}**",
        f"- Rejected: **{n_failed}**",
        f"- Claims with at least one failed gate: **{claims_with_failed_gates}**",
        "",
        "## Dominant fragility cluster",
        "",
    ]
    if cluster:
        lines.extend(
            [
                f"- Pattern size: **{cluster['size']} gates**",
                f"- Claims with this exact failure pattern: **{cluster['claims_with_this_pattern']}**",
                f"- Fraction of claims with failed gates: **{cluster['fraction_of_claims_with_failed_gates'] * 100:.1f}%**",
                f"- Fraction of all evaluated claims: **{cluster['fraction_of_all_claims'] * 100:.1f}%**",
                "- Failed gates: " + ", ".join(f"`{g}`" for g in cluster["failed_gates"]),
                "",
            ]
        )
    else:
        lines.append("- No co-failure data available.")
        lines.append("")

    lines.extend(["## Marginal failed-gate counts", "", "| Gate | Claims failing |", "|---|---|"])
    for gate, count in sorted(payload["marginal_failed_gate_counts"].items(), key=lambda kv: (-kv[1], kv[0])):
        lines.append(f"| `{gate}` | {count} |")

    lines.extend(["", "## Co-failure matrix (claims failing both gates)", ""])
    header = "| gate | " + " | ".join(gates) + " |"
    sep = "|---" * (len(gates) + 1) + "|"
    lines.append(header)
    lines.append(sep)
    for i, gi in enumerate(gates):
        row = "| `" + gi + "` | " + " | ".join(str(matrix[i][j]) for j in range(len(gates))) + " |"
        lines.append(row)

    lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    failure_summary = json.loads(FAILURE_SUMMARY_PATH.read_text())
    payload = compute_co_failure_matrix(failure_summary)
    REPRO_DIR.mkdir(parents=True, exist_ok=True)
    out_json = REPRO_DIR / "co_failure_matrix.json"
    out_md = REPRO_DIR / "co_failure_matrix.md"
    out_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    out_md.write_text(format_co_failure_md(payload))
    print(str(out_json))


if __name__ == "__main__":
    main()
