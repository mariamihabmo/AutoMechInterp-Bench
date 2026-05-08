# Red-Team Stress Probes

- Base bundle: `main/output/real_multi_task/ioi_v0_gpt2-small`

## Adaptive search

- Attempts: 10
- Successes: 3
- Success rate: 30.0% (95% CI: [10.8%, 60.3%])

## Near-miss negatives

- Accepted: 0/5
- Acceptance rate: 0.0% (95% CI: [0.0%, 43.4%])

## Bundle-hacking probes

| Attack | Blocked | Accepted | Error |
|---|---|---|---|
| missing_slice | True | False |  |
| single_direction | True | False |  |
| coverage_hole | True | False |  |
| protocol_hash_mismatch | True | False | evaluation_result.protocol_sha256 mismatch |
