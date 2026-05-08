# AutoMechInterp: Automated Mechanistic Interpretability via Deterministic Evaluation

> Public docs website: **redacted for double-blind review.** The URL is restored after the review window closes.

Auto-MechInterp is a verification harness for mechanistic interpretability claims. It separates *hypothesis generation* (from human analysts, circuit heuristics, automated neuron explanation systems, or SAE-based autointerp pipelines) from *verification*, which is performed by a deterministic stage-gate of causal interventions, negative controls, robustness checks, method-sensitivity analysis, and integrity/provenance requirements.

Circuit evaluation can be brittle: small changes in intervention methodology and evaluation choices can substantially change which explanations appear "faithful." Auto-MechInterp makes these degrees of freedom explicit by standardizing the execution grid and reporting stability and sensitivity diagnostics alongside effect sizes, rather than relying on a single faithfulness score.

The goal is not to replace automated interpretability or automated auditing; it is to provide a verification layer that turns automated discoveries into comparable empirical claims. By enforcing a common schema and explicit evidence tiers (`cross_model_confirmed`, `single_model_confirmed`, `causal_plus_robustness`, `causal_tested_unstable`, `suggestive`, `rejected`), Auto-MechInterp enables fair comparisons between discovery lanes and reduces cherry-picking in interpretability-driven model audits.

Current released evaluated snapshot, as regenerated from the visible bundle artifacts in this repo:

- `36` evaluated bundles
- `109` evaluated claims
- `26` accepted claims
- accepted claims now span all eight released tasks, two model families, the canonical path, discovery lanes `A`, `B`, and `C`, real zero-task repair reruns, prompt-repair reruns, the docstring multi-lane rerun, and the targeted n=48 fact-recall GPT-2 Small zero-cell repair. Accepted evidence still occupies only **11 / 16** task-by-model cells, so the breadth bullet should be read alongside `main/output/repro/breadth_gap_analysis.json`.
- evaluated breadth now also includes fully evaluated sentiment lane-`B` bundles and released `B3` / `sae_feature` bundles, though those specific added slices still contain rejected claims
- `19` released bundles now include `cross_model_results.json`; **12 / 26** accepted claims with transfer-effect rows currently reach `cross_model_confirmed` on the released artifact surface. Eight positives are country-capital paired-bundle replications, two are arithmetic paired-bundle replications, one is a GPT-2 Small -> GPT-2 Medium sentiment transfer, and one is a GPT-2 Small -> GPT-2 Medium docstring transfer after a targeted n=100 rerun; the new fact-recall GPT-2 Small accepted claim was immediately transfer-tested and remains single-model-only, and the remaining same-family and type-aware MLP/MLP-neuron transfer tail remains mostly negative or near-miss evidence under the current direction+floor rule. All transfer-confirmed claims are paired same-family transfer within maintainer-authored bundles, not independent third-party replication.
- prompt-holdout retention: a higher-power n=40 diagnostic covers the full current accepted surface and retains **23 / 26** claims; only **19 / 23** retained claims pass all held-out prompts.
- stress / Goodhart-resistance disclosure: evaluator-agnostic stress shows **0 / 200** false accepts on the release-grade cell and **49 / 200** on the paired reduced-rehearsal cell. The two cells differ on namespace and statistical budget, so quote them together; neither is a stand-alone Goodhart-resistance number, and the 0/200 figure is a same-generator-floor signal under the release-grade budget rather than an external Goodhart-resistance proof.
- runtime envelope: approximately **189.5 minutes** for one full released sweep and approximately **568.4 minutes** with three reruns, with **8 / 36** bundles directly measured and the remaining 28 extrapolated from the per-cell rate.
- external evidence to date: **0** external blinded submissions have been evaluated. The two pilot submissions under `holdout/pilot/` are maintainer-authored and never count as external evidence.
- publication-quality figure generation is reproducible from the released artifacts via `python main/generate_publication_figures.py`

