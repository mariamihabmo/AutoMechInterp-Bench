# Paired-Bundle Cross-Model Replication

- Bundles updated: **8**
- Cross-model-confirmed claims before (updated bundles only): **10**
- Cross-model-confirmed claims after (updated bundles only): **10**

Artifact-backed paired-bundle replication only writes a transfer effect when the paired-model claim with the same hypothesis_id is itself accepted. This is stricter than using any same-id effect regardless of the paired bundle verdict.

| Bundle | Paired bundle | Existing rows | Preserved non-paired rows | Artifact rows | Total rows | XM before | XM after | Promoted hypotheses |
|---|---|---:|---:|---:|---:|---:|---:|---|
| arithmetic_v0_gpt2-small | arithmetic_v0_pythia-70m | 4 | 3 | 1 | 4 | 1 | 1 | none |
| arithmetic_v0_pythia-70m | arithmetic_v0_gpt2-small | 4 | 1 | 3 | 4 | 1 | 1 | none |
| country_capital_v0_gpt2-small_lane_a | country_capital_v0_pythia-70m_lane_a | 5 | 3 | 2 | 5 | 2 | 2 | none |
| country_capital_v0_gpt2-small_lane_c | country_capital_v0_pythia-70m_lane_c | 5 | 3 | 2 | 5 | 2 | 2 | none |
| country_capital_v0_pythia-70m_lane_a | country_capital_v0_gpt2-small_lane_a | 5 | 2 | 3 | 5 | 2 | 2 | none |
| country_capital_v0_pythia-70m_lane_b | country_capital_v0_gpt2-small_lane_b | 1 | 0 | 1 | 1 | 0 | 0 | none |
| country_capital_v0_pythia-70m_lane_c | country_capital_v0_gpt2-small_lane_c | 5 | 2 | 3 | 5 | 2 | 2 | none |
| sentiment_v0_pythia-70m_lane_c | sentiment_v0_gpt2-small_lane_c | 2 | 0 | 2 | 2 | 0 | 0 | none |
