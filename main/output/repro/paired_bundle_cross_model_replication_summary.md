# Paired-Bundle Cross-Model Replication

- Bundles updated: **6**
- Cross-model-confirmed claims before (updated bundles only): **8**
- Cross-model-confirmed claims after (updated bundles only): **8**

Artifact-backed paired-bundle replication only writes a transfer effect when the paired-model claim with the same hypothesis_id is itself accepted. This is stricter than using any same-id effect regardless of the paired bundle verdict.

| Bundle | Paired bundle | Existing rows | Preserved non-paired rows | Artifact rows | Total rows | XM before | XM after | Promoted hypotheses |
|---|---|---:|---:|---:|---:|---:|---:|---|
| country_capital_v0_gpt2-small_lane_a | country_capital_v0_pythia-70m_lane_a | 2 | 0 | 2 | 2 | 2 | 2 | none |
| country_capital_v0_gpt2-small_lane_c | country_capital_v0_pythia-70m_lane_c | 2 | 0 | 2 | 2 | 2 | 2 | none |
| country_capital_v0_pythia-70m_lane_a | country_capital_v0_gpt2-small_lane_a | 3 | 0 | 3 | 3 | 2 | 2 | none |
| country_capital_v0_pythia-70m_lane_b | country_capital_v0_gpt2-small_lane_b | 2 | 0 | 2 | 2 | 0 | 0 | none |
| country_capital_v0_pythia-70m_lane_c | country_capital_v0_gpt2-small_lane_c | 3 | 0 | 3 | 3 | 2 | 2 | none |
| sentiment_v0_pythia-70m_lane_c | sentiment_v0_gpt2-small_lane_c | 3 | 0 | 3 | 3 | 0 | 0 | none |
