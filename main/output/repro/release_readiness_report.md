# Release Readiness Report

> **Filename note.** This report does NOT certify release-quality. The verdict is
> `plausible_but_not_high_confidence_release_quality`. The legacy filename is retained to
> preserve cross-references and committed SHAs; treat it as a release-readiness report
> with a hard cap at the contract-relative tier.

- Bundles: **36**
- Claims: **109**
- Accepted claims: **26**
- Tasks with accepted claims: **8/8**
- Cross-model-confirmed claims: **12/26**
- Prompt-holdout control: **20/26** claims and **63/70** checks pass
- High-power prompt-holdout diagnostic (n=40): **23/26** original accepted claims retained, **19/23** retained claims pass all holdouts, **59/63** retained-claim holdout checks pass
- Same-family transfer locally ready to run: **0**, blocked: **13**
- Legacy agnostic FAR (released artifact): **10.0%** with 95% CI [4.0%, 23.1%]
- Fresh agnostic FAR (release grade, rotated refresh, 200 negatives): **0.0%** with 95% CI [0.0%, 1.9%]
- Contract-hardening V1 candidate: **1/26** accepted claims retained (3.8%), **1/8** accepted tasks retained, worst hardened-stress CI upper bound **1.9%** across **2** rotated namespaces
- V1 migration decision: **deferred_pending_external_validation**; independent evidence: **False**
- Runtime envelope: **189.5** minutes one sweep, **568.4** minutes with reruns; measured coverage **8/36** (22.2%)
- Transfer breadth queue: **11** non-country candidate claims need new transfer evidence
- Top transfer tail case: `sentiment_v0_gpt2-small_lane_c / h_dla_sentiment_v0_001` is **near_miss_below_floor** at **70.0%** of the floor after the preregistered n=200 scored row
- Docstring explorer diagnosis counts: **{}**
- External blinded submissions evaluated: **0**
- Holdout rehearsal artifact present: **True**
- Zero-task real repair accepted claims: **7** across **4** formerly zero-accepted tasks
- Remaining zero-accepted tasks: **none**
- Zero-accepted task-model cells: **5/16**
- Prompt-variant repair: **25/25** affected accepted claims covered; retained **19**, demoted **6**
- Zero-task confirmatory-present failures (real repair): **0 -> 0**
- Zero-task confirmatory-CI failures (real repair): **23 -> 9**
- Bottom-line verdict: **plausible_but_not_high_confidence_release_quality**

## Binding release-quality criteria status

| criterion | satisfied |
|---|---|
| `operational_holdout_execution` | no |
| `second_cross_model_confirmed_claim` | yes |
| `accepted_claims_in_at_least_5_of_8_tasks` | yes |
| `second_external_third_party_bundle_accepted` | no |
| `agnostic_far_upper_bound_below_5pct` | yes |

- Criteria currently satisfied: **3**
- Additional count criteria needed for the old `plausible` threshold: **0**
- Genuine release-quality blockers still open: **no_external_blinded_or_independent_bundle_evaluated, no_operational_external_custodian_holdout, residual_task_model_breadth_gap, high_power_prompt_holdout_frontier_incomplete**

Meeting two count criteria is not enough to claim high-confidence release quality. External blinded evidence, operational holdout execution, and independent/current-contract Goodhart validation remain decisive.

## Priority order

### Priority 1 - prompt-holdout robustness

- Why still open: The prospective n=40 rerun covered all 26 originally accepted claims across 17/17 accepted bundles. It retained 23/26, demoted 3, and only 19/23 retained claims passed all held-out prompts (59/63 held-out checks).
- Next action: Treat arithmetic, IOI structural prompts, and one sentiment claim as targeted prompt-robustness weaknesses; do not promote a stronger prompt-robustness claim unless a pre-registered repair rerun improves the full accepted surface.
- Expected payoff: Turns a vague prompt-generalization concern into an artifact-backed field-level fragility finding.

### Priority 2 - residual breadth

- Why still open: task-level breadth criterion is now satisfied at 8/8, but remaining_zero_tasks=[], zero_acceptance_task_model_cells=5/16, and accepted evidence is still uneven across the task-model grid. Real zero-task repair contributes 7 accepted claims in ['arithmetic_v0', 'fact_recall_v0', 'gendered_pronoun_v0', 'greater_than_v0'].
- Next action: Target zero-accepted task-model cells without changing the contract; prioritize closest-to-pass cells in breadth_gap_analysis.json.
- Expected payoff: Turns task-level breadth from criterion-satisfying into concrete external-validity evidence.

### Priority 3 - external ecosystem / blinded authorship

- Why still open: external_blinded_submissions=0, external_evaluated=0; maintainer_pilot=2 and holdout_rehearsal_exists=True.
- Next action: Ingest one real external_blinded bundle and run one real private-suite holdout scoring pass with an external custodian.
- Expected payoff: Largest governance credibility gain; scaffolding is already in place, but evidence is still absent.

### Priority 5 - operational holdout

- Why still open: holdout_rehearsal_exists=True, external_evaluated=0.
- Next action: Run the aggregate-only helper on a real private suite with an external custodian and keep it separated from pilot/rehearsal counts.
- Expected payoff: Closes a named verdict criterion and demonstrates governance, not just tooling.

This report operationalizes late-stage release criteria but does not certify release readiness by count alone. The fresh agnostic refresh and hardening-candidate stress replicates use benchmark-authored generators, so treat them as release-grade stress/tradeoff evidence, not as independent Goodhart validation.
