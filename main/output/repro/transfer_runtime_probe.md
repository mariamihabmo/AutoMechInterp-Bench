# Transfer Runtime Probe

- Software stack ready: **True**
- Any local target-model snapshots present: **True**
- Online model resolution available from this runtime: **True**

## Per-target status

| Target model | Discovered dirs | Loadable dirs |
|---|---:|---:|
| `gpt2-medium` | 3 | 1 |
| `pythia-160m` | 2 | 1 |

Interpretation: if the software stack is ready but loadable local snapshots are absent and online resolution is unavailable, then the remaining blocker is genuinely missing target-model weights rather than a Python/package issue.