Treat those counts as the default truth unless you regenerate broader artifacts locally. The real zero-task repair reruns under `main/output/zero_task_real_repair/` supersede same-named legacy zero-task bundles in canonical aggregate reporting, while the new docstring multi-lane bundles add three evaluated bundles and nine claims. For the current blocker-closure status beyond the legacy released stress slice, see `main/output/repro/release_readiness_report.md` and `main/output/repro/direct_blocker_closure_report.md`.
Also note: much of the original `main/output/real_multi_task/` archive predates the latest runner-semantics fixes, so the strongest current evidence comes from the regenerated multi-lane bundles under `main/output/real_multilane/` and real repair reruns under `main/output/zero_task_real_repair/`.

---

## Multi-Lane Architecture

Auto‑MechInterp treats every upstream discovery system as a **hypothesis provider**. All providers emit structured claims through the same pipeline:

```
Provider (lane) → exploration artifact → hypothesis.jsonl
    → Stage-2 runner → evaluation_result.json
    → Stage-1 gates (15 core + optional transfer gate) → evidence tier + leaderboard
```

This matches the core philosophy: **Discovery proposes, verification disposes.** Stage-1 remains the only judge.

### Supported Discovery Lanes

| Lane | Source | What It Does |
|------|--------|-------------|
| **A** — Circuit Sweep | TransformerLens heuristics | Patches each head, ranks by effect, emits top-k |
| **B1** — OpenAI AutoInterp | Neuron explanations | Converts explainer/simulator artifacts → `mlp_neuron` hypotheses |
| **B2** — Efficient AutoInterp | Prompt-tuned explanations | Same as B1, tracks prompt engineering metadata |
| **B3** — SAE AutoInterp | SAE feature selection | Converts selected features → `sae_feature` hypotheses |
| **C** — Petri Behavioral | Anthropic Petri auditing | Links behavioral detection metrics to mechanistic claims |

See [`docs/reference/LANES.md`](docs/reference/LANES.md) for full details.

### 7 Component Types

The framework supports verification across multiple granularities of mechanistic claims:

| Type | Example Claim |
|------|--------------|
| `head` | "Attention head L9H6 performs name-moving in IOI" |
| `mlp` | "MLP layer 7 stores factual recall information" |
| `residual_stream` | "Residual stream at layer 5 encodes sentiment direction" |
| `edge` | "Head L2H3 composes with head L5H1 for induction" |
| `mlp_neuron` | "Neuron L4N2817 fires on closing brackets" |
| `sae_feature` | "SAE feature F1234 detects alignment-faking patterns" |
| `das_subspace` | "DAS subspace at layer 8 encodes truthfulness" |

Each component type has its own mandatory negative control families.

---

## Core Philosophy

1. **Discovery Proposes, Verification Disposes**: Upstream discovery systems may run exploratory patching and propose interesting mechanistic hypotheses in a pre-registered format, but they **cannot** self-certify their findings as true.
2. **Deterministic Stage-Gate Filtering**: Only the deterministic `automechinterp_evaluator` can accept or reject those hypotheses via a fixed sequence of core gates plus optional transfer evidence.
3. **No Interpretability Illusions**: Every accepted claim must survive causal interventions, rigorous negative controls, statistical adjustments for multiple comparisons across families, and a strict separation of exploratory and confirmatory data.

If a mechanized circuit survives all core gates (and optional transfer checks when present), it has passed the contract's empirical robustness gates. If it sounds extremely plausible but fails the gates, it is treated as an interpretability illusion.

---

## Repository Structure

*   `packages/evaluator/` — **Stage-1 Evaluator**: deterministic core gates + optional cross-model transfer gate, including bidirectional enforcement, robustness checks, permutation p-values, compensatory detection, and multiplicity correction.
*   `packages/runner/` — **Stage-2 Runner**: Generates intervention logits across an 8-model registry (GPT-2 + Pythia families), supporting head/MLP/residual/edge/neuron/SAE-feature patching.
    *   `providers/` — Discovery lane implementations (circuit sweep, OpenAI autointerp, SAE autointerp, efficient neuron explanations, Petri behavioral).
*   `docs/` — Methodology lineage and reference material.
*   `site_docs/` — Canonical MkDocs documentation source.

## Canonical released artifacts

The canonical released artifact surface for this lightweight repository is the evaluated bundle set under:

- `main/output/real_multi_task/`
- `main/output/real_multilane/`
- `main/output/repro/`

Those directories are what the benchmark summaries, methodology analyses, and papers refer to. Historical notes and earlier methodology versions remain under `docs/`, but they should not be treated as additional released evaluation lanes.

