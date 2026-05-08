# Red-Team Probes

## Goal

Probe adaptive failure modes that static stress regimes may miss.

## Command

```bash
python main/stress_test_red_team.py \
  --bundle-dir main/output/real_multi_task/ioi_v0_gpt2-small
```

## Probe families

- adaptive black-box search
- near-miss negatives
- bundle-hacking attempts

## Output artifacts

- `stress_test_red_team.json`
- `stress_test_red_team.md`

## What to monitor

- bypass success rate
- dominant bypass tactics
- recurring gate families targeted by successful probes

## How to use findings

- prioritize contract hardening where bypasses concentrate
- add regression tests for previously successful bypass classes
- re-run deterministic reviews after hardening changes
