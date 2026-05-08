#!/usr/bin/env python3
"""Per-cell breadth-gap forensics for zero-acceptance task-model cells.

The headline breadth number is now much stronger than the historical 3/8
snapshot, but it still does not identify *which* gates block acceptance
in remaining zero-acceptance task-model cells, *how close* rejected claims came
to passing, or *which (task, model) cells are the highest-priority targets* for
a future discovery iteration.

This analyzer produces that breakdown. For every (task, model) cell with
zero accepted claims, it reports:

* the number of evaluated claims in that cell,
* the failed-gate count for each gate (sorted by frequency),
* the "closest-to-pass" claim, defined as the claim with the *fewest*
  failed gates and (as a tie-breaker) the *most* gates marked as
  ``not_evaluated`` rather than as outright failures,
* a summary of which gate families dominate failures in that cell.

The analyzer reads existing per-bundle evaluation results via
:mod:`main._bundle_analysis` and does not change any underlying ground
truth. It does not propose threshold changes (that would risk
overfitting); it only surfaces where the evidence currently sits.

Outputs:

* ``main/output/repro/breadth_gap_analysis.json``
* ``main/output/repro/breadth_gap_analysis.md``
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from main._bundle_analysis import (  # noqa: E402
    REAL_MULTILANE_DIR,
    REAL_MULTI_TASK_DIR,
    evaluate_bundle_records,
    iter_claim_rows,
)

REPRO_DIR = ROOT / "main" / "output" / "repro"


def _closest_to_pass_score(row: dict[str, Any]) -> tuple[int, int, int]:
    """Lower is closer to passing.

    Sort key:
      1. Number of failed gates (fewer = closer).
      2. Negative number of not-evaluated gates (more not-evaluated = the
         claim simply lacked evidence, which is closer to fixable than an
         outright failure).
      3. Negative gate-outcomes count (more total gates considered = more
         informative).
    """
    n_failed = len(row.get("failed_checks", []))
    n_not_eval = len(row.get("not_evaluated_checks", []))
    n_gates = len(row.get("gate_outcomes", {}))
    return (n_failed, -n_not_eval, -n_gates)


def build_analysis() -> dict[str, Any]:
    records = evaluate_bundle_records(REAL_MULTI_TASK_DIR, REAL_MULTILANE_DIR, use_cached_results=True)
    rows = iter_claim_rows(records)

    cells: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for r in rows:
        cells.setdefault((r["task"], r["model"]), []).append(r)

    cell_summaries = []
    zero_cells = []
    nonzero_cells = []
    for (task, model), bucket in sorted(cells.items()):
        n_claims = len(bucket)
        n_accepted = sum(1 for r in bucket if r["passed"])
        gate_failure_counts: Counter[str] = Counter()
        for r in bucket:
            if not r["passed"]:
                gate_failure_counts.update(r.get("failed_checks", []))
        sorted_gates = sorted(gate_failure_counts.items(), key=lambda kv: (-kv[1], kv[0]))

        rejected = [r for r in bucket if not r["passed"]]
        closest = (
            min(rejected, key=_closest_to_pass_score) if rejected else None
        )

        summary = {
            "task": task,
            "model": model,
            "n_claims": n_claims,
            "n_accepted": n_accepted,
            "n_rejected": n_claims - n_accepted,
            "failed_gate_counts": dict(sorted_gates),
            "closest_to_pass": (
                {
                    "bundle": closest["bundle"],
                    "hypothesis_id": closest["hypothesis_id"],
                    "discovery_lane": closest["discovery_lane"],
                    "evidence_tier": closest["evidence_tier"],
                    "n_failed_gates": len(closest["failed_checks"]),
                    "failed_gates": list(closest["failed_checks"]),
                    "n_not_evaluated_gates": len(closest["not_evaluated_checks"]),
                    "not_evaluated_gates": list(closest["not_evaluated_checks"]),
                }
                if closest
                else None
            ),
        }
        cell_summaries.append(summary)
        if n_accepted == 0 and n_claims > 0:
            zero_cells.append(summary)
        elif n_accepted > 0:
            nonzero_cells.append(summary)

    # Highest-priority zero-cell = the zero-cell whose closest-to-pass claim
    # has the fewest failed gates (tie-break: most not_evaluated).
    priority_targets = sorted(
        [c for c in zero_cells if c["closest_to_pass"] is not None],
        key=lambda c: (
            c["closest_to_pass"]["n_failed_gates"],
            -c["closest_to_pass"]["n_not_evaluated_gates"],
        ),
    )

    payload = {
        "n_cells": len(cell_summaries),
        "n_zero_acceptance_cells": len(zero_cells),
        "n_nonzero_acceptance_cells": len(nonzero_cells),
        "zero_acceptance_cells": zero_cells,
        "nonzero_acceptance_cells": nonzero_cells,
        "priority_targets": priority_targets[:5],
    }
    return payload


def format_md(payload: dict[str, Any]) -> str:
    lines = [
        "# Breadth-Gap Forensics",
        "",
        f"- Total task-model cells: **{payload['n_cells']}**",
        f"- Cells with at least one accepted claim: **{payload['n_nonzero_acceptance_cells']}**",
        f"- Cells with zero accepted claims: **{payload['n_zero_acceptance_cells']}**",
        "",
        "## Highest-priority breadth targets",
        "",
        "These are zero-acceptance task-model cells whose closest-to-pass claim has",
        "the fewest failed gates. They are the cells where a small number of",
        "additional evidence improvements (or evidence collection for currently",
        "not-evaluated gates) could plausibly produce the next accepted claim",
        "*without changing the contract*.",
        "",
        "| task | model | closest-to-pass: bundle | failed gates | not-evaluated gates |",
        "|---|---|---|---|---|",
    ]
    for cell in payload["priority_targets"]:
        ctp = cell["closest_to_pass"]
        lines.append(
            f"| `{cell['task']}` | `{cell['model']}` | `{ctp['bundle']}` | "
            f"{ctp['n_failed_gates']} | {ctp['n_not_evaluated_gates']} |"
        )
    lines.append("")

    lines.extend(["## Per-cell failure breakdown (zero-acceptance cells)", ""])
    for cell in payload["zero_acceptance_cells"]:
        lines.extend(
            [
                f"### `{cell['task']}` × `{cell['model']}`",
                "",
                f"- Evaluated claims: **{cell['n_claims']}**, all rejected.",
            ]
        )
        if cell["failed_gate_counts"]:
            top = list(cell["failed_gate_counts"].items())[:6]
            lines.append(
                "- Top failed gates: " + ", ".join(f"`{g}` ({n})" for g, n in top)
            )
        if cell["closest_to_pass"]:
            ctp = cell["closest_to_pass"]
            lines.extend(
                [
                    f"- Closest-to-pass: `{ctp['bundle']}` / `{ctp['hypothesis_id']}`",
                    f"  - {ctp['n_failed_gates']} failed gates: " + (", ".join(f"`{g}`" for g in ctp["failed_gates"]) or "_(none)_"),
                    f"  - {ctp['n_not_evaluated_gates']} not-evaluated gates: " + (", ".join(f"`{g}`" for g in ctp["not_evaluated_gates"]) or "_(none)_"),
                ]
            )
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    REPRO_DIR.mkdir(parents=True, exist_ok=True)
    payload = build_analysis()
    out_json = REPRO_DIR / "breadth_gap_analysis.json"
    out_md = REPRO_DIR / "breadth_gap_analysis.md"
    out_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    out_md.write_text(format_md(payload))
    print(str(out_json))


if __name__ == "__main__":
    main()