---

## Quick Start

```bash
# Optional but recommended for repo-local CLI usage
python -m pip install -e packages/evaluator -e packages/runner

# Needed for publication figure regeneration
python -m pip install matplotlib

# Run evaluator tests (fresh-checkout compatible via repo-level test config)
python -m pytest packages/evaluator/tests -q

# Run runner tests
python -m pytest packages/runner/tests -q
```

### Community Submission Review

```bash
# If you did not install the packages editable, prefix with:
# PYTHONPATH=packages/evaluator/src

# Stable rerun check + workflow actions for any submitted bundle
python -m automechinterp_evaluator.cli submission-review \
  --bundle /path/to/bundle \
  --reruns 3 \
  --output-json /path/to/bundle/submission_review.json \
  --output-md /path/to/bundle/submission_review.md
```

This output is designed for independent users: it maps failed gates to actionable next experiments and converts evidence tiers into workflow decisions.

A representative reviewer kit for the canonical IOI bundle can also be generated under `main/output/repro/reviewer_kit/`.

### One-Command Reproducibility Audit

```bash
# From repo root
python main/reproducibility_audit.py
```

The current materialized audit is a 43-command cached-artifact audit. It
regenerates benchmark summaries, real-repair summaries, transfer diagnostics,
runtime/cost summaries, release-grade fresh evaluator-agnostic stress diagnostics,
docstring distributed-repair diagnostics, transfer/docstring blocker queues,
prompt-variant validity and repair-rerun diagnostics, prompt-repair paired-transfer
summaries, prompt-repair same-family transfer summaries,
independent-stress rehearsal artifacts, contract-hardening migration-decision artifacts, holdout rehearsal summaries,
publication figures, generated docs, the repo-integrity/prose-vs-artifact drift
checks, and the release-overclaim guard. It
does **not** run live model interventions; real model reruns remain hardware-
and dependency-sensitive and should be reported separately.

> **Scope of one-command audit.**
> One command regenerates the *summary* artifacts and validates them against
> canonical SHAs. Real Stage-2 generation (live HuggingFace weights, cached
> token logits, intervention re-execution) requires `make download-models` and
> a live-model envelope of approximately 5 minutes per bundle on the released
> hardware (median across 8 / 36 directly measured bundles, with the remaining
> 28 extrapolated). See `runtime_cost_report.md` and the `model_cache/` runbook
> for details.

The audit writes:
- `main/output/repro/environment_manifest.json` (sanitized, repo-relative provenance)
- `main/output/repro/reproducibility_audit.json`
- `main/output/repro/reproducibility_audit.md`
- `main/output/repro/benchmark_breadth_summary.json`
- `main/output/real_multi_task/coverage_summary.json`
- `main/output/real_multi_task/coverage_summary.md`
- `main/output/community_submissions/community_value_summary.json`
- `main/output/repro/field_level_findings.json`
- `main/output/repro/field_level_findings.md`
- `main/output/repro/transfer_results_summary.json`
- `main/output/repro/transfer_near_miss_analysis.json`
- `main/output/repro/runtime_cost_report.json`
- `main/output/repro/runtime_cost_report.md`
- `main/output/repro/stress_test_agnostic_fresh_release_grade.json`
- `main/output/repro/transfer_breadth_candidate_table.json`
- `main/output/repro/docstring_method_sensitivity_explorer.json`
- `main/output/repro/docstring_distributed_repair.json`
- `main/output/repro/independent_agnostic_stress_current_rehearsal.json`
- `main/output/repro/independent_agnostic_stress_hardened_v1_rehearsal.json`
- `main/output/repro/contract_hardening_v1_migration_decision.json`
- `methodology/contract_hardening_v1_migration_decision.md`
- `main/output/repro/release_readiness_report.json`
- `papers/submissions/shared/figures/`
- `site_docs/generated/` and `site_docs/assets/generated/`

### Publication Figures

```bash
python main/generate_publication_figures.py
```

This regenerates publication-oriented figures and distilled takeaways under:
- requires `matplotlib` in the active environment
- `main/output/repro/release_takeaways.json`
- `papers/submissions/shared/figures/`
- `site_docs/assets/generated/`

