# Targeted Zero-Cell Rerun Preregistrations

This file records targeted empirical reruns for zero-accepted task-model cells
before execution. These runs may change canonical repaired artifacts only when
the candidate, command, decision rule, and allowed claim updates are written
here first. The purpose is to separate legitimate blocker work from repeated
reruns until a favorable acceptance appears.

## 2026-05-04 - Fact-recall GPT-2 Small n=48 breadth check

**Candidate:** `fact_recall_v0_gpt2-small`

**Why this candidate:** `main/output/repro/breadth_gap_analysis.json` ranks
`fact_recall_v0 x gpt2-small` as a zero-accepted task-model cell whose
closest-to-pass claim (`h_fact_recall_v0_001`) fails only
`method_sensitivity` after the prior real repair. The existing
`zero_task_real_repair.json` row used `examples_per_cell = 24`; this rerun
doubles the per-cell examples without changing the protocol gates.

**Command:**

```bash
python main/zero_task_real_repair.py \
  --tasks fact_recall_v0 \
  --models gpt2-small \
  --device mps \
  --examples-per-cell 48 \
  --limit 1
```

**Frozen decision rule:** Use the current evaluator and current repaired
confirmatory protocol only. No method-sensitivity, multiplicity,
negative-control, causal-effect, or evidence-tier threshold may be changed
because of this run.

**Allowed claim update if pass:** report an additional maintainer-authored,
single-model zero-cell repair result in `fact_recall_v0 x gpt2-small`, update
the accepted-count and task-model breadth summaries from regenerated artifacts,
and keep external-validity caveats explicit.

**Required claim update if fail:** keep the current accepted-count headline,
report that the closest fact-recall GPT-2 Small zero-cell candidate still fails
under the n=48 breadth check, and treat the result as evidence that this cell
needs better discovery or claim formation rather than simple sample-size
repair.

**Not allowed:** treating the rerun as external evidence, changing thresholds
after seeing the result, silently replacing the previous n=24 history, or
presenting any new accepted claim as mechanistic truth.
