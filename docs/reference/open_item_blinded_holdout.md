# Open Item — Operational Blinded Holdout Workflow

**Status:** open (plan documented; rehearsal executed; no external operational execution)
**Severity:** major
**Open item.** Externally-authored sealed-envelope evaluation slice ("blinded holdout"); the parallel operational plan is `docs/reference/holdout_stress_governance_plan.md`.
**Owner:** unassigned (Option C/D session)

## Why this is open

The plan in `holdout_stress_governance_plan.md` is correct: without holdout governance, evaluator-authored stress generators can drift toward the released gate taxonomy and produce unrealistically clean false-accept rates. Today the project has the **plan**, a custodian runbook (`holdout/CUSTODIAN_RUNBOOK.md`), and a rehearsal artifact (`main/output/repro/holdout_v0-rehearsal.json`), but zero external executions. The D&B paper appropriately does not claim holdout-hardening; the methodology gap analysis appropriately keeps this open. The work to close it is operational, not theoretical.

## Definition of done

This item closes when **all** of the following are on disk and can be verified by an external reviewer:

1. **At least one privately held bundle suite** that scores against the public contract at a versioned release. The bundle suite itself is **not** in this repo; only its aggregate score is.
2. **A documented holdout-execution helper** under `main/` (e.g., `main/run_holdout.py`) that takes a path to a private suite, runs the released contract against it, and emits an aggregate-only artifact under `main/output/repro/holdout_<version>.json`. The helper must refuse to emit per-item information (only counts and aggregate rates).
3. **A versioning policy** describing when holdouts are scored (only at major contract revisions per the plan), documented in `holdout_stress_governance_plan.md` and cross-linked from `protocol_governance_and_migrations.md`.
4. **A holdout-rotation policy** describing how long an item can live in the holdout before it is rotated into the public test set (the plan currently leaves this unspecified).
5. **An entry in both papers** that updates "plan documented" to "first execution complete" and cites the aggregate score.

## First concrete step

The operational plumbing sub-item has been executed in rehearsal mode:

```bash
python -m holdout.tools.build_results_summary
python main/run_holdout.py --rehearsal --release-version v0-rehearsal --use-cached-results --output main/output/repro/holdout_v0-rehearsal.json
```

The next concrete step is no longer local plumbing; it is recruiting an
external custodian with a private suite and running the aggregate-only command
from `holdout/CUSTODIAN_RUNBOOK.md` exactly once for a named release.

## Evidence required to close

- `main/run_holdout.py` exists and is exercised in CI as a smoke test (against the rehearsal suite if a real one is not yet available).
- At least one `main/output/repro/holdout_*.json` aggregate artifact.
- `holdout_stress_governance_plan.md` extended with a "Status" section that links to the artifact and is honest about whether it is a rehearsal or a real holdout.
- A short entry in the maintainer changelog when an external blinded submission is evaluated.
- An entry moving F-018 to `## Closed` in `findings_inventory.md`.

## Blocking dependencies

- None for the rehearsal plumbing.
- A real holdout requires an external collaborator; that itself is blocked behind F-016 (third-party bundle ecosystem).

## Anti-patterns

- **Do not** describe the rehearsal as a real holdout in either paper. The labeling distinction is the entire point of governance.
- **Do not** commit the private suite, even gitignored. The rehearsal suite is OK to keep locally but should not appear in `main/output/`.
- **Do not** allow the helper to emit per-item information. Aggregate only.
- **Do not** re-score the public release against the same holdout multiple times to "improve" the number; that is exactly the overfitting failure mode the plan exists to prevent.