### Breadth / Lane Expansion Utilities

```bash
# Build evaluated multi-lane bundles from real lane artifacts + real raw cells
python main/build_multilane_real_bundles.py --mode real --device mps

# Quantify breadth across tasks, models, lanes, and providers
python main/summarize_benchmark_breadth.py

# Field-level findings: stratified acceptance/failure + policy sensitivity
python main/field_level_findings.py

# Runtime/cost envelope for Stage-1 evaluation
python main/runtime_cost_report.py --reruns 3
```

### Adversarial Robustness (Evaluator-Agnostic + Adaptive)

```bash
# Latent-factor evaluator-agnostic stress
python main/stress_test_agnostic.py --bundle-dir main/output/real_multi_task/ioi_v0_gpt2-small

# Adaptive black-box + near-miss + bundle-hacking probes
python main/stress_test_red_team.py --bundle-dir main/output/real_multi_task/ioi_v0_gpt2-small
```

### Released Transfer Diagnostics

```bash
# Generate cross-model transfer diagnostics for an evaluated bundle
python main/run_transfer_release.py \
  --bundle-dir main/output/real_multilane/country_capital_v0_gpt2-small_lane_c \
  --transfer-model pythia-70m \
  --device mps \
  --n-examples 8
```

This adds released transfer diagnostics. The current released artifact surface records **12 / 26** accepted claims with transfer-effect rows at `cross_model_confirmed`: eight country-capital paired-bundle replications, two arithmetic paired-bundle replications, one same-family sentiment transfer, and one same-family docstring transfer after the targeted n=100 rerun. Do not describe this as broad cross-model generalization; the remaining same-family, fact-recall, and type-aware MLP/MLP-neuron transfer runs mostly expose direction/floor failures.

### Compatibility Standard (Reference Vectors)

```bash
# If you did not install the packages editable, prefix with:
# PYTHONPATH=packages/evaluator/src

# Canonical compatibility vectors for third-party evaluator implementations
python -m automechinterp_evaluator.cli reference-vectors

# Reviewer kit for a publication-facing bundle
python -m automechinterp_evaluator.cli reviewer-kit \
  --bundle main/output/real_multi_task/ioi_v0_gpt2-small \
  --output-dir .
```

Reviewer kits are portable but not fully standalone: rerunning them requires either an installed `automechinterp_evaluator` package or a checkout of this repository (the helper script supports `AUTOMECHINTERP_REPO_ROOT`).

Standards docs:
- [Claim Bundle Spec v1](docs/reference/claim_bundle_spec_v1.md)
- [Protocol Governance and Migrations](docs/reference/protocol_governance_and_migrations.md)
- [Holdout Stress Governance Plan](docs/reference/holdout_stress_governance_plan.md)
- [Independent Researcher External Evidence Playbook](docs/reference/independent_researcher_external_evidence_playbook.md)

### GitHub Pages Documentation Site

User-facing docs and tutorials are built from `site_docs/` (MkDocs).

- Public website: `https://anonymous.example.org/automechinterp/` *(URL redacted for NeurIPS 2026 double-blind review; restored after the review window closes)*
- Legacy website archive: `https://anonymous.example.org/automechinterp/legacy/index.html` *(URL redacted for NeurIPS 2026 double-blind review)*
- Docs source: `site_docs/`
- Site config: `mkdocs.yml`
- Deployment workflow: `.github/workflows/pages.yml`

### Using a Discovery Lane

```python
from automechinterp_runner.providers.circuits_sweep import CircuitSweepProvider

provider = CircuitSweepProvider(mode="mock", top_k=10)
hypotheses = provider.propose(protocol, budget=10)
# → list of hypothesis dicts ready for hypothesis.jsonl
```

> **Docs**: Website *(URL redacted for NeurIPS 2026 double-blind review)* · [Methodology V26](docs/methodology_versions/methodologyV26_main_track_significance_gap_analysis.md) · [Benchmark Contract](docs/reference/BENCHMARK_CONTRACT.md) · [Lanes Reference](docs/reference/LANES.md)
> · [Claim Bundle Spec v1](docs/reference/claim_bundle_spec_v1.md) · [Reproducibility Runbook](docs/reference/reproducibility_runbook.md)
