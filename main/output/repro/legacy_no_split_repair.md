# Legacy No-Split Bundle Repair

This migration is intentionally narrow: it only repairs archived bundles that
explicitly declared `require_confirmatory_split: false` yet labeled every raw
cell as `exploratory`. Under current evaluator semantics, those bundles are
supposed to use their single released slice as the confirmatory slice.

- Bundles scanned: **36**
- Bundles repaired: **0**
- Bundles skipped: **36**
- Accepted claims before repair (where cached current results existed): **0**
- Accepted claims after repair: **0**

## Repaired bundles

| bundle | changed cells | accepted before | accepted after | net change |
|---|---:|---:|---:|---:|

## Skipped bundles

- `require_confirmatory_split_not_false`: 21
- `raw_slices=['confirmatory']`: 15

## Interpretation

This migration removes a protocol/artifact mismatch. It does **not** create new
evidence or fabricate a held-out split. Any claims that remain blocked after the
repair are blocked for substantive reasons (for example multiplicity, causal
effect, robustness, or method sensitivity), not because the bundle mislabeled its
only released slice.
