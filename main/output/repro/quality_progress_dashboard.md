# Quality Progress Dashboard

This dashboard tracks local artifact quality progress. It does not convert maintainer-authored runs into external blinded submissions, external-custodian holdout executions, or independent Goodhart validation.

- Generated: **2023-11-14T22:13:20+00:00**
- Baseline: `main/output/repro/quality_dashboard_baseline_2026-05-04_pre_final_pass.json`
- Open no-human provenance blockers: **external_blinded_evaluated, external_holdout_executions, independent_goodhart_validations**

| Metric | Direction | Baseline | Current | Movement | Quality effect |
|---|---|---:|---:|---|---|
| Headline/prose drift check | higher | pass | not_run | down | worsened |
| Release overclaim guard | higher | pass | not_run | down | worsened |
| Python compile check | higher | pass | not_run | down | worsened |
| Evaluator+runner tests | higher | pass | not_run | down | worsened |
| Evaluated bundles | neutral | 36 | 36 | unchanged | unchanged |
| Evaluated claims | neutral | 109 | 109 | unchanged | unchanged |
| Accepted claims | neutral | 26/109 (23.85%) | 26/109 (23.85%) | unchanged | unchanged |
| Tasks with accepted claims | higher | 8/8 (100.00%) | 8/8 (100.00%) | unchanged | unchanged |
| Zero-accepted task-model cells | lower | 5/16 (31.25%) | 5/16 (31.25%) | unchanged | unchanged |
| Transfer-confirmed accepted claims | higher | 12/26 (46.15%) | 12/26 (46.15%) | unchanged | unchanged |
| Released prompt-holdout claims passing | higher | 20/26 (76.92%) | 20/26 (76.92%) | unchanged | unchanged |
| High-power prompt claims covered | higher | 25 | 26 | up | improved |
| High-power prompt retained claims | higher | 22/25 (88.00%) | 23/26 (88.46%) | up | improved |
| High-power prompt demoted claims | lower | 3/25 (12.00%) | 3/26 (11.54%) | down | improved |
| High-power retained claims passing all holdouts | higher | 18/22 (81.82%) | 19/23 (82.61%) | up | improved |
| High-power held-out checks passing | higher | 57/61 (93.44%) | 59/63 (93.65%) | up | improved |
| n=100 prompt-holdout completion | higher | 2/14 (14.29%) | 5/17 (29.41%) | up | improved |
| Release-grade fresh agnostic FAR (full budget, release_grade_2026q2) | lower | 42/200 (21.00%) | 0/200 (0.00%) | down | improved |
| Reduced-rehearsal fresh agnostic FAR (128/128, rotated_2026q2) | lower | 0 | 49/200 (24.50%) | up | worsened |
| V1 retained accepted claims | higher | 15/26 (57.69%) | 1/26 (3.85%) | down | worsened |
| V1 retained task breadth | higher | 4/8 (50.00%) | 1/8 (12.50%) | down | worsened |
| Measured runtime coverage | higher | 7.0/36.0 (19.44%) | 8.0/36.0 (22.22%) | up | improved |
| External blinded submissions evaluated | higher | 0 | 0 | unchanged | unchanged |
| External-custodian holdout executions | higher | 0 | 0 | unchanged | unchanged |
| Independent Goodhart validations | higher | 0 | 0 | unchanged | unchanged |

## Stress-row source caveat (2026-05 audit)

The `Release-grade fresh agnostic FAR` row's *baseline* number (42/200, 21.0%) was sourced from `stress_test_agnostic_fresh.json` under a 128/128 reduced statistical budget on the `rotated_2026q2` seed namespace; the *current* number (0/200, 0.0%) is sourced from `stress_test_agnostic_fresh_release_grade.json` under the full default statistical budget on the `release_grade_2026q2` seed namespace. The baseline-to-current movement therefore reflects both an artifact change AND a (budget, namespace) change; the new `Reduced-rehearsal fresh agnostic FAR` row makes the reduced-budget cell visible separately so the dual-budget spread is not silently collapsed onto a single "fresh" row.
