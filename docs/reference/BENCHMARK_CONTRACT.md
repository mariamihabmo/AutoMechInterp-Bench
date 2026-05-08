# AutoMechInterp Benchmark Contract

**Version**: 1.0  
**Status**: Active  
**Scope**: This document defines the evaluation contract for the AutoMechInterp benchmark.

---

## Purpose

This benchmark evaluates the reliability of mechanistic interpretability claims under a fixed evidence contract. It does NOT discover circuits — it tests whether a submitted claim bundle (whether produced by a human, a discovery method, or an automated agent) passes a deterministic battery of scientifically rigorous acceptance criteria.

## Evaluation Scope

| Dimension | Specification |
|-----------|--------------|
| **Task domain** | 8 curated NLP tasks with known/suspected circuits |
| **Model families** | GPT-2 (small/medium/large), Pythia (70m/160m/410m/1b) |
| **Intervention types** | Head, MLP, residual stream, edge (composition) |
| **Ablation modes** | Clean patch, zero ablation, mean ablation, resample ablation |
| **Statistical framework** | Non-parametric: permutation tests, bootstrap CIs |
| **Multiplicity control** | Benjamini-Hochberg (FDR) + Holm-Bonferroni (FWER) |
| **Data integrity** | Exploratory/confirmatory split (30/70 default) |

## Acceptance Criteria (15 Hard Gates)

A mechanistic claim passes the benchmark IFF all 15 gates pass:

1. **Execution coverage** — All declared grid cells present
2. **Confirmatory data present** — Held-out data exists
3. **Confirmatory firewall** — No data leakage across splits
4. **Causal effect** — Directional effect ≥ protocol floor
5. **Negative controls** — 6 control families near-zero
6. **Robustness** — Consistency ≥ threshold per axis (seed/prompt/resample)
7. **Method sensitivity** — Cross-method std below threshold
8. **Confirmatory CI** — Bootstrap CI excludes zero
9. **Multiplicity** — BH q-value ≤ FDR threshold
10. **Power adequacy** — n ≥ minimum for declared power + effect
11. **Effect size** — Cohen's d ≥ practical significance threshold
12. **Rank stability** — Cross-method hypothesis rankings stable
13. **Baseline superiority** — Effect exceeds random-circuit baseline
14. **Cross-model transfer** — Rank correlation ≥ threshold across families
15. **Bidirectional** — Both noising and denoising methods present

## Evidence Tiers

| Tier | Criteria |
|------|----------|
| `cross_model_confirmed` | All core gates pass and transfer evidence passes |
| `single_model_confirmed` | All core gates pass with required slices present |
| `causal_plus_robustness` | Core gates pass but accepted-tier slice or optional-transfer requirements remain incomplete |
| `causal_tested_unstable` | Causal/control/robustness signal exists but at least one core requirement still fails |
| `suggestive` | Causal and control evidence exists, but the claim remains below the contract bar |
| `rejected` | The claim fails causal or control requirements outright |

## Input Format

- `protocol.yaml` — Frozen, hashed protocol specification
- `hypothesis.jsonl` — Pre-registered mechanistic claims
- `evaluation_result.json` — Raw intervention results with provenance

## Output Format

- `claim_ledger.json` — Machine-readable per-claim verdicts
- `stage_gate_report.md` — Human-readable report with failure analysis
- `protocol_critic_report.md` — Automated protocol quality assessment

## Determinism Guarantee

Given identical inputs, the evaluator produces byte-identical outputs. All randomness is seeded via SHA-256 hash-based PRNG.

## Limitations

1. Node-level and edge-level interventions only (no SAE/feature-level)
2. Decoder-only transformer architectures (GPT-2, Pythia families)
3. Single metric per unit-of-work (multi-metric is protocol-level)
4. No formal verification (empirical reliability only)
