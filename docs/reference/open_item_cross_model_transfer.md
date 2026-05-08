# Open Item — Cross-Model Transfer Breadth And Unresolved Tail

> **Current status (2026-05-04).** This document supersedes the historical
> pre-replication `0/12` transfer note and the later country-capital-only
> `8/12` state and the pre-prompt-promotion `9/26` state. The current released
> artifact surface records **12/26** accepted claims with transfer-effect rows
> as `cross_model_confirmed`: eight country-capital paired-bundle replications,
> two arithmetic paired-bundle replications, plus one GPT-2 Small -> GPT-2
> Medium sentiment transfer and one targeted n=100 GPT-2 Small -> GPT-2 Medium
> docstring transfer. A preregistered n=200 rerun of the next top sentiment
> near-miss stayed same-direction but below the frozen floor. The remaining open
> problem is therefore that broader same-family transfer is mostly negative or
> near-miss under the current direction+floor rule, not that the obvious queued
> rows were left unrun. Target-specific same-family execution is no longer
> merely queued: the current preflight has 0 missing eligible rows; of 17
> ranked candidate bundles, 4 are already scored and 13 are blocked by
> missing local target-model snapshots.

**Status:** partially fixed  
**Severity:** major  
**Canonical artifacts:** `main/output/repro/transfer_results_summary.json`,
`main/output/repro/paired_bundle_cross_model_replication_summary.md`,
`main/output/repro/transfer_near_miss_analysis.json`,
`main/output/repro/transfer_breadth_candidate_table.json`

## Current artifact-backed state

- Accepted claims inside transfer-tested bundles: **26**
- Accepted claims with transfer-effect rows: **26**
- Transfer-confirmed accepted claims: **12**
- Transfer-confirmed evidence source: paired-bundle country-capital and arithmetic artifacts plus one same-family sentiment transfer and one targeted n=100 same-family docstring transfer
- Concentration risk: confirmed claims now span four task families, but eight of twelve positives are still country-capital
- Remaining unresolved tail: 14 accepted claims fail direction/floor; no accepted transfer-tested claims are missing transfer rows
- Current execution queue: `transfer_breadth_candidate_table.json` ranks 13
  candidate accepted claims needing new or follow-up transfer evidence, 10 of
  them non-country; same-family preflight now reports 0 missing eligible rows;
  of 17 ranked candidate bundles, 4 are already scored and 13 are blocked by
  missing local target-model snapshots.

This closes the old "0/12 transfer-confirmed" blocker, but it does **not**
support broad cross-model generalization claims.

## What remains open

1. **Transfer breadth:** confirmed claims now span four tasks, but remain
   country-capital-heavy and model-family-limited.
2. **Unresolved tail:** `transfer_near_miss_analysis.json` still identifies
   accepted claims with same-direction below-floor effects, led by sentiment
   `h_dla_sentiment_v0_001` at 70.0% of the transfer floor after the
   preregistered n=200 rerun.
3. **Same-family / source-stability controls:** existing controls still show
   noisy source effects for some transfer-tested claims; future claims should
   separate "does not transfer" from "source evidence itself is unstable."
4. **Governance:** any change to the transfer floor or direction rule must be
   versioned through `docs/reference/protocol_governance_and_migrations.md`.

## Definition of done

This item is fully closed only when at least one additional condition is met
with on-disk artifacts:

1. Transfer-confirmed accepted claims span at least four tasks, not only the
   strongest country-capital, arithmetic, and sentiment lanes. **Current status:
   met literally by the 2026-05-01 docstring n=100 rerun, but residual
   concentration remains.**
2. A same-family/source-stability control is rerun and summarized for the
   transfer-tested accepted claims.
3. The unresolved near-miss tail is reduced or explained by a pre-registered
   transfer analysis without relaxing the contract opportunistically. The
   2026-05-04 sentiment rerun explains the top row as a persistent below-floor
   result rather than sampling noise, but it does not reduce the tail.
4. A versioned transfer-contract migration is proposed and evaluated with
   before/after numbers if the current floor or direction rule is changed.

## First concrete next step

Run the existing transfer diagnostics after every artifact refresh:

```bash
python main/transfer_results_summary.py
python main/transfer_near_miss_analysis.py
python main/transfer_breadth_candidate_table.py
python main/paired_bundle_cross_model_replication.py  # if paired artifacts changed
```

Then update both papers only from the regenerated JSON/Markdown outputs.

## Anti-patterns

- Do not describe `12/26` as broad transfer. It is stronger but still narrow
  evidence: eight country-capital positives, two arithmetic paired positives,
  one same-family sentiment positive, and one targeted same-family docstring
  positive, with many non-country same-family failures.
- Do not lower `CROSS_MODEL_EFFECT_FLOOR` to rescue near-misses without a
  versioned protocol migration.
- Do not treat old `0/12` historical audit text as current methodology truth.
- Do not add a task or model solely to manufacture an easier transfer win.
