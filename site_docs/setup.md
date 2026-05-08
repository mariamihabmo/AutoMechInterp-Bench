# Setup

This page gives a reproducible local setup path for evaluator, runner, and docs tooling.

## Baseline requirements

- Python 3.10+
- Git
- OS with standard shell tooling
- Optional GPU stack for heavier Stage-2 runner jobs

## Recommended local environment

```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e packages/evaluator -e packages/runner
```

If your lab uses `conda` or `uv`, use equivalent isolated environments and keep lock metadata.

## Verify installation

```bash
python -m pytest packages/evaluator/tests -q
python -m pytest packages/runner/tests -q
```

## Optional docs preview environment

```bash
pip install mkdocs mkdocs-material
python scripts/generate_docs_from_json.py
mkdocs serve
```

## Core output paths

- `main/output/real_multi_task/`
- `main/output/community_submissions/`
- `main/output/repro/`

## Reproducibility hardening checklist

- pin Python and key package versions
- freeze protocol versions during evaluation cycles
- avoid changing artifacts after manifest hashing
- run rerun checks before reporting results
- capture environment manifest in shared outputs

## Suggested minimal environment metadata to record

- Python version
- package install method
- OS + architecture
- protocol version/hash
- bundle IDs evaluated

## Troubleshooting

| Issue | Likely cause | Fix |
|---|---|---|
| tests fail only in runner | missing optional task deps | inspect failing module and install task requirements |
| docs build fails locally | missing MkDocs deps | reinstall `mkdocs` and `mkdocs-material` |
| rerun mismatch | hidden nondeterminism | verify seeds, protocol pinning, and artifact immutability |
