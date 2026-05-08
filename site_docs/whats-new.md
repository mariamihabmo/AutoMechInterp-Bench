# What's New

## Documentation architecture refresh

The docs site now uses MkDocs Material and a Diataxis structure so users can quickly separate:

- Tutorials (guided learning)
- How-to guides (task-focused operations)
- Reference (exact interfaces and schemas)
- Explanation (methodology and design rationale)

## Major upgrades in this version

- Deeper contract and gate documentation, including evidence-tier behavior and failure interpretation.
- Expanded submission and reproducibility guidance for external users.
- Stronger comparisons/positioning section with benchmark and tooling context.
- Preserved legacy static website under `legacy/` for continuity.

## Legacy compatibility

The old static site remains available at:

- [Legacy home](https://anonymous.example.org/automechinterp/legacy/index.html)

## How to regenerate docs-backed summary pages

```bash
python scripts/generate_docs_from_json.py
```

Generated files are written to `site_docs/generated/`.
